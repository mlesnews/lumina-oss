#!/usr/bin/env python3
"""
Log File Monitor - Discovers and monitors all log files
"""

import os
from pathlib import Path
from typing import List
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def discover_all_log_files(project_root: Path) -> List[Path]:
    """Discover all log files in the project"""
    log_files = []

    # Common log file patterns
    patterns = ['*.log', '*.log.txt', '*.err', '*.error', '*.out']

    # Directories to search
    search_dirs = [
        project_root,
        project_root / "logs",
        project_root / "data",
        project_root / "scripts",
    ]

    # Directories to skip
    skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 
                 '.pytest_cache', '.mypy_cache', 'dist', 'build', '.tox'}

    for root_dir in search_dirs:
        if not root_dir.exists():
            continue

        for root, dirs, files in os.walk(root_dir):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]

            for file in files:
                if any(file.endswith(ext.replace('*', '')) for ext in patterns):
                    log_path = Path(root) / file
                    try:
                        # Check if file is readable
                        if log_path.is_file() and log_path.stat().st_size > 0:
                            log_files.append(log_path)
                    except (OSError, PermissionError):
                        continue

    return sorted(set(log_files))


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    log_files = discover_all_log_files(project_root)

    print(f"📋 Discovered {len(log_files)} log files:")
    for log_file in log_files[:20]:  # Show first 20
        print(f"   {log_file.relative_to(project_root)}")

    if len(log_files) > 20:
        print(f"   ... and {len(log_files) - 20} more")
