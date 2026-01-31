"""
Infrastructure Risk Assessment
Identify areas and assets at risk from flooding
"""

import numpy as np
from typing import List, Dict, Tuple
from scipy.ndimage import distance_transform_edt


def calculate_flood_risk_zones(dem: np.ndarray, flood_level: float) -> np.ndarray:
    """
    Calculate flood risk zones based on elevation
    
    Args:
        dem: Digital Elevation Model
        flood_level: Water level in meters
        
    Returns:
        Risk zone array: 0=safe, 1=low, 2=medium, 3=high, 4=critical
    """
    risk_zones = np.zeros_like(dem, dtype=int)
    
    # Calculate margin above flood level
    margin = dem - flood_level
    
    # Classify risk zones
    risk_zones[margin < 0] = 4  # Critical - below flood level
    risk_zones[(margin >= 0) & (margin < 1)] = 3  # High - within 1m
    risk_zones[(margin >= 1) & (margin < 2)] = 2  # Medium - within 2m
    risk_zones[(margin >= 2) & (margin < 3)] = 1  # Low - within 3m
    # margin >= 3 stays 0 (safe)
    
    return risk_zones


def assess_infrastructure_impact(
    risk_zones: np.ndarray,
    infrastructure_points: List[Dict],
    pixel_size_m: float = 1.0
) -> Dict:
    """
    Assess impact on infrastructure based on locations
    
    Args:
        risk_zones: Risk zone array
        infrastructure_points: List of dicts with 'type', 'x', 'y' (pixel coordinates)
        pixel_size_m: Size of each pixel in meters
        
    Returns:
        Impact assessment dictionary
    """
    impact = {
        'total_structures': len(infrastructure_points),
        'critical_risk': 0,
        'high_risk': 0,
        'medium_risk': 0,
        'low_risk': 0,
        'safe': 0,
        'by_type': {}
    }
    
    for point in infrastructure_points:
        x, y = int(point['y']), int(point['x'])  # Note: array indexing is [row, col]
        
        if 0 <= x < risk_zones.shape[0] and 0 <= y < risk_zones.shape[1]:
            risk_level = risk_zones[x, y]
            infra_type = point.get('type', 'unknown')
            
            # Count by risk level
            if risk_level == 4:
                impact['critical_risk'] += 1
                status = 'critical'
            elif risk_level == 3:
                impact['high_risk'] += 1
                status = 'high'
            elif risk_level == 2:
                impact['medium_risk'] += 1
                status = 'medium'
            elif risk_level == 1:
                impact['low_risk'] += 1
                status = 'low'
            else:
                impact['safe'] += 1
                status = 'safe'
            
            # Track by infrastructure type
            if infra_type not in impact['by_type']:
                impact['by_type'][infra_type] = {'total': 0, 'at_risk': 0, 'critical': 0}
            
            impact['by_type'][infra_type]['total'] += 1
            if risk_level >= 2:
                impact['by_type'][infra_type]['at_risk'] += 1
            if risk_level >= 4:
                impact['by_type'][infra_type]['critical'] += 1
    
    return impact


def calculate_evacuation_zones(dem: np.ndarray, flood_level: float, buffer_m: float = 100) -> Dict:
    """
    Calculate safe evacuation zones and routes
    
    Args:
        dem: Digital Elevation Model
        flood_level: Water level in meters
        buffer_m: Safety buffer distance in meters
        
    Returns:
        Dictionary with evacuation zone information
    """
    # Find safe areas (above flood level + buffer)
    safe_mask = dem >= (flood_level + 2.0)
    
    # Calculate distance to nearest safe zone for flooded areas
    flooded_mask = dem < flood_level
    distance_to_safety = distance_transform_edt(~safe_mask)
    
    # Calculate evacuation priority (closer to flood = higher priority)
    evacuation_priority = np.zeros_like(dem)
    evacuation_priority[flooded_mask] = 3  # Immediate evacuation
    
    # Areas within 50m of flooded zone
    near_flood = (distance_to_safety > 0) & (distance_to_safety <= 50) & ~flooded_mask
    evacuation_priority[near_flood] = 2
    
    # Areas 50-100m from flooded zone
    moderate_distance = (distance_to_safety > 50) & (distance_to_safety <= 100) & ~flooded_mask
    evacuation_priority[moderate_distance] = 1
    
    pixel_area_m2 = 1.0  # 1m resolution
    
    return {
        'flooded_area_km2': np.sum(flooded_mask) * pixel_area_m2 / 1e6,
        'safe_area_km2': np.sum(safe_mask) * pixel_area_m2 / 1e6,
        'immediate_evacuation_km2': np.sum(evacuation_priority == 3) * pixel_area_m2 / 1e6,
        'high_priority_km2': np.sum(evacuation_priority == 2) * pixel_area_m2 / 1e6,
        'moderate_priority_km2': np.sum(evacuation_priority == 1) * pixel_area_m2 / 1e6,
        'evacuation_priority': evacuation_priority
    }


def estimate_affected_population(
    risk_zones: np.ndarray,
    population_density_per_km2: float = 500,
    pixel_size_m: float = 1.0
) -> Dict:
    """
    Estimate affected population based on risk zones
    
    Args:
        risk_zones: Risk zone array
        population_density_per_km2: Average population density
        pixel_size_m: Pixel size in meters
        
    Returns:
        Population impact estimates
    """
    pixel_area_km2 = (pixel_size_m ** 2) / 1e6
    people_per_pixel = population_density_per_km2 * pixel_area_km2
    
    return {
        'critical_risk_population': int(np.sum(risk_zones == 4) * people_per_pixel),
        'high_risk_population': int(np.sum(risk_zones == 3) * people_per_pixel),
        'medium_risk_population': int(np.sum(risk_zones == 2) * people_per_pixel),
        'total_affected': int(np.sum(risk_zones >= 2) * people_per_pixel)
    }


def get_risk_zone_colorscale():
    """Return colorscale for risk zone visualization"""
    return [
        [0.0, 'rgb(0, 128, 0)'],      # Safe - Green
        [0.25, 'rgb(173, 255, 47)'],  # Low - Light green
        [0.5, 'rgb(255, 255, 0)'],    # Medium - Yellow
        [0.75, 'rgb(255, 140, 0)'],   # High - Orange
        [1.0, 'rgb(255, 0, 0)']       # Critical - Red
    ]
