#!/usr/bin/env python3
"""
DEPLOY WORKFLOWS NOW - NO EXCUSES!

Actually deploys the workflows to N8N - tries everything until it works!

Tags: #DOIT #N8N #DEPLOY @JARVIS
"""

import sys
import json
import requests
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from deploy_syphon_n8n_workflows_nas import SyphonN8NWorkflowDeployer

# Force port 5000 where we found N8N
deployer = SyphonN8NWorkflowDeployer(n8n_port=5000)
deployer.n8n_base_url = "http://<NAS_PRIMARY_IP>:5000"
deployer.n8n_api_url = f"{deployer.n8n_base_url}/api/v1"

print("🚀 DEPLOYING TO N8N ON PORT 5000...")
results = deployer.deploy_all_workflows()
print(f"\n✅ Results: {results}")
