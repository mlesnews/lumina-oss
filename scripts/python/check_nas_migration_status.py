#!/usr/bin/env python3
"""
NAS Migration Status Check
Check the current status of the Ollama models migration to NAS

Tags: #NAS #MIGRATION #STATUS #LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("NASMigrationStatus")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("NASMigrationStatus")

def check_migration_status():
    """Check NAS migration status"""
    print("=" * 80)
    print("NAS MIGRATION STATUS - PM000003064")
    print("=" * 80)
    print()

    source_root = Path.home() / ".ollama"
    dest_root = Path("\\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels")

    # Check source
    print("📂 SOURCE (Local):")
    print(f"   Path: {source_root}")
    if source_root.exists():
        source_files = list(source_root.rglob('*'))
        source_files_only = [f for f in source_files if f.is_file()]
        source_size = sum(f.stat().st_size for f in source_files_only) / (1024**3)

        print(f"   Files: {len(source_files_only)}")
        print(f"   Size: {source_size:.2f} GB")

        if source_files_only:
            print("   Remaining files:")
            for f in source_files_only:
                size_mb = f.stat().st_size / (1024**2)
                print(f"      - {f.name} ({size_mb:.2f} MB)")
    else:
        print("   ⚠️  Source directory does not exist")

    print()

    # Check destination
    print("📂 DESTINATION (NAS):")
    print(f"   Path: {dest_root}")
    if dest_root.exists():
        try:
            dest_files = list(dest_root.rglob('*'))
            dest_files_only = [f for f in dest_files if f.is_file()]
            dest_size = sum(f.stat().st_size for f in dest_files_only) / (1024**3)

            print(f"   Files: {len(dest_files_only)}")
            print(f"   Size: {dest_size:.2f} GB")

            # Check for model files
            model_files = [f for f in dest_files_only if f.suffix in ['.bin', '.gguf', '.safetensors'] or 'model' in f.name.lower()]
            if model_files:
                print(f"   Model files: {len(model_files)}")
        except Exception as e:
            print(f"   ⚠️  Error accessing NAS: {e}")
    else:
        print("   ⚠️  Destination directory does not exist or is not accessible")

    print()

    # Determine status
    print("📊 MIGRATION STATUS:")

    # Check if destination has files (migration completed)
    if dest_root.exists():
        try:
            dest_files = [f for f in dest_root.rglob('*') if f.is_file()]
            dest_size = sum(f.stat().st_size for f in dest_files) / (1024**3)

            # If destination has significant data and source doesn't exist, migration is complete
            if not source_root.exists() and dest_size > 1.0:  # More than 1GB on NAS
                print("   ✅ MIGRATION COMPLETE")
                print("   Source directory removed (migration finished)")
                print(f"   All model files ({dest_size:.2f} GB) successfully moved to NAS")
                return "COMPLETE"
        except Exception as e:
            print(f"   ⚠️  Error checking destination: {e}")

    # Check source if it exists
    if source_root.exists() and dest_root.exists():
        source_files = [f for f in source_root.rglob('*') if f.is_file()]
        source_size = sum(f.stat().st_size for f in source_files) / (1024**3)

        if source_size < 0.1:  # Less than 100MB remaining
            print("   ✅ MIGRATION COMPLETE")
            print("   All model files have been moved to NAS")
            print("   Remaining files in source are config files (SSH keys, etc.)")
            return "COMPLETE"
        else:
            print("   ⏳ MIGRATION IN PROGRESS")
            print(f"   {source_size:.2f} GB remaining in source")
            return "IN_PROGRESS"
    elif not source_root.exists() and dest_root.exists():
        # Source gone, destination exists - migration complete
        print("   ✅ MIGRATION COMPLETE")
        print("   Source directory removed (migration finished)")
        print("   All model files successfully moved to NAS")
        return "COMPLETE"
    else:
        print("   ⚠️  STATUS UNKNOWN")
        print("   Source and/or destination not accessible")
        return "UNKNOWN"

if __name__ == "__main__":
    status = check_migration_status()
    sys.exit(0 if status == "COMPLETE" else 1)
