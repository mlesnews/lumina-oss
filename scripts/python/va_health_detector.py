#!/usr/bin/env python3
"""
Virtual Assistant Health Detector

Detects if VAs (JARVIS, IMVA, ACVA, etc.) are running and healthy.
Integrates with autonomous AI agent to detect and fix VA failures.

Tags: #VA_HEALTH #DETECTION #AUTONOMOUS #LUMINA @JARVIS @IMVA @ACVA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
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

logger = get_logger("VAHealthDetector")


class VAHealthDetector:
    """
    Virtual Assistant Health Detector

    Detects VA status and health, identifies failures, and triggers fixes.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VA health detector"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "va_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # VA configurations
        self.va_configs = {
            "JARVIS_VA": {
                "script": "jarvis_default_va.py",
                "name": "JARVIS Virtual Assistant",
                "required": True,
                "first_impression": True
            },
            "JARVIS_CHAT": {
                "script": "jarvis_va_chat_coordinator.py",
                "name": "JARVIS Chat Coordinator",
                "required": True,
                "first_impression": True
            },
            "IMVA": {
                "script": "jarvis_ironman_bobblehead_gui.py",
                "name": "Iron Man Virtual Assistant",
                "required": False,
                "first_impression": False
            },
            "ACVA": {
                "script": "jarvis_acva_combat_demo.py",
                "name": "Anakin Combat Virtual Assistant",
                "required": False,
                "first_impression": False
            }
        }

        logger.info("✅ VA Health Detector initialized")

    def check_va_health(self) -> Dict[str, Any]:
        try:
            """
            Check health of all VAs

            Returns:
                Health status for all VAs
            """
            logger.info("=" * 80)
            logger.info("🔍 CHECKING VA HEALTH")
            logger.info("=" * 80)
            logger.info("")

            health_status = {
                "timestamp": datetime.now().isoformat(),
                "vas": {},
                "summary": {
                    "total": 0,
                    "running": 0,
                    "not_running": 0,
                    "failed": 0,
                    "required_running": 0,
                    "required_not_running": 0
                }
            }

            for va_id, config in self.va_configs.items():
                logger.info(f"   🔍 Checking: {config['name']} ({va_id})")

                va_status = self._check_single_va(va_id, config)
                health_status["vas"][va_id] = va_status

                # Update summary
                health_status["summary"]["total"] += 1
                if va_status["running"]:
                    health_status["summary"]["running"] += 1
                    if config["required"]:
                        health_status["summary"]["required_running"] += 1
                else:
                    health_status["summary"]["not_running"] += 1
                    if config["required"]:
                        health_status["summary"]["required_not_running"] += 1
                    if va_status.get("failed"):
                        health_status["summary"]["failed"] += 1

                # Log status
                if va_status["running"]:
                    logger.info(f"      ✅ Running (PID: {va_status.get('pid', 'N/A')})")
                else:
                    logger.info(f"      ❌ NOT RUNNING")
                    if va_status.get("failed"):
                        logger.info(f"         ⚠️  Failed: {va_status.get('failure_reason', 'Unknown')}")

                logger.info("")

            # Save health status
            health_file = self.data_dir / f"va_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, ensure_ascii=False)

            logger.info("=" * 80)
            logger.info("✅ VA HEALTH CHECK COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Total VAs: {health_status['summary']['total']}")
            logger.info(f"   Running: {health_status['summary']['running']}")
            logger.info(f"   Not Running: {health_status['summary']['not_running']}")
            logger.info(f"   Failed: {health_status['summary']['failed']}")
            logger.info(f"   Required Running: {health_status['summary']['required_running']}")
            logger.info(f"   Required NOT Running: {health_status['summary']['required_not_running']}")
            logger.info(f"   Health file: {health_file.name}")
            logger.info("")

            return health_status

        except Exception as e:
            self.logger.error(f"Error in check_va_health: {e}", exc_info=True)
            raise
    def _check_single_va(self, va_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a single VA"""
        script_name = config["script"]
        script_path = self.project_root / "scripts" / "python" / script_name

        status = {
            "va_id": va_id,
            "va_name": config["name"],
            "script": script_name,
            "script_path": str(script_path),
            "running": False,
            "pid": None,
            "failed": False,
            "failure_reason": None,
            "last_seen": None,
            "required": config["required"]
        }

        # Check if script exists
        if not script_path.exists():
            status["failed"] = True
            status["failure_reason"] = f"Script not found: {script_path}"
            return status

        # Check if process is running
        try:
            # Search for Python processes running this script
            result = subprocess.run(
                ["wmic", "process", "where", f"commandline like '%{script_name}%'", "get", "processid,commandline"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and script_name in result.stdout:
                # Process is running
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if script_name in line and 'processid' not in line.lower():
                        parts = line.strip().split()
                        if parts:
                            try:
                                status["pid"] = int(parts[-1])
                                status["running"] = True
                                status["last_seen"] = datetime.now().isoformat()
                                break
                            except (ValueError, IndexError):
                                pass
        except Exception as e:
            logger.debug(f"   ⚠️  Process check error for {va_id}: {e}")

        # If not running, check for state files or other indicators
        if not status["running"]:
            # Check for state files
            state_files = [
                self.project_root / "data" / va_id.lower() / "state.json",
                self.project_root / "data" / "vas" / f"{va_id.lower()}_state.json"
            ]

            for state_file in state_files:
                if state_file.exists():
                    try:
                        with open(state_file, 'r', encoding='utf-8') as f:
                            state_data = json.load(f)
                            if state_data.get("status") == "active":
                                # State says active but process not running - likely crashed
                                status["failed"] = True
                                status["failure_reason"] = "State indicates active but process not running (likely crashed)"
                                break
                    except Exception:
                        pass

        return status

    def fix_failed_vas(self, health_status: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fix failed VAs

        Args:
            health_status: Health status (if None, checks first)

        Returns:
            Fix results
        """
        logger.info("=" * 80)
        logger.info("🔧 FIXING FAILED VAs")
        logger.info("=" * 80)
        logger.info("")

        if health_status is None:
            health_status = self.check_va_health()

        fix_results = {
            "timestamp": datetime.now().isoformat(),
            "fixed": [],
            "failed_to_fix": [],
            "skipped": []
        }

        for va_id, va_status in health_status.get("vas", {}).items():
            if not va_status.get("running"):
                config = self.va_configs.get(va_id, {})
                logger.info(f"   🔧 Fixing: {config.get('name', va_id)}")

                try:
                    # Launch VA
                    script_path = self.project_root / "scripts" / "python" / config["script"]
                    if script_path.exists():
                        subprocess.Popen(
                            ["python", str(script_path)],
                            cwd=str(self.project_root),
                            creationflags=subprocess.CREATE_NEW_CONSOLE if config.get("first_impression") else 0
                        )

                        fix_results["fixed"].append({
                            "va_id": va_id,
                            "va_name": config.get("name"),
                            "action": "Launched"
                        })
                        logger.info(f"      ✅ Launched: {config.get('name')}")
                    else:
                        fix_results["failed_to_fix"].append({
                            "va_id": va_id,
                            "va_name": config.get("name"),
                            "reason": "Script not found"
                        })
                        logger.error(f"      ❌ Script not found: {script_path}")
                except Exception as e:
                    fix_results["failed_to_fix"].append({
                        "va_id": va_id,
                        "va_name": config.get("name"),
                        "reason": str(e)
                    })
                    logger.error(f"      ❌ Failed to launch: {e}")

                logger.info("")

        # Save fix results
        fix_file = self.data_dir / f"va_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fix_file, 'w', encoding='utf-8') as f:
            json.dump(fix_results, f, indent=2, ensure_ascii=False)

        logger.info("=" * 80)
        logger.info("✅ VA FIX COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Fixed: {len(fix_results['fixed'])}")
        logger.info(f"   Failed: {len(fix_results['failed_to_fix'])}")
        logger.info(f"   Fix file: {fix_file.name}")
        logger.info("")

        return fix_results


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="VA Health Detector")
    parser.add_argument("--check", action="store_true", help="Check VA health")
    parser.add_argument("--fix", action="store_true", help="Fix failed VAs")

    args = parser.parse_args()

    detector = VAHealthDetector()

    if args.fix:
        health = detector.check_va_health()
        detector.fix_failed_vas(health)
    elif args.check:
        detector.check_va_health()
    else:
        # Default: check
        detector.check_va_health()

    return 0


if __name__ == "__main__":


    sys.exit(main())