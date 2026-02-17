#!/usr/bin/env python3
"""
Complete Docker Migration @v3 Validation
Final verification and completion of Docker volume migration

Tags: #DOIT #NAS_MIGRATION #DOCKER #V3_VALIDATION @JARVIS @LUMINA
"""

import sys
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
    logger = get_comprehensive_logger("CompleteDockerMigrationV3")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CompleteDockerMigrationV3")

NAS_IP = "<NAS_PRIMARY_IP>"
DOCKER_SOURCE = Path("C:\\Users\\mlesn\\AppData\\Local\\Docker")
DOCKER_TARGET = Path(f"\\\\{NAS_IP}\\docker\\Docker")


def check_docker_terminal():
    """Verify Docker terminal access"""
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"   ✅ Docker terminal: {result.stdout.strip()}")
            return True
        return False
    except Exception as e:
        logger.error(f"   ❌ Docker terminal error: {e}")
        return False


def check_migration_completion():
    """Check if migration completed successfully"""
    logger.info("📊 Checking migration completion...")

    source_exists = DOCKER_SOURCE.exists()
    target_exists = DOCKER_TARGET.exists()

    if not source_exists:
        logger.warning("   ⚠️  Source directory does not exist (may have been moved)")
        source_size = 0
    else:
        try:
            source_size = sum(
                f.stat().st_size for f in DOCKER_SOURCE.rglob("*") if f.is_file()
            ) / (1024**3)
        except:
            source_size = 0

    if not target_exists:
        logger.error("   ❌ Target directory does not exist")
        return False, 0, 0

    try:
        target_items = list(DOCKER_TARGET.rglob("*"))
        target_size = sum(f.stat().st_size for f in target_items if f.is_file()) / (1024**3)
        target_files = len([f for f in target_items if f.is_file()])
    except Exception as e:
        logger.error(f"   ❌ Error checking target: {e}")
        return False, 0, 0

    logger.info(f"   Source: {source_size:.2f} GB")
    logger.info(f"   Target: {target_size:.2f} GB ({target_files:,} files)")

    # Migration is considered complete if target has substantial data
    # (at least 1GB or 80% of source, whichever is smaller)
    if target_size > 1.0 or (source_size > 0 and target_size >= source_size * 0.8):
        logger.info("   ✅ Migration appears complete")
        return True, source_size, target_size
    else:
        logger.warning("   ⚠️  Migration may be incomplete")
        return False, source_size, target_size


def check_docker_containers():
    """Check Docker container status"""
    logger.info("🐳 Checking Docker containers...")
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            containers = [line for line in result.stdout.strip().split('\n') if line.strip()]
            running = [c for c in containers if 'Up' in c]
            logger.info(f"   Total containers: {len(containers)}")
            logger.info(f"   Running: {len(running)}")
            return len(containers), len(running)
        return 0, 0
    except Exception as e:
        logger.warning(f"   ⚠️  Error checking containers: {e}")
        return 0, 0


def v3_validation():
    try:
        """Complete @v3 validation/verification"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ @V3 VALIDATION/VERIFICATION - FINAL")
        logger.info("=" * 80)
        logger.info("")

        validation_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "docker_terminal": False,
            "migration_complete": False,
            "shares_verified": False,
            "containers_status": "UNKNOWN",
            "status": "PENDING"
        }

        # Step 1: Docker Terminal
        logger.info("📋 Step 1: Docker Terminal Access")
        validation_results["docker_terminal"] = check_docker_terminal()
        logger.info("")

        # Step 2: Migration Completion
        logger.info("📋 Step 2: Migration Completion Check")
        migration_complete, source_size, target_size = check_migration_completion()
        validation_results["migration_complete"] = migration_complete
        validation_results["source_size_gb"] = round(source_size, 2)
        validation_results["target_size_gb"] = round(target_size, 2)
        logger.info("")

        # Step 3: Share Verification
        logger.info("📋 Step 3: Share Verification")
        share_exists = DOCKER_TARGET.exists()
        validation_results["shares_verified"] = share_exists
        if share_exists:
            logger.info(f"   ✅ Share accessible: {DOCKER_TARGET}")
        else:
            logger.warning(f"   ⚠️  Share not accessible: {DOCKER_TARGET}")
        logger.info("")

        # Step 4: Docker Containers
        logger.info("📋 Step 4: Docker Container Status")
        total_containers, running_containers = check_docker_containers()
        validation_results["containers_total"] = total_containers
        validation_results["containers_running"] = running_containers
        validation_results["containers_status"] = f"{running_containers}/{total_containers} running"
        logger.info("")

        # Final Status
        logger.info("=" * 80)
        if (validation_results["docker_terminal"] and 
            validation_results["migration_complete"] and 
            validation_results["shares_verified"]):
            validation_results["status"] = "SUCCESS"
            logger.info("✅ @V3 VALIDATION: SUCCESS")
            logger.info("   All checks passed - Migration complete")
        elif validation_results["migration_complete"]:
            validation_results["status"] = "PARTIAL_SUCCESS"
            logger.info("✅ @V3 VALIDATION: PARTIAL SUCCESS")
            logger.info("   Migration complete, some checks may need attention")
        else:
            validation_results["status"] = "PARTIAL"
            logger.warning("⚠️  @V3 VALIDATION: PARTIAL")
            logger.warning("   Migration may need additional steps")
        logger.info("=" * 80)
        logger.info("")

        return validation_results


    except Exception as e:
        logger.error(f"Error in v3_validation: {e}", exc_info=True)
        raise
def main():
    try:
        """Complete @v3 validation and finalize migration"""
        logger.info("=" * 80)
        logger.info("🚀 COMPLETE DOCKER MIGRATION - @V3 VALIDATION")
        logger.info("=" * 80)
        logger.info("Final verification and completion")
        logger.info("")

        # Run @v3 validation
        results = v3_validation()

        # Save results
        results_file = project_root / "data" / "nas_migration" / "docker_migration_v3_complete.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 FINAL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Docker Terminal: {'✅' if results['docker_terminal'] else '❌'}")
        logger.info(f"Migration Complete: {'✅' if results['migration_complete'] else '❌'}")
        logger.info(f"Shares Verified: {'✅' if results['shares_verified'] else '❌'}")
        logger.info(f"Containers: {results['containers_status']}")
        logger.info(f"@v3 Status: {results['status']}")
        logger.info("")
        logger.info(f"📄 Results saved: {results_file}")
        logger.info("")

        if results['status'] == "SUCCESS":
            logger.info("✅ @DOIT COMPLETE: All steps executed successfully with @v3 validation")
        elif results['status'] == "PARTIAL_SUCCESS":
            logger.info("✅ @DOIT MOSTLY COMPLETE: Migration successful, minor items may need attention")
        else:
            logger.warning("⚠️  @DOIT PARTIAL: Migration in progress, may need additional steps")
        logger.info("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()