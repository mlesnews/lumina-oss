#!/usr/bin/env python3
"""
Deploy N8N Workflows Using Azure Vault Credentials

Retrieves N8N credentials from Azure Vault and deploys all workflows.

Tags: #DOIT #N8N #AZUREVAULT @JARVIS
"""

import sys
import json
import requests
from pathlib import Path

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

logger = get_logger("DeployN8NWithVault")

# Import vault secret retrieval
try:
    from azure_service_bus_integration import AzureKeyVaultClient
    VAULT_AVAILABLE = True
except ImportError:
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
        VAULT_AVAILABLE = True
        AzureKeyVaultClient = None
    except ImportError:
        logger.warning("Azure Vault SDK not available")
        VAULT_AVAILABLE = False
        AzureKeyVaultClient = None

from deploy_syphon_n8n_workflows_nas import SyphonN8NWorkflowDeployer


def get_n8n_credentials_from_vault() -> dict:
    """Get N8N credentials from Azure Vault"""
    credentials = {}

    if not VAULT_AVAILABLE:
        logger.error("   ❌ Azure Vault integration not available")
        return credentials

    vault_url = "https://jarvis-lumina.vault.azure.net/"

    # Try AzureKeyVaultClient first
    if AzureKeyVaultClient:
        try:
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
        except Exception as e:
            logger.debug(f"   AzureKeyVaultClient failed: {e}")
            vault_client = None
    else:
        # Use direct SecretClient
        try:
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            vault_client = SecretClient(vault_url=vault_url, credential=credential)
        except Exception as e:
            logger.debug(f"   SecretClient failed: {e}")
            vault_client = None

    if not vault_client:
        logger.error("   ❌ Could not create Azure Vault client")
        return credentials

    # Try different secret names - get ALL N8N secrets
    secret_names = [
        "n8n-api-token",
        "n8n-api-key",
        "n8n-credentials",
        "n8n-token",
        "nas-n8n-token",
        "nas-n8n-api-key",
        "n8n-username",
        "n8n-basic-auth-password",
        "n8n-nas-password",
        "n8n-password",
        "n8n-username-password"
    ]

    for secret_name in secret_names:
        try:
            if AzureKeyVaultClient:
                secret_value = vault_client.get_secret(secret_name)
            else:
                secret = vault_client.get_secret(secret_name)
                secret_value = secret.value if secret else None

            if secret_value:
                logger.info(f"   ✅ Found secret: {secret_name}")
                credentials[secret_name] = secret_value
                # If it's a JSON, parse it
                try:
                    parsed = json.loads(secret_value)
                    credentials.update(parsed)
                except:
                    pass
        except Exception as e:
            logger.debug(f"   Secret {secret_name} not found: {e}")
            continue

    return credentials


def deploy_with_credentials(n8n_url: str, credentials: dict) -> bool:
    """Deploy workflows using credentials"""
    workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

    workflows = [
        ("email_syphon.json", "Email SYPHON"),
        ("sms_syphon.json", "SMS SYPHON"),
        ("education_syphon.json", "Education SYPHON")
    ]

    # Try API token first (N8N API may require API key instead of basic auth)
    api_token = credentials.get("n8n-api-token") or credentials.get("n8n-api-key") or credentials.get("token") or credentials.get("api_token")

    headers = {"Content-Type": "application/json"}
    if api_token:
        # N8N API key can be in different header formats
        headers["X-N8N-API-KEY"] = api_token
        headers["X-N8N-Api-Key"] = api_token  # Alternative format
        headers["Authorization"] = f"Bearer {api_token}"  # Bearer token format
        logger.info("   ✅ Using API token authentication")
    # Note: If no API token, we'll use basic auth below

    # Try basic auth if username/password
    auth = None
    username = credentials.get("username") or credentials.get("n8n-username")

    # Get password from any of the N8N password secrets (prioritize n8n-password)
    password = (
        credentials.get("n8n-password") or 
        credentials.get("n8n-basic-auth-password") or
        credentials.get("n8n-nas-password") or
        credentials.get("password")
    )

    # If we have password but no username, try NAS username from config
    if password and not username:
        # Try NAS username from config
        nas_config_file = project_root / "config" / "nas_config.json"
        if nas_config_file.exists():
            try:
                with open(nas_config_file, 'r') as f:
                    nas_config = json.load(f)
                    nas_user = nas_config.get("user")
                    if nas_user:
                        logger.info(f"   🔍 Trying NAS username from config: {nas_user}")
                        from requests.auth import HTTPBasicAuth
                        test_auth = HTTPBasicAuth(nas_user, password)
                        test_response = requests.get(f"{n8n_url}/api/v1/workflows", auth=test_auth, timeout=3, verify=False)
                        if test_response.status_code == 200:
                            username = nas_user
                            logger.info(f"   ✅ Found working username: {username}")
            except Exception as e:
                logger.debug(f"   Could not test NAS username: {e}")
                pass

        # If still no username, try common defaults
        if not username:
            logger.info("   ⚠️  Trying common N8N usernames...")
            for test_user in ["admin", "n8n", "user", "mlesn"]:
                try:
                    from requests.auth import HTTPBasicAuth
                    test_auth = HTTPBasicAuth(test_user, password)
                    test_response = requests.get(f"{n8n_url}/api/v1/workflows", auth=test_auth, timeout=3, verify=False)
                    if test_response.status_code == 200:
                        username = test_user
                        logger.info(f"   ✅ Found working username: {username}")
                        break
                except:
                    continue

    if username and password:
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth(username, password)
        logger.info(f"   ✅ Using basic authentication (user: {username})")
    elif password:
        logger.warning("   ⚠️  Have password but no username - will try deployment anyway")

    results = {}
    for filename, name in workflows:
        workflow_file = workflows_dir / filename
        if not workflow_file.exists():
            logger.error(f"   ❌ {name}: File not found")
            results[name] = False
            continue

        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # Ensure required fields for N8N API v1 and remove read-only fields
        if "settings" not in workflow:
            workflow["settings"] = {}
        if "staticData" not in workflow:
            workflow["staticData"] = {}
        # Remove read-only/not-allowed fields that cause errors
        workflow.pop("tags", None)  # Tags are read-only in API
        workflow.pop("id", None)  # ID is auto-generated
        workflow.pop("createdAt", None)
        workflow.pop("updatedAt", None)
        workflow.pop("pinData", None)  # Not allowed in API
        workflow.pop("triggerCount", None)  # Not allowed in API
        workflow.pop("versionId", None)  # Not allowed in API
        # Ensure staticData is object, not null
        if workflow.get("staticData") is None:
            workflow["staticData"] = {}

        # Try multiple endpoints and methods - N8N v1 uses /api/v1/workflows (POST)
        endpoints = [
            ("POST", f"{n8n_url}/api/v1/workflows", workflow),  # Correct N8N v1 format (confirmed working)
            ("POST", f"{n8n_url}/api/v1/workflows/import", {"workflow": workflow}),  # Alternative format
            ("POST", f"{n8n_url}/rest/workflows", workflow),  # Legacy format
        ]

        deployed = False
        for method, endpoint, payload in endpoints:
            try:
                # Try with auth (basic auth or API key in headers)
                if method == "POST":
                    response = requests.post(
                        endpoint,
                        json=payload,
                        headers=headers,
                        auth=auth,
                        timeout=10,
                        verify=False
                    )
                else:  # PUT
                    response = requests.put(
                        endpoint,
                        json=payload,
                        headers=headers,
                        auth=auth,
                        timeout=10,
                        verify=False
                    )
                if response.status_code in [200, 201]:
                    result = response.json()
                    workflow_id = result.get("id") or result.get("data", {}).get("id")
                    logger.info(f"   ✅ {name}: Deployed via {method} {endpoint} (ID: {workflow_id})")
                    results[name] = True
                    deployed = True
                    break
                elif response.status_code in [400, 401, 403, 404, 405]:
                    # Log detailed error for debugging
                    logger.info(f"   ⚠️  {method} {endpoint} returned {response.status_code}")
                    logger.info(f"   Response: {response.text[:400]}")
                elif response.status_code == 400:
                    # 400 might mean bad request format - log the response
                    logger.debug(f"   {method} {endpoint} returned 400: {response.text[:300]}")
                elif response.status_code == 401:
                    # If 401, log the response to see what's wrong
                    logger.debug(f"   {method} {endpoint} returned 401: {response.text[:200]}")
                    # Try without auth (some N8N versions allow unauthenticated POST for import)
                    logger.debug(f"   Trying {method} {endpoint} without auth...")
                    if method == "POST":
                        response_no_auth = requests.post(
                            endpoint,
                            json=payload,
                            headers={"Content-Type": "application/json"},
                            timeout=10,
                            verify=False
                        )
                    else:
                        response_no_auth = requests.put(
                            endpoint,
                            json=payload,
                            headers={"Content-Type": "application/json"},
                            timeout=10,
                            verify=False
                        )
                    if response_no_auth.status_code in [200, 201]:
                        result = response_no_auth.json()
                        workflow_id = result.get("id") or result.get("data", {}).get("id")
                        logger.info(f"   ✅ {name}: Deployed without auth (ID: {workflow_id})")
                        results[name] = True
                        deployed = True
                        break
                    else:
                        logger.warning(f"   ⚠️  {endpoint} returned {response.status_code} (with auth) and {response_no_auth.status_code} (without auth)")
                elif response.status_code == 405:
                    logger.debug(f"   {method} {endpoint} returned 405 (Method Not Allowed)")
                else:
                    logger.warning(f"   ⚠️  {method} {endpoint} returned {response.status_code}")
                    logger.debug(f"   Response: {response.text[:500]}")
            except Exception as e:
                logger.warning(f"   ⚠️  {endpoint} exception: {e}")
                continue

        if not deployed:
            logger.error(f"   ❌ {name}: Deployment failed - all endpoints returned errors")
            results[name] = False

    return all(results.values())


def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("🔐 DEPLOYING N8N WORKFLOWS WITH AZURE VAULT CREDENTIALS")
    logger.info("="*80)
    logger.info("")

    # Get credentials from vault
    logger.info("🔍 Retrieving N8N credentials from Azure Vault...")
    credentials = get_n8n_credentials_from_vault()

    if not credentials:
        logger.error("   ❌ No N8N credentials found in Azure Vault")
        logger.error("   Please add N8N credentials to Azure Vault:")
        logger.error("   - Secret name: 'n8n-api-token' or 'n8n-credentials'")
        logger.error("   - Value: API token or JSON with username/password")
        return 1

    logger.info(f"   ✅ Retrieved {len(credentials)} credential(s) from vault")
    logger.info("")

    # Find N8N URL - try port 5678 first (standard N8N port)
    # Get password for auth testing
    password = credentials.get("n8n-password") or credentials.get("n8n-basic-auth-password") or credentials.get("n8n-nas-password")
    username = credentials.get("username") or credentials.get("n8n-username") or "mlesn"  # Default to NAS user

    n8n_urls = [
        ("http://<NAS_PRIMARY_IP>:5678", True),  # Standard N8N port - test with auth
        ("http://<NAS_PRIMARY_IP>:5000", True),
        ("http://<LOCAL_HOSTNAME>:5678", True)
    ]

    n8n_url = None
    # Wait for N8N to be ready (container may have just started)
    import time
    logger.info("   ⏳ Waiting for N8N to be ready...")
    for attempt in range(12):  # Wait up to 60 seconds
        for url, test_auth in n8n_urls:
            try:
                if test_auth and password:
                    # Test with authentication
                    from requests.auth import HTTPBasicAuth
                    test_auth_obj = HTTPBasicAuth(username, password)
                    # Try root endpoint first (works with basic auth)
                    response = requests.get(url, auth=test_auth_obj, timeout=5, verify=False)
                    if response.status_code == 200:
                        n8n_url = url
                        logger.info(f"   ✅ Found N8N at {url} (authenticated)")
                        break
                    # Also try API endpoint
                    api_response = requests.get(f"{url}/api/v1/workflows", auth=test_auth_obj, timeout=5, verify=False)
                    if api_response.status_code == 200:
                        n8n_url = url
                        logger.info(f"   ✅ Found N8N at {url} (API authenticated)")
                        break
                else:
                    # Test without auth
                    response = requests.get(url, timeout=3, verify=False)
                    if response.status_code < 500:
                        content_lower = response.text.lower() if response.text else ""
                        if "n8n" in content_lower or "workflow" in content_lower or response.status_code == 200:
                            n8n_url = url
                            logger.info(f"   ✅ Found N8N at {url}")
                            break
            except requests.exceptions.ConnectionError:
                # Service not ready yet
                continue
            except Exception as e:
                logger.debug(f"   {url} test failed: {e}")
                continue
        if n8n_url:
            break
        if attempt < 11:
            time.sleep(5)

    if not n8n_url:
        logger.error("   ❌ N8N not found at any known URL")
        return 1

    logger.info("")
    logger.info("🚀 Deploying workflows...")
    success = deploy_with_credentials(n8n_url, credentials)

    logger.info("")
    logger.info("="*80)
    if success:
        logger.info("✅ ALL WORKFLOWS DEPLOYED SUCCESSFULLY")
    else:
        logger.info("⚠️  SOME WORKFLOWS FAILED - CHECK LOGS ABOVE")
    logger.info("="*80)

    return 0 if success else 1


if __name__ == "__main__":


    exit(main())