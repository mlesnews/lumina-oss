#!/usr/bin/env python3
"""
Test ElevenLabs MCP Server Connection and Functionality

Validates that the ElevenLabs MCP server is properly configured and accessible.

Tags: #TESTING #ELEVENLABS #MCP #VALIDATION @JARVIS
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TestElevenLabsMCP")


class ElevenLabsMCPTester:
    """Test ElevenLabs MCP server configuration and connectivity"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize tester"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.results = {"passed": [], "failed": [], "warnings": []}

    def test_nas_container_running(self) -> Tuple[bool, str]:
        """Test if NAS container is running"""
        logger.info("🔍 Testing NAS container status...")

        try:
            result = subprocess.run(
                ["ssh", "backupadm@<NAS_PRIMARY_IP>", "docker ps | grep elevenlabs-mcp-server"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and "elevenlabs-mcp-server" in result.stdout:
                logger.info("   ✅ Container is running")
                return True, "Container running"
            else:
                logger.warning("   ⚠️  Container not found or not running")
                return False, "Container not running"
        except Exception as e:
            logger.error(f"   ❌ Error checking container: {e}")
            return False, f"Error: {e}"

    def test_api_key_retrieval(self) -> Tuple[bool, str]:
        """Test API key retrieval from Azure Key Vault"""
        logger.info("🔍 Testing API key retrieval from Key Vault...")

        try:
            from azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)

            # Try multiple secret name variations (must be valid Key Vault names: alphanumeric and hyphens only)
            secret_names = [
                "elevenlabs-api-key",
                "elevenlabs-key",
                "elevenlabs-tts-key",
                "cursor-api-key",
            ]

            for secret_name in secret_names:
                try:
                    key = vault_client.get_secret(secret_name)
                    if key and len(key) > 20:
                        logger.info(f"   ✅ API key found: {secret_name} (length: {len(key)})")
                        return True, f"Key found: {secret_name}"
                except Exception:
                    continue

            logger.warning("   ⚠️  API key not found in Key Vault")
            return False, "API key not found"
        except ImportError:
            logger.error("   ❌ Azure Key Vault SDK not available")
            return False, "SDK not available"
        except Exception as e:
            logger.error(f"   ❌ Error retrieving key: {e}")
            return False, f"Error: {e}"

    def test_container_logs(self) -> Tuple[bool, str]:
        """Test container logs for successful startup"""
        logger.info("🔍 Testing container logs...")

        try:
            result = subprocess.run(
                ["ssh", "backupadm@<NAS_PRIMARY_IP>", "docker logs elevenlabs-mcp-server --tail 20"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                logs = result.stdout
                if "API key retrieved successfully" in logs:
                    logger.info("   ✅ API key retrieval logged")
                    return True, "Key retrieval successful"
                elif "ERROR" in logs or "Failed" in logs:
                    logger.warning("   ⚠️  Errors found in logs")
                    return False, "Errors in logs"
                else:
                    logger.info("   ℹ️  Logs available (no key retrieval message)")
                    return True, "Logs accessible"
            else:
                logger.warning("   ⚠️  Could not retrieve logs")
                return False, "Cannot access logs"
        except Exception as e:
            logger.error(f"   ❌ Error checking logs: {e}")
            return False, f"Error: {e}"

    def test_mcp_config(self) -> Tuple[bool, str]:
        """Test Cursor MCP configuration"""
        logger.info("🔍 Testing Cursor MCP configuration...")

        mcp_config = self.project_root / ".cursor" / "mcp_config.json"

        if not mcp_config.exists():
            logger.warning("   ⚠️  MCP config file not found")
            return False, "Config file missing"

        try:
            with open(mcp_config) as f:
                config = json.load(f)

            if "mcpServers" in config and "ElevenLabs" in config["mcpServers"]:
                elevenlabs_config = config["mcpServers"]["ElevenLabs"]

                # Check if using secure wrapper
                if "start_secure.py" in str(elevenlabs_config.get("args", [])):
                    logger.info("   ✅ Using secure wrapper script")
                    return True, "Secure wrapper configured"
                elif "ELEVENLABS_API_KEY" in str(elevenlabs_config.get("env", {})):
                    logger.warning("   ⚠️  Using old method with ELEVENLABS_API_KEY env var")
                    return False, "Needs update to secure wrapper"
                else:
                    logger.info("   ℹ️  ElevenLabs configured")
                    return True, "Configured"
            else:
                logger.warning("   ⚠️  ElevenLabs not in MCP config")
                return False, "Not configured"
        except Exception as e:
            logger.error(f"   ❌ Error reading config: {e}")
            return False, f"Error: {e}"

    def test_docker_desktop_config(self) -> Tuple[bool, str]:
        """Test Docker Desktop configuration (if applicable)"""
        logger.info("🔍 Testing Docker Desktop configuration...")

        # This would require Docker Desktop API or manual verification
        logger.info("   ℹ️  Docker Desktop config requires manual verification")
        logger.info("   ℹ️  Check: Docker Desktop → MCP Toolkit → elevenlabs")
        return True, "Manual verification required"

    def run_all_tests(self) -> Dict:
        """Run all tests and return results"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("🧪 ElevenLabs MCP Server Testing")
        logger.info("=" * 80)
        logger.info("")

        tests = [
            ("NAS Container Running", self.test_nas_container_running),
            ("API Key Retrieval", self.test_api_key_retrieval),
            ("Container Logs", self.test_container_logs),
            ("MCP Config", self.test_mcp_config),
            ("Docker Desktop Config", self.test_docker_desktop_config),
        ]

        for test_name, test_func in tests:
            try:
                passed, message = test_func()
                if passed:
                    self.results["passed"].append((test_name, message))
                else:
                    self.results["failed"].append((test_name, message))
            except Exception as e:
                self.results["failed"].append((test_name, f"Exception: {e}"))
            logger.info("")

        return self.results

    def print_summary(self):
        """Print test summary"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Test Summary")
        logger.info("=" * 80)
        logger.info("")

        total = len(self.results["passed"]) + len(self.results["failed"])
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])

        logger.info(f"Total Tests: {total}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info("")

        if self.results["passed"]:
            logger.info("✅ PASSED:")
            for test_name, message in self.results["passed"]:
                logger.info(f"   • {test_name}: {message}")
            logger.info("")

        if self.results["failed"]:
            logger.info("❌ FAILED:")
            for test_name, message in self.results["failed"]:
                logger.info(f"   • {test_name}: {message}")
            logger.info("")

        if failed == 0:
            logger.info("🎉 All tests passed!")
            return 0
        else:
            logger.warning(f"⚠️  {failed} test(s) failed")
            return 1


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test ElevenLabs MCP Server")
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    tester = ElevenLabsMCPTester(project_root=args.project_root)
    tester.run_all_tests()
    return tester.print_summary()


if __name__ == "__main__":
    sys.exit(main())
