from pathlib import Path

import pytest

import app as app_module


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise app_module.requests.HTTPError(f"status={self.status_code}")


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    history_file = data_dir / "history.json"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))
    monkeypatch.setattr(app_module, "HISTORY_FILE", Path(history_file))
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_image_queue_unavailable_returns_503(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/queue")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["running"] == []
    assert data["pending"] == []
    assert data["done"] == []
    assert "ComfyUI unavailable" in data["error"]


def test_image_queue_returns_done_for_prompt_ids(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_get(url, timeout=0, **kwargs):
        assert url.endswith("/queue")
        assert timeout == 10
        return DummyResponse(
            payload={
                "queue_running": [[1, "pid-run"]],
                "queue_pending": [[2, "pid-pend"]],
            }
        )

    def fake_parse_prompt_images(prompt_id):
        if prompt_id == "pid-done":
            return [{"filename": "img.png", "subfolder": "", "type": "output"}]
        return []

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    monkeypatch.setattr(app_module, "_parse_prompt_images", fake_parse_prompt_images)

    resp = client.get("/api/image/queue?prompt_ids=pid-done,pid-empty")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["running"] == [[1, "pid-run"]]
    assert data["pending"] == [[2, "pid-pend"]]
    assert data["done"] == [
        {
            "prompt_id": "pid-done",
            "images": [{"filename": "img.png", "subfolder": "", "type": "output"}],
        }
    ]


def test_image_queue_transient_parse_error_is_skipped_per_prompt(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_get(url, timeout=0, **kwargs):
        assert url.endswith("/queue")
        assert timeout == 10
        return DummyResponse(payload={"queue_running": [], "queue_pending": []})

    def fake_parse_prompt_images(prompt_id):
        if prompt_id == "pid-error":
            raise app_module.requests.RequestException("temporary parse failure")
        if prompt_id == "pid-done":
            return [{"filename": "ok.png", "subfolder": "", "type": "output"}]
        return []

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    monkeypatch.setattr(app_module, "_parse_prompt_images", fake_parse_prompt_images)

    resp = client.get("/api/image/queue?prompt_ids=pid-error,pid-done")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["running"] == []
    assert data["pending"] == []
    assert data["done"] == [
        {
            "prompt_id": "pid-done",
            "images": [{"filename": "ok.png", "subfolder": "", "type": "output"}],
        }
    ]


def test_image_queue_retry_returns_done_after_transient_parse_failure(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    parse_calls = {"pid-retry": 0}

    def fake_get(url, timeout=0, **kwargs):
        assert url.endswith("/queue")
        assert timeout == 10
        return DummyResponse(payload={"queue_running": [], "queue_pending": []})

    def fake_parse_prompt_images(prompt_id):
        if prompt_id != "pid-retry":
            return []
        parse_calls["pid-retry"] += 1
        if parse_calls["pid-retry"] == 1:
            raise app_module.requests.RequestException("history not ready")
        return [{"filename": "retry.png", "subfolder": "", "type": "output"}]

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    monkeypatch.setattr(app_module, "_parse_prompt_images", fake_parse_prompt_images)

    first = client.get("/api/image/queue?prompt_ids=pid-retry")
    second = client.get("/api/image/queue?prompt_ids=pid-retry")

    assert first.status_code == 200
    assert first.get_json()["done"] == []

    assert second.status_code == 200
    assert second.get_json()["done"] == [
        {
            "prompt_id": "pid-retry",
            "images": [{"filename": "retry.png", "subfolder": "", "type": "output"}],
        }
    ]


def test_image_cancel_requires_prompt_id(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post("/api/image/cancel", json={})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "prompt_id is required"


def test_image_cancel_posts_delete_payload(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    seen = {}

    def fake_post(url, json=None, timeout=0, **kwargs):
        seen["url"] = url
        seen["json"] = json
        seen["timeout"] = timeout
        return DummyResponse(status_code=200, payload={"ok": True})

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    resp = client.post("/api/image/cancel", json={"prompt_id": "pid-123"})

    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True, "prompt_id": "pid-123"}
    assert seen["url"].endswith("/queue")
    assert seen["json"] == {"delete": ["pid-123"]}
    assert seen["timeout"] == 12


def test_history_text_entry_stored_and_retrieved(client):
    text_entry = {
        "type": "text",
        "prompt": "Tell me a story",
        "model": "llama3",
        "response": "Once upon a time...",
    }

    post_resp = client.post("/api/history", json=text_entry)
    assert post_resp.status_code == 201

    get_resp = client.get("/api/history?type=text")
    assert get_resp.status_code == 200
    history = get_resp.get_json()["history"]
    assert len(history) == 1
    assert history[0]["prompt"] == "Tell me a story"
    assert history[0]["type"] == "text"


def test_history_type_and_limit_filters(client):
    image_entry = {
        "type": "image",
        "prompt": "img",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "m1",
        "params": {"steps": 20},
        "images": [{"filename": "a.png", "subfolder": "", "type": "output"}],
    }
    text_entry = {
        "type": "text",
        "prompt": "hello",
        "negative_prompt": "",
        "engine": "ollama",
        "model": "m2",
        "params": {"temperature": 0.7},
        "response": "world",
    }

    r1 = client.post("/api/history", json=image_entry)
    r2 = client.post("/api/history", json=text_entry)
    r3 = client.post("/api/history", json={**image_entry, "prompt": "img-2"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 201

    resp = client.get("/api/history?type=image&limit=1")

    assert resp.status_code == 200
    history = resp.get_json()["history"]
    assert len(history) == 1
    assert history[0]["type"] == "image"
    assert history[0]["prompt"] == "img-2"


def test_history_dedupes_image_entries_by_prompt_id_and_images(client):
    base_entry = {
        "type": "image",
        "prompt": "castle",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "model-a",
        "params": {"prompt_id": "pid-123", "steps": 20, "cfg": 7},
        "images": [{"filename": "out-1.png", "subfolder": "", "type": "output"}],
    }

    first = client.post("/api/history", json=base_entry)
    duplicate = client.post(
        "/api/history",
        json={
            **base_entry,
            "prompt": "Image generation",
            "model": "",
            "params": {"prompt_id": "pid-123", "steps": 0, "cfg": 0},
        },
    )

    assert first.status_code == 201
    assert duplicate.status_code == 201

    resp = client.get("/api/history?type=image")
    history = resp.get_json()["history"]

    assert len(history) == 1
    assert history[0]["prompt"] == "castle"
    assert history[0]["model"] == "model-a"
    assert history[0]["params"]["prompt_id"] == "pid-123"


def test_history_duplicate_image_entry_upgrades_placeholder_metadata(client):
    placeholder = {
        "type": "image",
        "prompt": "Image generation",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "",
        "params": {"prompt_id": "pid-upgrade", "steps": 0, "cfg": 0, "sampler": ""},
        "images": [{"filename": "out-upgrade.png", "subfolder": "", "type": "output"}],
    }
    richer = {
        "type": "image",
        "prompt": "Detailed castle matte painting",
        "negative_prompt": "blurry",
        "engine": "comfyui",
        "model": "model-b",
        "params": {"prompt_id": "pid-upgrade", "steps": 30, "cfg": 7, "sampler": "euler"},
        "images": [{"filename": "out-upgrade.png", "subfolder": "", "type": "output"}],
    }

    first = client.post("/api/history", json=placeholder)
    second = client.post("/api/history", json=richer)

    assert first.status_code == 201
    assert second.status_code == 201

    resp = client.get("/api/history?type=image")
    history = resp.get_json()["history"]

    assert len(history) == 1
    assert history[0]["prompt"] == "Detailed castle matte painting"
    assert history[0]["negative_prompt"] == "blurry"
    assert history[0]["model"] == "model-b"
    assert history[0]["params"]["steps"] == 30
    assert history[0]["params"]["cfg"] == 7
    assert history[0]["params"]["sampler"] == "euler"


def test_image_open_location_requires_resolvable_path(client, monkeypatch):
    def fail_resolve(_):
        raise ValueError("Set a ComfyUI path in Configurations")

    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", fail_resolve)

    resp = client.post("/api/image/open-location", json={"filename": "x.png"})

    assert resp.status_code == 400
    assert "Set a ComfyUI path" in resp.get_json()["error"]


def test_image_open_location_success_windows_uses_explorer_select(client, monkeypatch, tmp_path):
    image_path = tmp_path / "open-me.png"
    image_path.write_bytes(b"png")

    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: image_path)
    monkeypatch.setattr(app_module.os, "name", "nt", raising=False)

    seen = {}

    def fake_popen(args, stdout=None, stderr=None):
        seen["args"] = args
        seen["stdout"] = stdout
        seen["stderr"] = stderr
        return object()

    monkeypatch.setattr(app_module.subprocess, "Popen", fake_popen)

    resp = client.post("/api/image/open-location", json={"filename": "open-me.png", "subfolder": "", "type": "output"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["path"] == str(image_path)
    assert seen["args"][0] == "explorer"
    assert seen["args"][1] == f"/select,{image_path}"


def test_image_open_location_success_linux_uses_xdg_open_parent(client, monkeypatch, tmp_path):
    image_path = tmp_path / "folder" / "open-linux.png"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(b"png")

    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: image_path)
    monkeypatch.setattr(app_module.os, "name", "posix", raising=False)
    monkeypatch.setattr(app_module.sys, "platform", "linux", raising=False)

    seen = {}

    def fake_popen(args, stdout=None, stderr=None):
        seen["args"] = args
        seen["stdout"] = stdout
        seen["stderr"] = stderr
        return object()

    monkeypatch.setattr(app_module.subprocess, "Popen", fake_popen)

    resp = client.post("/api/image/open-location", json={"filename": "open-linux.png", "subfolder": "folder", "type": "output"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["path"] == str(image_path)
    assert seen["args"] == ["xdg-open", str(image_path.parent)]


def test_image_open_location_returns_404_when_file_missing(client, monkeypatch, tmp_path):
    missing_path = tmp_path / "missing.png"
    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: missing_path)

    resp = client.post("/api/image/open-location", json={"filename": "missing.png", "subfolder": "", "type": "output"})

    assert resp.status_code == 404
    assert "not found on disk" in resp.get_json()["error"]


def test_image_open_location_launcher_failure_returns_500(client, monkeypatch, tmp_path):
    image_path = tmp_path / "open-fail.png"
    image_path.write_bytes(b"png")

    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: image_path)
    monkeypatch.setattr(app_module.os, "name", "nt", raising=False)

    def explode_popen(*args, **kwargs):
        raise OSError("explorer unavailable")

    monkeypatch.setattr(app_module.subprocess, "Popen", explode_popen)

    resp = client.post("/api/image/open-location", json={"filename": "open-fail.png", "subfolder": "", "type": "output"})

    assert resp.status_code == 500
    assert "explorer unavailable" in resp.get_json()["error"]


def test_image_delete_removes_file_and_history_refs(client, monkeypatch, tmp_path):
    image_path = tmp_path / "to-delete.png"
    image_path.write_bytes(b"png")

    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda image_ref: image_path)

    image_entry = {
        "type": "image",
        "prompt": "img",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "m1",
        "params": {"steps": 20},
        "images": [{"filename": "to-delete.png", "subfolder": "", "type": "output"}],
    }
    keep_entry = {
        "type": "image",
        "prompt": "keep",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "m2",
        "params": {"steps": 20},
        "images": [{"filename": "keep.png", "subfolder": "", "type": "output"}],
    }

    assert client.post("/api/history", json=image_entry).status_code == 201
    assert client.post("/api/history", json=keep_entry).status_code == 201

    resp = client.post("/api/image/delete", json={"filename": "to-delete.png", "subfolder": "", "type": "output"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["deleted"] is True
    assert data["removed_history_refs"] == 1
    assert data["removed_history_entries"] == 1
    assert not image_path.exists()

    history_resp = client.get("/api/history?type=image")
    history = history_resp.get_json()["history"]
    assert len(history) == 1
    assert history[0]["prompt"] == "keep"


def test_image_delete_prunes_all_matching_refs_across_entries(client, monkeypatch, tmp_path):
    image_path = tmp_path / "shared.png"
    image_path.write_bytes(b"png")

    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda image_ref: image_path)

    shared_ref = {"filename": "shared.png", "subfolder": "", "type": "output"}
    entry_a = {
        "type": "image",
        "prompt": "entry-a",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "m1",
        "params": {"steps": 20},
        "images": [shared_ref],
    }
    entry_b = {
        "type": "image",
        "prompt": "entry-b",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "m2",
        "params": {"steps": 20},
        "images": [shared_ref],
    }
    keep_entry = {
        "type": "image",
        "prompt": "keep",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "m3",
        "params": {"steps": 20},
        "images": [{"filename": "keep.png", "subfolder": "", "type": "output"}],
    }

    assert client.post("/api/history", json=entry_a).status_code == 201
    assert client.post("/api/history", json=entry_b).status_code == 201
    assert client.post("/api/history", json=keep_entry).status_code == 201

    resp = client.post("/api/image/delete", json=shared_ref)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["deleted"] is True
    assert data["removed_history_refs"] == 2
    assert data["removed_history_entries"] == 2
    assert not image_path.exists()

    history_resp = client.get("/api/history?type=image")
    history = history_resp.get_json()["history"]
    assert len(history) == 1
    assert history[0]["prompt"] == "keep"


def test_image_delete_returns_404_when_file_missing(client, monkeypatch, tmp_path):
    missing_path = tmp_path / "ghost.png"
    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: missing_path)

    resp = client.post("/api/image/delete", json={"filename": "ghost.png", "subfolder": "", "type": "output"})

    assert resp.status_code == 404
    assert "not found on disk" in resp.get_json()["error"]


def test_image_delete_returns_500_on_unlink_oserror(client, monkeypatch, tmp_path):
    import pathlib

    image_path = tmp_path / "locked.png"
    image_path.write_bytes(b"png")
    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: image_path)

    def explode_unlink(self, *args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(pathlib.Path, "unlink", explode_unlink)

    resp = client.post("/api/image/delete", json={"filename": "locked.png", "subfolder": "", "type": "output"})

    assert resp.status_code == 500
    assert "permission denied" in resp.get_json()["error"]


def test_image_open_location_success_macos_uses_open_r(client, monkeypatch, tmp_path):
    image_path = tmp_path / "art.png"
    image_path.write_bytes(b"png")
    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: image_path)
    monkeypatch.setattr(app_module.os, "name", "posix", raising=False)
    monkeypatch.setattr(app_module.sys, "platform", "darwin", raising=False)

    captured = {}

    def fake_popen(cmd, **kwargs):
        captured["cmd"] = cmd

    monkeypatch.setattr(app_module.subprocess, "Popen", fake_popen)

    resp = client.post("/api/image/open-location", json={"filename": "art.png", "subfolder": "", "type": "output"})

    assert resp.status_code == 200
    assert captured["cmd"] == ["open", "-R", str(image_path)]


def test_image_delete_entry_survives_when_other_images_remain(client, monkeypatch, tmp_path):
    """An entry with multiple images keeps its remaining refs after one is deleted."""
    del_path = tmp_path / "del.png"
    del_path.write_bytes(b"png")

    del_ref = {"filename": "del.png", "subfolder": "", "type": "output"}
    keep_ref = {"filename": "keep.png", "subfolder": "", "type": "output"}

    entry = {
        "type": "image",
        "prompt": "two images",
        "negative_prompt": "",
        "engine": "comfyui",
        "model": "m1",
        "params": {"steps": 20},
        "images": [del_ref, keep_ref],
    }
    assert client.post("/api/history", json=entry).status_code == 201

    monkeypatch.setattr(app_module, "_resolve_comfy_image_path", lambda _: del_path)

    resp = client.post("/api/image/delete", json=del_ref)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["removed_history_refs"] == 1
    assert data["removed_history_entries"] == 0

    history = client.get("/api/history?type=image").get_json()["history"]
    assert len(history) == 1
    remaining_images = history[0]["images"]
    assert len(remaining_images) == 1
    assert remaining_images[0]["filename"] == "keep.png"


def test_live_preview_returns_first_available_prompt_image(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_get(url, timeout=0, **kwargs):
        assert url.endswith("/queue")
        assert timeout == 10
        return DummyResponse(
            payload={
                "queue_running": [[1, "pid-run"]],
                "queue_pending": [[2, "pid-pending"]],
            }
        )

    def fake_parse_prompt_images(prompt_id):
        if prompt_id == "pid-run":
            return [{"filename": "live.png", "subfolder": "", "type": "temp"}]
        return []

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    monkeypatch.setattr(app_module, "_parse_prompt_images", fake_parse_prompt_images)

    resp = client.get("/api/image/live-preview?prompt_ids=pid-run,pid-pending")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["preview"]["prompt_id"] == "pid-run"
    assert data["preview"]["status"] == "running"
    assert data["preview"]["image"] == {"filename": "live.png", "subfolder": "", "type": "temp"}


def test_live_preview_returns_503_when_comfy_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.get("/api/image/live-preview?prompt_ids=pid-1")

    assert resp.status_code == 503
    data = resp.get_json()
    assert data["ok"] is False
    assert data["preview"] is None
    assert "ComfyUI" in data["error"]


def test_live_preview_queue_fetch_failure_returns_no_preview_when_no_images(client, monkeypatch):
    """If the ComfyUI queue fetch raises, the warning is logged and we fall through.
    When _parse_prompt_images also returns nothing, result is ok=True, preview=None."""
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def exploding_get(url, timeout=0, **kwargs):
        raise app_module.requests.ConnectionError("refused")

    monkeypatch.setattr(app_module.requests, "get", exploding_get)
    monkeypatch.setattr(app_module, "_parse_prompt_images", lambda pid: [])

    resp = client.get("/api/image/live-preview?prompt_ids=pid-x")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["preview"] is None


def test_live_preview_parse_exception_skips_prompt_id(client, monkeypatch):
    """If _parse_prompt_images raises RequestException for a prompt_id it is skipped;
    the next prompt_id is tried; if none succeed, result is ok=True, preview=None."""
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(
        app_module.requests,
        "get",
        lambda url, timeout=0, **kw: DummyResponse(
            payload={"queue_running": [], "queue_pending": []}
        ),
    )

    call_order = []

    def flaky_parse(prompt_id):
        call_order.append(prompt_id)
        raise app_module.requests.ConnectionError("timeout")

    monkeypatch.setattr(app_module, "_parse_prompt_images", flaky_parse)

    resp = client.get("/api/image/live-preview?prompt_ids=pid-a,pid-b")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["preview"] is None
    # Both prompt_ids were attempted before giving up
    assert call_order == ["pid-a", "pid-b"]


# ---------------------------------------------------------------------------
# _coerce_seed / _clamp_int / _clamp_float — unit tests for workflow helpers
# ---------------------------------------------------------------------------

def test_coerce_seed_none_and_empty_produce_positive_int():
    for bad in (None, "", -1, -99, "not-a-number"):
        seed = app_module._coerce_seed(bad)
        assert isinstance(seed, int)
        assert seed >= 1


def test_coerce_seed_valid_positive_passthrough():
    assert app_module._coerce_seed(42) == 42
    assert app_module._coerce_seed("123") == 123
    assert app_module._coerce_seed(0) == 0


def test_clamp_int_clamps_to_bounds():
    assert app_module._clamp_int(0, app_module.MIN_STEPS, app_module.MAX_STEPS) == app_module.MIN_STEPS
    assert app_module._clamp_int(9999, app_module.MIN_STEPS, app_module.MAX_STEPS) == app_module.MAX_STEPS
    assert app_module._clamp_int(30, app_module.MIN_STEPS, app_module.MAX_STEPS) == 30


def test_clamp_float_clamps_to_bounds():
    assert app_module._clamp_float(0.0, app_module.MIN_CFG, app_module.MAX_CFG) == app_module.MIN_CFG
    assert app_module._clamp_float(999.0, app_module.MIN_CFG, app_module.MAX_CFG) == app_module.MAX_CFG
    assert app_module._clamp_float(7.0, app_module.MIN_CFG, app_module.MAX_CFG) == 7.0


def test_image_generate_clamps_out_of_range_workflow_params(client, monkeypatch):
    """Values outside allowed ranges are clamped before the workflow is built."""
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    captured_meta = {}

    def fake_build(body):
        # Call the real builder so clamping is exercised
        workflow, meta = app_module._original_build_txt2img_workflow(body)
        captured_meta.update(meta)
        return workflow, meta

    # Expose the real builder under an alias for the spy
    app_module._original_build_txt2img_workflow = app_module._build_txt2img_workflow

    def fake_submit(workflow, front=False):
        return {"prompt_id": "pid-clamp", "number": 1}

    monkeypatch.setattr(app_module, "_build_txt2img_workflow", fake_build)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", fake_submit)

    resp = client.post(
        "/api/image/generate",
        json={
            "prompt": "clamp test",
            "steps": 9999,          # > MAX_STEPS (150)
            "cfg": 0.0,             # < MIN_CFG (1.0)
            "width": 100,           # < 256
            "height": 8192,         # > 2048
            "batch_size": 50,       # > 8
        },
    )

    assert resp.status_code == 200
    assert captured_meta["steps"] == app_module.MAX_STEPS
    assert captured_meta["cfg"] == app_module.MIN_CFG
    assert captured_meta["width"] == 256
    assert captured_meta["height"] == 2048
    assert captured_meta["batch_size"] == 8
