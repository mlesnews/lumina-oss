#!/usr/bin/env python3
"""
Verify All Daemons - Test and validate all daemon scripts

Verifies that all daemon scripts can be imported and initialized correctly.
Tests the daemon infrastructure without running full cycles.

@DAEMON @VERIFICATION @TEST
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VerifyAllDaemons")


DAEMONS_TO_VERIFY = [
    {
        "name": "BaseDaemon",
        "module": "daemon_template",
        "class": "BaseDaemon",
        "test_import": True,
        "abstract": True  # Skip instantiation test for abstract base class
    },
    {
        "name": "MasterFeedbackLoopDaemon",
        "module": "master_feedback_loop_daemon",
        "class": "MasterFeedbackLoopDaemon",
        "test_import": True
    },
    {
        "name": "JARVISGodLoopDaemon",
        "module": "jarvis_god_feedback_loop_daemon",
        "class": "JARVISGodLoopDaemon",
        "test_import": True
    },
    {
        "name": "LuminaFeedbackLoopDaemon",
        "module": "lumina_feedback_loop_daemon",
        "class": "LuminaFeedbackLoopDaemon",
        "test_import": True
    },
]


def verify_daemon(daemon_def: Dict[str, Any]) -> Dict[str, Any]:
    """Verify a single daemon"""
    result = {
        "name": daemon_def["name"],
        "success": False,
        "errors": [],
        "warnings": []
    }

    try:
        # Test import
        logger.info(f"Testing import: {daemon_def['module']}.{daemon_def['class']}")
        module = __import__(daemon_def["module"], fromlist=[daemon_def["class"]])
        daemon_class = getattr(module, daemon_def["class"])

        # Test instantiation (skip for abstract classes)
        if daemon_def.get("abstract", False):
            logger.info(f"Skipping instantiation test for abstract class: {daemon_def['name']}")
            # Just verify the class exists and has required attributes
            required_methods = ["_initialize", "_run_cycle", "_cleanup", "run"]
            for method_name in required_methods:
                if hasattr(daemon_class, method_name):
                    if not callable(getattr(daemon_class, method_name)):
                        result["errors"].append(f"{method_name} is not callable")
                else:
                    result["warnings"].append(f"Missing method: {method_name}")
        else:
            # Test instantiation (without running)
            logger.info(f"Testing instantiation: {daemon_def['name']}")
            daemon_instance = daemon_class(interval=3600, project_root=project_root)

            # Verify required methods exist
            required_methods = ["_initialize", "_run_cycle", "_cleanup", "run"]
            for method_name in required_methods:
                if not hasattr(daemon_instance, method_name):
                    result["warnings"].append(f"Missing method: {method_name}")
                else:
                    if not callable(getattr(daemon_instance, method_name)):
                        result["errors"].append(f"{method_name} is not callable")

        result["success"] = len(result["errors"]) == 0
        logger.info(f"✅ {daemon_def['name']}: Verification successful")

    except ImportError as e:
        result["errors"].append(f"Import error: {e}")
        logger.error(f"❌ {daemon_def['name']}: Import failed - {e}")
    except Exception as e:
        result["errors"].append(f"Error: {e}")
        logger.error(f"❌ {daemon_def['name']}: Verification failed - {e}", exc_info=True)

    return result


def verify_cron_configs() -> List[str]:
    try:
        """Verify cron config files exist"""
        cron_dir = project_root / "scripts" / "automation" / "nas_cron"
        missing_configs = []

        expected_configs = [
            "master_feedback_loop_cron.conf",
            "jarvis_god_loop_cron.conf",
            "lumina_feedback_loop_cron.conf",
            "unified_crontab.txt"
        ]

        for config_file in expected_configs:
            config_path = cron_dir / config_file
            if not config_path.exists():
                missing_configs.append(config_file)
                logger.warning(f"⚠️  Missing cron config: {config_file}")
            else:
                logger.info(f"✅ Found cron config: {config_file}")

        return missing_configs


    except Exception as e:
        logger.error(f"Error in verify_cron_configs: {e}", exc_info=True)
        raise
def verify_log_directories() -> List[str]:
    try:
        """Verify log directories exist or can be created"""
        log_base = project_root / "data" / "logs"
        log_base.mkdir(parents=True, exist_ok=True)

        required_dirs = [
            "master_feedback_loop",
            "jarvis_god_loop",
            "lumina_feedback_loop"
        ]

        missing_dirs = []
        for log_dir in required_dirs:
            log_path = log_base / log_dir
            log_path.mkdir(parents=True, exist_ok=True)
            if not log_path.exists():
                missing_dirs.append(log_dir)
                logger.warning(f"⚠️  Cannot create log directory: {log_dir}")
            else:
                logger.info(f"✅ Log directory ready: {log_dir}")

        return missing_dirs


    except Exception as e:
        logger.error(f"Error in verify_log_directories: {e}", exc_info=True)
        raise
def main():
    """Main verification"""
    print("="*80)
    print("Verifying All Daemons")
    print("="*80)
    print()

    results = []
    all_success = True

    # Verify daemons
    print("Verifying daemon scripts...")
    print("-"*80)
    for daemon_def in DAEMONS_TO_VERIFY:
        result = verify_daemon(daemon_def)
        results.append(result)
        if not result["success"]:
            all_success = False

    print()

    # Verify cron configs
    print("Verifying cron configurations...")
    print("-"*80)
    missing_configs = verify_cron_configs()
    if missing_configs:
        all_success = False

    print()

    # Verify log directories
    print("Verifying log directories...")
    print("-"*80)
    missing_dirs = verify_log_directories()
    if missing_dirs:
        all_success = False

    print()
    print("="*80)
    print("Verification Summary")
    print("="*80)
    print()

    # Print results
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status}: {result['name']}")

        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"  ⚠️  {warning}")

        if result["errors"]:
            for error in result["errors"]:
                print(f"  ❌ {error}")

    print()

    if missing_configs:
        print(f"⚠️  Missing cron configs: {', '.join(missing_configs)}")

    if missing_dirs:
        print(f"⚠️  Missing log directories: {', '.join(missing_dirs)}")

    print()

    if all_success and not missing_configs and not missing_dirs:
        print("✅ All verifications passed!")
        print()
        print("Daemons are ready for NAS cron deployment.")
        print(f"Install cron jobs: crontab {project_root}/scripts/automation/nas_cron/unified_crontab.txt")
        return 0
    else:
        print("❌ Some verifications failed. Please review errors above.")
        return 1


if __name__ == "__main__":


    sys.exit(main())