#!/usr/bin/env python3
"""
Disable Snapshot Creation Processes

Breadcrumb 2: Disable snapshot creation processes
Part of Tape Library Team Prevention Strategies

Based on findings, disables or documents snapshot creation processes
to prevent recursive snapshot creation.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DisableSnapshotCreation")


def create_exclusion_config() -> Dict[str, Any]:
    """Create configuration to exclude snapshot directory from backups"""

    exclusion_config = {
        "timestamp": datetime.now().isoformat(),
        "purpose": "Prevent recursive snapshot creation",
        "exclusions": {
            "time_travel_snapshots": {
                "pattern": "data/time_travel/snapshots/**",
                "description": "Exclude snapshot output directory from all backup/snapshot operations",
                "reason": "Prevents recursive snapshot creation"
            },
            "snapshot_directory": {
                "pattern": "**/time_travel/snapshots/**",
                "description": "Wildcard exclusion for snapshot directories",
                "reason": "Prevents recursion at any level"
            }
        },
        "backup_scripts_to_update": [
            "scripts/nas_backup_syphon.ps1",
            "scripts/python/data_lifecycle_manager.py",
            "scripts/python/validate_and_mirror.py",
            "Any script using Copy-Item, robocopy, or shutil.copytree on data directory"
        ],
        "instructions": {
            "powershell": "Use -Exclude parameter or robocopy /XD to exclude directories",
            "python": "Use shutil.copytree with ignore parameter or manually exclude paths",
            "validation": "Always verify snapshot directory is excluded before running backup operations"
        }
    }

    return exclusion_config


def create_prevention_documentation() -> str:
    """Create documentation for preventing recursive snapshots"""

    doc = """# Prevention of Recursive Snapshot Creation

## Problem
Snapshots that include the snapshot directory itself create infinite recursion, consuming massive amounts of space (1.22 TB in our case).

## Solution: Exclusion Patterns

### PowerShell Scripts
When using `Copy-Item` or `robocopy`, always exclude the snapshot directory:

```powershell
# Using Copy-Item
$excludeDirs = @("time_travel\\snapshots")
Copy-Item -Path $source -Destination $dest -Recurse -Force -Exclude $excludeDirs

# Using robocopy
robocopy $source $dest /MIR /XD "time_travel\\snapshots"
```

### Python Scripts
When using `shutil.copytree`, use ignore parameter:

```python
import shutil

def ignore_snapshots(dirname, filenames):
    if 'snapshots' in dirname and 'time_travel' in dirname:
        return filenames
    return []

shutil.copytree(src, dst, ignore=ignore_snapshots)
```

### Always Verify
Before creating any backup/snapshot:
1. Check if snapshot directory exists in source
2. Verify exclusion patterns are in place
3. Test on small dataset first
4. Monitor output directory size

## Files to Update
- Any script that copies `data` directory
- Any script that creates backups
- Any script that creates snapshots
- Scheduled tasks that perform backups

## Git-Based Snapshots
Use Git/GitLens for snapshots instead of file system copies:
- Commits are snapshots
- Tags are milestones
- No file system space overhead
- No recursion risk

See: `scripts/python/git_time_travel.py`
"""

    return doc


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Disable snapshot creation processes - Create exclusion config"
        )
        parser.add_argument(
            "--output-config",
            type=str,
            default="config/snapshot_exclusion_config.json",
            help="Output exclusion config file"
        )
        parser.add_argument(
            "--output-doc",
            type=str,
            default="docs/system/SNAPSHOT_EXCLUSION_PREVENTION.md",
            help="Output prevention documentation file"
        )

        args = parser.parse_args()

        logger.info("=" * 70)
        logger.info("DISABLING SNAPSHOT CREATION - Creating Exclusion Config")
        logger.info("=" * 70)
        logger.info("")

        # Create exclusion config
        exclusion_config = create_exclusion_config()

        config_path = project_root / args.output_config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(exclusion_config, f, indent=2, ensure_ascii=False)

        logger.info(f"Exclusion config saved to: {config_path}")

        # Create prevention documentation
        prevention_doc = create_prevention_documentation()

        doc_path = project_root / args.output_doc
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(prevention_doc)

        logger.info(f"Prevention documentation saved to: {doc_path}")

        logger.info("")
        logger.info("=" * 70)
        logger.info("PREVENTION CONFIGURATION CREATED")
        logger.info("=" * 70)
        logger.info("Next steps:")
        logger.info("  1. Review exclusion_config.json")
        logger.info("  2. Update backup scripts with exclusion patterns")
        logger.info("  3. Test exclusion patterns on small dataset")
        logger.info("  4. Monitor snapshot directory size")
        logger.info("=" * 70)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())