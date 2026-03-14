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

SERVICE_PORTS = {
    "ollama": 11434,
    "comfyui": 8188,
}

_history_lock = threading.Lock()
_service_config_lock = threading.Lock()
_service_processes: dict[str, subprocess.Popen | None] = {
    "ollama": None,
    "comfyui": None,
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
    try:
        resp = requests.get(f"{COMFYUI_BASE_URL}/system_stats", timeout=2)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
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
            config["updated_at"] = str(raw.get("updated_at") or "").strip()

        SERVICE_CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=True, indent=2), encoding="utf-8")
        return config


def _save_service_config(config: dict) -> dict:
    _ensure_service_config_store()
    sanitized = {
        "ollama_path": str(config.get("ollama_path") or "").strip(),
        "comfyui_path": str(config.get("comfyui_path") or "").strip(),
        "updated_at": _service_config_timestamp(),
    }
    with _service_config_lock:
        SERVICE_CONFIG_FILE.write_text(json.dumps(sanitized, ensure_ascii=True, indent=2), encoding="utf-8")
    return sanitized


def _normalize_service_name(name: str) -> str:
    value = (name or "").strip().lower()
    if value not in SERVICE_PORTS:
        raise ValueError("service must be 'ollama' or 'comfyui'")
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
        main_py = candidate / "main.py"
        if main_py.exists():
            return [sys.executable, str(main_py)], candidate

        bat_candidates = ["run_nvidia_gpu.bat", "run_cpu.bat", "run.bat"]
        for bat_name in bat_candidates:
            bat_path = candidate / bat_name
            if bat_path.exists():
                return ["cmd", "/c", str(bat_path)], candidate

        raise ValueError("Configured ComfyUI directory must contain main.py or a run.bat script")

    if candidate.is_file():
        suffix = candidate.suffix.lower()
        if suffix == ".py":
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


def _spawn_service_process(command: list[str], cwd: Path | None = None) -> subprocess.Popen:
    kwargs = {
        "cwd": str(cwd) if cwd else None,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
        "start_new_session": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(command, **kwargs)


def _start_configured_service(service: str, config: dict) -> tuple[bool, str, int | None]:
    if service == "ollama":
        path_value = config.get("ollama_path") or ""
        if not path_value:
            raise ValueError("Set an Ollama install path in Configurations before launching.")
        command, cwd = _resolve_ollama_launch(path_value)
    else:
        path_value = config.get("comfyui_path") or ""
        if not path_value:
            raise ValueError("Set a ComfyUI install path in Configurations before launching.")
        command, cwd = _resolve_comfyui_launch(path_value)

    proc = _spawn_service_process(command, cwd=cwd)
    _service_processes[service] = proc
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
        }
    )
    return jsonify({"ok": True, "config": config})


@app.route("/api/config/pick-path", methods=["POST"])
def api_config_pick_path():
    """Open native picker for a service path and return selected value."""
    body = request.get_json(silent=True) or {}
    service = (body.get("service") or "").strip().lower()
    try:
        service_name = _normalize_service_name(service)
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
                return jsonify({"ok": True, "service": service_name, "action": action_name, "status": "already-running"})
            ok, status, pid = _start_configured_service(service_name, config)
            return jsonify({"ok": ok, "service": service_name, "action": action_name, "status": status, "pid": pid})

        if action_name == "stop":
            stopped = _kill_process_on_port(port)
            if not stopped:
                proc = _service_processes.get(service_name)
                if proc and proc.poll() is None:
                    proc.terminate()
                    stopped = True
            return jsonify({"ok": True, "service": service_name, "action": action_name, "status": "stopped" if stopped else "not-running"})

        # restart
        _kill_process_on_port(port)
        proc = _service_processes.get(service_name)
        if proc and proc.poll() is None:
            proc.terminate()
        ok, status, pid = _start_configured_service(service_name, config)
        return jsonify({"ok": ok, "service": service_name, "action": action_name, "status": status, "pid": pid})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
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
