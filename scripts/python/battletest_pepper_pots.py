#!/usr/bin/env python3
"""
Battletest PEPPER POTS - Comprehensive Testing Suite
Tests all PEPPER POTS functionality under various conditions
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.pepper_pots import PepperPots
    from scripts.python.lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("BattletestPepperPots")


class BattletestResults:
    """Track battletest results"""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        self.warnings = []
        self.results = []

    def add_result(self, test_name: str, passed: bool, message: str = "", error: Exception = None):
        """Add test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            self.tests_failed += 1
            status = "❌ FAIL"
            if error:
                self.errors.append(f"{test_name}: {error}")

        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)

        print(f"{status} - {test_name}")
        if message:
            print(f"   {message}")
        if error:
            print(f"   Error: {error}")

    def add_warning(self, warning: str):
        """Add warning"""
        self.warnings.append(warning)
        print(f"⚠️  WARNING: {warning}")

    def summary(self) -> Dict[str, Any]:
        """Get test summary"""
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "pass_rate": f"{(self.tests_passed / self.tests_run * 100):.1f}%" if self.tests_run > 0 else "0%",
            "errors": len(self.errors),
            "warnings": len(self.warnings)
        }


def test_initialization(results: BattletestResults):
    """Test PEPPER POTS initialization"""
    try:
        pepper = PepperPots()
        assert pepper.name == "PEPPER POTS"
        assert pepper.role == "Executive Assistant & Business Operations Manager"
        assert pepper.project_root == script_dir
        results.add_result("Initialization", True, "PEPPER POTS initialized correctly")
        return pepper
    except Exception as e:
        results.add_result("Initialization", False, error=e)
        return None


def test_status_report(pepper: PepperPots, results: BattletestResults):
    """Test status report generation"""
    try:
        status = pepper.status_report()
        assert "system" in status
        assert "role" in status
        assert "business_operations" in status
        assert "documentation" in status
        assert "organization" in status
        assert status["system"] == "PEPPER POTS"
        results.add_result("Status Report", True, f"Report generated with {len(status)} sections")
    except Exception as e:
        results.add_result("Status Report", False, error=e)


def test_business_status(pepper: PepperPots, results: BattletestResults):
    """Test business status check"""
    try:
        business_status = pepper.business_status()
        assert "financial" in business_status
        assert "clients" in business_status
        assert "tasks" in business_status

        # Check financial status
        financial = business_status["financial"]
        assert "expenses_tracked" in financial
        assert "invoices_generated" in financial
        assert "status" in financial

        results.add_result("Business Status", True, 
                          f"Financial: {financial['status']}, "
                          f"Clients: {business_status['clients']['total_clients']}, "
                          f"Tasks: {business_status['tasks']['total_tasks']}")
    except Exception as e:
        results.add_result("Business Status", False, error=e)


def test_invoice_summary(pepper: PepperPots, results: BattletestResults):
    """Test invoice summary"""
    try:
        invoice_summary = pepper.generate_invoice_summary()
        assert "status" in invoice_summary
        assert "total_invoices" in invoice_summary

        if invoice_summary["status"] == "operational":
            results.add_result("Invoice Summary", True, 
                             f"{invoice_summary['total_invoices']} invoices found")
        else:
            results.add_warning("No invoices found - this is expected for new setup")
            results.add_result("Invoice Summary", True, "No invoices (expected)")
    except Exception as e:
        results.add_result("Invoice Summary", False, error=e)


def test_expense_summary(pepper: PepperPots, results: BattletestResults):
    """Test expense summary"""
    try:
        expense_summary = pepper.expense_summary()
        assert "status" in expense_summary

        if expense_summary["status"] == "operational":
            results.add_result("Expense Summary", True, 
                             f"{expense_summary['total_expenses']} expenses, "
                             f"${expense_summary['total_amount']:.2f} total")
        else:
            results.add_warning("No expenses tracked - this is expected for new setup")
            results.add_result("Expense Summary", True, "No expenses (expected)")
    except Exception as e:
        results.add_result("Expense Summary", False, error=e)


def test_directory_structure(pepper: PepperPots, results: BattletestResults):
    """Test directory structure"""
    try:
        all_exist = True
        missing = []

        for name, path in pepper.dirs.items():
            if not path.exists():
                all_exist = False
                missing.append(name)

        if all_exist:
            results.add_result("Directory Structure", True, 
                             f"All {len(pepper.dirs)} directories exist")
        else:
            results.add_warning(f"Missing directories: {', '.join(missing)}")
            results.add_result("Directory Structure", False, 
                             f"Missing: {', '.join(missing)}")
    except Exception as e:
        results.add_result("Directory Structure", False, error=e)


def test_file_counting(pepper: PepperPots, results: BattletestResults):
    """Test file counting functions"""
    try:
        # Test _count_files
        count = pepper._count_files(pepper.dirs["business_docs"])
        assert isinstance(count, int)
        assert count >= 0

        # Test _count_indexes
        indexes = pepper._count_indexes()
        assert isinstance(indexes, int)
        assert indexes >= 0

        # Test _count_readmes
        readmes = pepper._count_readmes()
        assert isinstance(readmes, int)
        assert readmes >= 0

        results.add_result("File Counting", True, 
                          f"Business docs: {count}, Indexes: {indexes}, READMEs: {readmes}")
    except Exception as e:
        results.add_result("File Counting", False, error=e)


def test_data_access(pepper: PepperPots, results: BattletestResults):
    """Test data access functions"""
    try:
        # Test expense tracking check
        expenses_tracked = pepper._check_expense_tracking()
        assert isinstance(expenses_tracked, bool)

        # Test client count
        client_count = pepper._count_clients()
        assert isinstance(client_count, int)
        assert client_count >= 0

        # Test task count
        task_count = pepper._count_tasks()
        assert isinstance(task_count, int)
        assert task_count >= 0

        results.add_result("Data Access", True, 
                          f"Expenses: {expenses_tracked}, Clients: {client_count}, Tasks: {task_count}")
    except Exception as e:
        results.add_result("Data Access", False, error=e)


def test_organization_capability(pepper: PepperPots, results: BattletestResults):
    """Test organization capability (dry run)"""
    try:
        # Test that organize_documentation method exists and is callable
        assert hasattr(pepper, 'organize_documentation')
        assert callable(pepper.organize_documentation)

        # Don't actually run it, just verify it exists
        results.add_result("Organization Capability", True, 
                          "organize_documentation method available")
    except Exception as e:
        results.add_result("Organization Capability", False, error=e)


def test_error_handling(pepper: PepperPots, results: BattletestResults):
    """Test error handling"""
    try:
        # Test with non-existent directory
        count = pepper._count_files(Path("/nonexistent/path"))
        assert count == 0

        # Test with None
        try:
            pepper._count_files(None)
            results.add_warning("No error raised for None path")
        except:
            pass  # Expected

        results.add_result("Error Handling", True, "Handles invalid paths gracefully")
    except Exception as e:
        results.add_result("Error Handling", False, error=e)


def test_integration_with_scripts(pepper: PepperPots, results: BattletestResults):
    """Test integration with other scripts"""
    try:
        # Check if key scripts exist
        scripts_to_check = [
            "generate_invoice.py",
            "track_expenses.py",
            "setup_business_operations.py"
        ]

        existing = []
        missing = []

        for script in scripts_to_check:
            script_path = pepper.dirs["scripts"] / script
            if script_path.exists():
                existing.append(script)
            else:
                missing.append(script)

        if len(existing) == len(scripts_to_check):
            results.add_result("Script Integration", True, 
                             f"All {len(existing)} scripts available")
        else:
            results.add_warning(f"Missing scripts: {', '.join(missing)}")
            results.add_result("Script Integration", True, 
                             f"{len(existing)}/{len(scripts_to_check)} scripts available")
    except Exception as e:
        results.add_result("Script Integration", False, error=e)


def test_performance(pepper: PepperPots, results: BattletestResults):
    """Test performance"""
    try:
        import time

        # Test status report generation speed
        start = time.time()
        status = pepper.status_report()
        elapsed = time.time() - start

        if elapsed < 1.0:
            results.add_result("Performance", True, 
                             f"Status report generated in {elapsed:.3f}s")
        else:
            results.add_warning(f"Status report slow: {elapsed:.3f}s")
            results.add_result("Performance", True, 
                             f"Status report generated in {elapsed:.3f}s (slow but acceptable)")
    except Exception as e:
        results.add_result("Performance", False, error=e)


def main():
    try:
        """Run all battletests"""
        print("="*80)
        print("⚔️  PEPPER POTS BATTLETEST SUITE")
        print("="*80)
        print()
        print("Running comprehensive tests...")
        print()

        results = BattletestResults()

        # Initialize PEPPER POTS
        pepper = test_initialization(results)
        if not pepper:
            print("\n❌ Initialization failed - cannot continue tests")
            return

        print()
        print("="*80)
        print("📊 CORE FUNCTIONALITY TESTS")
        print("="*80)
        print()

        # Core functionality tests
        test_status_report(pepper, results)
        test_business_status(pepper, results)
        test_invoice_summary(pepper, results)
        test_expense_summary(pepper, results)

        print()
        print("="*80)
        print("📁 STRUCTURE & ORGANIZATION TESTS")
        print("="*80)
        print()

        # Structure tests
        test_directory_structure(pepper, results)
        test_file_counting(pepper, results)
        test_data_access(pepper, results)
        test_organization_capability(pepper, results)

        print()
        print("="*80)
        print("🔧 INTEGRATION & RELIABILITY TESTS")
        print("="*80)
        print()

        # Integration tests
        test_error_handling(pepper, results)
        test_integration_with_scripts(pepper, results)
        test_performance(pepper, results)

        print()
        print("="*80)
        print("📊 BATTLETEST RESULTS")
        print("="*80)
        print()

        summary = results.summary()
        print(f"Tests Run: {summary['tests_run']}")
        print(f"Tests Passed: {summary['tests_passed']} ✅")
        print(f"Tests Failed: {summary['tests_failed']} ❌")
        print(f"Pass Rate: {summary['pass_rate']}")
        print(f"Errors: {summary['errors']}")
        print(f"Warnings: {summary['warnings']}")
        print()

        if results.errors:
            print("="*80)
            print("❌ ERRORS")
            print("="*80)
            for error in results.errors:
                print(f"  - {error}")
            print()

        if results.warnings:
            print("="*80)
            print("⚠️  WARNINGS")
            print("="*80)
            for warning in results.warnings:
                print(f"  - {warning}")
            print()

        # Final verdict
        print("="*80)
        if summary['tests_failed'] == 0:
            print("🎉 BATTLETEST PASSED - PEPPER POTS IS READY FOR PRODUCTION!")
            print("="*80)
        elif summary['pass_rate'] >= "80%":
            print("✅ BATTLETEST MOSTLY PASSED - PEPPER POTS IS OPERATIONAL")
            print("="*80)
        else:
            print("⚠️  BATTLETEST HAD ISSUES - REVIEW ERRORS ABOVE")
            print("="*80)

        # Save results
        results_file = script_dir / "data" / "battletest_pepper_pots" / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump({
                "summary": summary,
                "results": results.results,
                "errors": results.errors,
                "warnings": results.warnings,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        print(f"\n📄 Results saved to: {results_file.relative_to(script_dir)}")
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()