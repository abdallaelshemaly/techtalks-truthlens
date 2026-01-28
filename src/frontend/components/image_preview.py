"""
Image preview component for TruthLens dashboard.
"""

import streamlit as st
from PIL import Image

def preview_image(image, caption="Uploaded Image"):
    """Display image preview with optional enhancements."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(
            image,
            caption=caption,
            width=600  # Fixed: specify pixel width or use 'stretch'
        )
    
    with col2:
        # Image enhancement options
        st.markdown("**🛠️ Preview Options:**")
        
        show_histogram = st.checkbox("Show Histogram", value=False)
        enhance_contrast = st.checkbox("Enhance Contrast", value=False)
        show_edges = st.checkbox("Show Edge Detection", value=False)
        
        if show_histogram:
            st.info("Histogram visualization will be implemented in Phase 2")
        if enhance_contrast:
            st.info("Contrast enhancement will be implemented in Phase 2")
        if show_edges:
            st.info("Edge detection will be implemented in Phase 2")
    
    return {
        'show_histogram': show_histogram,
        'enhance_contrast': enhance_contrast,
        'show_edges': show_edges
    }