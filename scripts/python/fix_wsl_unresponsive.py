#!/usr/bin/env python3
"""
WSL Unresponsive Fix Utility

Diagnoses and attempts to fix WSL unresponsiveness issues.
Handles Docker Desktop WSL communication failures.

Tags: #WSL #DOCKER #FIX #DIAGNOSTIC @JARVIS @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("WSLFix")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("WSLFix")


def check_wsl_status() -> Dict[str, Any]:
    """Check WSL status and responsiveness"""
    result = {
        "wsl_available": False,
        "wsl_responsive": False,
        "distributions": [],
        "error": None
    }

    try:
        # Try quick WSL command with short timeout
        test_cmd = subprocess.run(
            ['wsl', '--status'],
            capture_output=True,
            timeout=5,
            text=True
        )

        if test_cmd.returncode == 0:
            result["wsl_available"] = True

            # Try listing distributions
            list_cmd = subprocess.run(
                ['wsl', '--list', '--verbose'],
                capture_output=True,
                timeout=10,
                text=False
            )

            if list_cmd.returncode == 0:
                result["wsl_responsive"] = True
                # Parse distributions (handle UTF-16LE encoding)
                try:
                    decoded = list_cmd.stdout.decode("utf-16-le")
                except UnicodeDecodeError:
                    decoded = list_cmd.stdout.decode("utf-8", errors="ignore")

                lines = decoded.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.replace('*', '').strip().split()
                        if parts:
                            result["distributions"].append({
                                "name": parts[0],
                                "state": parts[1] if len(parts) > 1 else "Unknown",
                                "version": parts[2] if len(parts) > 2 else "Unknown"
                            })
            else:
                result["error"] = f"WSL list command failed: {list_cmd.stderr}"
        else:
            result["error"] = f"WSL status command failed: {test_cmd.stderr}"

    except subprocess.TimeoutExpired:
        result["error"] = "WSL command timed out - WSL is unresponsive"
    except FileNotFoundError:
        result["error"] = "WSL not found - WSL may not be installed"
    except Exception as e:
        result["error"] = f"WSL check failed: {e}"
        logger.error("WSL status check failed", exc_info=True)

    return result


def restart_wsl() -> Dict[str, Any]:
    """Attempt to restart WSL"""
    result = {
        "success": False,
        "method": None,
        "error": None
    }

    try:
        logger.info("Attempting to shutdown WSL...")
        shutdown_cmd = subprocess.run(
            ['wsl', '--shutdown'],
            capture_output=True,
            timeout=30,
            text=True
        )

        if shutdown_cmd.returncode == 0:
            logger.info("WSL shutdown command sent")
            result["method"] = "shutdown"
            # Wait a moment for shutdown to complete
            time.sleep(3)

            # Test if WSL is responsive now
            test_status = check_wsl_status()
            if test_status["wsl_responsive"]:
                result["success"] = True
                logger.info("✅ WSL is now responsive after shutdown")
            else:
                result["error"] = "WSL shutdown completed but WSL still unresponsive"
                logger.warning("WSL shutdown completed but WSL still unresponsive")
        else:
            result["error"] = f"WSL shutdown failed: {shutdown_cmd.stderr}"
            logger.error("WSL shutdown command failed")

    except subprocess.TimeoutExpired:
        result["error"] = "WSL shutdown command timed out"
        logger.error("WSL shutdown timed out - may need manual restart")
    except Exception as e:
        result["error"] = f"WSL restart failed: {e}"
        logger.error("WSL restart failed", exc_info=True)

    return result


def fix_wsl_unresponsive() -> Dict[str, Any]:
    """Main fix workflow for WSL unresponsiveness"""
    result = {
        "diagnosis": {},
        "fix_attempted": False,
        "fix_success": False,
        "recommendations": []
    }

    print("="*80)
    print("🔧 WSL UNRESPONSIVE FIX UTILITY")
    print("="*80)
    print()

    # Step 1: Diagnose
    print("Step 1: Diagnosing WSL status...")
    diagnosis = check_wsl_status()
    result["diagnosis"] = diagnosis

    print(f"WSL Available: {diagnosis['wsl_available']}")
    print(f"WSL Responsive: {diagnosis['wsl_responsive']}")

    if diagnosis.get("error"):
        print(f"Error: {diagnosis['error']}")

    if diagnosis["distributions"]:
        print(f"\nFound {len(diagnosis['distributions'])} WSL distribution(s):")
        for distro in diagnosis["distributions"]:
            print(f"  - {distro['name']}: {distro['state']} (WSL{distro['version']})")

    print()

    # Step 2: Attempt fix if needed
    if not diagnosis["wsl_responsive"]:
        print("Step 2: WSL is unresponsive. Attempting fix...")
        result["fix_attempted"] = True

        fix_result = restart_wsl()

        if fix_result["success"]:
            result["fix_success"] = True
            print("✅ WSL fix successful!")
            print()
            print("Next steps:")
            print("  1. Restart Docker Desktop")
            print("  2. Test WSL access: wsl -d kali-linux")
            print("  3. Verify Perl installation if needed")
        else:
            print(f"⚠️  Automatic fix failed: {fix_result.get('error')}")
            print()
            result["recommendations"].append("Manual restart required")
            result["recommendations"].append("Restart your machine to fully reset WSL")
    else:
        print("✅ WSL is responsive - no fix needed")
        result["fix_success"] = True

    print()
    print("="*80)

    return result


def main():
    """Main entry point"""
    result = fix_wsl_unresponsive()

    if not result["fix_success"]:
        print("\n📋 Manual Recovery Steps:")
        print("  1. Close Docker Desktop completely")
        print("  2. Run: wsl --shutdown")
        print("  3. Wait 10 seconds")
        print("  4. Restart Docker Desktop")
        print("  5. If still unresponsive, restart your machine")
        print()
        return 1

    return 0


if __name__ == "__main__":


    sys.exit(main())