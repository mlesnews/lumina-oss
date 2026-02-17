#!/usr/bin/env python3
"""
Cursor IDE Connection Diagnostic Tool
Diagnoses and fixes "Connection stalled" errors
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import requests


class CursorConnectionDiagnostic:
    def __init__(self):
        self.ollama_base = "http://localhost:11434"
        self.timeout = 10

    def check_ollama_service(self) -> Dict[str, Any]:
        """Check if Ollama service is running and accessible"""
        result = {"status": "unknown", "accessible": False, "error": None, "models": []}

        try:
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            result["status"] = "running"
            result["accessible"] = True
            result["models"] = [m.get("name", "") for m in data.get("models", [])]
        except requests.exceptions.ConnectionError:
            result["status"] = "not_running"
            result["error"] = "Cannot connect to Ollama service. Is it running?"
        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = f"Ollama service timed out after {self.timeout} seconds"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def test_model_response(self, model_name: str) -> Dict[str, Any]:
        """Test if a specific model can respond"""
        result = {"model": model_name, "responsive": False, "response_time": None, "error": None}

        import time

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.ollama_base}/api/generate",
                json={"model": model_name, "prompt": "test", "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            elapsed = time.time() - start_time
            result["responsive"] = True
            result["response_time"] = elapsed
        except Exception as e:
            result["error"] = str(e)

        return result

    def check_cursor_config(self) -> Dict[str, Any]:
        """Check Cursor configuration for issues"""
        result = {"config_file": None, "exists": False, "issues": []}

        workspace_root = Path.cwd()
        config_file = workspace_root / ".vscode" / "settings.json"
        result["config_file"] = str(config_file)
        result["exists"] = config_file.exists()

        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)

                # Check for missing timeout
                agent_models = config.get("cursor.agent.customModels", [])
                for model in agent_models:
                    if model.get("name") == "ULTRON" and "timeout" not in model:
                        result["issues"].append(
                            f"Model '{model.get('name')}' missing timeout configuration"
                        )
                    if model.get("name") == "ULTRON" and "maxTokens" not in model:
                        result["issues"].append(
                            f"Model '{model.get('name')}' missing maxTokens configuration"
                        )
            except Exception as e:
                result["issues"].append(f"Error reading config: {e}")

        return result

    def generate_fix_recommendations(self, ollama_status: Dict, config_status: Dict) -> list:
        """Generate recommendations based on diagnostic results"""
        recommendations = []

        if not ollama_status["accessible"]:
            recommendations.append(
                {
                    "priority": "critical",
                    "action": "Start Ollama Service",
                    "command": "ollama serve",
                    "description": "Ollama service is not running. Start it to enable Cursor agent functionality.",
                }
            )

        if ollama_status["accessible"] and not ollama_status["models"]:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Pull Required Models",
                    "command": "ollama pull qwen2.5-coder:7b",
                    "description": "No models available in Ollama. Pull the required models.",
                }
            )

        if config_status["issues"]:
            for issue in config_status["issues"]:
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": "Fix Configuration",
                        "description": issue,
                        "file": config_status["config_file"],
                    }
                )

        return recommendations

    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic"""
        print("🔍 Running Cursor Connection Diagnostic...\n")

        ollama_status = self.check_ollama_service()
        print(f"Ollama Service: {ollama_status['status']}")
        if ollama_status["error"]:
            print(f"  Error: {ollama_status['error']}")
        if ollama_status["models"]:
            print(f"  Available Models: {', '.join(ollama_status['models'])}")

        config_status = self.check_cursor_config()
        print(f"\nCursor Config: {'✅ Found' if config_status['exists'] else '❌ Not Found'}")
        if config_status["issues"]:
            print("  Issues:")
            for issue in config_status["issues"]:
                print(f"    - {issue}")

        if ollama_status["accessible"] and ollama_status["models"]:
            print("\n🧪 Testing Model Response...")
            test_model = "qwen2.5-coder:7b"
            if test_model in ollama_status["models"]:
                model_test = self.test_model_response(test_model)
                if model_test["responsive"]:
                    print(f"  ✅ {test_model} responded in {model_test['response_time']:.2f}s")
                else:
                    print(f"  ❌ {test_model} failed: {model_test['error']}")

        recommendations = self.generate_fix_recommendations(ollama_status, config_status)

        if recommendations:
            print("\n📋 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. [{rec['priority'].upper()}] {rec['action']}")
                print(f"   {rec['description']}")
                if "command" in rec:
                    print(f"   Command: {rec['command']}")

        return {
            "ollama": ollama_status,
            "config": config_status,
            "recommendations": recommendations,
        }


if __name__ == "__main__":
    diagnostic = CursorConnectionDiagnostic()
    result = diagnostic.run_full_diagnostic()

    # Exit with error code if critical issues found
    critical_issues = [r for r in result["recommendations"] if r["priority"] == "critical"]
    sys.exit(1 if critical_issues else 0)
