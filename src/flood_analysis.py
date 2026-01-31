"""
Flood Analysis Module
Advanced flood inundation modeling and risk assessment
"""

import numpy as np
from typing import Tuple, Dict, List
from pathlib import Path


def calculate_flood_depth(dem: np.ndarray, water_level: float) -> np.ndarray:
    """
    Calculate flood depth at each point given a water surface elevation
    
    Args:
        dem: Digital Elevation Model (terrain heights in meters)
        water_level: Water surface elevation (meters)
    
    Returns:
        Flood depth array (0 = no flooding, >0 = water depth in meters)
    """
    flood_depth = np.maximum(water_level - dem, 0)
    return flood_depth


def create_flood_zones(dem: np.ndarray, water_levels: List[float]) -> Dict[str, np.ndarray]:
    """
    Create multiple flood risk zones
    
    Args:
        dem: Digital Elevation Model
        water_levels: List of water levels to simulate (e.g., [125, 130, 135, 140])
    
    Returns:
        Dictionary mapping zone names to binary masks
    """
    zones = {}
    
    for level in water_levels:
        flood_mask = dem < level
        zones[f"{level}m"] = flood_mask
    
    # Create risk categories
    if len(water_levels) >= 3:
        high = dem < water_levels[0]
        medium = (dem >= water_levels[0]) & (dem < water_levels[1])
        low = (dem >= water_levels[1]) & (dem < water_levels[2])
        
        zones['high_risk'] = high
        zones['medium_risk'] = medium
        zones['low_risk'] = low
    
    return zones


def calculate_flood_statistics(dem: np.ndarray, water_level: float, 
                               resolution: float = 1.0) -> Dict:
    """
    Calculate statistics about flood extent
    
    Args:
        dem: Digital Elevation Model
        water_level: Water surface elevation
        resolution: Pixel resolution in meters (default 1m)
    
    Returns:
        Dictionary with flood statistics
    """
    flood_depth = calculate_flood_depth(dem, water_level)
    flooded_pixels = np.sum(flood_depth > 0)
    
    # Calculate area (assuming 1m resolution)
    pixel_area = resolution ** 2  # square meters
    flooded_area_m2 = flooded_pixels * pixel_area
    flooded_area_km2 = flooded_area_m2 / 1_000_000
    
    stats = {
        'water_level_m': water_level,
        'flooded_pixels': int(flooded_pixels),
        'flooded_area_km2': round(flooded_area_km2, 4),
        'max_depth_m': round(float(np.max(flood_depth)), 2),
        'avg_depth_m': round(float(np.mean(flood_depth[flood_depth > 0])), 2) if flooded_pixels > 0 else 0,
        'percent_flooded': round(100 * flooded_pixels / dem.size, 2)
    }
    
    return stats


def generate_flood_scenarios(dem: np.ndarray, 
                             num_scenarios: int = 10) -> List[Dict]:
    """
    Generate multiple flood scenarios from minimum to maximum elevation
    
    Args:
        dem: Digital Elevation Model
        num_scenarios: Number of water levels to simulate
    
    Returns:
        List of scenario dictionaries with statistics
    """
    min_elev = np.nanmin(dem)
    max_elev = np.nanmax(dem)
    
    # Create evenly spaced water levels
    water_levels = np.linspace(min_elev + 1, max_elev, num_scenarios)
    
    scenarios = []
    for level in water_levels:
        stats = calculate_flood_statistics(dem, level)
        scenarios.append(stats)
    
    return scenarios


def identify_safe_zones(dem: np.ndarray, flood_level: float, 
                        min_area_pixels: int = 100) -> np.ndarray:
    """
    Identify contiguous safe zones above flood level
    
    Args:
        dem: Digital Elevation Model
        flood_level: Water surface elevation
        min_area_pixels: Minimum size for a zone to be considered safe
    
    Returns:
        Labeled array where each safe zone has a unique ID
    """
    from scipy import ndimage
    
    # Find areas above water
    safe_mask = dem >= flood_level
    
    # Label connected components
    labeled_zones, num_zones = ndimage.label(safe_mask)
    
    # Filter small zones
    for zone_id in range(1, num_zones + 1):
        zone_size = np.sum(labeled_zones == zone_id)
        if zone_size < min_area_pixels:
            labeled_zones[labeled_zones == zone_id] = 0
    
    return labeled_zones


def calculate_slope(dem: np.ndarray, resolution: float = 1.0) -> np.ndarray:
    """
    Calculate terrain slope in degrees
    
    Args:
        dem: Digital Elevation Model
        resolution: Pixel size in meters
    
    Returns:
        Slope array in degrees
    """
    # Calculate gradients
    dy, dx = np.gradient(dem, resolution)
    
    # Calculate slope magnitude
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)
    
    return slope_deg


def assess_infrastructure_risk(dem: np.ndarray, 
                               infrastructure_points: List[Tuple[int, int]],
                               flood_level: float) -> List[Dict]:
    """
    Assess flood risk to specific infrastructure locations
    
    Args:
        dem: Digital Elevation Model
        infrastructure_points: List of (row, col) coordinates
        flood_level: Water surface elevation
    
    Returns:
        List of risk assessments for each point
    """
    assessments = []
    
    for idx, (row, col) in enumerate(infrastructure_points):
        if 0 <= row < dem.shape[0] and 0 <= col < dem.shape[1]:
            elevation = dem[row, col]
            depth = max(0, flood_level - elevation)
            
            if depth == 0:
                risk = "Safe"
            elif depth < 0.5:
                risk = "Low"
            elif depth < 2.0:
                risk = "Medium"
            else:
                risk = "High"
            
            assessments.append({
                'id': idx,
                'location': (row, col),
                'elevation_m': round(float(elevation), 2),
                'flood_depth_m': round(depth, 2),
                'risk_level': risk
            })
    
    return assessments


if __name__ == '__main__':
    print("\n🌊 Flood Analysis Module - Test\n")
    
    # Create synthetic test DEM
    test_dem = np.random.uniform(100, 150, (100, 100))
    
    print("Testing flood scenarios...")
    scenarios = generate_flood_scenarios(test_dem, num_scenarios=5)
    
    print("\nFlood Scenarios:")
    print("-" * 60)
    for s in scenarios:
        print(f"Water Level: {s['water_level_m']:.1f}m | "
              f"Flooded Area: {s['flooded_area_km2']:.4f} km² | "
              f"Max Depth: {s['max_depth_m']:.2f}m")
    
    print("\n✅ Module working correctly!")
