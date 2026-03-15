"""Tests for CivitAI model details endpoint sanitization."""

import app as app_module


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_civitai_model_details_endpoint_returns_sanitized_fields(monkeypatch):
    raw_payload = {
        "id": 101,
        "name": "Example Model",
        "type": "Checkpoint",
        "description": "model description",
        "creator": {"username": "builder"},
        "stats": {"rating": 4.6, "downloadCount": 1234, "thumbsUpCount": 321},
        "modelVersions": [
            {
                "id": 9001,
                "name": "v2",
                "baseModel": "SDXL 1.0",
                "trainedWords": ["hero", "portrait"],
                "files": [
                    {
                        "id": 1,
                        "name": "example_v2.safetensors",
                        "sizeKB": 2048,
                        "type": "Model",
                        "format": "SafeTensor",
                        "primary": True,
                        "downloadUrl": "https://example.test/file",
                    }
                ],
                "images": [{"url": "https://example.test/preview.png", "nsfwLevel": 0}],
                "meta": {"sampler": "euler", "steps": 30, "cfgScale": 7.0},
            }
        ],
    }

    def fake_get(url, headers=None, timeout=0):
        assert url.endswith("/models/101")
        return _FakeResponse(raw_payload)

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    client = app_module.app.test_client()
    resp = client.get("/api/models/civitai/model/101")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["name"] == "Example Model"
    assert data["creator"] == "builder"
    assert data["stats"]["likes"] == 321
    assert len(data["versions"]) == 1
    assert data["versions"][0]["files"][0]["name"] == "example_v2.safetensors"
    assert data["versions"][0]["defaults"]["sampler"] == "euler"


def test_civitai_model_details_endpoint_handles_upstream_error(monkeypatch):
    def fake_get(url, headers=None, timeout=0):
        raise app_module.requests.RequestException("boom")

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    client = app_module.app.test_client()
    resp = client.get("/api/models/civitai/model/999")

    assert resp.status_code == 502
    data = resp.get_json()
    assert data["ok"] is False
    assert "boom" in data["error"]
