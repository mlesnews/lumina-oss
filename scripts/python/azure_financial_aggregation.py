#!/usr/bin/env python3
"""
Azure Financial Data Aggregation
Integrates with financial data aggregators (Plaid, Finicity, MX, Akoya) via Azure services

Since Copilot Money uses these aggregators but has no public API, we integrate directly
with the aggregators using Azure infrastructure for secure, scalable data access.

Tags: #AZURE #FINANCIAL_DATA #PLAID #FINICITY #MX #AKOYA #INTEGRATION
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    UnifiedSecretsManager = None

logger = get_logger("AzureFinancialAggregation")


@dataclass
class FinancialAccount:
    """Represents a financial account from aggregator"""
    account_id: str
    name: str
    type: str
    balance: float
    currency: str
    institution: str
    aggregator: str  # 'plaid', 'finicity', 'mx', 'akoya'


@dataclass
class FinancialTransaction:
    """Represents a financial transaction"""
    transaction_id: str
    account_id: str
    date: str
    amount: float
    description: str
    category: Optional[str] = None
    merchant: Optional[str] = None


class PlaidAzureIntegration:
    """Plaid integration using Azure services"""

    def __init__(self, project_root: Path):
        """Initialize Plaid integration"""
        self.project_root = project_root
        self.logger = get_logger("PlaidAzureIntegration")
        self.base_url = "https://production.plaid.com"  # or sandbox.plaid.com for testing

        # Get credentials from Azure Key Vault
        if UnifiedSecretsManager:
            self.secrets_manager = UnifiedSecretsManager(project_root)
            self.client_id = self.secrets_manager.get_secret(
                "plaid-client-id", 
                source=SecretSource.AZURE_KEY_VAULT
            )
            self.secret = self.secrets_manager.get_secret(
                "plaid-secret", 
                source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.client_id = None
            self.secret = None

    def get_access_token(self, public_token: str) -> Optional[str]:
        """Exchange public token for access token"""
        if not self.client_id or not self.secret:
            self.logger.error("❌ Plaid credentials not found in Azure Key Vault")
            return None

        url = f"{self.base_url}/item/public_token/exchange"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "public_token": public_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
        except Exception as e:
            self.logger.error(f"❌ Error exchanging token: {e}")
            return None

    def get_accounts(self, access_token: str) -> List[FinancialAccount]:
        """Get accounts from Plaid"""
        url = f"{self.base_url}/accounts/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": access_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            accounts = []
            for acc in data.get("accounts", []):
                accounts.append(FinancialAccount(
                    account_id=acc.get("account_id"),
                    name=acc.get("name"),
                    type=acc.get("type"),
                    balance=acc.get("balances", {}).get("available", 0),
                    currency=acc.get("balances", {}).get("iso_currency_code", "USD"),
                    institution=acc.get("institution_id", ""),
                    aggregator="plaid"
                ))

            return accounts
        except Exception as e:
            self.logger.error(f"❌ Error getting accounts: {e}")
            return []

    def get_transactions(self, access_token: str, start_date: str, end_date: str) -> List[FinancialTransaction]:
        """Get transactions from Plaid"""
        url = f"{self.base_url}/transactions/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": access_token,
            "start_date": start_date,
            "end_date": end_date
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            transactions = []
            for txn in data.get("transactions", []):
                transactions.append(FinancialTransaction(
                    transaction_id=txn.get("transaction_id"),
                    account_id=txn.get("account_id"),
                    date=txn.get("date"),
                    amount=txn.get("amount"),
                    description=txn.get("name"),
                    category=txn.get("category", [None])[0] if txn.get("category") else None,
                    merchant=txn.get("merchant_name")
                ))

            return transactions
        except Exception as e:
            self.logger.error(f"❌ Error getting transactions: {e}")
            return []


class FinicityAzureIntegration:
    """Finicity (Mastercard Open Banking) integration using Azure services"""

    def __init__(self, project_root: Path):
        """Initialize Finicity integration"""
        self.project_root = project_root
        self.logger = get_logger("FinicityAzureIntegration")
        self.base_url = "https://api.finicity.com"

        # Get credentials from Azure Key Vault
        if UnifiedSecretsManager:
            self.secrets_manager = UnifiedSecretsManager(project_root)
            self.partner_id = self.secrets_manager.get_secret(
                "finicity-partner-id",
                source=SecretSource.AZURE_KEY_VAULT
            )
            self.partner_secret = self.secrets_manager.get_secret(
                "finicity-partner-secret",
                source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.partner_id = None
            self.partner_secret = None

    def get_app_token(self) -> Optional[str]:
        """Get application token for Finicity API"""
        if not self.partner_id or not self.partner_secret:
            self.logger.error("❌ Finicity credentials not found in Azure Key Vault")
            return None

        url = f"{self.base_url}/aggregation/v2/partners/authentication"
        headers = {
            "Finicity-App-Key": self.partner_secret,
            "Content-Type": "application/json"
        }
        payload = {
            "partnerId": self.partner_id,
            "partnerSecret": self.partner_secret
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("token")
        except Exception as e:
            self.logger.error(f"❌ Error getting app token: {e}")
            return None


class MXAzureIntegration:
    """MX integration using Azure services (requires IP allowlisting via NAT Gateway)"""

    def __init__(self, project_root: Path):
        """Initialize MX integration"""
        self.project_root = project_root
        self.logger = get_logger("MXAzureIntegration")
        self.base_url = "https://int-api.mx.com"

        # Get credentials from Azure Key Vault
        if UnifiedSecretsManager:
            self.secrets_manager = UnifiedSecretsManager(project_root)
            self.client_id = self.secrets_manager.get_secret(
                "mx-client-id",
                source=SecretSource.AZURE_KEY_VAULT
            )
            self.api_key = self.secrets_manager.get_secret(
                "mx-api-key",
                source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.client_id = None
            self.api_key = None

    def _get_auth_header(self) -> Optional[str]:
        """Get Basic auth header for MX"""
        if not self.client_id or not self.api_key:
            return None

        import base64
        credentials = f"{self.client_id}:{self.api_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def get_users(self) -> List[Dict[str, Any]]:
        """Get users from MX"""
        url = f"{self.base_url}/users"
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("users", [])
        except Exception as e:
            self.logger.error(f"❌ Error getting users: {e}")
            return []


class AkoyaAzureIntegration:
    """Akoya integration using Azure services (OAuth 2.0 + OIDC)"""

    def __init__(self, project_root: Path):
        """Initialize Akoya integration"""
        self.project_root = project_root
        self.logger = get_logger("AkoyaAzureIntegration")
        self.base_url = "https://api.akoya.com"

        # Get credentials from Azure Key Vault
        if UnifiedSecretsManager:
            self.secrets_manager = UnifiedSecretsManager(project_root)
            self.client_id = self.secrets_manager.get_secret(
                "akoya-client-id",
                source=SecretSource.AZURE_KEY_VAULT
            )
            self.client_secret = self.secrets_manager.get_secret(
                "akoya-client-secret",
                source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.client_id = None
            self.client_secret = None


class AzureFinancialAggregation:
    """
    Main Azure-based financial aggregation service

    Integrates with Plaid, Finicity, MX, and Akoya using Azure infrastructure
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Azure financial aggregation"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "azure_financial"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize aggregator integrations
        self.plaid = PlaidAzureIntegration(self.project_root)
        self.finicity = FinicityAzureIntegration(self.project_root)
        self.mx = MXAzureIntegration(self.project_root)
        self.akoya = AkoyaAzureIntegration(self.project_root)

        logger.info("✅ Azure Financial Aggregation initialized")
        logger.info("   Aggregators: Plaid, Finicity, MX, Akoya")
        logger.info("   Azure Services: Key Vault, Functions, API Management")

    def get_all_accounts(self, aggregator: Optional[str] = None) -> List[FinancialAccount]:
        """Get accounts from all or specific aggregator"""
        all_accounts = []

        aggregators = {
            "plaid": self.plaid,
            "finicity": self.finicity,
            "mx": self.mx,
            "akoya": self.akoya
        }

        if aggregator:
            if aggregator.lower() in aggregators:
                # Get accounts from specific aggregator
                # This would require access tokens from user authorization
                logger.info(f"📋 Getting accounts from {aggregator}")
                # Implementation would depend on stored access tokens
        else:
            # Get from all aggregators
            logger.info("📋 Getting accounts from all aggregators")
            # Implementation would aggregate from all sources

        return all_accounts

    def setup_azure_infrastructure(self) -> Dict[str, Any]:
        """Generate Azure infrastructure setup guide"""
        setup_guide = {
            "azure_services": {
                "key_vault": {
                    "purpose": "Store aggregator credentials (client IDs, secrets, API keys)",
                    "secrets_to_store": [
                        "plaid-client-id",
                        "plaid-secret",
                        "finicity-partner-id",
                        "finicity-partner-secret",
                        "mx-client-id",
                        "mx-api-key",
                        "akoya-client-id",
                        "akoya-client-secret"
                    ],
                    "best_practices": [
                        "Enable soft delete",
                        "Enable purge protection",
                        "Use managed identities where possible",
                        "Rotate secrets regularly"
                    ]
                },
                "azure_functions": {
                    "purpose": "Handle webhooks and API calls",
                    "use_cases": [
                        "Plaid webhook receiver (verify JWT signatures)",
                        "Finicity webhook handler",
                        "MX webhook handler",
                        "Akoya webhook handler",
                        "Scheduled account sync"
                    ],
                    "configuration": {
                        "runtime": "Python 3.11+",
                        "authentication": "Function keys or managed identity",
                        "retry_policy": "Exponential backoff",
                        "idempotency": "Required for webhooks"
                    }
                },
                "api_management": {
                    "purpose": "OAuth delegation and API proxy",
                    "features": [
                        "OAuth 2.0 between clients and aggregators",
                        "Credential management",
                        "Rate limiting",
                        "Request/response transformation"
                    ]
                },
                "nat_gateway": {
                    "purpose": "Fixed egress IP for MX (IP allowlisting required)",
                    "requirements": [
                        "Functions Premium or Dedicated plan",
                        "VNet integration",
                        "NAT Gateway with static IP",
                        "Register IP in MX dashboard"
                    ]
                },
                "logic_apps": {
                    "purpose": "Workflow automation",
                    "use_cases": [
                        "Scheduled account synchronization",
                        "Data transformation pipelines",
                        "Alert workflows"
                    ]
                }
            },
            "aggregator_specific": {
                "plaid": {
                    "webhook_verification": "JWT in Plaid-Verification header",
                    "webhook_endpoint": "Azure Function HTTP trigger",
                    "redirect_uris": "Azure App Service or Static Web Apps",
                    "testing": "Use Plaid Sandbox with /sandbox/public_token/create"
                },
                "finicity": {
                    "oauth_flow": "Mastercard Data Connect widget",
                    "backend_api": "Via API Management",
                    "testing": "Use public OpenAPI repo test drive"
                },
                "mx": {
                    "ip_allowlisting": "Required - use NAT Gateway",
                    "authentication": "Basic auth (client_id:api_key)",
                    "rate_limits": "GET 2000 rps, POST/PUT 750 rps",
                    "testing": "Use MXCU OAuth test institutions"
                },
                "akoya": {
                    "oauth_oidc": "OAuth 2.0 + OIDC flow",
                    "token_model": "ID token + refresh token",
                    "redirect_uri": "Must be registered in Data Recipient Hub",
                    "testing": "Use Sandbox Hub"
                }
            },
            "implementation_steps": [
                "1. Store aggregator credentials in Azure Key Vault",
                "2. Create Azure Functions for webhook handling",
                "3. Set up API Management for OAuth/proxy (if needed)",
                "4. Configure NAT Gateway for MX (if using MX)",
                "5. Register redirect URIs with aggregators",
                "6. Implement OAuth flows for user authorization",
                "7. Store access tokens securely (Key Vault or encrypted storage)",
                "8. Set up scheduled sync jobs (Logic Apps or Functions)",
                "9. Implement webhook verification (especially for Plaid)",
                "10. Test with sandbox environments"
            ]
        }

        return setup_guide

    def save_setup_guide(self) -> Path:
        try:
            """Save Azure infrastructure setup guide"""
            guide = self.setup_azure_infrastructure()
            output_file = self.data_dir / "azure_financial_setup_guide.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(guide, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Setup guide saved to: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in save_setup_guide: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Azure Financial Aggregation")
    parser.add_argument("--setup-guide", action="store_true", help="Generate Azure setup guide")
    parser.add_argument("--list-aggregators", action="store_true", help="List supported aggregators")

    args = parser.parse_args()

    aggregation = AzureFinancialAggregation()

    if args.setup_guide:
        guide_file = aggregation.save_setup_guide()
        print(f"\n✅ Azure setup guide generated: {guide_file}")
        print("\n📋 Quick Summary:")
        print("  • Azure Key Vault: Store aggregator credentials")
        print("  • Azure Functions: Handle webhooks and API calls")
        print("  • API Management: OAuth delegation and proxy")
        print("  • NAT Gateway: Fixed IP for MX (if using MX)")
        print("  • Logic Apps: Workflow automation")

    elif args.list_aggregators:
        print("\n📊 Supported Financial Data Aggregators:")
        print("  • Plaid - Primary aggregator (most banks)")
        print("  • Finicity - Mastercard Open Banking")
        print("  • MX - Account aggregation (requires IP allowlisting)")
        print("  • Akoya - OAuth 2.0 + OIDC based")
        print("\n💡 These are the same aggregators Copilot Money uses!")
        print("   By integrating directly, you get the same data without Copilot's limitations.")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()