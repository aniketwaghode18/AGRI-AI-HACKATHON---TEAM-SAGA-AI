import os
from typing import Set


class AppConfig:
    """
    Server configuration.

    Toggle mock mode using environment variables:
      - Windows (cmd):
          set MOCK_MODE=1
      - PowerShell:
          $env:MOCK_MODE = "1"
      - macOS/Linux (bash):
          export MOCK_MODE=1

    Set other options similarly, e.g.:
      export MODEL_PATH="models/latest.onnx"
      export OVERLAY_DIR="overlays"

    Example mock prediction response (when MOCK_MODE=1):
      {
        "ok": true,
        "prediction": {
          "label": "healthy",
          "confidence": 0.87,
          "brightness": 0.62
        }
      }
    """

    # General
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Mocking and inference
    MOCK_MODE: bool = os.environ.get("MOCK_MODE", "0") == "1"
    MODEL_PATH: str = os.environ.get("MODEL_PATH", "models/export.onnx")

    # Assets and uploads
    OVERLAY_DIR: str = os.environ.get("OVERLAY_DIR", "overlays")
    ALLOWED_EXTENSIONS: Set[str] = set(
        (os.environ.get("ALLOWED_EXTENSIONS", "jpg,jpeg,png,bmp,webp").lower()).split(",")
    )

    # Maximum incoming image payload size in bytes (default 10 MB)
    MAX_IMAGE_SIZE: int = int(os.environ.get("MAX_IMAGE_SIZE", str(10 * 1024 * 1024)))

    # Flask builtin limit for request body size
    MAX_CONTENT_LENGTH: int = MAX_IMAGE_SIZE

    # CORS
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")
