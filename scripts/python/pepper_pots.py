#!/usr/bin/env python3
"""
PEPPER POTS - Executive Assistant & Business Operations Manager
Handles business operations, documentation organization, and administrative tasks
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

logger = get_logger("PepperPots")


class PepperPots:
    """
    PEPPER POTS - Executive Assistant & Business Operations Manager

    Handles:
    - Business operations management
    - Documentation organization
    - Administrative coordination
    - Professional standards maintenance
    """

    def __init__(self):
        self.name = "PEPPER POTS"
        self.role = "Executive Assistant & Business Operations Manager"
        self.project_root = script_dir

        # Key directories
        self.dirs = {
            "business_docs": self.project_root / "docs" / "business",
            "startup_docs": self.project_root / "docs" / "startup",
            "email_docs": self.project_root / "docs" / "email",
            "templates": self.project_root / "templates",
            "data": self.project_root / "data",
            "scripts": self.project_root / "scripts" / "python"
        }

        logger.info(f"💼 {self.name} initialized - {self.role}")

    def status_report(self) -> Dict[str, Any]:
        """Generate status report"""
        report = {
            "system": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "business_operations": {
                "invoices": self._count_files(self.dirs["data"] / "invoices"),
                "expenses": self._check_expense_tracking(),
                "clients": self._count_clients(),
                "tasks": self._count_tasks()
            },
            "documentation": {
                "business_docs": self._count_files(self.dirs["business_docs"]),
                "startup_docs": self._count_files(self.dirs["startup_docs"]),
                "email_docs": self._count_files(self.dirs["email_docs"]),
                "templates": self._count_files(self.dirs["templates"])
            },
            "organization": {
                "indexes": self._count_indexes(),
                "readmes": self._count_readmes()
            }
        }
        return report

    def organize_documentation(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Organize documentation"""
        results = {
            "organized": [],
            "errors": []
        }

        try:
            if category == "email" or category is None:
                # Run email organization
                from scripts.python.organize_email_docs import main as organize_email
                organize_email()
                results["organized"].append("email_docs")

            if category == "startup" or category is None:
                # Run startup organization
                from scripts.python.organize_and_cleanup import main as organize_startup
                organize_startup()
                results["organized"].append("startup_docs")

            logger.info(f"✅ Documentation organized: {results['organized']}")
        except Exception as e:
            error_msg = f"Error organizing documentation: {e}"
            logger.error(f"❌ {error_msg}")
            results["errors"].append(error_msg)

        return results

    def business_status(self) -> Dict[str, Any]:
        try:
            """Get business operations status"""
            status = {
                "financial": {
                    "expenses_tracked": self._check_expense_tracking(),
                    "invoices_generated": self._count_files(self.dirs["data"] / "invoices"),
                    "status": "operational" if self._check_expense_tracking() else "needs_setup"
                },
                "clients": {
                    "total_clients": self._count_clients(),
                    "database_exists": (self.dirs["data"] / "clients" / "clients_database.json").exists(),
                    "status": "operational" if self._count_clients() > 0 else "needs_setup"
                },
                "tasks": {
                    "total_tasks": self._count_tasks(),
                    "database_exists": (self.dirs["data"] / "tasks.json").exists(),
                    "status": "operational" if (self.dirs["data"] / "tasks.json").exists() else "needs_setup"
                }
            }
            return status

        except Exception as e:
            self.logger.error(f"Error in business_status: {e}", exc_info=True)
            raise
    def generate_invoice_summary(self) -> Dict[str, Any]:
        try:
            """Generate invoice summary"""
            invoice_dir = self.dirs["data"] / "invoices"
            if not invoice_dir.exists():
                return {"status": "no_invoices", "count": 0}

            invoices = list(invoice_dir.glob("*.html"))
            return {
                "status": "operational",
                "total_invoices": len(invoices),
                "latest": max(invoices, key=lambda p: p.stat().st_mtime).name if invoices else None
            }

        except Exception as e:
            self.logger.error(f"Error in generate_invoice_summary: {e}", exc_info=True)
            raise
    def expense_summary(self) -> Dict[str, Any]:
        """Get expense tracking summary"""
        expense_file = self.dirs["data"] / "financial" / "expenses.json"
        if not expense_file.exists():
            return {"status": "no_expenses", "total": 0}

        try:
            with open(expense_file, 'r') as f:
                expenses = json.load(f)

            total = sum(exp.get("amount", 0) for exp in expenses)
            return {
                "status": "operational",
                "total_expenses": len(expenses),
                "total_amount": total,
                "latest": expenses[-1] if expenses else None
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _count_files(self, directory: Path) -> int:
        try:
            """Count files in directory"""
            if not directory.exists():
                return 0
            return len(list(directory.rglob("*.md"))) + len(list(directory.rglob("*.html")))

        except Exception as e:
            self.logger.error(f"Error in _count_files: {e}", exc_info=True)
            raise
    def _count_indexes(self) -> int:
        try:
            """Count index files"""
            indexes = 0
            for doc_dir in [self.dirs["business_docs"], self.dirs["startup_docs"], self.dirs["email_docs"]]:
                if (doc_dir / "INDEX.md").exists():
                    indexes += 1
            return indexes

        except Exception as e:
            self.logger.error(f"Error in _count_indexes: {e}", exc_info=True)
            raise
    def _count_readmes(self) -> int:
        """Count README files"""
        readmes = 0
        for root_dir in [self.dirs["business_docs"], self.dirs["startup_docs"], self.dirs["email_docs"], self.dirs["templates"], self.dirs["data"]]:
            if root_dir.exists():
                readmes += len(list(root_dir.rglob("README.md")))
        return readmes

    def _check_expense_tracking(self) -> bool:
        """Check if expense tracking is active"""
        expense_file = self.dirs["data"] / "financial" / "expenses.json"
        if not expense_file.exists():
            return False
        try:
            with open(expense_file, 'r') as f:
                expenses = json.load(f)
            return len(expenses) > 0
        except:
            return False

    def _count_clients(self) -> int:
        """Count clients in database"""
        client_db = self.dirs["data"] / "clients" / "clients_database.json"
        if not client_db.exists():
            return 0
        try:
            with open(client_db, 'r') as f:
                data = json.load(f)
            return len(data.get("clients", []))
        except:
            return 0

    def _count_tasks(self) -> int:
        """Count tasks"""
        task_file = self.dirs["data"] / "tasks.json"
        if not task_file.exists():
            return 0
        try:
            with open(task_file, 'r') as f:
                data = json.load(f)
            return len(data.get("tasks", []))
        except:
            return 0


def main():
    """PEPPER POTS main interface"""
    print("="*80)
    print("💼 PEPPER POTS - Executive Assistant & Business Operations Manager")
    print("="*80)
    print()

    pepper = PepperPots()

    print("📊 Status Report:")
    print()

    status = pepper.status_report()

    print("Business Operations:")
    print(f"  📄 Invoices: {status['business_operations']['invoices']}")
    print(f"  💰 Expenses: {'✅ Tracked' if status['business_operations']['expenses'] else '❌ Not tracked'}")
    print(f"  👥 Clients: {status['business_operations']['clients']}")
    print(f"  ✅ Tasks: {status['business_operations']['tasks']}")
    print()

    print("Documentation:")
    print(f"  📚 Business Docs: {status['documentation']['business_docs']} files")
    print(f"  🚀 Startup Docs: {status['documentation']['startup_docs']} files")
    print(f"  📧 Email Docs: {status['documentation']['email_docs']} files")
    print(f"  📝 Templates: {status['documentation']['templates']} files")
    print()

    print("Organization:")
    print(f"  📑 Indexes: {status['organization']['indexes']}")
    print(f"  📖 READMEs: {status['organization']['readmes']}")
    print()

    print("="*80)
    print("✅ PEPPER POTS Status Report Complete")
    print("="*80)
    print()
    print("💡 Quick Actions:")
    print("  - Organize docs: python scripts/python/pepper_pots.py --organize")
    print("  - Business status: python scripts/python/pepper_pots.py --business")
    print("  - Full report: python scripts/python/pepper_pots.py --full")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PEPPER POTS - Executive Assistant")
    parser.add_argument("--organize", action="store_true", help="Organize documentation")
    parser.add_argument("--business", action="store_true", help="Show business status")
    parser.add_argument("--full", action="store_true", help="Full status report")

    args = parser.parse_args()

    pepper = PepperPots()

    if args.organize:
        print("🧹 Organizing documentation...")
        results = pepper.organize_documentation()
        print(f"✅ Organized: {results['organized']}")
    elif args.business:
        print("💼 Business Operations Status:")
        status = pepper.business_status()
        print(json.dumps(status, indent=2))
    elif args.full:
        status = pepper.status_report()
        print(json.dumps(status, indent=2))
    else:


        main()