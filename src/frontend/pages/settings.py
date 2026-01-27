"""
Settings page for TruthLens dashboard.
"""

import streamlit as st
from components.header import render_header

def render_settings():
    """Render settings page."""
    
    render_header("⚙️ Settings")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "General", "Analysis", "API", "Appearance"
    ])
    
    with tab1:
        st.markdown("### General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            upload_folder = st.text_input(
                "Default Upload Folder",
                value="./uploads",
                help="Folder where uploaded files are temporarily stored"
            )
            
            max_file_size = st.number_input(
                "Max File Size (MB)",
                min_value=1,
                max_value=100,
                value=10,
                help="Maximum file size for uploads"
            )
        
        with col2:
            default_analysis = st.selectbox(
                "Default Analysis Mode",
                ["Standard", "Quick", "Detailed"],
                index=0,
                help="Default analysis mode for new uploads"
            )
            
            auto_save = st.checkbox(
                "Auto-save analysis history",
                value=True,
                help="Automatically save all analyses to history"
            )
        
        # Notifications
        st.markdown("#### Notifications")
        email_notifications = st.checkbox("Email notifications", value=False)
        
        if email_notifications:
            email_address = st.text_input("Email Address", value="user@example.com")
    
    with tab2:
        st.markdown("### Analysis Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Detection Options")
            
            enable_artifact = st.checkbox("Enable artifact detection", value=True)
            enable_ai = st.checkbox("Enable AI generation detection", value=True)
            enable_metadata = st.checkbox("Enable metadata analysis", value=True)
            enable_compression = st.checkbox("Enable compression analysis", value=False)
        
        with col2:
            st.markdown("#### Performance")
            
            processing_priority = st.select_slider(
                "Processing Priority",
                options=["Fast", "Balanced", "Thorough"],
                value="Balanced"
            )
            
            cache_analysis = st.checkbox(
                "Cache analysis results",
                value=True,
                help="Cache results for faster repeated analysis"
            )
        
        # Confidence thresholds
        st.markdown("#### Confidence Thresholds")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            low_risk_threshold = st.slider(
                "Low Risk Threshold",
                min_value=0,
                max_value=100,
                value=30,
                help="Below this value is considered low risk"
            )
        
        with col2:
            medium_risk_threshold = st.slider(
                "Medium Risk Threshold",
                min_value=0,
                max_value=100,
                value=70,
                help="Between low and this value is medium risk"
            )
        
        with col3:
            high_risk_threshold = st.slider(
                "High Risk Threshold",
                min_value=0,
                max_value=100,
                value=85,
                help="Above this value is high risk"
            )
    
    with tab3:
        st.markdown("### API Configuration")
        
        st.markdown("#### Backend API")
        
        api_url = st.text_input(
            "API Base URL",
            value="http://localhost:8000",
            help="Base URL for the backend API"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_endpoint = st.text_input(
                "Analysis Endpoint",
                value="/api/analyze",
                help="Endpoint for image analysis"
            )
        
        with col2:
            history_endpoint = st.text_input(
                "History Endpoint",
                value="/api/history",
                help="Endpoint for analysis history"
            )
        
        # API Timeout
        api_timeout = st.number_input(
            "API Timeout (seconds)",
            min_value=5,
            max_value=120,
            value=30,
            help="Timeout for API requests"
        )
        
        # Test connection
        st.markdown("---")
        if st.button("Test API Connection", type="secondary"):
            with st.spinner("Testing connection..."):
                time.sleep(1)
                st.success("✅ Connection successful (mock test)")
    
    with tab4:
        st.markdown("### Appearance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Theme",
                ["Light", "Dark", "Auto"],
                index=0,
                help="Dashboard color theme"
            )
            
            color_scheme = st.selectbox(
                "Color Scheme",
                ["Blue", "Green", "Purple", "Red", "Orange"],
                index=0,
                help="Primary color scheme"
            )
        
        with col2:
            font_size = st.slider(
                "Font Size",
                min_value=12,
                max_value=24,
                value=16,
                help="Base font size"
            )
            
            density = st.select_slider(
                "UI Density",
                options=["Compact", "Comfortable", "Spacious"],
                value="Comfortable"
            )
        
        # Preview
        st.markdown("#### Preview")
        st.info("Changes will take effect after restarting the dashboard.")
    
    # Save/Cancel buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            st.success("Settings saved successfully! (mock action)")
        
        if st.button("🔄 Reset to Defaults", type="secondary", use_container_width=True):
            st.warning("This will reset all settings to default values.")
            if st.checkbox("Confirm reset"):
                st.info("Settings reset to defaults (mock action)")