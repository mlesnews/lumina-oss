#!/usr/bin/env python3
"""
Specialized @BDA (Build, Deploy, Activate) script for NAS Migration and PXE Boot.
Derived from: c:\\Users\\mlesn\\.cursor\\plans\\nas_migration_pxe_boot_e883aa72.plan.md
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("execute_nas_migration_bda")


# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from doit_bda_final_step import DOITBDAFinalStep
except ImportError:
    print("Error: Could not import DOITBDAFinalStep. Ensure scripts/python/ is in your path.")
    sys.exit(1)

def main():
    try:
        bda = DOITBDAFinalStep()

        # 1. BUILD PHASE: Analysis and Preparation
        build_commands = [
            # Check current disk usage (Windows)
            "powershell -Command \"Get-PSDrive C | Select-Object Used, Free, @{Name='UsedGB';Expression={$_.Used/1GB}}, @{Name='FreeGB';Expression={$_.Free/1GB}}\"",
            # Find large files in AppData (common space hogs)
            "powershell -Command \"Get-ChildItem -Path $env:LOCALAPPDATA -Recurse -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10 FullName, @{Name='SizeGB';Expression={$_.Length/1GB}}\"",
            # Verify NAS connectivity
            "ping <NAS_PRIMARY_IP> -n 1"
        ]

        # 2. DEPLOY PHASE: Moving data and setting up shares
        # Note: These are simulated or setup-oriented since we can't move 3TB in one go
        deploy_commands = [
            # Check if NAS share is already mounted or accessible
            "powershell -Command \"Test-Path \\\\<NAS_PRIMARY_IP>\\homes\"",
            # Prepare Ollama models directory on NAS (placeholder)
            "powershell -Command \"if (!(Test-Path \\\\<NAS_PRIMARY_IP>\\data\\models\\ollama)) { echo 'Warning: NAS path not found. Manual share creation required.' }\"",
            # Backup Cursor models config before any migration
            "powershell -Command \"Copy-Item data\\cursor_models\\cursor_models_config.json data\\cursor_models\\cursor_models_config.json.bak -Force\""
        ]

        # 3. ACTIVATE PHASE: Environment and Service Activation
        activate_commands = [
            # Set environment variables for relocation (Simulated/User check)
            "echo 'Activation step: Set OLLAMA_MODELS=\\\\<NAS_PRIMARY_IP>\\data\\models\\ollama'",
            # Verify the new fix for local AI is still intact
            "python scripts/python/check_cursor_local_ai.py",
            # Check PXE prerequisites on NAS (via SSH ping or similar if possible)
            "echo 'Activation step: Verify Synology TFTP service status at <NAS_PRIMARY_IP>'"
        ]

        workflow_id = "nas_migration_pxe_boot_e883aa72"

        print("\n" + "=" * 80)
        print(f"🚀 @BDA EXECUTION: {workflow_id}")
        print("=" * 80)

        result = bda.execute_bda(
            workflow_id=workflow_id,
            workflow_type="nas_migration",
            build_commands=build_commands,
            deploy_commands=deploy_commands,
            activate_commands=activate_commands,
            metadata={
                "plan_file": "c:\\Users\\mlesn\\.cursor\\plans\\nas_migration_pxe_boot_e883aa72.plan.md",
                "target_nas": "<NAS_PRIMARY_IP>",
                "disk_relief_target": "200GB+"
            }
        )

        print("\n" + "=" * 80)
        print("BDA EXECUTION SUMMARY")
        print("-" * 80)
        print(f"Workflow: {result.workflow_id}")
        print(f"Overall:  {result.overall_status.upper()}")
        print(f"Duration: {result.duration_seconds:.1f}s")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()