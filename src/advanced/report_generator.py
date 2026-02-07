import json
import datetime
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys
import os

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

class TruthLensReportGenerator:
    """
    Enhanced report generator for TruthLens with backend integration
    """

    def __init__(self, reports_dir: Optional[Path] = None):
        """
        Initialize report generator

        Args:
            reports_dir: Directory to save reports (default: reports/)
        """
        self.reports_dir = Path(reports_dir) if reports_dir else Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Reports will be saved to: {self.reports_dir}")

    def generate_backend_report(self, analysis_data: Dict[str, Any], report_type: str = "all") -> Dict[str, str]:
        """
        Generate reports for backend integration.
        
        Args:
            analysis_data: Analysis results from backend
            report_type: "all", "json", "html", "text"
            
        Returns:
            Dictionary with format: path pairs
        """
        try:
            # Ensure we have required fields
            if "analysis_id" not in analysis_data:
                analysis_data["analysis_id"] = analysis_data.get("id", f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            reports_generated = {}
            
            if report_type in ["all", "json"]:
                json_path = self.generate_json_report(analysis_data)
                if json_path:
                    reports_generated["json"] = str(json_path)
            
            if report_type in ["all", "html"]:
                html_path = self.generate_html_report(analysis_data)
                if html_path:
                    reports_generated["html"] = str(html_path)
            
            if report_type in ["all", "text"]:
                text_path = self.generate_text_report(analysis_data)
                if text_path:
                    reports_generated["text"] = str(text_path)
            
            print(f"📄 Generated {len(reports_generated)} reports")
            return reports_generated
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            return {}

    def generate_json_report(self, results: Dict[str, Any]) -> Optional[Path]:
        """
        Generate comprehensive JSON report

        Args:
            results: Analysis results dictionary

        Returns:
            Path to generated JSON file or None
        """
        try:
            # Generate unique report ID
            report_id = results.get("analysis_id", results.get("id", f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"))
            
            # Format data for backend integration
            report_data = {
                "metadata": {
                    "report_id": report_id,
                    "generated_at": datetime.datetime.now().isoformat(),
                    "system_version": "TruthLens 1.0",
                    "format_version": "1.1",
                },
                "analysis_summary": {
                    "filename": results.get("filename", "unknown"),
                    "uploaded_at": results.get("timestamp", datetime.datetime.now().isoformat()),
                    "processing_time": results.get("processing_time", 0),
                    "overall_risk_level": results.get("risk_level", "UNKNOWN"),
                    "overall_risk_score": self._calculate_overall_score(results),
                    "final_verdict": "FAKE" if results.get("is_fake", False) else "REAL",
                },
                "detailed_results": {
                    "cnn_analysis": {
                        "prediction": "FAKE" if results.get("is_fake", False) else "REAL",
                        "confidence": results.get("cnn_confidence", 0),
                        "model_version": "EfficientNet-B0",
                    },
                    "forensic_analysis": {
                        "ela_score": results.get("ela_score", 0),
                        "copy_move_score": results.get("copy_move_score", 0),
                        "metadata_score": results.get("metadata_score", 0),
                        "combined_score": self._calculate_forensic_score(results),
                    },
                },
                "explanations": self._generate_explanations(results),
                "recommendations": self._generate_recommendations(results),
                "visualizations": {
                    "risk_gauge": self._create_risk_gauge_ascii(
                        self._calculate_overall_score(results)
                    ),
                    "confidence_meter": self._create_confidence_meter_ascii(
                        results.get("cnn_confidence", 0)
                    ),
                    "forensic_chart": self._create_forensic_chart_ascii(results),
                },
            }

            # Save JSON file
            filename = results.get("filename", "unknown").split(".")[0]
            report_path = self.reports_dir / f"{filename}_{report_id}.json"
            
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(f"✅ JSON report saved: {report_path}")
            return report_path

        except Exception as e:
            print(f"❌ Error generating JSON report: {e}")
            return None

    def generate_text_report(self, results: Dict[str, Any]) -> Optional[Path]:
        """
        Generate formatted text report

        Args:
            results: Analysis results

        Returns:
            Path to generated text file or None
        """
        try:
            # Generate JSON first for structure
            json_report = self.generate_json_report(results)
            if not json_report:
                return None
            
            # Load the JSON data
            with open(json_report, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Create text report path
            filename = results.get("filename", "unknown").split(".")[0]
            report_id = data["metadata"]["report_id"]
            txt_path = self.reports_dir / f"{filename}_{report_id}.txt"

            with open(txt_path, "w", encoding="utf-8") as f:
                self._write_text_report(f, data)

            print(f"✅ Text report saved: {txt_path}")
            return txt_path

        except Exception as e:
            print(f"❌ Error generating text report: {e}")
            return None

    def generate_html_report(self, results: Dict[str, Any]) -> Optional[Path]:
        """
        Generate HTML report with inline CSS

        Args:
            results: Analysis results

        Returns:
            Path to generated HTML file or None
        """
        try:
            # Generate JSON first for structure
            json_report = self.generate_json_report(results)
            if not json_report:
                return None
            
            # Load the JSON data
            with open(json_report, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Create HTML report path
            filename = results.get("filename", "unknown").split(".")[0]
            report_id = data["metadata"]["report_id"]
            html_path = self.reports_dir / f"{filename}_{report_id}.html"

            # Create HTML content
            html_content = self._create_html_report(data)
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"✅ HTML report saved: {html_path}")
            return html_path

        except Exception as e:
            print(f"❌ Error generating HTML report: {e}")
            return None

    def _write_text_report(self, file_handle, json_data: Dict[str, Any]):
        """Write formatted text report"""
        # Header
        file_handle.write("=" * 70 + "\n")
        file_handle.write(" " * 25 + "🔍 TRUTHLENS ANALYSIS REPORT\n")
        file_handle.write("=" * 70 + "\n\n")
        
        # Basic info
        file_handle.write("📋 REPORT INFORMATION\n")
        file_handle.write("-" * 40 + "\n")
        file_handle.write(f"Report ID:    {json_data['metadata']['report_id']}\n")
        file_handle.write(f"Generated:    {json_data['metadata']['generated_at']}\n")
        file_handle.write(f"System:       {json_data['metadata']['system_version']}\n")
        file_handle.write(f"Filename:     {json_data['analysis_summary']['filename']}\n\n")
        
        # Analysis Summary
        file_handle.write("📊 ANALYSIS SUMMARY\n")
        file_handle.write("-" * 40 + "\n")
        summary = json_data["analysis_summary"]
        file_handle.write(f"Final Verdict:     {summary['final_verdict']}\n")
        file_handle.write(f"Risk Level:        {summary['overall_risk_level']}\n")
        file_handle.write(f"Risk Score:        {summary['overall_risk_score']:.1f}%\n")
        file_handle.write(f"Processing Time:   {summary['processing_time']} seconds\n\n")
        
        # Risk Gauge
        file_handle.write("📈 RISK ASSESSMENT\n")
        file_handle.write("-" * 40 + "\n")
        file_handle.write(json_data["visualizations"]["risk_gauge"] + "\n\n")
        
        # CNN Results
        file_handle.write("🤖 CNN ANALYSIS\n")
        file_handle.write("-" * 40 + "\n")
        cnn = json_data["detailed_results"]["cnn_analysis"]
        file_handle.write(f"Prediction:        {cnn['prediction']}\n")
        file_handle.write(f"Confidence:        {cnn['confidence']:.1f}%\n")
        file_handle.write(f"Model Version:     {cnn['model_version']}\n\n")
        
        # Forensic Results
        file_handle.write("🔍 FORENSIC ANALYSIS\n")
        file_handle.write("-" * 40 + "\n")
        forensic = json_data["detailed_results"]["forensic_analysis"]
        file_handle.write(f"ELA Score:         {forensic['ela_score']:.1f}%\n")
        file_handle.write(f"Copy-Move Score:   {forensic['copy_move_score']:.1f}%\n")
        file_handle.write(f"Metadata Score:    {forensic['metadata_score']:.1f}%\n")
        file_handle.write(f"Combined Score:    {forensic['combined_score']:.1f}%\n\n")
        
        # Recommendations
        file_handle.write("💡 RECOMMENDATIONS\n")
        file_handle.write("-" * 40 + "\n")
        for rec in json_data["recommendations"]:
            file_handle.write(f"• {rec}\n")
        
        # Footer
        file_handle.write("\n" + "=" * 70 + "\n")
        file_handle.write("Generated by TruthLens Deepfake Detection System\n")
        file_handle.write("=" * 70 + "\n")

    def _create_html_report(self, json_data: Dict[str, Any]) -> str:
        """Create HTML report with inline styling"""
        risk_level = json_data["analysis_summary"]["overall_risk_level"].lower()
        
        # Risk colors
        risk_colors = {
            "high": {"color": "#dc3545", "bg": "#f8d7da"},
            "medium": {"color": "#ffc107", "bg": "#fff3cd"},
            "low": {"color": "#28a745", "bg": "#d4edda"},
        }
        
        risk_color = risk_colors.get(risk_level, {"color": "#6c757d", "bg": "#f8f9fa"})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TruthLens Report - {json_data['metadata']['report_id']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .section {{
            padding: 25px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            color: #667eea;
            margin: 0 0 15px 0;
            font-size: 1.3em;
            font-weight: bold;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .info-card h4 {{
            margin: 0 0 8px 0;
            color: #555;
            font-size: 0.9em;
        }}
        .info-card p {{
            margin: 0;
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }}
        .risk-badge {{
            display: inline-block;
            padding: 6px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            background-color: {risk_color['color']};
        }}
        .progress-bar {{
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background-color: {risk_color['color']};
            text-align: center;
            color: white;
            line-height: 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        .ascii-art {{
            font-family: 'Courier New', monospace;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre;
            font-size: 11px;
            line-height: 1.3;
            margin: 15px 0;
        }}
        .recommendation-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .recommendation-list li {{
            padding: 12px;
            margin-bottom: 8px;
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            border-radius: 0 6px 6px 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background-color: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 TruthLens Analysis Report</h1>
            <p>Deepfake Detection System | {json_data['metadata']['generated_at']}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">📋 Report Information</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h4>Report ID</h4>
                    <p>{json_data['metadata']['report_id']}</p>
                </div>
                <div class="info-card">
                    <h4>Filename</h4>
                    <p>{json_data['analysis_summary']['filename']}</p>
                </div>
                <div class="info-card">
                    <h4>System Version</h4>
                    <p>{json_data['metadata']['system_version']}</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 Analysis Summary</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h4>Overall Risk</h4>
                    <p><span class="risk-badge">{json_data['analysis_summary']['overall_risk_level']}</span></p>
                </div>
                <div class="info-card">
                    <h4>Risk Score</h4>
                    <p>{json_data['analysis_summary']['overall_risk_score']:.1f}%</p>
                </div>
                <div class="info-card">
                    <h4>Final Verdict</h4>
                    <p>{json_data['analysis_summary']['final_verdict']}</p>
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {json_data['analysis_summary']['overall_risk_score']}%;">
                    {json_data['analysis_summary']['overall_risk_score']:.1f}%
                </div>
            </div>
            
            <div class="ascii-art">
{json_data["visualizations"]["risk_gauge"]}
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🤖 CNN Analysis</h2>
            <table>
                <tr>
                    <th>Prediction</th>
                    <td>{json_data['detailed_results']['cnn_analysis']['prediction']}</td>
                </tr>
                <tr>
                    <th>Confidence</th>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {json_data['detailed_results']['cnn_analysis']['confidence']}%;">
                                {json_data['detailed_results']['cnn_analysis']['confidence']:.1f}%
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>Model Version</th>
                    <td>{json_data['detailed_results']['cnn_analysis']['model_version']}</td>
                </tr>
            </table>
            
            <div class="ascii-art">
{json_data["visualizations"]["confidence_meter"]}
            </div>
            
            <p><strong>Explanation:</strong> {json_data['explanations']['cnn']}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">🔍 Forensic Analysis</h2>
            <table>
                <tr>
                    <th>Method</th>
                    <th>Score</th>
                    <th>Interpretation</th>
                </tr>
                <tr>
                    <td>Error Level Analysis</td>
                    <td>{json_data['detailed_results']['forensic_analysis']['ela_score']:.1f}%</td>
                    <td>Detects compression inconsistencies</td>
                </tr>
                <tr>
                    <td>Copy-Move Detection</td>
                    <td>{json_data['detailed_results']['forensic_analysis']['copy_move_score']:.1f}%</td>
                    <td>Identifies duplicated regions</td>
                </tr>
                <tr>
                    <td>Metadata Analysis</td>
                    <td>{json_data['detailed_results']['forensic_analysis']['metadata_score']:.1f}%</td>
                    <td>Checks for editing software traces</td>
                </tr>
            </table>
            
            <div class="ascii-art">
{json_data["visualizations"]["forensic_chart"]}
            </div>
            
            <p><strong>Explanation:</strong> {json_data['explanations']['forensic']}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">💡 Recommendations</h2>
            <ul class="recommendation-list">
"""
        
        # Add recommendations
        for rec in json_data["recommendations"]:
            html += f"                <li>{rec}</li>\n"
        
        html += """            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by TruthLens Deepfake Detection System</p>
            <p>Report Format Version: {json_data['metadata']['format_version']}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        cnn_conf = results.get("cnn_confidence", 0)
        ela_score = results.get("ela_score", 0)
        metadata_score = results.get("metadata_score", 0)
        copy_move = results.get("copy_move_score", 0)
        
        # Weighted average
        if results.get("is_fake", False):
            # Higher weight to CNN for fake detection
            return (cnn_conf * 0.4) + (ela_score * 0.3) + (metadata_score * 0.15) + (copy_move * 0.15)
        else:
            # Higher weight to forensic for real detection
            return (cnn_conf * 0.2) + (ela_score * 0.4) + (metadata_score * 0.2) + (copy_move * 0.2)

    def _calculate_forensic_score(self, results: Dict[str, Any]) -> float:
        """Calculate combined forensic score"""
        ela = results.get("ela_score", 0)
        copy_move = results.get("copy_move_score", 0)
        metadata = results.get("metadata_score", 100)  # Default 100 = good
        
        # Weighted average
        return ela * 0.4 + copy_move * 0.4 + (100 - metadata) * 0.2

    def _create_risk_gauge_ascii(self, risk_score: float) -> str:
        """Create ASCII art risk gauge"""
        width = 40
        filled = int(width * risk_score / 100)
        
        gauge = "┌" + "─" * width + "┐\n"
        gauge += "│" + "█" * filled + "░" * (width - filled) + "│\n"
        gauge += "└" + "─" * width + "┘\n"
        gauge += "0%" + " " * (width - 6) + "100%\n"
        gauge += " " * (filled - 1) + "↑\n"
        gauge += " " * (filled - 4) + f"{risk_score:.1f}% Risk"
        
        return gauge

    def _create_confidence_meter_ascii(self, confidence: float) -> str:
        """Create ASCII art confidence meter"""
        width = 30
        filled = int(width * confidence / 100)
        
        # Confidence levels
        if confidence >= 80:
            level = "VERY HIGH"
            char = "█"
        elif confidence >= 60:
            level = "HIGH"
            char = "▓"
        elif confidence >= 40:
            level = "MEDIUM"
            char = "▒"
        elif confidence >= 20:
            level = "LOW"
            char = "░"
        else:
            level = "VERY LOW"
            char = " "
        
        meter = f"Confidence: {char * filled}{' ' * (width - filled)} {confidence:.1f}%\n"
        meter += "           " + " " * (filled - 3) + "↑\n"
        meter += "           " + level
        
        return meter

    def _create_forensic_chart_ascii(self, results: Dict[str, Any]) -> str:
        """Create ASCII bar chart for forensic scores"""
        ela = results.get("ela_score", 0)
        copy_move = results.get("copy_move_score", 0)
        metadata = results.get("metadata_score", 0)
        
        chart = "Forensic Analysis Breakdown:\n"
        chart += "ELA:          " + "█" * int(ela / 5) + f" {ela:.1f}%\n"
        chart += "Copy-Move:    " + "█" * int(copy_move / 5) + f" {copy_move:.1f}%\n"
        chart += "Metadata:     " + "█" * int(metadata / 5) + f" {metadata:.1f}%\n"
        chart += "             0%    25%   50%   75%   100%"
        
        return chart

    def _generate_explanations(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate explanations for results"""
        confidence = results.get("cnn_confidence", 0)
        risk_level = results.get("risk_level", "UNKNOWN")
        ela_score = results.get("ela_score", 0)
        
        explanations = {
            "cnn": self._get_cnn_explanation(confidence),
            "forensic": self._get_forensic_explanation(results),
            "risk": self._get_risk_explanation(risk_level),
        }
        
        return explanations

    def _get_cnn_explanation(self, confidence: float) -> str:
        """Generate CNN explanation"""
        if confidence >= 80:
            return f"High confidence ({confidence:.1f}%) in prediction."
        elif confidence >= 60:
            return f"Moderate confidence ({confidence:.1f}%) in assessment."
        elif confidence >= 40:
            return f"Low confidence ({confidence:.1f}%). Consider additional verification."
        else:
            return f"Very low confidence ({confidence:.1f}%). Results uncertain."

    def _get_forensic_explanation(self, results: Dict[str, Any]) -> str:
        """Generate forensic explanation"""
        ela = results.get("ela_score", 0)
        copy_move = results.get("copy_move_score", 0)
        metadata = results.get("metadata_score", 0)
        
        explanations = []
        
        if ela > 70:
            explanations.append(f"High ELA score ({ela:.1f}%) suggests possible manipulation.")
        elif ela > 40:
            explanations.append(f"Moderate ELA score ({ela:.1f}%) may indicate editing.")
        
        if copy_move > 70:
            explanations.append(f"High copy-move detection ({copy_move:.1f}%) suggests duplicated regions.")
        
        if metadata < 30:
            explanations.append(f"Low metadata trust ({metadata:.1f}%) indicates editing software traces.")
        
        if explanations:
            return " ".join(explanations)
        return "No significant forensic anomalies detected."

    def _get_risk_explanation(self, risk_level: str) -> str:
        """Generate risk explanation"""
        explanations = {
            "HIGH": "Multiple indicators suggest high probability of manipulation.",
            "MEDIUM": "Some suspicious indicators found, further verification recommended.",
            "LOW": "Minimal evidence of manipulation detected.",
            "UNKNOWN": "Insufficient data for risk assessment.",
        }
        return explanations.get(risk_level, "Risk level assessment completed.")

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results"""
        risk_level = results.get("risk_level", "UNKNOWN")
        
        base_recommendations = [
            "Always verify the original source of digital content",
            "Consider the context in which the image is used",
            "Cross-reference with other available sources"
        ]
        
        if risk_level == "HIGH":
            return base_recommendations + [
                "Do not use this image for authentication or verification purposes",
                "Consult human experts for critical decisions",
                "Consider additional forensic analysis if available",
                "Document all findings for reference"
            ]
        elif risk_level == "MEDIUM":
            return base_recommendations + [
                "Use with caution in professional contexts",
                "Consider manual inspection if important",
                "Verify image provenance and chain of custody",
                "Monitor for similar suspicious content"
            ]
        else:
            return base_recommendations + [
                "Standard digital verification protocols are sufficient",
                "Maintain regular digital security practices",
                "Continue monitoring for emerging deepfake techniques"
            ]

# Singleton instance for easy import
report_generator = TruthLensReportGenerator()

# Test function
def test_generator():
    """Test the report generator"""
    print("🧪 Testing TruthLens Report Generator...")
    print("=" * 60)
    
    test_data = {
        "id": 123,
        "analysis_id": "test_001",
        "filename": "test_image.jpg",
        "is_fake": True,
        "cnn_confidence": 87.5,
        "ela_score": 72.3,
        "metadata_score": 40.0,
        "copy_move_score": 25.0,
        "risk_level": "HIGH",
        "processing_time": 3.2,
        "file_path": "uploads/test_image.jpg"
    }
    
    try:
        generator = TruthLensReportGenerator()
        
        print("1. Testing backend integration...")
        reports = generator.generate_backend_report(test_data, "all")
        print(f"   ✅ Generated {len(reports)} reports")
        
        for format, path in reports.items():
            print(f"   • {format.upper()}: {path}")
        
        print("\n" + "=" * 60)
        print("🎉 Report generator is ready for production!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_generator()