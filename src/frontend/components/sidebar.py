"""
Sidebar component for TruthLens dashboard.
"""

import streamlit as st

def render_sidebar():
    """Render the sidebar and return selected page."""
    
    with st.sidebar:
        st.title("🔍 TruthLens")
        st.markdown("---")
        st.markdown("### Navigation")
        
        # Navigation with session state
        if 'page' not in st.session_state:
            st.session_state.page = "home"
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = "home"
        with col2:
            if st.button("📤 Upload", use_container_width=True):
                st.session_state.page = "upload"
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("📊 History", use_container_width=True):
                st.session_state.page = "history"
        with col4:
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.page = "settings"
        
        st.markdown("---")
        st.markdown("### About TruthLens")
        st.markdown("""
        AI-powered media verification platform.
        
        **Current Features:**
        - Image upload and preview
        - Basic authenticity analysis
        
        **Coming Soon:**
        - Deepfake detection
        - Text analysis
        """)
        
        st.markdown("---")
        st.markdown("**Version:** 1.0.0")
        st.markdown("**Status:** MVP Development")
    
    return st.session_state.page