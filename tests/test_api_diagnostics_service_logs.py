from pathlib import Path

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    history_file = data_dir / "history.json"
    config_file = data_dir / "service_config.json"
    disable_log_file = data_dir / "disable_op_log.json"
    service_log_dir = data_dir / "service_logs"

    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))
    monkeypatch.setattr(app_module, "HISTORY_FILE", Path(history_file))
    monkeypatch.setattr(app_module, "SERVICE_CONFIG_FILE", Path(config_file))
    monkeypatch.setattr(app_module, "DISABLE_OP_LOG_FILE", Path(disable_log_file))
    monkeypatch.setattr(app_module, "SERVICE_LOG_DIR", Path(service_log_dir))
    with app_module._disable_op_log_lock:
        app_module._disable_op_log.clear()
        app_module._disable_op_log_loaded = False

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


def test_diagnostics_repair_disable_log_uses_memory_when_file_invalid(client):
    app_module.DISABLE_OP_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    app_module.DISABLE_OP_LOG_FILE.write_text("{not-json", encoding="utf-8")

    with app_module._disable_op_log_lock:
        app_module._disable_op_log[:] = [
            {
                "id": "disable-repair-1",
                "created_at": "2026-03-19T00:00:00+00:00",
                "action": "disable_non_core",
                "summary": {"total": 1, "success": 1, "skipped": 0, "failed": 0},
                "moves": [{"from": "custom-pack", "to": "_custom-pack", "reverted": False, "reverted_at": ""}],
            }
        ]
        app_module._disable_op_log_loaded = True

    resp = client.post("/api/diagnostics/repair-disable-log", json={})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["status"] == "repaired-from-memory"
    assert data["source"] == "memory"
    assert data["count"] == 1

    raw = app_module.json.loads(app_module.DISABLE_OP_LOG_FILE.read_text(encoding="utf-8"))
    assert isinstance(raw, list)
    assert len(raw) == 1
    assert raw[0]["id"] == "disable-repair-1"


def test_diagnostics_repair_disable_log_clears_invalid_file_when_memory_empty(client):
    app_module.DISABLE_OP_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    app_module.DISABLE_OP_LOG_FILE.write_text("{still-not-json", encoding="utf-8")

    with app_module._disable_op_log_lock:
        app_module._disable_op_log.clear()
        app_module._disable_op_log_loaded = False

    resp = client.post("/api/diagnostics/repair-disable-log", json={})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["source"] == "empty"
    assert data["count"] == 0

    raw = app_module.json.loads(app_module.DISABLE_OP_LOG_FILE.read_text(encoding="utf-8"))
    assert raw == []
