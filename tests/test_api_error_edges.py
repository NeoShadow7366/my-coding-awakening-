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

    def exploding_submit(workflow):
        raise req_lib.ConnectionError("comfy down")

    monkeypatch.setattr(app_module, "_build_txt2img_workflow", fake_build)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", exploding_submit)

    resp = client.post("/api/image/generate", json={"prompt": "sunset"})

    assert resp.status_code == 502
    assert "comfy down" in resp.get_json()["error"]
