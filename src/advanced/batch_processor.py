"""
Batch Processing Module for TruthLens
"""
import os
import uuid
import json
import csv
import threading
import queue
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import streamlit as st
import requests
from PIL import Image
import time

class BatchProcessor:
    def __init__(self, backend_url="http://localhost:8000", max_workers=3):
        self.backend_url = backend_url
        self.max_workers = max_workers
        self.results_dir = Path("batch_results")
        self.results_dir.mkdir(exist_ok=True)
        
    def process_single_image(self, image_path, batch_id, index, total):
        """Process a single image in batch"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                response = requests.post(
                    f"{self.backend_url}/api/analyze/complete",
                    files=files,
                    timeout=45
                )
                
            if response.status_code == 200:
                result = response.json()
                return {
                    'batch_id': batch_id,
                    'index': index,
                    'filename': os.path.basename(image_path),
                    'success': True,
                    'result': result.get('result', {}),
                    'processing_time': result.get('processing_time', 0)
                }
            else:
                return {
                    'batch_id': batch_id,
                    'index': index,
                    'filename': os.path.basename(image_path),
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'processing_time': 0
                }
                
        except Exception as e:
            return {
                'batch_id': batch_id,
                'index': index,
                'filename': os.path.basename(image_path),
                'success': False,
                'error': str(e),
                'processing_time': 0
            }
    
    def process_batch(self, image_paths, progress_callback=None):
        """Process multiple images in parallel"""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        batch_dir = self.results_dir / batch_id
        batch_dir.mkdir(exist_ok=True)
        
        results = []
        total = len(image_paths)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for i, img_path in enumerate(image_paths):
                future = executor.submit(self.process_single_image, img_path, batch_id, i, total)
                futures.append((i, future))
                
                if progress_callback:
                    progress_callback(i + 1, total, f"Processing {os.path.basename(img_path)}")
            
            for i, future in futures:
                result = future.result()
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, total, f"Completed {result['filename']}")
        
        # Save batch results
        self.save_batch_results(batch_id, results)
        
        # Generate batch summary
        summary = self.generate_batch_summary(batch_id, results)
        
        return {
            'batch_id': batch_id,
            'total_images': total,
            'processed': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results,
            'summary': summary,
            'batch_dir': str(batch_dir)
        }
    
    def save_batch_results(self, batch_id, results):
        """Save batch results to JSON and CSV"""
        batch_dir = self.results_dir / batch_id
        
        # Save as JSON
        json_path = batch_dir / f"{batch_id}_results.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save as CSV
        csv_path = batch_dir / f"{batch_id}_results.csv"
        if results:
            # Extract successful results
            successful = [r for r in results if r['success']]
            if successful:
                rows = []
                for result in successful:
                    res_data = result.get('result', {})
                    rows.append({
                        'filename': result['filename'],
                        'is_fake': res_data.get('is_fake', False),
                        'cnn_confidence': res_data.get('cnn_confidence', 0),
                        'ela_score': res_data.get('ela_score', 0),
                        'ela_enhanced_score': res_data.get('ela_enhanced_score', 0),
                        'metadata_score': res_data.get('metadata_score', 0),
                        'copy_move_score': res_data.get('copy_move_score', 0),
                        'copy_move_enhanced_score': res_data.get('copy_move_enhanced_score', 0),
                        'risk_level': res_data.get('risk_level', 'UNKNOWN'),
                        'enhanced_risk_level': res_data.get('enhanced_risk_level', 'UNKNOWN'),
                        'processing_time': result.get('processing_time', 0)
                    })
                
                df = pd.DataFrame(rows)
                df.to_csv(csv_path, index=False)
        
        return str(json_path), str(csv_path) if successful else None
    
    def generate_batch_summary(self, batch_id, results):
        """Generate summary statistics for batch"""
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if not successful:
            return {
                'total': len(results),
                'successful': 0,
                'failed': len(failed),
                'avg_processing_time': 0,
                'fake_count': 0,
                'real_count': 0,
                'high_risk_count': 0,
                'success_rate': 0
            }
        
        # Calculate statistics
        fake_count = sum(1 for r in successful if r.get('result', {}).get('is_fake', False))
        high_risk_count = sum(1 for r in successful if r.get('result', {}).get('risk_level') == 'HIGH')
        avg_processing_time = sum(r.get('processing_time', 0) for r in successful) / len(successful)
        
        return {
            'total': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'avg_processing_time': round(avg_processing_time, 2),
            'fake_count': fake_count,
            'real_count': len(successful) - fake_count,
            'high_risk_count': high_risk_count,
            'success_rate': round((len(successful) / len(results)) * 100, 2)
        }
    
    def generate_batch_report(self, batch_id):
        """Generate comprehensive batch report"""
        batch_dir = self.results_dir / batch_id
        json_path = batch_dir / f"{batch_id}_results.json"
        
        if not json_path.exists():
            return None
        
        with open(json_path, 'r') as f:
            results = json.load(f)
        
        successful = [r for r in results if r['success']]
        summary = self.generate_batch_summary(batch_id, results)
        
        # Generate HTML report
        report_path = batch_dir / f"{batch_id}_report.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TruthLens Batch Report - {batch_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #1E88E5; color: white; padding: 20px; border-radius: 10px; }}
                .summary {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px 20px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; }}
                .metric-label {{ color: #666; }}
                .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .results-table th, .results-table td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
                .results-table th {{ background: #f2f2f2; }}
                .risk-high {{ color: #dc3545; font-weight: bold; }}
                .risk-medium {{ color: #ffc107; font-weight: bold; }}
                .risk-low {{ color: #28a745; font-weight: bold; }}
                .footer {{ margin-top: 40px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 TruthLens Batch Analysis Report</h1>
                <p>Batch ID: {batch_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Batch Summary</h2>
                <div class="metric">
                    <div class="metric-value">{summary['total']}</div>
                    <div class="metric-label">Total Images</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['successful']}</div>
                    <div class="metric-label">Successful</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['failed']}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['success_rate']}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['fake_count']}</div>
                    <div class="metric-label">Fake Detected</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['high_risk_count']}</div>
                    <div class="metric-label">High Risk</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['avg_processing_time']}s</div>
                    <div class="metric-label">Avg Time/Image</div>
                </div>
            </div>
            
            <h2>📋 Detailed Results</h2>
            <table class="results-table">
                <tr>
                    <th>Filename</th>
                    <th>CNN Prediction</th>
                    <th>CNN Confidence</th>
                    <th>ELA Score</th>
                    <th>Copy-Move</th>
                    <th>Risk Level</th>
                    <th>Processing Time</th>
                </tr>
        """
        
        for result in successful[:50]:  # Limit to first 50 for readability
            res_data = result.get('result', {})
            is_fake = res_data.get('is_fake', False)
            risk_level = res_data.get('risk_level', 'UNKNOWN')
            
            html_content += f"""
                <tr>
                    <td>{result['filename']}</td>
                    <td>{"FAKE" if is_fake else "REAL"}</td>
                    <td>{res_data.get('cnn_confidence', 0):.1f}%</td>
                    <td>{res_data.get('ela_enhanced_score', res_data.get('ela_score', 0)):.1f}%</td>
                    <td>{res_data.get('copy_move_enhanced_score', res_data.get('copy_move_score', 0)):.1f}%</td>
                    <td class="risk-{risk_level.lower()}">{risk_level}</td>
                    <td>{result.get('processing_time', 0):.1f}s</td>
                </tr>
            """
        
        if len(successful) > 50:
            html_content += f"""
                <tr>
                    <td colspan="7" style="text-align: center; font-style: italic;">
                        ... and {len(successful) - 50} more images
                    </td>
                </tr>
            """
        
        html_content += f"""
            </table>
            
            <div class="footer">
                <p>Generated by TruthLens Batch Processor</p>
                <p>Total processing time: {sum(r.get('processing_time', 0) for r in successful):.1f} seconds</p>
                <p>© {datetime.now().year} TruthLens Project</p>
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return str(report_path)

# Streamlit component for batch processing
def batch_upload_component():
    """Streamlit component for batch upload"""
    st.markdown("### 📦 Batch Image Processing")
    
    uploaded_files = st.file_uploader(
        "Upload multiple images for batch analysis",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Select multiple images (max 20 files, 10MB each)"
    )
    
    if uploaded_files and len(uploaded_files) > 0:
        st.info(f"📁 Selected {len(uploaded_files)} images for batch processing")
        
        # Display thumbnails
        cols = st.columns(min(4, len(uploaded_files)))
        for idx, uploaded_file in enumerate(uploaded_files[:8]):  # Show first 8
            with cols[idx % 4]:
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name[:20] + "...", width=100)
                except:
                    st.write(f"📄 {uploaded_file.name[:20]}...")
        
        if len(uploaded_files) > 8:
            st.caption(f"... and {len(uploaded_files) - 8} more images")
        
        # Processing options
        col1, col2 = st.columns(2)
        with col1:
            max_workers = st.slider("Parallel workers", 1, 5, 3, 
                                   help="Number of images to process simultaneously")
        with col2:
            generate_report = st.checkbox("Generate batch report", value=True)
        
        # Process button
        if st.button("🚀 Start Batch Processing", type="primary", use_container_width=True):
            processor = BatchProcessor(max_workers=max_workers)
            
            # Save uploaded files temporarily
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            
            image_paths = []
            for uploaded_file in uploaded_files:
                temp_path = temp_dir / uploaded_file.name
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                image_paths.append(str(temp_path))
            
            # Process batch
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total, message):
                progress_bar.progress(current / total)
                status_text.text(f"{message} ({current}/{total})")
            
            try:
                with st.spinner("Processing batch..."):
                    results = processor.process_batch(image_paths, update_progress)
                
                # Display results
                st.success(f"✅ Batch processing complete!")
                
                # Summary metrics
                summary = results['summary']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Successful", summary['successful'])
                with col2:
                    st.metric("Failed", summary['failed'])
                with col3:
                    st.metric("Fake Detected", summary['fake_count'])
                with col4:
                    st.metric("Avg Time", f"{summary['avg_processing_time']}s")
                
                # Generate report if requested
                if generate_report:
                    report_path = processor.generate_batch_report(results['batch_id'])
                    if report_path:
                        st.markdown(f"📄 [Download Batch Report]({report_path})")
                
                # Download CSV
                csv_path = processor.results_dir / results['batch_id'] / f"{results['batch_id']}_results.csv"
                if csv_path.exists():
                    with open(csv_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download CSV Results",
                            data=f,
                            file_name=f"batch_results_{results['batch_id']}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                # Show failures if any
                failures = [r for r in results['results'] if not r['success']]
                if failures:
                    with st.expander("❌ Failed Images"):
                        for failure in failures:
                            st.write(f"{failure['filename']}: {failure.get('error', 'Unknown error')}")
                
            except Exception as e:
                st.error(f"Batch processing failed: {str(e)}")
            finally:
                # Cleanup temp files
                for img_path in image_paths:
                    try:
                        os.remove(img_path)
                    except:
                        pass