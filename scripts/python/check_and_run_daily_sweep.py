#!/usr/bin/env python3
"""
@DAILY @SOURCE @SWEEPS - Check and Run Daily Sweep

Startup script that checks if daily sweep has run today.
If not, executes the sweep automatically.

This runs on Windows login via Startup folder.

Tags: #DAILY #SOURCE #SWEEPS #STARTUP #AUTOMATION @JARVIS
"""

import json
import logging
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

# Set up paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CheckDailySweep")


def get_last_sweep_date() -> date | None:
    """Get the date of the last successful sweep"""
    state_file = project_root / "data" / "daily_source_sweeps" / "sweep_state.json"

    if state_file.exists():
        try:
            with open(state_file) as f:
                state = json.load(f)
                last_run = state.get("last_successful_sweep")
                if last_run:
                    return datetime.fromisoformat(last_run).date()
        except Exception as e:
            logger.warning(f"Could not read sweep state: {e}")

    # Also check unified queue for recent activity
    queue_file = project_root / "data" / "unified_queue" / "queue_state.json"
    if queue_file.exists():
        try:
            with open(queue_file) as f:
                queue = json.load(f)
                updated = queue.get("updated_at")
                if updated:
                    return datetime.fromisoformat(updated).date()
        except Exception:
            pass

    return None


def save_sweep_state(success: bool) -> None:
    """Save the sweep state"""
    state_dir = project_root / "data" / "daily_source_sweeps"
    state_dir.mkdir(parents=True, exist_ok=True)

    state_file = state_dir / "sweep_state.json"
    state = {
        "last_sweep_attempt": datetime.now().isoformat(),
        "last_successful_sweep": datetime.now().isoformat() if success else None,
        "success": success,
    }

    # Merge with existing state
    if state_file.exists():
        try:
            with open(state_file) as f:
                existing = json.load(f)
                if success:
                    existing["last_successful_sweep"] = state["last_successful_sweep"]
                existing["last_sweep_attempt"] = state["last_sweep_attempt"]
                state = existing
        except Exception:
            pass

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def run_sweep() -> bool:
    """Execute the daily source sweep"""
    logger.info("🚀 Starting daily source sweep...")

    sweep_script = script_dir / "syphon_source_sweeps_scans.py"

    if not sweep_script.exists():
        logger.error(f"Sweep script not found: {sweep_script}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(sweep_script)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=7200,  # 2 hour timeout
        )

        if result.returncode == 0:
            logger.info("✅ Daily source sweep completed successfully")
            return True
        else:
            logger.error(f"❌ Sweep failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr[-500:] if result.stderr else 'No error output'}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Sweep timed out after 2 hours")
        return False
    except Exception as e:
        logger.error(f"❌ Sweep failed: {e}")
        return False


def main():
    """Main entry point - check if sweep needed and run if so"""
    logger.info("=" * 60)
    logger.info("🔍 LUMINA Daily Source Sweep - Startup Check")
    logger.info("=" * 60)

    today = date.today()
    last_sweep = get_last_sweep_date()

    logger.info(f"   Today: {today}")
    logger.info(f"   Last sweep: {last_sweep or 'Never'}")

    if last_sweep == today:
        logger.info("✅ Daily sweep already completed today. Skipping.")
        return

    if last_sweep:
        gap = (today - last_sweep).days
        logger.info(f"⚠️  Gap since last sweep: {gap} day(s)")
    else:
        logger.info("⚠️  No previous sweep found")

    logger.info("")
    logger.info("📋 Running daily source sweep...")

    success = run_sweep()
    save_sweep_state(success)

    if success:
        logger.info("")
        logger.info("✅ Daily sweep completed and state saved")
    else:
        logger.error("")
        logger.error("❌ Daily sweep failed - check logs for details")


if __name__ == "__main__":
    main()
