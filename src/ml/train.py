import argparse
import os
from pathlib import Path

# ultralytics is optional in runtime; required for training
try:
	from ultralytics import YOLO  # type: ignore
	_HAS_ULTRA = True
except Exception:
	YOLO = None  # type: ignore
	_HAS_ULTRA = False


def train(data_yaml: str, model: str = "yolov8n.pt", epochs: int = 20, imgsz: int = 640, device: str = "") -> None:
	if not _HAS_ULTRA:
		raise RuntimeError("ultralytics not installed. Install with: pip install ultralytics")
	if not os.path.exists(data_yaml):
		raise FileNotFoundError(f"data.yaml not found: {data_yaml}")

	yolo = YOLO(model)  # type: ignore
	yolo.train(
		data=data_yaml,
		epochs=epochs,
		imgsz=imgsz,
		device=device,  # "" auto, "cpu", "0" for first GPU
		project="runs/train",
		name=Path(model).stem,
	)


def main():
	parser = argparse.ArgumentParser(description="Train YOLO model using ultralytics.")
	parser.add_argument("--data", type=str, required=True, help="Path to data.yaml")
	parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model (e.g., yolov8n.pt)")
	parser.add_argument("--epochs", type=int, default=20, help="Number of epochs")
	parser.add_argument("--img", type=int, default=640, help="Image size")
	parser.add_argument("--device", type=str, default="", help='Device: "" auto, "cpu", "0" for GPU 0')
	args = parser.parse_args()

	train(args.data, args.model, args.epochs, args.img, args.device)


if __name__ == "__main__":
	main()

"""
Quick start:

1) Install:
   pip install ultralytics

2) Train on prepared dataset:
   python src/ml/train.py --data data/data.yaml --epochs 20 --img 640

3) GPU example:
   python src/ml/train.py --data data/data.yaml --epochs 20 --img 640 --device 0

4) CPU example:
   python src/ml/train.py --data data/data.yaml --epochs 10 --img 640 --device cpu
"""