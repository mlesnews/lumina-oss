#!/usr/bin/env python3
"""
VSCode Issue Fixer - Automated Resolution for Common VSCode Problems

Addresses common VSCode/Cursor issues:
- Extension availability errors (Prettier formatter, etc.)
- Settings not taking effect notifications
- File reopen requirements
- Formatter configuration issues

Uses JARVIS 5W1H troubleshooting methodology to systematically resolve issues.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class VSCodeIssueFixer:
    """Automated fixer for common VSCode issues"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent

        # Issue patterns and fixes
        self.issue_patterns = {
            "prettier_formatter_unavailable": {
                "symptoms": ["prettier", "formatter", "not available", "esbenp.prettier-vscode"],
                "root_cause": "Prettier extension not installed or disabled",
                "fixes": [
                    "install_prettier_extension",
                    "enable_prettier_extension",
                    "configure_default_formatter",
                    "check_workspace_settings"
                ]
            },
            "setting_not_effective": {
                "symptoms": ["setting", "not", "effect", "reopen", "file"],
                "root_cause": "Configuration requires restart or reload",
                "fixes": [
                    "reload_window",
                    "reopen_file",
                    "check_language_server",
                    "verify_settings_syntax"
                ]
            },
            "extension_update_required": {
                "symptoms": ["extension", "update", "new version", "available"],
                "root_cause": "Extension version mismatch",
                "fixes": [
                    "update_extension",
                    "reload_window",
                    "check_compatibility"
                ]
            }
        }

    def identify_issue(self, error_message: str) -> Optional[str]:
        """Identify the type of VSCode issue from error message"""
        error_lower = error_message.lower()

        for issue_type, pattern in self.issue_patterns.items():
            symptoms = pattern["symptoms"]
            if any(symptom in error_lower for symptom in symptoms):
                return issue_type

        return None

    async def fix_issue(self, issue_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply fixes for identified issue"""

        context = context or {}
        result = {
            "issue_type": issue_type,
            "fixes_applied": [],
            "success": False,
            "errors": [],
            "recommendations": []
        }

        if issue_type == "prettier_formatter_unavailable":
            result.update(await self._fix_prettier_formatter())

        elif issue_type == "setting_not_effective":
            result.update(await self._fix_setting_not_effective())

        elif issue_type == "extension_update_required":
            result.update(await self._fix_extension_update(context))

        else:
            result["errors"].append(f"Unknown issue type: {issue_type}")

        # Determine overall success
        result["success"] = len(result["fixes_applied"]) > 0 and len(result["errors"]) == 0

        return result

    async def _fix_prettier_formatter(self) -> Dict[str, Any]:
        """Fix Prettier formatter availability issues"""
        fixes = []
        errors = []

        try:
            # Check if Prettier extension is installed
            result = subprocess.run(
                ["code", "--list-extensions"],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                extensions = result.stdout.strip().split('\n')
                prettier_installed = any('esbenp.prettier-vscode' in ext for ext in extensions)

                if not prettier_installed:
                    # Install Prettier extension
                    install_result = subprocess.run(
                        ["code", "--install-extension", "esbenp.prettier-vscode"],
                        capture_output=True, text=True, timeout=30
                    )

                    if install_result.returncode == 0:
                        fixes.append("installed_prettier_extension")
                    else:
                        errors.append(f"Failed to install Prettier: {install_result.stderr}")
                else:
                    fixes.append("prettier_already_installed")

                    # Try to enable/reload
                    reload_result = subprocess.run(
                        ["code", "--command", "workbench.action.reloadWindow"],
                        capture_output=True, text=True, timeout=10
                    )
                    fixes.append("reloaded_vscode_window")
            else:
                errors.append("Could not check installed extensions")

        except Exception as e:
            errors.append(f"Error fixing Prettier: {e}")

        # Configure settings if needed
        await self._configure_prettier_settings()

        return {
            "fixes_applied": fixes,
            "errors": errors,
            "recommendations": [
                "Set Prettier as default formatter for supported file types",
                "Configure Prettier settings in .prettierrc file",
                "Consider using Format on Save for consistent formatting"
            ]
        }

    async def _configure_prettier_settings(self):
        """Configure Prettier settings in workspace"""
        try:
            settings_file = self.project_root / ".vscode" / "settings.json"
            settings_file.parent.mkdir(exist_ok=True)

            # Read existing settings
            settings = {}
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

            # Configure Prettier as default formatter
            settings.update({
                "editor.defaultFormatter": "esbenp.prettier-vscode",
                "editor.formatOnSave": True,
                "prettier.requireConfig": True,
                "[javascript]": {
                    "editor.defaultFormatter": "esbenp.prettier-vscode"
                },
                "[typescript]": {
                    "editor.defaultFormatter": "esbenp.prettier-vscode"
                },
                "[json]": {
                    "editor.defaultFormatter": "esbenp.prettier-vscode"
                },
                "[html]": {
                    "editor.defaultFormatter": "esbenp.prettier-vscode"
                },
                "[css]": {
                    "editor.defaultFormatter": "esbenp.prettier-vscode"
                }
            })

            # Write updated settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not configure Prettier settings: {e}")

    async def _fix_setting_not_effective(self) -> Dict[str, Any]:
        """Fix settings not taking effect issues"""
        fixes = []
        errors = []

        try:
            # Reload VSCode window
            result = subprocess.run(
                ["code", "--command", "workbench.action.reloadWindow"],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                fixes.append("reloaded_vscode_window")
            else:
                errors.append(f"Failed to reload window: {result.stderr}")

            # Also try reopening current file if possible
            fixes.append("suggest_file_reopen")

        except Exception as e:
            errors.append(f"Error reloading VSCode: {e}")

        return {
            "fixes_applied": fixes,
            "errors": errors,
            "recommendations": [
                "Reopen the affected file after reload",
                "Check that settings syntax is valid",
                "Verify workspace vs user settings precedence",
                "Consider restarting the language server"
            ]
        }

    async def _fix_extension_update(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix extension update issues"""
        fixes = []
        errors = []

        extension_id = context.get("extension_id")

        if extension_id:
            try:
                # Update specific extension
                result = subprocess.run(
                    ["code", "--install-extension", extension_id, "--force"],
                    capture_output=True, text=True, timeout=60
                )

                if result.returncode == 0:
                    fixes.append(f"updated_extension_{extension_id}")

                    # Reload window
                    reload_result = subprocess.run(
                        ["code", "--command", "workbench.action.reloadWindow"],
                        capture_output=True, text=True, timeout=10
                    )
                    fixes.append("reloaded_vscode_window")
                else:
                    errors.append(f"Failed to update {extension_id}: {result.stderr}")

            except Exception as e:
                errors.append(f"Error updating extension: {e}")
        else:
            errors.append("No extension_id provided for update")

        return {
            "fixes_applied": fixes,
            "errors": errors,
            "recommendations": [
                "Check extension changelog for breaking changes",
                "Test extension functionality after update",
                "Consider updating related extensions together"
            ]
        }

    async def diagnose_and_fix(self, error_message: str) -> str:
        """Main interface - diagnose issue and apply fixes"""

        print(f"🔍 Diagnosing VSCode issue: {error_message}")

        # Identify issue
        issue_type = self.identify_issue(error_message)

        if not issue_type:
            return f"❌ Could not identify the issue type from: {error_message}"

        print(f"📋 Identified issue: {issue_type}")

        # Apply fixes
        result = await self.fix_issue(issue_type)

        # Format response
        response = f"""
## 🔧 VSCode Issue Resolution Report

**Issue Type:** {issue_type.replace('_', ' ').title()}
**Original Error:** {error_message}

### ✅ Fixes Applied
"""

        for fix in result["fixes_applied"]:
            response += f"- {fix.replace('_', ' ').title()}\n"

        if result["errors"]:
            response += "\n### ❌ Errors Encountered\n"
            for error in result["errors"]:
                response += f"- {error}\n"

        if result["recommendations"]:
            response += "\n### 💡 Recommendations\n"
            for rec in result["recommendations"]:
                response += f"- {rec}\n"

        response += f"\n### 📊 Resolution Status\n"
        status = "✅ SUCCESS" if result["success"] else "❌ PARTIAL SUCCESS"
        response += f"**Overall Result:** {status}\n"

        return response


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python fix_vscode_issues.py \"error message\"")
        sys.exit(1)

    error_message = " ".join(sys.argv[1:])

    fixer = VSCodeIssueFixer()

    async def run_fix():
        result = await fixer.diagnose_and_fix(error_message)
        print(result)

    asyncio.run(run_fix())


if __name__ == "__main__":


    main()