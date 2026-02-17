#!/usr/bin/env python3
"""
Copilot Money Data Integration
Pulls data and information from Copilot Money app

Since Copilot Money has no public API, this module handles:
1. CSV export parsing (manual exports from the app)
2. Browser automation for web interface (if available)
3. Integration with underlying data sources (Plaid, etc.)

Tags: #COPILOT_MONEY #FINANCIAL_DATA #INTEGRATION #CSV_EXPORT
"""

import sys
import csv
import json
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

logger = get_logger("CopilotMoneyIntegration")


@dataclass
class CopilotTransaction:
    """Represents a Copilot Money transaction"""
    date: str
    name: str
    amount: float
    pending: bool
    posted: bool
    category: Optional[str] = None
    parent_category: Optional[str] = None
    excluded: bool = False
    type: Optional[str] = None
    account: Optional[str] = None
    account_mask: Optional[str] = None
    notes: Optional[str] = None
    recurring: Optional[str] = None


@dataclass
class CopilotAccount:
    """Represents a Copilot Money account"""
    name: str
    account_type: str
    balance: Optional[float] = None
    mask: Optional[str] = None
    institution: Optional[str] = None


class CopilotMoneyCSVParser:
    """Parser for Copilot Money CSV exports"""

    def __init__(self):
        """Initialize CSV parser"""
        self.logger = get_logger("CopilotMoneyCSVParser")

    def parse_export(self, csv_file: Path) -> List[CopilotTransaction]:
        """
        Parse Copilot Money CSV export

        CSV fields (from Copilot documentation):
        - date
        - name
        - amount
        - pending/posted
        - category
        - parent category
        - excluded
        - type
        - account
        - mask
        - notes
        - associated recurrings
        """
        self.logger.info(f"📄 Parsing Copilot Money CSV: {csv_file}")

        transactions = []

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(f, delimiter=delimiter)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Parse amount (handle negative for expenses)
                        amount_str = row.get('amount', '0').replace('$', '').replace(',', '').strip()
                        amount = float(amount_str) if amount_str else 0.0

                        # Parse pending/posted status
                        pending_posted = row.get('pending/posted', '').lower()
                        pending = 'pending' in pending_posted
                        posted = 'posted' in pending_posted

                        # Parse excluded flag
                        excluded_str = row.get('excluded', '').lower()
                        excluded = excluded_str in ['true', 'yes', '1', 'excluded']

                        transaction = CopilotTransaction(
                            date=row.get('date', ''),
                            name=row.get('name', ''),
                            amount=amount,
                            pending=pending,
                            posted=posted,
                            category=row.get('category', ''),
                            parent_category=row.get('parent category', ''),
                            excluded=excluded,
                            type=row.get('type', ''),
                            account=row.get('account', ''),
                            account_mask=row.get('mask', ''),
                            notes=row.get('notes', ''),
                            recurring=row.get('associated recurrings', '')
                        )

                        transactions.append(transaction)

                    except Exception as e:
                        self.logger.warning(f"⚠️  Error parsing row {row_num}: {e}")
                        continue

            self.logger.info(f"✅ Parsed {len(transactions)} transactions from CSV")
            return transactions

        except FileNotFoundError:
            self.logger.error(f"❌ CSV file not found: {csv_file}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error parsing CSV: {e}", exc_info=True)
            return []

    def export_to_json(self, transactions: List[CopilotTransaction], output_file: Path) -> Path:
        try:
            """Export transactions to JSON format"""
            self.logger.info(f"💾 Exporting {len(transactions)} transactions to JSON...")

            data = {
                "exported_at": datetime.now().isoformat(),
                "source": "copilot_money_csv",
                "total_transactions": len(transactions),
                "transactions": [asdict(t) for t in transactions]
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Exported to: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in export_to_json: {e}", exc_info=True)
            raise
class CopilotMoneyBrowserExtractor:
    """
    Browser-based data extraction for Copilot Money web interface

    Uses MCP Browser tools to extract data if web interface is available
    """

    def __init__(self):
        """Initialize browser extractor"""
        self.logger = get_logger("CopilotMoneyBrowserExtractor")
        self.copilot_url = "https://copilot.money"

    def extract_accounts(self) -> List[Dict[str, Any]]:
        """
        Extract account information from Copilot Money web interface

        Returns list of account dictionaries
        """
        self.logger.info("🌐 Extracting accounts from Copilot Money web interface...")

        # This would use MCP Browser tools to:
        # 1. Navigate to copilot.money
        # 2. Login (if needed)
        # 3. Extract account balances and information
        # 4. Return structured data

        accounts = []

        # Placeholder for browser automation
        # In production, this would use:
        # - browser_navigate()
        # - browser_snapshot()
        # - browser_click() to navigate
        # - Extract data from page elements

        self.logger.warning("⚠️  Browser extraction not yet implemented")
        self.logger.info("   Use CSV export method instead")

        return accounts

    def extract_transactions(self, account_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract transactions from Copilot Money web interface

        Args:
            account_name: Optional account name to filter by

        Returns list of transaction dictionaries
        """
        self.logger.info("🌐 Extracting transactions from Copilot Money web interface...")

        transactions = []

        # Placeholder for browser automation
        # Would navigate to transactions page and extract data

        self.logger.warning("⚠️  Browser extraction not yet implemented")
        self.logger.info("   Use CSV export method instead")

        return transactions


class CopilotMoneyIntegration:
    """
    Main integration class for Copilot Money

    Handles all methods of pulling data from Copilot Money
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Copilot Money integration"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "copilot_money"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.csv_parser = CopilotMoneyCSVParser()
        self.browser_extractor = CopilotMoneyBrowserExtractor()

        logger.info("✅ Copilot Money Integration initialized")
        logger.info("   Methods: CSV export parsing, Browser extraction (planned)")

    def import_csv_export(self, csv_file: Path) -> Dict[str, Any]:
        """
        Import data from Copilot Money CSV export

        Args:
            csv_file: Path to CSV export file

        Returns:
            Dictionary with imported data and statistics
        """
        logger.info(f"📥 Importing Copilot Money CSV export: {csv_file}")

        transactions = self.csv_parser.parse_export(csv_file)

        if not transactions:
            logger.warning("⚠️  No transactions found in CSV")
            return {
                "success": False,
                "transactions": [],
                "statistics": {}
            }

        # Generate statistics
        total_amount = sum(t.amount for t in transactions)
        income = sum(t.amount for t in transactions if t.amount > 0)
        expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)

        categories = {}
        for t in transactions:
            if t.category:
                categories[t.category] = categories.get(t.category, 0) + abs(t.amount)

        statistics = {
            "total_transactions": len(transactions),
            "total_amount": total_amount,
            "total_income": income,
            "total_expenses": expenses,
            "net_flow": income - expenses,
            "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            "date_range": {
                "earliest": min(t.date for t in transactions if t.date),
                "latest": max(t.date for t in transactions if t.date)
            }
        }

        # Export to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = self.data_dir / f"copilot_transactions_{timestamp}.json"
        self.csv_parser.export_to_json(transactions, json_file)

        result = {
            "success": True,
            "transactions": [asdict(t) for t in transactions],
            "statistics": statistics,
            "exported_json": str(json_file)
        }

        logger.info(f"✅ Imported {len(transactions)} transactions")
        logger.info(f"   Income: ${income:,.2f}")
        logger.info(f"   Expenses: ${expenses:,.2f}")
        logger.info(f"   Net: ${statistics['net_flow']:,.2f}")

        return result

    def get_export_instructions(self) -> str:
        """Get instructions for exporting data from Copilot Money"""
        instructions = """
📋 HOW TO EXPORT DATA FROM COPILOT MONEY:

1. Open Copilot Money app (iOS, iPadOS, or macOS)

2. Navigate to Settings

3. Find "Export" or "Export Transactions" option

4. Choose export format (CSV)

5. Save the exported file

6. Use this script to import:
   python scripts/python/copilot_money_integration.py --import-csv <path_to_export.csv>

CSV Fields Included:
- date
- name
- amount
- pending/posted
- category
- parent category
- excluded
- type
- account
- mask
- notes
- associated recurrings

Note: Balances and holdings are NOT exportable via CSV.
"""
        return instructions


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Copilot Money Data Integration")
        parser.add_argument("--import-csv", type=str, help="Import CSV export file")
        parser.add_argument("--instructions", action="store_true", help="Show export instructions")
        parser.add_argument("--stats", type=str, help="Show statistics for imported CSV file")

        args = parser.parse_args()

        integration = CopilotMoneyIntegration()

        if args.instructions:
            print(integration.get_export_instructions())

        elif args.import_csv:
            csv_file = Path(args.import_csv)
            if not csv_file.exists():
                print(f"❌ CSV file not found: {csv_file}")
                return

            result = integration.import_csv_export(csv_file)

            if result["success"]:
                print("\n" + "=" * 70)
                print("✅ COPILOT MONEY DATA IMPORTED")
                print("=" * 70)
                print(f"\nTransactions: {result['statistics']['total_transactions']}")
                print(f"Income: ${result['statistics']['total_income']:,.2f}")
                print(f"Expenses: ${result['statistics']['total_expenses']:,.2f}")
                print(f"Net Flow: ${result['statistics']['net_flow']:,.2f}")
                print(f"\nExported JSON: {result['exported_json']}")
            else:
                print("❌ Import failed")

        elif args.stats:
            # Load and display statistics from JSON file
            json_file = Path(args.stats)
            if json_file.exists():
                with open(json_file, 'r') as f:
                    data = json.load(f)

                stats = data.get("statistics", {})
                print("\n" + "=" * 70)
                print("📊 COPILOT MONEY STATISTICS")
                print("=" * 70)
                print(f"\nTotal Transactions: {stats.get('total_transactions', 0)}")
                print(f"Income: ${stats.get('total_income', 0):,.2f}")
                print(f"Expenses: ${stats.get('total_expenses', 0):,.2f}")
                print(f"Net Flow: ${stats.get('net_flow', 0):,.2f}")
            else:
                print(f"❌ JSON file not found: {json_file}")

        else:
            parser.print_help()
            print("\n" + integration.get_export_instructions())


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()