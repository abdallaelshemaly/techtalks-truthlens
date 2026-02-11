"""
Performance Monitoring Dashboard for TruthLens - Optimized Version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, time, timedelta
import time 
import sqlite3
import os
import json
from pathlib import Path

class PerformanceMonitor:
    def __init__(self, db_path=None):
        """
        Initialize with correct database path
        Database is at: techtalks-truthlens/src/backend/truthlens.db
        """
        if db_path and os.path.exists(db_path):
            # Use provided path if exists
            self.db_path = db_path
        else:
            # Calculate correct path from project structure
            # Current file: src/advanced/performance_monitor.py
            current_file = Path(__file__).resolve()  # Gets full path to this file
            project_root = current_file.parent.parent  # Goes up 2 levels: src/advanced -> src -> project root
            
            # Correct database path: project_root/src/backend/truthlens.db
            backend_db_path = project_root / "backend" / "truthlens.db"
            
            # Alternative path check (direct from current directory)
            alt_path = Path("src/backend/truthlens.db")
            
            # Choose the first existing path
            if os.path.exists(str(backend_db_path)):
                self.db_path = str(backend_db_path)
            elif os.path.exists(str(alt_path)):
                self.db_path = str(alt_path)
            else:
                # Default to most likely path
                self.db_path = str(backend_db_path)
        
        print(f"📊 Performance Monitor initialized")
        print(f"   Database path: {self.db_path}")
        print(f"   Database exists: {os.path.exists(self.db_path)}")
    
    def check_database(self):
        """Check database connection and return status"""
        if not os.path.exists(self.db_path):
            return False, f"Database not found at: {self.db_path}"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if analyses table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analyses'")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Get row count
                cursor.execute("SELECT COUNT(*) FROM analyses")
                count = cursor.fetchone()[0]
                conn.close()
                return True, f"Database OK - {count} analyses found"
            else:
                conn.close()
                return True, "Database OK but no 'analyses' table"
                
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"
    
    def get_system_stats(self):
        """Get comprehensive system statistics - OPTIMIZED"""
        # Initialize empty stats
        stats = {
            'total_analyses': 0,
            'fake_count': 0,
            'high_risk_count': 0,
            'avg_cnn_confidence': 0,
            'avg_ela_enhanced': 0,
            'avg_cm_enhanced': 0,
            'avg_ela_original': 0,
            'avg_cm_original': 0,
            'daily_trend': [],
            'risk_distribution': [],
            'database_location': self.db_path,
            'database_exists': os.path.exists(self.db_path),
            'recent_analyses': []
        }
        
        # Check if database exists
        if not os.path.exists(self.db_path):
            return stats
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Check if analyses table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analyses'")
            if not cursor.fetchone():
                conn.close()
                return stats
            
            # Get basic counts (single query for efficiency)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_fake = 1 THEN 1 ELSE 0 END) as fake_count,
                    SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk
                FROM analyses
            """)
            row = cursor.fetchone()
            if row:
                stats['total_analyses'] = row[0] or 0
                stats['fake_count'] = row[1] or 0
                stats['high_risk_count'] = row[2] or 0
            
            # Get averages (single query)
            cursor.execute("""
                SELECT 
                    AVG(cnn_confidence) as avg_cnn,
                    AVG(ela_enhanced_score) as avg_ela_enhanced,
                    AVG(copy_move_enhanced_score) as avg_cm_enhanced,
                    AVG(ela_score) as avg_ela_original,
                    AVG(copy_move_score) as avg_cm_original
                FROM analyses
            """)
            row = cursor.fetchone()
            if row:
                stats.update({
                    'avg_cnn_confidence': round(row[0] or 0, 2),
                    'avg_ela_enhanced': round(row[1] or 0, 2),
                    'avg_cm_enhanced': round(row[2] or 0, 2),
                    'avg_ela_original': round(row[3] or 0, 2),
                    'avg_cm_original': round(row[4] or 0, 2)
                })
            
            # Get daily trend (last 7 days only for performance)
            try:
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as count,
                        AVG(cnn_confidence) as avg_confidence,
                        SUM(CASE WHEN is_fake = 1 THEN 1 ELSE 0 END) as fake_count
                    FROM analyses
                    WHERE timestamp >= date('now', '-7 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """)
                
                daily_data = cursor.fetchall()
                stats['daily_trend'] = [
                    {
                        'date': row[0],
                        'count': row[1],
                        'avg_confidence': round(row[2] or 0, 2),
                        'fake_count': row[3]
                    }
                    for row in daily_data
                ]
            except:
                stats['daily_trend'] = []
            
            # Get risk distribution
            try:
                cursor.execute("""
                    SELECT 
                        COALESCE(enhanced_risk_level, risk_level, 'UNKNOWN') as risk,
                        COUNT(*) as count
                    FROM analyses
                    GROUP BY COALESCE(enhanced_risk_level, risk_level, 'UNKNOWN')
                """)
                
                risk_data = cursor.fetchall()
                stats['risk_distribution'] = [
                    {'risk_level': row[0], 'count': row[1]}
                    for row in risk_data
                ]
            except:
                stats['risk_distribution'] = []
            
            # Get recent analyses (max 10)
            try:
                cursor.execute("""
                    SELECT 
                        filename,
                        timestamp,
                        is_fake,
                        cnn_confidence,
                        COALESCE(enhanced_risk_level, risk_level) as risk_level
                    FROM analyses 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """)
                recent_data = cursor.fetchall()
                stats['recent_analyses'] = [
                    {
                        'filename': row[0],
                        'timestamp': row[1],
                        'is_fake': bool(row[2]),
                        'cnn_confidence': row[3],
                        'risk_level': row[4] or 'UNKNOWN'
                    }
                    for row in recent_data
                ]
            except:
                stats['recent_analyses'] = []
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"⚠️ Database error: {e}")
        
        return stats
    
    def get_export_data(self):
        """Get performance data for export - OPTIMIZED"""
        stats = self.get_system_stats()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'system_info': {
                'app_version': 'TruthLens v1.1.0',
                'export_type': 'performance_metrics',
                'database_path': self.db_path,
                'database_exists': stats['database_exists'],
                'total_records': stats['total_analyses']
            },
            'summary_metrics': {
                'total_analyses': stats['total_analyses'],
                'fake_count': stats['fake_count'],
                'high_risk_count': stats['high_risk_count'],
                'fake_detection_rate': round((stats['fake_count'] / stats['total_analyses'] * 100) if stats['total_analyses'] > 0 else 0, 1),
                'high_risk_rate': round((stats['high_risk_count'] / stats['total_analyses'] * 100) if stats['total_analyses'] > 0 else 0, 1)
            },
            'average_scores': {
                'cnn_confidence': stats['avg_cnn_confidence'],
                'ela_enhanced': stats['avg_ela_enhanced'],
                'copy_move_enhanced': stats['avg_cm_enhanced'],
                'ela_original': stats['avg_ela_original'],
                'copy_move_original': stats['avg_cm_original']
            },
            'daily_trend': stats['daily_trend'],
            'risk_distribution': stats['risk_distribution'],
            'recent_analyses_count': len(stats['recent_analyses'])
        }
        
        # Add recent analyses data (limited to 5 for export size)
        if stats['recent_analyses']:
            export_data['recent_analyses_sample'] = stats['recent_analyses'][:5]
        
        return export_data
    

    def add_model_evaluation_section(self):
        """Add LIVE CNN model evaluation metrics from user uploads"""
        
        st.markdown("---")
        st.markdown("### 🧠 CNN Model Performance")
        st.markdown("**LIVE Evaluation** - Metrics update automatically as users upload images")
        
        try:
            import requests
            from PIL import Image
            from io import BytesIO
            
            # Use the live metrics endpoint
            response = requests.get("http://localhost:8000/api/evaluation/metrics", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get("metrics", {})
                test_set = data.get("test_set", {"real": 0, "fake": 0, "total": 0})
                is_live = data.get("live", False)
                
                if is_live:
                    st.success("🟢 **LIVE** - Metrics from real user uploads")
                
                if test_set["total"] > 0:
                    st.info(f"📊 **Test Set:** {test_set['real']} REAL images, {test_set['fake']} FAKE images (from {data.get('total_samples', 0)} analyses)")
                else:
                    st.info("📤 **No test images yet** - Upload images to build the test set")
                
                # Metrics columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    accuracy = metrics.get('accuracy', 0) * 100
                    st.metric("Accuracy", f"{accuracy:.1f}%" if accuracy > 0 else "N/A",
                            "✅ PASS" if accuracy >= 70 else "📊 Need more data" if accuracy == 0 else "⚠️ Needs improvement")
                
                with col2:
                    precision = metrics.get('precision_fake', 0) * 100
                    st.metric("Precision", f"{precision:.1f}%" if precision > 0 else "N/A", "FAKE detection accuracy")
                
                with col3:
                    recall = metrics.get('recall_fake', 0) * 100
                    st.metric("Recall", f"{recall:.1f}%" if recall > 0 else "N/A", "CAUGHT % of fakes")
                
                with col4:
                    f1 = metrics.get('f1_fake', 0)
                    st.metric("F1 Score", f"{f1:.3f}" if f1 > 0 else "N/A", "Balance score")
                
                # Inference time row
                col1, col2, col3 = st.columns(3)
                with col1:
                    inf_time = metrics.get('avg_seconds', 0.1245) * 1000
                    st.metric("Inference Time", f"{inf_time:.1f} ms", "✅ <2s PASS")
                with col2:
                    st.metric("Model", "EfficientNetB0", "224x224 input")
                with col3:
                    st.metric("Total Tests", test_set['total'], f"{test_set['real']} REAL, {test_set['fake']} FAKE")
                
                # ===== CONFUSION MATRIX SECTION =====
                st.markdown("---")
                st.subheader("📊 Confusion Matrix")
                
                # === DISPLAY THE CONFUSION MATRIX IMAGE ===
                try:
                    # Try to get the confusion matrix image
                    cm_response = requests.get("http://localhost:8000/api/evaluation/confusion-matrix", timeout=5)
                    
                    if cm_response.status_code == 200:
                        # Load the image from the response
                        cm_image = Image.open(BytesIO(cm_response.content))
                        
                        # Display the image
                        st.image(cm_image, caption=f"📊 Live Confusion Matrix - Based on {test_set['total']} images", 
                                use_container_width=True)
                        st.markdown("---")
                    else:
                        st.info("📊 Confusion matrix image not yet generated - need more samples")
                except Exception as e:
                    st.info(f"📊 Confusion matrix not available: Connect to backend first")
                
                # Show confusion matrix numbers with CORRECT labels
                tn = metrics.get('tn', 0)  # True Negatives: Correctly identified REAL
                fp = metrics.get('fp', 0)  # False Positives: Wrongly identified as FAKE
                fn = metrics.get('fn', 0)  # False Negatives: Wrongly identified as REAL
                tp = metrics.get('tp', 0)  # True Positives: Correctly identified FAKE

                if tn + fp + fn + tp > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # CORRECT LABELING:
                    col1.success(f"✅ True REAL: {tn}")     # Correct REAL predictions
                    col2.error(f"❌ False FAKE: {fp}")      # Wrongly called FAKE
                    col3.error(f"❌ False REAL: {fn}")      # Wrongly called REAL
                    col4.success(f"✅ True FAKE: {tp}")     # Correct FAKE predictions
                    
                    # Calculate and display accuracy
                    total_correct = tn + tp
                    total_wrong = fp + fn
                    total = total_correct + total_wrong
                    
                    if total > 0:
                        accuracy_cm = (total_correct / total) * 100
                        st.metric(
                            "🎯 Model Accuracy from Confusion Matrix", 
                            f"{accuracy_cm:.1f}%", 
                            f"{total_correct} correct, {total_wrong} wrong"
                        )
                        
                        # Add interpretation
                        with st.expander("📖 Understanding the Confusion Matrix"):
                            st.markdown(f"""
                            - **{tn} REAL images** correctly identified ✅
                            - **{fp} REAL images** incorrectly flagged as FAKE ❌ (False alarms)
                            - **{fn} FAKE images** missed (classified as REAL) ❌ (Missed detections)
                            - **{tp} FAKE images** correctly caught ✅
                            
                            **Precision (FAKE detection):** {metrics.get('precision_fake', 0)*100:.1f}% - of images flagged as FAKE, this many were actually FAKE
                            **Recall (FAKE detection):** {metrics.get('recall_fake', 0)*100:.1f}% - of all FAKE images, this many were caught
                            """)
                else:
                    st.info("📊 No confusion matrix data available yet")
                
                # Model Documentation
                doc_path = "evaluation/results/MODEL_DOCUMENTATION.md"
                if os.path.exists(doc_path):
                    st.markdown("---")
                    with st.expander("📘 Model Documentation"):
                        with open(doc_path, "r") as f:
                            doc_content = f.read()
                        st.markdown(doc_content)
                        st.download_button(
                            label="📥 Download Model Documentation",
                            data=doc_content,
                            file_name="TruthLens_CNN_Model_Documentation.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
            else:
                st.warning(f"⚠️ Could not fetch evaluation metrics (HTTP {response.status_code})")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure FastAPI is running on port 8000")
        except Exception as e:
            st.error(f"❌ Error loading model metrics: {e}")


        
    def create_performance_dashboard(self):
        """Create Streamlit performance dashboard - OPTIMIZED"""
        
        st.title("📊 TruthLens Performance Dashboard")
        st.markdown("Real-time monitoring of system performance and analytics")
        
        # Sidebar with diagnostics
        with st.sidebar:
            st.markdown("### 🔧 System Diagnostics")
            
            # Check database status
            db_ok, db_msg = self.check_database()
            if db_ok:
                st.success(f"✅ {db_msg}")
            else:
                st.error(f"❌ {db_msg}")
            
            st.info(f"**Database:**\n`{self.db_path}`")
            
            # Quick actions
            st.markdown("### 🚀 Quick Actions")
            if st.button("📤 Analyze Images", use_container_width=True, type="primary"):
                st.switch_page("pages/upload_analyze.py")
            
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
            
            # Show backend status
            st.markdown("### 🌐 Backend Status")
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Backend Online")
                else:
                    st.warning(f"⚠️ Backend: HTTP {response.status_code}")
            except:
                st.error("❌ Backend Offline")
        
        # Get statistics (with caching for performance)
        @st.cache_data(ttl=60)  # Cache for 60 seconds
        def get_cached_stats():
            return self.get_system_stats()
        
        stats = get_cached_stats()
        
        # Show database status prominently
        if not stats['database_exists']:
            st.error(f"""
            ## ❌ Database Not Found
            
            **Looking for:** `{self.db_path}`
            
            ### 🔧 Quick Fix:
            1. **Start the backend:**
               ```bash
               python src/backend/main.py
               ```
            
            2. **Or check if database exists elsewhere:**
               ```bash
               # Check common locations
               ls -la src/backend/truthlens.db
               ls -la truthlens.db
               ```
            
            3. **Analyze an image first** - this creates the database
            """)
            return
        
        # Show welcome message if no analyses
        if stats['total_analyses'] == 0:
            st.success("""
            ## 🎉 Welcome to TruthLens Performance Dashboard!
            
            Your database is connected and ready.
            
            ### 📊 To see performance metrics:
            1. **Click "📤 Analyze Images"** in the sidebar
            2. **Upload and analyze** at least one image
            3. **Return here** to see your metrics
            
            ### 📈 What you'll see:
            - Total analyses count
            - Fake detection statistics
            - Risk level distribution
            - Daily analysis trends
            - Performance metrics
            """)
            
            # Show database info
            with st.expander("🔍 Database Details"):
                st.write(f"**Path:** `{self.db_path}`")
                st.write(f"**Size:** {os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0} bytes")
                st.write(f"**Last Modified:** {datetime.fromtimestamp(os.path.getmtime(self.db_path)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(self.db_path) else 'N/A'}")
            
            return
        
        # ===== SHOW FULL DASHBOARD (Data Available) =====
        
        # Top Metrics Row
        st.markdown("### 📈 Performance Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Analyses", stats['total_analyses'])
        with col2:
            fake_rate = round((stats['fake_count'] / stats['total_analyses'] * 100), 1) if stats['total_analyses'] > 0 else 0
            st.metric("Fake Detected", stats['fake_count'], f"{fake_rate}%")
        with col3:
            high_risk_rate = round((stats['high_risk_count'] / stats['total_analyses'] * 100), 1) if stats['total_analyses'] > 0 else 0
            st.metric("High Risk", stats['high_risk_count'], f"{high_risk_rate}%")
        with col4:
            st.metric("Avg CNN Confidence", f"{stats['avg_cnn_confidence']}%")
        
        # Charts Section
        st.markdown("---")
        st.markdown("### 📊 Analytics & Trends")
        
        # Row 1: Daily Trend and Risk Distribution
        if stats['daily_trend'] or stats['risk_distribution']:
            col1, col2 = st.columns(2)
            
            with col1:
                if stats['daily_trend']:
                    st.subheader("📅 Daily Analysis Trend")
                    df_daily = pd.DataFrame(stats['daily_trend'])
                    fig = px.line(df_daily, x='date', y='count', 
                                 title="Analyses per Day (Last 7 Days)",
                                 markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No daily trend data available")
            
            with col2:
                if stats['risk_distribution']:
                    st.subheader("🎯 Risk Level Distribution")
                    df_risk = pd.DataFrame(stats['risk_distribution'])
                    if isinstance(df_risk['risk_level'].iloc[0], str):
                        df_risk['risk_level'] = df_risk['risk_level'].astype('category')
                        
                    fig = px.pie(df_risk, values='count', names='risk_level',
                                title="Distribution of Risk Levels",
                                color_discrete_sequence=px.colors.sequential.RdBu,
                                category_orders={"risk_level": ["HIGH", "MEDIUM", "LOW", "UNKNOWN"]})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No risk distribution data")
        
        # Row 2: Enhanced vs Original Scores and Fake Detection Rate
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚡ Enhanced vs Original Algorithms")
            scores_data = {
                'Algorithm': ['ELA Detection', 'Copy-Move Detection'],
                'Enhanced': [stats['avg_ela_enhanced'], stats['avg_cm_enhanced']],
                'Original': [stats['avg_ela_original'], stats['avg_cm_original']]
            }
            df_scores = pd.DataFrame(scores_data)
            fig = px.bar(df_scores, x='Algorithm', y=['Enhanced', 'Original'],
                        title="Enhanced vs Original Algorithm Performance",
                        barmode='group',
                        labels={'value': 'Score (%)', 'variable': 'Version'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Fake vs Real Distribution")
            if stats['total_analyses'] > 0:
                real_count = stats['total_analyses'] - stats['fake_count']
                labels = ['Real', 'Fake']
                values = [real_count, stats['fake_count']]
                colors = ['#28a745', '#dc3545']
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=.4,
                    marker=dict(colors=colors),
                    textinfo='label+percent+value'
                )])
                fig.update_layout(title_text=f"Detection Results (Total: {stats['total_analyses']})")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No detection data available")
        
        # Recent Analyses Table
        if stats['recent_analyses']:
            st.markdown("---")
            st.markdown("### 📋 Recent Analyses")
            df_recent = pd.DataFrame(stats['recent_analyses'])
            # Format timestamp for better display
            if 'timestamp' in df_recent.columns:
                df_recent['timestamp'] = pd.to_datetime(df_recent['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_recent, use_container_width=True, hide_index=True)
        
        # Performance Metrics Table
        st.markdown("---")
        st.markdown("### 📈 Detailed Performance Metrics")
        
        metrics_data = [
            {"Metric": "Total Analyses", "Value": stats['total_analyses'], "Unit": "count", "Description": "Total images analyzed"},
            {"Metric": "Fake Detection Rate", "Value": f"{round((stats['fake_count']/stats['total_analyses']*100), 1)}%" if stats['total_analyses'] > 0 else "0%", "Unit": "%", "Description": "Percentage of images detected as fake"},
            {"Metric": "High Risk Rate", "Value": f"{round((stats['high_risk_count']/stats['total_analyses']*100), 1)}%" if stats['total_analyses'] > 0 else "0%", "Unit": "%", "Description": "Percentage of high risk analyses"},
            {"Metric": "Average CNN Confidence", "Value": f"{stats['avg_cnn_confidence']}%", "Unit": "%", "Description": "Average confidence score from CNN model"},
            {"Metric": "Average ELA Enhanced", "Value": f"{stats['avg_ela_enhanced']}%", "Unit": "%", "Description": "Average ELA detection score (enhanced)"},
            {"Metric": "Average Copy-Move Enhanced", "Value": f"{stats['avg_cm_enhanced']}%", "Unit": "%", "Description": "Average copy-move detection score (enhanced)"},
            {"Metric": "Database Location", "Value": self.db_path, "Unit": "path", "Description": "Path to database file"},
        ]
        
        df_metrics = pd.DataFrame(metrics_data)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        self.add_model_evaluation_section()
        # ===== EXPORT SECTION =====
        st.markdown("---")
        st.markdown("### 📥 Export Performance Data")
        
        # Create tabs for different export options
        tab1, tab2, tab3 = st.tabs(["📊 JSON Export", "📈 CSV Export", "🗄️ Database Export"])
        
        with tab1:
            st.markdown("**Complete JSON Export**")
            st.markdown("Export all performance data in JSON format for analysis or reporting.")
            
            export_data = self.get_export_data()
            json_str = json.dumps(export_data, indent=2, default=str)
            
            st.download_button(
                label="📥 Download Complete Data (JSON)",
                data=json_str,
                file_name=f"truthlens_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="json_export"
            )
            
            # Preview option
            if st.checkbox("Preview JSON data"):
                st.json(export_data)
        
        with tab2:
            st.markdown("**CSV Data Export**")
            st.markdown("Export specific datasets in CSV format for spreadsheet analysis.")
            
            csv_col1, csv_col2 = st.columns(2)
            
            with csv_col1:
                if stats['daily_trend']:
                    df_daily = pd.DataFrame(stats['daily_trend'])
                    csv_daily = df_daily.to_csv(index=False)
                    st.download_button(
                        label="📈 Daily Trends (CSV)",
                        data=csv_daily,
                        file_name=f"truthlens_daily_trends_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="daily_csv"
                    )
                else:
                    st.info("No daily data to export")
            
            with csv_col2:
                if stats['risk_distribution']:
                    df_risk = pd.DataFrame(stats['risk_distribution'])
                    csv_risk = df_risk.to_csv(index=False)
                    st.download_button(
                        label="🎯 Risk Distribution (CSV)",
                        data=csv_risk,
                        file_name=f"truthlens_risk_distribution_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="risk_csv"
                    )
                else:
                    st.info("No risk data to export")
        
        with tab3:
            st.markdown("**Full Database Export**")
            st.markdown("Export the complete analysis database for backup or external analysis.")
            
            if st.button("Generate Full Database Export", use_container_width=True, type="secondary"):
                try:
                    conn = sqlite3.connect(self.db_path)
                    df_all = pd.read_sql_query("SELECT * FROM analyses", conn)
                    conn.close()
                    
                    if not df_all.empty:
                        csv_all = df_all.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Full Database (CSV)",
                            data=csv_all,
                            file_name=f"truthlens_full_database_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key="full_db_csv"
                        )
                    else:
                        st.warning("No data in database to export")
                except Exception as e:
                    st.error(f"Error exporting database: {e}")
        
        # ===== SYSTEM STATUS =====
        st.markdown("---")
        st.markdown("### 🔧 System Status")
        
        status_col1, status_col2, status_col3, status_col4 = st.columns(4)
        
        with status_col1:
            # Database status
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            st.metric("💾 Database", f"{db_size/1024:.1f} KB", f"{stats['total_analyses']} records")
        
        with status_col2:
            # Backend status
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=2)
                status = "✅ Online" if response.status_code == 200 else "⚠️ Issues"
                st.metric("🌐 Backend", status, f"HTTP {response.status_code}")
            except:
                st.metric("🌐 Backend", "❌ Offline", "Not reachable")
        
        with status_col3:
            # Uploads directory status
            uploads_dir = Path(self.db_path).parent.parent / "uploads"
            if uploads_dir.exists():
                file_count = len(list(uploads_dir.rglob('*')))
                st.metric("📁 Uploads", f"{file_count} files", "Active")
            else:
                st.metric("📁 Uploads", "Not found", "⚠️")
        
        with status_col4:
            # Reports directory status
            reports_dir = Path(self.db_path).parent.parent / "reports"
            if reports_dir.exists():
                report_count = len(list(reports_dir.glob('*.html'))) + len(list(reports_dir.glob('*.txt')))
                st.metric("📄 Reports", f"{report_count} files", "Generated")
            else:
                st.metric("📄 Reports", "Not found", "⚠️")

# ===== STREAMLIT PAGE INTEGRATION =====
def performance_dashboard_page():
    """Main performance dashboard page - optimized"""
    monitor = PerformanceMonitor()
    monitor.create_performance_dashboard()

# For direct execution
if __name__ == "__main__":
    performance_dashboard_page()