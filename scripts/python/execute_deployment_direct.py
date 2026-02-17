#!/usr/bin/env python3
"""Execute deployment directly via paramiko"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import paramiko
import time
from nas_azure_vault_integration import NASAzureVaultIntegration

vault = NASAzureVaultIntegration()
creds = vault.get_nas_credentials()

print(f"Connecting as {creds['username']}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('<NAS_PRIMARY_IP>', username=creds['username'], password=creds['password'], timeout=10)

# Execute deployment directly
print("Executing deployment...")
command = f'cd /volume1/docker/nas-mcp-servers && echo "{creds["password"]}" | sudo -S /usr/local/bin/docker-compose -f docker-compose.yml up -d --build 2>&1'

stdin, stdout, stderr = ssh.exec_command(command, timeout=600)

# Stream output
output = ""
while True:
    if stdout.channel.recv_ready():
        data = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
        output += data
        print(data, end='', flush=True)

    if stdout.channel.exit_status_ready():
        break

    time.sleep(0.1)

exit_status = stdout.channel.recv_exit_status()
remaining = stdout.read().decode('utf-8', errors='ignore')
error = stderr.read().decode('utf-8', errors='ignore')

print("\n=== FINAL OUTPUT ===")
print(remaining)
if error:
    print("\n=== ERRORS ===")
    print(error)

print(f"\n=== EXIT STATUS: {exit_status} ===")

ssh.close()

if exit_status == 0:
    print("\n✅ DEPLOYMENT SUCCESSFUL!")
else:
    print(f"\n❌ DEPLOYMENT FAILED (exit code: {exit_status})")
