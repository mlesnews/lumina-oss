#!/usr/bin/env python3
"""
Deploy MCP Server Containers to Synology NAS
Creates and starts MCP service containers via Container Manager API
"""

import sys
from pathlib import Path

# Add scripts path
sys.path.insert(0, str(Path(__file__).parent))

from nas_azure_vault_integration import NASAzureVaultIntegration
from synology_container_manager import SynologyContainerManager

# MCP Container definitions
MCP_CONTAINERS = [
    {
        "name": "filesystem-mcp-server",
        "image": "modelcontextprotocol/server-filesystem:latest",
        "ports": {"8099": 8099},
        "env": {"SERVICE_NAME": "filesystem-mcp-server", "PORT": "8099"},
        "volumes": {"/volume1": "/mnt/volume1"},
    },
    {
        "name": "git-mcp-server",
        "image": "modelcontextprotocol/server-git:latest",
        "ports": {"8100": 8100},
        "env": {"SERVICE_NAME": "git-mcp-server", "PORT": "8100"},
    },
    {
        "name": "sqlite-mcp-server",
        "image": "modelcontextprotocol/server-sqlite:latest",
        "ports": {"8098": 8098},
        "env": {"SERVICE_NAME": "sqlite-mcp-server", "PORT": "8098"},
    },
    {
        "name": "brave-search-mcp-server",
        "image": "modelcontextprotocol/server-brave-search:latest",
        "ports": {"8101": 8101},
        "env": {"SERVICE_NAME": "brave-search-mcp-server", "PORT": "8101"},
    },
    {
        "name": "puppeteer-mcp-server",
        "image": "modelcontextprotocol/server-puppeteer:latest",
        "ports": {"8102": 8102},
        "env": {"SERVICE_NAME": "puppeteer-mcp-server", "PORT": "8102"},
    },
    {
        "name": "github-mcp-server",
        "image": "modelcontextprotocol/server-github:latest",
        "ports": {"8103": 8103},
        "env": {"SERVICE_NAME": "github-mcp-server", "PORT": "8103"},
    },
    {
        "name": "slack-mcp-server",
        "image": "modelcontextprotocol/server-slack:latest",
        "ports": {"8104": 8104},
        "env": {"SERVICE_NAME": "slack-mcp-server", "PORT": "8104"},
    },
]


def main():
    print("=" * 60)
    print("MCP Container Deployment to Synology NAS")
    print("=" * 60)

    # Get credentials from Azure Key Vault
    print("\nGetting credentials from Azure Key Vault...")
    vault = NASAzureVaultIntegration()
    creds = vault.get_nas_credentials()
    if not creds:
        print("ERROR: Failed to get NAS credentials")
        return 1

    username = creds["username"]
    password = creds["password"]
    print(f"Username: {username}")

    # Initialize manager
    manager = SynologyContainerManager()

    if not manager.login(username, password):
        print("ERROR: Failed to login to NAS")
        return 1

    try:
        # Get existing containers
        existing = manager.list_containers()
        existing_names = [c.get("name") for c in (existing or [])]
        print(f"\nExisting containers: {existing_names}")

        # Deploy each MCP container
        success_count = 0
        skip_count = 0
        fail_count = 0

        for container_def in MCP_CONTAINERS:
            name = container_def["name"]
            print(f"\n{'=' * 40}")
            print(f"Processing: {name}")

            if name in existing_names:
                print("  ⏭️  Skipping (already exists)")
                skip_count += 1
                continue

            # Create and run container
            result = manager.run_container(
                image=container_def["image"],
                name=name,
                port_bindings=container_def.get("ports"),
                env_vars=container_def.get("env"),
                volumes=container_def.get("volumes"),
                auto_restart=True,
            )

            if result:
                print(f"  ✅ Successfully deployed: {name}")
                success_count += 1
            else:
                print(f"  ❌ Failed to deploy: {name}")
                fail_count += 1

        print("\n" + "=" * 60)
        print("DEPLOYMENT SUMMARY")
        print("=" * 60)
        print(f"  ✅ Deployed: {success_count}")
        print(f"  ⏭️  Skipped:  {skip_count}")
        print(f"  ❌ Failed:   {fail_count}")
        print("=" * 60)

        return 0 if fail_count == 0 else 1

    finally:
        manager.logout()


if __name__ == "__main__":
    sys.exit(main())
