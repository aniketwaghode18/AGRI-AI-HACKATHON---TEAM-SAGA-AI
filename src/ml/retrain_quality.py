import os
import csv
import json
import random
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

try:
	import cv2
	_HAS_CV2 = True
except Exception:
	_HAS_CV2 = False

try:
	from PIL import Image
	_HAS_PIL = True
except Exception:
	_HAS_PIL = False


def create_quality_annotations_from_classification(
	classification_root: Path,
	output_csv: Path,
	quality_mapping: Dict[str, str] = None
) -> None:
	"""
	Create quality-based annotations from classification folders.
	
	Args:
		classification_root: Path to folder with class subfolders
		output_csv: Path to save annotations CSV
		quality_mapping: Maps folder names to quality classes
	"""
	if quality_mapping is None:
		# Default mapping for soybean quality
		quality_mapping = {
			"Intact soybeans": "Healthy",
			"Broken soybeans": "Defective", 
			"Immature soybeans": "Defective",
			"Skin-damaged soybeans": "Defective",
			"Spotted soybeans": "Defective"
		}
	
	annotations = []
	images_dir = classification_root
	
	# Find all class folders
	class_folders = [f for f in images_dir.iterdir() if f.is_dir()]
	
	for class_folder in class_folders:
		class_name = class_folder.name
		quality_class = quality_mapping.get(class_name, "Unknown")
		
		print(f"Processing {class_name} -> {quality_class}")
		
		# Process all images in this class folder
		for img_path in class_folder.rglob("*.*"):
			if not img_path.is_file() or img_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
				continue
				
			# Get image dimensions
			try:
				if _HAS_PIL:
					with Image.open(img_path) as im:
						w, h = im.size
				elif _HAS_CV2:
					img = cv2.imread(str(img_path))
					h, w = img.shape[:2]
				else:
					w, h = 640, 480  # fallback
				
				# Create full-image bounding box
				annotations.append({
					"filename": img_path.name,
					"xmin": 0,
					"ymin": 0, 
					"xmax": w-1,
					"ymax": h-1,
					"label": quality_class
				})
				
			except Exception as e:
				print(f"Error processing {img_path}: {e}")
				continue
	
	# Write CSV
	output_csv.parent.mkdir(parents=True, exist_ok=True)
	with output_csv.open("w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=["filename", "xmin", "ymin", "xmax", "ymax", "label"])
		writer.writeheader()
		writer.writerows(annotations)
	
	print(f"Created {len(annotations)} annotations in {output_csv}")
	
	# Print class distribution
	class_counts = {}
	for ann in annotations:
		class_counts[ann["label"]] = class_counts.get(ann["label"], 0) + 1
	
	print("\nClass distribution:")
	for cls, count in class_counts.items():
		print(f"  {cls}: {count}")


def main():
	import argparse
	parser = argparse.ArgumentParser(description="Create quality-based annotations from classification dataset.")
	parser.add_argument("--input_dir", required=True, help="Classification dataset root")
	parser.add_argument("--output_csv", default="data/raw/quality_annotations.csv", help="Output CSV path")
	args = parser.parse_args()
	
	create_quality_annotations_from_classification(
		Path(args.input_dir),
		Path(args.output_csv)
	)


if __name__ == "__main__":
	main()

