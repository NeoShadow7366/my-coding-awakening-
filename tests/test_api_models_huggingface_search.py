"""Tests for Hugging Face model search and details endpoints."""

from pathlib import Path

import pytest

import app as app_module


class _FakeResponse:
    def __init__(self, payload, headers=None):
        self._payload = payload
        self.headers = headers or {}

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


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


def test_huggingface_search_maps_results(monkeypatch):
    calls = []

    def fake_get(url, params=None, headers=None, timeout=0):
        calls.append({"url": url, "params": dict(params or {}), "headers": dict(headers or {})})
        return _FakeResponse(
            [
                {
                    "id": "author/model-one",
                    "likes": 12,
                    "downloads": 345,
                    "createdAt": "2024-01-01T00:00:00Z",
                    "tags": ["lora", "diffusers"],
                    "siblings": [{"rfilename": "model-one.safetensors"}],
                    "cardData": {"summary": "sample", "base_model": "SDXL 1.0"},
                    "sha": "abcdef1234567890",
                }
            ]
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    monkeypatch.setattr(app_module, "_load_service_config", lambda: {"huggingface_api_key": "hf_123"})

    result = app_module._huggingface_search("anime", "LORA", 1, "Most Downloaded")

    assert len(calls) == 1
    assert calls[0]["params"]["sort"] == "downloads"
    assert calls[0]["headers"]["Authorization"] == "Bearer hf_123"
    assert result["items"][0]["provider"] == "huggingface"
    assert result["items"][0]["type"] == "LORA"
    assert result["items"][0]["download_url"].endswith("model-one.safetensors")


def test_huggingface_search_passes_limit_and_offset(monkeypatch):
    calls = []

    def fake_get(url, params=None, headers=None, timeout=0):
        calls.append({"url": url, "params": dict(params or {})})
        return _FakeResponse([])

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._huggingface_search("anime", "", 2, "Highest Rated", limit=60)

    assert len(calls) == 1
    assert calls[0]["params"]["limit"] == 60
    assert calls[0]["params"]["offset"] == 60
    assert result["current_page"] == 2


def test_huggingface_search_exposes_total_items_from_header(monkeypatch):
    def fake_get(url, params=None, headers=None, timeout=0):
        return _FakeResponse(
            [
                {
                    "id": "author/model-total",
                    "likes": 1,
                    "downloads": 2,
                    "createdAt": "2024-01-01T00:00:00Z",
                    "tags": [],
                    "siblings": [{"rfilename": "model-total.safetensors"}],
                    "cardData": {},
                    "sha": "abcdef",
                }
            ],
            headers={"x-total-count": "512"},
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._huggingface_search("sdxl", "", 1, "Highest Rated", limit=20)

    assert result["total_items"] == 512


def test_huggingface_model_details_endpoint(client, monkeypatch):
    def fake_get(url, headers=None, timeout=0):
        assert url.endswith("/models/author/model-two")
        return _FakeResponse(
            {
                "id": "author/model-two",
                "likes": 44,
                "downloads": 555,
                "createdAt": "2024-02-02T00:00:00Z",
                "tags": ["controlnet"],
                "sha": "112233445566",
                "siblings": [{"rfilename": "controlnet.safetensors"}],
                "cardData": {"description": "details"},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.get("/api/models/huggingface/model/author%2Fmodel-two")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["provider"] == "huggingface"
    assert data["type"] == "ControlNet"
    assert data["versions"][0]["files"][0]["name"] == "controlnet.safetensors"


def test_huggingface_model_details_filters_non_model_repo_files(client, monkeypatch):
    def fake_get(url, headers=None, timeout=0):
        assert url.endswith("/models/author/model-three")
        return _FakeResponse(
            {
                "id": "author/model-three",
                "likes": 8,
                "downloads": 21,
                "createdAt": "2024-03-03T00:00:00Z",
                "tags": ["checkpoint"],
                "sha": "abcdef123456",
                "siblings": [
                    {"rfilename": ".gitattributes"},
                    {"rfilename": "README.md"},
                    {"rfilename": "text_encoder/model.fp16.safetensors"},
                    {"rfilename": "model-three.safetensors"},
                ],
                "cardData": {"description": "details"},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.get("/api/models/huggingface/model/author%2Fmodel-three")

    assert resp.status_code == 200
    data = resp.get_json()
    files = data["versions"][0]["files"]
    assert [file["name"] for file in files] == ["model-three.safetensors"]
    assert files[0]["primary"] is True
