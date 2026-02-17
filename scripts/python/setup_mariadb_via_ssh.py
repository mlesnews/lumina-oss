#!/usr/bin/env python3
"""
SETUP MARIADB VIA SSH (ROOT ACCESS)
Uses SSH root access to configure MariaDB permissions on NAS
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_AVAILABLE = True
except ImportError:
    NAS_AVAILABLE = False
    print("⚠️  nas_azure_vault_integration not available")

try:
    from unified_secrets_manager import SecretSource, UnifiedSecretsManager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

def get_admin_password():
    """Get admin password from Azure Vault."""
    if not SECRETS_MANAGER_AVAILABLE:
        return None

    project_root = Path(__file__).parent.parent.parent
    manager = UnifiedSecretsManager(project_root)

    try:
        return manager.get_secret("admin-password", source=SecretSource.AZURE_KEY_VAULT)
    except:
        return None

def setup_mariadb_via_ssh(database_name="lumina_holocrons", allow_host="%"):
    """Setup MariaDB permissions via SSH root access."""
    print("=" * 60)
    print("🔧 MARIADB SETUP VIA SSH (ROOT ACCESS)")
    print("=" * 60)

    if not NAS_AVAILABLE:
        print("❌ NAS integration not available")
        return 1

    # Initialize NAS integration (gets credentials from Azure Vault)
    nas = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")

    print("\n🔌 Connecting to NAS via SSH...")
    ssh_client = nas.get_ssh_client()

    if not ssh_client:
        print("❌ Failed to connect to NAS via SSH")
        return 1

    print("   ✅ Connected to NAS!")

    # Get admin password
    admin_password = get_admin_password()
    if not admin_password:
        print("❌ Admin password not found in Azure Vault")
        print("   Run: python scripts/python/add_admin_to_vault.py")
        ssh_client.close()
        return 1

    print(f"\n📦 Database: {database_name}")
    print(f"   User: admin@{allow_host}")

    # SQL commands to run
    sql_commands = [
        f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"CREATE USER IF NOT EXISTS 'admin'@'{allow_host}' IDENTIFIED BY '{admin_password}';",
        f"GRANT ALL PRIVILEGES ON `{database_name}`.* TO 'admin'@'{allow_host}';",
        f"GRANT CREATE ON *.* TO 'admin'@'{allow_host}';",
        "FLUSH PRIVILEGES;",
        "SELECT User, Host FROM mysql.user WHERE User='admin';",
    ]

    print("\n📝 Running MariaDB setup commands...")

    try:
        # Find mysql/mariadb command on Synology
        print("   🔍 Finding MariaDB command...")
        # Try Synology default paths first
        mysql_paths = [
            "/usr/local/mariadb10/bin/mysql",
            "/usr/local/mariadb/bin/mysql",
            "/usr/bin/mysql",
            "/opt/bin/mysql",
        ]

        mysql_path = None
        for path in mysql_paths:
            test_cmd = f"test -x {path} && echo {path} || echo ''"
            stdin, stdout, stderr = ssh_client.exec_command(test_cmd)
            result = stdout.read().decode('utf-8').strip()
            if result and result == path:
                mysql_path = result
                break

        # If not found, try which/find
        if not mysql_path:
            find_cmd = "which mysql 2>/dev/null || find /usr/local -type f -name mysql -perm +111 2>/dev/null | head -1"
            stdin, stdout, stderr = ssh_client.exec_command(find_cmd)
            result = stdout.read().decode('utf-8').strip()
            if result and '/mysql' in result and 'python' not in result.lower():
                mysql_path = result

        if not mysql_path:
            print("   ⚠️  Could not find mysql, using default path")
            mysql_path = "/usr/local/mariadb10/bin/mysql"

        print(f"   ✅ Using: {mysql_path}")

        # Get root password from vault
        root_password = None
        if SECRETS_MANAGER_AVAILABLE:
            project_root = Path(__file__).parent.parent.parent
            manager = UnifiedSecretsManager(project_root)
            try:
                root_password = manager.get_secret("mariadb-root-password", source=SecretSource.AZURE_KEY_VAULT)
            except:
                pass

        if root_password:
            mysql_command = f"{mysql_path} -u root -p'{root_password}'"
        else:
            # Try without password (if root has local access)
            mysql_command = f"{mysql_path} -u root"

        # Execute SQL commands
        for i, sql in enumerate(sql_commands, 1):
            print(f"   [{i}/{len(sql_commands)}] {sql[:50]}...")

            # Escape SQL for shell - use single quotes and escape properly
            escaped_sql = sql.replace("'", "'\"'\"'")
            command = f"{mysql_command} -e '{escaped_sql}'"

            stdin, stdout, stderr = ssh_client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            if exit_status == 0:
                if output.strip():
                    print(f"      ✅ {output.strip()[:100]}")
                else:
                    print("      ✅ Command executed")
            else:
                error_msg = error.strip()[:200] if error else 'Command failed'
                # Some errors are OK (like user already exists)
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    print(f"      ⚠️  {error_msg} (OK - already exists)")
                else:
                    print(f"      ❌ {error_msg}")

        print("\n" + "=" * 60)
        print("✅ MARIADB SETUP COMPLETE!")
        print("=" * 60)
        print("\n📋 Configuration:")
        print(f"   Database: {database_name}")
        print(f"   User: admin@{allow_host}")
        print("\n🧪 Test connection:")
        print("   python scripts/python/test_mariadb_connection.py \\")
        print(f"     --host <NAS_PRIMARY_IP> --database {database_name}")
        print("=" * 60)

        ssh_client.close()
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        ssh_client.close()
        return 1

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Setup MariaDB via SSH root access")
    parser.add_argument('--database', default='lumina_holocrons', help='Database name')
    parser.add_argument('--allow-host', default='%', help='Allow from host (default: % for any)')

    args = parser.parse_args()

    return setup_mariadb_via_ssh(args.database, args.allow_host)

if __name__ == "__main__":


    sys.exit(main())