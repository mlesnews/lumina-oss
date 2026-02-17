#!/usr/bin/env python3
"""
Setup APICLI Endpoint @BAU Cron Scheduler

Generates and deploys cron configurations for APICLI endpoint @BAU daemon
on NAS with multiple intervals for different check types.

Intervals:
- @v3 Verification: Every 15-30 minutes (configurable)
- Health Checks: Every 5-10 minutes (configurable)
- Full Update: Every hour (configurable)

Tags: #APICLI #BAU #V3 #HEALTH_CHECK #NAS #CRON @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from lumina_core.paths import get_script_dir
script_dir = get_script_dir()
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
except ImportError:
    from lumina_core.logging import get_logger

logger = get_logger("SetupAPICLIBauCron")


def generate_cron_configs(
    project_root_path: Path,
    python_path: str = "/usr/bin/python3",
    intervals: Optional[Dict[str, int]] = None
) -> Dict[str, str]:
    """
    Generate cron configuration files for APICLI endpoint @BAU daemon

    Args:
        project_root_path: Project root directory
        python_path: Python interpreter path
        intervals: Dictionary with interval configurations

    Returns:
        Dictionary of cron configuration strings
    """
    if intervals is None:
        # Default intervals
        intervals = {
            "v3_verification": 15,  # Every 15 minutes
            "health_check": 5,     # Every 5 minutes
            "full_update": 60       # Every hour
        }

    cron_configs = {}

    # @v3 Verification - every 15 minutes (configurable)
    v3_cron = f"""# APICLI Endpoint @BAU - @v3 Verification
# Generated: {datetime.now().isoformat()}
# Run every {intervals['v3_verification']} minutes
# Purpose: Verify all endpoints with @v3 (first pass)

*/{intervals['v3_verification']} * * * * cd {project_root_path} && {python_path} scripts/python/apicli_endpoint_bau_daemon.py --mode v3_only --cycle >> /dev/null 2>&1

# Logs: data/logs/apicli_bau_v3_only/apicli_bau_v3_only_*.log
"""
    cron_configs['apicli_bau_v3'] = v3_cron

    # Health Checks - every 5 minutes (configurable)
    health_cron = f"""# APICLI Endpoint @BAU - Health & Welfare Checks
# Generated: {datetime.now().isoformat()}
# Run every {intervals['health_check']} minutes
# Purpose: Health and welfare checks on all interconnected endpoints (second pass)

*/{intervals['health_check']} * * * * cd {project_root_path} && {python_path} scripts/python/apicli_endpoint_bau_daemon.py --mode health_only --cycle >> /dev/null 2>&1

# Logs: data/logs/apicli_bau_health_only/apicli_bau_health_only_*.log
"""
    cron_configs['apicli_bau_health'] = health_cron

    # Full Update - every hour (configurable)
    full_cron = f"""# APICLI Endpoint @BAU - Full Update
# Generated: {datetime.now().isoformat()}
# Run every {intervals['full_update']} minutes
# Purpose: Comprehensive endpoint update with @v3 verification and health checks

*/{intervals['full_update']} * * * * cd {project_root_path} && {python_path} scripts/python/apicli_endpoint_bau_daemon.py --mode full --cycle >> /dev/null 2>&1

# Logs: data/logs/apicli_bau_full/apicli_bau_full_*.log
"""
    cron_configs['apicli_bau_full'] = full_cron

    return cron_configs


def create_deployment_script(
    configs: Dict[str, str],
    output_dir: Path,
    project_root: Path,
    python_path: str = "/usr/bin/python3",
    intervals: Optional[Dict[str, int]] = None
):
    """Create deployment script for NAS"""

    if intervals is None:
        intervals = {
            "v3_verification": 15,
            "health_check": 5,
            "full_update": 60
        }

    script_content = f"""#!/bin/bash
# APICLI Endpoint @BAU - NAS Cron Deployment Script
# Generated: {datetime.now().isoformat()}

set -e

PROJECT_ROOT="{project_root}"
PYTHON_PATH="{python_path}"

echo "=========================================="
echo "APICLI Endpoint @BAU Cron Deployment"
echo "=========================================="
echo ""

# Backup current crontab
echo "📦 Backing up current crontab..."
crontab -l > /tmp/crontab_backup_apicli_bau_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "✅ Backup complete"
echo ""

# Remove existing APICLI @BAU entries
echo "🧹 Removing existing APICLI @BAU cron entries..."
(crontab -l 2>/dev/null | grep -v "apicli_endpoint_bau_daemon.py" || true) | crontab -
echo "✅ Old entries removed"
echo ""

# Add @v3 Verification cron entry (every {intervals['v3_verification']} minutes)
echo "🔍 Adding @v3 Verification cron entry (every {intervals['v3_verification']} minutes)..."
(crontab -l 2>/dev/null; echo "*/{intervals['v3_verification']} * * * * cd $PROJECT_ROOT && $PYTHON_PATH scripts/python/apicli_endpoint_bau_daemon.py --mode v3_only --cycle >> /dev/null 2>&1") | crontab -
echo "✅ @v3 Verification scheduled"
echo ""

# Add Health Checks cron entry (every {intervals['health_check']} minutes)
echo "🏥 Adding Health & Welfare Checks cron entry (every {intervals['health_check']} minutes)..."
(crontab -l 2>/dev/null; echo "*/{intervals['health_check']} * * * * cd $PROJECT_ROOT && $PYTHON_PATH scripts/python/apicli_endpoint_bau_daemon.py --mode health_only --cycle >> /dev/null 2>&1") | crontab -
echo "✅ Health Checks scheduled"
echo ""

# Add Full Update cron entry (every {intervals['full_update']} minutes)
echo "🔄 Adding Full Update cron entry (every {intervals['full_update']} minutes)..."
(crontab -l 2>/dev/null; echo "*/{intervals['full_update']} * * * * cd $PROJECT_ROOT && $PYTHON_PATH scripts/python/apicli_endpoint_bau_daemon.py --mode full --cycle >> /dev/null 2>&1") | crontab -
echo "✅ Full Update scheduled"
echo ""

echo "=========================================="
echo "✅ APICLI Endpoint @BAU Cron Deployment Complete"
echo "=========================================="
echo ""
echo "Current crontab entries:"
crontab -l | grep "apicli_endpoint_bau_daemon.py" || echo "  (none found)"
echo ""
echo "Log locations:"
echo "  @v3 Verification: $PROJECT_ROOT/data/logs/apicli_bau_v3_only/"
echo "  Health Checks: $PROJECT_ROOT/data/logs/apicli_bau_health_only/"
echo "  Full Update: $PROJECT_ROOT/data/logs/apicli_bau_full/"
echo ""
echo "Intervals:"
echo "  @v3 Verification: Every {intervals['v3_verification']} minutes"
echo "  Health Checks: Every {intervals['health_check']} minutes"
echo "  Full Update: Every {intervals['full_update']} minutes"
echo ""
"""

    script_file = output_dir / "deploy_apicli_bau_cron.sh"
    script_file.write_text(script_content)
    script_file.chmod(0o755)

    logger.info(f"✅ Deployment script created: {script_file}")
    return script_file


def create_config_file(
    output_dir: Path,
    intervals: Optional[Dict[str, int]] = None
):
    """Create configuration file for intervals"""

    if intervals is None:
        intervals = {
            "v3_verification": 15,  # minutes
            "health_check": 5,      # minutes
            "full_update": 60        # minutes
        }

    config = {
        "intervals": intervals,
        "description": {
            "v3_verification": "Run @v3 verification on all endpoints (first pass)",
            "health_check": "Run health and welfare checks on interconnected endpoints (second pass)",
            "full_update": "Run comprehensive endpoint update with all checks"
        },
        "generated_at": datetime.now().isoformat(),
        "notes": [
            "Intervals are in minutes",
            "Multiple intervals allow for different check frequencies",
            "@v3 verification is less frequent (more comprehensive)",
            "Health checks are more frequent (lighter checks)",
            "Full update runs comprehensive checks"
        ]
    }

    config_file = output_dir / "apicli_bau_cron_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Configuration file created: {config_file}")
    return config_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup APICLI Endpoint @BAU Cron Scheduler for NAS"
    )
    parser.add_argument(
        "--v3-interval",
        type=int,
        default=15,
        help="@v3 verification interval in minutes (default: 15)"
    )
    parser.add_argument(
        "--health-interval",
        type=int,
        default=5,
        help="Health check interval in minutes (default: 5)"
    )
    parser.add_argument(
        "--full-interval",
        type=int,
        default=60,
        help="Full update interval in minutes (default: 60)"
    )
    parser.add_argument(
        "--python-path",
        type=str,
        default="/usr/bin/python3",
        help="Python interpreter path (default: /usr/bin/python3)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for cron configs (default: data/nas_cron/apicli_bau)"
    )

    args = parser.parse_args()

    from lumina_core.paths import get_project_root
    project_root = get_project_root()

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "data" / "nas_cron" / "apicli_bau"

    output_dir.mkdir(parents=True, exist_ok=True)

    intervals = {
        "v3_verification": args.v3_interval,
        "health_check": args.health_interval,
        "full_update": args.full_interval
    }

    logger.info("=" * 80)
    logger.info("APICLI Endpoint @BAU Cron Setup")
    logger.info("=" * 80)
    logger.info(f"   Project Root: {project_root}")
    logger.info(f"   Output Directory: {output_dir}")
    logger.info(f"   Python Path: {args.python_path}")
    logger.info("")
    logger.info("   Intervals:")
    logger.info(f"     @v3 Verification: Every {intervals['v3_verification']} minutes")
    logger.info(f"     Health Checks: Every {intervals['health_check']} minutes")
    logger.info(f"     Full Update: Every {intervals['full_update']} minutes")
    logger.info("")

    # Generate cron configs
    cron_configs = generate_cron_configs(
        project_root_path=project_root,
        python_path=args.python_path,
        intervals=intervals
    )

    # Save cron configs
    for name, config in cron_configs.items():
        config_file = output_dir / f"{name}.cron"
        config_file.write_text(config)
        logger.info(f"✅ Cron config saved: {config_file}")

    # Create deployment script
    deploy_script = create_deployment_script(
        configs=cron_configs,
        output_dir=output_dir,
        project_root=project_root,
        python_path=args.python_path,
        intervals=intervals
    )

    # Create config file
    config_file = create_config_file(
        output_dir=output_dir,
        intervals=intervals
    )

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ APICLI Endpoint @BAU Cron Setup Complete")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Next steps:")
    logger.info(f"  1. Review cron configs in: {output_dir}")
    logger.info(f"  2. Run deployment script on NAS: {deploy_script}")
    logger.info(f"  3. Verify cron entries: crontab -l | grep apicli_endpoint_bau_daemon")
    logger.info("")
    logger.info("To deploy on NAS:")
    logger.info(f"  scp {deploy_script} user@nas:/path/to/deploy_apicli_bau_cron.sh")
    logger.info(f"  ssh user@nas 'bash /path/to/deploy_apicli_bau_cron.sh'")
    logger.info("")


if __name__ == "__main__":


    main()