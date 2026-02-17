#!/usr/bin/env python3
"""
@MANUS Azure Function REST API Deployment
Deploys function directly via Azure REST API - no browser needed
Full @manus authority
"""
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
    from azure.mgmt.web import WebSiteManagementClient
    from azure.mgmt.web.models import FunctionEnvelope
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False

try:
    from lumina_logger import get_logger
    logger = get_logger("ManusRESTDeploy")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ManusRESTDeploy")


class ManusRESTDeployer:
    """@MANUS - Deploy via Azure REST API"""

    def __init__(self):
        self.function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
        self.function_app_name = "jarvis-lumina-functions"
        self.resource_group = "jarvis-lumina-rg"
        self.subscription_id = None
        self.credential = None

    def get_azure_credentials(self):
        """Get Azure credentials"""
        try:
            # Try DefaultAzureCredential first (works if already logged in)
            self.credential = DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                )
            logger.info("✅ Using DefaultAzureCredential")
            return True
        except Exception as e:
            logger.warning(f"⚠️  DefaultAzureCredential failed: {e}")
            try:
                # Fallback to interactive browser
                self.credential = InteractiveBrowserCredential()
                logger.info("✅ Using InteractiveBrowserCredential")
                return True
            except Exception as e2:
                logger.error(f"❌ Credential acquisition failed: {e2}")
                return False

    def deploy_via_rest_api(self) -> bool:
        """Deploy function via Azure REST API"""
        if not AZURE_SDK_AVAILABLE:
            logger.error("❌ Azure SDK not available - install: pip install azure-identity azure-mgmt-web")
            return False

        try:
            logger.info("🚀 @MANUS: Deploying via Azure REST API...")

            # Get credentials
            if not self.get_azure_credentials():
                return False

            # Get subscription ID from environment or config
            import os
            self.subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
            if not self.subscription_id:
                logger.warning("⚠️  AZURE_SUBSCRIPTION_ID not set - checking config...")
                config_path = project_root / "config" / "azure_services_config.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        self.subscription_id = config.get("azure_services_config", {}).get("subscription_id", "").replace("${AZURE_SUBSCRIPTION_ID}", "")

            if not self.subscription_id:
                logger.error("❌ Subscription ID not found")
                logger.info("   Set AZURE_SUBSCRIPTION_ID environment variable")
                return False

            # Load function code
            with open(self.function_code_path, 'r', encoding='utf-8') as f:
                function_code = f.read()

            # Create WebSiteManagementClient
            web_client = WebSiteManagementClient(self.credential, self.subscription_id)

            logger.info(f"📦 Creating function: RenderIronLegion...")

            # Create function via REST API
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

            # Deploy function
            function = web_client.web_apps.create_or_update_function(
                resource_group_name=self.resource_group,
                name=self.function_app_name,
                function_name="RenderIronLegion",
                function_envelope=function_config
            )

            logger.info("✅ Function deployed successfully!")
            logger.info(f"   Endpoint: https://{self.function_app_name}.azurewebsites.net/api/RenderIronLegion")
            return True

        except Exception as e:
            logger.error(f"❌ REST API deployment failed: {e}")
            logger.info("   Falling back to browser automation...")
            return False


def main():
    """@MANUS deployment execution"""
    print("=" * 80)
    print("🔥 @MANUS AUTHORITY: Azure Function REST API Deployment")
    print("=" * 80)

    deployer = ManusRESTDeployer()
    success = deployer.deploy_via_rest_api()

    if not success:
        print("\n🔄 Falling back to browser automation...")
        print("   Run: python scripts/python/manus_azure_deploy_automation.py")

    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())