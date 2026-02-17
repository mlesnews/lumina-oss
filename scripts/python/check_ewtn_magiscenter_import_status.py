#!/usr/bin/env python3
"""
Check EWTN & Magis Center Import Status
Shows what has been imported and what's missing

@SYPHON @EWTN @MAGISCENTER @ACCESSIBILITY
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
import logging
logger = logging.getLogger("check_ewtn_magiscenter_import_status")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

def check_import_status():
    try:
        """Check what has been imported"""
        status_file = project_root / "data" / "ewtn_magiscenter" / "import_status.json"
        r5_dir = project_root / "data" / "r5_living_matrix" / "sessions"

        print("=" * 80)
        print("📊 EWTN & Magis Center Import Status")
        print("=" * 80)
        print("\n🎯 Purpose: For Father Spiter (legally blind) & all with disabilities/aging challenges")
        print("")

        # Check status file
        if status_file.exists():
            with open(status_file, 'r') as f:
                status = json.load(f)

            print("📋 Import Status from File:")
            for source_id, source_status in status.items():
                if source_status.get("imported"):
                    print(f"   ✅ {source_id}: {source_status.get('items_count', 0)} items imported")
                    print(f"      Imported at: {source_status.get('imported_at', 'Unknown')}")
                else:
                    print(f"   ❌ {source_id}: NOT IMPORTED")
        else:
            print("   ⚠️  No import status file found - nothing imported yet")

        # Check R5 sessions
        print("\n📚 R5 Sessions (Content Available):")
        if r5_dir.exists():
            sessions = list(r5_dir.glob("*.json"))
            ewtn_sessions = [s for s in sessions if 'ewtn' in s.name.lower() or 'magis' in s.name.lower() or 'spiter' in s.name.lower() or 'spitzer' in s.name.lower()]

            if ewtn_sessions:
                print(f"   ✅ Found {len(ewtn_sessions)} EWTN/Magis Center sessions in R5")
                for session in ewtn_sessions[:10]:  # Show first 10
                    print(f"      - {session.name}")
                if len(ewtn_sessions) > 10:
                    print(f"      ... and {len(ewtn_sessions) - 10} more")
            else:
                print("   ❌ No EWTN/Magis Center sessions found in R5")
        else:
            print("   ⚠️  R5 directory not found")

        # Sources that should be imported
        print("\n📋 Sources to Import:")
        sources = {
            "EWTN YouTube": "https://www.youtube.com/@EWTN",
            "EWTN Website": "https://www.ewtn.com",
            "Father Spiter's Universe YouTube": "https://www.youtube.com/@FatherSpitzersUniverse",
            "MagiCenter Website": "https://www.magiscenter.com"
        }

        for name, url in sources.items():
            print(f"   📍 {name}: {url}")

        print("\n" + "=" * 80)
        print("💡 To import all sources, run:")
        print("   python scripts/python/import_ewtn_magiscenter_complete.py")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error in check_import_status: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    check_import_status()
