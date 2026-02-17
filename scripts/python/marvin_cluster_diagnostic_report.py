#!/usr/bin/env python3
"""
MARVIN Cluster Diagnostic Report (@rr)
Generates comprehensive diagnostic report with MARVIN analysis

Tags: #MARVIN #DIAGNOSTIC #REPORT #CLUSTER @JARVIS @LUMINA
"""
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("MARVINClusterDiagnostic")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MARVINClusterDiagnostic")


class MARVINClusterDiagnostic:
    """MARVIN: Comprehensive cluster diagnostic analysis"""

    def __init__(self):
        self.findings = []
        self.recommendations = []

    def diagnose_cluster_connectivity(self) -> Dict[str, Any]:
        """MARVIN: Diagnose cluster connectivity issues"""
        logger.info("🔍 MARVIN: Diagnosing cluster connectivity...")

        findings = []

        # Test Iron Legion cluster
        try:
            response = requests.get("http://<NAS_IP>:3000/health", timeout=5)
            if response.status_code == 200:
                findings.append({
                    "cluster": "Iron Legion",
                    "status": "online",
                    "endpoint": "<NAS_IP>:3000",
                    "severity": "INFO"
                })
            else:
                findings.append({
                    "cluster": "Iron Legion",
                    "status": "responding_but_error",
                    "status_code": response.status_code,
                    "severity": "MEDIUM"
                })
        except requests.exceptions.ConnectionError:
            findings.append({
                "cluster": "Iron Legion",
                "status": "offline",
                "error": "Connection refused",
                "severity": "HIGH",
                "recommendation": "Check if Iron Legion service is running on KAIJU_NO_8 (<NAS_IP>)"
            })
        except Exception as e:
            findings.append({
                "cluster": "Iron Legion",
                "status": "unknown_error",
                "error": str(e),
                "severity": "HIGH"
            })

        # Test ULTRON local
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                findings.append({
                    "cluster": "ULTRON",
                    "status": "online",
                    "endpoint": "localhost:11434",
                    "severity": "INFO"
                })
            else:
                findings.append({
                    "cluster": "ULTRON",
                    "status": "responding_but_error",
                    "status_code": response.status_code,
                    "severity": "MEDIUM"
                })
        except requests.exceptions.ConnectionError:
            findings.append({
                "cluster": "ULTRON",
                "status": "offline",
                "error": "Connection refused",
                "severity": "HIGH",
                "recommendation": "Check if Ollama service is running locally"
            })
        except Exception as e:
            findings.append({
                "cluster": "ULTRON",
                "status": "unknown_error",
                "error": str(e),
                "severity": "HIGH"
            })

        # Test individual models
        model_findings = []
        for port in range(3001, 3008):
            model_name = f"Mark {port - 3000}"
            try:
                response = requests.get(f"http://<NAS_IP>:{port}/health", timeout=3)
                if response.status_code == 200:
                    model_findings.append({
                        "model": model_name,
                        "port": port,
                        "status": "online",
                        "severity": "INFO"
                    })
                else:
                    model_findings.append({
                        "model": model_name,
                        "port": port,
                        "status": "error",
                        "status_code": response.status_code,
                        "severity": "MEDIUM"
                    })
            except requests.exceptions.ConnectionError:
                model_findings.append({
                    "model": model_name,
                    "port": port,
                    "status": "offline",
                    "severity": "MEDIUM",
                    "recommendation": f"Check if {model_name} service is running on port {port}"
                })
            except Exception as e:
                model_findings.append({
                    "model": model_name,
                    "port": port,
                    "status": "unknown_error",
                    "error": str(e),
                    "severity": "MEDIUM"
                })

        findings.append({
            "category": "individual_models",
            "models": model_findings
        })

        return {"findings": findings}

    def generate_recommendations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """MARVIN: Generate actionable recommendations"""
        recommendations = []

        for finding in findings:
            if finding.get("severity") in ["HIGH", "MEDIUM"]:
                if finding.get("status") == "offline":
                    recommendations.append({
                        "priority": finding.get("severity"),
                        "cluster": finding.get("cluster", finding.get("model", "Unknown")),
                        "issue": finding.get("error", "Service offline"),
                        "action": finding.get("recommendation", "Investigate service status"),
                        "category": "connectivity"
                    })

        return recommendations

    def generate_report(self) -> str:
        """Generate comprehensive @rr report"""
        logger.info("=" * 70)
        logger.info("🤖 MARVIN CLUSTER DIAGNOSTIC REPORT (@rr)")
        logger.info("=" * 70)

        # Run diagnostics
        connectivity = self.diagnose_cluster_connectivity()
        findings = connectivity.get("findings", [])
        recommendations = self.generate_recommendations(findings)

        # Build report
        report = []
        report.append("=" * 70)
        report.append("🤖 MARVIN CLUSTER DIAGNOSTIC REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")

        report.append("📊 CLUSTER STATUS:")
        report.append("")

        for finding in findings:
            if "category" not in finding:
                cluster = finding.get("cluster", "Unknown")
                status = finding.get("status", "unknown")
                severity = finding.get("severity", "INFO")

                status_icon = "✅" if status == "online" else "❌" if status == "offline" else "⚠️"
                report.append(f"   {status_icon} {cluster}: {status.upper()} [{severity}]")
                if finding.get("error"):
                    report.append(f"      Error: {finding.get('error')}")
                if finding.get("recommendation"):
                    report.append(f"      Recommendation: {finding.get('recommendation')}")

        report.append("")
        report.append("🔧 INDIVIDUAL MODELS:")
        report.append("")

        for finding in findings:
            if finding.get("category") == "individual_models":
                models = finding.get("models", [])
                online_count = sum(1 for m in models if m.get("status") == "online")
                total_count = len(models)

                report.append(f"   Status: {online_count}/{total_count} models online")
                report.append("")

                for model in models:
                    status_icon = "✅" if model.get("status") == "online" else "❌"
                    report.append(f"   {status_icon} {model.get('model')} (port {model.get('port')}): {model.get('status')}")

        report.append("")
        report.append("=" * 70)
        report.append("🎯 MARVIN RECOMMENDATIONS")
        report.append("=" * 70)
        report.append("")

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. [{rec.get('priority')}] {rec.get('cluster')}")
                report.append(f"   Issue: {rec.get('issue')}")
                report.append(f"   Action: {rec.get('action')}")
                report.append("")
        else:
            report.append("✅ No critical issues found")
            report.append("")

        report.append("=" * 70)
        report.append("📋 NEXT STEPS")
        report.append("=" * 70)
        report.append("")
        report.append("1. Review cluster connectivity findings above")
        report.append("2. Address HIGH priority recommendations first")
        report.append("3. Verify services are running on expected endpoints")
        report.append("4. Re-run battletests after fixes")
        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


def main():
    try:
        diagnostic = MARVINClusterDiagnostic()
        report = diagnostic.generate_report()

        logger.info("")
        logger.info(report)

        # Save report
        report_file = project_root / "data" / "syphon_results" / f"marvin_cluster_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report)
        logger.info(f"📄 Report saved to: {report_file}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())