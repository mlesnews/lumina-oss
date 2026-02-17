#!/usr/bin/env python3
"""
Convert All JARVIS Recurring Tasks to NAS Cron Scheduler

Converts all scheduled tasks from:
- config/lumina_scheduled_tasks.json (Windows Task Scheduler tasks)
- task_daemon_orchestrator.py (Periodic daemon tasks)

Into cron format for deployment on NAS (Synology/Linux).

@MARVIN @JARVIS @TONY @MACE @GANDALF
Enhanced with NAS Proxy-Cache System for full functionality and performance optimization.
"""

import json
import sys
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Import universal decision tree (optional)
try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [CRON_CONVERTER] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Import NAS Proxy-Cache System
try:
    from nas_physics_cache import TieredPhysicsCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.debug("NAS Proxy-Cache not available - running without caching")

# Paths
SCHEDULED_TASKS_CONFIG = project_root / "config" / "lumina_scheduled_tasks.json"
TASK_DAEMON_FILE = project_root / "scripts" / "python" / "task_daemon_orchestrator.py"
OUTPUT_CRON_FILE = project_root / "scripts" / "nas_cron" / "jarvis_crontab"
NAS_DEPLOY_SCRIPT = project_root / "scripts" / "nas_cron" / "deploy_jarvis_cron.sh"
NAS_PYTHON_PATH = "/volume1/@appstore/python3/bin/python3"  # Adjust for your NAS
NAS_PROJECT_PATH = "/volume1/docker/jarvis/.lumina"  # Adjust for your NAS



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CronConverter:
    """Convert JARVIS tasks to cron format with NAS Proxy-Cache integration"""

    def __init__(self, enable_cache: bool = True):
        self.cron_entries = []
        self.task_definitions = []
        self.cache = None
        self.cache_enabled = enable_cache and CACHE_AVAILABLE

        # Initialize NAS Proxy-Cache if available (using decision tree)
        if self.cache_enabled:
            try:
                # Use decision tree to determine if cache should be enabled
                if DECISION_TREE_AVAILABLE:
                    from universal_decision_tree import DecisionContext, decide, DecisionOutcome

                    context = DecisionContext(
                        urgency="low",  # Cron conversion is not urgent
                        cost_sensitive=True,  # Be cost-conscious
                        custom_data={"operation": "cache_initialization"}
                    )

                    # Decide whether to enable cache
                    result = decide("error_handling", context)
                    if result.outcome == DecisionOutcome.FAIL:
                        logger.debug("Decision tree recommended skipping cache initialization")
                        self.cache_enabled = False
                        return

                cache_config = self._load_cache_config()
                self.cache = TieredPhysicsCache(cache_config)

                # Use decision tree to assess cache tier availability
                if DECISION_TREE_AVAILABLE:
                    from universal_decision_tree import DecisionContext, decide

                    context = DecisionContext(
                        nas_cache_available=not self.cache.nas_client_pool.empty(),
                        nas_api_available=self.cache.nas_api_enabled if hasattr(self.cache, 'nas_api_enabled') else False,
                        nas_ssh_available=not self.cache.nas_client_pool.empty(),
                        cache_domain="jarvis_cron"
                    )

                    result = decide("nas_connection", context)
                    if result.outcome.value == "skip_nas":
                        logger.debug(f"NAS Proxy-Cache initialized (local cache only - L1+L2 tiers) [{result.reasoning}]")
                    else:
                        logger.debug(f"NAS Proxy-Cache initialized (full functionality - L1+L2+L3 tiers) [{result.reasoning}]")
                else:
                    # Fallback: Traditional check
                    if self.cache.nas_client_pool.empty():
                        logger.debug("NAS Proxy-Cache initialized (local cache only - L1+L2 tiers)")
                    else:
                        logger.debug("NAS Proxy-Cache initialized (full functionality - L1+L2+L3 tiers)")

            except Exception as e:
                # Use decision tree for error handling
                if DECISION_TREE_AVAILABLE:
                    from universal_decision_tree import DecisionContext, decide, DecisionOutcome

                    context = DecisionContext(
                        error_count=1,
                        last_error=str(e),
                        retry_count=0,
                        max_retries=1,
                        urgency="low"
                    )

                    result = decide("error_handling", context)
                    if result.outcome == DecisionOutcome.SKIP:
                        logger.debug(f"Failed to initialize cache: {e} - continuing without cache [{result.reasoning}]")
                        self.cache_enabled = False
                    else:
                        logger.debug(f"Failed to initialize cache: {e} - continuing without cache")
                        self.cache_enabled = False
                else:
                    logger.debug(f"Failed to initialize cache: {e} - continuing without cache")
                    self.cache_enabled = False

    def _load_cache_config(self) -> Dict[str, Any]:
        """Load NAS proxy-cache configuration"""
        # Try to load from dedicated config file
        cache_config_file = project_root / "config" / "nas_proxy_cache_config.yaml"
        nas_ssh_config_file = project_root / "config" / "lumina_nas_ssh_config.json"

        nas_config = {
            'host': '<NAS_PRIMARY_IP>',
            'user': 'backupadm',
            'base_path': '/volume1/cache/jarvis_cron',
            'timeout': 30
        }

        # Load NAS config from YAML if available
        if cache_config_file.exists() and YAML_AVAILABLE:
            try:
                with open(cache_config_file, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if 'nas' in yaml_config:
                        nas_config.update({
                            'host': yaml_config['nas'].get('host', nas_config['host']),
                            'user': yaml_config['nas'].get('user', nas_config['user']),
                            'base_path': yaml_config['nas'].get('base_path', nas_config['base_path']),
                            'timeout': yaml_config['nas'].get('connection_timeout', nas_config['timeout'])
                        })
            except Exception as e:
                logger.debug(f"Could not load cache config YAML: {e} - using defaults")

        # Fallback to SSH config JSON (includes Azure Key Vault settings)
        if nas_ssh_config_file.exists():
            try:
                with open(nas_ssh_config_file, 'r') as f:
                    ssh_config = json.load(f)
                    if 'nas' in ssh_config:
                        nas_config.update({
                            'host': ssh_config['nas'].get('host', nas_config['host']),
                            'user': ssh_config['nas'].get('username', nas_config['user']),
                            'username': ssh_config['nas'].get('username', nas_config['user']),
                            'timeout': ssh_config['nas'].get('timeout', nas_config['timeout']),
                            'port': ssh_config['nas'].get('port', 22),
                        })
                        # Add Azure Key Vault configuration for full API support
                        if 'password_source' in ssh_config['nas'] and ssh_config['nas']['password_source'] == 'azure_key_vault':
                            nas_config['vault_name'] = ssh_config['nas'].get('key_vault_name', 'jarvis-lumina')
                            nas_config['password_secret_name'] = ssh_config['nas'].get('password_secret_name', 'nas-password')
                            # Try to construct vault URL
                            vault_name = nas_config['vault_name']
                            if vault_name and not vault_name.startswith('https://'):
                                nas_config['vault_url'] = f"https://{vault_name}.vault.azure.net/"
                            nas_config['api_port'] = 5001  # Synology DSM default
            except Exception as e:
                logger.debug(f"Could not load SSH config: {e} - using defaults")

        return {
            'memory_limit': 512 * 1024 * 1024,  # 512MB for cron workflow
            'ssd_cache_dir': str(project_root / 'data' / 'cache' / 'jarvis_cron'),
            'ssd_limit': 10 * 1024 * 1024 * 1024,  # 10GB
            'nas_config': nas_config
        }

    def _get_file_checksum(self, file_path: Path) -> str:
        """Get file checksum for cache invalidation"""
        if not file_path.exists():
            return ""
        try:
            stat = file_path.stat()
            # Use modification time + size as checksum
            content = f"{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return ""

    def load_scheduled_tasks(self) -> Dict[str, Any]:
        try:
            """Load scheduled tasks from config file (with proxy-cache)"""
            if not SCHEDULED_TASKS_CONFIG.exists():
                logger.warning(f"Scheduled tasks config not found: {SCHEDULED_TASKS_CONFIG}")
                return {"tasks": [], "monthly_tasks": []}

            # Check cache first
            if self.cache_enabled:
                cache_key = f"tasks_config_{self._get_file_checksum(SCHEDULED_TASKS_CONFIG)}"
                cached_data = self.cache.get(cache_key)
                if cached_data is not None:
                    logger.debug(f"Using cached task configuration (cache key: {cache_key[:16]}...)")
                    return cached_data

            # Load from file
            with open(SCHEDULED_TASKS_CONFIG, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Cache the result
            if self.cache_enabled:
                cache_key = f"tasks_config_{self._get_file_checksum(SCHEDULED_TASKS_CONFIG)}"
                self.cache.put(
                    cache_key, 
                    data, 
                    physics_domain="jarvis_cron",
                    ttl_seconds=3600,  # 1 hour
                    metadata={"source_file": str(SCHEDULED_TASKS_CONFIG)}
                )

            return data

        except Exception as e:
            self.logger.error(f"Error in load_scheduled_tasks: {e}", exc_info=True)
            raise
    def parse_task_daemon_tasks(self) -> List[Dict[str, Any]]:
        try:
            """Parse periodic tasks from task_daemon_orchestrator.py"""
            daemon_tasks = []

            if not TASK_DAEMON_FILE.exists():
                logger.debug(f"Task daemon file not found: {TASK_DAEMON_FILE} - using default periodic tasks")
                return daemon_tasks

            # Read the file and extract periodic tasks
            with open(TASK_DAEMON_FILE, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract periodic task definitions
            # These are hardcoded in load_task_definitions()
            # We'll extract them manually based on known patterns

            periodic_tasks = [
                {
                    "name": "system_health_check",
                    "command": "scripts/python/verify_system_state.py",
                    "interval": 300,  # 5 minutes
                    "type": "periodic",
                    "priority": "critical"
                },
                {
                    "name": "kaiju_iron_legion_monitor",
                    "command": "scripts/python/kaiju_iron_legion_monitor_self_healing.py",
                    "interval": 1800,  # 30 minutes
                    "type": "periodic",
                    "priority": "low"
                },
                {
                    "name": "gap_analysis_scan",
                    "command": "scripts/python/simple_gap_scanner.py",
                    "interval": 3600,  # 1 hour
                    "type": "periodic",
                    "priority": "low"
                },
                {
                    "name": "parallel_agent_processing",
                    "command": "scripts/python/parallel_agent_session_processor.py",
                    "interval": 1800,  # 30 minutes
                    "type": "periodic",
                    "priority": "low"
                }
            ]

            return periodic_tasks

        except Exception as e:
            self.logger.error(f"Error in parse_task_daemon_tasks: {e}", exc_info=True)
            raise
    def convert_time_to_cron(self, schedule: Dict[str, Any]) -> str:
        """Convert schedule to cron format"""
        schedule_type = schedule.get("type", "daily")

        if schedule_type == "hourly":
            return "0 * * * *"  # Every hour at minute 0

        elif schedule_type == "daily":
            time_str = schedule.get("time", "00:00")
            hour, minute = map(int, time_str.split(":"))
            return f"{minute} {hour} * * *"  # Daily at specified time

        elif schedule_type == "weekly":
            day = schedule.get("day", "Monday")
            time_str = schedule.get("time", "00:00")
            hour, minute = map(int, time_str.split(":"))

            day_map = {
                "Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3,
                "Thursday": 4, "Friday": 5, "Saturday": 6
            }
            day_num = day_map.get(day, 0)
            return f"{minute} {hour} * * {day_num}"

        elif schedule_type == "monthly":
            day = schedule.get("day", 1)
            time_str = schedule.get("time", "00:00")
            hour, minute = map(int, time_str.split(":"))

            if day == -1:  # Last day of month
                # Use a workaround - run on 28-31 and check if it's the last day
                return f"{minute} {hour} 28-31 * *"  # Approximate
            else:
                return f"{minute} {hour} {day} * *"

        else:
            return "0 0 * * *"  # Default: daily at midnight

    def convert_interval_to_cron(self, interval_seconds: int) -> str:
        """Convert interval in seconds to cron format"""
        if interval_seconds < 60:
            # Less than a minute - use */interval format (every N seconds -> approximate with minutes)
            minutes = max(1, interval_seconds // 60)
            return f"*/{minutes} * * * *"
        elif interval_seconds < 3600:
            # Less than an hour - every N minutes
            minutes = interval_seconds // 60
            return f"*/{minutes} * * * *"
        elif interval_seconds < 86400:
            # Less than a day - every N hours
            hours = interval_seconds // 3600
            return f"0 */{hours} * * *"
        else:
            # Daily or more - convert to daily
            return "0 0 * * *"

    def create_cron_entry(self, task: Dict[str, Any]) -> str:
        try:
            """Create a single cron entry for a task (with proxy-cache)"""
            name = task.get("name", "unknown_task")
            script_path = task.get("script") or task.get("command", "")
            schedule = task.get("schedule", {})
            arguments = task.get("arguments", [])
            description = task.get("description", "")

            # Check cache first
            if self.cache_enabled:
                task_hash = hashlib.md5(json.dumps(task, sort_keys=True).encode()).hexdigest()
                cache_key = f"cron_entry_{name}_{task_hash}"
                cached_entry = self.cache.get(cache_key)
                if cached_entry is not None:
                    return cached_entry

            # Convert schedule to cron format
            if schedule:
                cron_time = self.convert_time_to_cron(schedule)
            elif "interval" in task:
                cron_time = self.convert_interval_to_cron(task["interval"])
            else:
                cron_time = "0 0 * * *"  # Default: daily at midnight

            # Build command
            if script_path.startswith("scripts/"):
                full_script_path = f"{NAS_PROJECT_PATH}/{script_path}"
            else:
                full_script_path = f"{NAS_PROJECT_PATH}/scripts/python/{script_path}"

            # Add arguments
            args_str = " ".join(arguments) if arguments else ""
            command = f"{NAS_PYTHON_PATH} {full_script_path} {args_str}".strip()

            # Add logging
            log_file = f"/volume1/docker/jarvis/.lumina/logs/cron_{name}.log"
            command_with_log = f"{command} >> {log_file} 2>&1"

            # Create cron entry with comment
            cron_entry = f"# {description or name}\n"
            cron_entry += f"{cron_time} {command_with_log}\n"

            # Cache the result
            if self.cache_enabled:
                task_hash = hashlib.md5(json.dumps(task, sort_keys=True).encode()).hexdigest()
                cache_key = f"cron_entry_{name}_{task_hash}"
                self.cache.put(
                    cache_key,
                    cron_entry,
                    physics_domain="jarvis_cron",
                    ttl_seconds=7200,  # 2 hours
                    metadata={"task_name": name, "script_path": script_path}
                )

            return cron_entry

        except Exception as e:
            self.logger.error(f"Error in create_cron_entry: {e}", exc_info=True)
            raise
    def convert_all_tasks(self) -> List[str]:
        """Convert all tasks to cron format"""
        cron_entries = []

        # Load scheduled tasks
        scheduled_config = self.load_scheduled_tasks()

        # Convert scheduled tasks
        logger.debug("Converting scheduled tasks from config...")
        for task in scheduled_config.get("tasks", []):
            if task.get("enabled", True):
                entry = self.create_cron_entry(task)
                cron_entries.append(entry)
                logger.debug(f"Converted task: {task['name']}")

        # Convert monthly tasks
        for task in scheduled_config.get("monthly_tasks", []):
            if task.get("enabled", True):
                entry = self.create_cron_entry(task)
                cron_entries.append(entry)
                logger.debug(f"Converted monthly task: {task['name']}")

        # Convert daemon periodic tasks
        logger.debug("Converting daemon periodic tasks...")
        daemon_tasks = self.parse_task_daemon_tasks()
        for task in daemon_tasks:
            entry = self.create_cron_entry(task)
            cron_entries.append(entry)
            logger.debug(f"Converted daemon task: {task['name']}")

        return cron_entries

    def generate_crontab(self) -> str:
        """Generate complete crontab file (with proxy-cache)"""
        # Check cache first
        if self.cache_enabled:
            # Create cache key from source file checksums
            config_checksum = self._get_file_checksum(SCHEDULED_TASKS_CONFIG)
            daemon_checksum = self._get_file_checksum(TASK_DAEMON_FILE)
            cache_key = f"full_crontab_{config_checksum}_{daemon_checksum}"

            cached_crontab = self.cache.get(cache_key)
            if cached_crontab is not None:
                logger.debug(f"Using cached crontab (cache key: {cache_key[:16]}...)")
                # Update header timestamp
                header_lines = cached_crontab.split('\n', 1)
                if len(header_lines) > 1:
                    new_header = f"""# JARVIS Recurring Tasks - NAS Cron Scheduler
# Generated: {datetime.now().isoformat()} (from cache)
# 
# This crontab contains all JARVIS recurring tasks converted from:
# - Windows Task Scheduler (config/lumina_scheduled_tasks.json)
# - Task Daemon Orchestrator (task_daemon_orchestrator.py)
#
# NAS Python Path: {NAS_PYTHON_PATH}
# NAS Project Path: {NAS_PROJECT_PATH}
#
# CRONTAB FORMAT:
# minute hour day-of-month month day-of-week command
#
# To install: crontab -e (then paste this file)
# Or use: ./deploy_jarvis_cron.sh

"""
                    return new_header + header_lines[1]

        header = f"""# JARVIS Recurring Tasks - NAS Cron Scheduler
# Generated: {datetime.now().isoformat()}
# 
# This crontab contains all JARVIS recurring tasks converted from:
# - Windows Task Scheduler (config/lumina_scheduled_tasks.json)
# - Task Daemon Orchestrator (task_daemon_orchestrator.py)
#
# NAS Python Path: {NAS_PYTHON_PATH}
# NAS Project Path: {NAS_PROJECT_PATH}
#
# CRONTAB FORMAT:
# minute hour day-of-month month day-of-week command
#
# To install: crontab -e (then paste this file)
# Or use: ./deploy_jarvis_cron.sh

"""

        cron_entries = self.convert_all_tasks()
        crontab_content = header + "\n".join(cron_entries)

        # Cache the result
        if self.cache_enabled:
            config_checksum = self._get_file_checksum(SCHEDULED_TASKS_CONFIG)
            daemon_checksum = self._get_file_checksum(TASK_DAEMON_FILE)
            cache_key = f"full_crontab_{config_checksum}_{daemon_checksum}"
            self.cache.put(
                cache_key,
                crontab_content,
                physics_domain="jarvis_cron",
                ttl_seconds=3600,  # 1 hour
                metadata={"source_files": [str(SCHEDULED_TASKS_CONFIG), str(TASK_DAEMON_FILE)]}
            )

        return crontab_content

    def generate_deploy_script(self) -> str:
        """Generate deployment script for NAS"""
        script_content = f"""#!/bin/bash
# Deploy JARVIS Cron Jobs to NAS
# This script installs all JARVIS recurring tasks as cron jobs on NAS

set -e

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
CRON_FILE="$SCRIPT_DIR/jarvis_crontab"
BACKUP_FILE="/tmp/jarvis_crontab_backup_$(date +%Y%m%d_%H%M%S)"

echo "🚀 Deploying JARVIS Cron Jobs to NAS"
echo "====================================="
echo ""

# Check if crontab file exists
if [ ! -f "$CRON_FILE" ]; then
    echo "❌ Error: Cron file not found: $CRON_FILE"
    exit 1
fi

# Backup existing crontab
echo "📦 Backing up existing crontab..."
crontab -l > "$BACKUP_FILE" 2>/dev/null || echo "# Empty crontab" > "$BACKUP_FILE"
echo "   Backup saved to: $BACKUP_FILE"

# Install new crontab
echo "📥 Installing JARVIS cron jobs..."
crontab "$CRON_FILE"

# Verify installation
echo "✅ Verifying installation..."
crontab -l | grep -q "JARVIS Recurring Tasks" && echo "   ✅ JARVIS cron jobs installed successfully" || echo "   ⚠️  Warning: Installation may have failed"

echo ""
echo "📊 Current crontab entries:"
crontab -l | grep -v "^#" | grep -v "^$" | wc -l | xargs echo "   Total entries:"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To view crontab: crontab -l"
echo "To edit crontab: crontab -e"
echo "To remove JARVIS jobs: Restore from $BACKUP_FILE"

"""
        return script_content


def main():
    try:
        """Main entry point"""
        print("🔄 Converting JARVIS Tasks to NAS Cron Format")
        print("=" * 60)
        print()

        converter = CronConverter()

        # Generate crontab
        print("📝 Generating crontab file...")
        crontab_content = converter.generate_crontab()

        # Create output directory
        output_dir = project_root / "scripts" / "nas_cron"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write crontab file
        crontab_file = output_dir / "jarvis_crontab"
        with open(crontab_file, 'w', encoding='utf-8') as f:
            f.write(crontab_content)

        print(f"✅ Crontab file generated: {crontab_file}")

        # Generate deployment script
        print("\n📝 Generating deployment script...")
        deploy_script_content = converter.generate_deploy_script()
        deploy_script_file = output_dir / "deploy_jarvis_cron.sh"

        with open(deploy_script_file, 'w', encoding='utf-8') as f:
            f.write(deploy_script_content)

        # Make executable
        import os
        os.chmod(deploy_script_file, 0o755)

        print(f"✅ Deployment script generated: {deploy_script_file}")

        # Summary
        entry_count = crontab_content.count("\n# ")  # Count task entries
        print(f"\n📊 Summary:")
        print(f"   Total cron entries: {entry_count}")
        print(f"   Output directory: {output_dir}")

        # Cache metrics
        if converter.cache_enabled and converter.cache:
            cache_metrics = converter.cache.get_metrics()
            print(f"\n📦 Proxy-Cache Performance:")
            print(f"   Cache hits: {cache_metrics.get('hit_count', 0)}")
            print(f"   Cache misses: {cache_metrics.get('miss_count', 0)}")
            hit_rate = cache_metrics.get('hit_rate', 0.0)
            print(f"   Hit rate: {hit_rate:.1%}")
            print(f"   Memory usage: {cache_metrics.get('memory_usage_percent', 0):.1f}%")

        print()
        print("📋 Next Steps:")
        print(f"   1. Review crontab file: {crontab_file}")
        print(f"   2. Adjust NAS_PROJECT_PATH and NAS_PYTHON_PATH if needed")
        print(f"   3. Copy files to NAS:")
        print(f"      scp {crontab_file} user@nas:/path/to/jarvis/scripts/nas_cron/")
        print(f"      scp {deploy_script_file} user@nas:/path/to/jarvis/scripts/nas_cron/")
        print(f"   4. SSH to NAS and run:")
        print(f"      cd /path/to/jarvis/scripts/nas_cron")
        print(f"      ./deploy_jarvis_cron.sh")
        print()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())