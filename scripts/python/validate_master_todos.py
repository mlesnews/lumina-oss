#!/usr/bin/env python3
"""
Master TODO List Validator

Validates completed items in the master TODO list.
Works forwards or backwards through the list.
Focuses on business needs.

Tags: #TODO #VALIDATION #BUSINESS_NEEDS @JARVIS @LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("MasterTODOValidator")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MasterTODOValidator")


class MasterTODOValidator:
    """
    Validates completed items in master TODO list

    Can work forwards or backwards through the list.
    Focuses on business needs and priority.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        self.master_todos_file = self.project_root / "data" / "todo" / "master_todos.json"

        logger.info("=" * 80)
        logger.info("📋 MASTER TODO LIST VALIDATOR")
        logger.info("=" * 80)
        logger.info("   Validating completed items")
        logger.info("   Working forwards or backwards")
        logger.info("   Focus: Business needs")
        logger.info("")

    def load_master_todos(self) -> List[Dict[str, Any]]:
        """Load master todos from One Ring Blueprint"""
        todos = []

        # Try One Ring Blueprint first
        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)
                    todos = blueprint.get("master_todos", [])
                logger.info(f"✅ Loaded {len(todos)} todos from One Ring Blueprint")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load from blueprint: {e}")

        # Fallback to dedicated file
        if not todos and self.master_todos_file.exists():
            try:
                with open(self.master_todos_file, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                logger.info(f"✅ Loaded {len(todos)} todos from master_todos.json")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load from master_todos.json: {e}")

        return todos

    def validate_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single TODO item

        Checks if completed items are actually done.
        """
        validation = {
            "id": item.get("id", "unknown"),
            "content": item.get("content", ""),
            "status": item.get("status", "unknown"),
            "category": item.get("category", "unknown"),
            "priority": item.get("priority", "unknown"),
            "validated": False,
            "validation_method": None,
            "validation_result": None,
            "issues": [],
            "notes": []
        }

        status = item.get("status", "").lower()

        # Only validate completed items
        if status not in ["completed", "done", "finished"]:
            validation["validated"] = False
            validation["validation_result"] = "Not completed - skipping validation"
            return validation

        logger.info(f"   🔍 Validating: {item.get('id')} - {item.get('content', '')[:60]}...")

        # Validation methods based on category
        category = item.get("category", "").lower()

        if "communication" in category:
            validation = self._validate_communication(item, validation)
        elif "ai_development" in category or "development" in category:
            validation = self._validate_development(item, validation)
        elif "infrastructure" in category or "system" in category:
            validation = self._validate_infrastructure(item, validation)
        elif "security" in category:
            validation = self._validate_security(item, validation)
        else:
            validation = self._validate_generic(item, validation)

        return validation

    def _validate_communication(self, item: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Validate communication-related items"""
            content = item.get("content", "").lower()

            # Check for configuration files
            if "email" in content or "imap" in content or "oauth" in content:
                # Check if n8n workflows exist
                n8n_dir = self.project_root / "data" / "n8n"
                if n8n_dir.exists():
                    validation["notes"].append("n8n directory exists")

                # Check for credential storage
                if "azure" in content or "key vault" in content:
                    validation["notes"].append("Should use Azure Key Vault for credentials")

            if "sms" in content or "elevenlabs" in content:
                # Check for ElevenLabs SMS configuration
                elevenlabs_config = self.project_root / "config" / "elevenlabs_config.json"
                if elevenlabs_config.exists():
                    validation["validated"] = True
                    validation["validation_method"] = "config_file_exists"
                    validation["validation_result"] = "ElevenLabs config file found"
                else:
                    validation["issues"].append("ElevenLabs config file not found")

            if "telegram" in content or "discord" in content or "whatsapp" in content:
                # Check for bot configuration
                validation["notes"].append("Bot configuration should be in n8n or config directory")

            return validation

        except Exception as e:
            self.logger.error(f"Error in _validate_communication: {e}", exc_info=True)
            raise
    def _validate_development(self, item: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Validate development-related items"""
            content = item.get("content", "").lower()

            # Check for code files
            if "system" in content or "module" in content or "script" in content:
                # Try to find related files
                scripts_dir = self.project_root / "scripts" / "python"
                if scripts_dir.exists():
                    # Search for related files
                    related_files = list(scripts_dir.glob(f"*{content.split()[0]}*.py"))
                    if related_files:
                        validation["validated"] = True
                        validation["validation_method"] = "code_file_exists"
                        validation["validation_result"] = f"Found {len(related_files)} related files"
                    else:
                        validation["issues"].append("No related code files found")

            # Check for database/storage
            if "database" in content or "storage" in content or "schema" in content:
                data_dir = self.project_root / "data"
                if data_dir.exists():
                    validation["notes"].append("Data directory exists")

            return validation

        except Exception as e:
            self.logger.error(f"Error in _validate_development: {e}", exc_info=True)
            raise
    def _validate_infrastructure(self, item: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Validate infrastructure-related items"""
            content = item.get("content", "").lower()

            # Check for deployment files
            if "deploy" in content or "docker" in content:
                docker_dir = self.project_root / "docker"
                if docker_dir.exists():
                    validation["notes"].append("Docker directory exists")

            # Check for configuration
            if "config" in content or "setup" in content:
                config_dir = self.project_root / "config"
                if config_dir.exists():
                    validation["notes"].append("Config directory exists")

            return validation

        except Exception as e:
            self.logger.error(f"Error in _validate_infrastructure: {e}", exc_info=True)
            raise
    def _validate_security(self, item: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Validate security-related items"""
            content = item.get("content", "").lower()

            # Security items should have documentation
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                validation["notes"].append("Documentation directory exists")

            # Check for Azure Key Vault usage
            if "credential" in content or "secret" in content or "password" in content:
                validation["notes"].append("Should use Azure Key Vault for secrets")

            return validation

        except Exception as e:
            self.logger.error(f"Error in _validate_security: {e}", exc_info=True)
            raise
    def _validate_generic(self, item: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generic validation for items without specific category"""
        # Check if item has subtasks
        subtasks = item.get("subtasks", [])
        if subtasks:
            completed_subtasks = [st for st in subtasks if st.get("status", "").lower() in ["completed", "done"]]
            if len(completed_subtasks) == len(subtasks):
                validation["validated"] = True
                validation["validation_method"] = "all_subtasks_completed"
                validation["validation_result"] = f"All {len(subtasks)} subtasks completed"
            else:
                validation["issues"].append(f"Only {len(completed_subtasks)}/{len(subtasks)} subtasks completed")
        else:
            # No subtasks - mark as validated if status is completed
            validation["validated"] = True
            validation["validation_method"] = "status_check"
            validation["validation_result"] = "Status marked as completed"

        return validation

    def validate_all(
        self,
        direction: str = "forwards",
        priority_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate all completed items

        Args:
            direction: "forwards" or "backwards"
            priority_filter: Filter by priority ("high", "medium", "low")
            category_filter: Filter by category
        """
        todos = self.load_master_todos()

        if not todos:
            logger.error("❌ No todos found")
            return {"error": "No todos found"}

        logger.info(f"📋 Found {len(todos)} master todos")
        logger.info("")

        # Filter by priority (business needs)
        if priority_filter:
            todos = [t for t in todos if t.get("priority", "").lower() == priority_filter.lower()]
            logger.info(f"   Filtered to {len(todos)} {priority_filter}-priority todos")

        # Filter by category
        if category_filter:
            todos = [t for t in todos if category_filter.lower() in t.get("category", "").lower()]
            logger.info(f"   Filtered to {len(todos)} todos in category: {category_filter}")

        # Sort by direction
        if direction == "backwards":
            todos = list(reversed(todos))
            logger.info("   Working backwards through list")
        else:
            logger.info("   Working forwards through list")

        logger.info("")

        # Find completed items (top-level)
        completed_items = [t for t in todos if t.get("status", "").lower() in ["completed", "done", "finished"]]

        # Find completed subtasks
        completed_subtasks = []
        for item in todos:
            subtasks = item.get("subtasks", [])
            for subtask in subtasks:
                if subtask.get("status", "").lower() in ["completed", "done", "finished"]:
                    completed_subtasks.append({
                        "parent_id": item.get("id"),
                        "parent_content": item.get("content", ""),
                        "subtask": subtask
                    })

        logger.info(f"✅ Found {len(completed_items)} completed top-level items")
        logger.info(f"✅ Found {len(completed_subtasks)} completed subtasks")
        logger.info("")

        # Validate each completed item
        validations = []
        for item in completed_items:
            validation = self.validate_item(item)
            validations.append(validation)

        # Validate completed subtasks
        subtask_validations = []
        for st_info in completed_subtasks:
            subtask = st_info["subtask"]
            validation = self.validate_item(subtask)
            validation["parent_id"] = st_info["parent_id"]
            validation["parent_content"] = st_info["parent_content"]
            subtask_validations.append(validation)

        # Summary
        validated_count = sum(1 for v in validations if v.get("validated", False))
        issues_count = sum(len(v.get("issues", [])) for v in validations)

        subtask_validated_count = sum(1 for v in subtask_validations if v.get("validated", False))
        subtask_issues_count = sum(len(v.get("issues", [])) for v in subtask_validations)

        total_completed = len(completed_items) + len(completed_subtasks)
        total_validated = validated_count + subtask_validated_count
        total_issues = issues_count + subtask_issues_count

        result = {
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "priority_filter": priority_filter,
            "category_filter": category_filter,
            "total_todos": len(todos),
            "completed_items": len(completed_items),
            "completed_subtasks": len(completed_subtasks),
            "validated_count": validated_count,
            "subtask_validated_count": subtask_validated_count,
            "issues_count": issues_count,
            "subtask_issues_count": subtask_issues_count,
            "validations": validations,
            "subtask_validations": subtask_validations,
            "summary": {
                "total_completed": total_completed,
                "total_validated": total_validated,
                "total_issues": total_issues,
                "validation_rate": f"{(total_validated/total_completed*100):.1f}%" if total_completed > 0 else "0%"
            }
        }

        # Print summary
        logger.info("=" * 80)
        logger.info("📊 VALIDATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Total Completed Items: {len(completed_items)}")
        logger.info(f"   Total Completed Subtasks: {len(completed_subtasks)}")
        logger.info(f"   Total Completed: {total_completed}")
        logger.info(f"   Validated: {total_validated}")
        logger.info(f"   With Issues: {total_issues}")
        logger.info(f"   Validation Rate: {result['summary']['validation_rate']}")
        logger.info("")

        # Print completed subtasks
        if completed_subtasks:
            logger.info("📋 COMPLETED SUBTASKS:")
            logger.info("")
            for st_info in completed_subtasks:
                subtask = st_info["subtask"]
                logger.info(f"   ✅ {st_info['parent_id']} → {subtask.get('id')}: {subtask.get('content', '')[:60]}...")
            logger.info("")

        # Print issues
        if total_issues > 0:
            logger.info("⚠️  ITEMS WITH ISSUES:")
            logger.info("")
            for validation in validations + subtask_validations:
                if validation.get("issues"):
                    parent_info = f"({validation.get('parent_id', 'N/A')})" if validation.get("parent_id") else ""
                    logger.info(f"   {validation['id']} {parent_info}: {validation['content'][:60]}...")
                    for issue in validation.get("issues", []):
                        logger.info(f"      - {issue}")
            logger.info("")

        return result

    def save_validation_report(self, result: Dict[str, Any]) -> Path:
        """Save validation report to file"""
        reports_dir = self.project_root / "data" / "todo_validation"
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"validation_report_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"📁 Validation report saved: {report_file}")

        return report_file


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate master TODO list")
    parser.add_argument("--direction", choices=["forwards", "backwards"], default="forwards",
                       help="Direction to process list")
    parser.add_argument("--priority", choices=["high", "medium", "low"],
                       help="Filter by priority (business needs)")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--save", action="store_true", help="Save validation report")

    args = parser.parse_args()

    validator = MasterTODOValidator()

    result = validator.validate_all(
        direction=args.direction,
        priority_filter=args.priority,
        category_filter=args.category
    )

    if args.save:
        validator.save_validation_report(result)

    return result


if __name__ == "__main__":

    main()