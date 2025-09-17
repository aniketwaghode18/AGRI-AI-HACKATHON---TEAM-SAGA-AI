import os
import uuid
from pathlib import Path
from typing import Tuple

from flask import Flask, request, jsonify, url_for, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Robust imports: try package-relative first, then absolute fallbacks
try:
	from .config import AppConfig  # type: ignore
except Exception:
	try:
		from src.server.config import AppConfig  # type: ignore
	except Exception:
		from config import AppConfig  # type: ignore

# Inference import: prefer absolute from src.ml, fallback to relative
try:
	from src.ml.inference import detect_image  # type: ignore
except Exception:
	try:
		from ..ml.inference import detect_image  # type: ignore
	except Exception:
		# Last resort: modify sys.path to include project root
		import sys
		sys.path.append(str(Path(__file__).resolve().parents[2]))
		from src.ml.inference import detect_image  # type: ignore

try:
	from PIL import Image, ImageDraw
except Exception:
	Image = None
	ImageDraw = None

# Simple in-memory cache for demo purposes
ANALYSIS_CACHE = {}


def _allowed_file(filename: str, allowed: set) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def _format_text_report(analysis_entry: dict) -> str:
	res = analysis_entry.get("result", analysis_entry)
	dets = res.get("detections", [])
	w = res.get("width")
	h = res.get("height")
	lines = []
	lines.append("AgriVision Analysis Summary")
	lines.append("===========================")
	lines.append(f"Image size: {w}x{h}")
	lines.append(f"Detections: {len(dets)}")
	lines.append("")
	for i, d in enumerate(dets, start=1):
		label = d.get("label", "?")
		conf = d.get("confidence", 0.0)
		bbox = d.get("bbox", [])
		lines.append(f"{i}. {label}  {(conf*100):.1f}%  bbox={bbox}")
	return "\n".join(lines) + "\n"


def create_app() -> Flask:
	config = AppConfig()

	app = Flask(
		__name__,
		static_folder="static",
		static_url_path="/static",
	)
	CORS(app)

	# Directories
	overlays_dir = Path(app.static_folder) / "overlays"
	overlays_dir.mkdir(parents=True, exist_ok=True)
	tmp_dir = Path(getattr(config, "UPLOAD_DIR", "tmp"))
	tmp_dir.mkdir(parents=True, exist_ok=True)

	@app.get("/health")
	def health() -> Tuple[str, int]:
		return jsonify({"status": "ok"}), 200

	@app.post("/analyze")
	def analyze() -> Tuple[str, int]:
		# Size pre-check using Content-Length if provided
		content_length = request.content_length or 0
		if content_length and content_length > config.MAX_IMAGE_SIZE:
			return jsonify({"error": "uploaded file too large"}), 413

		if "image" not in request.files:
			return jsonify({"error": "missing multipart field 'image'"}), 400
		file = request.files["image"]
		if not file or file.filename == "":
			return jsonify({"error": "empty filename"}), 400

		filename = secure_filename(file.filename)
		if not _allowed_file(filename, set(config.ALLOWED_EXTENSIONS)):
			return jsonify({"error": "unsupported file type"}), 415

		# Save to temporary path
		tmp_path = tmp_dir / f"upload_{uuid.uuid4().hex}_{filename}"
		file.save(tmp_path)

		# Post-save size enforcement for clients not setting Content-Length
		try:
			if tmp_path.stat().st_size > config.MAX_IMAGE_SIZE:
				try:
					tmp_path.unlink(missing_ok=True)
				except Exception:
					pass
				return jsonify({"error": "uploaded file too large"}), 413
		except Exception:
			pass

		# Prepare overlay path
		overlay_name = f"{uuid.uuid4().hex}.png"
		overlay_path = overlays_dir / overlay_name
		request_id = uuid.uuid4().hex

		try:
			if getattr(config, "MOCK_MODE", False):
				if Image is None:
					return jsonify({"error": "Pillow not installed for mock overlay"}), 500
				# Deterministic mock response and overlay
				im = Image.open(tmp_path).convert("RGBA")
				draw = ImageDraw.Draw(im, "RGBA")
				w, h = im.size
				box = [int(0.1 * w), int(0.1 * h), int(0.9 * w), int(0.9 * h)]
				draw.rectangle(box, outline=(0, 200, 0, 255), width=4)
				draw.rectangle(box, fill=(0, 200, 0, 40))
				im.save(overlay_path, format="PNG")

				result = {
					"detections": [
						{"label": "healthy_crop", "confidence": 0.97, "bbox": box}
					],
					"width": w,
					"height": h,
				}
			else:
				result = detect_image(str(tmp_path), str(overlay_path))

			# Build URL for overlay
			overlay_url = url_for("static", filename=f"overlays/{overlay_name}", _external=False)
			result["overlay_url"] = overlay_url

			# Cache for report generation
			ANALYSIS_CACHE[request_id] = {
				"result": result,
				"overlay_path": str(overlay_path),
			}

			return jsonify({"ok": True, "request_id": request_id, "result": result}), 200
		except Exception as e:
			return jsonify({"ok": False, "error": str(e)}), 500
		finally:
			try:
				tmp_path.unlink(missing_ok=True)
			except Exception:
				pass

	@app.get("/report_text")
	def report_text() -> Response:
		request_id = request.args.get("request_id")
		if not request_id:
			return Response("missing request_id\n", status=400, mimetype="text/plain; charset=utf-8")
		entry = ANALYSIS_CACHE.get(request_id)
		if not entry:
			return Response("unknown request_id\n", status=404, mimetype="text/plain; charset=utf-8")
		text = _format_text_report(entry)
		return Response(text, status=200, mimetype="text/plain; charset=utf-8")

	return app


if __name__ == "__main__":
	# Respect FLASK_ENV and MOCK_MODE via environment variables
	app = create_app()
	app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_ENV") == "development")
