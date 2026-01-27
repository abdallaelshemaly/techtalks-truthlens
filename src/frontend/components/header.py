"""
Header component for TruthLens dashboard.
"""

import streamlit as st

def render_header(page_title):
    """Render page header."""
    
    st.markdown(f"""
    <h1 style='text-align: center; color: #1E88E5; margin-bottom: 2rem;'>
        {page_title}
    </h1>
    """, unsafe_allow_html=True)