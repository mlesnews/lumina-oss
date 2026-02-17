#!/usr/bin/env python3
"""
Activate N8N SYPHON Workflows

Activates all SYPHON workflows (Email, SMS, Education) in N8N.

Tags: #N8N #SYPHON #WORKFLOW #ACTIVATION @JARVIS @LUMINA
"""

import sys
import requests
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ActivateN8NSyphonWorkflows")

N8N_URL = "http://<NAS_PRIMARY_IP>:5678"
SYPHON_WORKFLOWS = [
    "SYPHON Email Intelligence Extraction",
    "SYPHON SMS Intelligence Extraction",
    "SYPHON Social-News-Education Intelligence Extraction"
]


def get_n8n_api_key():
    """Get N8N API key from Azure Vault"""
    try:
        vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
        # Try different possible secret names
        for secret_name in ["n8n-api-token", "n8n-api-key", "n8n_api_key", "n8n-api_key"]:
            try:
                return vault.get_secret(secret_name)
            except:
                continue
        return None
    except:
        return None


def activate_workflow(workflow_id: str, api_key: str) -> bool:
    """Activate a workflow in N8N"""
    try:
        # Use activation endpoint (POST to /active endpoint)
        activate_response = requests.post(
            f"{N8N_URL}/api/v1/workflows/{workflow_id}/activate",
            headers={"X-N8N-API-KEY": api_key},
            timeout=10
        )

        if activate_response.status_code == 200:
            logger.info(f"   ✅ Activated workflow: {workflow_id}")
            return True
        elif activate_response.status_code == 404:
            # Try alternative endpoint format
            activate_response = requests.post(
                f"{N8N_URL}/api/v1/workflows/{workflow_id}/active",
                headers={"X-N8N-API-KEY": api_key},
                json={"active": True},
                timeout=10
            )
            if activate_response.status_code == 200:
                logger.info(f"   ✅ Activated workflow: {workflow_id}")
                return True

        # If activation endpoint doesn't work, try getting workflow and updating with full structure
        get_response = requests.get(
            f"{N8N_URL}/api/v1/workflows/{workflow_id}",
            headers={"X-N8N-API-KEY": api_key},
            timeout=10
        )

        if get_response.status_code == 200:
            workflow = get_response.json()
            # Remove read-only fields and set active
            workflow.pop("id", None)
            workflow.pop("createdAt", None)
            workflow.pop("updatedAt", None)
            workflow.pop("tags", None)  # tags might be read-only
            workflow["active"] = True

            # Ensure required fields
            if "settings" not in workflow:
                workflow["settings"] = {}
            if "staticData" not in workflow:
                workflow["staticData"] = {}

            # Try PUT with full workflow (without read-only fields)
            put_response = requests.put(
                f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                headers={
                    "X-N8N-API-KEY": api_key,
                    "Content-Type": "application/json"
                },
                json=workflow,
                timeout=10
            )

            if put_response.status_code == 200:
                logger.info(f"   ✅ Activated workflow: {workflow_id}")
                return True

        logger.error(f"   ❌ Failed to activate {workflow_id}")
        logger.error(f"      Last response: {get_response.status_code if 'get_response' in locals() else 'N/A'}")
        return False

    except Exception as e:
        logger.error(f"   ❌ Error activating workflow {workflow_id}: {e}")
        return False


def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("🚀 ACTIVATING N8N SYPHON WORKFLOWS")
    logger.info("="*80)
    logger.info("")

    api_key = get_n8n_api_key()
    if not api_key:
        logger.error("   ❌ N8N API key not found in Azure Vault")
        logger.info("   💡 Add it with: python scripts/python/add_n8n_api_key_to_vault.py")
        return 1

    logger.info("   ✅ N8N API key found")
    logger.info("")

    # List all workflows
    try:
        response = requests.get(
            f"{N8N_URL}/api/v1/workflows",
            headers={"X-N8N-API-KEY": api_key},
            timeout=10
        )

        if response.status_code != 200:
            logger.error(f"   ❌ Could not fetch workflows: {response.status_code}")
            return 1

        workflows = response.json().get("data", [])
        logger.info(f"   📋 Found {len(workflows)} workflow(s)")
        logger.info("")

        # Find and activate SYPHON workflows
        activated = 0
        for workflow in workflows:
            workflow_name = workflow.get("name", "")
            if any(syphon_name in workflow_name for syphon_name in SYPHON_WORKFLOWS):
                workflow_id = workflow.get("id")
                is_active = workflow.get("active", False)

                if is_active:
                    logger.info(f"   ℹ️  Already active: {workflow_name}")
                else:
                    if activate_workflow(workflow_id, api_key):
                        activated += 1

        logger.info("")
        logger.info("="*80)
        if activated > 0:
            logger.info(f"✅ ACTIVATED {activated} WORKFLOW(S)")
        else:
            logger.info("ℹ️  All workflows already active or none found")
        logger.info("="*80)

        return 0

    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())