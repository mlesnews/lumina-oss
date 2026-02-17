#!/usr/bin/env python3
"""
Find N8N and Deploy - DO IT ALL!

Finds N8N, gets credentials if needed, deploys workflows.
Tags: #DOIT #N8N @JARVIS
"""

import sys
import json
import requests
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from deploy_syphon_n8n_workflows_nas import SyphonN8NWorkflowDeployer

# Try all ports
ports = [5678, 5000, 8080, 3000]
n8n_found = None

for port in ports:
    url = f"http://<NAS_PRIMARY_IP>:{port}"
    try:
        r = requests.get(url, timeout=2, verify=False)
        if r.status_code < 500 and ("n8n" in r.text.lower() or "workflow" in r.text.lower()):
            n8n_found = (url, port)
            print(f"✅ Found N8N at {url}")
            break
    except:
        continue

if n8n_found:
    url, port = n8n_found
    deployer = SyphonN8NWorkflowDeployer(n8n_port=port)
    print(f"\n🚀 Deploying to {url}...")
    results = deployer.deploy_all_workflows()
    print(f"\n✅ Deployment complete: {results}")
else:
    print("❌ N8N not found. Need operator input:")
    print("   1. What port is N8N on?")
    print("   2. What URL to access N8N?")
    print("   3. API token or credentials?")
