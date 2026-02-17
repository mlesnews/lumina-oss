#!/usr/bin/env python3
"""
Deploy N8N Workflows via NAS API

Uses Synology DSM API to deploy workflows to N8N on the NAS.
"""

import sys
import json
import requests
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration
from azure_service_bus_integration import AzureKeyVaultClient

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DeployN8NViaNASAPI")

# NAS configuration
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_DSM_PORT = 5001  # HTTPS
NAS_DSM_API_BASE = f"https://{NAS_IP}:{NAS_DSM_PORT}/webapi"
N8N_URL = f"http://{NAS_IP}:5678"

workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

def deploy_via_nas_dsm_api(workflow_data: dict, workflow_name: str) -> bool:
    """Deploy workflow via NAS DSM API"""

    nas = NASAzureVaultIntegration()
    vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")

    # Get NAS credentials
    nas_user = "mlesn"  # From nas_config.json
    nas_password = vault.get_secret("nas-password")

    # Step 1: Authenticate with DSM API
    try:
        auth_url = f"{NAS_DSM_API_BASE}/auth.cgi"
        auth_params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": nas_user,
            "passwd": nas_password,
            "session": "FileStation",
            "format": "sid"
        }

        # Disable SSL verification for self-signed certs
        auth_response = requests.get(
            auth_url,
            params=auth_params,
            verify=False,
            timeout=10
        )

        if auth_response.status_code != 200:
            logger.error(f"   ❌ DSM API authentication failed: {auth_response.status_code}")
            return False

        auth_data = auth_response.json()
        if not auth_data.get("success"):
            logger.error(f"   ❌ DSM API authentication failed: {auth_data}")
            return False

        sid = auth_data["data"]["sid"]
        logger.info("   ✅ Authenticated with NAS DSM API")

    except Exception as e:
        logger.error(f"   ❌ DSM API authentication error: {e}")
        return False

    # Step 2: Use DSM API to deploy to N8N
    # Try Container Manager API or direct N8N deployment via NAS

    # Option 1: Use Container Manager API to execute command in N8N container
    try:
        # Get N8N container info
        container_url = f"{NAS_DSM_API_BASE}/entry.cgi"
        container_params = {
            "api": "SYNO.Docker.Container",
            "version": "1",
            "method": "list",
            "sid": sid
        }

        container_response = requests.get(
            container_url,
            params=container_params,
            verify=False,
            timeout=10
        )

        if container_response.status_code == 200:
            containers = container_response.json()
            logger.info("   ✅ Retrieved container list from NAS")

            # Find N8N container
            n8n_container = None
            for container in containers.get("data", {}).get("containers", []):
                if "n8n" in container.get("name", "").lower():
                    n8n_container = container
                    break

            if n8n_container:
                logger.info(f"   ✅ Found N8N container: {n8n_container.get('name')}")
                # Deploy workflow via container exec or file copy
                # This would require additional API calls
            else:
                logger.warning("   ⚠️  N8N container not found via DSM API")

    except Exception as e:
        logger.debug(f"   Container API error: {e}")

    # Option 2: Use DSM API to write workflow file to NAS, then import via N8N API
    # This is more direct - write to NAS storage, then trigger N8N import

    # For now, use the authenticated session to deploy directly to N8N
    # The NAS API authentication gives us access, but N8N still needs its own auth

    # Get N8N credentials
    n8n_password = vault.get_secret("n8n-password")

    # Deploy directly to N8N using credentials
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth(nas_user, n8n_password)

    try:
        response = requests.post(
            f"{N8N_URL}/rest/workflows",
            json=workflow_data,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=30,
            verify=False
        )

        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            logger.info(f"   ✅ Deployed via N8N API (ID: {workflow_id})")
            return True
        else:
            logger.warning(f"   ⚠️  N8N API returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        logger.debug(f"   N8N API error: {e}")

    return False

def main():
    try:
        """Main execution"""
        logger.info("="*80)
        logger.info("🚀 DEPLOYING N8N WORKFLOWS VIA NAS API")
        logger.info("="*80)
        logger.info(f"   NAS: {NAS_IP}")
        logger.info(f"   DSM API: {NAS_DSM_API_BASE}")
        logger.info(f"   N8N URL: {N8N_URL}")
        logger.info("")

        success_count = 0
        for filename, name in workflows:
            workflow_file = workflows_dir / filename
            if not workflow_file.exists():
                logger.error(f"❌ {name}: File not found")
                continue

            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)

            logger.info(f"📤 Deploying {name}...")

            if deploy_via_nas_dsm_api(workflow_data, name):
                logger.info(f"   ✅ {name}: Deployed successfully")
                success_count += 1
            else:
                logger.error(f"   ❌ {name}: Deployment failed")
                logger.info(f"   💡 Workflow file ready: {workflow_file}")

        logger.info("")
        logger.info("="*80)
        if success_count == len(workflows):
            logger.info("✅ ALL WORKFLOWS DEPLOYED SUCCESSFULLY")
        elif success_count > 0:
            logger.info(f"⚠️  {success_count}/{len(workflows)} WORKFLOWS DEPLOYED")
        else:
            logger.info("❌ NO WORKFLOWS DEPLOYED")
            logger.info("")
            logger.info("💡 Note: N8N API requires API key for programmatic deployment.")
            logger.info("   Manual import via web UI may be required.")
        logger.info("="*80)

        return 0 if success_count == len(workflows) else 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())