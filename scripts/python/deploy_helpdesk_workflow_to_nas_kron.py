#!/usr/bin/env python3
"""
Deploy Helpdesk Workflow to NAS KronScheduler
Deploys the helpdesk workflow resume job to NAS for automated scheduling.

Tags: #JARVIS #HELPDESK #NAS #KRONSCHEDULER #DEPLOY @helpdesk @c3po @r2d2
"""

import json
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DeployHelpdeskWorkflowToNAS")


def deploy_to_nas_kron():
    try:
        """Deploy helpdesk workflow to NAS KronScheduler"""

        project_root = Path(__file__).parent.parent.parent
        job_config_file = project_root / "data" / "nas_kronscheduler" / "helpdesk_workflow_resume_job.json"
        registry_file = project_root / "data" / "nas_kronscheduler" / "all_jobs_registry.json"

        logger.info("="*80)
        logger.info("🚀 DEPLOYING HELPDESK WORKFLOW TO NAS KRONSCHEDULER")
        logger.info("="*80)
        logger.info("")

        # Verify job config exists
        if not job_config_file.exists():
            logger.error(f"❌ Job config not found: {job_config_file}")
            return False

        # Load job config
        with open(job_config_file, 'r', encoding='utf-8') as f:
            job_config = json.load(f)

        logger.info(f"✅ Job config loaded: {job_config['job_name']}")
        logger.info(f"   Script: {job_config['script']}")
        logger.info(f"   Schedule: {job_config['schedule']['interval_hours']} hours (dynamic: {job_config['schedule']['min_interval_hours']}-{job_config['schedule']['max_interval_hours']}h)")
        logger.info("")

        # Update registry
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
        job_id = "jarvis-helpdesk-workflow-resume"
        existing_job = next((j for j in registry['jobs'] if j['job_id'] == job_id), None)

        if existing_job:
            logger.info(f"⚠️  Job already registered: {job_id}")
            logger.info("   Updating registration...")
            existing_job.update({
                "config_file": "helpdesk_workflow_resume_job.json",
                "description": job_config['description'],
                "frequency": f"{job_config['schedule']['min_interval_hours']*60} minutes to {job_config['schedule']['max_interval_hours']} hours (dynamic)",
                "enabled": job_config['enabled'],
                "last_updated": datetime.now().isoformat()
            })
        else:
            logger.info(f"📝 Registering new job: {job_id}")
            registry['jobs'].append({
                "job_id": job_id,
                "config_file": "helpdesk_workflow_resume_job.json",
                "description": job_config['description'],
                "frequency": f"{job_config['schedule']['min_interval_hours']*60} minutes to {job_config['schedule']['max_interval_hours']} hours (dynamic)",
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
        logger.info("="*80)
        logger.info("📋 DEPLOYMENT SUMMARY")
        logger.info("="*80)
        logger.info("")
        logger.info(f"✅ Job: {job_config['job_name']}")
        logger.info(f"✅ Config: {job_config_file.name}")
        logger.info(f"✅ Registered: {job_id}")
        logger.info(f"✅ Enabled: {job_config['enabled']}")
        logger.info(f"✅ Schedule: Every {job_config['schedule']['interval_hours']*60} minutes (dynamic: {job_config['schedule']['min_interval_hours']*60}-{job_config['schedule']['max_interval_hours']*60} minutes)")
        logger.info("")
        logger.info("🎯 Resume Activities:")
        for activity in job_config['resume_activities']:
            logger.info(f"   - {activity}")
        logger.info("")
        logger.info("📊 Success Metrics:")
        for metric, enabled in job_config['success_metrics'].items():
            if enabled:
                logger.info(f"   - {metric}")
        logger.info("")
        logger.info("="*80)
        logger.info("✅ DEPLOYMENT COMPLETE")
        logger.info("="*80)
        logger.info("")
        logger.info("The helpdesk workflow will now resume activities automatically via NAS KronScheduler.")
        logger.info("Queue numbers should decrease as tickets are processed and problems are resolved.")
        logger.info("")

        return True


    except Exception as e:
        logger.error(f"Error in deploy_to_nas_kron: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    success = deploy_to_nas_kron()
    sys.exit(0 if success else 1)
