#!/usr/bin/env python3
"""
Setup NAS Cron Daemons

Generates and deploys cron configurations for JARVIS God Feedback Loop
and Lumina Feedback Loop daemons on NAS.

@JARVIS @LUMINA @NAS @CRON @DAEMON
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupNASCronDaemons")


def generate_cron_configs(project_root_path: Path, python_path: str = "/usr/bin/python3") -> Dict[str, str]:
    """Generate cron configuration files"""

    cron_configs = {}

    # JARVIS God Loop - every hour
    jarvis_cron = f"""# JARVIS God Feedback Loop - NAS Cron Configuration
# Generated: {datetime.now().isoformat()}
# Run every hour at minute 0

0 * * * * cd {project_root_path} && {python_path} scripts/python/jarvis_god_feedback_loop_daemon.py --cycle >> /dev/null 2>&1

# Logs: data/logs/jarvis_god_loop/jarvis_god_loop_*.log
"""
    cron_configs['jarvis_god_loop'] = jarvis_cron

    # Lumina Feedback Loop - every hour at minute 30 (offset)
    lumina_cron = f"""# Lumina Feedback Loop - NAS Cron Configuration
# Generated: {datetime.now().isoformat()}
# Run every hour at minute 30 (offset from JARVIS God Loop)

30 * * * * cd {project_root_path} && {python_path} scripts/python/lumina_feedback_loop_daemon.py --cycle >> /dev/null 2>&1

# Logs: data/logs/lumina_feedback_loop/lumina_feedback_loop_*.log
"""
    cron_configs['lumina_feedback_loop'] = lumina_cron

    return cron_configs


def create_deployment_script(configs: Dict[str, str], output_dir: Path):
    """Create deployment script for NAS"""

    script_content = f"""#!/bin/bash
# NAS Cron Deployment Script
# Generated: {datetime.now().isoformat()}

set -e

PROJECT_ROOT="{project_root}"
PYTHON_PATH="/usr/bin/python3"

echo "Deploying NAS cron configurations..."

# Backup current crontab
echo "Backing up current crontab..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Add JARVIS God Loop cron entry
echo "Adding JARVIS God Loop cron entry..."
(crontab -l 2>/dev/null | grep -v "jarvis_god_feedback_loop_daemon.py" || true; echo "0 * * * * cd $PROJECT_ROOT && $PYTHON_PATH scripts/python/jarvis_god_feedback_loop_daemon.py --cycle >> /dev/null 2>&1") | crontab -

# Add Lumina Feedback Loop cron entry
echo "Adding Lumina Feedback Loop cron entry..."
(crontab -l 2>/dev/null | grep -v "lumina_feedback_loop_daemon.py" || true; echo "30 * * * * cd $PROJECT_ROOT && $PYTHON_PATH scripts/python/lumina_feedback_loop_daemon.py --cycle >> /dev/null 2>&1") | crontab -

echo "✅ Cron configurations deployed"
echo ""
echo "Current crontab:"
crontab -l

echo ""
echo "Log locations:"
echo "  JARVIS God Loop: $PROJECT_ROOT/data/logs/jarvis_god_loop/"
echo "  Lumina Feedback Loop: $PROJECT_ROOT/data/logs/lumina_feedback_loop/"
"""

    script_file = output_dir / "deploy_nas_cron.sh"
    script_file.write_text(script_content)
    script_file.chmod(0o755)

    return script_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup NAS Cron Daemons")
    parser.add_argument("--project-root", type=Path, default=project_root,
                       help="Project root directory")
    parser.add_argument("--python-path", type=str, default="/usr/bin/python3",
                       help="Python executable path")
    parser.add_argument("--output-dir", type=Path,
                       default=project_root / "scripts" / "automation" / "nas_cron",
                       help="Output directory for cron configs")
    parser.add_argument("--deploy", action="store_true",
                       help="Deploy to NAS (requires nas_kron_daemon_manager)")

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate configs
    logger.info("Generating cron configurations...")
    configs = generate_cron_configs(args.project_root, args.python_path)

    # Write config files
    for name, content in configs.items():
        config_file = args.output_dir / f"{name}_cron.conf"
        config_file.write_text(content)
        logger.info(f"✅ Created: {config_file}")

    # Create deployment script
    deploy_script = create_deployment_script(configs, args.output_dir)
    logger.info(f"✅ Created: {deploy_script}")

    # Deploy if requested
    if args.deploy:
        try:
            from nas_kron_daemon_manager import NASKronDaemonManager

            logger.info("Deploying to NAS...")
            manager = NASKronDaemonManager()

            for name in configs.keys():
                config_file = args.output_dir / f"{name}_cron.conf"
                if manager.deploy_cron_to_nas(config_file):
                    logger.info(f"✅ Deployed {name} cron to NAS")
                else:
                    logger.error(f"❌ Failed to deploy {name} cron to NAS")

        except ImportError:
            logger.warning("nas_kron_daemon_manager not available - skipping deployment")
            logger.info("Run deploy script manually: bash scripts/automation/nas_cron/deploy_nas_cron.sh")

    print("\n" + "="*80)
    print("✅ NAS Cron Daemon Setup Complete!")
    print("="*80)
    print(f"\nConfiguration files created in: {args.output_dir}")
    print("\nTo deploy manually:")
    print(f"  bash {deploy_script}")
    print("\nOr add to crontab manually:")
    print("  crontab -e")
    print("  # Then add the lines from the *_cron.conf files")
    print("\nLog locations:")
    print(f"  JARVIS God Loop: {args.project_root}/data/logs/jarvis_god_loop/")
    print(f"  Lumina Feedback Loop: {args.project_root}/data/logs/lumina_feedback_loop/")


if __name__ == "__main__":


    main()