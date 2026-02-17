#!/usr/bin/env python3
"""
ProtonPass CLI Helper
Lists available accounts and retrieves credentials

Tags: #PROTONPASS #CREDENTIALS #SECURITY
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional

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

logger = get_logger("ProtonPassHelper")


class ProtonPassHelper:
    """Helper for ProtonPass CLI operations"""

    @staticmethod
    def check_installed() -> bool:
        """Check if ProtonPass CLI is installed"""
        try:
            result = subprocess.run(
                ["protonpass", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    @staticmethod
    def list_accounts() -> List[str]:
        """List all accounts in ProtonPass"""
        accounts = []

        try:
            # Try different list commands
            commands = [
                ["protonpass", "list"],
                ["protonpass", "ls"],
                ["protonpass", "search", ""],
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
                        if output:
                            # Parse output - format may vary
                            lines = output.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('#') and not line.startswith('Error'):
                                    accounts.append(line)

                            if accounts:
                                break
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Error listing accounts: {e}")

        return accounts

    @staticmethod
    def search_accounts(query: str) -> List[str]:
        """Search for accounts matching query"""
        accounts = ProtonPassHelper.list_accounts()
        matching = [acc for acc in accounts if query.lower() in acc.lower()]
        return matching

    @staticmethod
    def get_account_info(account_name: str) -> Dict[str, any]:
        """Get full account information"""
        info = {
            "name": account_name,
            "username": None,
            "password": None,
            "url": None,
            "totp": None,
            "notes": None,
            "available": False
        }

        try:
            # Try to get full account data
            commands = [
                ["protonpass", "get", account_name],
                ["protonpass", "show", account_name],
                ["protonpass", "view", account_name]
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
                        if output:
                            info["available"] = True
                            # Try to parse structured output (JSON, YAML, etc.)
                            try:
                                parsed = json.loads(output)
                                info.update(parsed)
                            except:
                                # If not JSON, try to extract fields
                                lines = output.split('\n')
                                for line in lines:
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        key = key.strip().lower()
                                        value = value.strip()
                                        if 'username' in key or 'user' in key or 'login' in key:
                                            info["username"] = value
                                        elif 'password' in key or 'pass' in key:
                                            info["password"] = value
                                        elif 'url' in key or 'website' in key:
                                            info["url"] = value

                            break
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Error getting account info: {e}")

        return info


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ProtonPass CLI Helper")
    parser.add_argument("--check", action="store_true", help="Check if ProtonPass CLI is installed")
    parser.add_argument("--list", "-l", action="store_true", help="List all accounts")
    parser.add_argument("--search", "-s", type=str, help="Search for accounts")
    parser.add_argument("--info", "-i", type=str, help="Get account information")

    args = parser.parse_args()

    if args.check:
        installed = ProtonPassHelper.check_installed()
        if installed:
            print("✅ ProtonPass CLI is installed")
            try:
                result = subprocess.run(
                    ["protonpass", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"   Version: {result.stdout.strip()}")
            except:
                pass
        else:
            print("❌ ProtonPass CLI is not installed")
            print("   Install from: https://github.com/ProtonPass/cli")

    if args.list:
        print("\n📋 Listing ProtonPass accounts...")
        accounts = ProtonPassHelper.list_accounts()
        if accounts:
            print(f"\nFound {len(accounts)} accounts:")
            for acc in accounts:
                print(f"  • {acc}")
        else:
            print("\nNo accounts found or ProtonPass CLI not configured")
            print("   Make sure you're logged in: protonpass login")

    if args.search:
        print(f"\n🔍 Searching for: {args.search}")
        matching = ProtonPassHelper.search_accounts(args.search)
        if matching:
            print(f"\nFound {len(matching)} matching accounts:")
            for acc in matching:
                print(f"  • {acc}")
        else:
            print("\nNo matching accounts found")

    if args.info:
        print(f"\n📊 Account information for: {args.info}")
        info = ProtonPassHelper.get_account_info(args.info)
        print(f"\nAvailable: {'✅' if info['available'] else '❌'}")
        if info['available']:
            if info.get('username'):
                print(f"Username: {info['username']}")
            if info.get('password'):
                print(f"Password: {'*' * len(info['password'])}")
            if info.get('url'):
                print(f"URL: {info['url']}")
            if info.get('totp'):
                print(f"TOTP: ✅")

    if not any([args.check, args.list, args.search, args.info]):
        parser.print_help()


if __name__ == "__main__":


    main()