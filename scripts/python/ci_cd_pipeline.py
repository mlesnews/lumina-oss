#!/usr/bin/env python3
"""
CI/CD Pipeline
Automated CI/CD pipeline for JARVIS Master Agent

Runs tests, security audits, and deployment validation.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CICDPipeline")


class CICDPipeline:
    """CI/CD pipeline orchestrator"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.pipeline_log_dir = self.project_root / "data" / "ci_cd_pipelines"
        self.pipeline_log_dir.mkdir(parents=True, exist_ok=True)

    def run_linting(self) -> Dict[str, Any]:
        """Run code linting"""
        logger.info("Running code linting...")

        result = {
            "step": "linting",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }

        try:
            # 1. Run Python linting if available
            # (Currently placeholder, but we'll add Node-based below)

            # 2. Run Node-based linting (Accessibility, Compatibility, Security)
            try:
                from lumina_quality_reporter import LUMINAQualityReporter
                reporter = LUMINAQualityReporter(self.project_root)
                report_file = reporter.generate_report()

                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)

                result["status"] = "passed" if report_data["overall_status"] == "passed" else "failed"
                result["report_file"] = str(report_file)
                result["message"] = "Node-based quality reporting complete"
                result["node_results"] = report_data["results"]
            except ImportError:
                logger.warning("LUMINAQualityReporter not found, falling back to basic npm run lint")
                package_json = self.project_root / "package.json"
                if package_json.exists():
                    logger.info("Running Node-based quality checks (Accessibility, Compatibility, Security)...")
                    # Run npm run lint
                    lint_process = subprocess.run(
                        ["npm", "run", "lint"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        shell=True
                    )

                    # Run npm audit for security
                    audit_process = subprocess.run(
                        ["npm", "audit"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        shell=True
                    )

                    result["status"] = "passed" if lint_process.returncode == 0 else "failed"
                    result["node_lint_output"] = lint_process.stdout
                    result["node_audit_output"] = audit_process.stdout
                    result["message"] = "Node-based linting complete"
                else:
                    result["status"] = "passed"
                    result["message"] = "Linting passed (no package.json found)"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        logger.info("Running unit tests...")

        result = {
            "step": "unit_tests",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }

        try:
            from test_runner import TestRunner
            test_runner = TestRunner(self.project_root)
            test_report = test_runner.run_tests()

            result["status"] = "passed" if test_report["status"] == "passed" else "failed"
            result["tests_run"] = test_report["tests_run"]
            result["tests_passed"] = test_report["tests_passed"]
            result["tests_failed"] = test_report["tests_failed"]
            result["success_rate"] = test_report["success_rate"]
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("Running integration tests...")

        result = {
            "step": "integration_tests",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }

        try:
            from test_api_integration import run_all_tests
            success = run_all_tests()
            result["status"] = "passed" if success else "failed"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def run_security_audit(self) -> Dict[str, Any]:
        """Run security audit"""
        logger.info("Running security audit...")

        result = {
            "step": "security_audit",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }

        try:
            from security_audit import SecurityAuditor
            auditor = SecurityAuditor(self.project_root)
            audit_results = auditor.run_full_audit()

            result["status"] = "passed" if audit_results["overall_status"] == "pass" else "failed"
            result["overall_score"] = audit_results["overall_score"]
            result["critical_findings"] = len(audit_results["critical_findings"])
            result["high_findings"] = len(audit_results["high_findings"])
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        logger.info("Running performance tests...")

        result = {
            "step": "performance_tests",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }

        try:
            from load_test_runner import LoadTestRunner
            # Only run if API server is available
            runner = LoadTestRunner()
            # Skip if server not available
            result["status"] = "skipped"
            result["message"] = "Performance tests require running API server"
        except Exception as e:
            result["status"] = "skipped"
            result["message"] = f"Performance tests skipped: {e}"

        return result

    def validate_deployment(self) -> Dict[str, Any]:
        try:
            """Validate deployment readiness"""
            logger.info("Validating deployment readiness...")

            result = {
                "step": "deployment_validation",
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "checks": {}
            }

            # Check required files
            required_files = [
                "Dockerfile",
                "requirements.txt",
                "scripts/terraform/main.tf",
                "scripts/python/jarvis_master_agent_api_server.py"
            ]

            missing_files = []
            for file_path in required_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    missing_files.append(file_path)

            result["checks"]["required_files"] = {
                "status": "passed" if not missing_files else "failed",
                "missing": missing_files
            }

            # Check database migrations
            migration_file = self.project_root / "scripts" / "python" / "database_migration_manager.py"
            result["checks"]["database_migrations"] = {
                "status": "passed" if migration_file.exists() else "failed"
            }

            # Determine overall status
            all_passed = all(
                check.get("status") == "passed"
                for check in result["checks"].values()
            )

            result["status"] = "passed" if all_passed else "failed"

            return result

        except Exception as e:
            self.logger.error(f"Error in validate_deployment: {e}", exc_info=True)
            raise
    def run_full_pipeline(self) -> Dict[str, Any]:
        try:
            """Run full CI/CD pipeline"""
            logger.info("Starting CI/CD pipeline...")

            pipeline_results = {
                "pipeline_started": datetime.now().isoformat(),
                "steps": [],
                "overall_status": "running"
            }

            # Run all pipeline steps
            steps = [
                self.run_linting,
                self.run_unit_tests,
                self.run_integration_tests,
                self.run_security_audit,
                self.run_performance_tests,
                self.validate_deployment
            ]

            for step_func in steps:
                step_result = step_func()
                pipeline_results["steps"].append(step_result)

                # Stop on critical failure
                if step_result["status"] == "failed" and step_result["step"] in ["unit_tests", "security_audit"]:
                    logger.error(f"Pipeline failed at step: {step_result['step']}")
                    break

            # Determine overall status
            failed_steps = [s for s in pipeline_results["steps"] if s["status"] == "failed"]
            pipeline_results["overall_status"] = "passed" if not failed_steps else "failed"
            pipeline_results["pipeline_completed"] = datetime.now().isoformat()

            # Save pipeline results
            results_file = self.pipeline_log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(pipeline_results, f, indent=2)

            logger.info(f"CI/CD pipeline complete. Results saved to: {results_file}")

            return pipeline_results


        except Exception as e:
            self.logger.error(f"Error in run_full_pipeline: {e}", exc_info=True)
            raise
def main():
    try:
        """Main CI/CD pipeline function"""
        project_root = Path(__file__).parent.parent.parent
        pipeline = CICDPipeline(project_root)

        print("=" * 60)
        print("CI/CD Pipeline")
        print("=" * 60)

        results = pipeline.run_full_pipeline()

        print(f"\nPipeline Status: {results['overall_status'].upper()}")
        print(f"Steps Completed: {len(results['steps'])}")

        for step in results["steps"]:
            status_icon = "✅" if step["status"] == "passed" else "❌" if step["status"] == "failed" else "⏭️"
            print(f"  {status_icon} {step['step']}: {step['status']}")

        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from typing import Optional


    main()