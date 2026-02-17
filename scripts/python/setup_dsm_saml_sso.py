#!/usr/bin/env python3
"""
Setup SAML SSO for DSM with Azure AD
Automates Azure AD App Registration and provides DSM configuration
#JARVIS #SAML #SSO #AZURE-AD #DSM #FREE
"""

import sys
import subprocess
import platform
import json
import uuid
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_tenant_info():
    """Get Azure AD tenant information"""
    is_windows = platform.system() == "Windows"

    try:
        result = subprocess.run(
            ["az", "account", "show", "--query", "{tenantId:tenantId, tenantDefaultDomain:tenantDefaultDomain, subscriptionId:id}", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        logger.error(f"Failed to get tenant info: {e}")

    return None


def create_azure_ad_app(dsm_url: str, app_name: str = "Synology DSM SSO"):
    """Create Azure AD App Registration for SAML SSO"""
    is_windows = platform.system() == "Windows"
    tenant_info = get_tenant_info()

    if not tenant_info:
        print("❌ Could not get tenant information")
        return None

    tenant_id = tenant_info.get("tenantId")
    tenant_domain = tenant_info.get("tenantDefaultDomain", "")

    print("=" * 70)
    print("   CREATING AZURE AD APP REGISTRATION")
    print("=" * 70)
    print("")
    print(f"App Name: {app_name}")
    print(f"DSM URL: {dsm_url}")
    print("")

    # Check if URL is IP address (Azure AD requires domain)
    dsm_host = dsm_url.replace('https://', '').replace('http://', '').split(':')[0]
    is_ip = dsm_host.replace('.', '').isdigit()

    if is_ip:
        print("⚠️  DSM URL is an IP address")
        print("   Azure AD requires a domain name for app registration")
        print("   You'll need to create the app manually in Azure Portal")
        print("   Or set up a domain name for your DSM")
        print("")
        return None

    # Create app registration (without identifier-uris if IP)
    print("Creating app registration...")
    try:
        create_cmd = [
            "az", "ad", "app", "create",
            "--display-name", app_name
        ]

        result = subprocess.run(
            create_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            shell=is_windows
        )

        if result.returncode == 0:
            app_data = json.loads(result.stdout)
            app_id = app_data.get("appId")
            object_id = app_data.get("id")

            print(f"✅ App created successfully")
            print(f"   App ID: {app_id}")
            print(f"   Object ID: {object_id}")
            print("")
            print("⚠️  Note: You'll need to configure SAML manually in Azure Portal")
            print("   (App registration created, but SAML must be configured via Enterprise Applications)")
            print("")

            return {
                "appId": app_id,
                "objectId": object_id,
                "displayName": app_name,
                "dsmUrl": dsm_url
            }
        else:
            print(f"❌ Failed to create app: {result.stderr}")
            print("")
            print("You can create it manually in Azure Portal:")
            print("  Azure Portal → App registrations → New registration")
            print("")
            return None

    except Exception as e:
        print(f"❌ Error creating app: {e}")
        print("")
        print("You can create it manually in Azure Portal:")
        print("  Azure Portal → App registrations → New registration")
        print("")
        return None


def print_dsm_configuration_guide(app_info: dict, tenant_info: dict):
    """Print DSM SSO Server configuration guide"""
    dsm_url = app_info.get("dsmUrl", "")
    app_id = app_info.get("appId", "")
    tenant_domain = tenant_info.get("tenantDefaultDomain", "")

    print("=" * 70)
    print("   DSM SSO SERVER CONFIGURATION")
    print("=" * 70)
    print("")
    print("Step 1: Install SSO Server Package (if not installed)")
    print("")
    print("  1. DSM → Package Center")
    print("  2. Search: 'SSO Server'")
    print("  3. Install: Synology SSO Server")
    print("  4. Open: SSO Server application")
    print("")
    print("Step 2: Configure SSO Server as Identity Provider (IdP)")
    print("")
    print("  1. SSO Server → General Settings")
    print(f"     - Server URL: {dsm_url}")
    print("       (Must be HTTPS with valid certificate)")
    print("")
    print("  2. SSO Server → Service → SAML")
    print("     - Enable SAML Server: ✅ CHECKED")
    print("")
    print("  3. Copy the following (you'll need these):")
    print("     - IdP Single Sign-On URL")
    print("     - IdP Entity ID")
    print("     - Certificate (download)")
    print("")
    print("Step 3: Configure Azure AD Enterprise Application")
    print("")
    print("  1. Azure Portal → Azure Active Directory → Enterprise Applications")
    print("")
    print("  2. New Application:")
    print("     - Click 'New application'")
    print("     - Click 'Create your own application'")
    print("     - Name: 'Synology DSM SSO'")
    print("     - Type: 'Integrate any other application'")
    print("     - Click 'Create'")
    print("")
    print("  3. Configure SAML:")
    print("     - Click 'Set up single sign on'")
    print("     - Select 'SAML'")
    print("")
    print("  4. Basic SAML Configuration:")
    print("     - Identifier (Entity ID): [IdP Entity ID from SSO Server]")
    print(f"     - Reply URL: {dsm_url}/sso/acs")
    print(f"     - Sign on URL: {dsm_url}")
    print("")
    print("  5. User Attributes & Claims:")
    print("     - Unique User Identifier: user.userprincipalname")
    print("     - Email: user.mail")
    print("     - Display Name: user.displayname")
    print("")
    print("  6. SAML Signing Certificate:")
    print("     - Upload certificate from SSO Server")
    print("     - Or use Azure AD certificate")
    print("")
    print("  7. Save Configuration")
    print("")
    print("Step 4: Configure DSM as Service Provider (SP)")
    print("")
    print("  1. DSM → Control Panel → Domain/LDAP → SSO Client")
    print("")
    print("  2. Enable SAML SSO: ✅ CHECKED")
    print("")
    print("  3. IdP Information (from Azure AD):")
    print("     - IdP Entity ID: [From Azure AD SAML config]")
    print("     - IdP Single Sign-On URL: [From Azure AD SAML config]")
    print("     - IdP Certificate: [Upload from Azure AD]")
    print("")
    print("  4. SP Information:")
    print("     - SP Entity ID: [From SSO Server]")
    print("     - SP Assertion Consumer Service URL: [From SSO Server]")
    print("")
    print("  5. User Attribute Mapping:")
    print("     - User ID: userPrincipalName or mail")
    print("     - Email: mail")
    print("     - Display Name: displayName")
    print("")
    print("  6. Save Configuration")
    print("")
    print("Step 5: Assign Users/Groups in Azure AD")
    print("")
    print("  1. Azure Portal → Enterprise Applications → Your DSM app")
    print("  2. Users and groups → Add user/group")
    print("  3. Select users or groups")
    print("  4. Click 'Assign'")
    print("")
    print("=" * 70)
    print("   QUICK REFERENCE")
    print("=" * 70)
    print("")
    print("Azure AD App Registration:")
    print(f"  App ID: {app_id}")
    print(f"  Tenant: {tenant_domain}")
    print("")
    print("DSM Configuration:")
    print(f"  DSM URL: {dsm_url}")
    print(f"  Reply URL: {dsm_url}/sso/acs")
    print(f"  Sign on URL: {dsm_url}")
    print("")
    print("=" * 70)
    print("")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Setup SAML SSO for DSM with Azure AD")
    parser.add_argument("--dsm-url", required=True, help="DSM URL (e.g., https://nas.yourdomain.com:5001)")
    parser.add_argument("--app-name", default="Synology DSM SSO", help="Azure AD App name")
    parser.add_argument("--create-app", action="store_true", help="Create Azure AD app registration")
    args = parser.parse_args()

    print("")
    print("=" * 70)
    print("   DSM SAML SSO SETUP (FREE)")
    print("=" * 70)
    print("")

    # Get tenant info
    tenant_info = get_tenant_info()
    if not tenant_info:
        print("❌ Could not get tenant information")
        print("   Make sure you're logged in: az login")
        return 1

    print(f"✅ Azure AD Tenant: {tenant_info.get('tenantDefaultDomain')}")
    print("")

    # Create app if requested
    app_info = None
    if args.create_app:
        app_info = create_azure_ad_app(args.dsm_url, args.app_name)
        if not app_info:
            print("⚠️  App creation failed or skipped (IP address detected)")
            print("   You'll need to create it manually in Azure Portal")
            print("")
            app_info = {
                "appId": "[Create in Azure Portal]",
                "dsmUrl": args.dsm_url
            }
    else:
        print("ℹ️  Skipping app creation (use --create-app to create automatically)")
        print("")
        app_info = {
            "appId": "[Will be created in Azure Portal]",
            "dsmUrl": args.dsm_url
        }

    # Print configuration guide
    print_dsm_configuration_guide(app_info, tenant_info)

    print("=" * 70)
    print("   NEXT STEPS")
    print("=" * 70)
    print("")
    print("1. Install SSO Server package in DSM (if not installed)")
    print("2. Configure SSO Server as IdP")
    print("3. Create Enterprise Application in Azure AD")
    print("4. Configure SAML in both Azure AD and DSM")
    print("5. Assign users/groups in Azure AD")
    print("6. Test SSO")
    print("")
    print("Full guide: docs/system/DSM_SAML_SSO_SETUP_GUIDE.md")
    print("")
    print("=" * 70)
    print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())