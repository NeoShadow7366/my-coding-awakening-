"""Tests for CivitAI search pagination compatibility."""

import app as app_module


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.headers = {}

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _model_item(model_id: int, name: str) -> dict:
    return {
        "id": model_id,
        "name": name,
        "type": "Checkpoint",
        "creator": {"username": "tester"},
        "description": "sample",
        "stats": {"rating": 4.2, "downloadCount": 99},
        "modelVersions": [
            {
                "id": 1000 + model_id,
                "name": "v1",
                "files": [
                    {
                        "primary": True,
                        "name": f"{name}.safetensors",
                        "sizeKB": 123,
                        "downloadUrl": "https://example.test/download",
                    }
                ],
                "images": [{"nsfw": False, "url": "https://example.test/preview.png"}],
            }
        ],
    }


def test_civitai_query_search_uses_cursor_not_page(monkeypatch):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append(dict(params))
        assert params.get("query") == "zelda"
        assert "page" not in params
        return _FakeResponse(
            {
                "items": [_model_item(1, "zelda-model")],
                "metadata": {"nextCursor": "cursor-2"},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search("zelda", "", 1)

    assert len(calls) == 1
    assert result["current_page"] == 1
    assert result["total_pages"] == 2
    assert result["items"][0]["name"] == "zelda-model"


def test_civitai_query_page_two_walks_cursor_chain(monkeypatch):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append(dict(params))
        assert params.get("query") == "zelda"
        assert "page" not in params

        if len(calls) == 1:
            return _FakeResponse(
                {
                    "items": [_model_item(1, "page-1")],
                    "metadata": {"nextCursor": "cursor-2"},
                }
            )

        assert params.get("cursor") == "cursor-2"
        return _FakeResponse(
            {
                "items": [_model_item(2, "page-2")],
                "metadata": {},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search("zelda", "", 2)

    assert len(calls) == 2
    assert calls[0].get("cursor") is None
    assert calls[1].get("cursor") == "cursor-2"
    assert result["current_page"] == 2
    assert result["total_pages"] == 2
    assert result["items"][0]["name"] == "page-2"


def test_civitai_non_query_search_keeps_page_param(monkeypatch):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append(dict(params))
        assert params.get("page") == 3
        assert "query" not in params
        return _FakeResponse(
            {
                "items": [_model_item(3, "browse-page")],
                "metadata": {"totalPages": 10},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search("", "", 3)

    assert len(calls) == 1
    assert result["current_page"] == 3
    assert result["total_pages"] == 10
    assert result["items"][0]["name"] == "browse-page"


def test_civitai_query_search_uses_given_cursor_directly(monkeypatch):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append(dict(params))
        assert params.get("query") == "zelda"
        assert params.get("cursor") == "cursor-2"
        assert "page" not in params
        return _FakeResponse(
            {
                "items": [_model_item(4, "cursor-page")],
                "metadata": {"nextCursor": "cursor-3"},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search("zelda", "", 2, "cursor-2")

    assert len(calls) == 1
    assert result["current_page"] == 2
    assert result["has_next"] is True
    assert result["next_cursor"] == "cursor-3"
    assert result["items"][0]["name"] == "cursor-page"


def test_civitai_search_passes_sort_nsfw_and_base_model(monkeypatch):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append(dict(params))
        assert params.get("sort") == "Most Downloaded"
        assert params.get("nsfw") == "true"
        assert params.get("baseModels") == "SDXL 1.0"
        return _FakeResponse(
            {
                "items": [_model_item(8, "sorted-model")],
                "metadata": {"totalPages": 1},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search(
        "",
        "",
        1,
        "",
        sort="Most Downloaded",
        nsfw=True,
        base_model="SDXL 1.0",
    )

    assert len(calls) == 1
    assert result["items"][0]["name"] == "sorted-model"


def test_civitai_search_passes_limit_parameter(monkeypatch):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append(dict(params))
        return _FakeResponse(
            {
                "items": [_model_item(9, "limited-model")],
                "metadata": {"totalPages": 1},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search("", "", 1, limit=60)

    assert len(calls) == 1
    assert calls[0].get("limit") == 60
    assert result["items"][0]["name"] == "limited-model"


def test_civitai_preview_uses_level_one_image_when_level_zero_missing(monkeypatch):
    def fake_get(url, params, headers, timeout):
        return _FakeResponse(
            {
                "items": [
                    {
                        "id": 42,
                        "name": "preview-model",
                        "type": "Checkpoint",
                        "creator": {"username": "tester"},
                        "description": "sample",
                        "stats": {"rating": 4.5, "downloadCount": 10},
                        "modelVersions": [
                            {
                                "id": 2042,
                                "name": "v1",
                                "files": [
                                    {
                                        "primary": True,
                                        "name": "preview-model.safetensors",
                                        "sizeKB": 123,
                                        "downloadUrl": "https://example.test/download",
                                    }
                                ],
                                "images": [
                                    {"url": "https://example.test/preview-level1.jpg", "nsfwLevel": 1},
                                ],
                            }
                        ],
                    }
                ],
                "metadata": {"totalPages": 1},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search("", "", 1)

    assert result["items"][0]["preview_url"] == "https://example.test/preview-level1.jpg"


def test_civitai_search_exposes_total_items_from_metadata(monkeypatch):
    def fake_get(url, params, headers, timeout):
        return _FakeResponse(
            {
                "items": [_model_item(77, "counted-model")],
                "metadata": {"totalPages": 4, "totalItems": 321},
            }
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    result = app_module._civitai_search("", "", 1)

    assert result["total_items"] == 321
