#!/usr/bin/env python3
"""
@ask Ticket Holocron Middleware

Middleware layer using Jupyter notebook server on NAS and @holocrons to validate,
correct, and shape @ask ticket data before database propagation.

Data Flow:
@ask → Jupyter Notebook Server (NAS) → @Holocron Validation/Shaping → Database

Tags: #ASK #HELPDESK #GITLENS #HOLOCRON #MIDDLEWARE #VALIDATION #JUPYTER @JARVIS @LUMINA
"""

import json
import logging
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from ask_ticket_collation_system import AskTicketCollationSystem
from lumina_core.paths import setup_paths

setup_paths()
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

try:
    from lumina_core.logging import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)

    def get_logger(name: str):
        """Fallback logger factory"""
        return logging.getLogger(name)

logger = get_logger("AskTicketHolocronMiddleware")


@dataclass
class ValidationResult:
    """Result of holocron validation"""
    valid: bool
    corrected: bool
    corrections: List[Dict[str, Any]]
    holocron_insights: List[str]
    shaped_data: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = None


@dataclass
class HolocronShape:
    """Holocron data shape/template"""
    shape_id: str
    shape_name: str
    required_fields: List[str]
    field_types: Dict[str, str]
    validation_rules: Dict[str, Any]
    transformation_rules: Dict[str, Any]
    holocron_reference: Optional[str] = None


class AskTicketHolocronMiddleware:
    """
    Middleware using @holocrons to validate and shape @ask ticket data

    Data Flow:
    1. @ask ticket data received
    2. Sent to Jupyter notebook server on NAS for processing
    3. @holocron validation and shaping applied
    4. Data corrected and validated
    5. Propagated to database
    """

    def __init__(
        self,
        root_path: Optional[Path] = None,
        jupyter_nas_url: str = "http://<NAS_PRIMARY_IP>:8888",
        holocron_dir: Optional[Path] = None,
        enable_auto_execution: bool = False
    ):
        """Initialize holocron middleware"""
        if root_path is None:
            from lumina_core.paths import get_project_root
            self.project_root = Path(get_project_root())
        else:
            self.project_root = Path(root_path)

        self.jupyter_nas_url = jupyter_nas_url
        self.collation_system = AskTicketCollationSystem(self.project_root)
        self.enable_auto_execution = enable_auto_execution

        # Holocron directory
        if holocron_dir is None:
            holocron_dir = self.project_root / "data" / "holocron"
        self.holocron_dir = Path(holocron_dir)
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        # Load holocron shapes
        self.holocron_shapes = self._load_holocron_shapes()

        # Initialize auto-executor if enabled
        self.auto_executor = None
        if self.enable_auto_execution:
            try:
                from ask_ticket_auto_executor import AskTicketAutoExecutor
                self.auto_executor = AskTicketAutoExecutor(self.project_root)
                logger.info("   ✅ Auto-executor enabled (Code Cowork-style)")
            except ImportError:
                logger.warning("   ⚠️  Auto-executor not available")

        logger.info("✅ @ask Ticket Holocron Middleware initialized")
        logger.info("   Jupyter NAS URL: %s", self.jupyter_nas_url)
        logger.info("   Holocron directory: %s", self.holocron_dir)
        logger.info("   Loaded %d holocron shapes", len(self.holocron_shapes))

    def _load_holocron_shapes(self) -> Dict[str, HolocronShape]:
        """Load holocron shapes for validation"""
        shapes = {}

        # Default @ask ticket holocron shape
        ask_ticket_shape = HolocronShape(
            shape_id="ask_ticket",
            shape_name="@ask Ticket Data Shape",
            required_fields=["ask_id", "ask_text", "created_at"],
            field_types={
                "ask_id": "str",
                "ask_text": "str",
                "helpdesk_ticket": "str",
                "gitlens_ticket": "str",
                "gitlens_pr": "str",
                "tags": "list",
                "syphon_patterns": "list",
                "assigned_team": "str",
                "status": "str",
                "priority": "str"
            },
            validation_rules={
                "ask_id": {
                    "pattern": r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
                    "required": True
                },
                "ask_text": {
                    "min_length": 5,
                    "max_length": 5000,
                    "required": True
                },
                "helpdesk_ticket": {
                    "pattern": r"^TICKET-\d{8}-\d{4}$",
                    "required": False
                },
                "tags": {
                    "type": "list",
                    "max_items": 50
                }
            },
            transformation_rules={
                "ask_text": {
                    "trim_whitespace": True,
                    "normalize_unicode": True
                },
                "tags": {
                    "lowercase": True,
                    "remove_duplicates": True,
                    "sort": True
                }
            },
            holocron_reference="@holocron/ask_ticket_validation"
        )

        shapes["ask_ticket"] = ask_ticket_shape

        # Load additional shapes from holocron directory
        shapes_file = self.holocron_dir / "ask_ticket_shapes.json"
        if shapes_file.exists():
            try:
                with open(shapes_file, encoding='utf-8') as f:
                    shapes_data = json.load(f)
                    for shape_id, shape_data in shapes_data.items():
                        shapes[shape_id] = HolocronShape(**shape_data)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("⚠️  Error loading holocron shapes: %s", e)

        return shapes

    def _validate_with_holocron(
        self,
        data: Dict[str, Any],
        shape: HolocronShape
    ) -> ValidationResult:
        """
        Validate data using holocron shape

        Args:
            data: Data to validate
            shape: Holocron shape to validate against

        Returns:
            ValidationResult with validation status and corrections
        """
        valid = True
        corrections = []
        validation_errors = []
        holocron_insights = []

        # Check required fields
        for field_name in shape.required_fields:
            if field_name not in data or data[field_name] is None:
                valid = False
                validation_errors.append(f"Missing required field: {field_name}")
                corrections.append({
                    "field": field_name,
                    "action": "add_required",
                    "message": f"Required field {field_name} is missing"
                })

        # Validate field types
        for field_name, expected_type in shape.field_types.items():
            if field_name in data and data[field_name] is not None:
                actual_type = type(data[field_name]).__name__
                if expected_type == "list" and not isinstance(data[field_name], list):
                    valid = False
                    validation_errors.append(
                        f"Field {field_name} should be list, got {actual_type}"
                    )
                    corrections.append({
                        "field": field_name,
                        "action": "convert_type",
                        "from": actual_type,
                        "to": expected_type,
                        "value": [data[field_name]] if data[field_name] else []
                    })
                elif expected_type == "str" and not isinstance(data[field_name], str):
                    valid = False
                    validation_errors.append(
                        f"Field {field_name} should be str, got {actual_type}"
                    )
                    corrections.append({
                        "field": field_name,
                        "action": "convert_type",
                        "from": actual_type,
                        "to": expected_type,
                        "value": str(data[field_name])
                    })

        # Apply validation rules
        for field_name, rules in shape.validation_rules.items():
            if field_name not in data:
                continue

            value = data[field_name]

            # Pattern validation
            if "pattern" in rules:
                if not re.match(rules["pattern"], str(value)):
                    valid = False
                    validation_errors.append(f"Field {field_name} does not match pattern")
                    corrections.append({
                        "field": field_name,
                        "action": "fix_pattern",
                        "message": f"Field {field_name} needs pattern correction"
                    })

            # Length validation
            if "min_length" in rules and len(str(value)) < rules["min_length"]:
                valid = False
                validation_errors.append(
                    f"Field {field_name} is too short (min: {rules['min_length']})"
                )

            if "max_length" in rules and len(str(value)) > rules["max_length"]:
                valid = False
                validation_errors.append(
                    f"Field {field_name} is too long (max: {rules['max_length']})"
                )
                corrections.append({
                    "field": field_name,
                    "action": "truncate",
                    "max_length": rules["max_length"],
                    "value": str(value)[:rules["max_length"]]
                })

        # Holocron insights
        holocron_insights.append(f"Validated against @holocron shape: {shape.shape_name}")
        if shape.holocron_reference:
            holocron_insights.append(f"Holocron reference: {shape.holocron_reference}")

        return ValidationResult(
            valid=valid,
            corrected=len(corrections) > 0,
            corrections=corrections,
            holocron_insights=holocron_insights,
            validation_errors=validation_errors
        )

    def _shape_with_holocron(
        self,
        data: Dict[str, Any],
        shape: HolocronShape
    ) -> Dict[str, Any]:
        """
        Shape data using holocron transformation rules

        Args:
            data: Data to shape
            shape: Holocron shape with transformation rules

        Returns:
            Shaped data dictionary
        """
        shaped_data = data.copy()

        # Apply transformation rules
        for field_name, rules in shape.transformation_rules.items():
            if field_name not in shaped_data:
                continue

            value = shaped_data[field_name]

            # Trim whitespace
            if rules.get("trim_whitespace") and isinstance(value, str):
                shaped_data[field_name] = value.strip()

            # Normalize unicode
            if rules.get("normalize_unicode") and isinstance(value, str):
                shaped_data[field_name] = unicodedata.normalize('NFKC', value)

            # Lowercase
            if rules.get("lowercase") and isinstance(value, (str, list)):
                if isinstance(value, str):
                    shaped_data[field_name] = value.lower()
                elif isinstance(value, list):
                    shaped_data[field_name] = [
                        item.lower() if isinstance(item, str) else item
                        for item in value
                    ]

            # Remove duplicates
            if rules.get("remove_duplicates") and isinstance(value, list):
                seen = set()
                unique_list = []
                for item in value:
                    item_key = (tuple(item) if isinstance(item, (list, dict))
                                else item)
                    if item_key not in seen:
                        seen.add(item_key)
                        unique_list.append(item)
                shaped_data[field_name] = unique_list

            # Sort
            if rules.get("sort") and isinstance(value, list):
                shaped_data[field_name] = sorted(value)

        return shaped_data

    def _apply_corrections(
        self,
        data: Dict[str, Any],
        corrections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply corrections to data"""
        corrected_data = data.copy()

        for correction in corrections:
            field_name = correction["field"]
            action = correction["action"]

            if action == "add_required":
                # Add default value for required field
                if field_name == "created_at":
                    corrected_data[field_name] = datetime.now().isoformat()
                elif field_name == "status":
                    corrected_data[field_name] = "pending"
                elif field_name == "priority":
                    corrected_data[field_name] = "medium"
                else:
                    corrected_data[field_name] = ""

            elif action == "convert_type":
                corrected_data[field_name] = correction.get("value")

            elif action == "fix_pattern":
                # Try to fix pattern (e.g., add TICKET- prefix)
                if (field_name == "helpdesk_ticket" and
                    not str(corrected_data[field_name]).startswith("TICKET-")):
                    corrected_data[field_name] = f"TICKET-{corrected_data[field_name]}"

            elif action == "truncate":
                corrected_data[field_name] = correction.get("value")

        return corrected_data

    def _consult_holocron(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Consult @holocron for insights and validation rules"""
        insights = []

        # Check if holocron query system exists
        try:
            from holocron_query import HolocronQueryEngine
            engine = HolocronQueryEngine(self.project_root)
            results = engine.query(query, context=context)

            for result in results:
                insights.append(f"@holocron: {result.entry.title}")
        except ImportError:
            # Fallback: use local holocron directory
            holocron_files = list(self.holocron_dir.glob("*.json"))
            if holocron_files:
                msg = f"@holocron: Found {len(holocron_files)} holocron entries"
                insights.append(msg)

        return insights

    def _process_via_jupyter(self, data: Dict[str, Any]) -> None:
        """
        Process data via Jupyter notebook server on NAS

        This is a placeholder for actual Jupyter integration.

        Args:
            data: Data dictionary to process (currently unused)
        """
        # INFO: Jupyter notebook server integration is planned for future implementation
        _ = data  # Suppress unused argument warning
        # Placeholder: In production, this would connect to Jupyter server
        # For now, just check availability
        # INFO: Jupyter notebook server integration is pending

        try:
            # Check if Jupyter server is available
            response = requests.get(self.jupyter_nas_url + "/api", timeout=2)
            if response.status_code == 200:
                logger.info("   ✅ Jupyter notebook server available at %s",
                            self.jupyter_nas_url)
                # INFO: Data transmission to Jupyter is pending
        except requests.RequestException as e:
            logger.debug("   Jupyter server not available: %s", e)

        return None

    def process_through_middleware(
        self,
        ask_id: str,
        ask_text: str,
        helpdesk_ticket: Optional[str] = None,
        gitlens_ticket: Optional[str] = None,
        gitlens_pr: Optional[str] = None,
        source: str = "user_report"
    ) -> Tuple[None, ValidationResult]:
        """Process @ask ticket through middleware (Jupyter NAS + @holocron)"""
        logger.info("🔄 Processing @ask through middleware: %s", ask_id)

        # Step 1: Prepare data
        raw_data = {
            "ask_id": ask_id,
            "ask_text": ask_text,
            "helpdesk_ticket": helpdesk_ticket,
            "gitlens_ticket": gitlens_ticket,
            "gitlens_pr": gitlens_pr,
            "source": source,
            "created_at": datetime.now().isoformat()
        }

        # Step 2: Send to Jupyter notebook server on NAS (if available)
        self._process_via_jupyter(raw_data)

        # Step 3: Get holocron shape
        shape = self.holocron_shapes.get("ask_ticket")
        if not shape:
            logger.warning("⚠️  No holocron shape found, using default validation")
            shape = self.holocron_shapes["ask_ticket"]

        # Step 4: Validate with @holocron
        validation_result = self._validate_with_holocron(raw_data, shape)

        # Step 5: Apply corrections if needed
        if validation_result.corrected:
            logger.info("   🔧 Applying %d corrections", len(validation_result.corrections))
            raw_data = self._apply_corrections(raw_data, validation_result.corrections)
            # Re-validate after corrections
            validation_result = self._validate_with_holocron(raw_data, shape)

        # Step 6: Shape data with @holocron
        shaped_data = self._shape_with_holocron(raw_data, shape)
        validation_result.shaped_data = shaped_data

        # Step 7: Consult @holocron for additional insights
        holocron_insights = self._consult_holocron(
            f"@ask ticket validation for {ask_id}",
            {"ask_text": ask_text, "tags": shaped_data.get("tags", [])}
        )
        validation_result.holocron_insights.extend(holocron_insights)

        # Step 8: Collate and propagate to database
        if validation_result.valid:
            self.collation_system.collate_ask(
                ask_id=shaped_data["ask_id"],
                ask_text=shaped_data["ask_text"],
                helpdesk_ticket=shaped_data.get("helpdesk_ticket"),
                gitlens_ticket=shaped_data.get("gitlens_ticket"),
                gitlens_pr=shaped_data.get("gitlens_pr"),
                source=shaped_data.get("source", source)
            )

            # Step 9: Auto-execute if enabled (Code Cowork-style)
            if self.enable_auto_execution and self.auto_executor:
                try:
                    logger.info("🚀 Auto-executing validated @ask: %s", ask_id)
                    tickets = self.collation_system.query(ask_id=ask_id)
                    if tickets:
                        execution_result = self.auto_executor.execute_ticket(tickets[0])
                        validation_result.holocron_insights.append(
                            f"Auto-execution: {execution_result.status.value}"
                        )
                        if execution_result.error:
                            validation_result.holocron_insights.append(
                                f"Execution error: {execution_result.error}"
                            )
                except (ValueError, TypeError, AttributeError, KeyError) as e:
                    logger.error("❌ Auto-execution failed: %s", e)
                    validation_result.holocron_insights.append(
                        f"Auto-execution error: {str(e)}"
                    )

            logger.info("✅ Processed and propagated to database: %s", ask_id)
            logger.info("   Valid: %s", validation_result.valid)
            logger.info("   Corrected: %s", validation_result.corrected)
            logger.info("   Holocron insights: %d",
                        len(validation_result.holocron_insights))

            return None, validation_result

        logger.error("❌ Validation failed for @ask: %s", ask_id)
        logger.error("   Errors: %s", validation_result.validation_errors)
        raise ValueError(f"Validation failed: {validation_result.validation_errors}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="@ask Ticket Holocron Middleware - Validate and shape data before database"
    )
    parser.add_argument("--process", nargs=5,
                       metavar=("ASK_ID", "ASK_TEXT", "HELPDESK", "GITLENS_TICKET", "GITLENS_PR"),
                       help="Process @ask through middleware")
    parser.add_argument("--jupyter-url", default="http://<NAS_PRIMARY_IP>:8888",
                       help="Jupyter notebook server URL")

    args = parser.parse_args()

    middleware = AskTicketHolocronMiddleware(jupyter_nas_url=args.jupyter_url)

    if args.process:
        ask_id, ask_text, helpdesk, gitlens_ticket, gitlens_pr = args.process
        try:
            _, val = middleware.process_through_middleware(
                ask_id=ask_id,
                ask_text=ask_text,
                helpdesk_ticket=helpdesk if helpdesk != "None" else None,
                gitlens_ticket=gitlens_ticket if gitlens_ticket != "None" else None,
                gitlens_pr=gitlens_pr if gitlens_pr != "None" else None
            )

            print("\n✅ Processed through middleware:")
            print(f"   Ask ID: {ask_id}")
            print(f"   Valid: {val.valid}")
            print(f"   Corrected: {val.corrected}")
            print(f"   Corrections: {len(val.corrections)}")
            print(f"   Holocron insights: {len(val.holocron_insights)}")

            if val.corrections:
                print("\n   Corrections applied:")
                for correction in val.corrections:
                    print(f"     - {correction['field']}: {correction['action']}")

            if val.holocron_insights:
                print("\n   @Holocron insights:")
                for insight in val.holocron_insights:
                    print(f"     - {insight}")
        except (ValueError, requests.RequestException) as e:
            print(f"\n❌ Error: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()