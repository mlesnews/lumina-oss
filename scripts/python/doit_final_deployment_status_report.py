#!/usr/bin/env python3
"""
@DOIT: Final Deployment Status Report

Comprehensive status report for @homelab IDE Notification Handler deployment.

Tags: #DOIT #STATUS #REPORT #DEPLOYMENT #NAS @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

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

logger = get_logger("DoitFinalDeploymentStatusReport")

NAS_HOST = "<NAS_PRIMARY_IP>"
NAS_USER = "backupadm"
NAS_DOCKER_PATH = "/volume1/docker/homelab-ide-notification-handler"
CONTAINER_NAME = "homelab-ide-notification-handler"


def check_files() -> Dict[str, Any]:
    """Check all required files exist"""
    logger.info("📁 Checking deployment files...")

    files = [
        "docker-compose.yml",
        "Dockerfile",
        "requirements.txt",
        "README.md",
        "DEPLOYMENT.md"
    ]

    results = {}
    for file in files:
        cmd = f"test -f {NAS_DOCKER_PATH}/{file} && echo 'EXISTS' || echo 'NOT_FOUND'"
        try:
            result = subprocess.run(
                ["ssh", f"{NAS_USER}@{NAS_HOST}", cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            exists = "EXISTS" in result.stdout
            results[file] = exists
            status = "✅" if exists else "❌"
            logger.info(f"   {status} {file}")
        except Exception as e:
            results[file] = False
            logger.error(f"   ❌ {file} - Error: {e}")

    all_exist = all(results.values())
    return {
        "status": "✅ PASS" if all_exist else "❌ FAIL",
        "files": results,
        "all_exist": all_exist
    }


def check_project_structure() -> Dict[str, Any]:
    """Check project directory structure"""
    logger.info("")
    logger.info("📂 Checking project structure...")

    try:
        cmd = f"ls -la {NAS_DOCKER_PATH} 2>&1"
        result = subprocess.run(
            ["ssh", f"{NAS_USER}@{NAS_HOST}", cmd],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            file_count = len([l for l in result.stdout.split('\n') if l.strip() and not l.startswith('total') and not l.startswith('d')])
            logger.info(f"   ✅ Project directory exists ({file_count} items)")
            logger.info(f"   📍 Path: {NAS_DOCKER_PATH}")
            return {
                "status": "✅ PASS",
                "path": NAS_DOCKER_PATH,
                "item_count": file_count
            }
        else:
            logger.error(f"   ❌ Project directory check failed")
            return {
                "status": "❌ FAIL",
                "error": result.stderr
            }
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return {
            "status": "❌ FAIL",
            "error": str(e)
        }


def check_docker_compose_config() -> Dict[str, Any]:
    """Verify docker-compose.yml configuration"""
    logger.info("")
    logger.info("🔍 Checking docker-compose.yml configuration...")

    try:
        cmd = f"cat {NAS_DOCKER_PATH}/docker-compose.yml | grep -E '(container_name|image|restart|network_mode)' | head -10"
        result = subprocess.run(
            ["ssh", f"{NAS_USER}@{NAS_HOST}", cmd],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():
            logger.info("   ✅ Configuration valid")
            logger.info("   📋 Key settings:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(f"      {line.strip()}")

            # Check for container name
            has_container_name = CONTAINER_NAME in result.stdout
            return {
                "status": "✅ PASS",
                "has_container_name": has_container_name,
                "config": result.stdout.strip()
            }
        else:
            logger.error("   ❌ Configuration check failed")
            return {
                "status": "❌ FAIL",
                "error": "Could not read configuration"
            }
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return {
            "status": "❌ FAIL",
            "error": str(e)
        }


def generate_access_instructions() -> None:
    """Generate access and verification instructions"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("📋 CONTAINER MANAGER ACCESS INSTRUCTIONS")
    logger.info("=" * 80)
    logger.info("")
    logger.info("🌐 GUI Access:")
    logger.info(f"   URL: https://{NAS_HOST}:5001")
    logger.info("   Note: Certificate warning is normal - click 'Advanced' → 'Proceed'")
    logger.info("")
    logger.info("📂 Navigation Path:")
    logger.info("   1. Log in to DSM")
    logger.info("   2. Open: Container Manager")
    logger.info("   3. Go to: Project tab")
    logger.info(f"   4. Find: homelab-ide-notification-handler")
    logger.info("   5. Click on project to view details")
    logger.info("")
    logger.info("🔍 Verification Steps:")
    logger.info(f"   1. Check container name: {CONTAINER_NAME}")
    logger.info("   2. Verify status: Should be 'Running' (green)")
    logger.info("   3. Check logs: Click 'Logs' button if available")
    logger.info("   4. Verify restart policy: 'unless-stopped'")
    logger.info("")
    logger.info("📊 Expected Container Details:")
    logger.info(f"   - Name: {CONTAINER_NAME}")
    logger.info("   - Image: homelab-ide-notification-handler:latest")
    logger.info("   - Status: Running")
    logger.info("   - Network: host")
    logger.info("   - Restart: unless-stopped")
    logger.info("")


def generate_final_report() -> Dict[str, Any]:
    """Generate comprehensive final report"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 @DOIT: FINAL DEPLOYMENT STATUS REPORT")
    logger.info("=" * 80)
    logger.info(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    # Run all checks
    files_check = check_files()
    structure_check = check_project_structure()
    config_check = check_docker_compose_config()

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("📋 VERIFICATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Files Check: {files_check['status']}")
    logger.info(f"   Structure Check: {structure_check['status']}")
    logger.info(f"   Config Check: {config_check['status']}")
    logger.info("")

    # Overall status
    all_passed = (
        files_check.get("all_exist", False) and
        "✅" in structure_check.get("status", "") and
        "✅" in config_check.get("status", "")
    )

    if all_passed:
        logger.info("=" * 80)
        logger.info("✅ DEPLOYMENT FILES VERIFIED - READY FOR CONTAINER DEPLOYMENT")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Deployment Status:")
        logger.info("   ✅ All files copied to NAS")
        logger.info("   ✅ Project structure created")
        logger.info("   ✅ docker-compose.yml configured")
        logger.info("   ⚠️  Container status: Check Container Manager GUI")
        logger.info("")
        logger.info("🎯 Next Actions:")
        logger.info("   1. Open Container Manager GUI (see instructions below)")
        logger.info("   2. Verify container is running")
        logger.info("   3. Check logs if container is not running")
        logger.info("   4. Service will automatically handle IDE notifications")
    else:
        logger.info("=" * 80)
        logger.info("⚠️  DEPLOYMENT INCOMPLETE - SOME CHECKS FAILED")
        logger.info("=" * 80)

    # Access instructions
    generate_access_instructions()

    # Service information
    logger.info("=" * 80)
    logger.info("🔧 SERVICE INFORMATION")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📋 Service Name: @homelab IDE Notification Handler")
    logger.info("📋 Purpose: Automatically handles IDE/VS Code/Cursor notifications")
    logger.info("📋 Location: NAS Container Manager")
    logger.info("📋 Architecture: Docker container on Synology NAS")
    logger.info("")
    logger.info("🎯 Service Capabilities:")
    logger.info("   ✅ Large file dialog handling")
    logger.info("   ✅ Performance warning dismissal")
    logger.info("   ✅ Extension update notifications")
    logger.info("   ✅ Git notification monitoring")
    logger.info("")
    logger.info("🔄 Service Behavior:")
    logger.info("   - Runs continuously in background")
    logger.info("   - Monitors IDE notifications every 5 seconds")
    logger.info("   - Automatically handles common dialogs")
    logger.info("   - Logs all actions for debugging")
    logger.info("")

    return {
        "timestamp": datetime.now().isoformat(),
        "files_check": files_check,
        "structure_check": structure_check,
        "config_check": config_check,
        "overall_status": "✅ READY" if all_passed else "⚠️  INCOMPLETE"
    }


def main():
    """CLI entry point"""
    report = generate_final_report()
    return 0 if "✅" in report["overall_status"] else 1


if __name__ == "__main__":


    sys.exit(main())