"""
Synthetic Data Generator
Creates realistic terrain and RGB data when real LiDAR files are unavailable
"""

import numpy as np
import streamlit as st


def generate_synthetic_dem(zone_name, size=None):
    """
    Generate realistic synthetic DEM for demo when data files are missing
    
    Args:
        zone_name: Zone identifier (e.g., 'zone_53L1NW')
        size: Grid size (default: 1000 for L1NW, 500 for others)
    
    Returns:
        np.ndarray: Synthetic elevation data
    """
    if size is None:
        size = 1000 if "53L1NW" in zone_name else 500
    
    np.random.seed(hash(zone_name) % 2**32)  # Consistent data per zone
    
    x = np.linspace(-5, 5, size)
    y = np.linspace(-5, 5, size)
    X, Y = np.meshgrid(x, y)
    
    # Create valley terrain with river channel
    base_elevation = 100 + 20 * np.sin(X/2) + 15 * np.cos(Y/2)
    river_valley = -30 * np.exp(-((X-0.5)**2 + (Y-0.2)**2) / 2)
    
    # Add hills and ridges
    hills = 25 * np.sin(X * 0.8) * np.cos(Y * 0.6)
    
    # Add realistic noise
    noise = 5 * np.random.randn(size, size)
    
    dem = base_elevation + river_valley + hills + noise
    
    return dem


def generate_synthetic_rgb(dem_shape):
    """
    Generate synthetic RGB ortho image based on elevation
    
    Args:
        dem_shape: Shape of DEM array
    
    Returns:
        np.ndarray: Synthetic RGB image (H, W, 3)
    """
    height, width = dem_shape
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create vegetation-based coloring
    np.random.seed(42)
    
    # Green for vegetation (darker in valleys)
    rgb[:, :, 1] = np.random.randint(80, 180, (height, width))  # Green
    rgb[:, :, 0] = rgb[:, :, 1] // 3  # Red
    rgb[:, :, 2] = rgb[:, :, 1] // 2  # Blue
    
    # Add some brown/tan areas (bare earth)
    bare_mask = np.random.rand(height, width) > 0.7
    rgb[bare_mask, 0] = np.random.randint(150, 200, np.sum(bare_mask))  # Red
    rgb[bare_mask, 1] = np.random.randint(130, 170, np.sum(bare_mask))  # Green
    rgb[bare_mask, 2] = np.random.randint(80, 120, np.sum(bare_mask))   # Blue
    
    return rgb


def generate_synthetic_metadata(zone_name, dem_shape):
    """
    Generate metadata for synthetic data
    
    Args:
        zone_name: Zone identifier
        dem_shape: Shape of DEM array
    
    Returns:
        dict: Metadata dictionary
    """
    area_per_pixel = 1.0  # m²
    total_area = (dem_shape[0] * dem_shape[1] * area_per_pixel) / 1_000_000  # km²
    
    return {
        'zone_name': zone_name,
        'total_tiles': 1,
        'tile_count': 1,
        'total_area': total_area,
        'grid_size': dem_shape,
        'resolution': 1.0,  # meters per pixel
        'data_type': 'synthetic',
        'bounds': {
            'min_x': 0,
            'max_x': dem_shape[1],
            'min_y': 0,
            'max_y': dem_shape[0]
        }
    }


def load_data_with_fallback(zone_name, loader_func):
    """
    Try to load real data, fall back to synthetic if unavailable
    
    Args:
        zone_name: Zone identifier
        loader_func: Function that loads real data (should return (dem, rgb, metadata))
    
    Returns:
        tuple: (dem, rgb, metadata, error_message)
    """
    try:
        dem, rgb, metadata = loader_func(zone_name)
        
        # Check if data is valid
        if dem is None or dem.size == 0:
            raise ValueError("Empty data returned")
        
        return dem, rgb, metadata, None
        
    except Exception as e:
        # Generate synthetic data
        st.warning(f"⚠️ No LiDAR data found for {zone_name}. Using synthetic terrain for demo.")
        
        dem = generate_synthetic_dem(zone_name)
        rgb = generate_synthetic_rgb(dem.shape)
        metadata = generate_synthetic_metadata(zone_name, dem.shape)
        
        st.info(f"ℹ️ Using synthetic {dem.shape[0]}x{dem.shape[1]} terrain model")
        
        return dem, rgb, metadata, None
