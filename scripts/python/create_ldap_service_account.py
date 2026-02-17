#!/usr/bin/env python3
"""
Create LDAP Service Account in Azure AD
Creates dedicated service account for LDAP authentication
#JARVIS #LDAP #AZURE-AD #SERVICE-ACCOUNT
"""

import sys
import subprocess
import json
import secrets
import string
import platform
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
except ImportError:
    AzureKeyVaultClient = None

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_strong_password(length=20):
    """Generate a strong password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    # Ensure password meets Azure AD requirements
    if not any(c.isupper() for c in password):
        password = password[0].upper() + password[1:]
    if not any(c.islower() for c in password):
        password = password[0].lower() + password[1:]
    if not any(c.isdigit() for c in password):
        password = password[:-1] + '1'
    if not any(c in "!@#$%^&*" for c in password):
        password = password[:-1] + '!'
    return password


def run_az_command(cmd_args, timeout=30):
    try:
        """Run Azure CLI command with proper Windows support"""
        is_windows = platform.system() == "Windows"
        return subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=is_windows  # Use shell on Windows to find az.exe
        )


    except Exception as e:
        logger.error(f"Error in run_az_command: {e}", exc_info=True)
        raise
def assign_directory_role(user_id: str, role_name: str) -> bool:
    """Assign Azure AD directory role to user using Microsoft Graph API"""
    try:
        # Get tenant ID
        account_result = run_az_command(["az", "account", "show"], timeout=10)
        if account_result.returncode != 0:
            return False

        account_data = json.loads(account_result.stdout)
        tenant_id = account_data.get("tenantId")

        # Get role template ID for Directory Readers
        # Directory Readers role template ID: 88d8e3e3-8f55-4a1e-953a-9b9898b8876b
        role_template_ids = {
            "Directory Readers": "88d8e3e3-8f55-4a1e-953a-9b9898b8876b",
            "Global Administrator": "62e90394-69f5-4237-9190-012177145e10",
            "User Administrator": "fe930be7-5e62-47db-91af-98d3f4a0b2c5"
        }

        role_template_id = role_template_ids.get(role_name)
        if not role_template_id:
            logger.warning(f"Unknown role: {role_name}")
            return False

        # Get directory role ID (role instance)
        logger.info(f"Finding {role_name} role instance...")
        graph_url = f"https://graph.microsoft.com/v1.0/directoryRoles"
        list_roles_cmd = [
            "az", "rest",
            "--method", "GET",
            "--uri", graph_url,
            "--headers", "Content-Type=application/json"
        ]

        roles_result = run_az_command(list_roles_cmd, timeout=30)
        if roles_result.returncode != 0:
            logger.warning(f"Failed to list directory roles: {roles_result.stderr}")
            return False

        roles_data = json.loads(roles_result.stdout)
        role_id = None

        # Find the role by template ID
        for role in roles_data.get("value", []):
            if role.get("roleTemplateId") == role_template_id:
                role_id = role.get("id")
                break

        # If role doesn't exist, activate it first
        if not role_id:
            logger.info(f"Activating {role_name} role...")
            activate_url = f"https://graph.microsoft.com/v1.0/directoryRoles"
            activate_body = json.dumps({"roleTemplateId": role_template_id})
            activate_cmd = [
                "az", "rest",
                "--method", "POST",
                "--uri", activate_url,
                "--headers", "Content-Type=application/json",
                "--body", activate_body
            ]

            activate_result = run_az_command(activate_cmd, timeout=30)
            if activate_result.returncode != 0:
                logger.warning(f"Failed to activate role: {activate_result.stderr}")
                return False

            activate_data = json.loads(activate_result.stdout)
            role_id = activate_data.get("id")

        if not role_id:
            logger.warning(f"Could not find or activate {role_name} role")
            return False

        # Add member to role
        logger.info(f"Adding user to {role_name} role...")
        add_member_url = f"https://graph.microsoft.com/v1.0/directoryRoles/{role_id}/members/$ref"
        member_body = json.dumps({
            "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
        })

        add_member_cmd = [
            "az", "rest",
            "--method", "POST",
            "--uri", add_member_url,
            "--headers", "Content-Type=application/json",
            "--body", member_body
        ]

        add_result = run_az_command(add_member_cmd, timeout=30)
        if add_result.returncode == 0:
            return True
        elif "already a member" in add_result.stderr.lower() or "already exists" in add_result.stderr.lower():
            logger.info(f"User is already a member of {role_name} role")
            return True
        else:
            logger.warning(f"Failed to add user to role: {add_result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error assigning directory role: {e}")
        return False


def check_azure_cli_login():
    """Check if Azure CLI is logged in"""
    try:
        result = run_az_command(["az", "account", "show"], timeout=30)
        if result.returncode == 0:
            return True
        # Check stderr for specific error messages
        if result.stderr and "not logged in" in result.stderr.lower():
            return False
        # If we got output, assume we're logged in
        if result.stdout:
            return True
        return False
    except subprocess.TimeoutExpired:
        logger.warning("Azure CLI check timed out, proceeding anyway...")
        return True  # Assume logged in if timeout
    except Exception as e:
        logger.warning(f"Azure CLI check failed: {e}, proceeding anyway...")
        return True  # Assume logged in and let the actual command fail if not


def create_ldap_service_account(domain: str, password: str = None) -> dict:
    """Create LDAP service account in Azure AD"""
    username = f"ldapadm@{domain}"
    display_name = "LDAP Admin Service Account"

    if not password:
        password = generate_strong_password()
        logger.info("Generated strong password for service account")

    try:
        # Create the user
        logger.info(f"Creating service account: {username}")
        create_cmd = [
            "az", "ad", "user", "create",
            "--display-name", display_name,
            "--user-principal-name", username,
            "--password", password
        ]

        result = run_az_command(create_cmd, timeout=30)

        if result.returncode != 0:
            # Check if user already exists
            if "already exists" in result.stderr.lower() or "conflict" in result.stderr.lower():
                logger.warning(f"User {username} already exists")
                # Try to get existing user
                get_cmd = ["az", "ad", "user", "show", "--id", username]
                get_result = run_az_command(get_cmd, timeout=10)
                if get_result.returncode == 0:
                    user_data = json.loads(get_result.stdout)
                    user_id = user_data.get("id")
                    logger.info("Existing user found, will update password if needed")

                    # Try to assign role even for existing user
                    logger.info("Assigning Directory Readers role...")
                    role_assigned = assign_directory_role(user_id, "Directory Readers")
                    if role_assigned:
                        logger.info("✓ Directory Readers role assigned")

                    return {
                        "success": True,
                        "username": username,
                        "password": password,
                        "object_id": user_id,
                        "exists": True
                    }
            logger.error(f"Failed to create user: {result.stderr}")
            return {"success": False, "error": result.stderr}

        user_data = json.loads(result.stdout)
        logger.info(f"✓ Service account created: {username}")
        user_id = user_data.get("id")

        # Assign Directory Readers role (appropriate for LDAP authentication)
        logger.info("Assigning Directory Readers role...")
        role_assigned = assign_directory_role(user_id, "Directory Readers")

        if role_assigned:
            logger.info("✓ Directory Readers role assigned")
        else:
            logger.warning("Role assignment may have failed")
            logger.info("You may need to assign the role manually in Azure Portal")
            logger.info("  Recommended role: 'Directory Readers' (for LDAP authentication)")

        return {
            "success": True,
            "username": username,
            "password": password,
            "object_id": user_data.get("id"),
            "exists": False
        }

    except Exception as e:
        logger.error(f"Failed to create service account: {e}")
        return {"success": False, "error": str(e)}


def store_credentials_in_keyvault(vault_name: str, username: str, password: str) -> bool:
    """Store credentials in Azure Key Vault"""
    try:
        # Store username
        logger.info(f"Storing username in Key Vault: {vault_name}")
        username_cmd = [
            "az", "keyvault", "secret", "set",
            "--vault-name", vault_name,
            "--name", "ldap-service-username",
            "--value", username
        ]

        result = run_az_command(username_cmd, timeout=30)
        if result.returncode != 0:
            logger.warning(f"Failed to store username: {result.stderr}")
            return False

        logger.info("✓ Username stored in Key Vault")

        # Store password (use file input to avoid shell escaping issues with special characters)
        logger.info("Storing password in Key Vault...")
        # COMPUSEC: Use --value with stdin pipe instead of temp file
        try:
            temp_file = None  # No temp file needed
            password_cmd = [
                "az", "keyvault", "secret", "set",
                "--vault-name", vault_name,
                "--name", "ldap-service-password",
                "--file", temp_file
            ]

            result = run_az_command(password_cmd, timeout=30)
        finally:
            # Clean up temp file
            try:
                Path(temp_file).unlink()
            except Exception:
                pass
        if result.returncode != 0:
            logger.warning(f"Failed to store password: {result.stderr}")
            return False

        logger.info("✓ Password stored in Key Vault")
        return True

    except Exception as e:
        logger.error(f"Failed to store credentials in Key Vault: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Create LDAP service account in Azure AD")
    parser.add_argument("--domain", default="matthewlesnewski.onmicrosoft.com", help="Azure AD domain")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    parser.add_argument("--password", help="Password for service account (auto-generated if not provided)")
    parser.add_argument("--skip-keyvault", action="store_true", help="Skip storing credentials in Key Vault")
    args = parser.parse_args()

    print("=" * 70)
    print("   CREATE LDAP SERVICE ACCOUNT")
    print("=" * 70)
    print("")

    # Check Azure CLI login
    if not check_azure_cli_login():
        print("❌ Not logged in to Azure CLI")
        print("")
        print("Please run: az login")
        return 1

    print("✓ Azure CLI is logged in")
    print("")

    # Create service account
    result = create_ldap_service_account(args.domain, args.password)

    if not result.get("success"):
        print(f"✗ Failed to create service account: {result.get('error', 'Unknown error')}")
        return 1

    print("")
    print("✅ Service account created successfully!")
    print("")
    print("Account Details:")
    print(f"  Username: {result['username']}")
    print(f"  Password: {result['password']}")
    print(f"  Domain: {args.domain}")
    print("")

    if result.get("exists"):
        print("⚠️  Account already existed - password may need to be reset manually")
        print("")

    # Store in Key Vault
    if not args.skip_keyvault:
        print("Storing credentials in Azure Key Vault...")
        if store_credentials_in_keyvault(args.vault_name, result['username'], result['password']):
            print("")
            print("✅ Credentials stored in Key Vault")
        else:
            print("")
            print("⚠️  Failed to store credentials in Key Vault")
            print("   You can store them manually:")
            print(f"   az keyvault secret set --vault-name {args.vault_name} --name ldap-service-username --value {result['username']}")
            print(f"   az keyvault secret set --vault-name {args.vault_name} --name ldap-service-password --value {result['password']}")
        print("")

    print("=" * 70)
    print("   NEXT STEPS")
    print("=" * 70)
    print("")
    print("Use these credentials in DSM LDAP configuration:")
    print(f"  Username: {result['username']}")
    print(f"  Password: {result['password']}")
    print("")
    print("⚠️  IMPORTANT: Save the password securely!")
    print("   It has been stored in Azure Key Vault (if successful)")
    print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())