"""
Data Organization Script
Moves existing files to proper directory structure
"""

import os
import shutil
from pathlib import Path

def organize_existing_data():
    """Move existing data files to organized structure"""
    
    project_root = Path(__file__).parent
    old_data_dir = project_root / 'data'
    
    # Target directories
    dem_target = project_root / 'data' / 'raw' / 'zone_53H13SE' / 'DEM'
    ortho_target = project_root / 'data' / 'raw' / 'zone_53H13SE' / 'ORTHO'
    
    print("\n📦 Organizing Existing Data Files...\n")
    
    # Find and move files
    moved_files = []
    
    if old_data_dir.exists():
        for file in old_data_dir.iterdir():
            if file.is_file():
                # Determine target based on filename
                if 'EGM-NMCG' in file.name or 'DEM' in file.name.upper():
                    target_dir = dem_target
                    category = "DEM"
                elif 'NMCG' in file.name or 'ORTHO' in file.name.upper():
                    target_dir = ortho_target
                    category = "ORTHO"
                else:
                    print(f"  ⚠️ Skipping unknown file: {file.name}")
                    continue
                
                # Move file
                target_path = target_dir / file.name
                
                if target_path.exists():
                    print(f"  ⏭️ Already exists: {file.name}")
                else:
                    try:
                        shutil.move(str(file), str(target_path))
                        print(f"  ✓ Moved to {category}: {file.name}")
                        moved_files.append(file.name)
                    except Exception as e:
                        print(f"  ❌ Error moving {file.name}: {e}")
    
    if moved_files:
        print(f"\n✅ Organized {len(moved_files)} files!")
    else:
        print("\n⚠️ No files found to organize.")
        print("   Files may already be in correct locations.")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Download additional files from FTP (see DATA_DOWNLOAD_GUIDE.md)")
    print("2. Ensure DEM and ORTHO files have matching tile IDs")
    print("3. Run: python src/data_loader.py (to verify)")
    print("="*60 + "\n")


if __name__ == '__main__':
    organize_existing_data()
