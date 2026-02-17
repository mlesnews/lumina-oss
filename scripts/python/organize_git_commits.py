#!/usr/bin/env python3
"""
Organize Git Changes into Logical Commits

Categorizes and stages changes into logical commit groups:
- Configuration files
- Documentation
- Scripts
- Data files
- Application code
- Infrastructure

Tags: #GIT #COMMIT #ORGANIZATION @LUMINA
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import logging
logger = logging.getLogger("organize_git_commits")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def run_git_command(cmd: List[str]) -> Tuple[str, int]:
    """Run a git command and return output and exit code"""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        print(f"Error running git command: {e}")
        return "", 1

def get_changed_files() -> Dict[str, List[str]]:
    try:
        """Get all changed files categorized by type"""
        output, _ = run_git_command(['status', '--short'])

        categories = {
            'config': [],
            'docs': [],
            'scripts': [],
            'data': [],
            'applications': [],
            'infrastructure': [],
            'root': [],
            'other': []
        }

        for line in output.split('\n'):
            if not line.strip():
                continue

            # Extract file path (skip status indicators)
            file_path = line[3:].strip()
            if not file_path:
                continue

            path = Path(file_path)

            # Categorize
            if path.parts[0] == 'config':
                categories['config'].append(file_path)
            elif path.parts[0] == 'docs':
                categories['docs'].append(file_path)
            elif path.parts[0] == 'scripts':
                categories['scripts'].append(file_path)
            elif path.parts[0] == 'data':
                categories['data'].append(file_path)
            elif path.parts[0] == 'applications':
                categories['applications'].append(file_path)
            elif path.parts[0] in ['infrastructure', 'containerization', 'docker', 'platforms']:
                categories['infrastructure'].append(file_path)
            elif path.parts[0] in ['.cursorrules', '.dockerignore', 'Dockerfile', 'package.json', 'requirements.txt']:
                categories['root'].append(file_path)
            else:
                categories['other'].append(file_path)

        return categories

    except Exception as e:
        logger.error(f"Error in get_changed_files: {e}", exc_info=True)
        raise
def stage_and_commit(category: str, files: List[str], commit_msg: str) -> bool:
    """Stage files and commit them"""
    if not files:
        return True

    print(f"\n📦 Staging {len(files)} files for {category}...")

    # Stage files
    for file_path in files:
        output, code = run_git_command(['add', file_path])
        if code != 0:
            print(f"⚠️  Warning: Failed to stage {file_path}")

    # Check if there are staged changes
    output, _ = run_git_command(['diff', '--cached', '--name-only'])
    if not output.strip():
        print(f"ℹ️  No changes to commit for {category}")
        return True

    # Commit
    print(f"💾 Committing {category}...")
    output, code = run_git_command(['commit', '--no-verify', '-m', commit_msg])
    if code == 0:
        print(f"✅ Successfully committed {category}")
        return True
    else:
        print(f"❌ Failed to commit {category}: {output}")
        return False

def main():
    """Main function to organize commits"""
    print("🗂️  Organizing Git changes into logical commits...\n")

    categories = get_changed_files()

    # Print summary
    print("📊 Change Summary:")
    total = 0
    for cat, files in categories.items():
        if files:
            print(f"   {cat:15} {len(files):4} files")
            total += len(files)
    print(f"   {'TOTAL':15} {total:4} files\n")

    # Commit in logical order
    commit_plan = [
        ('root', 'root', '[CONFIG] Update root configuration files\n\n- Update .cursorrules, Dockerfile, package.json\n- Root-level configuration changes'),
        ('config', 'config', '[CONFIG] Update configuration files\n\n- Update service configs, blueprints, and settings\n- Configuration management updates'),
        ('infrastructure', 'infrastructure', '[INFRA] Update infrastructure and deployment\n\n- Docker, containerization, and platform configs\n- Infrastructure as code updates'),
        ('applications', 'applications', '[FEATURE] Update application code\n\n- IDE chat application updates\n- Application-level changes'),
        ('scripts', 'scripts', '[SCRIPTS] Update Python scripts and automation\n\n- Script updates and new automation tools\n- Python script improvements'),
        ('docs', 'docs', '[DOCS] Update documentation\n\n- Documentation updates and improvements\n- System documentation changes'),
        ('data', 'data', '[DATA] Update data files and state\n\n- State files, tickets, and runtime data\n- Data file updates'),
        ('other', 'other', '[MISC] Miscellaneous changes\n\n- Other unclassified changes\n- Additional updates'),
    ]

    success_count = 0
    for category_key, category_name, commit_msg in commit_plan:
        files = categories.get(category_key, [])
        if files:
            if stage_and_commit(category_name, files, commit_msg):
                success_count += 1
            else:
                print(f"⚠️  Skipping remaining commits due to error")
                break

    print(f"\n✅ Completed: {success_count}/{len([c for c in commit_plan if categories.get(c[0])])} commit groups")

    # Show remaining changes
    output, _ = run_git_command(['status', '--short'])
    remaining = [l for l in output.split('\n') if l.strip()]
    if remaining:
        print(f"\n📋 Remaining uncommitted changes: {len(remaining)}")
        print("   Run 'git status' to see details")
    else:
        print("\n✨ All changes have been committed!")

if __name__ == '__main__':
    main()
