"""Tests for service path configuration and service control endpoints."""
import json
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


def test_api_vault_links_ensure_creates_link_and_registers(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    link_path = tmp_path / "package_src_link"
    target_dir = tmp_path / "vault_target"
    target_dir.mkdir(parents=True, exist_ok=True)

    response = client.post(
        "/api/vault/links/ensure",
        json={
            "package_name": "alpha",
            "link_path": str(link_path),
            "target_path": str(target_dir),
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["result"]["package_name"] == "alpha"
    assert payload["result"]["status"] in {"created", "exists", "registered", "updated"}


def test_api_vault_links_health_reports_unhealthy(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    link_path = tmp_path / "broken_link"
    target_path = tmp_path / "missing_target"
    link_path.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(link_path),
        target_path=str(target_path),
        allow_shared=False,
    )

    response = client.get("/api/vault/links/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["total"] == 1
    assert payload["unhealthy"] == 1
    assert payload["links"][0]["reason"] in {"missing_target_path", "target_mismatch", "missing_link_path"}


def test_api_vault_links_repair_dry_run_does_not_modify(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    link_path = tmp_path / "link_to_fix"
    target_path = tmp_path / "missing_target"
    link_path.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(link_path),
        target_path=str(target_path),
        allow_shared=False,
    )

    response = client.post("/api/vault/links/repair", json={"dry_run": True})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["total_unhealthy"] == 1
    assert payload["repaired"] == 0
    assert payload["actions"][0]["status"] == "would-repair"


def test_api_vault_links_repair_exec_reports_conflict_without_mutation(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    link_path = tmp_path / "existing_dir"
    target_path = tmp_path / "correct_target"
    link_path.mkdir(parents=True, exist_ok=True)
    target_path.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(link_path),
        target_path=str(target_path),
        allow_shared=False,
    )

    response = client.post("/api/vault/links/repair", json={"dry_run": False})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["dry_run"] is False
    assert payload["failed"] == 1
    assert payload["actions"][0]["status"] == "failed"
    assert payload["actions"][0]["error"] == "path_conflict_requires_manual_resolution"


def test_api_vault_links_ensure_requires_fields(client):
    resp = client.post("/api/vault/links/ensure", json={})
    assert resp.status_code == 400
    assert "package_name is required" in resp.get_json()["error"]

    resp = client.post("/api/vault/links/ensure", json={"package_name": "alpha"})
    assert resp.status_code == 400
    assert "link_path is required" in resp.get_json()["error"]

    resp = client.post(
        "/api/vault/links/ensure",
        json={"package_name": "alpha", "link_path": "X:/missing"},
    )
    assert resp.status_code == 400
    assert "target_path is required" in resp.get_json()["error"]


def test_api_vault_links_ensure_conflict_returns_409(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    link_path = tmp_path / "existing_regular_dir"
    target_dir = tmp_path / "vault_target"
    link_path.mkdir(parents=True, exist_ok=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    resp = client.post(
        "/api/vault/links/ensure",
        json={
            "package_name": "alpha",
            "link_path": str(link_path),
            "target_path": str(target_dir),
        },
    )
    assert resp.status_code == 409
    assert "Path conflict" in resp.get_json()["error"]


def test_api_vault_links_health_package_filter(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "alpha-link"),
        target_path=str(tmp_path / "alpha-target"),
        allow_shared=False,
    )
    app_module._register_global_link(
        package_name="beta",
        link_path=str(tmp_path / "beta-link"),
        target_path=str(tmp_path / "beta-target"),
        allow_shared=False,
    )

    resp = client.get("/api/vault/links/health?package=alpha")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["package"] == "alpha"
    assert payload["total"] == 1
    assert payload["links"][0]["package_name"] == "alpha"


def test_api_vault_links_recent_requires_valid_limit(client):
    resp = client.get("/api/vault/links/recent?limit=abc")
    assert resp.status_code == 400
    assert "limit must be an integer" in resp.get_json()["error"]

    resp = client.get("/api/vault/links/recent?limit=0")
    assert resp.status_code == 400
    assert "limit must be between 1 and 500" in resp.get_json()["error"]


def test_api_vault_links_recent_filters_and_limits(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "alpha-link-1"),
        target_path=str(tmp_path / "alpha-target-1"),
        allow_shared=False,
    )
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "alpha-link-2"),
        target_path=str(tmp_path / "alpha-target-2"),
        allow_shared=False,
    )
    app_module._register_global_link(
        package_name="beta",
        link_path=str(tmp_path / "beta-link-1"),
        target_path=str(tmp_path / "beta-target-1"),
        allow_shared=False,
    )

    resp = client.get("/api/vault/links/recent?package=alpha&limit=1")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["package"] == "alpha"
    assert payload["limit"] == 1
    assert payload["count"] == 1
    assert len(payload["links"]) == 1
    assert payload["links"][0]["package_name"] == "alpha"


def test_api_vault_links_stats_aggregate_and_filter(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "alpha-link-1"),
        target_path=str(tmp_path / "alpha-target-1"),
        link_type="symlink",
        allow_shared=False,
    )
    app_module._register_global_link(
        package_name="beta",
        link_path=str(tmp_path / "beta-link-1"),
        target_path=str(tmp_path / "beta-target-1"),
        link_type="junction",
        allow_shared=False,
    )

    resp = client.get("/api/vault/links/stats")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["total"] == 2
    assert payload["packages"]["alpha"] == 1
    assert payload["packages"]["beta"] == 1
    assert payload["link_types"]["symlink"] == 1
    assert payload["link_types"]["junction"] == 1

    scoped = client.get("/api/vault/links/stats?package=alpha")
    assert scoped.status_code == 200
    scoped_payload = scoped.get_json()
    assert scoped_payload["ok"] is True
    assert scoped_payload["package"] == "alpha"
    assert scoped_payload["total"] == 1
    assert scoped_payload["packages"]["alpha"] == 1


def test_api_vault_links_prune_stale_dry_run_default_scope(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    existing_target = tmp_path / "target-ok"
    existing_target.mkdir(parents=True, exist_ok=True)

    # Missing link path (stale candidate by default)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "missing-link"),
        target_path=str(existing_target),
        allow_shared=False,
    )

    # Missing target path (not pruned unless include_missing_target=true)
    existing_link = tmp_path / "existing-link"
    existing_link.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(existing_link),
        target_path=str(tmp_path / "missing-target"),
        allow_shared=False,
    )

    resp = client.post("/api/vault/links/prune-stale", json={"dry_run": True})
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["total_unhealthy"] == 2
    assert payload["considered"] == 1
    assert payload["pruned"] == 0
    statuses = {item["status"] for item in payload["actions"]}
    assert "would_prune" in statuses
    assert "skipped_reason" in statuses


def test_api_vault_links_prune_stale_execute_with_include_missing_target(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    existing_target = tmp_path / "target-ok"
    existing_target.mkdir(parents=True, exist_ok=True)

    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "missing-link"),
        target_path=str(existing_target),
        allow_shared=False,
    )

    existing_link = tmp_path / "existing-link"
    existing_link.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(existing_link),
        target_path=str(tmp_path / "missing-target"),
        allow_shared=False,
    )

    resp = client.post(
        "/api/vault/links/prune-stale",
        json={"dry_run": False, "include_missing_target": True, "package_name": "alpha"},
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["dry_run"] is False
    assert payload["considered"] == 2
    assert payload["pruned"] == 2
    assert payload["failed"] == 0

    health = client.get("/api/vault/links/health?package=alpha").get_json()
    assert health["total"] == 0


def test_api_vault_links_repair_package_filter_limits_actions(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "alpha-link"),
        target_path=str(tmp_path / "alpha-target"),
        allow_shared=False,
    )
    app_module._register_global_link(
        package_name="beta",
        link_path=str(tmp_path / "beta-link"),
        target_path=str(tmp_path / "beta-target"),
        allow_shared=False,
    )

    resp = client.post(
        "/api/vault/links/repair",
        json={"package_name": "beta", "dry_run": True},
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["package"] == "beta"
    assert payload["total_unhealthy"] == 1
    assert len(payload["actions"]) == 1
    assert payload["actions"][0]["package_name"] == "beta"


def test_api_vault_links_unregister_requires_link_path(client):
    resp = client.post("/api/vault/links/unregister", json={})
    assert resp.status_code == 400
    assert "link_path is required" in resp.get_json()["error"]


def test_api_vault_links_unregister_returns_404_for_unknown(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    resp = client.post(
        "/api/vault/links/unregister",
        json={"link_path": str(tmp_path / "missing-link")},
    )
    assert resp.status_code == 404
    assert "Link not found" in resp.get_json()["error"]


def test_api_vault_links_unregister_removes_registry_entry(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    link_path = tmp_path / "alpha-link"
    target_path = tmp_path / "alpha-target"
    link_path.mkdir(parents=True, exist_ok=True)
    target_path.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(link_path),
        target_path=str(target_path),
        allow_shared=False,
    )

    resp = client.post(
        "/api/vault/links/unregister",
        json={"link_path": str(link_path)},
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["result"]["status"] == "unregistered"
    assert payload["result"]["removed_link_path"] is False
    assert app_module._get_registered_link(link_path) == {}


def test_api_vault_links_unregister_remove_link_conflict_returns_409(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    link_path = tmp_path / "beta-link"
    target_path = tmp_path / "beta-target"
    link_path.mkdir(parents=True, exist_ok=True)
    target_path.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="beta",
        link_path=str(link_path),
        target_path=str(target_path),
        allow_shared=False,
    )

    resp = client.post(
        "/api/vault/links/unregister",
        json={"link_path": str(link_path), "remove_link": True},
    )
    assert resp.status_code == 409
    assert "remove_link requested" in resp.get_json()["error"]
    # Registry row remains when link removal fails.
    assert app_module._get_registered_link(link_path) != {}


def test_api_vault_links_unregister_package_requires_name(client):
    resp = client.post("/api/vault/links/unregister-package", json={})
    assert resp.status_code == 400
    assert "package_name is required" in resp.get_json()["error"]


def test_api_vault_links_unregister_package_removes_only_target_package(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "alpha-link-1"),
        target_path=str(tmp_path / "alpha-target-1"),
        allow_shared=False,
    )
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(tmp_path / "alpha-link-2"),
        target_path=str(tmp_path / "alpha-target-2"),
        allow_shared=False,
    )
    app_module._register_global_link(
        package_name="beta",
        link_path=str(tmp_path / "beta-link-1"),
        target_path=str(tmp_path / "beta-target-1"),
        allow_shared=False,
    )

    resp = client.post(
        "/api/vault/links/unregister-package",
        json={"package_name": "alpha", "remove_link": False},
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["package"] == "alpha"
    assert payload["total"] == 2
    assert payload["unregistered"] == 2
    assert payload["failed"] == 0

    alpha_health = client.get("/api/vault/links/health?package=alpha").get_json()
    beta_health = client.get("/api/vault/links/health?package=beta").get_json()
    assert alpha_health["total"] == 0
    assert beta_health["total"] == 1


def test_api_vault_links_unregister_package_remove_link_reports_failures(client, tmp_path, monkeypatch):
    db_path = tmp_path / "link_registry.db"
    monkeypatch.setattr(app_module, "_link_registry_db_path", lambda: db_path)

    # Regular directories are intentionally non-removable by remove_link safety guard.
    link_path = tmp_path / "alpha-link"
    target_path = tmp_path / "alpha-target"
    link_path.mkdir(parents=True, exist_ok=True)
    target_path.mkdir(parents=True, exist_ok=True)
    app_module._register_global_link(
        package_name="alpha",
        link_path=str(link_path),
        target_path=str(target_path),
        allow_shared=False,
    )

    resp = client.post(
        "/api/vault/links/unregister-package",
        json={"package_name": "alpha", "remove_link": True},
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["total"] == 1
    assert payload["unregistered"] == 0
    assert payload["failed"] == 1
    assert payload["results"][0]["status"] == "failed"


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


def test_restart_flask_via_helper_uses_restart_and_wait_script_on_windows(monkeypatch):
    if app_module.os.name != "nt":
        pytest.skip("Windows-specific restart helper invocation")

    seen = {}

    class _Proc:
        pid = 4242

    def fake_popen(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return _Proc()

    monkeypatch.setattr(app_module.subprocess, "Popen", fake_popen)

    helper_pid = app_module._restart_flask_via_helper(port=5007)

    assert helper_pid == 4242
    cmd = " ".join(str(x) for x in seen["args"])
    assert "restart_and_wait.ps1" in cmd
    assert "-Port 5007" in cmd
    assert "-TimeoutSec 45" in cmd


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


def test_resolve_comfyui_launch_adds_cors_header_args_for_main_py(tmp_path):
    comfy_dir = tmp_path / "ComfyUI"
    comfy_dir.mkdir()
    (comfy_dir / "main.py").write_text("print('ok')", encoding="utf-8")

    portable_python = tmp_path / "python_embeded"
    portable_python.mkdir()
    (portable_python / "python.exe").write_text("", encoding="utf-8")

    command, cwd = app_module._resolve_comfyui_launch(str(comfy_dir))

    assert cwd == comfy_dir
    assert command[-2:] == ["--enable-cors-header", "*"]


def test_resolve_comfyui_launch_portable_uses_venv_when_embedded_python_unusable(tmp_path, monkeypatch):
    portable_root = tmp_path / "ComfyUI_windows_portable"
    portable_main_dir = portable_root / "ComfyUI"
    portable_main_dir.mkdir(parents=True)
    (portable_main_dir / "main.py").write_text("print('ok')", encoding="utf-8")

    embedded_py = portable_root / "python_embeded" / "python.exe"
    embedded_py.parent.mkdir(parents=True)
    embedded_py.write_text("", encoding="utf-8")

    venv_py = portable_main_dir / ".venv" / "Scripts" / "python.exe"
    venv_py.parent.mkdir(parents=True)
    venv_py.write_text("", encoding="utf-8")

    monkeypatch.setattr(app_module.os, "name", "nt", raising=False)
    monkeypatch.setattr(app_module, "_is_usable_python_executable", lambda p: False)

    command, cwd = app_module._resolve_comfyui_launch(str(portable_root))

    assert cwd == portable_main_dir
    assert command[0] == str(venv_py)
    assert command[1] == str(portable_main_dir / "main.py")
    assert command[-2:] == ["--enable-cors-header", "*"]


def test_resolve_comfyui_launch_py_file_falls_back_when_embedded_python_unusable(tmp_path, monkeypatch):
    repo_root = tmp_path / "portable"
    comfy_dir = repo_root / "ComfyUI"
    comfy_dir.mkdir(parents=True)
    script_py = comfy_dir / "main.py"
    script_py.write_text("print('ok')", encoding="utf-8")

    embedded_py = repo_root / "python_embeded" / "python.exe"
    embedded_py.parent.mkdir(parents=True)
    embedded_py.write_text("", encoding="utf-8")

    monkeypatch.setattr(app_module.os, "name", "nt", raising=False)
    monkeypatch.setattr(app_module, "_is_usable_python_executable", lambda p: False)

    command, cwd = app_module._resolve_comfyui_launch(str(script_py))

    assert cwd == comfy_dir
    assert command[0] == app_module.sys.executable
    assert command[1] == str(script_py)
    assert command[-2:] == ["--enable-cors-header", "*"]


def test_find_comfyui_python_falls_back_when_sibling_embedded_python_unusable(tmp_path, monkeypatch):
    portable_root = tmp_path / "portable"
    comfy_dir = portable_root / "ComfyUI"
    comfy_dir.mkdir(parents=True)

    embedded_py = portable_root / "python_embeded" / "python.exe"
    embedded_py.parent.mkdir(parents=True)
    embedded_py.write_text("", encoding="utf-8")

    monkeypatch.setattr(app_module.os, "name", "nt", raising=False)
    monkeypatch.setattr(app_module, "_is_usable_python_executable", lambda p: False)

    resolved = app_module._find_comfyui_python(comfy_dir)

    assert resolved == app_module.sys.executable


def test_migration_status_unknown_job_returns_404(client):
    resp = client.get("/api/config/migrate-model-folders/status/unknown-job")
    assert resp.status_code == 404


def test_start_comfyui_install_job_includes_txn_staging_and_journal(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    captured = {}

    class _FakeThread:
        def __init__(self, target=None, args=(), daemon=None):
            captured["target"] = target
            captured["args"] = args
            captured["daemon"] = daemon

        def start(self):
            captured["started"] = True

    monkeypatch.setattr(app_module.threading, "Thread", _FakeThread)

    snapshot = app_module._start_comfyui_install_job(str(tmp_path / "install-root"), "nvidia")

    assert snapshot["id"].startswith("install-")
    assert snapshot["txn_id"].startswith("txn-")
    assert snapshot["staging_dir"].endswith(snapshot["txn_id"])
    assert Path(snapshot["staging_dir"]).exists()
    assert isinstance(snapshot["journal"], list)
    assert snapshot["manifest_path"] == ""
    assert captured.get("started") is True


def test_write_comfyui_install_manifest_persists_file(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    install_path = tmp_path / "ComfyUI_windows_portable"
    comfy_root = install_path / "ComfyUI"
    comfy_root.mkdir(parents=True)
    (comfy_root / "main.py").write_text("print('ok')", encoding="utf-8")
    (comfy_root / "requirements.txt").write_text("requests\n", encoding="utf-8")

    job = {
        "txn_id": "txn-test-123",
        "staging_dir": str(data_dir / "staging" / "txn-test-123"),
        "journal": [{"event": "txn_start", "at": "2026-01-01T00:00:00+00:00", "details": {}}],
    }

    manifest_path = app_module._write_comfyui_install_manifest(
        job=job,
        install_path=install_path,
        comfy_root=comfy_root,
        python_executable="X:/portable/python.exe",
        used_embedded_python=True,
        status="committed",
        error="",
    )

    manifest_file = Path(manifest_path)
    assert manifest_file.exists()
    payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert payload["package"] == "comfyui"
    assert payload["txn_id"] == "txn-test-123"
    assert payload["status"] == "committed"
    assert payload["python_executable"] == "X:/portable/python.exe"
    assert payload["used_embedded_python"] is True
    assert str(comfy_root / "main.py") in payload["files"]


def test_run_comfyui_install_job_writes_error_manifest_on_failure(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    install_path = tmp_path / "install-root"
    job_id = "install-test-fail"
    job = {
        "id": job_id,
        "txn_id": "txn-test-fail",
        "staging_dir": str(data_dir / "staging" / "txn-test-fail"),
        "status": "running",
        "install_path": str(install_path),
        "gpu": "nvidia",
        "log": "",
        "journal": [],
        "manifest_path": "",
        "error": "",
        "started_at": "",
        "finished_at": "",
    }
    app_module._comfyui_install_jobs[job_id] = job

    class _GitFail:
        returncode = 1
        stdout = ""
        stderr = "git missing"

    monkeypatch.setattr(app_module.subprocess, "run", lambda *args, **kwargs: _GitFail())

    app_module._run_comfyui_install_job(job_id)

    assert job["status"] == "error"
    assert job["manifest_path"]
    manifest_payload = json.loads(Path(job["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest_payload["status"] == "error"
    assert any(item.get("event") == "txn_rollback" for item in (job.get("journal") or []))

    app_module._comfyui_install_jobs.pop(job_id, None)


def test_register_global_link_creates_registry_entry(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    link_path = tmp_path / "packages" / "comfyui" / "models" / "checkpoints"
    target_path = tmp_path / "vault" / "checkpoints"

    result = app_module._register_global_link(
        package_name="comfyui",
        link_path=link_path,
        target_path=target_path,
        link_type="junction",
    )

    assert result["status"] == "registered"
    stored = app_module._get_registered_link(link_path)
    assert stored["package_name"] == "comfyui"
    assert stored["link_type"] == "junction"


def test_register_global_link_rejects_same_link_path_different_target(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    link_path = tmp_path / "packages" / "comfyui" / "models" / "checkpoints"
    first_target = tmp_path / "vault" / "checkpoints-a"
    second_target = tmp_path / "vault" / "checkpoints-b"

    app_module._register_global_link("comfyui", link_path, first_target)

    with pytest.raises(ValueError, match="Link path conflict"):
        app_module._register_global_link("comfyui", link_path, second_target)


def test_register_global_link_rejects_double_link_for_same_package_target(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    target = tmp_path / "vault" / "loras"
    link_a = tmp_path / "packages" / "comfyui" / "models" / "loras"
    link_b = tmp_path / "packages" / "comfyui" / "pkg" / "alt-loras"

    app_module._register_global_link("comfyui", link_a, target)

    with pytest.raises(ValueError, match="Double-link conflict"):
        app_module._register_global_link("comfyui", link_b, target)


def test_register_global_link_rejects_cross_package_ownership_without_shared_flag(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    link_path = tmp_path / "packages" / "shared" / "models" / "checkpoints"
    target = tmp_path / "vault" / "checkpoints"

    app_module._register_global_link("comfyui", link_path, target)

    with pytest.raises(ValueError, match="Link ownership conflict"):
        app_module._register_global_link("automatic1111", link_path, target)


def test_register_global_link_allows_shared_when_flag_enabled(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    link_path = tmp_path / "packages" / "shared" / "models" / "checkpoints"
    target = tmp_path / "vault" / "checkpoints"

    app_module._register_global_link("comfyui", link_path, target)
    result = app_module._register_global_link(
        "automatic1111",
        link_path,
        target,
        allow_shared=True,
    )

    assert result["status"] == "updated"
    stored = app_module._get_registered_link(link_path)
    assert stored["package_name"] == "automatic1111"
