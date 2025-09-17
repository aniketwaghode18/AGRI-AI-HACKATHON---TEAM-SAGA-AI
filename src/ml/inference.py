import os
from typing import Any, Dict, List, Optional, Tuple

try:
	from PIL import Image, ImageDraw
except Exception:
	Image = None
	ImageDraw = None

# Try to import ultralytics YOLO if available
try:
	from ultralytics import YOLO  # type: ignore
	_ULTRA_AVAILABLE = True
except Exception:
	YOLO = None  # type: ignore
	_ULTRA_AVAILABLE = False


def _draw_overlay(
	image_path: str,
	overlay_output_path: Optional[str],
	boxes_xyxy: List[Tuple[int, int, int, int]],
	color: Tuple[int, int, int, int] = (0, 200, 0, 255),
	fill_alpha: int = 40,
) -> Tuple[int, int]:
	"""
	Draws simple rectangles for detections onto an overlay image saved as PNG.
	Returns (width, height). If PIL is not available or overlay_output_path is None, no file is saved.
	"""
	if Image is None:
		with Image.open(image_path) as im:
			w, h = im.size
		return w, h

	with Image.open(image_path).convert("RGBA") as im:
		w, h = im.size
		if overlay_output_path:
			draw = ImageDraw.Draw(im, "RGBA")
			for x1, y1, x2, y2 in boxes_xyxy:
				draw.rectangle([x1, y1, x2, y2], outline=color, width=4)
				draw.rectangle([x1, y1, x2, y2], fill=(color[0], color[1], color[2], fill_alpha))
			im.save(overlay_output_path, format="PNG")
	return w, h


def _parse_model_output(
	model_output: Any,
	image_size: Tuple[int, int],
	class_names: Optional[Dict[int, str]] = None,
) -> Dict[str, Any]:
	"""
	Converts model output to API JSON contract:
	{
	  "detections": [{"label": str, "confidence": float, "bbox": [x1,y1,x2,y2]}, ...],
	  "width": int,
	  "height": int
	}
	"""
	w, h = image_size
	response: Dict[str, Any] = {"detections": [], "width": w, "height": h}

	try:
		# ultralytics Results object
		# Expecting list-like, take first result
		res = model_output[0] if isinstance(model_output, (list, tuple)) else model_output
		boxes = getattr(res, "boxes", None)
		names = class_names or getattr(res, "names", {}) or {}
		if boxes is not None:
			xyxy = getattr(boxes, "xyxy", None)
			conf = getattr(boxes, "conf", None)
			cls_idx = getattr(boxes, "cls", None)
			if xyxy is not None:
				for i in range(len(xyxy)):
					coords = [int(v) for v in list(xyxy[i].tolist())]
					confidence = float(conf[i].item()) if conf is not None else 0.0
					cls_i = int(cls_idx[i].item()) if cls_idx is not None else -1
					label = names.get(cls_i, f"cls_{cls_i}") if isinstance(names, dict) else str(cls_i)
					response["detections"].append({
						"label": label,
						"confidence": round(confidence, 4),
						"bbox": coords,
					})
	except Exception:
		# Fallback: empty detections if parse fails
		pass

	return response


def mock_detect(image_path: str, overlay_output_path: Optional[str] = None) -> Dict[str, Any]:
	"""
	Returns a fixed mock detection and writes a simple overlay PNG if path provided.
	"""
	# Fixed green box at 10%..90%
	if Image is not None:
		with Image.open(image_path) as im:
			w, h = im.size
	else:
		# Minimal probing if PIL missing; rely on draw helper to get size
		with Image.open(image_path) as im:  # type: ignore
			w, h = im.size

	box = [int(0.1 * w), int(0.1 * h), int(0.9 * w), int(0.9 * h)]
	_draw_overlay(image_path, overlay_output_path, [tuple(box)])
	return {
		"detections": [
			{"label": "healthy_crop", "confidence": 0.97, "bbox": box}
		],
		"width": w,
		"height": h,
	}


def detect_image(image_path: str, overlay_output_path: Optional[str] = None) -> Dict[str, Any]:
	"""
	Non-async detection entrypoint.
	- If ultralytics is available and a model is loadable (MODEL_PATH env), run real inference.
	- Otherwise, fall back to mock_detect.
	- If overlay_output_path is provided, save an overlay PNG with rectangles.
	Returns dict matching the API JSON contract.
	"""
	model_path = os.getenv("MODEL_PATH")

	# Try real inference with ultralytics YOLO
	if _ULTRA_AVAILABLE and model_path and os.path.exists(model_path):
		try:
			model = YOLO(model_path)  # type: ignore
			results = model.predict(image_path, verbose=False)  # type: ignore

			# Build list of boxes for overlay
			boxes_for_overlay: List[Tuple[int, int, int, int]] = []
			try:
				res0 = results[0]
				xyxy = res0.boxes.xyxy if hasattr(res0, "boxes") else None
				if xyxy is not None:
					for i in range(len(xyxy)):
						coords = [int(v) for v in list(xyxy[i].tolist())]
						boxes_for_overlay.append(tuple(coords))
			except Exception:
				pass

			# Determine image size and draw overlay if requested
			if Image is not None:
				with Image.open(image_path) as im:
					w, h = im.size
			else:
				with Image.open(image_path) as im:  # type: ignore
					w, h = im.size

			if overlay_output_path:
				_draw_overlay(image_path, overlay_output_path, boxes_for_overlay)

			return _parse_model_output(results, (w, h), getattr(model, "names", None))
		except Exception:
			# Fall through to mock on any failure
			pass

	# Fallback mock
	return mock_detect(image_path, overlay_output_path)
