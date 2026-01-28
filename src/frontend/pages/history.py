"""
History page for TruthLens dashboard.
This appears as "History" in Streamlit's sidebar.
"""

import streamlit as st
import pandas as pd
from components.header import render_header

# Page configuration
st.set_page_config(
    page_title="History - TruthLens",
    page_icon="📊",
    layout="wide"
)

# Header
render_header("📊 Analysis History")

# Mock history data
history_data = [
    {
        "id": 1,
        "date": "2024-01-15 14:30",
        "filename": "portrait.jpg",
        "risk": 15,
        "authenticity": 85,
        "status": "Verified",
        "size_kb": 2450,
        "analysis_type": "Standard"
    },
    {
        "id": 2,
        "date": "2024-01-14 11:15",
        "filename": "news_image.png",
        "risk": 67,
        "authenticity": 33,
        "status": "Suspicious",
        "size_kb": 1870,
        "analysis_type": "Comprehensive"
    },
    {
        "id": 3,
        "date": "2024-01-13 09:45",
        "filename": "profile_pic.jpeg",
        "risk": 42,
        "authenticity": 58,
        "status": "Review Needed",
        "size_kb": 1250,
        "analysis_type": "Quick Scan"
    },
    {
        "id": 4,
        "date": "2024-01-12 16:20",
        "filename": "document.jpg",
        "risk": 8,
        "authenticity": 92,
        "status": "Verified",
        "size_kb": 3450,
        "analysis_type": "Standard"
    },
    {
        "id": 5,
        "date": "2024-01-11 13:10",
        "filename": "social_media.png",
        "risk": 89,
        "authenticity": 11,
        "status": "High Risk",
        "size_kb": 980,
        "analysis_type": "Comprehensive"
    },
]

# Convert to DataFrame
df = pd.DataFrame(history_data)

# Filter section
st.markdown("### 🔍 Filter History")

col1, col2, col3 = st.columns(3)

with col1:
    date_filter = st.selectbox(
        "Time Period",
        ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
    )

with col2:
    risk_filter = st.multiselect(
        "Risk Level",
        ["Low (<30%)", "Medium (30-70%)", "High (>70%)"],
        default=["Low (<30%)", "Medium (30-70%)", "High (>70%)"]
    )

with col3:
    status_filter = st.multiselect(
        "Status",
        ["Verified", "Suspicious", "Review Needed", "High Risk"],
        default=["Verified", "Suspicious", "Review Needed", "High Risk"]
    )

# Apply filters (mock)
filtered_df = df.copy()

# Display results count
st.markdown(f"**Showing {len(filtered_df)} of {len(df)} analyses**")

# Display as interactive table
st.dataframe(
    filtered_df,
    column_config={
        "date": st.column_config.DatetimeColumn("Date/Time"),
        "filename": "Filename",
        "risk": st.column_config.ProgressColumn(
            "Risk Score",
            help="Risk score percentage",
            format="%d%%",
            min_value=0,
            max_value=100,
        ),
        "authenticity": st.column_config.ProgressColumn(
            "Authenticity",
            help="Authenticity score percentage",
            format="%d%%",
            min_value=0,
            max_value=100,
        ),
        "status": st.column_config.TextColumn(
            "Status",
            help="Analysis status"
        ),
        "size_kb": st.column_config.NumberColumn(
            "Size (KB)",
            help="File size in kilobytes"
        ),
        "analysis_type": "Analysis Type",
    },
    hide_index=True,
    use_container_width=True
)

# Action buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export History (CSV)", use_container_width=True):
        st.info("Export functionality will be implemented in Phase 2")

with col2:
    if st.button("🗑️ Clear History", use_container_width=True, type="secondary"):
        st.warning("This will delete all history. Are you sure?")
        confirm = st.checkbox("Yes, I'm sure")
        if confirm:
            st.info("History cleared (mock action)")

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Statistics
st.markdown("---")
st.markdown("### 📈 History Statistics")

if len(filtered_df) > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_risk = filtered_df['risk'].mean()
        st.metric("Average Risk", f"{avg_risk:.1f}%")
    
    with col2:
        avg_auth = filtered_df['authenticity'].mean()
        st.metric("Average Authenticity", f"{avg_auth:.1f}%")
    
    with col3:
        total_files = len(filtered_df)
        st.metric("Total Analyses", total_files)
    
    with col4:
        total_size = filtered_df['size_kb'].sum() / 1024
        st.metric("Total Size", f"{total_size:.1f} MB")
else:
    st.info("No history data available with current filters.")

# Sidebar content for this page
with st.sidebar:
    st.markdown("### 📊 History Info")
    st.markdown("""
    View and manage your analysis history.
    
    **Features:**
    - Filter by date, risk, and status
    - Export data as CSV
    - View detailed statistics
    - Clear history
    
    **Note:** History is stored locally in your session.
    """)
    
    st.markdown("---")
    if st.button("📤 New Analysis"):
        st.switch_page("pages/upload.py")
    
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")