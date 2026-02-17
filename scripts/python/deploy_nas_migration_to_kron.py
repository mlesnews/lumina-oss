#!/usr/bin/env python3
"""
Deploy NAS Migration to NAS KronScheduler
Deploys the NAS migration script to run automatically on the NAS.

Tags: #NAS #MIGRATION #KRONSCHEDULER #DEPLOY #AUTOMATION @DOIT
"""

import json
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("DeployNASMigrationToKron")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DeployNASMigrationToKron")


def create_migration_job_config():
    try:
        """Create NAS migration job configuration for KronScheduler"""

        data_dir = project_root / "data" / "nas_kronscheduler"
        data_dir.mkdir(parents=True, exist_ok=True)

        job_config = {
            "job_name": "LUMINA-NAS-Migration-Ollama",
            "job_id": "nas-migration-ollama",
            "description": "LUMINA: Automatic NAS Migration for Ollama Models - SMB Optimized",
            "script": str(project_root / "scripts" / "python" / "real_deal_migration_v3.py"),
            "script_type": "python",
            "args": [],
            "schedule": {
                "type": "cron",
                "cron_expression": "0 2 * * *",  # Daily at 2 AM
                "timezone": "America/New_York",
                "enabled": True
            },
            "conditions": {
                "check_source_exists": True,
                "check_destination_accessible": True,
                "check_ollama_stopped": True,
                "min_source_size_gb": 1.0  # Only run if source has at least 1GB
            },
            "notifications": {
                "on_start": True,
                "on_complete": True,
                "on_failure": True
            },
            "tags": [
                "#NAS",
                "#MIGRATION",
                "#OLLAMA",
                "#AUTOMATION",
                "@DOIT",
                "#SMB_OPTIMIZED"
            ],
            "enabled": True,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        # Save job config
        config_file = data_dir / "nas_migration_ollama_job.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(job_config, f, indent=2, ensure_ascii=False)

        logger.info("✅ NAS Migration job configuration created")
        logger.info(f"   Job: {job_config['job_name']}")
        logger.info(f"   Schedule: Daily at 2 AM")
        logger.info(f"   Config saved: {config_file.name}")

        return job_config, config_file


    except Exception as e:
        logger.error(f"Error in create_migration_job_config: {e}", exc_info=True)
        raise
def deploy_to_nas_kron():
    try:
        """Deploy NAS migration job to NAS KronScheduler registry"""

        logger.info("=" * 80)
        logger.info("🚀 DEPLOYING NAS MIGRATION TO NAS KRONSCHEDULER")
        logger.info("=" * 80)
        logger.info("")

        # Create job config
        job_config, config_file = create_migration_job_config()

        # Update registry
        data_dir = project_root / "data" / "nas_kronscheduler"
        registry_file = data_dir / "all_jobs_registry.json"

        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        else:
            registry = {
                "registry_version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "jobs": []
            }

        # Check if job already registered
        job_id = job_config["job_id"]
        existing_job = next((j for j in registry['jobs'] if j['job_id'] == job_id), None)

        if existing_job:
            logger.info(f"⚠️  Job already registered: {job_id}")
            logger.info("   Updating registration...")
            existing_job.update({
                "config_file": config_file.name,
                "description": job_config['description'],
                "frequency": "Daily at 2 AM",
                "enabled": job_config['enabled'],
                "last_updated": datetime.now().isoformat()
            })
        else:
            logger.info(f"📝 Registering new job: {job_id}")
            registry['jobs'].append({
                "job_id": job_id,
                "config_file": config_file.name,
                "description": job_config['description'],
                "frequency": "Daily at 2 AM",
                "enabled": job_config['enabled'],
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            })

        registry['last_updated'] = datetime.now().isoformat()

        # Save updated registry
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        logger.info("")
        logger.info("✅ Registry updated")
        logger.info("")
        logger.info("=" * 80)
        logger.info("📋 DEPLOYMENT SUMMARY")
        logger.info("=" * 80)
        logger.info("")
        logger.info("✅ Job Configuration:")
        logger.info(f"   Name: {job_config['job_name']}")
        logger.info(f"   ID: {job_id}")
        logger.info(f"   Script: {job_config['script']}")
        logger.info(f"   Schedule: {job_config['schedule']['cron_expression']} (Daily at 2 AM)")
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("   1. Copy job config to NAS KronScheduler directory")
        logger.info(f"   2. Config file: {config_file}")
        logger.info("   3. Ensure NAS can access the script path")
        logger.info("   4. Verify NAS has Python 3.x installed")
        logger.info("   5. Test job execution manually first")
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ DEPLOYMENT COMPLETE")
        logger.info("=" * 80)
        logger.info("")

        return True


    except Exception as e:
        logger.error(f"Error in deploy_to_nas_kron: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    try:
        deploy_to_nas_kron()
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)
