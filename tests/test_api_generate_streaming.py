"""Regression tests for /api/generate SSE streaming behavior."""
import json

import pytest
import requests as req_lib

import app as app_module


class DummyStreamResponse:
    def __init__(self, status_code=200, lines=None, text=""):
        self.status_code = status_code
        self._lines = lines or []
        self.text = text

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def iter_lines(self):
        for line in self._lines:
            yield line


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    history_file = data_dir / "history.json"
    monkeypatch.setattr(app_module, "DATA_DIR", data_dir)
    monkeypatch.setattr(app_module, "HISTORY_FILE", history_file)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_generate_requires_model(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)

    resp = client.post("/api/generate", json={"model": "   ", "prompt": "hello"})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "model is required"


def test_generate_stream_success_emits_tokens_meta_and_done(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)
    captured_payload = {}

    stream_lines = [
        b'{"response":"Hello","done":false}',
        b'not-json',
        b'{"response":" world","done":false}',
        b'{"done":true}',
    ]

    def fake_post(url, json=None, stream=False, timeout=0, **kwargs):
        captured_payload.update(json or {})
        assert url.endswith("/api/generate")
        assert stream is True
        assert timeout == 120
        return DummyStreamResponse(status_code=200, lines=stream_lines)

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    resp = client.post(
        "/api/generate",
        json={
            "model": "llama3",
            "prompt": "Say hello",
            "temperature": 9,
            "top_p": -1,
            "top_k": 5000,
            "num_predict": 99999,
            "seed": 42,
            "system": "You are concise",
            "negative_prompt": "rambling",
        },
    )

    assert resp.status_code == 200
    assert resp.mimetype == "text/event-stream"

    text = resp.get_data(as_text=True)
    assert 'data: {"token": "Hello"}' in text
    assert 'data: {"token": " world"}' in text
    assert 'data: [DONE]' in text

    meta_prefix = "data: {\"meta\": "
    meta_line = next(line for line in text.splitlines() if line.startswith(meta_prefix))
    meta_json = json.loads(meta_line[len("data: "):])
    assert meta_json == {
        "meta": {
            "seed": 42,
            "temperature": 2.0,
            "top_p": 0.0,
            "top_k": 1000,
            "num_predict": 4096,
        }
    }

    assert captured_payload["model"] == "llama3"
    assert captured_payload["prompt"] == "Say hello"
    assert captured_payload["stream"] is True
    assert captured_payload["system"] == "You are concise"
    assert "Avoid this style/content: rambling" in captured_payload["suffix"]
    assert captured_payload["options"] == {
        "temperature": 2.0,
        "top_p": 0.0,
        "top_k": 1000,
        "num_predict": 4096,
        "seed": 42,
    }


def test_generate_stream_non_200_emits_error_event(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)

    def fake_post(url, json=None, stream=False, timeout=0, **kwargs):
        return DummyStreamResponse(status_code=500, text="upstream exploded")

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    resp = client.post("/api/generate", json={"model": "llama3", "prompt": "x"})

    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert 'data: {"error": "upstream exploded"}' in text
    assert 'data: [DONE]' not in text


def test_generate_stream_request_exception_emits_error_event(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)

    def exploding_post(url, json=None, stream=False, timeout=0, **kwargs):
        raise req_lib.Timeout("read timed out")

    monkeypatch.setattr(app_module.requests, "post", exploding_post)

    resp = client.post("/api/generate", json={"model": "llama3", "prompt": "x"})

    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert 'data: {"error": "read timed out"}' in text
