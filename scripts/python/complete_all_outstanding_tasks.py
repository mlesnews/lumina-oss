#!/usr/bin/env python3
"""
Complete All Outstanding Tasks
Runs all automation scripts to complete outstanding items
#JARVIS #AUTOMATION #TASKS #COMPLETION
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import logging
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CompleteOutstandingTasks")


class OutstandingTasksCompleter:
    """Complete all outstanding tasks"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "completed": [],
            "failed": [],
            "pending_manual": []
        }

    def run_all(self) -> Dict[str, Any]:
        """Run all automation tasks"""
        logger.info("🚀 Starting completion of all outstanding tasks...")
        logger.info("")

        # Task 1: Verify NAS Cron Tasks
        logger.info("=" * 70)
        logger.info("TASK 1: Verify NAS Cron Tasks")
        logger.info("=" * 70)
        try:
            from verify_nas_cron_tasks import NASCronVerifier
            verifier = NASCronVerifier(self.project_root)
            cron_result = verifier.verify_cron_installation()

            if cron_result.get("success"):
                if cron_result.get("cron_installed"):
                    self.results["completed"].append({
                        "task": "Verify NAS Cron Tasks",
                        "status": "verified",
                        "details": f"Found {len(cron_result.get('cron_tasks', []))} tasks"
                    })
                    logger.info("✅ NAS cron tasks verified")
                else:
                    # Try to install
                    install_result = verifier.install_cron_if_missing()
                    if install_result.get("success"):
                        self.results["completed"].append({
                            "task": "Install NAS Cron Tasks",
                            "status": "installed"
                        })
                        logger.info("✅ NAS cron tasks installed")
                    else:
                        self.results["pending_manual"].append({
                            "task": "Install NAS Cron Tasks",
                            "reason": install_result.get("error", "Unknown")
                        })
                        logger.warning("⚠️  Manual installation required")
            else:
                self.results["failed"].append({
                    "task": "Verify NAS Cron Tasks",
                    "error": cron_result.get("error", "Unknown")
                })
        except Exception as e:
            logger.error(f"❌ Error in cron verification: {e}")
            self.results["failed"].append({
                "task": "Verify NAS Cron Tasks",
                "error": str(e)
            })

        logger.info("")

        # Task 2: Test Synology APIs
        logger.info("=" * 70)
        logger.info("TASK 2: Test All Synology API Endpoints")
        logger.info("=" * 70)
        try:
            from test_all_synology_apis import SynologyAPITester
            tester = SynologyAPITester()
            api_result = tester.test_all_apis()

            if api_result.get("success"):
                summary = api_result.get("summary", {})
                self.results["completed"].append({
                    "task": "Test Synology APIs",
                    "status": "tested",
                    "details": f"{summary.get('working', 0)}/{summary.get('total_tested', 0)} APIs working"
                })
                logger.info(f"✅ Tested {summary.get('total_tested', 0)} APIs")
            else:
                self.results["failed"].append({
                    "task": "Test Synology APIs",
                    "error": api_result.get("error", "Unknown")
                })
        except Exception as e:
            logger.error(f"❌ Error in API testing: {e}")
            self.results["failed"].append({
                "task": "Test Synology APIs",
                "error": str(e)
            })

        logger.info("")

        # Task 3: Optimize Model Selection
        logger.info("=" * 70)
        logger.info("TASK 3: Optimize LLM Model Selection")
        logger.info("=" * 70)
        try:
            from optimize_llm_model_selection import LLMModelOptimizer
            optimizer = LLMModelOptimizer(self.project_root)
            model_result = optimizer.recommend_models()

            if model_result:
                providers_checked = len([p for p in model_result.get("providers", {}).values() if p.get("available")])
                self.results["completed"].append({
                    "task": "Optimize Model Selection",
                    "status": "analyzed",
                    "details": f"Checked {providers_checked} providers, {len(model_result.get('recommendations', []))} recommendations"
                })
                logger.info("✅ Model optimization analysis complete")
        except Exception as e:
            logger.error(f"❌ Error in model optimization: {e}")
            self.results["failed"].append({
                "task": "Optimize Model Selection",
                "error": str(e)
            })

        logger.info("")

        # Task 4: Automate SSO Setup
        logger.info("=" * 70)
        logger.info("TASK 4: Automate SSO Setup Steps")
        logger.info("=" * 70)
        try:
            from automate_sso_setup_steps import SSOSetupAutomation
            sso_automation = SSOSetupAutomation(self.project_root)
            sso_result = sso_automation.run_all_automation()

            if sso_result.get("success"):
                files_created = len(sso_result.get("files_created", []))
                self.results["completed"].append({
                    "task": "Automate SSO Setup",
                    "status": "automated",
                    "details": f"Created {files_created} automation files"
                })
                logger.info(f"✅ SSO automation files created")

                # Add pending manual steps
                for step in sso_result.get("steps_pending", []):
                    self.results["pending_manual"].append({
                        "task": step,
                        "reason": "Manual configuration required"
                    })
        except Exception as e:
            logger.error(f"❌ Error in SSO automation: {e}")
            self.results["failed"].append({
                "task": "Automate SSO Setup",
                "error": str(e)
            })

        logger.info("")

        # Summary
        logger.info("=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        logger.info(f"✅ Completed: {len(self.results['completed'])}")
        logger.info(f"❌ Failed: {len(self.results['failed'])}")
        logger.info(f"⏳ Manual Steps: {len(self.results['pending_manual'])}")
        logger.info("")

        return {
            "success": len(self.results["failed"]) == 0,
            "results": self.results
        }


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Complete All Outstanding Tasks")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--save-report", action="store_true", help="Save report to file")

        args = parser.parse_args()

        completer = OutstandingTasksCompleter(project_root)
        result = completer.run_all()

        if args.save_report:
            report_file = project_root / "data" / "system" / f"outstanding_tasks_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"📄 Report saved: {report_file}")

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print("\n✅ All automated tasks completed!")
            else:
                print("\n⚠️  Some tasks had issues (see details above)")

        return 0 if result.get("success") else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())