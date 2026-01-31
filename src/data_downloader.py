"""
Automatic Data Downloader
Downloads LiDAR data from external storage on first run
"""

import os
import requests
from pathlib import Path
import zipfile
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

def download_file(url: str, destination: Path):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    with open(destination, 'wb') as file, tqdm(
        desc=destination.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            bar.update(len(chunk))

def extract_zip(zip_path: Path, extract_to: Path):
    """Extract zip file"""
    print(f"📦 Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✅ Extracted to {extract_to}")

def download_lidar_data(force=False):
    """Download LiDAR data if not present"""
    
    # Check if data already exists
    zone_dirs = [DATA_DIR / 'raw' / 'zone_53H13SE', DATA_DIR / 'raw' / 'zone_53L1NW']
    if not force and all(d.exists() for d in zone_dirs):
        print("✅ LiDAR data already present")
        return True
    
    print("🌐 Downloading LiDAR data from external storage...")
    
    # Add your Google Drive/Dropbox/OneDrive links here
    # Format: Direct download link (use gdown for Google Drive)
    DATA_URLS = {
        'zone_53H13SE': 'https://drive.google.com/uc?id=1KyI12jXZpJ7WgjN6haClB6p7NXfFZ8mm',
        'zone_53L1NW': 'https://drive.google.com/uc?id=1QIQKk9IA-8ktjJYf1WAegD1zLDLPNidm',
    }
    
    for zone_name, url in DATA_URLS.items():
        if url == 'YOUR_GOOGLE_DRIVE_LINK_HERE':
            print(f"⚠️ No download URL configured for {zone_name}")
            continue
            
        zip_path = DATA_DIR / f'{zone_name}.zip'
        extract_path = DATA_DIR / 'raw'
        
        # Download
        print(f"📥 Downloading {zone_name}...")
        download_file(url, zip_path)
        
        # Extract
        extract_zip(zip_path, extract_path)
        
        # Clean up zip
        zip_path.unlink()
        print(f"🗑️ Removed {zip_path.name}")
    
    print("✅ All data downloaded and ready!")
    return True

if __name__ == "__main__":
    download_lidar_data()
