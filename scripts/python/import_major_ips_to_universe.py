#!/usr/bin/env python3
"""
Import Major IPs to Storytelling Universe - ORDER 66: @DOIT

Imports all major IPs (Star Wars, LoTR, Transformers, BSG, and far too many to list)
into the storytelling universe system.

Tags: #STORYTELLING #IP #IMPORT #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_storytelling_universe_system import LuminaStorytellingUniverse
from storytelling_universe_major_ips import import_major_ips_to_universe, MAJOR_IPS

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ImportMajorIPs")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Import Major IPs to Storytelling Universe - ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t actually import)')

    args = parser.parse_args()

    print("\n📚 Importing Major IPs to Storytelling Universe")
    print("="*80)
    print(f"Total IPs to import: {len(MAJOR_IPS)}")
    print("\nIPs:")
    for ip_id, ip in MAJOR_IPS.items():
        print(f"  • {ip.title}")

    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        return 0

    universe = LuminaStorytellingUniverse(project_root=args.project_root)

    print("\n📥 Importing...")
    result = import_major_ips_to_universe(universe)

    print(f"\n✅ Import Complete:")
    print(f"   Total: {result['total']}")
    print(f"   Successful: {result['successful']}")
    print(f"   Failed: {result['failed']}")

    if result['imported']:
        print(f"\n📥 Imported IPs ({len(result['imported'])}):")
        for ip_id in result['imported'][:10]:  # Show first 10
            print(f"   • {MAJOR_IPS[ip_id].title}")
        if len(result['imported']) > 10:
            print(f"   ... and {len(result['imported']) - 10} more")

    if result['errors']:
        print(f"\n❌ Errors ({len(result['errors'])}):")
        for error in result['errors'][:5]:  # Show first 5
            print(f"   • {error['ip_id']}: {error['error']}")

    return 0


if __name__ == "__main__":


    sys.exit(main())