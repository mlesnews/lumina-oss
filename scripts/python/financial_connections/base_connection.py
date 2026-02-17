#!/usr/bin/env python3
"""
Base Financial Connection
Abstract base class for all financial account connections

Tags: #FINANCIAL_CONNECTIONS #API_INTEGRATION @JARVIS
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BaseFinancialConnection")


@dataclass
class ConnectionResult:
    """Connection operation result"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class BaseFinancialConnection(ABC):
    """
    Base class for financial account connections

    All financial connections should inherit from this class
    """

    def __init__(self, account_id: str, credentials: Dict[str, str]):
        """
        Initialize connection

        Args:
            account_id: Unique account identifier
            credentials: Dictionary of credentials (api_key, api_secret, etc.)
        """
        self.account_id = account_id
        self.credentials = credentials
        self.connected = False
        self.last_connection_attempt: Optional[str] = None
        self.last_error: Optional[str] = None

    @abstractmethod
    def connect(self) -> ConnectionResult:
        """Connect to the financial service"""
        pass

    @abstractmethod
    def disconnect(self) -> ConnectionResult:
        """Disconnect from the financial service"""
        pass

    @abstractmethod
    def test_connection(self) -> ConnectionResult:
        """Test the connection"""
        pass

    @abstractmethod
    def get_balance(self) -> ConnectionResult:
        """Get account balance"""
        pass

    @abstractmethod
    def get_account_info(self) -> ConnectionResult:
        """Get account information"""
        pass

    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.connected

    def get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            "account_id": self.account_id,
            "connected": self.connected,
            "last_connection_attempt": self.last_connection_attempt,
            "last_error": self.last_error
        }
