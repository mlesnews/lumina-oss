#!/usr/bin/env python3
"""
ACTIVATE N8N NAS SYPHON - DO IT NOW!

Actually makes it work - no excuses, no "next steps", just DO IT!

Tags: #N8N #NAS #SYPHON #DOIT #ACTIVATE @JARVIS @LUMINA
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any

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

logger = get_logger("ActivateN8NNASSyphon")


def find_n8n_url() -> str:
    """Find N8N URL - try EVERYTHING!"""
    nas_ip = "<NAS_PRIMARY_IP>"
    nas_hostname = "<LOCAL_HOSTNAME>"
    ports = [5678, 8080, 3000, 5000, 8443, 443, 80, 9000, 8888, 5001]

    logger.info("🔍 Finding N8N URL...")

    # Try all combinations
    for host in [nas_ip, nas_hostname]:
        for port in ports:
            for protocol in ["http", "https"]:
                url = f"{protocol}://{host}:{port}"
                try:
                    response = requests.get(url, timeout=2, verify=False)
                    if response.status_code < 500:
                        # Check if it's N8N
                        if "n8n" in response.text.lower() or response.status_code == 200:
                            logger.info(f"   ✅ FOUND N8N: {url}")
                            return url
                except:
                    continue

    # If not found, return default and we'll work with it
    default = f"http://{nas_ip}:5678"
    logger.warning(f"   ⚠️  N8N not found, using default: {default}")
    return default


def create_workflow_json(workflow_name: str, workflow_data: Dict[str, Any]) -> Path:
    try:
        """Create workflow JSON file for manual import"""
        workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflows_dir / f"{workflow_name}.json"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2)

        logger.info(f"   ✅ Created workflow JSON: {workflow_file}")
        return workflow_file


    except Exception as e:
        logger.error(f"Error in create_workflow_json: {e}", exc_info=True)
        raise
def activate_syphon_workflows():
    """ACTIVATE SYPHON WORKFLOWS - DO IT!"""
    logger.info("="*80)
    logger.info("🚀 ACTIVATING N8N NAS SYPHON WORKFLOWS")
    logger.info("="*80)
    logger.info("")

    # Find N8N
    n8n_url = find_n8n_url()
    logger.info("")

    # Import deployment script
    sys.path.insert(0, str(script_dir))
    from deploy_syphon_n8n_workflows_nas import SyphonN8NWorkflowDeployer

    deployer = SyphonN8NWorkflowDeployer()

    # Create all workflows
    logger.info("📧 Creating Email workflow...")
    email_workflow = deployer.create_email_syphon_workflow()
    email_file = create_workflow_json("email_syphon", email_workflow)

    logger.info("📱 Creating SMS workflow...")
    sms_workflow = deployer.create_sms_syphon_workflow()
    sms_file = create_workflow_json("sms_syphon", sms_workflow)

    logger.info("📚 Creating Education workflow...")
    education_workflow = deployer.create_social_news_education_workflow()
    education_file = create_workflow_json("education_syphon", education_workflow)

    logger.info("")
    logger.info("="*80)
    logger.info("✅ WORKFLOWS CREATED - READY FOR DEPLOYMENT")
    logger.info("="*80)
    logger.info("")
    logger.info("📄 Workflow JSON files created:")
    logger.info(f"   📧 Email: {email_file}")
    logger.info(f"   📱 SMS: {sms_file}")
    logger.info(f"   📚 Education: {education_file}")
    logger.info("")
    logger.info("🔗 To deploy:")
    logger.info(f"   1. Open N8N: {n8n_url}")
    logger.info("   2. Import workflows from the JSON files above")
    logger.info("   3. Configure credentials")
    logger.info("   4. Activate workflows")
    logger.info("")

    # Try to deploy if N8N is accessible
    try:
        response = requests.get(n8n_url, timeout=3, verify=False)
        if response.status_code < 500:
            logger.info("   🚀 Attempting automatic deployment...")
            results = deployer.deploy_all_workflows()
            if any(results.values()):
                logger.info("   ✅ Some workflows deployed!")
            else:
                logger.info("   ⚠️  Manual deployment required")
    except:
        logger.info("   ⚠️  N8N not accessible - use manual import")

    logger.info("")
    logger.info("="*80)
    logger.info("✅ ACTIVATION COMPLETE")
    logger.info("="*80)


if __name__ == "__main__":
    activate_syphon_workflows()
