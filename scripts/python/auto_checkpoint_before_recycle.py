#!/usr/bin/env python3
"""
AUTO CHECKPOINT BEFORE RECYCLE

Automatically creates memory checkpoints before Cursor IDE warm recycle
to prevent AI memory drift. This should be run automatically on IDE startup
and before any recycle operation.
"""

import sys
from pathlib import Path

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from prevent_memory_drift import MemoryDriftPreventer

def main():
    """Auto-checkpoint before recycle"""
    preventer = MemoryDriftPreventer()

    # Always create checkpoint before any recycle
    checkpoint_file = preventer.create_checkpoint_before_recycle()

    print(f"\n✅ Memory checkpoint created: {checkpoint_file}")
    print("🛡️  Memory drift protection active")

    return 0

if __name__ == "__main__":



    sys.exit(main())