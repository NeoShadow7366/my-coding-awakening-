"""Edge-case and error-path regression tests for the backend API."""
import pytest
import requests as req_lib

import app as app_module


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text
        self.headers = {"content-type": "image/png"}
        self.content = b""

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise req_lib.HTTPError(f"status={self.status_code}")


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    history_file = data_dir / "history.json"
    monkeypatch.setattr(app_module, "DATA_DIR", data_dir)
    monkeypatch.setattr(app_module, "HISTORY_FILE", history_file)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# /api/image/queue — upstream ComfyUI request exception → 502
# ---------------------------------------------------------------------------

def test_image_queue_upstream_error_returns_502(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def exploding_get(url, timeout=0, **kwargs):
        raise req_lib.ConnectionError("refused")

    monkeypatch.setattr(app_module.requests, "get", exploding_get)

    resp = client.get("/api/image/queue?prompt_ids=pid-1")

    assert resp.status_code == 502
    assert "refused" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# /api/image/cancel — upstream ComfyUI 4xx → 502 wrapper
# ---------------------------------------------------------------------------

def test_image_cancel_upstream_4xx_returns_502(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def bad_post(url, json=None, timeout=0, **kwargs):
        return DummyResponse(status_code=422, text="Unprocessable")

    monkeypatch.setattr(app_module.requests, "post", bad_post)

    resp = client.post("/api/image/cancel", json={"prompt_id": "pid-bad"})

    assert resp.status_code == 502
    assert "ComfyUI cancel failed" in resp.get_json()["error"]


def test_image_cancel_upstream_exception_returns_502(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def exploding_post(url, json=None, timeout=0, **kwargs):
        raise req_lib.Timeout("timed out")

    monkeypatch.setattr(app_module.requests, "post", exploding_post)

    resp = client.post("/api/image/cancel", json={"prompt_id": "pid-timeout"})

    assert resp.status_code == 502
    assert "timed out" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# /api/history POST — invalid type rejected with 400
# ---------------------------------------------------------------------------

def test_history_invalid_type_returns_400(client):
    resp = client.post("/api/history", json={"type": "video", "prompt": "test"})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "type must be 'text' or 'image'"


def test_history_missing_type_returns_400(client):
    resp = client.post("/api/history", json={"prompt": "no type"})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "type must be 'text' or 'image'"


# ---------------------------------------------------------------------------
# /api/image/view — missing filename → 400, upstream error → 502
# ---------------------------------------------------------------------------

def test_image_view_missing_filename_returns_400(client):
    resp = client.get("/api/image/view")

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "filename is required"


def test_image_view_upstream_error_returns_502(client, monkeypatch):
    def exploding_get(url, params=None, timeout=0, **kwargs):
        raise req_lib.ConnectionError("no route")

    monkeypatch.setattr(app_module.requests, "get", exploding_get)

    resp = client.get("/api/image/view?filename=test.png")

    assert resp.status_code == 502
    assert "no route" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# /api/image/generate — upstream submit error → 502
# ---------------------------------------------------------------------------

def test_image_generate_submit_exception_returns_502(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_build(body):
        return {"1": {}}, {"prompt": body["prompt"]}

    def exploding_submit(workflow, front=False):
        raise req_lib.ConnectionError("comfy down")

    monkeypatch.setattr(app_module, "_build_txt2img_workflow", fake_build)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", exploding_submit)

    resp = client.post("/api/image/generate", json={"prompt": "sunset"})

    assert resp.status_code == 502
    assert "comfy down" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# /api/status — response shape
# ---------------------------------------------------------------------------

def test_status_returns_expected_shape_when_both_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.get("/api/status")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["text"]["available"] is True
    assert data["image"]["available"] is True
    assert "service_errors" in data
    assert "ollama" in data["service_errors"]
    assert "comfyui" in data["service_errors"]


def test_status_reflects_unavailable_backends(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: False)
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/status")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["text"]["available"] is False
    assert data["image"]["available"] is False


# ---------------------------------------------------------------------------
# /api/models — Ollama model list
# ---------------------------------------------------------------------------

def test_models_returns_list_from_ollama(client, monkeypatch):
    fake_models = [{"name": "llama3"}, {"name": "mistral"}]
    monkeypatch.setattr(app_module, "_list_ollama_models", lambda: fake_models)

    resp = client.get("/api/models")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["models"] == fake_models


def test_models_returns_empty_list_when_ollama_down(client, monkeypatch):
    monkeypatch.setattr(app_module, "_list_ollama_models", lambda: [])

    resp = client.get("/api/models")

    assert resp.status_code == 200
    assert resp.get_json()["models"] == []


# ---------------------------------------------------------------------------
# /api/image/models + /api/image/samplers
# ---------------------------------------------------------------------------

def test_image_models_returns_list_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_models", lambda: ["v1-5.safetensors", "xl.safetensors"])

    resp = client.get("/api/image/models")

    assert resp.status_code == 200
    assert resp.get_json()["models"] == ["v1-5.safetensors", "xl.safetensors"]


def test_image_models_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/models")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["models"] == []
    assert "error" in data


def test_image_samplers_returns_list_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_samplers", lambda: ["euler", "dpmpp_2m"])

    resp = client.get("/api/image/samplers")

    assert resp.status_code == 200
    assert resp.get_json()["samplers"] == ["euler", "dpmpp_2m"]


def test_image_samplers_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/samplers")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["samplers"] == []
    assert "error" in data


# ---------------------------------------------------------------------------
# /api/image/view — happy path (proxied image bytes)
# ---------------------------------------------------------------------------

def test_image_view_proxies_bytes_and_mimetype(client, monkeypatch):
    fake_bytes = b"\x89PNG\r\n\x1a\n"  # PNG magic bytes

    class FakeImageResponse:
        status_code = 200
        content = fake_bytes
        headers = {"content-type": "image/png"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(app_module.requests, "get", lambda url, params=None, timeout=0, **kw: FakeImageResponse())

    resp = client.get("/api/image/view?filename=test.png&subfolder=&type=output")

    assert resp.status_code == 200
    assert resp.content_type == "image/png"
    assert resp.data == fake_bytes
    assert "public" in (resp.headers.get("Cache-Control") or "")


# ---------------------------------------------------------------------------
# /api/image/cancel — success path
# ---------------------------------------------------------------------------

def test_image_cancel_success_returns_ok_and_prompt_id(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_post(url, json=None, timeout=0, **kwargs):
        assert json == {"delete": ["pid-xyz"]}
        return DummyResponse(status_code=200)

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    resp = client.post("/api/image/cancel", json={"prompt_id": "pid-xyz"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["prompt_id"] == "pid-xyz"


# ---------------------------------------------------------------------------
# /api/image/source-image — prompt lookup for legacy img2img compare
# ---------------------------------------------------------------------------

def test_image_source_image_requires_prompt_id(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.get("/api/image/source-image")

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "prompt_id is required"


def test_image_source_image_returns_filename_when_found(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_parse_prompt_source_image", lambda prompt_id: "legacy-upload.png")

    resp = client.get("/api/image/source-image?prompt_id=abc-123")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["image"] == "legacy-upload.png"


def test_image_source_image_reads_comfy_history_list_format_via_endpoint(client, monkeypatch):
    prompt_id = "pid-live-shape"
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_history",
        lambda _: {
            prompt_id: {
                "prompt": [
                    17,
                    prompt_id,
                    {
                        "42": {
                            "class_type": "LoadImage",
                            "inputs": {"image": "source-from-history.png"},
                        }
                    },
                ]
            }
        },
    )

    resp = client.get(f"/api/image/source-image?prompt_id={prompt_id}")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["image"] == "source-from-history.png"


def test_history_img2img_source_backfill_updates_matching_prompt(client):
    create = client.post(
        "/api/history",
        json={
            "type": "image",
            "prompt": "legacy img2img",
            "engine": "comfyui",
            "params": {"mode": "img2img", "prompt_id": "pid-legacy"},
            "images": [{"filename": "out.png", "subfolder": "", "type": "output"}],
        },
    )
    assert create.status_code == 201

    patch_resp = client.post(
        "/api/history/img2img-source",
        json={"prompt_id": "pid-legacy", "image": "source-legacy.png"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["updated"] == 1

    history = client.get("/api/history?type=image").get_json()["history"]
    assert history[0]["params"]["image"] == "source-legacy.png"


def test_history_img2img_source_backfill_updates_matching_entry_id_only(client):
    create = client.post(
        "/api/history",
        json={
            "type": "image",
            "prompt": "legacy img2img by id",
            "engine": "comfyui",
            "params": {"mode": "img2img", "prompt_id": "pid-by-id"},
            "images": [{"filename": "out-id.png", "subfolder": "", "type": "output"}],
        },
    )
    assert create.status_code == 201
    entry_id = create.get_json()["entry"]["id"]

    patch_resp = client.post(
        "/api/history/img2img-source",
        json={"entry_id": entry_id, "image": "source-by-id.png"},
    )

    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["updated"] == 1

    history = client.get("/api/history?type=image").get_json()["history"]
    target = next(item for item in history if item["id"] == entry_id)
    assert target["params"]["image"] == "source-by-id.png"


def test_history_img2img_source_backfill_requires_identity_or_prompt(client):
    resp = client.post("/api/history/img2img-source", json={"image": "source.png"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "entry_id or prompt_id is required"


def test_parse_prompt_source_image_supports_comfy_prompt_list_format(monkeypatch):
    prompt_id = "pid-list"
    monkeypatch.setattr(
        app_module,
        "_comfy_history",
        lambda _: {
            prompt_id: {
                "prompt": [
                    1,
                    prompt_id,
                    {
                        "23": {
                            "class_type": "LoadImage",
                            "inputs": {"image": "legacy-source.png"},
                        }
                    },
                ]
            }
        },
    )

    assert app_module._parse_prompt_source_image(prompt_id) == "legacy-source.png"
