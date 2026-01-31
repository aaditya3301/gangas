"""
Compare the two zones
"""
from src.data_loader import LiDARDataset
import numpy as np

print('='*70)
print('ZONE COMPARISON ANALYSIS')
print('='*70)

# Load both zones
zone1 = LiDARDataset('zone_53H13SE', load_ortho=True)
zone2 = LiDARDataset('zone_53L1NW', load_ortho=False)

print('\nBASIC STATISTICS:')
print(f'\nZone 53H13SE:')
print(f'  DEM files: {len(zone1.dem_files)}')
print(f'  ORTHO files: {len(zone1.ortho_files)}')
print(f'  Matched pairs: {len(zone1.matched_pairs)}')

print(f'\nZone 53L1NW:')
print(f'  DEM files: {len(zone2.dem_files)}')
print(f'  ORTHO files: 0 (DEM-only mode)')
print(f'  Matched pairs: {len(zone2.matched_pairs)}')

# Load sample tiles
print('\nTILE SIZE ANALYSIS:')
dem1_path, ortho1_path = zone1.matched_pairs[0]
dem1, meta1 = zone1.load_dem(dem1_path)

dem2_path, _ = zone2.matched_pairs[0]
dem2, meta2 = zone2.load_dem(dem2_path)

print(f'\nZone 53H13SE (Sample Tile):')
print(f'  Dimensions: {dem1.shape}')
print(f'  Resolution: {meta1["resolution"]}')
print(f'  Elevation range: {np.nanmin(dem1):.2f}m - {np.nanmax(dem1):.2f}m')
print(f'  Area per tile: {dem1.shape[0] * dem1.shape[1] / 1e6:.3f} km2')

print(f'\nZone 53L1NW (Sample Tile):')
print(f'  Dimensions: {dem2.shape}')
print(f'  Resolution: {meta2["resolution"]}')
print(f'  Elevation range: {np.nanmin(dem2):.2f}m - {np.nanmax(dem2):.2f}m')
print(f'  Area per tile: {dem2.shape[0] * dem2.shape[1] / 1e6:.3f} km2')

# Total coverage
total_area_1 = len(zone1.matched_pairs) * dem1.shape[0] * dem1.shape[1] / 1e6
total_area_2 = len(zone2.matched_pairs) * dem2.shape[0] * dem2.shape[1] / 1e6

print(f'\nTOTAL COVERAGE:')
print(f'  Zone 53H13SE: {total_area_1:.2f} km2')
print(f'  Zone 53L1NW: {total_area_2:.2f} km2')
print(f'  Size ratio: Zone 53L1NW is {total_area_2/total_area_1:.1f}x larger')

# Tile naming patterns
print(f'\nNAMING PATTERNS:')
print(f'\nZone 53H13SE samples:')
for i, (dem, ortho) in enumerate(zone1.matched_pairs[:3]):
    tid = zone1._extract_tile_id(dem.name)
    print(f'  Tile {tid}: {dem.name}')

print(f'\nZone 53L1NW samples:')
for i, (dem, _) in enumerate(zone2.matched_pairs[:3]):
    tid = zone2._extract_tile_id(dem.name)
    print(f'  Tile {tid}: {dem.name}')

# Geographic location (based on tile IDs)
print(f'\nGEOGRAPHIC INFO (from tile IDs):')
zone1_tiles = [zone1._extract_tile_id(dem.name) for dem, _ in zone1.matched_pairs]
zone2_tiles = [zone2._extract_tile_id(dem.name) for dem, _ in zone2.matched_pairs[:5]]

print(f'\nZone 53H13SE tile ID range:')
print(f'  First: {min(zone1_tiles)} | Last: {max(zone1_tiles)}')
print(f'  Row range: {min(t[:3] for t in zone1_tiles)} - {max(t[:3] for t in zone1_tiles)}')

print(f'\nZone 53L1NW tile ID range (sample):')
print(f'  First: {min(zone2_tiles)} | Last: {max(zone2_tiles)}')
print(f'  Row range: {min(t[:3] for t in zone2_tiles)} - {max(t[:3] for t in zone2_tiles)}')

# Data organization
print(f'\nDATA ORGANIZATION:')
print(f'\nZone 53H13SE:')
print(f'  Structure: Flat (DEM/ and ORTHO/ folders)')
print(f'  File pattern: EGM-NMCG_*.tif and NMCG_*.tif')

print(f'\nZone 53L1NW:')
print(f'  Structure: Nested (5 DEM subfolders, 4 ORTHO subfolders)')
print(f'  File patterns: EGM-NHP_*.tif, EGM-NMCG_*.tif, EGM-NMCG-*.tif')
print(f'  Subfolders: NHP 3-11, NHP 3-12, NMCG 1-2, NMCG 1-3, etc.')

print('\n' + '='*70)
