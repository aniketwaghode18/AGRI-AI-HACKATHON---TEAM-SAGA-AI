import csv
import os
from pathlib import Path
from typing import List

try:
	from PIL import Image
	_HAS_PIL = True
except Exception:
	_HAS_PIL = False

"""
Generate annotations.csv for detection from a classification dataset directory tree.
Input folder structure:
  root_dir/
    class_a/*.jpg
    class_b/*.jpg
    ...
Output CSV columns: filename,xmin,ymin,xmax,ymax,label
Images are expected to be copied/moved under data/raw/images; this script writes
relative filenames for that directory.
"""

def make_fullbox_csv(root_dir: Path, images_out_dir: Path, out_csv: Path) -> int:
	root_dir = root_dir.resolve()
	images_out_dir.mkdir(parents=True, exist_ok=True)
	count = 0
	with out_csv.open("w", newline="", encoding="utf-8") as f:
		writer = csv.writer(f)
		writer.writerow(["filename", "xmin", "ymin", "xmax", "ymax", "label"])
		for class_dir in sorted([p for p in root_dir.iterdir() if p.is_dir()]):
			label = class_dir.name
			for img_path in class_dir.rglob("*.*"):
				if not img_path.is_file():
					continue
				try:
					# Copy/flatten into images_out_dir keeping unique names by prefixing label
					# If name collision, prefix with label and an index
					filename = f"{label}_{img_path.name}"
					dst_path = images_out_dir / filename
					if dst_path.exists():
						base = img_path.stem
						i = 1
						while True:
							candidate = images_out_dir / f"{label}_{base}_{i}{img_path.suffix}"
							if not candidate.exists():
								dst_path = candidate
								break
							i += 1
					# Copy file
					dst_path.write_bytes(img_path.read_bytes())
					# Determine image size
					if _HAS_PIL:
						with Image.open(dst_path) as im:
							w, h = im.size
					else:
						# Default size if PIL missing (not ideal)
						w = h = 640
					# Full-image bbox
					xmin, ymin, xmax, ymax = 0, 0, max(1, w - 1), max(1, h - 1)
					writer.writerow([filename, xmin, ymin, xmax, ymax, label])
					count += 1
				except Exception:
					continue
	return count

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description="Create detection CSV with full-image boxes from classification dataset.")
	parser.add_argument("--root_dir", required=True, help="Classification dataset root with class subfolders")
	parser.add_argument("--images_out", default="data/raw/images", help="Where to copy/flatten images")
	parser.add_argument("--out_csv", default="data/raw/annotations.csv", help="Output CSV path")
	args = parser.parse_args()
	n = make_fullbox_csv(Path(args.root_dir), Path(args.images_out), Path(args.out_csv))
	print(f"wrote {n} rows to {args.out_csv}")
