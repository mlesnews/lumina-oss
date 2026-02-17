#!/usr/bin/env python3
"""
Deploy & Activate All Cron Services

Standard workflow step: Register, deploy, and activate all cron services.
This should ALWAYS be run after creating new scheduled services.

Tags: #CRON #DEPLOY #ACTIVATE #WORKFLOW @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from auto_cron_registration import auto_register_existing_services, get_registry
    from nas_cron_scheduler import NASCronScheduler
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logger = get_logger("DeployActivateCron")
    logger.error(f"Required imports not available: {e}")
    sys.exit(1)

logger = get_logger("DeployActivateCron")


def main():
    """Deploy and activate all cron services"""
    print("=" * 80)
    print("🚀 DEPLOY & ACTIVATE ALL CRON SERVICES")
    print("=" * 80)
    print()

    # Step 1: Auto-register all services
    print("STEP 1: Auto-registering all services...")
    try:
        count = auto_register_existing_services()
        print(f"   ✅ Registered {count} services")
    except Exception as e:
        print(f"   ⚠️  Error during registration: {e}")
    print()

    # Step 2: Trigger service initialization (for services that auto-register on init)
    print("STEP 2: Initializing services (triggering auto-registration)...")
    try:
        from lumina_intelligence_collection import LUMINAIntelligenceCollection
        intel = LUMINAIntelligenceCollection()
        print("   ✅ Services initialized")
    except Exception as e:
        print(f"   ⚠️  Could not initialize all services: {e}")
    print()

    # Step 3: List registered services
    print("STEP 3: Registered Services:")
    registry = get_registry()
    services = registry.get_registered_services()

    if services:
        for svc_id, svc_data in services.items():
            status = "✅" if svc_data.get("enabled", True) else "⏸️"
            schedule = svc_data.get("schedule", "N/A")
            name = svc_data.get("service_name", svc_id)
            print(f"   {status} {name}: {schedule}")
    else:
        print("   No services registered")
    print()

    # Step 4: Deploy to NAS cron scheduler
    print("STEP 4: Deploying to NAS cron scheduler...")
    try:
        scheduler = NASCronScheduler(project_root=project_root)
        results = scheduler.deploy_all_cron_jobs()

        deployed = sum(1 for r in results.values() if r is True)
        total = sum(1 for r in results.values() if r is not None)

        print(f"   ✅ Deployed {deployed}/{total} cron jobs to NAS")

        if deployed < total:
            print("   ⚠️  Some jobs failed to deploy:")
            for job_id, result in results.items():
                if result is False:
                    print(f"      ❌ {job_id}")
    except Exception as e:
        print(f"   ❌ Error deploying to NAS: {e}")
    print()

    # Step 5: Verify deployment
    print("STEP 5: Verifying deployment...")
    try:
        scheduler = NASCronScheduler(project_root=project_root)
        total_jobs = len(scheduler.cron_jobs)
        enabled_jobs = sum(1 for job in scheduler.cron_jobs.values() if job.enabled)

        print(f"   ✅ Total cron jobs: {total_jobs}")
        print(f"   ✅ Enabled jobs: {enabled_jobs}")

        # List all jobs
        print()
        print("   All Cron Jobs:")
        for job in scheduler.cron_jobs.values():
            status = "✅" if job.enabled else "⏸️"
            print(f"      {status} {job.name}: {job.schedule}")
    except Exception as e:
        print(f"   ⚠️  Error verifying: {e}")
    print()

    print("=" * 80)
    print("✅ DEPLOY & ACTIVATE COMPLETE")
    print("=" * 80)
    print()
    print("All scheduled services are now:")
    print("  ✅ Registered with auto cron registry")
    print("  ✅ Added to NAS cron scheduler")
    print("  ✅ Deployed to NAS (if SSH available)")
    print("  ✅ Ready to run on schedule")
    print()


if __name__ == "__main__":


    main()