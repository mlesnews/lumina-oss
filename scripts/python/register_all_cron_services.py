#!/usr/bin/env python3
"""
Register All Cron Services

Automatically registers all services that need cron scheduling.
Run this after creating new services to ensure they're scheduled.

Tags: #CRON #REGISTRATION #AUTOMATION @JARVIS @LUMINA
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
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logger = get_logger("RegisterAllCronServices")
    logger.error(f"Required imports not available: {e}")
    sys.exit(1)

logger = get_logger("RegisterAllCronServices")


def main():
    """Register all services with cron"""
    print("=" * 80)
    print("🚀 REGISTERING ALL CRON SERVICES")
    print("=" * 80)
    print()

    # Auto-register existing services
    print("1. Auto-registering existing services...")
    count = auto_register_existing_services()
    print(f"   ✅ Registered {count} services")
    print()

    # Also trigger registration by importing services
    print("2. Triggering service initialization (auto-registration)...")
    try:
        # Import services that auto-register on init
        from lumina_intelligence_collection import LUMINAIntelligenceCollection

        # Initialize to trigger auto-registration
        intel = LUMINAIntelligenceCollection()
        print("   ✅ LUMINA Intelligence Collection initialized (auto-registered)")
    except Exception as e:
        print(f"   ⚠️  Could not initialize services: {e}")

    print()

    # List all registered services
    print("3. Registered Services:")
    registry = get_registry()
    services = registry.get_registered_services()

    if services:
        for svc_id, svc_data in services.items():
            status = "✅" if svc_data.get("enabled", True) else "⏸️"
            schedule = svc_data.get("schedule", "N/A")
            name = svc_data.get("service_name", svc_id)
            print(f"   {status} {name}")
            print(f"      Schedule: {schedule}")
            print(f"      ID: {svc_id}")
            print()
    else:
        print("   No services registered yet")

    print("=" * 80)
    print("✅ REGISTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review registered services above")
    print("  2. Deploy to NAS:")
    print("     python scripts/python/auto_cron_registration.py --deploy")
    print("  3. Or use NAS scheduler:")
    print("     python scripts/python/nas_cron_scheduler.py --deploy")
    print()


if __name__ == "__main__":


    main()