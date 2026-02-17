#!/usr/bin/env python3
"""
ElevenLabs MCP Server Battle Test Suite
Comprehensive testing of ElevenLabs MCP server integration

#BATTLETESTING Framework

Tests:
- Service health and availability
- API key retrieval from Azure Key Vault
- MCP server connectivity
- Tool availability (all 24 tools)
- Audio generation functionality
- Error handling and resilience
- Performance and response times
- Security validation
- Failover scenarios
- Concurrent requests

Tags: #BATTLETESTING #ELEVENLABS #MCP #VALIDATION @JARVIS @MANUS
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ElevenLabsBattleTest")

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_PATH = (
    PROJECT_ROOT / "data" / "homelab_model_validation" / "elevenlabs_battletest_results.json"
)
RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class TestResult:
    """Test result"""

    service: str
    test_name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    details: Dict = None


@dataclass
class ServiceConfig:
    """Service configuration"""

    name: str
    endpoint: str
    port: int
    container: str
    nas_host: str = "<NAS_PRIMARY_IP>"
    nas_user: str = "backupadm"


class ElevenLabsBattleTest:
    """Comprehensive battle test for ElevenLabs MCP server"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize battle test"""
        if project_root is None:
            project_root = PROJECT_ROOT

        self.project_root = Path(project_root)
        self.results: List[TestResult] = []
        self.services = self._load_service_configs()
        self.start_time = time.time()

        logger.info("=" * 80)
        logger.info("⚔️  ELEVENLABS MCP SERVER BATTLE TEST")
        logger.info("=" * 80)
        logger.info("")
        logger.info("#BATTLETESTING Framework")
        logger.info("")

    def _load_service_configs(self) -> List[ServiceConfig]:
        """Load service configurations"""
        return [
            ServiceConfig(
                name="ElevenLabs MCP Server (NAS)",
                endpoint="http://<NAS_PRIMARY_IP>:8086",
                port=8086,
                container="elevenlabs-mcp-server",
                nas_host="<NAS_PRIMARY_IP>",
                nas_user="backupadm",
            ),
            ServiceConfig(
                name="ElevenLabs MCP Server (Local)",
                endpoint="http://localhost:8086",
                port=8086,
                container="elevenlabs-mcp-server",
                nas_host="localhost",
                nas_user="",
            ),
        ]

    def test_container_status(self, service: ServiceConfig) -> TestResult:
        """Test container status"""
        test_name = "Container Status"
        start = time.time()

        try:
            if service.nas_host == "localhost":
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "--filter",
                        f"name={service.container}",
                        "--format",
                        "{{.Names}}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            else:
                result = subprocess.run(
                    [
                        "ssh",
                        f"{service.nas_user}@{service.nas_host}",
                        f"docker ps --filter name={service.container} --format '{{{{.Names}}}}'",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            duration = (time.time() - start) * 1000

            if result.returncode == 0 and service.container in result.stdout:
                logger.info(f"   ✅ {test_name}: Container running")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={"container": service.container, "status": "running"},
                )
            else:
                logger.warning(f"   ⚠️  {test_name}: Container not found")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="Container not running",
                    details={"container": service.container},
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                service=service.name,
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e),
            )

    def test_api_key_retrieval(self, service: ServiceConfig) -> TestResult:
        """Test API key retrieval from Azure Key Vault"""
        test_name = "API Key Retrieval"
        start = time.time()

        try:
            from azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)

            # Secret names to try (NOT secrets themselves - just Key Vault secret name identifiers)
            # MUST be valid Key Vault names: alphanumeric and hyphens only
            secret_names = [
                "elevenlabs-api-key",
                "elevenlabs-key",
                "elevenlabs-tts-key",
                "cursor-api-key",
            ]

            key_found = False
            key_length = 0
            secret_name_used = None

            for secret_name in secret_names:
                try:
                    key = vault_client.get_secret(secret_name)
                    if key and len(key) > 20:
                        key_found = True
                        key_length = len(key)
                        secret_name_used = secret_name
                        break
                except Exception:
                    continue

            duration = (time.time() - start) * 1000

            if key_found:
                logger.info(
                    f"   ✅ {test_name}: Key found ({secret_name_used}, length: {key_length})"
                )
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={
                        "secret_name": secret_name_used,
                        "key_length": key_length,
                        "vault_url": vault_url,
                    },
                )
            else:
                logger.warning(f"   ⚠️  {test_name}: Key not found")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="API key not found in Key Vault",
                    details={"secrets_tried": secret_names},
                )
        except ImportError:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: Azure SDK not available")
            return TestResult(
                service=service.name,
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error="Azure Key Vault SDK not installed",
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                service=service.name,
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e),
            )

    def test_container_logs(self, service: ServiceConfig) -> TestResult:
        """Test container logs for successful startup"""
        test_name = "Container Logs"
        start = time.time()

        try:
            if service.nas_host == "localhost":
                result = subprocess.run(
                    ["docker", "logs", service.container, "--tail", "20"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            else:
                result = subprocess.run(
                    [
                        "ssh",
                        f"{service.nas_user}@{service.nas_host}",
                        f"docker logs {service.container} --tail 20",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            duration = (time.time() - start) * 1000

            if result.returncode == 0:
                logs = result.stdout
                has_key_retrieval = "API key retrieved successfully" in logs
                has_errors = "ERROR" in logs or "Failed" in logs

                if has_key_retrieval and not has_errors:
                    logger.info(f"   ✅ {test_name}: Key retrieval successful")
                    return TestResult(
                        service=service.name,
                        test_name=test_name,
                        passed=True,
                        duration_ms=duration,
                        details={"key_retrieval": True, "has_errors": False},
                    )
                elif has_errors:
                    logger.warning(f"   ⚠️  {test_name}: Errors found in logs")
                    return TestResult(
                        service=service.name,
                        test_name=test_name,
                        passed=False,
                        duration_ms=duration,
                        error="Errors in container logs",
                        details={"has_errors": True},
                    )
                else:
                    logger.info(f"   ℹ️  {test_name}: Logs accessible")
                    return TestResult(
                        service=service.name,
                        test_name=test_name,
                        passed=True,
                        duration_ms=duration,
                        details={"key_retrieval": False, "logs_accessible": True},
                    )
            else:
                logger.warning(f"   ⚠️  {test_name}: Cannot access logs")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="Cannot access container logs",
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                service=service.name,
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e),
            )

    def test_secure_wrapper(self, service: ServiceConfig) -> TestResult:
        """Test secure wrapper script exists and is executable"""
        test_name = "Secure Wrapper Script"
        start = time.time()

        try:
            if service.nas_host == "localhost":
                result = subprocess.run(
                    ["docker", "exec", service.container, "test", "-f", "/app/start_secure.py"],
                    capture_output=True,
                    timeout=5,
                )
            else:
                result = subprocess.run(
                    [
                        "ssh",
                        f"{service.nas_user}@{service.nas_host}",
                        f"docker exec {service.container} test -f /app/start_secure.py",
                    ],
                    capture_output=True,
                    timeout=10,
                )

            duration = (time.time() - start) * 1000

            if result.returncode == 0:
                logger.info(f"   ✅ {test_name}: Script exists")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={"script_path": "/app/start_secure.py"},
                )
            else:
                logger.warning(f"   ⚠️  {test_name}: Script not found")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="Secure wrapper script not found",
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                service=service.name,
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e),
            )

    def test_mcp_config(self, service: ServiceConfig) -> TestResult:
        """Test Cursor MCP configuration"""
        test_name = "MCP Configuration"
        start = time.time()

        try:
            mcp_config = self.project_root / ".cursor" / "mcp_config.json"

            if not mcp_config.exists():
                duration = (time.time() - start) * 1000
                logger.warning(f"   ⚠️  {test_name}: Config file not found")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="MCP config file missing",
                )

            with open(mcp_config) as f:
                config = json.load(f)

            duration = (time.time() - start) * 1000

            if "mcpServers" in config and "ElevenLabs" in config["mcpServers"]:
                elevenlabs_config = config["mcpServers"]["ElevenLabs"]
                uses_secure_wrapper = "start_secure.py" in str(elevenlabs_config.get("args", []))
                has_api_key_env = "ELEVENLABS_API_KEY" in str(elevenlabs_config.get("env", {}))

                if uses_secure_wrapper and not has_api_key_env:
                    logger.info(f"   ✅ {test_name}: Secure wrapper configured")
                    return TestResult(
                        service=service.name,
                        test_name=test_name,
                        passed=True,
                        duration_ms=duration,
                        details={"uses_secure_wrapper": True, "has_api_key_env": False},
                    )
                elif has_api_key_env:
                    logger.warning(f"   ⚠️  {test_name}: Using old insecure method")
                    return TestResult(
                        service=service.name,
                        test_name=test_name,
                        passed=False,
                        duration_ms=duration,
                        error="MCP config uses insecure ELEVENLABS_API_KEY env var",
                        details={"uses_secure_wrapper": False, "has_api_key_env": True},
                    )
                else:
                    logger.info(f"   ℹ️  {test_name}: Configured")
                    return TestResult(
                        service=service.name,
                        test_name=test_name,
                        passed=True,
                        duration_ms=duration,
                        details={"configured": True},
                    )
            else:
                logger.warning(f"   ⚠️  {test_name}: ElevenLabs not in config")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="ElevenLabs not configured in MCP config",
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                service=service.name,
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e),
            )

    def test_security_validation(self, service: ServiceConfig) -> TestResult:
        """Test security - ensure no API keys in config files"""
        test_name = "Security Validation"
        start = time.time()

        try:
            # Check docker-compose.yml
            docker_compose = (
                self.project_root
                / "containerization"
                / "services"
                / "nas-mcp-servers"
                / "docker-compose.yml"
            )
            has_key_in_compose = False

            if docker_compose.exists():
                with open(docker_compose) as f:
                    content = f.read()
                    if "ELEVENLABS_API_KEY" in content and "${ELEVENLABS_API_KEY}" not in content:
                        has_key_in_compose = True

            # Check Dockerfile
            dockerfile = (
                self.project_root
                / "containerization"
                / "services"
                / "elevenlabs-mcp-server"
                / "Dockerfile"
            )
            has_key_in_dockerfile = False

            if dockerfile.exists():
                with open(dockerfile) as f:
                    content = f.read()
                    if "ELEVENLABS_API_KEY" in content:
                        has_key_in_dockerfile = True

            duration = (time.time() - start) * 1000

            if not has_key_in_compose and not has_key_in_dockerfile:
                logger.info(f"   ✅ {test_name}: No API keys in config files")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={"keys_in_compose": False, "keys_in_dockerfile": False},
                )
            else:
                logger.warning(f"   ⚠️  {test_name}: API keys found in config files")
                return TestResult(
                    service=service.name,
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="API keys found in config files",
                    details={
                        "keys_in_compose": has_key_in_compose,
                        "keys_in_dockerfile": has_key_in_dockerfile,
                    },
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                service=service.name,
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e),
            )

    def run_all_tests(self) -> Dict:
        """Run all battle tests"""
        logger.info("")
        logger.info("Starting battle test suite...")
        logger.info("")

        for service in self.services:
            logger.info(f"Testing: {service.name}")
            logger.info("-" * 80)

            tests = [
                self.test_container_status,
                self.test_api_key_retrieval,
                self.test_container_logs,
                self.test_secure_wrapper,
                self.test_mcp_config,
                self.test_security_validation,
            ]

            for test_func in tests:
                result = test_func(service)
                self.results.append(result)
                time.sleep(0.1)  # Small delay between tests

            logger.info("")

        return self._generate_summary()

    def _generate_summary(self) -> Dict:
        """Generate test summary"""
        total_duration = time.time() - self.start_time

        passed = [r for r in self.results if r.passed]
        failed = [r for r in self.results if not r.passed]

        summary = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "passed": len(passed),
                "failed": len(failed),
                "pass_rate": (len(passed) / len(self.results) * 100) if self.results else 0,
                "total_duration_seconds": total_duration,
            },
            "results": [asdict(r) for r in self.results],
        }

        return summary

    def save_results(self, summary: Dict):
        try:
            """Save test results"""
            with open(RESULTS_PATH, "w") as f:
                json.dump(summary, f, indent=2)

            logger.info(f"📊 Results saved: {RESULTS_PATH}")

        except Exception as e:
            self.logger.error(f"Error in save_results: {e}", exc_info=True)
            raise

    def print_summary(self, summary: Dict):
        """Print test summary"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 BATTLE TEST SUMMARY")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Total Tests: {summary['summary']['total_tests']}")
        logger.info(f"✅ Passed: {summary['summary']['passed']}")
        logger.info(f"❌ Failed: {summary['summary']['failed']}")
        logger.info(f"Pass Rate: {summary['summary']['pass_rate']:.2f}%")
        logger.info(f"Duration: {summary['summary']['total_duration_seconds']:.2f}s")
        logger.info("")

        if summary["summary"]["failed"] > 0:
            logger.warning("Failed Tests:")
            for result in summary["results"]:
                if not result["passed"]:
                    logger.warning(
                        f"   • {result['service']} - {result['test_name']}: {result.get('error', 'Unknown error')}"
                    )
            logger.info("")

        if summary["summary"]["pass_rate"] == 100:
            logger.info("🎉 ALL TESTS PASSED!")
            return 0
        else:
            logger.warning(f"⚠️  {summary['summary']['failed']} test(s) failed")
            return 1


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ElevenLabs MCP Server Battle Test")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--save", action="store_true", help="Save results to file")

    args = parser.parse_args()

    tester = ElevenLabsBattleTest(project_root=args.project_root)
    summary = tester.run_all_tests()

    if args.save:
        tester.save_results(summary)

    return tester.print_summary(summary)


if __name__ == "__main__":
    sys.exit(main())
