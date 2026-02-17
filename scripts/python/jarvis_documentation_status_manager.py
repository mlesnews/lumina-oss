#!/usr/bin/env python3
"""
JARVIS Documentation Status Manager

Manages documentation completion status for workflows, tickets, and areas.
Documentation must be complete and successful before automatic archiving.

Tags: #DOCUMENTATION #WORKFLOW #HELPDESK #FINTECH
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDocsManager")


class DocumentationStatusManager:
    """Manages documentation completion status"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.docs_status_dir = project_root / "data" / "documentation_status"
        self.docs_status_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Documentation Status Manager initialized")

    def mark_complete(self, item_id: str, item_type: str = "agent",
                         required_docs: Optional[List[str]] = None,
                         completed_docs: Optional[List[str]] = None,
                         verified_by: str = "JARVIS") -> Dict[str, Any]:
        try:
            """Mark documentation as complete and successful"""
            status_file = self.docs_status_dir / f"{item_type}_{item_id}_docs.json"

            required = required_docs or []
            completed = completed_docs or required

            status_data = {
                "item_id": item_id,
                "item_type": item_type,
                "status": "complete",
                "all_successful": True,
                "has_issues": False,
                "issues": [],
                "completed_at": datetime.now().isoformat(),
                "verified_by": verified_by,
                "required_docs": required,
                "completed_docs": completed,
                "missing_docs": [],
                "failed_docs": []
            }

            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Marked documentation complete for {item_type} {item_id}")
            return status_data

        except Exception as e:
            logger.error(f"Error in mark_complete: {e}", exc_info=True)
            raise

    def mark_incomplete(self, item_id: str, item_type: str = "agent",
                           missing_docs: Optional[List[str]] = None,
                           failed_docs: Optional[List[str]] = None,
                           issues: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            """Mark documentation as incomplete or with issues"""
            status_file = self.docs_status_dir / f"{item_type}_{item_id}_docs.json"

            status_data = {
                "item_id": item_id,
                "item_type": item_type,
                "status": "incomplete",
                "all_successful": False,
                "has_issues": True,
                "issues": issues or [],
                "updated_at": datetime.now().isoformat(),
                "missing_docs": missing_docs or [],
                "failed_docs": failed_docs or []
            }

            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ⚠️  Marked documentation incomplete for {item_type} {item_id}")
            return status_data

        except Exception as e:
            logger.error(f"Error in mark_incomplete: {e}", exc_info=True)
            raise

    def add_issue(self, item_id: str, issue: str, item_type: str = "agent") -> Dict[str, Any]:
        try:
            """Add an issue to documentation status"""
            status_file = self.docs_status_dir / f"{item_type}_{item_id}_docs.json"

            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
            else:
                status_data = {
                    "item_id": item_id,
                    "item_type": item_type,
                    "status": "incomplete",
                    "all_successful": False,
                    "has_issues": True,
                    "issues": [],
                    "missing_docs": [],
                    "failed_docs": []
                }

            if issue not in status_data["issues"]:
                status_data["issues"].append(issue)

            status_data["has_issues"] = True
            status_data["all_successful"] = False
            status_data["status"] = "incomplete"
            status_data["updated_at"] = datetime.now().isoformat()

            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ⚠️  Added issue to {item_type} {item_id}: {issue}")
            return status_data

        except Exception as e:
            self.logger.error(f"Error in add_issue: {e}", exc_info=True)
            raise
    def get_status(self, item_id: str, item_type: str = "agent") -> Optional[Dict]:
        """Get documentation status"""
        status_file = self.docs_status_dir / f"{item_type}_{item_id}_docs.json"

        if not status_file.exists():
            return None

        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Documentation Status Manager")
        parser.add_argument("--complete", type=str,
                           help="Mark documentation complete (format: ITEM_ID:TYPE)")
        parser.add_argument("--incomplete", type=str,
                           help="Mark documentation incomplete (format: ITEM_ID:TYPE)")
        parser.add_argument("--add-issue", type=str,
                           help="Add issue (format: ITEM_ID:TYPE:ISSUE)")
        parser.add_argument("--status", type=str,
                           help="Get documentation status (format: ITEM_ID:TYPE)")
        parser.add_argument("--docs", type=str, nargs="+",
                           help="List of required/completed documentation files")

        args = parser.parse_args()

        manager = DocumentationStatusManager()

        if args.complete:
            parts = args.complete.split(":")
            item_id = parts[0]
            item_type = parts[1] if len(parts) > 1 else "agent"
            result = manager.mark_complete(item_id, item_type, completed_docs=args.docs)
            print(json.dumps(result, indent=2))
        elif args.incomplete:
            parts = args.incomplete.split(":")
            item_id = parts[0]
            item_type = parts[1] if len(parts) > 1 else "agent"
            result = manager.mark_incomplete(item_id, item_type, missing_docs=args.docs)
            print(json.dumps(result, indent=2))
        elif args.add_issue:
            parts = args.add_issue.split(":", 2)
            item_id = parts[0]
            item_type = parts[1] if len(parts) > 1 else "agent"
            issue = parts[2] if len(parts) > 2 else "Issue detected"
            result = manager.add_issue(item_id, item_type, issue)
            print(json.dumps(result, indent=2))
        elif args.status:
            parts = args.status.split(":")
            item_id = parts[0]
            item_type = parts[1] if len(parts) > 1 else "agent"
            result = manager.get_status(item_id, item_type)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"No documentation status found for {item_type} {item_id}")
        else:
            parser.print_help()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())