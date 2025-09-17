import os
from typing import Set

class AppConfig:
	"""
	Configuration for the Flask server.

	Toggle mock mode via environment variables (any of the following):
	- Windows cmd:  set MOCK_MODE=1  (or: set MOCK=1)
	- Bash (macOS/Linux):  export MOCK_MODE=1  (or: MOCK=1)
	- Disable mock mode by setting to 0.

	Example mock response structure (returned when MOCK_MODE=1):
	{
	  "ok": true,
	  "result": {
	    "label": "healthy_crop",
	    "confidence": 0.97,
	    "notes": "Mocked response. Set MOCK_MODE=0 to use real model.",
	    "file": "sample.jpg"
	  }
	}
	"""

	def __init__(self):
		# Core settings
		self.MOCK_MODE: bool = self._read_bool_env(["MOCK_MODE", "MOCK"], default=True)
		self.MODEL_PATH: str = os.getenv("MODEL_PATH", "models/model.onnx")
		self.OVERLAY_DIR: str = os.getenv("OVERLAY_DIR", "tmp")

		# Upload constraints
		self.ALLOWED_EXTENSIONS: Set[str] = self._read_exts_env(
			"ALLOWED_EXTENSIONS",
			default={"jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff"},
		)
		# Bytes. You can specify MAX_IMAGE_SIZE (bytes) or MAX_IMAGE_SIZE_MB (megabytes).
		self.MAX_IMAGE_SIZE: int = self._read_size_env()

		# Backward-compatibility keys used elsewhere in the codebase
		# (Prefer the new names above in new code)
		self.MOCK = int(self.MOCK_MODE)  # legacy integer form
		self.UPLOAD_DIR = self.OVERLAY_DIR

	def __getitem__(self, key):
		return getattr(self, key, None)

	def get(self, key, default=None):
		return getattr(self, key, default)

	@staticmethod
	def _read_bool_env(names, default: bool) -> bool:
		for name in names:
			val = os.getenv(name)
			if val is not None:
				val = val.strip().lower()
				if val in {"1", "true", "yes", "y", "on"}:
					return True
				if val in {"0", "false", "no", "n", "off"}:
					return False
		return default

	@staticmethod
	def _read_exts_env(name: str, default: Set[str]) -> Set[str]:
		val = os.getenv(name)
		if not val:
			return default
		return {p.strip().lstrip(".").lower() for p in val.split(",") if p.strip()}

	@staticmethod
	def _read_size_env() -> int:
		# Prefer explicit bytes; else allow MB convenience var
		val_b = os.getenv("MAX_IMAGE_SIZE")
		val_mb = os.getenv("MAX_IMAGE_SIZE_MB")
		if val_b and val_b.isdigit():
			return int(val_b)
		if val_mb and val_mb.isdigit():
			return int(val_mb) * 1024 * 1024
		# Default: 10 MB
		return 10 * 1024 * 1024
