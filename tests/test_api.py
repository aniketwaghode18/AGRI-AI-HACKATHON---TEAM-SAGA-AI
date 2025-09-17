import io
import json
from typing import Any, Dict

import pytest
from PIL import Image

from src.server.app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def _fake_detect_image(_: str) -> Dict[str, Any]:
    # Return a minimal valid prediction schema
    return {
        "prediction": {
            "objects": [
                {"label": "plant", "confidence": 0.9, "box": [10.0, 10.0, 50.0, 50.0]}
            ]
        }
    }


def _make_image_bytes() -> bytes:
    img = Image.new("RGB", (64, 64), color=(120, 200, 120))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_analyze_with_mocked_detection(client, monkeypatch):
    # Arrange: mock detect_image
    from src import ml as _  # ensure package import path
    from src.ml import inference as inf

    monkeypatch.setattr(inf, "detect_image", _fake_detect_image)

    # Act: post an in-memory image
    image_bytes = _make_image_bytes()
    data = {"image": (io.BytesIO(image_bytes), "test.png")}
    resp = client.post("/analyze", data=data, content_type="multipart/form-data")

    # Assert
    assert resp.status_code == 200
    body = resp.get_json()
    assert body and body.get("ok") is True
    assert "prediction" in body
    assert "objects" in body["prediction"]
    assert isinstance(body["prediction"]["objects"], list)


def test_analyze_integration_mock_mode(client, monkeypatch):
    # Force MOCK_MODE via config override for this app instance
    client.application.config["MOCK_MODE"] = True

    image_bytes = _make_image_bytes()
    data = {"image": (io.BytesIO(image_bytes), "test.png")}
    resp = client.post("/analyze", data=data, content_type="multipart/form-data")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body and body.get("ok") is True
    assert "prediction" in body
    # overlay_url present in mock mode
    assert "overlay_url" in body
