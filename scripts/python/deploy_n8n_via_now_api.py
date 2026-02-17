#!/usr/bin/env python3
"""
Deploy N8N Workflows via The Now API

Deploys workflows through The Now API (<NAS_IP>:8000) instead of directly to N8N.
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

logger = get_logger("DeployN8NViaNowAPI")

# The Now API endpoint
NOW_API_BASE = "http://<NAS_IP>:8000"
workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

def deploy_workflow_via_now_api(workflow_data: dict, workflow_name: str) -> bool:
    """Deploy workflow via The Now API"""

    # Try different possible endpoints
    endpoints = [
        f"{NOW_API_BASE}/api/n8n/workflows",
        f"{NOW_API_BASE}/api/workflows",
        f"{NOW_API_BASE}/api/n8n/deploy",
        f"{NOW_API_BASE}/api/deploy/workflow",
        f"{NOW_API_BASE}/api/automation/workflows"
    ]

    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                json={
                    "workflow": workflow_data,
                    "workflow_name": workflow_name,
                    "n8n_url": "http://<NAS_PRIMARY_IP>:5678"
                },
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
                # Endpoint doesn't exist, try next
                continue
            else:
                logger.debug(f"   {endpoint} returned {response.status_code}: {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"   ⚠️  Could not connect to {endpoint}")
            continue
        except Exception as e:
            logger.debug(f"   {endpoint} error: {e}")
            continue

    return False

def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("🚀 DEPLOYING N8N WORKFLOWS VIA THE NOW API")
    logger.info("="*80)
    logger.info(f"   API Base: {NOW_API_BASE}")
    logger.info("")

    # Check API connectivity
    try:
        health_check = requests.get(f"{NOW_API_BASE}/health", timeout=5, verify=False)
        if health_check.status_code == 200:
            logger.info("   ✅ The Now API is accessible")
        else:
            logger.warning(f"   ⚠️  Health check returned {health_check.status_code}")
    except Exception as e:
        logger.warning(f"   ⚠️  Could not verify API health: {e}")

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

        if deploy_workflow_via_now_api(workflow_data, name):
            logger.info(f"   ✅ {name}: Deployed successfully")
            success_count += 1
        else:
            logger.error(f"   ❌ {name}: Deployment failed - no working endpoint found")
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
        logger.info("💡 Possible solutions:")
        logger.info("   1. Check if The Now API has a workflow deployment endpoint")
        logger.info("   2. Verify API is running at http://<NAS_IP>:8000")
        logger.info("   3. Check API documentation for correct endpoint")
    logger.info("="*80)

    return 0 if success_count == len(workflows) else 1

if __name__ == "__main__":


    exit(main())