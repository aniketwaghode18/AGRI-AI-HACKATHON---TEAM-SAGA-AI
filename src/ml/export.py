from typing import Any

def export_model(train_artifact_path: str, out_path: str) -> None:
	"""
	Stub: convert a trained model to a deployable artifact (e.g., ONNX).
	"""
	# Implement real export here
	with open(out_path, "w", encoding="utf-8") as f:
		f.write("DUMMY_MODEL")
	print(f"Exported dummy model to {out_path}")
