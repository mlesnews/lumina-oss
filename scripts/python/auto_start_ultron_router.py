#!/usr/bin/env python3
"""
Auto-Start ULTRON Cluster Router API

Waits for Docker Desktop to start, then automatically starts the ULTRON cluster router API.
Runs as a background service that monitors Docker and starts the router when ready.

Tags: #ULTRON #AUTO_START #DOCKER #ROUTER @JARVIS @LUMINA
"""

import sys
import time
import subprocess
import signal
import os
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_unified_logger import LuminaUnifiedLogger
    logger_module = LuminaUnifiedLogger("Application", "ULTRONRouter")
    logger = logger_module.get_logger()
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("AutoStartULTRONRouter")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("AutoStartULTRONRouter")

# Global process handle
router_process: Optional[subprocess.Popen] = None


def check_docker_desktop_process() -> bool:
    """Check if Docker Desktop process is running (faster check)"""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Docker Desktop.exe"],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "Docker Desktop.exe" in result.stdout
        else:
            # Unix: check for docker process
            result = subprocess.run(
                ["pgrep", "-f", "Docker Desktop"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
    except Exception:
        return False


def check_docker_running() -> bool:
    """Check if Docker daemon is responding"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    except Exception as e:
        logger.debug(f"Docker check error: {e}")
        return False


def wait_for_docker(max_wait: int = 300) -> bool:
    """Wait for Docker Desktop to be ready"""
    logger.info("⏳ Waiting for Docker Desktop to start...")

    start_time = time.time()
    check_interval = 2  # Check every 2 seconds (faster)
    docker_process_seen = False

    while time.time() - start_time < max_wait:
        # First check if Docker Desktop process is running
        if check_docker_desktop_process():
            docker_process_seen = True
            logger.info("   Docker Desktop process detected, waiting for daemon...")
            # Now check if Docker daemon is responding
            if check_docker_running():
                logger.info("✅ Docker Desktop is running and ready")
                # Give it a few more seconds to fully initialize
                time.sleep(2)
                return True
        elif docker_process_seen:
            # Process was seen but now gone? Might be restarting
            logger.warning("   Docker Desktop process disappeared, continuing to wait...")

        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:  # Log every 10 seconds
            logger.info(f"   Waiting for Docker Desktop... ({elapsed}s elapsed)")
        time.sleep(check_interval)

    logger.error(f"❌ Docker Desktop did not start within {max_wait} seconds")
    return False


def start_ultron_router() -> Optional[subprocess.Popen]:
    """Start ULTRON cluster router API"""
    router_script = script_dir / "ultron_cluster_router_api.py"

    if not router_script.exists():
        logger.error(f"❌ Router script not found: {router_script}")
        return None

    try:
        logger.info("🚀 Starting ULTRON cluster router API...")

        # Start router in background (detached, so it continues after script exits)
        if sys.platform == "win32":
            # Windows: Use DETACHED_PROCESS to run in background
            process = subprocess.Popen(
                [sys.executable, str(router_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                start_new_session=True
            )
        else:
            # Unix: Use nohup-like behavior
            process = subprocess.Popen(
                [sys.executable, str(router_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

        # Give it a moment to start
        time.sleep(2)

        # Check if it's still running
        if process.poll() is None:
            logger.info("✅ ULTRON cluster router API started (PID: {})".format(process.pid))
            logger.info("   API available at: http://localhost:8080")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Router failed to start")
            logger.error(f"   stdout: {stdout}")
            logger.error(f"   stderr: {stderr}")
            return None

    except Exception as e:
        logger.error(f"❌ Error starting router: {e}")
        return None


def check_router_running(process: Optional[subprocess.Popen]) -> bool:
    """Check if router process is still running"""
    if process is None:
        return False

    return process.poll() is None


def monitor_and_restart():
    """Monitor router and restart if needed"""
    global router_process

    logger.info("=" * 80)
    logger.info("🔄 ULTRON CLUSTER ROUTER AUTO-START MONITOR")
    logger.info("=" * 80)
    logger.info("")

    # Wait for Docker
    if not wait_for_docker():
        logger.error("❌ Cannot start router - Docker not available")
        return

    # Start router
    router_process = start_ultron_router()

    if router_process is None:
        logger.error("❌ Failed to start router")
        return

    # Monitor loop
    logger.info("")
    logger.info("📊 Monitoring router (Ctrl+C to stop)...")
    logger.info("")

    try:
        while True:
            time.sleep(30)  # Check every 30 seconds

            # Check if Docker is still running
            if not check_docker_running():
                logger.warning("⚠️  Docker stopped - waiting for restart...")
                if router_process:
                    router_process.terminate()
                    router_process = None
                wait_for_docker()
                router_process = start_ultron_router()
                continue

            # Check if router is still running
            if not check_router_running(router_process):
                logger.warning("⚠️  Router stopped - restarting...")
                router_process = start_ultron_router()
                if router_process is None:
                    logger.error("❌ Failed to restart router")
                    time.sleep(60)  # Wait before retry

    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Stopping monitor...")
        if router_process:
            logger.info("   Terminating router process...")
            router_process.terminate()
            router_process.wait(timeout=5)
        logger.info("✅ Monitor stopped")
    except Exception as e:
        logger.error(f"❌ Monitor error: {e}")
        if router_process:
            router_process.terminate()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global router_process
    logger.info("🛑 Received shutdown signal")
    if router_process:
        router_process.terminate()
    sys.exit(0)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-start ULTRON Cluster Router API")
    parser.add_argument("--once", action="store_true", help="Start once and exit (no monitoring)")
    parser.add_argument("--wait", type=int, default=300, help="Max wait time for Docker (seconds)")

    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.once:
        # Start once and exit
        if wait_for_docker(max_wait=args.wait):
            process = start_ultron_router()
            if process:
                logger.info("✅ Router started - running in background")
                logger.info("   Process will continue after script exits")
                # Don't wait - let it run in background
            else:
                sys.exit(1)
        else:
            sys.exit(1)
    else:
        # Monitor and restart
        monitor_and_restart()


if __name__ == "__main__":

    main()