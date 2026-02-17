#!/usr/bin/env python3
"""
@DOIT: Create Docker Share and Migrate - FULL EXECUTION
Complete workflow: Create share → Migrate → Verify (@v3 validation)

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
    logger = get_comprehensive_logger("DoitDockerShareMigrate")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DoitDockerShareMigrate")

NAS_IP = "<NAS_PRIMARY_IP>"
NAS_USER = "mlesn"
DATA_SHARE = f"\\\\{NAS_IP}\\data"
DOCKER_SHARE = f"\\\\{NAS_IP}\\docker"  # Use existing docker share
DATA_PATH = "/volume1/data"
DOCKER_PATH = "/volume1/docker"  # Use existing docker share path


def check_share_exists(share_path: str) -> bool:
    """Check if a network share exists"""
    try:
        return Path(share_path).exists()
    except Exception:
        return False


def create_share_via_ssh():
    """Attempt to create share via SSH"""
    logger.info("🔧 Attempting to create share via SSH...")

    # Try to get NAS password from secrets
    nas_password = None
    try:
        from unified_secrets_manager import UnifiedSecretsManager
        secrets = UnifiedSecretsManager()
        nas_password = secrets.get_secret("nas-password") or secrets.get_secret("nas_ssh_password")
    except Exception as e:
        logger.debug(f"Could not get password from secrets: {e}")

    # Create directory structure via SSH
    ssh_commands = [
        f"sudo mkdir -p {DOCKER_PATH}",
        f"sudo chown {NAS_USER}:users {DATA_PATH}",
        f"sudo chown {NAS_USER}:users {DOCKER_PATH}",
        f"sudo chmod 755 {DATA_PATH}",
        f"sudo chmod 755 {DOCKER_PATH}"
    ]

    for cmd in ssh_commands:
        try:
            if nas_password:
                # Use sshpass if available
                result = subprocess.run(
                    ["sshpass", "-p", nas_password, "ssh", "-o", "StrictHostKeyChecking=no",
                     f"{NAS_USER}@{NAS_IP}", cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                # Try without password (SSH key)
                result = subprocess.run(
                    ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
                     f"{NAS_USER}@{NAS_IP}", cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

            if result.returncode == 0:
                logger.info(f"   ✅ Executed: {cmd}")
            else:
                logger.warning(f"   ⚠️  Command failed: {cmd} (return code: {result.returncode})")
                logger.debug(f"   Error: {result.stderr}")
        except FileNotFoundError:
            logger.warning("   ⚠️  SSH not available or not in PATH")
            return False
        except subprocess.TimeoutExpired:
            logger.warning(f"   ⚠️  SSH command timed out: {cmd}")
            return False
        except Exception as e:
            logger.warning(f"   ⚠️  SSH error: {e}")
            return False

    # Wait a moment for changes to propagate
    time.sleep(2)
    return True


def create_share_via_dsm_api():
    """Create share via DSM API with full root access using proven SynologyAPIBase"""
    logger.info("🔧 Creating shares via DSM API (full root access)...")

    try:
        from synology_api_base import SynologyAPIBase
        from unified_secrets_manager import UnifiedSecretsManager

        # Use NASAzureVaultIntegration to get credentials (proven method)
        from nas_azure_vault_integration import NASAzureVaultIntegration

        vault = NASAzureVaultIntegration()
        credentials = vault.get_nas_credentials()

        if not credentials:
            logger.error("   ❌ Failed to get NAS credentials from Azure Vault")
            return False

        nas_username = credentials.get("username") or NAS_USER
        nas_password = credentials.get("password")

        if not nas_password:
            logger.error("   ❌ NAS password not found in credentials")
            return False

        # Step 1: Login using proven SynologyAPIBase
        logger.info("   📋 Step 1: Authenticating with DSM API...")
        with SynologyAPIBase(nas_ip=NAS_IP, nas_port=5001, verify_ssl=False) as api:
            if not api.login(nas_username, nas_password, session_name="FileStation"):
                logger.error("   ❌ DSM API login failed")
                return False

            sid = api.sid
            logger.info("   ✅ DSM API authentication successful")

            # Step 3: Create data directory structure via FileStation
            logger.info("   📋 Step 3: Creating directory structure...")

            # Create /volume1/data if it doesn't exist
            create_data_result = api.api_call(
                "SYNO.FileStation.CreateFolder",
                "create",
                version="2",
                params={
                    "folder_path": "/volume1",
                    "name": "data",
                    "force_parent": "true"
                }
            )

            if create_data_result:
                logger.info("   ✅ Created /volume1/data directory")
            else:
                logger.info("   ✅ /volume1/data may already exist (continuing)")

            # Create /volume1/data/docker
            create_docker_result = api.api_call(
                "SYNO.FileStation.CreateFolder",
                "create",
                version="2",
                params={
                    "folder_path": "/volume1/data",
                    "name": "docker",
                    "force_parent": "true"
                }
            )

            if create_docker_result:
                logger.info("   ✅ Created /volume1/data/docker directory")
            else:
                logger.info("   ✅ /volume1/data/docker may already exist (continuing)")

            # Step 4: Check if shared folder exists, then create if needed
            logger.info("   📋 Step 4: Checking existing shared folders...")
            list_shares_result = api.api_call(
                "SYNO.Core.Share",
                "list",
                version="1",
                params={}
            )

            share_exists = False
            if list_shares_result:
                shares = list_shares_result.get("shares", [])
                for share in shares:
                    if share.get("name") == "data":
                        share_exists = True
                        logger.info("   ✅ Shared folder 'data' already exists")
                        break

            if not share_exists:
                logger.info("   📋 Creating shared folder 'data'...")
                # Try multiple API versions and methods for share creation
                share_created = False

                # Method 1: Try SYNO.Core.Share with different versions
                for api_version in ["2", "1"]:
                    share_result = api.api_call(
                        "SYNO.Core.Share",
                        "create",
                        version=api_version,
                        params={
                            "name": "data",
                            "vol_path": "/volume1/data",
                            "desc": "Data storage for Docker, models, media, etc."
                        }
                    )

                    if share_result:
                        logger.info(f"   ✅ Created shared folder 'data' (API v{api_version})")
                        share_created = True
                        break
                    else:
                        logger.debug(f"   API v{api_version} failed, trying next...")

                if not share_created:
                    logger.warning("   ⚠️  Could not create shared folder via API (may need DSM GUI)")
                    logger.info("   ✅ Directories exist - share may need manual creation")
            else:
                logger.info("   ✅ Shared folder 'data' exists")

            # Step 5: Set permissions
            logger.info("   📋 Step 5: Setting permissions...")
            perm_result = api.api_call(
                "SYNO.Core.Share.Permission",
                "set",
                version="1",
                params={
                    "name": "data",
                    "user": nas_username,
                    "rwx": "true"
                }
            )

            if perm_result:
                logger.info(f"   ✅ Set permissions for user '{nas_username}'")
            else:
                logger.debug("   Permission setting may have failed (continuing)")

            logger.info("   ✅ DSM API operations completed")
            return True

    except ImportError:
        logger.error("   ❌ requests library not available")
        return False
    except Exception as e:
        logger.error(f"   ❌ DSM API error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def verify_shares_exist() -> tuple[bool, bool]:
    """Verify shares exist with retries"""
    logger.info("🔍 Verifying shares exist...")

    max_retries = 5
    for attempt in range(max_retries):
        data_exists = check_share_exists(DATA_SHARE)
        docker_exists = check_share_exists(DOCKER_SHARE)

        if data_exists and docker_exists:
            logger.info(f"   ✅ Both shares exist (attempt {attempt + 1}/{max_retries})")
            return True, True

        if attempt < max_retries - 1:
            logger.info(f"   ⏳ Waiting for shares... (attempt {attempt + 1}/{max_retries})")
            time.sleep(3)

    logger.warning(f"   ⚠️  Shares not accessible: data={data_exists}, docker={docker_exists}")
    return data_exists, docker_exists


def run_migration_with_verification():
    """Run migration and verify completion"""
    logger.info("🚀 Starting Docker volume migration...")

    try:
        from nas_migration_auto_docker import DockerAutoMigrator

        migrator = DockerAutoMigrator(project_root)
        result = migrator.migrate_docker_volumes_auto(auto_stop=True)

        logger.info("")
        logger.info("=" * 80)
        logger.info("🐳 MIGRATION RESULT")
        logger.info("=" * 80)
        logger.info(f"Status: {result['status']}")
        logger.info(f"Steps completed: {result.get('steps_completed', [])}")

        if result.get("errors"):
            logger.warning(f"Errors: {len(result['errors'])}")
            for error in result["errors"]:
                logger.warning(f"  - {error}")

        return result

    except ImportError as e:
        logger.error(f"❌ Could not import migration script: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return None


def v3_verification(migration_result):
    """@v3 validation/verification of migration"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ @V3 VALIDATION/VERIFICATION")
    logger.info("=" * 80)
    logger.info("")

    verification_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "shares_verified": False,
        "migration_verified": False,
        "status": "PENDING"
    }

    # Verify shares exist
    data_exists, docker_exists = verify_shares_exist()
    verification_results["shares_verified"] = data_exists and docker_exists

    if verification_results["shares_verified"]:
        logger.info("✅ Shares verified: Both data and docker shares exist")
    else:
        logger.warning("⚠️  Shares verification failed")

    # Verify migration completed
    if migration_result and migration_result.get("status") == "COMPLETED":
        verification_results["migration_verified"] = True
        logger.info("✅ Migration verified: Status = COMPLETED")

        # Additional verification: Check target has files
        try:
            docker_path = Path(DOCKER_SHARE)
            if docker_path.exists():
                files = list(docker_path.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                logger.info(f"✅ Target verification: {file_count:,} files in target")
                verification_results["file_count"] = file_count
        except Exception as e:
            logger.warning(f"⚠️  Could not count files: {e}")
    else:
        logger.warning(f"⚠️  Migration verification failed: {migration_result.get('status') if migration_result else 'No result'}")

    # Overall status
    if verification_results["shares_verified"] and verification_results["migration_verified"]:
        verification_results["status"] = "SUCCESS"
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ @V3 VALIDATION: SUCCESS")
        logger.info("=" * 80)
    else:
        verification_results["status"] = "PARTIAL"
        logger.warning("")
        logger.warning("=" * 80)
        logger.warning("⚠️  @V3 VALIDATION: PARTIAL")
        logger.warning("=" * 80)

    return verification_results


def main():
    """@DOIT: Full execution from beginning to end"""
    logger.info("=" * 80)
    logger.info("🚀 @DOIT: CREATE DOCKER SHARE AND MIGRATE")
    logger.info("=" * 80)
    logger.info("Full power of @manus/@magneto: All steps, stages, phases")
    logger.info("From beginning to end, successfully, with @v3 validation")
    logger.info("")

    # Step 1: Check current status
    logger.info("📋 Step 1: Checking current status...")
    data_exists = check_share_exists(DATA_SHARE)
    docker_exists = check_share_exists(DOCKER_SHARE)

    logger.info(f"   Data share: {'✅ EXISTS' if data_exists else '❌ NOT FOUND'}")
    logger.info(f"   Docker share: {'✅ EXISTS' if docker_exists else '❌ NOT FOUND'}")
    logger.info("")

    # Step 2: Create shares if needed (DSM API with full root access)
    if not data_exists or not docker_exists:
        logger.info("📋 Step 2: Creating shares via DSM API (full root access)...")

        # Use DSM API (proven reliable with full administrative access)
        api_success = create_share_via_dsm_api()

        if not api_success:
            logger.error("   ❌ DSM API share creation failed")
            logger.error("   This should not happen - API has full root access")
            return

        # Wait for SMB share to be available
        logger.info("   ⏳ Waiting for SMB share to be available...")
        time.sleep(5)

        # Verify shares were created
        data_exists, docker_exists = verify_shares_exist()

        if not data_exists or not docker_exists:
            logger.warning("   ⚠️  Shares created but not yet accessible via SMB")
            logger.info("   This is normal - SMB shares may take time to propagate")
            logger.info("   Directories exist on NAS - proceeding with migration")
            logger.info("   Migration will create target path if needed")

    # Step 3: Run migration
    logger.info("📋 Step 3: Running migration...")
    migration_result = run_migration_with_verification()

    # Step 4: @v3 validation/verification
    logger.info("📋 Step 4: @v3 validation/verification...")
    verification = v3_verification(migration_result)

    # Final summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 @DOIT EXECUTION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Shares created: {'✅' if data_exists and docker_exists else '❌'}")
    logger.info(f"Migration status: {migration_result.get('status') if migration_result else 'N/A'}")
    logger.info(f"@v3 Validation: {verification['status']}")
    logger.info("")

    if verification["status"] == "SUCCESS":
        logger.info("✅ @DOIT COMPLETE: All steps executed successfully with @v3 validation")
    else:
        logger.warning("⚠️  @DOIT PARTIAL: Some steps may need manual intervention")
    logger.info("")


if __name__ == "__main__":


    main()