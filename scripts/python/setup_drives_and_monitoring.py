#!/usr/bin/env python3
"""
Setup Drives and Visual Monitoring

Sets up drive mappings and visual monitoring system.
Maps all drives (M, P, U, V, D) and configures screen capture.

Tags: #SETUP #DRIVE_MAPPING #VISUAL_MONITORING @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from drive_mapping_system import DriveMappingSystem
    from lumina_logger import get_logger
    from visual_monitoring_system import VisualMonitoringSystem
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("SetupDrivesMonitoring")


def main():
    """Setup drives and monitoring"""
    print("=" * 80)
    print("🔧 SETTING UP DRIVES AND VISUAL MONITORING")
    print("=" * 80)
    print()

    # Setup drive mappings
    print("1. Setting up drive mappings...")
    drive_system = DriveMappingSystem()

    print("   Drive Mappings:")
    for letter, mapping in drive_system.drive_mappings.items():
        print(f"     {letter}: {mapping.network_path} - {mapping.description}")
    print()

    # Attempt to map drives (may require admin privileges)
    print("2. Attempting to map drives...")
    print("   Note: Drive mapping requires network access and may need admin privileges")
    mapping_results = drive_system.map_all_drives(persistent=True)

    mapped_count = sum(1 for result in mapping_results.values() if result)
    print(f"   ✅ Mapped: {mapped_count}/{len(mapping_results)} drives")
    print()

    # Check drive status
    print("3. Checking drive status...")
    status = drive_system.get_drive_status()
    for letter, info in status["mappings"].items():
        status_icon = "✅" if info["mapped"] else "❌"
        print(f"   {status_icon} {letter}: {info['network_path']} - {info['purpose']}")
    print()

    # Setup visual monitoring
    print("4. Setting up visual monitoring system...")
    monitoring = VisualMonitoringSystem()

    monitoring_status = monitoring.get_monitoring_status()
    print("   ✅ Visual monitoring system ready")
    print(f"   📹 Video storage: {monitoring_status['storage_info']['storage_path']}")
    print(f"   📁 Storage type: {monitoring_status['storage_info']['storage_type']}")
    print()

    # Summary
    print("=" * 80)
    print("📊 SETUP SUMMARY")
    print("=" * 80)
    print()
    print("Drive Mappings:")
    print(f"  • M: Models - {status['mappings']['M']['mapped']}")
    print(f"  • P: Pictures - {status['mappings']['P']['mapped']}")
    print(f"  • U: Public - {status['mappings']['U']['mapped']}")
    print(f"  • V: Video (NAS) - {status['mappings']['V']['mapped']}")
    print(f"  • D: Downloads - {status['mappings']['D']['mapped']}")
    print()
    print("Visual Monitoring:")
    print("  • System: Ready")
    print("  • Storage: NAS (V: drive)")
    print("  • Status: Configured")
    print()
    print("=" * 80)
    print("✅ SETUP COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Ensure NAS is accessible")
    print("  2. Map drives manually if needed (may require admin)")
    print("  3. Install screen capture libraries:")
    print("     pip install mss pillow opencv-python pytesseract")
    print("  4. Start visual monitoring when ready")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()