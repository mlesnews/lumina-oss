#!/usr/bin/env python3
"""
HOLOCRON BACKUP SCHEDULER
DBA/DBE Team - Automated Backup Scheduling

Integrates with NAS cron/scheduler systems for automated backups
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse
import logging
logger = logging.getLogger("schedule_holocron_backups")


# Configuration template for NAS schedulers
CRON_TEMPLATE = """# Holocron Backup Schedule
# Generated: {timestamp}

# Daily backup at 2 AM
0 2 * * * {python_path} {script_path} --host {host} --user {user} --database {database} --backup-dir {backup_dir} --action backup

# Weekly cleanup (remove backups older than 30 days) - Sunday at 3 AM
0 3 * * 0 {python_path} {script_path} --host {host} --user {user} --database {database} --backup-dir {backup_dir} --action cleanup --retention-days 30
"""

SYSTEMD_SERVICE_TEMPLATE = """[Unit]
Description=Holocron Backup Service
After=network.target

[Service]
Type=oneshot
ExecStart={python_path} {script_path} --host {host} --user {user} --database {database} --backup-dir {backup_dir} --action backup
Environment="MARIADB_PASSWORD={password}"

[Install]
WantedBy=multi-user.target
"""

SYSTEMD_TIMER_TEMPLATE = """[Unit]
Description=Holocron Backup Timer
Requires=holocron-backup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
"""

def generate_cron_config(config_file: Path, output_file: Path):
    try:
        """Generate cron configuration."""
        with open(config_file, 'r') as f:
            config = json.load(f)

        script_path = Path(__file__).parent / 'backup_mariadb_holocrons.py'
        python_path = sys.executable

        cron_config = CRON_TEMPLATE.format(
            timestamp=datetime.now().isoformat(),
            python_path=python_path,
            script_path=script_path,
            host=config['host'],
            user=config['user'],
            database=config['database'],
            backup_dir=config['backup_dir']
        )

        with open(output_file, 'w') as f:
            f.write(cron_config)

        print(f"✅ Cron config generated: {output_file}")
        print(f"\n📋 To install on NAS:")
        print(f"   crontab -e")
        print(f"   # Then paste contents of {output_file}")

    except Exception as e:
        logger.error(f"Error in generate_cron_config: {e}", exc_info=True)
        raise
def generate_systemd_config(config_file: Path, output_dir: Path):
    try:
        """Generate systemd service and timer files."""
        with open(config_file, 'r') as f:
            config = json.load(f)

        script_path = Path(__file__).parent / 'backup_mariadb_holocrons.py'
        python_path = sys.executable

        # Service file
        service_content = SYSTEMD_SERVICE_TEMPLATE.format(
            python_path=python_path,
            script_path=script_path,
            host=config['host'],
            user=config['user'],
            database=config['database'],
            backup_dir=config['backup_dir'],
            password=config.get('password', '${MARIADB_PASSWORD}')
        )

        service_file = output_dir / 'holocron-backup.service'
        with open(service_file, 'w') as f:
            f.write(service_content)

        # Timer file
        timer_content = SYSTEMD_TIMER_TEMPLATE.format()
        timer_file = output_dir / 'holocron-backup.timer'
        with open(timer_file, 'w') as f:
            f.write(timer_content)

        print(f"✅ Systemd files generated:")
        print(f"   Service: {service_file}")
        print(f"   Timer: {timer_file}")
        print(f"\n📋 To install:")
        print(f"   sudo cp {service_file} /etc/systemd/system/")
        print(f"   sudo cp {timer_file} /etc/systemd/system/")
        print(f"   sudo systemctl daemon-reload")
        print(f"   sudo systemctl enable holocron-backup.timer")
        print(f"   sudo systemctl start holocron-backup.timer")

    except Exception as e:
        logger.error(f"Error in generate_systemd_config: {e}", exc_info=True)
        raise
def create_config_template(output_file: Path):
    try:
        """Create configuration template."""
        config = {
            "host": "your_nas_ip",
            "port": 3306,
            "user": "your_username",
            "password": "your_password_or_env_var",
            "database": "lumina_holocrons",
            "backup_dir": "/path/to/backups",
            "retention_days": 30,
            "backup_schedule": {
                "daily": "02:00",
                "weekly_cleanup": "Sunday 03:00"
            }
        }

        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Config template created: {output_file}")
        print("   Edit this file with your MariaDB connection details")

    except Exception as e:
        logger.error(f"Error in create_config_template: {e}", exc_info=True)
        raise
def main():
    try:
        parser = argparse.ArgumentParser(
            description="Generate backup scheduler configurations"
        )
        parser.add_argument(
            '--config',
            type=str,
            help='Configuration file path'
        )
        parser.add_argument(
            '--create-config',
            type=str,
            help='Create config template at this path'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file/directory for generated configs'
        )
        parser.add_argument(
            '--type',
            choices=['cron', 'systemd', 'both'],
            default='cron',
            help='Type of scheduler config to generate'
        )

        args = parser.parse_args()

        if args.create_config:
            create_config_template(Path(args.create_config))
            return

        if not args.config:
            print("❌ --config required (or use --create-config to create template)")
            sys.exit(1)

        config_file = Path(args.config)
        if not config_file.exists():
            print(f"❌ Config file not found: {config_file}")
            sys.exit(1)

        if args.type in ('cron', 'both'):
            output_file = Path(args.output) if args.output else Path('holocron_backup.cron')
            generate_cron_config(config_file, output_file)

        if args.type in ('systemd', 'both'):
            output_dir = Path(args.output).parent if args.output else Path('.')
            generate_systemd_config(config_file, output_dir)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()