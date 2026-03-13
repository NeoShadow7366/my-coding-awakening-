from io import BytesIO

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    history_file = data_dir / "history.json"
    monkeypatch.setattr(app_module, "DATA_DIR", data_dir)
    monkeypatch.setattr(app_module, "HISTORY_FILE", history_file)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_image_generate_requires_prompt(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post("/api/image/generate", json={"prompt": "   "})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "prompt is required"


def test_image_generate_unavailable_returns_503(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: False)

    resp = client.post("/api/image/generate", json={"prompt": "test"})

    assert resp.status_code == 503
    assert "ComfyUI is not running" in resp.get_json()["error"]


def test_image_generate_success_returns_prompt_metadata(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    expected_meta = {
        "prompt": "castle",
        "model": "test-model",
        "sampler": "euler",
        "steps": 30,
    }

    def fake_build_txt2img_workflow(body):
        assert body["prompt"] == "castle"
        return {"1": {"class_type": "MockNode", "inputs": {}}}, expected_meta

    def fake_submit(workflow):
        assert workflow["1"]["class_type"] == "MockNode"
        return {"prompt_id": "pid-xyz", "number": 7}

    monkeypatch.setattr(app_module, "_build_txt2img_workflow", fake_build_txt2img_workflow)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", fake_submit)

    resp = client.post("/api/image/generate", json={"prompt": "castle"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["prompt_id"] == "pid-xyz"
    assert data["number"] == 7
    assert data["meta"] == expected_meta


def test_img2img_requires_image_and_prompt(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    no_image = client.post("/api/image/img2img", data={"prompt": "x"}, content_type="multipart/form-data")
    assert no_image.status_code == 400
    assert no_image.get_json()["error"] == "image is required"

    no_prompt = client.post(
        "/api/image/img2img",
        data={"prompt": "   ", "image": (BytesIO(b"fake"), "in.png")},
        content_type="multipart/form-data",
    )
    assert no_prompt.status_code == 400
    assert no_prompt.get_json()["error"] == "prompt is required"


def test_img2img_success_returns_prompt_metadata(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_upload(file_storage):
        assert file_storage.filename == "in.png"
        return "uploaded-in.png"

    def fake_build_img2img_workflow(body, uploaded_name):
        assert body["prompt"] == "forest"
        assert uploaded_name == "uploaded-in.png"
        return ({"node": {}}, {"prompt": "forest", "image": uploaded_name, "mode": "img2img"})

    def fake_submit(workflow):
        assert workflow == {"node": {}}
        return {"prompt_id": "pid-img2img", "number": 13}

    monkeypatch.setattr(app_module, "_upload_image_to_comfy", fake_upload)
    monkeypatch.setattr(app_module, "_build_img2img_workflow", fake_build_img2img_workflow)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", fake_submit)

    resp = client.post(
        "/api/image/img2img",
        data={
            "prompt": "forest",
            "negative_prompt": "",
            "model": "test-model",
            "sampler": "euler",
            "seed": "",
            "steps": "30",
            "cfg": "7",
            "denoise": "0.75",
            "image": (BytesIO(b"fake-image-bytes"), "in.png"),
        },
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["prompt_id"] == "pid-img2img"
    assert data["number"] == 13
    assert data["meta"] == {"prompt": "forest", "image": "uploaded-in.png", "mode": "img2img"}
