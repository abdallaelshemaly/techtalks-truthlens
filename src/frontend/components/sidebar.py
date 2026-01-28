"""
Optional sidebar component for additional content.
Not needed for navigation anymore.
"""

import streamlit as st

def render_additional_sidebar():
    """Render additional sidebar content if needed."""
    
    with st.sidebar:
        st.markdown("### Quick Stats")
        st.markdown("""
        - **Active Users:** 128
        - **Today's Analyses:** 24
        - **Avg. Risk Score:** 38%
        - **System Status:** 🟢 Online
        """)
        
        st.markdown("---")
        st.markdown("### Quick Links")
        
        if st.button("📋 View Documentation", use_container_width=True):
            st.info("Documentation coming soon!")
        
        if st.button("🐛 Report Bug", use_container_width=True):
            st.info("Bug reporting coming soon!")