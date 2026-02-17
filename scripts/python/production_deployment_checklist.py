#!/usr/bin/env python3
"""
Production Deployment Checklist
Validates system readiness for production deployment

Checks all components and generates deployment readiness report.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

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

logger = get_logger("DeploymentChecklist")


class ProductionDeploymentChecklist:
    """Validates production deployment readiness"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.checks: List[Dict[str, Any]] = []

    def check_file_exists(self, file_path: Path, description: str) -> bool:
        try:
            """Check if a file exists"""
            exists = file_path.exists()
            self.checks.append({
                "check": description,
                "file": str(file_path),
                "status": "pass" if exists else "fail",
                "required": True
            })
            return exists

        except Exception as e:
            self.logger.error(f"Error in check_file_exists: {e}", exc_info=True)
            raise
    def check_directory_exists(self, dir_path: Path, description: str) -> bool:
        try:
            """Check if a directory exists"""
            exists = dir_path.exists() and dir_path.is_dir()
            self.checks.append({
                "check": description,
                "directory": str(dir_path),
                "status": "pass" if exists else "fail",
                "required": True
            })
            return exists

        except Exception as e:
            self.logger.error(f"Error in check_directory_exists: {e}", exc_info=True)
            raise
    def validate_deployment_readiness(self) -> Dict[str, Any]:
        """Validate all deployment requirements"""
        logger.info("Validating production deployment readiness...")

        # Check infrastructure files
        self.check_file_exists(
            self.project_root / "scripts" / "terraform" / "main.tf",
            "Terraform main configuration"
        )
        self.check_file_exists(
            self.project_root / "scripts" / "terraform" / "variables.tf",
            "Terraform variables"
        )
        self.check_file_exists(
            self.project_root / "Dockerfile",
            "Dockerfile"
        )
        self.check_file_exists(
            self.project_root / "docker-compose.yml",
            "Docker Compose configuration"
        )
        self.check_file_exists(
            self.project_root / "requirements.txt",
            "Python requirements"
        )

        # Check API server
        self.check_file_exists(
            self.project_root / "scripts" / "python" / "jarvis_master_agent_api_server.py",
            "API server implementation"
        )

        # Check API services
        services = [
            "api_authentication_service.py",
            "api_workflow_service.py",
            "api_chat_service.py",
            "api_r5_service.py",
            "api_helpdesk_service.py",
            "api_intelligence_service.py"
        ]
        for service in services:
            self.check_file_exists(
                self.project_root / "scripts" / "python" / service,
                f"API service: {service}"
            )

        # Check infrastructure integration
        infrastructure_files = [
            "azure_service_bus_integration.py",
            "database_connection_manager.py",
            "database_migration_manager.py"
        ]
        for infra_file in infrastructure_files:
            self.check_file_exists(
                self.project_root / "scripts" / "python" / infra_file,
                f"Infrastructure: {infra_file}"
            )

        # Check defense architecture
        defense_files = [
            "defense_architecture_killswitch.py",
            "defense_architecture_airgap.py",
            "defense_architecture_privilege_separation.py",
            "defense_architecture_transaction_logging.py"
        ]
        for defense_file in defense_files:
            self.check_file_exists(
                self.project_root / "scripts" / "python" / defense_file,
                f"Defense: {defense_file}"
            )

        # Check documentation
        self.check_file_exists(
            self.project_root / "docs" / "api" / "JARVIS_MASTER_AGENT_API_SPECIFICATION.md",
            "API specification"
        )
        self.check_file_exists(
            self.project_root / "README_DEPLOYMENT.md",
            "Deployment documentation"
        )

        # Check database schemas
        self.check_file_exists(
            self.project_root / "docs" / "data_models" / "database_schemas.json",
            "Database schemas"
        )

        # Calculate results
        total_checks = len(self.checks)
        passed_checks = sum(1 for c in self.checks if c["status"] == "pass")
        failed_checks = [c for c in self.checks if c["status"] == "fail" and c.get("required")]

        readiness = {
            "validation_date": datetime.now().isoformat(),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": len(failed_checks),
            "readiness_score": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            "production_ready": len(failed_checks) == 0,
            "checks": self.checks,
            "failed_required_checks": failed_checks
        }

        return readiness

    def generate_report(self) -> Dict[str, Any]:
        try:
            """Generate deployment readiness report"""
            readiness = self.validate_deployment_readiness()

            report_file = self.project_root / "data" / "deployment_readiness_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(readiness, f, indent=2)

            logger.info(f"Deployment readiness report saved to: {report_file}")

            return readiness


        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
def main():
    try:
        """Main validation function"""
        project_root = Path(__file__).parent.parent.parent
        checklist = ProductionDeploymentChecklist(project_root)

        print("=" * 60)
        print("Production Deployment Readiness Checklist")
        print("=" * 60)

        readiness = checklist.generate_report()

        print(f"\nReadiness Score: {readiness['readiness_score']:.1f}%")
        print(f"Passed Checks: {readiness['passed_checks']}/{readiness['total_checks']}")
        print(f"Failed Required Checks: {readiness['failed_checks']}")
        print(f"Production Ready: {'✅ YES' if readiness['production_ready'] else '❌ NO'}")

        if readiness['failed_required_checks']:
            print("\nFailed Required Checks:")
            for check in readiness['failed_required_checks']:
                print(f"  ❌ {check['check']}: {check.get('file', check.get('directory', 'N/A'))}")

        print("=" * 60)

        return readiness['production_ready']


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from typing import Optional
    sys.exit(0 if success else 1)


    success = main()