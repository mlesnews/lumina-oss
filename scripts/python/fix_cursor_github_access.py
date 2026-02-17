#!/usr/bin/env python3
"""
Fix Cursor IDE GitHub Access

Fixes GitHub access denied errors for Cursor IDE cloud agents.
Configures GitHub access token properly.

Tags: #CURSOR_IDE #GITHUB #ACCESS_TOKEN #CLOUD_AGENT @JARVIS @LUMINA
"""

import sys
import json
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixCursorGitHub")


class CursorGitHubAccessFixer:
    """
    Fix Cursor IDE GitHub Access

    Helps configure GitHub access token for Cursor IDE cloud agents.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize GitHub access fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Cursor GitHub Access Fixer initialized")
        logger.info("   🔧 Ready to fix GitHub access")

    def get_github_token_instructions(self) -> Dict[str, Any]:
        """
        Get instructions for creating GitHub access token

        Returns:
            Instructions dictionary
        """
        return {
            "steps": [
                {
                    "step": 1,
                    "title": "Go to GitHub Settings",
                    "description": "Navigate to GitHub Personal Access Tokens",
                    "url": "https://github.com/settings/tokens",
                    "action": "Click 'Generate new token' > 'Generate new token (classic)'"
                },
                {
                    "step": 2,
                    "title": "Configure Token",
                    "description": "Set up token with required permissions",
                    "settings": {
                        "note": "Cursor IDE Cloud Agent - lumina-ai",
                        "expiration": "90 days (or custom)",
                        "scopes": [
                            "repo (Full control of private repositories)",
                            "workflow (Update GitHub Action workflows)",
                            "read:org (Read org and team membership)"
                        ]
                    }
                },
                {
                    "step": 3,
                    "title": "Generate Token",
                    "description": "Click 'Generate token' and copy the token",
                    "warning": "⚠️  Copy the token immediately - you won't be able to see it again!"
                },
                {
                    "step": 4,
                    "title": "Configure in Cursor IDE",
                    "description": "Add token to Cursor IDE settings",
                    "instructions": [
                        "Open Cursor IDE Settings",
                        "Go to 'GitHub Access' section",
                        "Click 'Connect GitHub' or 'Add Token'",
                        "Paste the token",
                        "Click 'Save' or 'Connect'"
                    ]
                },
                {
                    "step": 5,
                    "title": "Verify Access",
                    "description": "Check that repository access is granted",
                    "actions": [
                        "Refresh the GitHub Access section in Cursor IDE",
                        "Verify 'mlesnews/lumina-ai' shows as 'Connected' or 'Access Granted'",
                        "Status should show green checkmark instead of red X"
                    ]
                }
            ],
            "repository": "mlesnews/lumina-ai",
            "required_scopes": [
                "repo",
                "workflow",
                "read:org"
            ],
            "cursor_settings_path": "Settings > GitHub Access",
            "troubleshooting": {
                "if_still_denied": [
                    "Verify token has 'repo' scope (full control)",
                    "Check token hasn't expired",
                    "Try disconnecting and reconnecting",
                    "Check if repository is private (requires 'repo' scope)",
                    "Verify token was copied correctly (no extra spaces)"
                ],
                "if_token_expired": [
                    "Generate a new token",
                    "Update token in Cursor IDE settings",
                    "Refresh GitHub Access section"
                ]
            }
        }

    def open_github_token_page(self):
        """Open GitHub token creation page in Neo browser"""
        url = "https://github.com/settings/tokens/new"
        logger.info(f"   🌐 Opening GitHub token creation page in Neo browser...")
        logger.info(f"      URL: {url}")

        # Always try to open in Neo browser specifically
        try:
            from set_neo_default_browser import NeoDefaultBrowserSetter
            neo_setter = NeoDefaultBrowserSetter()

            # Open in Neo browser (even if not default)
            if neo_setter.open_url_in_neo(url):
                logger.info("   ✅ Opened in Neo browser")
                return
            else:
                logger.warning("   ⚠️  Could not open in Neo browser")
        except ImportError:
            logger.warning("   ⚠️  Neo browser setter not available")
        except Exception as e:
            logger.warning(f"   ⚠️  Error opening in Neo: {e}")

        # Fallback to default browser (only if Neo method failed)
        try:
            webbrowser.open(url)
            logger.info("   ✅ Opened in default browser (fallback)")
            logger.warning("   ⚠️  Note: Opened in default browser, not Neo")
        except Exception as e:
            logger.error(f"   ❌ Could not open browser: {e}")
            logger.info(f"   📋 Please manually visit: {url}")

    def print_instructions(self):
        """Print step-by-step instructions"""
        instructions = self.get_github_token_instructions()

        print("=" * 80)
        print("🔧 FIX CURSOR IDE GITHUB ACCESS")
        print("=" * 80)
        print(f"\nRepository: {instructions['repository']}")
        print(f"Required Scopes: {', '.join(instructions['required_scopes'])}")
        print("\n" + "=" * 80)

        for step in instructions['steps']:
            print(f"\n📋 Step {step['step']}: {step['title']}")
            print(f"   {step['description']}")

            if 'url' in step:
                print(f"   🌐 URL: {step['url']}")

            if 'settings' in step:
                print(f"   ⚙️  Settings:")
                for key, value in step['settings'].items():
                    if isinstance(value, list):
                        print(f"      {key}:")
                        for item in value:
                            print(f"        • {item}")
                    else:
                        print(f"      {key}: {value}")

            if 'instructions' in step:
                print(f"   📝 Instructions:")
                for i, instruction in enumerate(step['instructions'], 1):
                    print(f"      {i}. {instruction}")

            if 'actions' in step:
                print(f"   ✅ Actions:")
                for i, action in enumerate(step['actions'], 1):
                    print(f"      {i}. {action}")

            if 'warning' in step:
                print(f"   ⚠️  {step['warning']}")

        print("\n" + "=" * 80)
        print("🔍 TROUBLESHOOTING")
        print("=" * 80)

        troubleshooting = instructions['troubleshooting']

        print("\n❌ If Still Denied:")
        for item in troubleshooting['if_still_denied']:
            print(f"   • {item}")

        print("\n⏰ If Token Expired:")
        for item in troubleshooting['if_token_expired']:
            print(f"   • {item}")

        print("\n" + "=" * 80)
        print("💡 TIP: After creating token, go to Cursor IDE Settings > GitHub Access")
        print("   and paste the token. Then click 'Refresh' to verify access.")
        print("=" * 80)

    def create_token_config_template(self):
        """Create a template config file for GitHub token (for reference only)"""
        template_file = self.config_dir / "github_token_template.json"

        template = {
            "_comment": "DO NOT STORE ACTUAL TOKEN IN THIS FILE - This is a template only",
            "_warning": "GitHub tokens should be stored securely, not in version control",
            "_instructions": "Use Cursor IDE Settings > GitHub Access to configure token",
            "repository": "mlesnews/lumina-ai",
            "required_scopes": [
                "repo",
                "workflow",
                "read:org"
            ],
            "token_creation_url": "https://github.com/settings/tokens/new",
            "cursor_settings_path": "Settings > GitHub Access",
            "note": "Cursor IDE Cloud Agent - lumina-ai"
        }

        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            logger.info(f"   ✅ Created template: {template_file}")
            logger.info("   ⚠️  Remember: Do NOT store actual token in this file!")
        except Exception as e:
            logger.error(f"   ❌ Error creating template: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Fix Cursor IDE GitHub Access")
        parser.add_argument("--instructions", action="store_true", help="Show instructions")
        parser.add_argument("--open-github", action="store_true", help="Open GitHub token page")
        parser.add_argument("--create-template", action="store_true", help="Create config template")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        fixer = CursorGitHubAccessFixer()

        if args.open_github:
            fixer.open_github_token_page()

        elif args.create_template:
            fixer.create_token_config_template()

        elif args.instructions or not any([args.open_github, args.create_template]):
            if args.json:
                instructions = fixer.get_github_token_instructions()
                print(json.dumps(instructions, indent=2))
            else:
                fixer.print_instructions()

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()