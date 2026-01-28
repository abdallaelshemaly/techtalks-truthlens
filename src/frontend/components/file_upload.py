"""
File upload component for TruthLens dashboard.
"""  

import streamlit as st
from PIL import Image
import io

def file_uploader():
    """Render file uploader and return uploaded file."""
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png'],
        help="Upload an image for authenticity analysis. Max size: 10MB"
    )
    
    return uploaded_file

def display_image_info(uploaded_file, image):
    """Display image information."""
    
    if uploaded_file and image:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 File Details:**")
            st.write(f"**Name:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        
        with col2:
            st.markdown("**🖼️ Image Details:**")
            st.write(f"**Format:** {image.format}")
            st.write(f"**Dimensions:** {image.size[0]} x {image.size[1]}")
            st.write(f"**Mode:** {image.mode}")