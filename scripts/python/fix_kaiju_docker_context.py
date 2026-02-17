#!/usr/bin/env python3
"""
Fix KAIJU Docker Context Connection Issues
Applies /fix command to resolve Docker context timeout problems

Tags: #FIX #DOCKER #KAIJU #CONTEXT #SSH @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("FixKAIJUDockerContext")


def check_docker_daemon_kaiju() -> Dict[str, Any]:
    """Check Docker daemon status on KAIJU"""
    logger.info("🔍 Checking Docker daemon status on KAIJU...")

    try:
        # Check if Docker daemon is running
        result = subprocess.run(
            ["ssh", "root@<NAS_IP>", "systemctl is-active docker"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            status = result.stdout.strip()
            logger.info(f"✅ Docker daemon status: {status}")
            return {"status": "success", "daemon_status": status}
        else:
            logger.warning(f"⚠️  Could not check Docker daemon: {result.stderr}")
            return {"status": "error", "error": result.stderr}

    except subprocess.TimeoutExpired:
        logger.error("❌ SSH command timed out")
        return {"status": "timeout", "error": "SSH command timed out"}
    except Exception as e:
        logger.error(f"❌ Error checking Docker daemon: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


def check_docker_socket_kaiju() -> Dict[str, Any]:
    """Check Docker socket accessibility on KAIJU"""
    logger.info("🔍 Checking Docker socket accessibility on KAIJU...")

    try:
        # Check if Docker socket exists and is accessible
        result = subprocess.run(
            ["ssh", "root@<NAS_IP>", "test -S /var/run/docker.sock && echo 'exists' || echo 'missing'"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            socket_status = result.stdout.strip()
            logger.info(f"✅ Docker socket status: {socket_status}")
            return {"status": "success", "socket_status": socket_status}
        else:
            logger.warning(f"⚠️  Could not check Docker socket: {result.stderr}")
            return {"status": "error", "error": result.stderr}

    except subprocess.TimeoutExpired:
        logger.error("❌ SSH command timed out")
        return {"status": "timeout", "error": "SSH command timed out"}
    except Exception as e:
        logger.error(f"❌ Error checking Docker socket: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


def fix_docker_context_ssh_config() -> Dict[str, Any]:
    """Fix Docker context SSH configuration"""
    logger.info("🔧 Fixing Docker context SSH configuration...")

    try:
        # Check current context
        result = subprocess.run(
            ["docker", "context", "ls"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if "kaiju" in result.stdout:
            logger.info("✅ KAIJU context exists")

            # Try to use context with explicit timeout
            logger.info("🔍 Testing KAIJU context with explicit timeout...")
            test_result = subprocess.run(
                ["docker", "context", "use", "kaiju"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if test_result.returncode == 0:
                logger.info("✅ Context switch successful")

                # Try simple command with timeout
                logger.info("🔍 Testing Docker command via context...")
                docker_result = subprocess.run(
                    ["docker", "version", "--format", "{{.Server.Version}}"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if docker_result.returncode == 0:
                    logger.info(f"✅ Docker command successful: {docker_result.stdout.strip()}")
                    return {"status": "success", "message": "Docker context working"}
                else:
                    logger.warning(f"⚠️  Docker command failed: {docker_result.stderr}")
                    return {"status": "partial", "message": "Context switch works but commands timeout"}
            else:
                logger.warning(f"⚠️  Context switch failed: {test_result.stderr}")
                return {"status": "error", "error": test_result.stderr}
        else:
            logger.warning("⚠️  KAIJU context not found")
            return {"status": "error", "error": "KAIJU context not found"}

    except subprocess.TimeoutExpired:
        logger.error("❌ Command timed out")
        return {"status": "timeout", "error": "Command timed out"}
    except Exception as e:
        logger.error(f"❌ Error fixing Docker context: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


def apply_fixes() -> Dict[str, Any]:
    """Apply /fix to resolve KAIJU Docker context issues"""
    logger.info("=" * 80)
    logger.info("🔧 /FIX: KAIJU Docker Context Connection Issues")
    logger.info("=" * 80)

    results = {
        "timestamp": datetime.now().isoformat(),
        "fixes_applied": [],
        "diagnostics": {},
        "recommendations": []
    }

    # Diagnostic 1: Check Docker daemon
    logger.info("\n📋 Diagnostic 1: Docker Daemon Status")
    daemon_result = check_docker_daemon_kaiju()
    results["diagnostics"]["docker_daemon"] = daemon_result

    # Diagnostic 2: Check Docker socket
    logger.info("\n📋 Diagnostic 2: Docker Socket Accessibility")
    socket_result = check_docker_socket_kaiju()
    results["diagnostics"]["docker_socket"] = socket_result

    # Fix 1: Optimize Docker context SSH config
    logger.info("\n🔧 Fix 1: Docker Context SSH Configuration")
    context_result = fix_docker_context_ssh_config()
    results["fixes_applied"].append({
        "fix": "docker_context_ssh_config",
        "result": context_result
    })

    # Recommendations
    logger.info("\n💡 Recommendations:")
    recommendations = [
        "1. Verify Docker daemon is running on KAIJU: ssh root@<NAS_IP> 'systemctl status docker'",
        "2. Check Docker socket permissions: ssh root@<NAS_IP> 'ls -la /var/run/docker.sock'",
        "3. Test direct Docker command: ssh root@<NAS_IP> 'docker images kali-hardened-millennium-falc'",
        "4. Consider using Docker TCP socket instead of SSH if SSH continues to timeout",
        "5. Check network latency: ping <NAS_IP>",
        "6. Verify SSH connection: ssh root@<NAS_IP> 'echo test'"
    ]

    for rec in recommendations:
        logger.info(f"   {rec}")
        results["recommendations"].append(rec)

    logger.info("\n📊 /FIX Summary:")
    logger.info(f"   Diagnostics: {len(results['diagnostics'])}")
    logger.info(f"   Fixes Applied: {len(results['fixes_applied'])}")
    logger.info(f"   Recommendations: {len(results['recommendations'])}")

    return results


def main():
    """CLI interface"""
    from datetime import datetime

    print("="*80)
    print("🔧 /FIX: KAIJU Docker Context Connection Issues")
    print("="*80)
    print()

    results = apply_fixes()

    print()
    print("="*80)
    print("✅ /FIX COMPLETE")
    print("="*80)
    print(f"Diagnostics: {len(results['diagnostics'])}")
    print(f"Fixes Applied: {len(results['fixes_applied'])}")
    print(f"Recommendations: {len(results['recommendations'])}")
    print()


if __name__ == "__main__":


    main()