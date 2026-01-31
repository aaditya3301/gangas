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

# Enhanced Custom CSS for ultra-modern look
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', 'Poppins', sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Main container background with gradient */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Animated gradient header */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0 0.5rem 0;
        margin-bottom: 0;
        animation: gradientShift 5s ease infinite;
        letter-spacing: -1px;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subtitle {
        text-align: center;
        color: #495057;
        font-size: 1.3rem;
        margin-bottom: 3rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.8;
    }
    
    /* Enhanced metric cards with glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: -200% 0; }
        50% { background-position: 200% 0; }
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .metric-value {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 1rem 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    /* Alert cards with pulsing effect */
    .alert-critical {
        background: linear-gradient(135deg, rgba(255, 65, 108, 0.15) 0%, rgba(255, 69, 86, 0.15) 100%);
        border-left: 5px solid #ff416c;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(255, 65, 108, 0.2);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 5px 20px rgba(255, 65, 108, 0.2); }
        50% { box-shadow: 0 5px 30px rgba(255, 65, 108, 0.4); }
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(247, 151, 30, 0.15) 0%, rgba(255, 210, 0, 0.15) 100%);
        border-left: 5px solid #f7971e;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(247, 151, 30, 0.2);
    }
    
    .alert-moderate {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 213, 79, 0.15) 100%);
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(255, 193, 7, 0.2);
    }
    
    /* Health status colors with glow */
    .health-excellent { 
        color: #28a745;
        text-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
    }
    .health-good { 
        color: #5cb85c;
        text-shadow: 0 0 10px rgba(92, 184, 92, 0.5);
    }
    .health-moderate { 
        color: #ffc107;
        text-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
    }
    .health-poor { 
        color: #fd7e14;
        text-shadow: 0 0 10px rgba(253, 126, 20, 0.5);
    }
    .health-critical { 
        color: #dc3545;
        text-shadow: 0 0 10px rgba(220, 53, 69, 0.5);
    }
    
    /* Enhanced buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        padding: 1rem 2.5rem;
        border-radius: 15px;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Section headers */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #667eea, #764ba2) 1;
        position: relative;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        left: 0;
        bottom: -3px;
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
    }
    
    /* Navigation cards */
    .nav-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        cursor: pointer;
        text-align: center;
    }
    
    .nav-card:hover {
        transform: translateY(-10px) rotate(2deg);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.6);
    }
    
    .nav-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 5px 10px rgba(0,0,0,0.2));
    }
    
    /* Sidebar styling - Elegant & Clean */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            rgba(102, 126, 234, 0.03) 0%, 
            rgba(118, 75, 162, 0.05) 50%,
            rgba(240, 147, 251, 0.03) 100%
        );
        backdrop-filter: blur(20px);
        box-shadow: 2px 0 30px rgba(102, 126, 234, 0.08);
        border-right: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        padding: 2rem 1rem;
    }
    
    /* Sidebar logo/header area */
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #2c3e50 !important;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        text-align: center;
        font-size: 1.5rem;
    }
    
    /* Sidebar text content */
    section[data-testid="stSidebar"] .stMarkdown {
        color: #495057 !important;
        font-weight: 500;
    }
    
    /* Sidebar dividers */
    section[data-testid="stSidebar"] hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(102, 126, 234, 0.3) 50%, 
            transparent 100%
        );
    }
    
    /* Sidebar widgets (selectbox, slider, etc.) */
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stCheckbox label,
        section[data-testid="stSidebar"] .stNumberInput label,
        section[data-testid="stSidebar"] .stTextInput label,
        section[data-testid="stSidebar"] .stDateInput label,
        section[data-testid="stSidebar"] .stTimeInput label {
            color: #2c3e50 !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
            display: block;
            text-shadow: 0 1px 2px rgba(0,0,0,0.05);
        background: rgba(255, 255, 255, 0.8);
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 3px 12px rgba(102, 126, 234, 0.15);
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar info boxes */
    section[data-testid="stSidebar"] .stAlert {
        background: rgba(255, 255, 255, 0.7) !important;
        border-left: 4px solid #667eea !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar metric containers */
    section[data-testid="stSidebar"] div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid rgba(102, 126, 234, 0.15);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    
    /* Sidebar expander */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        color: #2c3e50 !important;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        border-radius: 15px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        padding: 0 30px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #667eea15, #764ba215);
        border-color: rgba(102, 126, 234, 0.6);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    /* Metric container enhancements */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Success/Info/Warning/Error boxes */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 15px !important;
        border-left-width: 5px !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1) !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
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
st.markdown('<h2 class="section-header">📊 Live System Status</h2>', unsafe_allow_html=True)
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
        <div class="nav-icon">🌿</div>
        <h4 style="margin:0; color: #6c757d; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Ecosystem Health</h4>
        <h1 class="metric-value {health_color}">{overall_score}</h1>
        <p style="margin:0; color: #6c757d; font-weight: 500;">Grade: <strong>{grade}</strong> • {status}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Active Alerts
    total_alerts = len(alerts)
    alert_color = "#dc3545" if len(critical_alerts) > 0 else "#ffc107" if len(high_alerts) > 0 else "#28a745"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="nav-icon">🚨</div>
        <h4 style="margin:0; color: #6c757d; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Active Alerts</h4>
        <h1 class="metric-value" style="-webkit-text-fill-color: {alert_color};">{total_alerts}</h1>
        <p style="margin:0; color: #6c757d; font-weight: 500;"><strong>{len(critical_alerts)}</strong> Critical • <strong>{len(high_alerts)}</strong> High</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Flood Risk
    flood_risk = decision_engine.get_current_flood_risk()
    risk_color = {"LOW": "#28a745", "MODERATE": "#ffc107", "HIGH": "#fd7e14", "CRITICAL": "#dc3545"}
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="nav-icon">🌊</div>
        <h4 style="margin:0; color: #6c757d; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Flood Risk (48h)</h4>
        <h1 class="metric-value" style="-webkit-text-fill-color: {risk_color.get(flood_risk['level'], '#ffc107')};">{flood_risk['level']}</h1>
        <p style="margin:0; color: #6c757d; font-weight: 500;">Probability: <strong>{flood_risk['probability']}%</strong></p>
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
st.markdown('<h2 class="section-header">🧭 Explore System Features</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">🚨</div>
        <h3 style="color: #2c3e50; font-weight: 700; margin: 1rem 0 0.5rem 0;">Decision Center</h3>
        <p style="color: #6c757d; font-size: 0.95rem; margin: 0;">Real-time alerts, evacuation planning, and resource allocation</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Decision Center →", key="btn_decision", use_container_width=True):
        st.switch_page("pages/01_decision_center.py")

with col2:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">🤖</div>
        <h3 style="color: #2c3e50; font-weight: 700; margin: 1rem 0 0.5rem 0;">AI Predictions</h3>
        <p style="color: #6c757d; font-size: 0.95rem; margin: 0;">Machine learning flood forecasting and climate impact analysis</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch AI Predictions →", key="btn_ai", use_container_width=True):
        st.switch_page("pages/02_ai_predictions.py")

with col3:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">👥</div>
        <h3 style="color: #2c3e50; font-weight: 700; margin: 1rem 0 0.5rem 0;">Community Portal</h3>
        <p style="color: #6c757d; font-size: 0.95rem; margin: 0;">Citizen science reports and interactive community engagement</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Community Portal →", key="btn_community", use_container_width=True):
        st.switch_page("pages/03_community_portal.py")

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">🛰️</div>
        <h3 style="color: #2c3e50; font-weight: 700; margin: 1rem 0 0.5rem 0;">Multi-Sensor Fusion</h3>
        <p style="color: #6c757d; font-size: 0.95rem; margin: 0;">LiDAR + Satellite + IoT sensor data integration</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Sensor Fusion →", key="btn_fusion", use_container_width=True):
        st.switch_page("pages/04_multi_sensor.py")

with col5:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">📊</div>
        <h3 style="color: #2c3e50; font-weight: 700; margin: 1rem 0 0.5rem 0;">Analytics Dashboard</h3>
        <p style="color: #6c757d; font-size: 0.95rem; margin: 0;">Advanced geospatial analysis and terrain insights</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Analytics →", key="btn_analytics", use_container_width=True):
        st.switch_page("pages/05_analytics.py")

with col6:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">🎮</div>
        <h3 style="color: #2c3e50; font-weight: 700; margin: 1rem 0 0.5rem 0;">3D Terrain Viewer</h3>
        <p style="color: #6c757d; font-size: 0.95rem; margin: 0;">Interactive 3D flood simulation on real terrain</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch 3D Viewer →", key="btn_3d", use_container_width=True):
        st.switch_page("pages/06_3d_terrain.py")

st.markdown("<br>", unsafe_allow_html=True)

# Evacuation route card - full width for emphasis
st.markdown("""
<div class="nav-card" style="background: linear-gradient(135deg, rgba(255,65,108,0.1), rgba(255,69,86,0.1)); border-color: rgba(255,65,108,0.3);">
    <div style="display: flex; align-items: center; gap: 2rem;">
        <div class="nav-icon" style="font-size: 5rem;">🎯</div>
        <div style="text-align: left; flex: 1;">
            <h2 style="color: #dc3545; font-weight: 800; margin: 0.5rem 0;">Emergency Evacuation Optimizer</h2>
            <p style="color: #6c757d; font-size: 1.1rem; margin: 0;">AI-powered route planning for emergency evacuations with real-time traffic and risk assessment</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🚨 Launch Evacuation Planner →", key="btn_evac", use_container_width=True, type="primary"):
    st.switch_page("pages/07_evacuation.py")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 2rem 0;">
    <p style="font-size: 1.2rem;"><strong>🌊 Aqua Guardians</strong> | Riverathon 1.0 National Hackathon</p>
    <p style="font-size: 1rem; margin: 0.5rem 0;">Protecting Ganga through Technology, Community & AI</p>
    <small style="opacity: 0.7;">Last updated: {}</small>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
