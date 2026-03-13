"""Local AI inference UI backend for text and image generation.

The app uses:
- Ollama for local text generation
- ComfyUI for local image generation
"""

import json
import logging
import os
import threading
import time
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

_history_lock = threading.Lock()


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


def _append_history(item: dict) -> dict:
    entries = _load_history()
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


@app.route("/api/models")
def api_models():
    """List models available in Ollama."""
    models = _list_ollama_models()
    return jsonify({"models": models})


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
