#!/usr/bin/env python3
"""
JARVIS Financial API-CLI Suite
Unified command-line interface for complete financial account control, monitoring, and administration

Provides JARVIS with full control over:
- All connected financial accounts
- Real-time monitoring and alerts
- Administrative operations
- Portfolio management
- Trading operations
- Data synchronization

Tags: #JARVIS #FINANCIAL_CLI #API_SUITE #CONTROL #MONITORING #ADMIN
"""

import sys
import json
import asyncio
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
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFinancialCLI")

# Import financial modules
try:
    from financial_account_manager import FinancialAccountManager
    from financial_account_registry import FinancialAccountRegistry, AccountType, ConnectionStatus
    from financial_connections.threecommas_connection import ThreeCommasConnection
    from financial_connections.binance_connection import BinanceConnection
    from financial_connections.fidelity_connection import FidelityConnection
    from copilot_money_integration import CopilotMoneyIntegration
    from azure_financial_aggregation import AzureFinancialAggregation
except ImportError as e:
    logger.warning(f"Some financial modules not available: {e}")


@dataclass
class FinancialStatus:
    """Comprehensive financial status"""
    timestamp: str
    total_accounts: int
    connected_accounts: int
    total_balance: float
    accounts: List[Dict[str, Any]]
    alerts: List[str]
    last_sync: Optional[str] = None


class JARVISFinancialCLI:
    """
    JARVIS Financial API-CLI Suite

    Unified interface for all financial operations
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Financial CLI"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "financial_cli"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize managers
        self.account_manager = FinancialAccountManager(self.project_root)
        self.account_registry = FinancialAccountRegistry(self.project_root)
        self.copilot_integration = CopilotMoneyIntegration(self.project_root)
        self.azure_aggregation = AzureFinancialAggregation(self.project_root) if 'AzureFinancialAggregation' in globals() else None

        logger.info("✅ JARVIS Financial CLI Suite initialized")
        logger.info("   Full control, monitoring, and administration: ENABLED")

    # ============================================================================
    # ACCOUNT MANAGEMENT
    # ============================================================================

    def list_accounts(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all financial accounts"""
        logger.info("📋 Listing financial accounts...")

        accounts = self.account_registry.list_accounts()

        if status_filter:
            status_enum = ConnectionStatus[status_filter.upper()]
            accounts = [a for a in accounts if a.status == status_enum]

        return accounts

    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account details"""
        account = self.account_registry.get_account(account_id)
        return account

    def connect_account(self, account_id: str) -> Dict[str, Any]:
        """Connect to a financial account"""
        logger.info(f"🔌 Connecting to account: {account_id}")

        result = self.account_manager.connect_account(account_id)
        return result

    def disconnect_account(self, account_id: str) -> Dict[str, Any]:
        """Disconnect from a financial account"""
        logger.info(f"🔌 Disconnecting from account: {account_id}")

        result = self.account_manager.disconnect_account(account_id)
        return result

    def connect_all(self) -> Dict[str, Any]:
        """Connect to all registered accounts"""
        logger.info("🔌 Connecting to all accounts...")

        result = self.account_manager.connect_all_accounts()
        return result

    def register_account(self, account_type: str, name: str, **kwargs) -> Dict[str, Any]:
        """Register a new financial account"""
        logger.info(f"➕ Registering account: {name} ({account_type})")

        account_type_enum = AccountType[account_type.upper()]
        result = self.account_registry.register_account(
            account_type=account_type_enum,
            name=name,
            **kwargs
        )
        return result

    # ============================================================================
    # BALANCE & PORTFOLIO
    # ============================================================================

    def get_balances(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get account balances"""
        logger.info("💰 Retrieving balances...")

        if account_id:
            account = self.account_registry.get_account(account_id)
            if not account:
                return {"error": f"Account {account_id} not found"}

            # Get balance for specific account
            connection = self._get_connection(account)
            if connection:
                balance = connection.get_balance()
                return {
                    "account_id": account_id,
                    "balance": balance,
                    "currency": account.get("currency", "USD")
                }
        else:
            # Get all balances
            accounts = self.account_registry.list_accounts()
            balances = {}
            total = 0.0

            for account in accounts:
                if account.status == ConnectionStatus.CONNECTED:
                    connection = self._get_connection(account)
                    if connection:
                        balance = connection.get_balance()
                        balances[account.id] = {
                            "name": account.name,
                            "balance": balance,
                            "currency": account.get("currency", "USD")
                        }
                        total += balance if isinstance(balance, (int, float)) else 0.0

            return {
                "total_balance": total,
                "accounts": balances,
                "count": len(balances)
            }

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        logger.info("📊 Generating portfolio summary...")

        accounts = self.account_registry.list_accounts()
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_accounts": len(accounts),
            "connected_accounts": sum(1 for a in accounts if a.status == ConnectionStatus.CONNECTED),
            "accounts": [],
            "total_balance": 0.0,
            "by_type": {}
        }

        for account in accounts:
            account_data = {
                "id": account.id,
                "name": account.name,
                "type": account.account_type.value,
                "status": account.status.value,
                "balance": None
            }

            if account.status == ConnectionStatus.CONNECTED:
                connection = self._get_connection(account)
                if connection:
                    balance = connection.get_balance()
                    account_data["balance"] = balance
                    if isinstance(balance, (int, float)):
                        summary["total_balance"] += balance

                    # Group by type
                    acc_type = account.account_type.value
                    if acc_type not in summary["by_type"]:
                        summary["by_type"][acc_type] = {"count": 0, "balance": 0.0}
                    summary["by_type"][acc_type]["count"] += 1
                    if isinstance(balance, (int, float)):
                        summary["by_type"][acc_type]["balance"] += balance

            summary["accounts"].append(account_data)

        return summary

    # ============================================================================
    # MONITORING & ALERTS
    # ============================================================================

    def monitor_accounts(self, interval: int = 60) -> Dict[str, Any]:
        """Monitor all accounts continuously"""
        logger.info(f"👁️  Starting account monitoring (interval: {interval}s)...")

        # This would run in a loop, checking account status
        # For now, return current status
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        logger.info("📊 Getting system status...")

        accounts = self.account_registry.list_accounts()
        connected = [a for a in accounts if a.status == ConnectionStatus.CONNECTED]

        status = FinancialStatus(
            timestamp=datetime.now().isoformat(),
            total_accounts=len(accounts),
            connected_accounts=len(connected),
            total_balance=0.0,
            accounts=[],
            alerts=[],
            last_sync=None
        )

        # Check each account
        for account in accounts:
            account_status = {
                "id": account.id,
                "name": account.name,
                "type": account.account_type.value,
                "status": account.status.value,
                "last_check": None,
                "balance": None
            }

            if account.status == ConnectionStatus.CONNECTED:
                connection = self._get_connection(account)
                if connection:
                    try:
                        balance = connection.get_balance()
                        account_status["balance"] = balance
                        account_status["last_check"] = datetime.now().isoformat()

                        if isinstance(balance, (int, float)):
                            status.total_balance += balance
                    except Exception as e:
                        status.alerts.append(f"Error getting balance for {account.name}: {e}")

            status.accounts.append(account_status)

        return asdict(status)

    def check_alerts(self) -> List[str]:
        """Check for alerts and issues"""
        logger.info("🔔 Checking for alerts...")

        alerts = []
        accounts = self.account_registry.list_accounts()

        for account in accounts:
            if account.status == ConnectionStatus.DISCONNECTED:
                alerts.append(f"⚠️  {account.name} is disconnected")
            elif account.status == ConnectionStatus.ERROR:
                alerts.append(f"❌ {account.name} has errors")

        return alerts

    # ============================================================================
    # TRADING OPERATIONS
    # ============================================================================

    def get_positions(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get trading positions"""
        logger.info("📈 Retrieving positions...")

        positions = {}

        if account_id:
            account = self.account_registry.get_account(account_id)
            if account and account.account_type in [AccountType.CRYPTO_EXCHANGE, AccountType.TRADING_BOT]:
                connection = self._get_connection(account)
                if connection and hasattr(connection, 'get_positions'):
                    positions[account_id] = connection.get_positions()
        else:
            accounts = self.account_registry.list_accounts()
            for account in accounts:
                if account.status == ConnectionStatus.CONNECTED:
                    if account.account_type in [AccountType.CRYPTO_EXCHANGE, AccountType.TRADING_BOT]:
                        connection = self._get_connection(account)
                        if connection and hasattr(connection, 'get_positions'):
                            try:
                                positions[account.id] = connection.get_positions()
                            except Exception as e:
                                logger.warning(f"Error getting positions for {account.name}: {e}")

        return positions

    def get_orders(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get open orders"""
        logger.info("📋 Retrieving orders...")

        orders = {}

        if account_id:
            account = self.account_registry.get_account(account_id)
            if account:
                connection = self._get_connection(account)
                if connection and hasattr(connection, 'get_open_orders'):
                    orders[account_id] = connection.get_open_orders()
        else:
            accounts = self.account_registry.list_accounts()
            for account in accounts:
                if account.status == ConnectionStatus.CONNECTED:
                    connection = self._get_connection(account)
                    if connection and hasattr(connection, 'get_open_orders'):
                        try:
                            orders[account.id] = connection.get_open_orders()
                        except Exception as e:
                            logger.warning(f"Error getting orders for {account.name}: {e}")

        return orders

    # ============================================================================
    # DATA SYNCHRONIZATION
    # ============================================================================

    def sync_all(self) -> Dict[str, Any]:
        """Synchronize all account data"""
        logger.info("🔄 Synchronizing all accounts...")

        results = {
            "started_at": datetime.now().isoformat(),
            "accounts_synced": 0,
            "accounts_failed": 0,
            "results": {}
        }

        accounts = self.account_registry.list_accounts()

        for account in accounts:
            if account.status == ConnectionStatus.CONNECTED:
                try:
                    connection = self._get_connection(account)
                    if connection:
                        # Get latest data
                        balance = connection.get_balance()
                        account_info = connection.get_account_info()

                        results["results"][account.id] = {
                            "success": True,
                            "balance": balance,
                            "info": account_info
                        }
                        results["accounts_synced"] += 1
                except Exception as e:
                    results["results"][account.id] = {
                        "success": False,
                        "error": str(e)
                    }
                    results["accounts_failed"] += 1

        results["completed_at"] = datetime.now().isoformat()
        return results

    def import_copilot_data(self, csv_file: Path) -> Dict[str, Any]:
        """Import Copilot Money CSV data"""
        logger.info(f"📥 Importing Copilot Money data: {csv_file}")

        result = self.copilot_integration.import_csv_export(csv_file)
        return result

    def get_azure_aggregation_status(self) -> Dict[str, Any]:
        """Get Azure financial aggregation status"""
        if not self.azure_aggregation:
            return {"error": "Azure aggregation not available"}

        logger.info("☁️  Checking Azure aggregation status...")

        status = {
            "available": True,
            "aggregators": ["plaid", "finicity", "mx", "akoya"],
            "azure_services": {
                "key_vault": "For credential storage",
                "functions": "For webhooks and API calls",
                "api_management": "For OAuth and proxy",
                "nat_gateway": "For MX IP allowlisting"
            },
            "setup_guide": str(self.azure_aggregation.data_dir / "azure_financial_setup_guide.json")
        }

        return status

    # ============================================================================
    # ADMINISTRATIVE OPERATIONS
    # ============================================================================

    def export_account_map(self, output_file: Optional[Path] = None) -> Path:
        try:
            """Export complete account map"""
            logger.info("💾 Exporting account map...")

            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"account_map_{timestamp}.json"

            result = self.account_manager.export_account_map(str(output_file))
            return Path(result)

        except Exception as e:
            self.logger.error(f"Error in export_account_map: {e}", exc_info=True)
            raise
    def generate_report(self, report_type: str = "full") -> Dict[str, Any]:
        try:
            """Generate financial report"""
            logger.info(f"📊 Generating {report_type} report...")

            report = {
                "generated_at": datetime.now().isoformat(),
                "report_type": report_type,
                "portfolio": self.get_portfolio_summary(),
                "status": self.get_status(),
                "alerts": self.check_alerts()
            }

            if report_type == "full":
                report["positions"] = self.get_positions()
                report["orders"] = self.get_orders()
                report["sync_status"] = self.sync_all()

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.output_dir / f"financial_report_{report_type}_{timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            report["report_file"] = str(report_file)
            return report

        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _get_connection(self, account: Any):
        """Get connection instance for account"""
        try:
            if account.account_type == AccountType.TRADING_BOT:
                return ThreeCommasConnection(account.id)
            elif account.account_type == AccountType.CRYPTO_EXCHANGE:
                return BinanceConnection(account.id)
            elif account.account_type == AccountType.TRADITIONAL_BROKERAGE:
                return FidelityConnection(account.id)
        except Exception as e:
            logger.warning(f"Could not create connection for {account.name}: {e}")
        return None


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Financial API-CLI Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all accounts
  jarvis-financial list

  # Get portfolio summary
  jarvis-financial portfolio

  # Connect to all accounts
  jarvis-financial connect --all

  # Get balances
  jarvis-financial balances

  # Monitor accounts
  jarvis-financial monitor

  # Generate full report
  jarvis-financial report --type full
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Account management
    list_parser = subparsers.add_parser('list', help='List all accounts')
    list_parser.add_argument('--status', choices=['connected', 'disconnected', 'error'], help='Filter by status')

    connect_parser = subparsers.add_parser('connect', help='Connect to account(s)')
    connect_parser.add_argument('--account-id', help='Specific account ID')
    connect_parser.add_argument('--all', action='store_true', help='Connect to all accounts')

    disconnect_parser = subparsers.add_parser('disconnect', help='Disconnect from account')
    disconnect_parser.add_argument('account_id', help='Account ID to disconnect')

    register_parser = subparsers.add_parser('register', help='Register new account')
    register_parser.add_argument('--type', required=True, help='Account type')
    register_parser.add_argument('--name', required=True, help='Account name')

    # Portfolio & balances
    portfolio_parser = subparsers.add_parser('portfolio', help='Get portfolio summary')

    balances_parser = subparsers.add_parser('balances', help='Get account balances')
    balances_parser.add_argument('--account-id', help='Specific account ID')

    # Monitoring
    status_parser = subparsers.add_parser('status', help='Get system status')

    monitor_parser = subparsers.add_parser('monitor', help='Monitor accounts')
    monitor_parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')

    alerts_parser = subparsers.add_parser('alerts', help='Check for alerts')

    # Trading
    positions_parser = subparsers.add_parser('positions', help='Get trading positions')
    positions_parser.add_argument('--account-id', help='Specific account ID')

    orders_parser = subparsers.add_parser('orders', help='Get open orders')
    orders_parser.add_argument('--account-id', help='Specific account ID')

    # Data sync
    sync_parser = subparsers.add_parser('sync', help='Synchronize all accounts')

    import_parser = subparsers.add_parser('import', help='Import external data')
    import_parser.add_argument('--copilot-csv', help='Import Copilot Money CSV')

    azure_parser = subparsers.add_parser('azure', help='Azure financial aggregation')
    azure_parser.add_argument('--status', action='store_true', help='Get Azure aggregation status')
    azure_parser.add_argument('--setup-guide', action='store_true', help='Generate setup guide')

    # Reports
    report_parser = subparsers.add_parser('report', help='Generate financial report')
    report_parser.add_argument('--type', choices=['full', 'summary', 'status'], default='full', help='Report type')

    # Export
    export_parser = subparsers.add_parser('export', help='Export account map')
    export_parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = JARVISFinancialCLI()

    # Execute command
    try:
        if args.command == 'list':
            accounts = cli.list_accounts(args.status)
            print(f"\n📋 Financial Accounts ({len(accounts)}):\n")
            for acc in accounts:
                print(f"  • {acc.name} ({acc.account_type.value}) - {acc.status.value}")

        elif args.command == 'connect':
            if args.all:
                result = cli.connect_all()
                print(f"\n✅ Connected to {result.get('connected', 0)} accounts")
            elif args.account_id:
                result = cli.connect_account(args.account_id)
                print(f"\n✅ Connection result: {result.get('success', False)}")
            else:
                connect_parser.print_help()

        elif args.command == 'disconnect':
            result = cli.disconnect_account(args.account_id)
            print(f"\n✅ Disconnected: {result.get('success', False)}")

        elif args.command == 'register':
            result = cli.register_account(args.type, args.name)
            print(f"\n✅ Registered account: {result.get('account_id')}")

        elif args.command == 'portfolio':
            summary = cli.get_portfolio_summary()
            print("\n" + "=" * 70)
            print("📊 PORTFOLIO SUMMARY")
            print("=" * 70)
            print(f"\nTotal Accounts: {summary['total_accounts']}")
            print(f"Connected: {summary['connected_accounts']}")
            print(f"Total Balance: ${summary['total_balance']:,.2f}")
            print(f"\nBy Type:")
            for acc_type, data in summary['by_type'].items():
                print(f"  {acc_type}: {data['count']} accounts, ${data['balance']:,.2f}")

        elif args.command == 'balances':
            balances = cli.get_balances(args.account_id)
            if args.account_id:
                print(f"\n💰 Balance for {args.account_id}:")
                print(f"  ${balances.get('balance', 0):,.2f} {balances.get('currency', 'USD')}")
            else:
                print(f"\n💰 Total Balance: ${balances.get('total_balance', 0):,.2f}")
                print(f"Accounts: {balances.get('count', 0)}")
                for acc_id, data in balances.get('accounts', {}).items():
                    print(f"  {data['name']}: ${data['balance']:,.2f} {data['currency']}")

        elif args.command == 'status':
            status = cli.get_status()
            print("\n" + "=" * 70)
            print("📊 SYSTEM STATUS")
            print("=" * 70)
            print(f"\nTotal Accounts: {status['total_accounts']}")
            print(f"Connected: {status['connected_accounts']}")
            print(f"Total Balance: ${status['total_balance']:,.2f}")
            if status['alerts']:
                print(f"\n⚠️  Alerts ({len(status['alerts'])}):")
                for alert in status['alerts']:
                    print(f"  {alert}")

        elif args.command == 'monitor':
            print(f"\n👁️  Monitoring accounts (interval: {args.interval}s)...")
            print("Press Ctrl+C to stop")
            try:
                while True:
                    status = cli.monitor_accounts(args.interval)
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Status: {status['connected_accounts']}/{status['total_accounts']} connected")
                    if status['alerts']:
                        for alert in status['alerts']:
                            print(f"  {alert}")
                    import time
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n\n✅ Monitoring stopped")

        elif args.command == 'alerts':
            alerts = cli.check_alerts()
            if alerts:
                print(f"\n🔔 Alerts ({len(alerts)}):")
                for alert in alerts:
                    print(f"  {alert}")
            else:
                print("\n✅ No alerts")

        elif args.command == 'positions':
            positions = cli.get_positions(args.account_id)
            print(f"\n📈 Positions:")
            print(json.dumps(positions, indent=2))

        elif args.command == 'orders':
            orders = cli.get_orders(args.account_id)
            print(f"\n📋 Orders:")
            print(json.dumps(orders, indent=2))

        elif args.command == 'sync':
            result = cli.sync_all()
            print(f"\n🔄 Synchronization complete:")
            print(f"  Synced: {result['accounts_synced']}")
            print(f"  Failed: {result['accounts_failed']}")

        elif args.command == 'import':
            if args.copilot_csv:
                result = cli.import_copilot_data(Path(args.copilot_csv))
                if result['success']:
                    print(f"\n✅ Imported {result['statistics']['total_transactions']} transactions")
                else:
                    print("\n❌ Import failed")
            else:
                import_parser.print_help()

        elif args.command == 'report':
            report = cli.generate_report(args.type)
            print(f"\n📊 Report generated: {report['report_file']}")
            print(f"  Type: {report['report_type']}")
            print(f"  Accounts: {report['portfolio']['total_accounts']}")
            print(f"  Balance: ${report['portfolio']['total_balance']:,.2f}")

        elif args.command == 'export':
            output_file = Path(args.output) if args.output else None
            result = cli.export_account_map(output_file)
            print(f"\n💾 Account map exported: {result}")

        elif args.command == 'azure':
            if args.status:
                status = cli.get_azure_aggregation_status()
                print("\n" + "=" * 70)
                print("☁️  AZURE FINANCIAL AGGREGATION")
                print("=" * 70)
                if "error" in status:
                    print(f"\n❌ {status['error']}")
                else:
                    print(f"\n✅ Available: {status['available']}")
                    print(f"Aggregators: {', '.join(status['aggregators'])}")
                    print(f"\nAzure Services:")
                    for service, purpose in status['azure_services'].items():
                        print(f"  • {service}: {purpose}")
                    print(f"\nSetup Guide: {status['setup_guide']}")
            elif args.setup_guide:
                if cli.azure_aggregation:
                    guide_file = cli.azure_aggregation.save_setup_guide()
                    print(f"\n✅ Azure setup guide generated: {guide_file}")
                else:
                    print("\n❌ Azure aggregation not available")
            else:
                azure_parser.print_help()

    except Exception as e:
        logger.error(f"❌ Error executing command: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":


    main()