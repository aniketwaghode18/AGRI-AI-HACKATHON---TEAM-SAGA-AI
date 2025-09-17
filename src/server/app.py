import os
import uuid
import tempfile
from typing import Tuple, Optional

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw

from src.server.config import AppConfig
from src.ml.inference import detect_image

# flask file
OVERLAYS_SUBDIR = os.path.join("static", "overlays")


def ensure_overlays_dir() -> str:
    overlays_dir = os.path.abspath(OVERLAYS_SUBDIR)
    os.makedirs(overlays_dir, exist_ok=True)
    return overlays_dir


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")
    CORS(app)
    app.config.from_object(AppConfig)

    ensure_overlays_dir()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/analyze")
    def analyze():
        try:
            if "image" not in request.files:
                return jsonify({"ok": False, "error": "Missing 'image' file"}), 400

            file = request.files["image"]
            filename = secure_filename(file.filename or "upload.png")

            # Save to temp file
            suffix = os.path.splitext(filename)[1].lower() or ".png"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                temp_path = tmp.name
                file.save(temp_path)

            try:
                if AppConfig.MOCK_MODE:
                    # Create deterministic mock overlay
                    image = Image.open(temp_path).convert("RGBA")
                    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(overlay)
                    w, h = image.size
                    rect = [int(w * 0.1), int(h * 0.1), int(w * 0.9), int(h * 0.9)]
                    draw.rectangle(rect, outline=(255, 0, 0, 200), width=max(2, min(w, h) // 100))

                    # Save overlay
                    overlays_dir = ensure_overlays_dir()
                    overlay_id = f"{uuid.uuid4()}.png"
                    overlay_path = os.path.join(overlays_dir, overlay_id)
                    overlay.save(overlay_path, format="PNG")

                    resp = {
                        "ok": True,
                        "mode": "mock",
                        "prediction": {
                            "label": "healthy",
                            "confidence": 0.87,
                            "brightness": 0.62,
                        },
                        "overlay_url": f"/static/overlays/{overlay_id}",
                    }
                else:
                    result = detect_image(temp_path)
                    # result may include an overlay image; if so, save it
                    overlay_url: Optional[str] = None
                    overlay_img = result.get("overlay_image") if isinstance(result, dict) else None
                    if overlay_img is not None:
                        overlays_dir = ensure_overlays_dir()
                        overlay_id = f"{uuid.uuid4()}.png"
                        overlay_path = os.path.join(overlays_dir, overlay_id)
                        overlay_img.save(overlay_path, format="PNG")
                        overlay_url = f"/static/overlays/{overlay_id}"

                    resp = {
                        "ok": True,
                        "mode": "real",
                        "prediction": result.get("prediction", result),
                    }
                    if overlay_url:
                        resp["overlay_url"] = overlay_url

                return jsonify(resp)
            finally:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    # Static overlays served from /static/overlays/<file> automatically by Flask static
    # Adding explicit route for clarity (optional)
    @app.get("/static/overlays/<path:filename>")
    def get_overlay(filename: str):
        return send_from_directory(ensure_overlays_dir(), filename)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=AppConfig.DEBUG)
