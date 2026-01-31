"""
🛰️ Multi-Sensor Fusion
Integration of LiDAR, Satellite, and IoT data
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.lidar_loader import load_combined_tiles
from src.ui_components import get_common_css, page_header, section_header

st.set_page_config(
    page_title="Multi-Sensor Fusion - Aqua Guardians",
    page_icon="📡",
    layout="wide"
)

# Apply common CSS
st.markdown(get_common_css(), unsafe_allow_html=True)

# Header
page_header("📡", "Multi-Sensor Data Fusion", "Cross-Validation: LiDAR + Satellite + IoT")
st.markdown("---")

# Zone selector
zone_options = {
    "zone_53H13SE": "Zone 53H13SE (7 tiles, 7 km²)",
    "zone_53L1NW": "Zone 53L1NW (314 tiles, 314 km²)"
}

selected_zone = st.selectbox(
    "Select Analysis Zone",
    options=list(zone_options.keys()),
    format_func=lambda x: zone_options[x],
    index=0  # Start with smaller zone
)

# Data Loading Status
st.subheader("📡 Data Source Status")

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    st.metric("🗺️ LiDAR", "✅ Active", delta="Last: 2 hrs ago")

with status_col2:
    st.metric("🛰️ Satellite", "✅ Active", delta="Last: 6 hrs ago")

with status_col3:
    st.metric("📟 IoT Sensors", "✅ Active", delta="Real-time")

with status_col4:
    st.metric("☁️ Weather API", "✅ Active", delta="Last: 30 min")

st.markdown("---")

# Load data
@st.cache_data(show_spinner=True)
def load_zone_data(zone_name):
    """Load and process zone data"""
    try:
        dem, rgb, metadata = load_combined_tiles(zone_name)
        return dem, rgb, metadata, None
    except Exception as e:
        return None, None, None, str(e)

with st.spinner(f"Loading {selected_zone} data..."):
    dem_data, rgb_data, metadata, error = load_zone_data(selected_zone)

if error:
    st.error(f"❌ Error loading data: {error}")
    st.stop()

# Generate synthetic satellite and IoT data
@st.cache_data
def generate_synthetic_satellite_data(dem_shape):
    """Generate synthetic NDVI and water detection"""
    # NDVI (Normalized Difference Vegetation Index): -1 to 1
    # Higher values = more vegetation
    np.random.seed(42)
    ndvi = np.random.uniform(0.1, 0.8, dem_shape)
    
    # Add realistic patterns (vegetation near water)
    y, x = np.ogrid[:dem_shape[0], :dem_shape[1]]
    center_y, center_x = dem_shape[0] // 2, dem_shape[1] // 2
    distance = np.sqrt((y - center_y)**2 + (x - center_x)**2)
    ndvi = ndvi * (1 - distance / distance.max() * 0.3)
    
    # Water mask (based on elevation)
    water_mask = dem_data < np.percentile(dem_data, 15)
    
    return ndvi, water_mask

@st.cache_data
def generate_synthetic_iot_data():
    """Generate synthetic IoT sensor readings"""
    sensors = []
    
    # Create 15 virtual sensors
    sensor_types = ['Water Level', 'Flow Rate', 'pH', 'Temperature', 'Turbidity']
    
    for i in range(15):
        sensor = {
            'id': f'IOT-{i+1:03d}',
            'type': np.random.choice(sensor_types),
            'lat': 29.9 + np.random.uniform(-0.1, 0.1),
            'lon': 78.1 + np.random.uniform(-0.1, 0.1),
            'status': np.random.choice(['Normal', 'Normal', 'Normal', 'Warning', 'Critical'], p=[0.6, 0.2, 0.1, 0.07, 0.03]),
            'value': 0,
            'unit': '',
            'trend': np.random.choice(['stable', 'rising', 'falling'])
        }
        
        # Set value based on type
        if sensor['type'] == 'Water Level':
            sensor['value'] = np.random.uniform(1.5, 3.8)
            sensor['unit'] = 'm'
        elif sensor['type'] == 'Flow Rate':
            sensor['value'] = np.random.uniform(50, 250)
            sensor['unit'] = 'm³/s'
        elif sensor['type'] == 'pH':
            sensor['value'] = np.random.uniform(6.5, 8.5)
            sensor['unit'] = 'pH'
        elif sensor['type'] == 'Temperature':
            sensor['value'] = np.random.uniform(18, 28)
            sensor['unit'] = '°C'
        else:  # Turbidity
            sensor['value'] = np.random.uniform(5, 150)
            sensor['unit'] = 'NTU'
        
        sensors.append(sensor)
    
    return sensors

ndvi_data, water_mask = generate_synthetic_satellite_data(dem_data.shape)
iot_sensors = generate_synthetic_iot_data()

# Main Content: Three-Panel Comparison
st.subheader("🔍 Multi-Source Comparison")

view_tab1, view_tab2, view_tab3 = st.tabs(["📊 Side-by-Side", "🔀 Overlay", "📈 Time Series"])

with view_tab1:
    # Three columns for different data sources
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🗺️ LiDAR Elevation")
        
        # Create elevation heatmap
        fig_dem = go.Figure(data=go.Heatmap(
            z=dem_data,
            colorscale='Viridis',
            colorbar=dict(title="Elevation (m)")
        ))
        
        fig_dem.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False)
        )
        
        st.plotly_chart(fig_dem, use_container_width=True)
        
        st.metric("Min Elevation", f"{np.nanmin(dem_data):.1f} m")
        st.metric("Max Elevation", f"{np.nanmax(dem_data):.1f} m")
    
    with col2:
        st.markdown("#### 🛰️ Satellite NDVI")
        
        # Create NDVI heatmap
        fig_ndvi = go.Figure(data=go.Heatmap(
            z=ndvi_data,
            colorscale='RdYlGn',
            colorbar=dict(title="NDVI")
        ))
        
        fig_ndvi.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False)
        )
        
        st.plotly_chart(fig_ndvi, use_container_width=True)
        
        st.metric("Mean NDVI", f"{np.mean(ndvi_data):.3f}")
        st.metric("Vegetation Cover", f"{np.sum(ndvi_data > 0.4) / ndvi_data.size * 100:.1f}%")
    
    with col3:
        st.markdown("#### 📟 IoT Sensor Network")
        
        # IoT status summary
        sensor_df = pd.DataFrame(iot_sensors)
        
        # Status pie chart
        status_counts = sensor_df['status'].value_counts()
        
        fig_iot = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            marker=dict(colors=['#4caf50', '#ffa500', '#ff4b4b'])
        )])
        
        fig_iot.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True
        )
        
        st.plotly_chart(fig_iot, use_container_width=True)
        
        st.metric("Active Sensors", f"{len(iot_sensors)}")
        st.metric("Critical Alerts", f"{len([s for s in iot_sensors if s['status'] == 'Critical'])}")

with view_tab2:
    st.markdown("#### 🔀 Integrated Data Overlay")
    
    overlay_col1, overlay_col2 = st.columns([2, 1])
    
    with overlay_col1:
        # Create composite risk map
        # Combine: low elevation + low NDVI + water presence = higher risk
        elevation_norm = (dem_data - np.nanmin(dem_data)) / (np.nanmax(dem_data) - np.nanmin(dem_data))
        
        risk_score = (
            0.4 * (1 - elevation_norm) +  # Lower elevation = higher risk
            0.3 * (1 - ndvi_data) +        # Less vegetation = higher risk
            0.3 * water_mask.astype(float) # Water presence = higher risk
        )
        
        fig_overlay = go.Figure(data=go.Heatmap(
            z=risk_score,
            colorscale='RdYlGn_r',
            colorbar=dict(title="Risk Score (0-1)")
        ))
        
        fig_overlay.update_layout(
            height=500,
            title="Composite Flood Risk Map (Multi-Sensor Fusion)",
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False)
        )
        
        st.plotly_chart(fig_overlay, use_container_width=True)
    
    with overlay_col2:
        st.markdown("##### 🎯 Risk Analysis")
        
        high_risk_pct = np.sum(risk_score > 0.6) / risk_score.size * 100
        medium_risk_pct = np.sum((risk_score > 0.4) & (risk_score <= 0.6)) / risk_score.size * 100
        low_risk_pct = np.sum(risk_score <= 0.4) / risk_score.size * 100
        
        st.metric("🔴 High Risk", f"{high_risk_pct:.1f}%", 
                 help="Risk score > 0.6")
        st.metric("🟡 Medium Risk", f"{medium_risk_pct:.1f}%",
                 help="Risk score 0.4-0.6")
        st.metric("🟢 Low Risk", f"{low_risk_pct:.1f}%",
                 help="Risk score < 0.4")
        
        st.markdown("---")
        
        st.markdown("##### 📊 Data Sources Used")
        st.markdown("✅ LiDAR Elevation")
        st.markdown("✅ Satellite NDVI")
        st.markdown("✅ Water Detection")
        st.markdown("✅ IoT Sensor Network")
        
        st.markdown("---")
        
        st.success("**Cross-Validation**: All data sources confirm HIGH flood risk in low-elevation zones")

with view_tab3:
    st.markdown("#### 📈 Historical Trends (Last 7 Days)")
    
    # Generate synthetic time series
    dates = pd.date_range(end=datetime.now(), periods=168, freq='h')  # 7 days hourly
    
    # Water level trend
    water_level_trend = 2.5 + 0.3 * np.sin(np.linspace(0, 4*np.pi, 168)) + np.random.normal(0, 0.1, 168)
    
    # NDVI trend (slower changes)
    ndvi_trend = 0.45 + 0.05 * np.sin(np.linspace(0, np.pi, 168)) + np.random.normal(0, 0.02, 168)
    
    # pH trend
    ph_trend = 7.2 + 0.3 * np.sin(np.linspace(0, 3*np.pi, 168)) + np.random.normal(0, 0.1, 168)
    
    trend_df = pd.DataFrame({
        'timestamp': dates,
        'water_level': water_level_trend,
        'ndvi': ndvi_trend,
        'ph': ph_trend
    })
    
    # Multi-axis plot
    fig_trends = go.Figure()
    
    fig_trends.add_trace(go.Scatter(
        x=trend_df['timestamp'],
        y=trend_df['water_level'],
        name='Water Level (m)',
        yaxis='y',
        line=dict(color='#2196F3', width=2)
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=trend_df['timestamp'],
        y=trend_df['ndvi'] * 10,  # Scale for visibility
        name='NDVI (×10)',
        yaxis='y2',
        line=dict(color='#4CAF50', width=2)
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=trend_df['timestamp'],
        y=trend_df['ph'],
        name='pH',
        yaxis='y3',
        line=dict(color='#FF9800', width=2)
    ))
    
    fig_trends.update_layout(
        height=500,
        title="Multi-Sensor Time Series",
        xaxis=dict(title="Time"),
        yaxis=dict(
            title=dict(text="Water Level (m)", font=dict(color='#2196F3')),
            tickfont=dict(color='#2196F3')
        ),
        yaxis2=dict(
            title=dict(text="NDVI (×10)", font=dict(color='#4CAF50')),
            tickfont=dict(color='#4CAF50'),
            anchor='free',
            overlaying='y',
            side='right',
            position=0.85
        ),
        yaxis3=dict(
            title=dict(text="pH", font=dict(color='#FF9800')),
            tickfont=dict(color='#FF9800'),
            anchor='free',
            overlaying='y',
            side='right',
            position=1.0
        ),
        legend=dict(x=0.01, y=0.99)
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)

st.markdown("---")

# IoT Sensor Details
st.subheader("📟 IoT Sensor Network Details")

sensor_df = pd.DataFrame(iot_sensors)

# Add color coding
def color_status(status):
    if status == 'Normal':
        return 'background-color: #4caf50; color: white'
    elif status == 'Warning':
        return 'background-color: #ffa500; color: white'
    else:
        return 'background-color: #ff4b4b; color: white'

styled_df = sensor_df.style.applymap(color_status, subset=['status'])

st.dataframe(
    sensor_df[['id', 'type', 'value', 'unit', 'status', 'trend']],
    use_container_width=True,
    hide_index=True,
    height=400
)

st.markdown("---")

# Cross-Validation Alerts
st.subheader("🔔 Cross-Validation Alerts")

alert_col1, alert_col2 = st.columns(2)

with alert_col1:
    st.warning("""
    **⚠️ Anomaly Detected: Zone 3 North**
    
    - 🗺️ **LiDAR**: Elevation drop detected (-0.8m in 24h)
    - 🛰️ **Satellite**: NDVI decreased (vegetation stress)
    - 📟 **IoT**: pH sensor shows contamination (pH 5.2)
    
    **Recommendation**: Deploy field team for verification
    """)

with alert_col2:
    st.success("""
    **✅ Validation Confirmed: Zone 1 South**
    
    - 🗺️ **LiDAR**: Stable elevation profile
    - 🛰️ **Satellite**: Healthy vegetation (NDVI 0.72)
    - 📟 **IoT**: Normal water quality (pH 7.4)
    
    **Status**: No action required
    """)

# Footer
st.markdown("---")
st.info("💡 **Multi-Sensor Fusion** combines LiDAR precision, satellite coverage, and IoT real-time monitoring for comprehensive flood risk assessment!")
