#!/usr/bin/env python3
"""
Setup NAS Video Storage - Initialize V: Drive for Quantum Anime Videos

Sets up the V: drive mapping and creates necessary directory structure
for quantum anime video production.

Tags: #NAS #VIDEO #SETUP @LUMINA @JARVIS
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from map_nas_video_drive import NASVideoDriveMapper

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupNASVideoStorage")


def setup_video_storage():
    """Setup NAS video storage structure"""
    print("="*80)
    print("SETUP NAS VIDEO STORAGE")
    print("="*80)

    # Map V: drive
    mapper = NASVideoDriveMapper()

    # Check if drive is mapped
    info = mapper.get_drive_info()

    if not info['mapped'] or not info['accessible']:
        print("\n🗺️  Mapping V: drive...")
        share_path = mapper.find_video_share()

        if not share_path:
            # Use backups share as fallback
            share_path = f"\\\\{mapper.nas_ip}\\backups"

        if mapper.map_drive(share_path):
            print("   ✅ V: drive mapped successfully")
        else:
            print("   ❌ Failed to map V: drive")
            print("   💡 Run: python map_nas_video_drive.py [share_path]")
            return False
    else:
        print(f"\n✅ V: drive already mapped: {info['path']}")

    # Create directory structure
    print("\n📁 Creating directory structure...")

    v_drive = Path("V:\\")

    directories = [
        "quantum_anime",
        "quantum_anime/videos",
        "quantum_anime/renders",
        "quantum_anime/animations",
        "quantum_anime/trailers",
        "quantum_anime/episodes"
    ]

    for dir_path in directories:
        full_path = v_drive / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {full_path}")
        except Exception as e:
            print(f"   ⚠️  Could not create {full_path}: {e}")

    print("\n✅ NAS video storage setup complete!")
    print(f"   📁 Videos: V:\\quantum_anime\\videos")
    print(f"   📁 Renders: V:\\quantum_anime\\renders")
    print(f"   📁 Animations: V:\\quantum_anime\\animations")
    print("="*80)

    return True


if __name__ == "__main__":
    setup_video_storage()
