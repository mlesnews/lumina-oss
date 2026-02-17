#!/usr/bin/env python3
"""
JARVIS Post-Startup Checklist Executor

Executes the AI post-startup checklist automatically after system initialization.

Tags: #POST_STARTUP #CHECKLIST #AUTOMATION @JARVIS @LUMINA
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISPostStartup")


class PostStartupExecutor:
    """Execute post-startup checklist"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checklist_file = project_root / "config" / "ai_post_startup_checklist.json"
        self.data_dir = project_root / "data" / "post_startup_execution"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.checklist = self.load_checklist()

    def load_checklist(self) -> Dict[str, Any]:
        """Load post-startup checklist"""
        if not self.checklist_file.exists():
            logger.warning(f"Checklist file not found: {self.checklist_file}")
            return {"checklist_items": [], "execution_order": []}

        try:
            with open(self.checklist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("ai_post_startup_checklist", {})
        except Exception as e:
            logger.error(f"Error loading checklist: {e}")
            return {"checklist_items": [], "execution_order": []}

    def get_checklist_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a checklist item by ID"""
        items = self.checklist.get("checklist_items", [])
        for item in items:
            if item.get("id") == item_id:
                return item
        return None

    def execute_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a checklist item"""
        item_id = item.get("id")
        item_name = item.get("name")
        script_path = item.get("script")
        args = item.get("args", [])
        enabled = item.get("enabled", True)
        runs_continuously = item.get("runs_continuously", False)

        if not enabled:
            logger.info(f"⏭️  Skipping {item_name} (disabled)")
            return {
                "success": True,
                "skipped": True,
                "reason": "disabled"
            }

        logger.info(f"▶️  Executing: {item_name}")

        if runs_continuously:
            # Start in background
            try:
                script_full_path = self.project_root / script_path
                if not script_full_path.exists():
                    return {
                        "success": False,
                        "error": f"Script not found: {script_full_path}"
                    }

                # Start as background process
                subprocess.Popen(
                    [sys.executable, str(script_full_path)] + args,
                    cwd=str(self.project_root),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                logger.info(f"   ✅ Started {item_name} (running continuously)")
                return {
                    "success": True,
                    "running_continuously": True
                }
            except Exception as e:
                logger.error(f"   ❌ Error starting {item_name}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            # Execute and wait
            try:
                script_full_path = self.project_root / script_path
                if not script_full_path.exists():
                    return {
                        "success": False,
                        "error": f"Script not found: {script_full_path}"
                    }

                result = subprocess.run(
                    [sys.executable, str(script_full_path)] + args,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=item.get("estimated_duration_seconds", 60) * 2
                )

                if result.returncode == 0:
                    logger.info(f"   ✅ Completed {item_name}")
                    return {
                        "success": True,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                else:
                    logger.warning(f"   ⚠️  {item_name} completed with warnings (returncode: {result.returncode})")
                    return {
                        "success": False,
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
            except subprocess.TimeoutExpired:
                logger.error(f"   ❌ {item_name} timed out")
                return {
                    "success": False,
                    "error": "Timeout"
                }
            except Exception as e:
                logger.error(f"   ❌ Error executing {item_name}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    def execute_checklist(self) -> Dict[str, Any]:
        try:
            """Execute the entire checklist"""
            logger.info("=" * 80)
            logger.info("🚀 JARVIS POST-STARTUP CHECKLIST EXECUTION")
            logger.info("=" * 80)
            logger.info("")

            if not self.checklist.get("enabled", True):
                logger.warning("Post-startup checklist is disabled")
                return {
                    "success": False,
                    "error": "Checklist disabled"
                }

            execution_order = self.checklist.get("execution_order", [])
            execution_policy = self.checklist.get("execution_policy", {})

            results = {
                "started_at": datetime.now().isoformat(),
                "items_executed": [],
                "items_failed": [],
                "items_skipped": []
            }

            logger.info(f"📋 Executing {len(execution_order)} checklist items")
            logger.info("")

            for item_id in execution_order:
                item = self.get_checklist_item(item_id)
                if not item:
                    logger.warning(f"⚠️  Checklist item not found: {item_id}")
                    continue

                result = self.execute_item(item)
                result["item_id"] = item_id
                result["item_name"] = item.get("name")

                if result.get("success"):
                    results["items_executed"].append(result)
                elif result.get("skipped"):
                    results["items_skipped"].append(result)
                else:
                    results["items_failed"].append(result)

                    if execution_policy.get("stop_on_error", False):
                        logger.error("🛑 Stopping execution due to error (stop_on_error=true)")
                        break

                # Brief pause between items
                time.sleep(1)

            results["completed_at"] = datetime.now().isoformat()
            results["summary"] = {
                "total": len(execution_order),
                "executed": len(results["items_executed"]),
                "failed": len(results["items_failed"]),
                "skipped": len(results["items_skipped"])
            }

            # Save execution report
            report_file = self.data_dir / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ POST-STARTUP CHECKLIST EXECUTION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Executed: {results['summary']['executed']}")
            logger.info(f"   Failed: {results['summary']['failed']}")
            logger.info(f"   Skipped: {results['summary']['skipped']}")
            logger.info(f"📄 Report saved: {report_file}")
            logger.info("=" * 80)

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_checklist: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Post-Startup Checklist Executor")
        parser.add_argument("--execute", action="store_true", help="Execute checklist")
        parser.add_argument("--list", action="store_true", help="List checklist items")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        executor = PostStartupExecutor(project_root)

        if args.execute:
            results = executor.execute_checklist()
            print(json.dumps(results, indent=2, default=str))

        elif args.list:
            items = executor.checklist.get("checklist_items", [])
            order = executor.checklist.get("execution_order", [])

            print("=" * 80)
            print("POST-STARTUP CHECKLIST ITEMS")
            print("=" * 80)
            print(f"\nExecution Order ({len(order)} items):")
            for i, item_id in enumerate(order, 1):
                item = executor.get_checklist_item(item_id)
                if item:
                    status = "✅" if item.get("enabled") else "⏸️ "
                    print(f"  {i}. {status} {item.get('name')} ({item_id})")

            print(f"\nAll Items ({len(items)} total):")
            for item in items:
                status = "✅" if item.get("enabled") else "⏸️ "
                priority = item.get("priority", "medium")
                print(f"  {status} [{priority}] {item.get('name')} ({item.get('id')})")
            print("=" * 80)

        else:
            # Default: execute checklist
            results = executor.execute_checklist()
            print(json.dumps(results, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()