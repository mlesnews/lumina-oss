#!/usr/bin/env python3
"""
@FRB Battleground Sandbox - Full-Robust-Battleground AI Model Testing

Comprehensive AI model testing environment with Azure AI Labs integration.
Load, swap, test, and compare AI models from any source.

Motto: "Test everything. Trust nothing. Validate always."
Philosophy: "AI models must prove themselves in battle before deployment."

Tags: @FRB @AILAB @ULTRON @IRONLEGION #SANDBOX #BATTLEGROUND
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import urllib.request
import urllib.error

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

logger = get_logger("FRBBattleground")


class ModelStatus(Enum):
    """Model availability status"""
    ACTIVE = "active"
    AVAILABLE = "available"
    PENDING = "pending"
    ERROR = "error"
    OFFLINE = "offline"


class TestResult(Enum):
    """Test result status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ModelInfo:
    """AI Model information"""
    name: str
    provider: str
    endpoint: str
    status: ModelStatus
    api_key: Optional[str] = None
    context_length: int = 8192
    specialty: Optional[str] = None
    last_tested: Optional[str] = None
    latency_ms: Optional[float] = None


@dataclass
class TestSuiteResult:
    """Result of a test suite run"""
    suite_name: str
    model_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration_ms: float
    results: List[Dict[str, Any]]
    timestamp: str


class FRBBattlegroundSandbox:
    """
    @FRB Battleground Sandbox

    Full-Robust-Battleground AI Model Testing Environment

    Features:
    - Load models from Azure, OpenAI, Anthropic, Google, Homelab
    - Hot-swap models without restart
    - Run comprehensive test suites
    - A/B compare models
    - Generate detailed reports
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize FRB Battleground Sandbox"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_path = self.project_root / "config" / "frb_battleground_sandbox.json"
        self.data_path = self.project_root / "data" / "frb_battleground"
        self.reports_path = self.data_path / "reports"
        self.logs_path = self.project_root / "logs" / "frb_battleground"

        # Create directories
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Active models
        self.active_model: Optional[ModelInfo] = None
        self.available_models: Dict[str, ModelInfo] = {}
        self.swap_history: List[Dict[str, Any]] = []

        # Test results
        self.test_results: List[TestSuiteResult] = []

        logger.info("🏟️  @FRB Battleground Sandbox initialized")
        logger.info("   Motto: Test everything. Trust nothing. Validate always.")

    def _load_config(self) -> Dict[str, Any]:
        """Load FRB configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Error loading config: {e}")
        return {}

    def _save_config(self):
        """Save configuration"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")

    # ===== MODEL DISCOVERY =====

    def discover_homelab_models(self) -> Dict[str, List[ModelInfo]]:
        """Discover available models from homelab endpoints"""
        logger.info("🔍 Discovering homelab models...")

        discovered = {
            "kaiju": [],
            "localhost": [],
            "nas": []
        }

        endpoints = {
            "kaiju": "http://<NAS_IP>:3001",
            "localhost": "http://localhost:11434",
            "nas": "http://<NAS_PRIMARY_IP>:11434"
        }

        for location, endpoint in endpoints.items():
            try:
                url = f"{endpoint}/api/tags"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read())
                    models = data.get("models", [])

                    for model in models:
                        model_name = model.get("name", "unknown")
                        model_info = ModelInfo(
                            name=model_name,
                            provider=f"ollama-{location}",
                            endpoint=endpoint,
                            status=ModelStatus.ACTIVE,
                            context_length=model.get("details", {}).get("parameter_size", 8192)
                        )
                        discovered[location].append(model_info)
                        self.available_models[f"{location}/{model_name}"] = model_info

                    logger.info(f"   ✅ {location}: {len(models)} models found")

            except Exception as e:
                logger.warning(f"   ⚠️  {location} ({endpoint}): Connection failed - {e}")
                discovered[location] = []

        return discovered

    def discover_cloud_models(self) -> Dict[str, List[ModelInfo]]:
        """Discover configured cloud models (Azure, OpenAI, Anthropic)"""
        logger.info("☁️  Checking cloud model configurations...")

        discovered = {}

        # Azure OpenAI
        azure_config = self.config.get("azure_ai_labs_integration", {}).get("services", {}).get("azure_openai", {})
        if azure_config.get("enabled"):
            discovered["azure_openai"] = []
            for deployment_name, deployment in azure_config.get("deployments", {}).items():
                model_info = ModelInfo(
                    name=deployment.get("model", deployment_name),
                    provider="azure_openai",
                    endpoint=azure_config.get("endpoint", ""),
                    status=ModelStatus.AVAILABLE if deployment.get("status") == "available" else ModelStatus.PENDING,
                    context_length=deployment.get("max_tokens", 128000)
                )
                discovered["azure_openai"].append(model_info)
                self.available_models[f"azure/{deployment_name}"] = model_info
            logger.info(f"   ✅ Azure OpenAI: {len(discovered['azure_openai'])} deployments configured")

        # Check model registry from config
        registry = self.config.get("model_registry", {}).get("categories", {})

        for provider in ["anthropic", "openai_direct", "google"]:
            provider_models = registry.get("cloud_providers", {}).get(provider, [])
            if provider_models:
                discovered[provider] = []
                for model in provider_models:
                    model_info = ModelInfo(
                        name=model.get("name"),
                        provider=model.get("provider", provider),
                        endpoint="api",
                        status=ModelStatus.AVAILABLE if model.get("status") == "active" else ModelStatus.PENDING
                    )
                    discovered[provider].append(model_info)
                    self.available_models[f"{provider}/{model.get('name')}"] = model_info
                logger.info(f"   ✅ {provider}: {len(discovered[provider])} models configured")

        return discovered

    def discover_all_models(self) -> Dict[str, Any]:
        """Discover all available models"""
        logger.info("=" * 60)
        logger.info("🏟️  @FRB BATTLEGROUND - Model Discovery")
        logger.info("=" * 60)

        result = {
            "homelab": self.discover_homelab_models(),
            "cloud": self.discover_cloud_models(),
            "total_models": len(self.available_models),
            "timestamp": datetime.now().isoformat()
        }

        logger.info("")
        logger.info(f"📊 Total models discovered: {result['total_models']}")

        return result

    # ===== MODEL LOADING & SWAPPING =====

    def load_model(self, model_key: str) -> bool:
        """Load a model as the active model"""
        logger.info(f"📥 Loading model: {model_key}")

        if model_key not in self.available_models:
            # Try to find by name
            for key, model in self.available_models.items():
                if model.name == model_key or key.endswith(f"/{model_key}"):
                    model_key = key
                    break
            else:
                logger.error(f"❌ Model not found: {model_key}")
                return False

        model = self.available_models[model_key]

        # Test connectivity
        if self._test_model_connectivity(model):
            self.active_model = model
            logger.info(f"   ✅ Model loaded: {model.name} ({model.provider})")
            return True
        else:
            logger.error(f"   ❌ Model not reachable: {model.name}")
            return False

    def swap_model(self, new_model_key: str, reason: str = "manual") -> bool:
        """Hot-swap to a different model"""
        old_model = self.active_model

        logger.info(f"🔄 Swapping model: {old_model.name if old_model else 'None'} → {new_model_key}")

        if self.load_model(new_model_key):
            # Record swap
            swap_record = {
                "timestamp": datetime.now().isoformat(),
                "from_model": old_model.name if old_model else None,
                "to_model": self.active_model.name,
                "reason": reason
            }
            self.swap_history.append(swap_record)

            logger.info(f"   ✅ Swap complete: Now using {self.active_model.name}")
            return True
        else:
            logger.error(f"   ❌ Swap failed")
            return False

    def _test_model_connectivity(self, model: ModelInfo) -> bool:
        """Test if a model is reachable"""
        if model.provider.startswith("ollama"):
            try:
                url = f"{model.endpoint}/api/tags"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    return response.status == 200
            except Exception:
                return False

        # For cloud models, assume available if configured
        return model.status in [ModelStatus.ACTIVE, ModelStatus.AVAILABLE]

    # ===== TESTING =====

    def run_connectivity_test(self, model_key: Optional[str] = None) -> Dict[str, Any]:
        """Test model connectivity and latency"""
        if model_key:
            models_to_test = {model_key: self.available_models.get(model_key)}
        else:
            models_to_test = self.available_models

        results = {}

        for key, model in models_to_test.items():
            if model is None:
                continue

            start = time.time()
            reachable = self._test_model_connectivity(model)
            latency = (time.time() - start) * 1000

            results[key] = {
                "name": model.name,
                "provider": model.provider,
                "endpoint": model.endpoint,
                "reachable": reachable,
                "latency_ms": round(latency, 2),
                "status": "✅" if reachable else "❌"
            }

            model.latency_ms = latency
            model.status = ModelStatus.ACTIVE if reachable else ModelStatus.OFFLINE

        return results

    def run_basic_test_suite(self, model_key: str) -> TestSuiteResult:
        """Run basic capability test suite on a model"""
        logger.info(f"🧪 Running basic test suite on: {model_key}")

        start_time = time.time()
        results = []

        # Test: Connectivity
        conn_result = self.run_connectivity_test(model_key)
        model_conn = conn_result.get(model_key, {})

        results.append({
            "test": "connectivity",
            "result": TestResult.PASSED.value if model_conn.get("reachable") else TestResult.FAILED.value,
            "latency_ms": model_conn.get("latency_ms"),
            "details": model_conn
        })

        # Test: API Format (for Ollama models)
        model = self.available_models.get(model_key)
        if model and model.provider.startswith("ollama"):
            try:
                # Test v1/models endpoint (OpenAI compatible)
                url = f"{model.endpoint}/v1/models"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read())
                    results.append({
                        "test": "openai_compatible_api",
                        "result": TestResult.PASSED.value,
                        "details": {"models_count": len(data.get("data", []))}
                    })
            except Exception as e:
                results.append({
                    "test": "openai_compatible_api",
                    "result": TestResult.FAILED.value,
                    "error": str(e)
                })

        duration = (time.time() - start_time) * 1000

        passed = sum(1 for r in results if r["result"] == TestResult.PASSED.value)
        failed = sum(1 for r in results if r["result"] == TestResult.FAILED.value)
        skipped = sum(1 for r in results if r["result"] == TestResult.SKIPPED.value)

        suite_result = TestSuiteResult(
            suite_name="basic_capability",
            model_name=model_key,
            total_tests=len(results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration_ms=round(duration, 2),
            results=results,
            timestamp=datetime.now().isoformat()
        )

        self.test_results.append(suite_result)

        logger.info(f"   📊 Results: {passed}/{len(results)} passed ({duration:.0f}ms)")

        return suite_result

    # ===== REPORTING =====

    def generate_report(self, format: str = "json") -> Path:
        try:
            """Generate battleground test report"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            report_data = {
                "report_type": "FRB Battleground Report",
                "generated_at": datetime.now().isoformat(),
                "active_model": asdict(self.active_model) if self.active_model else None,
                "total_models_discovered": len(self.available_models),
                "models": {k: asdict(v) for k, v in self.available_models.items()},
                "swap_history": self.swap_history,
                "test_results": [asdict(r) for r in self.test_results]
            }

            # Fix enum serialization
            def fix_enums(obj):
                if isinstance(obj, dict):
                    return {k: fix_enums(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [fix_enums(v) for v in obj]
                elif isinstance(obj, Enum):
                    return obj.value
                return obj

            report_data = fix_enums(report_data)

            if format == "json":
                report_path = self.reports_path / f"frb_report_{timestamp}.json"
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)

            elif format == "markdown":
                report_path = self.reports_path / f"frb_report_{timestamp}.md"
                md_content = self._generate_markdown_report(report_data)
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

            logger.info(f"📄 Report generated: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate markdown report"""
        lines = [
            "# @FRB Battleground Report",
            "",
            f"**Generated:** {data['generated_at']}",
            f"**Total Models:** {data['total_models_discovered']}",
            "",
            "## Active Model",
            "",
        ]

        if data["active_model"]:
            lines.append(f"- **Name:** {data['active_model']['name']}")
            lines.append(f"- **Provider:** {data['active_model']['provider']}")
            lines.append(f"- **Endpoint:** {data['active_model']['endpoint']}")
        else:
            lines.append("*No active model*")

        lines.extend([
            "",
            "## Available Models",
            "",
            "| Model | Provider | Endpoint | Status |",
            "|-------|----------|----------|--------|"
        ])

        for key, model in data["models"].items():
            lines.append(f"| {model['name']} | {model['provider']} | {model['endpoint']} | {model['status']} |")

        lines.extend([
            "",
            "## Test Results",
            ""
        ])

        for result in data["test_results"]:
            lines.append(f"### {result['suite_name']} - {result['model_name']}")
            lines.append(f"- **Passed:** {result['passed']}/{result['total_tests']}")
            lines.append(f"- **Duration:** {result['duration_ms']}ms")
            lines.append("")

        lines.extend([
            "",
            "---",
            "*@FRB Battleground Sandbox - Test everything. Trust nothing. Validate always.*"
        ])

        return "\n".join(lines)

    # ===== STATUS =====

    def get_status(self) -> Dict[str, Any]:
        """Get current battleground status"""
        return {
            "active_model": self.active_model.name if self.active_model else None,
            "total_models": len(self.available_models),
            "homelab_online": sum(1 for m in self.available_models.values() 
                                  if m.provider.startswith("ollama") and m.status == ModelStatus.ACTIVE),
            "cloud_configured": sum(1 for m in self.available_models.values() 
                                    if not m.provider.startswith("ollama")),
            "swap_count": len(self.swap_history),
            "test_runs": len(self.test_results)
        }

    def print_status(self):
        """Print formatted status"""
        status = self.get_status()

        print("")
        print("=" * 60)
        print("  🏟️  @FRB BATTLEGROUND STATUS")
        print("=" * 60)
        print(f"  Active Model:     {status['active_model'] or 'None'}")
        print(f"  Total Models:     {status['total_models']}")
        print(f"  Homelab Online:   {status['homelab_online']}")
        print(f"  Cloud Configured: {status['cloud_configured']}")
        print(f"  Model Swaps:      {status['swap_count']}")
        print(f"  Test Runs:        {status['test_runs']}")
        print("=" * 60)
        print("")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="@FRB Battleground Sandbox - AI Model Testing"
    )
    parser.add_argument("--discover", action="store_true", help="Discover all available models")
    parser.add_argument("--test", type=str, help="Run tests on specified model")
    parser.add_argument("--load", type=str, help="Load specified model as active")
    parser.add_argument("--swap", type=str, help="Swap to specified model")
    parser.add_argument("--status", action="store_true", help="Show battleground status")
    parser.add_argument("--report", type=str, choices=["json", "markdown"], help="Generate report")
    parser.add_argument("--connectivity", action="store_true", help="Test connectivity to all models")

    args = parser.parse_args()

    sandbox = FRBBattlegroundSandbox()

    if args.discover:
        sandbox.discover_all_models()

    if args.connectivity:
        results = sandbox.run_connectivity_test()
        print("\n📡 Connectivity Results:")
        for key, result in results.items():
            print(f"   {result['status']} {key}: {result['latency_ms']}ms")

    if args.test:
        sandbox.discover_all_models()
        sandbox.run_basic_test_suite(args.test)

    if args.load:
        sandbox.discover_all_models()
        sandbox.load_model(args.load)

    if args.swap:
        sandbox.discover_all_models()
        sandbox.swap_model(args.swap)

    if args.report:
        sandbox.generate_report(args.report)

    if args.status or not any([args.discover, args.test, args.load, args.swap, args.report, args.connectivity]):
        sandbox.discover_all_models()
        sandbox.print_status()


if __name__ == "__main__":


    main()