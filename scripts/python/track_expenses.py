#!/usr/bin/env python3
"""
Track Business Expenses
Simple expense tracking system for startup
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TrackExpenses")


def load_expenses() -> List[Dict[str, Any]]:
    try:
        """Load expenses from file"""
        expenses_file = script_dir / "data" / "financial" / "expenses.json"
        expenses_file.parent.mkdir(parents=True, exist_ok=True)

        if expenses_file.exists():
            with open(expenses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


    except Exception as e:
        logger.error(f"Error in load_expenses: {e}", exc_info=True)
        raise
def save_expenses(expenses: List[Dict[str, Any]]):
    try:
        """Save expenses to file"""
        expenses_file = script_dir / "data" / "financial" / "expenses.json"
        expenses_file.parent.mkdir(parents=True, exist_ok=True)

        with open(expenses_file, 'w', encoding='utf-8') as f:
            json.dump(expenses, f, indent=2, default=str, ensure_ascii=False)

        logger.info(f"✅ Saved {len(expenses)} expenses")


    except Exception as e:
        logger.error(f"Error in save_expenses: {e}", exc_info=True)
        raise
def add_expense(
    description: str,
    amount: float,
    category: str,
    date: Optional[str] = None,
    vendor: Optional[str] = None,
    receipt_path: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Add a new expense"""
    expense = {
        "expense_id": f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "amount": float(amount),
        "category": category,
        "vendor": vendor or "",
        "receipt_path": receipt_path or "",
        "notes": notes or "",
        "created_at": datetime.now().isoformat()
    }

    expenses = load_expenses()
    expenses.append(expense)
    save_expenses(expenses)

    logger.info(f"✅ Added expense: {description} (${amount:.2f})")
    return expense


def get_expense_summary(month: Optional[str] = None, year: Optional[str] = None) -> Dict[str, Any]:
    """Get expense summary"""
    expenses = load_expenses()

    # Filter by date if specified
    if month or year:
        filtered = []
        for exp in expenses:
            exp_date = datetime.fromisoformat(exp.get("created_at", exp.get("date", "")))
            if year and exp_date.strftime("%Y") != year:
                continue
            if month and exp_date.strftime("%m") != month:
                continue
            filtered.append(exp)
        expenses = filtered

    # Calculate totals
    total = sum(exp["amount"] for exp in expenses)

    # By category
    by_category = {}
    for exp in expenses:
        cat = exp.get("category", "Uncategorized")
        by_category[cat] = by_category.get(cat, 0) + exp["amount"]

    return {
        "total_expenses": len(expenses),
        "total_amount": total,
        "by_category": by_category,
        "period": f"{year or 'All'}-{month or 'All'}"
    }


def main():
    """Interactive expense tracking"""
    print("=" * 80)
    print("💰 Business Expense Tracker")
    print("=" * 80)
    print()

    while True:
        print("Options:")
        print("  1. Add expense")
        print("  2. View expenses")
        print("  3. View summary")
        print("  4. Exit")
        print()

        choice = input("Select option (1-4): ").strip()

        if choice == "1":
            print()
            print("Add New Expense:")
            description = input("Description: ").strip()
            if not description:
                print("❌ Description required")
                continue

            try:
                amount = float(input("Amount: $").strip())
            except ValueError:
                print("❌ Invalid amount")
                continue

            category = input("Category: ").strip() or "Uncategorized"
            date = input("Date (YYYY-MM-DD, or Enter for today): ").strip()
            vendor = input("Vendor (optional): ").strip()
            notes = input("Notes (optional): ").strip()

            expense = add_expense(description, amount, category, date or None, vendor, None, notes)
            print(f"✅ Expense added: {expense['expense_id']}")
            print()

        elif choice == "2":
            expenses = load_expenses()
            if not expenses:
                print("No expenses recorded yet.")
            else:
                print()
                print(f"Total Expenses: {len(expenses)}")
                print("-" * 80)
                for exp in sorted(expenses, key=lambda x: x.get("date", ""), reverse=True)[:10]:
                    print(f"{exp.get('date', 'N/A')} | {exp.get('category', 'N/A'):15} | ${exp['amount']:8.2f} | {exp.get('description', 'N/A')}")
                print()

        elif choice == "3":
            year = input("Year (YYYY, or Enter for all): ").strip() or None
            month = input("Month (MM, or Enter for all): ").strip() or None
            summary = get_expense_summary(month, year)

            print()
            print(f"Expense Summary ({summary['period']}):")
            print(f"  Total Expenses: {summary['total_expenses']}")
            print(f"  Total Amount: ${summary['total_amount']:.2f}")
            print()
            print("By Category:")
            for cat, amount in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat:20} ${amount:10.2f}")
            print()

        elif choice == "4":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option")
            print()


if __name__ == "__main__":


    main()