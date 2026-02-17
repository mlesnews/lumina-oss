#!/usr/bin/env python3
"""
Setup NAS as Git Remote Repository

Creates a bare Git repository on NAS and pushes the current branch.

Tags: #GIT #NAS #SETUP @LUMINA
"""

import os
import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

NAS_PATH = r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\git\lumina.git"
PROJECT_ROOT = Path(r"C:\Users\mlesn\Dropbox\my_projects\.lumina")

def run_command(cmd, cwd=None, check=True):
    """Run a command and return output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=check,
            shell=True
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr, e.returncode

def main():
    print("🗂️  Setting up NAS as Git remote...\n")

    # Create directory on NAS
    print("📁 Creating NAS directory...")
    nas_path = Path(NAS_PATH)
    try:
        nas_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ready: {NAS_PATH}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create directory: {e}")
        print("   (May already exist or need manual creation)")

    # Initialize bare repository on NAS
    print("\n🔧 Initializing bare repository on NAS...")
    output, code = run_command(
        f'git init --bare',
        cwd=NAS_PATH,
        check=False
    )
    if code == 0 or "already exists" in output.lower() or "already a git repository" in output.lower():
        print("✅ Bare repository initialized")
    else:
        print(f"ℹ️  Repository status: {output}")

    # Change to project directory
    os.chdir(PROJECT_ROOT)

    # Configure remote
    print("\n🔗 Configuring Git remote...")

    # Check current origin
    output, _ = run_command("git remote get-url origin", check=False)
    if output and "github.com" in output:
        print("🔄 Removing GitHub remote...")
        run_command("git remote remove origin", check=False)

    # Add/update NAS remote
    output, _ = run_command("git remote get-url nas", check=False)
    if not output:
        run_command(f'git remote add nas "{NAS_PATH}"')
        print("✅ Added NAS as remote 'nas'")
    else:
        run_command(f'git remote set-url nas "{NAS_PATH}"')
        print("✅ Updated NAS remote URL")

    # Show remotes
    print("\n📋 Current remotes:")
    output, _ = run_command("git remote -v")
    print(output)

    # Get current branch
    output, _ = run_command("git branch --show-current")
    current_branch = output.strip()
    print(f"\n🌿 Current branch: {current_branch}")

    # Push to NAS
    print(f"\n📤 Pushing to NAS...")
    output, code = run_command(
        f'git push -u nas {current_branch}',
        check=False
    )

    if code == 0:
        print("\n✅ Successfully pushed to NAS!")
        print(f"   Remote: nas")
        print(f"   Branch: {current_branch}")
        print(f"   Location: {NAS_PATH}")
    else:
        print(f"\n❌ Error pushing to NAS:")
        print(output)
        return 1

    print("\n✨ Setup complete!")
    return 0

if __name__ == '__main__':
    import os
    sys.exit(main())
