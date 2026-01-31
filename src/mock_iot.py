"""
Mock IoT Sensor System
Simulate real-time environmental monitoring data
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random


class MockSensorNetwork:
    """Simulate IoT sensor network for environmental monitoring"""
    
    def __init__(self, num_sensors: int = 5):
        self.num_sensors = num_sensors
        self.sensors = self._initialize_sensors()
        self.baseline_time = datetime.now()
        
    def _initialize_sensors(self) -> List[Dict]:
        """Create mock sensor stations"""
        sensor_locations = [
            ("Ganga Bridge - Upstream", 77.5, 29.1),
            ("Hapur Treatment Plant", 77.52, 29.08),
            ("Agricultural Zone", 77.48, 29.12),
            ("Residential Area", 77.51, 29.09),
            ("Downstream Monitor", 77.54, 29.06)
        ]
        
        sensors = []
        for i, (name, lon, lat) in enumerate(sensor_locations[:self.num_sensors]):
            sensors.append({
                'id': f'SENSOR_{i+1:03d}',
                'name': name,
                'location': {'lon': lon, 'lat': lat},
                'status': 'active',
                'last_update': datetime.now(),
                'battery': 95 - i * 5  # Simulate different battery levels
            })
        
        return sensors
    
    def get_current_readings(self) -> List[Dict]:
        """Generate current sensor readings with realistic variations"""
        readings = []
        current_time = datetime.now()
        
        # Simulate time-based variations (e.g., daily cycles)
        hour = current_time.hour
        time_factor = np.sin((hour - 6) * np.pi / 12)  # Peak at noon
        
        for sensor in self.sensors:
            # Base values with time variations
            ph_base = 7.2 + time_factor * 0.3
            do_base = 7.5 + time_factor * 1.5  # Dissolved Oxygen peaks in afternoon
            temp_base = 22 + time_factor * 5  # Temperature follows sun
            turbidity_base = 15 + random.uniform(-5, 10)
            
            # Add sensor-specific offsets (location differences)
            sensor_idx = int(sensor['id'].split('_')[1]) - 1
            location_offset = sensor_idx * 0.1
            
            reading = {
                'sensor_id': sensor['id'],
                'sensor_name': sensor['name'],
                'timestamp': current_time.isoformat(),
                'measurements': {
                    'water_level_m': round(2.5 + random.uniform(-0.5, 0.5) + location_offset, 2),
                    'ph': round(ph_base + random.uniform(-0.3, 0.3), 2),
                    'dissolved_oxygen_mg_l': round(max(0, do_base + random.uniform(-1, 1)), 2),
                    'temperature_c': round(temp_base + random.uniform(-2, 2), 1),
                    'turbidity_ntu': round(max(0, turbidity_base), 1),
                    'conductivity_us_cm': round(450 + random.uniform(-50, 100), 0),
                    'flow_rate_m3_s': round(15 + random.uniform(-3, 5) + location_offset, 1)
                },
                'alerts': self._check_alerts(sensor_idx, ph_base, do_base, turbidity_base)
            }
            
            readings.append(reading)
        
        return readings
    
    def _check_alerts(self, sensor_idx: int, ph: float, do: float, turbidity: float) -> List[str]:
        """Check if any parameters exceed thresholds"""
        alerts = []
        
        # Water quality thresholds
        if ph < 6.5 or ph > 8.5:
            alerts.append(f"⚠️ pH out of range: {ph:.2f}")
        
        if do < 5.0:
            alerts.append(f"⚠️ Low dissolved oxygen: {do:.2f} mg/L")
        
        if turbidity > 30:
            alerts.append(f"⚠️ High turbidity: {turbidity:.1f} NTU")
        
        # Simulate occasional random alerts
        if random.random() < 0.05:  # 5% chance
            alerts.append("ℹ️ Communication delay detected")
        
        return alerts
    
    def get_historical_data(self, hours: int = 24) -> Dict[str, List[Dict]]:
        """Generate historical data for trending"""
        historical = {sensor['id']: [] for sensor in self.sensors}
        
        current_time = datetime.now()
        for i in range(hours * 6):  # Data every 10 minutes
            timestamp = current_time - timedelta(minutes=i * 10)
            hour = timestamp.hour
            time_factor = np.sin((hour - 6) * np.pi / 12)
            
            for sensor in self.sensors:
                sensor_idx = int(sensor['id'].split('_')[1]) - 1
                
                data_point = {
                    'timestamp': timestamp.isoformat(),
                    'water_level_m': 2.5 + random.uniform(-0.3, 0.3) + sensor_idx * 0.1,
                    'ph': 7.2 + time_factor * 0.3 + random.uniform(-0.2, 0.2),
                    'dissolved_oxygen_mg_l': max(0, 7.5 + time_factor * 1.5 + random.uniform(-0.5, 0.5)),
                    'temperature_c': 22 + time_factor * 5 + random.uniform(-1, 1)
                }
                
                historical[sensor['id']].insert(0, data_point)
        
        return historical
    
    def get_network_health(self) -> Dict:
        """Get overall network status"""
        active_sensors = sum(1 for s in self.sensors if s['status'] == 'active')
        avg_battery = np.mean([s['battery'] for s in self.sensors])
        
        return {
            'total_sensors': len(self.sensors),
            'active_sensors': active_sensors,
            'inactive_sensors': len(self.sensors) - active_sensors,
            'network_uptime_%': (active_sensors / len(self.sensors)) * 100,
            'average_battery_%': avg_battery,
            'last_update': datetime.now().isoformat()
        }


def calculate_water_quality_index(readings: Dict) -> Tuple[float, str]:
    """
    Calculate Water Quality Index (WQI) from sensor readings
    
    Returns:
        Tuple of (wqi_score, quality_category)
    """
    measurements = readings['measurements']
    
    # Normalize parameters (0-100, higher is better)
    ph_score = 100 if 6.5 <= measurements['ph'] <= 8.5 else max(0, 100 - abs(7.0 - measurements['ph']) * 20)
    do_score = min(100, measurements['dissolved_oxygen_mg_l'] / 8.0 * 100)
    turbidity_score = max(0, 100 - measurements['turbidity_ntu'] * 2)
    
    # Weighted average
    wqi = (ph_score * 0.3 + do_score * 0.4 + turbidity_score * 0.3)
    
    if wqi >= 90:
        category = "Excellent"
    elif wqi >= 70:
        category = "Good"
    elif wqi >= 50:
        category = "Fair"
    elif wqi >= 30:
        category = "Poor"
    else:
        category = "Very Poor"
    
    return wqi, category
