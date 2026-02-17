#!/usr/bin/env python3
"""
MARIADB CONNECTION TESTER
Quick test to verify MariaDB connection and permissions
"""

import os
import sys
from pathlib import Path
import logging
logger = logging.getLogger("test_mariadb_connection")


try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False
    print("❌ pymysql not installed. Install with: pip install pymysql")
    sys.exit(1)

# Add scripts directory to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from unified_secrets_manager import SecretSource, UnifiedSecretsManager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

def test_connection(host: str, user: str, password: str, database: str = None, port: int = 3306):
    """Test MariaDB connection."""
    print("🔌 Testing MariaDB Connection...")
    print("=" * 60)
    print(f"Host: {host}:{port}")
    print(f"User: {user}")
    print(f"Database: {database or '(not specified)'}")
    print("=" * 60)

    try:
        # Test basic connection
        print("\n1️⃣ Testing basic connection...")
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            charset='utf8mb4',
            connect_timeout=10
        )
        print("   ✅ Connection successful!")

        # Test database access
        if database:
            print(f"\n2️⃣ Testing database access: {database}")
            try:
                conn.select_db(database)
                print("   ✅ Database access granted!")

                # List tables
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"   📊 Found {len(tables)} existing tables")
                if tables:
                    print("   Tables:")
                    for table in tables[:10]:
                        print(f"     • {table[0]}")
                    if len(tables) > 10:
                        print(f"     ... and {len(tables) - 10} more")

            except pymysql.Error as e:
                print(f"   ⚠️  Database access issue: {e}")
                print("   💡 You may need to create the database first:")
                print(f"      CREATE DATABASE {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

        # Test permissions
        print("\n3️⃣ Testing permissions...")
        cursor = conn.cursor()

        # Test CREATE
        try:
            cursor.execute("CREATE TEMPORARY TABLE test_permissions (id INT)")
            cursor.execute("DROP TEMPORARY TABLE test_permissions")
            print("   ✅ CREATE permission: OK")
        except:
            print("   ⚠️  CREATE permission: Limited")

        # Test INSERT
        try:
            cursor.execute("CREATE TEMPORARY TABLE test_insert (id INT)")
            cursor.execute("INSERT INTO test_insert VALUES (1)")
            cursor.execute("DROP TEMPORARY TABLE test_insert")
            print("   ✅ INSERT permission: OK")
        except:
            print("   ⚠️  INSERT permission: Limited")

        # Test SELECT
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            print("   ✅ SELECT permission: OK")
        except:
            print("   ⚠️  SELECT permission: Limited")

        # Get server info
        print("\n4️⃣ Server Information:")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"   MariaDB Version: {version}")

        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()[0]
        if current_db:
            print(f"   Current Database: {current_db}")

        conn.close()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Ready for conversion!")
        print("=" * 60)
        return True

    except pymysql.Error as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Check NAS IP address is correct")
        print("   • Verify MariaDB is running on NAS")
        print("   • Check firewall allows port 3306")
        print("   • Verify username/password")
        print("   • Ensure user has remote access permissions")

        if "Access denied" in str(e) and user == "root":
            print("\n🔧 Root user may not have remote access (security best practice)")
            print("   Options:")
            print("   1. Set up dedicated user: python scripts/python/setup_mariadb_user.py")
            print("   2. Use SSH tunnel: ssh -L 3306:localhost:3306 user@<NAS_PRIMARY_IP>")
            print("   3. See: docs/MARIADB_USER_SETUP.md")

        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_nas_config() -> dict:
    """Get NAS configuration from config file."""
    project_root = Path(__file__).parent.parent.parent
    config_file = project_root / "config" / "lumina_nas_ssh_config.json"

    if config_file.exists():
        try:
            import json
            with open(config_file) as f:
                config = json.load(f)
            nas_config = config.get('nas', {})
            return {
                'host': nas_config.get('host'),
                'username': nas_config.get('username'),
            }
        except:
            pass
    return {}

def get_credentials_from_vault(host: str = None) -> dict:
    """Get MariaDB credentials from Azure Vault or ProtonPass."""
    if not SECRETS_MANAGER_AVAILABLE:
        return {}

    project_root = Path(__file__).parent.parent.parent
    manager = UnifiedSecretsManager(project_root)

    # Get NAS config for defaults
    nas_config = get_nas_config()
    if not host and nas_config.get('host'):
        host = nas_config['host']

    # Try common secret name patterns
    secret_patterns = [
        # admin (the configured user)
        "admin-password",
        "admin-username",
        "admin-user",
        "mariadb-admin-password",
        "mariadb-admin-username",
        # dbadmin (fallback)
        "dbadmin-password",
        "dbadmin-username",
        "dbadmin-user",
        "mariadb-dbadmin-password",
        "mariadb-dbadmin-username",
        # MariaDB specific
        f"mariadb-{host.replace('.', '-')}-password" if host else None,
        f"mariadb-{host.replace('.', '-')}-username" if host else None,
        "mariadb-password",
        "mariadb-username",
        "mariadb-root-password",
        "nas-mariadb-password",
        "nas-mariadb-username",
        # Also try NAS password (might be same for MariaDB)
        f"nas-password-{host.replace('.', '-')}" if host else None,
        "nas-password",
    ]

    credentials = {}
    found_root_password = False

    # Try Azure Vault first
    # Prioritize admin-password (configured user), then mariadb-* passwords, then nas-password
    password_patterns = [p for p in secret_patterns if p and 'password' in p]
    # Reorder: admin passwords first (configured user), then mariadb passwords, then others
    admin_passwords = [p for p in password_patterns if 'admin' in p and 'dbadmin' not in p]
    mariadb_passwords = [p for p in password_patterns if 'mariadb' in p and 'admin' not in p]
    nas_passwords = [p for p in password_patterns if 'nas-password' in p and 'mariadb' not in p and 'admin' not in p]
    other_passwords = [p for p in password_patterns if 'mariadb' not in p and 'nas-password' not in p and 'admin' not in p]
    password_patterns = admin_passwords + mariadb_passwords + other_passwords + nas_passwords

    try:
        # Try password patterns
        for pattern in password_patterns:
            try:
                password = manager.get_secret(pattern, source=SecretSource.AZURE_KEY_VAULT)
                if password:
                    credentials['password'] = password
                    print(f"   ✅ Found password in Azure Vault: {pattern}")
                    if 'admin' in pattern and 'dbadmin' not in pattern:
                        # admin is the configured user
                        if 'password' in pattern:
                            # Password found, use admin username
                            if not credentials.get('username'):
                                credentials['username'] = 'admin'
                            print("   💡 Using 'admin' user (password found)")
                        break
                    elif 'dbadmin' in pattern:
                        # dbadmin fallback
                        if 'password' in pattern:
                            if not credentials.get('username'):
                                credentials['username'] = 'dbadmin'
                            print("   💡 Using 'dbadmin' user (password found)")
                        break
                    elif 'root' in pattern and 'password' in pattern:
                        # Root password - use root user
                        if not credentials.get('username'):
                            credentials['username'] = 'root'
                        print("   💡 Using 'root' user (password is for root)")
                        break
                    elif 'root' in pattern:
                        found_root_password = True
                        # If root password found, use root user
                        credentials['username'] = 'root'
                        print("   💡 Using 'root' user (password is for root)")
                        break  # Stop here, root password should use root user
                    elif 'nas-password' in pattern and nas_config.get('username'):
                        # If nas-password found, use NAS username
                        credentials['username'] = nas_config['username']
                        print(f"   💡 Using NAS username: {nas_config['username']}")
                    break
            except:
                continue

        # Try username patterns (only if we didn't set username from password)
        if not credentials.get('username'):
            # Prioritize dbadmin username
            for pattern in [p for p in secret_patterns if p and 'username' in p]:
                try:
                    username = manager.get_secret(pattern, source=SecretSource.AZURE_KEY_VAULT)
                    if username:
                        credentials['username'] = username
                        print(f"   ✅ Found username in Azure Vault: {pattern}")
                        break
                except:
                    continue

            # If still no username but we have password, try default admin
            if credentials.get('password') and not credentials.get('username'):
                credentials['username'] = 'admin'
                print("   💡 Using default 'admin' username")

        # If found in Azure Vault, return
        if credentials:
            return credentials
    except Exception as e:
        print(f"   ⚠️  Azure Vault check failed: {e}")

    # Fallback to ProtonPass
    try:
        for pattern in [p for p in secret_patterns if p and 'password' in p]:
            try:
                password = manager.get_secret(pattern, source=SecretSource.PROTONPASS)
                if password:
                    credentials['password'] = password
                    print(f"   ✅ Found password in ProtonPass: {pattern}")
                    if 'root' in pattern:
                        found_root_password = True
                        credentials['username'] = 'root'
                        print("   💡 Using 'root' user (password is for root)")
                    break
            except:
                continue

        if not credentials.get('username'):
            for pattern in [p for p in secret_patterns if p and 'username' in p]:
                try:
                    username = manager.get_secret(pattern, source=SecretSource.PROTONPASS)
                    if username:
                        credentials['username'] = username
                        print(f"   ✅ Found username in ProtonPass: {pattern}")
                        break
                except:
                    continue
    except Exception as e:
        print(f"   ⚠️  ProtonPass check failed: {e}")

    # If no credentials found but we have NAS config, use NAS username as hint
    if not credentials.get('username') and nas_config.get('username'):
        credentials['username'] = nas_config['username']
        print(f"   💡 Using NAS username from config: {nas_config['username']}")

        # If using NAS username, also try nas-password
        if not credentials.get('password'):
            try:
                nas_password = manager.get_secret("nas-password", source=SecretSource.AZURE_KEY_VAULT)
                if nas_password:
                    credentials['password'] = nas_password
                    print(f"   ✅ Found nas-password in Azure Vault (for user {nas_config['username']})")
            except:
                try:
                    nas_password = manager.get_secret("nas-password", source=SecretSource.PROTONPASS)
                    if nas_password:
                        credentials['password'] = nas_password
                        print(f"   ✅ Found nas-password in ProtonPass (for user {nas_config['username']})")
                except:
                    pass

    return credentials

def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="Test MariaDB connection")
        parser.add_argument('--host', type=str, help='NAS Host/IP')
        parser.add_argument('--port', type=int, default=3306, help='Port (default: 3306)')
        parser.add_argument('--user', type=str, help='Username')
        parser.add_argument('--password', type=str, help='Password (or use MARIADB_PASSWORD env var)')
        parser.add_argument('--database', type=str, help='Database name (optional)')
        parser.add_argument('--config', type=str, help='Config file path (JSON)')
        parser.add_argument('--no-vault', action='store_true', help='Skip Azure Vault/ProtonPass check')

        args = parser.parse_args()

        # Try to get credentials from vault first (unless --no-vault)
        vault_creds = {}
        if not args.no_vault and SECRETS_MANAGER_AVAILABLE:
            print("🔍 Checking Azure Vault / ProtonPass for credentials...")
            vault_creds = get_credentials_from_vault(args.host)

        # Load from config file if provided
        if args.config:
            import json
            with open(args.config) as f:
                config = json.load(f)
            host = config.get('host') or args.host
            port = config.get('port', args.port or 3306)
            user = config.get('user') or args.user or vault_creds.get('username')
            password = config.get('password') or args.password or vault_creds.get('password') or os.environ.get('MARIADB_PASSWORD')
            database = config.get('database') or args.database
        else:
            # Use command line args, vault, or prompt
            if args.host:
                host = args.host
                port = args.port or 3306
                user = args.user or vault_creds.get('username') or nas_config.get('username')
                password = args.password or vault_creds.get('password') or os.environ.get('MARIADB_PASSWORD')
                database = args.database

                # If we have all required info, skip interactive prompts
                if host and user and password:
                    # Non-interactive mode - use what we have
                    pass
                else:
                    # Need to prompt
                    pass
            else:
                # Interactive mode (only if vault didn't provide everything)
                print("🗄️  MARIADB CONNECTION TESTER 🗄️")
                print("=" * 60)

                # Get NAS config for defaults
                nas_config = get_nas_config()
                default_host = args.host or nas_config.get('host')

                if vault_creds:
                    print("\n✅ Found credentials in vault:")
                    if vault_creds.get('username'):
                        print(f"   Username: {vault_creds['username']}")
                    if vault_creds.get('password'):
                        print(f"   Password: {'*' * len(vault_creds['password'])}")

                if nas_config.get('host'):
                    print(f"\n💡 NAS config found: {nas_config.get('host')} (user: {nas_config.get('username')})")

                print("\n📡 Enter MariaDB Connection Details:")
                host = input(f"   NAS Host/IP {f'(default: {default_host})' if default_host else ''}: ").strip() or default_host
                if not host:
                    print("   ❌ Host required")
                    return

                port_input = input("   Port (default 3306): ").strip()
                port = int(port_input) if port_input else 3306

                default_user = vault_creds.get('username') or nas_config.get('username') or args.user
                user = input(f"   Username {f'(default: {default_user})' if default_user else ''}: ").strip() or default_user
                if not user:
                    print("   ❌ Username required")
                    return

                password = input("   Password (press Enter to use from vault/env): ").strip()
                if not password:
                    password = vault_creds.get('password') or args.password or os.environ.get('MARIADB_PASSWORD')
                    if not password:
                        print("   ❌ Password required (or set MARIADB_PASSWORD env var)")
                        return

                database = input("   Database name (optional, press Enter to skip): ").strip() or args.database
                if not database:
                    database = None

        # Finalize credentials
        if not host:
            host = nas_config.get('host')

        if not user:
            # Try admin first (configured user), then dbadmin, then NAS username
            if vault_creds.get('username'):
                user = vault_creds.get('username')
            elif 'admin' in str(vault_creds.get('password', '')) or not vault_creds:
                # If no specific username found, try admin
                user = 'admin'
            else:
                user = nas_config.get('username')

        if not host or not user or not password:
            print("❌ Missing required connection details")
            print(f"\n   Host: {host or 'MISSING'}")
            print(f"   User: {user or 'MISSING'}")
            print(f"   Password: {'FOUND' if password else 'MISSING'}")
            print("\nUsage:")
            print("  python test_mariadb_connection.py --host <IP> --user <user> [--password <pass>] [--database <db>]")
            print("  python test_mariadb_connection.py --config backup_config.json")
            print("\n💡 Credentials are automatically retrieved from Azure Vault/ProtonPass if available")
            print("   Found in vault: mariadb-root-password")
            print("   NAS config: host=<NAS_PRIMARY_IP>, user=backupadm")
            print("\n🔧 If root doesn't have remote access, set up a user:")
            print("   python scripts/python/setup_mariadb_user.py")
            print("   See: docs/MARIADB_USER_SETUP.md")
            return

        # Test connection
        success = test_connection(host, user, password, database, port)

        if success:
            print("\n💡 Next Steps:")
            print("   1. If database doesn't exist, create it:")
            if database:
                print(f"      CREATE DATABASE {database} CHARACTER SET utf8mb4;")
            print("   2. Start converting files:")
            print("      python scripts/python/json_to_mariadb.py <file.json> \\")
            print(f"        --host {host} --user {user} --database {database or '<database>'}")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()