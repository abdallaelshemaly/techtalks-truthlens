"""
Style utilities for TruthLens dashboard.
"""

import streamlit as st

def apply_custom_style():
    """Apply custom CSS styles to the dashboard."""
    
    custom_css = """
    <style>
    /* Main styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1E88E5;
    }
    
    /* Cards */
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1E88E5;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 8px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)