#!/usr/bin/env python3
"""
JARVIS Developers' Windows Reboot
Automates a comprehensive development-safe Windows reboot.

Features:
- Reason Analysis (Updates, uptime, performance)
- Pre-flight checks (Saved work, sync status)
- Graceful application shutdown
- Automated restart command
- Next-login resumption protocol

Tags: #REBOOT #ADMIN #WINDOWS #AUTOMATION @AUTO @MANUS
"""

import sys
import os
import subprocess
import json
import time
import ctypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_manus_admin_orchestrator import JARVISManusAdminOrchestrator
    from cursor_intelligent_warm_recycle import CursorIntelligentWarmRecycle
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    JARVISManusAdminOrchestrator = None
    CursorIntelligentWarmRecycle = None

logger = get_logger("JARVISDeveloperReboot")


class JARVISDeveloperReboot:
    """
    Automates a developer-friendly Windows reboot.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.admin = JARVISManusAdminOrchestrator() if JARVISManusAdminOrchestrator else None
        self.cursor_recycle = CursorIntelligentWarmRecycle(self.project_root) if CursorIntelligentWarmRecycle else None

        self.data_dir = self.project_root / "data" / "reboot_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "reboot_state.json"

    def analyze_reboot_need(self) -> Dict[str, Any]:
        """Analyze if a reboot is needed and why"""
        reasons = []

        # 1. Check Uptime
        try:
            import psutil
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_days = uptime_seconds / 86400
            if uptime_days > 7:
                reasons.append(f"System uptime is {uptime_days:.1f} days (threshold: 7)")
        except ImportError:
            pass

        # 2. Check Pending Updates (Registry check)
        if self.admin and self.admin.is_admin():
            try:
                import winreg
                keys = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending")
                ]
                for hkey, path in keys:
                    try:
                        winreg.OpenKey(hkey, path)
                        reasons.append(f"Windows Update reboot pending ({path.split('\\')[-1]})")
                    except FileNotFoundError:
                        continue
            except ImportError:
                pass

        # 3. Memory Pressure check
        try:
            import psutil
            if psutil.virtual_memory().percent > 90:
                reasons.append(f"System memory critical: {psutil.virtual_memory().percent}%")
        except ImportError:
            pass

        return {
            "needed": len(reasons) > 0,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat()
        }

    def prepare_for_reboot(self) -> Dict[str, Any]:
        """Perform pre-flight safety checks and data saving"""
        self.logger.info("🛠️  Preparing for Developers' Reboot...")

        pre_flight = {
            "files_saved": False,
            "holocron_synced": False,
            "db_committed": False,
            "resumption_set": False
        }

        # 1. Save IDE Work
        if self.cursor_recycle:
            self.logger.info("   💾 Saving all open IDE files...")
            pre_flight["files_saved"] = self.cursor_recycle.save_all_files()
            self.cursor_recycle.save_workspace_state()

        # 2. Sync Holocron & Database
        try:
            self.logger.info("   📚 Syncing Holocron and committing DB entries...")
            # Trigger existing migration/sync scripts
            subprocess.run([sys.executable, str(script_dir / "jarvis_tickets_to_holocron_db.py"), "--all"], check=False)
            pre_flight["holocron_synced"] = True
            pre_flight["db_committed"] = True
        except Exception as e:
            self.logger.warning(f"   ⚠️  Sync failed: {e}")

        # 3. Set Resumption Protocol (Add to Windows Startup)
        try:
            self.logger.info("   ♻️  Setting resumption protocol for next login...")
            self._set_resumption_startup()
            pre_flight["resumption_set"] = True
        except Exception as e:
            self.logger.warning(f"   ⚠️  Could not set resumption: {e}")

        return pre_flight

    def _set_resumption_startup(self):
        try:
            """Adds a script to the user's startup folder to resume JARVIS apps after reboot"""
            startup_folder = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            resume_bat = startup_folder / "JARVIS_Resume.bat"

            # Create a batch file that runs the command center and bobblehead
            content = f"""@echo off
timeout /t 10 /nobreak
cd /d "{self.project_root}"
start "" "{sys.executable}" scripts/python/jarvis_command_center.py
del "%~f0"
"""
            with open(resume_bat, 'w') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Error in _set_resumption_startup: {e}", exc_info=True)
            raise

    def execute_reboot(self, force: bool = False):
        """Actually trigger the Windows reboot"""
        if not force:
            need = self.analyze_reboot_need()
            if not need["needed"]:
                self.logger.info("ℹ️  Reboot not strictly necessary based on metrics.")
                return False

        # Pre-flight
        self.prepare_for_reboot()

        self.logger.info("="*80)
        self.logger.info("🚀 TRIGGERING DEVELOPERS' WINDOWS REBOOT")
        self.logger.info("="*80)

        # Shutdown Cursor first to be clean
        if self.cursor_recycle:
            self.cursor_recycle.graceful_shutdown()

        # Final countdown
        for i in range(5, 0, -1):
            self.logger.info(f"   Rebooting in {i} seconds...")
            time.sleep(1)

        # Trigger Windows restart
        os.system("shutdown /r /t 0")
        return True


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Developers' Windows Reboot")
        parser.add_argument("--check", action="store_true", help="Analyze if reboot is needed")
        parser.add_argument("--reboot", action="store_true", help="Trigger development-safe reboot")
        parser.add_argument("--force", action="store_true", help="Force reboot without checking metrics")

        args = parser.parse_args()
        manager = JARVISDeveloperReboot()

        if args.check:
            report = manager.analyze_reboot_need()
            print(json.dumps(report, indent=2))
        elif args.reboot:
            manager.execute_reboot(force=args.force)
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()