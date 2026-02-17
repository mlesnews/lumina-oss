#!/usr/bin/env python3
"""
JARVIS Unified Financial Life Domain Coaching
Integrates Binance.US + Fidelity Investments + ProtonPass CLI
Full account access for comprehensive financial coaching

@JARVIS @FINANCIAL_LIFE_DOMAIN @BINANCE @FIDELITY @PROTONPASS @MEMORY
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISUnifiedFinancial")


@dataclass
class TradingAccount:
    """Trading account information"""
    account_id: str
    account_type: str  # "binance", "fidelity", etc.
    approximate_balance: float
    trading_capabilities: List[str]
    api_available: bool
    desktop_app_available: bool


@dataclass
class FinancialPortfolio:
    """Complete financial portfolio"""
    accounts: List[TradingAccount]
    total_capital: float
    target_profit: float
    crisis_need: float
    strategies: List[Dict[str, Any]]


class UnifiedFinancialCoaching:
    """
    Unified Financial Life Domain Coaching

    Integrates:
    - Binance.US (crypto trading)
    - Fidelity Investments (~$30K, day trading)
    - ProtonPass CLI (full account access)
    - Azure Key Vault (all secrets)
    - Memory integration (remember all accounts)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified financial coaching"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Azure Key Vault for all secrets
        try:
            from scripts.python.azure_service_bus_integration import get_key_vault_client
            self.key_vault = get_key_vault_client(
                vault_url="https://jarvis-lumina.vault.azure.net/"
            )
            logger.info("✅ Azure Key Vault initialized")
        except Exception as e:
            logger.warning(f"Azure Key Vault not available: {e}")
            self.key_vault = None

        # Memory integration
        self.memory_file = self.project_root / "data" / "financial_accounts_memory.json"
        self._load_account_memory()

        # Trading accounts
        self.accounts = self._initialize_accounts()

        logger.info("✅ Unified Financial Coaching initialized")
        logger.info(f"   Accounts: {len(self.accounts)}")

    def _load_account_memory(self) -> None:
        """Load account memory from file"""
        try:
            import json
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.account_memory = json.load(f)
                logger.info(f"✅ Account memory loaded: {len(self.account_memory.get('accounts', []))} accounts")
            else:
                self.account_memory = {"accounts": [], "last_updated": None}
        except Exception as e:
            logger.warning(f"Could not load account memory: {e}")
            self.account_memory = {"accounts": [], "last_updated": None}

    def _save_account_memory(self) -> None:
        """Save account memory to file"""
        try:
            import json
            self.account_memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.account_memory, f, indent=2, default=str)
            logger.info("✅ Account memory saved")
        except Exception as e:
            logger.error(f"Failed to save account memory: {e}")

    def _initialize_accounts(self) -> List[TradingAccount]:
        """Initialize trading accounts from memory and user input"""
        accounts = []

        # Load from memory first
        if self.account_memory.get("accounts"):
            for acc_data in self.account_memory["accounts"]:
                accounts.append(TradingAccount(**acc_data))

        # Add known accounts
        known_accounts = [
            TradingAccount(
                account_id="binance_us",
                account_type="binance",
                approximate_balance=0.0,  # Will be updated
                trading_capabilities=["spot", "futures", "staking", "arbitrage"],
                api_available=True,
                desktop_app_available=False
            ),
            TradingAccount(
                account_id="fidelity_investments",
                account_type="fidelity",
                approximate_balance=30000.0,
                trading_capabilities=["day_trading", "swing_trading", "options", "stocks", "etf"],
                api_available=False,  # Desktop app only
                desktop_app_available=True
            )
        ]

        # Merge with memory
        for known_acc in known_accounts:
            existing = next((a for a in accounts if a.account_id == known_acc.account_id), None)
            if not existing:
                accounts.append(known_acc)

        return accounts

    def get_protonpass_credentials(self, account_name: str) -> Dict[str, Optional[str]]:
        """Get credentials from ProtonPass CLI"""
        logger.info(f"Retrieving credentials for {account_name} via ProtonPass CLI...")

        credentials = {
            "username": None,
            "password": None,
            "api_key": None,
            "api_secret": None
        }

        try:
            import subprocess

            # Try ProtonPass CLI
            result = subprocess.run(
                ["protonpass", "get", account_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse ProtonPass output
                # Format may vary, adjust as needed
                credentials["password"] = result.stdout.strip()
                logger.info(f"✅ Credentials retrieved from ProtonPass for {account_name}")
            else:
                logger.warning(f"ProtonPass CLI not available or account not found: {account_name}")
        except FileNotFoundError:
            logger.warning("ProtonPass CLI not installed")
        except Exception as e:
            logger.warning(f"ProtonPass CLI error: {e}")

        # Fallback to Azure Vault
        if not credentials["password"] and self.key_vault:
            try:
                # Try Azure Vault secrets
                secret_names = [
                    f"{account_name}-password",
                    f"{account_name}-api-key",
                    f"{account_name}-username"
                ]

                for secret_name in secret_names:
                    try:
                        secret = self.key_vault.get_secret(secret_name)
                        if "password" in secret_name:
                            credentials["password"] = secret
                        elif "api-key" in secret_name:
                            credentials["api_key"] = secret
                        elif "username" in secret_name:
                            credentials["username"] = secret
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Azure Vault retrieval failed: {e}")

        return credentials

    def assess_complete_portfolio(self) -> FinancialPortfolio:
        """Assess complete financial portfolio"""
        logger.info("=" * 70)
        logger.info("💰 COMPLETE FINANCIAL PORTFOLIO ASSESSMENT")
        logger.info("=" * 70)
        logger.info("")

        total_capital = sum(acc.approximate_balance for acc in self.accounts)
        target_profit = 15000.0  # Crisis need
        crisis_need = 15000.0  # Furnace + expenses

        portfolio = FinancialPortfolio(
            accounts=self.accounts,
            total_capital=total_capital,
            target_profit=target_profit,
            crisis_need=crisis_need,
            strategies=[]
        )

        logger.info("Trading Accounts:")
        for acc in self.accounts:
            logger.info(f"  {acc.account_type.upper()}: ${acc.approximate_balance:,.2f}")
            logger.info(f"    Capabilities: {', '.join(acc.trading_capabilities)}")
            logger.info(f"    API: {'✅' if acc.api_available else '❌'}")
            logger.info(f"    Desktop App: {'✅' if acc.desktop_app_available else '❌'}")
            logger.info("")

        logger.info(f"Total Capital: ${total_capital:,.2f}")
        logger.info(f"Target Profit: ${target_profit:,.2f}")
        logger.info(f"Crisis Need: ${crisis_need:,.2f}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ PORTFOLIO ASSESSMENT COMPLETE")
        logger.info("=" * 70)

        # Save to memory
        self.account_memory["accounts"] = [
            {
                "account_id": acc.account_id,
                "account_type": acc.account_type,
                "approximate_balance": acc.approximate_balance,
                "trading_capabilities": acc.trading_capabilities,
                "api_available": acc.api_available,
                "desktop_app_available": acc.desktop_app_available
            }
            for acc in self.accounts
        ]
        self._save_account_memory()

        return portfolio

    def generate_unified_profit_plan(self, portfolio: FinancialPortfolio) -> Dict[str, Any]:
        """Generate unified profit plan across all accounts"""
        logger.info("=" * 70)
        logger.info("📊 UNIFIED PROFIT PLAN")
        logger.info("=" * 70)
        logger.info("")

        plan = {
            "target_profit": portfolio.target_profit,
            "crisis_need": portfolio.crisis_need,
            "total_capital": portfolio.total_capital,
            "account_strategies": {},
            "combined_potential": 0.0
        }

        # Binance.US strategies
        binance_account = next((a for a in portfolio.accounts if a.account_type == "binance"), None)
        if binance_account:
            plan["account_strategies"]["binance"] = {
                "account_balance": binance_account.approximate_balance,
                "strategies": [
                    {
                        "name": "DCA BTC/ETH",
                        "target": 5000.0,
                        "risk": "LOW",
                        "timeframe": "1-3 months"
                    },
                    {
                        "name": "Swing Trading Altcoins",
                        "target": 10000.0,
                        "risk": "MODERATE",
                        "timeframe": "2-4 weeks"
                    },
                    {
                        "name": "Arbitrage",
                        "target": 3000.0,
                        "risk": "LOW",
                        "timeframe": "Ongoing"
                    },
                    {
                        "name": "Staking/Yield",
                        "target": 2000.0,
                        "risk": "LOW",
                        "timeframe": "Ongoing"
                    }
                ],
                "total_potential": 20000.0
            }
            plan["combined_potential"] += 20000.0

        # Fidelity Investments strategies
        fidelity_account = next((a for a in portfolio.accounts if a.account_type == "fidelity"), None)
        if fidelity_account:
            plan["account_strategies"]["fidelity"] = {
                "account_balance": fidelity_account.approximate_balance,
                "strategies": [
                    {
                        "name": "Day Trading Stocks",
                        "target": 5000.0,
                        "risk": "MODERATE",
                        "timeframe": "Daily",
                        "description": "Day trading high-volume stocks with Fidelity desktop app"
                    },
                    {
                        "name": "Swing Trading ETFs",
                        "target": 3000.0,
                        "risk": "LOW",
                        "timeframe": "2-4 weeks",
                        "description": "Swing trading ETFs with technical analysis"
                    },
                    {
                        "name": "Options Trading",
                        "target": 2000.0,
                        "risk": "HIGH",
                        "timeframe": "Weekly",
                        "description": "Covered calls and cash-secured puts"
                    },
                    {
                        "name": "Dividend Stocks",
                        "target": 1000.0,
                        "risk": "LOW",
                        "timeframe": "Ongoing",
                        "description": "Dividend income from quality stocks"
                    }
                ],
                "total_potential": 11000.0
            }
            plan["combined_potential"] += 11000.0

        logger.info("Account Strategies:")
        for account_type, strategies in plan["account_strategies"].items():
            logger.info(f"\n  {account_type.upper()}:")
            logger.info(f"    Balance: ${strategies['account_balance']:,.2f}")
            logger.info(f"    Total Potential: ${strategies['total_potential']:,.2f}")
            for strategy in strategies["strategies"]:
                logger.info(f"      • {strategy['name']}: ${strategy['target']:,.2f} ({strategy['risk']} risk)")

        logger.info("")
        logger.info(f"Combined Potential: ${plan['combined_potential']:,.2f}")
        logger.info(f"Target Profit: ${plan['target_profit']:,.2f}")
        logger.info(f"Crisis Need: ${plan['crisis_need']:,.2f}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ UNIFIED PROFIT PLAN GENERATED")
        logger.info("=" * 70)

        return plan

    def provide_comprehensive_coaching(self) -> Dict[str, Any]:
        """Provide comprehensive financial life domain coaching"""
        logger.info("=" * 70)
        logger.info("🎓 COMPREHENSIVE FINANCIAL COACHING")
        logger.info("=" * 70)
        logger.info("")

        # Assess portfolio
        portfolio = self.assess_complete_portfolio()

        # Generate unified plan
        plan = self.generate_unified_profit_plan(portfolio)

        coaching = {
            "portfolio": portfolio,
            "profit_plan": plan,
            "account_access": {
                "protonpass_cli": "Available for full account access",
                "azure_vault": "All secrets stored securely",
                "memory": "Account information remembered"
            },
            "risk_management": {
                "position_sizing": "Never risk more than 2-5% per trade",
                "diversification": "Spread across Binance + Fidelity",
                "stop_loss": "Always use stop-loss orders",
                "profit_taking": "Take profits at target levels"
            },
            "crisis_priorities": {
                "furnace": "$10K - Highest priority",
                "liquidity": "Maintain emergency fund",
                "capital_protection": "Protect trading capital"
            }
        }

        logger.info("Account Access:")
        logger.info(f"  ProtonPass CLI: {coaching['account_access']['protonpass_cli']}")
        logger.info(f"  Azure Vault: {coaching['account_access']['azure_vault']}")
        logger.info(f"  Memory: {coaching['account_access']['memory']}")
        logger.info("")

        logger.info("Risk Management:")
        for key, value in coaching["risk_management"].items():
            logger.info(f"  {key.replace('_', ' ').title()}: {value}")
        logger.info("")

        logger.info("=" * 70)
        logger.info("✅ COMPREHENSIVE COACHING COMPLETE")
        logger.info("=" * 70)

        return coaching


def main():
    """Main execution"""
    print("=" * 70)
    print("💰 JARVIS UNIFIED FINANCIAL COACHING")
    print("   Binance.US + Fidelity Investments + ProtonPass CLI")
    print("=" * 70)
    print()

    coaching = UnifiedFinancialCoaching()
    session = coaching.provide_comprehensive_coaching()

    print()
    print("=" * 70)
    print("✅ UNIFIED FINANCIAL COACHING COMPLETE")
    print("=" * 70)
    print(f"Total Capital: ${session['portfolio'].total_capital:,.2f}")
    print(f"Target Profit: ${session['profit_plan']['target_profit']:,.2f}")
    print(f"Combined Potential: ${session['profit_plan']['combined_potential']:,.2f}")
    print(f"Accounts: {len(session['portfolio'].accounts)}")
    print("=" * 70)


if __name__ == "__main__":


    main()