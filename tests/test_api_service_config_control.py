"""Tests for service path configuration and service control endpoints."""
import time
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
    assert resp.get_json() == {
        "ollama_path": "",
        "comfyui_path": "",
        "shared_models_path": "",
        "civitai_api_key": "",
        "huggingface_api_key": "",
        "default_negative_prompt": "",
        "updated_at": "",
    }


def test_service_config_post_persists_paths(client):
    save_resp = client.post(
        "/api/config/services",
        json={
            "ollama_path": " C:/Ollama/ollama.exe ",
            "comfyui_path": " D:/ComfyUI ",
            "shared_models_path": " E:/AI/models ",
            "civitai_api_key": " civitai-key-123 ",
            "huggingface_api_key": " hf_token_abc ",
        },
    )
    read_resp = client.get("/api/config/services")

    assert save_resp.status_code == 200
    assert save_resp.get_json()["ok"] is True
    assert save_resp.get_json()["config"]["updated_at"]
    assert read_resp.status_code == 200
    read_data = read_resp.get_json()
    assert read_data["ollama_path"] == "C:/Ollama/ollama.exe"
    assert read_data["comfyui_path"] == "D:/ComfyUI"
    assert read_data["shared_models_path"] == "E:/AI/models"
    assert read_data["civitai_api_key"] == "civitai-key-123"
    assert read_data["huggingface_api_key"] == "hf_token_abc"
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


def test_comfy_models_root_prefers_shared_path(client, tmp_path):
    shared_root = tmp_path / "shared-models"
    client.post(
        "/api/config/services",
        json={
            "ollama_path": "C:/Ollama/ollama.exe",
            "comfyui_path": "D:/ComfyUI",
            "shared_models_path": str(shared_root),
        },
    )

    resolved = app_module._comfy_models_root()
    assert resolved == shared_root


def test_shared_models_path_creates_stability_matrix_subfolders(client, tmp_path):
    shared_root = tmp_path / "models-root"

    resp = client.post(
        "/api/config/services",
        json={
            "ollama_path": "C:/Ollama/ollama.exe",
            "comfyui_path": "D:/ComfyUI",
            "shared_models_path": str(shared_root),
        },
    )

    assert resp.status_code == 200
    for folder in ("StableDiffusion", "Lora", "VAE", "Embeddings", "ControlNet", "ESRGAN"):
        assert (shared_root / folder).is_dir()


def test_model_folder_aliases_map_to_stability_names_when_shared(client, tmp_path):
    shared_root = tmp_path / "models-root"
    client.post(
        "/api/config/services",
        json={
            "shared_models_path": str(shared_root),
        },
    )

    assert app_module._normalize_model_folder("checkpoints") == "StableDiffusion"
    assert app_module._normalize_model_folder("loras") == "Lora"
    assert app_module._normalize_model_folder("upscale_models") == "ESRGAN"


def test_migrate_model_folders_requires_shared_root(client):
    resp = client.post("/api/config/migrate-model-folders")

    assert resp.status_code == 400
    assert "Set Shared Model Root Path" in resp.get_json()["error"]


def test_migrate_model_folders_moves_legacy_content(client, tmp_path):
    shared_root = tmp_path / "models-root"
    (shared_root / "checkpoints").mkdir(parents=True)
    (shared_root / "checkpoints" / "legacy.safetensors").write_bytes(b"abc")
    (shared_root / "loras").mkdir(parents=True)
    (shared_root / "loras" / "style.safetensors").write_bytes(b"xyz")

    client.post(
        "/api/config/services",
        json={"shared_models_path": str(shared_root)},
    )

    resp = client.post("/api/config/migrate-model-folders")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["moved_count"] == 2
    assert (shared_root / "StableDiffusion" / "legacy.safetensors").exists()
    assert (shared_root / "Lora" / "style.safetensors").exists()


def test_migrate_model_folders_dry_run_does_not_move_files(client, tmp_path):
    shared_root = tmp_path / "models-root"
    (shared_root / "checkpoints").mkdir(parents=True)
    (shared_root / "checkpoints" / "legacy.safetensors").write_bytes(b"abc")

    client.post("/api/config/services", json={"shared_models_path": str(shared_root)})

    resp = client.post("/api/config/migrate-model-folders", json={"dry_run": True})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["dry_run"] is True
    assert data["moved_count"] == 1
    assert (shared_root / "checkpoints" / "legacy.safetensors").exists()
    assert not (shared_root / "StableDiffusion" / "legacy.safetensors").exists()


def test_migrate_model_folders_async_returns_job_status(client, tmp_path):
    shared_root = tmp_path / "models-root"
    (shared_root / "checkpoints").mkdir(parents=True)
    (shared_root / "checkpoints" / "legacy.safetensors").write_bytes(b"abc")
    client.post("/api/config/services", json={"shared_models_path": str(shared_root)})

    start = client.post("/api/config/migrate-model-folders", json={"async": True})
    assert start.status_code == 202
    job_id = start.get_json()["job"]["id"]

    final = None
    for _ in range(50):
        status = client.get(f"/api/config/migrate-model-folders/status/{job_id}")
        assert status.status_code == 200
        job = status.get_json()["job"]
        if job["status"] in {"done", "error"}:
            final = job
            break
        time.sleep(0.02)

    assert final is not None
    assert final["status"] == "done"
    assert final["result"]["moved_count"] == 1


def test_migration_status_unknown_job_returns_404(client):
    resp = client.get("/api/config/migrate-model-folders/status/unknown-job")
    assert resp.status_code == 404
