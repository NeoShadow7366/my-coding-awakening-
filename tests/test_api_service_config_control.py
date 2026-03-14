"""Tests for service path configuration and service control endpoints."""
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


def test_service_config_get_defaults(client):
    resp = client.get("/api/config/services")

    assert resp.status_code == 200
    assert resp.get_json() == {"ollama_path": "", "comfyui_path": "", "updated_at": ""}


def test_service_config_post_persists_paths(client):
    save_resp = client.post(
        "/api/config/services",
        json={"ollama_path": " C:/Ollama/ollama.exe ", "comfyui_path": " D:/ComfyUI "},
    )
    read_resp = client.get("/api/config/services")

    assert save_resp.status_code == 200
    assert save_resp.get_json()["ok"] is True
    assert save_resp.get_json()["config"]["updated_at"]
    assert read_resp.status_code == 200
    read_data = read_resp.get_json()
    assert read_data["ollama_path"] == "C:/Ollama/ollama.exe"
    assert read_data["comfyui_path"] == "D:/ComfyUI"
    assert read_data["updated_at"]


def test_service_start_requires_configured_path(client, monkeypatch):
    monkeypatch.setattr(app_module, "_service_available", lambda service: False)

    resp = client.post("/api/service/ollama/start")

    assert resp.status_code == 400
    assert "Set an Ollama install path" in resp.get_json()["error"]


def test_service_start_returns_already_running_when_online(client, monkeypatch):
    monkeypatch.setattr(app_module, "_service_available", lambda service: True)

    resp = client.post("/api/service/ollama/start")

    assert resp.status_code == 200
    assert resp.get_json()["status"] == "already-running"


def test_service_stop_reports_stopped_when_port_killed(client, monkeypatch):
    monkeypatch.setattr(app_module, "_kill_process_on_port", lambda port: True)

    resp = client.post("/api/service/comfyui/stop")

    assert resp.status_code == 200
    assert resp.get_json()["status"] == "stopped"


def test_service_restart_starts_with_pid(client, monkeypatch):
    client.post(
        "/api/config/services",
        json={"ollama_path": "C:/Ollama/ollama.exe", "comfyui_path": "D:/ComfyUI"},
    )

    monkeypatch.setattr(app_module, "_kill_process_on_port", lambda port: True)

    def fake_start(service, config):
        assert service == "ollama"
        assert config["ollama_path"] == "C:/Ollama/ollama.exe"
        return True, "started", 4567

    monkeypatch.setattr(app_module, "_start_configured_service", fake_start)

    resp = client.post("/api/service/ollama/restart")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "started"
    assert data["pid"] == 4567


def test_app_restart_returns_202_and_helper_pid(client, monkeypatch):
    monkeypatch.setattr(app_module, "_restart_flask_via_helper", lambda port=5000: 9991)

    resp = client.post("/api/app/restart", json={"port": 5000})

    assert resp.status_code == 202
    data = resp.get_json()
    assert data["ok"] is True
    assert data["status"] == "restarting"
    assert data["port"] == 5000
    assert data["helper_pid"] == 9991


def test_app_restart_rejects_bad_port(client):
    resp = client.post("/api/app/restart", json={"port": "abc"})

    assert resp.status_code == 400
    assert "port must be an integer" in resp.get_json()["error"]


def test_app_restart_reports_helper_error(client, monkeypatch):
    def fail_restart(port=5000):
        raise RuntimeError("helper failed")

    monkeypatch.setattr(app_module, "_restart_flask_via_helper", fail_restart)

    resp = client.post("/api/app/restart", json={"port": 5000})

    assert resp.status_code == 500
    assert "helper failed" in resp.get_json()["error"]
