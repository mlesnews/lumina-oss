#!/usr/bin/env python3
"""
Lumina onboard — one CLI wizard for "new user" or "new machine".

Steps:
  1. Bones (health check) — config, bindings, keybindings, JARVIS connectivity
  2. Keybindings — apply Cursor keybindings (F23 → @JARVIS, accept-all, etc.)
  3. JARVIS pin — consolidate and pin JARVIS Master Chat session
  4. Router test — verify request_tier_router (JARVIS easy code_generation)
  5. Optional MCP — mention MCP/SSOT setup (no auto-run)

Usage:
  python scripts/python/lumina_onboard.py
  python scripts/python/lumina_onboard.py --yes     # Non-interactive, run all
  python scripts/python/lumina_onboard.py --skip-bones
  python scripts/python/lumina_onboard.py --steps 1,2,3

Tags: #automation #onboard @JARVIS @PEAK
See: docs/system/WHAT_WE_CAN_LEARN_FROM_OPENCLAW_OPEN_SOURCE.md
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def run_step(
    step_name: str,
    cmd: List[str],
    cwd: Path,
    optional: bool = False,
) -> bool:
    """Run a step; return True if success or optional and non-zero."""
    print("")
    print(f"  → {step_name}")
    print(f"    {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, cwd=cwd, timeout=120, check=False)
        ok = r.returncode == 0
        if not ok and optional:
            print("    (optional step failed; continuing)")
        return ok or optional
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"    Error: {e}")
        return optional


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lumina onboard — one CLI wizard for new user or new machine.",
    )
    parser.add_argument("--yes", "-y", action="store_true", help="Non-interactive; run all steps")
    parser.add_argument("--skip-bones", action="store_true", help="Skip Bones health check")
    parser.add_argument("--skip-keybindings", action="store_true", help="Skip keybindings step")
    parser.add_argument("--skip-jarvis-pin", action="store_true", help="Skip JARVIS pin step")
    parser.add_argument("--skip-router-test", action="store_true", help="Skip router test step")
    parser.add_argument(
        "--steps",
        type=str,
        default=None,
        help="Comma-separated step numbers to run (e.g. 1,2,3). Default: all.",
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="Project root")
    args = parser.parse_args()

    root = args.project_root
    py = sys.executable

    steps_to_run: Optional[List[int]] = None
    if args.steps:
        try:
            steps_to_run = [int(s.strip()) for s in args.steps.split(",")]
        except ValueError:
            steps_to_run = [1, 2, 3, 4, 5]

    print("")
    print("=" * 60)
    print("  Lumina onboard")
    print("  One path for new user or new machine")
    print("=" * 60)

    if not args.yes and not args.steps:
        print("")
        print("  Steps: 1=Bones, 2=Keybindings, 3=JARVIS pin, 4=Router test, 5=MCP (info only)")
        print("  Run all? [Y/n]: ", end="")
        try:
            a = input().strip().lower()
            if a and a != "y" and a != "yes":
                print("  Aborted.")
                return 0
        except EOFError:
            pass

    failed = False

    # Step 1: Bones
    if steps_to_run is None or 1 in steps_to_run:
        if not args.skip_bones:
            ok = run_step(
                "Bones (health check)",
                [py, str(SCRIPT_DIR / "bones.py"), "--skip-full", "--project-root", str(root)],
                root,
            )
            if not ok:
                failed = True
        else:
            print("")
            print("  → Bones (skipped)")

    # Step 2: Keybindings
    if steps_to_run is None or 2 in steps_to_run:
        if not args.skip_keybindings:
            ok = run_step(
                "Keybindings",
                [py, str(SCRIPT_DIR / "apply_cursor_keybindings.py")],
                root,
            )
            if not ok:
                failed = True
        else:
            print("")
            print("  → Keybindings (skipped)")

    # Step 3: JARVIS pin
    if steps_to_run is None or 3 in steps_to_run:
        if not args.skip_jarvis_pin:
            ok = run_step(
                "JARVIS Master Chat (consolidate + pin)",
                [py, str(SCRIPT_DIR / "jarvis_master_chat_session.py"), "--consolidate", "--pin"],
                root,
            )
            if not ok:
                failed = True
        else:
            print("")
            print("  → JARVIS pin (skipped)")

    # Step 4: Router test
    if steps_to_run is None or 4 in steps_to_run:
        if not args.skip_router_test:
            ok = run_step(
                "Router test (request_tier_router)",
                [
                    py,
                    str(SCRIPT_DIR / "request_tier_router.py"),
                    "JARVIS",
                    "easy",
                    "code_generation",
                    "--json",
                ],
                root,
            )
            if not ok:
                failed = True
        else:
            print("")
            print("  → Router test (skipped)")

    # Step 5: MCP (info only)
    if steps_to_run is None or 5 in steps_to_run:
        print("")
        print("  → MCP / SSOT (info only)")
        print(
            "    Optional: configure MCP servers and SSOT. See config/homelab_mcp_hybrid_config.json"
        )
        print("    and config/lumina_ssot_registry.json.")

    print("")
    print("=" * 60)
    if failed:
        print("  Onboard completed with one or more failures. Review output above.")
    else:
        print("  Onboard complete. Restart Cursor if you changed keybindings or JARVIS pin.")
    print("=" * 60)
    print("")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
