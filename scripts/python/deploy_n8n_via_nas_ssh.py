#!/usr/bin/env python3
"""
Deploy N8N Workflows via NAS SSH

Uses NAS SSH access (via NAS API integration) to deploy workflows to N8N.
"""

import sys
import json
import base64
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

logger = get_logger("DeployN8NViaNASSSH")

NAS_IP = "<NAS_PRIMARY_IP>"
N8N_URL = f"http://{NAS_IP}:5678"
workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

def deploy_via_nas_ssh(workflow_data: dict, workflow_name: str) -> bool:
    try:
        """Deploy workflow via NAS SSH"""

        nas = NASAzureVaultIntegration()
        vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")

        # Get credentials
        n8n_password = vault.get_secret("n8n-password")
        nas_user = "mlesn"

        # Method 1: Copy workflow file to NAS and use N8N CLI (if available)
        # First, encode workflow JSON for safe transfer
        workflow_json = json.dumps(workflow_data)
        workflow_b64 = base64.b64encode(workflow_json.encode('utf-8')).decode('utf-8')

        # Write workflow to temp file on NAS
        temp_file = f"/tmp/{workflow_name.lower().replace(' ', '_')}.json"

        # Create file on NAS via SSH
        write_cmd = f"echo '{workflow_b64}' | base64 -d > {temp_file}"
        result = nas.execute_ssh_command(write_cmd)

        if not result["success"]:
            logger.warning(f"   ⚠️  Could not write workflow file to NAS: {result.get('error')}")
            # Try alternative: write directly
            import shlex
            escaped_json = shlex.quote(workflow_json)
            write_cmd2 = f"cat > {temp_file} << 'EOF'\n{workflow_json}\nEOF"
            result = nas.execute_ssh_command(write_cmd2)
            if not result["success"]:
                logger.error(f"   ❌ Failed to write workflow file")
                return False

        logger.info(f"   ✅ Workflow file written to NAS: {temp_file}")

        # Method 2: Use curl to POST to N8N API via SSH
        # Since N8N API requires API key, try with basic auth first
        import shlex
        escaped_pwd = shlex.quote(n8n_password)

        # Try to deploy via curl on NAS
        curl_cmd = f"""curl -X POST '{N8N_URL}/rest/workflows' \\
      -u '{nas_user}:{escaped_pwd}' \\
      -H 'Content-Type: application/json' \\
      -d @{temp_file} \\
      2>&1"""

        result = nas.execute_ssh_command(curl_cmd)

        if result["success"]:
            output = result["output"].strip()
            logger.info(f"   📋 Curl response: {output[:500]}")
            if '"id"' in output or '"status":"success"' in output.lower() or '"success":true' in output.lower():
                logger.info(f"   ✅ Deployed via NAS SSH + curl")
                # Clean up temp file
                nas.execute_ssh_command(f"rm -f {temp_file}")
                return True
            elif '"status":"error"' in output.lower() or '"Unauthorized"' in output:
                logger.warning(f"   ⚠️  Authentication failed - N8N requires API key")
            else:
                logger.debug(f"   Response: {output[:300]}")

        # Method 3: If N8N CLI is available, use it
        n8n_cli_cmd = f"n8n import:workflow --input={temp_file} 2>&1"
        result = nas.execute_ssh_command(n8n_cli_cmd)

        if result["success"] and "imported" in result["output"].lower():
            logger.info(f"   ✅ Deployed via N8N CLI")
            nas.execute_ssh_command(f"rm -f {temp_file}")
            return True

        # Clean up
        nas.execute_ssh_command(f"rm -f {temp_file}")
        return False

    except Exception as e:
        logger.error(f"Error in deploy_via_nas_ssh: {e}", exc_info=True)
        raise
def main():
    try:
        """Main execution"""
        logger.info("="*80)
        logger.info("🚀 DEPLOYING N8N WORKFLOWS VIA NAS SSH")
        logger.info("="*80)
        logger.info(f"   NAS: {NAS_IP}")
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

            if deploy_via_nas_ssh(workflow_data, name):
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
            logger.info("💡 N8N API requires API key for programmatic deployment.")
            logger.info("   Manual import via web UI may be required.")
        logger.info("="*80)

        return 0 if success_count == len(workflows) else 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())