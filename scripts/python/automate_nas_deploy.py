#!/usr/bin/env python3
"""
Automate NAS credential sync + cron deploy. #automation — AI does the heavy lifting.

Single entry point: optionally sync NAS credentials from ProtonPass to Azure (Triad),
then deploy all cron jobs to NAS Kron. Credentials are resolved automatically
(Azure → UnifiedSecretManager → ProtonPass); no secrets in logs or files.

Usage:
  python scripts/python/automate_nas_deploy.py              # Deploy only (creds from Triad)
  python scripts/python/automate_nas_deploy.py --sync-first # Sync ProtonPass→Azure then deploy

Tags: #automation @JARVIS @triad
"""

import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


def main():
    import argparse

    p = argparse.ArgumentParser(
        description="Automate NAS deploy (#automation). Optionally sync ProtonPass→Azure then deploy cron to NAS."
    )
    p.add_argument(
        "--sync-first",
        action="store_true",
        help="Sync NAS credentials from ProtonPass CLI to Azure Key Vault before deploy",
    )
    p.add_argument(
        "--dry-run-sync",
        action="store_true",
        help="With --sync-first: only test ProtonPass fetch, do not write to Azure",
    )
    args = p.parse_args()

    if args.sync_first:
        sync_script = script_dir / "sync_nas_credentials_protonpass_to_vault.py"
        sync_cmd = [sys.executable, str(sync_script)]
        if args.dry_run_sync:
            sync_cmd.append("--dry-run")
        r = subprocess.run(sync_cmd, cwd=str(project_root), check=False)
        if r.returncode != 0:
            print("Sync step failed; aborting deploy.")
            _print_login_prompts(sync_failed=True)
            return r.returncode

    deploy_script = script_dir / "deploy_all_cron_to_nas.py"
    r = subprocess.run([sys.executable, str(deploy_script)], cwd=str(project_root), check=False)
    if r.returncode != 0:
        _print_login_prompts(sync_failed=False)
    return r.returncode


def _print_login_prompts(sync_failed: bool) -> None:
    """Print login prompts; optionally run az login if user says yes."""
    try:
        from prompt_nas_login import print_nas_login_prompts, prompt_and_run_az_login
    except ImportError:
        print("Run: az login")
        if sync_failed:
            print("Run: pass-cli login --interactive <your-proton-email>")
        return
    print_nas_login_prompts()
    if not sync_failed:
        if prompt_and_run_az_login():
            print("Re-running deploy...")
            deploy_script = script_dir / "deploy_all_cron_to_nas.py"
            subprocess.run([sys.executable, str(deploy_script)], cwd=str(project_root), check=False)


if __name__ == "__main__":
    sys.exit(main())
