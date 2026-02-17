#!/usr/bin/env python3
"""
LUMINA NAS YouTube Storage - Autonomous Setup

Automatically sets up NAS storage for LUMINA YouTube content:
1. Connect to NAS via API
2. Create LUMINA-YT share/folder structure
3. Map network drive
4. Create all storage directories
5. Verify setup
"""

import sys
from pathlib import Path
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaNASYTSetupAutonomous")

from lumina_nas_yt_storage import LuminaNASYTStorage, StorageType
from nas_azure_vault_integration import NASAzureVaultIntegration
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def autonomous_setup():
    """Autonomously set up NAS storage for LUMINA YouTube content"""

    print("\n" + "="*80)
    print("🤖 LUMINA NAS YouTube Storage - Autonomous Setup")
    print("="*80 + "\n")

    # Step 1: Initialize storage system
    print("Step 1: Initializing storage system...")
    storage = LuminaNASYTStorage()
    logger.info("✅ Storage system initialized")

    # Step 2: Connect to NAS via API and create folder structure
    print("\nStep 2: Connecting to NAS and creating folder structure...")
    try:
        vault = NASAzureVaultIntegration()
        credentials = vault.get_nas_credentials()

        if credentials:
            logger.info("✅ NAS credentials retrieved from Azure Key Vault")

            # Try to connect and create folders via NAS API
            try:
                if vault.connect_to_nas():
                    logger.info("✅ Connected to NAS via API")

                    # Create base folder structure
                    base_path = f"/LUMINA-YT"
                    logger.info(f"Creating base folder: {base_path}")
                    vault.create_folder(base_path)

                    # Create all subdirectories
                    storage_types = [
                        ("trailers", StorageType.TRAILERS),
                        ("episodes", StorageType.EPISODES),
                        ("raw_footage", StorageType.RAW_FOOTAGE),
                        ("edited_content", StorageType.EDITED_CONTENT),
                        ("eighties_segments", StorageType.EIGHTIES_SEGMENTS),
                        ("thumbnails", StorageType.THUMBNAILS),
                        ("assets", StorageType.ASSETS),
                        ("archive", StorageType.ARCHIVE)
                    ]

                    for folder_name, storage_type in storage_types:
                        folder_path = f"{base_path}/{folder_name}"
                        logger.info(f"Creating folder: {folder_path}")
                        vault.create_folder(folder_path)

                    logger.info("✅ All folders created on NAS")
                    vault.disconnect()
                else:
                    logger.warning("⚠️  Could not connect to NAS via API - will try network drive mapping")
            except Exception as e:
                logger.warning(f"⚠️  NAS API operation failed: {e} - continuing with drive mapping")
        else:
            logger.warning("⚠️  Could not retrieve NAS credentials - will try manual mapping")
    except Exception as e:
        logger.warning(f"⚠️  NAS API setup failed: {e} - continuing with drive mapping")

    # Step 3: Map network drive
    print("\nStep 3: Mapping network drive...")
    is_mapped = storage.check_drive_mapped()

    if not is_mapped:
        logger.info("Network drive not mapped - attempting to map...")
        success = storage.map_network_drive()
        if success:
            logger.info("✅ Network drive mapped successfully")
        else:
            logger.warning("⚠️  Network drive mapping failed - may require manual mapping")
            logger.info("   Manual command: net use Y: \\\\<NAS_PRIMARY_IP>\\LUMINA-YT /user:backupadm <password> /persistent:yes")
    else:
        logger.info("✅ Network drive already mapped")

    # Step 4: Ensure storage directories exist
    print("\nStep 4: Ensuring storage directories exist...")
    try:
        storage.ensure_storage_paths()
        logger.info("✅ Storage directories verified/created")
    except Exception as e:
        logger.warning(f"⚠️  Directory creation failed: {e}")
        logger.info("   This may require the NAS share to exist first")

    # Step 5: Verify setup
    print("\nStep 5: Verifying setup...")
    summary = storage.get_config_summary()

    print("\n" + "="*80)
    print("📊 Setup Summary")
    print("="*80)
    print(f"NAS IP: {summary['nas_ip']}")
    print(f"Share: {summary['share_name']}")
    print(f"Mount Point: {summary['mount_point']}")
    print(f"Status: {'✅ Mapped' if summary['is_mapped'] else '❌ Not Mapped'}")

    print("\nStorage Paths:")
    for storage_type, path in summary['storage_paths'].items():
        print(f"  {storage_type:20s}: {path}")

    # Final status
    print("\n" + "="*80)
    if summary['is_mapped']:
        print("✅ AUTONOMOUS SETUP COMPLETE")
        print("   Network drive mapped and ready")
        print("   Storage directories configured")
    else:
        print("⚠️  SETUP PARTIALLY COMPLETE")
        print("   Configuration ready, but network drive needs mapping")
        print("   Run: python scripts/python/lumina_nas_yt_storage.py --map")
    print("="*80 + "\n")

    return summary


if __name__ == "__main__":
    autonomous_setup()

