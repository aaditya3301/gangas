"""
Shared UI Components and Styling
Consistent design system across all pages
"""

def get_common_css():
    """Return common CSS styling for all pages"""
    return """
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
        header {visibility: hidden;}
        
        /* Main container background */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Page title styling */
        .page-title {
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            padding: 1.5rem 0 0.5rem 0;
            margin-bottom: 0;
            animation: gradientShift 5s ease infinite;
            letter-spacing: -1px;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .page-subtitle {
            text-align: center;
            color: #495057;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            font-weight: 500;
            letter-spacing: 1px;
            opacity: 0.9;
        }
        
        /* Enhanced metric cards */
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
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            background-size: 200% 100%;
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { background-position: -200% 0; }
            50% { background-position: 200% 0; }
        }
        
        .metric-card:hover {
            transform: translateY(-5px) scale(1.01);
            box-shadow: 0 15px 45px rgba(102, 126, 234, 0.25);
        }
        
        /* Section headers */
        .section-header {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
            margin: 2rem 0 1.5rem 0;
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
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
        }
        
        /* Alert boxes */
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
        
        .alert-high {
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
        
        .alert-low {
            background: linear-gradient(135deg, rgba(40, 167, 69, 0.15) 0%, rgba(92, 184, 92, 0.15) 100%);
            border-left: 5px solid #28a745;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 5px 20px rgba(40, 167, 69, 0.2);
        }
        
        /* Enhanced buttons */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: none;
            padding: 1rem 2.5rem;
            border-radius: 15px;
            font-weight: 700;
            font-size: 1rem;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
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
        
        /* Data containers */
        div[data-testid="stDataFrame"], div[data-testid="stTable"] {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-radius: 10px;
            font-weight: 600;
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
        }
        
        /* Sidebar selectbox styling */
        section[data-testid="stSidebar"] .stSelectbox > div > div {
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
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: #2c3e50 !important;
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
        
        /* Metric containers */
        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
        }
        
        /* Success/Info/Warning/Error boxes */
        .stSuccess {
            background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(92, 184, 92, 0.1)) !important;
            border-radius: 15px !important;
            border-left: 5px solid #28a745 !important;
            box-shadow: 0 5px 20px rgba(40, 167, 69, 0.1) !important;
        }
        
        .stInfo {
            background: linear-gradient(135deg, rgba(23, 162, 184, 0.1), rgba(102, 126, 234, 0.1)) !important;
            border-radius: 15px !important;
            border-left: 5px solid #17a2b8 !important;
            box-shadow: 0 5px 20px rgba(23, 162, 184, 0.1) !important;
        }
        
        .stWarning {
            background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(253, 126, 20, 0.1)) !important;
            border-radius: 15px !important;
            border-left: 5px solid #ffc107 !important;
            box-shadow: 0 5px 20px rgba(255, 193, 7, 0.1) !important;
        }
        
        .stError {
            background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(255, 65, 108, 0.1)) !important;
            border-radius: 15px !important;
            border-left: 5px solid #dc3545 !important;
            box-shadow: 0 5px 20px rgba(220, 53, 69, 0.1) !important;
        }
        
        /* Loading animation */
        .stSpinner > div {
            border-top-color: #667eea !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            border-radius: 10px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Slider */
        .stSlider > div > div > div > div {
            background-color: #667eea;
        }
        
        /* Radio buttons */
        .stRadio > div {
            gap: 10px;
        }
        
        /* Checkbox */
        .stCheckbox > label > div {
            border-color: #667eea;
        }
    </style>
    """


def page_header(icon, title, subtitle=""):
    """Create consistent page header"""
    import streamlit as st
    st.markdown(f'<p class="page-title">{icon} {title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)


def section_header(title):
    """Create section header"""
    import streamlit as st
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)


def metric_card(icon, label, value, sublabel=""):
    """Create a metric card"""
    return f"""
    <div class="metric-card">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
        <h4 style="margin:0; color: #6c757d; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">{label}</h4>
        <h1 style="margin:0.5rem 0; font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</h1>
        {f'<p style="margin:0; color: #6c757d; font-weight: 500;">{sublabel}</p>' if sublabel else ''}
    </div>
    """
