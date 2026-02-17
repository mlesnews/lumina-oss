#!/usr/bin/env python3
"""
Restart Neo Browser with CDP Enabled
Restarts Neo with --remote-allow-origins flag to enable CDP automation

Tags: #NEO #CDP #AUTOMATION #BROWSER
"""

import sys
import os
import time
import subprocess
import psutil
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RestartNeoWithCDP")


def kill_neo_processes():
    """Kill all existing Neo browser processes"""
    logger.info("🔪 Killing existing Neo processes...")
    killed = 0

    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                name = proc.info['name'] or ''
                exe = proc.info['exe'] or ''

                if 'neo' in name.lower() or 'neo.exe' in name.lower():
                    logger.info(f"   Killing process: PID {proc.info['pid']} - {name}")
                    proc.kill()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.warning(f"   Error killing processes: {e}")

    if killed > 0:
        logger.info(f"   ✅ Killed {killed} Neo process(es)")
        time.sleep(2)  # Wait for processes to terminate
    else:
        logger.info("   ℹ️  No Neo processes found")

    return killed


def restart_neo_with_cdp(url: str = None):
    """Restart Neo browser with CDP enabled"""
    logger.info("=" * 70)
    logger.info("🚀 RESTARTING NEO WITH CDP ENABLED")
    logger.info("=" * 70)
    logger.info("")

    # Step 1: Kill existing processes
    kill_neo_processes()

    # Step 2: Find Neo executable
    neo_exe = Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "Application" / "neo.exe"

    if not neo_exe.exists():
        logger.error(f"❌ Neo executable not found at: {neo_exe}")
        return False

    logger.info(f"✅ Found Neo executable: {neo_exe}")
    logger.info("")

    # Step 3: Build launch arguments
    args = [str(neo_exe)]

    # Enable remote debugging (CDP)
    args.append(f"--remote-debugging-port=9222")

    # Allow CDP connections from any origin (required for automation)
    args.append("--remote-allow-origins=*")

    # Additional automation-friendly flags
    args.extend([
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-blink-features=AutomationControlled",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ])

    # Add URL if provided
    if url:
        args.append(url)

    logger.info("STEP 2: Launching Neo with CDP enabled...")
    logger.info(f"   Command: {' '.join(args[:5])}... (truncated)")
    logger.info("")

    try:
        # Launch Neo
        process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        logger.info(f"✅ Neo launched (PID: {process.pid})")
        logger.info("")

        # Step 3: Wait for CDP to become available
        logger.info("STEP 3: Waiting for CDP to become available...")
        import requests

        max_wait = 20
        for i in range(max_wait):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:9222/json", timeout=2)
                if response.status_code == 200:
                    sessions = response.json()
                    if sessions:
                        logger.info(f"✅ CDP is available! ({len(sessions)} session(s))")
                        logger.info("")
                        logger.info("=" * 70)
                        logger.info("✅ NEO RESTARTED WITH CDP ENABLED")
                        logger.info("=" * 70)
                        logger.info("")
                        logger.info("📋 Next steps:")
                        logger.info("   1. Navigate to ProtonPass: https://proton.me/pass")
                        logger.info("   2. Run credential extraction:")
                        logger.info("      python scripts/python/jarvis_fidelity_neo_protonpass_extractor.py --extract")
                        logger.info("")
                        return True
            except requests.exceptions.ConnectionError:
                if i % 5 == 0 and i > 0:
                    logger.info(f"   Still waiting... ({i}/{max_wait})")
                continue
            except Exception as e:
                logger.debug(f"   CDP check error: {e}")

        logger.warning("⚠️  CDP not available after waiting")
        logger.info("   Neo may need more time to start")
        return False

    except Exception as e:
        logger.error(f"❌ Failed to launch Neo: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Restart Neo Browser with CDP Enabled")
    parser.add_argument("--url", "-u", help="URL to open after restart")
    parser.add_argument("--protonpass", "-p", action="store_true", help="Open ProtonPass after restart")

    args = parser.parse_args()

    url = args.url
    if args.protonpass:
        url = "https://proton.me/pass"

    success = restart_neo_with_cdp(url)

    if success:
        print("\n✅ Neo restarted successfully with CDP enabled!")
        print("   You can now run credential extraction scripts")
    else:
        print("\n⚠️  Neo restart completed, but CDP may not be fully ready")
        print("   Wait a few seconds and try credential extraction")


if __name__ == "__main__":


    main()