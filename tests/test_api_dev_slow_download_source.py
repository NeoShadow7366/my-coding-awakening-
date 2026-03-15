"""Tests for local slow streaming download source endpoint."""

import app as app_module



def test_dev_slow_download_source_streams_expected_size():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        resp = client.get(
            "/api/dev/slow-download-source?total_bytes=4096&chunk_bytes=512&delay_ms=0"
        )

    assert resp.status_code == 200
    assert resp.headers.get("Content-Type", "").startswith("application/octet-stream")
    assert resp.headers.get("Content-Length") == "4096"
    assert len(resp.data) == 4096



def test_dev_slow_download_source_invalid_values_fall_back_to_defaults():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        resp = client.get(
            "/api/dev/slow-download-source?total_bytes=nope&chunk_bytes=0&delay_ms=-1"
        )

    assert resp.status_code == 200
    # Defaults: total_bytes=8MB when invalid input is provided.
    assert resp.headers.get("Content-Length") == str(8 * 1024 * 1024)
