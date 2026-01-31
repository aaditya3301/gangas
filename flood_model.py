"""
3D Flood Simulation Model
Advanced 3D visualization with animated flood progression
Aqua Guardians - Riverathon 1.0
"""

import sys
from pathlib import Path
import plotly.graph_objects as go
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from data_loader import LiDARDataset
from flood_analysis import calculate_flood_depth

def create_3d_flood_simulation(zone='zone_53H13SE', downsample=5, num_levels=15):
    """
    Create interactive 3D flood simulation with slider
    
    Args:
        zone: Geographic zone to load
        downsample: Factor to reduce data size (higher = faster)
        num_levels: Number of water level steps in animation
    """
    print("\n" + "="*60)
    print("🌊 3D Flood Simulation - Aqua Guardians")
    print("="*60 + "\n")
    
    # Load data
    print("📥 Loading LiDAR data...")
    dataset = LiDARDataset(zone)
    
    if len(dataset.dem_files) == 0:
        print("❌ No data found! Please download data first.")
        return
    
    dem_path, ortho_path = dataset.find_matching_pair(dataset.dem_files[0].name)
    dem, metadata = dataset.load_dem(dem_path)
    rgb = dataset.load_ortho(ortho_path, target_shape=dem.shape)
    
    print(f"✓ Loaded terrain: {dem.shape}")
    print(f"✓ Elevation range: {np.nanmin(dem):.2f}m to {np.nanmax(dem):.2f}m\n")
    
    # Downsample for performance
    print(f"⚙️ Downsampling by factor {downsample} for smooth performance...")
    dem_ds = dem[::downsample, ::downsample]
    rgb_ds = rgb[::downsample, ::downsample]
    
    # Create RGB color matrix for terrain texture
    print("🎨 Applying satellite imagery texture...")
    color_surface = np.zeros(dem_ds.shape, dtype=object)
    for i in range(dem_ds.shape[0]):
        for j in range(dem_ds.shape[1]):
            color_surface[i, j] = f'rgb({rgb_ds[i,j,0]},{rgb_ds[i,j,1]},{rgb_ds[i,j,2]})'
    
    # Calculate water levels
    min_elev = np.nanmin(dem_ds)
    max_elev = np.nanmax(dem_ds)
    water_levels = np.linspace(min_elev + 0.5, max_elev - 0.5, num_levels)
    
    print(f"💧 Creating {num_levels} flood scenarios...\n")
    
    # Create base figure with terrain
    fig = go.Figure()
    
    # Add textured terrain surface
    fig.add_trace(go.Surface(
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
    
    # Add initial water surface (transparent blue)
    water_plane = np.full_like(dem_ds, water_levels[0])
    fig.add_trace(go.Surface(
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
        # Calculate flooded area
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
                title_text=f'Flood Simulation | Water Level: {level:.2f}m | Flooded Area: {flooded_pct:.1f}%'
            )
        ))
    
    fig.frames = frames
    
    # Configure layout and slider
    fig.update_layout(
        title={
            'text': f'🌊 3D Flood Simulation - {zone}<br><sub>Drag slider to adjust water level</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        scene=dict(
            zaxis=dict(
                range=[min_elev - 1, max_elev + 1],
                title='Elevation (m)',
                gridcolor='white',
                backgroundcolor='rgb(230, 230,230)'
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
        width=1200,
        height=800,
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
    
    print("✅ Simulation ready!")
    print("\n💡 Tips:")
    print("  - Drag the slider to change water level")
    print("  - Click 'Play Flood' to animate")
    print("  - Click and drag to rotate view")
    print("  - Scroll to zoom\n")
    
    print("🚀 Opening in browser...")
    fig.show()


if __name__ == "__main__":
    # Configuration
    ZONE = 'zone_53H13SE'
    DOWNSAMPLE = 8  # Reduce to 5 for more detail (slower), increase to 10 for speed
    NUM_LEVELS = 20  # Number of water level steps
    
    create_3d_flood_simulation(
        zone=ZONE,
        downsample=DOWNSAMPLE,
        num_levels=NUM_LEVELS
    )