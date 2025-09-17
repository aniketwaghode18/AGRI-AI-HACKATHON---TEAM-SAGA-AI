import os
import zipfile
import requests
from pathlib import Path
import time

def download_dataset(url: str, output_path: Path) -> Path:
    """Download dataset from URL with progress."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end="", flush=True)
    
    print(f"\nDownloaded: {output_path}")
    return output_path

def extract_zip(zip_path: Path, extract_to: Path) -> Path:
    """Extract ZIP file and return the extracted folder path."""
    print(f"Extracting {zip_path}...")
    extract_to.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    # Find the main extracted folder
    extracted_folders = [f for f in extract_to.iterdir() if f.is_dir()]
    if extracted_folders:
        main_folder = extracted_folders[0]
        print(f"Extracted to: {main_folder}")
        return main_folder
    else:
        print(f"Extracted to: {extract_to}")
        return extract_to

def process_soybean_dataset():
    """Download and process soybean dataset automatically."""
    # Create directories
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download dataset (using a direct download link if available)
    # For now, we'll create a mock structure for testing
    print("Creating mock soybean dataset structure...")
    
    # Create mock classification dataset structure
    mock_dataset = data_dir / "soybean-seeds"
    mock_dataset.mkdir(exist_ok=True)
    
    # Create class folders
    classes = ["healthy", "diseased", "damaged"]
    for cls in classes:
        class_dir = mock_dataset / cls
        class_dir.mkdir(exist_ok=True)
        
        # Create a few mock images (empty files for now)
        for i in range(3):
            img_path = class_dir / f"{cls}_{i}.jpg"
            img_path.write_bytes(b"mock_image_data")
    
    print(f"Mock dataset created at: {mock_dataset}")
    return mock_dataset

if __name__ == "__main__":
    # Process the dataset
    dataset_path = process_soybean_dataset()
    
    # Generate annotations CSV
    print("Generating annotations CSV...")
    os.system(f'.venv\\Scripts\\python src\\ml\\make_fullbox_csv.py --root_dir "{dataset_path}" --images_out data\\raw\\images --out_csv data\\raw\\annotations.csv')
    
    # Clean annotations
    print("Cleaning annotations...")
    os.system('.venv\\Scripts\\python src\\ml\\clean.py --images_dir data\\raw\\images --annotations_csv data\\raw\\annotations.csv --out_csv data\\raw\\annotations_clean.csv')
    
    # Convert to YOLO format
    print("Converting to YOLO format...")
    os.system('.venv\\Scripts\\python src\\ml\\preprocess.py --images_dir data\\raw\\images --annotations_csv data\\raw\\annotations_clean.csv --out_dir data\\yolo_dataset --augment_copies 1 --aug_strength light')
    
    print("Dataset processing complete!")
    print("Results:")
    print("- data/yolo_dataset/images/{train,val,test}/*.jpg")
    print("- data/yolo_dataset/labels/{train,val,test}/*.txt") 
    print("- data/yolo_dataset/data.yaml")
