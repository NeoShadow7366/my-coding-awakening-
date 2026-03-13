"""
Local AI Model Web Interface
-----------------------------
Backend server for running and interacting with local AI models.

Two model types are supported:
  - Generative AI  : text generation via Ollama (runs LLMs like Llama, Mistral locally)
  - Discriminative : text classification via Hugging Face Transformers

Run with:
    python app.py

Then open http://localhost:5000 in your browser.
"""

import json
import logging
import os
import threading

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

# Discriminative model identifier (Hugging Face Hub model name).
CLASSIFIER_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

# ---------------------------------------------------------------------------
# Discriminative model (loaded once at startup in a background thread so the
# server is immediately responsive even while the model downloads).
# ---------------------------------------------------------------------------
_classifier = None
_classifier_lock = threading.Lock()
_classifier_ready = False
_classifier_error: str | None = None


def _load_classifier() -> None:
    """Load a lightweight sentiment / zero-shot classification pipeline."""
    global _classifier, _classifier_ready, _classifier_error
    try:
        from transformers import pipeline

        logger.info("Loading discriminative model (%s)…", CLASSIFIER_MODEL)
        # This small model (~250 MB) classifies text as POSITIVE / NEGATIVE.
        _classifier = pipeline(
            "sentiment-analysis",
            model=CLASSIFIER_MODEL,
            truncation=True,
        )
        with _classifier_lock:
            _classifier_ready = True
        logger.info("Discriminative model ready.")
    except Exception as exc:
        with _classifier_lock:
            _classifier_error = str(exc)
        logger.error("Failed to load discriminative model: %s", exc)


# Start loading the classifier in a daemon thread so it doesn't block startup.
threading.Thread(target=_load_classifier, daemon=True).start()


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


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Main interface page."""
    return render_template("index.html", classifier_model=CLASSIFIER_MODEL)


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------

@app.route("/api/status")
def api_status():
    """Return the health status of both AI backends."""
    with _classifier_lock:
        disc_ready = _classifier_ready
        disc_error = _classifier_error

    return jsonify(
        {
            "generative": {
                "available": _ollama_available(),
                "url": OLLAMA_BASE_URL,
            },
            "discriminative": {
                "ready": disc_ready,
                "error": disc_error,
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

    Request JSON:
      {
        "model":  "llama3",          // Ollama model name
        "prompt": "Hello, world!",   // User prompt
        "system": "You are helpful." // (optional) system message
      }

    Response: newline-delimited JSON stream (Server-Sent Events style).
    Each line is: data: {"token": "…"}\n\n
    Last line is:  data: [DONE]\n\n
    """
    body = request.get_json(silent=True) or {}
    model = (body.get("model") or "").strip()
    prompt = (body.get("prompt") or "").strip()
    system = (body.get("system") or "").strip()

    if not model:
        return jsonify({"error": "model is required"}), 400
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    if not _ollama_available():
        return jsonify({"error": "Ollama is not running. Please install and start Ollama."}), 503

    ollama_payload: dict = {"model": model, "prompt": prompt, "stream": True}
    if system:
        ollama_payload["system"] = system

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


@app.route("/api/classify", methods=["POST"])
def api_classify():
    """
    Classify text using the discriminative model.

    Request JSON:
      {
        "text": "The movie was absolutely fantastic!"
      }

    Response JSON:
      {
        "label": "POSITIVE",
        "score": 0.9998,
        "model": "distilbert-base-uncased-finetuned-sst-2-english"
      }
    """
    with _classifier_lock:
        ready = _classifier_ready
        error = _classifier_error

    if not ready:
        if error:
            return jsonify({"error": f"Model failed to load: {error}"}), 503
        return jsonify({"error": "Discriminative model is still loading, please wait."}), 503

    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()

    if not text:
        return jsonify({"error": "text is required"}), 400

    if len(text) > 512:
        return jsonify({"error": "text must be 512 characters or fewer"}), 400

    try:
        results = _classifier(text)
        top = results[0]
        return jsonify(
            {
                "label": top["label"],
                "score": round(top["score"], 4),
                "model": CLASSIFIER_MODEL,
            }
        )
    except Exception as exc:
        logger.error("Classification error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Local AI Model Interface")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
