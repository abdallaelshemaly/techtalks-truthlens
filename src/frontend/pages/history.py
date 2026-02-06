""" 
History page for TruthLens dashboard showing past analyses from database
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.api_client import TruthLensAPIClient
from components.header import render_header

# Page configuration
st.set_page_config(
    page_title="History - TruthLens",
    page_icon="📜",
    layout="wide"
)

# Header
render_header("📜 Analysis History")

# Initialize API client
api_client = TruthLensAPIClient(base_url="http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
    }
    
    .risk-high {
        background-color: #f8d7da;
        color: #dc3545;
    }
    
    .risk-medium {
        background-color: #fff3cd;
        color: #ffc107;
    }
    
    .risk-low {
        background-color: #d4edda;
        color: #28a745;
    }
    
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("View and filter past image analyses from the database.")

# Load history
@st.cache_data(ttl=30)
def load_history_data(limit=50):
    """Load analysis history from API"""
    try:
        response = api_client.get_history(limit=limit)
        if response and "history" in response:
            return response["history"]
        return []
    except:
        return []

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filter History")
    
    # Date range filter (simplified)
    time_filter = st.selectbox(
        "Time Period",
        ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    # Risk level filter
    risk_filter = st.multiselect(
        "Risk Level",
        ["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"]
    )
    
    # Authenticity filter
    authenticity_filter = st.selectbox(
        "Authenticity",
        ["All", "Fake Only", "Real Only"]
    )
    
    # Confidence threshold
    confidence_threshold = st.slider(
        "Minimum CNN Confidence",
        min_value=0,
        max_value=100,
        value=50,
        help="Filter by minimum CNN confidence percentage"
    )
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    if st.button("📤 New Analysis"):
        st.switch_page("pages/upload_analyze.py")
    
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")

# Load data
history_data = load_history_data(limit=100)

if history_data:
    # Convert to DataFrame
    df_data = []
    for item in history_data:
        # Format risk badge
        risk_level = item.get("risk_level", "UNKNOWN")
        if risk_level == "HIGH":
            risk_badge = '<span class="risk-badge risk-high">HIGH</span>'
        elif risk_level == "MEDIUM":
            risk_badge = '<span class="risk-badge risk-medium">MEDIUM</span>'
        else:
            risk_badge = '<span class="risk-badge risk-low">LOW</span>'
        
        # Format timestamp
        timestamp = item.get("timestamp", "")
        if timestamp:
            try:
                date_only = timestamp.split("T")[0]
                time_only = timestamp.split("T")[1][:8]
                formatted_time = f"{date_only} {time_only}"
            except:
                formatted_time = timestamp
        else:
            formatted_time = "N/A"
        
        df_data.append({
            "ID": item.get("id", ""),
            "Filename": item.get("filename", "Unknown"),
            "Date": formatted_time,
            "Risk": risk_badge,
            "CNN %": float(item.get("cnn_confidence", 0)),
            "ELA %": float(item.get("ela_score", 0)),
            "Meta %": float(item.get("metadata_score", 0)),
            "CM %": float(item.get("copy_move_score", 0)),
            "Is Fake": "✅" if item.get("is_fake") else "❌",
            "Risk Level": risk_level  # Hidden column for filtering
        })
    
    df = pd.DataFrame(df_data)
    
    # Apply filters
    if risk_filter:
        df = df[df["Risk Level"].isin(risk_filter)]
    
    if authenticity_filter == "Fake Only":
        df = df[df["Is Fake"] == "✅"]
    elif authenticity_filter == "Real Only":
        df = df[df["Is Fake"] == "❌"]
    
    if confidence_threshold > 0:
        df = df[df["CNN %"] >= confidence_threshold]
    
    # Display summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Analyses", len(df))
    with col2:
        high_count = len(df[df["Risk Level"] == "HIGH"])
        st.metric("High Risk", high_count)
    with col3:
        fake_count = len(df[df["Is Fake"] == "✅"])
        st.metric("Fake Detected", fake_count)
    with col4:
        avg_cnn = df["CNN %"].mean() if len(df) > 0 else 0
        st.metric("Avg CNN %", f"{avg_cnn:.1f}")
    
    # Display the table
    st.markdown(f"### Showing {len(df)} of {len(history_data)} analyses")
    
    # Create display DataFrame (without hidden columns)
    display_df = df.drop(columns=["Risk Level", "ID"]).copy()
    
    # Display as interactive table
    st.dataframe(
        display_df,
        column_config={
            "Risk": st.column_config.TextColumn(
                "Risk Level",
                help="Overall risk assessment",
                width="small"
            ),
            "CNN %": st.column_config.ProgressColumn(
                "CNN Confidence",
                help="CNN model confidence percentage",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "ELA %": st.column_config.ProgressColumn(
                "ELA Score",
                help="Error Level Analysis score",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "Meta %": st.column_config.ProgressColumn(
                "Metadata Score",
                help="Metadata analysis score",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "CM %": st.column_config.ProgressColumn(
                "Copy-Move Score",
                help="Copy-Move detection score",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "Is Fake": st.column_config.TextColumn(
                "Fake",
                help="CNN prediction (Fake/Real)",
                width="small"
            ),
            "Filename": st.column_config.TextColumn(
                "Filename",
                help="Original filename",
                width="medium"
            ),
            "Date": st.column_config.DatetimeColumn(
                "Date/Time",
                help="Analysis timestamp",
                format="YYYY-MM-DD HH:mm"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Data")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            # Convert to CSV string
            csv_data = df.to_csv(index=False)
            st.code(csv_data[:500] + "..." if len(csv_data) > 500 else csv_data, language="text")
            st.success("CSV data ready to copy!")
    
    with col_exp2:
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"truthlens_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Chart visualization
    st.markdown("---")
    st.markdown("### 📈 Analysis Trends")
    
    if len(df) > 0:
        tab1, tab2, tab3 = st.tabs(["Risk Distribution", "CNN Confidence", "Forensic Scores"])
        
        with tab1:
            risk_counts = df["Risk Level"].value_counts()
            st.bar_chart(risk_counts)
        
        with tab2:
            if len(df) > 1:
                st.line_chart(df["CNN %"])
            else:
                st.info("Need more data for trend analysis")
        
        with tab3:
            if len(df) > 1:
                forensic_df = df[["ELA %", "Meta %", "CM %"]]
                st.line_chart(forensic_df)
            else:
                st.info("Need more data for trend analysis")
    
else:
    st.info("📭 No analysis history found in the database.")
    st.markdown("""
    To get started:
    1. Go to the **Upload & Analyze** page
    2. Upload an image for analysis
    3. Your first analysis will appear here!
    """)
    
    if st.button("📤 Go to Upload Page", type="primary"):
        st.switch_page("pages/upload_analyze.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>📜 TruthLens Analysis History | Database records from local SQLite</p>
    <p>Data is stored locally in <code>truthlens.db</code> file</p>
</div>
""", unsafe_allow_html=True)