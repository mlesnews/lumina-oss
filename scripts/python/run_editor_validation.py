#!/usr/bin/env python3
"""
Run editor validation (Ruff + Mypy) on a manifest of Python files.

#automation

Single entry point for the "V3" workflow: fix underlying problems only (no
suppressions). Runs Ruff check, then Mypy with --follow-imports=skip. Optional
Ruff --fix and optional markdownlint. Exit 0 only if all steps pass.

Usage (from repo root):
  python scripts/python/run_editor_validation.py
  python scripts/python/run_editor_validation.py --fix
  python scripts/python/run_editor_validation.py --manifest config/other_manifest.txt

See docs/system/EDITOR_VALIDATION_NOTES.md and .cursor/rules/fix_underlying_problem.mdc.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    # Script at scripts/python/run_editor_validation.py -> parent.parent.parent = repo root
    root = Path(__file__).resolve().parent.parent.parent
    return root


def _load_manifest(manifest_path: Path, root: Path) -> list[Path]:
    paths: list[Path] = []
    if not manifest_path.is_file():
        return paths
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = (root / line).resolve()
        if p.is_file():
            paths.append(p)
    return paths


def _run(cmd: list[str], cwd: Path, step_name: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        out = (result.stdout or "").strip() + "\n" + (result.stderr or "").strip()
        return result.returncode == 0, out
    except FileNotFoundError:
        return False, f"{step_name}: command not found (install required tool)"


def main() -> int:
    root = _repo_root()
    default_manifest = root / "config" / "editor_validation_manifest.txt"

    parser = argparse.ArgumentParser(
        description="Run Ruff + Mypy on manifest of Python files (editor V3 workflow)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest,
        help="Path to manifest file (one path per line, relative to repo root)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Run Ruff with --fix (auto-fix safe issues); default is check-only",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Also run markdownlint on docs (if markdownlint is available)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print summary; hide tool output unless failed",
    )
    args = parser.parse_args()

    paths = _load_manifest(args.manifest.resolve(), root)
    if not paths:
        print("No files in manifest or manifest missing:", args.manifest, file=sys.stderr)
        return 1

    # Paths for subprocess: pass relative to cwd for cleaner output
    rel_paths = [str(p.relative_to(root)) for p in paths]
    all_ok = True

    # 1) Ruff
    ruff_cmd = ["python", "-m", "ruff", "check"] + rel_paths
    if args.fix:
        ruff_cmd.insert(3, "--fix")
    ok, out = _run(ruff_cmd, root, "Ruff")
    if not ok:
        all_ok = False
        print("Ruff failed:")
        print(out)
    elif not args.quiet:
        print("Ruff: OK")

    # 2) Mypy (script-only)
    mypy_cmd = [
        "python", "-m", "mypy",
        "--follow-imports=skip",
    ] + rel_paths
    ok, out = _run(mypy_cmd, root, "Mypy")
    if not ok:
        all_ok = False
        print("Mypy failed:")
        print(out)
    elif not args.quiet:
        print("Mypy: OK")

    # 3) Optional markdownlint
    if args.markdown:
        md_cmd = ["markdownlint", "-c", ".markdownlint.json", "-f", "docs/**/*.md"]
        ok, out = _run(md_cmd, root, "Markdownlint")
        if not ok:
            all_ok = False
            print("Markdownlint failed:")
            print(out)
        elif not args.quiet:
            print("Markdownlint: OK")

    if all_ok:
        print("Editor validation passed (Ruff + Mypy).")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
