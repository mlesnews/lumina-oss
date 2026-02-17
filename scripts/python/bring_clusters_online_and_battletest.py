#!/usr/bin/env python3
"""
Bring Local Clusters Online and Battletest
- Authenticates ProtonPass CLI
- Brings Iron Legion and ULTRON clusters online
- Runs comprehensive battletests
- Uses @marvin for diagnostics if issues found

Tags: #CLUSTER #BATTLETEST #MARVIN #ONLINE @JARVIS @LUMINA
"""
import sys
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("ClusterOnlineBattletest")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ClusterOnlineBattletest")


class ClusterOnlineManager:
    """Bring clusters online and battletest them"""

    def __init__(self):
        self.project_root = project_root
        self.results = []
        self.issues = []

    def authenticate_protonpass(self) -> bool:
        """Authenticate ProtonPass CLI"""
        logger.info("=" * 70)
        logger.info("🔐 AUTHENTICATING PROTONPASS CLI")
        logger.info("=" * 70)

        try:
            from protonpass_auto_login import main as auto_login
            result = auto_login()
            if result:
                logger.info("✅ ProtonPass CLI authenticated")
                return True
            else:
                logger.warning("⚠️  ProtonPass CLI authentication failed")
                return False
        except Exception as e:
            logger.error(f"❌ ProtonPass authentication error: {e}")
            return False

    def check_cluster_health(self, endpoint: str, name: str) -> Dict[str, Any]:
        """Check if a cluster endpoint is healthy"""
        try:
            response = requests.get(f"{endpoint}/health", timeout=5)
            if response.status_code == 200:
                return {"healthy": True, "status_code": 200, "response": response.json()}
            else:
                return {"healthy": False, "status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            return {"healthy": False, "error": "Connection refused"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    def start_cluster_services(self) -> Dict[str, Any]:
        """Start all cluster services"""
        logger.info("=" * 70)
        logger.info("🚀 BRINGING CLUSTERS ONLINE")
        logger.info("=" * 70)

        results = {}

        # Start cluster services script
        logger.info("📡 Starting cluster services...")
        try:
            script_path = script_dir / "start_all_cluster_services.py"
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    logger.info("✅ Cluster services started")
                    results["services"] = {"started": True}
                else:
                    logger.warning(f"⚠️  Cluster services start returned code {result.returncode}")
                    results["services"] = {"started": False, "error": result.stderr}
            else:
                logger.warning("⚠️  start_all_cluster_services.py not found")
                results["services"] = {"started": False, "error": "Script not found"}
        except Exception as e:
            logger.error(f"❌ Error starting services: {e}")
            results["services"] = {"started": False, "error": str(e)}

        # Wait for services to initialize
        logger.info("⏳ Waiting for services to initialize...")
        time.sleep(10)

        # Check Iron Legion cluster
        logger.info("🔍 Checking Iron Legion cluster (<NAS_IP>:3000)...")
        iron_legion_health = self.check_cluster_health("http://<NAS_IP>:3000", "Iron Legion")
        results["iron_legion"] = iron_legion_health

        if iron_legion_health.get("healthy"):
            logger.info("✅ Iron Legion cluster is online")
        else:
            logger.warning(f"⚠️  Iron Legion cluster is not responding: {iron_legion_health.get('error', 'Unknown')}")
            self.issues.append({
                "cluster": "Iron Legion",
                "issue": "Not responding",
                "details": iron_legion_health
            })

        # Check ULTRON local
        logger.info("🔍 Checking ULTRON local (localhost:11434)...")
        ultron_health = self.check_cluster_health("http://localhost:11434", "ULTRON")
        results["ultron"] = ultron_health

        if ultron_health.get("healthy"):
            logger.info("✅ ULTRON cluster is online")
        else:
            logger.warning(f"⚠️  ULTRON cluster is not responding: {ultron_health.get('error', 'Unknown')}")
            self.issues.append({
                "cluster": "ULTRON",
                "issue": "Not responding",
                "details": ultron_health
            })

        # Check individual Iron Legion models
        logger.info("🔍 Checking individual Iron Legion models...")
        model_results = {}
        for port in range(3001, 3008):
            model_name = f"Mark {port - 3000}"
            endpoint = f"http://<NAS_IP>:{port}"
            health = self.check_cluster_health(endpoint, model_name)
            model_results[model_name] = health
            if health.get("healthy"):
                logger.info(f"   ✅ {model_name} is online")
            else:
                logger.warning(f"   ⚠️  {model_name} is not responding")

        results["individual_models"] = model_results

        return results

    def run_battletests(self) -> Dict[str, Any]:
        """Run comprehensive battletests"""
        logger.info("=" * 70)
        logger.info("🔥 RUNNING BATTLETESTS")
        logger.info("=" * 70)

        results = {}

        # Run ULTRON battletest
        logger.info("🧪 Running ULTRON cluster battletest...")
        try:
            script_path = script_dir / "battletest_ultron_cluster.py"
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✅ ULTRON battletest passed")
                    results["ultron"] = {"passed": True, "output": result.stdout}
                else:
                    logger.warning("⚠️  ULTRON battletest had issues")
                    results["ultron"] = {"passed": False, "error": result.stderr}
                    self.issues.append({
                        "test": "ULTRON Battletest",
                        "issue": "Test failures",
                        "details": result.stderr
                    })
            else:
                logger.warning("⚠️  battletest_ultron_cluster.py not found")
        except Exception as e:
            logger.error(f"❌ ULTRON battletest error: {e}")
            results["ultron"] = {"passed": False, "error": str(e)}

        # Run Iron Legion battletest
        logger.info("🧪 Running Iron Legion battletest...")
        try:
            script_path = script_dir / "battletest_ultron_iron_legion.py"
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✅ Iron Legion battletest passed")
                    results["iron_legion"] = {"passed": True, "output": result.stdout}
                else:
                    logger.warning("⚠️  Iron Legion battletest had issues")
                    results["iron_legion"] = {"passed": False, "error": result.stderr}
                    self.issues.append({
                        "test": "Iron Legion Battletest",
                        "issue": "Test failures",
                        "details": result.stderr
                    })
            else:
                logger.warning("⚠️  battletest_ultron_iron_legion.py not found")
        except Exception as e:
            logger.error(f"❌ Iron Legion battletest error: {e}")
            results["iron_legion"] = {"passed": False, "error": str(e)}

        return results

    def use_marvin_diagnostics(self) -> Dict[str, Any]:
        """Use @marvin to diagnose issues"""
        if not self.issues:
            logger.info("✅ No issues found - MARVIN diagnostics not needed")
            return {"needed": False}

        logger.info("=" * 70)
        logger.info("🤖 MARVIN DIAGNOSTICS")
        logger.info("=" * 70)

        try:
            from security_audit_marvin_teams import MARVINSecurityAuditor

            logger.info("🔍 MARVIN: Analyzing cluster issues...")
            diagnostics = {
                "issues_found": len(self.issues),
                "issues": self.issues,
                "recommendations": []
            }

            # Analyze each issue
            for issue in self.issues:
                logger.info(f"   🔍 Analyzing: {issue.get('cluster', issue.get('test', 'Unknown'))}")

                if "Not responding" in issue.get("issue", ""):
                    diagnostics["recommendations"].append({
                        "issue": issue.get("issue"),
                        "cluster": issue.get("cluster"),
                        "action": "Check if service is running and network connectivity",
                        "priority": "high"
                    })
                elif "Test failures" in issue.get("issue", ""):
                    diagnostics["recommendations"].append({
                        "issue": issue.get("issue"),
                        "test": issue.get("test"),
                        "action": "Review test output and fix underlying issues",
                        "priority": "medium"
                    })

            logger.info(f"✅ MARVIN: Found {len(diagnostics['recommendations'])} recommendations")

            return {"needed": True, "diagnostics": diagnostics}

        except ImportError:
            logger.warning("⚠️  MARVIN diagnostics not available")
            return {"needed": True, "error": "MARVIN module not found"}
        except Exception as e:
            logger.error(f"❌ MARVIN diagnostics error: {e}")
            return {"needed": True, "error": str(e)}

    def generate_report(self) -> str:
        """Generate @rr report"""
        report = []
        report.append("=" * 70)
        report.append("📊 CLUSTER ONLINE & BATTLETEST REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")

        report.append("🔐 ProtonPass CLI:")
        report.append(f"   Status: {'✅ Authenticated' if hasattr(self, 'protonpass_auth') and self.protonpass_auth else '❌ Not authenticated'}")
        report.append("")

        report.append("🚀 Cluster Status:")
        if hasattr(self, 'cluster_status'):
            for cluster, status in self.cluster_status.items():
                if isinstance(status, dict):
                    healthy = status.get("healthy", False)
                    report.append(f"   {cluster}: {'✅ Online' if healthy else '❌ Offline'}")
        report.append("")

        report.append("🔥 Battletest Results:")
        if hasattr(self, 'battletest_results'):
            for test, result in self.battletest_results.items():
                if isinstance(result, dict):
                    passed = result.get("passed", False)
                    report.append(f"   {test}: {'✅ Passed' if passed else '❌ Failed'}")
        report.append("")

        if self.issues:
            report.append("⚠️  Issues Found:")
            for issue in self.issues:
                report.append(f"   - {issue.get('cluster', issue.get('test', 'Unknown'))}: {issue.get('issue', 'Unknown issue')}")
            report.append("")

        if hasattr(self, 'marvin_diagnostics') and self.marvin_diagnostics.get("needed"):
            report.append("🤖 MARVIN Recommendations:")
            diagnostics = self.marvin_diagnostics.get("diagnostics", {})
            for rec in diagnostics.get("recommendations", []):
                report.append(f"   [{rec.get('priority', 'unknown').upper()}] {rec.get('action', 'No action')}")
            report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def run_full_pipeline(self) -> int:
        try:
            """Run the complete pipeline"""
            logger.info("=" * 70)
            logger.info("🚀 CLUSTER ONLINE & BATTLETEST PIPELINE")
            logger.info("=" * 70)
            logger.info("")

            # Step 1: Authenticate ProtonPass
            self.protonpass_auth = self.authenticate_protonpass()
            logger.info("")

            # Step 2: Bring clusters online
            self.cluster_status = self.start_cluster_services()
            logger.info("")

            # Step 3: Run battletests
            self.battletest_results = self.run_battletests()
            logger.info("")

            # Step 4: Use MARVIN if issues found
            if self.issues:
                self.marvin_diagnostics = self.use_marvin_diagnostics()
                logger.info("")
            else:
                self.marvin_diagnostics = {"needed": False}

            # Step 5: Generate report
            report = self.generate_report()
            logger.info(report)

            # Save report
            report_file = project_root / "data" / "syphon_results" / f"cluster_online_battletest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            report_file.write_text(report)
            logger.info(f"📄 Report saved to: {report_file}")

            # Return exit code
            if self.issues:
                return 1
            return 0


        except Exception as e:
            self.logger.error(f"Error in run_full_pipeline: {e}", exc_info=True)
            raise
def main():
    manager = ClusterOnlineManager()
    return manager.run_full_pipeline()


if __name__ == "__main__":

    sys.exit(main())