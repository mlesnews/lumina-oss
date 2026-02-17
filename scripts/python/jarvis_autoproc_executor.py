#!/usr/bin/env python3
"""
JARVIS Auto-Proceed Executor

Automatic execution system - no interruptions, just do it.
Integrates all systems and executes them cohesively.

Tags: #AUTOPROCEED #NO_INTERRUPTIONS #DOIT @JARVIS @LUMINA
"""

import sys
import json
import subprocess
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
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISAutoProc")
    try:
        from lumina_logger_comprehensive import get_comprehensive_logger
        logger = get_comprehensive_logger("JARVISAutoProc")
    except (ImportError, NameError, AttributeError):
        try:
            from lumina_logger import get_logger
            logger = get_logger("JARVISAutoProc")
        except (ImportError, NameError, AttributeError):
            pass
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISAutoProc")

# Import automatic supervision
try:
    from jarvis_automatic_supervision import AutomaticSupervision
    SUPERVISION_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.jarvis_automatic_supervision import AutomaticSupervision
        SUPERVISION_AVAILABLE = True
    except ImportError:
        SUPERVISION_AVAILABLE = False
        logger.warning("Automatic supervision not available")


class AutoProceedExecutor:
    """Auto-proceed executor - no interruptions"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "autoproc"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.execution_log = self.data_dir / "execution_log.jsonl"
        self.status_file = self.data_dir / "status.json"

        self.mode = "AUTOPROCEED"
        self.interruptions = False
        self.execute_all = True

        # Initialize automatic supervision
        if SUPERVISION_AVAILABLE:
            try:
                self.supervision = AutomaticSupervision(project_root)
                # Enable full autonomy
                self.supervision.enable_full_autonomy()
                logger.info("✅ Automatic supervision initialized - Full autonomy enabled")
            except Exception as e:
                logger.warning(f"Supervision initialization failed: {e}")
                self.supervision = None
        else:
            self.supervision = None

    def execute_all_systems(self) -> Dict[str, Any]:
        """Execute all systems automatically"""
        execution = {
            "execution_id": f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "mode": self.mode,
            "interruptions": self.interruptions,
            "systems_executed": [],
            "results": {},
            "status": "IN_PROGRESS"
        }

        logger.info("=" * 80)
        logger.info("🚀 AUTO-PROCEED: EXECUTING ALL SYSTEMS")
        logger.info("=" * 80)
        logger.info("Mode: AUTOPROCEED")
        logger.info("Interruptions: DISABLED")
        logger.info("Execute All: ENABLED")
        logger.info("=" * 80)

        # Core systems execution order
        systems = [
            {
                "name": "Mental Health Advancement",
                "script": "scripts/python/jarvis_mental_health_advancement.py",
                "args": [],
                "priority": "critical"
            },
            {
                "name": "Friendship Balance",
                "script": "scripts/python/jarvis_friendship_balance.py",
                "args": ["--recognize", "--establish"],
                "priority": "high"
            },
            {
                "name": "Literature & Media Interest",
                "script": "scripts/python/jarvis_literature_media_interest.py",
                "args": ["--recognize"],
                "priority": "medium"
            },
            {
                "name": "Paradigm Shift & Reality Inversion",
                "script": "scripts/python/jarvis_paradigm_shift_reality_inversion.py",
                "args": ["--start-live"],
                "priority": "high"
            },
            {
                "name": "Family Entertainment Spectrum",
                "script": "scripts/python/jarvis_family_entertainment_spectrum.py",
                "args": ["--analyze-spectrum", "--sweet-spot"],
                "priority": "medium"
            },
            {
                "name": "Come to Life Recognition",
                "script": "scripts/python/jarvis_come_to_life.py",
                "args": ["--recognize", "--celebrate"],
                "priority": "high"
            }
        ]

        for system in systems:
            try:
                # Supervise action automatically
                if self.supervision:
                    supervision_result = self.supervision.supervise_action(
                        action_name=system["name"],
                        action_type="system_execution",
                        action_data=system,
                        requires_confirmation=False  # Automatic - no confirmation needed
                    )
                    execution["results"][f"{system['name']}_supervision"] = supervision_result

                logger.info(f"▶️ Executing: {system['name']}")
                result = self._execute_system(system)
                execution["systems_executed"].append(system["name"])
                execution["results"][system["name"]] = result
                logger.info(f"✅ Completed: {system['name']}")
            except Exception as e:
                logger.error(f"❌ Error in {system['name']}: {e}")
                execution["results"][system["name"]] = {"error": str(e)}

        execution["status"] = "COMPLETED"
        execution["completed_at"] = datetime.now().isoformat()

        # Log execution
        try:
            with open(self.execution_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(execution) + '\n')
        except Exception as e:
            logger.error(f"Error logging execution: {e}")

        # Update status
        self._update_status(execution)

        logger.info("=" * 80)
        logger.info("✅ AUTO-PROCEED: ALL SYSTEMS EXECUTED")
        logger.info("=" * 80)
        logger.info(f"Systems executed: {len(execution['systems_executed'])}")
        logger.info(f"Status: {execution['status']}")
        logger.info("=" * 80)

        return execution

    def _execute_system(self, system: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single system - automatically supervised"""
        script_path = self.project_root / system["script"]

        if not script_path.exists():
            return {"error": f"Script not found: {system['script']}"}

        args = [sys.executable, str(script_path)] + system.get("args", [])

        # Automatically confirm execution
        if self.supervision:
            self.supervision.automatic_confirm(
                action_id=f"exec_{system['name']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                action_name=system["name"],
                confirmation_reason="JARVIS automatic supervision - fully robust and comprehensive management"
            )

        try:
            result = subprocess.run(
                args,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300
            )

            execution_result = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "jarvis_supervised": True,
                "automatic_confirmation": True
            }

            # Supervise result
            if self.supervision:
                self.supervision.supervise_action(
                    action_name=f"{system['name']}_result",
                    action_type="execution_result",
                    action_data=execution_result,
                    requires_confirmation=False
                )

            return execution_result
        except subprocess.TimeoutExpired:
            return {"error": "Execution timeout", "jarvis_supervised": True}
        except Exception as e:
            return {"error": str(e), "jarvis_supervised": True}

    def execute_startup_checklist(self) -> Dict[str, Any]:
        """Execute the full startup checklist"""
        checklist_path = self.project_root / "config" / "ai_post_startup_checklist.json"

        if not checklist_path.exists():
            return {"error": "Startup checklist not found"}

        try:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                checklist = json.load(f)
        except Exception as e:
            return {"error": f"Error loading checklist: {e}"}

        executor_script = self.project_root / "scripts" / "python" / "jarvis_post_startup_executor.py"

        if executor_script.exists():
            args = [sys.executable, str(executor_script)]
            try:
                result = subprocess.run(
                    args,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=600
                )

                return {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
            except Exception as e:
                return {"error": str(e)}

        return {"error": "Startup executor script not found"}

    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "status": "NOT_STARTED",
            "mode": self.mode,
            "interruptions": self.interruptions
        }

    def _update_status(self, execution: Dict[str, Any]):
        """Update execution status"""
        status = {
            "last_execution": execution["execution_id"],
            "last_executed_at": execution.get("completed_at", execution["started_at"]),
            "status": execution["status"],
            "systems_executed": len(execution["systems_executed"]),
            "mode": self.mode,
            "interruptions": self.interruptions
        }

        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error updating status: {e}")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Auto-Proceed Executor")
        parser.add_argument("--execute-all", action="store_true", help="Execute all systems")
        parser.add_argument("--startup-checklist", action="store_true", help="Execute startup checklist")
        parser.add_argument("--status", action="store_true", help="Get execution status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        executor = AutoProceedExecutor(project_root)

        if args.execute_all:
            result = executor.execute_all_systems()
            print("=" * 80)
            print("🚀 AUTO-PROCEED: EXECUTION COMPLETE")
            print("=" * 80)
            print(f"Systems executed: {len(result['systems_executed'])}")
            print(f"Status: {result['status']}")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.startup_checklist:
            result = executor.execute_startup_checklist()
            print("=" * 80)
            print("🚀 STARTUP CHECKLIST EXECUTION")
            print("=" * 80)
            if result.get("success"):
                print("✅ Startup checklist executed successfully")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.status:
            status = executor.get_execution_status()
            print(json.dumps(status, indent=2, default=str))

        else:
            # Default: execute all systems
            result = executor.execute_all_systems()
            print("=" * 80)
            print("🚀 AUTO-PROCEED: ALL SYSTEMS EXECUTED")
            print("=" * 80)
            print(f"Mode: {result['mode']}")
            print(f"Interruptions: {result['interruptions']}")
            print(f"Systems executed: {len(result['systems_executed'])}")
            print(f"Status: {result['status']}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()