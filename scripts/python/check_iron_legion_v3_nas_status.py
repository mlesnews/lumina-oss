#!/usr/bin/env python3
"""
Check Iron Legion V3 with NAS Containers Status
"""

import json
import sys
from pathlib import Path
import subprocess
import requests
from typing import Dict, List, Optional

from lumina_core.paths import get_project_root
project_root = get_project_root()

def check_iron_legion_status() -> Dict:
    """Check Iron Legion cluster status"""
    config_file = project_root / "config" / "iron_legion_cluster_config.json"

    if not config_file.exists():
        return {"status": "config_not_found", "error": "Config file not found"}

    with open(config_file, 'r') as f:
        config = json.load(f)

    cluster_info = config.get("cluster_info", {})
    models = config.get("standalone_access", {}).get("models", {})

    # Check each model endpoint
    model_status = {}
    for model_id, model_config in models.items():
        endpoint = model_config.get("endpoint", "")
        status = model_config.get("status", "unknown")

        # Try to ping endpoint
        try:
            response = requests.get(f"{endpoint}/health", timeout=2)
            ping_status = "online" if response.status_code == 200 else "offline"
        except requests.RequestException:
            ping_status = "offline"

        model_status[model_id] = {
            "config_status": status,
            "ping_status": ping_status,
            "endpoint": endpoint
        }

    return {
        "cluster_name": cluster_info.get("name", "Iron Legion"),
        "cluster_endpoint": cluster_info.get("cluster_endpoint", ""),
        "total_models": cluster_info.get("total_models", 0),
        "operational_models": cluster_info.get("operational_models", 0),
        "model_status": model_status,
        "config_status": cluster_info.get("status", "unknown")
    }

def check_nas_containers() -> Dict:
    """Check NAS container status"""
    nas_ip = "<NAS_PRIMARY_IP>"

    # Check if NAS is reachable
    try:
        requests.get(f"http://{nas_ip}:5000", timeout=2)
        nas_reachable = True
    except requests.RequestException:
        nas_reachable = False

    # Check for Iron Legion router on NAS
    router_endpoint = f"http://{nas_ip}:3000"
    try:
        response = requests.get(f"{router_endpoint}/health", timeout=2)
        router_online = response.status_code == 200
    except requests.RequestException:
        router_online = False

    return {
        "nas_reachable": nas_reachable,
        "nas_ip": nas_ip,
        "router_endpoint": router_endpoint,
        "router_online": router_online
    }

def main():
    """Check status"""
    print("=" * 80)
    print("IRON LEGION V3 + NAS CONTAINERS STATUS")
    print("=" * 80)
    print()

    # Check Iron Legion
    print("Iron Legion Cluster:")
    print("-" * 80)
    iron_status = check_iron_legion_status()
    print(f"  Cluster: {iron_status.get('cluster_name', 'Unknown')}")
    print(f"  Endpoint: {iron_status.get('cluster_endpoint', 'Unknown')}")
    print(f"  Total Models: {iron_status.get('total_models', 0)}")
    print(f"  Operational: {iron_status.get('operational_models', 0)}")
    print(f"  Status: {iron_status.get('config_status', 'Unknown')}")
    print()

    print("  Model Status:")
    for model_id, status in iron_status.get("model_status", {}).items():
        ping_icon = "✅" if status["ping_status"] == "online" else "❌"
        # Truncate output to fit within 100 chars
        line = f"    {ping_icon} {model_id}: {status['config_status']} " \
               f"(ping: {status['ping_status']})"
        print(line)
    print()

    # Check NAS
    print("NAS Containers:")
    print("-" * 80)
    nas_status = check_nas_containers()
    nas_icon = "✅" if nas_status["nas_reachable"] else "❌"
    router_icon = "✅" if nas_status["router_online"] else "❌"
    print(f"  {nas_icon} NAS Reachable: {nas_status['nas_ip']}")
    print(f"  {router_icon} Router Online: {nas_status['router_endpoint']}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    iron_operational = iron_status.get("operational_models", 0) > 0
    nas_operational = nas_status["router_online"]

    if iron_operational and nas_operational:
        print("✅ Iron Legion V3 + NAS Containers: OPERATIONAL")
    elif iron_operational:
        print("⚠️  Iron Legion V3: OPERATIONAL, NAS Containers: NOT READY")
    elif nas_operational:
        print("⚠️  NAS Containers: OPERATIONAL, Iron Legion V3: NOT READY")
    else:
        print("❌ Iron Legion V3 + NAS Containers: NOT READY")

    return {
        "iron_legion": iron_status,
        "nas_containers": nas_status,
        "overall_status": "operational" if (iron_operational and nas_operational) else "not_ready"
    }

if __name__ == "__main__":
    sys.exit(0)


    result = main()