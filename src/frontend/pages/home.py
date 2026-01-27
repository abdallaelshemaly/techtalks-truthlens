"""
Home page for TruthLens dashboard.
"""

import streamlit as st
from components.header import render_header

def render_home():
    """Render home page."""
    
    render_header("🔍 TruthLens - AI-Powered Media Verification")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to TruthLens
        
        TruthLens is a multimodal AI dashboard designed to assist analysts, 
        media organizations, and security professionals in assessing the 
        authenticity of digital content.
        
        **How it works:**
        1. 📤 **Upload** an image for analysis
        2. 🔍 **Analyze** with our AI models
        3. 📊 **Review** detailed risk assessment
        4. 📄 **Download** comprehensive reports
        
        **⚠️ Important Note:** 
        TruthLens is a **decision-support system**, not an absolute "truth detector". 
        It aids but does not replace human analysis.
        """)
        
        st.warning("This is an MVP version. Advanced features are under development.")
    
    with col2:
        st.image(
            "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400",
            caption="Digital Verification",
            use_column_width=True
        )
    
    # Quick actions
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Start New Analysis", type="primary", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    
    with col2:
        if st.button("📚 View Documentation", use_container_width=True):
            st.info("Documentation will be available in the next sprint")
    
    with col3:
        if st.button("🎥 Watch Tutorial", use_container_width=True):
            st.info("Tutorial videos will be available in the next sprint")
    
    # Stats/Info section
    st.markdown("---")
    st.markdown("### 📈 Platform Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Images Analyzed", "1,247", "+12%")
    
    with col2:
        st.metric("Avg. Processing Time", "2.3s", "-0.5s")
    
    with col3:
        st.metric("Accuracy Rate", "94%", "+2%")