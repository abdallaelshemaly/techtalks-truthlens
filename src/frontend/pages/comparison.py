"""
Comparison Mode - TruthLens
Compare two images side-by-side for forensic analysis.
"""
import streamlit as st
import requests
from PIL import Image
import pandas as pd
import io
import time

# Page Config
st.set_page_config(page_title="Compare - TruthLens", page_icon="⚖️", layout="wide")

# Apply CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("src/frontend/assets/custom.css")
except:
    pass # Fallback if running from different dir

st.markdown("# ⚖️ Forensic Comparison Mode")
st.markdown("Upload two images to compare their authenticity markers side-by-side.")

# --- Layout ---
col_a, col_b = st.columns(2)

# --- HELPER FUNCTION ---
def analyze_image(uploaded_file):
    """Sends image to backend and returns JSON result"""
    if uploaded_file is None:
        return None
    
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post("http://localhost:8000/api/analyze/complete", files=files, timeout=60)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None

# --- SIDE A ---
with col_a:
    st.markdown("### 🖼️ Image A (Reference)")
    file_a = st.file_uploader("Upload Image A", type=['jpg', 'png', 'jpeg'], key="a")
    if file_a:
        st.image(file_a, use_container_width=True)

# --- SIDE B ---
with col_b:
    st.markdown("### 🖼️ Image B (Suspect)")
    file_b = st.file_uploader("Upload Image B", type=['jpg', 'png', 'jpeg'], key="b")
    if file_b:
        st.image(file_b, use_container_width=True)

# --- ACTION ---
if file_a and file_b:
    st.markdown("---")
    if st.button("🔍 Compare Images", type="primary", use_container_width=True):
        
        # Real-time Progress Container
        with st.status("Running Comparative Analysis...", expanded=True) as status:
            
            st.write("📤 Uploading and processing Image A...")
            res_a = analyze_image(file_a)
            st.progress(45)
            
            st.write("📤 Uploading and processing Image B...")
            res_b = analyze_image(file_b)
            st.progress(90)
            
            st.write("📊 Generating comparison matrix...")
            time.sleep(0.5)
            st.progress(100)
            
            status.update(label="Analysis Complete", state="complete", expanded=False)

        # --- RESULTS DISPLAY ---
        if res_a and res_b:
            data_a = res_a.get("result", {})
            data_b = res_b.get("result", {})

            # Metric Comparison Table
            st.subheader("📊 Metric Comparison")
            
            metrics = {
                "Metric": ["Risk Level", "CNN Confidence", "ELA Score", "Copy-Move", "Metadata Trust"],
                "Image A": [
                    data_a.get("risk_level"),
                    f"{data_a.get('cnn_confidence', 0):.1f}%",
                    f"{data_a.get('ela_score', 0):.1f}%",
                    f"{data_a.get('copy_move_score', 0):.1f}%",
                    f"{data_a.get('metadata_score', 0):.1f}%"
                ],
                "Image B": [
                    data_b.get("risk_level"),
                    f"{data_b.get('cnn_confidence', 0):.1f}%",
                    f"{data_b.get('ela_score', 0):.1f}%",
                    f"{data_b.get('copy_move_score', 0):.1f}%",
                    f"{data_b.get('metadata_score', 0):.1f}%"
                ]
            }
            
            df = pd.DataFrame(metrics)
            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Metric": st.column_config.TextColumn("Analysis Metric", width="medium"),
                    "Image A": st.column_config.TextColumn(f"A: {file_a.name}", width="medium"),
                    "Image B": st.column_config.TextColumn(f"B: {file_b.name}", width="medium"),
                }
            )

            # Visual Comparison (ELA)
            st.markdown("---")
            st.subheader("🔬 ELA Visualization Comparison")
            
            res_col_a, res_col_b = st.columns(2)
            
            with res_col_a:
                st.markdown("**Image A ELA**")
                if res_a.get("ela_image_url"):
                    st.image(f"http://localhost:8000{res_a.get('ela_image_url')}", use_container_width=True)
                else:
                    st.info("No ELA generated")
                    
            with res_col_b:
                st.markdown("**Image B ELA**")
                if res_b.get("ela_image_url"):
                    st.image(f"http://localhost:8000{res_b.get('ela_image_url')}", use_container_width=True)
                else:
                    st.info("No ELA generated")

            # Conclusion
            diff_score = abs(data_a.get('cnn_confidence', 0) - data_b.get('cnn_confidence', 0))
            if diff_score > 20:
                st.warning(f"⚠️ Significant discrepancy detected ({diff_score:.1f}%) between the two images.")
            else:
                st.success("✅ Images show similar authenticity characteristics.")

else:
    st.info("Please upload both images to start the comparison.")