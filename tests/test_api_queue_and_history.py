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
