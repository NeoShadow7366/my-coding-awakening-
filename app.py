"""Local AI inference UI backend for text and image generation.

The app uses:
- Ollama for local text generation
- ComfyUI for local image generation
"""

import io
import json
import logging
import os
import re
import shlex
import subprocess
import sys
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from random import randint
from urllib.parse import quote

import requests
from flask import Flask, Response, jsonify, render_template, request, send_file, stream_with_context

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
ASSET_VERSION = str(int(time.time()))

# Ollama runs on this address by default when installed locally.
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

COMFYUI_BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://localhost:8188")

DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 1024
DEFAULT_IMAGE_STEPS = 30
DEFAULT_IMAGE_CFG = 7.0
DEFAULT_IMAGE_DENOISE = 0.75

MAX_STEPS = 150
MIN_STEPS = 1
MAX_CFG = 30.0
MIN_CFG = 1.0

DATA_DIR = Path(app.root_path) / "data"
HISTORY_FILE = DATA_DIR / "history.json"
SERVICE_CONFIG_FILE = DATA_DIR / "service_config.json"
SERVICE_LOG_DIR = DATA_DIR / "service_logs"

SERVICE_PORTS = {
    "ollama": 11434,
    "comfyui": 8188,
}

_history_lock = threading.Lock()
_service_config_lock = threading.Lock()
_service_log_lock = threading.Lock()
_model_metadata_lock = threading.Lock()
_migration_jobs_lock = threading.Lock()
_migration_jobs: dict[str, dict] = {}
_comfyui_update_jobs_lock = threading.Lock()
_comfyui_update_jobs: dict[str, dict] = {}
_service_processes: dict[str, subprocess.Popen | None] = {
    "ollama": None,
    "comfyui": None,
}
_last_service_errors: dict[str, str] = {
    "ollama": "",
    "comfyui": "",
}


@app.context_processor
def inject_asset_version() -> dict[str, str]:
    """Expose a simple asset version string to templates for cache busting."""
    return {"asset_version": ASSET_VERSION}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _ollama_available() -> bool:
    """Return True if the local Ollama service is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _list_ollama_models() -> list[dict]:
    """Return a list of locally available Ollama models."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        return resp.json().get("models", [])
    except Exception as exc:
        logger.warning("Could not fetch Ollama models: %s", exc)
        return []


def _pick_default_ollama_model() -> str:
    """Return a usable local Ollama model name or empty string."""
    models = _list_ollama_models()
    for model in models:
        name = (model.get("name") or "").strip()
        if name:
            return name
    return ""


def _extract_prompt_suggestions(raw_text: str) -> list[str]:
    """Parse up to 3 concise prompt suggestions from an LLM response."""
    lines: list[str] = []
    for raw_line in (raw_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = line.lstrip("- ").strip()
        if ". " in line[:4] and line[0].isdigit():
            line = line.split(". ", 1)[1].strip()
        if line:
            lines.append(line)

    if not lines:
        fallback = (raw_text or "").strip()
        return [fallback] if fallback else []

    # Keep only unique suggestions while preserving order.
    unique_lines: list[str] = []
    seen = set()
    for line in lines:
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_lines.append(line)
        if len(unique_lines) >= 3:
            break
    return unique_lines


def _comfy_available() -> bool:
    """Return True if ComfyUI is reachable."""
    # Some ComfyUI builds expose /queue reliably even when /system_stats is missing.
    health_paths = ["/system_stats", "/queue"]
    for path in health_paths:
        try:
            resp = requests.get(f"{COMFYUI_BASE_URL}{path}", timeout=2)
            if resp.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            continue
    return False


def _get_comfyui_version() -> dict:
    """Get ComfyUI version/commit info from git repo."""
    config = _load_service_config()
    path_value = config.get("comfyui_path") or ""
    if not path_value:
        return {"error": "ComfyUI path not configured", "current_branch": None, "current_commit": None, "current_version": None}
    
    try:
        comfyui_path = Path(path_value).expanduser().resolve()
        if not comfyui_path.exists():
            return {"error": f"ComfyUI path does not exist: {comfyui_path}", "current_branch": None, "current_commit": None, "current_version": None}
        
        # Try to get git commit hash (short)
        current_commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=comfyui_path,
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
        
        # Try to get current branch
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=comfyui_path,
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
        
        # Try to get tag or version
        current_version = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            cwd=comfyui_path,
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
        
        return {
            "current_commit": current_commit or None,
            "current_branch": current_branch or None,
            "current_version": current_version or None,
            "error": None
        }
    except Exception as exc:
        return {
            "error": f"Failed to get ComfyUI version: {str(exc)}",
            "current_branch": None,
            "current_commit": None,
            "current_version": None
        }


def _comfy_get_object_info(node_type: str) -> dict:
    """Fetch ComfyUI node metadata for available options."""
    try:
        resp = requests.get(f"{COMFYUI_BASE_URL}/object_info/{node_type}", timeout=6)
        resp.raise_for_status()
        return resp.json() or {}
    except Exception as exc:
        logger.warning("Could not fetch ComfyUI object info for %s: %s", node_type, exc)
        return {}


def _image_samplers() -> list[str]:
    """Return sampler names from ComfyUI's KSampler metadata."""
    data = _comfy_get_object_info("KSampler")
    required = data.get("KSampler", {}).get("input", {}).get("required", {})
    names = required.get("sampler_name", [[]])
    if names and isinstance(names[0], list):
        return names[0]
    return ["euler", "euler_ancestral", "dpmpp_2m"]


def _image_schedulers() -> list[str]:
    """Return scheduler names from ComfyUI's KSampler metadata."""
    data = _comfy_get_object_info("KSampler")
    required = data.get("KSampler", {}).get("input", {}).get("required", {})
    names = required.get("scheduler", [[]])
    if names and isinstance(names[0], list) and names[0]:
        return names[0]
    return ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]


def _image_models() -> list[str]:
    """Return available checkpoint names from ComfyUI."""
    data = _comfy_get_object_info("CheckpointLoaderSimple")
    required = data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {})
    names = required.get("ckpt_name", [[]])
    if names and isinstance(names[0], list):
        return names[0]
    return []


def _infer_image_model_family(model_name: str) -> str:
    """Infer broad model family from checkpoint file naming conventions."""
    value = str(model_name or "").strip().lower()
    if not value:
        return "unknown"
    if "flux" in value:
        return "flux"
    if any(token in value for token in ("sdxl", "pony", "illustrious", "xl")):
        return "sdxl"
    if any(token in value for token in ("sd15", "1.5", "v1-5", "1_5")):
        return "sd15"
    return "unknown"


def _infer_flux_variant(model_name: str) -> str:
    """Infer Flux checkpoint variant from naming conventions."""
    value = str(model_name or "").strip().lower()
    if "flux" not in value:
        return ""
    if "schnell" in value or "flux.1-s" in value or "flux1-s" in value or "flux_1_s" in value:
        return "schnell"
    if "dev" in value or "flux.1-d" in value or "flux1-d" in value or "flux_1_d" in value:
        return "dev"
    return "dev"


def _image_model_capabilities(model_name: str) -> dict:
    """Return UI-facing capability flags for a checkpoint family."""
    family = _infer_image_model_family(model_name)
    flux_variant = _infer_flux_variant(model_name) if family == "flux" else ""
    is_flux = family == "flux"
    recommended_sampler = "euler" if is_flux else ""
    if not is_flux:
        recommended_scheduler = ""
    elif flux_variant == "schnell":
        recommended_scheduler = "simple"
    else:
        recommended_scheduler = "normal"
    # These flags drive frontend control visibility and payload shaping.
    return {
        "family": family,
        "flux_variant": flux_variant,
        "recommended_sampler": recommended_sampler,
        "recommended_scheduler": recommended_scheduler,
        "supports_refiner": not is_flux,
        "supports_vae": not is_flux,
        "supports_controlnet": not is_flux,
        "supports_hiresfix": not is_flux,
        "cfg_min": 1,
        "cfg_max": 10 if is_flux else 30,
        "cfg_default": 3.5 if is_flux else 7.0,
    }


def _image_lora_models() -> list[str]:
    """Return available LoRA names from ComfyUI."""
    data = _comfy_get_object_info("LoraLoader")
    required = data.get("LoraLoader", {}).get("input", {}).get("required", {})
    names = required.get("lora_name", [[]])
    if names and isinstance(names[0], list):
        return names[0]
    return []


def _image_controlnet_models() -> list[str]:
    """Return available ControlNet names from ComfyUI."""
    data = _comfy_get_object_info("ControlNetLoader")
    required = data.get("ControlNetLoader", {}).get("input", {}).get("required", {})
    names = required.get("control_net_name", [[]])
    if names and isinstance(names[0], list):
        return names[0]
    return []


def _image_vae_models() -> list[str]:
    """Return available VAE names from ComfyUI."""
    data = _comfy_get_object_info("VAELoader")
    required = data.get("VAELoader", {}).get("input", {}).get("required", {})
    names = required.get("vae_name", [[]])
    if names and isinstance(names[0], list):
        return names[0]
    return []


def _get_lora_tags(lora_name: str) -> list[str]:
    """Try to read trigger words for a LoRA from sidecar JSON metadata files."""
    shared = _resolve_shared_models_root_dir()
    search_dirs: list[Path] = []
    if shared:
        search_dirs.append(shared / "Lora")
    base = Path(lora_name).stem
    for search_dir in search_dirs:
        for ext in (".json", ".civitai.info", ".meta.json"):
            meta_path = search_dir / (base + ext)
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8", errors="replace"))
                    trained_words = (
                        meta.get("trainedWords")
                        or meta.get("trained_words")
                        or meta.get("tags")
                        or []
                    )
                    if isinstance(trained_words, list):
                        return [str(w) for w in trained_words if w]
                except Exception:
                    pass
    return []


def _clamp_float(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def _coerce_seed(value) -> int:
    if value in (None, "", -1):
        return randint(1, 2_147_483_647)
    try:
        seed = int(value)
    except (TypeError, ValueError):
        return randint(1, 2_147_483_647)
    if seed < 0:
        return randint(1, 2_147_483_647)
    return seed


def _ensure_history_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def _default_service_config() -> dict:
    return {
        "ollama_path": "",
        "comfyui_path": "",
        "shared_models_path": "",
        "civitai_api_key": "",
        "huggingface_api_key": "",
        "default_negative_prompt": "",
        "updated_at": "",
    }


def _service_config_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_service_config_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SERVICE_CONFIG_FILE.exists():
        SERVICE_CONFIG_FILE.write_text(
            json.dumps(_default_service_config(), ensure_ascii=True, indent=2),
            encoding="utf-8",
        )


def _service_log_path(service: str) -> Path:
    SERVICE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    return SERVICE_LOG_DIR / f"{service}.log"


def _append_service_log_marker(service: str, message: str) -> None:
    with _service_log_lock:
        path = _service_log_path(service)
        stamp = datetime.now(timezone.utc).isoformat()
        with path.open("a", encoding="utf-8", errors="replace") as fh:
            fh.write(f"\n[{stamp}] {message}\n")


def _read_service_log_tail(service: str, max_chars: int = 1800) -> str:
    with _service_log_lock:
        path = _service_log_path(service)
        if not path.exists():
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
    return text[-max_chars:].strip()


def _load_service_config() -> dict:
    _ensure_service_config_store()
    with _service_config_lock:
        try:
            raw = json.loads(SERVICE_CONFIG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Service config file was invalid JSON, resetting.")
            raw = _default_service_config()

        config = _default_service_config()
        if isinstance(raw, dict):
            config["ollama_path"] = str(raw.get("ollama_path") or "").strip()
            config["comfyui_path"] = str(raw.get("comfyui_path") or "").strip()
            config["shared_models_path"] = str(raw.get("shared_models_path") or "").strip()
            config["civitai_api_key"] = str(raw.get("civitai_api_key") or "").strip()
            config["huggingface_api_key"] = str(raw.get("huggingface_api_key") or "").strip()
            config["default_negative_prompt"] = str(raw.get("default_negative_prompt") or "").strip()
            config["updated_at"] = str(raw.get("updated_at") or "").strip()

        SERVICE_CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=True, indent=2), encoding="utf-8")
        return config


def _save_service_config(config: dict) -> dict:
    _ensure_service_config_store()
    sanitized = {
        "ollama_path": str(config.get("ollama_path") or "").strip(),
        "comfyui_path": str(config.get("comfyui_path") or "").strip(),
        "shared_models_path": str(config.get("shared_models_path") or "").strip(),
        "civitai_api_key": str(config.get("civitai_api_key") or "").strip(),
        "huggingface_api_key": str(config.get("huggingface_api_key") or "").strip(),
        "default_negative_prompt": str(config.get("default_negative_prompt") or "").strip(),
        "updated_at": _service_config_timestamp(),
    }

    shared_root_raw = sanitized["shared_models_path"]
    if shared_root_raw:
        shared_root = Path(shared_root_raw).expanduser()
        shared_root.mkdir(parents=True, exist_ok=True)
        for folder in ("StableDiffusion", "Lora", "VAE", "Embeddings", "ControlNet", "ESRGAN"):
            (shared_root / folder).mkdir(parents=True, exist_ok=True)

    with _service_config_lock:
        SERVICE_CONFIG_FILE.write_text(json.dumps(sanitized, ensure_ascii=True, indent=2), encoding="utf-8")
    return sanitized


def _normalize_service_name(name: str) -> str:
    value = (name or "").strip().lower()
    if value not in SERVICE_PORTS:
        raise ValueError("service must be 'ollama' or 'comfyui'")
    return value


def _normalize_path_picker_target(name: str) -> str:
    value = (name or "").strip().lower()
    if value not in {"ollama", "comfyui", "models"}:
        raise ValueError("service must be 'ollama', 'comfyui', or 'models'")
    return value


def _resolve_ollama_launch(path_value: str) -> tuple[list[str], Path | None]:
    candidate = Path(path_value).expanduser()
    if candidate.is_dir():
        exe_name = "ollama.exe" if os.name == "nt" else "ollama"
        exe_path = candidate / exe_name
        if not exe_path.exists():
            raise ValueError(f"Could not find {exe_name} in configured Ollama directory")
        return [str(exe_path), "serve"], candidate

    if candidate.is_file():
        return [str(candidate), "serve"], candidate.parent

    raise ValueError("Configured Ollama path does not exist")


def _resolve_comfyui_launch(path_value: str) -> tuple[list[str], Path | None]:
    candidate = Path(path_value).expanduser()
    comfy_args = ["--enable-cors-header", "*"]
    if candidate.is_dir():
        # Prefer ComfyUI's bundled launch scripts so it runs in the intended env.
        bat_candidates = ["run_nvidia_gpu.bat", "run_cpu.bat", "run.bat"]
        for bat_name in bat_candidates:
            bat_path = candidate / bat_name
            if bat_path.exists():
                return ["cmd", "/c", str(bat_path), *comfy_args], candidate

        main_py = candidate / "main.py"
        if main_py.exists():
            portable_python = candidate.parent / "python_embeded" / "python.exe"
            if os.name == "nt" and portable_python.exists():
                return [str(portable_python), str(main_py), *comfy_args], candidate
            return [sys.executable, str(main_py), *comfy_args], candidate

        raise ValueError("Configured ComfyUI directory must contain main.py or a run.bat script")

    if candidate.is_file():
        suffix = candidate.suffix.lower()
        if suffix == ".py":
            portable_python = candidate.parent.parent / "python_embeded" / "python.exe"
            if os.name == "nt" and portable_python.exists():
                return [str(portable_python), str(candidate), *comfy_args], candidate.parent
            return [sys.executable, str(candidate), *comfy_args], candidate.parent
        if suffix in {".bat", ".cmd"}:
            return ["cmd", "/c", str(candidate), *comfy_args], candidate.parent
        return [str(candidate)], candidate.parent

    raise ValueError("Configured ComfyUI path does not exist")


def _kill_process_on_port(port: int) -> bool:
    if os.name == "nt":
        script = (
            "$owners = Get-NetTCPConnection -State Listen -LocalPort "
            f"{port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; "
            "if (-not $owners) { 'NOT_FOUND'; exit 0 }; "
            "foreach ($id in $owners) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }; "
            "'STOPPED'"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        return "STOPPED" in (proc.stdout or "")

    try:
        find_proc = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}"],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
        pids = [line.strip() for line in (find_proc.stdout or "").splitlines() if line.strip()]
        if not pids:
            return False
        for pid in pids:
            subprocess.run(["kill", "-9", pid], timeout=4, check=False)
        return True
    except Exception:
        return False


def _spawn_service_process(
    service: str,
    command: list[str],
    cwd: Path | None = None,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.Popen:
    log_path = _service_log_path(service)
    log_fh = log_path.open("a", encoding="utf-8", errors="replace")
    env = os.environ.copy()
    if env_overrides:
        env.update({k: str(v) for k, v in env_overrides.items() if v is not None})
    kwargs = {
        "cwd": str(cwd) if cwd else None,
        "stdout": log_fh,
        "stderr": log_fh,
        "stdin": subprocess.DEVNULL,
        "start_new_session": True,
        "env": env,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        proc = subprocess.Popen(command, **kwargs)
    finally:
        log_fh.close()
    return proc


def _start_configured_service(service: str, config: dict) -> tuple[bool, str, int | None]:
    env_overrides: dict[str, str] = {}
    if service == "ollama":
        path_value = config.get("ollama_path") or ""
        if not path_value:
            raise ValueError("Set an Ollama install path in Configurations before launching.")
        command, cwd = _resolve_ollama_launch(path_value)
        shared_root_raw = str(config.get("shared_models_path") or "").strip()
        if shared_root_raw:
            shared_ollama = Path(shared_root_raw).expanduser() / "ollama"
            shared_ollama.mkdir(parents=True, exist_ok=True)
            env_overrides["OLLAMA_MODELS"] = str(shared_ollama)
    else:
        path_value = config.get("comfyui_path") or ""
        if not path_value:
            raise ValueError("Set a ComfyUI install path in Configurations before launching.")
        command, cwd = _resolve_comfyui_launch(path_value)

    proc = _spawn_service_process(service, command, cwd=cwd, env_overrides=env_overrides)
    _service_processes[service] = proc
    _append_service_log_marker(service, f"Launch command: {' '.join(command)}")
    _last_service_errors[service] = ""

    # If the process exits immediately, return a useful failure instead of a false "started" state.
    time.sleep(0.9)
    exit_code = proc.poll()
    if exit_code is not None:
        log_tail = _read_service_log_tail(service)
        _last_service_errors[service] = (
            f"{service} process exited immediately (code {exit_code})."
            + (f" Recent log output: {log_tail}" if log_tail else "")
        )
        raise RuntimeError(
            f"{service} process exited immediately (code {exit_code}). Verify configured path and runtime dependencies."
        )

    return True, "started", proc.pid


def _service_available(service: str) -> bool:
    return _ollama_available() if service == "ollama" else _comfy_available()


def _restart_flask_via_helper(port: int = 5000) -> int:
    """Launch a detached helper that restarts this Flask app on the target port."""
    script_path = Path(app.root_path) / "scripts" / "start_app.ps1"
    if not script_path.exists():
        raise FileNotFoundError(f"Missing restart helper script: {script_path}")

    if os.name == "nt":
        script_for_ps = str(script_path).replace("'", "''")
        ps_command = (
            f"Start-Sleep -Milliseconds 800; & '{script_for_ps}' -Port {int(port)}"
        )
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        proc = subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps_command,
            ],
            cwd=app.root_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True,
        )
        return proc.pid

    # Fallback for non-Windows environments.
    cmd = f"sleep 1; {shlex.quote(sys.executable)} {shlex.quote(str(Path(app.root_path) / 'app.py'))}"
    proc = subprocess.Popen(
        ["sh", "-lc", cmd],
        cwd=app.root_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )
    return proc.pid


def _pick_path_dialog(service: str, initial_path: str = "") -> str:
    """Open a native path picker dialog and return the selected path."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as exc:
        raise RuntimeError("Native file picker is unavailable in this environment") from exc

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    initial_dir = ""
    if initial_path:
        p = Path(initial_path).expanduser()
        if p.is_dir():
            initial_dir = str(p)
        elif p.parent.exists():
            initial_dir = str(p.parent)

    try:
        if service == "ollama":
            selected = filedialog.askopenfilename(
                title="Select Ollama executable",
                initialdir=initial_dir or None,
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            )
        elif service == "models":
            selected = filedialog.askdirectory(
                title="Select shared model root folder",
                initialdir=initial_dir or None,
                mustexist=False,
            )
        else:
            selected = filedialog.askdirectory(
                title="Select ComfyUI folder",
                initialdir=initial_dir or None,
                mustexist=True,
            )
        return (selected or "").strip()
    finally:
        root.destroy()


def _load_history() -> list[dict]:
    _ensure_history_store()
    with _history_lock:
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("History file was invalid JSON, resetting.")
            HISTORY_FILE.write_text("[]", encoding="utf-8")
            return []


def _save_history(items: list[dict]) -> None:
    _ensure_history_store()
    with _history_lock:
        HISTORY_FILE.write_text(json.dumps(items, ensure_ascii=True, indent=2), encoding="utf-8")


def _model_metadata_path() -> Path:
    return DATA_DIR / "model_metadata.json"


def _ensure_model_metadata_store() -> None:
    path = _model_metadata_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")


def _load_model_metadata() -> dict[str, dict]:
    _ensure_model_metadata_store()
    path = _model_metadata_path()
    with _model_metadata_lock:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, dict) else {}
        except json.JSONDecodeError:
            logger.warning("Model metadata store was invalid JSON, resetting.")
            path.write_text("{}", encoding="utf-8")
            return {}


def _save_model_metadata(items: dict[str, dict]) -> None:
    _ensure_model_metadata_store()
    path = _model_metadata_path()
    with _model_metadata_lock:
        path.write_text(json.dumps(items, ensure_ascii=True, indent=2), encoding="utf-8")


def _sanitize_optional_preview_url(value: str) -> str:
    url = str(value or "").strip()
    if not url:
        return ""
    if url.startswith("/"):
        return url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return ""


def _sanitize_preview_urls(values) -> list[str]:
    urls: list[str] = []
    if not isinstance(values, list):
        return urls
    for value in values:
        cleaned = _sanitize_optional_preview_url(value)
        if cleaned and cleaned not in urls:
            urls.append(cleaned)
    return urls


def _extract_preview_urls_from_images(images: list[dict]) -> list[str]:
    urls: list[str] = []
    for image in images or []:
        if not isinstance(image, dict):
            continue
        cleaned = _sanitize_optional_preview_url(image.get("url") or "")
        if cleaned and cleaned not in urls:
            urls.append(cleaned)
    return urls


def _upsert_model_download_metadata(file_name: str, folder: str, body: dict, provider: str, model_id: str) -> None:
    key = f"{str(folder or '').strip().lower()}/{str(file_name or '').strip().lower()}"
    if not key.strip("/"):
        return

    metadata_map = _load_model_metadata()
    existing = metadata_map.get(key) if isinstance(metadata_map.get(key), dict) else {}
    preview_from_body = _sanitize_optional_preview_url(body.get("preview_url") or "")
    preview_from_existing = _sanitize_optional_preview_url(existing.get("preview_url") or "")
    preview_urls_from_body = _sanitize_preview_urls(body.get("preview_urls") or [])
    preview_urls_from_existing = _sanitize_preview_urls(existing.get("preview_urls") or [])
    merged_preview_urls = preview_urls_from_body or preview_urls_from_existing
    if preview_from_body and preview_from_body not in merged_preview_urls:
        merged_preview_urls.insert(0, preview_from_body)
    if not preview_from_body and preview_from_existing and preview_from_existing not in merged_preview_urls:
        merged_preview_urls.insert(0, preview_from_existing)

    def _pick_value(new_value: str, fallback_value: str) -> str:
        new_text = str(new_value or "").strip()
        return new_text if new_text else str(fallback_value or "").strip()

    metadata_map[key] = {
        "file_name": _pick_value(file_name, existing.get("file_name") or ""),
        "folder": _pick_value(folder, existing.get("folder") or ""),
        "provider": _pick_value(provider, existing.get("provider") or ""),
        "model_id": _pick_value(model_id or body.get("model_id") or "", existing.get("model_id") or ""),
        "model_name": _pick_value(body.get("model_name") or "", existing.get("model_name") or ""),
        "version_name": _pick_value(body.get("version_name") or "", existing.get("version_name") or ""),
        "model_type": _pick_value(body.get("model_type") or "", existing.get("model_type") or ""),
        "base_model": _pick_value(body.get("base_model") or "", existing.get("base_model") or ""),
        "model_url": _pick_value(body.get("model_url") or "", existing.get("model_url") or ""),
        "preview_url": preview_from_body or preview_from_existing,
        "preview_urls": merged_preview_urls,
        "updated_at": int(time.time()),
    }
    _save_model_metadata(metadata_map)


def _lookup_model_download_metadata(metadata_map: dict[str, dict], file_name: str, folder: str) -> dict:
    key = f"{str(folder or '').strip().lower()}/{str(file_name or '').strip().lower()}"
    exact = metadata_map.get(key)
    if isinstance(exact, dict):
        return exact

    file_name_lc = str(file_name or "").strip().lower()
    if not file_name_lc:
        return {}
    for item in metadata_map.values():
        if not isinstance(item, dict):
            continue
        if str(item.get("file_name") or "").strip().lower() == file_name_lc:
            return item
    return {}


def _is_civitai_video_preview(image: dict) -> bool:
    """Return True if a CivitAI image dict is a video (not usable as <img> src)."""
    img_type = str(image.get("type") or "").strip().lower()
    url = str(image.get("url") or "").strip().lower()
    return img_type == "video" or any(url.endswith(ext) for ext in (".mp4", ".webm", ".mov", ".avi"))


def _pick_civitai_preview_url(images: list[dict]) -> str:
    """Pick a safer preview URL from CivitAI image payloads with a practical fallback."""
    safe = []
    fallback = []
    for image in images or []:
        url = str(image.get("url") or "").strip()
        if not url:
            continue
        if _is_civitai_video_preview(image):
            continue
        fallback.append(url)
        nsfw_flag = image.get("nsfw")
        nsfw_level = image.get("nsfwLevel")
        is_safe_flag = nsfw_flag is False
        is_safe_level = False
        if nsfw_level is not None:
            try:
                is_safe_level = int(nsfw_level) <= 1
            except (TypeError, ValueError):
                is_safe_level = False
        if is_safe_flag or is_safe_level:
            safe.append(url)
    if safe:
        return safe[0]
    return fallback[0] if fallback else ""


def _normalized_name_for_match(value: str) -> str:
    value = str(value or "").strip().lower()
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "", value)


def _candidate_name_matches_local_file(local_file_name: str, *candidate_names: str) -> bool:
    local_file_name = str(local_file_name or "").strip()
    if not local_file_name:
        return False

    local_file_name_lc = local_file_name.lower()
    local_stem_lc = Path(local_file_name).stem.lower()
    normalized_local_file = _normalized_name_for_match(local_file_name_lc)
    normalized_local_stem = _normalized_name_for_match(local_stem_lc)

    for candidate_name in candidate_names:
        candidate_text = str(candidate_name or "").strip()
        if not candidate_text:
            continue
        candidate_name_lc = Path(candidate_text).name.lower()
        candidate_stem_lc = Path(candidate_name_lc).stem.lower()
        if candidate_name_lc == local_file_name_lc or candidate_stem_lc == local_stem_lc:
            return True

        normalized_values = {
            _normalized_name_for_match(candidate_text),
            _normalized_name_for_match(candidate_name_lc),
            _normalized_name_for_match(candidate_stem_lc),
        }
        normalized_values.discard("")
        if normalized_local_file in normalized_values or normalized_local_stem in normalized_values:
            return True
    return False


def _score_local_metadata_candidate(
    local_file_name: str,
    *,
    file_candidate: str = "",
    version_name: str = "",
    model_name: str = "",
    query_index: int = 0,
    type_bonus: int = 0,
) -> int:
    """Score candidate confidence so compare prefers the strongest metadata match."""
    local_file_name_lc = str(local_file_name or "").strip().lower()
    local_stem_lc = Path(local_file_name_lc).stem
    local_norm = _normalized_name_for_match(local_stem_lc)

    score = 0
    score += max(0, 4 - max(0, int(query_index)))
    score += max(0, int(type_bonus))

    candidate_name_lc = Path(str(file_candidate or "").strip().lower()).name
    candidate_stem_lc = Path(candidate_name_lc).stem if candidate_name_lc else ""
    candidate_norm = _normalized_name_for_match(candidate_stem_lc)

    if candidate_name_lc and candidate_name_lc == local_file_name_lc:
        score += 120
    elif candidate_stem_lc and candidate_stem_lc == local_stem_lc:
        score += 100
    elif local_norm and candidate_norm and (candidate_norm in local_norm or local_norm in candidate_norm):
        score += 70

    normalized_version = _normalized_name_for_match(version_name)
    if normalized_version and local_norm and normalized_version in local_norm:
        score += 24

    normalized_model_name = _normalized_name_for_match(model_name)
    if normalized_model_name and local_norm:
        if normalized_model_name in local_norm:
            score += 32
        elif local_norm in normalized_model_name:
            score += 20

    return score


def _build_local_model_query_candidates(file_name: str) -> list[str]:
    raw_name = Path(str(file_name or "").strip()).name
    raw_stem = Path(raw_name).stem.strip()
    spaced_stem = re.sub(r"[_\-.]+", " ", raw_stem).strip()
    stripped_stem = re.sub(r"(?i)(?:[-_. ]v\d+(?:\.\d+)*)$", "", raw_stem).strip("-_. ")
    stripped_spaced_stem = re.sub(r"[_\-.]+", " ", stripped_stem).strip()

    candidates: list[str] = []
    for candidate in [raw_stem, raw_name, spaced_stem, stripped_stem, stripped_spaced_stem]:
        text = str(candidate or "").strip()
        if not text or text in candidates:
            continue
        candidates.append(text)
    return candidates


def _sidecar_metadata_candidates_for_model_file(model_path: Path) -> list[Path]:
    """Return likely sidecar metadata files adjacent to a model file."""
    stem = model_path.stem
    parent = model_path.parent
    return [
        parent / f"{stem}.civitai.info",
        parent / f"{stem}.json",
    ]


def _extract_local_sidecar_model_metadata(model_path: Path) -> dict:
    """Extract best-effort model metadata from adjacent sidecar files."""
    model_name = model_path.name
    model_stem = model_path.stem

    def extract_payload_metadata(payload: dict, is_fallback: bool = False) -> dict:
        if not isinstance(payload, dict):
            return {}

        model_id = str(payload.get("modelId") or payload.get("model_id") or payload.get("id") or "").strip()
        model_name_field = str(payload.get("name") or payload.get("modelName") or "").strip()
        version_name = str(payload.get("modelVersionName") or payload.get("versionName") or payload.get("version") or "").strip()
        model_type = str(payload.get("type") or payload.get("modelType") or "").strip()
        base_model = str(payload.get("baseModel") or payload.get("base_model") or "").strip()
        model_url = str(payload.get("modelUrl") or payload.get("model_url") or "").strip()
        if not model_url and model_id:
            model_url = f"https://civitai.com/models/{model_id}"

        images = payload.get("images") or payload.get("modelImages") or []
        if not isinstance(images, list):
            images = []
        preview_url = _pick_civitai_preview_url(images)
        preview_urls = _extract_preview_urls_from_images(images)

        if is_fallback and not (model_id or model_name_field or preview_url or model_url):
            return {}

        return {
            "provider": "civitai" if (model_id or model_url or preview_url) else "",
            "model_id": model_id,
            "model_name": model_name_field,
            "version_name": version_name,
            "model_type": model_type,
            "base_model": base_model,
            "model_url": model_url,
            "preview_url": _sanitize_optional_preview_url(preview_url),
            "preview_urls": preview_urls,
        }

    def payload_matches_model_file(payload: dict) -> bool:
        files = payload.get("files") or payload.get("modelFiles") or []
        for file_obj in files or []:
            if isinstance(file_obj, str):
                candidate = file_obj
            elif isinstance(file_obj, dict):
                candidate = str(file_obj.get("name") or file_obj.get("fileName") or file_obj.get("filename") or "")
            else:
                candidate = ""
            candidate = candidate.strip()
            if not candidate:
                continue
            candidate_name = Path(candidate).name.lower()
            if candidate_name == model_name.lower() or Path(candidate_name).stem == model_stem.lower():
                return True
        return False

    inspected: list[Path] = []
    for candidate in _sidecar_metadata_candidates_for_model_file(model_path):
        if not candidate.is_file():
            continue
        inspected.append(candidate.resolve())
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload_matches_model_file(payload):
            return extract_payload_metadata(payload)
        meta = extract_payload_metadata(payload, is_fallback=True)
        if meta:
            return meta

    # Broader fallback for repos where sidecar file naming does not match local file naming.
    for candidate in sorted(model_path.parent.glob("*.civitai.info")):
        resolved = candidate.resolve()
        if resolved in inspected:
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload_matches_model_file(payload):
            return extract_payload_metadata(payload)
    return {}


def _find_civitai_match_for_local_file(item: dict) -> dict:
    """Find best-effort CivitAI metadata match for a local model file."""
    file_name = str(item.get("name") or "").strip()
    model_type = str(item.get("type") or "").strip()
    if not file_name:
        return {}

    query_candidates = _build_local_model_query_candidates(file_name)
    if not query_candidates:
        return {}

    best_match: dict = {}
    best_score = -1

    for query_index, query in enumerate(query_candidates):
        type_candidates = [model_type] if model_type in _CIVITAI_MODEL_TYPES else []
        type_candidates.append("")
        for type_candidate in type_candidates:
            params: dict[str, str | int] = {
                "query": query,
                "limit": 8,
                "sort": "Highest Rated",
                "nsfw": "false",
            }
            if type_candidate:
                params["types"] = type_candidate

            resp = requests.get(
                f"{_CIVITAI_API}/models",
                params=params,
                headers=_external_api_headers("civitai"),
                timeout=15,
            )
            resp.raise_for_status()
            raw = resp.json() or {}
            items = raw.get("items") or []
            if not items:
                continue

            for model in items:
                model_name = str(model.get("name") or "").strip()
                versions = model.get("modelVersions") or []
                for version in versions:
                    version_name = str(version.get("name") or "").strip()
                    files = version.get("files") or []
                    combined_names = []
                    if model_name and version_name:
                        combined_names.extend([
                            f"{model_name} {version_name}",
                            f"{version_name} {model_name}",
                        ])
                    for file_obj in files:
                        candidate_name = str(file_obj.get("name") or "").strip()
                        if not candidate_name:
                            continue
                        if not _candidate_name_matches_local_file(
                            file_name,
                            candidate_name,
                            version_name,
                            model_name,
                            *combined_names,
                        ):
                            continue
                        model_id = str(model.get("id") or "").strip()
                        preview_url = _pick_civitai_preview_url(version.get("images") or model.get("images") or [])
                        type_bonus = 12 if type_candidate and str(model.get("type") or "").strip() == type_candidate else 0
                        score = _score_local_metadata_candidate(
                            file_name,
                            file_candidate=candidate_name,
                            version_name=version_name,
                            model_name=model_name,
                            query_index=query_index,
                            type_bonus=type_bonus,
                        )
                        if score <= best_score:
                            continue
                        best_score = score
                        best_match = {
                            "provider": "civitai",
                            "model_id": model_id,
                            "model_name": model_name,
                            "version_name": version_name,
                            "model_type": str(model.get("type") or model_type).strip(),
                            "base_model": str(version.get("baseModel") or "").strip(),
                            "model_url": str(model.get("url") or f"https://civitai.com/models/{model_id}").strip(),
                            "preview_url": preview_url,
                        }
    return best_match


def _find_huggingface_match_for_local_file(item: dict) -> dict:
    """Find best-effort Hugging Face metadata match for a local model file."""
    file_name = str(item.get("name") or "").strip()
    if not file_name:
        return {}

    query_candidates = _build_local_model_query_candidates(file_name)
    if not query_candidates:
        return {}

    best_match: dict = {}
    best_score = -1

    for query_index, query in enumerate(query_candidates):
        resp = requests.get(
            f"{_HUGGINGFACE_API}/models",
            params={
                "search": query,
                "limit": 12,
                "full": "true",
                "sort": "downloads",
                "direction": -1,
            },
            headers=_external_api_headers("huggingface"),
            timeout=20,
        )
        resp.raise_for_status()
        raw_items = resp.json() or []

        for model in raw_items:
            model_id = str(model.get("id") or "").strip()
            version_name = str(model.get("sha") or "")[:8] if model.get("sha") else ""
            model_short_name = model_id.split("/")[-1] if model_id else ""
            combined_names = []
            if model_short_name and version_name:
                combined_names.extend([
                    f"{model_short_name} {version_name}",
                    f"{version_name} {model_short_name}",
                ])
            siblings = model.get("siblings") or []
            for sibling in siblings:
                candidate_name = str(sibling.get("rfilename") or "").strip()
                candidate_basename = Path(candidate_name).name
                if not candidate_basename or not _is_huggingface_model_file(candidate_basename):
                    continue
                if not _candidate_name_matches_local_file(
                    file_name,
                    candidate_basename,
                    model_short_name,
                    model_id,
                    version_name,
                    *combined_names,
                ):
                    continue

                card_data = model.get("cardData") or {}
                preview_url = _sanitize_optional_preview_url(
                    model.get("thumbnail")
                    or model.get("thumbnailUrl")
                    or model.get("preview_url")
                    or ""
                )
                score = _score_local_metadata_candidate(
                    file_name,
                    file_candidate=candidate_basename,
                    version_name=version_name,
                    model_name=model_short_name,
                    query_index=query_index,
                )
                if score <= best_score:
                    continue
                best_score = score
                best_match = {
                    "provider": "huggingface",
                    "model_id": model_id,
                    "model_name": model_id,
                    "version_name": version_name,
                    "model_type": _infer_huggingface_model_type(model),
                    "base_model": str(card_data.get("base_model") or card_data.get("baseModel") or "").strip(),
                    "model_url": f"https://huggingface.co/{model_id}" if model_id else "",
                    "preview_url": preview_url,
                }
    return best_match


def _compare_local_model_metadata_with_providers(
    limit: int = 80,
    providers: list[str] | None = None,
    overwrite: bool = False,
) -> dict:
    """Backfill missing metadata for local models by comparing names across providers."""
    models = _scan_local_models()
    metadata_map = _load_model_metadata()
    allowed_providers = {"civitai", "huggingface"}
    provider_order = [
        provider
        for provider in [str(p).strip().lower() for p in (providers or ["civitai", "huggingface"])]
        if provider in allowed_providers
    ]
    if not provider_order:
        provider_order = ["civitai", "huggingface"]

    updated = 0
    skipped = 0
    failed = 0
    scanned = 0
    skip_reasons: dict[str, int] = {
        "already_has_metadata": 0,
        "missing_folder_or_name": 0,
        "no_provider_match": 0,
    }
    failure_reasons: dict[str, int] = {
        "request_error": 0,
    }
    matched_by_provider: dict[str, int] = {
        "civitai": 0,
        "huggingface": 0,
    }
    updated_samples: list[dict[str, str]] = []
    skipped_samples: list[dict[str, str]] = []
    failed_samples: list[dict[str, str]] = []

    def _remember_sample(sample_list: list, sample: dict[str, str], cap: int = 8) -> None:
        if len(sample_list) < cap:
            sample_list.append(sample)

    def _has_missing_metadata(item: dict, existing: dict) -> bool:
        provider_value = str(existing.get("provider") or item.get("provider") or "").strip()
        model_id_value = str(existing.get("model_id") or item.get("model_id") or "").strip()
        version_name_value = str(existing.get("version_name") or item.get("version_name") or "").strip()
        model_url_value = str(existing.get("model_url") or item.get("model_url") or "").strip()
        model_type_value = str(existing.get("model_type") or item.get("type") or "").strip()
        base_model_value = str(existing.get("base_model") or item.get("base_model") or "").strip()
        preview_value = _sanitize_optional_preview_url(existing.get("preview_url") or item.get("preview_url") or "")
        return not (provider_value and model_id_value and version_name_value and model_url_value and model_type_value and base_model_value and preview_value)

    for item in models:
        if scanned >= max(1, int(limit)):
            break

        folder = str(item.get("folder") or "").strip()
        file_name = str(item.get("name") or "").strip()
        if not folder or not file_name:
            skipped += 1
            skip_reasons["missing_folder_or_name"] += 1
            _remember_sample(skipped_samples, {"file": file_name or "<unknown>", "reason": "missing_folder_or_name"})
            continue

        existing = _lookup_model_download_metadata(metadata_map, file_name, folder)
        if not overwrite and not _has_missing_metadata(item, existing):
            skipped += 1
            skip_reasons["already_has_metadata"] += 1
            _remember_sample(skipped_samples, {"file": file_name, "reason": "already_has_metadata"})
            continue

        scanned += 1
        match: dict = {}
        matched_provider = ""
        request_errors: list[str] = []

        for provider in provider_order:
            try:
                if provider == "civitai":
                    candidate = _find_civitai_match_for_local_file(item)
                elif provider == "huggingface":
                    candidate = _find_huggingface_match_for_local_file(item)
                else:
                    candidate = {}
            except requests.RequestException as exc:
                request_errors.append(f"{provider}: {exc}")
                continue

            if candidate:
                match = candidate
                matched_provider = provider
                break

        if not match:
            if request_errors:
                failed += 1
                failure_reasons["request_error"] += 1
                _remember_sample(
                    failed_samples,
                    {
                        "file": file_name,
                        "reason": "request_error",
                        "error": request_errors[0],
                    },
                )
            else:
                skipped += 1
                skip_reasons["no_provider_match"] += 1
                _remember_sample(skipped_samples, {"file": file_name, "reason": "no_provider_match"})
            continue

        _upsert_model_download_metadata(
            file_name=file_name,
            folder=folder,
            body=match,
            provider=matched_provider,
            model_id=str(match.get("model_id") or ""),
        )
        updated += 1
        matched_by_provider[matched_provider] = matched_by_provider.get(matched_provider, 0) + 1
        _remember_sample(
            updated_samples,
            {
                "file": f"{folder}/{file_name}",
                "provider": matched_provider,
                "version_name": str(match.get("version_name") or "").strip(),
            },
        )

    return {
        "scanned": scanned,
        "updated": updated,
        "skipped": skipped,
        "failed": failed,
        "providers": provider_order,
        "skip_reasons": skip_reasons,
        "failure_reasons": failure_reasons,
        "matched_by_provider": matched_by_provider,
        "updated_samples": updated_samples,
        "skipped_samples": skipped_samples,
        "failed_samples": failed_samples,
    }


def _enrich_local_model_metadata_with_civitai(limit: int = 40) -> dict:
    """Backfill missing local model metadata by querying CivitAI using local filenames."""
    models = _scan_local_models()
    metadata_map = _load_model_metadata()

    updated = 0
    skipped = 0
    failed = 0
    scanned = 0
    skip_reasons: dict[str, int] = {
        "already_has_preview": 0,
        "missing_folder_or_name": 0,
        "no_civitai_match": 0,
    }
    failure_reasons: dict[str, int] = {
        "request_error": 0,
    }
    updated_samples: list[str] = []
    skipped_samples: list[dict[str, str]] = []
    failed_samples: list[dict[str, str]] = []

    def _remember_sample(sample_list: list, sample: str | dict[str, str], cap: int = 8) -> None:
        if len(sample_list) < cap:
            sample_list.append(sample)

    for item in models:
        if scanned >= max(1, int(limit)):
            break
        if str(item.get("preview_url") or "").strip():
            skipped += 1
            skip_reasons["already_has_preview"] += 1
            sample_name = str(item.get("name") or "").strip()
            if sample_name:
                _remember_sample(skipped_samples, {"file": sample_name, "reason": "already_has_preview"})
            continue

        folder = str(item.get("folder") or "").strip()
        file_name = str(item.get("name") or "").strip()
        if not folder or not file_name:
            skipped += 1
            skip_reasons["missing_folder_or_name"] += 1
            _remember_sample(skipped_samples, {"file": file_name or "<unknown>", "reason": "missing_folder_or_name"})
            continue

        scanned += 1
        try:
            match = _find_civitai_match_for_local_file(item)
        except requests.RequestException as exc:
            logger.warning("CivitAI enrichment failed for %s: %s", file_name, exc)
            failed += 1
            failure_reasons["request_error"] += 1
            _remember_sample(failed_samples, {"file": file_name, "reason": "request_error", "error": str(exc)})
            continue

        if not match:
            skipped += 1
            skip_reasons["no_civitai_match"] += 1
            _remember_sample(skipped_samples, {"file": file_name, "reason": "no_civitai_match"})
            continue

        _upsert_model_download_metadata(
            file_name=file_name,
            folder=folder,
            body=match,
            provider="civitai",
            model_id=str(match.get("model_id") or ""),
        )
        updated += 1
        _remember_sample(updated_samples, f"{folder}/{file_name}")

    return {
        "scanned": scanned,
        "updated": updated,
        "skipped": skipped,
        "failed": failed,
        "skip_reasons": skip_reasons,
        "failure_reasons": failure_reasons,
        "updated_samples": updated_samples,
        "skipped_samples": skipped_samples,
        "failed_samples": failed_samples,
    }


def _history_image_key(item: dict) -> tuple[str, str, tuple[tuple[str, str, str], ...]] | None:
    """Return the dedupe key for persisted image history entries."""
    if item.get("type") != "image":
        return None
    params = item.get("params") if isinstance(item.get("params"), dict) else {}
    prompt_id = str(params.get("prompt_id") or "").strip()
    image_sig = _image_refs_signature(item.get("images") or [])
    if not prompt_id or not image_sig:
        return None
    return ("image", prompt_id, image_sig)


def _image_refs_signature(images: list[dict]) -> tuple[tuple[str, str, str], ...]:
    """Create a stable signature for generated image references."""
    refs: list[tuple[str, str, str]] = []
    for image in images or []:
        filename = (image.get("filename") or "").strip()
        if not filename:
            continue
        refs.append(
            (
                filename,
                (image.get("subfolder") or "").strip(),
                (image.get("type") or "output").strip(),
            )
        )
    return tuple(sorted(refs))


def _history_entry_score(item: dict) -> int:
    """Score how useful a history entry is so richer duplicates win."""
    score = 0
    prompt = (item.get("prompt") or "").strip()
    if prompt and prompt.lower() != "image generation":
        score += 4

    negative_prompt = (item.get("negative_prompt") or "").strip()
    if negative_prompt:
        score += 1

    engine = (item.get("engine") or "").strip()
    if engine:
        score += 1

    model = (item.get("model") or "").strip()
    if model:
        score += 4

    params = item.get("params") if isinstance(item.get("params"), dict) else {}
    if (params.get("sampler") or "").strip():
        score += 2
    if params.get("seed") not in (None, ""):
        score += 1
    if params.get("steps") not in (None, "", 0):
        score += 2
    if params.get("cfg") not in (None, "", 0):
        score += 2
    if params.get("denoise") not in (None, "", 0):
        score += 1
    if params.get("width") not in (None, "", 0):
        score += 1
    if params.get("height") not in (None, "", 0):
        score += 1
    if params.get("batch_size") not in (None, ""):
        score += 1
    if (params.get("mode") or "").strip():
        score += 1

    if item.get("response"):
        score += 1

    score += len(_image_refs_signature(item.get("images") or []))
    return score


def _merge_preferred_history_entry(existing: dict, candidate: dict) -> dict:
    """Keep the entry with richer metadata while preserving the existing history slot."""
    if _history_entry_score(candidate) <= _history_entry_score(existing):
        return existing
    return {
        **existing,
        **candidate,
        "id": existing.get("id") or candidate.get("id"),
        "created_at": existing.get("created_at") or candidate.get("created_at"),
    }


def _dedupe_history_entries(entries: list[dict]) -> list[dict]:
    """Remove duplicate image-history rows while preserving the best metadata."""
    deduped: list[dict] = []
    key_to_index: dict[tuple[str, str, tuple[tuple[str, str, str], ...]], int] = {}

    for entry in entries:
        key = _history_image_key(entry)
        if not key:
            deduped.append(entry)
            continue

        existing_index = key_to_index.get(key)
        if existing_index is None:
            key_to_index[key] = len(deduped)
            deduped.append(entry)
            continue

        deduped[existing_index] = _merge_preferred_history_entry(deduped[existing_index], entry)

    return deduped


def _append_history(item: dict) -> dict:
    entries = _load_history()

    duplicate_key = _history_image_key(item)
    if duplicate_key:
        for index, existing in enumerate(entries):
            if _history_image_key(existing) != duplicate_key:
                continue
            merged = _merge_preferred_history_entry(existing, item)
            if merged != existing:
                entries[index] = merged
                _save_history(entries[:300])
            return merged

    entry = {
        "id": f"h_{int(time.time() * 1000)}",
        "created_at": int(time.time()),
        **item,
    }
    entries.insert(0, entry)
    _save_history(entries[:300])
    return entry


def _comfy_submit_prompt(workflow: dict, *, front: bool = False) -> dict:
    """Submit a workflow prompt to ComfyUI and return the raw JSON response."""
    payload = {"prompt": workflow}
    if front:
        payload["front"] = True
    resp = requests.post(
        f"{COMFYUI_BASE_URL}/prompt",
        json=payload,
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def _comfy_history(prompt_id: str) -> dict:
    """Fetch prompt history payload from ComfyUI."""
    resp = requests.get(f"{COMFYUI_BASE_URL}/history/{prompt_id}", timeout=20)
    resp.raise_for_status()
    return resp.json() or {}


def _parse_prompt_images(prompt_id: str) -> list[dict]:
    """Extract generated image references from ComfyUI history format."""
    data = _comfy_history(prompt_id)
    payload = data.get(prompt_id, {})
    outputs = payload.get("outputs", {})
    images: list[dict] = []
    for output in outputs.values():
        for image in output.get("images", []):
            filename = image.get("filename")
            if not filename:
                continue
            images.append(
                {
                    "filename": filename,
                    "subfolder": image.get("subfolder", ""),
                    "type": image.get("type", "output"),
                }
            )
    return images


def _parse_prompt_source_image(prompt_id: str) -> str:
    """Extract the primary img2img source image filename from ComfyUI history."""
    data = _comfy_history(prompt_id)
    payload = data.get(prompt_id, {})
    prompt_payload = payload.get("prompt")
    workflow = {}
    if isinstance(prompt_payload, dict):
        workflow = prompt_payload
    elif isinstance(prompt_payload, list) and len(prompt_payload) >= 3 and isinstance(prompt_payload[2], dict):
        # ComfyUI history commonly returns prompt as: [number, prompt_id, workflow, extra_data, outputs]
        workflow = prompt_payload[2]

    if not isinstance(workflow, dict):
        return ""

    for node in workflow.values():
        if not isinstance(node, dict):
            continue
        if node.get("class_type") != "LoadImage":
            continue
        inputs = node.get("inputs") or {}
        filename = str(inputs.get("image") or "").strip()
        if filename:
            return filename
    return ""


def _safe_child_path(base: Path, *parts: str) -> Path:
    """Resolve a child path and reject traversal outside the base directory."""
    base_resolved = base.resolve()
    candidate = base_resolved.joinpath(*parts).resolve()
    try:
        candidate.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError("Invalid image path reference") from exc
    return candidate


def _resolve_comfy_root_dir() -> Path | None:
    """Resolve a usable ComfyUI root directory from saved service config."""
    config = _load_service_config()
    raw_path = str(config.get("comfyui_path") or "").strip()
    if not raw_path:
        return None

    candidate = Path(raw_path).expanduser()
    if candidate.is_dir():
        return candidate
    if candidate.is_file():
        return candidate.parent
    return None


def _resolve_shared_models_root_dir() -> Path | None:
    """Resolve a shared model root directory from saved service config."""
    config = _load_service_config()
    raw_path = str(config.get("shared_models_path") or "").strip()
    if not raw_path:
        return None

    candidate = Path(raw_path).expanduser()
    if candidate.is_file():
        return None
    return candidate


def _migrate_shared_model_folders(dry_run: bool = False, progress_cb=None) -> dict:
    """Move legacy Comfy-style folder content into Stability Matrix-style shared folders."""
    shared_root = _resolve_shared_models_root_dir()
    if shared_root is None:
        raise ValueError("Set Shared Model Root Path in Configurations before running migration")

    shared_root.mkdir(parents=True, exist_ok=True)
    legacy_to_stability = {
        "checkpoints": "StableDiffusion",
        "loras": "Lora",
        "vae": "VAE",
        "embeddings": "Embeddings",
        "controlnet": "ControlNet",
        "upscale_models": "ESRGAN",
    }

    moved: list[dict] = []
    skipped: list[dict] = []
    errors: list[dict] = []
    processed_files = 0

    def _append_capped(items: list[dict], payload: dict, cap: int = 500) -> None:
        if len(items) < cap:
            items.append(payload)

    candidate_files: list[tuple[Path, Path, str, str]] = []
    for legacy_folder, target_folder in legacy_to_stability.items():
        src_dir = shared_root / legacy_folder
        dst_dir = shared_root / target_folder
        if not src_dir.exists() or not src_dir.is_dir():
            continue
        for src_file in src_dir.rglob("*"):
            if not src_file.is_file():
                continue
            rel_path = src_file.relative_to(src_dir)
            dest_file = dst_dir / rel_path
            src_rel = str(src_file.relative_to(shared_root)).replace("\\", "/")
            dest_rel = str(dest_file.relative_to(shared_root)).replace("\\", "/")
            candidate_files.append((src_file, dest_file, src_rel, dest_rel))

    total_files = len(candidate_files)
    if progress_cb:
        progress_cb(processed_files, total_files, len(moved), len(skipped), len(errors))

    for legacy_folder, target_folder in legacy_to_stability.items():
        src_dir = shared_root / legacy_folder
        dst_dir = shared_root / target_folder

        if not src_dir.exists() or not src_dir.is_dir():
            continue

        dst_dir.mkdir(parents=True, exist_ok=True)

        for src_file, dest_file, src_rel, dest_rel in [
            entry for entry in candidate_files if entry[2].startswith(f"{legacy_folder}/")
        ]:
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            if dest_file.exists():
                _append_capped(skipped, {
                    "source": src_rel,
                    "destination": dest_rel,
                    "reason": "destination exists",
                })
                processed_files += 1
                if progress_cb:
                    progress_cb(processed_files, total_files, len(moved), len(skipped), len(errors))
                continue

            if dry_run:
                _append_capped(moved, {"source": src_rel, "destination": dest_rel})
                processed_files += 1
                if progress_cb:
                    progress_cb(processed_files, total_files, len(moved), len(skipped), len(errors))
                continue

            try:
                src_file.replace(dest_file)
                _append_capped(moved, {"source": src_rel, "destination": dest_rel})
            except OSError as exc:
                _append_capped(errors, {
                    "source": src_rel,
                    "destination": dest_rel,
                    "error": str(exc),
                })
            processed_files += 1
            if progress_cb:
                progress_cb(processed_files, total_files, len(moved), len(skipped), len(errors))

        if dry_run:
            continue

        # Best-effort cleanup of emptied legacy folders.
        for entry in sorted(src_dir.rglob("*"), reverse=True):
            if entry.is_dir():
                try:
                    entry.rmdir()
                except OSError:
                    pass
        try:
            src_dir.rmdir()
        except OSError:
            pass

    return {
        "dry_run": dry_run,
        "root": str(shared_root),
        "total_files": total_files,
        "moved_count": len(moved),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "moved": moved,
        "skipped": skipped,
        "errors": errors,
    }


def _migration_job_snapshot(job: dict) -> dict:
    return {
        "id": job.get("id"),
        "status": job.get("status"),
        "dry_run": bool(job.get("dry_run")),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "error": job.get("error", ""),
        "progress": job.get("progress", {}),
        "result": job.get("result"),
    }


def _run_migration_job(job_id: str, dry_run: bool = False) -> None:
    def _on_progress(processed: int, total: int, moved: int, skipped: int, errors: int) -> None:
        with _migration_jobs_lock:
            job = _migration_jobs.get(job_id)
            if not job:
                return
            job["progress"] = {
                "processed_files": processed,
                "total_files": total,
                "moved_count": moved,
                "skipped_count": skipped,
                "error_count": errors,
            }

    try:
        result = _migrate_shared_model_folders(dry_run=dry_run, progress_cb=_on_progress)
        with _migration_jobs_lock:
            job = _migration_jobs.get(job_id)
            if job:
                job["status"] = "done"
                job["result"] = result
                job["finished_at"] = datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        with _migration_jobs_lock:
            job = _migration_jobs.get(job_id)
            if job:
                job["status"] = "error"
                job["error"] = str(exc)
                job["finished_at"] = datetime.now(timezone.utc).isoformat()


def _start_migration_job(dry_run: bool = False) -> dict:
    job_id = f"mig-{int(time.time() * 1000)}"
    job = {
        "id": job_id,
        "status": "running",
        "dry_run": dry_run,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": "",
        "error": "",
        "progress": {
            "processed_files": 0,
            "total_files": 0,
            "moved_count": 0,
            "skipped_count": 0,
            "error_count": 0,
        },
        "result": None,
    }
    with _migration_jobs_lock:
        _migration_jobs[job_id] = job

    threading.Thread(target=_run_migration_job, args=(job_id, dry_run), daemon=True).start()
    return _migration_job_snapshot(job)


def _comfyui_update_job_snapshot(job: dict) -> dict:
    """Return a serializable snapshot of a ComfyUI update job."""
    return {
        "id": job.get("id"),
        "status": job.get("status"),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "error": job.get("error", ""),
        "output": job.get("output", ""),
        "result": job.get("result"),
    }


def _run_comfyui_update_job(job_id: str) -> None:
    """Background thread that runs the ComfyUI git pull update."""
    config = _load_service_config()
    path_value = config.get("comfyui_path") or ""
    
    try:
        comfyui_path = Path(path_value).expanduser().resolve()
        if not comfyui_path.exists():
            raise ValueError(f"ComfyUI path does not exist: {comfyui_path}")
        
        # Before-update version
        before_version = _get_comfyui_version()
        
        # Run git pull
        result = subprocess.run(
            ["git", "pull"],
            cwd=comfyui_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + (f"\nError: {result.stderr}" if result.stderr else "")
        
        if result.returncode != 0:
            raise RuntimeError(f"git pull failed (exit code {result.returncode}): {result.stderr or result.stdout}")
        
        # After-update version
        after_version = _get_comfyui_version()
        
        with _comfyui_update_jobs_lock:
            job = _comfyui_update_jobs.get(job_id)
            if job:
                job["status"] = "done"
                job["output"] = output
                job["result"] = {
                    "before_version": before_version,
                    "after_version": after_version,
                    "success": True
                }
                job["finished_at"] = datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        with _comfyui_update_jobs_lock:
            job = _comfyui_update_jobs.get(job_id)
            if job:
                job["status"] = "error"
                job["error"] = str(exc)
                job["finished_at"] = datetime.now(timezone.utc).isoformat()


def _start_comfyui_update_job() -> dict:
    """Create and start a background ComfyUI update job."""
    job_id = f"update-{int(time.time() * 1000)}"
    job = {
        "id": job_id,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": "",
        "error": "",
        "output": "",
        "result": None,
    }
    with _comfyui_update_jobs_lock:
        _comfyui_update_jobs[job_id] = job
    
    threading.Thread(target=_run_comfyui_update_job, args=(job_id,), daemon=True).start()
    return _comfyui_update_job_snapshot(job)


def _normalize_image_ref(body: dict) -> dict:
    """Extract a stable image reference payload from request JSON."""
    return {
        "filename": str(body.get("filename") or "").strip(),
        "subfolder": str(body.get("subfolder") or "").strip(),
        "type": str(body.get("type") or "output").strip(),
    }


def _resolve_comfy_image_path(image_ref: dict) -> Path:
    """Resolve an image ref (filename/subfolder/type) into a local ComfyUI file path."""
    filename = str(image_ref.get("filename") or "").strip()
    subfolder = str(image_ref.get("subfolder") or "").strip().replace("\\", "/")
    image_type = str(image_ref.get("type") or "output").strip().lower()

    if not filename:
        raise ValueError("filename is required")
    if Path(filename).name != filename:
        raise ValueError("filename must not include path separators")

    type_dir = {
        "output": "output",
        "input": "input",
        "temp": "temp",
    }.get(image_type)
    if not type_dir:
        raise ValueError("type must be one of: output, input, temp")

    comfy_root = _resolve_comfy_root_dir()
    if comfy_root is None:
        raise ValueError("Set a ComfyUI path in Configurations before using gallery file actions")

    subfolder_parts = [part for part in subfolder.split("/") if part and part != "."]
    return _safe_child_path(comfy_root, type_dir, *subfolder_parts, filename)


def _image_ref_matches(item: dict, image_ref: dict) -> bool:
    """Return True when history image reference equals the target image ref."""
    return (
        str(item.get("filename") or "").strip() == str(image_ref.get("filename") or "").strip()
        and str(item.get("subfolder") or "").strip() == str(image_ref.get("subfolder") or "").strip()
        and str(item.get("type") or "output").strip() == str(image_ref.get("type") or "output").strip()
    )


def _prune_history_image_references(image_ref: dict) -> tuple[int, int]:
    """Remove image references from local history and drop empty image entries."""
    entries = _load_history()
    removed_refs = 0
    removed_entries = 0
    next_entries: list[dict] = []

    for entry in entries:
        if entry.get("type") != "image":
            next_entries.append(entry)
            continue

        images = entry.get("images") if isinstance(entry.get("images"), list) else []
        filtered_images = [img for img in images if not _image_ref_matches(img, image_ref)]
        diff = len(images) - len(filtered_images)
        if diff <= 0:
            next_entries.append(entry)
            continue

        removed_refs += diff
        if not filtered_images:
            removed_entries += 1
            continue

        next_entries.append({**entry, "images": filtered_images})

    if removed_refs:
        _save_history(next_entries)

    return removed_refs, removed_entries


def _build_txt2img_workflow(body: dict) -> tuple[dict, dict]:
    """Create a txt2img workflow for ComfyUI.

    Supports: multi-LoRA chaining, custom VAE, Refiner checkpoint, HiresFix.
    """
    prompt = (body.get("prompt") or "").strip()
    negative = (body.get("negative_prompt") or "").strip()
    model = (body.get("model") or "").strip()
    sampler = (body.get("sampler") or "euler").strip() or "euler"
    scheduler = (body.get("scheduler") or "normal").strip() or "normal"

    seed = _coerce_seed(body.get("seed"))
    steps = _clamp_int(int(body.get("steps", DEFAULT_IMAGE_STEPS)), MIN_STEPS, MAX_STEPS)
    cfg = _clamp_float(float(body.get("cfg", DEFAULT_IMAGE_CFG)), MIN_CFG, MAX_CFG)
    width = _clamp_int(int(body.get("width", DEFAULT_IMAGE_WIDTH)), 256, 2048)
    height = _clamp_int(int(body.get("height", DEFAULT_IMAGE_HEIGHT)), 256, 2048)
    batch_size = _clamp_int(int(body.get("batch_size", 1)), 1, 8)

    # Multi-LoRA stack: prefer loras[] array; fall back to legacy lora/lora_strength
    raw_loras = body.get("loras")
    if isinstance(raw_loras, list) and raw_loras:
        loras = [
            {
                "name": str(e.get("name") or "").strip(),
                "strength": _clamp_float(float(e.get("strength", 0.8)), 0.0, 2.0),
            }
            for e in raw_loras
            if isinstance(e, dict) and str(e.get("name") or "").strip()
        ]
    else:
        legacy_name = (body.get("lora") or "").strip()
        loras = [{"name": legacy_name, "strength": _clamp_float(float(body.get("lora_strength", 0.8)), 0.0, 2.0)}] if legacy_name else []

    custom_vae = (body.get("vae") or "").strip()
    refiner_model = (body.get("refiner_model") or "").strip()

    hiresfix_enable = bool(body.get("hiresfix_enable"))
    hiresfix_upscaler = (body.get("hiresfix_upscaler") or "").strip()
    hiresfix_scale = _clamp_float(float(body.get("hiresfix_scale", 2.0)), 1.1, 8.0)
    hiresfix_steps = _clamp_int(int(body.get("hiresfix_steps", 20)), 1, 100)
    hiresfix_denoise = _clamp_float(float(body.get("hiresfix_denoise", 0.4)), 0.05, 1.0)

    controlnet_model = (body.get("controlnet_model") or "").strip()
    controlnet_image_name = (body.get("controlnet_image_name") or "").strip()
    controlnet_weight = _clamp_float(float(body.get("controlnet_weight", 1.0)), 0.0, 2.0)
    controlnet_start = _clamp_float(float(body.get("controlnet_start", 0.0)), 0.0, 1.0)
    controlnet_end = _clamp_float(float(body.get("controlnet_end", 1.0)), 0.0, 1.0)
    if controlnet_start > controlnet_end:
        controlnet_start, controlnet_end = controlnet_end, controlnet_start

    if not model:
        models = _image_models()
        model = models[0] if models else ""

    meta = {
        "prompt": prompt,
        "negative_prompt": negative,
        "model": model,
        "sampler": sampler,
        "scheduler": scheduler,
        "seed": seed,
        "steps": steps,
        "cfg": cfg,
        "width": width,
        "height": height,
        "batch_size": batch_size,
        "loras": loras,
        "vae": custom_vae,
        "refiner_model": refiner_model,
        "hiresfix_enable": hiresfix_enable,
        "hiresfix_upscaler": hiresfix_upscaler,
        "hiresfix_scale": hiresfix_scale,
        "hiresfix_steps": hiresfix_steps,
        "hiresfix_denoise": hiresfix_denoise,
        "controlnet_model": controlnet_model,
        "controlnet_image_name": controlnet_image_name,
        "controlnet_weight": controlnet_weight,
        "controlnet_start": controlnet_start,
        "controlnet_end": controlnet_end,
    }

    # --- Node counter helper ------------------------------------------------
    _node_id = [20]  # start well above reserved 1-19

    def _nid() -> str:
        _node_id[0] += 1
        return str(_node_id[0])

    # --- Backbone -----------------------------------------------------------
    model_ref: list = ["1", 0]
    clip_ref: list = ["1", 1]
    vae_ref: list = ["1", 2]

    workflow: dict = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": model}},
    }

    # Custom VAE override
    if custom_vae:
        vae_node = _nid()
        workflow[vae_node] = {"class_type": "VAELoader", "inputs": {"vae_name": custom_vae}}
        vae_ref = [vae_node, 0]

    # LoRA chain
    for lora_entry in loras:
        lora_node = _nid()
        workflow[lora_node] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_entry["name"],
                "strength_model": lora_entry["strength"],
                "strength_clip": lora_entry["strength"],
                "model": model_ref,
                "clip": clip_ref,
            },
        }
        model_ref = [lora_node, 0]
        clip_ref = [lora_node, 1]

    # Text conditioning
    pos_node, neg_node = _nid(), _nid()
    workflow[pos_node] = {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": clip_ref}}
    workflow[neg_node] = {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": clip_ref}}
    positive_ref: list = [pos_node, 0]
    negative_ref: list = [neg_node, 0]

    # Latent image
    latent_node = _nid()
    workflow[latent_node] = {
        "class_type": "EmptyLatentImage",
        "inputs": {"width": width, "height": height, "batch_size": batch_size},
    }
    latent_ref: list = [latent_node, 0]

    # ControlNet
    if controlnet_model and controlnet_image_name:
        cn_loader = _nid()
        cn_img = _nid()
        cn_apply = _nid()
        workflow[cn_loader] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": controlnet_model}}
        workflow[cn_img] = {"class_type": "LoadImage", "inputs": {"image": controlnet_image_name}}
        workflow[cn_apply] = {
            "class_type": "ControlNetApplyAdvanced",
            "inputs": {
                "positive": positive_ref,
                "negative": negative_ref,
                "control_net": [cn_loader, 0],
                "image": [cn_img, 0],
                "strength": controlnet_weight,
                "start_percent": controlnet_start,
                "end_percent": controlnet_end,
            },
        }
        positive_ref = [cn_apply, 0]
        negative_ref = [cn_apply, 1]

    # Flux guidance node: wraps positive conditioning; KSampler cfg is set to 1.0
    family = body.get("model_family") or _infer_image_model_family(model)
    if family == "flux":
        fg_node = _nid()
        workflow[fg_node] = {
            "class_type": "FluxGuidance",
            "inputs": {"conditioning": positive_ref, "guidance": cfg},
        }
        positive_ref = [fg_node, 0]
        ks_cfg = 1.0
    else:
        ks_cfg = cfg

    # Primary KSampler
    ks_node = _nid()
    workflow[ks_node] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": seed,
            "steps": steps,
            "cfg": ks_cfg,
            "sampler_name": sampler,
            "scheduler": scheduler,
            "denoise": 1.0,
            "model": model_ref,
            "positive": positive_ref,
            "negative": negative_ref,
            "latent_image": latent_ref,
        },
    }
    sampled_ref: list = [ks_node, 0]

    # Refiner pass (optional second KSampler with refiner checkpoint)
    if refiner_model:
        ref_ckpt = _nid()
        ref_pos = _nid()
        ref_neg = _nid()
        ref_ks = _nid()
        workflow[ref_ckpt] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": refiner_model}}
        workflow[ref_pos] = {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": [ref_ckpt, 1]}}
        workflow[ref_neg] = {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": [ref_ckpt, 1]}}
        workflow[ref_ks] = {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "denoise": 0.2,
                "model": [ref_ckpt, 0],
                "positive": [ref_pos, 0],
                "negative": [ref_neg, 0],
                "latent_image": sampled_ref,
            },
        }
        sampled_ref = [ref_ks, 0]
        # Refiner provides its own VAE if none was specified
        if not custom_vae:
            vae_ref = [ref_ckpt, 2]

    # HiresFix (upscale + second KSampler)
    if hiresfix_enable:
        # Decode primary latent → pixels
        hf_decode = _nid()
        workflow[hf_decode] = {"class_type": "VAEDecode", "inputs": {"samples": sampled_ref, "vae": vae_ref}}

        # Upscale pixels
        if hiresfix_upscaler:
            hf_model = _nid()
            hf_upscale = _nid()
            workflow[hf_model] = {"class_type": "UpscaleModelLoader", "inputs": {"model_name": hiresfix_upscaler}}
            workflow[hf_upscale] = {
                "class_type": "ImageUpscaleWithModel",
                "inputs": {"upscale_model": [hf_model, 0], "image": [hf_decode, 0]},
            }
            upscaled_img_ref: list = [hf_upscale, 0]
        else:
            # Fallback: simple pixel-space scale
            hf_scale_img = _nid()
            workflow[hf_scale_img] = {
                "class_type": "ImageScale",
                "inputs": {
                    "image": [hf_decode, 0],
                    "upscale_method": "lanczos",
                    "width": int(width * hiresfix_scale),
                    "height": int(height * hiresfix_scale),
                    "crop": "disabled",
                },
            }
            upscaled_img_ref = [hf_scale_img, 0]

        # Re-encode to latent
        hf_encode = _nid()
        workflow[hf_encode] = {"class_type": "VAEEncode", "inputs": {"pixels": upscaled_img_ref, "vae": vae_ref}}

        # Hi-res KSampler
        hf_ks = _nid()
        workflow[hf_ks] = {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": hiresfix_steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "denoise": hiresfix_denoise,
                "model": model_ref,
                "positive": positive_ref,
                "negative": negative_ref,
                "latent_image": [hf_encode, 0],
            },
        }
        sampled_ref = [hf_ks, 0]

    # Final decode + save
    decode_node = _nid()
    save_node = _nid()
    workflow[decode_node] = {"class_type": "VAEDecode", "inputs": {"samples": sampled_ref, "vae": vae_ref}}
    workflow[save_node] = {
        "class_type": "SaveImage",
        "inputs": {"images": [decode_node, 0], "filename_prefix": "links-awakening"},
    }

    return workflow, meta


def _upload_image_to_comfy(file_storage) -> str:
    """Upload an image to ComfyUI input folder and return its server-side name."""
    files = {
        "image": (
            file_storage.filename,
            file_storage.stream,
            file_storage.mimetype or "application/octet-stream",
        )
    }
    data = {"type": "input", "overwrite": "true"}
    resp = requests.post(f"{COMFYUI_BASE_URL}/upload/image", files=files, data=data, timeout=30)
    resp.raise_for_status()
    payload = resp.json() or {}
    return payload.get("name", "")


def _build_img2img_workflow(body: dict, uploaded_name: str) -> tuple[dict, dict]:
    """Create an img2img workflow for ComfyUI.

    Supports: multi-LoRA chaining, custom VAE, ControlNet.
    """
    prompt = (body.get("prompt") or "").strip()
    negative = (body.get("negative_prompt") or "").strip()
    model = (body.get("model") or "").strip()
    sampler = (body.get("sampler") or "euler").strip() or "euler"
    scheduler = (body.get("scheduler") or "normal").strip() or "normal"

    seed = _coerce_seed(body.get("seed"))
    steps = _clamp_int(int(body.get("steps", DEFAULT_IMAGE_STEPS)), MIN_STEPS, MAX_STEPS)
    cfg = _clamp_float(float(body.get("cfg", DEFAULT_IMAGE_CFG)), MIN_CFG, MAX_CFG)
    denoise = _clamp_float(float(body.get("denoise", DEFAULT_IMAGE_DENOISE)), 0.05, 1.0)

    # Multi-LoRA stack (same logic as txt2img)
    raw_loras = body.get("loras")
    if isinstance(raw_loras, list) and raw_loras:
        loras = [
            {
                "name": str(e.get("name") or "").strip(),
                "strength": _clamp_float(float(e.get("strength", 0.8)), 0.0, 2.0),
            }
            for e in raw_loras
            if isinstance(e, dict) and str(e.get("name") or "").strip()
        ]
    else:
        legacy_name = (body.get("lora") or "").strip()
        loras = [{"name": legacy_name, "strength": _clamp_float(float(body.get("lora_strength", 0.8)), 0.0, 2.0)}] if legacy_name else []

    custom_vae = (body.get("vae") or "").strip()

    controlnet_model = (body.get("controlnet_model") or "").strip()
    controlnet_image_name = (body.get("controlnet_image_name") or "").strip()
    controlnet_weight = _clamp_float(float(body.get("controlnet_weight", 1.0)), 0.0, 2.0)
    controlnet_start = _clamp_float(float(body.get("controlnet_start", 0.0)), 0.0, 1.0)
    controlnet_end = _clamp_float(float(body.get("controlnet_end", 1.0)), 0.0, 1.0)
    if controlnet_start > controlnet_end:
        controlnet_start, controlnet_end = controlnet_end, controlnet_start

    if not model:
        models = _image_models()
        model = models[0] if models else ""

    meta = {
        "prompt": prompt,
        "negative_prompt": negative,
        "model": model,
        "sampler": sampler,
        "scheduler": scheduler,
        "seed": seed,
        "steps": steps,
        "cfg": cfg,
        "denoise": denoise,
        "image": uploaded_name,
        "loras": loras,
        "vae": custom_vae,
        "controlnet_model": controlnet_model,
        "controlnet_image_name": controlnet_image_name,
        "controlnet_weight": controlnet_weight,
        "controlnet_start": controlnet_start,
        "controlnet_end": controlnet_end,
    }

    _node_id = [20]

    def _nid() -> str:
        _node_id[0] += 1
        return str(_node_id[0])

    model_ref: list = ["1", 0]
    clip_ref: list = ["1", 1]
    vae_ref: list = ["1", 2]

    workflow: dict = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": model}},
    }

    if custom_vae:
        vae_node = _nid()
        workflow[vae_node] = {"class_type": "VAELoader", "inputs": {"vae_name": custom_vae}}
        vae_ref = [vae_node, 0]

    for lora_entry in loras:
        lora_node = _nid()
        workflow[lora_node] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_entry["name"],
                "strength_model": lora_entry["strength"],
                "strength_clip": lora_entry["strength"],
                "model": model_ref,
                "clip": clip_ref,
            },
        }
        model_ref = [lora_node, 0]
        clip_ref = [lora_node, 1]

    pos_node, neg_node = _nid(), _nid()
    workflow[pos_node] = {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": clip_ref}}
    workflow[neg_node] = {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": clip_ref}}
    positive_ref: list = [pos_node, 0]
    negative_ref: list = [neg_node, 0]

    # Load and encode input image
    load_img_node = _nid()
    vae_encode_node = _nid()
    workflow[load_img_node] = {"class_type": "LoadImage", "inputs": {"image": uploaded_name}}
    workflow[vae_encode_node] = {"class_type": "VAEEncode", "inputs": {"pixels": [load_img_node, 0], "vae": vae_ref}}

    if controlnet_model and controlnet_image_name:
        cn_loader = _nid()
        cn_img = _nid()
        cn_apply = _nid()
        workflow[cn_loader] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": controlnet_model}}
        workflow[cn_img] = {"class_type": "LoadImage", "inputs": {"image": controlnet_image_name}}
        workflow[cn_apply] = {
            "class_type": "ControlNetApplyAdvanced",
            "inputs": {
                "positive": positive_ref,
                "negative": negative_ref,
                "control_net": [cn_loader, 0],
                "image": [cn_img, 0],
                "strength": controlnet_weight,
                "start_percent": controlnet_start,
                "end_percent": controlnet_end,
            },
        }
        positive_ref = [cn_apply, 0]
        negative_ref = [cn_apply, 1]

    # Flux guidance node
    img2img_family = body.get("model_family") or _infer_image_model_family(model)
    if img2img_family == "flux":
        fg_node = _nid()
        workflow[fg_node] = {
            "class_type": "FluxGuidance",
            "inputs": {"conditioning": positive_ref, "guidance": cfg},
        }
        positive_ref = [fg_node, 0]
        ks_cfg = 1.0
    else:
        ks_cfg = cfg

    ks_node = _nid()
    workflow[ks_node] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": seed,
            "steps": steps,
            "cfg": ks_cfg,
            "sampler_name": sampler,
            "scheduler": scheduler,
            "denoise": denoise,
            "model": model_ref,
            "positive": positive_ref,
            "negative": negative_ref,
            "latent_image": [vae_encode_node, 0],
        },
    }

    decode_node = _nid()
    save_node = _nid()
    workflow[decode_node] = {"class_type": "VAEDecode", "inputs": {"samples": [ks_node, 0], "vae": vae_ref}}
    workflow[save_node] = {
        "class_type": "SaveImage",
        "inputs": {"images": [decode_node, 0], "filename_prefix": "links-awakening-img2img"},
    }

    return workflow, meta


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Main interface page."""
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Model browser state
# ---------------------------------------------------------------------------

_model_downloads: dict[str, dict] = {}      # download_id → state dict
_model_downloads_lock = threading.Lock()

_CIVITAI_API = "https://civitai.com/api/v1"
_HUGGINGFACE_API = "https://huggingface.co/api"
_CIVITAI_MODEL_TYPES = {"Checkpoint", "LORA", "VAE", "TextualInversion", "ControlNet", "Upscaler"}

# Maps CivitAI model type → ComfyUI subfolder name
_CIVITAI_TYPE_TO_COMFY_FOLDER: dict[str, str] = {
    "Checkpoint": "checkpoints",
    "LORA": "loras",
    "VAE": "vae",
    "TextualInversion": "embeddings",
    "ControlNet": "controlnet",
    "Upscaler": "upscale_models",
}

# Maps CivitAI model type → Stability Matrix shared folder name
_CIVITAI_TYPE_TO_STABILITY_FOLDER: dict[str, str] = {
    "Checkpoint": "StableDiffusion",
    "LORA": "Lora",
    "VAE": "VAE",
    "TextualInversion": "Embeddings",
    "ControlNet": "ControlNet",
    "Upscaler": "ESRGAN",
}

_COMFY_MODEL_SUBFOLDERS = sorted(set(_CIVITAI_TYPE_TO_COMFY_FOLDER.values()))
_STABILITY_MODEL_SUBFOLDERS = sorted(set(_CIVITAI_TYPE_TO_STABILITY_FOLDER.values()))


def _external_api_headers(provider: str) -> dict[str, str]:
    config = _load_service_config()
    key = ""
    if provider == "civitai":
        key = str(config.get("civitai_api_key") or "").strip()
    elif provider == "huggingface":
        key = str(config.get("huggingface_api_key") or "").strip()

    if not key:
        return {}
    return {"Authorization": f"Bearer {key}"}


def _infer_huggingface_model_type(item: dict) -> str:
    tags = [str(t).lower() for t in (item.get("tags") or [])]
    model_id = str(item.get("id") or "").lower()
    joined = " ".join(tags + [model_id])
    if "controlnet" in joined:
        return "ControlNet"
    if "textual-inversion" in joined or "textual inversion" in joined or "embedding" in joined:
        return "TextualInversion"
    if "vae" in joined:
        return "VAE"
    if "lora" in joined or "lycoris" in joined:
        return "LORA"
    if "upscaler" in joined or "esrgan" in joined:
        return "Upscaler"
    return "Checkpoint"


def _find_primary_huggingface_file(files: list[dict]) -> str:
    preferred_name = ""
    for file_obj in files or []:
        name = str(file_obj.get("rfilename") or "")
        if name:
            preferred_name = name
            if str(file_obj.get("primary") or "").lower() in {"1", "true", "yes"}:
                break

    resolved = _pick_huggingface_download_file(files, preferred_name=preferred_name)
    if resolved:
        return resolved

    if files:
        return str(files[0].get("rfilename") or "")
    return ""


def _is_huggingface_model_file(file_name: str) -> bool:
    name = (file_name or "").strip().lower()
    if not name:
        return False
    if "/" in name:
        return False
    blocked_suffixes = (
        ".json",
        ".md",
        ".txt",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".yaml",
        ".yml",
        ".toml",
        ".license",
        ".gitattributes",
    )
    if name.endswith(blocked_suffixes):
        return False
    blocked_tokens = (
        "tokenizer",
        "vocab",
        "merges",
        "scheduler",
        "feature_extractor",
        "preprocessor_config",
        "special_tokens_map",
        "config",
    )
    return not any(token in name for token in blocked_tokens)


def _pick_huggingface_download_file(files: list[dict], preferred_name: str = "") -> str:
    ranked_exts = (".safetensors", ".ckpt", ".pt", ".pth", ".bin")
    candidates = [str(f.get("rfilename") or "") for f in (files or [])]
    candidates = [name for name in candidates if _is_huggingface_model_file(name)]
    if not candidates:
        return ""

    preferred = (preferred_name or "").strip()
    if preferred and preferred in candidates:
        return preferred

    for ext in ranked_exts:
        hit = next((name for name in candidates if name.lower().endswith(ext)), None)
        if hit:
            return hit
    return candidates[0]


def _build_huggingface_download_url(model_id: str, file_name: str) -> str:
    safe_model_id = quote((model_id or "").strip(), safe="/")
    safe_file_name = quote((file_name or "").strip(), safe="")
    if not safe_model_id or not safe_file_name:
        return ""
    return f"https://huggingface.co/{safe_model_id}/resolve/main/{safe_file_name}"


def _resolve_huggingface_download_target(model_id: str, preferred_file_name: str = "") -> tuple[str, str]:
    safe_model_id = (model_id or "").strip()
    if not safe_model_id:
        raise ValueError("model_id is required for huggingface downloads")

    resp = requests.get(
        f"{_HUGGINGFACE_API}/models/{safe_model_id}",
        headers=_external_api_headers("huggingface"),
        timeout=20,
    )
    resp.raise_for_status()
    raw = resp.json() or {}
    selected_file = _pick_huggingface_download_file(raw.get("siblings") or [], preferred_name=preferred_file_name)
    if not selected_file:
        raise ValueError("No compatible downloadable model file was found for this Hugging Face repository")

    return selected_file, _build_huggingface_download_url(safe_model_id, selected_file)


def _using_shared_models_root() -> bool:
    return _resolve_shared_models_root_dir() is not None


def _preferred_model_folder_for_type(model_type: str) -> str:
    if _using_shared_models_root():
        return _CIVITAI_TYPE_TO_STABILITY_FOLDER.get(model_type, "StableDiffusion")
    return _CIVITAI_TYPE_TO_COMFY_FOLDER.get(model_type, "checkpoints")


def _normalize_model_folder(folder: str) -> str | None:
    value = (folder or "").strip()
    if not value:
        return None

    # Compatibility aliases between Comfy and Stability Matrix naming.
    shared_aliases = {
        "checkpoints": "StableDiffusion",
        "loras": "Lora",
        "vae": "VAE",
        "embeddings": "Embeddings",
        "controlnet": "ControlNet",
        "upscale_models": "ESRGAN",
    }
    comfy_aliases = {v: k for k, v in shared_aliases.items()}

    if _using_shared_models_root():
        if value in _STABILITY_MODEL_SUBFOLDERS:
            return value
        return shared_aliases.get(value)

    if value in _COMFY_MODEL_SUBFOLDERS:
        return value
    return comfy_aliases.get(value)


def _comfy_models_root() -> Path | None:
    """Return the effective model root directory from shared path or ComfyUI path."""
    shared_root = _resolve_shared_models_root_dir()
    if shared_root is not None:
        return shared_root

    root = _resolve_comfy_root_dir()
    if root is None:
        return None
    return root / "models"


def _infer_local_model_type(folder: str) -> str:
    """Map local model folder names to model-browser type labels."""
    value = str(folder or "").strip().lower()
    if not value:
        return "Checkpoint"
    if "lora" in value:
        return "LORA"
    if "vae" in value:
        return "VAE"
    if "embedding" in value:
        return "TextualInversion"
    if "controlnet" in value:
        return "ControlNet"
    if "upscale" in value or "esrgan" in value:
        return "Upscaler"
    return "Checkpoint"


def _infer_local_base_model(file_name: str) -> str:
    """Best-effort local base-model label inference from file naming conventions."""
    value = str(file_name or "").strip().lower()
    if not value:
        return ""
    if "sdxl" in value and "turbo" in value:
        return "SDXL Turbo"
    if "sdxl" in value:
        return "SDXL 1.0"
    if "pony" in value:
        return "Pony"
    if "flux" in value and ("schnell" in value or "flux.1-s" in value or "flux1-s" in value or "flux_1_s" in value):
        return "Flux.1 S"
    if "flux" in value:
        return "Flux.1 D"
    if any(token in value for token in ("sd15", "sd_15", "sd-15", "sd 1.5", "v1-5", "v1_5", "v1.5")):
        return "SD 1.5"
    return ""


def _scan_local_models() -> list[dict]:
    """Walk all ComfyUI model subdirectories and return file metadata."""
    models_root = _comfy_models_root()
    if models_root is None:
        return []
    if not models_root.exists() or not models_root.is_dir():
        return []
    results: list[dict] = []
    if _using_shared_models_root():
        folders_to_scan = sorted(set(_STABILITY_MODEL_SUBFOLDERS + _COMFY_MODEL_SUBFOLDERS))
    else:
        folders_to_scan = _COMFY_MODEL_SUBFOLDERS
    metadata_map = _load_model_metadata()

    seen_paths: set[str] = set()
    root_resolved = models_root.resolve()
    preview_extensions = (".png", ".jpg", ".jpeg", ".webp")
    for folder in folders_to_scan:
        folder_path = models_root / folder
        if not folder_path.is_dir():
            continue
        for f in folder_path.iterdir():
            if f.is_file() and f.suffix.lower() in {".safetensors", ".ckpt", ".pt", ".pth", ".bin"}:
                resolved_path = str(f.resolve())
                if resolved_path in seen_paths:
                    continue
                seen_paths.add(resolved_path)

                normalized_folder = _normalize_model_folder(folder) or folder
                preview_url = ""
                local_preview_urls: list[str] = []
                for ext in preview_extensions:
                    preview_candidate = f.with_suffix(ext)
                    if not preview_candidate.is_file():
                        continue
                    try:
                        preview_rel = preview_candidate.resolve().relative_to(root_resolved).as_posix()
                    except ValueError:
                        continue
                    preview_url = f"/api/models/local-preview?path={quote(preview_rel)}"
                    local_preview_urls.append(preview_url)
                    break
                metadata = _lookup_model_download_metadata(metadata_map, f.name, normalized_folder)
                sidecar_metadata = _extract_local_sidecar_model_metadata(f)
                metadata_preview_urls = _sanitize_preview_urls(metadata.get("preview_urls") or [])
                sidecar_preview_urls = _sanitize_preview_urls(sidecar_metadata.get("preview_urls") or [])
                if not preview_url:
                    preview_url = _sanitize_optional_preview_url(metadata.get("preview_url") or "")
                if not preview_url:
                    preview_url = _sanitize_optional_preview_url(sidecar_metadata.get("preview_url") or "")

                preview_urls: list[str] = []
                for candidate in local_preview_urls + metadata_preview_urls + sidecar_preview_urls:
                    if candidate and candidate not in preview_urls:
                        preview_urls.append(candidate)
                if preview_url and preview_url not in preview_urls:
                    preview_urls.insert(0, preview_url)
                if not preview_url and preview_urls:
                    preview_url = preview_urls[0]

                provider = str(metadata.get("provider") or sidecar_metadata.get("provider") or "")
                model_id = str(metadata.get("model_id") or sidecar_metadata.get("model_id") or "")
                model_url = str(metadata.get("model_url") or sidecar_metadata.get("model_url") or "")
                version_name = str(metadata.get("version_name") or sidecar_metadata.get("version_name") or "")
                inferred_type = _infer_local_model_type(normalized_folder)
                inferred_base_model = _infer_local_base_model(f.name)
                resolved_type = str(sidecar_metadata.get("model_type") or inferred_type or "")
                resolved_base_model = str(sidecar_metadata.get("base_model") or inferred_base_model or "")

                results.append({
                    "name": f.name,
                    "folder": normalized_folder,
                    "type": resolved_type,
                    "base_model": resolved_base_model,
                    "preview_url": preview_url,
                    "preview_urls": preview_urls,
                    "provider": provider,
                    "model_id": model_id,
                    "model_url": model_url,
                    "version_name": version_name,
                    "size_bytes": f.stat().st_size,
                    "path": str(f),
                })
    results.sort(key=lambda m: (m["folder"], m["name"].lower()))
    return results


def _civitai_search(
    query: str,
    model_type: str,
    page: int,
    cursor: str = "",
    sort: str = "Highest Rated",
    nsfw: bool = False,
    base_model: str = "",
    limit: int = 20,
) -> dict:
    """Call CivitAI models API and return sanitised results."""
    headers = _external_api_headers("civitai")
    per_page = max(1, min(100, int(limit or 20)))
    base_params: dict = {
        "limit": per_page,
        "sort": sort if sort in {"Highest Rated", "Most Downloaded", "Newest"} else "Highest Rated",
        "nsfw": "true" if nsfw else "false",
    }
    if base_model:
        base_params["baseModels"] = base_model

    raw: dict = {}
    current_page = max(1, page)

    # CivitAI rejects query + page together and requires cursor pagination.
    if query:
        params = dict(base_params)
        params["query"] = query
        if model_type and model_type in _CIVITAI_MODEL_TYPES:
            params["types"] = model_type

        # Preferred mode: client supplies cursor for requested page.
        if cursor:
            params["cursor"] = cursor
            resp = requests.get(f"{_CIVITAI_API}/models", params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            raw = resp.json() or {}
        else:
            # Compatibility mode: derive requested page by walking cursors.
            walk_cursor = None
            resolved_page = 1
            for requested_page in range(1, current_page + 1):
                walk_params = dict(params)
                if walk_cursor:
                    walk_params["cursor"] = walk_cursor
                resp = requests.get(f"{_CIVITAI_API}/models", params=walk_params, headers=headers, timeout=15)
                resp.raise_for_status()
                raw = resp.json() or {}
                resolved_page = requested_page
                walk_cursor = (raw.get("metadata") or {}).get("nextCursor")
                if requested_page < current_page and not walk_cursor:
                    break
            current_page = resolved_page
    else:
        params = dict(base_params)
        params["page"] = current_page
        if model_type and model_type in _CIVITAI_MODEL_TYPES:
            params["types"] = model_type
        resp = requests.get(f"{_CIVITAI_API}/models", params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        raw = resp.json() or {}

    metadata = raw.get("metadata") or {}
    next_cursor = metadata.get("nextCursor") or ""
    has_next_cursor = bool(next_cursor)

    items = []
    for model in raw.get("items", []):
        versions = model.get("modelVersions") or []
        latest = versions[0] if versions else {}
        files = latest.get("files") or []
        primary_file = next((f for f in files if f.get("primary")), files[0] if files else {})
        preview_images = latest.get("images") or []
        preview_url = ""
        if preview_images:
            # Filter out videos first - they cannot render as <img> src.
            still_images = [img for img in preview_images if not _is_civitai_video_preview(img)]
            pool = still_images if still_images else []
            safe_candidates = [
                img
                for img in pool
                if img.get("nsfw") is False or int(img.get("nsfwLevel") or 0) <= 1
            ]
            chosen_preview = safe_candidates[0] if safe_candidates else (pool[0] if pool else None)
            preview_url = str(chosen_preview.get("url") or "") if chosen_preview else ""
        items.append({
            "provider": "civitai",
            "id": model.get("id"),
            "name": model.get("name", ""),
            "type": model.get("type", ""),
            "creator": (model.get("creator") or {}).get("username", ""),
            "description": (model.get("description") or "")[:300],
            "rating": (model.get("stats") or {}).get("rating", 0),
            "likes": (model.get("stats") or {}).get("thumbsUpCount")
            or (model.get("stats") or {}).get("favoriteCount")
            or 0,
            "download_count": (model.get("stats") or {}).get("downloadCount", 0),
            "preview_url": preview_url,
            "version_id": latest.get("id"),
            "version_name": latest.get("name", ""),
            "base_model": latest.get("baseModel", ""),
            "published_at": latest.get("publishedAt") or model.get("publishedAt") or "",
            "is_early_access": bool(
                latest.get("earlyAccessDeadline")
                or latest.get("earlyAccessEndsAt")
                or latest.get("availability") == "EarlyAccess"
            ),
            "is_nsfw": bool(model.get("nsfw") or latest.get("nsfw")),
            "file_name": primary_file.get("name", ""),
            "file_size_bytes": primary_file.get("sizeKB", 0) * 1024,
            "download_url": primary_file.get("downloadUrl", ""),
            "model_url": f"https://civitai.com/models/{model.get('id')}" if model.get("id") else "",
            "model_type_folder": _preferred_model_folder_for_type(model.get("type", "")),
        })
    return {
        "items": items,
        "total_items": metadata.get("totalItems"),
        "total_pages": metadata.get("totalPages") or (current_page + 1 if has_next_cursor else current_page),
        "current_page": current_page,
        "has_next": has_next_cursor,
        "next_cursor": next_cursor,
    }


def _do_download(download_id: str, url: str, dest_path: Path, headers: dict[str, str] | None = None) -> None:
    """Background thread: stream a file from url to dest_path, updating state."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")
    try:
        with requests.get(url, headers=headers or {}, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        with _model_downloads_lock:
                            dl = _model_downloads.get(download_id)
                            if dl and dl["status"] == "cancelled":
                                raise InterruptedError("cancelled")
                            if dl:
                                dl["downloaded_bytes"] = downloaded
                                dl["total_bytes"] = total
        tmp_path.rename(dest_path)
        with _model_downloads_lock:
            if download_id in _model_downloads:
                _model_downloads[download_id]["status"] = "done"
                _model_downloads[download_id]["downloaded_bytes"] = _model_downloads[download_id]["total_bytes"]
    except InterruptedError:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        with _model_downloads_lock:
            if download_id in _model_downloads:
                _model_downloads[download_id]["status"] = "cancelled"
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        logger.error("Model download %s failed: %s", download_id, exc)
        error_text = str(exc)
        if isinstance(exc, requests.HTTPError):
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code == 401:
                error_text = "Unauthorized (401). Check your API key for this provider in Configurations."
        with _model_downloads_lock:
            if download_id in _model_downloads:
                _model_downloads[download_id]["status"] = "error"
                _model_downloads[download_id]["error"] = error_text


@app.route("/api/models/library")
def api_models_library():
    """List locally installed ComfyUI model files."""
    models = _scan_local_models()
    root = _comfy_models_root()
    return jsonify({"models": models, "models_root": str(root) if root else None})


@app.route("/api/models/library/enrich-previews", methods=["POST"])
def api_models_library_enrich_previews():
    """Backfill missing local model preview metadata using CivitAI search."""
    body = request.get_json(silent=True) or {}
    try:
        limit = int(body.get("limit", 40))
    except (TypeError, ValueError):
        limit = 40
    limit = max(1, min(limit, 200))

    try:
        result = _enrich_local_model_metadata_with_civitai(limit=limit)
    except requests.RequestException as exc:
        logger.error("Local preview enrichment request failed: %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 502

    return jsonify({"ok": True, **result})


@app.route("/api/models/library/compare-metadata", methods=["POST"])
def api_models_library_compare_metadata():
    """Compare local model names against providers to fill missing metadata."""
    body = request.get_json(silent=True) or {}
    try:
        limit = int(body.get("limit", 80))
    except (TypeError, ValueError):
        limit = 80
    limit = max(1, min(limit, 300))

    providers_raw = body.get("providers")
    if isinstance(providers_raw, list):
        providers = [str(provider).strip().lower() for provider in providers_raw]
    else:
        providers = ["civitai", "huggingface"]

    overwrite = bool(body.get("overwrite", False))

    result = _compare_local_model_metadata_with_providers(limit=limit, providers=providers, overwrite=overwrite)
    return jsonify({"ok": True, **result})


@app.route("/api/models/library/recover-metadata", methods=["POST"])
def api_models_library_recover_metadata():
    """Run metadata compare and preview enrichment in one recovery pass."""
    body = request.get_json(silent=True) or {}
    try:
        compare_limit = int(body.get("compare_limit", body.get("limit", 80)))
    except (TypeError, ValueError):
        compare_limit = 80
    compare_limit = max(1, min(compare_limit, 300))

    try:
        preview_limit = int(body.get("preview_limit", body.get("enrich_limit", 40)))
    except (TypeError, ValueError):
        preview_limit = 40
    preview_limit = max(1, min(preview_limit, 200))

    providers_raw = body.get("providers")
    if isinstance(providers_raw, list):
        providers = [str(provider).strip().lower() for provider in providers_raw]
    else:
        providers = ["civitai", "huggingface"]

    overwrite = bool(body.get("overwrite", False))

    try:
        compare_result = _compare_local_model_metadata_with_providers(
            limit=compare_limit,
            providers=providers,
            overwrite=overwrite,
        )
        preview_result = _enrich_local_model_metadata_with_civitai(limit=preview_limit)
    except requests.RequestException as exc:
        logger.error("Local metadata recovery request failed: %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 502

    return jsonify(
        {
            "ok": True,
            "compare": compare_result,
            "preview": preview_result,
            "updated_total": int(compare_result.get("updated") or 0) + int(preview_result.get("updated") or 0),
            "skipped_total": int(compare_result.get("skipped") or 0) + int(preview_result.get("skipped") or 0),
            "failed_total": int(compare_result.get("failed") or 0) + int(preview_result.get("failed") or 0),
        }
    )


@app.route("/api/models/library/update-version-metadata", methods=["POST"])
def api_models_library_update_version_metadata():
    """Refresh local metadata and preview set for installed files of a selected model version."""
    body = request.get_json(silent=True) or {}

    provider = str(body.get("provider") or "").strip().lower()
    model_id = str(body.get("model_id") or "").strip()
    model_name = str(body.get("model_name") or "").strip()
    model_type = str(body.get("model_type") or "").strip()
    base_model = str(body.get("base_model") or "").strip()
    model_url = str(body.get("model_url") or "").strip()
    version_name = str(body.get("version_name") or "").strip()

    installed_files_raw = body.get("installed_files")
    installed_files = [
        str(file_name).strip()
        for file_name in (installed_files_raw if isinstance(installed_files_raw, list) else [])
        if str(file_name).strip()
    ]
    if not installed_files:
        return jsonify({"ok": False, "error": "installed_files is required"}), 400

    preview_urls = _sanitize_preview_urls(body.get("preview_urls") or [])
    preview_url = _sanitize_optional_preview_url(body.get("preview_url") or "")
    if not preview_url and preview_urls:
        preview_url = preview_urls[0]
    if preview_url and preview_url not in preview_urls:
        preview_urls.insert(0, preview_url)

    local_models = _scan_local_models()
    installed_lookup = {name.lower() for name in installed_files}
    updated_files: list[str] = []

    for item in local_models:
        file_name = str(item.get("name") or "").strip()
        folder = str(item.get("folder") or "").strip()
        if not file_name or not folder:
            continue
        if file_name.lower() not in installed_lookup:
            continue

        _upsert_model_download_metadata(
            file_name=file_name,
            folder=folder,
            body={
                "model_id": model_id,
                "model_name": model_name,
                "version_name": version_name,
                "model_type": model_type,
                "base_model": base_model,
                "model_url": model_url,
                "preview_url": preview_url,
                "preview_urls": preview_urls,
            },
            provider=provider,
            model_id=model_id,
        )
        updated_files.append(f"{folder}/{file_name}")

    return jsonify(
        {
            "ok": True,
            "updated": len(updated_files),
            "updated_files": updated_files,
            "preview_count": len(preview_urls),
            "version_name": version_name,
        }
    )


@app.route("/api/models/local-preview")
def api_models_local_preview():
    """Serve preview images for local model files from the configured models root."""
    rel_path = (request.args.get("path") or "").strip()
    if not rel_path:
        return jsonify({"ok": False, "error": "Missing path"}), 400

    models_root = _comfy_models_root()
    if models_root is None:
        return jsonify({"ok": False, "error": "Models root not configured"}), 400

    root_resolved = models_root.resolve()
    candidate = (models_root / rel_path).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid preview path"}), 400

    if candidate.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        return jsonify({"ok": False, "error": "Unsupported preview format"}), 400
    if not candidate.is_file():
        return jsonify({"ok": False, "error": "Preview not found"}), 404

    return send_file(candidate)


@app.route("/api/models/civitai/search")
def api_models_civitai_search():
    """Search CivitAI for models."""
    query = (request.args.get("query") or "").strip()
    model_type = (request.args.get("type") or "").strip()
    sort = (request.args.get("sort") or "Highest Rated").strip()
    base_model = (request.args.get("base_model") or "").strip()
    nsfw_raw = (request.args.get("nsfw") or "false").strip().lower()
    nsfw = nsfw_raw in {"1", "true", "yes", "on"}
    cursor = (request.args.get("cursor") or "").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        limit = max(1, min(100, int(request.args.get("limit", 20))))
    except (TypeError, ValueError):
        limit = 20
    try:
        results = _civitai_search(query, model_type, page, cursor, sort, nsfw, base_model, limit)
        return jsonify({"ok": True, **results})
    except requests.RequestException as exc:
        logger.error("CivitAI search failed: %s", exc)
        return jsonify({"ok": False, "error": str(exc), "items": [], "total_items": 0, "total_pages": 1, "current_page": 1}), 502


@app.route("/api/models/civitai/model/<int:model_id>")
def api_models_civitai_model(model_id: int):
    """Fetch and sanitize CivitAI model details for the details modal."""
    try:
        resp = requests.get(
            f"{_CIVITAI_API}/models/{model_id}",
            headers=_external_api_headers("civitai"),
            timeout=20,
        )
        resp.raise_for_status()
        raw = resp.json() or {}
    except requests.RequestException as exc:
        logger.error("CivitAI model details failed for %s: %s", model_id, exc)
        return jsonify({"ok": False, "error": str(exc)}), 502

    versions: list[dict] = []
    for version in raw.get("modelVersions") or []:
        files = []
        for f in version.get("files") or []:
            size_kb = f.get("sizeKB") or 0
            try:
                size_bytes = int(float(size_kb) * 1024)
            except (TypeError, ValueError):
                size_bytes = 0
            files.append(
                {
                    "id": f.get("id"),
                    "name": f.get("name", ""),
                    "size_bytes": size_bytes,
                    "type": f.get("type", ""),
                    "format": f.get("format", ""),
                    "fp": f.get("fp", ""),
                    "primary": bool(f.get("primary")),
                    "download_url": f.get("downloadUrl", ""),
                }
            )

        images = []
        for img in version.get("images") or []:
            images.append(
                {
                    "url": img.get("url", ""),
                    "type": img.get("type", ""),
                    "nsfw_level": img.get("nsfwLevel", 0),
                    "width": img.get("width"),
                    "height": img.get("height"),
                }
            )

        meta = version.get("meta") or {}
        defaults = {
            "sampler": meta.get("sampler") or version.get("sampler") or "",
            "steps": meta.get("steps") or version.get("steps") or "",
            "cfg": meta.get("cfgScale") or version.get("cfgScale") or "",
            "clip_skip": meta.get("clipSkip") or version.get("clipSkip") or "",
            "base_model": version.get("baseModel", ""),
            "trained_words": version.get("trainedWords") or [],
        }

        versions.append(
            {
                "id": version.get("id"),
                "name": version.get("name", ""),
                "description": (version.get("description") or "")[:1200],
                "created_at": version.get("createdAt") or "",
                "base_model": version.get("baseModel") or "",
                "is_early_access": bool(
                    version.get("earlyAccessDeadline")
                    or version.get("earlyAccessEndsAt")
                    or version.get("availability") == "EarlyAccess"
                ),
                "images": images,
                "files": files,
                "defaults": defaults,
            }
        )

    payload = {
        "ok": True,
        "provider": "civitai",
        "id": raw.get("id"),
        "name": raw.get("name", ""),
        "type": raw.get("type", ""),
        "description": (raw.get("description") or "")[:2000],
        "creator": (raw.get("creator") or {}).get("username", ""),
        "tags": raw.get("tags") or [],
        "stats": {
            "rating": (raw.get("stats") or {}).get("rating", 0),
            "downloads": (raw.get("stats") or {}).get("downloadCount", 0),
            "likes": (raw.get("stats") or {}).get("thumbsUpCount")
            or (raw.get("stats") or {}).get("favoriteCount")
            or 0,
        },
        "versions": versions,
        "model_url": f"https://civitai.com/models/{raw.get('id')}" if raw.get("id") else "",
    }
    return jsonify(payload)


def _huggingface_search(query: str, model_type: str, page: int, sort: str = "Highest Rated", limit: int = 20) -> dict:
    """Search Hugging Face models and map to shared model card structure."""
    current_page = max(1, page)
    per_page = max(1, min(100, int(limit or 20)))
    hf_sort = "likes"
    if sort == "Most Downloaded":
        hf_sort = "downloads"
    elif sort == "Newest":
        hf_sort = "createdAt"

    params: dict = {
        "search": query,
        "limit": per_page,
        "sort": hf_sort,
        "direction": -1,
        "full": "true",
        "offset": (current_page - 1) * per_page,
    }

    if model_type == "LORA":
        params["search"] = f"{query} lora".strip()
    elif model_type == "ControlNet":
        params["search"] = f"{query} controlnet".strip()
    elif model_type == "VAE":
        params["search"] = f"{query} vae".strip()

    resp = requests.get(
        f"{_HUGGINGFACE_API}/models",
        params=params,
        headers=_external_api_headers("huggingface"),
        timeout=20,
    )
    resp.raise_for_status()
    raw_items = resp.json() or []
    total_items = None
    try:
        total_header = getattr(resp, "headers", {}).get("x-total-count")
        if total_header is not None:
            total_items = max(0, int(total_header))
    except (TypeError, ValueError):
        total_items = None

    items = []
    for model in raw_items:
        model_id = str(model.get("id") or "")
        files = model.get("siblings") or []
        file_name = _find_primary_huggingface_file(files)
        download_url = _build_huggingface_download_url(model_id, file_name)
        inferred_type = _infer_huggingface_model_type(model)
        if model_type and model_type in _CIVITAI_MODEL_TYPES and inferred_type != model_type:
            continue

        card_data = model.get("cardData") or {}
        base_model = str(card_data.get("base_model") or card_data.get("baseModel") or "")
        items.append(
            {
                "provider": "huggingface",
                "id": model_id,
                "name": model_id,
                "type": inferred_type,
                "creator": model_id.split("/")[0] if "/" in model_id else "",
                "description": str(card_data.get("summary") or card_data.get("description") or "")[:300],
                "rating": float(model.get("likes") or 0),
                "likes": int(model.get("likes") or 0),
                "download_count": int(model.get("downloads") or 0),
                "preview_url": "",
                "version_id": str(model.get("sha") or "")[:12],
                "version_name": str(model.get("sha") or "")[:8] if model.get("sha") else "",
                "base_model": base_model,
                "published_at": str(model.get("createdAt") or ""),
                "is_early_access": False,
                "is_nsfw": any("nsfw" in str(t).lower() for t in (model.get("tags") or [])),
                "file_name": file_name,
                "file_size_bytes": 0,
                "download_url": download_url,
                "model_url": f"https://huggingface.co/{model_id}" if model_id else "",
                "model_type_folder": _preferred_model_folder_for_type(inferred_type),
            }
        )

    has_next = len(raw_items) >= per_page
    return {
        "items": items,
        "total_items": total_items,
        "total_pages": current_page + 1 if has_next else current_page,
        "current_page": current_page,
        "has_next": has_next,
    }


@app.route("/api/models/huggingface/search")
def api_models_huggingface_search():
    """Search Hugging Face repositories for model candidates."""
    query = (request.args.get("query") or "").strip()
    model_type = (request.args.get("type") or "").strip()
    sort = (request.args.get("sort") or "Highest Rated").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        limit = max(1, min(100, int(request.args.get("limit", 20))))
    except (TypeError, ValueError):
        limit = 20

    try:
        results = _huggingface_search(query, model_type, page, sort, limit)
        return jsonify({"ok": True, **results})
    except requests.RequestException as exc:
        logger.error("Hugging Face search failed: %s", exc)
        return jsonify({"ok": False, "error": str(exc), "items": [], "total_items": 0, "total_pages": 1, "current_page": 1}), 502


@app.route("/api/models/huggingface/model/<path:model_id>")
def api_models_huggingface_model(model_id: str):
    """Fetch and sanitize Hugging Face model details for the details modal."""
    safe_model_id = (model_id or "").strip()
    if not safe_model_id:
        return jsonify({"ok": False, "error": "model id required"}), 400

    try:
        resp = requests.get(
            f"{_HUGGINGFACE_API}/models/{safe_model_id}",
            headers=_external_api_headers("huggingface"),
            timeout=20,
        )
        resp.raise_for_status()
        raw = resp.json() or {}
    except requests.RequestException as exc:
        logger.error("Hugging Face model details failed for %s: %s", safe_model_id, exc)
        return jsonify({"ok": False, "error": str(exc)}), 502

    siblings = raw.get("siblings") or []
    primary_file = _find_primary_huggingface_file(siblings)
    files = []
    for sibling in siblings:
        filename = str(sibling.get("rfilename") or "")
        if not filename or not _is_huggingface_model_file(filename):
            continue
        files.append(
            {
                "id": filename,
                "name": filename,
                "size_bytes": 0,
                "type": "Model",
                "format": "",
                "fp": "",
                "primary": filename == primary_file,
                "download_url": _build_huggingface_download_url(safe_model_id, filename),
            }
        )

    card_data = raw.get("cardData") or {}
    tags = raw.get("tags") or []
    defaults = {
        "sampler": "",
        "steps": "",
        "cfg": "",
        "clip_skip": "",
        "base_model": str(card_data.get("base_model") or card_data.get("baseModel") or ""),
        "trained_words": [],
    }

    versions = [
        {
            "id": raw.get("sha") or safe_model_id,
            "name": str(raw.get("sha") or "main")[:12],
            "description": str(card_data.get("description") or card_data.get("summary") or "")[:1200],
            "created_at": raw.get("createdAt") or "",
            "base_model": defaults["base_model"],
            "is_early_access": False,
            "images": [],
            "files": files,
            "defaults": defaults,
        }
    ]

    payload = {
        "ok": True,
        "provider": "huggingface",
        "id": safe_model_id,
        "name": safe_model_id,
        "type": _infer_huggingface_model_type(raw),
        "description": str(card_data.get("description") or card_data.get("summary") or "")[:2000],
        "creator": safe_model_id.split("/")[0] if "/" in safe_model_id else "",
        "tags": tags,
        "stats": {
            "rating": float(raw.get("likes") or 0),
            "downloads": int(raw.get("downloads") or 0),
            "likes": int(raw.get("likes") or 0),
        },
        "versions": versions,
        "model_url": f"https://huggingface.co/{safe_model_id}",
    }
    return jsonify(payload)


@app.route("/api/models/download", methods=["POST"])
def api_models_download():
    """Start downloading a model file into the ComfyUI models directory."""
    body = request.get_json(silent=True) or {}
    provider = str(body.get("provider") or "").strip().lower()
    model_id = (body.get("model_id") or "").strip()
    url = (body.get("url") or "").strip()
    file_name = (body.get("file_name") or "").strip()
    folder_raw = (body.get("folder") or _preferred_model_folder_for_type("Checkpoint")).strip()
    folder = _normalize_model_folder(folder_raw)
    download_headers: dict[str, str] = {}

    if provider == "huggingface":
        try:
            resolved_file_name, resolved_url = _resolve_huggingface_download_target(model_id, preferred_file_name=file_name)
            if not file_name:
                file_name = resolved_file_name
            if not url:
                url = resolved_url
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except requests.RequestException as exc:
            logger.error("Hugging Face download target resolution failed for %s: %s", model_id, exc)
            return jsonify({"error": str(exc)}), 502
        download_headers = _external_api_headers("huggingface")
    elif provider == "civitai":
        download_headers = _external_api_headers("civitai")

    if not download_headers and "civitai.com" in url.lower():
        # Some CivitAI download URLs require auth even when the provider field is absent.
        download_headers = _external_api_headers("civitai")

    if not url:
        return jsonify({"error": "url is required"}), 400
    if not file_name or Path(file_name).name != file_name:
        return jsonify({"error": "invalid file_name"}), 400
    allowed_folders = _STABILITY_MODEL_SUBFOLDERS if _using_shared_models_root() else _COMFY_MODEL_SUBFOLDERS
    if folder is None or folder not in allowed_folders:
        return jsonify({"error": f"folder must be one of: {', '.join(allowed_folders)}"}), 400

    models_root = _comfy_models_root()
    if models_root is None:
        return jsonify({"error": "Set a shared model path or ComfyUI path in Configurations before downloading models"}), 400

    dest_path = _safe_child_path(models_root, folder, file_name)
    if dest_path.exists():
        return jsonify({"error": f"{file_name} already exists in {folder}"}), 409

    _upsert_model_download_metadata(file_name=file_name, folder=folder, body=body, provider=provider, model_id=model_id)

    download_id = f"{int(time.time() * 1000)}-{file_name}"
    state = {
        "id": download_id,
        "provider": provider,
        "file_name": file_name,
        "folder": folder,
        "status": "downloading",
        "downloaded_bytes": 0,
        "total_bytes": 0,
        "error": "",
    }
    with _model_downloads_lock:
        _model_downloads[download_id] = state

    t = threading.Thread(target=_do_download, args=(download_id, url, dest_path, download_headers), daemon=True)
    t.start()
    return jsonify({"ok": True, "download_id": download_id, "file_name": file_name, "folder": folder, "provider": provider})


@app.route("/api/models/download/<download_id>")
def api_models_download_status(download_id: str):
    """Return download progress for a given download_id."""
    with _model_downloads_lock:
        state = _model_downloads.get(download_id)
    if state is None:
        return jsonify({"error": "unknown download_id"}), 404
    return jsonify(state)


@app.route("/api/models/download/<download_id>/cancel", methods=["POST"])
def api_models_download_cancel(download_id: str):
    """Cancel an in-progress download."""
    with _model_downloads_lock:
        state = _model_downloads.get(download_id)
        if state is None:
            return jsonify({"error": "unknown download_id"}), 404
        if state["status"] == "downloading":
            state["status"] = "cancelled"
    return jsonify({"ok": True})


@app.route("/api/models/delete", methods=["POST"])
def api_models_delete_local():
    """Delete a locally installed model file."""
    body = request.get_json(silent=True) or {}
    file_name = (body.get("file_name") or "").strip()
    folder_raw = (body.get("folder") or "").strip()
    folder = _normalize_model_folder(folder_raw)

    if not file_name or Path(file_name).name != file_name:
        return jsonify({"error": "invalid file_name"}), 400
    allowed_folders = _STABILITY_MODEL_SUBFOLDERS if _using_shared_models_root() else _COMFY_MODEL_SUBFOLDERS
    if folder is None or folder not in allowed_folders:
        return jsonify({"error": f"folder must be one of: {', '.join(allowed_folders)}"}), 400

    models_root = _comfy_models_root()
    if models_root is None:
        return jsonify({"error": "Set a shared model path or ComfyUI path in Configurations before managing models"}), 400

    file_path = _safe_child_path(models_root, folder, file_name)
    if not file_path.exists():
        return jsonify({"error": "Model file not found"}), 404

    try:
        file_path.unlink()
    except OSError as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"ok": True, "deleted": file_name})


@app.route("/api/dev/slow-download-source")
def api_dev_slow_download_source():
    """Stream bytes slowly for deterministic local download/cancel testing."""
    def _bounded_int(name: str, default: int, low: int, high: int) -> int:
        raw = (request.args.get(name) or "").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            return default
        return max(low, min(high, value))

    total_bytes = _bounded_int("total_bytes", default=8 * 1024 * 1024, low=1024, high=100 * 1024 * 1024)
    chunk_bytes = _bounded_int("chunk_bytes", default=128 * 1024, low=1024, high=1024 * 1024)
    delay_ms = _bounded_int("delay_ms", default=120, low=0, high=2000)
    delay_seconds = delay_ms / 1000.0

    def generate():
        pattern = b"copilot-slow-download-source-"
        remaining = total_bytes
        while remaining > 0:
            size = min(chunk_bytes, remaining)
            repeats = (size // len(pattern)) + 1
            yield (pattern * repeats)[:size]
            remaining -= size
            if remaining > 0 and delay_seconds > 0:
                time.sleep(delay_seconds)

    return Response(
        stream_with_context(generate()),
        mimetype="application/octet-stream",
        headers={
            "Content-Length": str(total_bytes),
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )

@app.route("/api/status")
def api_status():
    """Return the health status of both inference backends."""

    return jsonify(
        {
            "text": {
                "available": _ollama_available(),
                "url": OLLAMA_BASE_URL,
            },
            "image": {
                "available": _comfy_available(),
                "url": COMFYUI_BASE_URL,
            },
            "service_errors": {
                "ollama": _last_service_errors.get("ollama", ""),
                "comfyui": _last_service_errors.get("comfyui", ""),
            },
        }
    )


@app.route("/api/diagnostics/service-logs")
def api_diagnostics_service_logs():
    """Return tail output for managed service logs and last known launch errors."""
    return jsonify(
        {
            "logs": {
                "ollama": _read_service_log_tail("ollama"),
                "comfyui": _read_service_log_tail("comfyui"),
            },
            "errors": {
                "ollama": _last_service_errors.get("ollama", ""),
                "comfyui": _last_service_errors.get("comfyui", ""),
            },
        }
    )


@app.route("/api/config/services", methods=["GET", "POST"])
def api_config_services():
    """Persist and retrieve local service launch paths."""
    if request.method == "GET":
        return jsonify(_load_service_config())

    body = request.get_json(silent=True) or {}
    config = _save_service_config(
        {
            "ollama_path": body.get("ollama_path"),
            "comfyui_path": body.get("comfyui_path"),
            "shared_models_path": body.get("shared_models_path"),
            "civitai_api_key": body.get("civitai_api_key"),
            "huggingface_api_key": body.get("huggingface_api_key"),
            "default_negative_prompt": body.get("default_negative_prompt"),
        }
    )
    return jsonify({"ok": True, "config": config})


@app.route("/api/config/pick-path", methods=["POST"])
def api_config_pick_path():
    """Open native picker for a service path and return selected value."""
    body = request.get_json(silent=True) or {}
    service = (body.get("service") or "").strip().lower()
    try:
        service_name = _normalize_path_picker_target(service)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    initial_path = str(body.get("initial_path") or "").strip()
    try:
        path = _pick_path_dialog(service_name, initial_path)
        return jsonify({"ok": True, "service": service_name, "path": path})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        logger.error("Path picker failed for %s: %s", service_name, exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/config/migrate-model-folders", methods=["POST"])
def api_config_migrate_model_folders():
    """Move shared model files from legacy Comfy naming to Stability Matrix naming."""
    body = request.get_json(silent=True) or {}
    dry_run = bool(body.get("dry_run", False))
    run_async = bool(body.get("async", False))

    if _resolve_shared_models_root_dir() is None:
        return jsonify({"error": "Set Shared Model Root Path in Configurations before running migration"}), 400

    try:
        if run_async:
            job = _start_migration_job(dry_run=dry_run)
            return jsonify({"ok": True, "job": job}), 202

        result = _migrate_shared_model_folders(dry_run=dry_run)
        return jsonify({"ok": True, **result})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.error("Shared model folder migration failed: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/config/migrate-model-folders/status/<job_id>")
def api_config_migrate_model_folders_status(job_id: str):
    """Return migration job status and progress."""
    with _migration_jobs_lock:
        job = _migration_jobs.get(job_id)
    if not job:
        return jsonify({"error": "unknown migration job id"}), 404
    return jsonify({"ok": True, "job": _migration_job_snapshot(job)})


@app.route("/api/service/<service>/<action>", methods=["POST"])
def api_service_control(service: str, action: str):
    """Start, stop, and restart local inference services from configured paths."""
    try:
        service_name = _normalize_service_name(service)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    action_name = (action or "").strip().lower()
    if action_name not in {"start", "stop", "restart"}:
        return jsonify({"error": "action must be 'start', 'stop', or 'restart'"}), 400

    port = SERVICE_PORTS[service_name]
    config = _load_service_config()

    try:
        if action_name == "start":
            if _service_available(service_name):
                _last_service_errors[service_name] = ""
                return jsonify({"ok": True, "service": service_name, "action": action_name, "status": "already-running"})
            ok, status, pid = _start_configured_service(service_name, config)
            _last_service_errors[service_name] = ""
            return jsonify({"ok": ok, "service": service_name, "action": action_name, "status": status, "pid": pid})

        if action_name == "stop":
            stopped = _kill_process_on_port(port)
            if not stopped:
                proc = _service_processes.get(service_name)
                if proc and proc.poll() is None:
                    proc.terminate()
                    stopped = True
            if stopped:
                _last_service_errors[service_name] = ""
            return jsonify({"ok": True, "service": service_name, "action": action_name, "status": "stopped" if stopped else "not-running"})

        # restart
        _kill_process_on_port(port)
        proc = _service_processes.get(service_name)
        if proc and proc.poll() is None:
            proc.terminate()
        ok, status, pid = _start_configured_service(service_name, config)
        _last_service_errors[service_name] = ""
        return jsonify({"ok": ok, "service": service_name, "action": action_name, "status": status, "pid": pid})
    except ValueError as exc:
        _last_service_errors[service_name] = str(exc)
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        _last_service_errors[service_name] = str(exc)
        logger.error("Service control failed for %s/%s: %s", service_name, action_name, exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/service/comfyui/version", methods=["GET"])
def api_comfyui_version():
    """Get ComfyUI version/commit info."""
    version_info = _get_comfyui_version()
    return jsonify(version_info)


@app.route("/api/service/comfyui/update", methods=["POST"])
def api_comfyui_update():
    """Start a background ComfyUI update (git pull)."""
    try:
        # Check if ComfyUI is running (optional: could stop first)
        if _comfy_available():
            return jsonify({
                "error": "ComfyUI is currently running. Stop it before updating.",
                "suggestion": "Use /api/service/comfyui/stop to stop ComfyUI first"
            }), 409
        
        job = _start_comfyui_update_job()
        return jsonify({"ok": True, "job": job}), 202
    except Exception as exc:
        logger.error("ComfyUI update failed: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/service/comfyui/update-status/<job_id>", methods=["GET"])
def api_comfyui_update_status(job_id: str):
    """Get status of a running ComfyUI update job."""
    with _comfyui_update_jobs_lock:
        job = _comfyui_update_jobs.get(job_id)
    
    if not job:
        return jsonify({"error": f"Job {job_id} not found"}), 404
    
    return jsonify(_comfyui_update_job_snapshot(job))


@app.route("/api/app/restart", methods=["POST"])
def api_app_restart():
    """Trigger a detached app restart sequence via helper script."""
    body = request.get_json(silent=True) or {}
    try:
        port = int(body.get("port", 5000))
    except (TypeError, ValueError):
        return jsonify({"error": "port must be an integer"}), 400

    if port < 1 or port > 65535:
        return jsonify({"error": "port must be between 1 and 65535"}), 400

    try:
        helper_pid = _restart_flask_via_helper(port=port)
        return jsonify({"ok": True, "status": "restarting", "port": port, "helper_pid": helper_pid}), 202
    except Exception as exc:
        logger.error("App restart failed: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/models")
def api_models():
    """List models available in Ollama."""
    models = _list_ollama_models()
    return jsonify({"models": models})


@app.route("/api/image/prompt-suggestions", methods=["POST"])
def api_image_prompt_suggestions():
    """Generate enhanced image prompt suggestions using local Ollama."""
    if not _ollama_available():
        return jsonify({"error": "Ollama is not running. Start Ollama first."}), 503

    body = request.get_json(silent=True) or {}
    fields = {
        "subject": (body.get("subject") or "").strip(),
        "setting": (body.get("setting") or "").strip(),
        "composition": (body.get("composition") or "").strip(),
        "lighting": (body.get("lighting") or "").strip(),
        "style": (body.get("style") or "").strip(),
    }
    missing = [name for name, value in fields.items() if not value]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    model = (body.get("model") or "").strip() or _pick_default_ollama_model()
    if not model:
        return jsonify({"error": "No local Ollama models found. Pull a model first."}), 400

    prompt = (
        "Create 3 enhanced text-to-image prompts using these constraints. "
        "Each prompt must be one line, vivid, and under 55 words. "
        "Do not include explanations, labels, markdown, or numbering.\n\n"
        f"Subject: {fields['subject']}\n"
        f"Setting/Environment: {fields['setting']}\n"
        f"Composition & Framing: {fields['composition']}\n"
        f"Lighting: {fields['lighting']}\n"
        f"Style/Medium: {fields['style']}"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 60,
            "num_predict": 300,
        },
    }

    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=60)
        resp.raise_for_status()
        content = (resp.json() or {}).get("response", "")
        suggestions = _extract_prompt_suggestions(content)
        if not suggestions:
            return jsonify({"error": "No suggestions were generated."}), 502
        return jsonify({"ok": True, "model": model, "suggestions": suggestions})
    except requests.RequestException as exc:
        logger.error("Ollama prompt suggestions failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Stream a generative response from Ollama.

        Request supports core text inference controls.
    """
    body = request.get_json(silent=True) or {}
    model = (body.get("model") or "").strip()
    prompt = (body.get("prompt") or "").strip()
    system = (body.get("system") or "").strip()
    negative_prompt = (body.get("negative_prompt") or "").strip()

    temperature = _clamp_float(float(body.get("temperature", 0.7)), 0.0, 2.0)
    top_p = _clamp_float(float(body.get("top_p", 0.9)), 0.0, 1.0)
    top_k = _clamp_int(int(body.get("top_k", 40)), 1, 1000)
    num_predict = _clamp_int(int(body.get("num_predict", 512)), 1, 4096)
    seed = _coerce_seed(body.get("seed"))

    if not model:
        return jsonify({"error": "model is required"}), 400
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    if not _ollama_available():
        return jsonify({"error": "Ollama is not running. Please install and start Ollama."}), 503

    ollama_payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_predict": num_predict,
            "seed": seed,
        },
    }
    if system:
        ollama_payload["system"] = system
    if negative_prompt:
        ollama_payload["suffix"] = f"\n\nAvoid this style/content: {negative_prompt}"

    def generate():
        try:
            with requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=ollama_payload,
                stream=True,
                timeout=120,
            ) as resp:
                if resp.status_code != 200:
                    error_text = resp.text[:200]
                    yield f"data: {json.dumps({'error': error_text})}\n\n"
                    return

                for raw_line in resp.iter_lines():
                    if not raw_line:
                        continue
                    try:
                        chunk = json.loads(raw_line)
                    except json.JSONDecodeError:
                        continue

                    token = chunk.get("response", "")
                    if token:
                        yield f"data: {json.dumps({'token': token})}\n\n"

                    if chunk.get("done"):
                        yield f"data: {json.dumps({'meta': {'seed': seed, 'temperature': temperature, 'top_p': top_p, 'top_k': top_k, 'num_predict': num_predict}})}\n\n"
                        yield "data: [DONE]\n\n"
                        return

        except requests.exceptions.RequestException as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/image/models")
def api_image_models():
    """List ComfyUI checkpoint names."""
    if not _comfy_available():
        return jsonify({"models": [], "model_details": [], "error": "ComfyUI is not available"}), 503
    models = _image_models()
    model_details = [
        {
            "name": model_name,
            **_image_model_capabilities(model_name),
        }
        for model_name in models
    ]
    return jsonify({"models": models, "model_details": model_details})


@app.route("/api/image/samplers")
def api_image_samplers():
    """List ComfyUI sampler names."""
    if not _comfy_available():
        return jsonify({"samplers": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"samplers": _image_samplers()})


@app.route("/api/image/schedulers")
def api_image_schedulers():
    """List ComfyUI scheduler names."""
    if not _comfy_available():
        return jsonify({"schedulers": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"schedulers": _image_schedulers()})


@app.route("/api/image/lora-models")
def api_image_lora_models():
    """List ComfyUI LoRA names."""
    if not _comfy_available():
        return jsonify({"loras": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"loras": _image_lora_models()})


@app.route("/api/image/vae-models")
def api_image_vae_models():
    """List ComfyUI VAE model names."""
    if not _comfy_available():
        return jsonify({"vaes": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"vaes": _image_vae_models()})


@app.route("/api/image/upscaler-models")
def api_image_upscaler_models():
    """List ComfyUI upscaler model names."""
    if not _comfy_available():
        return jsonify({"models": [], "error": "ComfyUI is not available"}), 503
    data = _comfy_get_object_info("UpscaleModelLoader")
    required = data.get("UpscaleModelLoader", {}).get("input", {}).get("required", {})
    names = required.get("model_name", [[]])
    models = names[0] if names and isinstance(names[0], list) else []
    return jsonify({"models": models})


@app.route("/api/image/refiner-models")
def api_image_refiner_models():
    """List checkpoint models available as refiners (same source as checkpoints)."""
    if not _comfy_available():
        return jsonify({"models": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"models": _image_models()})


@app.route("/api/image/lora-tags")
def api_image_lora_tags():
    """Return trigger words/tags for a given LoRA by reading its sidecar metadata."""
    lora_name = request.args.get("name", "").strip()
    if not lora_name:
        return jsonify({"tags": []})
    return jsonify({"tags": _get_lora_tags(lora_name)})


@app.route("/api/image/controlnet-models")
def api_image_controlnet_models():
    """List ComfyUI ControlNet model names."""
    if not _comfy_available():
        return jsonify({"models": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"models": _image_controlnet_models()})


@app.route("/api/image/upload-image", methods=["POST"])
def api_image_upload_image():
    """Upload an input image to ComfyUI and return the stored filename."""
    if not _comfy_available():
        return jsonify({"error": "ComfyUI is not running. Start ComfyUI first."}), 503
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "image is required"}), 400
    try:
        uploaded_name = _upload_image_to_comfy(image)
        if not uploaded_name:
            return jsonify({"error": "Failed to upload image to ComfyUI"}), 502
        return jsonify({"ok": True, "name": uploaded_name})
    except requests.RequestException as exc:
        logger.error("ComfyUI upload image failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/image/generate", methods=["POST"])
def api_image_generate():
    """Submit a txt2img prompt to ComfyUI queue."""
    if not _comfy_available():
        return jsonify({"error": "ComfyUI is not running. Start ComfyUI first."}), 503

    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    queue_front_raw = body.get("queue_front", False)
    queue_front = str(queue_front_raw).strip().lower() in {"1", "true", "yes", "on"}

    try:
        workflow, meta = _build_txt2img_workflow(body)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid parameters: {exc}"}), 400

    try:
        result = _comfy_submit_prompt(workflow, front=queue_front)
        return jsonify(
            {
                "ok": True,
                "prompt_id": result.get("prompt_id"),
                "number": result.get("number"),
                "meta": meta,
            }
        )
    except requests.RequestException as exc:
        logger.error("ComfyUI txt2img submit failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/image/img2img", methods=["POST"])
def api_image_img2img():
    """Submit an img2img prompt to ComfyUI queue."""
    if not _comfy_available():
        return jsonify({"error": "ComfyUI is not running. Start ComfyUI first."}), 503

    image = request.files.get("image")
    prompt = (request.form.get("prompt") or "").strip()
    if not image:
        return jsonify({"error": "image is required"}), 400
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    body = {
        "prompt": prompt,
        "negative_prompt": request.form.get("negative_prompt", ""),
        "model": request.form.get("model", ""),
        "sampler": request.form.get("sampler", "euler"),
        "lora": request.form.get("lora", ""),
        "lora_strength": request.form.get("lora_strength", 0.8),
        "controlnet_model": request.form.get("controlnet_model", ""),
        "controlnet_image_name": request.form.get("controlnet_image_name", ""),
        "controlnet_weight": request.form.get("controlnet_weight", 1.0),
        "controlnet_start": request.form.get("controlnet_start", 0.0),
        "controlnet_end": request.form.get("controlnet_end", 1.0),
        "scheduler": request.form.get("scheduler", "normal"),
        "seed": request.form.get("seed", ""),
        "steps": request.form.get("steps", DEFAULT_IMAGE_STEPS),
        "cfg": request.form.get("cfg", DEFAULT_IMAGE_CFG),
        "denoise": request.form.get("denoise", DEFAULT_IMAGE_DENOISE),
    }
    queue_front_raw = request.form.get("queue_front", "")
    queue_front = str(queue_front_raw).strip().lower() in {"1", "true", "yes", "on"}

    try:
        uploaded_name = _upload_image_to_comfy(image)
        if not uploaded_name:
            return jsonify({"error": "Failed to upload image to ComfyUI"}), 502
        workflow, meta = _build_img2img_workflow(body, uploaded_name)
        result = _comfy_submit_prompt(workflow, front=queue_front)
        return jsonify(
            {
                "ok": True,
                "prompt_id": result.get("prompt_id"),
                "number": result.get("number"),
                "meta": meta,
            }
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid parameters: {exc}"}), 400
    except requests.RequestException as exc:
        logger.error("ComfyUI img2img submit failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/image/img2img-requeue", methods=["POST"])
def api_image_img2img_requeue():
    """Re-submit an img2img job using an already-uploaded ComfyUI image name (no file upload).

    Used by the prioritize action to move a queued img2img job to the front of the queue
    without requiring the client to re-upload the source image.
    """
    if not _comfy_available():
        return jsonify({"error": "ComfyUI is not running. Start ComfyUI first."}), 503

    body = request.get_json(silent=True) or {}
    image_name = (body.get("image_name") or body.get("image") or "").strip()
    prompt = (body.get("prompt") or "").strip()

    if not image_name:
        return jsonify({"error": "image_name is required"}), 400
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    queue_front_raw = body.get("queue_front", False)
    queue_front = str(queue_front_raw).strip().lower() in {"1", "true", "yes", "on"}

    try:
        workflow, meta = _build_img2img_workflow(body, image_name)
        result = _comfy_submit_prompt(workflow, front=queue_front)
        return jsonify(
            {
                "ok": True,
                "prompt_id": result.get("prompt_id"),
                "number": result.get("number"),
                "meta": meta,
            }
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid parameters: {exc}"}), 400
    except requests.RequestException as exc:
        logger.error("ComfyUI img2img requeue failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/image/queue")
def api_image_queue():
    """Return queue status and completed images for known prompt IDs."""
    if not _comfy_available():
        return jsonify({"running": [], "pending": [], "done": [], "error": "ComfyUI unavailable"}), 503

    prompt_ids_raw = (request.args.get("prompt_ids") or "").strip()
    single_prompt_id = (request.args.get("prompt_id") or "").strip()

    prompt_ids: list[str] = []
    if prompt_ids_raw:
        prompt_ids = [pid.strip() for pid in prompt_ids_raw.split(",") if pid.strip()]
    elif single_prompt_id:
        prompt_ids = [single_prompt_id]

    try:
        queue_resp = requests.get(f"{COMFYUI_BASE_URL}/queue", timeout=10)
        queue_resp.raise_for_status()
        queue_data = queue_resp.json() or {}

        done = []
        for prompt_id in prompt_ids:
            try:
                done_images = _parse_prompt_images(prompt_id)
                if done_images:
                    done.append({"prompt_id": prompt_id, "images": done_images})
            except requests.RequestException:
                continue

        return jsonify(
            {
                "running": queue_data.get("queue_running", []),
                "pending": queue_data.get("queue_pending", []),
                "done": done,
            }
        )
    except requests.RequestException as exc:
        logger.error("ComfyUI queue fetch failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/image/cancel", methods=["POST"])
def api_image_cancel():
    """Best-effort cancellation for a queued/running ComfyUI prompt id."""
    if not _comfy_available():
        return jsonify({"error": "ComfyUI is not running. Start ComfyUI first."}), 503

    body = request.get_json(silent=True) or {}
    prompt_id = (body.get("prompt_id") or "").strip()
    if not prompt_id:
        return jsonify({"error": "prompt_id is required"}), 400

    try:
        cancel_payload = {"delete": [prompt_id]}
        resp = requests.post(f"{COMFYUI_BASE_URL}/queue", json=cancel_payload, timeout=12)
        if resp.status_code >= 400:
            return jsonify({"error": f"ComfyUI cancel failed: {resp.text[:200]}"}), 502
        return jsonify({"ok": True, "prompt_id": prompt_id})
    except requests.RequestException as exc:
        logger.error("ComfyUI cancel failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/image/view")
def api_image_view():
    """Proxy ComfyUI /view image URL params into a stable app endpoint."""
    filename = (request.args.get("filename") or "").strip()
    if not filename:
        return jsonify({"error": "filename is required"}), 400

    params = {
        "filename": filename,
        "subfolder": (request.args.get("subfolder") or "").strip(),
        "type": (request.args.get("type") or "output").strip(),
    }

    try:
        upstream = requests.get(f"{COMFYUI_BASE_URL}/view", params=params, timeout=20)
        upstream.raise_for_status()
        response = Response(upstream.content, mimetype=upstream.headers.get("content-type", "image/png"))
        # ComfyUI output filenames are immutable snapshots, so allow browser caching.
        response.headers["Cache-Control"] = "public, max-age=86400, immutable"
        return response
    except requests.RequestException as exc:
        logger.error("ComfyUI image view failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/api/image/source-image")
def api_image_source_image():
    """Resolve img2img source image filename from ComfyUI history for a prompt."""
    if not _comfy_available():
        return jsonify({"error": "ComfyUI is not available"}), 503

    prompt_id = (request.args.get("prompt_id") or "").strip()
    if not prompt_id:
        return jsonify({"error": "prompt_id is required"}), 400

    try:
        image_name = _parse_prompt_source_image(prompt_id)
    except requests.RequestException as exc:
        logger.error("ComfyUI source image lookup failed: %s", exc)
        return jsonify({"error": str(exc)}), 502

    if not image_name:
        return jsonify({"ok": False, "image": "", "error": "No source image found"}), 404
    return jsonify({"ok": True, "image": image_name})


@app.route("/api/history/img2img-source", methods=["POST"])
def api_history_img2img_source():
    """Backfill missing img2img source image metadata in local history entries."""
    body = request.get_json(silent=True) or {}
    image_name = str(body.get("image") or "").strip()
    if not image_name:
        return jsonify({"error": "image is required"}), 400

    entry_id = str(body.get("entry_id") or "").strip()
    prompt_id = str(body.get("prompt_id") or "").strip()
    if not entry_id and not prompt_id:
        return jsonify({"error": "entry_id or prompt_id is required"}), 400

    entries = _load_history()
    updated = 0

    for entry in entries:
        if str(entry.get("type") or "") != "image":
            continue
        params = entry.get("params") if isinstance(entry.get("params"), dict) else {}
        if str(params.get("mode") or "") != "img2img":
            continue

        entry_match = bool(entry_id and str(entry.get("id") or "") == entry_id)
        prompt_match = bool(prompt_id and str(params.get("prompt_id") or "") == prompt_id)
        if not entry_match and not prompt_match:
            continue

        if str(params.get("image") or "").strip() == image_name:
            continue

        params["image"] = image_name
        entry["params"] = params
        updated += 1
        if entry_match:
            break

    if updated:
        _save_history(entries[:300])
    return jsonify({"ok": True, "updated": updated})


@app.route("/api/image/live-preview")
def api_image_live_preview():
    """Return the newest available image for active prompt IDs, if any."""
    if not _comfy_available():
        return jsonify({"ok": False, "preview": None, "error": "ComfyUI is not running"}), 503

    prompt_ids_raw = (request.args.get("prompt_ids") or "").strip()
    prompt_ids = [pid.strip() for pid in prompt_ids_raw.split(",") if pid.strip()]
    if not prompt_ids:
        return jsonify({"ok": True, "preview": None})

    status_by_prompt_id: dict[str, str] = {}
    try:
        queue_resp = requests.get(f"{COMFYUI_BASE_URL}/queue", timeout=10)
        queue_resp.raise_for_status()
        queue_data = queue_resp.json() or {}
        for row in queue_data.get("queue_running", []):
            if isinstance(row, list) and len(row) > 1 and row[1]:
                status_by_prompt_id[str(row[1])] = "running"
        for row in queue_data.get("queue_pending", []):
            if isinstance(row, list) and len(row) > 1 and row[1]:
                status_by_prompt_id[str(row[1])] = "pending"
    except requests.RequestException as exc:
        logger.warning("ComfyUI queue fetch failed during live preview lookup: %s", exc)

    for prompt_id in prompt_ids:
        try:
            images = _parse_prompt_images(prompt_id)
        except requests.RequestException:
            continue
        if not images:
            continue

        return jsonify(
            {
                "ok": True,
                "preview": {
                    "prompt_id": prompt_id,
                    "status": status_by_prompt_id.get(prompt_id, "unknown"),
                    "image": images[0],
                    "updated_at": int(time.time()),
                },
            }
        )

    return jsonify({"ok": True, "preview": None})


@app.route("/api/image/open-location", methods=["POST"])
def api_image_open_location():
    """Open the generated file location in the OS file explorer."""
    body = request.get_json(silent=True) or {}
    image_ref = _normalize_image_ref(body)

    try:
        image_path = _resolve_comfy_image_path(image_ref)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not image_path.exists():
        return jsonify({"error": "Image file was not found on disk"}), 404

    try:
        if os.name == "nt":
            subprocess.Popen(["explorer", f"/select,{image_path}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(image_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", str(image_path.parent)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        logger.error("Failed to open image location: %s", exc)
        return jsonify({"error": str(exc)}), 500

    return jsonify({"ok": True, "path": str(image_path)})


@app.route("/api/image/delete", methods=["POST"])
def api_image_delete():
    """Delete a generated image file and remove matching references from local history."""
    body = request.get_json(silent=True) or {}
    image_ref = _normalize_image_ref(body)

    try:
        image_path = _resolve_comfy_image_path(image_ref)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not image_path.exists():
        return jsonify({"error": "Image file was not found on disk"}), 404

    try:
        image_path.unlink()
    except OSError as exc:
        logger.error("Failed deleting image file %s: %s", image_path, exc)
        return jsonify({"error": str(exc)}), 500

    removed_refs, removed_entries = _prune_history_image_references(image_ref)
    return jsonify(
        {
            "ok": True,
            "deleted": True,
            "removed_history_refs": removed_refs,
            "removed_history_entries": removed_entries,
        }
    )


@app.route("/api/gallery/bulk-delete", methods=["POST"])
def api_gallery_bulk_delete():
    """Delete multiple gallery images and remove their history entries in one request."""
    body = request.get_json(silent=True) or {}
    image_refs = body.get("image_refs")
    if not isinstance(image_refs, list) or not image_refs:
        return jsonify({"error": "image_refs must be a non-empty list"}), 400

    total_deleted = 0
    total_missing = 0
    total_refs_removed = 0
    total_entries_removed = 0
    errors: list[str] = []

    for raw_ref in image_refs[:200]:  # cap at 200 per request
        if not isinstance(raw_ref, dict):
            continue
        image_ref = _normalize_image_ref(raw_ref)
        try:
            image_path = _resolve_comfy_image_path(image_ref)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if not image_path.exists():
            total_missing += 1
        else:
            try:
                image_path.unlink()
                total_deleted += 1
            except OSError as exc:
                logger.error("Bulk delete failed for %s: %s", image_path, exc)
                errors.append(str(exc))
                continue

        removed_refs, removed_entries = _prune_history_image_references(image_ref)
        total_refs_removed += removed_refs
        total_entries_removed += removed_entries

    return jsonify(
        {
            "ok": True,
            "deleted": total_deleted,
            "missing": total_missing,
            "removed_history_refs": total_refs_removed,
            "removed_history_entries": total_entries_removed,
            "errors": errors,
        }
    )


@app.route("/api/gallery/bulk-export", methods=["POST"])
def api_gallery_bulk_export():
    """Return a ZIP archive containing the requested gallery images."""
    body = request.get_json(silent=True) or {}
    image_refs = body.get("image_refs")
    if not isinstance(image_refs, list) or not image_refs:
        return jsonify({"error": "image_refs must be a non-empty list"}), 400

    buf = io.BytesIO()
    added = 0
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for raw_ref in image_refs[:200]:  # cap at 200 per request
            if not isinstance(raw_ref, dict):
                continue
            image_ref = _normalize_image_ref(raw_ref)
            try:
                image_path = _resolve_comfy_image_path(image_ref)
            except ValueError:
                continue
            if not image_path.exists():
                continue
            arcname = image_path.name
            # Avoid duplicate arc names by appending a counter suffix if needed
            existing = {zi.filename for zi in zf.infolist()}
            stem, ext = os.path.splitext(arcname)
            counter = 1
            while arcname in existing:
                arcname = f"{stem}_{counter}{ext}"
                counter += 1
            zf.write(image_path, arcname)
            added += 1

    if not added:
        return jsonify({"error": "No accessible images found for the given refs"}), 404

    buf.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"gallery_export_{timestamp}.zip"
    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/history", methods=["GET", "POST"])
def api_history():
    """Persist and retrieve local generation history."""
    if request.method == "GET":
        entries = _load_history()
        entry_type = (request.args.get("type") or "").strip()
        limit_raw = (request.args.get("limit") or "").strip()
        if entry_type:
            entries = [e for e in entries if e.get("type") == entry_type]
        if limit_raw:
            try:
                limit = max(1, int(limit_raw))
                entries = entries[:limit]
            except ValueError:
                pass
        return jsonify({"history": entries})

    body = request.get_json(silent=True) or {}
    entry_type = (body.get("type") or "").strip()
    if entry_type not in {"text", "image"}:
        return jsonify({"error": "type must be 'text' or 'image'"}), 400

    item = {
        "type": entry_type,
        "prompt": (body.get("prompt") or "").strip(),
        "negative_prompt": (body.get("negative_prompt") or "").strip(),
        "engine": (body.get("engine") or "").strip(),
        "model": (body.get("model") or "").strip(),
        "params": body.get("params") or {},
        "response": body.get("response") or "",
        "images": body.get("images") or [],
    }
    entry = _append_history(item)
    return jsonify({"ok": True, "entry": entry}), 201


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Local AI Model Interface")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
