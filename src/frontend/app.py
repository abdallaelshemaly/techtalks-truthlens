"""  
TruthLens - Main Application
Professional UI Update
"""
import streamlit as st
import sys
import os

# Apply CSS immediately
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Configure page
st.set_page_config(
    page_title="TruthLens AI",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
try:
    local_css("src/frontend/assets/custom.css")
except:
    pass

# Sidebar Navigation
st.sidebar.markdown("## 👁️ TruthLens")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📤 Analyze", "⚖️ Compare", "📜 History", "📊 Performance", "⚙️ Settings"]
)

# Routing
if page == "🏠 Home":
    st.markdown("""
    # Welcome to TruthLens
    ### The Professional Deepfake Detection Platform
    
    TruthLens uses advanced **CNNs** and **Forensic Analysis** to detect manipulated media.
    
    #### 🚀 New Features in v2.0
    * **Comparison Mode:** Compare original vs suspect images side-by-side.
    * **Real-time Progress:** Live feedback during analysis.
    * **Mobile Optimized:** Full functionality on any device.
    
    """)
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### 📤 Quick Analysis")
            st.markdown("Upload a single image for immediate forensic breakdown.")
            if st.button("Go to Analyze"):
                st.switch_page("pages/upload_analyze.py")
                
    with c2:
        with st.container(border=True):
            st.markdown("#### ⚖️ Compare Images")
            st.markdown("Analyze two images side-by-side to find discrepancies.")
            if st.button("Go to Comparison"):
                st.switch_page("pages/comparison.py")

elif page == "📤 Analyze":
    st.switch_page("pages/upload_analyze.py")

elif page == "⚖️ Compare":
    st.switch_page("pages/comparison.py")
    
elif page == "📜 History":
    st.switch_page("pages/history.py")

elif page == "📊 Performance":
    # (Existing performance logic here, simplified for brevity)
    st.switch_page("src/frontend/app.py?page=📊 Performance") 
    # Note: In a real structure, Performance should likely be its own page file 
    # but sticking to your structure, you might just run the monitor here:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'advanced'))
    try:
        from performance_monitor import performance_dashboard_page
        performance_dashboard_page()
    except ImportError:
        st.error("Performance module not found.")

elif page == "⚙️ Settings":
    st.switch_page("pages/settings.py")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("v2.1.0 | Professional Edition")