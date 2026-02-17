#!/usr/bin/env python3
"""
Process Watchdog - Prevents System Lockups

Monitors Python process count and automatically stops processes if count exceeds safe limits.
This prevents the system freeze issue caused by process proliferation.

Tags: #CRITICAL #MEMORY #SYSTEM_STABILITY #WATCHDOG @JARVIS @LUMINA
"""

import sys
import time
import psutil
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ProcessWatchdog")

# CRITICAL LIMITS (from MEMORY_CRITICAL_SYSTEM_FREEZE_PREVENTION.md)
MAX_PYTHON_PROCESSES = 10
WARNING_THRESHOLD = 7
CHECK_INTERVAL = 5.0  # Check every 5 seconds


class ProcessWatchdog:
    """Watchdog that monitors and kills excessive Python processes"""

    def __init__(self, max_processes: int = MAX_PYTHON_PROCESSES):
        self.max_processes = max_processes
        self.warning_threshold = WARNING_THRESHOLD
        self.running = False
        self.killed_count = 0

    def get_python_processes(self) -> List[Dict[str, Any]]:
        """Get all Python processes with details"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline') or []
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(cmdline) if cmdline else '',
                        'memory_mb': proc.info['memory_info'].rss / (1024 * 1024) if proc.info.get('memory_info') else 0,
                        'cpu_percent': proc.info.get('cpu_percent', 0),
                        'process': proc
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def get_jarvis_processes(self) -> List[Dict[str, Any]]:
        """Get JARVIS-related Python processes"""
        all_procs = self.get_python_processes()
        jarvis_procs = []

        project_path_str = str(project_root).lower()

        for proc in all_procs:
            cmdline_lower = proc['cmdline'].lower()
            if any(keyword in cmdline_lower for keyword in [
                'jarvis', 'lumina', 'monitor', 'health', 'compound_log'
            ]) or project_path_str in cmdline_lower:
                jarvis_procs.append(proc)

        return jarvis_procs

    def kill_excess_processes(self) -> int:
        """Kill excess processes if count exceeds limit"""
        all_procs = self.get_python_processes()
        count = len(all_procs)

        if count <= self.max_processes:
            return 0

        logger.warning(f"⚠️  CRITICAL: {count} Python processes detected (limit: {self.max_processes})")

        # Sort by memory usage (kill largest first)
        all_procs.sort(key=lambda x: x['memory_mb'], reverse=True)

        # Get JARVIS processes first (these are most likely to be problematic)
        jarvis_procs = self.get_jarvis_processes()

        killed = 0
        excess = count - self.max_processes

        # Kill JARVIS processes first
        for proc in jarvis_procs[:excess]:
            try:
                logger.warning(f"🛑 Killing process {proc['pid']}: {proc['cmdline'][:100]}")
                proc['process'].terminate()
                killed += 1
                self.killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # If still need to kill more, kill largest processes
        remaining_excess = excess - killed
        if remaining_excess > 0:
            for proc in all_procs:
                if proc['pid'] not in [p['pid'] for p in jarvis_procs[:excess]]:
                    try:
                        logger.warning(f"🛑 Killing process {proc['pid']}: {proc['cmdline'][:100]}")
                        proc['process'].terminate()
                        killed += 1
                        self.killed_count += 1
                        remaining_excess -= 1
                        if remaining_excess <= 0:
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

        # Wait and force kill if needed
        time.sleep(2)
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    # Check if it's one we tried to kill
                    if any(p['pid'] == proc.info['pid'] for p in all_procs[:excess]):
                        logger.warning(f"💀 Force killing process {proc.info['pid']}")
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return killed

    def check_and_act(self) -> Dict[str, Any]:
        """Check process count and take action if needed"""
        all_procs = self.get_python_processes()
        count = len(all_procs)

        status = {
            'count': count,
            'max_allowed': self.max_processes,
            'status': 'healthy',
            'action_taken': False,
            'killed': 0
        }

        if count > self.max_processes:
            status['status'] = 'critical'
            status['action_taken'] = True
            status['killed'] = self.kill_excess_processes()
            logger.critical(f"🚨 CRITICAL: Killed {status['killed']} excess processes")
        elif count > self.warning_threshold:
            status['status'] = 'warning'
            logger.warning(f"⚠️  WARNING: {count} Python processes (threshold: {self.warning_threshold})")

        return status

    def run(self, interval: float = CHECK_INTERVAL):
        """Run watchdog continuously"""
        self.running = True
        logger.info(f"🐕 Process Watchdog started (max processes: {self.max_processes}, check interval: {interval}s)")

        try:
            while self.running:
                status = self.check_and_act()

                if status['status'] == 'critical':
                    logger.critical(f"🚨 Process count: {status['count']} (killed {status['killed']})")
                elif status['status'] == 'warning':
                    logger.warning(f"⚠️  Process count: {status['count']}")
                else:
                    logger.debug(f"✅ Process count: {status['count']} (healthy)")

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("🛑 Watchdog stopped by user")
        except Exception as e:
            logger.error(f"❌ Watchdog error: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info(f"📊 Watchdog stopped. Total processes killed: {self.killed_count}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Process Watchdog - Prevents System Lockups")
    parser.add_argument("--max", type=int, default=MAX_PYTHON_PROCESSES, help="Maximum Python processes allowed")
    parser.add_argument("--interval", type=float, default=CHECK_INTERVAL, help="Check interval in seconds")
    parser.add_argument("--check", action="store_true", help="One-time check (don't run continuously)")
    parser.add_argument("--kill", action="store_true", help="Kill excess processes immediately")

    args = parser.parse_args()

    watchdog = ProcessWatchdog(max_processes=args.max)

    if args.check or args.kill:
        # One-time check
        status = watchdog.check_and_act()
        print("=" * 80)
        print("🐕 PROCESS WATCHDOG CHECK")
        print("=" * 80)
        print(f"Python Processes: {status['count']}")
        print(f"Max Allowed: {status['max_allowed']}")
        print(f"Status: {status['status'].upper()}")
        if status['action_taken']:
            print(f"Processes Killed: {status['killed']}")
        print("=" * 80)
    else:
        # Run continuously
        watchdog.run(interval=args.interval)


if __name__ == "__main__":


    main()