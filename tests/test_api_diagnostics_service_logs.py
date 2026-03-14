from pathlib import Path

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    history_file = data_dir / "history.json"
    config_file = data_dir / "service_config.json"
    service_log_dir = data_dir / "service_logs"

    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))
    monkeypatch.setattr(app_module, "HISTORY_FILE", Path(history_file))
    monkeypatch.setattr(app_module, "SERVICE_CONFIG_FILE", Path(config_file))
    monkeypatch.setattr(app_module, "SERVICE_LOG_DIR", Path(service_log_dir))

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_diagnostics_service_logs_defaults_empty(client, monkeypatch):
    monkeypatch.setitem(app_module._last_service_errors, "ollama", "")
    monkeypatch.setitem(app_module._last_service_errors, "comfyui", "")

    resp = client.get("/api/diagnostics/service-logs")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["logs"]["ollama"] == ""
    assert data["logs"]["comfyui"] == ""
    assert data["errors"]["ollama"] == ""
    assert data["errors"]["comfyui"] == ""


def test_diagnostics_service_logs_returns_tail_and_errors(client, monkeypatch):
    app_module.SERVICE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    (app_module.SERVICE_LOG_DIR / "ollama.log").write_text(
        ("A" * 2200) + "\nOLLAMA_TAIL_MARKER",
        encoding="utf-8",
    )
    (app_module.SERVICE_LOG_DIR / "comfyui.log").write_text(
        "ComfyUI started\nCOMFY_TAIL_MARKER",
        encoding="utf-8",
    )

    monkeypatch.setitem(app_module._last_service_errors, "ollama", "ollama launch failed")
    monkeypatch.setitem(app_module._last_service_errors, "comfyui", "")

    resp = client.get("/api/diagnostics/service-logs")

    assert resp.status_code == 200
    data = resp.get_json()
    assert "OLLAMA_TAIL_MARKER" in data["logs"]["ollama"]
    assert "COMFY_TAIL_MARKER" in data["logs"]["comfyui"]
    assert len(data["logs"]["ollama"]) <= 1800
    assert data["errors"]["ollama"] == "ollama launch failed"
    assert data["errors"]["comfyui"] == ""


def test_status_includes_service_errors(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)
    monkeypatch.setitem(app_module._last_service_errors, "ollama", "")
    monkeypatch.setitem(app_module._last_service_errors, "comfyui", "startup traceback")

    resp = client.get("/api/status")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["text"]["available"] is True
    assert data["image"]["available"] is False
    assert data["service_errors"]["ollama"] == ""
    assert data["service_errors"]["comfyui"] == "startup traceback"
