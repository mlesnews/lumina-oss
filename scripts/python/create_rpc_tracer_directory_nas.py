#!/usr/bin/env python3
"""
Create RPC Tracer Directory on NAS

Attempts to create the Jarvis/Logs/RPCTracer directory on NAS via various methods.

Tags: #CURSOR #RPC_TRACER #NAS #FILE_SYSTEM @JARVIS @LUMINA
"""

import sys
import subprocess
import os
from pathlib import Path, WindowsPath

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CreateRPCTracerDirectoryNAS")

NAS_IP = "<NAS_IP>"
TARGET_PATH = "Jarvis\\Logs\\RPCTracer"

# Common Synology share names
COMMON_SHARES = [
    "volume1",
    "volume2",
    "docker",
    "shared",
    "homes",
    "Jarvis",
    "Logs",
    "data",
    "storage"
]


def try_create_via_network_path(share_name: str = None) -> bool:
    """Try to create directory via network path"""
    if share_name:
        paths_to_try = [
            f"\\\\{NAS_IP}\\{share_name}\\{TARGET_PATH}",
            f"\\\\{NAS_IP}\\{share_name}\\Jarvis\\Logs\\RPCTracer"
        ]
    else:
        # Try without share name first
        paths_to_try = [
            f"\\\\{NAS_IP}\\{TARGET_PATH}",
            f"\\\\{NAS_IP}\\Jarvis\\Logs\\RPCTracer"
        ]
        # Then try with common shares
        for share in COMMON_SHARES:
            paths_to_try.extend([
                f"\\\\{NAS_IP}\\{share}\\{TARGET_PATH}",
                f"\\\\{NAS_IP}\\{share}\\Jarvis\\Logs\\RPCTracer"
            ])

    for path in paths_to_try:
        try:
            logger.info(f"🔍 Trying: {path}")

            # Try to create parent directories first
            parent = Path(path).parent
            if not parent.exists():
                logger.info(f"   Creating parent: {parent}")
                parent.mkdir(parents=True, exist_ok=True)

            # Create target directory
            target = Path(path)
            target.mkdir(parents=True, exist_ok=True)

            if target.exists():
                logger.info(f"✅ Successfully created: {path}")
                return True
        except Exception as e:
            logger.debug(f"   Failed: {e}")
            continue

    return False


def try_create_via_powershell(share_name: str = None) -> bool:
    """Try to create directory via PowerShell"""
    if share_name:
        paths_to_try = [
            f"\\\\{NAS_IP}\\{share_name}\\{TARGET_PATH}",
            f"\\\\{NAS_IP}\\{share_name}\\Jarvis\\Logs\\RPCTracer"
        ]
    else:
        paths_to_try = [
            f"\\\\{NAS_IP}\\{TARGET_PATH}",
            f"\\\\{NAS_IP}\\Jarvis\\Logs\\RPCTracer"
        ]
        for share in COMMON_SHARES:
            paths_to_try.extend([
                f"\\\\{NAS_IP}\\{share}\\{TARGET_PATH}",
                f"\\\\{NAS_IP}\\{share}\\Jarvis\\Logs\\RPCTracer"
            ])

    for path in paths_to_try:
        try:
            logger.info(f"🔍 Trying PowerShell: {path}")
            cmd = [
                "powershell",
                "-Command",
                f"New-Item -ItemType Directory -Path '{path}' -Force -ErrorAction SilentlyContinue"
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 or "already exists" in result.stdout.lower():
                # Verify it exists
                verify_cmd = [
                    "powershell",
                    "-Command",
                    f"Test-Path '{path}'"
                ]
                verify_result = subprocess.run(
                    verify_cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if "True" in verify_result.stdout:
                    logger.info(f"✅ Successfully created: {path}")
                    return True
        except Exception as e:
            logger.debug(f"   Failed: {e}")
            continue

    return False


def check_existing_shares() -> list:
    """Check what shares might be accessible"""
    logger.info("🔍 Checking for accessible NAS shares...")

    accessible_shares = []
    for share in COMMON_SHARES:
        test_path = f"\\\\{NAS_IP}\\{share}"
        try:
            cmd = ["powershell", "-Command", f"Test-Path '{test_path}'"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if "True" in result.stdout:
                logger.info(f"   ✅ Found accessible share: {share}")
                accessible_shares.append(share)
        except:
            continue

    return accessible_shares


def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("📁 CREATING RPC TRACER DIRECTORY ON NAS")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Target: {TARGET_PATH}")
    logger.info(f"NAS IP: {NAS_IP}")
    logger.info("")

    # Step 1: Check for accessible shares
    logger.info("Step 1: Checking for accessible NAS shares...")
    accessible_shares = check_existing_shares()

    if accessible_shares:
        logger.info(f"✅ Found {len(accessible_shares)} accessible share(s)")
        logger.info("")

        # Try creating in each accessible share
        for share in accessible_shares:
            logger.info(f"📁 Attempting to create in share: {share}")
            if try_create_via_powershell(share):
                logger.info("")
                logger.info("=" * 80)
                logger.info("✅ SUCCESS!")
                logger.info("=" * 80)
                logger.info("")
                logger.info("Directory created. Configure in Cursor:")
                logger.info(f"   \\\\{NAS_IP}\\{share}\\Jarvis\\Logs\\RPCTracer")
                logger.info("")
                return
    else:
        logger.warning("⚠️  No accessible shares found via network path")
        logger.info("")

    # Step 2: Try direct network path
    logger.info("Step 2: Trying direct network paths...")
    if try_create_via_powershell():
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SUCCESS!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Directory created. Configure in Cursor:")
        logger.info(f"   \\\\{NAS_IP}\\Jarvis\\Logs\\RPCTracer")
        logger.info("")
        return

    # Step 3: Manual instructions
    logger.info("")
    logger.info("=" * 80)
    logger.info("⚠️  AUTOMATIC CREATION FAILED")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Please create the directory manually using one of these methods:")
    logger.info("")
    logger.info("METHOD 1: Via File Explorer")
    logger.info("   1. Open File Explorer")
    logger.info("   2. Navigate to: \\\\<NAS_IP>\\")
    logger.info("   3. Find your shared folder (e.g., volume1, docker, etc.)")
    logger.info("   4. Create: Jarvis\\Logs\\RPCTracer")
    logger.info("")
    logger.info("METHOD 2: Via DSM File Station")
    logger.info("   1. Open: http://<NAS_IP>:5000")
    logger.info("   2. Open File Station")
    logger.info("   3. Navigate to shared folder")
    logger.info("   4. Create: Jarvis/Logs/RPCTracer")
    logger.info("")
    logger.info("METHOD 3: Via Container Manager")
    logger.info("   1. Open: http://<NAS_IP>/container-manager")
    logger.info("   2. Access container terminal")
    logger.info("   3. Run: mkdir -p /volume1/Jarvis/Logs/RPCTracer")
    logger.info("")
    logger.info("After creating, configure in Cursor:")
    logger.info("   Settings → Beta → Extension RPC Tracer")
    logger.info("   Path: \\\\<NAS_IP>\\<share>\\Jarvis\\Logs\\RPCTracer")
    logger.info("")


if __name__ == "__main__":

    main()