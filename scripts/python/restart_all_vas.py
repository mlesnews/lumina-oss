#!/usr/bin/env python3
"""
Restart All Virtual Assistants

Restarts all running virtual assistants to apply SYPHON/R5/JARVIS improvements.

Tags: #VA #RESTART #SYPHON @JARVIS @LUMINA
"""

import sys
import subprocess
import time
import psutil
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RestartAllVAs")


class VARestartManager:
    """Manages restarting all virtual assistants"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.va_scripts = {
            "ironman": project_root / "scripts" / "python" / "ironman_virtual_assistant.py",
            "kenny": project_root / "scripts" / "python" / "kenny_imva_enhanced.py",
            "anakin": project_root / "scripts" / "python" / "anakin_combat_virtual_assistant.py",
            "jarvis": project_root / "scripts" / "python" / "jarvis_virtual_assistant.py"
        }

    def find_running_vas(self) -> List[Dict[str, Any]]:
        """Find all running virtual assistant processes"""
        running_vas = []

        for va_name, va_script in self.va_scripts.items():
            if not va_script.exists():
                continue

            script_name = va_script.name

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any(script_name in str(arg) for arg in cmdline):
                        running_vas.append({
                            "name": va_name,
                            "pid": proc.info['pid'],
                            "script": script_name,
                            "process": proc
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        return running_vas

    def kill_va_processes(self, running_vas: List[Dict[str, Any]]) -> int:
        """Kill all running VA processes"""
        killed = 0

        for va_info in running_vas:
            try:
                proc = va_info["process"]
                logger.info(f"🛑 Stopping {va_info['name']} (PID: {va_info['pid']})")
                proc.terminate()

                # Wait for graceful shutdown
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    logger.warning(f"⚠️  {va_info['name']} didn't terminate gracefully, forcing...")
                    proc.kill()
                    proc.wait(timeout=2)

                killed += 1
                logger.info(f"✅ Stopped {va_info['name']}")
            except Exception as e:
                logger.error(f"❌ Error stopping {va_info['name']}: {e}")

        return killed

    def start_va(self, va_name: str, va_script: Path) -> bool:
        """Start a virtual assistant"""
        if not va_script.exists():
            logger.warning(f"⚠️  Script not found: {va_script.name}")
            return False

        try:
            logger.info(f"🚀 Starting {va_name}...")

            # Start in background
            # Headless/daemon mode - no visible terminals
            creation_flags = 0
            if sys.platform == 'win32':
                # DETACHED_PROCESS (0x00000008) + CREATE_NO_WINDOW (0x08000000)
                creation_flags = 0x08000008

            # Log file
            log_dir = project_root / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{va_name}_{datetime.now().strftime('%Y%m%d')}.log"

            with open(log_file, 'a') as log_handle:
                subprocess.Popen(
                    [sys.executable, str(va_script)],
                    cwd=str(project_root),
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    creationflags=creation_flags,
                    start_new_session=True if sys.platform != 'win32' else False
                )

            time.sleep(2)  # Give it time to start

            # Verify it's running
            running = False
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and va_script.name in str(cmdline):
                        running = True
                        logger.info(f"✅ {va_name} started (PID: {proc.info['pid']})")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not running:
                logger.warning(f"⚠️  {va_name} may not have started properly")

            return running

        except Exception as e:
            logger.error(f"❌ Error starting {va_name}: {e}")
            return False

    def restart_all(self, start_all: bool = False) -> Dict[str, Any]:
        """Restart all virtual assistants"""
        logger.info("=" * 80)
        logger.info("🔄 RESTARTING ALL VIRTUAL ASSISTANTS")
        logger.info("=" * 80)
        logger.info("")

        # Find running VAs
        running_vas = self.find_running_vas()
        logger.info(f"Found {len(running_vas)} running virtual assistants:")
        for va_info in running_vas:
            logger.info(f"  - {va_info['name']} (PID: {va_info['pid']})")
        logger.info("")

        # Kill running processes
        if running_vas:
            logger.info("Stopping running VAs...")
            killed = self.kill_va_processes(running_vas)
            logger.info(f"✅ Stopped {killed} virtual assistants")
            logger.info("")
            time.sleep(2)  # Wait for processes to fully terminate

        # Start VAs
        results = {
            "stopped": len(running_vas),
            "started": 0,
            "failed": []
        }

        if start_all:
            logger.info("Starting all virtual assistants...")
            for va_name, va_script in self.va_scripts.items():
                if self.start_va(va_name, va_script):
                    results["started"] += 1
                else:
                    results["failed"].append(va_name)
                time.sleep(1)  # Stagger starts

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 RESTART SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Stopped: {results['stopped']}")
        logger.info(f"Started: {results['started']}")
        if results["failed"]:
            logger.warning(f"Failed to start: {', '.join(results['failed'])}")
        logger.info("")
        logger.info("✅ All virtual assistants restarted with SYPHON/R5/JARVIS improvements!")
        logger.info("=" * 80)

        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Restart All Virtual Assistants")
    parser.add_argument("--stop-only", action="store_true", help="Only stop running VAs")
    parser.add_argument("--start-all", action="store_true", help="Start all VAs after stopping")
    parser.add_argument("--restart", action="store_true", help="Stop and restart all VAs")

    args = parser.parse_args()

    manager = VARestartManager(project_root)

    if args.restart or (not args.stop_only and not args.start_all):
        # Default: restart all
        manager.restart_all(start_all=True)
    elif args.stop_only:
        running_vas = manager.find_running_vas()
        if running_vas:
            manager.kill_va_processes(running_vas)
        else:
            logger.info("No running virtual assistants found")
    elif args.start_all:
        manager.restart_all(start_all=True)


if __name__ == "__main__":


    main()