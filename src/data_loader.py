"""
Data Loader Utility
Handles reading and validating LiDAR datasets
"""

import os
import rasterio
import numpy as np
from pathlib import Path
import json
import re
from typing import Tuple, Dict, List

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED = PROJECT_ROOT / 'data' / 'processed'


class LiDARDataset:
    """Manages LiDAR DEM and ORTHO image pairs"""
    
    def __init__(self, zone_name: str = 'zone_53H13SE', load_ortho: bool = True):
        """
        Initialize dataset loader
        
        Args:
            zone_name: Name of geographic zone (e.g., 'zone_53H13SE')
            load_ortho: If False, skip ORTHO scanning (DEM-only mode for large datasets)
        """
        self.zone_name = zone_name
        self.enable_ortho = load_ortho  # Renamed to avoid conflict with method name
        self.dem_dir = DATA_RAW / zone_name / 'DEM'
        self.ortho_dir = DATA_RAW / zone_name / 'ORTHO'
        
        # Scan available files
        self.dem_files = self._scan_tif_files(self.dem_dir)
        self.ortho_files = self._scan_tif_files(self.ortho_dir) if load_ortho else []
        
        # Find matched pairs only (or just DEM files in DEM-only mode)
        self.matched_pairs = self._find_all_matched_pairs()
        
    def _scan_tif_files(self, directory: Path) -> List[Path]:
        """Recursively find all .tif files in directory and subdirectories"""
        if not directory.exists():
            print(f"WARNING Directory not found: {directory}")
            return []
        
        # Recursively find all .tif files (including in subdirectories)
        tif_files = list(directory.rglob('*.tif'))
        # Filter out .ovr files (overviews) and geodatabase files
        tif_files = [f for f in tif_files if not f.name.endswith('.ovr') 
                     and '.gdb' not in str(f) 
                     and '.Overviews' not in str(f)]
        print(f"OK Found {len(tif_files)} .tif files in {directory.name} (recursive)")
        return sorted(tif_files)
    
    def _extract_tile_id(self, filename: str) -> str:
        """
        Extract tile ID from filename
        Examples:
        - 'EGM-NMCG_2063195.tif' -> '2063195'
        - 'EGM-NHP_2123200.tif' -> '2123200'
        - 'EGM-NMCG-7923199.tif' -> '7923199'
        """
        # Extract 7-digit number from filename
        match = re.search(r'\d{7}', filename)
        return match.group(0) if match else None
    
    def _find_all_matched_pairs(self) -> List[Tuple[Path, Path]]:
        """
        Find all DEM files that have matching ORTHO files.
        In DEM-only mode, returns (dem_file, None) tuples.
        Handles various naming patterns:
        - DEM: EGM-NMCG_*.tif, EGM-NHP_*.tif, EGM-NMCG-*.tif
        - ORTHO: NMCG_*.tif, NHP_*.tif
        """
        matched = []
        
        # DEM-only mode: return all DEM files with None for ORTHO
        if not self.enable_ortho:
            for dem_file in self.dem_files:
                matched.append((dem_file, None))
            print(f"[OK] Found {len(matched)} DEM files (DEM-only mode)")
            return matched
        
        # Normal mode: Build a map of tile_id -> ortho_path for fast lookup
        ortho_map = {}
        for ortho_file in self.ortho_files:
            tile_id = self._extract_tile_id(ortho_file.name)
            if tile_id:
                ortho_map[tile_id] = ortho_file
        
        # Match DEM files with ORTHO files
        for dem_file in self.dem_files:
            tile_id = self._extract_tile_id(dem_file.name)
            if not tile_id:
                continue
            
            # Check if we have a matching ORTHO file
            if tile_id in ortho_map:
                matched.append((dem_file, ortho_map[tile_id]))
        
        print(f"[OK] Found {len(matched)} matched DEM-ORTHO pairs")
        return matched
    
    def find_matching_pair(self, dem_filename: str = None) -> Tuple[Path, Path]:
        """
        Find matching ORTHO file for a given DEM file, or return first available pair
        
        Args:
            dem_filename: Name of DEM file (optional). If None, returns first matched pair
            
        Returns:
            Tuple of (dem_path, ortho_path)
        """
        # If no filename specified, return first matched pair
        if dem_filename is None:
            if len(self.matched_pairs) == 0:
                raise FileNotFoundError("No matched DEM-ORTHO pairs found!")
            dem_path, ortho_path = self.matched_pairs[0]
            print(f"[OK] Using first matched pair: {dem_path.name} <-> {ortho_path.name}")
            return dem_path, ortho_path
        
        # Extract tile ID from DEM filename
        tile_id = self._extract_tile_id(dem_filename)
        if not tile_id:
            raise ValueError(f"Could not extract tile ID from: {dem_filename}")
        
        # Find DEM file
        dem_path = self.dem_dir / dem_filename
        if not dem_path.exists():
            raise FileNotFoundError(f"DEM file not found: {dem_path}")
        
        # Find matching ORTHO (format: 'NMCG_2063195.tif')
        ortho_filename = f'NMCG_{tile_id}.tif'
        ortho_path = self.ortho_dir / ortho_filename
        
        if not ortho_path.exists():
            raise FileNotFoundError(f"Matching ORTHO not found for tile {tile_id}")
        
        print(f"[OK] Matched pair: {dem_filename} <-> {ortho_path.name}")
        return dem_path, ortho_path
    
    def get_all_pairs(self) -> List[Tuple[Path, Path]]:
        """Get all matched DEM-ORTHO pairs"""
        return self.matched_pairs
    
    def load_combined_tiles(self) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Load and combine all matched tile pairs into a geographic mosaic.
        Arranges tiles side-by-side based on their geographic positions.
        
        Returns:
            Tuple of (combined_dem, combined_rgb, metadata)
        """
        if len(self.matched_pairs) == 0:
            raise ValueError("No matched pairs available to combine")
        
        print(f"\n[INFO] Combining {len(self.matched_pairs)} tiles into geographic mosaic...")
        
        # Parse tile IDs and organize by grid position
        # Tile ID format: RRRCCCCC (3-digit row + 4-digit column)
        tiles_by_position = {}
        
        for dem_path, ortho_path in self.matched_pairs:
            tile_id = self._extract_tile_id(dem_path.name)
            if tile_id:
                row = int(tile_id[:3])  # First 3 digits = row
                col = int(tile_id[3:])  # Last 4 digits = column
                tiles_by_position[(row, col)] = (dem_path, ortho_path, tile_id)
        
        # Find grid bounds
        rows = sorted(set(pos[0] for pos in tiles_by_position.keys()))
        cols = sorted(set(pos[1] for pos in tiles_by_position.keys()))
        
        print(f"  Grid layout: {len(rows)} rows x {len(cols)} columns")
        
        # Create grid of tiles (row by row)
        grid_dem = []
        grid_rgb = []
        
        # First pass: find max dimensions for padding
        max_tile_height = 0
        max_tile_width = 0
        
        for dem_path, ortho_path, _ in tiles_by_position.values():
            dem, _ = self.load_dem(dem_path)
            max_tile_height = max(max_tile_height, dem.shape[0])
            max_tile_width = max(max_tile_width, dem.shape[1])
        
        print(f"  Standard tile size: {max_tile_height} x {max_tile_width}")
        
        # Second pass: load and pad tiles to standard size
        for row_idx, row in enumerate(rows):
            print(f"  Processing row {row_idx+1}/{len(rows)} (row {row})...")
            row_dem_tiles = []
            row_rgb_tiles = []
            
            for col in cols:
                if (row, col) in tiles_by_position:
                    dem_path, ortho_path, tile_id = tiles_by_position[(row, col)]
                    print(f"    Loading tile {tile_id}...")
                    dem, _ = self.load_dem(dem_path)
                    
                    # Load RGB if available, otherwise create grayscale
                    if ortho_path and self.enable_ortho:
                        rgb = self.load_ortho(ortho_path, target_shape=dem.shape)
                    else:
                        # Create grayscale heightmap
                        normalized = ((dem - np.nanmin(dem)) / (np.nanmax(dem) - np.nanmin(dem)) * 255).astype(np.uint8)
                        rgb = np.stack([normalized, normalized, normalized], axis=-1)
                    
                    # Pad to standard size if needed
                    if dem.shape[0] < max_tile_height or dem.shape[1] < max_tile_width:
                        pad_height = max_tile_height - dem.shape[0]
                        pad_width = max_tile_width - dem.shape[1]
                        dem = np.pad(dem, ((0, pad_height), (0, pad_width)), constant_values=np.nan)
                        rgb = np.pad(rgb, ((0, pad_height), (0, pad_width), (0, 0)), constant_values=0)
                    
                    row_dem_tiles.append(dem)
                    row_rgb_tiles.append(rgb)
            
            if row_dem_tiles:
                # Concatenate tiles horizontally (side by side)
                row_dem = np.hstack(row_dem_tiles)
                row_rgb = np.hstack(row_rgb_tiles)
                grid_dem.append(row_dem)
                grid_rgb.append(row_rgb)
        
        # Pad rows to same width before stacking
        max_row_width = max(row.shape[1] for row in grid_dem)
        
        for i in range(len(grid_dem)):
            if grid_dem[i].shape[1] < max_row_width:
                pad_width = max_row_width - grid_dem[i].shape[1]
                grid_dem[i] = np.pad(grid_dem[i], ((0, 0), (0, pad_width)), constant_values=np.nan)
                grid_rgb[i] = np.pad(grid_rgb[i], ((0, 0), (0, pad_width), (0, 0)), constant_values=0)
        
        # Stack rows vertically
        print("  Assembling final mosaic...")
        combined_dem = np.vstack(grid_dem)
        combined_rgb = np.vstack(grid_rgb)
        
        metadata = {
            'num_tiles': len(tiles_by_position),
            'grid_layout': f"{len(rows)} rows x {len(cols)} columns",
            'combined_shape': combined_dem.shape,
            'tiles': sorted([tid for _, _, tid in tiles_by_position.values()])
        }
        
        print(f"[OK] Geographic mosaic created: {combined_dem.shape}")
        print(f"  Elevation range: {np.nanmin(combined_dem):.2f}m to {np.nanmax(combined_dem):.2f}m")
        
        return combined_dem, combined_rgb, metadata
    
    def load_dem(self, filepath: Path) -> Tuple[np.ndarray, Dict]:
        """
        Load Digital Elevation Model
        
        Returns:
            Tuple of (elevation_array, metadata_dict)
        """
        with rasterio.open(filepath) as src:
            dem = src.read(1)  # Read first band
            
            metadata = {
                'bounds': src.bounds,
                'crs': src.crs.to_string() if src.crs else None,
                'transform': src.transform,
                'width': src.width,
                'height': src.height,
                'resolution': src.res,
                'nodata': src.nodata
            }
            
            # Clean nodata values
            if metadata['nodata'] is not None:
                dem = np.where(dem == metadata['nodata'], np.nan, dem)
            
            # Remove extreme outliers (likely errors)
            dem = np.where(dem < -100, np.nan, dem)
            dem = np.where(dem > 5000, np.nan, dem)
            
        print(f"  Elevation range: {np.nanmin(dem):.2f}m to {np.nanmax(dem):.2f}m")
        return dem, metadata
    
    def load_ortho(self, filepath: Path, target_shape: Tuple[int, int] = None) -> np.ndarray:
        """
        Load orthophoto (RGB satellite image)
        
        Args:
            filepath: Path to ORTHO .tif file
            target_shape: If provided, resample to match this shape (height, width)
            
        Returns:
            RGB array of shape (height, width, 3)
        """
        with rasterio.open(filepath) as src:
            if target_shape:
                # Resample to match DEM size
                from rasterio.enums import Resampling
                r = src.read(1, out_shape=target_shape, resampling=Resampling.bilinear)
                g = src.read(2, out_shape=target_shape, resampling=Resampling.bilinear)
                b = src.read(3, out_shape=target_shape, resampling=Resampling.bilinear)
            else:
                r = src.read(1)
                g = src.read(2)
                b = src.read(3)
            
            # Normalize to 8-bit if needed
            if r.max() > 255:
                r = (r / r.max() * 255).astype(np.uint8)
                g = (g / g.max() * 255).astype(np.uint8)
                b = (b / b.max() * 255).astype(np.uint8)
            
            rgb = np.stack([r, g, b], axis=-1)
        
        print(f"  Loaded RGB image: {rgb.shape}")
        return rgb
    
    def get_dataset_summary(self) -> str:
        """Generate a summary report of available data"""
        summary = f"\n{'='*60}\n"
        summary += f"[Dataset Summary: {self.zone_name}]\n"
        summary += f"{'='*60}\n\n"
        
        summary += f"DEM Files: {len(self.dem_files)}\n"
        summary += f"ORTHO Files: {len(self.ortho_files)}\n"
        summary += f"[OK] Matched Pairs: {len(self.matched_pairs)}\n\n"
        
        if len(self.matched_pairs) > 0:
            summary += "Available Matched Pairs:\n"
            for dem, ortho in self.matched_pairs[:5]:  # Show first 5
                tile_id = self._extract_tile_id(dem.name)
                summary += f"  * Tile {tile_id}: {dem.name} <-> {ortho.name}\n"
            if len(self.matched_pairs) > 5:
                summary += f"  ... and {len(self.matched_pairs) - 5} more\n"
        else:
            summary += "[WARNING] No matched pairs found!\n"
            summary += "  Make sure DEM and ORTHO files have matching tile IDs.\n"
        
        summary += f"\n{'='*60}\n"
        return summary


def verify_installation():
    """Check if all required libraries are installed"""
    print("\n[Verifying Installation...]\n")
    
    libraries = {
        'rasterio': 'Geospatial raster I/O',
        'numpy': 'Numerical operations',
        'plotly': '3D visualization',
        'folium': 'Web mapping',
        'streamlit': 'Dashboard framework'
    }
    
    all_ok = True
    for lib, desc in libraries.items():
        try:
            __import__(lib)
            print(f"[OK] {lib:15s} - {desc}")
        except ImportError:
            print(f"[X] {lib:15s} - NOT INSTALLED")
            all_ok = False
    
    if all_ok:
        print("\n[SUCCESS] All core libraries installed!")
    else:
        print("\n[WARNING] Some libraries missing. Run: pip install -r requirements.txt")
    
    return all_ok


if __name__ == '__main__':
    # Run verification and data scan
    print("\nAqua Guardians - Data Loader Utility\n")
    
    verify_installation()
    
    # Try to load dataset
    try:
        dataset = LiDARDataset('zone_53H13SE')
        print(dataset.get_dataset_summary())
        
        if len(dataset.matched_pairs) > 0:
            print("\n[Testing data loading...]")
            dem_path, ortho_path = dataset.find_matching_pair()
            
            dem, metadata = dataset.load_dem(dem_path)
            print(f"[OK] DEM loaded: {dem.shape}")
            
            rgb = dataset.load_ortho(ortho_path, target_shape=dem.shape)
            print(f"[OK] ORTHO loaded: {rgb.shape}")
            
            print("\n[SUCCESS] Data loading test successful!")
        else:
            print("\n[WARNING] No matched pairs found. Please download matching data.")
            print("   See DATA_DOWNLOAD_GUIDE.md for instructions.")
    
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if data files are in correct directories")
        print("2. Review DATA_DOWNLOAD_GUIDE.md")
        print("3. Ensure .tif files are not corrupted")
