#!/usr/bin/env python3
"""
Kill Idle Cursor Terminals

Detects and kills idle Cursor IDE terminal processes that are consuming resources.

Tags: #CURSOR #TERMINAL #CLEANUP #RESOURCE_MANAGEMENT @LUMINA
"""

import sys
import time
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KillIdleCursorTerminals")


def kill_idle_cursor_terminals(max_idle_time: float = 60.0, force: bool = False) -> int:
    """
    Kill idle Cursor terminal processes

    Args:
        max_idle_time: Maximum idle time in seconds before killing (default: 60 seconds)
        force: If True, kill all Cursor terminals regardless of idle time

    Returns:
        Number of terminals killed
    """
    killed_count = 0

    try:
        import psutil

        current_pid = os.getpid()
        current_time = time.time()

        logger.info(f"🔍 Searching for Cursor terminal processes (max_idle: {max_idle_time}s, force: {force})...")

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
            try:
                # Skip current process
                if proc.info['pid'] == current_pid:
                    continue

                # Check if it's a Cursor-related process
                proc_name = proc.info.get('name', '').lower()
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(str(arg) for arg in cmdline).lower() if cmdline else ''

                # Look for Cursor terminal processes
                is_cursor_terminal = False

                # Check process name
                if 'cursor' in proc_name or 'code' in proc_name:
                    # Check if it's a terminal (not the main Cursor process)
                    if 'terminal' in cmdline_str or 'powershell' in cmdline_str or 'cmd' in cmdline_str:
                        is_cursor_terminal = True

                # Also check for Python processes running in Cursor terminals
                if 'python' in proc_name and 'cursor' in cmdline_str:
                    # Check if it's a terminal session (has terminal-like characteristics)
                    if any(term_indicator in cmdline_str for term_indicator in ['terminal', 'shell', 'cmd', 'powershell']):
                        is_cursor_terminal = True

                if not is_cursor_terminal:
                    continue

                # Calculate idle time
                create_time = proc.info.get('create_time', current_time)
                process_age = current_time - create_time

                # Check CPU usage (idle processes have low CPU)
                try:
                    cpu_percent = proc.cpu_percent(interval=0.1)
                except:
                    cpu_percent = 0.0

                # Check memory usage
                try:
                    memory_mb = proc.info.get('memory_info', {}).get('rss', 0) / (1024 * 1024)
                except:
                    memory_mb = 0.0

                # Determine if process is idle
                is_idle = False
                if force:
                    is_idle = True  # Force kill all
                elif cpu_percent < 1.0:  # Less than 1% CPU
                    # Check if it's been idle for longer than max_idle_time
                    # For terminals, we consider them idle if:
                    # 1. Low CPU usage (< 1%)
                    # 2. Process has been running for a while
                    # 3. No recent activity (heuristic: process age > max_idle_time)
                    if process_age > max_idle_time:
                        is_idle = True

                if is_idle:
                    logger.info(f"   🎯 Found idle Cursor terminal: PID {proc.info['pid']}")
                    logger.info(f"      Age: {process_age:.1f}s, CPU: {cpu_percent:.1f}%, Memory: {memory_mb:.1f}MB")
                    logger.info(f"      Cmdline: {cmdline_str[:100]}")

                    try:
                        # Try graceful termination first (prevents exit code 15 notifications)
                        proc.terminate()
                        killed_count += 1
                        logger.info(f"   ✅ Terminated idle terminal PID {proc.info['pid']} (graceful)")

                        # Wait for graceful shutdown
                        try:
                            proc.wait(timeout=2.0)  # Wait up to 2 seconds for graceful exit
                            logger.info(f"   ✅ PID {proc.info['pid']} exited gracefully")
                        except psutil.TimeoutExpired:
                            # Process didn't exit gracefully, force kill
                            logger.warning(f"   ⚠️  Terminal {proc.info['pid']} didn't exit gracefully, force killing...")
                            proc.kill()
                            proc.wait(timeout=1.0)
                            logger.info(f"   ✅ Force killed PID {proc.info['pid']}")
                        except psutil.NoSuchProcess:
                            # Already dead
                            pass
                    except psutil.NoSuchProcess:
                        # Already dead
                        pass
                    except psutil.AccessDenied:
                        logger.warning(f"   ⚠️  Access denied for PID {proc.info['pid']} - trying taskkill...")
                        try:
                            import subprocess
                            subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])],
                                         capture_output=True, timeout=2)
                            killed_count += 1
                            logger.info(f"   ✅ Killed via taskkill: PID {proc.info['pid']}")
                        except:
                            pass
                    except Exception as e:
                        logger.debug(f"   Error killing PID {proc.info['pid']}: {e}")

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"Process iteration error: {e}")

        if killed_count > 0:
            logger.info(f"✅ Killed {killed_count} idle Cursor terminal(s)")
        else:
            logger.info("   ✅ No idle terminals found")

        return killed_count

    except ImportError:
        logger.warning("⚠️  psutil not available - cannot detect idle terminals")
        logger.warning("   Install: pip install psutil")
        # Fallback: try Windows taskkill for obvious terminal processes
        try:
            import subprocess
            # This is a less precise method, but can catch some terminal processes
            result = subprocess.run(
                ['taskkill', '/F', '/FI', 'WINDOWTITLE eq *Terminal*'],
                capture_output=True,
                timeout=3
            )
            if result.returncode == 0:
                logger.info("   ✅ Killed some terminal processes using taskkill")
                return 1
        except:
            pass
        return 0
    except Exception as e:
        logger.warning(f"⚠️  Error killing idle terminals: {e}")
        return 0


def kill_all_cursor_terminals() -> int:
    """Kill ALL Cursor terminal processes (force kill)"""
    return kill_idle_cursor_terminals(max_idle_time=0.0, force=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kill idle Cursor terminal processes")
    parser.add_argument("--max-idle", type=float, default=60.0,
                       help="Maximum idle time in seconds (default: 60)")
    parser.add_argument("--force", action="store_true",
                       help="Force kill all Cursor terminals")
    parser.add_argument("--all", action="store_true",
                       help="Kill all Cursor terminals (same as --force)")

    args = parser.parse_args()

    if args.all or args.force:
        killed = kill_all_cursor_terminals()
    else:
        killed = kill_idle_cursor_terminals(max_idle_time=args.max_idle, force=False)

    sys.exit(0 if killed >= 0 else 1)
