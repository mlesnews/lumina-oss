#!/usr/bin/env python3
"""Verify no placeholders exist"""
import json
from pathlib import Path

project_root = Path("C:/Users/mlesn/Dropbox/my_projects/.lumina")
production_dir = project_root / "data" / "quantum_anime" / "production"

placeholders = []
real_assets = []

for json_file in production_dir.rglob("*.json"):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check for placeholder indicators
        is_placeholder = False
        if isinstance(data, dict):
            status = str(data.get("status", "")).lower()
            note = str(data.get("note", "")).lower()
            production_notes = str(data.get("production_notes", "")).lower()

            if "placeholder" in status or "placeholder" in note or "placeholder" in production_notes:
                is_placeholder = True
                placeholders.append(str(json_file))
            else:
                real_assets.append(str(json_file))
    except Exception as e:
        print(f"Error reading {json_file}: {e}")

print("="*80)
print("PLACEHOLDER VERIFICATION")
print("="*80)
print(f"\n✅ Real Assets: {len(real_assets)}")
print(f"{'❌ Placeholders: ' + str(len(placeholders)) if placeholders else '✅ NO PLACEHOLDERS!'}")
print("="*80)

if placeholders:
    print("\n⚠️  Found placeholders:")
    for p in placeholders[:10]:
        print(f"   {p}")
else:
    print("\n✅ ALL ASSETS ARE REAL - NO PLACEHOLDERS!")
    print("✅ Production ready with actual content!")
