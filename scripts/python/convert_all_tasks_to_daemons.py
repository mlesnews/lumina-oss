#!/usr/bin/env python3
"""
Convert All Tasks to NAS Cron Scheduled Headless Terminal-less Daemons

Scans for task scripts and converts them to daemons with full logging module support.
Creates daemon wrappers and cron configurations for NAS deployment.

@DAEMON @NAS @CRON @LOGGING @AUTOMATION
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConvertAllTasksToDaemons")


# Task definitions - scripts that should be daemonized
TASK_DEFINITIONS = [
    {
        "name": "master_feedback_loop",
        "module": "master_feedback_loop_autonomous_executor",
        "class": "MasterFeedbackLoopAutonomousExecutor",
        "daemon_name": "MasterFeedbackLoopDaemon",
        "interval": 3600,  # 1 hour
        "cron_schedule": "0 */6 * * *",  # Every 6 hours
        "description": "Master Feedback Loop Autonomous Executor"
    },
    {
        "name": "jarvis_god_loop",
        "module": "jarvis_god_feedback_loop",
        "class": "JARVISGodFeedbackLoop",
        "daemon_name": "JARVISGodLoopDaemon",
        "daemon_file": "jarvis_god_feedback_loop_daemon.py",  # Already exists
        "interval": 3600,
        "cron_schedule": "0 * * * *",  # Every hour
        "description": "JARVIS God Feedback Loop"
    },
    {
        "name": "lumina_feedback_loop",
        "module": "lumina_data_mining_feedback_loop",
        "class": "LuminaFeedbackLoop",
        "daemon_name": "LuminaFeedbackLoopDaemon",
        "daemon_file": "lumina_feedback_loop_daemon.py",  # Already exists
        "interval": 3600,
        "cron_schedule": "30 * * * *",  # Every hour at :30 (offset from JARVIS)
        "description": "Lumina Data Mining Feedback Loop"
    },
]


def create_daemon_script(task_def: Dict[str, Any], output_dir: Path) -> Path:
    try:
        """
        Create daemon script for a task definition.

        Returns path to created daemon script.
        """
        # If daemon file already specified and exists, skip
        if task_def.get("daemon_file"):
            daemon_file = script_dir / task_def["daemon_file"]
            if daemon_file.exists():
                logger.info(f"✅ Daemon file already exists: {daemon_file.name}")
                return daemon_file

        daemon_name = task_def["daemon_name"]
        module = task_def["module"]
        class_name = task_def["class"]
        log_subdirectory = task_def["name"]
        interval = task_def.get("interval", 3600)

        # Generate daemon script content
        script_content = f'''#!/usr/bin/env python3
"""
{daemon_name} - Headless Terminal-less Daemon with Logging

Runs {class_name} as a headless daemon for NAS cron scheduling.
No terminal/TTY required. All output goes to log files.

@DAEMON @NAS @CRON @LOGGING
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from daemon_template import BaseDaemon

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from {module} import {class_name}
except ImportError as e:
    import logging
    logging.error(f"Failed to import {class_name}: {{e}}", exc_info=True)
    sys.exit(1)


class {daemon_name}(BaseDaemon):
    """Headless daemon wrapper for {class_name}"""

    def __init__(self, interval: int = {interval}, project_root: Optional[Path] = None):
        super().__init__(
            daemon_name="{daemon_name}",
            log_subdirectory="{log_subdirectory}",
            project_root=project_root,
            interval=interval
        )
        self.executor: Optional[{class_name}] = None

    def _initialize(self):
        """Initialize the target class instance"""
        self.logger.info(f"Initializing {class_name}...")
        try:
            self.executor = {class_name}(project_root=self.project_root)
            self.logger.info(f"{class_name} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize {class_name}: {{e}}", exc_info=True)
            raise

    def _run_cycle(self) -> bool:
        """Run one cycle of the daemon's work"""
        if not self.executor:
            self.logger.error("{class_name} not initialized")
            return False

        try:
            # Try different execution methods
            executor = self.executor

            # Check for async execute method
            if hasattr(executor, 'execute_autonomous'):
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(executor.execute_autonomous())
                    return result.get('final_status') != 'failed' if isinstance(result, dict) else result is not False
                finally:
                    loop.close()
            elif hasattr(executor, 'run_cycle'):
                result = executor.run_cycle()
                return result is not False
            elif hasattr(executor, 'execute'):
                result = executor.execute()
                return result is not False
            elif hasattr(executor, 'run'):
                result = executor.run()
                return result is not False
            else:
                self.logger.error("No suitable execution method found in {class_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error executing cycle: {{e}}", exc_info=True)
            return False

    def _cleanup(self):
        """Cleanup resources"""
        if self.executor:
            if hasattr(self.executor, 'cleanup'):
                try:
                    self.executor.cleanup()
                except Exception as e:
                    self.logger.error(f"Error during cleanup: {{e}}", exc_info=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="{daemon_name}")
    parser.add_argument('--cycle', action='store_true', help='Run single cycle and exit')
    parser.add_argument('--interval', type=int, default={interval}, help='Cycle interval in seconds')
    parser.add_argument('--project-root', type=str, help='Project root directory')

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else None

    daemon = {daemon_name}(interval=args.interval, project_root=project_root)

    if args.cycle:
        # Single cycle mode (for cron)
        daemon._initialize()
        try:
            success = daemon._run_cycle()
            sys.exit(0 if success else 1)
        finally:
            daemon._cleanup()
    else:
        # Continuous mode
        daemon.run()


if __name__ == "__main__":
    main()
'''

        # Write daemon script
        daemon_file = output_dir / f"{task_def['name']}_daemon.py"
        daemon_file.write_text(script_content)
        daemon_file.chmod(0o755)

        logger.info(f"✅ Created daemon script: {daemon_file.name}")
        return daemon_file
    except Exception as e:
        logger.error(f"Error in create_daemon_script: {e}", exc_info=True)
        raise


def create_cron_config(task_def: Dict[str, Any], project_root_path: Path, 
                       python_path: str = "/usr/bin/python3") -> str:
    """Create cron configuration for a task"""

    daemon_file = f"{task_def['name']}_daemon.py"
    cron_schedule = task_def.get("cron_schedule", "0 * * * *")
    description = task_def.get("description", task_def["name"])
    log_subdirectory = task_def["name"]

    config = f"""# {description} - NAS Cron Configuration
# Generated: {datetime.now().isoformat()}
# Schedule: {cron_schedule}
# Description: {description}

{cron_schedule} cd {project_root_path} && {python_path} scripts/python/{daemon_file} --cycle >> /dev/null 2>&1

# Logs: data/logs/{log_subdirectory}/{log_subdirectory}_*.log
"""

    return config


def generate_all_configs(project_root_path: Path, python_path: str = "/usr/bin/python3",
                        output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Generate all daemon scripts and cron configs"""

    if output_dir is None:
        output_dir = script_dir

    cron_dir = project_root_path / "scripts" / "automation" / "nas_cron"
    cron_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "daemons_created": [],
        "daemons_existing": [],
        "cron_configs": {},
        "errors": []
    }

    logger.info("Converting all tasks to daemons...")

    for task_def in TASK_DEFINITIONS:
        try:
            task_name = task_def["name"]
            logger.info(f"\nProcessing: {task_name}")

            # Create daemon script
            try:
                daemon_file = create_daemon_script(task_def, output_dir)
                if daemon_file.exists():
                    if task_def.get("daemon_file"):
                        results["daemons_existing"].append(daemon_file.name)
                    else:
                        results["daemons_created"].append(daemon_file.name)
            except Exception as e:
                logger.error(f"Failed to create daemon for {task_name}: {e}", exc_info=True)
                results["errors"].append(f"{task_name}: {str(e)}")
                continue

            # Create cron config
            try:
                cron_config = create_cron_config(task_def, project_root_path, python_path)
                cron_file = cron_dir / f"{task_name}_cron.conf"
                cron_file.write_text(cron_config)
                results["cron_configs"][task_name] = str(cron_file)
                logger.info(f"✅ Created cron config: {cron_file.name}")
            except Exception as e:
                logger.error(f"Failed to create cron config for {task_name}: {e}", exc_info=True)
                results["errors"].append(f"{task_name} cron: {str(e)}")

        except Exception as e:
            logger.error(f"Error processing {task_def.get('name', 'unknown')}: {e}", exc_info=True)
            results["errors"].append(f"{task_def.get('name', 'unknown')}: {str(e)}")

    return results


def create_unified_crontab(configs: Dict[str, str], output_dir: Path, 
                           project_root_path: Path) -> Path:
    """Create unified crontab file"""

    content = f"""# Unified NAS Cron Configuration
# Generated: {datetime.now().isoformat()}
# All daemon tasks for Lumina/JARVIS system
# 
# To install: crontab {output_dir / 'unified_crontab.txt'}

"""

    for task_name, config_file in configs.items():
        config_path = Path(config_file)
        if config_path.exists():
            config_content = config_path.read_text()
            # Extract just the cron line
            for line in config_content.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    content += line + '\n'

    content += "\n# All logs are in: data/logs/<task_name>/\n"

    crontab_file = output_dir / "unified_crontab.txt"
    crontab_file.write_text(content)

    return crontab_file


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Convert All Tasks to NAS Cron Daemons")
        parser.add_argument("--project-root", type=Path, default=project_root,
                           help="Project root directory")
        parser.add_argument("--python-path", type=str, default="/usr/bin/python3",
                           help="Python executable path")
        parser.add_argument("--output-dir", type=Path, default=script_dir,
                           help="Output directory for daemon scripts")

        args = parser.parse_args()

        logger.info("="*80)
        logger.info("Converting All Tasks to NAS Cron Scheduled Headless Daemons")
        logger.info("="*80)

        # Generate all configs
        results = generate_all_configs(
            args.project_root,
            args.python_path,
            args.output_dir
        )

        # Create unified crontab
        cron_dir = args.project_root / "scripts" / "automation" / "nas_cron"
        if results["cron_configs"]:
            unified_crontab = create_unified_crontab(results["cron_configs"], cron_dir, args.project_root)
            logger.info(f"✅ Created unified crontab: {unified_crontab}")

        # Summary
        print("\n" + "="*80)
        print("✅ Conversion Complete!")
        print("="*80)
        print(f"\nDaemons created: {len(results['daemons_created'])}")
        for daemon in results["daemons_created"]:
            print(f"  ✅ {daemon}")

        print(f"\nDaemons already existing: {len(results['daemons_existing'])}")
        for daemon in results["daemons_existing"]:
            print(f"  ✓ {daemon}")

        print(f"\nCron configs created: {len(results['cron_configs'])}")
        for task_name, config_file in results["cron_configs"].items():
            print(f"  ✅ {Path(config_file).name}")

        if results["errors"]:
            print(f"\nErrors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  ❌ {error}")

        print(f"\nTo install cron jobs:")
        print(f"  crontab {cron_dir / 'unified_crontab.txt'}")
        print(f"\nOr install individually:")
        for task_name, config_file in results["cron_configs"].items():
            print(f"  perl -pe '' {config_file} | crontab -")
            print(f"  # Or: awk '{{print}}' {config_file} | crontab -")
            print(f"  # Or: sed '' {config_file} | crontab -")
            print(f"  # Or: crontab - < {config_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()