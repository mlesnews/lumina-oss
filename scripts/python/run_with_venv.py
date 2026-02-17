#!/usr/bin/env python3
"""
Wrapper script to ensure venv is activated before running Python commands
This ensures all AI-executed commands use venv automatically
"""

import sys
import os
import subprocess
from pathlib import Path

def find_venv(project_root: Path) -> Path:
    """Find venv in project root"""
    venv_paths = [
        project_root / "venv",
        project_root / ".venv",
        project_root / "env"
    ]

    for venv_path in venv_paths:
        if venv_path.exists():
            python_exe = venv_path / "Scripts" / "python.exe" if os.name == 'nt' else venv_path / "bin" / "python"
            if python_exe.exists():
                return venv_path

    return None

def get_venv_python(venv_path: Path) -> Path:
    """Get Python executable from venv"""
    if os.name == 'nt':
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def run_with_venv(command: list, project_root: Path = None) -> int:
    """
    Run a command with venv activated

    Args:
        command: Command to run (list of strings)
        project_root: Project root directory (defaults to current directory)

    Returns:
        Exit code
    """
    if project_root is None:
        project_root = Path.cwd()

    # Find venv
    venv_path = find_venv(project_root)

    if venv_path:
        # Use venv Python
        python_exe = get_venv_python(venv_path)
        print(f"🐍 Using venv Python: {python_exe}", file=sys.stderr)

        # Replace 'python' with venv python in command
        cmd = []
        for arg in command:
            if arg == 'python' or arg == 'python.exe':
                cmd.append(str(python_exe))
            else:
                cmd.append(arg)

        # Run command
        return subprocess.run(cmd).returncode
    else:
        # No venv found, run normally
        print(f"⚠️  No venv found in {project_root}. Running without venv.", file=sys.stderr)
        return subprocess.run(command).returncode

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_with_venv.py <command> [args...]")
        sys.exit(1)

    # Get project root (assume .lumina project)
    project_root = Path(__file__).parent.parent.parent

    # Run command with venv
    exit_code = run_with_venv(sys.argv[1:], project_root)
    sys.exit(exit_code)
