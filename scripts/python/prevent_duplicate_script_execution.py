#!/usr/bin/env python3
"""
Prevent Duplicate Script Execution

Detects and prevents multiple instances of the same script from running simultaneously.
Uses lock files and process detection.

Tags: #DUPLICATE_PREVENTION #LOCK_FILE #PROCESS_MANAGEMENT @LUMINA
"""

import sys
import os
import time
import fcntl
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

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

logger = get_logger("PreventDuplicateExecution")


def check_duplicate_script_execution(script_name: str) -> bool:
    """
    Check if the same script is already running

    Args:
        script_name: Name of the script (e.g., "recycle_jarvis.py")

    Returns:
        True if duplicate found, False otherwise
    """
    try:
        import psutil

        current_pid = os.getpid()
        script_basename = os.path.basename(script_name)

        # Count how many processes are running this script
        running_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Skip current process
                if proc.info['pid'] == current_pid:
                    continue

                # Check if it's a Python process
                proc_name = proc.info.get('name', '').lower()
                if 'python' not in proc_name and 'pythonw' not in proc_name:
                    continue

                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue

                cmdline_str = ' '.join(str(arg) for arg in cmdline)

                # Check if this script is in the command line
                if script_basename in cmdline_str:
                    running_count += 1
                    logger.warning(f"   ⚠️  Found duplicate execution: PID {proc.info['pid']} - {cmdline_str[:80]}")

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"Process check error: {e}")

        if running_count > 0:
            logger.warning(f"⚠️  DUPLICATE DETECTED: {running_count} other instance(s) of '{script_basename}' are running!")
            return True

        return False

    except ImportError:
        logger.debug("psutil not available - cannot check for duplicates")
        return False
    except Exception as e:
        logger.debug(f"Error checking for duplicates: {e}")
        return False


@contextmanager
def script_execution_lock(script_name: str, timeout: float = 10.0):
    """
    Context manager to prevent duplicate script execution using lock file

    Usage:
        with script_execution_lock("recycle_jarvis.py"):
            # Script code here
            pass
    """
    lock_file_path = project_root / "data" / "script_locks" / f"{script_name}.lock"
    lock_file_path.parent.mkdir(parents=True, exist_ok=True)

    lock_file = None
    lock_acquired = False

    try:
        # Check for duplicate processes first
        if check_duplicate_script_execution(script_name):
            raise RuntimeError(f"Another instance of '{script_name}' is already running!")

        # Try to acquire lock file
        if os.name == 'nt':  # Windows
            try:
                import msvcrt
                lock_file = open(lock_file_path, 'w')
                try:
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    lock_acquired = True
                    logger.info(f"✅ Acquired execution lock for {script_name}")
                except IOError:
                    # Lock already held
                    raise RuntimeError(f"Lock file for '{script_name}' is already held - another instance may be running")
            except ImportError:
                # Fallback: just check for duplicate processes
                logger.debug("msvcrt not available - using process check only")
                lock_acquired = True
        else:  # Unix/Linux
            try:
                lock_file = open(lock_file_path, 'w')
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                lock_acquired = True
                logger.info(f"✅ Acquired execution lock for {script_name}")
            except IOError:
                # Lock already held
                raise RuntimeError(f"Lock file for '{script_name}' is already held - another instance may be running")

        # Write current PID to lock file
        if lock_file:
            lock_file.write(f"{os.getpid()}\n")
            lock_file.flush()

        yield  # Execute script code

    finally:
        # Release lock
        if lock_file and lock_acquired:
            try:
                if os.name == 'nt':
                    try:
                        import msvcrt
                        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    except:
                        pass
                else:
                    try:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    except:
                        pass
                lock_file.close()

                # Remove lock file
                if lock_file_path.exists():
                    lock_file_path.unlink()

                logger.info(f"✅ Released execution lock for {script_name}")
            except Exception as e:
                logger.debug(f"Error releasing lock: {e}")


def kill_duplicate_script_executions(script_name: str) -> int:
    """
    Kill all other instances of the same script

    Args:
        script_name: Name of the script

    Returns:
        Number of duplicate instances killed
    """
    killed_count = 0

    try:
        import psutil

        current_pid = os.getpid()
        script_basename = os.path.basename(script_name)

        logger.info(f"🔍 Searching for duplicate executions of '{script_basename}'...")

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Skip current process
                if proc.info['pid'] == current_pid:
                    continue

                # Check if it's a Python process
                proc_name = proc.info.get('name', '').lower()
                if 'python' not in proc_name and 'pythonw' not in proc_name:
                    continue

                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue

                cmdline_str = ' '.join(str(arg) for arg in cmdline)

                # Check if this script is in the command line
                if script_basename in cmdline_str:
                    logger.info(f"   🎯 Found duplicate: PID {proc.info['pid']} - {cmdline_str[:80]}")
                    try:
                        # Graceful termination
                        proc.terminate()
                        killed_count += 1
                        logger.info(f"   ✅ Terminated duplicate PID {proc.info['pid']}")

                        # Wait for graceful shutdown
                        try:
                            proc.wait(timeout=2.0)
                        except psutil.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=1.0)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"Process check error: {e}")

        if killed_count > 0:
            logger.info(f"✅ Killed {killed_count} duplicate execution(s)")
        else:
            logger.info("   ✅ No duplicates found")

        return killed_count

    except ImportError:
        logger.debug("psutil not available - cannot kill duplicates")
        return 0
    except Exception as e:
        logger.warning(f"Error killing duplicates: {e}")
        return 0
