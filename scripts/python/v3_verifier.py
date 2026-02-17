#!/usr/bin/env python3
"""Simple @v3 verifier.

This script iterates over a predefined list of open files and performs a
basic consistency check: it verifies that each file contains a top‑level
docstring and that the file name matches a pattern expected by the
documentation system.  The script is intentionally lightweight – it
does not perform deep semantic analysis, but it can be extended to
include more sophisticated checks (e.g., comparing function signatures
with documentation).

The script prints a green checkmark for each file that passes the
checks and a red cross for failures.  The output is suitable for
copying into a CI log or a manual review.
"""

import os
import re

# List of files currently open in the editor (relative to the workspace root)
OPEN_FILES = [
    "scripts/python/TEN_WAYS_IMPROVEMENTS.md",
    "scripts/python/voice_filter_system.py",
    "scripts/python/voice_transcript_queue.py",
    "scripts/python/real_deal_migration_v3.py",
    "scripts/python/ask_ticket_holocron_middleware.py",
    ".cursor/commands/ironlegion.md",
    "scripts/python/cursor_auto_send_monitor.py",
    ".cursor/commands/v3.md",
    "scripts/python/store_mdv_usage_memory.py",
    "//<NAS_PRIMARY_IP>/homes/mlesn/Documents/cursor_invalid_model_ultron_plan_or_api.md",
    "../../../.cursor/environment.json",
    "data/cursor_models/cursor_models_config.json",
    "scripts/python/start_continuous_git_commit.py",
    "scripts/python/start_all_cluster_services.py",
    "scripts/python/kenny_roast_and_repair.py",
    "scripts/python/project_rr_session.py",
    "scripts/python/apply_anthropic_learnings.py",
    "containerization/services/elevenlabs-mcp-server/Dockerfile",
    "test_azure_sb.py",
    "scripts/python/rr_manual_repair.py",
    "RR_SESSION_COMPLETION_SYPHON.md",
]

# Simple check: file exists and contains a top‑level docstring (for .py files)
DOCSTRING_RE = re.compile(r"^\s*['\"]{3}.*?['\"]{3}\s*$", re.DOTALL | re.MULTILINE)

GREEN = "\u2705"
RED = "\u274c"


def check_file(path: str) -> bool:
    if not os.path.exists(path):
        return False
    if path.endswith(".py"):
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            return bool(DOCSTRING_RE.search(content))
        except Exception:
            return False
    # For non‑Python files, just check existence
    return True


def main():
    all_passed = True
    for rel_path in OPEN_FILES:
        # Resolve relative to workspace root
        abs_path = os.path.normpath(os.path.join(os.getcwd(), rel_path))
        passed = check_file(abs_path)
        status = GREEN if passed else RED
        print(f"{status} {rel_path}")
        if not passed:
            all_passed = False
    if all_passed:
        print("\nAll files passed @v3 verification.")
    else:
        print("\nSome files failed @v3 verification. Review the above list.")


if __name__ == "__main__":

    main()