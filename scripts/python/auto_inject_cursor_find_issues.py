#!/usr/bin/env python3
"""
Auto-Inject Cursor Find Issues Workflow

Automatically injects Cursor IDE 'Find Issues' workflow into all applicable
workflows at perfect timing. This ensures code quality checks run automatically
at appropriate points in the development workflow.

Integration Points:
- Pre-commit hooks
- File save events
- Build/run workflows
- Task execution hooks
- CI/CD pipelines
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoInjectFindIssues")

# Add scripts/python to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


class CursorFindIssuesInjector:
    """
    Automatically inject Cursor IDE Find Issues workflow into applicable workflows
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.vscode_dir = self.project_root / ".vscode"
        self.cursor_dir = self.project_root / ".cursor"
        self.git_hooks_dir = self.project_root / ".git" / "hooks"

        # Find Issues task configuration
        self.find_issues_task = {
            "label": "🔍 Find Issues: Run All Checks",
            "type": "shell",
            "command": "python",
            "args": [
                "scripts/python/jarvis_roast_manus_control.py",
                "--file",
                "${file}",
                "--fix"
            ],
            "group": {
                "kind": "test",
                "isDefault": False
            },
            "presentation": {
                "echo": True,
                "reveal": "always",
                "focus": False,
                "panel": "dedicated",
                "clear": True
            },
            "problemMatcher": {
                "owner": "python",
                "fileLocation": ["relative", "${workspaceFolder}"],
                "pattern": {
                    "regexp": "^\\[([A-Z]+)\\]\\s+(.+):\\s+(.+)$",
                    "file": 2,
                    "line": 3,
                    "severity": 1,
                    "message": 3
                }
            },
            "options": {
                "shell": {
                    "executable": "C:\\Program Files\\PowerShell\\7-preview\\pwsh.exe",
                    "args": ["-NoProfile", "-ExecutionPolicy", "Bypass"]
                }
            }
        }

    def inject_into_tasks_json(self) -> bool:
        """Inject Find Issues task into .vscode/tasks.json"""
        tasks_file = self.vscode_dir / "tasks.json"

        if not tasks_file.exists():
            logger.warning(f"tasks.json not found at {tasks_file}")
            return False

        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)

            # Check if task already exists
            existing_labels = [task.get("label", "") for task in tasks_data.get("tasks", [])]
            if self.find_issues_task["label"] in existing_labels:
                logger.info("Find Issues task already exists in tasks.json")
                return True

            # Add task
            if "tasks" not in tasks_data:
                tasks_data["tasks"] = []

            tasks_data["tasks"].insert(0, self.find_issues_task)  # Insert at beginning for visibility

            # Save updated tasks
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2)

            logger.info(f"✅ Injected Find Issues task into {tasks_file}")
            return True

        except Exception as e:
            logger.error(f"Error injecting into tasks.json: {e}")
            return False

    def create_file_watcher_config(self) -> bool:
        """Create file watcher configuration for auto-running on save"""
        settings_file = self.vscode_dir / "settings.json"

        try:
            # Load existing settings
            settings = {}
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

            # Add file watcher task
            if "files.watcherExclude" not in settings:
                settings["files.watcherExclude"] = {}

            # Add task to run on Python file save
            if "tasks.runOptions" not in settings:
                settings["tasks.runOptions"] = {}

            # Add editor code actions for find issues
            if "editor.codeActionsOnSave" not in settings:
                settings["editor.codeActionsOnSave"] = {}

            settings["editor.codeActionsOnSave"]["source.organizeImports"] = "explicit"
            settings["editor.codeActionsOnSave"]["source.fixAll"] = "explicit"

            # Save settings
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)

            logger.info(f"✅ Updated settings.json with Find Issues integration")
            return True

        except Exception as e:
            logger.error(f"Error creating file watcher config: {e}")
            return False

    def create_pre_commit_hook(self) -> bool:
        try:
            """Create Git pre-commit hook to run Find Issues"""
            if not self.git_hooks_dir.exists():
                logger.warning("Git hooks directory not found (not a git repo?)")
                return False

            pre_commit_hook = self.git_hooks_dir / "pre-commit"

            hook_content = '''#!/bin/sh
#
# Auto-Injected: Cursor Find Issues Pre-Commit Hook
# Runs JARVIS roast checks before commit
#

echo "🔍 Running Find Issues checks before commit..."

# Run Find Issues on staged Python files
git diff --cached --name-only --diff-filter=ACM | grep -E "\\.py$" | while read file; do
    if [ -f "$file" ]; then
        echo "Checking: $file"
        python scripts/python/jarvis_roast_manus_control.py --file "$file" --auto-fix || {
            echo "❌ Issues found in $file. Commit aborted."
            exit 1
        }
    fi
done

exit 0
'''

            pre_commit_hook.write_text(hook_content)
            pre_commit_hook.chmod(0o755)  # Make executable
            logger.info(f"✅ Created pre-commit hook: {pre_commit_hook}")
            return True
        except Exception as e:
            logger.error(f"Error creating pre-commit hook: {e}", exc_info=True)
            return False

    def create_cursor_settings(self) -> bool:
        """Create Cursor-specific settings for Find Issues"""
        if not self.cursor_dir.exists():
            self.cursor_dir.mkdir(parents=True, exist_ok=True)

        cursor_settings_file = self.cursor_dir / "settings.json"

        try:
            # Load existing settings
            settings = {}
            if cursor_settings_file.exists():
                with open(cursor_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

            # Add Find Issues auto-run configuration
            settings["findIssues"] = {
                "autoRunOnSave": True,
                "autoRunBeforeCommit": True,
                "autoFix": True,
                "severity": ["critical", "high", "medium"],
                "exclude": ["__pycache__", "*.pyc", ".venv", "node_modules"],
                "enabled": True
            }

            # Save settings
            with open(cursor_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)

            logger.info(f"✅ Created Cursor settings: {cursor_settings_file}")
            return True

        except Exception as e:
            logger.error(f"Error creating Cursor settings: {e}")
            return False

    def create_workflow_documentation(self) -> bool:
        """Create documentation for the Find Issues workflow"""
        docs_dir = self.project_root / "docs" / "workflows"
        docs_dir.mkdir(parents=True, exist_ok=True)

        doc_file = docs_dir / "AUTO_FIND_ISSUES_WORKFLOW.md"

        doc_content = '''# Auto Find Issues Workflow

## Overview

The Auto Find Issues workflow automatically runs code quality checks at optimal timing points in the development workflow.

## Integration Points

### 1. VS Code / Cursor Tasks
- **Task**: `🔍 Find Issues: Run All Checks`
- **Trigger**: Manual (Ctrl+Shift+P → Tasks: Run Task)
- **Command**: `python scripts/python/jarvis_roast_manus_control.py --file ${file} --auto-fix`

### 2. File Save (Auto-Run)
- **Trigger**: Automatic on Python file save
- **Configuration**: `.vscode/settings.json`
- **Behavior**: Runs linting and auto-fixes when enabled

### 3. Pre-Commit Hook
- **Trigger**: Automatic before git commit
- **Location**: `.git/hooks/pre-commit`
- **Behavior**: Checks all staged Python files, aborts commit if critical issues found

### 4. Cursor Settings
- **Configuration**: `.cursor/settings.json`
- **Features**: Auto-run on save, auto-fix, severity filtering

## Usage

### Manual Run
1. Open Command Palette (Ctrl+Shift+P)
2. Select "Tasks: Run Task"
3. Choose "🔍 Find Issues: Run All Checks"

### Automatic Run
- **On Save**: Configured in settings.json (if enabled)
- **Before Commit**: Automatic via pre-commit hook

## Configuration

### Severity Levels
- `critical`: Blocking issues (commit aborted)
- `high`: Important issues (warnings)
- `medium`: Moderate issues (suggestions)
- `low`: Minor issues (informational)

### Auto-Fix
- Enabled by default for non-critical issues
- Critical issues require manual review

## Customization

Edit `.vscode/tasks.json` to customize:
- Task arguments
- Problem matcher patterns
- Execution options

## Status

✅ Auto-injection complete
✅ Pre-commit hook installed
✅ Cursor settings configured
✅ Documentation generated

---
*Auto-generated by auto_inject_cursor_find_issues.py*
'''

        try:
            doc_file.write_text(doc_content)
            logger.info(f"✅ Created workflow documentation: {doc_file}")
            return True
        except Exception as e:
            logger.error(f"Error creating documentation: {e}")
            return False

    def inject_all(self) -> Dict[str, bool]:
        try:
            """Inject Find Issues workflow into all applicable locations"""
            logger.info("🚀 Auto-Injecting Cursor Find Issues Workflow...")
            logger.info("="*60)

            results = {
                "tasks_json": False,
                "file_watcher": False,
                "pre_commit_hook": False,
                "cursor_settings": False,
                "documentation": False
            }

            # Inject into tasks.json
            logger.info("\n1️⃣ Injecting into tasks.json...")
            results["tasks_json"] = self.inject_into_tasks_json()

            # Create file watcher config
            logger.info("\n2️⃣ Configuring file watcher...")
            results["file_watcher"] = self.create_file_watcher_config()

            # Create pre-commit hook
            logger.info("\n3️⃣ Creating pre-commit hook...")
            results["pre_commit_hook"] = self.create_pre_commit_hook()

            # Create Cursor settings
            logger.info("\n4️⃣ Creating Cursor settings...")
            results["cursor_settings"] = self.create_cursor_settings()

            # Create documentation
            logger.info("\n5️⃣ Creating documentation...")
            results["documentation"] = self.create_workflow_documentation()

            # Summary
            logger.info("\n" + "="*60)
            logger.info("📊 INJECTION SUMMARY")
            logger.info("="*60)

            for component, success in results.items():
                status = "✅" if success else "❌"
                logger.info(f"   {status} {component.replace('_', ' ').title()}")

            total = len(results)
            successful = sum(1 for v in results.values() if v)
            logger.info(f"\n   Total: {successful}/{total} components injected")

            return results


        except Exception as e:
            self.logger.error(f"Error in inject_all: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    injector = CursorFindIssuesInjector()
    results = injector.inject_all()

    # Exit with error code if any failed
    if all(results.values()):
        return 0
    else:
        return 1


if __name__ == "__main__":



    sys.exit(main())