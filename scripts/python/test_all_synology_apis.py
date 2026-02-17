#!/usr/bin/env python3
"""
Test All Synology API Endpoints
Tests all available Synology DSM API endpoints and documents which ones work
#JARVIS #MANUS #NAS #SYNOLOGY #API #TESTING
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from synology_api_base import SynologyAPIBase
    from nas_azure_vault_integration import NASAzureVaultIntegration
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

logger = get_logger("TestSynologyAPIs")


class SynologyAPITester:
    """Test all Synology DSM API endpoints"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001):
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.api: SynologyAPIBase = None
        self.results = {
            "working": [],
            "failed": [],
            "unknown": []
        }

    def test_endpoint(self, api: str, method: str, version: str = "1", 
                     params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a single API endpoint"""
        try:
            data = self.api.api_call(
                api=api,
                method=method,
                version=version,
                params=params or {},
                require_auth=True
            )

            if data is not None:
                return {
                    "success": True,
                    "api": api,
                    "method": method,
                    "version": version,
                    "data_available": True
                }
            else:
                return {
                    "success": False,
                    "api": api,
                    "method": method,
                    "version": version,
                    "error": "API call returned None"
                }
        except Exception as e:
            return {
                "success": False,
                "api": api,
                "method": method,
                "version": version,
                "error": str(e)
            }

    def test_all_apis(self) -> Dict[str, Any]:
        """Test all known Synology API endpoints"""
        if not API_AVAILABLE:
            return {
                "success": False,
                "error": "Synology API modules not available"
            }

        try:
            # Initialize API
            self.api = SynologyAPIBase(nas_ip=self.nas_ip, nas_port=self.nas_port)

            # Get credentials
            vault = NASAzureVaultIntegration()
            credentials = vault.get_nas_credentials()

            if not credentials:
                return {
                    "success": False,
                    "error": "Could not retrieve credentials"
                }

            # Login
            logger.info("🔐 Logging in to Synology DSM...")
            if not self.api.login(credentials["username"], credentials["password"]):
                return {
                    "success": False,
                    "error": "Login failed"
                }

            logger.info("✅ Logged in successfully")
            logger.info("🧪 Testing API endpoints...")

            # List of APIs to test
            apis_to_test = [
                # Core APIs
                ("SYNO.API.Info", "query", "1"),
                ("SYNO.API.Auth", "logout", "3"),

                # System Info
                ("SYNO.Core.System", "info", "1"),
                ("SYNO.Core.System", "time", "1"),
                ("SYNO.Core.System", "network", "1"),

                # Task Scheduler
                ("SYNO.Core.TaskScheduler", "list", "1"),
                ("SYNO.Core.TaskScheduler", "get", "1"),

                # Storage
                ("SYNO.Storage.Volume", "list", "1"),
                ("SYNO.Storage.Pool", "list", "1"),
                ("SYNO.Storage.Disk", "list", "1"),

                # Package Manager
                ("SYNO.Core.Package", "list", "1"),
                ("SYNO.Core.Package", "get", "1"),

                # File Station
                ("SYNO.FileStation.List", "list", "2"),
                ("SYNO.FileStation.Info", "get", "2"),

                # Network
                ("SYNO.Core.Network", "list", "1"),
                ("SYNO.Core.Network.Router", "list", "1"),

                # User Management
                ("SYNO.Core.User", "list", "1"),
                ("SYNO.Core.Group", "list", "1"),

                # Log Center
                ("SYNO.Core.SyslogClient", "list", "1"),
            ]

            for api, method, version in apis_to_test:
                logger.info(f"   Testing: {api}.{method} (v{version})")
                result = self.test_endpoint(api, method, version)

                if result["success"]:
                    self.results["working"].append(result)
                    logger.info(f"      ✅ Working")
                else:
                    self.results["failed"].append(result)
                    logger.warning(f"      ❌ Failed: {result.get('error', 'Unknown')}")

            # Logout
            self.api.logout()

            return {
                "success": True,
                "results": self.results,
                "summary": {
                    "total_tested": len(apis_to_test),
                    "working": len(self.results["working"]),
                    "failed": len(self.results["failed"])
                }
            }

        except Exception as e:
            logger.error(f"❌ Error testing APIs: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Test All Synology API Endpoints")
        parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
        parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        tester = SynologyAPITester(nas_ip=args.nas_ip, nas_port=args.nas_port)
        result = tester.test_all_apis()

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("=" * 70)
            print("   SYNOLOGY API ENDPOINT TEST RESULTS")
            print("=" * 70)
            print("")

            if result.get("success"):
                summary = result.get("summary", {})
                print(f"📊 Summary:")
                print(f"   Total Tested: {summary.get('total_tested', 0)}")
                print(f"   ✅ Working: {summary.get('working', 0)}")
                print(f"   ❌ Failed: {summary.get('failed', 0)}")
                print("")

                if tester.results["working"]:
                    print("✅ Working APIs:")
                    for api_result in tester.results["working"]:
                        print(f"   • {api_result['api']}.{api_result['method']} (v{api_result['version']})")
                    print("")

                if tester.results["failed"]:
                    print("❌ Failed APIs:")
                    for api_result in tester.results["failed"]:
                        print(f"   • {api_result['api']}.{api_result['method']} (v{api_result['version']})")
                        print(f"     Error: {api_result.get('error', 'Unknown')}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                return 1

        return 0 if result.get("success") else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())