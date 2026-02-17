#!/usr/bin/env python3
"""
Startup Safety Check

Runs before any monitoring script to ensure system is safe to start.
Prevents system freeze by checking process count and resource usage.

Tags: #CRITICAL #MEMORY #SYSTEM_STABILITY #SAFETY @JARVIS @LUMINA
"""

import sys
import psutil
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartupSafetyCheck")

# CRITICAL LIMITS (from MEMORY_CRITICAL_SYSTEM_FREEZE_PREVENTION.md)
MAX_PYTHON_PROCESSES = 10
MAX_MEMORY_PERCENT = 70
MAX_CPU_PERCENT = 70


def check_system_safe() -> tuple[bool, str]:
    """
    Check if system is safe to start new processes.
    Returns (is_safe, message)
    """
    issues = []

    # Check Python process count
    python_count = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                python_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if python_count >= MAX_PYTHON_PROCESSES:
        issues.append(f"❌ CRITICAL: {python_count} Python processes (limit: {MAX_PYTHON_PROCESSES})")
        return False, f"Too many Python processes: {python_count}"
    elif python_count > 7:
        issues.append(f"⚠️  WARNING: {python_count} Python processes (approaching limit)")

    # Check memory usage
    memory = psutil.virtual_memory()
    if memory.percent > MAX_MEMORY_PERCENT:
        issues.append(f"❌ CRITICAL: Memory usage {memory.percent:.1f}% (limit: {MAX_MEMORY_PERCENT}%)")
        return False, f"Memory usage too high: {memory.percent:.1f}%"
    elif memory.percent > 60:
        issues.append(f"⚠️  WARNING: Memory usage {memory.percent:.1f}%")

    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > MAX_CPU_PERCENT:
        issues.append(f"⚠️  WARNING: CPU usage {cpu_percent:.1f}% (limit: {MAX_CPU_PERCENT}%)")
        # CPU is less critical, just warn

    if issues:
        message = "\n".join(issues)
        logger.warning(f"⚠️  Safety check warnings:\n{message}")
        return True, message  # Still safe, but with warnings

    logger.info(f"✅ System safe: {python_count} Python processes, {memory.percent:.1f}% memory, {cpu_percent:.1f}% CPU")
    return True, "System is safe"


def main():
    """Main entry point - returns exit code"""
    is_safe, message = check_system_safe()

    if not is_safe:
        print("=" * 80)
        print("🚨 STARTUP SAFETY CHECK FAILED")
        print("=" * 80)
        print(message)
        print()
        print("RECOMMENDED ACTIONS:")
        print("1. Run: python scripts/python/emergency_stop_all_monitors.py")
        print("2. Wait 10 seconds")
        print("3. Run: python scripts/python/process_watchdog.py --check")
        print("4. Only then start your monitoring script")
        print("=" * 80)
        return 1

    if "WARNING" in message:
        print("⚠️  Warnings detected, but system is safe to proceed")
        return 0

    return 0


if __name__ == "__main__":


    sys.exit(main())