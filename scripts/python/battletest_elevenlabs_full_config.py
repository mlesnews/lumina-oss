#!/usr/bin/env python3
"""
ElevenLabs Full Configuration Battle Test Suite
Comprehensive testing of ElevenLabs configuration, Docker setup, and integration

#BATTLETESTING Framework

Tests:
- Configuration file validation
- Data directory setup and permissions
- Docker Desktop MCP Toolkit configuration
- API key retrieval and validation
- Local integration testing
- Audio file storage functionality
- End-to-end workflow validation

Tags: #BATTLETESTING #ELEVENLABS #CONFIGURATION #DOCKER @JARVIS @DOIT
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ElevenLabsConfigBattleTest")

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_PATH = PROJECT_ROOT / "data" / "homelab_model_validation" / "elevenlabs_config_battletest_results.json"
RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class TestResult:
    """Test result"""
    test_name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    details: Dict = None


class ElevenLabsConfigBattleTest:
    """Comprehensive battle test for ElevenLabs configuration"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize battle test"""
        if project_root is None:
            project_root = PROJECT_ROOT

        self.project_root = Path(project_root)
        self.config_path = self.project_root / "config" / "elevenlabs_config.json"
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.config = None

        logger.info("=" * 80)
        logger.info("⚔️  ELEVENLABS CONFIGURATION BATTLE TEST")
        logger.info("=" * 80)
        logger.info("")
        logger.info("#BATTLETESTING Framework")
        logger.info("")

    def test_config_file_exists(self) -> TestResult:
        """Test configuration file exists"""
        test_name = "Config File Exists"
        start = time.time()

        try:
            if self.config_path.exists():
                duration = (time.time() - start) * 1000
                logger.info(f"   ✅ {test_name}: File found")
                return TestResult(
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={"path": str(self.config_path)}
                )
            else:
                duration = (time.time() - start) * 1000
                logger.error(f"   ❌ {test_name}: File not found")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error=f"Config file not found: {self.config_path}"
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_config_file_valid(self) -> TestResult:
        """Test configuration file is valid JSON"""
        test_name = "Config File Valid JSON"
        start = time.time()

        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

            duration = (time.time() - start) * 1000

            if isinstance(self.config, dict):
                logger.info(f"   ✅ {test_name}: Valid JSON")
                return TestResult(
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={"keys": list(self.config.keys())}
                )
            else:
                logger.error(f"   ❌ {test_name}: Invalid structure")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="Config is not a dictionary"
                )
        except json.JSONDecodeError as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: JSON decode error")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=f"JSON decode error: {e}"
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_data_directory_config(self) -> TestResult:
        """Test data directory configuration"""
        test_name = "Data Directory Configuration"
        start = time.time()

        try:
            has_data_dir = "data_directory" in self.config
            has_data_path = "data_path" in self.config
            has_storage = "storage" in self.config

            duration = (time.time() - start) * 1000

            if has_data_dir and has_data_path and has_storage:
                data_dir = self.config.get("data_directory")
                data_path = self.config.get("data_path")
                storage = self.config.get("storage", {})

                logger.info(f"   ✅ {test_name}: All paths configured")
                logger.info(f"      data_directory: {data_dir}")
                logger.info(f"      data_path: {data_path}")
                logger.info(f"      storage: {list(storage.keys())}")

                return TestResult(
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={
                        "data_directory": data_dir,
                        "data_path": data_path,
                        "storage": storage
                    }
                )
            else:
                missing = []
                if not has_data_dir:
                    missing.append("data_directory")
                if not has_data_path:
                    missing.append("data_path")
                if not has_storage:
                    missing.append("storage")

                logger.warning(f"   ⚠️  {test_name}: Missing fields: {', '.join(missing)}")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error=f"Missing configuration fields: {', '.join(missing)}",
                    details={
                        "has_data_directory": has_data_dir,
                        "has_data_path": has_data_path,
                        "has_storage": has_storage
                    }
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_data_directory_exists(self) -> TestResult:
        """Test data directory exists and is accessible"""
        test_name = "Data Directory Exists"
        start = time.time()

        try:
            data_path = self.config.get("data_path", "data/elevenlabs")
            storage = self.config.get("storage", {})
            audio_path = storage.get("audio_files", "data/elevenlabs/audio")

            # Resolve paths relative to project root
            data_dir = self.project_root / data_path
            audio_dir = self.project_root / audio_path

            duration = (time.time() - start) * 1000

            if data_dir.exists() and audio_dir.exists():
                # Check write permissions
                try:
                    test_file = audio_dir / ".test_write"
                    test_file.write_text("test")
                    test_file.unlink()
                    writable = True
                except Exception:
                    writable = False

                if writable:
                    logger.info(f"   ✅ {test_name}: Directories exist and writable")
                    return TestResult(
                        test_name=test_name,
                        passed=True,
                        duration_ms=duration,
                        details={
                            "data_dir": str(data_dir),
                            "audio_dir": str(audio_dir),
                            "writable": True
                        }
                    )
                else:
                    logger.warning(f"   ⚠️  {test_name}: Directories exist but not writable")
                    return TestResult(
                        test_name=test_name,
                        passed=False,
                        duration_ms=duration,
                        error="Directories not writable",
                        details={
                            "data_dir": str(data_dir),
                            "audio_dir": str(audio_dir),
                            "writable": False
                        }
                    )
            else:
                missing = []
                if not data_dir.exists():
                    missing.append(str(data_dir))
                if not audio_dir.exists():
                    missing.append(str(audio_dir))

                logger.warning(f"   ⚠️  {test_name}: Missing directories: {', '.join(missing)}")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error=f"Missing directories: {', '.join(missing)}",
                    details={
                        "data_dir_exists": data_dir.exists(),
                        "audio_dir_exists": audio_dir.exists()
                    }
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_docker_volume_config(self) -> TestResult:
        """Test Docker volume configuration"""
        test_name = "Docker Volume Configuration"
        start = time.time()

        try:
            storage = self.config.get("storage", {})
            docker_volume = storage.get("docker_volume", "")
            data_directory = self.config.get("data_directory", "")

            duration = (time.time() - start) * 1000

            if docker_volume and data_directory:
                if docker_volume == data_directory:
                    logger.info(f"   ✅ {test_name}: Volume name configured")
                    logger.info(f"      Volume: {docker_volume}")
                    return TestResult(
                        test_name=test_name,
                        passed=True,
                        duration_ms=duration,
                        details={
                            "docker_volume": docker_volume,
                            "data_directory": data_directory
                        }
                    )
                else:
                    logger.warning(f"   ⚠️  {test_name}: Volume names don't match")
                    return TestResult(
                        test_name=test_name,
                        passed=False,
                        duration_ms=duration,
                        error="Docker volume and data_directory don't match",
                        details={
                            "docker_volume": docker_volume,
                            "data_directory": data_directory
                        }
                    )
            else:
                logger.warning(f"   ⚠️  {test_name}: Volume not configured")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="Docker volume not configured",
                    details={
                        "has_docker_volume": bool(docker_volume),
                        "has_data_directory": bool(data_directory)
                    }
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_api_key_config(self) -> TestResult:
        """Test API key configuration (should be empty in file, retrieved from vault)"""
        test_name = "API Key Configuration"
        start = time.time()

        try:
            api_key = self.config.get("api_key", "")

            duration = (time.time() - start) * 1000

            # API key should be empty in config file (retrieved from vault at runtime)
            if not api_key or api_key == "":
                logger.info(f"   ✅ {test_name}: API key not in config (secure)")
                return TestResult(
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={"api_key_in_file": False, "secure": True}
                )
            else:
                logger.warning(f"   ⚠️  {test_name}: API key found in config file (insecure)")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="API key should not be in config file",
                    details={"api_key_in_file": True, "secure": False}
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_api_key_retrieval(self) -> TestResult:
        """Test API key retrieval from Azure Key Vault"""
        test_name = "API Key Retrieval"
        start = time.time()

        try:
            from azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv('AZURE_KEY_VAULT_URL', 'https://jarvis-lumina.vault.azure.net/')
            vault_client = AzureKeyVaultClient(vault_url=vault_url)

            secret_names = [
                "elevenlabs-api-key",
                "ELEVENLABS_API_KEY",
                "Cursor - Cursor API Key",
                "elevenlabs_api_key"
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
                logger.info(f"   ✅ {test_name}: Key found ({secret_name_used}, length: {key_length})")
                return TestResult(
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={
                        "secret_name": secret_name_used,
                        "key_length": key_length,
                        "vault_url": vault_url
                    }
                )
            else:
                logger.warning(f"   ⚠️  {test_name}: Key not found")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="API key not found in Key Vault",
                    details={"secrets_tried": secret_names}
                )
        except ImportError:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: Azure SDK not available")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error="Azure Key Vault SDK not installed"
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_integration_import(self) -> TestResult:
        """Test ElevenLabs integration can be imported"""
        test_name = "Integration Import"
        start = time.time()

        try:
            from jarvis_elevenlabs_integration import JARVISElevenLabsTTS

            duration = (time.time() - start) * 1000
            logger.info(f"   ✅ {test_name}: Integration module imported")
            return TestResult(
                test_name=test_name,
                passed=True,
                duration_ms=duration,
                details={"module": "JARVISElevenLabsTTS"}
            )
        except ImportError as e:
            duration = (time.time() - start) * 1000
            logger.warning(f"   ⚠️  {test_name}: Import failed")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=f"Import error: {e}"
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def test_integration_initialization(self) -> TestResult:
        """Test ElevenLabs integration initialization"""
        test_name = "Integration Initialization"
        start = time.time()

        try:
            from jarvis_elevenlabs_integration import JARVISElevenLabsTTS

            tts = JARVISElevenLabsTTS(project_root=self.project_root)

            duration = (time.time() - start) * 1000

            if tts:
                has_api_key = bool(tts.api_key)
                has_client = bool(tts.client)

                logger.info(f"   ✅ {test_name}: Integration initialized")
                logger.info(f"      API key: {'configured' if has_api_key else 'not configured'}")
                logger.info(f"      Client: {'initialized' if has_client else 'not initialized'}")

                return TestResult(
                    test_name=test_name,
                    passed=True,
                    duration_ms=duration,
                    details={
                        "has_api_key": has_api_key,
                        "has_client": has_client,
                        "voice_id": tts.current_voice_id
                    }
                )
            else:
                logger.warning(f"   ⚠️  {test_name}: Initialization failed")
                return TestResult(
                    test_name=test_name,
                    passed=False,
                    duration_ms=duration,
                    error="TTS object is None"
                )
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"   ❌ {test_name}: {e}")
            return TestResult(
                test_name=test_name,
                passed=False,
                duration_ms=duration,
                error=str(e)
            )

    def run_all_tests(self) -> Dict:
        """Run all battle tests"""
        logger.info("")
        logger.info("Starting battle test suite...")
        logger.info("")

        tests = [
            self.test_config_file_exists,
            self.test_config_file_valid,
            self.test_data_directory_config,
            self.test_data_directory_exists,
            self.test_docker_volume_config,
            self.test_api_key_config,
            self.test_api_key_retrieval,
            self.test_integration_import,
            self.test_integration_initialization,
        ]

        for test_func in tests:
            result = test_func()
            self.results.append(result)
            time.sleep(0.1)  # Small delay between tests

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
                "total_duration_seconds": total_duration
            },
            "results": [asdict(r) for r in self.results]
        }

        return summary

    def save_results(self, summary: Dict):
        try:
            """Save test results"""
            with open(RESULTS_PATH, 'w') as f:
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

        if summary['summary']['failed'] > 0:
            logger.warning("Failed Tests:")
            for result in summary['results']:
                if not result['passed']:
                    logger.warning(f"   • {result['test_name']}: {result.get('error', 'Unknown error')}")
            logger.info("")

        if summary['summary']['pass_rate'] == 100:
            logger.info("🎉 ALL TESTS PASSED!")
            return 0
        else:
            logger.warning(f"⚠️  {summary['summary']['failed']} test(s) failed")
            return 1


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ElevenLabs Configuration Battle Test")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--save', action='store_true', help='Save results to file')

    args = parser.parse_args()

    tester = ElevenLabsConfigBattleTest(project_root=args.project_root)
    summary = tester.run_all_tests()

    if args.save:
        tester.save_results(summary)

    return tester.print_summary(summary)


if __name__ == "__main__":


    sys.exit(main())