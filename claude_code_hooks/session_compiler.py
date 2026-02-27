#!/usr/bin/env python3
"""
Stop Hook: Session Memory Compiler

On session end, compiles all memory files from ~/.claude/projects/*/memory/
into a single optimized JSON blob and saves it as a session baton for
instant context recovery on next startup.

Baton location: ~/.claude/session_batons/
Install: Register as Stop hook.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MEMORY_BASE = Path.home() / ".claude" / "projects"
BATON_DIR = Path.home() / ".claude" / "session_batons"
MAX_BATONS = 10

# Standard memory files to compile (ordered by importance)
MEMORY_FILES = [
    "MEMORY.md",
]


def find_memory_dirs() -> list[Path]:
    """Find all project memory directories."""
    dirs = []
    if not MEMORY_BASE.exists():
        return dirs
    for project_dir in MEMORY_BASE.iterdir():
        if not project_dir.is_dir():
            continue
        memory_dir = project_dir / "memory"
        if memory_dir.exists() and (memory_dir / "MEMORY.md").exists():
            dirs.append(memory_dir)
    return dirs


def compile_memory(memory_dirs: list[Path]) -> dict:
    """Read all memory files and compile into a single structure."""
    compiled = {
        "compiled_at": datetime.now(timezone.utc).isoformat(),
        "projects": {},
        "total_chars": 0,
        "total_files": 0,
    }

    for memory_dir in memory_dirs:
        project_name = memory_dir.parent.name
        project_files = {}

        # Read all .md files in the memory directory
        for md_file in sorted(memory_dir.glob("*.md")):
            try:
                content = md_file.read_text(errors="replace")
                project_files[md_file.name] = content
                compiled["total_chars"] += len(content)
                compiled["total_files"] += 1
            except OSError:
                continue

        if project_files:
            compiled["projects"][project_name] = {
                "path": str(memory_dir),
                "files": project_files,
            }

    return compiled


def write_baton(compiled: dict) -> Path | None:
    """Write session baton to filesystem."""
    try:
        BATON_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        filename = f"baton_{now.strftime('%Y%m%d_%H%M%S')}.json"
        baton_path = BATON_DIR / filename

        baton = {
            "session_end": now.isoformat(),
            "total_files": compiled["total_files"],
            "total_chars": compiled["total_chars"],
            "projects": list(compiled["projects"].keys()),
            "compiled": compiled,
        }

        with open(baton_path, "w") as f:
            json.dump(baton, f, indent=2)

        # Prune old batons
        batons = sorted(BATON_DIR.glob("baton_*.json"), reverse=True)
        for old in batons[MAX_BATONS:]:
            old.unlink(missing_ok=True)

        return baton_path
    except OSError:
        return None


def main():
    try:
        memory_dirs = find_memory_dirs()
        if not memory_dirs:
            sys.exit(0)

        compiled = compile_memory(memory_dirs)
        if compiled["total_files"] == 0:
            sys.exit(0)

        baton_path = write_baton(compiled)
        if baton_path:
            print(json.dumps({
                "systemMessage": (
                    f"Session compiled: {compiled['total_files']} memory files, "
                    f"{compiled['total_chars']} chars, saved to {baton_path.name}"
                )
            }))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
