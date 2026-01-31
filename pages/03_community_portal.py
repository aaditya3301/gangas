"""
👥 Community Portal
Citizen science platform for flood observations
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.community_db import CommunityDatabase

st.set_page_config(
    page_title="Community Portal - Aqua Guardians",
    page_icon="👥",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_database():
    """Initialize database and populate demo data"""
    db = CommunityDatabase()
    db.populate_demo_data(count=127)  # Match the 127 from landing page
    return db

db = init_database()

# Header
st.title("👥 Community Portal")
st.markdown("### Citizen Science: Your Eyes on the River")
st.markdown("---")

# Top Stats Row
stats = db.get_statistics()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Reports",
        f"{stats['total_reports']:,}",
        delta=f"+{stats['last_24h']} today",
        delta_color="normal"
    )

with col2:
    st.metric(
        "Verified",
        f"{stats['verified_count']:,}",
        delta=f"{stats['verified_count']/max(stats['total_reports'],1)*100:.0f}% verified"
    )

with col3:
    critical_count = stats['by_severity'].get('CRITICAL', 0)
    st.metric(
        "Critical Alerts",
        f"{critical_count}",
        delta="⚠️ Needs Attention" if critical_count > 0 else "✅ All Clear"
    )

with col4:
    st.metric(
        "Active Citizens",
        f"{min(stats['total_reports'], 89)}",  # Mock unique reporters
        delta="+12 this week"
    )

st.markdown("---")

# Main Layout: Map + Reports
col_map, col_reports = st.columns([1.2, 1])

with col_map:
    st.subheader("📍 Report Map")
    
    # Filter controls
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        time_filter = st.selectbox(
            "Time Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
            index=1
        )
    
    with filter_col2:
        severity_filter = st.multiselect(
            "Severity",
            ["CRITICAL", "HIGH", "MODERATE", "LOW"],
            default=["CRITICAL", "HIGH", "MODERATE", "LOW"]
        )
    
    # Get filtered reports
    if time_filter == "Last 24 Hours":
        reports = db.get_recent_reports(hours=24)
    elif time_filter == "Last 7 Days":
        reports = db.get_recent_reports(hours=168)
    elif time_filter == "Last 30 Days":
        reports = db.get_recent_reports(hours=720)
    else:
        reports = db.get_all_reports(limit=500)
    
    # Filter by severity
    reports = [r for r in reports if r['severity'] in severity_filter]
    
    # Create map centered on Ganga
    m = folium.Map(
        location=[28.5, 80.0],  # Central Ganga region
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Severity colors
    severity_colors = {
        'CRITICAL': 'red',
        'HIGH': 'orange',
        'MODERATE': 'yellow',
        'LOW': 'green'
    }
    
    # Add markers
    for report in reports:
        folium.CircleMarker(
            location=[report['latitude'], report['longitude']],
            radius=8 if report['severity'] == 'CRITICAL' else 6,
            popup=folium.Popup(
                f"""
                <b>{report['report_type']}</b><br>
                {report['location_name']}<br>
                Severity: {report['severity']}<br>
                {report['description'][:50]}...<br>
                <i>Reported by {report['reporter_name']}</i><br>
                <i>{report['timestamp']}</i>
                """,
                max_width=250
            ),
            color=severity_colors[report['severity']],
            fill=True,
            fillColor=severity_colors[report['severity']],
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Display map
    st_folium(m, width=700, height=500)
    
    st.caption(f"📊 Showing {len(reports)} reports")

with col_reports:
    st.subheader("📋 Recent Reports")
    
    # Report type filter
    report_types = ["All Types"] + sorted(list(set([r['report_type'] for r in reports])))
    type_filter = st.selectbox("Filter by Type", report_types)
    
    # Filter reports
    display_reports = reports
    if type_filter != "All Types":
        display_reports = [r for r in reports if r['report_type'] == type_filter]
    
    # Display reports in scrollable container
    st.markdown(
        """
        <style>
        .report-card {
            border-left: 4px solid;
            padding: 10px;
            margin-bottom: 10px;
            background-color: rgba(255,255,255,0.05);
            border-radius: 4px;
        }
        .critical { border-color: #ff4b4b; }
        .high { border-color: #ffa500; }
        .moderate { border-color: #ffeb3b; }
        .low { border-color: #4caf50; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Scrollable container
    with st.container(height=500):
        for idx, report in enumerate(display_reports[:30]):  # Limit to 30 for performance
            severity_class = report['severity'].lower()
            
            verified_badge = "✅ Verified" if report['verified'] else ""
            
            st.markdown(
                f"""
                <div class="report-card {severity_class}">
                    <b>{report['report_type']}</b> - {report['severity']} {verified_badge}<br>
                    📍 {report['location_name']}<br>
                    {report['description']}<br>
                    <small>👤 {report['reporter_name']} | 🕒 {report['timestamp']} | 👍 {report['upvotes']}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")

# Submit New Report Section
st.subheader("📝 Submit a Report")

with st.expander("➕ Report a Flood Observation", expanded=False):
    report_col1, report_col2 = st.columns(2)
    
    with report_col1:
        reporter_name = st.text_input("Your Name", placeholder="John Doe")
        location_name = st.text_input("Location Name", placeholder="Haridwar Ghat")
        
        report_type = st.selectbox(
            "Report Type",
            [
                "Flooding",
                "Rising Water",
                "Blocked Drain",
                "Erosion",
                "Water Contamination",
                "Infrastructure Damage",
                "Wildlife Alert"
            ]
        )
        
        severity = st.select_slider(
            "Severity Level",
            options=["LOW", "MODERATE", "HIGH", "CRITICAL"],
            value="MODERATE"
        )
    
    with report_col2:
        latitude = st.number_input("Latitude", value=29.9457, format="%.4f")
        longitude = st.number_input("Longitude", value=78.1642, format="%.4f")
        
        water_level = st.number_input(
            "Water Level (cm) - Optional",
            min_value=0,
            max_value=500,
            value=0,
            help="Leave as 0 if not applicable"
        )
        
        description = st.text_area(
            "Description",
            placeholder="Describe what you observed...",
            height=100
        )
    
    if st.button("🚀 Submit Report", type="primary"):
        if reporter_name and location_name and description:
            report_id = db.add_report(
                reporter_name=reporter_name,
                location_name=location_name,
                latitude=latitude,
                longitude=longitude,
                report_type=report_type,
                severity=severity,
                description=description,
                water_level_cm=water_level if water_level > 0 else None
            )
            
            st.success(f"✅ Report #{report_id} submitted successfully!")
            st.balloons()
            
            # Refresh page after 2 seconds
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields (Name, Location, Description)")

# Bottom Statistics
st.markdown("---")
st.subheader("📊 Community Impact")

stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.markdown("### Report Types")
    type_df = pd.DataFrame([
        {"Type": k, "Count": v}
        for k, v in stats['by_type'].items()
    ]).sort_values('Count', ascending=False)
    
    st.dataframe(
        type_df,
        use_container_width=True,
        hide_index=True,
        height=250
    )

with stat_col2:
    st.markdown("### Severity Distribution")
    severity_df = pd.DataFrame([
        {"Severity": k, "Count": v}
        for k, v in stats['by_severity'].items()
    ])
    
    # Sort by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MODERATE': 2, 'LOW': 3}
    severity_df['order'] = severity_df['Severity'].map(severity_order)
    severity_df = severity_df.sort_values('order').drop('order', axis=1)
    
    st.dataframe(
        severity_df,
        use_container_width=True,
        hide_index=True,
        height=250
    )

with stat_col3:
    st.markdown("### Top Locations")
    
    # Count reports by location
    location_counts = {}
    for report in db.get_all_reports(limit=500):
        loc = report['location_name']
        location_counts[loc] = location_counts.get(loc, 0) + 1
    
    location_df = pd.DataFrame([
        {"Location": k, "Reports": v}
        for k, v in sorted(location_counts.items(), key=lambda x: -x[1])[:10]
    ])
    
    st.dataframe(
        location_df,
        use_container_width=True,
        hide_index=True,
        height=250
    )

# Footer
st.markdown("---")
st.info("💡 **Citizen Science Works!** Your observations help authorities respond faster and save lives. Thank you for being an Aqua Guardian!")
