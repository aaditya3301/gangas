"""
Ecosystem Health Score Calculator
Combines multiple environmental indicators into unified health metric
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict, List


def calculate_ecosystem_health(
    vegetation_health: float,
    water_quality: float,
    terrain_stability: float,
    biodiversity_index: float
) -> Tuple[int, str, str]:
    """
    Calculate overall ecosystem health score from component metrics.
    
    Parameters:
    -----------
    vegetation_health : float (0-100)
        NDVI-based vegetation health score
    water_quality : float (0-100)
        Water Quality Index from IoT sensors
    terrain_stability : float (0-100)
        Erosion and slope stability score
    biodiversity_index : float (0-100)
        Species diversity and habitat quality
    
    Returns:
    --------
    overall_score : int (0-100)
        Weighted ecosystem health score
    grade : str
        Letter grade (A+ to F)
    status : str
        Health status (Excellent, Good, Moderate, Poor, Critical)
    """
    
    # Weighted importance of each component
    weights = {
        'vegetation': 0.30,  # 30% - Critical for soil stability and oxygen
        'water': 0.35,       # 35% - Most critical for Ganga ecosystem
        'terrain': 0.20,     # 20% - Important for flood prevention
        'biodiversity': 0.15 # 15% - Long-term health indicator
    }
    
    # Calculate weighted score
    overall_score = (
        vegetation_health * weights['vegetation'] +
        water_quality * weights['water'] +
        terrain_stability * weights['terrain'] +
        biodiversity_index * weights['biodiversity']
    )
    
    overall_score = int(round(overall_score))
    
    # Determine grade
    if overall_score >= 95:
        grade = "A+"
        status = "Excellent"
    elif overall_score >= 90:
        grade = "A"
        status = "Excellent"
    elif overall_score >= 85:
        grade = "A-"
        status = "Excellent"
    elif overall_score >= 80:
        grade = "B+"
        status = "Good"
    elif overall_score >= 75:
        grade = "B"
        status = "Good"
    elif overall_score >= 70:
        grade = "B-"
        status = "Good"
    elif overall_score >= 65:
        grade = "C+"
        status = "Moderate"
    elif overall_score >= 60:
        grade = "C"
        status = "Moderate"
    elif overall_score >= 55:
        grade = "C-"
        status = "Moderate"
    elif overall_score >= 50:
        grade = "D+"
        status = "Poor"
    elif overall_score >= 45:
        grade = "D"
        status = "Poor"
    elif overall_score >= 40:
        grade = "D-"
        status = "Poor"
    else:
        grade = "F"
        status = "Critical"
    
    return overall_score, grade, status


def get_health_trend(days: int = 30) -> Dict[str, List]:
    """
    Generate synthetic health trend data for the last N days.
    In production, this would query historical database.
    
    Parameters:
    -----------
    days : int
        Number of days to generate trend for
    
    Returns:
    --------
    dict with 'dates' and 'scores' lists
    """
    
    # Generate dates
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]
    
    # Generate synthetic scores with realistic variation
    # Start from 75, gradually decline to current 67
    base_scores = np.linspace(75, 67, days)
    
    # Add realistic daily variation (±3 points)
    np.random.seed(42)  # For reproducibility
    daily_variation = np.random.normal(0, 2, days)
    
    scores = base_scores + daily_variation
    scores = np.clip(scores, 0, 100)  # Keep in valid range
    
    return {
        'dates': dates,
        'scores': scores.tolist()
    }


def get_component_trends(days: int = 30) -> Dict[str, Dict]:
    """
    Get trends for individual health components.
    
    Returns:
    --------
    dict with trends for each component
    """
    
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]
    
    np.random.seed(42)
    
    # Each component has different trend
    components = {
        'vegetation_health': {
            'base': np.linspace(75, 72, days),  # Slight decline
            'variation': 2.5
        },
        'water_quality': {
            'base': np.linspace(65, 58, days),  # Concerning decline
            'variation': 3.0
        },
        'terrain_stability': {
            'base': np.linspace(82, 81, days),  # Stable
            'variation': 1.5
        },
        'biodiversity_index': {
            'base': np.linspace(68, 65, days),  # Gradual decline
            'variation': 2.0
        }
    }
    
    trends = {}
    for component, params in components.items():
        variation = np.random.normal(0, params['variation'], days)
        scores = params['base'] + variation
        scores = np.clip(scores, 0, 100)
        
        trends[component] = {
            'dates': dates,
            'scores': scores.tolist(),
            'current': scores[-1],
            'change_7d': scores[-1] - scores[-8],
            'change_30d': scores[-1] - scores[0]
        }
    
    return trends


def analyze_health_factors(
    vegetation_health: float,
    water_quality: float,
    terrain_stability: float,
    biodiversity_index: float
) -> Dict[str, str]:
    """
    Analyze which factors are contributing most to health issues.
    
    Returns:
    --------
    dict with insights for each component
    """
    
    insights = {}
    
    # Vegetation
    if vegetation_health >= 80:
        insights['vegetation'] = "✅ Excellent vegetation cover - ecosystem is thriving"
    elif vegetation_health >= 60:
        insights['vegetation'] = "⚠️ Moderate vegetation health - monitor for declining trends"
    else:
        insights['vegetation'] = "🔴 Poor vegetation health - urgent restoration needed"
    
    # Water Quality
    if water_quality >= 80:
        insights['water'] = "✅ Clean water - safe for ecosystem and human use"
    elif water_quality >= 60:
        insights['water'] = "⚠️ Moderate pollution - requires monitoring and intervention"
    else:
        insights['water'] = "🔴 Critical pollution levels - immediate action required"
    
    # Terrain
    if terrain_stability >= 80:
        insights['terrain'] = "✅ Stable riverbanks - low erosion risk"
    elif terrain_stability >= 60:
        insights['terrain'] = "⚠️ Some erosion detected - preventive measures recommended"
    else:
        insights['terrain'] = "🔴 High erosion risk - structural interventions needed"
    
    # Biodiversity
    if biodiversity_index >= 80:
        insights['biodiversity'] = "✅ Rich biodiversity - healthy ecosystem indicators"
    elif biodiversity_index >= 60:
        insights['biodiversity'] = "⚠️ Declining species diversity - habitat restoration suggested"
    else:
        insights['biodiversity'] = "🔴 Low biodiversity - ecosystem under stress"
    
    return insights


def get_health_recommendations(overall_score: int, component_scores: Dict[str, float]) -> List[Dict]:
    """
    Generate actionable recommendations based on health scores.
    
    Returns:
    --------
    list of recommendation dicts with priority, action, and impact
    """
    
    recommendations = []
    
    # Water quality issues (highest priority for Ganga)
    if component_scores['water_quality'] < 70:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Water Quality',
            'action': 'Investigate upstream pollution sources and implement water treatment',
            'impact': 'Could improve overall score by 8-12 points',
            'timeline': '1-3 months'
        })
    
    # Vegetation restoration
    if component_scores['vegetation_health'] < 70:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Vegetation',
            'action': 'Implement riverbank afforestation with native species',
            'impact': 'Could improve overall score by 5-8 points',
            'timeline': '3-6 months'
        })
    
    # Erosion control
    if component_scores['terrain_stability'] < 70:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Erosion Control',
            'action': 'Install bio-engineering structures to stabilize riverbanks',
            'impact': 'Could improve overall score by 4-6 points',
            'timeline': '2-4 months'
        })
    
    # Biodiversity enhancement
    if component_scores['biodiversity_index'] < 70:
        recommendations.append({
            'priority': 'LOW',
            'category': 'Biodiversity',
            'action': 'Create wildlife corridors and protect critical habitats',
            'impact': 'Could improve overall score by 3-5 points',
            'timeline': '6-12 months'
        })
    
    # Overall health critical
    if overall_score < 50:
        recommendations.insert(0, {
            'priority': 'CRITICAL',
            'category': 'Emergency Response',
            'action': 'Declare ecosystem emergency - coordinate multi-agency intervention',
            'impact': 'Prevent further degradation',
            'timeline': 'Immediate'
        })
    
    return recommendations


if __name__ == "__main__":
    # Test the calculator
    print("🌊 Ecosystem Health Calculator Test\n")
    
    test_scores = {
        'vegetation_health': 72,
        'water_quality': 58,
        'terrain_stability': 81,
        'biodiversity_index': 65
    }
    
    overall, grade, status = calculate_ecosystem_health(**test_scores)
    
    print(f"Overall Score: {overall}/100")
    print(f"Grade: {grade}")
    print(f"Status: {status}\n")
    
    insights = analyze_health_factors(**test_scores)
    print("Component Insights:")
    for component, insight in insights.items():
        print(f"  {component}: {insight}")
    
    print("\nRecommendations:")
    recommendations = get_health_recommendations(overall, test_scores)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['priority']}] {rec['action']}")
