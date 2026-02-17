#!/usr/bin/env python3
"""Query MailPlus API to find available methods"""
import sys
from pathlib import Path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration
from synology_api_base import SynologyAPIBase
import requests
import json

nas = NASAzureVaultIntegration()
creds = nas.get_nas_credentials()
api = SynologyAPIBase(nas_ip='<NAS_PRIMARY_IP>', nas_port=5001, verify_ssl=False)
api.login(creds['username'], creds['password'])

# Query API info
query_url = f"{api.base_url}/webapi/query.cgi"
query_params = {
    "api": "SYNO.API.Info",
    "version": "1",
    "method": "query",
    "query": "all",
    "_sid": api.sid
}

response = api.session.get(query_url, params=query_params, timeout=10, verify=False)
data = response.json()

if data.get("success"):
    apis = data.get("data", {})
    mailplus_apis = {k: v for k, v in apis.items() if "mail" in k.lower() or "plus" in k.lower()}

    print("=" * 80)
    print("MailPlus-related APIs found:")
    print("=" * 80)
    for api_name, api_info in mailplus_apis.items():
        print(f"\n{api_name}:")
        print(f"  Path: {api_info.get('path', 'N/A')}")
        print(f"  Min Version: {api_info.get('minVersion', 'N/A')}")
        print(f"  Max Version: {api_info.get('maxVersion', 'N/A')}")

        # Try to get methods
        try:
            methods_url = f"{api.base_url}{api_info.get('path', '')}"
            methods_params = {
                "api": api_name,
                "version": api_info.get('maxVersion', '1'),
                "method": "list",
                "_sid": api.sid
            }
            methods_response = api.session.get(methods_url, params=methods_params, timeout=10, verify=False)
            methods_data = methods_response.json()
            if methods_data.get("success"):
                print(f"  Methods available: {methods_data.get('data', {})}")
        except:
            pass
else:
    print("Failed to query APIs")

api.logout()
