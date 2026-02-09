"""
Performance Monitoring Dashboard for TruthLens
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import os
from pathlib import Path

class PerformanceMonitor:
    def __init__(self, db_path="truthlens.db"):
        self.db_path = db_path
    
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        # Basic counts
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analyses")
        stats['total_analyses'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE is_fake = 1")
        stats['fake_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE risk_level = 'HIGH'")
        stats['high_risk_count'] = cursor.fetchone()[0]
        
        # Time-based statistics
        cursor.execute("""
            SELECT 
                AVG(cnn_confidence) as avg_cnn,
                AVG(ela_enhanced_score) as avg_ela,
                AVG(copy_move_enhanced_score) as avg_cm,
                AVG(ela_score) as avg_ela_original,
                AVG(copy_move_score) as avg_cm_original
            FROM analyses
        """)
        avg_results = cursor.fetchone()
        stats.update({
            'avg_cnn_confidence': round(avg_results[0] or 0, 2),
            'avg_ela_enhanced': round(avg_results[1] or 0, 2),
            'avg_cm_enhanced': round(avg_results[2] or 0, 2),
            'avg_ela_original': round(avg_results[3] or 0, 2),
            'avg_cm_original': round(avg_results[4] or 0, 2)
        })
        
        # Daily trend
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as count,
                AVG(cnn_confidence) as avg_confidence,
                SUM(CASE WHEN is_fake = 1 THEN 1 ELSE 0 END) as fake_count
            FROM analyses
            WHERE timestamp >= date('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
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
        
        # Risk distribution
        cursor.execute("""
            SELECT 
                enhanced_risk_level,
                COUNT(*) as count
            FROM analyses
            GROUP BY enhanced_risk_level
        """)
        
        risk_data = cursor.fetchall()
        stats['risk_distribution'] = [
            {'risk_level': row[0] or 'UNKNOWN', 'count': row[1]}
            for row in risk_data
        ]
        
        # Batch results if available
        batch_dir = Path("batch_results")
        if batch_dir.exists():
            batch_folders = [d for d in batch_dir.iterdir() if d.is_dir()]
            stats['batch_analyses'] = len(batch_folders)
            
            # Calculate batch statistics
            total_batch_images = 0
            successful_batch = 0
            for folder in batch_folders:
                json_files = list(folder.glob("*_results.json"))
                if json_files:
                    import json
                    with open(json_files[0], 'r') as f:
                        batch_data = json.load(f)
                        total_batch_images += len(batch_data)
                        successful_batch += len([r for r in batch_data if r.get('success', False)])
            
            stats['total_batch_images'] = total_batch_images
            stats['batch_success_rate'] = round((successful_batch / total_batch_images * 100), 2) if total_batch_images > 0 else 0
        
        conn.close()
        
        return stats
    
    def create_performance_dashboard(self):
        """Create Streamlit performance dashboard"""
        st.set_page_config(
            page_title="Performance Dashboard - TruthLens",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 TruthLens Performance Dashboard")
        st.markdown("Real-time monitoring of system performance and analytics")
        
        # Get statistics
        with st.spinner("Loading performance data..."):
            stats = self.get_system_stats()
        
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Analyses", stats['total_analyses'])
        with col2:
            st.metric("Fake Detected", stats['fake_count'])
        with col3:
            st.metric("High Risk Cases", stats['high_risk_count'])
        with col4:
            if 'batch_analyses' in stats:
                st.metric("Batch Analyses", stats['batch_analyses'])
            else:
                st.metric("Avg CNN Confidence", f"{stats['avg_cnn_confidence']}%")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Daily Analysis Trend")
            if stats['daily_trend']:
                df_daily = pd.DataFrame(stats['daily_trend'])
                fig = px.line(df_daily, x='date', y='count', 
                             title="Analyses per Day (Last 30 days)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No daily data available")
        
        with col2:
            st.subheader("🎯 Risk Level Distribution")
            if stats['risk_distribution']:
                df_risk = pd.DataFrame(stats['risk_distribution'])
                fig = px.pie(df_risk, values='count', names='risk_level',
                            title="Distribution of Risk Levels",
                            color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No risk distribution data")
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚡ Enhanced vs Original Scores")
            scores_data = {
                'Metric': ['ELA Detection', 'Copy-Move Detection'],
                'Enhanced': [stats['avg_ela_enhanced'], stats['avg_cm_enhanced']],
                'Original': [stats['avg_ela_original'], stats['avg_cm_original']]
            }
            df_scores = pd.DataFrame(scores_data)
            fig = px.bar(df_scores, x='Metric', y=['Enhanced', 'Original'],
                        title="Comparison of Enhanced vs Original Algorithms",
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Fake Detection Rate")
            if stats['total_analyses'] > 0:
                fake_rate = (stats['fake_count'] / stats['total_analyses']) * 100
                real_rate = 100 - fake_rate
                
                fig = go.Figure(data=[go.Pie(
                    labels=['Real', 'Fake'],
                    values=[real_rate, fake_rate],
                    hole=.3,
                    marker_colors=['#28a745', '#dc3545']
                )])
                fig.update_layout(title_text="Fake vs Real Detection")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No detection data available")
        
        # Performance Metrics Table
        st.subheader("📋 Detailed Performance Metrics")
        
        metrics_data = [
            {"Metric": "Total Analyses", "Value": stats['total_analyses'], "Unit": "count"},
            {"Metric": "Fake Detection Rate", "Value": f"{(stats['fake_count']/stats['total_analyses']*100):.1f}" if stats['total_analyses'] > 0 else "0", "Unit": "%"},
            {"Metric": "High Risk Rate", "Value": f"{(stats['high_risk_count']/stats['total_analyses']*100):.1f}" if stats['total_analyses'] > 0 else "0", "Unit": "%"},
            {"Metric": "Avg CNN Confidence", "Value": stats['avg_cnn_confidence'], "Unit": "%"},
            {"Metric": "Avg ELA Enhanced Score", "Value": stats['avg_ela_enhanced'], "Unit": "%"},
            {"Metric": "Avg Copy-Move Enhanced Score", "Value": stats['avg_cm_enhanced'], "Unit": "%"},
        ]
        
        if 'batch_success_rate' in stats:
            metrics_data.extend([
                {"Metric": "Batch Analyses", "Value": stats.get('batch_analyses', 0), "Unit": "count"},
                {"Metric": "Batch Success Rate", "Value": stats.get('batch_success_rate', 0), "Unit": "%"},
                {"Metric": "Total Batch Images", "Value": stats.get('total_batch_images', 0), "Unit": "count"},
            ])
        
        df_metrics = pd.DataFrame(metrics_data)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        
        # System Status
        st.subheader("🔧 System Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Backend status check
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Backend: Online")
                else:
                    st.warning("⚠️ Backend: Issues detected")
            except:
                st.error("❌ Backend: Offline")
        
        with col2:
            # Database status
            if os.path.exists(self.db_path):
                db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
                st.info(f"💾 Database: {db_size:.2f} MB")
            else:
                st.error("❌ Database: Not found")
        
        with col3:
            # Storage status
            uploads_dir = Path("uploads")
            if uploads_dir.exists():
                uploads_size = sum(f.stat().st_size for f in uploads_dir.rglob('*')) / (1024 * 1024)
                st.info(f"📁 Storage: {uploads_size:.2f} MB")
            else:
                st.warning("⚠️ Storage: No uploads directory")
        
        # Export Data
        st.markdown("---")
        st.subheader("📥 Export Performance Data")
        
        if st.button("Export All Performance Data", use_container_width=True):
            # Create comprehensive export
            export_data = {
                'summary': {
                    'total_analyses': stats['total_analyses'],
                    'fake_count': stats['fake_count'],
                    'high_risk_count': stats['high_risk_count'],
                    'avg_cnn_confidence': stats['avg_cnn_confidence'],
                    'avg_ela_enhanced': stats['avg_ela_enhanced'],
                    'avg_cm_enhanced': stats['avg_cm_enhanced']
                },
                'daily_trend': stats['daily_trend'],
                'risk_distribution': stats['risk_distribution']
            }
            
            # Convert to JSON for download
            import json
            json_data = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="Download Performance Data (JSON)",
                data=json_data,
                file_name=f"truthlens_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# Streamlit page integration
def performance_dashboard_page():
    """Main performance dashboard page"""
    monitor = PerformanceMonitor()
    monitor.create_performance_dashboard()

# For direct execution
if __name__ == "__main__":
    performance_dashboard_page()