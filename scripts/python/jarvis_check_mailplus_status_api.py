#!/usr/bin/env python3
"""Quick check of MailPlus-Server status via DSM API"""
import sys
from pathlib import Path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration
from synology_api_base import SynologyAPIBase

nas = NASAzureVaultIntegration()
creds = nas.get_nas_credentials()
api = SynologyAPIBase(nas_ip='<NAS_PRIMARY_IP>', nas_port=5001, verify_ssl=False)
api.login(creds['username'], creds['password'])

import requests
r = requests.get(f'{api.base_url}/webapi/entry.cgi', params={'api': 'SYNO.Core.Package', 'version': '1', 'method': 'list', '_sid': api.sid}, timeout=10, verify=False)
data = r.json()
packages = data.get('data', {}).get('packages', [])
mailplus = [p for p in packages if 'mailplus' in p.get('name', '').lower() and 'server' in p.get('name', '').lower()]

if mailplus:
    status = mailplus[0].get('status', 'unknown')
    print(f"MailPlus-Server status: {status}")
    if status == 'running':
        print("✅ MailPlus-Server is RUNNING!")
        sys.exit(0)
    else:
        print(f"⚠️  MailPlus-Server status: {status}")
        sys.exit(1)
else:
    print("❌ MailPlus-Server package not found")
    sys.exit(2)

api.logout()
