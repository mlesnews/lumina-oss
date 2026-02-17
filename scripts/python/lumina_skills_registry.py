#!/usr/bin/env python3
"""
Lumina skills registry — discover, list, and gate skills (ClawHub-style).

Discovers skills from .cursor/skills/*/SKILL.md; lists them; optional install/gate
(install = ensure present; gate = check allowlist before use).

Usage:
  python scripts/python/lumina_skills_registry.py list [--json]
  python scripts/python/lumina_skills_registry.py discover [--json]
  python scripts/python/lumina_skills_registry.py check <skill_id>

Tags: #skills_registry #OpenClaw #ClawHub @PEAK
See: config/lumina_skills_registry.json, docs/system/OPENCLAW_UNIQUE_FEATURES_AND_LUMINA_FIT.md
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def get_skills_root(project_root: Path) -> Path:
    return project_root / ".cursor" / "skills"


def discover_skills(project_root: Path) -> List[Dict[str, Any]]:
    """Discover skills from .cursor/skills/*/SKILL.md."""
    root = get_skills_root(project_root)
    result: List[Dict[str, Any]] = []
    if not root.exists():
        return result
    for d in root.iterdir():
        if d.is_dir():
            skill_md = d / "SKILL.md"
            entry: Dict[str, Any] = {
                "skill_id": d.name,
                "path": str(d.relative_to(project_root)),
                "installed": skill_md.exists(),
            }
            if skill_md.exists():
                try:
                    text = skill_md.read_text(encoding="utf-8")
                    first_line = text.strip().split("\n")[0] if text else ""
                    if first_line.startswith("#"):
                        entry["description"] = first_line.lstrip("#").strip()
                    else:
                        entry["description"] = text[:200].strip()
                except (OSError, UnicodeDecodeError):
                    entry["description"] = "(read error)"
            else:
                entry["description"] = "(no SKILL.md)"
            result.append(entry)
    return result


def list_cmd(project_root: Path, as_json: bool) -> int:
    skills = discover_skills(project_root)
    if as_json:
        print(json.dumps(skills, indent=2, ensure_ascii=False))
    else:
        for s in skills:
            print(f"  {s['skill_id']}: {s.get('description', '')[:60]}")
    return 0


def check_cmd(project_root: Path, skill_id: str) -> int:
    root = get_skills_root(project_root)
    skill_dir = root / skill_id
    skill_md = skill_dir / "SKILL.md"
    if not skill_dir.exists():
        print(f"Skill not found: {skill_id}", file=sys.stderr)
        return 1
    if not skill_md.exists():
        print(f"SKILL.md missing: {skill_dir}", file=sys.stderr)
        return 1
    print(f"OK: {skill_id} ({skill_md})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lumina skills registry: list, discover, check.")
    parser.add_argument("command", choices=["list", "discover", "check"], help="Command")
    parser.add_argument("args", nargs="*", help="Arguments (e.g. skill_id for check)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="Project root")
    args = parser.parse_args()

    root = args.project_root
    if args.command in ("list", "discover"):
        return list_cmd(root, as_json=args.json)
    if args.command == "check":
        skill_id = args.args[0] if args.args else ""
        if not skill_id:
            print("Error: check requires skill_id", file=sys.stderr)
            return 1
        return check_cmd(root, skill_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
