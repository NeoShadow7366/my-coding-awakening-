from io import BytesIO

import pytest
import requests as req_lib

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


def test_image_generate_rerun_payload_missing_prompt_returns_400(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    # Mirrors a rerun-style payload shape but intentionally omits prompt.
    rerun_like_payload = {
        "negative_prompt": "",
        "model": "AnythingXL_xl.safetensors",
        "sampler": "euler",
        "scheduler": "normal",
        "steps": 30,
        "cfg": 7,
        "width": 1024,
        "height": 1024,
        "batch_size": 1,
        "mode": "txt2img",
    }

    resp = client.post("/api/image/generate", json=rerun_like_payload)

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

    def fake_submit(workflow, front=False):
        assert workflow["1"]["class_type"] == "MockNode"
        assert front is False
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

    def fake_submit(workflow, front=False):
        assert workflow == {"node": {}}
        assert front is False
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


def test_image_lora_models_endpoint(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_lora_models", lambda: ["detail-tweaker.safetensors"])

    resp = client.get("/api/image/lora-models")

    assert resp.status_code == 200
    assert resp.get_json()["loras"] == ["detail-tweaker.safetensors"]


def test_image_controlnet_models_endpoint(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_image_controlnet_models", lambda: ["control_v11p_sd15_canny.safetensors"])

    resp = client.get("/api/image/controlnet-models")

    assert resp.status_code == 200
    assert resp.get_json()["models"] == ["control_v11p_sd15_canny.safetensors"]


def test_image_upload_image_requires_file(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post("/api/image/upload-image", data={}, content_type="multipart/form-data")

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "image is required"


def test_image_upload_image_success(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)
    monkeypatch.setattr(app_module, "_upload_image_to_comfy", lambda _file: "uploaded-control.png")

    resp = client.post(
        "/api/image/upload-image",
        data={"image": (BytesIO(b"control-image"), "control.png")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["name"] == "uploaded-control.png"


def test_image_generate_queue_front_passed_to_submit(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_build_txt2img_workflow(body):
        assert body["prompt"] == "prioritize me"
        assert body["queue_front"] is True
        return {"1": {"class_type": "MockNode", "inputs": {}}}, {"prompt": body["prompt"]}

    seen = {}

    def fake_submit(workflow, front=False):
        seen["front"] = front
        return {"prompt_id": "pid-front", "number": 5}

    monkeypatch.setattr(app_module, "_build_txt2img_workflow", fake_build_txt2img_workflow)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", fake_submit)

    resp = client.post("/api/image/generate", json={"prompt": "prioritize me", "queue_front": True})

    assert resp.status_code == 200
    assert seen["front"] is True


def test_img2img_queue_front_passed_to_submit(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    def fake_upload(file_storage):
        assert file_storage.filename == "in.png"
        return "uploaded-front.png"

    def fake_build_img2img_workflow(body, uploaded_name):
        assert body["prompt"] == "forest"
        assert uploaded_name == "uploaded-front.png"
        return ({"node": {}}, {"prompt": "forest", "image": uploaded_name, "mode": "img2img"})

    seen = {}

    def fake_submit(workflow, front=False):
        seen["front"] = front
        return {"prompt_id": "pid-img2img-front", "number": 23}

    monkeypatch.setattr(app_module, "_upload_image_to_comfy", fake_upload)
    monkeypatch.setattr(app_module, "_build_img2img_workflow", fake_build_img2img_workflow)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", fake_submit)

    resp = client.post(
        "/api/image/img2img",
        data={
            "prompt": "forest",
            "queue_front": "true",
            "image": (BytesIO(b"fake-image-bytes"), "in.png"),
        },
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    assert seen["front"] is True


def test_img2img_requeue_missing_image_name_returns_400(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post("/api/image/img2img-requeue", json={"prompt": "forest"})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "image_name is required"


def test_img2img_requeue_missing_prompt_returns_400(client, monkeypatch):
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    resp = client.post("/api/image/img2img-requeue", json={"image_name": "uploaded.png"})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "prompt is required"


def test_img2img_requeue_uses_existing_image_name_no_upload(client, monkeypatch):
    """Re-queue must call _build_img2img_workflow with image_name but NOT _upload_image_to_comfy."""
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    upload_called = {"called": False}

    def unexpected_upload(file_storage):
        upload_called["called"] = True
        return ""

    seen = {}

    def fake_build_img2img_workflow(body, uploaded_name):
        seen["image_name"] = uploaded_name
        seen["prompt"] = body["prompt"]
        return ({"node": {}}, {"prompt": body["prompt"], "image": uploaded_name, "mode": "img2img"})

    def fake_submit(workflow, front=False):
        seen["front"] = front
        return {"prompt_id": "pid-requeue", "number": 99}

    monkeypatch.setattr(app_module, "_upload_image_to_comfy", unexpected_upload)
    monkeypatch.setattr(app_module, "_build_img2img_workflow", fake_build_img2img_workflow)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", fake_submit)

    resp = client.post(
        "/api/image/img2img-requeue",
        json={
            "prompt": "forest",
            "negative_prompt": "",
            "model": "test-model.safetensors",
            "image_name": "comfy-resident.png",
            "queue_front": True,
        },
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["prompt_id"] == "pid-requeue"
    assert data["meta"]["image"] == "comfy-resident.png"
    assert seen["image_name"] == "comfy-resident.png"
    assert seen["prompt"] == "forest"
    assert seen["front"] is True
    assert upload_called["called"] is False


def test_img2img_requeue_accepts_image_field_fallback(client, monkeypatch):
    """image_name falls back to 'image' key for legacy snapshot compatibility."""
    monkeypatch.setattr(app_module, "_comfy_available", lambda: True)

    seen = {}

    def fake_build_img2img_workflow(body, uploaded_name):
        seen["image_name"] = uploaded_name
        return ({"node": {}}, {"prompt": body["prompt"], "image": uploaded_name, "mode": "img2img"})

    def fake_submit(workflow, front=False):
        return {"prompt_id": "pid-legacy", "number": 5}

    monkeypatch.setattr(app_module, "_build_img2img_workflow", fake_build_img2img_workflow)
    monkeypatch.setattr(app_module, "_comfy_submit_prompt", fake_submit)

    resp = client.post(
        "/api/image/img2img-requeue",
        json={"prompt": "clouds", "image": "legacy-name.png"},
    )

    assert resp.status_code == 200
    assert seen["image_name"] == "legacy-name.png"


def test_build_txt2img_workflow_includes_lora_node(monkeypatch):
    monkeypatch.setattr(app_module, "_image_models", lambda: ["base.safetensors"])

    workflow, meta = app_module._build_txt2img_workflow(
        {
            "prompt": "ruins",
            "negative_prompt": "",
            "model": "base.safetensors",
            "sampler": "euler",
            "lora": "detail-tweaker.safetensors",
            "lora_strength": 0.75,
        }
    )

    # Verify LoraLoader exists and is wired correctly
    lora_nodes = {k: v for k, v in workflow.items() if v.get("class_type") == "LoraLoader"}
    assert len(lora_nodes) == 1
    lora_key, lora_node = next(iter(lora_nodes.items()))
    assert lora_node["inputs"]["lora_name"] == "detail-tweaker.safetensors"
    assert lora_node["inputs"]["strength_model"] == 0.75
    ks_nodes = [v for v in workflow.values() if v.get("class_type") == "KSampler"]
    assert len(ks_nodes) == 1
    assert ks_nodes[0]["inputs"]["model"] == [lora_key, 0]
    assert meta["loras"] == [{"name": "detail-tweaker.safetensors", "strength": 0.75}]


def test_build_txt2img_workflow_includes_controlnet_nodes(monkeypatch):
    monkeypatch.setattr(app_module, "_image_models", lambda: ["base.safetensors"])

    workflow, meta = app_module._build_txt2img_workflow(
        {
            "prompt": "ruins",
            "negative_prompt": "",
            "model": "base.safetensors",
            "sampler": "euler",
            "controlnet_model": "control_v11p_sd15_canny.safetensors",
            "controlnet_image_name": "cn-input.png",
            "controlnet_weight": 1.0,
            "controlnet_start": 0.0,
            "controlnet_end": 0.9,
        }
    )

    cn_loaders = [v for v in workflow.values() if v.get("class_type") == "ControlNetLoader"]
    assert len(cn_loaders) == 1
    cn_applies = {k: v for k, v in workflow.items() if v.get("class_type") == "ControlNetApplyAdvanced"}
    assert len(cn_applies) == 1
    cn_apply_key, cn_apply_node = next(iter(cn_applies.items()))
    assert cn_apply_node["inputs"]["strength"] == 1.0
    load_images = {k: v for k, v in workflow.items() if v.get("class_type") == "LoadImage" and v["inputs"].get("image") == "cn-input.png"}
    assert len(load_images) == 1
    ks_nodes = [v for v in workflow.values() if v.get("class_type") == "KSampler"]
    assert len(ks_nodes) == 1
    assert ks_nodes[0]["inputs"]["positive"] == [cn_apply_key, 0]
    assert ks_nodes[0]["inputs"]["negative"] == [cn_apply_key, 1]
    assert meta["controlnet_model"] == "control_v11p_sd15_canny.safetensors"


def test_image_prompt_suggestions_requires_all_fields(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)

    resp = client.post(
        "/api/image/prompt-suggestions",
        json={
            "subject": "weathered fisherman",
            "setting": "on a storm-tossed deck",
            "composition": "close-up portrait",
            "lighting": "dramatic rim lighting",
            "style": "   ",
        },
    )

    assert resp.status_code == 400
    assert "Missing required fields" in resp.get_json()["error"]


def test_image_prompt_suggestions_unavailable_returns_503(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: False)

    resp = client.post(
        "/api/image/prompt-suggestions",
        json={
            "subject": "vintage brass compass",
            "setting": "inside a foggy lantern-lit cabin",
            "composition": "wide-angle lens",
            "lighting": "golden hour glow",
            "style": "cinematic photography",
        },
    )

    assert resp.status_code == 503
    assert "Ollama is not running" in resp.get_json()["error"]


def test_image_prompt_suggestions_success_returns_suggestions(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)
    monkeypatch.setattr(app_module, "_pick_default_ollama_model", lambda: "llama3")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "response": "- cinematic portrait of a weathered fisherman in dense fog\n"
                "- low-angle deck shot of a weathered fisherman at sea\n"
                "- moody close-up of a weathered fisherman under storm light"
            }

    def fake_post(url, json=None, timeout=0, **kwargs):
        assert url.endswith("/api/generate")
        assert timeout == 60
        assert json["model"] == "llama3"
        assert json["stream"] is False
        assert "Subject:" in json["prompt"]
        return FakeResponse()

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    resp = client.post(
        "/api/image/prompt-suggestions",
        json={
            "subject": "weathered fisherman",
            "setting": "storm-tossed deck, dense fog",
            "composition": "close-up portrait",
            "lighting": "dramatic rim lighting",
            "style": "cinematic photography",
        },
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["model"] == "llama3"
    assert len(data["suggestions"]) == 3


def test_image_prompt_suggestions_upstream_error_returns_502(client, monkeypatch):
    monkeypatch.setattr(app_module, "_ollama_available", lambda: True)
    monkeypatch.setattr(app_module, "_pick_default_ollama_model", lambda: "llama3")

    def exploding_post(url, json=None, timeout=0, **kwargs):
        raise req_lib.Timeout("read timed out")

    monkeypatch.setattr(app_module.requests, "post", exploding_post)

    resp = client.post(
        "/api/image/prompt-suggestions",
        json={
            "subject": "weathered fisherman",
            "setting": "storm-tossed deck, dense fog",
            "composition": "close-up portrait",
            "lighting": "dramatic rim lighting",
            "style": "cinematic photography",
        },
    )

    assert resp.status_code == 502
    assert "read timed out" in resp.get_json()["error"]


def test_build_txt2img_workflow_flux_model_family_uses_flux_guidance_node(monkeypatch):
    """Flux txt2img workflow must include a FluxGuidance node and set KSampler cfg to 1.0."""
    monkeypatch.setattr(app_module, "_image_models", lambda: ["flux1-dev.safetensors"])

    input_cfg = 3.5
    workflow, meta = app_module._build_txt2img_workflow(
        {
            "prompt": "a neon city at night",
            "negative_prompt": "",
            "model": "flux1-dev.safetensors",
            "model_family": "flux",
            "sampler": "euler",
            "scheduler": "normal",
            "cfg": input_cfg,
            "steps": 20,
        }
    )

    fg_nodes = [v for v in workflow.values() if v.get("class_type") == "FluxGuidance"]
    assert len(fg_nodes) == 1, "Expected exactly one FluxGuidance node for Flux model"
    assert fg_nodes[0]["inputs"]["guidance"] == input_cfg

    ks_nodes = [v for v in workflow.values() if v.get("class_type") == "KSampler"]
    assert len(ks_nodes) == 1
    assert ks_nodes[0]["inputs"]["cfg"] == 1.0


def test_build_txt2img_workflow_sd_model_family_no_flux_guidance_node(monkeypatch):
    """SD txt2img workflow must NOT include FluxGuidance; KSampler cfg equals input cfg."""
    monkeypatch.setattr(app_module, "_image_models", lambda: ["v1-5-pruned.safetensors"])

    input_cfg = 7.5
    workflow, meta = app_module._build_txt2img_workflow(
        {
            "prompt": "mountain landscape",
            "negative_prompt": "blurry",
            "model": "v1-5-pruned.safetensors",
            "model_family": "sd",
            "sampler": "euler",
            "cfg": input_cfg,
            "steps": 20,
        }
    )

    fg_nodes = [v for v in workflow.values() if v.get("class_type") == "FluxGuidance"]
    assert len(fg_nodes) == 0, "No FluxGuidance node expected for SD model"

    ks_nodes = [v for v in workflow.values() if v.get("class_type") == "KSampler"]
    assert len(ks_nodes) == 1
    assert ks_nodes[0]["inputs"]["cfg"] == input_cfg


def test_build_img2img_workflow_flux_model_family_uses_flux_guidance_node(monkeypatch):
    """Flux img2img workflow must include a FluxGuidance node and set KSampler cfg to 1.0."""
    monkeypatch.setattr(app_module, "_image_models", lambda: ["flux1-dev.safetensors"])

    input_cfg = 3.0
    workflow, meta = app_module._build_img2img_workflow(
        {
            "prompt": "futuristic robot",
            "negative_prompt": "",
            "model": "flux1-dev.safetensors",
            "model_family": "flux",
            "sampler": "euler",
            "scheduler": "simple",
            "cfg": input_cfg,
            "steps": 20,
            "denoise": 0.7,
        },
        "source.png",
    )

    fg_nodes = [v for v in workflow.values() if v.get("class_type") == "FluxGuidance"]
    assert len(fg_nodes) == 1, "Expected exactly one FluxGuidance node for Flux img2img"
    assert fg_nodes[0]["inputs"]["guidance"] == input_cfg

    ks_nodes = [v for v in workflow.values() if v.get("class_type") == "KSampler"]
    assert len(ks_nodes) == 1
    assert ks_nodes[0]["inputs"]["cfg"] == 1.0
