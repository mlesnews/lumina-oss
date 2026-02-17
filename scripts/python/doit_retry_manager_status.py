#!/usr/bin/env python3
"""
@DOIT: JARVIS Retry Manager Status Report

Comprehensive status report for the JARVIS Retry Manager system including:
- Configuration status
- Pending retries count
- NAS KronScheduler integration
- System health

Tags: #DOIT #RETRY_MANAGER #STATUS #REPORT @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

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

logger = get_logger("DoitRetryManagerStatus")

RETRY_MANAGER_CONFIG = project_root / "data" / "nas_kronscheduler" / "retry_manager_job.json"
RETRY_TRACKING_DIR = project_root / "data" / "cursor_retry_tracking"
PENDING_RETRIES_FILE = RETRY_TRACKING_DIR / "pending_retries.json"
PROCESSED_RETRIES_FILE = RETRY_TRACKING_DIR / "processed_retries.jsonl"


def check_configuration() -> Dict[str, Any]:
    """Check retry manager configuration"""
    logger.info("📋 Checking configuration...")

    if not RETRY_MANAGER_CONFIG.exists():
        logger.error("   ❌ Configuration file not found")
        return {
            "status": "❌ NOT CONFIGURED",
            "exists": False
        }

    try:
        with open(RETRY_MANAGER_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)

        logger.info("   ✅ Configuration file found")
        logger.info(f"   📋 Job Name: {config.get('job_name', 'N/A')}")
        logger.info(f"   📋 Script: {config.get('script', 'N/A')}")
        logger.info(f"   📋 Enabled: {config.get('enabled', False)}")

        schedule = config.get('schedule', {})
        interval = schedule.get('interval_hours', 0.25)
        logger.info(f"   📋 Schedule: Every {interval * 60:.0f} minutes")

        return {
            "status": "✅ CONFIGURED",
            "exists": True,
            "config": config,
            "enabled": config.get('enabled', False)
        }
    except Exception as e:
        logger.error(f"   ❌ Error reading configuration: {e}")
        return {
            "status": "❌ ERROR",
            "exists": True,
            "error": str(e)
        }


def check_pending_retries() -> Dict[str, Any]:
    """Check pending retries"""
    logger.info("")
    logger.info("🔄 Checking pending retries...")

    if not RETRY_TRACKING_DIR.exists():
        RETRY_TRACKING_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("   ✅ Retry tracking directory created")

    if not PENDING_RETRIES_FILE.exists():
        logger.info("   ✅ No pending retries")
        return {
            "status": "✅ NO PENDING RETRIES",
            "count": 0,
            "exists": False
        }

    try:
        with open(PENDING_RETRIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            retries = data
        elif isinstance(data, dict) and "pending_retries" in data:
            retries = data["pending_retries"]
        else:
            retries = []

        count = len(retries)
        if count > 0:
            logger.warning(f"   ⚠️  {count} pending retries found")
            for i, retry in enumerate(retries[:5], 1):  # Show first 5
                request_id = retry.get("request_id", "unknown")
                error = retry.get("error", "unknown")
                logger.info(f"      [{i}] {request_id}: {error[:50]}...")
            if count > 5:
                logger.info(f"      ... and {count - 5} more")
        else:
            logger.info("   ✅ No pending retries")

        return {
            "status": "⚠️  PENDING RETRIES" if count > 0 else "✅ NO PENDING RETRIES",
            "count": count,
            "exists": True,
            "retries": retries[:10]  # First 10 for details
        }
    except Exception as e:
        logger.error(f"   ❌ Error reading pending retries: {e}")
        return {
            "status": "❌ ERROR",
            "count": 0,
            "exists": True,
            "error": str(e)
        }


def check_processed_retries() -> Dict[str, Any]:
    """Check processed retries log"""
    logger.info("")
    logger.info("📊 Checking processed retries log...")

    if not PROCESSED_RETRIES_FILE.exists():
        logger.info("   ℹ️  No processed retries log (normal if no retries processed yet)")
        return {
            "status": "ℹ️  NO LOG",
            "count": 0,
            "exists": False
        }

    try:
        count = 0
        with open(PROCESSED_RETRIES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1

        logger.info(f"   ✅ {count} processed retries logged")
        return {
            "status": "✅ LOG EXISTS",
            "count": count,
            "exists": True
        }
    except Exception as e:
        logger.error(f"   ❌ Error reading processed retries: {e}")
        return {
            "status": "❌ ERROR",
            "count": 0,
            "exists": True,
            "error": str(e)
        }


def check_script_exists() -> Dict[str, Any]:
    try:
        """Check if retry processing script exists"""
        logger.info("")
        logger.info("🔍 Checking retry processing script...")

        script_path = project_root / "scripts" / "python" / "process_pending_retries.py"

        if script_path.exists():
            logger.info(f"   ✅ Script found: {script_path.name}")
            return {
                "status": "✅ EXISTS",
                "exists": True,
                "path": str(script_path)
            }
        else:
            logger.error(f"   ❌ Script not found: {script_path}")
            return {
                "status": "❌ NOT FOUND",
                "exists": False,
                "path": str(script_path)
            }


    except Exception as e:
        logger.error(f"Error in check_script_exists: {e}", exc_info=True)
        raise
def generate_status_report() -> Dict[str, Any]:
    """Generate comprehensive status report"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 JARVIS RETRY MANAGER STATUS REPORT")
    logger.info("=" * 80)
    logger.info(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    # Run all checks
    config_check = check_configuration()
    pending_check = check_pending_retries()
    processed_check = check_processed_retries()
    script_check = check_script_exists()

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("📋 STATUS SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Configuration: {config_check['status']}")
    logger.info(f"   Pending Retries: {pending_check['status']} ({pending_check.get('count', 0)} items)")
    logger.info(f"   Processed Log: {processed_check['status']} ({processed_check.get('count', 0)} entries)")
    logger.info(f"   Script: {script_check['status']}")
    logger.info("")

    # Overall status
    all_ok = (
        "✅" in config_check.get("status", "") and
        config_check.get("enabled", False) and
        script_check.get("exists", False) and
        pending_check.get("count", 0) == 0
    )

    if all_ok:
        logger.info("=" * 80)
        logger.info("✅ RETRY MANAGER: HEALTHY AND OPERATIONAL")
        logger.info("=" * 80)
    elif pending_check.get("count", 0) > 0:
        logger.info("=" * 80)
        logger.info("⚠️  RETRY MANAGER: PENDING RETRIES DETECTED")
        logger.info("=" * 80)
        logger.info("")
        logger.info("🔄 To process pending retries:")
        logger.info("   python scripts/python/process_pending_retries.py --max-retries 10")
    else:
        logger.info("=" * 80)
        logger.info("⚠️  RETRY MANAGER: CONFIGURATION ISSUES")
        logger.info("=" * 80)

    # Configuration details
    if config_check.get("config"):
        config = config_check["config"]
        logger.info("")
        logger.info("=" * 80)
        logger.info("⚙️  CONFIGURATION DETAILS")
        logger.info("=" * 80)
        logger.info(f"   Job Name: {config.get('job_name', 'N/A')}")
        logger.info(f"   Description: {config.get('description', 'N/A')}")
        logger.info(f"   Script: {config.get('script', 'N/A')}")
        logger.info(f"   Enabled: {config.get('enabled', False)}")

        schedule = config.get('schedule', {})
        interval = schedule.get('interval_hours', 0.25)
        logger.info(f"   Schedule: Every {interval * 60:.0f} minutes ({interval} hours)")
        logger.info(f"   Dynamic Scaling: {schedule.get('dynamic_scaling', False)}")

        if schedule.get('dynamic_scaling'):
            logger.info("   📊 Scaling Criteria:")
            criteria = schedule.get('scaling_criteria', {})
            for key, values in criteria.items():
                logger.info(f"      {key}:")
                for level, hours in values.items():
                    logger.info(f"         {level}: {hours} hours ({hours * 60:.0f} minutes)")

    # Manual execution
    logger.info("")
    logger.info("=" * 80)
    logger.info("🔧 MANUAL EXECUTION")
    logger.info("=" * 80)
    logger.info("")
    logger.info("To manually process pending retries:")
    logger.info("   python scripts/python/process_pending_retries.py --max-retries 10")
    logger.info("")
    logger.info("To check retry manager configuration:")
    logger.info(f"   {RETRY_MANAGER_CONFIG}")
    logger.info("")

    return {
        "timestamp": datetime.now().isoformat(),
        "config_check": config_check,
        "pending_check": pending_check,
        "processed_check": processed_check,
        "script_check": script_check,
        "overall_status": "✅ HEALTHY" if all_ok else "⚠️  ISSUES"
    }


def main():
    """CLI entry point"""
    report = generate_status_report()
    return 0 if "✅ HEALTHY" in report["overall_status"] else 1


if __name__ == "__main__":


    sys.exit(main())