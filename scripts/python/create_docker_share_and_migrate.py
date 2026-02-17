#!/usr/bin/env python3
"""
Create Docker Share and Migrate - One-Step Docker Volume Migration

Checks if data/docker share exists, provides instructions if not,
then runs migration with --auto-stop when ready.

Tags: #NAS_MIGRATION #DOCKER #AUTO @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("CreateDockerShareAndMigrate")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CreateDockerShareAndMigrate")

NAS_IP = "<NAS_PRIMARY_IP>"
DATA_SHARE = f"\\\\{NAS_IP}\\data"
DOCKER_SHARE = f"\\\\{NAS_IP}\\data\\docker"


def check_share_exists(share_path: str) -> bool:
    """Check if a network share exists"""
    try:
        return Path(share_path).exists()
    except Exception:
        return False


def create_share_via_dsm_instructions():
    """Provide instructions for creating share via DSM GUI"""
    print("=" * 80)
    print("📁 CREATE DATA/DOCKER SHARE ON NAS")
    print("=" * 80)
    print()
    print("The data/docker share needs to be created on the Synology NAS.")
    print()
    print("METHOD 1: DSM Web Interface (Recommended)")
    print("-" * 80)
    print("1. Open browser and go to: https://<NAS_PRIMARY_IP>:5001")
    print("2. Log in with your NAS credentials")
    print("3. Go to: Control Panel > Shared Folder")
    print("4. Click 'Create' button")
    print("5. Fill in the following:")
    print("   - Name: data")
    print("   - Location: /volume1/data")
    print("   - Description: Data storage for Docker, models, media, etc.")
    print("6. Set permissions:")
    print("   - User 'mlesn': Read/Write")
    print("7. Click 'OK' to create")
    print()
    print("8. After 'data' share is created, create subfolder:")
    print("   - In File Station, navigate to /volume1/data")
    print("   - Create new folder: 'docker'")
    print("   - Or use SSH: mkdir -p /volume1/data/docker")
    print()
    print("METHOD 2: SSH Command (If SSH access available)")
    print("-" * 80)
    print("SSH into NAS and run:")
    print("  ssh mlesn@<NAS_PRIMARY_IP>")
    print("  sudo mkdir -p /volume1/data/docker")
    print("  sudo chown mlesn:users /volume1/data/docker")
    print("  sudo chmod 755 /volume1/data/docker")
    print()
    print("Then create the 'data' shared folder via DSM GUI:")
    print("  Control Panel > Shared Folder > Create")
    print("  Name: data, Path: /volume1/data")
    print()
    print("=" * 80)
    print()


def main():
    """Main execution"""
    import argparse
    parser = argparse.ArgumentParser(
        description="Create Docker share and migrate volumes"
    )
    parser.add_argument(
        "--auto-stop",
        action="store_true",
        help="Automatically stop Docker Desktop before migration"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check if share exists, don't migrate"
    )
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("🐳 DOCKER VOLUME MIGRATION - SHARE CHECK")
    logger.info("=" * 80)
    logger.info("")

    # Check if data share exists
    logger.info("📋 Checking NAS shares...")
    data_exists = check_share_exists(DATA_SHARE)
    docker_exists = check_share_exists(DOCKER_SHARE)

    logger.info(f"   Data share (\\<NAS_PRIMARY_IP>\\data): {'✅ EXISTS' if data_exists else '❌ NOT FOUND'}")
    logger.info(f"   Docker share (\\<NAS_PRIMARY_IP>\\data\\docker): {'✅ EXISTS' if docker_exists else '❌ NOT FOUND'}")
    logger.info("")

    if not data_exists or not docker_exists:
        logger.warning("⚠️  Required shares are missing!")
        logger.info("")
        create_share_via_dsm_instructions()

        if args.check_only:
            logger.info("✅ Check complete. Create shares and run again without --check-only")
            return

        # Ask user if they want to continue anyway
        logger.info("")
        logger.info("After creating the shares, run this script again to start migration.")
        logger.info("Or run: python nas_migration_auto_docker.py --auto-stop")
        return

    # Shares exist, proceed with migration
    logger.info("✅ All required shares exist!")
    logger.info("")
    logger.info("🚀 Starting Docker volume migration...")
    logger.info("")

    # Import and run the migration script
    try:
        from nas_migration_auto_docker import DockerAutoMigrator

        migrator = DockerAutoMigrator(project_root)
        result = migrator.migrate_docker_volumes_auto(auto_stop=args.auto_stop)

        print("\n" + "=" * 80)
        print("🐳 DOCKER MIGRATION RESULT")
        print("=" * 80)
        print()
        print(f"Status: {result['status']}")
        print(f"Steps completed: {len(result['steps_completed'])}")
        if result.get("errors"):
            print(f"Errors: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"  - {error}")
        print()

    except ImportError as e:
        logger.error(f"❌ Could not import migration script: {e}")
        logger.info("   Run directly: python nas_migration_auto_docker.py --auto-stop")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")


if __name__ == "__main__":


    main()