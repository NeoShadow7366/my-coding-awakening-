"""Edge-case and error-path regression tests for the backend API."""
from pathlib import Path

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
    disable_log_file = data_dir / "disable_op_log.json"
    monkeypatch.setattr(app_module, "DATA_DIR", data_dir)
    monkeypatch.setattr(app_module, "HISTORY_FILE", history_file)
    monkeypatch.setattr(app_module, "DISABLE_OP_LOG_FILE", disable_log_file)
    with app_module._disable_op_log_lock:
        app_module._disable_op_log.clear()
        app_module._disable_op_log_loaded = False
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

    def exploding_submit(workflow, front=False):
        raise req_lib.ConnectionError("comfy down")

    monkeypatch.setattr(app_module, "_build_txt2img_workflow", fake_build)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", exploding_submit)

    resp = client.post("/api/image/generate", json={"prompt": "sunset"})

    assert resp.status_code == 502
    assert "comfy down" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# /api/status — response shape
# ---------------------------------------------------------------------------

def test_status_returns_expected_shape_when_both_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.get("/api/status")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["text"]["available"] is True
    assert data["image"]["available"] is True
    assert "service_errors" in data
    assert "ollama" in data["service_errors"]
    assert "comfyui" in data["service_errors"]


def test_status_reflects_unavailable_backends(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: False)
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/status")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["text"]["available"] is False
    assert data["image"]["available"] is False


def test_healthz_returns_expected_shape(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/healthz")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "app" in data
    assert "asset_version" in data["app"]
    assert "template_version" in data["app"]
    assert "started_at" in data["app"]
    assert isinstance(data["app"]["uptime_seconds"], int)
    assert "disable_log_store" in data["app"]
    assert "status" in data["app"]["disable_log_store"]
    assert "count" in data["app"]["disable_log_store"]
    assert "services" in data
    assert data["services"]["text_available"] is True
    assert data["services"]["image_available"] is False


# ---------------------------------------------------------------------------
# /api/models — Ollama model list
# ---------------------------------------------------------------------------

def test_models_returns_list_from_ollama(client, monkeypatch):
    fake_models = [{"name": "llama3"}, {"name": "mistral"}]
    monkeypatch.setattr(app_module, "_list_ollama_models", lambda: fake_models)

    resp = client.get("/api/models")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["models"] == fake_models


def test_models_returns_empty_list_when_ollama_down(client, monkeypatch):
    monkeypatch.setattr(app_module, "_list_ollama_models", lambda: [])

    resp = client.get("/api/models")

    assert resp.status_code == 200
    assert resp.get_json()["models"] == []


# ---------------------------------------------------------------------------
# /api/image/models + /api/image/samplers
# ---------------------------------------------------------------------------

def test_image_models_returns_list_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_models", lambda: ["v1-5.safetensors", "xl.safetensors"])

    resp = client.get("/api/image/models")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["models"] == ["v1-5.safetensors", "xl.safetensors"]
    assert "model_details" in data
    assert isinstance(data["model_details"], list)
    assert data["model_details"][0]["name"] == "v1-5.safetensors"
    assert data["model_details"][0]["family"] in {"sd15", "sdxl", "unknown", "flux"}
    assert "supports_controlnet" in data["model_details"][0]


def test_image_models_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/models")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["models"] == []
    assert data["model_details"] == []
    assert "error" in data


def test_image_models_flux_family_capabilities(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_models", lambda: ["flux1-dev.safetensors"])

    resp = client.get("/api/image/models")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["models"] == ["flux1-dev.safetensors"]
    assert data["model_details"][0]["family"] == "flux"
    assert data["model_details"][0]["supports_refiner"] is False
    assert data["model_details"][0]["supports_vae"] is False
    assert data["model_details"][0]["supports_controlnet"] is False
    assert data["model_details"][0]["supports_hiresfix"] is False
    assert data["model_details"][0]["cfg_max"] == 10
    assert data["model_details"][0]["flux_variant"] == "dev"
    assert data["model_details"][0]["recommended_sampler"] == "euler"
    assert data["model_details"][0]["recommended_scheduler"] == "normal"


def test_image_models_flux_schnell_variant_capabilities(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_models", lambda: ["flux.1-schnell.safetensors"])

    resp = client.get("/api/image/models")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["models"] == ["flux.1-schnell.safetensors"]
    assert data["model_details"][0]["family"] == "flux"
    assert data["model_details"][0]["flux_variant"] == "schnell"
    assert data["model_details"][0]["recommended_sampler"] == "euler"
    assert data["model_details"][0]["recommended_scheduler"] == "simple"


def test_comfy_custom_nodes_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/comfy/custom-nodes")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["nodes"] == []
    assert "error" in data


def test_comfy_custom_nodes_returns_rows_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_custom_nodes",
        lambda include_builtin=False: [
            {
                "type": "MyNode",
                "display_name": "My Node",
                "category": "custom_nodes/tools",
                "python_module": "custom_nodes.my_pack",
                "is_custom": True,
            }
        ] if not include_builtin else [
            {
                "type": "KSampler",
                "display_name": "KSampler",
                "category": "sampling",
                "python_module": "nodes",
                "is_custom": False,
            },
            {
                "type": "MyNode",
                "display_name": "My Node",
                "category": "custom_nodes/tools",
                "python_module": "custom_nodes.my_pack",
                "is_custom": True,
            },
        ],
    )

    resp = client.get("/api/comfy/custom-nodes?include_builtin=1")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["include_builtin"] is True
    assert data["count"] == 2
    assert data["custom_count"] == 1
    assert data["nodes"][0]["type"] == "KSampler"
    assert data["nodes"][1]["type"] == "MyNode"


def test_comfy_custom_node_packages_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/comfy/custom-node-packages")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["packages"] == []
    assert "error" in data


def test_comfy_custom_node_packages_returns_rows_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_custom_node_packages",
        lambda: [
            {"name": "ComfyUI-Manager", "path": "X:/ComfyUI/custom_nodes/ComfyUI-Manager", "enabled": True},
            {"name": "_disabled-pack", "path": "X:/ComfyUI/custom_nodes/_disabled-pack", "enabled": False},
        ],
    )

    resp = client.get("/api/comfy/custom-node-packages")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 2
    assert data["enabled_count"] == 1
    assert data["packages"][0]["name"] == "ComfyUI-Manager"


def test_comfy_custom_node_package_details_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/comfy/custom-node-packages/details?name=ComfyUI-Manager")

    assert resp.status_code == 503
    assert "error" in resp.get_json()


def test_comfy_custom_node_package_details_returns_git_data(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)
    monkeypatch.setattr(
        app_module,
        "_collect_custom_node_package_git_info",
        lambda path: {
            "is_git": True,
            "branch": "main",
            "commit": "abc1234",
            "remote": "https://example.invalid/repo.git",
            "upstream": "origin/main",
            "ahead": 1,
            "behind": 2,
            "dirty": False,
        },
    )

    resp = client.get("/api/comfy/custom-node-packages/details?name=ComfyUI-Manager")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["name"] == "ComfyUI-Manager"
    assert data["git"]["is_git"] is True
    assert data["git"]["branch"] == "main"


def test_comfy_custom_node_package_open_success_windows(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)
    monkeypatch.setattr(app_module.sys, "platform", "win32")

    calls = []

    def _fake_popen(args, **kwargs):
        calls.append(args)

        class _Proc:
            pass

        return _Proc()

    monkeypatch.setattr(app_module.subprocess, "Popen", _fake_popen)

    resp = client.post("/api/comfy/custom-node-packages/open", json={"name": "ComfyUI-Manager"})

    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
    assert calls and calls[0][0] == "explorer"


def test_comfy_custom_node_package_toggle_success(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)
    monkeypatch.setattr(
        app_module,
        "_toggle_custom_node_package_enabled",
        lambda path, enabled: path.parent / (path.name if enabled else f"_{path.name}"),
    )

    resp = client.post("/api/comfy/custom-node-packages/toggle", json={"name": "ComfyUI-Manager", "enabled": False})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["enabled"] is False
    assert data["renamed_to"] == "_ComfyUI-Manager"


def test_comfy_custom_node_package_toggle_conflict_returns_409(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)

    def _raise_conflict(path, enabled):
        raise FileExistsError("Target package folder already exists: ComfyUI-Manager")

    monkeypatch.setattr(app_module, "_toggle_custom_node_package_enabled", _raise_conflict)

    resp = client.post("/api/comfy/custom-node-packages/toggle", json={"name": "_ComfyUI-Manager", "enabled": True})

    assert resp.status_code == 409
    assert "already exists" in resp.get_json()["error"]


def test_comfy_custom_node_package_update_success(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)
    monkeypatch.setattr(
        app_module,
        "_run_custom_node_package_git_pull",
        lambda path: {
            "message": "Already up to date.",
            "git": {
                "is_git": True,
                "branch": "main",
                "commit": "abc1234",
                "remote": "https://example.invalid/repo.git",
                "upstream": "origin/main",
                "ahead": 0,
                "behind": 0,
                "dirty": False,
            },
        },
    )

    resp = client.post("/api/comfy/custom-node-packages/update", json={"name": "ComfyUI-Manager"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["message"] == "Already up to date."
    assert data["git"]["is_git"] is True


def test_comfy_custom_node_package_update_non_git_returns_400(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)

    def _raise_non_git(path):
        raise ValueError("package is not a git repository")

    monkeypatch.setattr(app_module, "_run_custom_node_package_git_pull", _raise_non_git)

    resp = client.post("/api/comfy/custom-node-packages/update", json={"name": "ComfyUI-Manager"})

    assert resp.status_code == 400
    assert "not a git" in resp.get_json()["error"]


def test_comfy_custom_node_packages_bulk_update_all(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_custom_node_packages",
        lambda: [
            {"name": "ComfyUI-Manager", "path": "X:/ComfyUI/custom_nodes/ComfyUI-Manager", "enabled": True},
            {"name": "custom-pack", "path": "X:/ComfyUI/custom_nodes/custom-pack", "enabled": True},
        ],
    )
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)

    def _fake_pull(path):
        if path.name == "custom-pack":
            raise ValueError("package is not a git repository")
        return {"message": "Already up to date.", "git": {"is_git": True}}

    monkeypatch.setattr(app_module, "_run_custom_node_package_git_pull", _fake_pull)

    resp = client.post("/api/comfy/custom-node-packages/bulk", json={"action": "update_all"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["action"] == "update_all"
    assert data["success"] == 1
    assert data["skipped"] == 1
    assert data["failed"] == 0


def test_comfy_custom_node_packages_bulk_disable_non_core(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_custom_node_packages",
        lambda: [
            {"name": "ComfyUI-Manager", "path": "X:/ComfyUI/custom_nodes/ComfyUI-Manager", "enabled": True},
            {"name": "custom-pack", "path": "X:/ComfyUI/custom_nodes/custom-pack", "enabled": True},
            {"name": "_already-off", "path": "X:/ComfyUI/custom_nodes/_already-off", "enabled": False},
        ],
    )
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)

    toggled = []

    def _fake_toggle(path, enabled):
        toggled.append((path.name, enabled))
        return path.parent / f"_{path.name}"

    monkeypatch.setattr(app_module, "_toggle_custom_node_package_enabled", _fake_toggle)

    resp = client.post("/api/comfy/custom-node-packages/bulk", json={"action": "disable_non_core"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["action"] == "disable_non_core"
    assert data["success"] == 1
    assert data["skipped"] == 2
    assert data["failed"] == 0
    assert ("custom-pack", False) in toggled


def test_comfy_custom_node_packages_bulk_disable_non_core_dry_run(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_custom_node_packages",
        lambda: [
            {"name": "ComfyUI-Manager", "path": "X:/ComfyUI/custom_nodes/ComfyUI-Manager", "enabled": True},
            {"name": "custom-pack", "path": "X:/ComfyUI/custom_nodes/custom-pack", "enabled": True},
            {"name": "_already-off", "path": "X:/ComfyUI/custom_nodes/_already-off", "enabled": False},
        ],
    )
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)

    toggled = []

    def _fake_toggle(path, enabled):
        toggled.append((path.name, enabled))
        return path.parent / f"_{path.name}"

    monkeypatch.setattr(app_module, "_toggle_custom_node_package_enabled", _fake_toggle)

    resp = client.post("/api/comfy/custom-node-packages/bulk", json={"action": "disable_non_core", "dry_run": True})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["action"] == "disable_non_core"
    assert data["dry_run"] is True
    assert data["success"] == 1
    assert data["skipped"] == 2
    assert data["failed"] == 0
    assert toggled == []
    preview_rows = [row for row in data["results"] if row.get("would_disable")]
    assert len(preview_rows) == 1
    assert preview_rows[0]["name"] == "custom-pack"


def test_comfy_custom_node_packages_bulk_disable_non_core_selected_names(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_custom_node_packages",
        lambda: [
            {"name": "custom-pack-a", "path": "X:/ComfyUI/custom_nodes/custom-pack-a", "enabled": True},
            {"name": "custom-pack-b", "path": "X:/ComfyUI/custom_nodes/custom-pack-b", "enabled": True},
        ],
    )
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)

    toggled = []

    def _fake_toggle(path, enabled):
        toggled.append((path.name, enabled))
        return path.parent / f"_{path.name}"

    monkeypatch.setattr(app_module, "_toggle_custom_node_package_enabled", _fake_toggle)

    resp = client.post(
        "/api/comfy/custom-node-packages/bulk",
        json={"action": "disable_non_core", "names": ["custom-pack-a"]},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] == 1
    assert data["skipped"] == 1
    assert data["failed"] == 0
    assert toggled == [("custom-pack-a", False)]


def test_comfy_custom_node_packages_bulk_rejects_invalid_names(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post(
        "/api/comfy/custom-node-packages/bulk",
        json={"action": "disable_non_core", "names": "custom-pack-a"},
    )

    assert resp.status_code == 400
    assert "names" in resp.get_json()["error"]


def test_comfy_custom_node_packages_bulk_rejects_invalid_action(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post("/api/comfy/custom-node-packages/bulk", json={"action": "delete_everything"})

    assert resp.status_code == 400
    assert "update_all" in resp.get_json()["error"]


def test_comfy_custom_node_packages_disable_log_endpoint(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    with app_module._disable_op_log_lock:
        app_module._disable_op_log.clear()
        app_module._disable_op_log.append(
            {
                "id": "disable-1",
                "created_at": "2026-03-19T00:00:00+00:00",
                "action": "disable_non_core",
                "summary": {"total": 1, "success": 1, "skipped": 0, "failed": 0},
                "moves": [{"from": "custom-pack", "to": "_custom-pack", "reverted": False, "reverted_at": ""}],
            }
        )

    resp = client.get("/api/comfy/custom-node-packages/disable-log")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["total"] == 1
    assert len(data["entries"]) == 1
    assert data["entries"][0]["id"] == "disable-1"
    assert data["entries"][0]["pending_revert_count"] == 1


def test_comfy_custom_node_packages_disable_log_persists_to_disk(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_custom_node_packages",
        lambda: [
            {"name": "custom-pack-a", "enabled": True, "path": "X:/ComfyUI/custom_nodes/custom-pack-a"},
            {"name": "ComfyUI-Manager", "enabled": True, "path": "X:/ComfyUI/custom_nodes/ComfyUI-Manager"},
        ],
    )
    monkeypatch.setattr(app_module, "_resolve_custom_node_package_path", lambda name: Path("X:/ComfyUI/custom_nodes") / name)
    monkeypatch.setattr(app_module, "_toggle_custom_node_package_enabled", lambda path, enabled: path.parent / f"_{path.name}")

    resp = client.post(
        "/api/comfy/custom-node-packages/bulk",
        json={"action": "disable_non_core", "names": ["custom-pack-a"]},
    )

    assert resp.status_code == 200
    disk_raw = app_module.DISABLE_OP_LOG_FILE.read_text(encoding="utf-8")
    disk_entries = app_module.json.loads(disk_raw)
    assert isinstance(disk_entries, list)
    assert len(disk_entries) == 1
    assert disk_entries[0]["action"] == "disable_non_core"
    assert disk_entries[0]["moves"][0]["from"] == "custom-pack-a"
    assert disk_entries[0]["moves"][0]["to"] == "_custom-pack-a"


def test_comfy_custom_node_packages_revert_last_disable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    with app_module._disable_op_log_lock:
        app_module._disable_op_log.clear()
        app_module._disable_op_log.append(
            {
                "id": "disable-2",
                "created_at": "2026-03-19T00:00:00+00:00",
                "action": "disable_non_core",
                "summary": {"total": 1, "success": 1, "skipped": 0, "failed": 0},
                "moves": [{"from": "custom-pack", "to": "_custom-pack", "reverted": False, "reverted_at": ""}],
            }
        )

    monkeypatch.setattr(
        app_module,
        "_resolve_custom_node_package_path",
        lambda name: Path("X:/ComfyUI/custom_nodes") / name if name == "_custom-pack" else None,
    )

    def _fake_toggle(path, enabled):
        assert path.name == "_custom-pack"
        assert enabled is True
        return path.parent / "custom-pack"

    monkeypatch.setattr(app_module, "_toggle_custom_node_package_enabled", _fake_toggle)

    resp = client.post("/api/comfy/custom-node-packages/revert-last-disable", json={})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["batch_id"] == "disable-2"
    assert data["success"] == 1
    assert data["failed"] == 0
    assert data["pending_revert_count"] == 0


def test_comfy_custom_node_packages_revert_disable_batch_by_id(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    with app_module._disable_op_log_lock:
        app_module._disable_op_log.clear()
        app_module._disable_op_log.append(
            {
                "id": "disable-3",
                "created_at": "2026-03-19T00:00:00+00:00",
                "action": "disable_non_core",
                "summary": {"total": 1, "success": 1, "skipped": 0, "failed": 0},
                "moves": [{"from": "custom-pack", "to": "_custom-pack", "reverted": False, "reverted_at": ""}],
            }
        )

    monkeypatch.setattr(
        app_module,
        "_resolve_custom_node_package_path",
        lambda name: Path("X:/ComfyUI/custom_nodes") / name if name == "_custom-pack" else None,
    )
    monkeypatch.setattr(app_module, "_toggle_custom_node_package_enabled", lambda path, enabled: path.parent / "custom-pack")

    resp = client.post("/api/comfy/custom-node-packages/revert-disable-batch", json={"batch_id": "disable-3"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["batch_id"] == "disable-3"
    assert data["success"] == 1
    assert data["failed"] == 0


def test_comfy_custom_node_packages_revert_disable_batch_requires_id(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post("/api/comfy/custom-node-packages/revert-disable-batch", json={})

    assert resp.status_code == 400
    assert "batch_id" in resp.get_json()["error"]


def test_image_samplers_returns_list_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_samplers", lambda: ["euler", "dpmpp_2m"])

    resp = client.get("/api/image/samplers")

    assert resp.status_code == 200
    assert resp.get_json()["samplers"] == ["euler", "dpmpp_2m"]


def test_image_samplers_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/samplers")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["samplers"] == []
    assert "error" in data


def test_image_schedulers_returns_list_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_schedulers", lambda: ["normal", "karras", "exponential"])

    resp = client.get("/api/image/schedulers")

    assert resp.status_code == 200
    assert resp.get_json()["schedulers"] == ["normal", "karras", "exponential"]


def test_image_schedulers_returns_503_when_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/schedulers")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["schedulers"] == []
    assert "error" in data


def test_image_schedulers_fallback_when_comfy_returns_empty(client, monkeypatch):
    """_image_schedulers() returns a sensible fallback list when ComfyUI metadata is empty."""
    monkeypatch.setattr(app_module, "_comfy_get_object_info", lambda node: {})

    result = app_module._image_schedulers()

    assert isinstance(result, list)
    assert len(result) > 0
    assert "normal" in result


# ---------------------------------------------------------------------------
# /api/image/flux-components
# ---------------------------------------------------------------------------

def test_flux_components_returns_all_when_available(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_flux_clip_vae_components",
        lambda: {"t5": "t5xxl_fp8_e4m3fn.safetensors", "clip_l": "clip_l.safetensors", "vae": "ae.safetensors"},
    )

    resp = client.get("/api/image/flux-components")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["t5"] == "t5xxl_fp8_e4m3fn.safetensors"
    assert data["clip_l"] == "clip_l.safetensors"
    assert data["vae"] == "ae.safetensors"
    assert data["ready"] is True


def test_flux_components_returns_503_when_comfy_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/flux-components")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["ok"] is False
    assert "error" in data


def test_flux_components_ready_false_when_t5_missing(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_flux_clip_vae_components",
        lambda: {"t5": None, "clip_l": "clip_l.safetensors", "vae": "ae.safetensors"},
    )

    resp = client.get("/api/image/flux-components")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["t5"] is None
    assert data["ready"] is False


# ---------------------------------------------------------------------------
# /api/image/view — happy path (proxied image bytes)
# ---------------------------------------------------------------------------

def test_image_view_proxies_bytes_and_mimetype(client, monkeypatch):
    fake_bytes = b"\x89PNG\r\n\x1a\n"  # PNG magic bytes

    class FakeImageResponse:
        status_code = 200
        content = fake_bytes
        headers = {"content-type": "image/png"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(app_module.requests, "get", lambda url, params=None, timeout=0, **kw: FakeImageResponse())

    resp = client.get("/api/image/view?filename=test.png&subfolder=&type=output")

    assert resp.status_code == 200
    assert resp.content_type == "image/png"
    assert resp.data == fake_bytes
    assert "public" in (resp.headers.get("Cache-Control") or "")


# ---------------------------------------------------------------------------
# /api/image/cancel — success path
# ---------------------------------------------------------------------------

def test_image_cancel_success_returns_ok_and_prompt_id(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_post(url, json=None, timeout=0, **kwargs):
        assert json == {"delete": ["pid-xyz"]}
        return DummyResponse(status_code=200)

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    resp = client.post("/api/image/cancel", json={"prompt_id": "pid-xyz"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["prompt_id"] == "pid-xyz"


# ---------------------------------------------------------------------------
# /api/image/source-image — prompt lookup for legacy img2img compare
# ---------------------------------------------------------------------------

def test_image_source_image_requires_prompt_id(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.get("/api/image/source-image")

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "prompt_id is required"


def test_image_source_image_returns_filename_when_found(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_parse_prompt_source_image", lambda prompt_id: "legacy-upload.png")

    resp = client.get("/api/image/source-image?prompt_id=abc-123")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["image"] == "legacy-upload.png"


def test_image_source_image_reads_comfy_history_list_format_via_endpoint(client, monkeypatch):
    prompt_id = "pid-live-shape"
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module,
        "_comfy_history",
        lambda _: {
            prompt_id: {
                "prompt": [
                    17,
                    prompt_id,
                    {
                        "42": {
                            "class_type": "LoadImage",
                            "inputs": {"image": "source-from-history.png"},
                        }
                    },
                ]
            }
        },
    )

    resp = client.get(f"/api/image/source-image?prompt_id={prompt_id}")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["image"] == "source-from-history.png"


def test_history_img2img_source_backfill_updates_matching_prompt(client):
    create = client.post(
        "/api/history",
        json={
            "type": "image",
            "prompt": "legacy img2img",
            "engine": "comfyui",
            "params": {"mode": "img2img", "prompt_id": "pid-legacy"},
            "images": [{"filename": "out.png", "subfolder": "", "type": "output"}],
        },
    )
    assert create.status_code == 201

    patch_resp = client.post(
        "/api/history/img2img-source",
        json={"prompt_id": "pid-legacy", "image": "source-legacy.png"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["updated"] == 1

    history = client.get("/api/history?type=image").get_json()["history"]
    assert history[0]["params"]["image"] == "source-legacy.png"


def test_history_img2img_source_backfill_updates_matching_entry_id_only(client):
    create = client.post(
        "/api/history",
        json={
            "type": "image",
            "prompt": "legacy img2img by id",
            "engine": "comfyui",
            "params": {"mode": "img2img", "prompt_id": "pid-by-id"},
            "images": [{"filename": "out-id.png", "subfolder": "", "type": "output"}],
        },
    )
    assert create.status_code == 201
    entry_id = create.get_json()["entry"]["id"]

    patch_resp = client.post(
        "/api/history/img2img-source",
        json={"entry_id": entry_id, "image": "source-by-id.png"},
    )

    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["updated"] == 1

    history = client.get("/api/history?type=image").get_json()["history"]
    target = next(item for item in history if item["id"] == entry_id)
    assert target["params"]["image"] == "source-by-id.png"


def test_history_img2img_source_backfill_requires_identity_or_prompt(client):
    resp = client.post("/api/history/img2img-source", json={"image": "source.png"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "entry_id or prompt_id is required"


def test_parse_prompt_source_image_supports_comfy_prompt_list_format(monkeypatch):
    prompt_id = "pid-list"
    monkeypatch.setattr(
        app_module,
        "_comfy_history",
        lambda _: {
            prompt_id: {
                "prompt": [
                    1,
                    prompt_id,
                    {
                        "23": {
                            "class_type": "LoadImage",
                            "inputs": {"image": "legacy-source.png"},
                        }
                    },
                ]
            }
        },
    )

    assert app_module._parse_prompt_source_image(prompt_id) == "legacy-source.png"
