#!/usr/bin/env python3
"""
MANUS Complete All DSM Tasks
Orchestrates completion of all DSM tasks via RDP/MANUS automation
#JARVIS #MANUS #NAS #DSM #AUTOMATION #RDP
"""

import sys
from pathlib import Path
from typing import Dict, Any
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

logger = get_logger("MANUSCompleteDSMTasks")


class MANUSCompleteDSMTasks:
    """Complete all DSM tasks via RDP/MANUS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_port = 5001
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {}
        }

    def complete_all_tasks(self) -> Dict[str, Any]:
        """Complete all DSM tasks"""
        logger.info("🚀 Starting MANUS DSM Task Completion...")
        logger.info("")

        # Task 1: Install Cron Tasks
        logger.info("=" * 70)
        logger.info("TASK 1: Install NAS Cron Tasks via DSM Task Scheduler")
        logger.info("=" * 70)
        try:
            from manus_dsm_task_scheduler_automation import DSMTaskSchedulerAutomation
            scheduler = DSMTaskSchedulerAutomation(
                nas_ip=self.nas_ip, 
                nas_port=self.nas_port,
                project_root=self.project_root
            )

            # Find cron file
            cron_file = self.project_root / "scripts" / "nas" / "cron" / "cursor_tasks_crontab.txt"
            if not cron_file.exists():
                logger.warning("⚠️  Local cron file not found, will try to use deployed file")
                cron_file = "/var/services/homes/backupadm/.crontab_cursor_tasks_20260101_225836"

            result = scheduler.install_cron_tasks_from_file(str(cron_file))
            self.results["tasks"]["cron_installation"] = result

            if result["success"]:
                logger.info(f"✅ Cron tasks installed: {len(result['tasks_created'])} tasks")
            else:
                logger.warning(f"⚠️  Cron installation had issues: {len(result.get('errors', []))} errors")

            scheduler.close()

        except Exception as e:
            logger.error(f"❌ Error in cron installation: {e}")
            self.results["tasks"]["cron_installation"] = {
                "success": False,
                "error": str(e)
            }

        logger.info("")

        # Task 2: Complete SSO Setup
        logger.info("=" * 70)
        logger.info("TASK 2: Complete SAML SSO Setup")
        logger.info("=" * 70)
        try:
            from manus_dsm_sso_automation import DSMSSOAutomation
            sso = DSMSSOAutomation(
                nas_ip=self.nas_ip, 
                nas_port=self.nas_port,
                project_root=self.project_root
            )

            # Look for Azure metadata file
            metadata_file = None
            metadata_paths = [
                self.project_root / "config" / "azure_ad_federation_metadata.xml",
                self.project_root / "data" / "azure_ad_federation_metadata.xml",
            ]
            for path in metadata_paths:
                if path.exists():
                    metadata_file = str(path)
                    break

            result = sso.complete_sso_setup(azure_metadata_file=metadata_file)
            self.results["tasks"]["sso_setup"] = result

            if result["success"]:
                logger.info(f"✅ SSO setup completed: {len(result['steps_completed'])} steps")
            else:
                logger.warning(f"⚠️  SSO setup had issues: {len(result.get('steps_failed', []))} failed steps")

            sso.close()

        except Exception as e:
            logger.error(f"❌ Error in SSO setup: {e}")
            self.results["tasks"]["sso_setup"] = {
                "success": False,
                "error": str(e)
            }

        logger.info("")

        # Summary
        logger.info("=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)

        total_tasks = len(self.results["tasks"])
        successful_tasks = sum(1 for t in self.results["tasks"].values() if t.get("success", False))

        logger.info(f"✅ Successful: {successful_tasks}/{total_tasks}")
        logger.info(f"❌ Failed: {total_tasks - successful_tasks}/{total_tasks}")
        logger.info("")

        self.results["summary"] = {
            "total_tasks": total_tasks,
            "successful": successful_tasks,
            "failed": total_tasks - successful_tasks
        }

        return self.results


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Complete All DSM Tasks via RDP/MANUS")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--save-report", action="store_true", help="Save report to file")

        args = parser.parse_args()

        completer = MANUSCompleteDSMTasks(project_root)
        result = completer.complete_all_tasks()

        if args.save_report:
            report_file = project_root / "data" / "system" / f"manus_dsm_tasks_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"📄 Report saved: {report_file}")

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            summary = result.get("summary", {})
            if summary.get("successful", 0) == summary.get("total_tasks", 0):
                print("\n✅ All tasks completed successfully!")
            else:
                print(f"\n⚠️  Completed {summary.get('successful', 0)}/{summary.get('total_tasks', 0)} tasks")

        return 0 if summary.get("successful", 0) == summary.get("total_tasks", 0) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())