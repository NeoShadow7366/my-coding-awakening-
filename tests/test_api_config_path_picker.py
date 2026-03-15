"""Tests for native path picker API endpoint."""
from pathlib import Path

import pytest

import app as app_module


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


def test_pick_path_rejects_unknown_service(client):
    resp = client.post("/api/config/pick-path", json={"service": "unknown"})

    assert resp.status_code == 400
    assert "service must be 'ollama', 'comfyui', or 'models'" in resp.get_json()["error"]


def test_pick_path_returns_selected_path(client, monkeypatch):
    monkeypatch.setattr(app_module, "_pick_path_dialog", lambda service, initial_path='': "C:/Ollama/ollama.exe")

    resp = client.post("/api/config/pick-path", json={"service": "ollama", "initial_path": "C:/"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["service"] == "ollama"
    assert data["path"] == "C:/Ollama/ollama.exe"


def test_pick_path_returns_selected_models_root(client, monkeypatch):
    monkeypatch.setattr(app_module, "_pick_path_dialog", lambda service, initial_path='': "E:/AI/models")

    resp = client.post("/api/config/pick-path", json={"service": "models", "initial_path": "E:/AI"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["service"] == "models"
    assert data["path"] == "E:/AI/models"


def test_pick_path_returns_500_on_runtime_error(client, monkeypatch):
    def raising_picker(service, initial_path=''):
        raise RuntimeError("picker unavailable")

    monkeypatch.setattr(app_module, "_pick_path_dialog", raising_picker)

    resp = client.post("/api/config/pick-path", json={"service": "comfyui"})

    assert resp.status_code == 500
    assert "picker unavailable" in resp.get_json()["error"]
