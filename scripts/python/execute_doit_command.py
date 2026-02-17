#!/usr/bin/env python3
"""
Execute @DOIT Command
Reads and complies with /DOIT +COMMAND
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("execute_doit_command")


project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from doit_enhanced import DOITEnhanced
    DOIT_AVAILABLE = True
except ImportError:
    DOIT_AVAILABLE = False
    print("❌ DOIT Enhanced not available")

def execute_doit_command(command: str, context: dict = None):
    try:
        """Execute @DOIT command"""
        if not DOIT_AVAILABLE:
            print("❌ DOIT system not available")
            return None

        print("=" * 80)
        print("🚀 @DOIT COMMAND EXECUTION - ORDER 66")
        print("=" * 80)
        print(f"Command: {command}")
        print()

        doit = DOITEnhanced(project_root)
        result = doit.doit(
            task_description=command,
            context=context or {},
            auto_5w1h=True,
            auto_root_cause=True,
            execute=True
        )

        # Save result
        data_dir = project_root / "data" / "doit_enhanced"
        data_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = data_dir / f"doit_{timestamp}.json"

        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        print()
        print(f"✅ DOIT execution complete")
        print(f"   Result saved: {result_file}")
        print()

        return result

    except Exception as e:
        logger.error(f"Error in execute_doit_command: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Check for @DOIT in recent context
        command = "Configure Cursor IDE models properly with localOnly, skipProviderSelection, requiresApiKey"
        context = {
            "task": "Cursor IDE model configuration",
            "completed": True,
            "files_created": [
                "scripts/python/configure_cursor_models_properly.py",
                "docs/system/CURSOR_IDE_MODEL_CONFIGURATION.md",
                "scripts/startup/CONFIGURE_CURSOR_MODELS.ps1"
            ]
        }
    else:
        command = sys.argv[1]
        context = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    result = execute_doit_command(command, context)

    if result:
        print("=" * 80)
        print("✅ @DOIT EXECUTION COMPLETE")
        print("=" * 80)
        sys.exit(0)
    else:
        sys.exit(1)
