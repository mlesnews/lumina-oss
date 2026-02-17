#!/usr/bin/env python3
"""Check container status on NAS"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import paramiko
from nas_azure_vault_integration import NASAzureVaultIntegration

vault = NASAzureVaultIntegration()
creds = vault.get_nas_credentials()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('<NAS_PRIMARY_IP>', username=creds['username'], password=creds['password'], timeout=10)

# Check containers
stdin, stdout, stderr = ssh.exec_command('echo "' + creds['password'] + '" | sudo -S /usr/local/bin/docker ps -a --format "{{.Names}} - {{.Status}}" 2>&1 | head -30', timeout=30)
print("=== CONTAINER STATUS ===")
print(stdout.read().decode())
print("\n=== ERRORS ===")
print(stderr.read().decode())

# Check compose status
stdin2, stdout2, stderr2 = ssh.exec_command('cd /volume1/docker/nas-mcp-servers && echo "' + creds['password'] + '" | sudo -S /usr/local/bin/docker-compose ps 2>&1', timeout=30)
print("\n=== DOCKER-COMPOSE STATUS ===")
print(stdout2.read().decode())

ssh.close()
