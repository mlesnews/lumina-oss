#!/usr/bin/env python3
"""
Kill and Recycle All Virtual Assistants

Kills all VA processes, cleans up state files, then restarts them cleanly.
This prevents needing to recycle the laptop.

Tags: #VA #KILL #RECYCLE #CLEAN #RESTART @JARVIS @LUMINA
"""

import sys
import subprocess
import time
import json
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

logger = get_logger("KillAndRecycleAllVAs")


class KillAndRecycleAllVAs:
    """
    Kill and Recycle All Virtual Assistants

    Kills all VA processes, cleans state, then restarts cleanly.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize kill and recycle system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "va_recycle"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # VA scripts to kill and restart
        self.va_scripts = {
            "JARVIS_VA": "jarvis_default_va.py",
            "JARVIS_CHAT": "jarvis_va_chat_coordinator.py",
            "IMVA": "jarvis_ironman_bobblehead_gui.py",
            "ACVA": "jarvis_acva_combat_demo.py"
        }

        logger.info("✅ Kill and Recycle All VAs initialized")

    def kill_all_va_processes(self) -> Dict[str, Any]:
        """Kill all VA processes"""
        logger.info("=" * 80)
        logger.info("🛑 KILLING ALL VA PROCESSES")
        logger.info("=" * 80)
        logger.info("")

        killed = {
            "timestamp": datetime.now().isoformat(),
            "killed_processes": [],
            "errors": []
        }

        try:
            import psutil

            # Find all Python processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if not cmdline:
                        continue

                    cmdline_str = ' '.join(str(c) for c in cmdline).lower()

                    # Check if it's a VA process
                    is_va = False
                    va_name = None
                    for va_id, script_name in self.va_scripts.items():
                        if script_name.lower() in cmdline_str:
                            is_va = True
                            va_name = va_id
                            break

                    if is_va:
                        try:
                            pid = proc.info['pid']
                            proc_name = proc.info['name']
                            logger.info(f"   🛑 Killing: {va_name} (PID: {pid})")
                            # Try terminate first
                            try:
                                proc.terminate()
                                proc.wait(timeout=2)
                            except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                                pass
                            # Force kill
                            try:
                                if proc.is_running():
                                    proc.kill()
                                    proc.wait(timeout=2)
                            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                                pass
                            killed["killed_processes"].append({
                                "va_id": va_name,
                                "pid": pid,
                                "name": proc_name
                            })
                            logger.info(f"      ✅ Killed: {va_name} (PID: {pid})")
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                            killed["errors"].append({
                                "va_id": va_name,
                                "error": str(e)
                            })
                            logger.warning(f"      ⚠️  Could not kill {va_name}: {e}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Also kill by script name using PowerShell
            logger.info("")
            logger.info("   🔍 Checking for remaining processes...")
            for va_id, script_name in self.va_scripts.items():
                try:
                    result = subprocess.run(
                        ["powershell", "-Command",
                         f"Get-Process python -ErrorAction SilentlyContinue | Where-Object {{ $_.CommandLine -like '*{script_name}*' }} | Stop-Process -Force"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                except Exception as e:
                    logger.debug(f"   PowerShell kill check for {va_id}: {e}")

        except ImportError:
            logger.warning("   ⚠️  psutil not available, using PowerShell method")
            # Fallback to PowerShell
            for va_id, script_name in self.va_scripts.items():
                try:
                    result = subprocess.run(
                        ["powershell", "-Command",
                         f"Get-Process python -ErrorAction SilentlyContinue | Where-Object {{ $_.CommandLine -like '*{script_name}*' }} | Stop-Process -Force"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        logger.info(f"   ✅ Killed {va_id} via PowerShell")
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not kill {va_id}: {e}")

        # Wait for processes to fully terminate
        logger.info("")
        logger.info("   ⏳ Waiting for processes to terminate...")
        time.sleep(3)

        logger.info("")
        logger.info(f"   ✅ Killed {len(killed['killed_processes'])} VA processes")
        logger.info("")

        return killed

    def clean_state_files(self) -> Dict[str, Any]:
        """Clean up VA state files"""
        logger.info("=" * 80)
        logger.info("🧹 CLEANING VA STATE FILES")
        logger.info("=" * 80)
        logger.info("")

        cleaned = {
            "timestamp": datetime.now().isoformat(),
            "cleaned_files": [],
            "errors": []
        }

        # State file locations
        state_locations = [
            self.project_root / "data" / "jarvis_va" / "state.json",
            self.project_root / "data" / "jarvis_chat" / "state.json",
            self.project_root / "data" / "imva" / "state.json",
            self.project_root / "data" / "acva" / "state.json",
            self.project_root / "data" / "vas" / "jarvis_va_state.json",
            self.project_root / "data" / "vas" / "jarvis_chat_state.json",
            self.project_root / "data" / "vas" / "imva_state.json",
            self.project_root / "data" / "vas" / "acva_state.json",
        ]

        for state_file in state_locations:
            if state_file.exists():
                try:
                    # Backup before deleting
                    backup_file = self.data_dir / f"{state_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    if state_file.exists():
                        import shutil
                        shutil.copy2(state_file, backup_file)

                    # Update state to inactive instead of deleting
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)

                    state_data["status"] = "inactive"
                    state_data["last_updated"] = datetime.now().isoformat()
                    state_data["recycled"] = True

                    with open(state_file, 'w', encoding='utf-8') as f:
                        json.dump(state_data, f, indent=2, ensure_ascii=False)

                    cleaned["cleaned_files"].append(str(state_file))
                    logger.info(f"   ✅ Cleaned: {state_file.name}")
                except Exception as e:
                    cleaned["errors"].append({
                        "file": str(state_file),
                        "error": str(e)
                    })
                    logger.warning(f"   ⚠️  Could not clean {state_file.name}: {e}")

        logger.info("")
        logger.info(f"   ✅ Cleaned {len(cleaned['cleaned_files'])} state files")
        logger.info("")

        return cleaned

    def restart_all_vas(self) -> Dict[str, Any]:
        """Restart all VAs cleanly"""
        logger.info("=" * 80)
        logger.info("🚀 RESTARTING ALL VAs")
        logger.info("=" * 80)
        logger.info("")

        restarted = {
            "timestamp": datetime.now().isoformat(),
            "restarted": [],
            "failed": []
        }

        # Restart in priority order (IMVA and ACVA optional - user can enable if needed)
        restart_order = ["JARVIS_VA", "JARVIS_CHAT"]  # Only required VAs - IMVA and ACVA disabled by default

        for va_id in restart_order:
            script_name = self.va_scripts[va_id]
            script_path = self.project_root / "scripts" / "python" / script_name

            if not script_path.exists():
                restarted["failed"].append({
                    "va_id": va_id,
                    "reason": "Script not found"
                })
                logger.error(f"   ❌ {va_id}: Script not found")
                continue

            try:
                logger.info(f"   🚀 Starting: {va_id}")

                # Launch with proper window handling
                if va_id in ["JARVIS_VA", "IMVA"]:
                    # GUI VAs - launch with window
                    subprocess.Popen(
                        ["python", str(script_path)],
                        cwd=str(self.project_root),
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                else:
                    # Background VAs
                    subprocess.Popen(
                        ["python", str(script_path)],
                        cwd=str(self.project_root)
                    )

                restarted["restarted"].append({
                    "va_id": va_id,
                    "script": script_name,
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"      ✅ Started: {va_id}")

                # Stagger launches
                time.sleep(2)

            except Exception as e:
                restarted["failed"].append({
                    "va_id": va_id,
                    "reason": str(e)
                })
                logger.error(f"      ❌ Failed to start {va_id}: {e}")

        logger.info("")
        logger.info(f"   ✅ Restarted {len(restarted['restarted'])} VAs")
        logger.info("")

        return restarted

    def kill_and_recycle(self) -> Dict[str, Any]:
        try:
            """Complete kill and recycle process"""
            logger.info("=" * 80)
            logger.info("🔄 KILL AND RECYCLE ALL VAs")
            logger.info("=" * 80)
            logger.info("")

            result = {
                "timestamp": datetime.now().isoformat(),
                "killed": {},
                "cleaned": {},
                "restarted": {}
            }

            # Step 1: Kill all processes
            result["killed"] = self.kill_all_va_processes()

            # Step 2: Clean state files
            result["cleaned"] = self.clean_state_files()

            # Step 3: Wait a moment
            logger.info("   ⏳ Waiting before restart...")
            time.sleep(2)

            # Step 4: Restart all VAs
            result["restarted"] = self.restart_all_vas()

            # Save report
            report_file = self.data_dir / f"recycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ KILL AND RECYCLE COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Killed: {len(result['killed']['killed_processes'])}")
            logger.info(f"   Cleaned: {len(result['cleaned']['cleaned_files'])}")
            logger.info(f"   Restarted: {len(result['restarted']['restarted'])}")
            logger.info(f"   Report: {report_file.name}")
            logger.info("")

            return result


        except Exception as e:
            self.logger.error(f"Error in kill_and_recycle: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Kill and Recycle All Virtual Assistants")
    parser.add_argument("--kill-only", action="store_true", help="Only kill processes, don't restart")
    parser.add_argument("--clean-only", action="store_true", help="Only clean state files")
    parser.add_argument("--restart-only", action="store_true", help="Only restart VAs")

    args = parser.parse_args()

    recycler = KillAndRecycleAllVAs()

    if args.kill_only:
        recycler.kill_all_va_processes()
    elif args.clean_only:
        recycler.clean_state_files()
    elif args.restart_only:
        recycler.restart_all_vas()
    else:
        recycler.kill_and_recycle()

    return 0


if __name__ == "__main__":


    sys.exit(main())