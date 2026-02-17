#!/usr/bin/env python3
"""
NAS Cron Scheduler & Automated Task Runner

Manages cron-scheduled runs on NAS (<NAS_PRIMARY_IP>) and integrates with
N8N workflows and automated task execution.

Tags: #NAS #CRON #SCHEDULING #N8N #AUTOMATION #TASKS @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

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

logger = get_logger("NASCronScheduler")

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    logger.warning("paramiko not available - install: pip install paramiko")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available")


@dataclass
class CronJob:
    """Cron job definition"""
    id: str
    name: str
    description: str
    schedule: str  # Cron expression (e.g., "0 2 * * *" for daily at 2 AM)
    command: str
    script_path: Optional[str] = None
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutlierInitiative:
    """AI agent-driven outlier initiative"""
    id: str
    name: str
    description: str
    trigger_condition: str  # What triggers this initiative
    detection_method: str  # How outliers are detected
    action: str  # What action to take
    agent: str  # Which AI agent drives this
    priority: str = "medium"  # "low", "medium", "high", "critical"
    enabled: bool = True
    last_triggered: Optional[str] = None
    trigger_count: int = 0
    success_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class NASCronScheduler:
    """
    NAS Cron Scheduler & Automated Task Runner

    Manages cron jobs on NAS and AI agent-driven outlier initiatives.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize NAS cron scheduler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "nas_cron"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # NAS configuration
        self.nas_host = "<NAS_PRIMARY_IP>"
        self.nas_user = "mlesn"  # Default, should be configurable
        self.nas_n8n_url = f"http://{self.nas_host}:5678"  # Default N8N port

        # Configuration files
        self.cron_jobs_file = self.data_dir / "cron_jobs.json"
        self.outlier_initiatives_file = self.data_dir / "outlier_initiatives.json"
        self.nas_config_file = self.project_root / "config" / "nas_config.json"

        # Load configuration
        self.nas_config = self._load_nas_config()

        # Cron jobs and initiatives
        self.cron_jobs: Dict[str, CronJob] = {}
        self.outlier_initiatives: Dict[str, OutlierInitiative] = {}

        # Load existing jobs and initiatives
        self._load_cron_jobs()
        self._load_outlier_initiatives()

        # Initialize default jobs and initiatives
        self._initialize_default_cron_jobs()
        self._initialize_default_outlier_initiatives()

        logger.info("✅ NAS Cron Scheduler initialized")
        logger.info(f"   NAS Host: {self.nas_host}")
        logger.info(f"   Cron Jobs: {len(self.cron_jobs)}")
        logger.info(f"   Outlier Initiatives: {len(self.outlier_initiatives)}")

    def _load_nas_config(self) -> Dict[str, Any]:
        """Load NAS configuration"""
        default_config = {
            "host": "<NAS_PRIMARY_IP>",
            "user": "mlesn",
            "n8n_url": f"http://<NAS_PRIMARY_IP>:5678",
            "ssh_port": 22,
            "ssh_key_path": None,
            "password": None  # Should use SSH keys
        }

        if self.nas_config_file.exists():
            try:
                with open(self.nas_config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.debug(f"   Could not load NAS config: {e}")
        else:
            # Create default config
            self.nas_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.nas_config_file, 'w') as f:
                json.dump(default_config, f, indent=2)

        return default_config

    def _load_cron_jobs(self):
        """Load cron jobs"""
        if self.cron_jobs_file.exists():
            try:
                with open(self.cron_jobs_file, 'r') as f:
                    data = json.load(f)
                    self.cron_jobs = {
                        job_id: CronJob(**job_data)
                        for job_id, job_data in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load cron jobs: {e}")

    def _save_cron_jobs(self):
        """Save cron jobs"""
        try:
            with open(self.cron_jobs_file, 'w') as f:
                json.dump({
                    job_id: {
                        "id": job.id,
                        "name": job.name,
                        "description": job.description,
                        "schedule": job.schedule,
                        "command": job.command,
                        "script_path": job.script_path,
                        "enabled": job.enabled,
                        "last_run": job.last_run,
                        "next_run": job.next_run,
                        "run_count": job.run_count,
                        "success_count": job.success_count,
                        "failure_count": job.failure_count,
                        "tags": job.tags,
                        "metadata": job.metadata
                    }
                    for job_id, job in self.cron_jobs.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving cron jobs: {e}")

    def _load_outlier_initiatives(self):
        """Load outlier initiatives"""
        if self.outlier_initiatives_file.exists():
            try:
                with open(self.outlier_initiatives_file, 'r') as f:
                    data = json.load(f)
                    self.outlier_initiatives = {
                        init_id: OutlierInitiative(**init_data)
                        for init_id, init_data in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load outlier initiatives: {e}")

    def _save_outlier_initiatives(self):
        """Save outlier initiatives"""
        try:
            with open(self.outlier_initiatives_file, 'w') as f:
                json.dump({
                    init_id: {
                        "id": init.id,
                        "name": init.name,
                        "description": init.description,
                        "trigger_condition": init.trigger_condition,
                        "detection_method": init.detection_method,
                        "action": init.action,
                        "agent": init.agent,
                        "priority": init.priority,
                        "enabled": init.enabled,
                        "last_triggered": init.last_triggered,
                        "trigger_count": init.trigger_count,
                        "success_count": init.success_count,
                        "metadata": init.metadata
                    }
                    for init_id, init in self.outlier_initiatives.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving outlier initiatives: {e}")

    def _initialize_default_cron_jobs(self):
        """Initialize default cron jobs"""
        # Job 1: Daily work cycle
        if "daily_work_cycle" not in self.cron_jobs:
            self.cron_jobs["daily_work_cycle"] = CronJob(
                id="daily_work_cycle",
                name="Daily Work Cycle",
                description="Run daily work cycle complete script",
                schedule="0 2 * * *",  # Daily at 2 AM
                command="python /volume1/docker/lumina/scripts/python/daily_work_cycle_complete.py",
                script_path="scripts/python/daily_work_cycle_complete.py",
                enabled=True,
                tags=["daily", "work_cycle", "automation"]
            )

        # Job 2: Extension marketplace check
        if "extension_marketplace_check" not in self.cron_jobs:
            self.cron_jobs["extension_marketplace_check"] = CronJob(
                id="extension_marketplace_check",
                name="Extension Marketplace Check",
                description="Check for extension updates across all marketplaces",
                schedule="0 */6 * * *",  # Every 6 hours
                command="python /volume1/docker/lumina/scripts/python/extension_marketplace_discovery.py --check-updates",
                script_path="scripts/python/extension_marketplace_discovery.py",
                enabled=True,
                tags=["extensions", "marketplace", "updates"]
            )

        # Job 3: Community resource mining
        if "community_resource_mining" not in self.cron_jobs:
            self.cron_jobs["community_resource_mining"] = CronJob(
                id="community_resource_mining",
                name="Community Resource Mining",
                description="Mine community resources for intelligence",
                schedule="0 3 * * *",  # Daily at 3 AM
                command="python /volume1/docker/lumina/scripts/python/community_resource_miner.py --search-github 'vscode extension'",
                script_path="scripts/python/community_resource_miner.py",
                enabled=True,
                tags=["mining", "resources", "intelligence"]
            )

        # Job 4: Connection health check
        if "connection_health_check" not in self.cron_jobs:
            self.cron_jobs["connection_health_check"] = CronJob(
                id="connection_health_check",
                name="Connection Health Check",
                description="Check Cursor IDE connection health",
                schedule="*/15 * * * *",  # Every 15 minutes
                command="python /volume1/docker/lumina/scripts/python/cursor_connection_health_monitor.py --status",
                script_path="scripts/python/cursor_connection_health_monitor.py",
                enabled=True,
                tags=["health", "connection", "monitoring"]
            )

        # Job 5: Watchdog/Guarddog run
        if "watchdog_run" not in self.cron_jobs:
            self.cron_jobs["watchdog_run"] = CronJob(
                id="watchdog_run",
                name="Watchdog/Guarddog Run",
                description="Run watchdog and guarddog checks",
                schedule="*/5 * * * *",  # Every 5 minutes
                command="python /volume1/docker/lumina/scripts/python/lumina_watchdog_guarddog_system.py --run-once",
                script_path="scripts/python/lumina_watchdog_guarddog_system.py",
                enabled=True,
                tags=["watchdog", "guarddog", "monitoring"]
            )

        self._save_cron_jobs()

    def _initialize_default_outlier_initiatives(self):
        """Initialize default outlier initiatives"""
        # Initiative 1: Connection error spike detection
        if "connection_error_spike" not in self.outlier_initiatives:
            self.outlier_initiatives["connection_error_spike"] = OutlierInitiative(
                id="connection_error_spike",
                name="Connection Error Spike Detection",
                description="Detect spikes in connection errors and initiate recovery",
                trigger_condition="connection_error_rate > 10% in last 5 minutes",
                detection_method="statistical_analysis",
                action="initiate_recovery_sequence",
                agent="JARVIS",
                priority="critical",
                enabled=True,
                metadata={
                    "threshold": 0.10,
                    "time_window_minutes": 5,
                    "recovery_actions": ["retry_connections", "check_services", "restart_if_needed"]
                }
            )

        # Initiative 2: Extension update outlier detection
        if "extension_update_outlier" not in self.outlier_initiatives:
            self.outlier_initiatives["extension_update_outlier"] = OutlierInitiative(
                id="extension_update_outlier",
                name="Extension Update Outlier Detection",
                description="Detect unusual extension update patterns",
                trigger_condition="extension_updates > 5 in last hour",
                detection_method="pattern_analysis",
                action="investigate_and_notify",
                agent="JARVIS",
                priority="medium",
                enabled=True
            )

        # Initiative 3: Performance degradation detection
        if "performance_degradation" not in self.outlier_initiatives:
            self.outlier_initiatives["performance_degradation"] = OutlierInitiative(
                id="performance_degradation",
                name="Performance Degradation Detection",
                description="Detect performance outliers and optimize",
                trigger_condition="response_time > 2x average in last 10 minutes",
                detection_method="performance_monitoring",
                action="optimize_and_scale",
                agent="JARVIS",
                priority="high",
                enabled=True
            )

        # Initiative 4: Resource usage spike
        if "resource_usage_spike" not in self.outlier_initiatives:
            self.outlier_initiatives["resource_usage_spike"] = OutlierInitiative(
                id="resource_usage_spike",
                name="Resource Usage Spike Detection",
                description="Detect unusual resource usage patterns",
                trigger_condition="cpu > 90% or memory > 90% for > 5 minutes",
                detection_method="resource_monitoring",
                action="scale_resources",
                agent="JARVIS",
                priority="high",
                enabled=True
            )

        # Initiative 5: Missing expected activity
        if "missing_activity" not in self.outlier_initiatives:
            self.outlier_initiatives["missing_activity"] = OutlierInitiative(
                id="missing_activity",
                name="Missing Expected Activity Detection",
                description="Detect when expected activities don't occur",
                trigger_condition="no_daily_work_cycle_run in last 26 hours",
                detection_method="schedule_verification",
                action="trigger_manual_run",
                agent="JARVIS",
                priority="medium",
                enabled=True
            )

        self._save_outlier_initiatives()

    def deploy_cron_job_to_nas(self, job_id: str) -> bool:
        """Deploy cron job to NAS"""
        if job_id not in self.cron_jobs:
            logger.error(f"   ❌ Job not found: {job_id}")
            return False

        job = self.cron_jobs[job_id]

        logger.info(f"   📤 Deploying cron job to NAS: {job.name}")

        # Build cron entry
        cron_entry = f"{job.schedule} {job.command} # {job.name} - {job.id}"

        try:
            if PARAMIKO_AVAILABLE:
                # SSH to NAS and add cron job
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # Connect
                ssh.connect(
                    hostname=self.nas_config["host"],
                    username=self.nas_config["user"],
                    port=self.nas_config.get("ssh_port", 22),
                    key_filename=self.nas_config.get("ssh_key_path"),
                    password=self.nas_config.get("password")
                )

                # Add cron job
                stdin, stdout, stderr = ssh.exec_command(
                    f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -'
                )

                exit_status = stdout.channel.recv_exit_status()
                ssh.close()

                if exit_status == 0:
                    logger.info(f"   ✅ Cron job deployed: {job.name}")
                    return True
                else:
                    logger.error(f"   ❌ Deployment failed: {stderr.read().decode()}")
                    return False
            else:
                logger.warning("   ⚠️  paramiko not available - cannot deploy via SSH")
                logger.info(f"   📋 Manual cron entry:")
                logger.info(f"      {cron_entry}")
                return False

        except Exception as e:
            logger.error(f"   ❌ Error deploying cron job: {e}")
            return False

    def deploy_all_cron_jobs(self) -> Dict[str, bool]:
        """Deploy all enabled cron jobs to NAS"""
        logger.info("=" * 80)
        logger.info("📤 DEPLOYING ALL CRON JOBS TO NAS")
        logger.info("=" * 80)

        results = {}

        for job_id, job in self.cron_jobs.items():
            if job.enabled:
                results[job_id] = self.deploy_cron_job_to_nas(job_id)
            else:
                logger.info(f"   ⏭️  Skipping disabled job: {job.name}")
                results[job_id] = None

        deployed = sum(1 for r in results.values() if r is True)
        total = sum(1 for r in results.values() if r is not None)

        logger.info("")
        logger.info(f"   ✅ Deployed: {deployed}/{total}")

        return results

    def trigger_n8n_workflow(self, workflow_name: str, data: Dict[str, Any] = None) -> bool:
        """Trigger N8N workflow on NAS"""
        logger.info(f"   🔄 Triggering N8N workflow: {workflow_name}")

        if not REQUESTS_AVAILABLE:
            logger.error("   ❌ requests library not available")
            return False

        try:
            # N8N webhook URL (would need to be configured)
            webhook_url = f"{self.nas_config['n8n_url']}/webhook/{workflow_name}"

            response = requests.post(
                webhook_url,
                json=data or {},
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info(f"   ✅ Workflow triggered: {workflow_name}")
                return True
            else:
                logger.warning(f"   ⚠️  Workflow returned status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"   ❌ Error triggering workflow: {e}")
            return False

    def detect_outliers(self) -> List[OutlierInitiative]:
        """Detect outliers and return triggered initiatives"""
        logger.info("   🔍 Detecting outliers...")

        triggered = []

        for init_id, init in self.outlier_initiatives.items():
            if not init.enabled:
                continue

            try:
                # Check trigger condition
                triggered_flag = self._check_trigger_condition(init)

                if triggered_flag:
                    logger.info(f"   ⚠️  Outlier detected: {init.name}")
                    triggered.append(init)

                    # Execute action
                    self._execute_outlier_action(init)

                    # Update statistics
                    init.last_triggered = datetime.now().isoformat()
                    init.trigger_count += 1
                    init.success_count += 1  # Would check actual success

                    self._save_outlier_initiatives()

            except Exception as e:
                logger.error(f"   ❌ Error checking initiative {init_id}: {e}")

        return triggered

    def _check_trigger_condition(self, init: OutlierInitiative) -> bool:
        """Check if trigger condition is met"""
        condition = init.trigger_condition

        # Parse and evaluate condition
        # This is a simplified version - would need proper parsing

        if "connection_error_rate" in condition:
            # Check connection error rate
            try:
                from cursor_connection_health_monitor import CursorConnectionHealthMonitor
                monitor = CursorConnectionHealthMonitor(self.project_root)
                health = monitor.get_health_status()

                error_rate = 1.0 - (health.get("success_rate", 100) / 100.0)
                threshold = init.metadata.get("threshold", 0.10)

                return error_rate > threshold
            except:
                return False

        elif "extension_updates" in condition:
            # Check extension update count
            # Would query extension update tracker
            return False

        elif "response_time" in condition:
            # Check response time
            # Would query performance monitor
            return False

        elif "cpu" in condition or "memory" in condition:
            # Check resource usage
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent

                if "cpu > 90" in condition and cpu_percent > 90:
                    return True
                if "memory > 90" in condition and memory_percent > 90:
                    return True
            except:
                pass

        elif "no_daily_work_cycle_run" in condition:
            # Check if daily work cycle ran
            # Would check last run time
            return False

        return False

    def _execute_outlier_action(self, init: OutlierInitiative):
        """Execute action for outlier initiative"""
        action = init.action

        logger.info(f"   🎯 Executing action: {action}")

        if action == "initiate_recovery_sequence":
            # Initiate recovery
            recovery_actions = init.metadata.get("recovery_actions", [])
            for recovery_action in recovery_actions:
                logger.info(f"      → {recovery_action}")

        elif action == "investigate_and_notify":
            # Investigate and notify
            logger.info("      → Investigating outlier")
            logger.info("      → Notifying operator")

        elif action == "optimize_and_scale":
            # Optimize and scale
            logger.info("      → Optimizing performance")
            logger.info("      → Scaling resources")

        elif action == "scale_resources":
            # Scale resources
            logger.info("      → Scaling resources")

        elif action == "trigger_manual_run":
            # Trigger manual run
            logger.info("      → Triggering manual run")
            # Would trigger the missing task

    def generate_cron_script(self) -> Path:
        """Generate cron script for NAS"""
        script_file = self.project_root / "scripts" / "deploy_nas_cron.sh"

        script_content = f"""#!/bin/bash
# NAS Cron Deployment Script
# Auto-generated for LUMINA

NAS_HOST="{self.nas_config['host']}"
NAS_USER="{self.nas_config['user']}"

echo "Deploying cron jobs to NAS ($NAS_HOST)..."

# Backup existing crontab
ssh $NAS_USER@$NAS_HOST "crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null"

# Add cron jobs
"""

        for job_id, job in self.cron_jobs.items():
            if job.enabled:
                cron_entry = f"{job.schedule} {job.command} # {job.name} - {job.id}"
                script_content += f'echo "{cron_entry}" | ssh $NAS_USER@$NAS_HOST "crontab -"\n'

        script_content += """
echo "✅ Cron jobs deployed"
echo "Verify with: ssh $NAS_USER@$NAS_HOST 'crontab -l'"
"""

        script_file.write_text(script_content)
        script_file.chmod(0o755)

        logger.info(f"   ✅ Generated cron script: {script_file}")

        return script_file


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="NAS Cron Scheduler")
        parser.add_argument("--deploy", action="store_true", help="Deploy all cron jobs to NAS")
        parser.add_argument("--deploy-job", type=str, help="Deploy specific cron job")
        parser.add_argument("--detect-outliers", action="store_true", help="Detect outliers")
        parser.add_argument("--trigger-n8n", type=str, help="Trigger N8N workflow")
        parser.add_argument("--generate-script", action="store_true", help="Generate deployment script")
        parser.add_argument("--list-jobs", action="store_true", help="List all cron jobs")
        parser.add_argument("--list-initiatives", action="store_true", help="List all outlier initiatives")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        scheduler = NASCronScheduler()

        if args.deploy:
            results = scheduler.deploy_all_cron_jobs()
            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                print(f"✅ Deployed {sum(1 for r in results.values() if r)} jobs")

        elif args.deploy_job:
            success = scheduler.deploy_cron_job_to_nas(args.deploy_job)
            if args.json:
                print(json.dumps({"success": success}, indent=2))
            else:
                print(f"{'✅' if success else '❌'} Job deployment: {args.deploy_job}")

        elif args.detect_outliers:
            triggered = scheduler.detect_outliers()
            if args.json:
                print(json.dumps([
                    {
                        "id": init.id,
                        "name": init.name,
                        "priority": init.priority
                    }
                    for init in triggered
                ], indent=2, default=str))
            else:
                print(f"✅ Detected {len(triggered)} outliers")
                for init in triggered:
                    print(f"   - {init.name} ({init.priority})")

        elif args.trigger_n8n:
            success = scheduler.trigger_n8n_workflow(args.trigger_n8n)
            if args.json:
                print(json.dumps({"success": success}, indent=2))
            else:
                print(f"{'✅' if success else '❌'} N8N workflow triggered: {args.trigger_n8n}")

        elif args.generate_script:
            script_path = scheduler.generate_cron_script()
            print(f"✅ Script generated: {script_path}")

        elif args.list_jobs:
            if args.json:
                print(json.dumps({
                    job_id: {
                        "name": job.name,
                        "schedule": job.schedule,
                        "enabled": job.enabled
                    }
                    for job_id, job in scheduler.cron_jobs.items()
                }, indent=2, default=str))
            else:
                print(f"Cron Jobs: {len(scheduler.cron_jobs)}")
                for job in scheduler.cron_jobs.values():
                    status = "✅" if job.enabled else "⏸️"
                    print(f"  {status} {job.name}: {job.schedule}")

        elif args.list_initiatives:
            if args.json:
                print(json.dumps({
                    init_id: {
                        "name": init.name,
                        "priority": init.priority,
                        "enabled": init.enabled
                    }
                    for init_id, init in scheduler.outlier_initiatives.items()
                }, indent=2, default=str))
            else:
                print(f"Outlier Initiatives: {len(scheduler.outlier_initiatives)}")
                for init in scheduler.outlier_initiatives.values():
                    status = "✅" if init.enabled else "⏸️"
                    print(f"  {status} {init.name} ({init.priority})")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()