"""
Decision Center - Real-time Alert Dashboard
Critical alerts, evacuation planning, resource allocation
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from decision_engine import DecisionEngine
from ui_components import get_common_css, page_header, section_header

# Page config
st.set_page_config(
    page_title="Decision Center - Ganga Guardian AI",
    page_icon="⚠️",
    layout="wide"
)

# Apply common CSS
st.markdown(get_common_css(), unsafe_allow_html=True)

# Additional page-specific CSS
st.markdown("""
<style>
    .alert-critical {
        background: linear-gradient(135deg, #ff416c15 0%, #ff415615 100%);
        border-left: 5px solid #ff416c;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .alert-high {
        background: linear-gradient(135deg, #f7971e15 0%, #ffd20015 100%);
        border-left: 5px solid #f7971e;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .alert-medium {
        background: linear-gradient(135deg, #ffd89b15 0%, #19547b15 100%);
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-card-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4156 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
    }
    .metric-card-warning {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
    }
    .metric-card-success {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
    }
    .action-button {
        background: #667eea;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .action-button:hover {
        background: #764ba2;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Header
page_header("⚠️", "Decision Support Center", "Real-time Alerts & Emergency Response")
st.divider()

# Initialize decision engine
@st.cache_resource
def get_decision_engine():
    return DecisionEngine()

engine = get_decision_engine()

# Get current data
alerts = engine.generate_alerts()
flood_risk = engine.get_current_flood_risk()
impact = engine.calculate_impact_estimate()
resources = engine.get_resource_allocation()
timeline = engine.get_action_timeline()

# Categorize alerts
critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
high_alerts = [a for a in alerts if a['severity'] == 'HIGH']
medium_alerts = [a for a in alerts if a['severity'] == 'MEDIUM']

# ===== TOP STATUS ROW =====
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card-critical">
        <h2 style="margin:0; font-size: 3rem;">{len(critical_alerts)}</h2>
        <p style="margin:0; font-size: 1.2rem;">CRITICAL ALERTS</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card-warning">
        <h2 style="margin:0; font-size: 3rem;">{len(high_alerts)}</h2>
        <p style="margin:0; font-size: 1.2rem;">HIGH PRIORITY</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    risk_class = "metric-card-critical" if flood_risk['level'] in ['CRITICAL', 'HIGH'] else "metric-card-warning"
    st.markdown(f"""
    <div class="{risk_class}">
        <h2 style="margin:0; font-size: 2rem;">{flood_risk['level']}</h2>
        <p style="margin:0; font-size: 1.2rem;">FLOOD RISK</p>
        <p style="margin:0; font-size: 0.9rem;">{flood_risk['probability']}% in {flood_risk['time_to_event_hours']}h</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card-success">
        <h2 style="margin:0; font-size: 3rem;">{len(resources)}</h2>
        <p style="margin:0; font-size: 1.2rem;">TEAMS DEPLOYED</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===== MAIN CONTENT: ALERTS AND ACTIONS =====
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("## 📢 Active Alerts")
    
    # Filter options
    filter_severity = st.multiselect(
        "Filter by severity",
        ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        default=['CRITICAL', 'HIGH']
    )
    
    filtered_alerts = [a for a in alerts if a['severity'] in filter_severity]
    
    if len(filtered_alerts) == 0:
        st.success("✅ No alerts matching selected filters")
    else:
        for idx, alert in enumerate(filtered_alerts):
            severity_class = {
                'CRITICAL': 'alert-critical',
                'HIGH': 'alert-high',
                'MEDIUM': 'alert-medium'
            }.get(alert['severity'], 'alert-medium')
            
            severity_icon = {
                'CRITICAL': '🔴',
                'HIGH': '🟡',
                'MEDIUM': '🟠'
            }.get(alert['severity'], '🔵')
            
            with st.container():
                st.markdown(f"""
                <div class="{severity_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h3 style="margin:0; color: #212529;">{severity_icon} {alert['title']}</h3>
                            <p style="margin:0.5rem 0; color: #495057; font-size: 0.95rem;">{alert['description']}</p>
                            <p style="margin:0.5rem 0; font-weight: 600; color: #212529;">
                                <span style="color: #667eea;">→ ACTION:</span> {alert['recommendation']}
                            </p>
                        </div>
                    </div>
                    <div style="margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
                        <small style="color: #6c757d;">
                            📍 {alert['location']} | ⏰ {alert['timestamp']} | 
                            🎯 Confidence: {alert['confidence']:.0%}
                        </small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable impact details
                with st.expander(f"📊 View Impact Details - Alert #{idx+1}"):
                    if 'impact' in alert:
                        impact_cols = st.columns(len(alert['impact']))
                        for col, (key, value) in zip(impact_cols, alert['impact'].items()):
                            col.metric(key.replace('_', ' ').title(), value)

with col_right:
    st.markdown("## 📊 Impact Estimate")
    
    st.metric(
        "People at Risk",
        f"{impact['people']:,}",
        delta=f"+{impact['people_change']}" if impact['people_change'] > 0 else None,
        delta_color="inverse"
    )
    
    st.metric(
        "Buildings Affected",
        f"{impact['buildings']:,}"
    )
    
    st.metric(
        "Area at Risk",
        f"{impact['area_km2']:.1f} km²"
    )
    
    st.metric(
        "Economic Impact",
        f"₹{impact['economic_impact_cr']:.1f} Cr"
    )
    
    st.metric(
        "Critical Infrastructure",
        f"{impact['critical_infrastructure']} facilities"
    )
    
    st.divider()
    
    st.markdown("### 🎯 Affected Zones")
    zone_data = pd.DataFrame({
        'Zone': [f'Zone {z}' for z in flood_risk['affected_zones']],
        'Risk Level': ['HIGH', 'CRITICAL', 'HIGH']
    })
    st.dataframe(zone_data, hide_index=True, use_container_width=True)

st.divider()

# ===== RESOURCE ALLOCATION =====
st.markdown("## 🚁 Resource Deployment")

resource_tabs = st.tabs(["📋 Deployment Plan", "🗺️ Geographic View", "⏱️ Action Timeline"])

with resource_tabs[0]:
    st.markdown("### Recommended Resource Allocation")
    
    for resource in resources:
        priority_color = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107'
        }.get(resource['priority'], '#6c757d')
        
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**{resource['resource']}**")
                st.caption(f"📍 {resource['location']}")
            
            with col2:
                st.markdown(f"*{resource['task']}*")
                st.caption(f"👥 {resource['personnel']} personnel")
            
            with col3:
                st.markdown(f"<span style='color: {priority_color}; font-weight: bold;'>{resource['priority']}</span>", unsafe_allow_html=True)
            
            if 'equipment' in resource:
                with st.expander("🛠️ Equipment Required"):
                    for item in resource['equipment']:
                        st.markdown(f"• {item}")
            
            st.divider()

with resource_tabs[1]:
    st.markdown("### Geographic Deployment Map")
    
    # Create mock map data
    map_data = pd.DataFrame({
        'Resource': [r['resource'] for r in resources],
        'Lat': [26.16 + i*0.01 for i in range(len(resources))],
        'Lon': [77.96 + i*0.01 for i in range(len(resources))],
        'Priority': [r['priority'] for r in resources],
        'Size': [30 if r['priority']=='CRITICAL' else 20 if r['priority']=='HIGH' else 15 for r in resources]
    })
    
    fig_map = px.scatter_mapbox(
        map_data,
        lat='Lat',
        lon='Lon',
        color='Priority',
        size='Size',
        hover_name='Resource',
        color_discrete_map={
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107'
        },
        zoom=11,
        height=500
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig_map, use_container_width=True)

with resource_tabs[2]:
    st.markdown("### 48-Hour Action Timeline")
    
    # Create timeline visualization
    timeline_df = pd.DataFrame(timeline)
    
    # Color code by urgency
    color_map = {
        'IMMEDIATE': '#dc3545',
        'CRITICAL': '#ff416c',
        'HIGH': '#fd7e14',
        'MEDIUM': '#ffc107'
    }
    
    timeline_df['color'] = timeline_df['urgency'].map(color_map)
    
    for idx, row in timeline_df.iterrows():
        col1, col2, col3 = st.columns([1, 2, 2])
        
        with col1:
            st.markdown(f"**{row['time']}**")
        
        with col2:
            st.markdown(f"<span style='color: {row['color']}; font-weight: bold;'>{row['urgency']}</span>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"{row['action']}")
            st.caption(f"👤 {row['responsible']}")
        
        if idx < len(timeline_df) - 1:
            st.markdown("---")

st.divider()

# ===== EVACUATION PLANNING =====
st.markdown("## 🚨 Evacuation Planning")

evac_zone = st.selectbox(
    "Select zone for evacuation details",
    flood_risk['affected_zones'],
    format_func=lambda x: f"Zone {x}"
)

evac_plan = engine.get_evacuation_plan(evac_zone)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Evacuation Overview")
    
    st.metric("Estimated Population", f"{evac_plan['estimated_population']:,}")
    st.metric("Priority Level", evac_plan['priority'])
    
    st.markdown("#### 🚗 Evacuation Routes")
    for route in evac_plan['evacuation_routes']:
        st.markdown(f"""
        - **{route['route']}**
          - Capacity: {route['capacity']} people
          - Distance: {route['distance_km']} km
        """)

with col2:
    st.markdown("### 🏕️ Safe Zones")
    
    for camp in evac_plan['safe_zones']:
        st.markdown(f"""
        **{camp['name']}**
        - Capacity: {camp['capacity']} people
        - Facilities: {', '.join(camp['facilities'])}
        """)
        st.divider()
    
    st.markdown("### ⏱️ Timeline")
    for phase, timing in evac_plan['timeline'].items():
        st.markdown(f"**{phase.replace('_', ' ').title()}:** {timing}")

# ===== QUICK ACTIONS =====
st.divider()
st.markdown("## ⚡ Quick Actions")

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("🚨 Issue Evacuation Alert", use_container_width=True, type="primary"):
        st.success("✅ Evacuation alert issued to Zone 3 residents")

with action_col2:
    if st.button("📱 Notify Emergency Teams", use_container_width=True):
        st.success("✅ All emergency teams notified")

with action_col3:
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("📄 Detailed report being generated...")

with action_col4:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Footer
st.divider()
st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data refresh every 5 minutes")
