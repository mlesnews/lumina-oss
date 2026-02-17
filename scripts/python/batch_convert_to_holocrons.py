#!/usr/bin/env python3
"""
BATCH CONVERT MONSTER FILES TO HOLOCRONS
Converts all large JSON files in data directories to queryable Holocrons
"""

import sys
from pathlib import Path
from json_to_holocron import HolocronConverter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def find_large_json_files(min_size_mb: int = 50) -> list:
    """Find all JSON files larger than threshold."""
    large_files = []

    # Directories to search
    search_dirs = [
        DATA_DIR / "syphon_lumina_hourly",
        DATA_DIR / "lumina_syphon",
        DATA_DIR / "ask_cache",
        DATA_DIR / "intelligence",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        for json_file in search_dir.rglob("*.json"):
            try:
                size_mb = json_file.stat().st_size / (1024 * 1024)
                if size_mb > min_size_mb:
                    large_files.append((json_file, size_mb))
            except:
                pass

    return sorted(large_files, key=lambda x: x[1], reverse=True)

def main():
    print("🔥 BATCH HOLOCRON CONVERSION 🔥")
    print("=" * 60)

    converter = HolocronConverter()

    # Find large JSON files
    print("\n🔍 Scanning for large JSON files...")
    large_files = find_large_json_files(min_size_mb=50)

    if not large_files:
        print("   ✅ No large JSON files found to convert")
        return

    print(f"   Found {len(large_files)} files to convert")
    print("\n📋 Files to convert:")
    for i, (file_path, size_mb) in enumerate(large_files[:20], 1):  # Show top 20
        rel_path = file_path.relative_to(PROJECT_ROOT)
        print(f"   {i}. {rel_path} ({size_mb:.2f} MB)")

    if len(large_files) > 20:
        print(f"   ... and {len(large_files) - 20} more files")

    # Confirm
    response = input(f"\n❓ Convert {len(large_files)} files to Holocrons? (yes/no): ")
    if response.lower() not in ('yes', 'y'):
        print("   Cancelled.")
        return

    # Convert
    print("\n📦 Converting files...")
    converted = 0
    failed = 0

    for file_path, size_mb in large_files:
        try:
            holocron_path = converter.convert_json_to_holocron(file_path)
            if holocron_path:
                converted += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Failed to convert {file_path.name}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("📈 CONVERSION COMPLETE:")
    print("=" * 60)
    print(f"   ✅ Converted: {converted}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📦 Holocrons location: {converter.output_dir}")
    print("=" * 60)
    print("\n💡 Query your Holocrons with:")
    print("   python scripts/python/query_holocron.py <holocron.db> --list-tables")

if __name__ == "__main__":


    main()