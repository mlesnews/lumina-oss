#!/usr/bin/env python3
"""
Remove GitHub Token from Git History
Uses git filter-branch or git filter-repo to remove sensitive data

Tags: #SECURITY #GIT #TOKEN @JARVIS @LUMINA
"""
import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Token value should be provided via environment variable or prompt
# This avoids hardcoding the token in the script itself
EXPOSED_TOKEN = None

def main():
    global EXPOSED_TOKEN

    print("=" * 70)
    print("🔐 REMOVING GITHUB TOKEN FROM GIT HISTORY")
    print("=" * 70)
    print("")

    # Get token from environment or prompt
    import os
    EXPOSED_TOKEN = os.environ.get("GITHUB_EXPOSED_TOKEN")

    if not EXPOSED_TOKEN:
        print("⚠️  Token not found in environment variable GITHUB_EXPOSED_TOKEN")
        print("   For security, provide the token via environment variable:")
        print("   $env:GITHUB_EXPOSED_TOKEN = 'token-value'")
        print("")
        token_input = input("Enter the exposed token to remove (or 'skip' to search git history): ")
        if token_input.lower() == 'skip':
            print("⚠️  Cannot proceed without token value")
            return 1
        EXPOSED_TOKEN = token_input

    print("⚠️  WARNING: This will rewrite git history!")
    print("⚠️  All collaborators must re-clone after this operation")
    print("⚠️  Make sure you have a backup!")
    print("")

    response = input("Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        return 1

    print("")
    print("🔍 Checking if git-filter-repo is available...")

    # Check for git-filter-repo (preferred method)
    try:
        result = subprocess.run(
            ["git", "filter-repo", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ git-filter-repo found - using it (safer method)")
            use_filter_repo = True
        else:
            use_filter_repo = False
    except FileNotFoundError:
        print("⚠️  git-filter-repo not found - will use git filter-branch")
        use_filter_repo = False

    print("")
    print("🔧 Removing token from git history...")

    if use_filter_repo:
        # Use git-filter-repo (safer, faster)
        cmd = [
            "git", "filter-repo",
            "--path", ".kilocode/mcp.json",
            "--invert-paths",
            "--force"
        ]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_root)

        if result.returncode != 0:
            print("❌ git-filter-repo failed, trying alternative method...")
            use_filter_repo = False

    if not use_filter_repo:
        # Use git filter-branch (fallback)
        print("Using git filter-branch...")

        # Create a script to replace the token
        filter_script = f'''
import sys
import re

token = "{EXPOSED_TOKEN}"
replacement = "REDACTED_TOKEN_REMOVED"

for line in sys.stdin:
    line = line.replace(token, replacement)
    sys.stdout.write(line)
'''

        # Write filter script
        filter_script_path = project_root / ".git" / "filter-token.py"
        filter_script_path.parent.mkdir(parents=True, exist_ok=True)
        filter_script_path.write_text(filter_script)

        # Run filter-branch
        cmd = [
            "git", "filter-branch",
            "--force",
            "--index-filter",
            f'python "{filter_script_path}"',
            "--prune-empty",
            "--tag-name-filter", "cat",
            "--", "--all"
        ]

        print(f"Running: {' '.join(cmd[:5])} ...")
        result = subprocess.run(cmd, cwd=project_root)

        # Clean up
        if filter_script_path.exists():
            filter_script_path.unlink()

    if result.returncode == 0:
        print("")
        print("✅ Token removed from git history")
        print("")
        print("📋 Next steps:")
        print("   1. Force push to remote (if you're sure):")
        print("      git push --force --all")
        print("      git push --force --tags")
        print("   2. Notify all collaborators to re-clone")
        print("   3. Verify token is gone:")
        print(f"      git log --all --full-history --source -p -- .kilocode/mcp.json | Select-String '{EXPOSED_TOKEN[:10]}'")
        print("")
        print("⚠️  IMPORTANT: Revoke the token on GitHub immediately!")
        return 0
    else:
        print("")
        print("❌ Failed to remove token from history")
        print("   You may need to manually use BFG Repo-Cleaner or git filter-branch")
        return 1


if __name__ == "__main__":

    sys.exit(main())