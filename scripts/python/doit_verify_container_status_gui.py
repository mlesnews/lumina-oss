#!/usr/bin/env python3
"""
@DOIT: Verify Container Status via Container Manager GUI

Opens Container Manager in browser and verifies container deployment status.

Tags: #DOIT #VERIFICATION #GUI #CONTAINER #NAS @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any

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

logger = get_logger("DoitVerifyContainerStatusGUI")

NAS_HOST = "<NAS_PRIMARY_IP>"
CONTAINER_NAME = "homelab-ide-notification-handler"


def open_container_manager() -> Dict[str, Any]:
    """Open Container Manager GUI in browser"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("🌐 OPENING CONTAINER MANAGER GUI")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Try to use browser MCP if available
        try:
            from mcp_cursor_ide_browser_browser_navigate import mcp_cursor_ide_browser_browser_navigate
            from mcp_cursor_ide_browser_browser_snapshot import mcp_cursor_ide_browser_browser_snapshot
            from mcp_cursor_ide_browser_browser_wait_for import mcp_cursor_ide_browser_browser_wait_for

            dsm_url = f"https://{NAS_HOST}:5001"
            logger.info(f"📱 Opening DSM: {dsm_url}")

            # Navigate to DSM
            mcp_cursor_ide_browser_browser_navigate(url=dsm_url)
            time.sleep(5)  # Wait for page load

            # Take snapshot to see current state
            snapshot = mcp_cursor_ide_browser_browser_snapshot()
            logger.info("   ✅ Browser opened")

            logger.info("")
            logger.info("📋 Manual Verification Steps:")
            logger.info("   1. Log in to DSM if prompted")
            logger.info("   2. Navigate to: Container Manager")
            logger.info("   3. Go to: Project → homelab-ide-notification-handler")
            logger.info("   4. Check container status:")
            logger.info(f"      - Container name: {CONTAINER_NAME}")
            logger.info("      - Status should be: Running")
            logger.info("      - Check logs if needed")
            logger.info("")

            return {
                "success": True,
                "url": dsm_url,
                "message": "Container Manager opened in browser"
            }
        except ImportError:
            # Fallback: Use webbrowser module
            import webbrowser

            dsm_url = f"https://{NAS_HOST}:5001"
            logger.info(f"📱 Opening DSM: {dsm_url}")

            webbrowser.open(dsm_url)
            time.sleep(2)

            logger.info("   ✅ Browser opened")
            logger.info("")
            logger.info("📋 Manual Verification Steps:")
            logger.info("   1. Log in to DSM if prompted")
            logger.info("   2. Navigate to: Container Manager")
            logger.info("   3. Go to: Project → homelab-ide-notification-handler")
            logger.info("   4. Check container status:")
            logger.info(f"      - Container name: {CONTAINER_NAME}")
            logger.info("      - Status should be: Running")
            logger.info("      - Check logs if needed")
            logger.info("")

            return {
                "success": True,
                "url": dsm_url,
                "message": "Container Manager opened in browser"
            }
    except Exception as e:
        logger.error(f"   ❌ Error opening browser: {e}")
        logger.info("")
        logger.info("📋 Manual Access:")
        logger.info(f"   URL: https://{NAS_HOST}:5001")
        logger.info("   Navigate to: Container Manager → Project → homelab-ide-notification-handler")
        return {
            "success": False,
            "error": str(e),
            "url": f"https://{NAS_HOST}:5001"
        }


def check_container_via_ssh() -> Dict[str, Any]:
    """Attempt to check container via SSH (may fail due to permissions)"""
    logger.info("")
    logger.info("🔍 Attempting SSH container check...")

    import subprocess

    try:
        # Try multiple docker paths
        commands = [
            "docker ps -a --filter name=homelab-ide-notification-handler --format '{{.Names}}|{{.Status}}|{{.Ports}}'",
            "/usr/local/bin/docker ps -a --filter name=homelab-ide-notification-handler --format '{{.Names}}|{{.Status}}|{{.Ports}}'",
            "sudo docker ps -a --filter name=homelab-ide-notification-handler --format '{{.Names}}|{{.Status}}|{{.Ports}}'",
        ]

        for cmd in commands:
            try:
                result = subprocess.run(
                    ["ssh", f"backupadm@{NAS_HOST}", cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and result.stdout.strip():
                    output = result.stdout.strip()
                    if CONTAINER_NAME in output:
                        logger.info(f"   ✅ Container found via SSH")
                        logger.info(f"   📊 Status: {output}")

                        # Parse status
                        parts = output.split('|')
                        if len(parts) >= 2:
                            status = parts[1]
                            if "Up" in status or "Running" in status:
                                logger.info("   ✅ Container is RUNNING")
                            else:
                                logger.warning(f"   ⚠️  Container status: {status}")

                        return {
                            "success": True,
                            "method": "ssh",
                            "status": output
                        }
            except Exception:
                continue

        logger.warning("   ⚠️  SSH docker commands not available (permissions)")
        return {
            "success": False,
            "method": "ssh",
            "message": "Docker commands not available via SSH"
        }
    except Exception as e:
        logger.warning(f"   ⚠️  SSH check failed: {e}")
        return {
            "success": False,
            "method": "ssh",
            "error": str(e)
        }


def main():
    """CLI entry point"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("🚀 @DOIT: OPTIONAL CONTAINER VERIFICATION")
    logger.info("=" * 80)

    # Method 1: SSH check (may fail)
    ssh_result = check_container_via_ssh()

    # Method 2: GUI check (always works)
    gui_result = open_container_manager()

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 80)

    if ssh_result.get("success"):
        logger.info("   ✅ SSH Check: Container status retrieved")
        logger.info(f"      {ssh_result.get('status', 'N/A')}")
    else:
        logger.info("   ⚠️  SSH Check: Not available (use GUI instead)")

    if gui_result.get("success"):
        logger.info("   ✅ GUI Check: Container Manager opened")
        logger.info(f"      URL: {gui_result.get('url', 'N/A')}")

    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("   1. Check Container Manager GUI for container status")
    logger.info("   2. Verify container is 'Running'")
    logger.info("   3. Check logs if container is not running")
    logger.info("   4. Service will handle IDE notifications automatically")
    logger.info("")

    return 0


if __name__ == "__main__":


    sys.exit(main())