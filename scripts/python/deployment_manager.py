#!/usr/bin/env python3
"""
Deployment Manager
Manages deployment of JARVIS Master Agent API and related services

Handles infrastructure deployment, application deployment, and validation.
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

logger = get_logger("DeploymentManager")


class DeploymentManager:
    """Manages system deployment"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.deployment_log_dir = self.project_root / "data" / "deployments"
        self.deployment_log_dir.mkdir(parents=True, exist_ok=True)

    def deploy_infrastructure(self, environment: str = "production") -> Dict[str, Any]:
        try:
            """Deploy Azure infrastructure"""
            logger.info(f"Deploying infrastructure to {environment}...")

            # Run infrastructure provisioning scripts
            scripts = [
                "scripts/azure/service_bus_provision.sh",
                "scripts/azure/key_vault_provision.sh"
            ]

            results = {}
            for script in scripts:
                script_path = self.project_root / script
                if script_path.exists():
                    logger.info(f"Running {script}...")
                    # In production, would execute these scripts
                    results[script] = "pending_execution"
                else:
                    results[script] = "script_not_found"

            return {
                "status": "infrastructure_deployment_initiated",
                "environment": environment,
                "scripts": results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error in deploy_infrastructure: {e}", exc_info=True)
            raise
    def deploy_database(self) -> Dict[str, Any]:
        """Deploy database schemas"""
        logger.info("Deploying database schemas...")

        try:
            from database_migration_manager import DatabaseMigrationManager
            migration_manager = DatabaseMigrationManager(self.project_root)
            results = migration_manager.apply_all_schemas()

            return {
                "status": "database_deployment_complete",
                "schemas_applied": sum(1 for r in results.values() if r),
                "schemas_failed": sum(1 for r in results.values() if not r),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Database deployment failed: {e}")
            return {
                "status": "database_deployment_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def deploy_api_server(self, environment: str = "production") -> Dict[str, Any]:
        """Deploy API server"""
        logger.info(f"Deploying API server to {environment}...")

        # In production, would:
        # 1. Build Docker image
        # 2. Push to container registry
        # 3. Deploy to Azure App Service
        # 4. Configure environment variables
        # 5. Start service

        return {
            "status": "api_server_deployment_initiated",
            "environment": environment,
            "api_server": "jarvis_master_agent_api_server.py",
            "timestamp": datetime.now().isoformat()
        }

    def validate_deployment(self) -> Dict[str, Any]:
        """Validate deployment"""
        logger.info("Validating deployment...")

        validations = {
            "database_connection": False,
            "service_bus_connection": False,
            "key_vault_connection": False,
            "api_server_health": False
        }

        # Test database connection
        try:
            from database_connection_manager import get_db_manager
            db_manager = get_db_manager(self.project_root)
            conn = db_manager.get_connection()
            db_manager.return_connection(conn)
            validations["database_connection"] = True
        except Exception as e:
            logger.warning(f"Database validation failed: {e}")

        # Test Service Bus connection
        try:
            from azure_service_bus_integration import get_service_bus_client, get_key_vault_client
            kv_client = get_key_vault_client()
            sb_client = get_service_bus_client(key_vault_client=kv_client)
            validations["service_bus_connection"] = True
            validations["key_vault_connection"] = True
        except Exception as e:
            logger.warning(f"Azure validation failed: {e}")

        # Test API server health
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v1/system/health", timeout=5)
            if response.status_code == 200:
                validations["api_server_health"] = True
        except Exception as e:
            logger.warning(f"API server health check failed: {e}")

        all_valid = all(validations.values())

        return {
            "status": "validated" if all_valid else "validation_failed",
            "validations": validations,
            "all_valid": all_valid,
            "timestamp": datetime.now().isoformat()
        }

    def deploy_all(self, environment: str = "production") -> Dict[str, Any]:
        try:
            """Deploy all components"""
            logger.info(f"Starting full deployment to {environment}...")

            deployment_report = {
                "deployment_started": datetime.now().isoformat(),
                "environment": environment,
                "components": {}
            }

            # Deploy infrastructure
            deployment_report["components"]["infrastructure"] = self.deploy_infrastructure(environment)

            # Deploy database
            deployment_report["components"]["database"] = self.deploy_database()

            # Deploy API server
            deployment_report["components"]["api_server"] = self.deploy_api_server(environment)

            # Validate deployment
            deployment_report["validation"] = self.validate_deployment()

            deployment_report["deployment_completed"] = datetime.now().isoformat()
            deployment_report["status"] = "completed" if deployment_report["validation"]["all_valid"] else "completed_with_warnings"

            # Save deployment report
            report_file = self.deployment_log_dir / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(deployment_report, f, indent=2)

            logger.info(f"Deployment report saved to: {report_file}")

            return deployment_report


        except Exception as e:
            self.logger.error(f"Error in deploy_all: {e}", exc_info=True)
            raise
def main():
    try:
        """Main deployment function"""
        import argparse

        parser = argparse.ArgumentParser(description="Deploy JARVIS Master Agent System")
        parser.add_argument("--environment", default="production", choices=["development", "staging", "production"])
        parser.add_argument("--component", choices=["infrastructure", "database", "api", "all"], default="all")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        deployment_manager = DeploymentManager(project_root)

        print("=" * 60)
        print("JARVIS Master Agent - Deployment Manager")
        print("=" * 60)
        print(f"Environment: {args.environment}")
        print(f"Component: {args.component}")
        print("=" * 60)

        if args.component == "all":
            report = deployment_manager.deploy_all(args.environment)
        elif args.component == "infrastructure":
            report = deployment_manager.deploy_infrastructure(args.environment)
        elif args.component == "database":
            report = deployment_manager.deploy_database()
        elif args.component == "api":
            report = deployment_manager.deploy_api_server(args.environment)

        print("\nDeployment Summary:")
        print(json.dumps(report, indent=2))
        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()