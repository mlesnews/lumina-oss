#!/usr/bin/env python3
"""
LUMINA Quality Reporter
<COMPANY_NAME> LLC

Automated reporting of issues in source files pertaining to:
- Accessibility (pa11y-ci)
- Compatibility (eslint-plugin-compat)
- Security (eslint-plugin-security, npm audit)
- Code Standards (eslint)

Tags: #QUALITY #REPORTING #ACCESSIBILITY #SECURITY #COMPATIBILITY @JARVIS @LUMINA @PEAK
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINAQualityReporter")

class LUMINAQualityReporter:
    """Orchestrates and reports on project quality metrics"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.reports_dir = self.project_root / "data" / "quality_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def check_node_npm(self) -> Dict[str, Any]:
        """Check if node and npm are installed and working"""
        results = {"node": False, "npm": False, "versions": {}}

        try:
            node_v = subprocess.check_output(["node", "-v"], text=True, shell=True).strip()
            results["node"] = True
            results["versions"]["node"] = node_v
        except Exception as e:
            logger.error(f"Node.js not found: {e}")

        try:
            npm_v = subprocess.check_output(["npm", "-v"], text=True, shell=True).strip()
            results["npm"] = True
            results["versions"]["npm"] = npm_v
        except Exception as e:
            logger.error(f"NPM not found: {e}")

        return results

    def run_npm_script(self, script_name: str) -> Dict[str, Any]:
        """Run a specific npm script and capture output"""
        logger.info(f"Running npm script: {script_name}")

        try:
            process = subprocess.run(
                ["npm", "run", script_name],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=True
            )

            return {
                "script": script_name,
                "status": "passed" if process.returncode == 0 else "failed",
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr
            }
        except Exception as e:
            logger.error(f"Error running npm script {script_name}: {e}")
            return {
                "script": script_name,
                "status": "error",
                "error": str(e)
            }

    def run_npm_audit(self) -> Dict[str, Any]:
        """Run npm audit for security"""
        logger.info("Running npm audit...")

        try:
            # Using --json for easier parsing if needed, but for reporting we might want the text
            process = subprocess.run(
                ["npm", "audit"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=True
            )

            return {
                "step": "npm_audit",
                "status": "passed" if process.returncode == 0 else "vulnerabilities_found",
                "output": process.stdout
            }
        except Exception as e:
            logger.error(f"Error running npm audit: {e}")
            return {"step": "npm_audit", "status": "error", "error": str(e)}

    def generate_report(self) -> Path:
        try:
            """Run all quality checks and generate a comprehensive report"""
            logger.info("=" * 60)
            logger.info("LUMINA QUALITY REPORT GENERATION")
            logger.info("=" * 60)

            report_data = {
                "timestamp": datetime.now().isoformat(),
                "environment": self.check_node_npm(),
                "results": {}
            }

            if not report_data["environment"]["node"] or not report_data["environment"]["npm"]:
                logger.error("Node/NPM missing. Cannot run quality checks.")
                report_data["status"] = "failed"
                report_data["error"] = "Node/NPM missing"
            else:
                # Check package.json exists
                if not (self.project_root / "package.json").exists():
                    logger.error("package.json not found in project root.")
                    report_data["status"] = "failed"
                    report_data["error"] = "package.json missing"
                else:
                    # Run quality scripts
                    scripts = ["lint", "accessibility", "security"]
                    for script in scripts:
                        report_data["results"][script] = self.run_npm_script(script)

                    # Run npm audit
                    report_data["results"]["audit"] = self.run_npm_audit()

                    # Determine overall status
                    all_passed = all(
                        res["status"] == "passed" 
                        for res in report_data["results"].values()
                    )
                    report_data["overall_status"] = "passed" if all_passed else "issues_detected"

            # Save report
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"quality_report_{timestamp_str}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)

            logger.info(f"Quality report generated: {report_file}")

            # Also generate a summary markdown report
            self._generate_markdown_summary(report_data, timestamp_str)

            return report_file

        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
    def _generate_markdown_summary(self, data: Dict[str, Any], timestamp: str):
        try:
            """Generate a human-readable markdown summary"""
            summary_file = self.reports_dir / f"quality_summary_{timestamp}.md"

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# LUMINA Quality Summary - {timestamp}\n\n")
                f.write(f"**Overall Status:** {data.get('overall_status', 'N/A')}\n")
                f.write(f"**Timestamp:** {data['timestamp']}\n\n")

                f.write("## Environment\n")
                env = data["environment"]
                f.write(f"- Node.js: {'✅ ' + env['versions'].get('node', '') if env['node'] else '❌ Missing'}\n")
                f.write(f"- NPM: {'✅ ' + env['versions'].get('npm', '') if env['npm'] else '❌ Missing'}\n\n")

                f.write("## Check Results\n")
                if "results" in data:
                    for name, res in data["results"].items():
                        status_icon = "✅" if res["status"] == "passed" else "❌" if res["status"] == "failed" else "⚠️"
                        f.write(f"### {status_icon} {name.capitalize()}\n")
                        f.write(f"**Status:** {res['status']}\n")
                        if res.get("stdout"):
                            # Truncate output for summary
                            lines = res["stdout"].split('\n')
                            if len(lines) > 20:
                                f.write("```text\n" + '\n'.join(lines[:20]) + "\n... (truncated)\n" + "```\n")
                            else:
                                f.write("```text\n" + res["stdout"] + "```\n")
                        elif res.get("output"):
                            lines = res["output"].split('\n')
                            if len(lines) > 20:
                                f.write("```text\n" + '\n'.join(lines[:20]) + "\n... (truncated)\n" + "```\n")
                            else:
                                f.write("```text\n" + res["output"] + "```\n")
                        f.write("\n")
                else:
                    f.write("No results available.\n")

            logger.info(f"Quality summary generated: {summary_file}")

        except Exception as e:
            self.logger.error(f"Error in _generate_markdown_summary: {e}", exc_info=True)
            raise
def main():
    reporter = LUMINAQualityReporter()
    reporter.generate_report()

if __name__ == "__main__":


    main()