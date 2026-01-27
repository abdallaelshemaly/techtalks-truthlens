"""
TruthLens - Main Streamlit Application
Entry point for the TruthLens dashboard.
"""

import streamlit as st
from components.sidebar import render_sidebar
from utils.style import apply_custom_style

# Apply custom styles
apply_custom_style()

# Configure page
st.set_page_config(
    page_title="TruthLens - Media Verification",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar and get selected page
page = render_sidebar()

# Main content routing
if page == "home":
    from pages.home import render_home
    render_home()
elif page == "upload":
    from pages.upload import render_upload
    render_upload()
elif page == "history":
    from pages.history import render_history
    render_history()
elif page == "settings":
    from pages.settings import render_settings
    render_settings()
else:
    # Fallback to home
    from pages.home import render_home
    render_home()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🔍 TruthLens v1.0.0 | AI-Powered Media Verification Platform</p>
    <p>⚠️ This tool is for decision support only. Always verify critical information through multiple sources.</p>
</div>
""", unsafe_allow_html=True)