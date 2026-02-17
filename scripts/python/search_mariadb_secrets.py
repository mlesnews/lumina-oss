#!/usr/bin/env python3
"""Search for all MariaDB-related secrets in Azure Vault and ProtonPass"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from unified_secrets_manager import UnifiedSecretsManager, SecretSource

project_root = Path(__file__).parent.parent.parent
manager = UnifiedSecretsManager(project_root)

print("=" * 60)
print("🔍 SEARCHING FOR MARIADB SECRETS")
print("=" * 60)

# Get all secrets from both sources
print("\n📦 Azure Key Vault:")
az_secrets = manager.list_secrets(SecretSource.AZURE_KEY_VAULT)
all_az = az_secrets.get('azure_key_vault', [])
mariadb_az = [s for s in all_az if 'mariadb' in s.lower()]
print(f"   Found {len(mariadb_az)} MariaDB secrets:")
for secret in mariadb_az:
    print(f"     - {secret}")
    try:
        value = manager.get_secret(secret, source=SecretSource.AZURE_KEY_VAULT)
        if value:
            if 'password' in secret.lower():
                print(f"       Value: {'*' * len(value)} (length: {len(value)})")
            else:
                print(f"       Value: {value}")
    except Exception as e:
        print(f"       Error: {e}")

print("\n📦 ProtonPass:")
pp_secrets = manager.list_secrets(SecretSource.PROTONPASS)
all_pp = pp_secrets.get('protonpass', [])
mariadb_pp = [s for s in all_pp if 'mariadb' in s.lower()]
print(f"   Found {len(mariadb_pp)} MariaDB secrets:")
if mariadb_pp:
    for secret in mariadb_pp:
        print(f"     - {secret}")
        try:
            value = manager.get_secret(secret, source=SecretSource.PROTONPASS)
            if value:
                if 'password' in secret.lower():
                    print(f"       Value: {'*' * len(value)} (length: {len(value)})")
                else:
                    print(f"       Value: {value}")
        except Exception as e:
            print(f"       Error: {e}")
else:
    print("     None found")

# Try specific patterns
print("\n🔎 Trying specific patterns:")
patterns = [
    'mariadb-user',
    'mariadb-username', 
    'mariadb-account',
    'mariadb-login',
    'mariadb-db-user',
    'mariadb-db-username',
    'mariadb-root-user',
    'mariadb-root-username',
]

for pattern in patterns:
    for source in [SecretSource.AZURE_KEY_VAULT, SecretSource.PROTONPASS]:
        try:
            value = manager.get_secret(pattern, source=source)
            if value:
                source_name = 'Azure Vault' if source == SecretSource.AZURE_KEY_VAULT else 'ProtonPass'
                print(f"   ✅ {pattern} ({source_name}): {value}")
        except:
            pass

# Also search all secrets for anything that might be MariaDB related
print("\n🔎 Searching ALL secrets for MariaDB/database keywords:")
all_az_secrets = az_secrets.get('azure_key_vault', [])
db_related = [s for s in all_az_secrets if any(kw in s.lower() for kw in ['mariadb', 'mysql', 'db-', 'database-', 'sql-'])]
if db_related:
    print(f"   Found {len(db_related)} potentially related secrets:")
    for secret in db_related:
        print(f"     - {secret}")
        try:
            value = manager.get_secret(secret, source=SecretSource.AZURE_KEY_VAULT)
            if value and 'password' not in secret.lower():
                print(f"       Value: {value}")
            elif value:
                print(f"       Value: [REDACTED]")
        except:
            pass
else:
    print("   None found")

print("\n" + "=" * 60)
