#!/usr/bin/env python3
"""
Fail if any file in the repo contains vsce publish or npx vsce publish.

#automation: Run from repo root: python scripts/python/check_no_lumina_publish_scripts.py
Use in CI or pre-commit to ensure no script ever adds marketplace publish for Lumina.

See docs/system/LUMINA_EXTENSION_NEVER_PUBLISH_WHY.md
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = ("vsce publish", "npx vsce publish")
EXTENSIONS = (".py", ".ps1", ".sh", ".bat", ".yml", ".yaml", ".json", ".md")
EXCLUDE_DIRS = {"node_modules", ".git", "__pycache__", "out", "dist", ".venv", "venv"}


def main() -> int:
    hits = []
    for path in REPO_ROOT.rglob("*"):
        if path.is_dir() and path.name in EXCLUDE_DIRS:
            continue
        if path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for bad in FORBIDDEN:
                if bad in text:
                    # Allow docs that say "do not run vsce publish"
                    if path.suffix.lower() == ".md" and ("do not" in text.lower() or "unpublish" in path.name or "FORBIDDEN" in text):
                        continue
                    rel = path.relative_to(REPO_ROOT)
                    hits.append((str(rel), bad))
                    break
        except Exception:
            continue

    if hits:
        print("FORBIDDEN: The following files contain 'vsce publish' or 'npx vsce publish'. Remove or change to unpublish/package only.", file=sys.stderr)
        for rel, bad in hits:
            print(f"  {rel}: contains '{bad}'", file=sys.stderr)
        return 1
    print("OK: No vsce publish / npx vsce publish found in repo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
