#!/usr/bin/env python3
"""
Prompt users to log in when NAS credentials are unavailable.

Prints clear login instructions and can optionally run login commands
(az login; ProtonPass login must be run by user for password input).

Tags: #automation @JARVIS
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# No secrets in these messages; use placeholders only.
# Official Proton Pass CLI: pass-cli login --interactive <USERNAME> (see PROTONPASS_CLI_STEP_BY_STEP.md)
AZURE_LOGIN_CMD = "az login"
PROTONPASS_LOGIN_CMD = "pass-cli login --interactive <your-proton-email@example.com>"
VAULT_NAME = "jarvis-lumina"
SECRET_NAMES = "nas-username, nas-password (or nas-username-10-17-17-32, nas-password-10-17-17-32)"


# Short lead lines (I.E. "No credentials active, please run ...")
NO_CREDS_AZURE = "No credentials active. Please run: az login"
NO_CREDS_PROTONPASS = (
    "No credentials active. Please run: pass-cli login --interactive <your-proton-email>"
)


def print_nas_login_prompts(reason: str = "no_credentials") -> None:  # pylint: disable=unused-argument
    """Print login prompts so users know what to run. No secrets in output."""
    print()
    print(NO_CREDS_AZURE)
    print("  or, if you use ProtonPass CLI:", NO_CREDS_PROTONPASS)
    print()
    print("=" * 70)
    print("  Details — run in this terminal")
    print("=" * 70)
    print()
    print("1. Azure Key Vault (for NAS credentials):")
    print(f"   Run:  {AZURE_LOGIN_CMD}")
    print("   Then ensure this Key Vault has the NAS secrets:")
    print(f"   Vault: {VAULT_NAME}  |  Secrets: {SECRET_NAMES}")
    print()
    print("2. ProtonPass CLI (optional; if you use it for NAS credentials):")
    print(f"   Run:  {PROTONPASS_LOGIN_CMD}")
    print("   (Replace with your Proton Pass email; type password when prompted.)")
    print()
    print("3. Then re-run your command:")
    print("   python scripts/python/automate_nas_deploy.py")
    print("   or  python scripts/python/automate_nas_deploy.py --sync-first")
    print()
    print("=" * 70)


def prompt_and_run_az_login() -> bool:
    """Ask user to run 'az login' now; if yes, run it and return True."""
    try:
        answer = input("Run 'az login' now? (y/n) [y]: ").strip().lower() or "y"
    except (EOFError, KeyboardInterrupt):
        answer = "n"
    if answer != "y":
        return False
    import subprocess

    r = subprocess.run([AZURE_LOGIN_CMD.split()[0], "login"], check=False)
    return r.returncode == 0


def prompt_and_run_protonpass_login() -> bool:
    """Print Proton Pass CLI login command; optionally run it (user will type password). Official: pass-cli login --interactive <USERNAME>."""
    print("Proton Pass CLI login must be run in this terminal (you type your password).")
    try:
        answer = (
            input("Run 'pass-cli login --interactive <email>' now? (y/n) [n]: ").strip().lower()
            or "n"
        )
    except (EOFError, KeyboardInterrupt):
        answer = "n"
    if answer != "y":
        return False
    email = input("Proton Pass email: ").strip()
    if not email:
        print("No email entered; skipping.")
        return False
    import subprocess

    cli = __get_protonpass_cli_path()
    cmd = [cli] if cli else ["pass-cli"]
    # Official syntax: pass-cli login --interactive <USERNAME> (positional, not --username)
    r = subprocess.run(cmd + ["login", "--interactive", email], check=False)
    return r.returncode == 0


def __get_protonpass_cli_path() -> str:
    """Return path to ProtonPass CLI if found."""
    import os

    path = os.getenv("PROTONPASS_CLI_PATH")
    if path and Path(path).exists():
        return path
    for p in [
        Path(os.path.expanduser("~/AppData/Local/Programs/ProtonPass/pass-cli.exe")),
        Path(os.path.expanduser("~/AppData/Local/Programs/pass-cli.exe")),
    ]:
        if p.exists():
            return str(p)
    return ""


if __name__ == "__main__":
    print_nas_login_prompts()
    if len(sys.argv) > 1 and sys.argv[1] == "--prompt-az":
        prompt_and_run_az_login()
