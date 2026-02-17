#!/usr/bin/env python3
"""
JARVIS Tail Compound Log

Opens an external terminal console to tail the compound log file.
Similar to `tail -f` on Linux or `Get-Content -Wait` on PowerShell.

Tags: #TAIL #COMPOUND_LOG #EXTERNAL_TERMINAL #LIVE_MONITORING @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Compound log file path
compound_log = project_root / "data" / "compound_log_health" / "compound.log"

# Create log file if it doesn't exist
compound_log.parent.mkdir(parents=True, exist_ok=True)
compound_log.touch()

# PowerShell script path
ps_script = script_dir / "tail_compound_log.ps1"

# Open new PowerShell window and tail the log
if sys.platform == "win32":
    # Windows: Open new PowerShell window
    powershell_cmd = f'powershell.exe -NoExit -Command "cd \'{project_root}\'; Get-Content -Path \'{compound_log}\' -Wait -Tail 50"'

    # Use start to open in new window
    subprocess.Popen(
        f'start powershell.exe -NoExit -Command "cd \'{project_root}\'; Write-Host \'📋 Tailing Compound Log\' -ForegroundColor Cyan; Write-Host \'File: {compound_log}\' -ForegroundColor White; Write-Host \'Press Ctrl+C to stop\' -ForegroundColor Yellow; Write-Host \'\'; Get-Content -Path \'{compound_log}\' -Wait -Tail 50"',
        shell=True
    )

    print(f"✅ Opened external terminal to tail compound log")
    print(f"📋 Log file: {compound_log}")
    print("")
    print("The terminal window will show live log updates.")
    print("Press Ctrl+C in that window to stop tailing.")
else:
    # Linux/Mac: Use xterm or gnome-terminal
    import shutil

    if shutil.which("gnome-terminal"):
        subprocess.Popen([
            "gnome-terminal", "--", "bash", "-c",
            f"cd '{project_root}' && tail -f '{compound_log}'"
        ])
    elif shutil.which("xterm"):
        subprocess.Popen([
            "xterm", "-e", "bash", "-c",
            f"cd '{project_root}' && tail -f '{compound_log}'"
        ])
    else:
        # Fallback: use current terminal
        print(f"📋 Tailing compound log: {compound_log}")
        print("Press Ctrl+C to stop")
        print("")
        subprocess.run(["tail", "-f", str(compound_log)])
