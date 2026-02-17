#!/usr/bin/env python3
"""
Fidelity Investments Connection
Note: Fidelity does not have a public API for retail customers
This module provides desktop app integration guidance and account tracking

Tags: #FIDELITY #TRADITIONAL_BROKERAGE @JARVIS
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
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

logger = get_logger("FidelityConnection")


class FidelityConnection(BaseFinancialConnection):
    """
    Fidelity Investments Connection

    Note: Fidelity does not provide a public API for retail customers.
    This connection tracks account information manually or via desktop app integration.

    For automated trading, use Fidelity Active Trader Pro desktop application.
    """

    # Fidelity URLs
    TRADER_DASHBOARD_URL = "https://digital.fidelity.com/ftgw/digital/trader-dashboard"
    ACTIVE_TRADER_PRO_URL = "https://www.fidelity.com/trading/advanced-trading-tools/active-trader-pro/overview"
    LOGIN_URL = "https://digital.fidelity.com/ftgw/digital/login"

    def __init__(self, account_id: str, credentials: Dict[str, str]):
        """
        Initialize Fidelity connection

        Credentials:
            - username: Fidelity account username
            - password: Fidelity account password (for manual tracking)
            - account_number: Fidelity account number
        """
        super().__init__(account_id, credentials)
        self.username = credentials.get("username")
        self.password = credentials.get("password")
        self.account_number = credentials.get("account_number")

        logger.info("⚠️  Fidelity does not have a public API")
        logger.info("   Use Fidelity Active Trader Pro desktop app for trading")

    def connect(self) -> ConnectionResult:
        """Connect to Fidelity (manual/desktop app only)"""
        logger.info(f"🔌 Fidelity connection for {self.account_id}...")
        logger.warning("Fidelity requires manual connection via desktop app")

        # Mark as connected if credentials exist (manual tracking)
        if self.username and self.account_number:
            self.connected = True
            self.last_connection_attempt = datetime.now().isoformat()
            return ConnectionResult(
                success=True,
                message="Fidelity account tracked (manual/desktop app)",
                data={
                    "connection_type": "manual",
                    "desktop_app_required": True,
                    "api_available": False
                }
            )

        result = ConnectionResult(
            success=False,
            message="Fidelity credentials not provided",
            error="username and account_number required for tracking"
        )
        self.last_error = result.error
        return result

    def disconnect(self) -> ConnectionResult:
        """Disconnect from Fidelity"""
        logger.info(f"🔌 Disconnecting from Fidelity...")
        self.connected = False
        return ConnectionResult(
            success=True,
            message="Disconnected successfully"
        )

    def test_connection(self) -> ConnectionResult:
        """Test Fidelity connection"""
        if self.connected:
            return ConnectionResult(
                success=True,
                message="Fidelity account tracked",
                data={"connection_type": "manual"}
            )
        return ConnectionResult(
            success=False,
            message="Not connected",
            error="Fidelity requires manual connection"
        )

    def get_balance(self) -> ConnectionResult:
        """Get account balance (requires manual input or desktop app)"""
        logger.warning("Fidelity balance requires manual input or desktop app integration")

        return ConnectionResult(
            success=False,
            message="Balance retrieval not automated",
            error="Fidelity does not provide API access. Use desktop app or manual entry.",
            data={
                "suggestion": "Use Fidelity Active Trader Pro desktop app",
                "manual_entry": "Update balance manually in account registry"
            }
        )

    def get_account_info(self) -> ConnectionResult:
        """Get Fidelity account information"""
        return ConnectionResult(
            success=True,
            message="Fidelity account information",
            data={
                "account_id": self.account_id,
                "account_number": self.account_number,
                "connection_type": "manual",
                "desktop_app": "Fidelity Active Trader Pro",
                "api_available": False,
                "trading_method": "Desktop application",
                "dashboard_url": self.TRADER_DASHBOARD_URL,
                "login_url": self.LOGIN_URL
            }
        )

    def open_trader_dashboard(self) -> ConnectionResult:
        """Open Fidelity Trader Dashboard in browser"""
        try:
            import webbrowser
            webbrowser.open(self.TRADER_DASHBOARD_URL)
            logger.info(f"✅ Opened Fidelity Trader Dashboard: {self.TRADER_DASHBOARD_URL}")
            return ConnectionResult(
                success=True,
                message="Trader Dashboard opened in browser",
                data={"url": self.TRADER_DASHBOARD_URL}
            )
        except Exception as e:
            logger.error(f"❌ Failed to open dashboard: {e}")
            return ConnectionResult(
                success=False,
                message="Failed to open dashboard",
                error=str(e)
            )

    def update_balance_manual(self, balance: float, currency: str = "USD") -> ConnectionResult:
        """Manually update account balance"""
        logger.info(f"📝 Manually updating Fidelity balance: {balance} {currency}")

        return ConnectionResult(
            success=True,
            message="Balance updated manually",
            data={
                "balance": balance,
                "currency": currency,
                "updated_at": datetime.now().isoformat(),
                "source": "manual"
            }
        )
