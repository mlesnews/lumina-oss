#!/usr/bin/env python3
"""
ProtonPass CLI API Credentials Check

Comprehensive credential verification for ProtonPass CLI:
- CLI installation status
- Authentication status
- Credential validity test
- Azure Key Vault credential check
- API connectivity test

Tags: #PROTONPASS #CREDENTIALS #API #SECURITY #JARVIS #LUMINA
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
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

logger = get_logger("ProtonPassCLICredentialsCheck")

# ProtonPass CLI paths
PROTONPASS_CLI_WINDOWS = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")
PROTONPASS_CLI_GENERIC = "protonpass"


class ProtonPassCLICredentialsChecker:
    """Comprehensive ProtonPass CLI credentials checker"""

    def __init__(self):
        self.logger = logger
        self.cli_path = self._find_cli_path()
        self.check_results = {}

    def _find_cli_path(self) -> Optional[Path]:
        """Find ProtonPass CLI executable path"""
        # Check Windows-specific path first
        if PROTONPASS_CLI_WINDOWS.exists():
            return PROTONPASS_CLI_WINDOWS

        # Check if in PATH
        try:
            result = subprocess.run(
                [PROTONPASS_CLI_GENERIC, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return Path(PROTONPASS_CLI_GENERIC)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return None

    def check_cli_installation(self) -> Dict[str, Any]:
        """Check if ProtonPass CLI is installed"""
        self.logger.info("🔍 Checking ProtonPass CLI installation...")

        result = {
            "installed": False,
            "path": None,
            "version": None,
            "error": None
        }

        if not self.cli_path:
            result["error"] = "ProtonPass CLI not found"
            self.logger.warning("❌ ProtonPass CLI not found")
            return result

        result["installed"] = True
        result["path"] = str(self.cli_path)

        # Get version
        try:
            version_cmd = [str(self.cli_path), "--version"]
            if self.cli_path == Path(PROTONPASS_CLI_GENERIC):
                version_cmd = [PROTONPASS_CLI_GENERIC, "--version"]

            version_result = subprocess.run(
                version_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if version_result.returncode == 0:
                result["version"] = version_result.stdout.strip()
                self.logger.info(f"✅ ProtonPass CLI installed: {result['version']}")
            else:
                result["error"] = version_result.stderr.strip()
                self.logger.warning(f"⚠️  Could not get version: {result['error']}")
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"❌ Error checking version: {e}")

        return result

    def check_authentication_status(self) -> Dict[str, Any]:
        """Check if user is authenticated with ProtonPass CLI"""
        self.logger.info("🔐 Checking authentication status...")

        result = {
            "authenticated": False,
            "status": "unknown",
            "error": None,
            "details": {}
        }

        if not self.cli_path:
            result["error"] = "CLI not installed"
            return result

        # Try different test commands
        test_commands = [
            ["test"],
            ["info"],
            ["item", "list"]
        ]

        for cmd in test_commands:
            try:
                full_cmd = [str(self.cli_path)] + cmd
                if self.cli_path == Path(PROTONPASS_CLI_GENERIC):
                    full_cmd = [PROTONPASS_CLI_GENERIC] + cmd

                test_result = subprocess.run(
                    full_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if test_result.returncode == 0:
                    result["authenticated"] = True
                    result["status"] = "authenticated"
                    result["details"]["test_command"] = " ".join(cmd)
                    result["details"]["output"] = test_result.stdout.strip()
                    self.logger.info("✅ Authentication verified")
                    break
                else:
                    stderr = test_result.stderr.strip().lower()
                    stdout = test_result.stdout.strip().lower()

                    if "not logged in" in stderr or "not authenticated" in stderr:
                        result["status"] = "not_logged_in"
                        result["error"] = "Not logged in"
                    elif "needs extra password" in stderr or "extra password" in stderr:
                        result["status"] = "needs_extra_password"
                        result["error"] = "Needs extra password"
                    elif "session" in stderr and ("expired" in stderr or "invalid" in stderr):
                        result["status"] = "session_expired"
                        result["error"] = "Session expired"
                    elif "unauthorized" in stderr or "authentication" in stderr:
                        result["status"] = "unauthorized"
                        result["error"] = "Authentication failed"
                    else:
                        result["status"] = "unknown_error"
                        result["error"] = test_result.stderr.strip() or "Unknown error"

                    result["details"]["test_command"] = " ".join(cmd)
                    result["details"]["stderr"] = test_result.stderr.strip()
                    result["details"]["stdout"] = test_result.stdout.strip()

            except subprocess.TimeoutExpired:
                result["status"] = "timeout"
                result["error"] = "Command timed out"
                self.logger.warning("⚠️  Authentication check timed out")
                break
            except Exception as e:
                result["error"] = str(e)
                self.logger.error(f"❌ Error checking authentication: {e}")
                continue

        if not result["authenticated"]:
            self.logger.warning(f"⚠️  Authentication check failed: {result['status']}")

        return result

    def test_api_connectivity(self) -> Dict[str, Any]:
        """Test API connectivity by attempting to list items"""
        self.logger.info("🌐 Testing API connectivity...")

        result = {
            "connected": False,
            "items_count": 0,
            "error": None,
            "test_command": None
        }

        if not self.cli_path:
            result["error"] = "CLI not installed"
            return result

        # Try to list items (this requires authentication)
        list_commands = [
            ["item", "list", "--format", "json"],
            ["item", "list"],
            ["test"]  # Fallback to test command
        ]

        for cmd in list_commands:
            try:
                full_cmd = [str(self.cli_path)] + cmd
                if self.cli_path == Path(PROTONPASS_CLI_GENERIC):
                    full_cmd = [PROTONPASS_CLI_GENERIC] + cmd

                test_result = subprocess.run(
                    full_cmd,
                    capture_output=True,
                    text=True,
                    timeout=20
                )

                result["test_command"] = " ".join(cmd)

                if test_result.returncode == 0:
                    output = test_result.stdout.strip()
                    if output:
                        # Try to parse JSON
                        try:
                            items = json.loads(output)
                            if isinstance(items, list):
                                result["items_count"] = len(items)
                            elif isinstance(items, dict) and "items" in items:
                                result["items_count"] = len(items["items"])
                            else:
                                # Count lines if not JSON
                                lines = [l for l in output.split('\n') if l.strip()]
                                result["items_count"] = len(lines)
                        except json.JSONDecodeError:
                            # Not JSON, count lines
                            lines = [l for l in output.split('\n') if l.strip() and not l.startswith('#')]
                            result["items_count"] = len(lines)

                        result["connected"] = True
                        self.logger.info(f"✅ API connectivity verified ({result['items_count']} items)")
                        break
                else:
                    result["error"] = test_result.stderr.strip() or "Command failed"

            except subprocess.TimeoutExpired:
                result["error"] = "Command timed out"
                self.logger.warning("⚠️  API connectivity test timed out")
                break
            except Exception as e:
                result["error"] = str(e)
                self.logger.error(f"❌ Error testing API connectivity: {e}")
                continue

        if not result["connected"]:
            self.logger.warning(f"⚠️  API connectivity test failed: {result['error']}")

        return result

    def check_azure_vault_credentials(self) -> Dict[str, Any]:
        """Check if credentials are stored in Azure Key Vault"""
        self.logger.info("🔑 Checking Azure Key Vault credentials...")

        result = {
            "available": False,
            "credentials_found": [],
            "missing_credentials": [],
            "error": None
        }

        try:
            from unified_secrets_manager import UnifiedSecretsManager, SecretSource

            manager = UnifiedSecretsManager(project_root)

            # Check for common ProtonPass credentials
            credential_keys = [
                "protonpass-extra-password",
                "protonpass-username",
                "protonpass-password",
                "protonpass-api-key",
                "protonpass-token"
            ]

            for key in credential_keys:
                try:
                    secret = manager.get_secret(key, source=SecretSource.AZURE_KEY_VAULT)
                    if secret:
                        result["credentials_found"].append(key)
                    else:
                        result["missing_credentials"].append(key)
                except Exception as e:
                    result["missing_credentials"].append(key)
                    self.logger.debug(f"Could not retrieve {key}: {e}")

            result["available"] = len(result["credentials_found"]) > 0

            if result["available"]:
                self.logger.info(f"✅ Found {len(result['credentials_found'])} credential(s) in Azure Key Vault")
            else:
                self.logger.warning("⚠️  No ProtonPass credentials found in Azure Key Vault")

        except ImportError:
            result["error"] = "UnifiedSecretsManager not available"
            self.logger.warning("⚠️  UnifiedSecretsManager not available")
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"❌ Error checking Azure Key Vault: {e}")

        return result

    def run_full_check(self) -> Dict[str, Any]:
        """Run comprehensive credential check"""
        self.logger.info("=" * 70)
        self.logger.info("🔐 PROTONPASS CLI API CREDENTIALS CHECK")
        self.logger.info("=" * 70)

        results = {
            "timestamp": datetime.now().isoformat(),
            "cli_installation": self.check_cli_installation(),
            "authentication": self.check_authentication_status(),
            "api_connectivity": self.test_api_connectivity(),
            "azure_vault": self.check_azure_vault_credentials(),
            "overall_status": "unknown"
        }

        # Determine overall status
        if not results["cli_installation"]["installed"]:
            results["overall_status"] = "cli_not_installed"
        elif not results["authentication"]["authenticated"]:
            results["overall_status"] = "not_authenticated"
        elif not results["api_connectivity"]["connected"]:
            results["overall_status"] = "api_not_connected"
        else:
            results["overall_status"] = "healthy"

        self.check_results = results
        return results

    def print_summary(self):
        """Print human-readable summary"""
        if not self.check_results:
            self.run_full_check()

        results = self.check_results

        print("\n" + "=" * 70)
        print("📊 PROTONPASS CLI API CREDENTIALS CHECK SUMMARY")
        print("=" * 70)

        # CLI Installation
        print("\n1️⃣  CLI INSTALLATION:")
        if results["cli_installation"]["installed"]:
            print(f"   ✅ Installed: {results['cli_installation']['path']}")
            if results["cli_installation"]["version"]:
                print(f"   📦 Version: {results['cli_installation']['version']}")
        else:
            print(f"   ❌ Not installed")
            if results["cli_installation"]["error"]:
                print(f"   ⚠️  Error: {results['cli_installation']['error']}")

        # Authentication
        print("\n2️⃣  AUTHENTICATION:")
        if results["authentication"]["authenticated"]:
            print("   ✅ Authenticated")
        else:
            print(f"   ❌ Not authenticated")
            print(f"   📋 Status: {results['authentication']['status']}")
            if results["authentication"]["error"]:
                print(f"   ⚠️  Error: {results['authentication']['error']}")

        # API Connectivity
        print("\n3️⃣  API CONNECTIVITY:")
        if results["api_connectivity"]["connected"]:
            print(f"   ✅ Connected")
            print(f"   📊 Items accessible: {results['api_connectivity']['items_count']}")
        else:
            print(f"   ❌ Not connected")
            if results["api_connectivity"]["error"]:
                print(f"   ⚠️  Error: {results['api_connectivity']['error']}")

        # Azure Key Vault
        print("\n4️⃣  AZURE KEY VAULT:")
        if results["azure_vault"]["available"]:
            print(f"   ✅ Credentials found: {len(results['azure_vault']['credentials_found'])}")
            for cred in results["azure_vault"]["credentials_found"]:
                print(f"      • {cred}")
        else:
            print("   ⚠️  No credentials found in Azure Key Vault")
            if results["azure_vault"]["missing_credentials"]:
                print("   📋 Missing credentials:")
                for cred in results["azure_vault"]["missing_credentials"]:
                    print(f"      • {cred}")

        # Overall Status
        print("\n" + "=" * 70)
        print("🎯 OVERALL STATUS:")
        status = results["overall_status"]
        if status == "healthy":
            print("   ✅ HEALTHY - All systems operational")
        elif status == "cli_not_installed":
            print("   ❌ CLI NOT INSTALLED - Install ProtonPass CLI first")
        elif status == "not_authenticated":
            print("   ⚠️  NOT AUTHENTICATED - Run: python scripts/python/protonpass_auto_login.py")
        elif status == "api_not_connected":
            print("   ⚠️  API NOT CONNECTED - Check network and authentication")
        else:
            print(f"   ❓ UNKNOWN STATUS: {status}")

        print("=" * 70)
        print(f"⏰ Check completed at: {results['timestamp']}")
        print("=" * 70 + "\n")

        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ProtonPass CLI API Credentials Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/protonpasscli_api_credentials_check.py
  python scripts/python/protonpasscli_api_credentials_check.py --json
  python scripts/python/protonpasscli_api_credentials_check.py --quiet
        """
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output (only return exit code)"
    )

    args = parser.parse_args()

    checker = ProtonPassCLICredentialsChecker()
    results = checker.run_full_check()

    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.quiet:
        checker.print_summary()

    # Exit code based on overall status
    if results["overall_status"] == "healthy":
        return 0
    else:
        return 1


if __name__ == "__main__":


    sys.exit(main())