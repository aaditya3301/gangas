"""
Test data loader for zone_53L1NW with nested folder structure
"""

import numpy as np
from src.data_loader import LiDARDataset

print("\n" + "="*70)
print("TESTING ZONE: zone_53L1NW")
print("="*70)

# Initialize dataset
dataset = LiDARDataset('zone_53L1NW')

# Show summary
print(dataset.get_dataset_summary())

# Show sample file paths
print("\nSample DEM files (first 10):")
for i, dem_path in enumerate(dataset.dem_files[:10]):
    tile_id = dataset._extract_tile_id(dem_path.name)
    print(f"  {i+1}. {dem_path.name} (Tile ID: {tile_id})")
    print(f"     Path: {dem_path.relative_to(dem_path.parent.parent.parent)}")

print("\nSample ORTHO files (first 10):")
for i, ortho_path in enumerate(dataset.ortho_files[:10]):
    tile_id = dataset._extract_tile_id(ortho_path.name)
    print(f"  {i+1}. {ortho_path.name} (Tile ID: {tile_id})")
    print(f"     Path: {ortho_path.relative_to(ortho_path.parent.parent.parent)}")

print("\nMatched pairs (first 10):")
for i, (dem, ortho) in enumerate(dataset.matched_pairs[:10]):
    tile_id = dataset._extract_tile_id(dem.name)
    print(f"  {i+1}. Tile {tile_id}:")
    print(f"     DEM:   {dem.relative_to(dem.parent.parent.parent)}")
    print(f"     ORTHO: {ortho.relative_to(ortho.parent.parent.parent)}")

# Test loading a single tile
if len(dataset.matched_pairs) > 0:
    print("\n" + "="*70)
    print("Testing tile loading...")
    print("="*70)
    
    dem_path, ortho_path = dataset.matched_pairs[0]
    tile_id = dataset._extract_tile_id(dem_path.name)
    
    print(f"\nLoading tile: {tile_id}")
    
    dem, dem_metadata = dataset.load_dem(dem_path)
    rgb = dataset.load_ortho(ortho_path, target_shape=dem.shape)
    
    print(f"[OK] DEM shape: {dem.shape}")
    print(f"[OK] RGB shape: {rgb.shape}")
    print(f"[OK] Elevation: {np.nanmin(dem):.2f}m - {np.nanmax(dem):.2f}m")

print("\n" + "="*70)
print("✅ TEST COMPLETE!")
print("="*70)
