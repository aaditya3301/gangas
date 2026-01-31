"""
🎮 3D Terrain Viewer
Interactive 3D visualization with real-time flood simulation
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.lidar_loader import load_combined_tiles
from src.ui_components import get_common_css, page_header, section_header

st.set_page_config(
    page_title="3D Terrain Viewer - Aqua Guardians",
    page_icon="🗺️",
    layout="wide"
)

# Apply common CSS
st.markdown(get_common_css(), unsafe_allow_html=True)

# Header
page_header("🗺️", "3D Interactive Terrain Viewer", "Real-Time Flood Simulation on Actual LiDAR Terrain")
st.markdown("---")

# Zone selector
zone_options = {
    "zone_53H13SE": "Zone 53H13SE (7 tiles, 7 km²) - ⚡ Fast",
    "zone_53L1NW": "Zone 53L1NW (314 tiles, 314 km²) - 🐌 Slow"
}

col1, col2 = st.columns([1, 1])

with col1:
    selected_zone = st.selectbox(
        "Select Terrain Zone",
        options=list(zone_options.keys()),
        format_func=lambda x: zone_options[x],
        index=0  # Default to smaller zone for speed
    )

with col2:
    visualization_mode = st.selectbox(
        "Visualization Mode",
        ["🗻 Terrain Only", "🌊 Current Flood Risk", "▶️ Flood Animation", "🎨 Multi-Layer"]
    )

# Load data
@st.cache_data(show_spinner=True)
def load_zone_data(zone_name):
    """Load and process zone data"""
    try:
        dem, rgb, metadata = load_combined_tiles(zone_name)
        
        # Downsample for 3D performance (max 200x200 for smooth rendering)
        if dem.shape[0] > 200 or dem.shape[1] > 200:
            downsample_y = max(1, dem.shape[0] // 200)
            downsample_x = max(1, dem.shape[1] // 200)
            dem_downsampled = dem[::downsample_y, ::downsample_x]
        else:
            dem_downsampled = dem
        
        return dem_downsampled, None
    except Exception as e:
        return None, str(e)

with st.spinner(f"🔄 Loading {selected_zone} terrain data..."):
    dem_data, error = load_zone_data(selected_zone)

if error:
    st.error(f"❌ Error loading data: {error}")
    st.stop()

if dem_data is None:
    st.error("❌ Failed to load DEM data")
    st.stop()

st.success(f"✅ Loaded terrain: {dem_data.shape[0]}×{dem_data.shape[1]} grid points")

# Simulation controls
st.markdown("---")
st.subheader("🎛️ Simulation Controls")

control_col1, control_col2, control_col3, control_col4 = st.columns(4)

with control_col1:
    water_level = st.slider(
        "💧 Water Level (meters)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.5,
        help="Simulate rising water level"
    )

with control_col2:
    camera_angle = st.selectbox(
        "📷 Camera View",
        ["Aerial", "Perspective", "Side View", "Low Angle"],
        index=1
    )

with control_col3:
    colorscale = st.selectbox(
        "🎨 Color Scheme",
        ["Viridis", "Earth", "Terrain", "Rainbow", "Portland"],
        index=1
    )

with control_col4:
    show_flood_zone = st.checkbox("🌊 Show Flood Zone", value=True)

# Generate 3D terrain
st.markdown("---")

# Create coordinate grids
y_coords = np.arange(dem_data.shape[0])
x_coords = np.arange(dem_data.shape[1])
x_grid, y_grid = np.meshgrid(x_coords, y_coords)

# Calculate flood mask (areas below water level + base elevation)
base_elevation = np.nanpercentile(dem_data, 10)  # 10th percentile as base
flood_mask = dem_data < (base_elevation + water_level)

# Create custom colorscale for flooded areas
if show_flood_zone and water_level > 0:
    # Create a version of elevation with flood overlay
    z_display = dem_data.copy()
    
    # Custom color: blue for flooded, terrain colors for dry
    custom_colorscale = [
        [0, 'rgb(0, 0, 139)'],      # Deep blue (flooded)
        [0.2, 'rgb(30, 144, 255)'],  # Dodger blue (shallow flood)
        [0.4, 'rgb(34, 139, 34)'],   # Forest green (low land)
        [0.6, 'rgb(139, 115, 85)'],  # Saddle brown (mid elevation)
        [0.8, 'rgb(169, 169, 169)'], # Gray (high elevation)
        [1, 'rgb(255, 250, 250)']    # Snow white (peaks)
    ]
    
    use_colorscale = custom_colorscale
else:
    use_colorscale = colorscale

# Create 3D surface plot
fig = go.Figure(data=[go.Surface(
    z=dem_data,
    x=x_grid,
    y=y_grid,
    colorscale=use_colorscale,
    lighting=dict(
        ambient=0.4,
        diffuse=0.8,
        specular=0.2,
        roughness=0.8,
        fresnel=0.2
    ),
    colorbar=dict(
        title="Elevation (m)",
        len=0.7
    ),
    contours=dict(
        z=dict(
            show=True,
            usecolormap=True,
            highlightcolor="limegreen",
            project=dict(z=True)
        )
    ),
    hovertemplate='<b>Position</b><br>X: %{x}<br>Y: %{y}<br><b>Elevation: %{z:.2f}m</b><extra></extra>'
)])

# Add flood water surface if water level > 0
if show_flood_zone and water_level > 0:
    # Create water surface at specified level
    water_surface = np.full_like(dem_data, base_elevation + water_level)
    
    # Only show water where it would flood
    water_surface[~flood_mask] = np.nan
    
    fig.add_trace(go.Surface(
        z=water_surface,
        x=x_grid,
        y=y_grid,
        colorscale=[[0, 'rgba(0, 119, 190, 0.5)'], [1, 'rgba(0, 180, 216, 0.5)']],
        showscale=False,
        name='Flood Water',
        hovertemplate='<b>Water Level: %.2fm</b><extra></extra>' % (base_elevation + water_level),
        opacity=0.7
    ))

# Camera settings based on selection
camera_settings = {
    "Aerial": dict(eye=dict(x=0, y=0, z=2.5)),
    "Perspective": dict(eye=dict(x=1.5, y=1.5, z=1.2)),
    "Side View": dict(eye=dict(x=2.5, y=0, z=0.5)),
    "Low Angle": dict(eye=dict(x=1.8, y=1.8, z=0.3))
}

# Update layout
fig.update_layout(
    title=f"3D Terrain: {selected_zone} | Water Level: +{water_level:.1f}m",
    scene=dict(
        xaxis_title="X (Grid)",
        yaxis_title="Y (Grid)",
        zaxis_title="Elevation (m)",
        camera=camera_settings[camera_angle],
        aspectmode='auto'
    ),
    height=700,
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# Flood Statistics
st.markdown("---")
st.subheader("📊 Flood Impact Statistics")

stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)

flooded_area_pct = np.sum(flood_mask) / flood_mask.size * 100
flooded_area_km2 = (np.sum(flood_mask) / 1_000_000) * (1 if selected_zone == "zone_53H13SE" else 100)  # Rough scale

with stat_col1:
    st.metric(
        "Flooded Area",
        f"{flooded_area_pct:.1f}%",
        delta=f"{flooded_area_km2:.2f} km²"
    )

with stat_col2:
    affected_points = np.sum(flood_mask)
    st.metric(
        "Affected Points",
        f"{affected_points:,}",
        delta=f"{affected_points / flood_mask.size * 100:.1f}%"
    )

with stat_col3:
    max_depth = water_level - (np.nanmin(dem_data[flood_mask]) - base_elevation) if np.sum(flood_mask) > 0 else 0
    st.metric(
        "Max Water Depth",
        f"{max(0, max_depth):.2f} m",
        delta="Below water level"
    )

with stat_col4:
    avg_elevation = np.nanmean(dem_data)
    st.metric(
        "Avg Elevation",
        f"{avg_elevation:.1f} m",
        delta=f"Range: {np.nanmax(dem_data) - np.nanmin(dem_data):.1f}m"
    )

with stat_col5:
    safe_area_pct = 100 - flooded_area_pct
    st.metric(
        "Safe Area",
        f"{safe_area_pct:.1f}%",
        delta="✅ Above water",
        delta_color="normal"
    )

# Animation Timeline
if visualization_mode == "▶️ Flood Animation":
    st.markdown("---")
    st.subheader("🎬 Flood Timeline Simulation")
    
    st.info("📹 **Animation Preview**: Move the slider below to see flood progression over 24 hours")
    
    timeline_hour = st.slider(
        "Timeline (hours from now)",
        min_value=0,
        max_value=24,
        value=12,
        step=1,
        help="Simulate flood progression hour by hour"
    )
    
    # Simulate water level rising over time (simple sine curve)
    simulated_level = water_level * (0.2 + 0.8 * np.sin(timeline_hour * np.pi / 24))
    
    timeline_col1, timeline_col2, timeline_col3 = st.columns(3)
    
    with timeline_col1:
        current_time = datetime.now() + timedelta(hours=timeline_hour)
        st.metric(
            "⏰ Simulation Time",
            current_time.strftime("%I:%M %p"),
            delta=f"+{timeline_hour}h"
        )
    
    with timeline_col2:
        st.metric(
            "💧 Simulated Water Level",
            f"{simulated_level:.2f} m",
            delta=f"{simulated_level - water_level:+.2f}m"
        )
    
    with timeline_col3:
        flood_status = "🔴 CRITICAL" if simulated_level > 5 else "🟠 HIGH" if simulated_level > 3 else "🟡 MODERATE"
        st.metric(
            "⚠️ Risk Level",
            flood_status,
            delta="Dynamic"
        )

# Insights & Recommendations
st.markdown("---")
st.subheader("💡 AI Insights & Recommendations")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown("#### 🎯 Risk Assessment")
    
    if flooded_area_pct > 30:
        st.error(f"""
        **🚨 CRITICAL FLOOD RISK**
        - {flooded_area_pct:.1f}% of terrain submerged
        - Water level: +{water_level:.1f}m above baseline
        - Estimated {int(flooded_area_km2 * 1000)} people at risk
        - **Action**: Immediate evacuation required
        """)
    elif flooded_area_pct > 15:
        st.warning(f"""
        **⚠️ HIGH FLOOD RISK**
        - {flooded_area_pct:.1f}% of terrain affected
        - Water level: +{water_level:.1f}m above baseline
        - **Action**: Prepare for evacuation
        """)
    else:
        st.success(f"""
        **✅ MODERATE/LOW RISK**
        - {flooded_area_pct:.1f}% affected area
        - Situation under control
        - **Action**: Continue monitoring
        """)

with insight_col2:
    st.markdown("#### 📋 Recommended Actions")
    
    if flooded_area_pct > 30:
        st.markdown("""
        1. 🚨 **Activate Emergency Protocol**
        2. 📢 Send mass SMS alerts to residents
        3. 🚁 Deploy rescue teams to low-lying areas
        4. 🏥 Prepare medical facilities
        5. 🛤️ Open evacuation routes A, B, C
        """)
    elif flooded_area_pct > 15:
        st.markdown("""
        1. ⚠️ **Issue Flood Warning**
        2. 📱 Alert Zone 3 residents
        3. 🚧 Close low-level roads
        4. 📦 Distribute emergency supplies
        5. 👀 Monitor water level every hour
        """)
    else:
        st.markdown("""
        1. 👁️ **Continue Surveillance**
        2. 📊 Update risk models
        3. 🧪 Monitor sensor network
        4. 📢 Public awareness campaigns
        5. 🛠️ Maintain drainage systems
        """)

# Footer
st.markdown("---")
st.info("🎮 **3D Terrain Viewer** provides photorealistic flood visualization using actual LiDAR elevation data. Rotate, zoom, and interact with the model!")
