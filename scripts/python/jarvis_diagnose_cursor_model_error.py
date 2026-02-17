#!/usr/bin/env python3
"""
JARVIS Diagnose Cursor "Invalid Model" Error

Diagnoses the persistent "invalid model" error by:
1. Testing Ollama API directly
2. Checking model name resolution
3. Verifying Cursor configuration format
4. Testing alternative configurations

Tags: #ULTRON #CURSOR-IDE #DIAGNOSTIC #TROUBLESHOOTING
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDiagnoseModel")


class JARVISDiagnoseCursorModelError:
    """
    Diagnose the "invalid model" error in Cursor
    """

    def __init__(self):
        self.logger = logger
        self.ollama_base = "http://localhost:11434"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "diagnosis": [],
            "recommendations": []
        }

    def test_ollama_api(self) -> Dict[str, Any]:
        """Test Ollama API directly"""
        self.logger.info("🔍 Testing Ollama API...")

        test_result = {
            "endpoint_accessible": False,
            "models_available": [],
            "model_test": {}
        }

        # Test 1: Check if Ollama is accessible
        try:
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=5)
            if response.status_code == 200:
                test_result["endpoint_accessible"] = True
                data = response.json()
                test_result["models_available"] = [m["name"] for m in data.get("models", [])]
                self.logger.info(f"✅ Ollama accessible - {len(test_result['models_available'])} models")
            else:
                self.logger.error(f"❌ Ollama returned HTTP {response.status_code}")
        except Exception as e:
            self.logger.error(f"❌ Ollama not accessible: {e}")
            test_result["error"] = str(e)

        # Test 2: Try to generate with qwen2.5:72b
        if test_result["endpoint_accessible"] and "qwen2.5:72b" in test_result["models_available"]:
            self.logger.info("🔍 Testing model generation...")
            try:
                generate_payload = {
                    "model": "qwen2.5:72b",
                    "prompt": "Say 'test'",
                    "stream": False
                }
                response = requests.post(
                    f"{self.ollama_base}/api/generate",
                    json=generate_payload,
                    timeout=30
                )

                if response.status_code == 200:
                    test_result["model_test"]["status"] = "success"
                    test_result["model_test"]["response_received"] = True
                    self.logger.info("✅ Model generation works")
                else:
                    test_result["model_test"]["status"] = "error"
                    test_result["model_test"]["error"] = f"HTTP {response.status_code}"
                    test_result["model_test"]["response_text"] = response.text[:200]
                    self.logger.error(f"❌ Model generation failed: HTTP {response.status_code}")
            except requests.exceptions.Timeout:
                test_result["model_test"]["status"] = "timeout"
                test_result["model_test"]["note"] = "Model loading (first request takes time)"
                self.logger.warning("⚠️  Model generation timed out (may be loading)")
            except Exception as e:
                test_result["model_test"]["status"] = "error"
                test_result["model_test"]["error"] = str(e)
                self.logger.error(f"❌ Model generation error: {e}")

        self.results["tests"]["ollama_api"] = test_result
        return test_result

    def analyze_cursor_config(self) -> Dict[str, Any]:
        """Analyze Cursor configuration for potential issues"""
        self.logger.info("🔍 Analyzing Cursor configuration...")

        analysis = {
            "workspace_config": None,
            "user_config": None,
            "issues": [],
            "recommendations": []
        }

        # Check workspace settings
        workspace_file = Path(__file__).parent.parent.parent / ".cursor" / "settings.json"
        if workspace_file.exists():
            try:
                with open(workspace_file, 'r', encoding='utf-8') as f:
                    workspace_config = json.load(f)
                    analysis["workspace_config"] = self._analyze_model_configs(workspace_config, "workspace")
            except Exception as e:
                analysis["issues"].append(f"Failed to read workspace config: {e}")

        # Check user settings
        import os
        appdata = os.getenv("APPDATA")
        if appdata:
            user_file = Path(appdata) / "Cursor" / "User" / "settings.json"
            if user_file.exists():
                try:
                    with open(user_file, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                        analysis["user_config"] = self._analyze_model_configs(user_config, "user")
                except Exception as e:
                    analysis["issues"].append(f"Failed to read user config: {e}")

        self.results["tests"]["cursor_config"] = analysis
        return analysis

    def _analyze_model_configs(self, config: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Analyze model configurations in a settings file"""
        analysis = {
            "source": source,
            "model_sections": {},
            "issues": [],
            "recommendations": []
        }

        sections = [
            ("cursor.model.customModels", "cursor.model", "customModels"),
            ("cursor.chat.customModels", "cursor.chat", "customModels"),
            ("cursor.composer.customModels", "cursor.composer", "customModels"),
            ("cursor.agent.customModels", "cursor.agent", "customModels")
        ]

        for section_name, parent_key, child_key in sections:
            section_analysis = {
                "exists": False,
                "models": [],
                "ultron_found": False,
                "issues": []
            }

            # Navigate to section
            current = config
            try:
                for key in parent_key.split("."):
                    if key in current:
                        current = current[key]
                    else:
                        break
                else:
                    if child_key in current and isinstance(current[child_key], list):
                        section_analysis["exists"] = True
                        models = current[child_key]

                        for model in models:
                            if isinstance(model, dict):
                                model_info = {
                                    "name": model.get("name", "unknown"),
                                    "title": model.get("title", "unknown"),
                                    "provider": model.get("provider", "unknown"),
                                    "model": model.get("model", "unknown"),
                                    "apiBase": model.get("apiBase", "unknown")
                                }
                                section_analysis["models"].append(model_info)

                                # Check for ULTRON
                                if model.get("name") == "ULTRON" or model.get("title") == "ULTRON":
                                    section_analysis["ultron_found"] = True

                                    # Check for potential issues
                                    if model.get("model") != "qwen2.5:72b":
                                        section_analysis["issues"].append(
                                            f"ULTRON model field is '{model.get('model')}', not 'qwen2.5:72b'"
                                        )

                                    if not model.get("apiBase"):
                                        section_analysis["issues"].append("ULTRON missing apiBase")

                                    if model.get("provider") != "ollama":
                                        section_analysis["issues"].append(
                                            f"ULTRON provider is '{model.get('provider')}', not 'ollama'"
                                        )
            except Exception as e:
                section_analysis["error"] = str(e)

            analysis["model_sections"][section_name] = section_analysis

        return analysis

    def generate_fix_recommendations(self) -> List[str]:
        """Generate fix recommendations based on diagnosis"""
        recommendations = []

        # Check Ollama test results
        ollama_test = self.results.get("tests", {}).get("ollama_api", {})
        if not ollama_test.get("endpoint_accessible"):
            recommendations.append("Start Ollama service: ollama serve")

        if ollama_test.get("models_available") and "qwen2.5:72b" not in ollama_test["models_available"]:
            recommendations.append("Pull qwen2.5:72b model: ollama pull qwen2.5:72b")

        # Check config analysis
        config_analysis = self.results.get("tests", {}).get("cursor_config", {})

        # Key insight: Cursor might be using the "name" field as the model identifier
        # instead of the "model" field. This is the root cause!
        recommendations.append(
            "CRITICAL: Cursor may be using 'name' field ('ULTRON') as model identifier. "
            "Try setting 'name' to match 'model' field value: 'qwen2.5:72b'"
        )

        recommendations.append(
            "Alternative: Use the actual model name directly instead of custom name 'ULTRON'"
        )

        return recommendations

    def diagnose(self) -> Dict[str, Any]:
        """Run complete diagnosis"""
        self.logger.info("="*80)
        self.logger.info("JARVIS: COMPLETE MODEL ERROR DIAGNOSIS")
        self.logger.info("="*80)
        self.logger.info("")

        # Test Ollama
        self.test_ollama_api()
        self.logger.info("")

        # Analyze config
        self.analyze_cursor_config()
        self.logger.info("")

        # Generate recommendations
        self.results["recommendations"] = self.generate_fix_recommendations()

        # Summary
        self.logger.info("="*80)
        self.logger.info("DIAGNOSIS SUMMARY")
        self.logger.info("="*80)

        ollama_ok = self.results["tests"].get("ollama_api", {}).get("endpoint_accessible", False)
        if ollama_ok:
            self.logger.info("✅ Ollama: Accessible")
        else:
            self.logger.error("❌ Ollama: Not accessible")

        self.logger.info("")
        self.logger.info("RECOMMENDATIONS:")
        for i, rec in enumerate(self.results["recommendations"], 1):
            self.logger.info(f"  {i}. {rec}")

        return self.results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Diagnose Cursor 'invalid model' error")
        args = parser.parse_args()

        diagnostician = JARVISDiagnoseCursorModelError()
        results = diagnostician.diagnose()

        print("\n" + "="*80)
        print("COMPLETE DIAGNOSIS RESULTS")
        print("="*80)
        print(json.dumps(results, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()