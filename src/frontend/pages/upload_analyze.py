"""
Upload & Analyze page for TruthLens dashboard with Complete Analysis Results
This replaces the old upload.py with real backend integration
"""
import streamlit as st
import requests
import time
import pandas as pd
from PIL import Image
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.api_client import TruthLensAPIClient
from components.header import render_header

# Page configuration
st.set_page_config(
    page_title="Upload & Analyze - TruthLens",
    page_icon="📤",
    layout="wide"
)

# Initialize API client
api_client = TruthLensAPIClient(base_url="http://localhost:8000")

# Header
render_header("📤 Upload & Analyze Images")

# Custom CSS
st.markdown("""
<style>
    /* Risk level indicators */
    .risk-high {
        color: #dc3545;
        font-weight: bold;
        background-color: #f8d7da;
        padding: 8px 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 1.2em;
    }
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
        background-color: #fff3cd;
        padding: 8px 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 1.2em;
    }
    .risk-low {
        color: #28a745;
        font-weight: bold;
        background-color: #d4edda;
        padding: 8px 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 1.2em;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    /* Progress bar colors */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1E88E5 0%, #1565C0 100%);
    }
    
    /* Visualization container */
    .visualization-container {
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("Upload an image for comprehensive deepfake detection analysis using CNN and forensic methods.")

# Session state initialization
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'processing_time' not in st.session_state:
    st.session_state.processing_time = 0
if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = None
if 'analysis_type' not in st.session_state:
    st.session_state.analysis_type = "complete"

# Sidebar - Quick Stats and History
with st.sidebar:
    st.markdown("### 📊 Quick Stats")
    
    # Try to load history for stats
    try:
        history_data = api_client.get_history(limit=50)
        if history_data and "history" in history_data:
            history = history_data["history"]
            total_analyses = len(history)
            high_risk = sum(1 for h in history if h.get("enhanced_risk_level", h.get("risk_level")) == "HIGH")
            fake_detected = sum(1 for h in history if h.get("is_fake") == True)
            
            st.metric("Total Analyses", total_analyses)
            st.metric("High Risk Cases", high_risk)
            st.metric("Fake Detected", fake_detected)
        else:
            st.info("No analysis history yet")
    except:
        st.warning("Could not load statistics")
    
    st.markdown("---")
    st.markdown("### 🔄 Quick Actions")
    
    if st.button("🔄 Refresh Stats", use_container_width=True):
        st.rerun()
    
    if st.button("📜 View Full History", use_container_width=True):
        st.switch_page("pages/history.py")
    
    # Connection status
    st.markdown("---")
    if api_client.test_connection():
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Offline")
        st.info("Start backend with: python run_backend.py")

# Main content - File upload section
st.markdown("### 📁 Upload Image for Analysis")

# Use the existing file upload component
from components.file_upload import file_uploader
uploaded_file = file_uploader()

if uploaded_file is not None:
    # Store filename in session state
    st.session_state.uploaded_filename = uploaded_file.name
    
    # Display uploaded image in columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📷 Image Preview")
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"**Original Image:** {uploaded_file.name}", use_container_width=True)
            
            # Image info using existing component
            from components.file_upload import display_image_info
            display_image_info(uploaded_file, image)
            
        except Exception as e:
            st.error(f"Error loading image: {e}")
    
    with col2:
        st.markdown("### ⚙️ Analysis Settings")
        
        # Analysis type with enhanced option
        analysis_type = st.selectbox(
            "**Analysis Mode**",
            [
                "Complete Analysis (CNN + Forensics)", 
                "Enhanced Forensics (With Visualizations)",
                "CNN Analysis Only", 
                "Forensic Analysis Only"
            ],
            help="Choose the type of analysis to perform"
        )
        
        st.markdown("---")
        st.markdown("**Additional Options:**")
        
        # Additional options
        generate_report = st.checkbox("📄 Generate Detailed Report", value=True)
        save_to_history = st.checkbox("💾 Save to History", value=True)
        
        # Analysis button
        if st.button("🔍 Start Deepfake Analysis", type="primary", use_container_width='stretch'):
            with st.spinner("🔬 Analyzing image with AI models... This may take 10-30 seconds."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Choose endpoint based on analysis type
                    if analysis_type == "Enhanced Forensics (With Visualizations)":
                        endpoint = "/api/analyze/enhanced-forensics"
                    elif analysis_type == "CNN Analysis Only":
                        endpoint = "/api/analyze/cnn"
                    elif analysis_type == "Forensic Analysis Only":
                        endpoint = "/api/analyze/forensics"
                    else:
                        endpoint = "/api/analyze/complete"
                    
                    # Send request
                    start_time = time.time()
                    
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(
                        f"http://localhost:8000{endpoint}",
                        files=files,
                        timeout=60  # Increased timeout for enhanced analysis
                    )
                    processing_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Store results in session state
                        st.session_state.analysis_results = data
                        st.session_state.processing_time = processing_time
                        
                        # Determine analysis type for display
                        if "enhanced-forensics" in endpoint:
                            st.session_state.analysis_type = "enhanced_forensic"
                        elif "cnn" in endpoint:
                            st.session_state.analysis_type = "cnn"
                        elif "forensics" in endpoint:
                            st.session_state.analysis_type = "forensic"
                        else:
                            st.session_state.analysis_type = "complete"
                        
                        # Show success message
                        st.success(f"✅ Analysis complete in {processing_time:.1f} seconds!")
                        
                        # Force rerun to show results
                        st.rerun()
                    else:
                        st.error(f"❌ Analysis failed (HTTP {response.status_code})")
                        st.code(response.text, language="json")
                        
                except requests.exceptions.ConnectionError:
                    st.error("""
                    ❌ Cannot connect to backend server!
                    
                    **Please make sure:**
                    1. The FastAPI server is running
                    2. It's running on port 8000
                    3. You can access http://localhost:8000
                    
                    **Start the backend with:**
                    ```bash
                    python run_backend.py
                    ```
                    """)
                except requests.exceptions.Timeout:
                    st.error("⏰ Analysis timed out. The server took too long to respond.")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")

# Function to display enhanced forensic results
def display_enhanced_forensic_results(data, processing_time):
    """Display enhanced forensic analysis with visualizations"""
    
    result = data.get("result", {})
    if not result:
        result = data  # Fallback if result is not nested
    
    # Enhanced Risk Level
    risk_level = result.get("enhanced_risk_level", result.get("risk_level", "UNKNOWN")).upper()
    
    # Risk display with icon
    if risk_level == "HIGH":
        risk_html = '<span class="risk-high">🔴 HIGH RISK</span>'
        risk_icon = "🔴"
        risk_description = "Strong evidence of manipulation detected"
    elif risk_level == "MEDIUM":
        risk_html = '<span class="risk-medium">🟡 MEDIUM RISK</span>'
        risk_icon = "🟡"
        risk_description = "Moderate evidence of possible manipulation"
    else:
        risk_html = '<span class="risk-low">🟢 LOW RISK</span>'
        risk_icon = "🟢"
        risk_description = "Minimal evidence of manipulation"
    
    # Header with risk level
    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
    with col_header1:
        st.markdown(f"### {risk_icon} Enhanced Forensic Analysis")
        st.markdown(f"**{risk_description}**")
    with col_header2:
        st.markdown(f"**Risk Level:**")
        st.markdown(risk_html, unsafe_allow_html=True)
    with col_header3:
        st.markdown(f"**Processing Time:**")
        st.markdown(f"**{processing_time:.1f} seconds**")
    
    # Enhanced metrics in columns
    st.markdown("### 🔬 Enhanced Forensic Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        ela_original = result.get("ela_score", 0)
        ela_enhanced = result.get("ela_enhanced_score", ela_original)
        st.metric(
            "ELA Analysis",
            f"{ela_enhanced:.1f}%",
            f"Original: {ela_original:.1f}%" if ela_original != ela_enhanced else ""
        )
        st.progress(ela_enhanced / 100, text=f"Enhanced ELA: {ela_enhanced:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        cm_original = result.get("copy_move_score", 0)
        cm_enhanced = result.get("copy_move_enhanced_score", cm_original)
        st.metric(
            "Copy-Move Detection",
            f"{cm_enhanced:.1f}%",
            f"Original: {cm_original:.1f}%" if cm_original != cm_enhanced else ""
        )
        st.progress(cm_enhanced / 100, text=f"Enhanced Copy-Move: {cm_enhanced:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        meta_score = result.get("metadata_score", 0)
        st.metric(
            "Metadata",
            f"{meta_score:.1f}%",
            "Consistency Score"
        )
        st.progress(meta_score / 100, text=f"Metadata: {meta_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        combined_score = result.get("enhanced_combined_risk", result.get("combined_risk", 0))
        st.metric(
            "Combined Risk",
            f"{combined_score:.1f}%",
            "Enhanced Assessment"
        )
        st.progress(combined_score / 100, text=f"Combined Risk: {combined_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations Section
    st.markdown("### 🎨 Forensic Visualizations")
    
    # ELA Overlay Visualization
    ela_overlay_url = result.get("ela_overlay_url")
    if ela_overlay_url:
        st.markdown("#### 🔥 ELA Heatmap Overlay")
        col_ela1, col_ela2 = st.columns([3, 2])
        with col_ela1:
            try:
                full_url = f"http://localhost:8000{ela_overlay_url}"
                st.image(full_url, caption="ELA Heatmap Overlay - Red/orange areas indicate compression inconsistencies", 
                        use_container_width=True)
            except:
                st.info("ELA overlay could not be loaded.")
        
        with col_ela2:
            st.markdown("""
            **What the heatmap shows:**
            - **Red/Orange:** High compression differences
            - **Yellow/Green:** Moderate differences  
            - **Blue:** Minimal differences
            - **Pattern recognition:** Look for unnatural edges/patterns
            """)
    
    # Copy-Move Visualization
    cm_visual_url = result.get("copy_move_visual_url")
    if cm_visual_url:
        st.markdown("#### 🔍 Copy-Move Detection")
        col_cm1, col_cm2 = st.columns([3, 2])
        with col_cm1:
            try:
                full_url = f"http://localhost:8000{ela_overlay_url}"
                st.image(full_url, caption="Copy-Move Detection - Red/blue circles show suspected duplicate regions", 
                        use_container_width=True)
            except:
                st.info("Copy-move visualization could not be loaded.")
        
        with col_cm2:
            st.markdown("""
            **What the markers show:**
            - **Red circles:** Source regions
            - **Blue circles:** Duplicated regions
            - **Connecting lines:** Matching feature points
            - **Clustered markers:** Indicate copy-move tampering
            """)
    
    if not ela_overlay_url and not cm_visual_url:
        st.info("Visualizations were not generated for this analysis. Try 'Enhanced Forensics' mode.")
    
    # Enhanced Algorithm Details
    st.markdown("### ⚡ Enhanced Algorithm Features")
    
    with st.expander("📊 Algorithm Improvements", expanded=False):
        st.markdown("""
        **Enhanced Detection Methods:**
        
        1. **Improved ELA Algorithm:**
           - Better compression level detection
           - Adaptive thresholding
           - Noise reduction filtering
        
        2. **Advanced Copy-Move Detection:**
           - Increased feature points (1500 vs 1000)
           - Better distance threshold (0.12 vs 0.10)
           - Enhanced scoring multiplier (3.5x vs 10x)
        
        3. **Visualization Generation:**
           - Heatmap overlays for ELA
           - Point-to-point matching for copy-move
           - Real-time processing optimization
        """)
    
    # Recommendations based on risk level
    st.markdown("### 💡 Recommendations & Next Steps")
    
    if risk_level == "HIGH":
        st.warning("""
        **⚠️ CRITICAL - High Manipulation Probability Detected**
        
        **Immediate Actions:**
        1. **Do not use** this image for authentication or verification
        2. **Verify original source** through independent channels
        3. **Contact subject matter experts** for manual review
        4. **Document all findings** for evidence preservation
        """)
    elif risk_level == "MEDIUM":
        st.info("""
        **📝 MODERATE RISK - Further Verification Required**
        
        **Recommended Actions:**
        1. **Cross-reference** with other available sources
        2. **Verify image context** and provenance
        3. **Use with caution** in professional contexts
        4. **Consider manual inspection** if decision-critical
        """)
    else:
        st.success("""
        **✅ LOW RISK - Appears Authentic**
        
        **Standard Protocol:**
        1. **Standard verification** protocols are sufficient
        2. **Maintain normal** digital security practices
        3. **Always verify** critical information through multiple sources
        """)
    
    # Action buttons
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔄 New Analysis", use_container_width='stretch'):
            st.session_state.analysis_results = None
            st.session_state.uploaded_filename = None
            st.rerun()
    
    with col_btn2:
        if st.button("📜 View History", use_container_width='stretch'):
            st.switch_page("pages/history.py")
    
    with col_btn3:
        if st.button("🏠 Back to Home", use_container_width='stretch'):
            st.switch_page("app.py")

# Function to display complete results (keep original for backward compatibility)
def display_complete_results(data, processing_time):
    """Display complete analysis results with CNN and forensic data."""
    
    result = data.get("result", {})
    if not result:
        result = data  # Fallback if result is not nested
    
    # Overall Risk Level
    risk_level = result.get("risk_level", "UNKNOWN").upper()
    
    # Risk display with icon
    if risk_level == "HIGH":
        risk_html = '<span class="risk-high">🔴 HIGH RISK</span>'
        risk_icon = "🔴"
        risk_description = "Strong evidence of manipulation detected"
    elif risk_level == "MEDIUM":
        risk_html = '<span class="risk-medium">🟡 MEDIUM RISK</span>'
        risk_icon = "🟡"
        risk_description = "Moderate evidence of possible manipulation"
    else:
        risk_html = '<span class="risk-low">🟢 LOW RISK</span>'
        risk_icon = "🟢"
        risk_description = "Minimal evidence of manipulation"
    
    # Header with risk level
    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
    with col_header1:
        st.markdown(f"### {risk_icon} Overall Risk Assessment")
        st.markdown(f"**{risk_description}**")
    with col_header2:
        st.markdown(f"**Risk Level:**")
        st.markdown(risk_html, unsafe_allow_html=True)
    with col_header3:
        st.markdown(f"**Processing Time:**")
        st.markdown(f"**{processing_time:.1f} seconds**")
    
    # Main metrics in columns
    st.markdown("### 📈 Analysis Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        is_fake = result.get("is_fake", False)
        cnn_conf = result.get("cnn_confidence", 0)
        st.metric(
            "CNN Prediction",
            "FAKE" if is_fake else "REAL",
            f"{cnn_conf:.1f}% confidence"
        )
        # CNN Progress bar
        st.progress(cnn_conf / 100, text=f"CNN Confidence: {cnn_conf:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        ela_score = result.get("ela_score", 0)
        st.metric(
            "ELA Analysis",
            f"{ela_score:.1f}%",
            "Tampering Indicator"
        )
        st.progress(ela_score / 100, text=f"ELA Score: {ela_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        meta_score = result.get("metadata_score", 0)
        st.metric(
            "Metadata",
            f"{meta_score:.1f}%",
            "Consistency Score"
        )
        st.progress(meta_score / 100, text=f"Metadata: {meta_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        copy_score = result.get("copy_move_score", 0)
        st.metric(
            "Copy-Move",
            f"{copy_score:.1f}%",
            "Duplication Detection"
        )
        st.progress(copy_score / 100, text=f"Copy-Move: {copy_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Forensic Breakdown
    st.markdown("### 🔍 Detailed Forensic Analysis")
    
    forensic_col1, forensic_col2 = st.columns(2)
    
    with forensic_col1:
        with st.expander("📊 Forensic Scores Breakdown", expanded=True):
            # Create a mini dataframe for forensic scores
            forensic_data = pd.DataFrame({
                "Method": ["Error Level Analysis", "Metadata Analysis", "Copy-Move Detection"],
                "Score": [
                    result.get("ela_score", 0),
                    result.get("metadata_score", 0),
                    result.get("copy_move_score", 0)
                ],
                "Interpretation": [
                    "Detects compression inconsistencies",
                    "Checks for editing software traces",
                    "Identifies duplicated regions"
                ]
            })
            
            for idx, row in forensic_data.iterrows():
                st.markdown(f"**{row['Method']}:** {row['Score']:.1f}%")
                st.progress(row['Score'] / 100)
                st.caption(row['Interpretation'])
                if idx < len(forensic_data) - 1:
                    st.markdown("---")
    
    with forensic_col2:
        with st.expander("📋 Score Interpretation Guide", expanded=False):
            st.markdown("""
            **Score Interpretation:**
            - **0-30%:** Low probability of manipulation
            - **31-70%:** Moderate probability - requires further review
            - **71-100%:** High probability of manipulation
            
            **Method Details:**
            - **ELA:** Analyzes JPEG compression levels for inconsistencies
            - **Metadata:** Examines EXIF data for editing software traces
            - **Copy-Move:** Detects duplicated or cloned regions
            """)
    
    # ELA Image Visualization
    ela_url = data.get("ela_image_url")
    if ela_url:
        st.markdown("### 🔬 Error Level Analysis Visualization")
        
        col_ela1, col_ela2 = st.columns([3, 2])
        with col_ela1:
            try:
                full_url = f"http://localhost:8000{ela_url}"
                st.image(full_url, caption="ELA Visualization - Brighter areas indicate higher tampering likelihood", 
                        use_container_width=True)
            except:
                st.info("ELA image could not be loaded. Check if the file exists.")
        
        with col_ela2:
            st.markdown("""
            **Understanding ELA:**
            
            Error Level Analysis highlights areas where compression
            levels differ from the rest of the image.
            
            **What to look for:**
            - **Uniform brightness:** Likely authentic
            - **Patchy bright areas:** Possible local edits
            - **Sharp bright edges:** Indicates object insertion/removal
            """)
    
    # Enhanced features check
    ela_enhanced = result.get("ela_enhanced_score")
    cm_enhanced = result.get("copy_move_enhanced_score")
    
    if ela_enhanced or cm_enhanced:
        st.markdown("### ⭐ Enhanced Features Available")
        st.info("""
        This analysis includes enhanced forensic detection. For visualizations and 
        detailed enhanced analysis, try the **'Enhanced Forensics (With Visualizations)'** mode.
        """)
    
    # Recommendations based on risk level
    st.markdown("### 💡 Recommendations & Next Steps")
    
    if risk_level == "HIGH":
        st.warning("""
        **⚠️ CRITICAL - High Manipulation Probability Detected**
        
        **Immediate Actions:**
        1. **Do not use** this image for authentication or verification
        2. **Verify original source** through independent channels
        3. **Contact subject matter experts** for manual review
        4. **Document all findings** for evidence preservation
        """)
    elif risk_level == "MEDIUM":
        st.info("""
        **📝 MODERATE RISK - Further Verification Required**
        
        **Recommended Actions:**
        1. **Cross-reference** with other available sources
        2. **Verify image context** and provenance
        3. **Use with caution** in professional contexts
        4. **Consider manual inspection** if decision-critical
        """)
    else:
        st.success("""
        **✅ LOW RISK - Appears Authentic**
        
        **Standard Protocol:**
        1. **Standard verification** protocols are sufficient
        2. **Maintain normal** digital security practices
        3. **Always verify** critical information through multiple sources
        """)
    
    # Report Download
    report_url = data.get("report_url")
    if report_url:
        st.markdown("### 📄 Analysis Report")
        full_report_url = f"http://localhost:8000{report_url}"
        st.markdown(f"Download the complete analysis report: [📥 Download Report]({full_report_url})")
    
    # Action buttons
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.analysis_results = None
            st.session_state.uploaded_filename = None
            st.rerun()
    
    with col_btn2:
        if st.button("📜 View History", use_container_width=True):
            st.switch_page("pages/history.py")
    
    with col_btn3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("app.py")

def display_cnn_results(data):
    """Display CNN-only analysis results."""
    st.markdown("### 🧠 CNN Analysis Results")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        is_fake = data.get("is_fake", False)
        confidence = data.get("confidence", 0)
        
        st.markdown(f"**Prediction:** {'**FAKE** 🔴' if is_fake else '**REAL** 🟢'}")
        st.markdown(f"**Confidence:** {confidence:.1f}%")
        
        # Confidence progress bar
        st.progress(confidence / 100, text=f"Model Confidence: {confidence:.1f}%")
    
    with col2:
        st.info("""
        **CNN Model Info:**
        - Model: EfficientNet-B0
        - Training: 25 epochs
        - Dataset: Custom deepfake dataset
        - Accuracy: ~70-80%
        """)
    
    # Action buttons
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.analysis_results = None
            st.rerun()
    
    with col_btn2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("app.py")

def display_forensic_results(data):
    """Display forensic-only analysis results."""
    st.markdown("### 🔍 Forensic Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ela_score = data.get("ela_score", 0)
        st.metric("ELA Score", f"{ela_score:.1f}%")
        st.progress(ela_score / 100)
        st.caption("Error Level Analysis")
    
    with col2:
        meta_score = data.get("metadata_score", 0)
        st.metric("Metadata Score", f"{meta_score:.1f}%")
        st.progress(meta_score / 100)
        st.caption("EXIF Data Analysis")
    
    with col3:
        copy_score = data.get("copy_move_score", 0)
        st.metric("Copy-Move Score", f"{copy_score:.1f}%")
        st.progress(copy_score / 100)
        st.caption("Duplicate Detection")
    
    # Forensic average
    forensic_avg = data.get("forensic_average", 0)
    st.markdown(f"**Forensic Average Score:** {forensic_avg:.1f}%")
    
    # Interpretation
    if forensic_avg > 70:
        st.warning("High probability of manipulation based on forensic analysis")
    elif forensic_avg > 40:
        st.info("Moderate probability - requires further investigation")
    else:
        st.success("Low probability of manipulation based on forensic analysis")
    
    # Action buttons
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.analysis_results = None
            st.rerun()
    
    with col_btn2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("app.py")

# Display analysis results if available
if st.session_state.analysis_results:
    data = st.session_state.analysis_results
    processing_time = st.session_state.processing_time
    
    st.markdown("---")
    st.markdown('<div class="section-header"><h2>📊 Analysis Results</h2></div>', unsafe_allow_html=True)
    
    # Show results based on analysis type
    analysis_type = st.session_state.get("analysis_type", "complete")
    
    if analysis_type == "enhanced_forensic":
        display_enhanced_forensic_results(data, processing_time)
    elif analysis_type == "complete":
        display_complete_results(data, processing_time)
    elif analysis_type == "cnn":
        display_cnn_results(data)
    else:
        display_forensic_results(data)

# Sidebar content for this page
with st.sidebar:
    st.markdown("### 📤 Upload Tips")
    st.markdown("""
    1. Use clear, high-resolution images
    2. Avoid heavily compressed files
    3. Include original metadata if possible
    4. For best results, use images under 5MB
    
    **Enhanced Forensics:**
    - Generates visual heatmaps
    - Shows copy-move detections
    - Better accuracy with enhanced algorithms
    """)
    
    st.markdown("---")
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px;">
    <p><strong>TruthLens Deepfake Detection System v1.0</strong></p>
    <p>⚠️ This tool provides AI-assisted analysis for educational and research purposes.</p>
    <p>Always verify critical information through multiple sources and expert review.</p>
</div>
""", unsafe_allow_html=True)
