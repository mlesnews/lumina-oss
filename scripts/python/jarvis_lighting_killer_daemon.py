#!/usr/bin/env python3
"""
JARVIS Lighting Killer Daemon

Background daemon that continuously kills AacAmbientLighting.
Runs in background without requiring admin privileges.

@JARVIS @DAEMON @LIGHTING @KILLER @BACKGROUND
"""

import sys
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LightingKillerDaemon")


class LightingKillerDaemon:
    """
    Lighting Killer Daemon

    Runs continuously in background, killing AacAmbientLighting as it restarts.
    """

    def __init__(self, project_root: Path, check_interval: int = 3):
        self.project_root = project_root
        self.check_interval = check_interval
        self.logger = get_logger("LightingKillerDaemon")
        self.running = True
        self.kill_count = 0
        self.start_time = datetime.now()

        # Create log file
        self.log_dir = self.project_root / "data" / "lighting_killer_daemon"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"daemon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # Setup file logging
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info("=" * 70)
        self.logger.info("🔧 LIGHTING KILLER DAEMON STARTED")
        self.logger.info(f"   Check interval: {self.check_interval} seconds")
        self.logger.info(f"   Log file: {self.log_file}")
        self.logger.info("=" * 70)

    def kill_process(self) -> bool:
        """Kill AacAmbientLighting process"""
        try:
            # Kill process
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue | Stop-Process -Force"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Also try to stop parent services (may fail without admin, but try anyway)
            services = ["ArmouryCrateService", "LightingService", "AuraWallpaperService", "AuraService"]
            for service in services:
                try:
                    subprocess.run(
                        ["powershell", "-Command", f"Stop-Service -Name '{service}' -Force -ErrorAction SilentlyContinue"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                except Exception:
                    pass

            return True
        except Exception as e:
            self.logger.error(f"Error killing process: {str(e)}")
            return False

    def is_running(self) -> bool:
        """Check if AacAmbientLighting is running"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    def run(self):
        """Run daemon loop"""
        self.logger.info("")
        self.logger.info("🔄 Starting daemon loop...")
        self.logger.info("")

        consecutive_failures = 0
        max_failures = 10

        try:
            while self.running:
                if self.is_running():
                    self.logger.info(f"   🔍 AacAmbientLighting detected - killing...")
                    if self.kill_process():
                        self.kill_count += 1
                        consecutive_failures = 0
                        elapsed = (datetime.now() - self.start_time).total_seconds()
                        self.logger.info(f"   ✅ Killed (total: {self.kill_count}, elapsed: {elapsed:.0f}s)")
                    else:
                        consecutive_failures += 1
                        self.logger.warning(f"   ⚠️  Failed to kill (consecutive failures: {consecutive_failures})")

                        if consecutive_failures >= max_failures:
                            self.logger.error(f"   ❌ Too many consecutive failures ({max_failures}), stopping daemon")
                            break
                else:
                    consecutive_failures = 0

                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("   ⏹️  Stopped by user (Ctrl+C)")
        except Exception as e:
            self.logger.error(f"   ❌ Error in daemon loop: {str(e)}")
        finally:
            self.running = False
            self.log_summary()

    def log_summary(self):
        """Log summary statistics"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 DAEMON SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"   🔧 Total Kills: {self.kill_count}")
        self.logger.info(f"   ⏱️  Total Time: {elapsed:.0f} seconds ({elapsed/60:.1f} minutes)")
        if elapsed > 0:
            kills_per_minute = (self.kill_count / elapsed) * 60
            self.logger.info(f"   📊 Kills per Minute: {kills_per_minute:.1f}")
        self.logger.info(f"   📝 Log File: {self.log_file}")
        self.logger.info("=" * 70)
        self.logger.info("✅ DAEMON STOPPED")
        self.logger.info("=" * 70)


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Lighting Killer Daemon")
        parser.add_argument("--interval", type=int, default=3, help="Check interval in seconds (default: 3)")
        parser.add_argument("--background", action="store_true", help="Run in background (detached)")

        args = parser.parse_args()

        if args.background:
            # Run in background (Windows)
            import subprocess
            script_path = Path(__file__).resolve()
            project_root = script_path.parent.parent.parent
            subprocess.Popen(
                [sys.executable, str(script_path), "--interval", str(args.interval)],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ Daemon started in background")
            print(f"   Check interval: {args.interval} seconds")
            print(f"   Logs: {project_root / 'data' / 'lighting_killer_daemon'}")
        else:
            project_root = Path(__file__).parent.parent.parent
            daemon = LightingKillerDaemon(project_root, check_interval=args.interval)
            daemon.run()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()