""" 
TruthLens - Main Streamlit Application
Home page for the TruthLens dashboard.
"""

import streamlit as st
from utils.style import apply_custom_style

# Apply custom styles
apply_custom_style()

# Configure page
st.set_page_config(
    page_title="TruthLens - Media Verification",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/truthlens',
        'Report a bug': 'https://github.com/your-repo/truthlens/issues',
        'About': '''
        # TruthLens v1.0.0
        
        AI-Powered Media Verification Platform
        
        **Features:**
        - Image authenticity analysis
        - Risk assessment
        - Analysis history tracking
        - Detailed reports
        
        ⚠️ This tool is for decision support only.
        '''
    }
)

# Hero section
st.markdown("""
    <h1 style='text-align: center; color: #1E88E5; margin-bottom: 2rem;'>
        🔍 TruthLens - AI-Powered Media Verification
    </h1>
""", unsafe_allow_html=True)

# Two-column layout
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
        width=400  # Fixed: specify pixel width or use 'stretch'
    )

# Quick actions
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Start New Analysis", type="primary", use_container_width=True):
        st.switch_page("pages/upload.py")

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

# About section in sidebar
with st.sidebar:
    st.markdown("### About TruthLens")
    st.markdown("""
    AI-powered media verification platform.
    
    **Current Features:**
    - Image upload and preview
    - Basic authenticity analysis
    - Analysis history
    
    **Coming Soon:**
    - Deepfake detection
    - Text analysis
    - API integration
    """)
    
    st.markdown("---")
    st.markdown("**Version:** 1.0.0")
    st.markdown("**Status:** MVP Development")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🔍 TruthLens v1.0.0 | AI-Powered Media Verification Platform</p>
    <p>⚠️ This tool is for decision support only. Always verify critical information through multiple sources.</p>
</div>
""", unsafe_allow_html=True)