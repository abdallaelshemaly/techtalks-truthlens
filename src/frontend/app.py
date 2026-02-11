"""  
TruthLens - Main Streamlit Application
Home page with navigation to Upload page
"""
import pandas as pd
import streamlit as st
import sys
import os
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
        'Get Help': 'https://github.com/abdallaelshemaly/techtalks-truthlens',
        'Report a bug': 'https://github.com/abdallaelshemaly/techtalks-truthlens/issues',
        'About': '''
        # TruthLens v1.0.0
        
        AI-Powered Media Verification Platform
        
        **Features:**
        - Image authenticity analysis
        - Risk assessment
        - Analysis history tracking
        - Detailed reports
        - Performance monitoring
        - Batch processing
        
        ⚠️ This tool is for decision support only.
        '''
    }
)

# Set up page navigation in sidebar
st.sidebar.title("📊 TruthLens Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "📤 Upload & Analyze", "📜 Analysis History", "📊 Performance", "⚙️ Settings"]  # ADDED
)

if page == "🏠 Home":
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
        
        **New Features:**
        - 📊 **Performance Dashboard** - Monitor system analytics
        - 📦 **Batch Processing** - Analyze multiple images at once
        - 📈 **Enhanced Visualizations** - Better forensic analysis
        
        **⚠️ Important Note:** 
        TruthLens is a **decision-support system**, not an absolute "truth detector". 
        It aids but does not replace human analysis.
        """)
        
        st.success("🚀 Enhanced features now available in v1.1!")

    # Quick actions
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📤 Start New Analysis", type="primary", use_container_width='stretch'):
            st.switch_page("pages/upload_analyze.py")

    with col2:
        if st.button("📊 Performance Dashboard", use_container_width=True):
            st.switch_page("src/frontend/app.py?page=📊 Performance")

    with col3:
        if st.button("📚 View Documentation", use_container_width=True):
            st.info("Documentation will be available in the next sprint")

    # Stats/Info section
    st.markdown("---")
    st.markdown("### 📈 Platform Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Images Analyzed", "1,247", "+12%")

    with col2:
        st.metric("Avg. Processing Time", "2.3s", "-0.5s")

    with col3:
        st.metric("Accuracy Rate", "94%", "+2%")

    with col4:
        st.metric("Fake Detection", "68%", "+5%")

elif page == "📤 Upload & Analyze":
    st.switch_page("pages/upload_analyze.py")
    
elif page == "📜 Analysis History":
    st.switch_page("pages/history.py")

elif page == "📊 Performance":
    try:
        # Try multiple import approaches
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'advanced'))
        
        # Try importing PerformanceMonitor
        try:
            from performance_monitor import PerformanceMonitor
            monitor = PerformanceMonitor()
            monitor.create_performance_dashboard()
        except ImportError:
            # Try importing performance_dashboard_page directly
            try:
                from performance_monitor import performance_dashboard_page
                performance_dashboard_page()
            except ImportError:
                # Try creating instance from module
                try:
                    import performance_monitor
                    if hasattr(performance_monitor, 'PerformanceMonitor'):
                        monitor = performance_monitor.PerformanceMonitor()
                        monitor.create_performance_dashboard()
                    elif hasattr(performance_monitor, 'performance_dashboard_page'):
                        performance_monitor.performance_dashboard_page()
                    else:
                        # Try to call the module directly
                        performance_monitor.create_performance_dashboard()
                except Exception as e:
                    raise ImportError(f"Cannot find PerformanceMonitor: {e}")
                    
    except Exception as e:
        st.error(f"⚠️ Performance dashboard error: {str(e)[:100]}")
        st.info("""
        The performance monitoring module exists but has issues.
        
        **Quick fixes:**
        1. Check if `src/advanced/performance_monitor.py` exists
        2. Make sure it has `PerformanceMonitor` class
        3. Or use the simplified version below
        """)
        
        # Show simplified version
        st.markdown("## 📊 Performance Dashboard (Simplified)")
        
        # Get basic stats from API
        try:
            import requests
            response = requests.get("http://localhost:8000/api/history", params={'limit': 100})
            if response.status_code == 200:
                data = response.json()
                if data and "history" in data:
                    history = data["history"]
                    total = len(history)
                    fake_count = sum(1 for h in history if h.get('is_fake'))
                    high_risk = sum(1 for h in history if h.get('risk_level') == 'HIGH')
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Analyses", total)
                    with col2:
                        st.metric("Fake Detected", fake_count)
                    with col3:
                        st.metric("High Risk", high_risk)
                    with col4:
                        if total > 0:
                            avg_cnn = sum(h.get('cnn_confidence', 0) for h in history) / total
                            st.metric("Avg CNN %", f"{avg_cnn:.1f}")
                        else:
                            st.metric("Avg CNN %", "0")
                    
                    # Show recent analyses
                    if history:
                        st.markdown("### Recent Analyses")
                        recent_df = pd.DataFrame(history[:5])
                        if not recent_df.empty:
                            # Select only relevant columns
                            display_cols = ['filename', 'timestamp', 'is_fake', 'cnn_confidence', 'risk_level']
                            display_cols = [c for c in display_cols if c in recent_df.columns]
                            st.dataframe(recent_df[display_cols], use_container_width=True)
        except Exception as api_error:
            st.error(f"API error: {api_error}") 
    
elif page == "⚙️ Settings":
    st.switch_page("pages/settings.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🔍 TruthLens v1.1.0 | AI-Powered Media Verification Platform</p>
    <p>📊 Now with Performance Monitoring & Batch Processing</p>
    <p>⚠️ This tool is for decision support only. Always verify critical information through multiple sources.</p>
</div>
""", unsafe_allow_html=True)