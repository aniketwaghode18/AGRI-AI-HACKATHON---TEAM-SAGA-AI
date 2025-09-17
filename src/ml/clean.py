import csv
import os
from pathlib import Path
from typing import Dict, List

try:
	from PIL import Image
	_HAS_PIL = True
except Exception:
	_HAS_PIL = False


def clean_annotations(images_dir: Path, annotations_csv: Path, out_csv: Path) -> Dict[str, int]:
	images_dir = images_dir.resolve()
	ok, dropped_missing, dropped_invalid, total = 0, 0, 0, 0
	out_csv.parent.mkdir(parents=True, exist_ok=True)

	with annotations_csv.open("r", newline="", encoding="utf-8") as fin, out_csv.open("w", newline="", encoding="utf-8") as fout:
		reader = csv.DictReader(fin)
		fieldnames = ["filename", "xmin", "ymin", "xmax", "ymax", "label"]
		writer = csv.DictWriter(fout, fieldnames=fieldnames)
		writer.writeheader()
		for row in reader:
			total += 1
			fname = row["filename"].strip()
			img_path = images_dir / fname
			if not img_path.exists():
				dropped_missing += 1
				continue
			try:
				if _HAS_PIL:
					with Image.open(img_path) as im:
						w, h = im.size
				else:
					# fallback: skip dimension checks if PIL missing
					w = h = None
				xmin = int(float(row["xmin"]))
				ymin = int(float(row["ymin"]))
				xmax = int(float(row["xmax"]))
				ymax = int(float(row["ymax"]))
				# clamp boxes within image bounds if known
				if w is not None and h is not None:
					xmin = max(0, min(xmin, w - 1))
					xmax = max(0, min(xmax, w - 1))
					ymin = max(0, min(ymin, h - 1))
					ymax = max(0, min(ymax, h - 1))
				# ensure proper ordering
				if xmax <= xmin or ymax <= ymin:
					dropped_invalid += 1
					continue
				writer.writerow({
					"filename": fname,
					"xmin": xmin,
					"ymin": ymin,
					"xmax": xmax,
					"ymax": ymax,
					"label": row["label"].strip(),
				})
				ok += 1
			except Exception:
				dropped_invalid += 1

	return {"kept": ok, "dropped_missing": dropped_missing, "dropped_invalid": dropped_invalid, "total": total}


if __name__ == "__main__":
	import argparse, json
	parser = argparse.ArgumentParser(description="Clean annotations CSV and clamp invalid boxes.")
	parser.add_argument("--images_dir", required=True)
	parser.add_argument("--annotations_csv", required=True)
	parser.add_argument("--out_csv", default="data/raw/annotations_clean.csv")
	args = parser.parse_args()
	stats = clean_annotations(Path(args.images_dir), Path(args.annotations_csv), Path(args.out_csv))
	print(json.dumps(stats, indent=2))
