"""
Interactive Streamlit Dashboard
Aqua Guardians - Ganga River Climate Monitoring System
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_loader import LiDARDataset
from flood_analysis import (
    calculate_flood_depth,
    generate_flood_scenarios,
    calculate_flood_statistics,
    calculate_slope
)
from ndvi_analysis import (
    calculate_ndvi_from_rgb,
    classify_vegetation,
    get_ndvi_colormap,
    calculate_vegetation_health_score
)
from infrastructure_risk import (
    calculate_flood_risk_zones,
    assess_infrastructure_impact,
    calculate_evacuation_zones,
    estimate_affected_population,
    get_risk_zone_colorscale
)
from mock_iot import MockSensorNetwork, calculate_water_quality_index

# Page configuration
st.set_page_config(
    page_title="Aqua Guardians - River Monitoring",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🌊 Aqua Guardians - Ganga River Climate Monitoring</p>', unsafe_allow_html=True)
st.markdown("**Riverathon 1.0** | *Climate and Environmental Monitoring*")
st.divider()

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Aqua+Guardians", use_container_width=True)
    
    st.header("⚙️ Configuration")
    
    zone = st.selectbox(
        "Select Zone",
        ["zone_53H13SE", "zone_53L1NW"],
        index=0
    )
    
    # Get available tiles for the selected zone
    @st.cache_data
    def get_available_tiles(zone_name):
        dataset = LiDARDataset(zone_name)
        tiles = []
        for dem, ortho in dataset.matched_pairs:
            tile_id = dataset._extract_tile_id(dem.name)
            tiles.append((tile_id, dem.name))
        return tiles, dataset
    
    available_tiles, dataset_info = get_available_tiles(zone)
    
    if len(available_tiles) > 0:
        # Add "Combined" option at the beginning
        tile_options = [f"🗺️ Combined (All {len(available_tiles)} Tiles)"] + [f"Tile {tid} ({name})" for tid, name in available_tiles]
        selected_tile_idx = st.selectbox(
            f"Select Tile ({len(available_tiles)} available)",
            range(len(tile_options)),
            format_func=lambda x: tile_options[x]
        )
        
        if selected_tile_idx == 0:
            selected_tile_id = "COMBINED"  # Special marker for combined view
        else:
            selected_tile_id = available_tiles[selected_tile_idx - 1][1]  # Get the DEM filename
        
        st.success(f"✓ {len(available_tiles)} tiles loaded")
    else:
        st.error("No matched tiles found!")
        selected_tile_id = None
    
    st.divider()
    
    analysis_type = st.radio(
        "Analysis Type",
        [
            "Data Analytics",
            "Flood Simulation", 
            "3D Animated Flood",
            "Terrain Analysis",
            "3D Visualization",
            "🌿 Vegetation (NDVI)",
            "🏘️ Infrastructure Risk",
            "📡 IoT Sensors"
        ]
    )
    
    st.divider()
    
    st.header("📊 Dataset Info")
    st.info(f"""
    **Coverage**: Hapur District, UP  
    **Resolution**: 1-meter precision  
    **Source**: Survey of India LiDAR
    **Available Tiles**: {len(available_tiles)}
    """)


# Load data
@st.cache_data
def load_dataset(zone_name, dem_filename):
    """Load and cache dataset for specific tile or combined mosaic"""
    # Use DEM-only mode for large zones
    load_ortho = zone_name != 'zone_53L1NW'
    dataset = LiDARDataset(zone_name, load_ortho=load_ortho)
    
    if len(dataset.matched_pairs) == 0:
        return None, None, None
    
    # Check if combined view requested
    if dem_filename == "COMBINED":
        dem, rgb, metadata = dataset.load_combined_tiles()
        return dem, rgb, metadata
    
    # Load specific tile
    dem_path, ortho_path = dataset.find_matching_pair(dem_filename)
    dem, metadata = dataset.load_dem(dem_path)
    
    # Load RGB if available
    if ortho_path and load_ortho:
        rgb = dataset.load_ortho(ortho_path, target_shape=dem.shape)
    else:
        # Create grayscale heightmap as fallback
        rgb = np.zeros((*dem.shape, 3), dtype=np.uint8)
    
    return dem, rgb, metadata


with st.spinner("🔄 Loading LiDAR data..."):
    dem, rgb, metadata = load_dataset(zone, selected_tile_id) if selected_tile_id else (None, None, None)

if dem is None:
    st.error("❌ No data files found! Please download data first (see DATA_DOWNLOAD_GUIDE.md)")
    st.stop()

# Show info about DEM-only mode
if zone == 'zone_53L1NW':
    st.info("ℹ️ **DEM-only mode**: This zone has 288 tiles - RGB imagery disabled to prevent browser overload. Showing elevation data only.")

if selected_tile_id == "COMBINED":
    st.success(f"✅ Combined mosaic loaded ({dem.shape[0]} x {dem.shape[1]} pixels)")
else:
    st.success(f"✅ Data loaded: {selected_tile_id}")

# Main content based on analysis type
if analysis_type == "Data Analytics":
    st.header("📊 LiDAR Data Analytics Dashboard")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Zone Coverage",
            value=f"{dem.shape[0]} × {dem.shape[1]}",
            delta="pixels"
        )
    
    with col2:
        area_km2 = (dem.shape[0] * dem.shape[1]) / 1_000_000  # Assuming 1m resolution
        st.metric(
            label="Area Coverage",
            value=f"{area_km2:.2f} km²",
            delta=f"{len(available_tiles)} tiles"
        )
    
    with col3:
        st.metric(
            label="Elevation Range",
            value=f"{np.nanmax(dem) - np.nanmin(dem):.2f}m",
            delta=f"{np.nanmin(dem):.1f}m min"
        )
    
    with col4:
        valid_pixels = np.sum(~np.isnan(dem))
        coverage_pct = (valid_pixels / dem.size) * 100
        st.metric(
            label="Data Quality",
            value=f"{coverage_pct:.1f}%",
            delta="valid pixels"
        )
    
    st.divider()
    
    # Tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Elevation Stats", "🗺️ Terrain Distribution", "🌍 Geographic Overview", "📊 Comparative Analysis"])
    
    with tab1:
        st.subheader("Elevation Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Elevation histogram
            valid_elevation = dem[~np.isnan(dem)].flatten()
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=valid_elevation,
                nbinsx=50,
                marker_color='#1f77b4',
                name='Elevation Distribution'
            ))
            fig.update_layout(
                title="Elevation Distribution",
                xaxis_title="Elevation (m)",
                yaxis_title="Pixel Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistical summary
            st.write("**Statistical Summary:**")
            stats_df = {
                "Metric": ["Mean", "Median", "Std Dev", "Min", "Max", "Range"],
                "Value (m)": [
                    f"{np.nanmean(valid_elevation):.2f}",
                    f"{np.nanmedian(valid_elevation):.2f}",
                    f"{np.nanstd(valid_elevation):.2f}",
                    f"{np.nanmin(valid_elevation):.2f}",
                    f"{np.nanmax(valid_elevation):.2f}",
                    f"{np.nanmax(valid_elevation) - np.nanmin(valid_elevation):.2f}"
                ]
            }
            st.dataframe(stats_df, hide_index=True, use_container_width=True)
        
        with col2:
            # Box plot
            fig = go.Figure()
            fig.add_trace(go.Box(
                y=valid_elevation,
                name='Elevation',
                marker_color='#2ca02c',
                boxmean='sd'
            ))
            fig.update_layout(
                title="Elevation Box Plot",
                yaxis_title="Elevation (m)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Percentiles
            st.write("**Elevation Percentiles:**")
            percentiles = [10, 25, 50, 75, 90, 95, 99]
            perc_values = np.nanpercentile(valid_elevation, percentiles)
            perc_df = {
                "Percentile": [f"{p}th" for p in percentiles],
                "Elevation (m)": [f"{v:.2f}" for v in perc_values]
            }
            st.dataframe(perc_df, hide_index=True, use_container_width=True)
    
    with tab2:
        st.subheader("Terrain Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate slope
            slope = calculate_slope(dem)
            valid_slope = slope[~np.isnan(slope)].flatten()
            
            # Slope histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=valid_slope,
                nbinsx=50,
                marker_color='#ff7f0e',
                name='Slope Distribution'
            ))
            fig.update_layout(
                title="Terrain Slope Distribution",
                xaxis_title="Slope (degrees)",
                yaxis_title="Pixel Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Slope categories
            flat = np.sum(valid_slope < 2)
            gentle = np.sum((valid_slope >= 2) & (valid_slope < 5))
            moderate = np.sum((valid_slope >= 5) & (valid_slope < 15))
            steep = np.sum(valid_slope >= 15)
            
            st.write("**Terrain Classification:**")
            terrain_df = {
                "Category": ["Flat (< 2°)", "Gentle (2-5°)", "Moderate (5-15°)", "Steep (> 15°)"],
                "Pixels": [flat, gentle, moderate, steep],
                "Percentage": [f"{(flat/len(valid_slope)*100):.1f}%",
                              f"{(gentle/len(valid_slope)*100):.1f}%",
                              f"{(moderate/len(valid_slope)*100):.1f}%",
                              f"{(steep/len(valid_slope)*100):.1f}%"]
            }
            st.dataframe(terrain_df, hide_index=True, use_container_width=True)
        
        with col2:
            # Elevation zones pie chart
            low = np.sum(valid_elevation < np.nanpercentile(valid_elevation, 33))
            mid = np.sum((valid_elevation >= np.nanpercentile(valid_elevation, 33)) & 
                        (valid_elevation < np.nanpercentile(valid_elevation, 67)))
            high = np.sum(valid_elevation >= np.nanpercentile(valid_elevation, 67))
            
            fig = go.Figure()
            fig.add_trace(go.Pie(
                labels=['Low Elevation', 'Medium Elevation', 'High Elevation'],
                values=[low, mid, high],
                marker_colors=['#3498db', '#2ecc71', '#e74c3c'],
                hole=0.4
            ))
            fig.update_layout(
                title="Elevation Zones Distribution",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Aspect analysis (if we have enough variation)
            if dem.shape[0] > 3 and dem.shape[1] > 3:
                # Simple aspect calculation using gradients
                gy, gx = np.gradient(dem)
                aspect = np.arctan2(-gx, gy) * 180 / np.pi
                aspect = (aspect + 360) % 360
                
                # Categorize aspects
                aspect_flat = aspect[~np.isnan(aspect)].flatten()
                north = np.sum((aspect_flat >= 337.5) | (aspect_flat < 22.5))
                east = np.sum((aspect_flat >= 67.5) & (aspect_flat < 112.5))
                south = np.sum((aspect_flat >= 157.5) & (aspect_flat < 202.5))
                west = np.sum((aspect_flat >= 247.5) & (aspect_flat < 292.5))
                
                st.write("**Aspect Distribution:**")
                aspect_df = {
                    "Direction": ["North", "East", "South", "West"],
                    "Percentage": [f"{(north/len(aspect_flat)*100):.1f}%",
                                  f"{(east/len(aspect_flat)*100):.1f}%",
                                  f"{(south/len(aspect_flat)*100):.1f}%",
                                  f"{(west/len(aspect_flat)*100):.1f}%"]
                }
                st.dataframe(aspect_df, hide_index=True, use_container_width=True)
    
    with tab3:
        st.subheader("Geographic Overview")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create 2D elevation map with colorscale
            downsample = max(1, dem.shape[0] // 500)
            dem_display = dem[::downsample, ::downsample]
            
            fig = go.Figure()
            fig.add_trace(go.Heatmap(
                z=dem_display,
                colorscale='earth',
                colorbar=dict(title="Elevation (m)"),
            ))
            fig.update_layout(
                title="Elevation Heatmap",
                xaxis_title="X (pixels)",
                yaxis_title="Y (pixels)",
                height=500,
                yaxis=dict(scaleanchor="x", scaleratio=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # RGB preview
            st.write("**RGB Orthophoto Preview**")
            rgb_display = rgb[::downsample, ::downsample]
            st.image(rgb_display, caption="Satellite Imagery", use_container_width=True)
            
            # Data quality metrics
            st.write("**Data Quality Metrics:**")
            quality_metrics = {
                "Metric": ["Valid Pixels", "Missing Data", "Elevation Range", "Tile Count"],
                "Value": [
                    f"{valid_pixels:,}",
                    f"{np.sum(np.isnan(dem)):,}",
                    f"{np.nanmax(dem) - np.nanmin(dem):.2f}m",
                    f"{len(available_tiles)}"
                ]
            }
            st.dataframe(quality_metrics, hide_index=True, use_container_width=True)
    
    with tab4:
        st.subheader("Comparative Analysis")
        
        if selected_tile_id == "COMBINED":
            st.info("📊 Showing combined data from all tiles. Select individual tiles to compare them.")
            
            # Show tile-by-tile statistics
            st.write("**Per-Tile Statistics:**")
            
            tile_stats = []
            for idx, (dem_path, ortho_path) in enumerate(dataset_info.matched_pairs[:20]):  # Show first 20
                tile_id = dataset_info._extract_tile_id(dem_path.name)
                tile_dem, _ = dataset_info.load_dem(dem_path)
                
                tile_stats.append({
                    "Tile ID": tile_id,
                    "Min Elev (m)": f"{np.nanmin(tile_dem):.2f}",
                    "Max Elev (m)": f"{np.nanmax(tile_dem):.2f}",
                    "Mean Elev (m)": f"{np.nanmean(tile_dem):.2f}",
                    "Std Dev (m)": f"{np.nanstd(tile_dem):.2f}"
                })
            
            st.dataframe(tile_stats, hide_index=True, use_container_width=True)
            if len(dataset_info.matched_pairs) > 20:
                st.caption(f"Showing first 20 of {len(dataset_info.matched_pairs)} tiles")
        
        else:
            st.info("Select 'Combined (All Tiles)' view to see comparative statistics across all tiles.")
            
            # Show current tile details
            st.write("**Current Tile Analysis:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Elevation Profile (Center Line):**")
                center_row = dem[dem.shape[0]//2, :]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=center_row,
                    mode='lines',
                    line=dict(color='#1f77b4', width=2),
                    name='Elevation'
                ))
                fig.update_layout(
                    xaxis_title="Position (pixels)",
                    yaxis_title="Elevation (m)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Elevation Contour Map:**")
                downsample_contour = max(1, dem.shape[0] // 200)
                dem_contour = dem[::downsample_contour, ::downsample_contour]
                
                fig = go.Figure()
                fig.add_trace(go.Contour(
                    z=dem_contour,
                    colorscale='earth',
                    contours=dict(
                        coloring='heatmap',
                        showlabels=True
                    ),
                    colorbar=dict(title="Elevation (m)")
                ))
                fig.update_layout(
                    height=300,
                    yaxis=dict(scaleanchor="x", scaleratio=1)
                )
                st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "Flood Simulation":
    st.header("🌊 Flood Inundation Simulation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Water level slider
        min_elev = float(np.nanmin(dem))
        max_elev = float(np.nanmax(dem))
        
        water_level = st.slider(
            "Water Surface Elevation (meters)",
            min_value=min_elev,
            max_value=max_elev,
            value=min_elev + (max_elev - min_elev) * 0.3,
            step=0.1,
            help="Adjust the water level to simulate flooding"
        )
        
        # Calculate flood
        flood_depth = calculate_flood_depth(dem, water_level)
        stats = calculate_flood_statistics(dem, water_level)
        
        # Create visualization
        fig = go.Figure()
        
        # Add terrain
        fig.add_trace(go.Heatmap(
            z=dem,
            colorscale='Earth',
            name='Elevation',
            hovertemplate='Elevation: %{z:.2f}m<extra></extra>',
            showscale=True,
            colorbar=dict(title="Elevation (m)", x=1.15)
        ))
        
        # Add flood overlay
        flood_mask = np.where(flood_depth > 0, flood_depth, np.nan)
        fig.add_trace(go.Heatmap(
            z=flood_mask,
            colorscale=[[0, 'rgba(0,0,255,0)'], [1, 'rgba(0,0,255,0.7)']],
            name='Flood Depth',
            hovertemplate='Flood Depth: %{z:.2f}m<extra></extra>',
            showscale=True,
            colorbar=dict(title="Flood Depth (m)", x=1.3)
        ))
        
        fig.update_layout(
            title=f"Flood Inundation Map @ {water_level:.2f}m",
            xaxis_title="Distance (m)",
            yaxis_title="Distance (m)",
            height=600,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Flood Statistics")
        
        st.metric("Water Level", f"{stats['water_level_m']:.2f} m")
        st.metric("Flooded Area", f"{stats['flooded_area_km2']:.4f} km²")
        st.metric("Max Flood Depth", f"{stats['max_depth_m']:.2f} m")
        st.metric("Avg Flood Depth", f"{stats['avg_depth_m']:.2f} m")
        st.metric("% Area Flooded", f"{stats['percent_flooded']:.2f}%")
        
        st.divider()
        
        st.subheader("⚠️ Risk Assessment")
        
        if stats['percent_flooded'] > 50:
            st.error("🔴 **CRITICAL RISK**")
            st.write("Immediate evacuation recommended")
        elif stats['percent_flooded'] > 25:
            st.warning("🟡 **HIGH RISK**")
            st.write("Prepare emergency measures")
        elif stats['percent_flooded'] > 10:
            st.info("🟢 **MODERATE RISK**")
            st.write("Monitor conditions closely")
        else:
            st.success("✅ **LOW RISK**")
            st.write("Normal monitoring")
    
    # Scenario analysis
    st.divider()
    st.subheader("📊 Multi-Scenario Analysis")
    
    scenarios = generate_flood_scenarios(dem, num_scenarios=10)
    
    # Create scenario chart
    fig_scenarios = go.Figure()
    
    fig_scenarios.add_trace(go.Scatter(
        x=[s['water_level_m'] for s in scenarios],
        y=[s['flooded_area_km2'] for s in scenarios],
        mode='lines+markers',
        name='Flooded Area',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig_scenarios.update_layout(
        title="Flood Extent vs Water Level",
        xaxis_title="Water Level (m)",
        yaxis_title="Flooded Area (km²)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_scenarios, use_container_width=True)

elif analysis_type == "Terrain Analysis":
    st.header("🏔️ Terrain Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Elevation Distribution")
        
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=dem.flatten(),
            nbinsx=50,
            marker_color='#2ca02c'
        ))
        fig_hist.update_layout(
            xaxis_title="Elevation (m)",
            yaxis_title="Frequency",
            height=400
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("Slope Analysis")
        
        slope = calculate_slope(dem)
        
        fig_slope = go.Figure()
        fig_slope.add_trace(go.Heatmap(
            z=slope,
            colorscale='YlOrRd',
            colorbar=dict(title="Slope (°)")
        ))
        fig_slope.update_layout(
            title="Terrain Slope Map",
            height=400
        )
        st.plotly_chart(fig_slope, use_container_width=True)
    
    # Statistics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Min Elevation", f"{np.nanmin(dem):.2f} m")
    with col2:
        st.metric("Max Elevation", f"{np.nanmax(dem):.2f} m")
    with col3:
        st.metric("Elevation Range", f"{np.nanmax(dem) - np.nanmin(dem):.2f} m")
    with col4:
        st.metric("Avg Slope", f"{np.nanmean(slope):.2f}°")

elif analysis_type == "3D Animated Flood":
    st.header("🌊 3D Animated Flood Simulation")
    
    st.info("💡 **Interactive Controls**: Drag slider to change water level | Click 'Play Flood' to animate | Rotate view by dragging")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("⚙️ Settings")
        downsample = st.slider("Downsample Factor", 5, 20, 8, 
                              help="Higher = faster performance")
        num_levels = st.slider("Animation Steps", 10, 30, 20,
                              help="Number of water level frames")
        
        st.divider()
        st.subheader("📊 Info")
        st.metric("Min Elevation", f"{np.nanmin(dem):.2f} m")
        st.metric("Max Elevation", f"{np.nanmax(dem):.2f} m")
    
    with col1:
        # Downsample data
        dem_ds = dem[::downsample, ::downsample]
        rgb_ds = rgb[::downsample, ::downsample]
        
        # Create RGB color matrix
        with st.spinner("🎨 Applying satellite texture..."):
            color_surface = np.zeros(dem_ds.shape, dtype=object)
            for i in range(dem_ds.shape[0]):
                for j in range(dem_ds.shape[1]):
                    color_surface[i, j] = f'rgb({rgb_ds[i,j,0]},{rgb_ds[i,j,1]},{rgb_ds[i,j,2]})'
        
        # Calculate water levels
        min_elev = np.nanmin(dem_ds)
        max_elev = np.nanmax(dem_ds)
        water_levels = np.linspace(min_elev + 0.3, max_elev - 0.3, num_levels)
        
        # Create base figure
        fig_3d_flood = go.Figure()
        
        # Add terrain surface
        fig_3d_flood.add_trace(go.Surface(
            z=dem_ds,
            surfacecolor=color_surface,
            name='Terrain',
            showscale=False,
            hovertemplate='<b>Elevation</b>: %{z:.2f}m<extra></extra>',
            lighting=dict(
                ambient=0.6,
                diffuse=0.5,
                fresnel=0.2,
                specular=0.05,
                roughness=0.1
            )
        ))
        
        # Add water surface
        water_plane = np.full_like(dem_ds, water_levels[0])
        fig_3d_flood.add_trace(go.Surface(
            z=water_plane,
            colorscale=[[0, 'rgba(30,144,255,0.7)'], [1, 'rgba(0,0,139,0.8)']],
            name='Flood Water',
            showscale=False,
            hovertemplate='<b>Water Level</b>: %{z:.2f}m<extra></extra>',
            opacity=0.7,
            cmin=0,
            cmax=1
        ))
        
        # Create animation frames
        frames = []
        for idx, level in enumerate(water_levels):
            flood_depth = calculate_flood_depth(dem_ds, level)
            flooded_pixels = np.sum(flood_depth > 0)
            flooded_pct = (flooded_pixels / dem_ds.size) * 100
            
            water_surface = np.full_like(dem_ds, level)
            
            frames.append(go.Frame(
                data=[
                    go.Surface(z=dem_ds, surfacecolor=color_surface),
                    go.Surface(
                        z=water_surface,
                        colorscale=[[0, 'rgba(30,144,255,0.7)'], [1, 'rgba(0,0,139,0.8)']],
                        opacity=0.7,
                        cmin=0,
                        cmax=1
                    )
                ],
                name=f'{level:.2f}',
                layout=go.Layout(
                    title_text=f'Water Level: {level:.2f}m | Flooded: {flooded_pct:.1f}%'
                )
            ))
        
        fig_3d_flood.frames = frames
        
        # Configure layout
        fig_3d_flood.update_layout(
            title={
                'text': '🌊 3D Flood Animation<br><sub>Drag slider or click Play to animate</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            scene=dict(
                zaxis=dict(
                    range=[min_elev - 0.5, max_elev + 0.5],
                    title='Elevation (m)',
                    gridcolor='white',
                    backgroundcolor='rgb(230, 230, 230)'
                ),
                xaxis=dict(title='Distance (m)', gridcolor='white'),
                yaxis=dict(title='Distance (m)', gridcolor='white'),
                aspectmode='manual',
                aspectratio=dict(x=2, y=2, z=0.6),
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.2),
                    center=dict(x=0, y=0, z=-0.1)
                ),
                bgcolor='rgb(240, 248, 255)'
            ),
            height=700,
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶️ Play Flood',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 500, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 300}
                        }]
                    },
                    {
                        'label': '⏸️ Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ],
                'x': 0.1,
                'y': 1.15,
                'xanchor': 'left',
                'yanchor': 'top'
            }],
            sliders=[{
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 16, 'color': '#1f77b4'},
                    'prefix': '💧 Water Level: ',
                    'suffix': ' m',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                'pad': {'b': 10, 't': 50},
                'len': 0.8,
                'x': 0.1,
                'y': 0,
                'steps': [
                    {
                        'args': [
                            [f.name],
                            {'frame': {'duration': 300, 'redraw': True},
                             'mode': 'immediate',
                             'transition': {'duration': 300}}
                        ],
                        'label': f'{float(f.name):.1f}',
                        'method': 'animate'
                    }
                    for f in frames
                ]
            }]
        )
        
        st.plotly_chart(fig_3d_flood, use_container_width=True)
    
    # Show sample statistics for current middle water level
    st.divider()
    st.subheader("📊 Flood Impact Preview")
    
    mid_level = water_levels[len(water_levels)//2]
    mid_stats = calculate_flood_statistics(dem, mid_level)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sample Water Level", f"{mid_stats['water_level_m']:.2f} m")
    with col2:
        st.metric("Flooded Area", f"{mid_stats['flooded_area_km2']:.4f} km²")
    with col3:
        st.metric("Max Flood Depth", f"{mid_stats['max_depth_m']:.2f} m")
    with col4:
        st.metric("% Area Flooded", f"{mid_stats['percent_flooded']:.1f}%")

elif analysis_type == "3D Visualization":
    st.header("🎨 3D Terrain Visualization")
    
    # Downsample for performance
    downsample = st.slider("Downsample Factor", 1, 20, 10, 
                          help="Higher = faster but less detail")
    
    dem_ds = dem[::downsample, ::downsample]
    rgb_ds = rgb[::downsample, ::downsample]
    
    # Create RGB color array for surface
    color_surface = np.zeros(dem_ds.shape, dtype=object)
    for i in range(dem_ds.shape[0]):
        for j in range(dem_ds.shape[1]):
            color_surface[i, j] = f'rgb({rgb_ds[i,j,0]},{rgb_ds[i,j,1]},{rgb_ds[i,j,2]})'
    
    fig_3d = go.Figure(data=[
        go.Surface(
            z=dem_ds,
            surfacecolor=color_surface,
            showscale=False,
            hovertemplate='Elevation: %{z:.2f}m<extra></extra>'
        )
    ])
    
    fig_3d.update_layout(
        title="3D Terrain Model with Satellite Imagery",
        scene=dict(
            zaxis_title='Elevation (m)',
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            aspectmode='manual',
            aspectratio=dict(x=2, y=2, z=0.5),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        height=700
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.info("💡 **Tip**: Click and drag to rotate. Scroll to zoom.")

elif analysis_type == "🌿 Vegetation (NDVI)":
    st.header("🌿 Vegetation Health Analysis (NDVI)")
    
    if zone == 'zone_53L1NW':
        st.warning("⚠️ NDVI analysis requires RGB imagery. Please select zone_53H13SE for vegetation analysis.")
    elif np.all(rgb == 0):
        st.warning("⚠️ No RGB imagery available for this tile.")
    else:
        # Calculate NDVI
        with st.spinner("Calculating NDVI..."):
            ndvi = calculate_ndvi_from_rgb(rgb)
            veg_stats = classify_vegetation(ndvi, dem)
            health_score, health_status = calculate_vegetation_health_score(ndvi)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Vegetation Health", health_status, f"{health_score:.1f}/100")
        with col2:
            st.metric("Coverage", f"{veg_stats['vegetation_coverage_%']:.1f}%")
        with col3:
            st.metric("Mean NDVI", f"{veg_stats['mean_ndvi']:.3f}")
        with col4:
            if 'riparian_vegetation_km2' in veg_stats:
                st.metric("Riparian Zones", f"{veg_stats['riparian_vegetation_km2']:.3f} km²")
        
        # NDVI Visualization
        tab1, tab2, tab3 = st.tabs(["NDVI Map", "Classification", "Statistics"])
        
        with tab1:
            # Downsample for display
            downsample = max(1, dem.shape[0] // 500)
            ndvi_ds = ndvi[::downsample, ::downsample]
            
            fig = go.Figure()
            fig.add_trace(go.Heatmap(
                z=ndvi_ds,
                colorscale=get_ndvi_colormap(),
                colorbar=dict(title="NDVI", tickvals=[-1, -0.5, 0, 0.5, 1]),
                zmin=-1,
                zmax=1
            ))
            fig.update_layout(
                title="NDVI (Normalized Difference Vegetation Index)",
                xaxis_title="X", yaxis_title="Y",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Classification map
            classification = np.zeros_like(ndvi, dtype=int)
            classification[ndvi < -0.1] = 0  # Water
            classification[(ndvi >= -0.1) & (ndvi < 0.2)] = 1  # Bare soil
            classification[(ndvi >= 0.2) & (ndvi < 0.4)] = 2  # Sparse veg
            classification[(ndvi >= 0.4) & (ndvi < 0.6)] = 3  # Moderate veg
            classification[ndvi >= 0.6] = 4  # Dense veg
            
            class_ds = classification[::downsample, ::downsample]
            
            fig = go.Figure()
            fig.add_trace(go.Heatmap(
                z=class_ds,
                colorscale=[
                    [0, 'blue'], [0.2, 'blue'],
                    [0.2, 'brown'], [0.4, 'brown'],
                    [0.4, 'yellow'], [0.6, 'yellow'],
                    [0.6, 'lightgreen'], [0.8, 'lightgreen'],
                    [0.8, 'darkgreen'], [1.0, 'darkgreen']
                ],
                colorbar=dict(
                    title="Class",
                    tickvals=[0, 1, 2, 3, 4],
                    ticktext=["Water", "Bare Soil", "Sparse Veg", "Moderate Veg", "Dense Veg"]
                )
            ))
            fig.update_layout(
                title="Vegetation Classification",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Statistics table
            st.subheader("Land Cover Statistics")
            stats_df = {
                "Category": ["Water", "Bare Soil", "Sparse Vegetation", "Moderate Vegetation", "Dense Vegetation"],
                "Area (km²)": [
                    veg_stats['water_area_km2'],
                    veg_stats['bare_soil_km2'],
                    veg_stats['sparse_vegetation_km2'],
                    veg_stats['moderate_vegetation_km2'],
                    veg_stats['dense_vegetation_km2']
                ]
            }
            st.dataframe(stats_df, use_container_width=True)
            
            # Bar chart
            fig = go.Figure(data=[
                go.Bar(x=stats_df["Category"], y=stats_df["Area (km²)"],
                      marker_color=['blue', 'brown', 'yellow', 'lightgreen', 'darkgreen'])
            ])
            fig.update_layout(title="Land Cover Distribution", yaxis_title="Area (km²)", height=400)
            st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "🏘️ Infrastructure Risk":
    st.header("🏘️ Infrastructure Risk Assessment")
    
    # Flood level slider
    flood_level = st.slider(
        "Flood Water Level (m)",
        float(np.nanmin(dem)),
        float(np.nanmax(dem)),
        float(np.nanpercentile(dem, 75)),
        0.5,
        help="Set the flood water level to assess impact"
    )
    
    # Calculate risk zones
    with st.spinner("Calculating risk zones..."):
        risk_zones = calculate_flood_risk_zones(dem, flood_level)
        evacuation_info = calculate_evacuation_zones(dem, flood_level)
        pop_impact = estimate_affected_population(risk_zones)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Flooded Area", f"{evacuation_info['flooded_area_km2']:.3f} km²")
    with col2:
        st.metric("Affected Population", f"{pop_impact['total_affected']:,}")
    with col3:
        st.metric("Critical Risk", f"{pop_impact['critical_risk_population']:,}")
    with col4:
        st.metric("Safe Area", f"{evacuation_info['safe_area_km2']:.3f} km²")
    
    # Visualizations
    tab1, tab2, tab3 = st.tabs(["Risk Zones", "Evacuation Map", "Infrastructure Impact"])
    
    with tab1:
        # Risk zone map
        downsample = max(1, dem.shape[0] // 500)
        risk_ds = risk_zones[::downsample, ::downsample]
        
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=risk_ds,
            colorscale=get_risk_zone_colorscale(),
            colorbar=dict(
                title="Risk Level",
                tickvals=[0, 1, 2, 3, 4],
                ticktext=["Safe", "Low", "Medium", "High", "Critical"]
            ),
            zmin=0,
            zmax=4
        ))
        fig.update_layout(
            title=f"Flood Risk Zones (Water Level: {flood_level:.1f}m)",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Evacuation priority map
        evac_ds = evacuation_info['evacuation_priority'][::downsample, ::downsample]
        
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=evac_ds,
            colorscale=[[0, 'green'], [0.33, 'yellow'], [0.66, 'orange'], [1.0, 'red']],
            colorbar=dict(
                title="Priority",
                tickvals=[0, 1, 2, 3],
                ticktext=["Safe", "Monitor", "Prepare", "Evacuate Now"]
            )
        ))
        fig.update_layout(
            title="Evacuation Priority Map",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Evacuation stats
        st.subheader("Evacuation Statistics")
        evac_stats = {
            "Priority Level": ["Immediate Evacuation", "High Priority", "Moderate Priority"],
            "Area (km²)": [
                evacuation_info['immediate_evacuation_km2'],
                evacuation_info['high_priority_km2'],
                evacuation_info['moderate_priority_km2']
            ]
        }
        st.dataframe(evac_stats, use_container_width=True)
    
    with tab3:
        # Mock infrastructure points (for demo)
        st.subheader("Infrastructure Assessment")
        st.info("💡 **Demo Mode**: Showing simulated infrastructure locations")
        
        # Generate random infrastructure points
        np.random.seed(42)
        num_structures = 50
        infrastructure_points = []
        for i in range(num_structures):
            infrastructure_points.append({
                'x': np.random.randint(0, dem.shape[1]),
                'y': np.random.randint(0, dem.shape[0]),
                'type': np.random.choice(['village', 'road', 'bridge', 'pump_station'])
            })
        
        impact = assess_infrastructure_impact(risk_zones, infrastructure_points)
        
        # Impact metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Structures", impact['total_structures'])
        with col2:
            st.metric("At Risk", impact['critical_risk'] + impact['high_risk'], 
                     delta=f"{(impact['critical_risk'] + impact['high_risk'])/impact['total_structures']*100:.1f}%")
        with col3:
            st.metric("Safe", impact['safe'])
        
        # By type
        st.subheader("Risk by Infrastructure Type")
        type_data = []
        for infra_type, data in impact['by_type'].items():
            type_data.append({
                "Type": infra_type.replace('_', ' ').title(),
                "Total": data['total'],
                "At Risk": data['at_risk'],
                "Critical": data['critical']
            })
        st.dataframe(type_data, use_container_width=True)

elif analysis_type == "📡 IoT Sensors":
    st.header("📡 IoT Sensor Network - Real-Time Monitoring")
    
    # Initialize sensor network
    @st.cache_resource
    def get_sensor_network():
        return MockSensorNetwork(num_sensors=5)
    
    sensor_network = get_sensor_network()
    
    # Auto-refresh toggle
    auto_refresh = st.toggle("Auto-refresh (every 5s)", value=False)
    
    if auto_refresh:
        st_autorefresh = st.empty()
        import time
        time.sleep(5)
        st.rerun()
    
    # Get current readings
    current_readings = sensor_network.get_current_readings()
    network_health = sensor_network.get_network_health()
    
    # Network status
    st.subheader("🌐 Network Status")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Sensors", f"{network_health['active_sensors']}/{network_health['total_sensors']}")
    with col2:
        st.metric("Network Uptime", f"{network_health['network_uptime_%']:.0f}%")
    with col3:
        st.metric("Avg Battery", f"{network_health['average_battery_%']:.0f}%")
    with col4:
        from datetime import datetime
        st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
    
    # Sensor readings
    st.subheader("📊 Live Sensor Data")
    
    for reading in current_readings:
        with st.expander(f"🔵 {reading['sensor_name']} ({reading['sensor_id']})", expanded=True):
            # Metrics
            m = reading['measurements']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                wqi, wqi_status = calculate_water_quality_index(reading)
                color = "🟢" if wqi >= 70 else "🟡" if wqi >= 50 else "🔴"
                st.metric("Water Quality Index", f"{color} {wqi:.0f}", wqi_status)
            
            with col2:
                st.metric("Water Level", f"{m['water_level_m']:.2f} m")
            
            with col3:
                ph_status = "✓" if 6.5 <= m['ph'] <= 8.5 else "⚠"
                st.metric("pH", f"{ph_status} {m['ph']:.2f}")
            
            with col4:
                do_status = "✓" if m['dissolved_oxygen_mg_l'] >= 5.0 else "⚠"
                st.metric("Dissolved O₂", f"{do_status} {m['dissolved_oxygen_mg_l']:.1f} mg/L")
            
            # Additional parameters
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Temperature", f"{m['temperature_c']:.1f} °C")
            with col2:
                st.metric("Turbidity", f"{m['turbidity_ntu']:.1f} NTU")
            with col3:
                st.metric("Flow Rate", f"{m['flow_rate_m3_s']:.1f} m³/s")
            
            # Alerts
            if reading['alerts']:
                st.warning("Alerts:\n" + "\n".join(f"- {alert}" for alert in reading['alerts']))
    
    # Historical trends
    st.subheader("📈 24-Hour Trends")
    historical_data = sensor_network.get_historical_data(hours=24)
    
    # Plot trends for first sensor
    sensor_id = sensor_network.sensors[0]['id']
    sensor_history = historical_data[sensor_id]
    
    import pandas as pd
    df = pd.DataFrame(sensor_history)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(df))), y=df['water_level_m'], name="Water Level (m)", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=list(range(len(df))), y=df['ph'], name="pH", line=dict(color='green'), yaxis='y2'))
    fig.add_trace(go.Scatter(x=list(range(len(df))), y=df['temperature_c'], name="Temperature (°C)", line=dict(color='red'), yaxis='y3'))
    
    fig.update_layout(
        title=f"Sensor Trends - {sensor_network.sensors[0]['name']}",
        xaxis=dict(title="Time (10-min intervals)"),
        yaxis=dict(title="Water Level (m)", side='left'),
        yaxis2=dict(title="pH", overlaying='y', side='right'),
        yaxis3=dict(title="Temperature (°C)", overlaying='y', side='right', position=0.85),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("👥 Team: Puneet, Aaditya, Aayush")
with col2:
    st.caption("🏆 Riverathon 1.0 - Amity University")
with col3:
    st.caption("📅 Grand Finale: Feb 11-12, 2026")
