#!/usr/bin/env python3
"""
System Validator
Comprehensive system validation

Validates all components, integrations, and system health.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SystemValidator")


class SystemValidator:
    """Validates entire system"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.validation_results: List[Dict[str, Any]] = []

    def validate_component(self, component_name: str, validation_func: callable) -> Dict[str, Any]:
        """Validate a component"""
        try:
            result = validation_func()
            self.validation_results.append({
                "component": component_name,
                "status": "pass" if result else "fail",
                "timestamp": datetime.now().isoformat()
            })
            return {"component": component_name, "status": "pass" if result else "fail"}
        except Exception as e:
            self.validation_results.append({
                "component": component_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return {"component": component_name, "status": "error", "error": str(e)}

    def validate_database(self) -> bool:
        """Validate database connection"""
        try:
            from database_connection_manager import get_db_manager
            db_manager = get_db_manager(self.project_root)
            conn = db_manager.get_connection()
            db_manager.return_connection(conn)
            return True
        except Exception:
            return False

    def validate_service_bus(self) -> bool:
        """Validate Service Bus connection"""
        try:
            from azure_service_bus_integration import get_service_bus_client, get_key_vault_client
            kv_client = get_key_vault_client()
            sb_client = get_service_bus_client(key_vault_client=kv_client)
            return sb_client is not None
        except Exception:
            return False

    def validate_key_vault(self) -> bool:
        """Validate Key Vault connection"""
        try:
            from azure_service_bus_integration import get_key_vault_client
            kv_client = get_key_vault_client()
            secrets = kv_client.list_secrets()
            return True
        except Exception:
            return False

    def validate_api_services(self) -> bool:
        """Validate all API services"""
        services = [
            "api_authentication_service",
            "api_workflow_service",
            "api_chat_service",
            "api_r5_service",
            "api_helpdesk_service",
            "api_intelligence_service"
        ]

        all_valid = True
        for service in services:
            try:
                module = __import__(service, fromlist=[None])
                all_valid = all_valid and module is not None
            except ImportError:
                all_valid = False

        return all_valid

    def validate_all(self) -> Dict[str, Any]:
        try:
            """Validate all system components"""
            logger.info("Starting comprehensive system validation...")

            validations = {
                "database": self.validate_component("Database", self.validate_database),
                "service_bus": self.validate_component("Service Bus", self.validate_service_bus),
                "key_vault": self.validate_component("Key Vault", self.validate_key_vault),
                "api_services": self.validate_component("API Services", self.validate_api_services)
            }

            all_passed = all(v.get("status") == "pass" for v in validations.values())

            result = {
                "validation_date": datetime.now().isoformat(),
                "overall_status": "valid" if all_passed else "invalid",
                "components": validations,
                "all_components_valid": all_passed
            }

            # Save validation report
            report_file = self.project_root / "data" / "system_validation_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

            return result


        except Exception as e:
            self.logger.error(f"Error in validate_all: {e}", exc_info=True)
            raise
def main():
    try:
        """Main validation function"""
        project_root = Path(__file__).parent.parent.parent
        validator = SystemValidator(project_root)

        print("=" * 60)
        print("JARVIS Master Agent - System Validator")
        print("=" * 60)

        result = validator.validate_all()

        print(f"\nOverall Status: {result['overall_status'].upper()}")
        print("\nComponent Status:")
        for component, validation in result["components"].items():
            status_icon = "✅" if validation["status"] == "pass" else "❌"
            print(f"  {status_icon} {component}: {validation['status']}")

        print("=" * 60)

        return result["all_components_valid"]


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from typing import Optional
    sys.exit(0 if success else 1)


    success = main()