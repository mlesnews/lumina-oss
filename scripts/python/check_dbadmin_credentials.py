#!/usr/bin/env python3
"""Check for dbAdmin credentials in Azure Key Vault"""
import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration

vault = NASAzureVaultIntegration()
# Initialize vault client
vault.get_key_vault_client()

# Secret patterns to check
secret_patterns = [
    "dbadmin-username",
    "dbadmin-password", 
    "dbadmin-user",
    "mariadb-dbadmin-username",
    "mariadb-dbadmin-password",
    "mariadb-dbadmin-user",
    "nas-dbadmin-username",
    "nas-dbadmin-password"
]

print("Checking for dbAdmin credentials in Azure Key Vault...")
print("=" * 60)

found_username = None
found_password = None

for pattern in secret_patterns:
    try:
        # Use the get_secret method properly
        client = vault.get_key_vault_client()
        if client:
            secret = client.get_secret(pattern)
            value = secret.value
            if value:
                if 'username' in pattern or 'user' in pattern:
                    found_username = (pattern, value)
                    print(f"✅ Found username: {pattern} = {value}")
                elif 'password' in pattern:
                    found_password = (pattern, value)
                    print(f"✅ Found password: {pattern} = [REDACTED]")
        else:
            print(f"⚠️  {pattern}: Vault client not available")
    except Exception as e:
        # Secret doesn't exist or error accessing
        error_msg = str(e)
        error_type = type(e).__name__
        if "NotFound" in error_msg or "404" in error_msg or "ResourceNotFound" in error_type:
            # Secret doesn't exist - this is expected for some patterns
            pass
        else:
            print(f"❌ {pattern}: Error ({error_type}: {error_msg[:50]})")

print("=" * 60)

if found_username and found_password:
    print(f"\n✅ Credentials found!")
    print(f"   Username secret: {found_username[0]}")
    print(f"   Password secret: {found_password[0]}")
    print(f"\n💡 These will be used for MariaDB MCP server connection")
elif found_password:
    print(f"\n⚠️  Password found but no username - will default to 'dbadmin'")
    print(f"   Password secret: {found_password[0]}")
elif found_username:
    print(f"\n⚠️  Username found but no password")
    print(f"   Username secret: {found_username[0]}")
else:
    print(f"\n❌ No dbAdmin credentials found in Azure Key Vault")
    print(f"\n💡 You may need to add these secrets:")
    print(f"   - dbadmin-username (or dbadmin-user)")
    print(f"   - dbadmin-password")
