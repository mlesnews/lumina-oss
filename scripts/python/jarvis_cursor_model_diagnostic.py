#!/usr/bin/env python3
"""
JARVIS Cursor Model Diagnostic Tool

Diagnoses Cursor IDE model connection issues and provides fixes.
Checks Ollama, Docker, and cloud model availability.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import socket
import requests
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class CursorModelDiagnostic:
    """Diagnostic tool for Cursor IDE model configuration."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        """Initialize diagnostic tool."""
        self.project_root = project_root
        self.settings_path = project_root / ".cursor" / "settings.json"
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "issues": [],
            "recommendations": []
        }

    def check_ollama_local(self) -> Dict[str, Any]:
        """Check if local Ollama is running."""
        result = {
            "status": "UNKNOWN",
            "endpoint": "http://localhost:11434",
            "accessible": False,
            "models": [],
            "error": None
        }

        try:
            # Test connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            connection_result = sock.connect_ex(('localhost', 11434))
            sock.close()

            if connection_result == 0:
                # Port is open, try API
                try:
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        result["status"] = "RUNNING"
                        result["accessible"] = True
                        result["models"] = [model.get("name", "") for model in data.get("models", [])]
                    else:
                        result["status"] = "PORT_OPEN_BUT_API_FAILED"
                        result["error"] = f"API returned status {response.status_code}"
                except requests.RequestException as e:
                    result["status"] = "PORT_OPEN_BUT_API_ERROR"
                    result["error"] = str(e)
            else:
                result["status"] = "NOT_RUNNING"
                result["error"] = "Port 11434 is not accessible"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def check_docker(self) -> Dict[str, Any]:
        """Check if Docker is running."""
        result = {
            "status": "UNKNOWN",
            "running": False,
            "error": None
        }

        try:
            # Try docker ps
            proc = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if proc.returncode == 0:
                result["status"] = "RUNNING"
                result["running"] = True
            else:
                result["status"] = "NOT_RUNNING"
                result["error"] = proc.stderr.strip() or "Docker command failed"
        except FileNotFoundError:
            result["status"] = "NOT_INSTALLED"
            result["error"] = "Docker not found in PATH"
        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["error"] = "Docker command timed out"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def check_ollama_kaiju(self) -> Dict[str, Any]:
        """Check if KAIJU (Desktop PC - KAIJU Number Eight) Ollama is accessible."""
        result = {
            "status": "UNKNOWN",
            "endpoint": "http://<NAS_IP>:11434",
            "accessible": False,
            "models": [],
            "error": None,
            "note": "KAIJU = Desktop PC (KAIJU Number Eight) at <NAS_IP>, NAS (DS2118+) is at <NAS_PRIMARY_IP>"
        }

        try:
            response = requests.get("http://<NAS_IP>:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                result["status"] = "ACCESSIBLE"
                result["accessible"] = True
                result["models"] = [model.get("name", "") for model in data.get("models", [])]
            else:
                result["status"] = "API_ERROR"
                result["error"] = f"API returned status {response.status_code}"
        except requests.ConnectionError:
            result["status"] = "NOT_ACCESSIBLE"
            result["error"] = "Connection refused or host unreachable"
        except requests.Timeout:
            result["status"] = "TIMEOUT"
            result["error"] = "Request timed out"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def check_cursor_settings(self) -> Dict[str, Any]:
        """Check Cursor settings.json configuration."""
        result = {
            "status": "UNKNOWN",
            "file_exists": False,
            "default_models": {},
            "custom_models": [],
            "issues": []
        }

        if not self.settings_path.exists():
            result["status"] = "FILE_NOT_FOUND"
            result["issues"].append(f"Settings file not found: {self.settings_path}")
            return result

        result["file_exists"] = True

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Check default models
            result["default_models"] = {
                "chat": settings.get("cursor.chat.defaultModel", "NOT_SET"),
                "composer": settings.get("cursor.composer.defaultModel", "NOT_SET"),
                "agent": settings.get("cursor.agent.defaultModel", "NOT_SET"),
                "inlineCompletion": settings.get("cursor.inlineCompletion.defaultModel", "NOT_SET")
            }

            # Check custom models
            custom_models = settings.get("cursor.chat.customModels", [])
            result["custom_models"] = [
                {
                    "name": model.get("name", "UNNAMED"),
                    "provider": model.get("provider", "UNKNOWN"),
                    "apiBase": model.get("apiBase", "NOT_SET"),
                    "model": model.get("model", "NOT_SET")
                }
                for model in custom_models
            ]

            # Check for issues
            all_defaults_are_local = all(
                v in ["ULTRON", "KAIJU"] 
                for v in result["default_models"].values()
            )

            if not all_defaults_are_local:
                result["issues"].append("Some default models are not set to local models (ULTRON/KAIJU)")

            result["status"] = "OK"

        except json.JSONDecodeError as e:
            result["status"] = "JSON_ERROR"
            result["issues"].append(f"Invalid JSON: {e}")
        except Exception as e:
            result["status"] = "ERROR"
            result["issues"].append(f"Error reading settings: {e}")

        return result

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on diagnostic results."""
        recommendations = []

        ollama_local = self.results["checks"].get("ollama_local", {})
        docker = self.results["checks"].get("docker", {})
        ollama_kaiju = self.results["checks"].get("ollama_kaiju", {})
        cursor_settings = self.results["checks"].get("cursor_settings", {})

        # If local Ollama is not running
        if ollama_local.get("status") != "RUNNING":
            if docker.get("status") == "NOT_RUNNING":
                recommendations.append(
                    "START DOCKER: Docker Desktop is not running. Start Docker Desktop first, "
                    "then Ollama should start automatically if configured as a Docker container."
                )
            elif docker.get("status") == "NOT_INSTALLED":
                recommendations.append(
                    "INSTALL DOCKER: Docker is not installed. Install Docker Desktop for Windows, "
                    "then configure Ollama as a container or install Ollama directly."
                )
            else:
                recommendations.append(
                    "START OLLAMA: Local Ollama is not running. "
                    "If using Docker: `docker start ollama` or check Docker Desktop. "
                    "If installed directly: Start Ollama service or run `ollama serve`."
                )

        # If KAIJU is accessible, recommend using it
        if ollama_kaiju.get("status") == "ACCESSIBLE":
            recommendations.append(
                "USE KAIJU: KAIJU (Desktop PC - KAIJU Number Eight) Ollama is accessible. "
                "You can temporarily use KAIJU as your default model in Cursor while local Ollama is unavailable."
            )

        # If no local models are available
        if (ollama_local.get("status") != "RUNNING" and 
            ollama_kaiju.get("status") != "ACCESSIBLE"):
            recommendations.append(
                "NO LOCAL MODELS: Neither local Ollama (ULTRON) nor KAIJU Number Eight (Desktop PC) is accessible. "
                "Cursor will try to use cloud models, which may fail if not properly configured. "
                "Either start local Ollama/Docker or configure cloud model credentials properly."
            )

        # Check Cursor settings
        if cursor_settings.get("status") == "OK":
            defaults = cursor_settings.get("default_models", {})
            if not all(v in ["ULTRON", "KAIJU"] for v in defaults.values()):
                recommendations.append(
                    "UPDATE CURSOR SETTINGS: Some default models are not set to local models. "
                    "In Cursor, go to Settings > Features and set Chat, Composer, and Agent "
                    "default models to 'ULTRON' or 'KAIJU'."
                )

        if not recommendations:
            recommendations.append("All checks passed! No issues detected.")

        return recommendations

    def run_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic checks."""
        print("🔍 Running Cursor Model Diagnostics...")
        print()

        # Check local Ollama
        print("Checking local Ollama (localhost:11434)...")
        self.results["checks"]["ollama_local"] = self.check_ollama_local()
        print(f"  Status: {self.results['checks']['ollama_local']['status']}")
        if self.results["checks"]["ollama_local"].get("models"):
            print(f"  Models: {', '.join(self.results['checks']['ollama_local']['models'])}")
        print()

        # Check Docker
        print("Checking Docker...")
        self.results["checks"]["docker"] = self.check_docker()
        print(f"  Status: {self.results['checks']['docker']['status']}")
        print()

        # Check KAIJU
        print("Checking KAIJU Number Eight (Desktop PC) Ollama (<NAS_IP>:11434)...")
        self.results["checks"]["ollama_kaiju"] = self.check_ollama_kaiju()
        print(f"  Status: {self.results['checks']['ollama_kaiju']['status']}")
        if self.results["checks"]["ollama_kaiju"].get("models"):
            print(f"  Models: {', '.join(self.results['checks']['ollama_kaiju']['models'])}")
        print(f"  Note: KAIJU = Desktop PC (KAIJU Number Eight), NAS = DS2118+ (Synology)")
        print()

        # Check Cursor settings
        print("Checking Cursor settings...")
        self.results["checks"]["cursor_settings"] = self.check_cursor_settings()
        print(f"  Status: {self.results['checks']['cursor_settings']['status']}")
        if self.results["checks"]["cursor_settings"].get("default_models"):
            defaults = self.results["checks"]["cursor_settings"]["default_models"]
            print(f"  Default Chat: {defaults.get('chat', 'NOT_SET')}")
            print(f"  Default Composer: {defaults.get('composer', 'NOT_SET')}")
            print(f"  Default Agent: {defaults.get('agent', 'NOT_SET')}")
        print()

        # Generate recommendations
        self.results["recommendations"] = self.generate_recommendations()

        # Print recommendations
        print("📋 Recommendations:")
        print()
        for i, rec in enumerate(self.results["recommendations"], 1):
            print(f"  {i}. {rec}")
        print()

        return self.results

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        try:
            """Save diagnostic report to JSON file."""
            if output_path is None:
                output_path = self.project_root / "data" / "diagnostics" / f"cursor_model_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)

            print(f"💾 Diagnostic report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Cursor Model Diagnostic Tool")
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save diagnostic report to JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for diagnostic report"
    )

    args = parser.parse_args()

    diagnostic = CursorModelDiagnostic()
    results = diagnostic.run_diagnostics()

    if args.save_report:
        diagnostic.save_report(args.output)

    # Exit with error code if issues found
    if results["recommendations"] and not results["recommendations"][0].startswith("All checks passed"):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":


    main()