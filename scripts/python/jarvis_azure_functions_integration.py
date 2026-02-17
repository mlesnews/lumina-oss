#!/usr/bin/env python3
"""
JARVIS Azure Functions Integration

Integration with Azure Functions for serverless event processing.
This module provides helpers for calling Azure Functions and
managing function triggers from Service Bus/Event Grid.

Tags: #AZURE #FUNCTIONS #SERVERLESS #EVENT_PROCESSING #LUMINA @JARVIS
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAzureFunctions")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISAzureFunctions")

# Azure Key Vault for secrets
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False


class AzureFunctionsIntegration:
    """Azure Functions integration for JARVIS/LUMINA"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "azure_services_config.json"
        self.config = self.load_config()
        self.function_app_name = self.config.get("azure_functions", {}).get("function_app_name", "jarvis-lumina-functions")
        self.function_keys: Dict[str, str] = {}

        self._load_function_keys()

    def load_config(self) -> Dict[str, Any]:
        """Load Azure services configuration"""
        default_config = {
            "azure_functions": {
                "enabled": False,
                "function_app_name": "jarvis-lumina-functions"
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    azure_config = data.get("azure_services_config", {})
                    if azure_config.get("azure_functions"):
                        default_config["azure_functions"].update(azure_config["azure_functions"])
            except Exception as e:
                logger.error(f"Error loading Azure config: {e}")

        return default_config

    def _load_function_keys(self):
        """Load function keys from Key Vault"""
        if not AZURE_KV_AVAILABLE:
            return

        if not self.config.get("azure_functions", {}).get("enabled", False):
            return

        try:
            vault_url = self.config.get("key_vault", {}).get("vault_url") or "https://jarvis-lumina.vault.azure.net/"
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            secret_client = SecretClient(vault_url=vault_url, credential=credential)

            # Load function keys
            functions = self.config.get("azure_functions", {}).get("functions", {})
            for func_key, func_config in functions.items():
                func_name = func_config.get("name")
                if func_name:
                    try:
                        secret_name = f"azure-function-{func_name}-key"
                        key = secret_client.get_secret(secret_name).value
                        self.function_keys[func_name] = key
                    except Exception:
                        pass

            # Load master key
            try:
                master_key = secret_client.get_secret("azure-function-app-key").value
                self.function_keys["_master"] = master_key
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"Could not load function keys: {e}")

    def invoke_function(self, function_name: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """Invoke Azure Function via HTTP"""
        if not self.config.get("azure_functions", {}).get("enabled", False):
            return {
                "success": False,
                "error": "Azure Functions not enabled"
            }

        try:
            # Get function key
            function_key = self.function_keys.get(function_name) or self.function_keys.get("_master")
            if not function_key:
                return {
                    "success": False,
                    "error": f"Function key not found for {function_name}"
                }

            # Construct function URL
            location = self.config.get("location", "eastus")
            function_url = f"https://{self.function_app_name}.azurewebsites.net/api/{function_name}?code={function_key}"

            # Invoke function
            response = requests.request(
                method=method,
                url=function_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code in [200, 202]:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response.json() if response.content else {}
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
        except Exception as e:
            logger.error(f"Error invoking function: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def process_terminal_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process terminal log via Azure Function"""
        return self.invoke_function("ProcessTerminalLog", log_data)

    def process_voice_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice transcript via Azure Function"""
        return self.invoke_function("ProcessVoiceTranscript", transcript_data)


def get_azure_functions(project_root: Path = None) -> AzureFunctionsIntegration:
    try:
        """Get or create Azure Functions integration instance"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return AzureFunctionsIntegration(project_root)


    except Exception as e:
        logger.error(f"Error in get_azure_functions: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test
    functions = get_azure_functions()
    print(f"Functions integration initialized: {functions.function_app_name}")
