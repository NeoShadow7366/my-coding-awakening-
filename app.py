"""Local AI inference UI backend for text and image generation.

The app uses:
- Ollama for local text generation
- ComfyUI for local image generation
"""

import json
import logging
import os
import shlex
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from random import randint

import requests
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

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
_service_processes: dict[str, subprocess.Popen | None] = {
    "ollama": None,
    "comfyui": None,
}
_last_service_errors: dict[str, str] = {
    "ollama": "",
    "comfyui": "",
}


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


def _image_models() -> list[str]:
    """Return available checkpoint names from ComfyUI."""
    data = _comfy_get_object_info("CheckpointLoaderSimple")
    required = data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {})
    names = required.get("ckpt_name", [[]])
    if names and isinstance(names[0], list):
        return names[0]
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
            config["updated_at"] = str(raw.get("updated_at") or "").strip()

        SERVICE_CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=True, indent=2), encoding="utf-8")
        return config


def _save_service_config(config: dict) -> dict:
    _ensure_service_config_store()
    sanitized = {
        "ollama_path": str(config.get("ollama_path") or "").strip(),
        "comfyui_path": str(config.get("comfyui_path") or "").strip(),
        "shared_models_path": str(config.get("shared_models_path") or "").strip(),
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
    if candidate.is_dir():
        # Prefer ComfyUI's bundled launch scripts so it runs in the intended env.
        bat_candidates = ["run_nvidia_gpu.bat", "run_cpu.bat", "run.bat"]
        for bat_name in bat_candidates:
            bat_path = candidate / bat_name
            if bat_path.exists():
                return ["cmd", "/c", str(bat_path)], candidate

        main_py = candidate / "main.py"
        if main_py.exists():
            portable_python = candidate.parent / "python_embeded" / "python.exe"
            if os.name == "nt" and portable_python.exists():
                return [str(portable_python), str(main_py)], candidate
            return [sys.executable, str(main_py)], candidate

        raise ValueError("Configured ComfyUI directory must contain main.py or a run.bat script")

    if candidate.is_file():
        suffix = candidate.suffix.lower()
        if suffix == ".py":
            portable_python = candidate.parent.parent / "python_embeded" / "python.exe"
            if os.name == "nt" and portable_python.exists():
                return [str(portable_python), str(candidate)], candidate.parent
            return [sys.executable, str(candidate)], candidate.parent
        if suffix in {".bat", ".cmd"}:
            return ["cmd", "/c", str(candidate)], candidate.parent
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


def _comfy_submit_prompt(workflow: dict) -> dict:
    """Submit a workflow prompt to ComfyUI and return the raw JSON response."""
    resp = requests.post(
        f"{COMFYUI_BASE_URL}/prompt",
        json={"prompt": workflow},
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
    """Create a minimal txt2img workflow for ComfyUI."""
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
    }

    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": model}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]},
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": batch_size},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
            },
        },
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {
            "class_type": "SaveImage",
            "inputs": {"images": ["6", 0], "filename_prefix": "links-awakening"},
        },
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
    """Create a minimal img2img workflow for ComfyUI."""
    prompt = (body.get("prompt") or "").strip()
    negative = (body.get("negative_prompt") or "").strip()
    model = (body.get("model") or "").strip()
    sampler = (body.get("sampler") or "euler").strip() or "euler"
    scheduler = (body.get("scheduler") or "normal").strip() or "normal"

    seed = _coerce_seed(body.get("seed"))
    steps = _clamp_int(int(body.get("steps", DEFAULT_IMAGE_STEPS)), MIN_STEPS, MAX_STEPS)
    cfg = _clamp_float(float(body.get("cfg", DEFAULT_IMAGE_CFG)), MIN_CFG, MAX_CFG)
    denoise = _clamp_float(float(body.get("denoise", DEFAULT_IMAGE_DENOISE)), 0.05, 1.0)

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
    }

    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": model}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]},
        },
        "4": {"class_type": "LoadImage", "inputs": {"image": uploaded_name}},
        "5": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}},
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "denoise": denoise,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["5", 0],
            },
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": "links-awakening-img2img"},
        },
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

    seen_paths: set[str] = set()
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
                results.append({
                    "name": f.name,
                    "folder": normalized_folder,
                    "size_bytes": f.stat().st_size,
                    "path": str(f),
                })
    results.sort(key=lambda m: (m["folder"], m["name"].lower()))
    return results


def _civitai_search(query: str, model_type: str, page: int) -> dict:
    """Call CivitAI models API and return sanitised results."""
    params: dict = {
        "limit": 20,
        "page": page,
        "sort": "Highest Rated",
        "nsfw": "false",
    }
    if query:
        params["query"] = query
    if model_type and model_type in _CIVITAI_MODEL_TYPES:
        params["types"] = model_type
    resp = requests.get(f"{_CIVITAI_API}/models", params=params, timeout=15)
    resp.raise_for_status()
    raw = resp.json() or {}
    items = []
    for model in raw.get("items", []):
        versions = model.get("modelVersions") or []
        latest = versions[0] if versions else {}
        files = latest.get("files") or []
        primary_file = next((f for f in files if f.get("primary")), files[0] if files else {})
        preview_images = latest.get("images") or []
        preview_url = ""
        for img in preview_images:
            if img.get("nsfwLevel", 0) == 0 or img.get("nsfw") is False:
                preview_url = img.get("url", "")
                break
        items.append({
            "id": model.get("id"),
            "name": model.get("name", ""),
            "type": model.get("type", ""),
            "creator": (model.get("creator") or {}).get("username", ""),
            "description": (model.get("description") or "")[:300],
            "rating": (model.get("stats") or {}).get("rating", 0),
            "download_count": (model.get("stats") or {}).get("downloadCount", 0),
            "preview_url": preview_url,
            "version_id": latest.get("id"),
            "version_name": latest.get("name", ""),
            "file_name": primary_file.get("name", ""),
            "file_size_bytes": primary_file.get("sizeKB", 0) * 1024,
            "download_url": primary_file.get("downloadUrl", ""),
            "model_type_folder": _preferred_model_folder_for_type(model.get("type", "")),
        })
    return {
        "items": items,
        "total_pages": (raw.get("metadata") or {}).get("totalPages", 1),
        "current_page": page,
    }


def _do_download(download_id: str, url: str, dest_path: Path) -> None:
    """Background thread: stream a file from url to dest_path, updating state."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")
    try:
        with requests.get(url, stream=True, timeout=30) as r:
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
        with _model_downloads_lock:
            if download_id in _model_downloads:
                _model_downloads[download_id]["status"] = "error"
                _model_downloads[download_id]["error"] = str(exc)


@app.route("/api/models/library")
def api_models_library():
    """List locally installed ComfyUI model files."""
    models = _scan_local_models()
    root = _comfy_models_root()
    return jsonify({"models": models, "models_root": str(root) if root else None})


@app.route("/api/models/civitai/search")
def api_models_civitai_search():
    """Search CivitAI for models."""
    query = (request.args.get("query") or "").strip()
    model_type = (request.args.get("type") or "").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        results = _civitai_search(query, model_type, page)
        return jsonify({"ok": True, **results})
    except requests.RequestException as exc:
        logger.error("CivitAI search failed: %s", exc)
        return jsonify({"ok": False, "error": str(exc), "items": [], "total_pages": 1, "current_page": 1}), 502


@app.route("/api/models/download", methods=["POST"])
def api_models_download():
    """Start downloading a model file into the ComfyUI models directory."""
    body = request.get_json(silent=True) or {}
    url = (body.get("url") or "").strip()
    file_name = (body.get("file_name") or "").strip()
    folder_raw = (body.get("folder") or _preferred_model_folder_for_type("Checkpoint")).strip()
    folder = _normalize_model_folder(folder_raw)

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

    download_id = f"{int(time.time() * 1000)}-{file_name}"
    state = {
        "id": download_id,
        "file_name": file_name,
        "folder": folder,
        "status": "downloading",
        "downloaded_bytes": 0,
        "total_bytes": 0,
        "error": "",
    }
    with _model_downloads_lock:
        _model_downloads[download_id] = state

    t = threading.Thread(target=_do_download, args=(download_id, url, dest_path), daemon=True)
    t.start()
    return jsonify({"ok": True, "download_id": download_id})


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
        return jsonify({"models": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"models": _image_models()})


@app.route("/api/image/samplers")
def api_image_samplers():
    """List ComfyUI sampler names."""
    if not _comfy_available():
        return jsonify({"samplers": [], "error": "ComfyUI is not available"}), 503
    return jsonify({"samplers": _image_samplers()})


@app.route("/api/image/generate", methods=["POST"])
def api_image_generate():
    """Submit a txt2img prompt to ComfyUI queue."""
    if not _comfy_available():
        return jsonify({"error": "ComfyUI is not running. Start ComfyUI first."}), 503

    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    try:
        workflow, meta = _build_txt2img_workflow(body)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid parameters: {exc}"}), 400

    try:
        result = _comfy_submit_prompt(workflow)
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
        "scheduler": request.form.get("scheduler", "normal"),
        "seed": request.form.get("seed", ""),
        "steps": request.form.get("steps", DEFAULT_IMAGE_STEPS),
        "cfg": request.form.get("cfg", DEFAULT_IMAGE_CFG),
        "denoise": request.form.get("denoise", DEFAULT_IMAGE_DENOISE),
    }

    try:
        uploaded_name = _upload_image_to_comfy(image)
        if not uploaded_name:
            return jsonify({"error": "Failed to upload image to ComfyUI"}), 502
        workflow, meta = _build_img2img_workflow(body, uploaded_name)
        result = _comfy_submit_prompt(workflow)
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
        return Response(upstream.content, mimetype=upstream.headers.get("content-type", "image/png"))
    except requests.RequestException as exc:
        logger.error("ComfyUI image view failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


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
