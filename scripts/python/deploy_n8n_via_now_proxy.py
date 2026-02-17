#!/usr/bin/env python3
"""
Deploy N8N Workflows via The Now API as Proxy

Uses The Now API (<NAS_IP>:8000) to proxy workflow deployment to N8N.
The Now API may have an endpoint that forwards to N8N with proper authentication.
"""

import sys
import json
import requests
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DeployN8NViaNowProxy")

# The Now API and N8N endpoints
NOW_API_BASE = "http://<NAS_IP>:8000"
N8N_URL = "http://<NAS_PRIMARY_IP>:5678"
workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

def deploy_via_now_proxy(workflow_data: dict, workflow_name: str) -> bool:
    """Deploy workflow via The Now API proxy to N8N"""

    # Try endpoints that might proxy to N8N
    endpoints = [
        f"{NOW_API_BASE}/api/n8n/workflows/deploy",
        f"{NOW_API_BASE}/api/workflows/deploy",
        f"{NOW_API_BASE}/api/n8n/deploy",
        f"{NOW_API_BASE}/api/deploy/n8n",
        f"{NOW_API_BASE}/api/proxy/n8n/workflows",
        f"{NOW_API_BASE}/api/n8n/workflows",
    ]

    for endpoint in endpoints:
        try:
            # Try with workflow data and N8N URL
            payload = {
                "workflow": workflow_data,
                "n8n_url": N8N_URL,
                "workflow_name": workflow_name
            }

            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
                verify=False
            )

            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"   ✅ Deployed via {endpoint}")
                logger.info(f"   Response: {result}")
                return True
            elif response.status_code == 404:
                continue
            else:
                logger.debug(f"   {endpoint} returned {response.status_code}: {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"   ⚠️  Could not connect to {endpoint}")
            continue
        except Exception as e:
            logger.debug(f"   {endpoint} error: {e}")
            continue

    # If proxy doesn't work, try direct N8N deployment with The Now API credentials
    # Maybe The Now API has N8N credentials stored
    logger.info("   🔄 Trying direct N8N deployment (The Now may handle auth)...")

    # Use The Now API to get N8N credentials or deploy directly
    try:
        # Try to get N8N token from The Now API
        token_response = requests.get(
            f"{NOW_API_BASE}/api/n8n/token",
            timeout=10,
            verify=False
        )
        if token_response.status_code == 200:
            token_data = token_response.json()
            api_token = token_data.get("token") or token_data.get("api_key")

            if api_token:
                # Deploy directly to N8N using token from The Now
                headers = {
                    "Content-Type": "application/json",
                    "X-N8N-API-KEY": api_token
                }
                response = requests.post(
                    f"{N8N_URL}/rest/workflows",
                    json=workflow_data,
                    headers=headers,
                    timeout=30,
                    verify=False
                )
                if response.status_code in [200, 201]:
                    logger.info(f"   ✅ Deployed to N8N using token from The Now API")
                    return True
    except Exception as e:
        logger.debug(f"   Token retrieval failed: {e}")

    return False

def main():
    try:
        """Main execution"""
        logger.info("="*80)
        logger.info("🚀 DEPLOYING N8N WORKFLOWS VIA THE NOW API PROXY")
        logger.info("="*80)
        logger.info(f"   The Now API: {NOW_API_BASE}")
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

            if deploy_via_now_proxy(workflow_data, name):
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
            logger.info("💡 The Now API may not have a workflow deployment endpoint.")
            logger.info("   Please check The Now API documentation or add the endpoint.")
        logger.info("="*80)

        return 0 if success_count == len(workflows) else 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())