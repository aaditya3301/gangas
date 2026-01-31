"""
Ganga Guardian AI - Landing Page
Comprehensive Ecosystem Monitoring System
Riverathon 1.0 - Aqua Guardians Team
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from ecosystem_score import calculate_ecosystem_health, get_health_trend
from decision_engine import DecisionEngine
from mock_iot import MockSensorNetwork

# Page configuration
st.set_page_config(
    page_title="Ganga Guardian AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern look
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern styling */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #667eea30;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .alert-critical {
        background: linear-gradient(135deg, #ff416c15 0%, #ff415615 100%);
        border: 2px solid #ff416c;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f7971e15 0%, #ffd20015 100%);
        border: 2px solid #f7971e;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .health-excellent { color: #28a745; }
    .health-good { color: #5cb85c; }
    .health-moderate { color: #ffc107; }
    .health-poor { color: #fd7e14; }
    .health-critical { color: #dc3545; }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🌊 Ganga Guardian AI</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Real-time Ecosystem Monitoring & Climate Impact Forecasting | Riverathon 1.0</p>', unsafe_allow_html=True)

# Initialize systems
@st.cache_resource
def initialize_systems():
    """Initialize decision engine and IoT network"""
    decision_engine = DecisionEngine()
    sensor_network = MockSensorNetwork()
    return decision_engine, sensor_network

decision_engine, sensor_network = initialize_systems()

# Calculate current ecosystem health
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_current_health():
    """Get current ecosystem health metrics"""
    # Mock data - will integrate real data from zones
    health_data = {
        'vegetation_health': 72,
        'water_quality': 58,
        'terrain_stability': 81,
        'biodiversity_index': 65
    }
    
    overall_score, grade, status = calculate_ecosystem_health(
        health_data['vegetation_health'],
        health_data['water_quality'],
        health_data['terrain_stability'],
        health_data['biodiversity_index']
    )
    
    return overall_score, grade, status, health_data

overall_score, grade, status, health_data = get_current_health()

# Get active alerts
alerts = decision_engine.generate_alerts()
critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
high_alerts = [a for a in alerts if a['severity'] == 'HIGH']

# ===== TOP METRICS ROW =====
st.markdown("### 📊 Live System Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Ecosystem Health Score
    health_color = {
        'Excellent': 'health-excellent',
        'Good': 'health-good',
        'Moderate': 'health-moderate',
        'Poor': 'health-poor',
        'Critical': 'health-critical'
    }.get(status, 'health-moderate')
    
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="margin:0; color: #6c757d;">🌿 Ecosystem Health</h4>
        <h1 style="margin:0.5rem 0;" class="{health_color}">{overall_score}/100</h1>
        <p style="margin:0; color: #6c757d;">Grade: {grade} ({status})</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Active Alerts
    total_alerts = len(alerts)
    alert_color = "#dc3545" if len(critical_alerts) > 0 else "#ffc107" if len(high_alerts) > 0 else "#28a745"
    
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="margin:0; color: #6c757d;">🚨 Active Alerts</h4>
        <h1 style="margin:0.5rem 0; color: {alert_color};">{total_alerts}</h1>
        <p style="margin:0; color: #6c757d;">{len(critical_alerts)} Critical | {len(high_alerts)} High</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Flood Risk
    flood_risk = decision_engine.get_current_flood_risk()
    risk_color = {"LOW": "#28a745", "MODERATE": "#ffc107", "HIGH": "#fd7e14", "CRITICAL": "#dc3545"}
    
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="margin:0; color: #6c757d;">🌊 Flood Risk (48h)</h4>
        <h1 style="margin:0.5rem 0; color: {risk_color.get(flood_risk['level'], '#ffc107')};">{flood_risk['level']}</h1>
        <p style="margin:0; color: #6c757d;">Probability: {flood_risk['probability']}%</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # Community Reports
    total_reports = decision_engine.get_community_stats()
    
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="margin:0; color: #6c757d;">👥 Community Reports</h4>
        <h1 style="margin:0.5rem 0; color: #667eea;">{total_reports['total']}</h1>
        <p style="margin:0; color: #6c757d;">{total_reports['verified']} Verified | {total_reports['pending']} Pending</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===== CRITICAL ALERTS SECTION =====
if len(critical_alerts) > 0 or len(high_alerts) > 0:
    st.markdown("### 🚨 Critical Alerts & Recommendations")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Show top 3 alerts
        for alert in (critical_alerts + high_alerts)[:3]:
            severity_class = "alert-critical" if alert['severity'] == 'CRITICAL' else "alert-warning"
            severity_icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡"
            
            st.markdown(f"""
            <div class="{severity_class}">
                <h4 style="margin:0;">{severity_icon} {alert['severity']} - {alert['title']}</h4>
                <p style="margin:0.5rem 0 0 0; color: #495057;">{alert['description']}</p>
                <p style="margin:0.5rem 0 0 0; font-weight: 600; color: #212529;">→ ACTION: {alert['recommendation']}</p>
                <small style="color: #6c757d;">{alert['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("#### 📍 Impact Estimate")
        impact = decision_engine.calculate_impact_estimate()
        
        st.metric("People at Risk", f"{impact['people']:,}", delta=f"+{impact['people_change']}" if impact['people_change'] > 0 else None, delta_color="inverse")
        st.metric("Buildings Affected", f"{impact['buildings']:,}")
        st.metric("Area at Risk", f"{impact['area_km2']:.1f} km²")

st.divider()

# ===== HEALTH BREAKDOWN & TRENDS =====
st.markdown("### 📈 Ecosystem Health Breakdown")

col1, col2 = st.columns([1, 2])

with col1:
    # Health component breakdown (donut chart)
    fig_breakdown = go.Figure(data=[go.Pie(
        labels=['Vegetation Health', 'Water Quality', 'Terrain Stability', 'Biodiversity'],
        values=[health_data['vegetation_health'], health_data['water_quality'], 
                health_data['terrain_stability'], health_data['biodiversity_index']],
        hole=0.5,
        marker=dict(colors=['#28a745', '#17a2b8', '#6c757d', '#ffc107']),
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig_breakdown.update_layout(
        title="Health Components",
        height=350,
        showlegend=False,
        annotations=[dict(text=f'{overall_score}<br>Overall', x=0.5, y=0.5, font_size=24, showarrow=False)]
    )
    
    st.plotly_chart(fig_breakdown, use_container_width=True)

with col2:
    # 30-day trend
    trend_data = get_health_trend(days=30)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_data['dates'],
        y=trend_data['scores'],
        mode='lines+markers',
        name='Ecosystem Health',
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    # Add threshold lines
    fig_trend.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Excellent (80+)")
    fig_trend.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="Moderate (60+)")
    fig_trend.add_hline(y=40, line_dash="dash", line_color="red", annotation_text="Poor (40+)")
    
    fig_trend.update_layout(
        title="30-Day Ecosystem Health Trend",
        xaxis_title="Date",
        yaxis_title="Health Score",
        height=350,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ===== NAVIGATION CARDS =====
st.markdown("### 🧭 Explore System Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🚨 Decision Center</h3>
        <p>Real-time alerts, evacuation planning, and resource allocation recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Decision Center →", key="btn_decision", use_container_width=True):
        st.switch_page("pages/01_🚨_Decision_Center.py")

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>🤖 AI Predictions</h3>
        <p>Machine learning flood forecasting and climate impact analysis</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open AI Predictions →", key="btn_ai", use_container_width=True):
        st.switch_page("pages/02_🤖_AI_Predictions.py")

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>👥 Community Portal</h3>
        <p>Citizen science reports, interactive mapping, and community engagement</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Community Portal →", key="btn_community", use_container_width=True):
        st.switch_page("pages/03_👥_Community_Portal.py")

col4, col5 = st.columns(2)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h3>🛰️ Multi-Sensor Fusion</h3>
        <p>LiDAR + Satellite + IoT sensor data integration and cross-validation</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Sensor Fusion →", key="btn_fusion", use_container_width=True):
        st.switch_page("pages/04_🛰️_Multi_Sensor.py")

with col5:
    st.markdown("""
    <div class="metric-card">
        <h3>📊 Analytics & Visualization</h3>
        <p>Detailed terrain analysis, flood simulation, and 3D visualization</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Analytics →", key="btn_analytics", use_container_width=True):
        st.switch_page("pages/05_📊_Analytics.py")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 2rem 0;">
    <p><strong>Aqua Guardians</strong> | Riverathon 1.0 National Hackathon</p>
    <p>🌊 Protecting Ganga through Technology, Community & AI 🌊</p>
    <small>Last updated: {}</small>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
