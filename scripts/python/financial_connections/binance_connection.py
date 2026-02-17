#!/usr/bin/env python3
"""
Binance.US API Connection
Connects to Binance.US cryptocurrency exchange

API Documentation: https://binance-docs.github.io/apidocs/spot/en/

Tags: #BINANCE #CRYPTO_EXCHANGE @JARVIS
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent.parent.parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from financial_connections.base_connection import BaseFinancialConnection, ConnectionResult
except ImportError:
    from .base_connection import BaseFinancialConnection, ConnectionResult

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BinanceConnection")


class BinanceConnection(BaseFinancialConnection):
    """
    Binance.US API Connection

    Connects to Binance.US cryptocurrency exchange
    """

    API_BASE_URL = "https://api.binance.us/api/v3"

    def __init__(self, account_id: str, credentials: Dict[str, str]):
        """
        Initialize Binance.US connection

        Required credentials:
            - api_key: Binance.US API key
            - api_secret: Binance.US API secret
        """
        super().__init__(account_id, credentials)
        self.api_key = credentials.get("api_key")
        self.api_secret = credentials.get("api_secret")
        self.base_url = self.API_BASE_URL

        if not self.api_key or not self.api_secret:
            logger.warning("Binance.US API credentials not provided")

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     signed: bool = False) -> ConnectionResult:
        """Make authenticated API request"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {}

            if signed:
                import hmac
                import hashlib
                import time

                if params is None:
                    params = {}

                params["timestamp"] = int(time.time() * 1000)
                query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])

                signature = hmac.new(
                    self.api_secret.encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()

                params["signature"] = signature
                headers["X-MBX-APIKEY"] = self.api_key

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            return ConnectionResult(
                success=True,
                message="Request successful",
                data=data
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            return ConnectionResult(
                success=False,
                message="Request failed",
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return ConnectionResult(
                success=False,
                message="Unexpected error",
                error=error_msg
            )

    def connect(self) -> ConnectionResult:
        """Connect to Binance.US API"""
        logger.info(f"🔌 Connecting to Binance.US API for {self.account_id}...")

        if not self.api_key or not self.api_secret:
            result = ConnectionResult(
                success=False,
                message="Missing API credentials",
                error="api_key and api_secret required"
            )
            self.last_error = result.error
            return result

        # Test connection by getting account info
        result = self.get_account_info()

        if result.success:
            self.connected = True
            self.last_connection_attempt = datetime.now().isoformat()
            logger.info(f"✅ Connected to Binance.US API")
        else:
            self.connected = False
            self.last_error = result.error
            logger.error(f"❌ Failed to connect: {result.error}")

        return result

    def disconnect(self) -> ConnectionResult:
        """Disconnect from Binance.US API"""
        logger.info(f"🔌 Disconnecting from Binance.US API...")
        self.connected = False
        return ConnectionResult(
            success=True,
            message="Disconnected successfully"
        )

    def test_connection(self) -> ConnectionResult:
        """Test Binance.US API connection"""
        # Test with a simple public endpoint
        result = self._make_request("GET", "/ping")
        if result.success:
            return self.get_account_info()
        return result

    def get_balance(self) -> ConnectionResult:
        """Get account balance from Binance.US"""
        logger.debug("💰 Getting Binance.US account balance...")

        result = self._make_request("GET", "/account", signed=True)

        if result.success and result.data:
            balances = result.data.get("balances", [])
            # Filter out zero balances
            non_zero_balances = [
                b for b in balances
                if float(b.get("free", 0)) > 0 or float(b.get("locked", 0)) > 0
            ]

            total_usd_value = 0.0  # Would need price data to calculate

            return ConnectionResult(
                success=True,
                message="Balance retrieved",
                data={
                    "balances": non_zero_balances,
                    "total_assets": len(non_zero_balances)
                }
            )

        return result

    def get_account_info(self) -> ConnectionResult:
        """Get Binance.US account information"""
        logger.debug("📊 Getting Binance.US account info...")
        return self._make_request("GET", "/account", signed=True)

    def get_ticker_price(self, symbol: str) -> ConnectionResult:
        """Get current price for a trading pair"""
        logger.debug(f"💹 Getting price for {symbol}...")
        params = {"symbol": symbol}
        return self._make_request("GET", "/ticker/price", params=params)

    def get_open_orders(self, symbol: Optional[str] = None) -> ConnectionResult:
        """Get open orders"""
        logger.debug("📋 Getting open orders...")
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._make_request("GET", "/openOrders", params=params, signed=True)
