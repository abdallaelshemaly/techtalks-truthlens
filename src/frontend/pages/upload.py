"""
Upload page for TruthLens dashboard.
This appears as "Upload" in Streamlit's sidebar.
"""

import streamlit as st
from PIL import Image
import time
from components.header import render_header
from components.file_upload import file_uploader, display_image_info
from components.image_preview import preview_image

# Page configuration
st.set_page_config(
    page_title="Upload - TruthLens",
    page_icon="📤",
    layout="wide"
)

# Header
render_header("📤 Upload Image for Analysis")

# Information box
st.info("📋 Supported formats: JPG, PNG, JPEG | Max size: 10MB")

# Upload section
st.markdown("### Upload Your Image")

uploaded_file = file_uploader()

if uploaded_file is not None:
    try:
        # Load and display image
        image = Image.open(uploaded_file)
        
        # Display in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Image Preview")
            preview_options = preview_image(image)
        
        with col2:
            st.markdown("### Analysis Configuration")
            
            # Analysis options
            analysis_type = st.selectbox(
                "Select analysis type:",
                ["Standard Analysis", "Quick Scan", "Comprehensive Analysis"],
                help="Choose the depth of analysis"
            )
            
            # Detection options
            st.markdown("**Detection Options:**")
            col_a, col_b = st.columns(2)
            with col_a:
                detect_artifacts = st.checkbox("Visual Artifacts", value=True)
                check_metadata = st.checkbox("Metadata Analysis", value=True)
            with col_b:
                detect_ai = st.checkbox("AI Generation", value=True)
                check_compression = st.checkbox("Compression Patterns", value=False)
            
            # Output options
            st.markdown("**Output Options:**")
            generate_report = st.checkbox("Generate Detailed Report", value=True)
            save_history = st.checkbox("Save to History", value=True)
            
            # API endpoint
            st.markdown("---")
            st.markdown("**API Configuration:**")
            api_endpoint = st.text_input(
                "Backend Endpoint:",
                value="http://localhost:8000/api/analyze",
                disabled=True,
                help="Backend API endpoint for analysis"
            )
        
        # Display image info
        display_image_info(uploaded_file, image)
        
        # Analyze button
        st.markdown("---")
        analyze_col1, analyze_col2 = st.columns([3, 1])
        
        with analyze_col1:
            if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    # Simulate API call
                    time.sleep(2)
                    
                    # Display results
                    show_analysis_results()
        
        with analyze_col2:
            if st.button("🔄 Clear", type="secondary", use_container_width=True):
                st.rerun()
    
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        st.info("Please try uploading a different image file.")

def show_analysis_results():
    """Display mock analysis results."""
    
    st.success("✅ Image uploaded successfully! Analysis complete.")
    
    # Results section
    st.markdown("### 📊 Analysis Results")
    
    # Metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Risk Score", "32%", "-12%")
        st.progress(0.32)
    
    with col2:
        st.metric("Authenticity", "68%", "+8%")
        st.progress(0.68)
    
    with col3:
        st.metric("Confidence", "85%", "High")
        st.progress(0.85)
    
    with col4:
        st.metric("Processing Time", "2.1s", "Fast")
    
    # Detailed findings
    st.markdown("### 🔍 Detailed Findings")
    
    with st.expander("View Detailed Analysis", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ No Major Issues Found:**")
            st.write("- No obvious visual artifacts detected")
            st.write("- Metadata appears consistent")
            st.write("- Compression patterns look normal")
        
        with col2:
            st.markdown("**⚠️ Minor Concerns:**")
            st.write("- Slight JPEG compression artifacts")
            st.write("- Minor color inconsistencies in shadows")
            st.write("- Edge smoothness slightly above average")
    
    # Recommendations
    st.markdown("### 📋 Recommendations")
    st.info("""
    1. **Verify Source:** Check the original source of this image
    2. **Cross-reference:** Compare with other available sources
    3. **Context Check:** Consider the context in which this image is used
    4. **Expert Review:** For critical decisions, consult a human expert
    """)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate Report", use_container_width=True):
            st.info("Report generation will be implemented in Phase 2")
    
    with col2:
        if st.button("💾 Save Results", use_container_width=True):
            st.success("Results saved to history!")
            st.switch_page("pages/history.py")
    
    with col3:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.rerun()

# Sidebar content for this page
with st.sidebar:
    st.markdown("### 📤 Upload Tips")
    st.markdown("""
    1. Use clear, high-resolution images
    2. Avoid heavily compressed files
    3. Include original metadata if possible
    4. For best results, use images under 5MB
    """)
    
    st.markdown("---")
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")