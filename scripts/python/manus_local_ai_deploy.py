#!/usr/bin/env python3
"""
@MANUS Local AI Deployment Assistant
Uses local AI to analyze deployment situation and create deployment solution
"""
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("ManusLocalAIDeploy")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ManusLocalAIDeploy")


class LocalAIDeploymentAssistant:
    """Uses local AI to handle deployment"""

    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
        self.function_app_name = "jarvis-lumina-functions"

    def query_local_ai(self, prompt: str, model: str = "llama3.2") -> Optional[str]:
        """Query local Ollama model"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.warning(f"⚠️  Ollama returned {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  Ollama not running on localhost:11434")
            return None
        except Exception as e:
            logger.error(f"❌ Local AI query error: {e}")
            return None

    def analyze_deployment_situation(self) -> Dict[str, Any]:
        """Use local AI to analyze deployment situation"""
        logger.info("🤖 Consulting local AI for deployment strategy...")

        prompt = f"""You are a deployment expert. Analyze this Azure Function deployment situation:

PROBLEM:
- Need to deploy Azure Function 'RenderIronLegion' to Function App 'jarvis-lumina-functions'
- Azure authentication/2FA is blocking browser automation
- Function code is ready at: {self.function_code_path}
- Subscription ID: 9835b511-4369-4619-94ae-4c505e74cff0
- Resource Group: jarvis-lumina-rg

REQUIREMENTS:
- Must deploy without browser automation
- Must work with Azure authentication already in place
- Function code is Python, uses azure.functions

Provide a step-by-step deployment solution using:
1. Azure CLI commands (if available)
2. Azure REST API with existing credentials
3. Azure Functions Core Tools
4. Alternative methods

Format as JSON with steps array.
"""

        ai_response = self.query_local_ai(prompt)

        if ai_response:
            logger.info("✅ Local AI provided deployment strategy")
            try:
                # Try to parse as JSON
                strategy = json.loads(ai_response)
                return strategy
            except:
                # Return as text if not JSON
                return {"strategy": ai_response, "raw": True}
        else:
            return self._fallback_strategy()

    def _fallback_strategy(self) -> Dict[str, Any]:
        """Fallback deployment strategy"""
        return {
            "steps": [
                {
                    "method": "azure_cli",
                    "command": "az functionapp function create --resource-group jarvis-lumina-rg --name jarvis-lumina-functions --function-name RenderIronLegion --runtime python --runtime-version 3.11"
                },
                {
                    "method": "kudu_api",
                    "description": "Upload code via Kudu API using existing Azure credentials"
                },
                {
                    "method": "zip_deploy",
                    "description": "Package function and deploy via ZIP deploy API"
                }
            ]
        }

    def execute_deployment(self) -> bool:
        """Execute deployment using local AI guidance"""
        logger.info("=" * 80)
        logger.info("🔥 @MANUS: Local AI Deployment Execution")
        logger.info("=" * 80)

        # Get strategy from local AI
        strategy = self.analyze_deployment_situation()

        # Load function code
        with open(self.function_code_path, 'r', encoding='utf-8') as f:
            function_code = f.read()

        # Try ZIP deploy method (most reliable)
        logger.info("📦 Attempting ZIP deployment via Azure REST API...")

        try:
            from azure.identity import DefaultAzureCredential
            import zipfile
            import io

            credential = DefaultAzureCredential(


                                exclude_interactive_browser_credential=False,


                                exclude_shared_token_cache_credential=False


                            )
            token = credential.get_token("https://management.azure.com/.default").token

            # Create function package
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr("RenderIronLegion/__init__.py", function_code)
                zip_file.writestr("host.json", json.dumps({
                    "version": "2.0",
                    "extensionBundle": {
                        "id": "Microsoft.Azure.Functions.ExtensionBundle",
                        "version": "[3.*, 4.0.0)"
                    }
                }))
                zip_file.writestr("requirements.txt", "azure-functions\nPillow>=10.0.0")

            zip_data = zip_buffer.getvalue()

            # Deploy via ZIP deploy API
            subscription_id = "9835b511-4369-4619-94ae-4c505e74cff0"
            resource_group = "jarvis-lumina-rg"

            deploy_url = f"https://{self.function_app_name}.scm.azurewebsites.net/api/zipdeploy"

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/zip"
            }

            logger.info(f"📤 Uploading ZIP package ({len(zip_data)} bytes)...")
            response = requests.post(deploy_url, data=zip_data, headers=headers, timeout=120)

            if response.status_code in [200, 202]:
                logger.info("✅ ZIP deployment successful!")
                logger.info(f"   Function should be available at:")
                logger.info(f"   https://{self.function_app_name}.azurewebsites.net/api/RenderIronLegion")
                return True
            else:
                logger.warning(f"⚠️  ZIP deploy returned {response.status_code}")
                logger.info("   Trying alternative method...")
                return self._try_alternative_deployment(function_code, token)

        except Exception as e:
            logger.error(f"❌ Deployment error: {e}")
            logger.info("   Using local AI to generate alternative solution...")
            return self._try_ai_generated_solution(function_code)

    def _try_alternative_deployment(self, function_code: str, token: str) -> bool:
        """Try alternative deployment methods"""
        logger.info("🔄 Trying alternative: Direct function creation via Management API...")

        # Use Azure Management API to create function
        subscription_id = "9835b511-4369-4619-94ae-4c505e74cff0"
        resource_group = "jarvis-lumina-rg"

        api_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{self.function_app_name}/functions/RenderIronLegion"

        function_config = {
            "properties": {
                "config": {
                    "bindings": [
                        {
                            "authLevel": "function",
                            "type": "httpTrigger",
                            "direction": "in",
                            "name": "req",
                            "methods": ["post"]
                        },
                        {
                            "type": "http",
                            "direction": "out",
                            "name": "$return"
                        }
                    ]
                },
                "files": {
                    "__init__.py": function_code
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.put(api_url, json=function_config, headers=headers, params={"api-version": "2022-03-01"}, timeout=30)

            if response.status_code in [200, 201]:
                logger.info("✅ Function created via Management API!")
                return True
            else:
                logger.warning(f"⚠️  Management API returned {response.status_code}: {response.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"❌ Alternative deployment failed: {e}")
            return False

    def _try_ai_generated_solution(self, function_code: str) -> bool:
        """Use local AI to generate deployment solution"""
        logger.info("🤖 Asking local AI for deployment solution...")

        prompt = f"""Generate a Python script to deploy this Azure Function code to Azure without browser automation.

Function App: jarvis-lumina-functions
Resource Group: jarvis-lumina-rg
Subscription: 9835b511-4369-4619-94ae-4c505e74cff0

Function code length: {len(function_code)} characters

Use Azure REST APIs with DefaultAzureCredential. Provide complete working Python code.
"""

        solution = self.query_local_ai(prompt, model="llama3.2")

        if solution:
            logger.info("✅ Local AI generated solution")
            logger.info("   Solution:")
            logger.info(solution[:500])
            # Could execute the generated code, but for safety, just return it
            return False
        else:
            logger.warning("⚠️  Local AI unavailable - using manual deployment")
            return False


def main():
    """@MANUS local AI deployment"""
    assistant = LocalAIDeploymentAssistant()
    success = assistant.execute_deployment()

    if success:
        print("\n✅ @MANUS DEPLOYMENT COMPLETE!")
        print("   Remote compute is now active")
    else:
        print("\n⚠️  Automated deployment had issues")
        print("   Function code is ready - manual deployment may be needed")

    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())