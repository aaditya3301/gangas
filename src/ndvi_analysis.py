"""
NDVI (Normalized Difference Vegetation Index) Analysis
Calculate vegetation health from RGB imagery
"""

import numpy as np
from typing import Tuple, Dict

def calculate_ndvi_from_rgb(rgb: np.ndarray) -> np.ndarray:
    """
    Calculate NDVI from RGB image using visible bands approximation
    
    NDVI = (NIR - Red) / (NIR + Red)
    Since we don't have NIR, we approximate: NIR ≈ Green (visible vegetation)
    
    Args:
        rgb: RGB array of shape (height, width, 3)
        
    Returns:
        NDVI array of shape (height, width) with values from -1 to 1
    """
    # Extract channels
    red = rgb[:, :, 0].astype(float)
    green = rgb[:, :, 1].astype(float)
    blue = rgb[:, :, 2].astype(float)
    
    # Approximate NDVI using visible bands
    # For true NDVI we'd need NIR band, but we can use green as proxy
    numerator = green - red
    denominator = green + red + 1e-10  # Avoid division by zero
    
    ndvi = numerator / denominator
    
    # Clip to valid range
    ndvi = np.clip(ndvi, -1, 1)
    
    return ndvi


def classify_vegetation(ndvi: np.ndarray, dem: np.ndarray = None) -> Dict:
    """
    Classify vegetation health and calculate statistics
    
    Args:
        ndvi: NDVI array
        dem: Optional DEM for riparian zone identification
        
    Returns:
        Dictionary with classification statistics
    """
    # Classification thresholds
    water_mask = ndvi < -0.1
    bare_soil = (ndvi >= -0.1) & (ndvi < 0.2)
    sparse_veg = (ndvi >= 0.2) & (ndvi < 0.4)
    moderate_veg = (ndvi >= 0.4) & (ndvi < 0.6)
    dense_veg = ndvi >= 0.6
    
    total_pixels = ndvi.size
    pixel_area_m2 = 1.0  # 1m resolution
    
    stats = {
        'water_area_km2': np.sum(water_mask) * pixel_area_m2 / 1e6,
        'bare_soil_km2': np.sum(bare_soil) * pixel_area_m2 / 1e6,
        'sparse_vegetation_km2': np.sum(sparse_veg) * pixel_area_m2 / 1e6,
        'moderate_vegetation_km2': np.sum(moderate_veg) * pixel_area_m2 / 1e6,
        'dense_vegetation_km2': np.sum(dense_veg) * pixel_area_m2 / 1e6,
        'mean_ndvi': float(np.mean(ndvi)),
        'vegetation_coverage_%': float(np.sum(ndvi > 0.2) / total_pixels * 100)
    }
    
    # Riparian zone analysis if DEM provided
    if dem is not None:
        # Identify low-lying areas near water (potential riparian zones)
        elevation_percentile_10 = np.nanpercentile(dem, 10)
        riparian_zone = (dem <= elevation_percentile_10 + 2) & (ndvi > 0.3)
        stats['riparian_vegetation_km2'] = np.sum(riparian_zone) * pixel_area_m2 / 1e6
    
    return stats


def get_ndvi_colormap():
    """Return custom colorscale for NDVI visualization"""
    return [
        [0.0, 'rgb(139, 69, 19)'],    # Dark brown (bare soil/low)
        [0.25, 'rgb(210, 180, 140)'],  # Tan
        [0.5, 'rgb(255, 255, 153)'],   # Light yellow
        [0.65, 'rgb(173, 255, 47)'],   # Yellow-green
        [0.75, 'rgb(50, 205, 50)'],    # Lime green
        [0.85, 'rgb(34, 139, 34)'],    # Forest green
        [1.0, 'rgb(0, 100, 0)']        # Dark green (dense vegetation)
    ]


def calculate_vegetation_health_score(ndvi: np.ndarray) -> Tuple[float, str]:
    """
    Calculate overall vegetation health score
    
    Returns:
        Tuple of (score, health_status)
    """
    mean_ndvi = np.mean(ndvi)
    veg_coverage = np.sum(ndvi > 0.2) / ndvi.size * 100
    
    # Weighted score (0-100)
    score = ((mean_ndvi + 1) / 2 * 50) + (veg_coverage * 0.5)
    
    if score >= 75:
        status = "Excellent"
    elif score >= 60:
        status = "Good"
    elif score >= 45:
        status = "Fair"
    elif score >= 30:
        status = "Poor"
    else:
        status = "Critical"
    
    return score, status
