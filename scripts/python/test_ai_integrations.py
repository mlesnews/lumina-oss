#!/usr/bin/env python3
"""
LUMINA AI Integrations Test Suite

Comprehensive testing for all AI provider integrations:
- Local models (ULTRON, Iron Legion)
- GitHub Models API
- Multi-provider routing
- Token pool management
- Cursor IDE integration

Tags: #AI #TESTING #INTEGRATION #GITHUB #ULTRON #ROUTING @LUMINA
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from github_ai_provider import GitHubAIProvider
    from ultron_cluster_router_api import cluster, github_provider
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    GitHubAIProvider = None

logger = get_logger("AITestSuite")


class AITestSuite:
    """
    Comprehensive AI Integration Test Suite

    Tests all AI providers and routing systems in LUMINA.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize test suite"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.results: Dict[str, Any] = {
            "timestamp": time.time(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": {}
        }

        logger.info("🧪 AI Integration Test Suite initialized")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🚀 LUMINA AI INTEGRATION TEST SUITE")
        print("="*80)

        # Test 1: Local AI Systems
        self.test_local_ai_systems()

        # Test 2: ULTRON Cluster Router
        self.test_ultron_cluster_router()

        # Test 3: GitHub AI Provider
        self.test_github_ai_provider()

        # Test 4: Multi-Provider Routing
        self.test_multi_provider_routing()

        # Test 5: Token Pool Management
        self.test_token_pool_management()

        # Test 6: Cursor IDE Integration
        self.test_cursor_integration()

        # Summary
        self.print_summary()

        return self.results

    def test_local_ai_systems(self):
        """Test local AI systems (Ollama, ULTRON)"""
        print("\n🔬 Testing Local AI Systems...")

        test_name = "local_ai_systems"
        self.results["test_details"][test_name] = {"status": "running", "checks": {}}

        # Check Ollama service
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.results["test_details"][test_name]["checks"]["ollama_service"] = {
                    "status": "pass",
                    "message": f"Ollama running with {len(models)} models"
                }
            else:
                self.results["test_details"][test_name]["checks"]["ollama_service"] = {
                    "status": "fail",
                    "message": f"Ollama responded with status {response.status_code}"
                }
        except Exception as e:
            self.results["test_details"][test_name]["checks"]["ollama_service"] = {
                "status": "fail",
                "message": f"Cannot connect to Ollama: {e}"
            }

        # Check NAS Ollama (Iron Legion)
        try:
            response = requests.get("http://<NAS_PRIMARY_IP>:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.results["test_details"][test_name]["checks"]["nas_ollama"] = {
                    "status": "pass",
                    "message": f"NAS Ollama running with {len(models)} models"
                }
            else:
                self.results["test_details"][test_name]["checks"]["nas_ollama"] = {
                    "status": "fail",
                    "message": f"NAS Ollama responded with status {response.status_code}"
                }
        except Exception as e:
            self.results["test_details"][test_name]["checks"]["nas_ollama"] = {
                "status": "warn",
                "message": f"NAS Ollama not accessible: {e}"
            }

        self._update_test_status(test_name)

    def test_ultron_cluster_router(self):
        """Test ULTRON Cluster Router API"""
        print("🔬 Testing ULTRON Cluster Router...")

        test_name = "ultron_cluster_router"
        self.results["test_details"][test_name] = {"status": "running", "checks": {}}

        # Check health endpoint
        try:
            response = requests.get("http://<NAS_IP>:8080/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.results["test_details"][test_name]["checks"]["health_endpoint"] = {
                    "status": "pass",
                    "message": f"Router healthy: {health_data.get('status', 'unknown')}"
                }
            else:
                self.results["test_details"][test_name]["checks"]["health_endpoint"] = {
                    "status": "fail",
                    "message": f"Health check failed: {response.status_code}"
                }
        except Exception as e:
            self.results["test_details"][test_name]["checks"]["health_endpoint"] = {
                "status": "fail",
                "message": f"Cannot connect to router: {e}"
            }

        # Test local model routing
        try:
            payload = {
                "model": "qwen2.5-coder:7b",
                "messages": [{"role": "user", "content": "Hello from test suite"}],
                "max_tokens": 50
            }
            response = requests.post("http://<NAS_IP>:8080/api/chat",
                                   json=payload, timeout=30)
            if response.status_code == 200:
                self.results["test_details"][test_name]["checks"]["local_routing"] = {
                    "status": "pass",
                    "message": "Local model routing works"
                }
            else:
                self.results["test_details"][test_name]["checks"]["local_routing"] = {
                    "status": "fail",
                    "message": f"Local routing failed: {response.status_code}"
                }
        except Exception as e:
            self.results["test_details"][test_name]["checks"]["local_routing"] = {
                "status": "fail",
                "message": f"Local routing error: {e}"
            }

        self._update_test_status(test_name)

    def test_github_ai_provider(self):
        """Test GitHub AI Provider"""
        print("🔬 Testing GitHub AI Provider...")

        test_name = "github_ai_provider"
        self.results["test_details"][test_name] = {"status": "running", "checks": {}}

        if not GitHubAIProvider:
            self.results["test_details"][test_name]["checks"]["provider_available"] = {
                "status": "fail",
                "message": "GitHubAIProvider not available"
            }
            self._update_test_status(test_name)
            return

        # Check GitHub provider status
        try:
            response = requests.get("http://<NAS_IP>:8080/api/github/status", timeout=10)
            if response.status_code == 200:
                status_data = response.json()
                available = status_data.get("available", False)
                tokens_remaining = status_data.get("remaining_tokens", 0)

                self.results["test_details"][test_name]["checks"]["provider_status"] = {
                    "status": "pass" if available else "warn",
                    "message": f"Provider {'available' if available else 'unavailable'}, {tokens_remaining} tokens remaining"
                }
            else:
                self.results["test_details"][test_name]["checks"]["provider_status"] = {
                    "status": "fail",
                    "message": f"Status check failed: {response.status_code}"
                }
        except Exception as e:
            self.results["test_details"][test_name]["checks"]["provider_status"] = {
                "status": "fail",
                "message": f"Cannot check status: {e}"
            }

        # Test GitHub model routing (if available)
        if self.results["test_details"][test_name]["checks"]["provider_status"]["status"] in ["pass", "warn"]:
            try:
                payload = {
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Hello from AI test suite"}],
                    "max_tokens": 50
                }
                response = requests.post("http://<NAS_IP>:8080/api/chat",
                                       json=payload, timeout=60)
                if response.status_code == 200:
                    self.results["test_details"][test_name]["checks"]["github_routing"] = {
                        "status": "pass",
                        "message": "GitHub model routing works"
                    }
                else:
                    self.results["test_details"][test_name]["checks"]["github_routing"] = {
                        "status": "fail",
                        "message": f"GitHub routing failed: {response.status_code}"
                    }
            except Exception as e:
                self.results["test_details"][test_name]["checks"]["github_routing"] = {
                    "status": "fail",
                    "message": f"GitHub routing error: {e}"
                }

        self._update_test_status(test_name)

    def test_multi_provider_routing(self):
        """Test multi-provider routing logic"""
        print("🔬 Testing Multi-Provider Routing...")

        test_name = "multi_provider_routing"
        self.results["test_details"][test_name] = {"status": "running", "checks": {}}

        # Test model detection and routing
        test_models = [
            ("qwen2.5-coder:7b", "local"),
            ("llama3.2:3b", "local"),
            ("openai/gpt-4o", "github"),
            ("anthropic/claude-3-5-sonnet", "github")
        ]

        for model, expected_provider in test_models:
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": f"Test from {model}"}],
                    "max_tokens": 20
                }
                response = requests.post("http://<NAS_IP>:8080/api/chat",
                                       json=payload, timeout=30)

                if response.status_code == 200:
                    self.results["test_details"][test_name]["checks"][f"{model}_routing"] = {
                        "status": "pass",
                        "message": f"{model} routed successfully"
                    }
                else:
                    self.results["test_details"][test_name]["checks"][f"{model}_routing"] = {
                        "status": "fail",
                        "message": f"{model} routing failed: {response.status_code}"
                    }
            except Exception as e:
                self.results["test_details"][test_name]["checks"][f"{model}_routing"] = {
                    "status": "fail",
                    "message": f"{model} routing error: {e}"
                }

        self._update_test_status(test_name)

    def test_token_pool_management(self):
        """Test token pool management"""
        print("🔬 Testing Token Pool Management...")

        test_name = "token_pool_management"
        self.results["test_details"][test_name] = {"status": "running", "checks": {}}

        # Check GitHub token pool status
        try:
            response = requests.get("http://<NAS_IP>:8080/api/github/status", timeout=10)
            if response.status_code == 200:
                status_data = response.json()
                usage_percent = status_data.get("usage_percent", 0)
                emergency_mode = status_data.get("emergency_mode", False)

                self.results["test_details"][test_name]["checks"]["token_tracking"] = {
                    "status": "pass",
                    "message": f"Token pool tracking active: {usage_percent}% used, emergency: {emergency_mode}"
                }
            else:
                self.results["test_details"][test_name]["checks"]["token_tracking"] = {
                    "status": "fail",
                    "message": f"Cannot check token pool: {response.status_code}"
                }
        except Exception as e:
            self.results["test_details"][test_name]["checks"]["token_tracking"] = {
                "status": "fail",
                "message": f"Token pool check error: {e}"
            }

        self._update_test_status(test_name)

    def test_cursor_integration(self):
        """Test Cursor IDE integration"""
        print("🔬 Testing Cursor IDE Integration...")

        test_name = "cursor_integration"
        self.results["test_details"][test_name] = {"status": "running", "checks": {}}

        # Check if Cursor models config exists and has GitHub models
        config_file = self.project_root / "data" / "cursor_models" / "cursor_models_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)

                composer_models = config.get("cursor.composer.customModels", [])
                github_models = [m for m in composer_models if "github" in m.get("name", "").lower()]

                if github_models:
                    self.results["test_details"][test_name]["checks"]["cursor_config"] = {
                        "status": "pass",
                        "message": f"Found {len(github_models)} GitHub models in Cursor config"
                    }
                else:
                    self.results["test_details"][test_name]["checks"]["cursor_config"] = {
                        "status": "fail",
                        "message": "No GitHub models found in Cursor config"
                    }
            except Exception as e:
                self.results["test_details"][test_name]["checks"]["cursor_config"] = {
                    "status": "fail",
                    "message": f"Cannot read Cursor config: {e}"
                }
        else:
            self.results["test_details"][test_name]["checks"]["cursor_config"] = {
                "status": "fail",
                "message": "Cursor models config file not found"
            }

        self._update_test_status(test_name)

    def _update_test_status(self, test_name: str):
        """Update test status based on checks"""
        checks = self.results["test_details"][test_name]["checks"]
        failed_checks = [k for k, v in checks.items() if v["status"] == "fail"]
        warn_checks = [k for k, v in checks.items() if v["status"] == "warn"]

        if failed_checks:
            self.results["test_details"][test_name]["status"] = "fail"
            self.results["tests_failed"] += 1
        elif warn_checks:
            self.results["test_details"][test_name]["status"] = "warn"
            self.results["tests_passed"] += 1  # Warnings count as passed
        else:
            self.results["test_details"][test_name]["status"] = "pass"
            self.results["tests_passed"] += 1

        self.results["tests_run"] += 1

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 TEST SUITE SUMMARY")
        print("="*80)

        print(f"Tests Run: {self.results['tests_run']}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")

        overall_status = "✅ ALL TESTS PASSED" if self.results['tests_failed'] == 0 else "❌ SOME TESTS FAILED"

        print(f"\nOverall Status: {overall_status}")

        print("\nDetailed Results:")
        for test_name, test_data in self.results["test_details"].items():
            status = test_data["status"]
            status_icon = {"pass": "✅", "fail": "❌", "warn": "⚠️"}.get(status, "❓")
            print(f"  {status_icon} {test_name.replace('_', ' ').title()}")

            for check_name, check_data in test_data["checks"].items():
                check_status = check_data["status"]
                check_icon = {"pass": "✅", "fail": "❌", "warn": "⚠️"}.get(check_status, "❓")
                print(f"    {check_icon} {check_name.replace('_', ' ').title()}: {check_data['message']}")

        # Save results
        results_file = self.project_root / "data" / "test_results" / f"ai_integration_test_{int(time.time())}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Detailed results saved to: {results_file}")


def main():
    """Main test entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Integration Test Suite for LUMINA")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--local", action="store_true", help="Test local AI systems only")
    parser.add_argument("--router", action="store_true", help="Test ULTRON router only")
    parser.add_argument("--github", action="store_true", help="Test GitHub provider only")

    args = parser.parse_args()

    suite = AITestSuite()

    if args.all:
        suite.run_all_tests()
    elif args.local:
        suite.test_local_ai_systems()
        suite.print_summary()
    elif args.router:
        suite.test_ultron_cluster_router()
        suite.print_summary()
    elif args.github:
        suite.test_github_ai_provider()
        suite.print_summary()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()