#!/usr/bin/env python3
"""
Plaid Financial Connection
Connects to Plaid API via Azure Key Vault credentials

Tags: #PLAID #FINANCIAL_CONNECTION #AZURE
"""

import sys
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from financial_connections.base_connection import BaseFinancialConnection, ConnectionResult
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    BaseFinancialConnection = None

logger = get_logger("PlaidConnection")


class PlaidConnection(BaseFinancialConnection):
    """Plaid financial connection via Azure"""

    def __init__(self, account_id: str):
        """Initialize Plaid connection"""
        if not BaseFinancialConnection:
            raise ImportError("BaseFinancialConnection not available")

        super().__init__(account_id)
        self.project_root = Path(__file__).parent.parent.parent.parent

        # Get credentials from Azure Key Vault
        self.secrets_manager = UnifiedSecretsManager(self.project_root)
        self.client_id = self.secrets_manager.get_secret(
            "plaid-client-id",
            source=SecretSource.AZURE_KEY_VAULT
        )
        self.secret = self.secrets_manager.get_secret(
            "plaid-secret",
            source=SecretSource.AZURE_KEY_VAULT
        )
        self.environment = self.secrets_manager.get_secret(
            "plaid-environment",
            source=SecretSource.AZURE_KEY_VAULT
        ) or "sandbox"

        # Set base URL based on environment
        if self.environment == "production":
            self.base_url = "https://production.plaid.com"
        else:
            self.base_url = "https://sandbox.plaid.com"

        self.access_token = None
        logger.info(f"✅ Plaid connection initialized (environment: {self.environment})")

    def connect(self, **kwargs) -> ConnectionResult:
        """Connect to Plaid using access token"""
        access_token = kwargs.get("access_token")

        if not access_token:
            return ConnectionResult(
                success=False,
                message="Access token required. Use exchange_public_token() first."
            )

        self.access_token = access_token

        # Test connection
        try:
            result = self.test_connection()
            if result.success:
                return ConnectionResult(
                    success=True,
                    message="Connected to Plaid successfully"
                )
            return result
        except Exception as e:
            return ConnectionResult(
                success=False,
                message=f"Connection failed: {e}"
            )

    def exchange_public_token(self, public_token: str) -> Optional[str]:
        """Exchange public token for access token"""
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
            self.access_token = data.get("access_token")
            logger.info("✅ Exchanged public token for access token")
            return self.access_token
        except Exception as e:
            logger.error(f"❌ Error exchanging token: {e}")
            return None

    def disconnect(self) -> ConnectionResult:
        """Disconnect from Plaid"""
        self.access_token = None
        return ConnectionResult(
            success=True,
            message="Disconnected from Plaid"
        )

    def test_connection(self) -> ConnectionResult:
        """Test Plaid connection"""
        if not self.access_token:
            return ConnectionResult(
                success=False,
                message="Not connected. No access token."
            )

        url = f"{self.base_url}/accounts/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return ConnectionResult(
                success=True,
                message="Plaid connection test successful"
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                message=f"Connection test failed: {e}"
            )

    def get_balance(self) -> Optional[float]:
        """Get total balance from all accounts"""
        if not self.access_token:
            return None

        url = f"{self.base_url}/accounts/balance/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            total = 0.0
            for account in data.get("accounts", []):
                balance = account.get("balances", {}).get("available", 0)
                if isinstance(balance, (int, float)):
                    total += balance

            return total
        except Exception as e:
            logger.error(f"❌ Error getting balance: {e}")
            return None

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.access_token:
            return {}

        url = f"{self.base_url}/accounts/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            return {
                "accounts": data.get("accounts", []),
                "item": data.get("item", {}),
                "request_id": data.get("request_id")
            }
        except Exception as e:
            logger.error(f"❌ Error getting account info: {e}")
            return {}

    def get_transactions(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get transactions"""
        if not self.access_token:
            return []

        # Default to last 30 days
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        url = f"{self.base_url}/transactions/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token,
            "start_date": start_date,
            "end_date": end_date
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("transactions", [])
        except Exception as e:
            logger.error(f"❌ Error getting transactions: {e}")
            return []
