#!/usr/bin/env python3
"""
Priority Import: Father Spiter's Universe
CRITICAL - Father is legally blind, accessibility is essential

Import Father Spiter's Universe YouTube channel with full accessibility features.

@SYPHON @EWTN @FATHERSPITER @ACCESSIBILITY @PRIORITY
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

from import_ewtn_magiscenter_complete import EWTNMagisCenterImporter

def main():
    """Priority import for Father Spiter's Universe"""
    print("=" * 80)
    print("🎯 PRIORITY IMPORT: Father Spiter's Universe")
    print("=" * 80)
    print("")
    print("⚠️  CRITICAL: Father Spiter is legally blind")
    print("   Accessibility features are ESSENTIAL")
    print("   Full transcripts required for all videos")
    print("")
    print("=" * 80)
    print("")

    importer = EWTNMagisCenterImporter()

    # Import Father Spiter's Universe specifically
    result = importer._import_youtube_channel(
        "father_spiter_youtube",
        {
            "name": "Father Spiter's Universe",
            "url": "https://www.youtube.com/@FatherSpitzersUniverse",
            "type": "youtube_channel",
            "description": "Father Spiter's Universe YouTube channel (Father is legally blind - accessibility critical)"
        }
    )

    print("\n" + "=" * 80)
    print("📊 IMPORT RESULT")
    print("=" * 80)
    print(f"Success: {result.get('success', False)}")
    print(f"Videos Imported: {result.get('items_imported', 0)}")
    print(f"Total Videos Found: {result.get('total_videos', 0)}")
    print(f"Transcripts Extracted: {result.get('transcripts_extracted', 0)}")

    if result.get('success'):
        print("\n✅ Father Spiter's Universe imported successfully!")
        print("   All content is now accessible for visually impaired users")
    else:
        print(f"\n❌ Import failed: {result.get('error', 'Unknown error')}")
        print("   Please check error message and retry")

    return 0 if result.get('success') else 1

if __name__ == "__main__":


    sys.exit(main())