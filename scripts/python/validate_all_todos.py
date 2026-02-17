#!/usr/bin/env python3
"""
Validate All TODOs - Compare Ask Stack to Master/Padawan TODO Lists

Reviews entire ask stack and compares to master to-do list and Padawan to-do list
to find what's been done and what's not been done. Things not validated/verified
as working are considered incomplete.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ValidateTodos")


class TodoValidator:
    """
    Validates all TODOs by comparing ask stack to master/Padawan TODO lists

    Identifies:
    - What's been done
    - What's not been done
    - What's not been validated/verified as working
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.ask_stack_file = self.project_root / "data" / "ask_heap_stack" / "ask_heap_stack.json"
        self.master_padawan_file = self.project_root / "data" / "ask_database" / "master_padawan_todos.json"
        self.master_todos_file = self.project_root / "data" / "todo" / "master_todos.json"

        self.ask_stack = {}
        self.master_padawan_todos = {}
        self.master_todos = {}

        self.validation_results = {
            "completed": [],
            "in_progress": [],
            "pending": [],
            "not_validated": [],
            "broken": [],
            "partial": []
        }

    def load_data(self):
        """Load all TODO and ask stack data"""
        logger.info("📂 Loading data files...")

        # Load ask stack
        if self.ask_stack_file.exists():
            try:
                with open(self.ask_stack_file, 'r', encoding='utf-8') as f:
                    self.ask_stack = json.load(f)
                logger.info(f"   ✅ Loaded ask stack: {len(self.ask_stack)} entries")
            except Exception as e:
                logger.error(f"   ❌ Failed to load ask stack: {e}")
        else:
            logger.warning(f"   ⚠️  Ask stack not found: {self.ask_stack_file}")

        # Load master/Padawan TODOs
        if self.master_padawan_file.exists():
            try:
                with open(self.master_padawan_file, 'r', encoding='utf-8') as f:
                    self.master_padawan_todos = json.load(f)
                logger.info(f"   ✅ Loaded master/Padawan TODOs: {len(self.master_padawan_todos)} entries")
            except Exception as e:
                logger.error(f"   ❌ Failed to load master/Padawan TODOs: {e}")
        else:
            logger.warning(f"   ⚠️  Master/Padawan TODOs not found: {self.master_padawan_file}")

        # Load master TODOs
        if self.master_todos_file.exists():
            try:
                with open(self.master_todos_file, 'r', encoding='utf-8') as f:
                    self.master_todos = json.load(f)
                logger.info(f"   ✅ Loaded master TODOs: {len(self.master_todos)} entries")
            except Exception as e:
                logger.error(f"   ❌ Failed to load master TODOs: {e}")
        else:
            logger.warning(f"   ⚠️  Master TODOs not found: {self.master_todos_file}")

    def validate_todos(self):
        """Validate all TODOs and categorize them"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("🔍 Validating All TODOs")
        logger.info("=" * 70)

        # Check master/Padawan TODOs
        for todo_id, todo in self.master_padawan_todos.items():
            master_status = todo.get("master_status", "unknown")
            padawan_status = todo.get("padawan_status", "unknown")

            # Determine overall status
            if master_status == "complete" and padawan_status == "complete":
                self.validation_results["completed"].append({
                    "id": todo_id,
                    "master": todo.get("master_todo", ""),
                    "padawan": todo.get("padawan_todo", ""),
                    "status": "complete"
                })
            elif master_status == "complete" and padawan_status in ["in_progress", "pending"]:
                self.validation_results["partial"].append({
                    "id": todo_id,
                    "master": todo.get("master_todo", ""),
                    "padawan": todo.get("padawan_todo", ""),
                    "status": "partial",
                    "issue": "Master complete but Padawan not"
                })
            elif master_status in ["in_progress", "pending"]:
                self.validation_results["in_progress"].append({
                    "id": todo_id,
                    "master": todo.get("master_todo", ""),
                    "padawan": todo.get("padawan_todo", ""),
                    "status": master_status
                })
            else:
                self.validation_results["pending"].append({
                    "id": todo_id,
                    "master": todo.get("master_todo", ""),
                    "padawan": todo.get("padawan_todo", ""),
                    "status": "pending"
                })

        # Check master TODOs
        for todo_id, todo in self.master_todos.items():
            status = todo.get("status", "unknown")

            if status == "complete":
                # Check if validated
                if not todo.get("completed_date"):
                    self.validation_results["not_validated"].append({
                        "id": todo_id,
                        "title": todo.get("title", ""),
                        "status": "complete_but_not_validated"
                    })
                else:
                    self.validation_results["completed"].append({
                        "id": todo_id,
                        "title": todo.get("title", ""),
                        "status": "complete"
                    })
            elif status == "in_progress":
                self.validation_results["in_progress"].append({
                    "id": todo_id,
                    "title": todo.get("title", ""),
                    "status": "in_progress"
                })
            elif status == "pending":
                self.validation_results["pending"].append({
                    "id": todo_id,
                    "title": todo.get("title", ""),
                    "status": "pending"
                })

    def identify_broken_items(self):
        """Identify broken/partial implementations"""
        logger.info("")
        logger.info("🔍 Identifying broken/partial items...")

        # Check for items marked complete but with issues
        for todo_id, todo in self.master_todos.items():
            if todo.get("status") == "complete":
                # Check for notes indicating issues
                notes = todo.get("notes", [])
                for note in notes:
                    if any(keyword in note.lower() for keyword in ["broken", "not working", "fix", "issue", "error"]):
                        self.validation_results["broken"].append({
                            "id": todo_id,
                            "title": todo.get("title", ""),
                            "issue": note
                        })

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "completed": len(self.validation_results["completed"]),
                "in_progress": len(self.validation_results["in_progress"]),
                "pending": len(self.validation_results["pending"]),
                "not_validated": len(self.validation_results["not_validated"]),
                "broken": len(self.validation_results["broken"]),
                "partial": len(self.validation_results["partial"])
            },
            "details": self.validation_results
        }

        return report

    def print_report(self):
        """Print validation report"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 Validation Report")
        logger.info("=" * 70)

        summary = {
            "completed": len(self.validation_results["completed"]),
            "in_progress": len(self.validation_results["in_progress"]),
            "pending": len(self.validation_results["pending"]),
            "not_validated": len(self.validation_results["not_validated"]),
            "broken": len(self.validation_results["broken"]),
            "partial": len(self.validation_results["partial"])
        }

        logger.info("")
        logger.info("Summary:")
        logger.info(f"   ✅ Completed: {summary['completed']}")
        logger.info(f"   🔄 In Progress: {summary['in_progress']}")
        logger.info(f"   ⏳ Pending: {summary['pending']}")
        logger.info(f"   ⚠️  Not Validated: {summary['not_validated']}")
        logger.info(f"   ❌ Broken: {summary['broken']}")
        logger.info(f"   🔧 Partial: {summary['partial']}")

        # Show broken items
        if self.validation_results["broken"]:
            logger.info("")
            logger.info("❌ Broken Items (need fixing):")
            for item in self.validation_results["broken"][:10]:  # Show first 10
                logger.info(f"   - {item['id']}: {item['title']}")
                logger.info(f"     Issue: {item.get('issue', 'Unknown')}")

        # Show partial items
        if self.validation_results["partial"]:
            logger.info("")
            logger.info("🔧 Partial Items (need completion):")
            for item in self.validation_results["partial"][:10]:  # Show first 10
                logger.info(f"   - {item['id']}: {item.get('master', item.get('title', ''))}")
                logger.info(f"     Issue: {item.get('issue', 'Unknown')}")

        # Show not validated items
        if self.validation_results["not_validated"]:
            logger.info("")
            logger.info("⚠️  Not Validated (need verification):")
            for item in self.validation_results["not_validated"][:10]:  # Show first 10
                logger.info(f"   - {item['id']}: {item.get('title', '')}")

        logger.info("")
        logger.info("=" * 70)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Validate All TODOs")
        parser.add_argument("--save-report", action="store_true", help="Save report to file")

        args = parser.parse_args()

        validator = TodoValidator(project_root)
        validator.load_data()
        validator.validate_todos()
        validator.identify_broken_items()
        validator.print_report()

        if args.save_report:
            report = validator.generate_report()
            report_file = project_root / "data" / f"todo_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"")
            logger.info(f"📄 Report saved to: {report_file}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())