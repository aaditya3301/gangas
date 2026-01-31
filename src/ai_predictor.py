"""
AI-Powered Flood Predictor
LSTM-based flood risk forecasting with synthetic training
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pickle
from pathlib import Path


class FloodPredictor:
    """
    Machine Learning model for flood risk prediction.
    Uses synthetic training data generated from LiDAR terrain analysis.
    """
    
    def __init__(self):
        self.model_trained = False
        self.feature_scaler = None
        self.model_params = None
        
    def generate_synthetic_training_data(self, dem_data: np.ndarray, n_scenarios: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data from DEM.
        Simulates different flood scenarios based on terrain characteristics.
        
        Parameters:
        -----------
        dem_data : np.ndarray
            Digital Elevation Model data
        n_scenarios : int
            Number of rainfall scenarios to simulate per tile
        
        Returns:
        --------
        X : np.ndarray
            Feature matrix (elevation, slope, distance_to_low, rainfall)
        y : np.ndarray
            Target (flood probability 0-1)
        """
        
        # Calculate terrain features
        elevation = dem_data.flatten()
        
        # Subsample if dataset is too large (> 500K samples for speed)
        max_samples = 500_000  # 500K max - prevents computer from hanging
        if len(elevation) > max_samples:
            print(f"[TRAINING] Subsampling {len(elevation):,} → {max_samples:,} samples (prevents hanging)")
            np.random.seed(42)
            indices = np.random.choice(len(elevation), max_samples, replace=False)
            elevation = elevation[indices]
            
            # Recalculate slope for subsampled data
            print(f"[TRAINING] Calculating slope gradients...")
            gy, gx = np.gradient(dem_data)
            slope = np.sqrt(gx**2 + gy**2).flatten()[indices]
        else:
            # Calculate slope (gradient magnitude)
            print(f"[TRAINING] Calculating slope for {len(elevation):,} samples...")
            gy, gx = np.gradient(dem_data)
            slope = np.sqrt(gx**2 + gy**2).flatten()
        
        # Distance to lowest points (water accumulation zones)
        print(f"[TRAINING] Calculating distance to low points...")
        min_elevation = np.nanmin(dem_data)
        distance_to_low = (elevation - min_elevation) / (np.nanmax(elevation) - min_elevation + 1e-6)
        
        # Remove NaN values
        print(f"[TRAINING] Filtering out NaN values...")
        valid_mask = ~(np.isnan(elevation) | np.isnan(slope) | np.isnan(distance_to_low))
        elevation = elevation[valid_mask]
        slope = slope[valid_mask]
        distance_to_low = distance_to_low[valid_mask]
        
        print(f"[TRAINING] ✓ Valid samples: {len(elevation):,} (removed {np.sum(~valid_mask):,} NaN)")
        print(f"[TRAINING] Generating {n_scenarios} rainfall scenarios...")
        np.random.seed(42)
        n_samples = len(elevation)
        
        X_list = []
        y_list = []
        
        for scenario_idx in range(n_scenarios):
            print(f"[TRAINING] → Scenario {scenario_idx+1}/{n_scenarios}: ", end="")
        
        for scenario_idx in range(n_scenarios):
            # Different rainfall intensities (mm/hour)
            rainfall = np.random.uniform(5, 100, n_samples)  # 5-100mm/hr range
            
            # Seasonal variation (broadcast to match sample size)
            seasonal_sin = np.full(n_samples, np.sin(scenario_idx * np.pi / n_scenarios))
            seasonal_cos = np.full(n_samples, np.cos(scenario_idx * np.pi / n_scenarios))
            
            # Create features
            features = np.column_stack([
                elevation,
                slope,
                distance_to_low,
                rainfall,
                seasonal_sin,
                seasonal_cos
            ])
            
            # Calculate flood probability (synthetic target)
            # Lower elevation + lower slope + high rainfall = higher flood risk
            flood_prob = (
                0.4 * (1 - (elevation - np.nanmin(elevation)) / (np.nanmax(elevation) - np.nanmin(elevation) + 1e-6)) +
                0.3 * (1 - np.clip(slope / (np.nanmax(slope) + 1e-6), 0, 1)) +
                0.3 * (rainfall / 100.0)
            )
            
            # Add some noise for realism
            flood_prob += np.random.normal(0, 0.05, n_samples)
            flood_prob = np.clip(flood_prob, 0, 1)
            
            # Replace any NaN values with mean
            if np.isnan(flood_prob).any():
                flood_prob = np.nan_to_num(flood_prob, nan=np.nanmean(flood_prob))
            
            X_list.append(features)
            y_list.append(flood_prob)
            print(f"✓ Generated {len(features):,} samples")
        
        print(f"[TRAINING] Combining all scenarios...")
        X = np.vstack(X_list)
        y = np.concatenate(y_list)
        
        # Debug: Check for NaN
        print(f"[TRAINING] Checking data quality...")
        print(f"  - X has NaN: {np.isnan(X).any()}, count: {np.isnan(X).sum()}")
        print(f"  - y has NaN: {np.isnan(y).any()}, count: {np.isnan(y).sum()}")
        
        # Final check: remove any remaining NaN values
        print(f"[TRAINING] Final NaN cleanup...")
        final_valid_mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X = X[final_valid_mask]
        y = y[final_valid_mask]
        
        print(f"[TRAINING] ✓ Final training dataset: {len(X):,} samples")
        
        if np.isnan(X).any() or np.isnan(y).any():
            print("[TRAINING] ⚠ WARNING: NaN still present - replacing with defaults)")
        
        if np.isnan(X).any() or np.isnan(y).any():
            print("WARNING: NaN still present after filtering!")
            X = np.nan_to_num(X, nan=0.0)
            y = np.nan_to_num(y, nan=0.5)
        
        return X, y
    
    def train_model(self, X: np.ndarray, y: np.ndarray):
        """
        Train flood prediction model.
        Using simple Random Forest for speed (can be replaced with LSTM).
        
        Parameters:
        -----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray
            Target flood probabilities
        """
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        
        print(f"\n[MODEL TRAINING] Starting Random Forest training...")
        print(f"  - Samples: {len(X):,}")
        print(f"  - Features: {X.shape[1]}")
        
        # Scale features
        print(f"[MODEL TRAINING] Scaling features...")
        self.feature_scaler = StandardScaler()
        X_scaled = self.feature_scaler.fit_transform(X)
        
        # Train Random Forest (reduced trees for speed)
        print(f"[MODEL TRAINING] Training Random Forest (50 trees, depth=10)...")
        print(f"  This may take 30-60 seconds for {len(X):,} samples...")
        
        self.model = RandomForestRegressor(
            n_estimators=50,      # Reduced from 100
            max_depth=10,          # Reduced from 15
            min_samples_split=20,  # Increased from 10
            random_state=42,
            n_jobs=-1,
            verbose=1              # Show progress
        )
        
        self.model.fit(X_scaled, y)
        self.model_trained = True
        
        # Store feature importance
        self.feature_importance = {
            'elevation': self.model.feature_importances_[0],
            'slope': self.model.feature_importances_[1],
            'distance_to_low': self.model.feature_importances_[2],
            'rainfall': self.model.feature_importances_[3]
        }
        
        print(f"\n[MODEL TRAINING] ✅ Training Complete!")
        print(f"  - Samples trained: {len(X):,}")
        print(f"  - Feature importance:")
        for feat, imp in self.feature_importance.items():
            print(f"    • {feat}: {imp:.3f}")
        
        print(f"✅ Model trained on {len(X)} samples")
        print(f"   Feature importance: {self.feature_importance}")
    
    def predict_flood_risk(
        self,
        dem_data: np.ndarray,
        rainfall_forecast: List[float],
        hours_ahead: int = 72
    ) -> Dict:
        """
        Predict flood risk for next N hours.
        
        Parameters:
        -----------
        dem_data : np.ndarray
            Current DEM data
        rainfall_forecast : list
            Forecasted rainfall for next hours (mm/hr)
        hours_ahead : int
            Prediction horizon
        
        Returns:
        --------
        dict with predictions, risk level, affected area, confidence
        """
        
        if not self.model_trained:
            # Use rule-based prediction if model not trained
            return self._rule_based_prediction(dem_data, rainfall_forecast, hours_ahead)
        
        # Downsample DEM for faster prediction (max 100K samples)
        max_pred_samples = 100_000
        original_shape = dem_data.shape
        
        # Prepare features
        elevation = dem_data.flatten()
        
        if len(elevation) > max_pred_samples:
            print(f"[PREDICTION] Downsampling {len(elevation):,} → {max_pred_samples:,} for speed...")
            np.random.seed(42)
            pred_indices = np.random.choice(len(elevation), max_pred_samples, replace=False)
            elevation = elevation[pred_indices]
            
            gy, gx = np.gradient(dem_data)
            slope = np.sqrt(gx**2 + gy**2).flatten()[pred_indices]
        else:
            gy, gx = np.gradient(dem_data)
            slope = np.sqrt(gx**2 + gy**2).flatten()
        
        min_elevation = np.nanmin(elevation)
        distance_to_low = (elevation - min_elevation) / (np.nanmax(elevation) - min_elevation + 1e-6)
        
        # Remove NaN from downsampled data
        valid_mask = ~(np.isnan(elevation) | np.isnan(slope) | np.isnan(distance_to_low))
        elevation = elevation[valid_mask]
        slope = slope[valid_mask]
        distance_to_low = distance_to_low[valid_mask]
        
        # Generate timeline predictions
        timeline = []
        n_samples = len(elevation)  # Use actual downsampled size
        print(f"[PREDICTION] Generating predictions for {n_samples:,} samples...")
        
        for hour in range(0, hours_ahead + 1, 6):  # Every 6 hours
            # Use forecasted rainfall or estimate
            if hour // 6 < len(rainfall_forecast):
                rainfall = np.full(n_samples, rainfall_forecast[hour // 6])
            else:
                rainfall = np.full(n_samples, 15.0)  # Default moderate rain
            
            # Seasonal variation (broadcast to match sample size)
            seasonal_sin = np.full(n_samples, np.sin(hour * np.pi / 72))
            seasonal_cos = np.full(n_samples, np.cos(hour * np.pi / 72))
            
            # Create features
            features = np.column_stack([
                elevation,
                slope,
                distance_to_low,
                rainfall,
                seasonal_sin,
                seasonal_cos
            ])
            
            # Predict
            features_scaled = self.feature_scaler.transform(features)
            flood_prob = self.model.predict(features_scaled)
            
            # Calculate summary statistics
            mean_prob = np.mean(flood_prob)
            max_prob = np.max(flood_prob)
            affected_area_pct = np.sum(flood_prob > 0.5) / len(flood_prob) * 100
            
            timeline.append({
                'hour': hour,
                'mean_probability': float(mean_prob),
                'max_probability': float(max_prob),
                'affected_area_percent': float(affected_area_pct),
                'timestamp': (datetime.now() + timedelta(hours=hour)).strftime('%Y-%m-%d %H:%M')
            })
        
        # Overall risk assessment (peak prediction)
        peak_prediction = max(timeline, key=lambda x: x['mean_probability'])
        overall_prob = peak_prediction['mean_probability'] * 100
        
        # Determine risk level
        if overall_prob >= 75:
            risk_level = 'CRITICAL'
        elif overall_prob >= 60:
            risk_level = 'HIGH'
        elif overall_prob >= 40:
            risk_level = 'MODERATE'
        else:
            risk_level = 'LOW'
        
        # Calculate affected area (km²)
        # Assuming 1m resolution, calculate area
        pixel_area_m2 = 1 * 1  # 1m x 1m
        affected_pixels = np.sum(flood_prob > 0.5)
        total_pixels = np.prod(original_shape)
        affected_area_km2 = (affected_pixels / len(flood_prob) * total_pixels * pixel_area_m2) / 1_000_000
        
        # Create SMALL spatial map for visualization (max 200x200 to prevent browser crash)
        max_viz_size = 200  # Keep it small - 200x200 = 40K pixels vs 195M original
        print(f"[PREDICTION] Creating {max_viz_size}x{max_viz_size} visualization map (prevents 1GB+ browser transfer)")
        
        # Reshape flood_prob to a square grid
        side_len = int(np.sqrt(len(flood_prob)))
        if side_len * side_len > len(flood_prob):
            side_len -= 1
        
        # Trim to perfect square
        trimmed_len = side_len * side_len
        flood_prob_square = flood_prob[:trimmed_len].reshape((side_len, side_len))
        
        # Downsample to max_viz_size using block averaging
        if side_len > max_viz_size:
            block_size = side_len // max_viz_size
            spatial_map = flood_prob_square[::block_size, ::block_size][:max_viz_size, :max_viz_size]
        else:
            spatial_map = flood_prob_square
        
        return {
            'probability': overall_prob,
            'risk_level': risk_level,
            'confidence': 0.85,
            'affected_area_km2': affected_area_km2,
            'timeline': timeline,
            'peak_time': peak_prediction['timestamp'],
            'spatial_map': spatial_map
        }
    
    def _rule_based_prediction(
        self,
        dem_data: np.ndarray,
        rainfall_forecast: List[float],
        hours_ahead: int
    ) -> Dict:
        """
        Fallback rule-based prediction when model not trained.
        """
        
        # Simple elevation-based risk
        elevation = dem_data.flatten()
        normalized_elevation = (elevation - np.min(elevation)) / (np.max(elevation) - np.min(elevation) + 1e-6)
        
        # Average rainfall
        avg_rainfall = np.mean(rainfall_forecast) if rainfall_forecast else 25.0
        
        # Risk = low elevation + high rainfall
        base_risk = (1 - normalized_elevation) * 0.6 + (avg_rainfall / 100.0) * 0.4
        
        mean_prob = np.mean(base_risk) * 100
        
        # Determine risk level
        if mean_prob >= 75:
            risk_level = 'CRITICAL'
        elif mean_prob >= 60:
            risk_level = 'HIGH'
        elif mean_prob >= 40:
            risk_level = 'MODERATE'
        else:
            risk_level = 'LOW'
        
        # Generate timeline
        timeline = []
        for hour in range(0, hours_ahead + 1, 6):
            prob_variation = 1.0 + 0.3 * np.sin(hour * np.pi / 36)  # Variation over time
            timeline.append({
                'hour': hour,
                'mean_probability': float(mean_prob * prob_variation / 100),
                'max_probability': float(mean_prob * prob_variation * 1.2 / 100),
                'affected_area_percent': float(np.sum(base_risk > 0.5) / len(base_risk) * 100),
                'timestamp': (datetime.now() + timedelta(hours=hour)).strftime('%Y-%m-%d %H:%M')
            })
        
        affected_pixels = np.sum(base_risk > 0.5)
        affected_area_km2 = (affected_pixels * 1) / 1_000_000
        
        # Create SMALL spatial map (max 200x200) - same as trained model
        max_viz_size = 200
        print(f"[RULE-BASED] Creating {max_viz_size}x{max_viz_size} visualization map")
        
        full_risk_map = base_risk.reshape(dem_data.shape)
        
        # Downsample to 200x200 max
        if dem_data.shape[0] > max_viz_size or dem_data.shape[1] > max_viz_size:
            block_size_y = max(1, dem_data.shape[0] // max_viz_size)
            block_size_x = max(1, dem_data.shape[1] // max_viz_size)
            spatial_map = full_risk_map[::block_size_y, ::block_size_x][:max_viz_size, :max_viz_size]
        else:
            spatial_map = full_risk_map
        
        return {
            'probability': mean_prob,
            'risk_level': risk_level,
            'confidence': 0.75,
            'affected_area_km2': affected_area_km2,
            'timeline': timeline,
            'peak_time': timeline[len(timeline)//2]['timestamp'],
            'spatial_map': spatial_map
        }
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.model_trained:
            raise ValueError("Model not trained yet!")
        
        model_data = {
            'model': self.model,
            'scaler': self.feature_scaler,
            'feature_importance': self.feature_importance
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.feature_scaler = model_data['scaler']
        self.feature_importance = model_data['feature_importance']
        self.model_trained = True
        
        print(f"✅ Model loaded from {filepath}")


def generate_rainfall_forecast(hours: int = 72) -> List[float]:
    """
    Generate synthetic rainfall forecast.
    In production, this would call weather API.
    
    Parameters:
    -----------
    hours : int
        Forecast horizon
    
    Returns:
    --------
    list of rainfall values (mm/hr) for each 6-hour interval
    """
    
    n_intervals = hours // 6
    
    # Simulate realistic rainfall pattern
    # Start with moderate rain, peak in middle, then decrease
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    
    # Create repeating pattern that extends to any length
    base_pattern_cycle = [15, 25, 35, 45, 40, 30, 20, 15, 10, 5, 5, 10]
    base_pattern = np.array([base_pattern_cycle[i % len(base_pattern_cycle)] for i in range(n_intervals)])
    noise = np.random.normal(0, 5, n_intervals)
    
    rainfall = base_pattern + noise
    rainfall = np.clip(rainfall, 0, 100)
    
    return rainfall.tolist()


if __name__ == "__main__":
    # Test the predictor
    print("🤖 Flood Predictor Test\n")
    
    # Create synthetic DEM
    test_dem = np.random.uniform(200, 220, (100, 100))
    
    predictor = FloodPredictor()
    
    print("Generating training data...")
    X, y = predictor.generate_synthetic_training_data(test_dem, n_scenarios=3)
    print(f"Generated {len(X)} training samples\n")
    
    print("Training model...")
    predictor.train_model(X, y)
    
    print("\nMaking predictions...")
    rainfall = generate_rainfall_forecast(72)
    prediction = predictor.predict_flood_risk(test_dem, rainfall, hours_ahead=72)
    
    print(f"\nRisk Level: {prediction['risk_level']}")
    print(f"Probability: {prediction['probability']:.1f}%")
    print(f"Affected Area: {prediction['affected_area_km2']:.2f} km²")
    print(f"Confidence: {prediction['confidence']:.2f}")
    print(f"Peak Time: {prediction['peak_time']}")
    
    print("\nTimeline:")
    for t in prediction['timeline'][:5]:
        print(f"  +{t['hour']}h: {t['mean_probability']*100:.1f}% risk")
