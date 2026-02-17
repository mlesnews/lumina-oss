#!/usr/bin/env python3
"""
JARVIS Safe Reboot Procedure
Safely reboots PC/OS after checking for critical processes and saving state.

Tags: #JARVIS #REBOOT #SAFE #OS @DOIT
"""

import sys
import json
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSafeReboot")

PROJECT_ROOT = script_dir.parent.parent


class JARVISSafeReboot:
    """Safe reboot procedure for PC/OS"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = PROJECT_ROOT
        self.project_root = Path(project_root)

    def check_critical_processes(self) -> Dict[str, Any]:
        """Check for critical processes that should be saved/closed"""
        critical_processes = []
        important_processes = []

        # Critical processes that should be saved before reboot
        critical_names = ["Cursor.exe", "code.exe", "notepad.exe", "word.exe", "excel.exe"]

        # Important processes to note
        important_names = ["python.exe", "node.exe", "docker.exe"]

        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                proc_info = proc.info
                name = proc_info['name'].lower()

                if any(cn.lower() in name for cn in critical_names):
                    critical_processes.append({
                        "name": proc_info['name'],
                        "pid": proc_info['pid'],
                        "memory_mb": proc_info['memory_info'].rss / (1024 * 1024)
                    })
                elif any(in_name.lower() in name for in_name in important_names):
                    important_processes.append({
                        "name": proc_info['name'],
                        "pid": proc_info['pid'],
                        "memory_mb": proc_info['memory_info'].rss / (1024 * 1024)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "critical": critical_processes,
            "important": important_processes,
            "timestamp": datetime.now().isoformat()
        }

    def save_system_state(self) -> Path:
        try:
            """Save current system state before reboot"""
            state_file = self.project_root / "data" / "system_state" / f"pre_reboot_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)

            state = {
                "timestamp": datetime.now().isoformat(),
                "reboot_initiated": True,
                "system_info": {
                    "platform": sys.platform,
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                    "disk_usage_percent": psutil.disk_usage('/').percent
                },
                "processes": self.check_critical_processes(),
                "reboot_reason": "User requested reboot via JARVIS"
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ System state saved to {state_file}")
            return state_file

        except Exception as e:
            self.logger.error(f"Error in save_system_state: {e}", exc_info=True)
            raise
    def prepare_reboot(self) -> Dict[str, Any]:
        """Prepare system for reboot"""
        logger.info("="*80)
        logger.info("🔄 JARVIS SAFE REBOOT PROCEDURE")
        logger.info("="*80)
        logger.info("")

        # Check critical processes
        logger.info("📋 Checking critical processes...")
        processes = self.check_critical_processes()

        if processes["critical"]:
            logger.warning(f"⚠️  Found {len(processes['critical'])} critical processes:")
            for proc in processes["critical"]:
                logger.warning(f"   - {proc['name']} (PID: {proc['pid']})")
            logger.warning("   ⚠️  Please save your work before rebooting!")
        else:
            logger.info("✅ No critical processes detected")

        if processes["important"]:
            logger.info(f"ℹ️  Found {len(processes['important'])} important processes:")
            for proc in processes["important"]:
                logger.info(f"   - {proc['name']} (PID: {proc['pid']})")

        # Save system state
        logger.info("")
        logger.info("💾 Saving system state...")
        state_file = self.save_system_state()

        # Prepare reboot summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "ready": True,
            "critical_processes": len(processes["critical"]),
            "important_processes": len(processes["important"]),
            "state_saved": str(state_file),
            "reboot_command": self.get_reboot_command()
        }

        logger.info("")
        logger.info("="*80)
        logger.info("✅ SYSTEM READY FOR REBOOT")
        logger.info("="*80)
        logger.info("")
        logger.info(f"📋 Summary:")
        logger.info(f"   - Critical processes: {summary['critical_processes']}")
        logger.info(f"   - Important processes: {summary['important_processes']}")
        logger.info(f"   - State saved: {summary['state_saved']}")
        logger.info("")
        logger.info(f"🔄 Reboot command: {summary['reboot_command']}")
        logger.info("")

        return summary

    def get_reboot_command(self) -> str:
        """Get the reboot command for current OS"""
        import platform
        os_name = platform.system()

        if os_name == "Windows":
            return "shutdown /r /t 60 /c \"JARVIS initiated reboot - System will restart in 60 seconds\""
        elif os_name == "Linux":
            return "sudo reboot"
        elif os_name == "Darwin":  # macOS
            return "sudo reboot"
        else:
            return "reboot"

    def execute_reboot(self, delay_seconds: int = 60, force: bool = False) -> bool:
        """Execute reboot with optional delay"""
        import platform
        os_name = platform.system()

        try:
            # Prepare first
            summary = self.prepare_reboot()

            if summary["critical_processes"] > 0 and not force:
                logger.warning("")
                logger.warning("⚠️  WARNING: Critical processes detected!")
                logger.warning("   Use --force to reboot anyway")
                logger.warning("   Or save your work and run again")
                return False

            logger.info("")
            logger.info("🚀 EXECUTING REBOOT...")
            logger.info(f"   Delay: {delay_seconds} seconds")
            logger.info("")

            if os_name == "Windows":
                # Windows reboot
                cmd = f"shutdown /r /t {delay_seconds} /c \"JARVIS initiated reboot - System will restart in {delay_seconds} seconds\""
                logger.info(f"   Command: {cmd}")
                subprocess.run(cmd, shell=True, check=True)
                logger.info(f"✅ Reboot scheduled - System will restart in {delay_seconds} seconds")
                logger.info("   You can cancel with: shutdown /a")
            elif os_name == "Linux":
                # Linux reboot
                if delay_seconds > 0:
                    logger.info(f"   Waiting {delay_seconds} seconds before reboot...")
                    import time
                    time.sleep(delay_seconds)
                subprocess.run(["sudo", "reboot"], check=True)
            elif os_name == "Darwin":  # macOS
                # macOS reboot
                if delay_seconds > 0:
                    logger.info(f"   Waiting {delay_seconds} seconds before reboot...")
                    import time
                    time.sleep(delay_seconds)
                subprocess.run(["sudo", "reboot"], check=True)
            else:
                logger.error(f"❌ Unsupported OS: {os_name}")
                return False

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Reboot failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error during reboot: {e}")
            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Safe Reboot")
    parser.add_argument('--prepare', action='store_true', help='Prepare for reboot (check processes, save state)')
    parser.add_argument('--reboot', action='store_true', help='Execute reboot')
    parser.add_argument('--delay', type=int, default=60, help='Reboot delay in seconds (default: 60)')
    parser.add_argument('--force', action='store_true', help='Force reboot even with critical processes')

    args = parser.parse_args()

    rebooter = JARVISSafeReboot()

    if args.prepare:
        rebooter.prepare_reboot()
    elif args.reboot:
        success = rebooter.execute_reboot(delay_seconds=args.delay, force=args.force)
        if not success:
            sys.exit(1)
    else:
        # Default: prepare
        rebooter.prepare_reboot()


if __name__ == "__main__":


    main()