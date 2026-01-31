"""
LiDAR Data Loader - Simplified interface
Wrapper around data_loader.py for easier imports
"""

from src.data_loader import LiDARDataset
from typing import Tuple
import numpy as np


def load_combined_tiles(zone_name: str) -> Tuple[np.ndarray, np.ndarray, dict]:
    """
    Load combined LiDAR tiles for a zone.
    
    Parameters:
    -----------
    zone_name : str
        Zone name (e.g., 'zone_53H13SE', 'zone_53L1NW')
    
    Returns:
    --------
    dem : np.ndarray
        Digital Elevation Model
    rgb : np.ndarray  
        RGB orthophoto (or empty if unavailable)
    metadata : dict
        Metadata about the loaded tiles
    """
    
    # For large zones, skip ortho loading for speed
    load_ortho = (zone_name == 'zone_53H13SE')  # Only load ortho for small zone
    
    dataset = LiDARDataset(zone_name=zone_name, load_ortho=load_ortho)
    dem, rgb, metadata = dataset.load_combined_tiles()
    
    return dem, rgb, metadata
