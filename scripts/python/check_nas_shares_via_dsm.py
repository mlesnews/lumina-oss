#!/usr/bin/env python3
"""Check existing NAS shares via DSM API"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from synology_api_base import SynologyAPIBase
from nas_azure_vault_integration import NASAzureVaultIntegration

vault = NASAzureVaultIntegration()
creds = vault.get_nas_credentials()
api = SynologyAPIBase(verify_ssl=False)
api.login(creds['username'], creds['password'], 'FileStation')

shares = api.api_call('SYNO.Core.Share', 'list', '1')
print("Existing shares:")
if shares and shares.get('shares'):
    for s in shares['shares']:
        print(f"  - {s.get('name')}: {s.get('vol_path')}")
else:
    print("  No shares found or API call failed")

api.logout()
