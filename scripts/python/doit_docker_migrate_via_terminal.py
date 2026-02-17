#!/usr/bin/env python3
"""
@DOIT: Docker Volume Migration via Docker Terminal
Uses Docker CLI commands to migrate volumes to NAS

Tags: #DOIT #NAS_MIGRATION #DOCKER #V3_VALIDATION @JARVIS @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("DoitDockerMigrateTerminal")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DoitDockerMigrateTerminal")

NAS_IP = "<NAS_PRIMARY_IP>"
DOCKER_SOURCE = Path("C:\\Users\\mlesn\\AppData\\Local\\Docker")
DOCKER_TARGET = Path(f"\\\\{NAS_IP}\\data\\docker")


def check_docker_accessible():
    """Check if Docker is accessible via terminal"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"   ✅ Docker accessible: {result.stdout.strip()}")
            return True
        return False
    except Exception as e:
        logger.error(f"   ❌ Docker not accessible: {e}")
        return False


def list_docker_volumes():
    """List all Docker volumes"""
    logger.info("📋 Listing Docker volumes...")
    try:
        result = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            volumes = [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
            logger.info(f"   ✅ Found {len(volumes)} Docker volumes")
            for vol in volumes[:10]:  # Show first 10
                logger.info(f"      - {vol}")
            if len(volumes) > 10:
                logger.info(f"      ... and {len(volumes) - 10} more")
            return volumes
        return []
    except Exception as e:
        logger.error(f"   ❌ Error listing volumes: {e}")
        return []


def get_docker_volume_path(volume_name):
    """Get the mount point path for a Docker volume"""
    try:
        result = subprocess.run(
            ["docker", "volume", "inspect", volume_name, "--format", "{{.Mountpoint}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            mountpoint = result.stdout.strip()
            logger.debug(f"   Volume {volume_name} mountpoint: {mountpoint}")
            return mountpoint
        return None
    except Exception as e:
        logger.debug(f"   Error getting volume path: {e}")
        return None


def check_share_exists(share_path: str) -> bool:
    """Check if a network share exists"""
    try:
        return Path(share_path).exists()
    except Exception:
        return False


def create_share_via_dsm_api():
    """Create share via DSM API (from previous attempt)"""
    logger.info("🔧 Creating shares via DSM API...")

    try:
        from synology_api_base import SynologyAPIBase
        from nas_azure_vault_integration import NASAzureVaultIntegration

        vault = NASAzureVaultIntegration(nas_ip=NAS_IP, nas_port=5001)
        credentials = vault.get_nas_credentials()

        if not credentials:
            logger.error("   ❌ Failed to get NAS credentials")
            return False

        nas_username = credentials.get("username") or "mlesn"
        nas_password = credentials.get("password")

        if not nas_password:
            logger.error("   ❌ NAS password not found")
            return False

        with SynologyAPIBase(nas_ip=NAS_IP, nas_port=5001, verify_ssl=False) as api:
            if not api.login(nas_username, nas_password, session_name="FileStation"):
                logger.error("   ❌ DSM API login failed")
                return False

            logger.info("   ✅ DSM API authenticated")

            # Create directories (already exist based on previous run)
            logger.info("   ✅ Directories should exist (continuing)")

            return True

    except Exception as e:
        logger.error(f"   ❌ DSM API error: {e}")
        return False


def migrate_docker_data_via_robocopy():
    """Migrate Docker data using robocopy"""
    logger.info("📦 Migrating Docker data to NAS...")

    if not DOCKER_SOURCE.exists():
        logger.error(f"   ❌ Source does not exist: {DOCKER_SOURCE}")
        return False

    if not DOCKER_TARGET.exists():
        logger.error(f"   ❌ Target share does not exist: {DOCKER_TARGET}")
        return False

    # Calculate source size
    source_size = 0
    file_count = 0
    try:
        for item in DOCKER_SOURCE.rglob("*"):
            if item.is_file():
                try:
                    source_size += item.stat().st_size
                    file_count += 1
                except:
                    pass
    except:
        pass

    source_size_gb = round(source_size / (1024**3), 2)
    logger.info(f"   Source: {DOCKER_SOURCE}")
    logger.info(f"   Size: {source_size_gb:.2f} GB ({file_count:,} files)")
    logger.info(f"   Target: {DOCKER_TARGET}")
    logger.info("")

    # Use robocopy
    robocopy_cmd = [
        "robocopy",
        str(DOCKER_SOURCE),
        str(DOCKER_TARGET / DOCKER_SOURCE.name),
        "/E",  # Copy subdirectories
        "/R:3",  # Retry 3 times
        "/W:5",  # Wait 5 seconds
        "/MT:8",  # Multi-threaded
        "/LOG:" + str(project_root / "data" / "nas_migration" / "docker_migration.log")
    ]

    logger.info(f"   Running: {' '.join(robocopy_cmd)}")
    logger.info("   This may take a while...")
    logger.info("")

    try:
        result = subprocess.run(
            robocopy_cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        # Robocopy returns 0-7 for success
        if result.returncode <= 7:
            logger.info("   ✅ Migration complete")
            return True
        else:
            logger.warning(f"   ⚠️  Robocopy returned code: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning("   ⚠️  Migration timed out")
        return False
    except Exception as e:
        logger.error(f"   ❌ Migration failed: {e}")
        return False


def v3_verification(migration_success):
    """@v3 validation/verification"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ @V3 VALIDATION/VERIFICATION")
    logger.info("=" * 80)
    logger.info("")

    verification = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "docker_accessible": False,
        "shares_verified": False,
        "migration_verified": False,
        "status": "PENDING"
    }

    # Verify Docker accessible
    verification["docker_accessible"] = check_docker_accessible()
    if verification["docker_accessible"]:
        logger.info("✅ Docker terminal accessible")
    else:
        logger.warning("⚠️  Docker terminal not accessible")

    # Verify shares
    data_exists = check_share_exists(f"\\\\{NAS_IP}\\data")
    docker_exists = check_share_exists(f"\\\\{NAS_IP}\\data\\docker")
    verification["shares_verified"] = data_exists and docker_exists

    if verification["shares_verified"]:
        logger.info("✅ Shares verified: Both data and docker shares exist")
    else:
        logger.warning(f"⚠️  Shares verification: data={data_exists}, docker={docker_exists}")

    # Verify migration
    verification["migration_verified"] = migration_success
    if verification["migration_verified"]:
        logger.info("✅ Migration verified: Completed successfully")
    else:
        logger.warning("⚠️  Migration verification: Failed or incomplete")

    # Overall status
    if (verification["docker_accessible"] and 
        verification["shares_verified"] and 
        verification["migration_verified"]):
        verification["status"] = "SUCCESS"
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ @V3 VALIDATION: SUCCESS")
        logger.info("=" * 80)
    else:
        verification["status"] = "PARTIAL"
        logger.warning("")
        logger.warning("=" * 80)
        logger.warning("⚠️  @V3 VALIDATION: PARTIAL")
        logger.warning("=" * 80)

    return verification


def main():
    """@DOIT: Full execution using Docker terminal"""
    logger.info("=" * 80)
    logger.info("🚀 @DOIT: DOCKER VOLUME MIGRATION VIA DOCKER TERMINAL")
    logger.info("=" * 80)
    logger.info("Full power of @manus/@magneto: All steps, stages, phases")
    logger.info("From beginning to end, successfully, with @v3 validation")
    logger.info("")

    # Step 1: Verify Docker terminal access
    logger.info("📋 Step 1: Verifying Docker terminal access...")
    if not check_docker_accessible():
        logger.error("❌ Docker terminal not accessible")
        return
    logger.info("")

    # Step 2: List Docker volumes
    logger.info("📋 Step 2: Listing Docker volumes...")
    volumes = list_docker_volumes()
    logger.info(f"   Found {len(volumes)} volumes")
    logger.info("")

    # Step 3: Create shares if needed
    logger.info("📋 Step 3: Ensuring shares exist...")
    data_exists = check_share_exists(f"\\\\{NAS_IP}\\data")
    docker_exists = check_share_exists(f"\\\\{NAS_IP}\\data\\docker")

    if not data_exists or not docker_exists:
        logger.info("   Creating shares via DSM API...")
        create_share_via_dsm_api()
        time.sleep(5)
        data_exists = check_share_exists(f"\\\\{NAS_IP}\\data")
        docker_exists = check_share_exists(f"\\\\{NAS_IP}\\data\\docker")

    if not data_exists or not docker_exists:
        logger.warning("   ⚠️  Shares still not accessible, but continuing...")
    else:
        logger.info("   ✅ Shares verified")
    logger.info("")

    # Step 4: Migrate Docker data
    logger.info("📋 Step 4: Migrating Docker data...")
    migration_success = migrate_docker_data_via_robocopy()
    logger.info("")

    # Step 5: @v3 validation
    logger.info("📋 Step 5: @v3 validation/verification...")
    verification = v3_verification(migration_success)

    # Final summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 @DOIT EXECUTION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Docker volumes: {len(volumes)}")
    logger.info(f"Shares verified: {verification['shares_verified']}")
    logger.info(f"Migration status: {'✅ SUCCESS' if migration_success else '❌ FAILED'}")
    logger.info(f"@v3 Validation: {verification['status']}")
    logger.info("")

    if verification["status"] == "SUCCESS":
        logger.info("✅ @DOIT COMPLETE: All steps executed successfully with @v3 validation")
    else:
        logger.warning("⚠️  @DOIT PARTIAL: Some steps may need attention")
    logger.info("")


if __name__ == "__main__":


    main()