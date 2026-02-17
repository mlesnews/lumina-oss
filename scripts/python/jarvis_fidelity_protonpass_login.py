#!/usr/bin/env python3
"""
JARVIS Fidelity Login with ProtonPass CLI
Automates Fidelity login using credentials from ProtonPass CLI

Tags: #FIDELITY #PROTONPASS #LOGIN_AUTOMATION #JARVIS
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFidelityProtonPassLogin")

# Fidelity URLs
FIDELITY_LOGIN_URL = "https://digital.fidelity.com/ftgw/digital/login"
FIDELITY_DASHBOARD_URL = "https://digital.fidelity.com/ftgw/digital/trader-dashboard"


class ProtonPassCLI:
    """ProtonPass CLI integration using existing setup"""

    # Use existing ProtonPass CLI path from previous setup
    PROTONPASS_CLI = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")

    @staticmethod
    def ensure_logged_in() -> bool:
        """Ensure ProtonPass CLI is logged in using existing auto-login"""
        try:
            from protonpass_auto_login import main as auto_login
            logger.info("🔐 Ensuring ProtonPass CLI is logged in...")
            result = auto_login()
            if result:
                logger.info("✅ ProtonPass CLI is authenticated")
                return True
            else:
                logger.warning("⚠️  ProtonPass CLI login may be required")
                return False
        except ImportError:
            logger.debug("protonpass_auto_login not available")
            return False
        except Exception as e:
            logger.warning(f"Could not auto-login: {e}")
            return False

    @staticmethod
    def list_items() -> List[str]:
        """List all items in ProtonPass"""
        items = []
        try:
            cli_path = ProtonPassCLI.PROTONPASS_CLI
            if not cli_path.exists():
                return items

            result = subprocess.run(
                [str(cli_path), "item", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        items.append(line)
        except Exception as e:
            logger.debug(f"Could not list items: {e}")

        return items

    @staticmethod
    def get_credential(account_name: str, field: str = "password") -> Optional[str]:
        """
        Get credential from ProtonPass CLI

        Args:
            account_name: Name of the account in ProtonPass
            field: Field to retrieve (password, username, totp, etc.)

        Returns:
            Credential value or None
        """
        try:
            # Use existing ProtonPass CLI path
            cli_path = ProtonPassCLI.PROTONPASS_CLI

            if not cli_path.exists():
                logger.warning(f"ProtonPass CLI not found at {cli_path}")
                return None

            # Try different ProtonPass CLI commands (using item subcommand)
            commands = [
                [str(cli_path), "item", "get", account_name, "--field", field],
                [str(cli_path), "item", "get", account_name],
                [str(cli_path), "get", account_name, field],
                [str(cli_path), "get", account_name]
            ]

            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if result.returncode == 0:
                        output = result.stdout.strip()
                        if output and not output.startswith("Error"):
                            logger.info(f"✅ Retrieved {field} for {account_name} from ProtonPass")
                            return output
                except FileNotFoundError:
                    continue
                except Exception as e:
                    logger.debug(f"Command failed: {' '.join(cmd)} - {e}")
                    continue

            logger.warning(f"Could not retrieve {field} for {account_name} from ProtonPass")
            return None

        except Exception as e:
            logger.error(f"ProtonPass CLI error: {e}")
            return None

    @staticmethod
    def get_full_credentials(account_name: str) -> Dict[str, Optional[str]]:
        """
        Get all credentials for an account from ProtonPass

        Uses direct CLI calls with the configured path

        Returns:
            Dictionary with username, password, and other fields
        """
        credentials = {
            "username": None,
            "password": None,
            "totp": None,
            "url": None,
            "notes": None
        }

        # Use direct CLI calls with configured path
        cli_path = ProtonPassCLI.PROTONPASS_CLI

        if not cli_path.exists():
            logger.warning(f"ProtonPass CLI not found at {cli_path}")
            return credentials

        try:
            # Get full item details as JSON
            result = subprocess.run(
                [str(cli_path), "item", "get", account_name, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                try:
                    item_data = json.loads(result.stdout.strip())
                    credentials["password"] = item_data.get("password") or item_data.get("fields", {}).get("password")
                    credentials["username"] = item_data.get("username") or item_data.get("fields", {}).get("username") or item_data.get("fields", {}).get("login")
                    credentials["url"] = item_data.get("url") or item_data.get("fields", {}).get("url")
                    credentials["totp"] = item_data.get("totp") or item_data.get("fields", {}).get("totp")
                    credentials["notes"] = item_data.get("notes") or item_data.get("fields", {}).get("notes")
                    logger.info(f"✅ Retrieved full credentials for {account_name}")
                    return credentials
                except json.JSONDecodeError:
                    logger.debug("Could not parse JSON, trying field-by-field")

            # Fallback: Get fields individually
            credentials["password"] = ProtonPassCLI.get_credential(account_name, "password")
            credentials["username"] = ProtonPassCLI.get_credential(account_name, "username")
            credentials["totp"] = ProtonPassCLI.get_credential(account_name, "totp")
            credentials["url"] = ProtonPassCLI.get_credential(account_name, "url")

            # Try alternative username fields
            if credentials["password"] and not credentials["username"]:
                for field in ["login", "email", "user", "account"]:
                    username = ProtonPassCLI.get_credential(account_name, field)
                    if username:
                        credentials["username"] = username
                        break

        except Exception as e:
            logger.error(f"Error getting credentials: {e}")

        return credentials


class JARVISFidelityProtonPassLogin:
    """
    JARVIS Fidelity Login Automation with ProtonPass CLI
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize login automation"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.protonpass = ProtonPassCLI()

        logger.info("✅ JARVIS Fidelity ProtonPass Login initialized")

    def get_fidelity_credentials(self, account_name: str = "Fidelity") -> Dict[str, Optional[str]]:
        """Get Fidelity credentials from ProtonPass"""
        logger.info(f"🔐 Retrieving Fidelity credentials from ProtonPass...")
        logger.info(f"   Account name: {account_name}")

        # Ensure ProtonPass is logged in
        ProtonPassCLI.ensure_logged_in()

        # First, try to list items to find the correct account name
        logger.info("📋 Listing ProtonPass items to find Fidelity account...")
        items = ProtonPassCLI.list_items()

        if items:
            logger.info(f"   Found {len(items)} items in ProtonPass")
            # Search for Fidelity-related items
            fidelity_items = [item for item in items if "fidelity" in item.lower()]
            if fidelity_items:
                logger.info(f"   Found Fidelity items: {', '.join(fidelity_items)}")
                # Use the first matching item
                account_name = fidelity_items[0]
                logger.info(f"   Using account name: {account_name}")

        credentials = self.protonpass.get_full_credentials(account_name)

        if credentials.get("password"):
            logger.info("✅ Credentials retrieved successfully")
            logger.info(f"   Username: {'✅' if credentials.get('username') else '❌'}")
            logger.info(f"   Password: ✅")
        else:
            logger.warning("❌ Could not retrieve credentials from ProtonPass")
            logger.info("   Trying alternative account names...")

            # Try alternative names
            alternatives = ["fidelity", "Fidelity Investments", "Fidelity.com", "fidelity.com"]
            for alt_name in alternatives:
                if alt_name.lower() != account_name.lower():
                    alt_creds = self.protonpass.get_full_credentials(alt_name)
                    if alt_creds.get("password"):
                        logger.info(f"✅ Found credentials under: {alt_name}")
                        credentials = alt_creds
                        break

        return credentials

    def generate_login_instructions(self, credentials: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Generate login instructions for browser automation"""
        logger.info("📝 Generating login instructions...")

        instructions = {
            "generated_at": datetime.now().isoformat(),
            "login_url": FIDELITY_LOGIN_URL,
            "dashboard_url": FIDELITY_DASHBOARD_URL,
            "has_username": credentials.get("username") is not None,
            "has_password": credentials.get("password") is not None,
            "has_totp": credentials.get("totp") is not None,
            "steps": []
        }

        if not credentials.get("username") or not credentials.get("password"):
            instructions["steps"].append({
                "step": 1,
                "action": "error",
                "message": "Missing credentials. Username and password required."
            })
            return instructions

        # Step 1: Navigate to login
        instructions["steps"].append({
            "step": 1,
            "action": "navigate",
            "url": FIDELITY_LOGIN_URL,
            "description": "Navigate to Fidelity login page"
        })

        # Step 2: Wait for page load
        instructions["steps"].append({
            "step": 2,
            "action": "wait",
            "time": 3,
            "description": "Wait for login page to load"
        })

        # Step 3: Find and fill username
        instructions["steps"].append({
            "step": 3,
            "action": "type",
            "element": "username input field",
            "text": credentials["username"],
            "description": "Enter username"
        })

        # Step 4: Find and fill password
        instructions["steps"].append({
            "step": 4,
            "action": "type",
            "element": "password input field",
            "text": credentials["password"],
            "description": "Enter password"
        })

        # Step 5: Click login button
        instructions["steps"].append({
            "step": 5,
            "action": "click",
            "element": "Log In button",
            "description": "Click login button"
        })

        # Step 6: Wait for login
        instructions["steps"].append({
            "step": 6,
            "action": "wait",
            "time": 5,
            "description": "Wait for login to complete"
        })

        # Step 7: Handle TOTP if needed
        if credentials.get("totp"):
            instructions["steps"].append({
                "step": 7,
                "action": "type",
                "element": "TOTP/2FA input field",
                "text": credentials["totp"],
                "description": "Enter 2FA code (if prompted)"
            })

        # Step 8: Navigate to dashboard
        instructions["steps"].append({
            "step": 8,
            "action": "navigate",
            "url": FIDELITY_DASHBOARD_URL,
            "description": "Navigate to trader dashboard"
        })

        logger.info(f"✅ Generated {len(instructions['steps'])} login steps")

        return instructions

    def execute_login_with_mcp(self, credentials: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Execute login using MCP Browser tools

        NOTE: This provides the structure. Actual execution requires
        MCP Browser tools to be called in the environment.
        """
        logger.info("🚀 Executing Fidelity login with MCP Browser...")

        if not credentials.get("username") or not credentials.get("password"):
            return {
                "success": False,
                "error": "Missing credentials"
            }

        result = {
            "started_at": datetime.now().isoformat(),
            "success": False,
            "steps_completed": [],
            "error": None
        }

        logger.info("")
        logger.info("LOGIN EXECUTION PLAN:")
        logger.info("")
        logger.info("Step 1: Navigate to login page")
        logger.info(f"   browser_navigate(url='{FIDELITY_LOGIN_URL}')")
        result["steps_completed"].append("navigate_to_login")

        logger.info("")
        logger.info("Step 2: Wait for page load")
        logger.info("   browser_wait_for(time=3)")
        result["steps_completed"].append("wait_for_load")

        logger.info("")
        logger.info("Step 3: Capture snapshot to find login form")
        logger.info("   snapshot = browser_snapshot()")
        result["steps_completed"].append("capture_snapshot")

        logger.info("")
        logger.info("Step 4: Type username")
        logger.info(f"   browser_type(element='username input', text='{credentials['username']}')")
        result["steps_completed"].append("type_username")

        logger.info("")
        logger.info("Step 5: Type password")
        logger.info("   browser_type(element='password input', text='[PASSWORD]')")
        result["steps_completed"].append("type_password")

        logger.info("")
        logger.info("Step 6: Click login button")
        logger.info("   browser_click(element='Log In button')")
        result["steps_completed"].append("click_login")

        logger.info("")
        logger.info("Step 7: Wait for login")
        logger.info("   browser_wait_for(time=5)")
        result["steps_completed"].append("wait_for_login")

        logger.info("")
        logger.info("Step 8: Navigate to dashboard")
        logger.info(f"   browser_navigate(url='{FIDELITY_DASHBOARD_URL}')")
        result["steps_completed"].append("navigate_to_dashboard")

        logger.info("")
        logger.info("✅ Login execution plan ready!")
        logger.info("")
        logger.info("NOTE: Execute these MCP Browser commands to perform login")
        logger.info("")

        result["success"] = True
        result["completed_at"] = datetime.now().isoformat()

        return result


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Fidelity Login with ProtonPass")
        parser.add_argument("--account", "-a", type=str, default="Fidelity", help="ProtonPass account name")
        parser.add_argument("--credentials", "-c", action="store_true", help="Get credentials only")
        parser.add_argument("--instructions", "-i", action="store_true", help="Generate login instructions")
        parser.add_argument("--execute", "-e", action="store_true", help="Generate execution plan")

        args = parser.parse_args()

        login_automation = JARVISFidelityProtonPassLogin()

        # Get credentials
        credentials = login_automation.get_fidelity_credentials(args.account)

        if args.credentials:
            print("\n" + "=" * 70)
            print("FIDELITY CREDENTIALS FROM PROTONPASS")
            print("=" * 70)
            print(f"\nAccount: {args.account}")
            print(f"Username: {'✅' if credentials.get('username') else '❌'}")
            print(f"Password: {'✅' if credentials.get('password') else '❌'}")
            print(f"TOTP: {'✅' if credentials.get('totp') else '❌'}")
            print("")
            if credentials.get("username"):
                print(f"Username: {credentials['username']}")
            if credentials.get("password"):
                print(f"Password: {'*' * len(credentials['password'])}")
            print("")

        if args.instructions:
            instructions = login_automation.generate_login_instructions(credentials)
            output_file = login_automation.project_root / "data" / "fidelity_exploration" / "login_instructions.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(instructions, f, indent=2, ensure_ascii=False)

            print(f"\n✅ Login instructions saved to: {output_file}")
            print(f"\nSteps: {len(instructions['steps'])}")

        if args.execute:
            result = login_automation.execute_login_with_mcp(credentials)
            if result["success"]:
                print("\n✅ Login execution plan generated!")
                print(f"   Steps: {len(result['steps_completed'])}")
            else:
                print(f"\n❌ Error: {result.get('error')}")

        if not any([args.credentials, args.instructions, args.execute]):
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()