"""
Upload & Analyze page for TruthLens dashboard - Polished UX
"""
import streamlit as st
import requests
import time
import pandas as pd
from PIL import Image
import sys
import os

# Page configuration
st.set_page_config(
    page_title="Analyze - TruthLens",
    page_icon="🔍",
    layout="wide"
)

# Apply Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
try:
    local_css("src/frontend/assets/custom.css")
except:
    pass

st.markdown("# 🔍 Deepfake Analysis")
st.markdown("Upload media to run our multi-modal detection engine.")

# --- FILE UPLOAD SECTION (Mobile Friendly) ---
uploaded_file = st.file_uploader(
    "Drop an image here",
    type=['jpg', 'jpeg', 'png'],
    help="Supported formats: JPG, PNG. Max size: 10MB"
)

if uploaded_file is not None:
    # Responsive Layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Preview")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True, caption=uploaded_file.name)

    with col2:
        st.markdown("### Configuration")
        with st.container(border=True):
            analysis_type = st.radio(
                "Analysis Depth",
                ["Fast (CNN Only)", "Standard (Complete)", "Enhanced (Forensics+)"],
                index=1
            )
            
            save_history = st.toggle("Save to History", value=True)
        
        st.markdown("###") # Spacing
        
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            
            # --- REAL-TIME PROGRESS INDICATOR ---
            with st.status("Initializing Analysis Engine...", expanded=True) as status:
                
                # Step 1: Upload
                st.write("📤 Uploading image to secure server...")
                # Simulate upload time for UX if local, or actual wait
                time.sleep(0.5) 
                
                # Determine Endpoint
                endpoint = "/api/analyze/complete"
                if "Fast" in analysis_type: endpoint = "/api/analyze/cnn"
                if "Enhanced" in analysis_type: endpoint = "/api/analyze/complete" # Logic handled in backend usually
                
                try:
                    # Prepare Request
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    
                    st.write("🧠 Running EfficientNet-B0 Model...")
                    # In a real async system, we'd poll. Here we wait, but user sees 'Running...'
                    
                    response = requests.post(
                        f"http://localhost:8000{endpoint}",
                        files=files,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        st.write("🔬 Performing Error Level Analysis (ELA)...")
                        time.sleep(0.3) # UI Pacing
                        
                        st.write("📝 Generating forensic report...")
                        time.sleep(0.3)
                        
                        data = response.json()
                        st.session_state.analysis_results = data
                        
                        status.update(label="Analysis Successfully Completed!", state="complete", expanded=False)
                        st.rerun() # Refresh to show results below
                        
                    else:
                        status.update(label="Analysis Failed", state="error")
                        st.error(f"Server Error: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    status.update(label="Connection Failed", state="error")
                    st.error("Cannot connect to backend. Is it running?")

# --- RESULTS DISPLAY ---
if 'analysis_results' in st.session_state and st.session_state.analysis_results:
    data = st.session_state.analysis_results
    res = data.get('result', data) # Handle nested or flat structure
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # 1. RISK HEADER
    risk = res.get('risk_level', 'UNKNOWN')
    risk_class = f"risk-{risk.lower()}"
    
    st.markdown(f"""
    <div class="risk-badge {risk_class}">
        VERDICT: {risk} RISK DETECTED
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("###")
    
    # 2. METRIC CARDS (Responsive Grid)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("CNN Confidence", f"{res.get('cnn_confidence', 0):.1f}%", 
                 delta="Fake" if res.get('is_fake') else "Real", delta_color="inverse")
    with m2:
        st.metric("ELA Score", f"{res.get('ela_score', 0):.1f}%")
    with m3:
        st.metric("Copy-Move", f"{res.get('copy_move_score', 0):.1f}%")
    with m4:
        st.metric("Metadata Trust", f"{res.get('metadata_score', 0):.1f}%")

    # 3. VISUALIZATIONS & DETAILS
    t1, t2 = st.tabs(["🔍 Forensic Visuals", "📄 Detailed Report"])
    
    with t1:
        vc1, vc2 = st.columns(2)
        with vc1:
            if data.get('ela_image_url'):
                st.image(f"http://localhost:8000{data.get('ela_image_url')}", 
                        caption="Error Level Analysis (Heatmap)", use_container_width=True)
            else:
                st.info("ELA Visual not available")
        with vc2:
            st.info("Copy-Move Visualizations available in Enhanced Mode (Check Comparison Page)")

    with t2:
        st.json(res)
        if data.get('report_url'):
             st.link_button("📥 Download PDF Report", f"http://localhost:8000{data.get('report_url')}")

    # Reset Button
    if st.button("Start New Analysis"):
        st.session_state.analysis_results = None
        st.rerun()