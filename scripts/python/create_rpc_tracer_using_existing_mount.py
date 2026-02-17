#!/usr/bin/env python3
"""
Create RPC Tracer Directory Using Existing NAS Mount Point

Uses the existing permanent mount point on NAS to create the RPC Tracer directory.

Tags: #CURSOR #RPC_TRACER #NAS #MOUNT @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

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

logger = get_logger("CreateRPCTracerExistingMount")

# Common mount point paths (user should specify which one)
MOUNT_PATHS = [
    "\\<NAS_IP>\\Jarvis",  # If Jarvis is a share
    "\\<NAS_IP>\\volume1\\Jarvis",  # If Jarvis is a folder in volume1
    "\\<NAS_IP>\\docker\\Jarvis",  # If Jarvis is in docker share
    "\\<NAS_IP>\\shared\\Jarvis",  # If Jarvis is in shared
    "L:\\Jarvis",  # If L drive is mapped
    "M:\\Jarvis",  # If M drive is mapped
]


def find_existing_mount() -> str:
    """Find the existing mount point"""
    logger.info("🔍 Checking for existing mount points...")

    for mount_path in MOUNT_PATHS:
        try:
            test_path = Path(mount_path)
            if test_path.exists():
                logger.info(f"✅ Found existing mount: {mount_path}")
                return mount_path
        except Exception as e:
            logger.debug(f"   {mount_path}: {e}")
            continue

    logger.warning("⚠️  Could not find existing mount point automatically")
    return None


def create_rpc_tracer_directory(base_path: str) -> bool:
    """Create RPC Tracer directory at the mount point"""
    try:
        target_path = Path(base_path) / "Logs" / "RPCTracer"

        logger.info(f"📁 Creating: {target_path}")
        target_path.mkdir(parents=True, exist_ok=True)

        if target_path.exists():
            logger.info(f"✅ Successfully created: {target_path}")
            return True
        else:
            logger.error(f"❌ Failed to create: {target_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Error creating directory: {e}")
        return False


def main():
    try:
        """Main function"""
        logger.info("=" * 80)
        logger.info("📁 CREATING RPC TRACER DIRECTORY USING EXISTING MOUNT")
        logger.info("=" * 80)
        logger.info("")

        # Find existing mount
        mount_path = find_existing_mount()

        if not mount_path:
            logger.info("")
            logger.info("⚠️  Please specify your existing mount point path:")
            logger.info("")
            logger.info("Common options:")
            logger.info("   - \\\\<NAS_IP>\\Jarvis")
            logger.info("   - \\\\<NAS_IP>\\volume1\\Jarvis")
            logger.info("   - \\\\<NAS_IP>\\docker\\Jarvis")
            logger.info("   - L:\\Jarvis (if L drive is mapped)")
            logger.info("   - M:\\Jarvis (if M drive is mapped)")
            logger.info("")
            logger.info("Or run this script with the path as an argument:")
            logger.info("   python create_rpc_tracer_using_existing_mount.py <mount_path>")
            logger.info("")
            return

        # Create directory
        logger.info("")
        if create_rpc_tracer_directory(mount_path):
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ SUCCESS!")
            logger.info("=" * 80)
            logger.info("")
            logger.info("Directory created. Configure in Cursor:")
            logger.info(f"   {Path(mount_path) / 'Logs' / 'RPCTracer'}")
            logger.info("")
            logger.info("Or if using network path:")
            network_path = Path(mount_path).as_posix().replace('/', '\\') + '\\Logs\\RPCTracer'
            logger.info(f"   {network_path}")
            logger.info("")
        else:
            logger.info("")
            logger.info("=" * 80)
            logger.info("❌ FAILED")
            logger.info("=" * 80)
            logger.info("")
            logger.info("Please create manually:")
            logger.info(f"   {Path(mount_path) / 'Logs' / 'RPCTracer'}")
            logger.info("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Use provided mount path
        mount_path = sys.argv[1]
        logger = get_logger("CreateRPCTracerExistingMount")
        logger.info(f"Using provided mount path: {mount_path}")
        if create_rpc_tracer_directory(mount_path):
            target = Path(mount_path) / "Logs" / "RPCTracer"
            logger.info(f"✅ Created: {target}")
            logger.info(f"Configure in Cursor: {target}")
        else:
            logger.error("Failed to create directory")
    else:

        main()