"""Tests for provider-aware model download behavior."""

from pathlib import Path

import pytest

import app as app_module


class _FakeJsonResponse:
    def __init__(self, payload):
        self._payload = payload
        self.headers = {}

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeStreamResponse:
    def __init__(self, content: bytes):
        self._content = content
        self.headers = {"content-length": str(len(content))}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=0):
        if chunk_size <= 0:
            yield self._content
            return
        for start in range(0, len(self._content), chunk_size):
            yield self._content[start : start + chunk_size]


class _ImmediateThread:
    def __init__(self, target=None, args=None, kwargs=None, daemon=None):
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}

    def start(self):
        if self._target:
            self._target(*self._args, **self._kwargs)


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    history_file = data_dir / "history.json"
    config_file = data_dir / "service_config.json"

    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))
    monkeypatch.setattr(app_module, "HISTORY_FILE", Path(history_file))
    monkeypatch.setattr(app_module, "SERVICE_CONFIG_FILE", Path(config_file))

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_pick_huggingface_download_prefers_model_weights():
    files = [
        {"rfilename": "README.md"},
        {"rfilename": "config.json"},
        {"rfilename": "model.bin"},
        {"rfilename": "model.safetensors"},
    ]

    selected = app_module._pick_huggingface_download_file(files)

    assert selected == "model.safetensors"


def test_api_models_download_huggingface_resolves_and_downloads(client, tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    payload_bytes = b"test-model-bytes"
    observed_calls = []

    def fake_get(url, params=None, headers=None, timeout=0, stream=False):
        observed_calls.append(
            {
                "url": url,
                "headers": dict(headers or {}),
                "stream": bool(stream),
            }
        )
        if url.endswith("/models/author/model-alpha"):
            return _FakeJsonResponse(
                {
                    "id": "author/model-alpha",
                    "siblings": [
                        {"rfilename": "README.md"},
                        {"rfilename": "weights/model.safetensors"},
                        {"rfilename": "model-alpha.safetensors"},
                    ],
                }
            )
        if url.endswith("/resolve/main/model-alpha.safetensors"):
            return _FakeStreamResponse(payload_bytes)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_load_service_config", lambda: {"huggingface_api_key": "hf_test_key"})
    monkeypatch.setattr(app_module.threading, "Thread", _ImmediateThread)
    with app_module._model_downloads_lock:
        app_module._model_downloads.clear()

    resp = client.post(
        "/api/models/download",
        json={
            "provider": "huggingface",
            "model_id": "author/model-alpha",
            "folder": "checkpoints",
        },
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["file_name"] == "model-alpha.safetensors"

    status_resp = client.get(f"/api/models/download/{data['download_id']}")
    assert status_resp.status_code == 200
    status = status_resp.get_json()
    assert status["status"] == "done"
    assert status["provider"] == "huggingface"

    saved_file = models_root / "checkpoints" / "model-alpha.safetensors"
    assert saved_file.exists()
    assert saved_file.read_bytes() == payload_bytes

    assert observed_calls[0]["url"].endswith("/models/author/model-alpha")
    assert observed_calls[0]["headers"].get("Authorization") == "Bearer hf_test_key"
    assert observed_calls[1]["stream"] is True
    assert observed_calls[1]["headers"].get("Authorization") == "Bearer hf_test_key"


def test_api_models_download_huggingface_requires_compatible_file(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: tmp_path / "models")
    monkeypatch.setattr(app_module, "_load_service_config", lambda: {"huggingface_api_key": ""})

    def fake_get(url, params=None, headers=None, timeout=0, stream=False):
        return _FakeJsonResponse(
            {
                "id": "author/metadata-only",
                "siblings": [
                    {"rfilename": "README.md"},
                    {"rfilename": "config.json"},
                    {"rfilename": "tokenizer.json"},
                ],
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.post(
        "/api/models/download",
        json={
            "provider": "huggingface",
            "model_id": "author/metadata-only",
            "folder": "checkpoints",
        },
    )

    assert resp.status_code == 400
    assert "No compatible downloadable model file" in resp.get_json()["error"]


def test_api_models_download_civitai_uses_configured_auth_header(client, tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    payload_bytes = b"civitai-model-bytes"
    observed_calls = []

    def fake_get(url, params=None, headers=None, timeout=0, stream=False):
        observed_calls.append(
            {
                "url": url,
                "headers": dict(headers or {}),
                "stream": bool(stream),
            }
        )
        if "civitai.com/api/download/models/2773071" in url:
            return _FakeStreamResponse(payload_bytes)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_load_service_config", lambda: {"civitai_api_key": "cv_test_key"})
    monkeypatch.setattr(app_module.threading, "Thread", _ImmediateThread)
    with app_module._model_downloads_lock:
        app_module._model_downloads.clear()

    resp = client.post(
        "/api/models/download",
        json={
            "provider": "civitai",
            "model_id": "123",
            "url": "https://civitai.com/api/download/models/2773071",
            "file_name": "hero-style-v2.safetensors",
            "folder": "checkpoints",
        },
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True

    status_resp = client.get(f"/api/models/download/{data['download_id']}")
    assert status_resp.status_code == 200
    status = status_resp.get_json()
    assert status["status"] == "done"
    assert status["provider"] == "civitai"

    saved_file = models_root / "checkpoints" / "hero-style-v2.safetensors"
    assert saved_file.exists()
    assert saved_file.read_bytes() == payload_bytes

    assert observed_calls[0]["stream"] is True
    assert observed_calls[0]["headers"].get("Authorization") == "Bearer cv_test_key"
