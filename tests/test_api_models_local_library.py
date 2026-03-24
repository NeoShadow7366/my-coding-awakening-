"""Tests for local model library preview metadata and preview-serving API."""

import json
import sqlite3
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


def test_scan_local_models_includes_preview_url_for_sidecar_images(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))
    models_root = tmp_path / "models"
    model_dir = models_root / "checkpoints"
    model_dir.mkdir(parents=True, exist_ok=True)

    model_file = model_dir / "dream.safetensors"
    model_file.write_bytes(b"weights")
    preview_file = model_dir / "dream.png"
    preview_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    models = app_module._scan_local_models()

    assert len(models) == 1
    assert models[0]["name"] == "dream.safetensors"
    assert models[0]["preview_url"].startswith("/api/models/local-preview?path=")
    assert "checkpoints/dream.png" in models[0]["preview_url"]


def test_scan_local_models_uses_metadata_preview_fallback_when_no_sidecar(tmp_path, monkeypatch):
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

        models_root = tmp_path / "models"
        model_dir = models_root / "checkpoints"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_file = model_dir / "fallback.safetensors"
        model_file.write_bytes(b"weights")

        metadata_file = data_dir / "model_metadata.json"
        metadata_file.write_text(
                """
{
    "checkpoints/fallback.safetensors": {
        "file_name": "fallback.safetensors",
        "folder": "checkpoints",
        "provider": "civitai",
        "model_id": "123",
        "model_name": "Fallback",
        "version_name": "v2.1",
        "model_type": "Checkpoint",
        "base_model": "SDXL 1.0",
        "model_url": "https://civitai.com/models/123",
        "preview_url": "https://example.test/fallback.jpg",
        "preview_urls": [
            "https://example.test/fallback.jpg",
            "https://example.test/fallback-2.jpg"
        ],
        "updated_at": 1
    }
}
""".strip(),
                encoding="utf-8",
        )

        monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
        monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

        models = app_module._scan_local_models()

        assert len(models) == 1
        assert models[0]["name"] == "fallback.safetensors"
        assert models[0]["preview_url"] == "https://example.test/fallback.jpg"
        assert models[0]["preview_urls"] == [
            "https://example.test/fallback.jpg",
            "https://example.test/fallback-2.jpg",
        ]
        assert models[0]["version_name"] == "v2.1"


def test_save_model_metadata_syncs_json_and_sqlite(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    payload = {
        "checkpoints/demo.safetensors": {
            "file_name": "demo.safetensors",
            "folder": "checkpoints",
            "provider": "civitai",
            "updated_at": 1,
        }
    }

    app_module._save_model_metadata(payload)

    json_path = data_dir / "model_metadata.json"
    db_path = data_dir / "model_metadata.db"
    assert json_path.exists()
    assert db_path.exists()

    stored_json = json.loads(json_path.read_text(encoding="utf-8"))
    assert stored_json == payload

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT metadata_key, payload_json FROM model_metadata WHERE metadata_key = ?",
            ("checkpoints/demo.safetensors",),
        ).fetchone()
    assert row is not None
    assert row[0] == "checkpoints/demo.safetensors"
    assert json.loads(row[1]) == payload["checkpoints/demo.safetensors"]


def test_load_model_metadata_bootstraps_sqlite_from_existing_json(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    payload = {
        "loras/hero-style.safetensors": {
            "file_name": "hero-style.safetensors",
            "folder": "loras",
            "provider": "huggingface",
            "updated_at": 2,
        }
    }
    (data_dir / "model_metadata.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = app_module._load_model_metadata()
    assert loaded == payload

    db_path = data_dir / "model_metadata.db"
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM model_metadata").fetchone()[0]
    assert count == 1


def test_scan_local_models_uses_civitai_sidecar_metadata_for_preview_and_model_fields(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "checkpoints"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "castle-vision.safetensors"
    model_file.write_bytes(b"weights")

    sidecar = model_dir / "castle-vision.civitai.info"
    sidecar.write_text(
        json.dumps(
            {
                "modelId": 777,
                "name": "Castle Vision",
                "modelVersionName": "v3.0",
                "type": "Checkpoint",
                "baseModel": "SDXL 1.0",
                "images": [{"url": "https://example.test/castle.jpg", "nsfwLevel": 0}],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    models = app_module._scan_local_models()

    assert len(models) == 1
    assert models[0]["name"] == "castle-vision.safetensors"
    assert models[0]["preview_url"] == "https://example.test/castle.jpg"
    assert models[0]["provider"] == "civitai"
    assert models[0]["model_id"] == "777"
    assert models[0]["model_url"] == "https://civitai.com/models/777"
    assert models[0]["version_name"] == "v3.0"
    assert models[0]["type"] == "Checkpoint"
    assert models[0]["base_model"] == "SDXL 1.0"


def test_scan_local_models_matches_non_stem_sidecar_when_payload_lists_file(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "checkpoints"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "my-model-v2.safetensors"
    model_file.write_bytes(b"weights")

    sidecar = model_dir / "12345.civitai.info"
    sidecar.write_text(
        json.dumps(
            {
                "id": 12345,
                "name": "My Model V2",
                "type": "Checkpoint",
                "baseModel": "SD 1.5",
                "files": [{"name": "my-model-v2.safetensors"}],
                "images": [{"url": "https://example.test/my-model-preview.jpg", "nsfwLevel": 0}],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    models = app_module._scan_local_models()

    assert len(models) == 1
    assert models[0]["preview_url"] == "https://example.test/my-model-preview.jpg"
    assert models[0]["model_id"] == "12345"
    assert models[0]["base_model"] == "SD 1.5"


def test_api_models_local_preview_serves_image(client, tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    preview_dir = models_root / "checkpoints"
    preview_dir.mkdir(parents=True, exist_ok=True)
    preview_file = preview_dir / "demo.png"
    preview_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)

    resp = client.get("/api/models/local-preview?path=checkpoints/demo.png")

    assert resp.status_code == 200
    assert resp.data.startswith(b"\x89PNG")


def test_api_models_local_preview_rejects_path_escape(client, tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    models_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)

    resp = client.get("/api/models/local-preview?path=../secret.png")

    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False


def test_api_models_library_enrich_previews_backfills_metadata(client, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "loras"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "forest-style.safetensors"
    model_file.write_bytes(b"weights")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    class _FakeCivitaiResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "items": [
                    {
                        "id": 321,
                        "name": "Forest Style",
                        "type": "LORA",
                        "url": "https://civitai.com/models/321",
                        "modelVersions": [
                            {
                                "baseModel": "SDXL 1.0",
                                "files": [{"name": "forest-style.safetensors"}],
                                "images": [{"url": "https://example.test/forest-preview.jpg", "nsfwLevel": 0}],
                            }
                        ],
                    }
                ]
            }

    def fake_get(url, params=None, headers=None, timeout=0):
        assert "/models" in url
        return _FakeCivitaiResponse()

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.post("/api/models/library/enrich-previews", json={"limit": 10})

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["updated"] >= 1
    assert payload["skip_reasons"]["already_has_preview"] >= 0
    assert payload["skip_reasons"]["missing_folder_or_name"] >= 0
    assert payload["skip_reasons"]["no_civitai_match"] >= 0
    assert payload["failure_reasons"]["request_error"] >= 0
    assert isinstance(payload["updated_samples"], list)
    assert isinstance(payload["skipped_samples"], list)
    assert isinstance(payload["failed_samples"], list)

    metadata_file = data_dir / "model_metadata.json"
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    key = "loras/forest-style.safetensors"
    assert key in metadata
    assert metadata[key]["preview_url"] == "https://example.test/forest-preview.jpg"


def test_api_models_library_enrich_previews_reports_no_match_skip_reason(client, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "loras"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "unknown-style.safetensors"
    model_file.write_bytes(b"weights")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    class _FakeEmptyCivitaiResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"items": []}

    def fake_get(url, params=None, headers=None, timeout=0):
        assert "/models" in url
        return _FakeEmptyCivitaiResponse()

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.post("/api/models/library/enrich-previews", json={"limit": 10})

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["updated"] == 0
    assert payload["failed"] == 0
    assert payload["skip_reasons"]["no_civitai_match"] >= 1
    assert any(sample.get("reason") == "no_civitai_match" for sample in payload["skipped_samples"])


def test_api_models_library_compare_metadata_matches_huggingface_by_name(client, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "checkpoints"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "princess-zelda-v1.safetensors"
    model_file.write_bytes(b"weights")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    class _FakeHfResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return [
                {
                    "id": "creator/zelda-style-pack",
                    "sha": "abc12345ff00ee11",
                    "tags": ["lora"],
                    "siblings": [
                        {"rfilename": "princess-zelda-v1.safetensors"},
                    ],
                    "cardData": {"base_model": "SDXL 1.0"},
                }
            ]

    requested_queries = []

    def fake_get(url, params=None, headers=None, timeout=0):
        assert url.endswith("/models")
        requested_queries.append(params["search"])
        return _FakeHfResponse()

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.post(
        "/api/models/library/compare-metadata",
        json={"limit": 20, "providers": ["huggingface"], "overwrite": False},
    )

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["updated"] >= 1
    assert payload["matched_by_provider"]["huggingface"] >= 1
    assert any(sample.get("version_name") == "abc12345" for sample in payload["updated_samples"])
    assert requested_queries[0] == "princess-zelda-v1"

    metadata_file = data_dir / "model_metadata.json"
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    key = "checkpoints/princess-zelda-v1.safetensors"
    assert key in metadata
    assert metadata[key]["provider"] == "huggingface"
    assert metadata[key]["model_id"] == "creator/zelda-style-pack"
    assert metadata[key]["version_name"] == "abc12345"
    assert metadata[key]["model_url"] == "https://huggingface.co/creator/zelda-style-pack"


def test_api_models_library_compare_metadata_matches_civitai_by_model_and_version_name(client, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "loras"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "princess-zelda-v10.safetensors"
    model_file.write_bytes(b"weights")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    class _FakeCivitaiResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "items": [
                    {
                        "id": 777,
                        "name": "Princess Zelda",
                        "type": "LoRA",
                        "modelVersions": [
                            {
                                "name": "v1.0",
                                "baseModel": "SDXL 1.0",
                                "images": [{"url": "https://example.test/zelda-preview.jpg", "nsfw": False}],
                                "files": [
                                    {"name": "zelda-style-release.safetensors"},
                                ],
                            }
                        ],
                    }
                ]
            }

    requested_queries = []

    def fake_get(url, params=None, headers=None, timeout=0):
        assert url.endswith("/models")
        requested_queries.append(params["query"])
        return _FakeCivitaiResponse()

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.post(
        "/api/models/library/compare-metadata",
        json={"limit": 20, "providers": ["civitai"], "overwrite": False},
    )

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["updated"] >= 1
    assert payload["matched_by_provider"]["civitai"] >= 1
    assert any(sample.get("version_name") == "v1.0" for sample in payload["updated_samples"])
    assert requested_queries[0] == "princess-zelda-v10"

    metadata_file = data_dir / "model_metadata.json"
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    key = "loras/princess-zelda-v10.safetensors"
    assert key in metadata
    assert metadata[key]["provider"] == "civitai"
    assert metadata[key]["model_id"] == "777"
    assert metadata[key]["model_name"] == "Princess Zelda"
    assert metadata[key]["version_name"] == "v1.0"
    assert metadata[key]["preview_url"] == "https://example.test/zelda-preview.jpg"


def test_api_models_library_compare_metadata_retries_with_version_stripped_filename_query(client, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "loras"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "forest-style-v12.safetensors"
    model_file.write_bytes(b"weights")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    requested_queries = []

    class _FakeCivitaiResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, params=None, headers=None, timeout=0):
        assert url.endswith("/models")
        requested_queries.append(params["query"])
        if params["query"] == "forest-style-v12":
            return _FakeCivitaiResponse({"items": []})
        if params["query"] == "forest style":
            return _FakeCivitaiResponse(
                {
                    "items": [
                        {
                            "id": 900,
                            "name": "Forest Style",
                            "type": "LoRA",
                            "modelVersions": [
                                {
                                    "name": "v12",
                                    "baseModel": "SDXL 1.0",
                                    "images": [{"url": "https://example.test/forest-style.jpg", "nsfw": False}],
                                    "files": [{"name": "forest-style-release.safetensors"}],
                                }
                            ],
                        }
                    ]
                }
            )
        return _FakeCivitaiResponse({"items": []})

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    resp = client.post(
        "/api/models/library/compare-metadata",
        json={"limit": 20, "providers": ["civitai"], "overwrite": False},
    )

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["updated"] >= 1
    assert requested_queries[0] == "forest-style-v12"
    assert "forest style" in requested_queries


def test_api_models_library_recover_metadata_runs_compare_and_preview(client, monkeypatch):
    compare_calls = []
    preview_calls = []

    def fake_compare(limit=0, providers=None, overwrite=False):
        compare_calls.append({
            "limit": limit,
            "providers": list(providers or []),
            "overwrite": overwrite,
        })
        return {
            "updated": 2,
            "failed": 1,
            "skipped": 3,
            "updated_samples": [{"file": "loras/sample.safetensors", "provider": "civitai", "version_name": "v1"}],
            "skipped_samples": [],
            "failed_samples": [],
        }

    def fake_preview(limit=0):
        preview_calls.append({"limit": limit})
        return {
            "updated": 4,
            "failed": 0,
            "skipped": 2,
            "updated_samples": ["loras/sample.safetensors"],
            "skipped_samples": [],
            "failed_samples": [],
        }

    monkeypatch.setattr(app_module, "_compare_local_model_metadata_with_providers", fake_compare)
    monkeypatch.setattr(app_module, "_enrich_local_model_metadata_with_civitai", fake_preview)

    resp = client.post(
        "/api/models/library/recover-metadata",
        json={
            "compare_limit": 55,
            "preview_limit": 22,
            "providers": ["huggingface"],
            "overwrite": True,
        },
    )

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["updated_total"] == 6
    assert payload["failed_total"] == 1
    assert payload["skipped_total"] == 5
    assert payload["compare"]["updated"] == 2
    assert payload["preview"]["updated"] == 4
    assert compare_calls == [{"limit": 55, "providers": ["huggingface"], "overwrite": True}]
    assert preview_calls == [{"limit": 22}]


def test_api_models_library_recover_metadata_returns_502_on_request_error(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "_compare_local_model_metadata_with_providers",
        lambda *args, **kwargs: {"updated": 0, "failed": 0, "skipped": 0},
    )

    def fake_preview_error(limit=0):
        raise app_module.requests.RequestException("provider timeout")

    monkeypatch.setattr(app_module, "_enrich_local_model_metadata_with_civitai", fake_preview_error)

    resp = client.post("/api/models/library/recover-metadata", json={})

    assert resp.status_code == 502
    payload = resp.get_json()
    assert payload["ok"] is False
    assert "provider timeout" in payload["error"]


def test_api_models_library_update_version_metadata_updates_installed_files(client, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", Path(data_dir))

    models_root = tmp_path / "models"
    model_dir = models_root / "loras"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "hero-style-v2.safetensors"
    model_file.write_bytes(b"weights")

    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)

    resp = client.post(
        "/api/models/library/update-version-metadata",
        json={
            "provider": "civitai",
            "model_id": "200",
            "model_name": "Hero Style",
            "model_type": "LORA",
            "base_model": "SDXL 1.0",
            "model_url": "https://civitai.com/models/200",
            "version_name": "v2",
            "preview_url": "https://example.test/hero-v2-1.jpg",
            "preview_urls": [
                "https://example.test/hero-v2-1.jpg",
                "https://example.test/hero-v2-2.jpg",
            ],
            "installed_files": ["hero-style-v2.safetensors"],
        },
    )

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["updated"] == 1
    assert payload["preview_count"] == 2

    metadata_file = data_dir / "model_metadata.json"
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    key = "loras/hero-style-v2.safetensors"
    assert key in metadata
    assert metadata[key]["provider"] == "civitai"
    assert metadata[key]["model_id"] == "200"
    assert metadata[key]["version_name"] == "v2"
    assert metadata[key]["preview_url"] == "https://example.test/hero-v2-1.jpg"
    assert metadata[key]["preview_urls"] == [
        "https://example.test/hero-v2-1.jpg",
        "https://example.test/hero-v2-2.jpg",
    ]


def test_find_civitai_match_prefers_highest_confidence_candidate(monkeypatch):
    class _FakeCivitaiResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "items": [
                    {
                        "id": 100,
                        "name": "Hero Style",
                        "type": "LoRA",
                        "modelVersions": [
                            {
                                "name": "v1",
                                "baseModel": "SDXL 1.0",
                                "files": [{"name": "hero-style.safetensors"}],
                            }
                        ],
                    },
                    {
                        "id": 200,
                        "name": "Hero Style",
                        "type": "LoRA",
                        "modelVersions": [
                            {
                                "name": "v2",
                                "baseModel": "SDXL 1.0",
                                "files": [{"name": "hero-style-v2.safetensors"}],
                            }
                        ],
                    },
                ]
            }

    monkeypatch.setattr(app_module.requests, "get", lambda *args, **kwargs: _FakeCivitaiResponse())

    match = app_module._find_civitai_match_for_local_file({"name": "hero-style-v2.safetensors", "type": "LoRA"})

    assert match["provider"] == "civitai"
    assert match["model_id"] == "200"
    assert match["version_name"] == "v2"


def test_find_huggingface_match_prefers_exact_filename_candidate(monkeypatch):
    class _FakeHfResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return [
                {
                    "id": "author/hero-style",
                    "sha": "11111111aaaa",
                    "siblings": [{"rfilename": "hero-style.safetensors"}],
                    "tags": ["lora"],
                },
                {
                    "id": "author/hero-style-v2",
                    "sha": "22222222bbbb",
                    "siblings": [{"rfilename": "hero-style-v2.safetensors"}],
                    "tags": ["lora"],
                },
            ]

    monkeypatch.setattr(app_module.requests, "get", lambda *args, **kwargs: _FakeHfResponse())

    match = app_module._find_huggingface_match_for_local_file({"name": "hero-style-v2.safetensors"})

    assert match["provider"] == "huggingface"
    assert match["model_id"] == "author/hero-style-v2"
    assert match["version_name"] == "22222222"


def test_api_models_open_folder_opens_parent_directory(client, tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    model_dir = models_root / "checkpoints"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "demo.safetensors"
    model_file.write_bytes(b"weights")

    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)
    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)
    monkeypatch.setattr(app_module.os, "name", "nt")

    popen_calls = []

    class _FakeProc:
        pass

    def fake_popen(args, stdout=None, stderr=None):
        popen_calls.append(args)
        return _FakeProc()

    monkeypatch.setattr(app_module.subprocess, "Popen", fake_popen)

    resp = client.post("/api/models/open-folder", json={"file_name": "demo.safetensors", "folder": "checkpoints"})

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["path"] == str(model_dir)
    assert popen_calls == [["explorer", str(model_dir)]]


def test_api_models_open_folder_rejects_invalid_file_name(client):
    resp = client.post("/api/models/open-folder", json={"file_name": "../evil.safetensors", "folder": "checkpoints"})

    assert resp.status_code == 400
    payload = resp.get_json()
    assert "invalid file_name" in payload["error"]


def test_api_models_open_folder_returns_not_found_for_missing_file(client, tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    (models_root / "checkpoints").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(app_module, "_using_shared_models_root", lambda: False)
    monkeypatch.setattr(app_module, "_comfy_models_root", lambda: models_root)

    resp = client.post("/api/models/open-folder", json={"file_name": "missing.safetensors", "folder": "checkpoints"})

    assert resp.status_code == 404
    payload = resp.get_json()
    assert "Model file not found" in payload["error"]
