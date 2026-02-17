#!/usr/bin/env python3
"""
Auto-Fix Local Models on Startup (Prevent Recurring Issues)

This script runs automatically to ensure local models never get subscription errors.
Can be added to startup scripts or run periodically.

Tags: #AUTO_FIX #LOCAL_MODELS #PREVENT_RECURRING #ULTRON #KAIJU
@JARVIS @MARVIN @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import the fix function
from fix_local_models_no_subscription_error import fix_all_local_models

if __name__ == "__main__":
    """Auto-run on import or direct execution"""
    fix_all_local_models(project_root)
