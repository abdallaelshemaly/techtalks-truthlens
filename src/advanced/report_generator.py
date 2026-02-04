import json
import datetime
import base64
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Try to import from utils (optional)
try:
    from utils.logger import setup_logger

    logger = setup_logger("report_generator")
    USE_LOGGER = True
except ImportError:
    USE_LOGGER = False
    print("⚠️  Logger not available - using print statements")


class ImprovedReportGenerator:
    """
    Enhanced report generator using only requirements.txt packages
    """

    def __init__(self, reports_dir: Optional[Path] = None):
        """
        Initialize report generator

        Args:
            reports_dir: Directory to save reports (default: reports/)
        """
        self.reports_dir = Path(reports_dir) if reports_dir else Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        if USE_LOGGER:
            logger.info(f"ReportGenerator initialized. Saving to: {self.reports_dir}")
        else:
            print(f"📁 Reports will be saved to: {self.reports_dir}")

    def generate_json_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive JSON report

        Args:
            results: Analysis results dictionary

        Returns:
            Complete JSON report as dictionary with report_path
        """
        try:
            # Generate unique report ID
            report_id = results.get(
                "analysis_id",
                f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

            # Create comprehensive report
            report = {
                "metadata": {
                    "report_id": report_id,
                    "generated_at": datetime.datetime.now().isoformat(),
                    "system_version": "TruthLens 1.0",
                    "format_version": "1.1",
                },
                "analysis_summary": {
                    "filename": results.get("filename", "unknown"),
                    "uploaded_at": results.get(
                        "created_at", datetime.datetime.now().isoformat()
                    ),
                    "processing_time": results.get("processing_time", 0),
                    "overall_risk_level": results.get("risk_level", "UNKNOWN"),
                    "overall_risk_score": results.get(
                        "overall_risk_score", results.get("cnn_confidence", 0)
                    ),
                    "final_verdict": results.get(
                        "cnn_prediction", results.get("prediction", "UNKNOWN")
                    ),
                },
                "detailed_results": {
                    "cnn_analysis": {
                        "prediction": results.get(
                            "cnn_prediction", results.get("prediction", "unknown")
                        ),
                        "confidence": results.get(
                            "cnn_confidence", results.get("confidence", 0)
                        ),
                        "model_version": results.get(
                            "cnn_model_version", "ResNet50_v1"
                        ),
                    },
                    "forensic_analysis": {
                        "ela_score": results.get("ela_score", 0),
                        "copy_move_score": results.get("copy_move_score", 0),
                        "metadata_score": results.get("metadata_score", 100),
                        "anomalies": results.get("forensic_anomalies", []),
                        "combined_score": self._calculate_forensic_score(results),
                    },
                },
                "visualizations": {
                    "risk_gauge": self._create_risk_gauge_ascii(
                        results.get(
                            "overall_risk_score", results.get("cnn_confidence", 0)
                        )
                    ),
                    "confidence_meter": self._create_confidence_meter_ascii(
                        results.get("cnn_confidence", results.get("confidence", 0))
                    ),
                    "forensic_chart": self._create_forensic_chart_ascii(results),
                },
                "explanations": self._generate_explanations(results),
                "recommendations": self._generate_recommendations(results),
                "evidence": {
                    "original_image": results.get("file_path", ""),
                    "ela_image": results.get("ela_image_path", ""),
                    "processing_logs": results.get("processing_logs", []),
                },
            }

            # Save JSON file with unique name
            report_path = self.reports_dir / f"{report_id}.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            report["report_path"] = str(report_path)

            if USE_LOGGER:
                logger.info(f"JSON report generated: {report_path}")
            else:
                print(f"✅ JSON report saved: {report_path}")

            return report

        except Exception as e:
            error_msg = f"Error generating JSON report: {e}"
            if USE_LOGGER:
                logger.error(error_msg)
            else:
                print(f"❌ {error_msg}")
            raise

    def generate_text_report(self, results: Dict[str, Any]) -> Path:
        """
        Generate formatted text report

        Args:
            results: Analysis results

        Returns:
            Path to generated text file
        """
        try:
            # First generate JSON for structure
            json_report = self.generate_json_report(results)
            report_id = json_report["metadata"]["report_id"]

            # Create text report
            txt_path = self.reports_dir / f"{report_id}.txt"

            with open(txt_path, "w", encoding="utf-8") as f:
                self._write_text_report(f, json_report)

            if USE_LOGGER:
                logger.info(f"Text report generated: {txt_path}")
            else:
                print(f"✅ Text report saved: {txt_path}")

            return txt_path

        except Exception as e:
            error_msg = f"Error generating text report: {e}"
            if USE_LOGGER:
                logger.error(error_msg)
            else:
                print(f"❌ {error_msg}")
            raise

    def generate_html_report(self, results: Dict[str, Any]) -> Path:
        """
        Generate HTML report with inline CSS

        Args:
            results: Analysis results

        Returns:
            Path to generated HTML file
        """
        try:
            json_report = self.generate_json_report(results)
            report_id = json_report["metadata"]["report_id"]

            # Create HTML with inline CSS (no external dependencies)
            html_content = self._create_html_report(json_report)

            html_path = self.reports_dir / f"{report_id}.html"

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            if USE_LOGGER:
                logger.info(f"HTML report generated: {html_path}")
            else:
                print(f"✅ HTML report saved: {html_path}")

            return html_path

        except Exception as e:
            error_msg = f"Error generating HTML report: {e}"
            if USE_LOGGER:
                logger.error(error_msg)
            else:
                print(f"❌ {error_msg}")
            raise

    def _write_text_report(self, file_handle, json_report: Dict[str, Any]):
        """Write formatted text report"""
        # Header with ASCII art
        file_handle.write("╔" + "═" * 68 + "╗\n")
        file_handle.write("║" + " " * 25 + "🔍 TRUTHLENS REPORT" + " " * 25 + "║\n")
        file_handle.write("╚" + "═" * 68 + "╝\n\n")

        # Basic info
        file_handle.write("📋 REPORT INFORMATION\n")
        file_handle.write("─" * 40 + "\n")
        file_handle.write(f"Report ID:    {json_report['metadata']['report_id']}\n")
        file_handle.write(f"Generated:    {json_report['metadata']['generated_at']}\n")
        file_handle.write(
            f"System:       {json_report['metadata']['system_version']}\n\n"
        )

        # Analysis Summary
        file_handle.write("📊 ANALYSIS SUMMARY\n")
        file_handle.write("─" * 40 + "\n")
        summary = json_report["analysis_summary"]
        file_handle.write(f"Filename:          {summary['filename']}\n")
        file_handle.write(f"Final Verdict:     {summary['final_verdict']}\n")
        file_handle.write(f"Risk Level:        {summary['overall_risk_level']}\n")
        file_handle.write(f"Risk Score:        {summary['overall_risk_score']:.1f}%\n")
        file_handle.write(
            f"Processing Time:   {summary['processing_time']} seconds\n\n"
        )

        # Risk Gauge
        file_handle.write("📈 RISK ASSESSMENT\n")
        file_handle.write("─" * 40 + "\n")
        file_handle.write(json_report["visualizations"]["risk_gauge"] + "\n\n")

        # CNN Results
        file_handle.write("🤖 CNN ANALYSIS\n")
        file_handle.write("─" * 40 + "\n")
        cnn = json_report["detailed_results"]["cnn_analysis"]
        file_handle.write(f"Prediction:        {cnn['prediction']}\n")
        file_handle.write(f"Confidence:        {cnn['confidence']:.1f}%\n")
        file_handle.write(f"Model Version:     {cnn['model_version']}\n\n")

        # Confidence Meter
        file_handle.write("Confidence Level:\n")
        file_handle.write(json_report["visualizations"]["confidence_meter"] + "\n\n")

        # Forensic Results
        file_handle.write("🔍 FORENSIC ANALYSIS\n")
        file_handle.write("─" * 40 + "\n")
        forensic = json_report["detailed_results"]["forensic_analysis"]
        file_handle.write(f"ELA Score:         {forensic['ela_score']:.1f}%\n")
        file_handle.write(f"Copy-Move Score:   {forensic['copy_move_score']:.1f}%\n")
        file_handle.write(f"Metadata Score:    {forensic['metadata_score']:.1f}%\n")
        file_handle.write(f"Combined Score:    {forensic['combined_score']:.1f}%\n\n")

        # Forensic Chart
        file_handle.write("Forensic Breakdown:\n")
        file_handle.write(json_report["visualizations"]["forensic_chart"] + "\n\n")

        # Recommendations
        file_handle.write("💡 RECOMMENDATIONS\n")
        file_handle.write("─" * 40 + "\n")
        for rec in json_report["recommendations"]:
            file_handle.write(f"• {rec}\n")

        # Footer
        file_handle.write("\n" + "═" * 70 + "\n")
        file_handle.write("Generated by TruthLens Deepfake Detection System\n")
        file_handle.write("=" * 70 + "\n")

    def _create_html_report(self, json_report: Dict[str, Any]) -> str:
        """Create HTML report with inline styling"""
        risk_level = json_report["analysis_summary"]["overall_risk_level"].lower()

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
    <title>TruthLens Report - {json_report['metadata']['report_id']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .section {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            color: #667eea;
            margin: 0 0 20px 0;
            font-size: 1.5em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }}
        .info-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .info-card h4 {{
            margin: 0 0 10px 0;
            color: #555;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .info-card p {{
            margin: 0;
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        .risk-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            background-color: {risk_color['color']};
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .progress-container {{
            margin: 20px 0;
        }}
        .progress-bar {{
            height: 25px;
            background-color: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, {risk_color['color']}, {risk_color['color']}cc);
            text-align: center;
            color: white;
            line-height: 25px;
            font-size: 14px;
            font-weight: bold;
            transition: width 1s ease-in-out;
        }}
        .ascii-art {{
            font-family: 'Courier New', monospace;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            white-space: pre;
            font-size: 12px;
            line-height: 1.4;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }}
        .recommendation-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .recommendation-list li {{
            padding: 15px;
            margin-bottom: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            border-radius: 0 8px 8px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .recommendation-list li:before {{
            content: "✅";
            font-size: 1.2em;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            background-color: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        @media (max-width: 768px) {{
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            .header h1 {{
                font-size: 2em;
            }}
            .section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 TruthLens Analysis Report</h1>
            <p>Comprehensive Deepfake Detection Results</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">📋 Report Information</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h4>Report ID</h4>
                    <p>{json_report['metadata']['report_id']}</p>
                </div>
                <div class="info-card">
                    <h4>Generated At</h4>
                    <p>{json_report['metadata']['generated_at']}</p>
                </div>
                <div class="info-card">
                    <h4>System Version</h4>
                    <p>{json_report['metadata']['system_version']}</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 Analysis Summary</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h4>Filename</h4>
                    <p>{json_report['analysis_summary']['filename']}</p>
                </div>
                <div class="info-card">
                    <h4>Overall Risk</h4>
                    <p><span class="risk-badge">{json_report['analysis_summary']['overall_risk_level']}</span></p>
                </div>
                <div class="info-card">
                    <h4>Risk Score</h4>
                    <p>{json_report['analysis_summary']['overall_risk_score']:.1f}%</p>
                </div>
                <div class="info-card">
                    <h4>Final Verdict</h4>
                    <p>{json_report['analysis_summary']['final_verdict']}</p>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {json_report['analysis_summary']['overall_risk_score']}%;">
                        {json_report['analysis_summary']['overall_risk_score']:.1f}%
                    </div>
                </div>
            </div>
            
            <div class="ascii-art">
{json_report['visualizations']['risk_gauge']}
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🤖 CNN Analysis</h2>
            <table>
                <tr>
                    <th>Prediction</th>
                    <td>{json_report['detailed_results']['cnn_analysis']['prediction']}</td>
                </tr>
                <tr>
                    <th>Confidence</th>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {json_report['detailed_results']['cnn_analysis']['confidence']}%;">
                                {json_report['detailed_results']['cnn_analysis']['confidence']:.1f}%
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>Model Version</th>
                    <td>{json_report['detailed_results']['cnn_analysis']['model_version']}</td>
                </tr>
            </table>
            
            <div class="ascii-art">
{json_report['visualizations']['confidence_meter']}
            </div>
            
            <p><strong>Explanation:</strong> {json_report['explanations']['cnn']}</p>
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
                    <td>{json_report['detailed_results']['forensic_analysis']['ela_score']:.1f}%</td>
                    <td>Detects compression inconsistencies</td>
                </tr>
                <tr>
                    <td>Copy-Move Detection</td>
                    <td>{json_report['detailed_results']['forensic_analysis']['copy_move_score']:.1f}%</td>
                    <td>Identifies duplicated regions</td>
                </tr>
                <tr>
                    <td>Metadata Analysis</td>
                    <td>{json_report['detailed_results']['forensic_analysis']['metadata_score']:.1f}%</td>
                    <td>Checks for editing software traces</td>
                </tr>
            </table>
            
            <div class="ascii-art">
{json_report['visualizations']['forensic_chart']}
            </div>
            
            <p><strong>Explanation:</strong> {json_report['explanations']['forensic']}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">💡 Recommendations</h2>
            <ul class="recommendation-list">
"""

        # Add recommendations
        for rec in json_report["recommendations"]:
            html += f"                <li>{rec}</li>\n"

        html += """            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by TruthLens Deepfake Detection System</p>
            <p>Report Format Version: {json_report['metadata']['format_version']}</p>
            <p>© 2024 TruthLens Project. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""

        return html

    def _calculate_forensic_score(self, results: Dict[str, Any]) -> float:
        """Calculate combined forensic score"""
        ela = results.get("ela_score", 0)
        copy_move = results.get("copy_move_score", 0)
        metadata = results.get("metadata_score", 100)  # Default 100 = good

        # Weighted average
        return ela * 0.4 + copy_move * 0.4 + (100 - metadata) * 0.2

    def _create_risk_gauge_ascii(self, risk_score: float) -> str:
        """Create ASCII art risk gauge"""
        width = 50
        filled = int(width * risk_score / 100)

        # Create gauge with better visualization
        gauge = "┌" + "─" * width + "┐\n"
        gauge += "│" + "█" * filled + "░" * (width - filled) + "│\n"
        gauge += "└" + "─" * width + "┘\n"
        gauge += "0%" + " " * (width - 6) + "100%\n"
        gauge += " " * (filled - 1) + "↑\n"
        gauge += " " * (filled - 4) + f"{risk_score:.1f}% Risk"

        return gauge

    def _create_confidence_meter_ascii(self, confidence: float) -> str:
        """Create ASCII art confidence meter"""
        width = 40
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

        meter = (
            f"Confidence: {char * filled}{' ' * (width - filled)} {confidence:.1f}%\n"
        )
        meter += "           " + " " * (filled - 3) + "↑\n"
        meter += "           " + level

        return meter

    def _create_forensic_chart_ascii(self, results: Dict[str, Any]) -> str:
        """Create ASCII bar chart for forensic scores"""
        ela = results.get("ela_score", 0)
        copy_move = results.get("copy_move_score", 0)
        metadata = results.get("metadata_score", 100)

        chart = "Forensic Analysis Breakdown:\n"
        chart += "ELA:          " + "█" * int(ela / 5) + f" {ela:.1f}%\n"
        chart += "Copy-Move:    " + "█" * int(copy_move / 5) + f" {copy_move:.1f}%\n"
        chart += "Metadata:     " + "█" * int(metadata / 5) + f" {metadata:.1f}%\n"
        chart += "             0%    25%   50%   75%   100%"

        return chart

    def _generate_explanations(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate explanations for results"""
        confidence = results.get("cnn_confidence", results.get("confidence", 0))
        risk_level = results.get("risk_level", "UNKNOWN")

        explanations = {
            "cnn": self._get_cnn_explanation(confidence),
            "forensic": self._get_forensic_explanation(results),
            "risk": self._get_risk_explanation(risk_level),
        }

        return explanations

    def _get_cnn_explanation(self, confidence: float) -> str:
        """Generate CNN explanation"""
        if confidence >= 90:
            return f"The CNN model shows very strong confidence ({confidence:.1f}%) in its prediction."
        elif confidence >= 70:
            return f"The CNN model is confident ({confidence:.1f}%) in its assessment."
        elif confidence >= 50:
            return f"The CNN model shows moderate confidence ({confidence:.1f}%)."
        else:
            return f"The CNN model has low confidence ({confidence:.1f}%). Consider additional verification."

    def _get_forensic_explanation(self, results: Dict[str, Any]) -> str:
        """Generate forensic explanation"""
        ela = results.get("ela_score", 0)
        copy_move = results.get("copy_move_score", 0)
        metadata = results.get("metadata_score", 100)

        explanations = []

        if ela > 70:
            explanations.append("High ELA score suggests possible image manipulation.")
        elif ela > 40:
            explanations.append("Moderate ELA score may indicate editing.")

        if copy_move > 70:
            explanations.append("High copy-move detection suggests duplicated regions.")

        if metadata < 50:
            explanations.append("Low metadata trust indicates editing software traces.")

        if explanations:
            return " ".join(explanations)
        return "No significant forensic anomalies detected."

    def _get_risk_explanation(self, risk_level: str) -> str:
        """Generate risk explanation"""
        explanations = {
            "HIGH": "Multiple indicators suggest high probability of manipulation.",
            "MEDIUM": "Some evidence of possible manipulation. Further review recommended.",
            "LOW": "Minimal evidence of manipulation detected.",
            "UNKNOWN": "Insufficient data for risk assessment.",
        }
        return explanations.get(risk_level, "Risk level assessment completed.")

    def _generate_recommendations(self, results: Dict[str, Any]) -> list:
        """Generate recommendations based on analysis"""
        recommendations = []
        risk_level = results.get("risk_level", "UNKNOWN")

        # Base recommendations
        if risk_level == "HIGH":
            recommendations.extend(
                [
                    "Exercise extreme caution when using this image",
                    "Verify the original source and context",
                    "Do not use for authentication or verification purposes",
                    "Consider additional expert analysis if critical",
                ]
            )
        elif risk_level == "MEDIUM":
            recommendations.extend(
                [
                    "Verify the image source and provenance",
                    "Cross-check with alternative verification methods",
                    "Use with caution in professional contexts",
                    "Consider manual inspection if important",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Image appears authentic based on available analysis",
                    "Standard verification protocols are sufficient",
                    "Maintain standard digital security practices",
                ]
            )

        # Forensic-specific recommendations
        if results.get("ela_score", 0) > 70:
            recommendations.append(
                "High compression inconsistency detected - image may have been re-saved multiple times."
            )

        if results.get("copy_move_score", 0) > 70:
            recommendations.append(
                "Duplicate regions detected - may indicate object cloning or removal."
            )

        if results.get("metadata_score", 100) < 30:
            recommendations.append(
                "Suspicious metadata found - verify creation source."
            )

        return recommendations


# Test function
def test_improved_generator():
    """Test the improved report generator"""

    # Sample data
    test_data = {
        "analysis_id": "demo_001",
        "filename": "suspicious_image.jpg",
        "cnn_prediction": "FAKE",
        "cnn_confidence": 87.5,
        "ela_score": 72.0,
        "copy_move_score": 45.0,
        "metadata_score": 25.0,
        "risk_level": "HIGH",
        "overall_risk_score": 82.5,
        "created_at": datetime.datetime.now().isoformat(),
        "processing_time": 3.2,
        "forensic_anomalies": ["Inconsistent compression", "Photoshop metadata"],
        "file_path": "/uploads/suspicious_image.jpg",
    }

    print("🧪 Testing Improved Report Generator...")
    print("=" * 60)

    try:
        generator = ImprovedReportGenerator()

        print("\n1. Testing JSON report...")
        json_report = generator.generate_json_report(test_data)
        print(f"   ✅ JSON saved: {json_report['report_path']}")

        print("\n2. Testing Text report...")
        txt_path = generator.generate_text_report(test_data)
        print(f"   ✅ Text saved: {txt_path}")

        print("\n3. Testing HTML report...")
        html_path = generator.generate_html_report(test_data)
        print(f"   ✅ HTML saved: {html_path}")

        print("\n" + "=" * 60)
        print("🎉 All reports generated successfully!")
        print(f"   Output folder: {generator.reports_dir}")

        # Show sample data
        print("\n📊 Sample Report Summary:")
        print(f"   Risk Level: {json_report['analysis_summary']['overall_risk_level']}")
        print(
            f"   CNN Confidence: {json_report['detailed_results']['cnn_analysis']['confidence']:.1f}%"
        )
        print(f"   Recommendations: {len(json_report['recommendations'])}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_improved_generator()
    if success:
        print("\n✨ ImprovedReportGenerator is ready for production!")
    else:
        print("\n⚠️  Please check the error above and fix.")
