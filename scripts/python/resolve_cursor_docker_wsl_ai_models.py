#!/usr/bin/env python3
"""
Resolve Docker/WSL/AI-Model Issues for Cursor IDE

Resolves all local Docker/WSL/AI-model configuration issues for:
- Cursor AI Chat (agent mode)
- Cursor Agent Chat (non-agent mode)
- All IDE agent and non-agent modes

Tags: #CURSOR #DOCKER #WSL #AI_MODELS #RESOLUTION @CURSOR
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ResolveCursorDockerWSL")


class CursorDockerWSLResolver:
    """Resolve Docker/WSL/AI-model issues for Cursor"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cursor_config_dir = project_root / ".cursor"
        self.cursor_settings = self.cursor_config_dir / "settings.json"
        self.cursor_mcp_config = self.cursor_config_dir / "mcp_config.json"

    def resolve_all(self) -> Dict[str, Any]:
        """Resolve all issues"""
        logger.info("=" * 80)
        logger.info("🔧 RESOLVING CURSOR DOCKER/WSL/AI-MODEL ISSUES")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "docker": self.resolve_docker(),
            "wsl": self.resolve_wsl(),
            "ollama_local": self.resolve_ollama_local(),
            "ollama_nas": self.resolve_ollama_nas(),
            "cursor_config": self.resolve_cursor_config(),
            "mcp_config": self.resolve_mcp_config(),
            "ai_models": self.resolve_ai_models(),
        }

        # Generate summary
        all_passed = all(r.get("success", False) for r in results.values())

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 RESOLUTION SUMMARY")
        logger.info("=" * 80)
        for key, result in results.items():
            status = "✅" if result.get("success") else "❌"
            logger.info(f"{status} {key}: {result.get('message', 'Unknown')}")
        logger.info("")

        return {
            "success": all_passed,
            "results": results,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    def resolve_docker(self) -> Dict[str, Any]:
        """Resolve Docker issues"""
        logger.info("📋 Checking Docker...")

        try:
            # Check if Docker is running
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "✅ Docker is running",
                    "containers": len(result.stdout.strip().split("\n")) - 1,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Docker is not running",
                    "error": result.stderr,
                }
        except FileNotFoundError:
            return {"success": False, "message": "❌ Docker not installed or not in PATH"}
        except Exception as e:
            return {"success": False, "message": f"❌ Docker check failed: {e}", "error": str(e)}

    def resolve_wsl(self) -> Dict[str, Any]:
        """Resolve WSL issues"""
        logger.info("📋 Checking WSL...")

        try:
            # Check if WSL is available
            result = subprocess.run(
                ["wsl", "--list", "--verbose"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                distros = [
                    line
                    for line in result.stdout.split("\n")
                    if line.strip() and not line.startswith("NAME")
                ]
                return {
                    "success": True,
                    "message": f"✅ WSL is available ({len(distros)} distributions)",
                    "distributions": distros,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ WSL is not available",
                    "error": result.stderr,
                }
        except FileNotFoundError:
            return {"success": False, "message": "❌ WSL not installed or not in PATH"}
        except Exception as e:
            return {"success": False, "message": f"❌ WSL check failed: {e}", "error": str(e)}

    def resolve_ollama_local(self) -> Dict[str, Any]:
        """Resolve local Ollama connection"""
        logger.info("📋 Checking local Ollama...")

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "success": True,
                    "message": f"✅ Local Ollama is running ({len(models)} models)",
                    "models": [m.get("name") for m in models],
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Local Ollama returned status {response.status_code}",
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "❌ Local Ollama is not running (connection refused)",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Local Ollama check failed: {e}",
                "error": str(e),
            }

    def resolve_ollama_nas(self) -> Dict[str, Any]:
        """Resolve NAS Ollama connection"""
        logger.info("📋 Checking NAS Ollama (KAIJU)...")

        try:
            response = requests.get("http://<NAS_PRIMARY_IP>:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "success": True,
                    "message": f"✅ NAS Ollama (KAIJU) is running ({len(models)} models)",
                    "models": [m.get("name") for m in models],
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ NAS Ollama returned status {response.status_code}",
                }
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "❌ NAS Ollama (KAIJU) is not reachable"}
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ NAS Ollama check failed: {e}",
                "error": str(e),
            }

    def resolve_cursor_config(self) -> Dict[str, Any]:
        """Resolve Cursor settings.json configuration"""
        logger.info("📋 Checking Cursor configuration...")

        try:
            if not self.cursor_settings.exists():
                # Create default configuration
                self.cursor_config_dir.mkdir(parents=True, exist_ok=True)
                default_config = self._get_default_cursor_config()
                with open(self.cursor_settings, "w") as f:
                    json.dump(default_config, f, indent=2)
                return {
                    "success": True,
                    "message": "✅ Created Cursor settings.json",
                    "action": "created",
                }

            # Validate existing configuration
            with open(self.cursor_settings) as f:
                config = json.load(f)

            # Check for required settings
            required_keys = ["cursor.chat.defaultModel", "cursor.composer.defaultModel"]
            missing = [key for key in required_keys if key not in config]

            if missing:
                # Add missing settings
                for key in missing:
                    config[key] = "ULTRON"
                with open(self.cursor_settings, "w") as f:
                    json.dump(config, f, indent=2)
                return {
                    "success": True,
                    "message": f"✅ Updated Cursor settings.json (added {len(missing)} missing keys)",
                    "action": "updated",
                    "added": missing,
                }

            return {
                "success": True,
                "message": "✅ Cursor settings.json is valid",
                "action": "validated",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Cursor config resolution failed: {e}",
                "error": str(e),
            }

    def resolve_mcp_config(self) -> Dict[str, Any]:
        """Resolve Cursor MCP configuration"""
        logger.info("📋 Checking Cursor MCP configuration...")

        try:
            if not self.cursor_mcp_config.exists():
                # Create default MCP configuration
                default_mcp = self._get_default_mcp_config()
                with open(self.cursor_mcp_config, "w") as f:
                    json.dump(default_mcp, f, indent=2)
                return {
                    "success": True,
                    "message": "✅ Created Cursor MCP config",
                    "action": "created",
                }

            return {
                "success": True,
                "message": "✅ Cursor MCP config exists",
                "action": "validated",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ MCP config resolution failed: {e}",
                "error": str(e),
            }

    def resolve_ai_models(self) -> Dict[str, Any]:
        """Resolve AI model configurations"""
        logger.info("📋 Checking AI model configurations...")

        try:
            if not self.cursor_settings.exists():
                return {"success": False, "message": "❌ Cursor settings.json not found"}

            with open(self.cursor_settings) as f:
                config = json.load(f)

            # Check for model configurations
            has_chat_models = "cursor.chat.customModels" in config
            has_composer_models = "cursor.composer.customModels" in config
            has_agent_models = "cursor.agent.customModels" in config

            if not (has_chat_models and has_composer_models and has_agent_models):
                # Add missing model configurations
                if not has_chat_models:
                    config["cursor.chat.customModels"] = self._get_default_models()
                if not has_composer_models:
                    config["cursor.composer.customModels"] = self._get_default_models()
                if not has_agent_models:
                    config["cursor.agent.customModels"] = self._get_default_models()

                with open(self.cursor_settings, "w") as f:
                    json.dump(config, f, indent=2)

                return {
                    "success": True,
                    "message": "✅ Added missing AI model configurations",
                    "action": "updated",
                }

            return {
                "success": True,
                "message": "✅ AI model configurations are valid",
                "action": "validated",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ AI model resolution failed: {e}",
                "error": str(e),
            }

    def _get_default_cursor_config(self) -> Dict[str, Any]:
        """Get default Cursor configuration"""
        return {
            "cursor.chat.defaultModel": "ULTRON",
            "cursor.composer.defaultModel": "ULTRON",
            "cursor.inlineCompletion.defaultModel": "ULTRON",
            "cursor.chat.customModels": self._get_default_models(),
            "cursor.composer.customModels": self._get_default_models(),
            "cursor.agent.customModels": self._get_default_models(),
        }

    def _get_default_models(self) -> List[Dict[str, Any]]:
        """Get default AI model configurations"""
        return [
            {
                "title": "ULTRON",
                "name": "ULTRON",
                "provider": "ollama",
                "model": "qwen2.5:72b",
                "apiBase": "http://localhost:11434",
                "contextLength": 32768,
                "description": "ULTRON - Local Docker/WSL Ollama instance",
                "localOnly": True,
                "skipProviderSelection": True,
            },
            {
                "title": "KAIJU (Iron Legion)",
                "name": "KAIJU",
                "provider": "ollama",
                "model": "llama3.2:3b",
                "apiBase": "http://<NAS_PRIMARY_IP>:11434",
                "contextLength": 8192,
                "description": "KAIJU / Iron Legion - NAS Docker/WSL cluster",
                "localOnly": True,
                "skipProviderSelection": True,
            },
        ]

    def _get_default_mcp_config(self) -> Dict[str, Any]:
        """Get default MCP configuration"""
        return {
            "mcpServers": {
                "MANUS": {
                    "command": "docker",
                    "args": ["exec", "-i", "manus-mcp-server", "python3", "-m", "manus_mcp_server"],
                },
                "ElevenLabs": {
                    "command": "docker",
                    "args": [
                        "exec",
                        "-i",
                        "elevenlabs-mcp-server",
                        "python3",
                        "-m",
                        "elevenlabs_mcp",
                    ],
                    "env": {"ELEVENLABS_API_KEY": "${elevenlabs-api-key}"},
                },
            }
        }


def main():
    try:
        """Main execution"""
        resolver = CursorDockerWSLResolver(project_root)
        results = resolver.resolve_all()

        # Save results
        results_file = project_root / "data" / "cursor_resolution_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"✅ Resolution results saved: {results_file.name}")

        # Exit with appropriate code
        exit_code = 0 if results["success"] else 1
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
