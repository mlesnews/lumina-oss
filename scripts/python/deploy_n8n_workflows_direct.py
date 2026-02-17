#!/usr/bin/env python3
"""
Deploy N8N Workflows Directly - DO IT!

Tries every possible method to deploy workflows to N8N.
If authentication is needed, asks operator directly.

Tags: #DOIT #N8N #DEPLOY @JARVIS
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("DeployN8NDirect")


def deploy_workflow_direct(workflow_file: Path, n8n_url: str) -> tuple[bool, str]:
    """Deploy workflow using every possible method"""

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # Method 1: REST API (older N8N)
    endpoints = [
        f"{n8n_url}/rest/workflows",
        f"{n8n_url}/api/v1/workflows",
        f"{n8n_url}/api/workflows"
    ]

    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                json=workflow,
                headers={"Content-Type": "application/json"},
                timeout=10,
                verify=False
            )
            if response.status_code in [200, 201]:
                result = response.json()
                workflow_id = result.get("id") or result.get("data", {}).get("id")
                return True, f"Deployed via {endpoint} (ID: {workflow_id})"
            elif response.status_code == 401:
                return False, f"Authentication required for {endpoint}"
            elif response.status_code == 403:
                return False, f"Access forbidden for {endpoint} - needs API token or credentials"
        except Exception as e:
            continue

    return False, "All deployment methods failed - authentication required"


def main():
    try:
        """Main - deploy all workflows"""
        logger.info("="*80)
        logger.info("🚀 DEPLOYING N8N WORKFLOWS - DOING IT NOW")
        logger.info("="*80)
        logger.info("")

        n8n_url = "http://<NAS_PRIMARY_IP>:5000"
        workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

        workflows = [
            ("email_syphon.json", "Email SYPHON"),
            ("sms_syphon.json", "SMS SYPHON"),
            ("education_syphon.json", "Education SYPHON")
        ]

        results = {}
        auth_needed = False

        for filename, name in workflows:
            workflow_file = workflows_dir / filename
            if not workflow_file.exists():
                logger.error(f"   ❌ {name}: File not found")
                results[name] = False
                continue

            logger.info(f"   📤 Deploying {name}...")
            success, message = deploy_workflow_direct(workflow_file, n8n_url)

            if success:
                logger.info(f"   ✅ {name}: {message}")
                results[name] = True
            else:
                logger.warning(f"   ⚠️  {name}: {message}")
                if "authentication" in message.lower() or "forbidden" in message.lower():
                    auth_needed = True
                results[name] = False

        logger.info("")
        logger.info("="*80)
        logger.info("📊 DEPLOYMENT RESULTS")
        logger.info("="*80)
        for name, success in results.items():
            icon = "✅" if success else "❌"
            logger.info(f"   {icon} {name}: {'Deployed' if success else 'Failed'}")

        if auth_needed:
            logger.info("")
            logger.info("="*80)
            logger.info("❓ OPERATOR: AUTHENTICATION REQUIRED")
            logger.info("="*80)
            logger.info("")
            logger.info("   N8N API requires authentication to deploy workflows.")
            logger.info("")
            logger.info("   Please provide ONE of the following:")
            logger.info("   1. N8N API Token (from N8N Settings → API)")
            logger.info("   2. N8N Username/Password")
            logger.info("   3. Alternative deployment method")
            logger.info("")
            logger.info("   Once provided, I will deploy all workflows immediately.")
            logger.info("")

        return 0 if all(results.values()) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())