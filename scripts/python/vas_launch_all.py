#!/usr/bin/env python3
"""
Launch All VAs on Desktop - ORDER 66: @DOIT PROCEED

Actually launches all Virtual Assistants so they appear on the desktop.
This is the "DOING" part - not just initializing, but actually running them.

Tags: #VAS #IMVA #ACVA #JARVIS #LAUNCH #DESKTOP #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsLaunchAll")


class VAsLaunchAll:
    """
    Launch All VAs on Desktop - Actually DO IT

    Launches all Virtual Assistants so they appear and run on the desktop.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VA launcher"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts" / "python"

        # VA launch configurations
        # IMPORTANT: JARVIS is FIRST - The First Impression for all clients/customers
        self.va_launch_configs = {
            "JARVIS_VA": {
                "script": "jarvis_default_va.py",
                "name": "JARVIS Virtual Assistant",
                "description": "JARVIS - THE FIRST IMPRESSION (runs first)",
                "priority": 1,
                "first_impression": True
            },
            "JARVIS_CHAT": {
                "script": "jarvis_va_chat_coordinator.py",
                "name": "JARVIS Chat Coordinator",
                "description": "JARVIS chat coordinator (runs in background)",
                "priority": 2,
                "first_impression": True
            },
            "IMVA": {
                "script": "jarvis_ironman_bobblehead_gui.py",
                "name": "Iron Man Virtual Assistant",
                "description": "Desktop visual companion with IRON MAN theme",
                "priority": 3
            },
            "ACVA": {
                "script": "jarvis_acva_combat_demo.py",
                "name": "Anakin/Vader Combat Virtual Assistant",
                "description": "Combat-focused Virtual Assistant",
                "priority": 4
            }
        }

        logger.info("✅ VAs Launch All initialized")

    def launch_va(self, va_id: str, va_config: Dict[str, Any]) -> Dict[str, Any]:
        """Launch a single VA"""
        script_name = va_config.get("script")
        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            logger.warning(f"   ⚠️  Script not found: {script_name}")
            return {
                "va_id": va_id,
                "launched": False,
                "error": f"Script not found: {script_name}"
            }

        logger.info(f"🚀 Launching {va_id} ({va_config.get('name')})...")

        try:
            # Launch in a new process (detached for desktop VAs)
            # For GUI VAs (IMVA), don't redirect stdout/stderr so window can show
            if sys.platform == "win32":
                if va_id == "IMVA":
                    # Launch IMVA without redirecting output so GUI window appears
                    # Use DETACHED_PROCESS to allow window to show independently
                    process = subprocess.Popen(
                        [sys.executable, str(script_path)],
                        cwd=str(self.project_root),
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    # Background VAs - can redirect output
                    process = subprocess.Popen(
                        [sys.executable, str(script_path)],
                        cwd=str(self.project_root),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
            else:
                # Linux/Mac - launch in background
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            # Give it a moment to start
            time.sleep(1)

            # Check if process is still running
            if process.poll() is None:
                logger.info(f"   ✅ {va_id} launched successfully (PID: {process.pid})")
                return {
                    "va_id": va_id,
                    "launched": True,
                    "pid": process.pid,
                    "script": script_name
                }
            else:
                # Process exited immediately - check for errors
                stdout, stderr = process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Process exited immediately"
                logger.error(f"   ❌ {va_id} failed to launch: {error_msg[:200]}")
                return {
                    "va_id": va_id,
                    "launched": False,
                    "error": error_msg[:200]
                }

        except Exception as e:
            logger.error(f"   ❌ Error launching {va_id}: {e}", exc_info=True)
            return {
                "va_id": va_id,
                "launched": False,
                "error": str(e)
            }

    def launch_all_vas(self) -> Dict[str, Any]:
        """
        Launch all VAs on desktop

        ORDER 66: @DOIT PROCEED - Actually DO IT
        """
        logger.info("="*80)
        logger.info("🚀 ORDER 66: @DOIT PROCEED - Launching All VAs on Desktop")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT PROCEED - Launch",
            "vas_launched": [],
            "vas_failed": [],
            "launch_results": [],
            "success": True,
            "errors": []
        }

        # Launch each VA - JARVIS FIRST (The First Impression)
        logger.info("\n🚀 Launching VAs...")
        logger.info("🎯 JARVIS will be launched FIRST - The First Impression")
        logger.info("")

        # Sort by priority (JARVIS first)
        sorted_vas = sorted(
            self.va_launch_configs.items(),
            key=lambda x: x[1].get("priority", 999)
        )

        for va_id, va_config in sorted_vas:
            try:
                launch_result = self.launch_va(va_id, va_config)
                result["launch_results"].append(launch_result)

                if launch_result.get("launched"):
                    result["vas_launched"].append(va_id)
                    logger.info(f"   ✅ {va_id} is now running on desktop")
                else:
                    result["vas_failed"].append(va_id)
                    error = launch_result.get("error", "Unknown error")
                    result["errors"].append(f"{va_id}: {error}")
                    logger.warning(f"   ⚠️  {va_id} failed to launch")

                # Small delay between launches
                time.sleep(0.5)

            except Exception as e:
                error_msg = f"Error launching {va_id}: {e}"
                logger.error(f"   ❌ {error_msg}", exc_info=True)
                result["errors"].append(error_msg)
                result["vas_failed"].append(va_id)

        # Update success status
        result["success"] = len(result["vas_launched"]) > 0

        # Save report
        report_file = self.project_root / "data" / "vas" / f"vas_launch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"   ✅ Report saved: {report_file.name}")
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")

        logger.info("="*80)
        logger.info("✅ VAs Launch Complete")
        logger.info(f"   VAs Launched: {len(result['vas_launched'])}")
        logger.info(f"   VAs Failed: {len(result['vas_failed'])}")
        if result.get('errors'):
            logger.info(f"   Errors: {len(result['errors'])}")
        logger.info("="*80)

        return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ORDER 66: @DOIT PROCEED - Launching All VAs on Desktop")
    print("="*80 + "\n")

    launcher = VAsLaunchAll()
    result = launcher.launch_all_vas()

    print("\n" + "="*80)
    print("📊 LAUNCH RESULTS")
    print("="*80)
    print(f"Timestamp: {result['timestamp']}")
    print(f"Execution Type: {result['execution_type']}")
    print(f"Success: {result['success']}")

    print(f"\nVAs Launched: {len(result['vas_launched'])}")
    for va_id in result['vas_launched']:
        print(f"   🚀 {va_id}")

    if result.get('vas_failed'):
        print(f"\nVAs Failed: {len(result['vas_failed'])}")
        for va_id in result['vas_failed']:
            print(f"   ❌ {va_id}")

    if result.get('errors'):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   ❌ {error}")

    print("\n✅ VAs Launch Complete")
    print("="*80 + "\n")
