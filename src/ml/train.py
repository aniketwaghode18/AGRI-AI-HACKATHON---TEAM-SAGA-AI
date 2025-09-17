def train(data_dir: str, out_dir: str) -> None:
	"""
	Stub: train a model and save checkpoints.
	"""
	print(f"Training with data at {data_dir}, writing outputs to {out_dir}")

if __name__ == "__main__":
	train("data/", "checkpoints/")
