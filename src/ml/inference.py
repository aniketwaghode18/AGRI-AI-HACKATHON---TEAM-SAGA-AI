from __future__ import annotations
from typing import Any, Dict, List

import os
from PIL import Image, ImageDraw


def detect_image(image_path: str) -> Dict[str, Any]:
    """
    Run object detection on an image, returning API-contract JSON and optional overlay image.
    Falls back to mock detection if Ultralytics is unavailable or model load fails.
    """
    try:
        from ultralytics import YOLO  # type: ignore
        # Lazy import succeeded; try to load a model
        from src.server.config import AppConfig  # late import to avoid cycles at import time

        model_path = AppConfig.MODEL_PATH
        model = None
        try:
            if os.path.isfile(model_path):
                model = YOLO(model_path)
            else:
                # Fallback to a small default model if available
                model = YOLO("yolov8n.pt")
        except Exception:
            # Loading failed; fall back to mock
            return mock_detect(image_path)

        try:
            results = model(image_path, verbose=False)
        except Exception:
            return mock_detect(image_path)

        if not results:
            return mock_detect(image_path)

        result = results[0]
        names = None
        try:
            names = result.names if hasattr(result, "names") else getattr(model.model, "names", None)
        except Exception:
            names = None

        detections = _parse_model_output(result, names)

        # Build overlay
        base_img = Image.open(image_path).convert("RGBA")
        overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        w, h = base_img.size
        for det in detections:
            x1, y1, x2, y2 = det.get("box", [0, 0, 0, 0])
            label = det.get("label", "obj")
            conf = det.get("confidence", 0.0)
            draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0, 220), width=max(2, min(w, h) // 150))
            text = f"{label} {conf:.2f}"
            # Simple text background
            tw, th = draw.textlength(text), 12
            draw.rectangle([x1, max(0, y1 - th - 4), x1 + tw + 6, y1], fill=(0, 0, 0, 160))
            draw.text((x1 + 3, max(0, y1 - th - 2)), text, fill=(255, 255, 255, 255))

        return {
            "prediction": {"objects": detections},
            "overlay_image": overlay,
        }
    except Exception:
        # Ultralytics not installed or other failure
        return mock_detect(image_path)


def _parse_model_output(result: Any, names: Any = None) -> List[Dict[str, Any]]:
    """Convert model output to the API JSON detections list.

    Returns a list of {label, confidence, box:[x1,y1,x2,y2]}.
    """
    detections: List[Dict[str, Any]] = []
    try:
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        xyxy = getattr(boxes, "xyxy", None)
        conf = getattr(boxes, "conf", None)
        cls = getattr(boxes, "cls", None)

        if xyxy is None or conf is None or cls is None:
            return detections

        # Convert tensors to lists safely
        try:
            xyxy_list = xyxy.cpu().tolist()
            conf_list = conf.cpu().tolist()
            cls_list = cls.cpu().tolist()
        except Exception:
            xyxy_list = list(xyxy)
            conf_list = list(conf)
            cls_list = list(cls)

        for i in range(min(len(xyxy_list), len(conf_list), len(cls_list))):
            x1, y1, x2, y2 = xyxy_list[i]
            c = float(conf_list[i])
            class_idx = int(cls_list[i])
            label = None
            if isinstance(names, dict):
                label = names.get(class_idx, str(class_idx))
            elif isinstance(names, list) and 0 <= class_idx < len(names):
                label = names[class_idx]
            else:
                label = str(class_idx)

            detections.append({
                "label": label,
                "confidence": round(c, 4),
                "box": [float(x1), float(y1), float(x2), float(y2)],
            })
    except Exception:
        # If parsing fails, return empty list and let caller decide
        return []

    return detections


def mock_detect(image_path: str) -> Dict[str, Any]:
    """Return fixed predictions and draw a simple overlay rectangle.

    The overlay is returned as a PIL Image under key 'overlay_image'.
    """
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size

    # Fixed central box
    x1, y1 = int(w * 0.2), int(h * 0.2)
    x2, y2 = int(w * 0.8), int(h * 0.8)

    overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0, 220), width=max(2, min(w, h) // 100))

    detections = [{
        "label": "plant",
        "confidence": 0.87,
        "box": [float(x1), float(y1), float(x2), float(y2)],
    }]

    return {
        "prediction": {"objects": detections},
        "overlay_image": overlay,
        "mode": "mock",
    }
