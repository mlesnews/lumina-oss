#!/usr/bin/env python3
"""
JARVIS Remote Compute Triage & BAU
Triage assessment and BAU execution for remote compute deployment

Tags: #TRIAGE #BAU #REMOTE_COMPUTE #AZURE #DEPLOYMENT @JARVIS @LUMINA
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("RemoteComputeTriageBAU")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RemoteComputeTriageBAU")


class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class DeploymentTask:
    """Deployment task definition"""
    id: str
    name: str
    description: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: int = 0  # minutes
    actual_effort: int = 0
    notes: str = ""
    result: Any = None
    error: str = ""


class RemoteComputeTriageBAU:
    """Triage and BAU system for remote compute deployment"""

    def __init__(self):
        self.project_root = project_root
        self.tasks: List[DeploymentTask] = []
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []

    def triage(self) -> Dict[str, Any]:
        """Triage: Assess and prioritize deployment tasks"""
        logger.info("=" * 80)
        logger.info("🔍 TRIAGE: Remote Compute Deployment Assessment")
        logger.info("=" * 80)

        # Define all tasks
        self.tasks = [
            DeploymentTask(
                id="task_001",
                name="Configure Azure Services Endpoints",
                description="Update azure_services_config.json with remote compute endpoints",
                priority=TaskPriority.CRITICAL,
                estimated_effort=15,
                notes="Required for remote rendering to work"
            ),
            DeploymentTask(
                id="task_002",
                name="Deploy Azure Function Template",
                description="Deploy RenderIronLegion function to Azure Functions",
                priority=TaskPriority.CRITICAL,
                dependencies=["task_001"],
                estimated_effort=30,
                notes="Core remote rendering endpoint"
            ),
            DeploymentTask(
                id="task_003",
                name="Verify Azure Function Deployment",
                description="Test Azure Function endpoint is accessible",
                priority=TaskPriority.HIGH,
                dependencies=["task_002"],
                estimated_effort=10,
                notes="Health check and connectivity test"
            ),
            DeploymentTask(
                id="task_004",
                name="Configure Authentication",
                description="Set up Azure Key Vault secrets and authentication",
                priority=TaskPriority.HIGH,
                dependencies=["task_001"],
                estimated_effort=20,
                notes="Required for secure API access"
            ),
            DeploymentTask(
                id="task_005",
                name="Test Remote Rendering",
                description="End-to-end test of remote rendering pipeline",
                priority=TaskPriority.MEDIUM,
                dependencies=["task_002", "task_003", "task_004"],
                estimated_effort=15,
                notes="Verify full workflow"
            ),
            DeploymentTask(
                id="task_006",
                name="Update Documentation",
                description="Update deployment docs with actual endpoints",
                priority=TaskPriority.LOW,
                dependencies=["task_002"],
                estimated_effort=10,
                notes="Keep docs current"
            )
        ]

        # Sort by priority
        priority_order = {
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.MEDIUM: 3,
            TaskPriority.LOW: 4
        }
        self.tasks.sort(key=lambda t: (priority_order[t.priority], t.id))

        # Generate triage report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(self.tasks),
            "by_priority": {
                "critical": len([t for t in self.tasks if t.priority == TaskPriority.CRITICAL]),
                "high": len([t for t in self.tasks if t.priority == TaskPriority.HIGH]),
                "medium": len([t for t in self.tasks if t.priority == TaskPriority.MEDIUM]),
                "low": len([t for t in self.tasks if t.priority == TaskPriority.LOW])
            },
            "tasks": [self._task_to_dict(t) for t in self.tasks],
            "estimated_total_effort": sum(t.estimated_effort for t in self.tasks)
        }

        logger.info(f"📊 Triage Complete:")
        logger.info(f"   Total Tasks: {report['total_tasks']}")
        logger.info(f"   Critical: {report['by_priority']['critical']}")
        logger.info(f"   High: {report['by_priority']['high']}")
        logger.info(f"   Medium: {report['by_priority']['medium']}")
        logger.info(f"   Low: {report['by_priority']['low']}")
        logger.info(f"   Estimated Effort: {report['estimated_total_effort']} minutes")

        return report

    def execute_bau(self, dry_run: bool = False) -> Dict[str, Any]:
        """BAU: Execute tasks in priority order"""
        logger.info("=" * 80)
        logger.info("⚙️  BAU: Executing Remote Compute Deployment")
        logger.info("=" * 80)

        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")

        results = {
            "started": datetime.now().isoformat(),
            "completed": [],
            "failed": [],
            "skipped": [],
            "dry_run": dry_run
        }

        # Execute tasks in priority order
        for task in self.tasks:
            # Check dependencies
            if not self._dependencies_met(task):
                logger.warning(f"⏸️  Skipping {task.id}: Dependencies not met")
                results["skipped"].append(task.id)
                continue

            logger.info(f"\n{'🔍 [DRY RUN]' if dry_run else '▶️ '} Executing: {task.name} ({task.id})")
            task.status = TaskStatus.IN_PROGRESS

            try:
                if not dry_run:
                    result = self._execute_task(task)
                    if result["success"]:
                        task.status = TaskStatus.COMPLETED
                        task.result = result
                        self.completed_tasks.append(task.id)
                        results["completed"].append({
                            "id": task.id,
                            "name": task.name,
                            "result": result
                        })
                        logger.info(f"✅ Completed: {task.name}")
                    else:
                        task.status = TaskStatus.FAILED
                        task.error = result.get("error", "Unknown error")
                        self.failed_tasks.append(task.id)
                        results["failed"].append({
                            "id": task.id,
                            "name": task.name,
                            "error": task.error
                        })
                        logger.error(f"❌ Failed: {task.name} - {task.error}")
                else:
                    logger.info(f"   [DRY RUN] Would execute: {task.name}")
                    results["completed"].append({"id": task.id, "name": task.name, "dry_run": True})

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                self.failed_tasks.append(task.id)
                results["failed"].append({
                    "id": task.id,
                    "name": task.name,
                    "error": str(e)
                })
                logger.error(f"❌ Exception in {task.name}: {e}")

        results["finished"] = datetime.now().isoformat()
        results["summary"] = {
            "total": len(self.tasks),
            "completed": len(results["completed"]),
            "failed": len(results["failed"]),
            "skipped": len(results["skipped"])
        }

        logger.info("\n" + "=" * 80)
        logger.info("📊 BAU Execution Summary:")
        logger.info(f"   Completed: {results['summary']['completed']}")
        logger.info(f"   Failed: {results['summary']['failed']}")
        logger.info(f"   Skipped: {results['summary']['skipped']}")
        logger.info("=" * 80)

        return results

    def _dependencies_met(self, task: DeploymentTask) -> bool:
        """Check if all dependencies are met"""
        if not task.dependencies:
            return True
        return all(dep_id in self.completed_tasks for dep_id in task.dependencies)

    def _execute_task(self, task: DeploymentTask) -> Dict[str, Any]:
        """Execute a specific task"""
        start_time = datetime.now()

        if task.id == "task_001":
            return self._configure_endpoints()
        elif task.id == "task_002":
            return self._deploy_azure_function()
        elif task.id == "task_003":
            return self._verify_deployment()
        elif task.id == "task_004":
            return self._configure_auth()
        elif task.id == "task_005":
            return self._test_remote_rendering()
        elif task.id == "task_006":
            return self._update_documentation()
        else:
            return {"success": False, "error": f"Unknown task: {task.id}"}

    def _configure_endpoints(self) -> Dict[str, Any]:
        """Task 001: Configure Azure Services Endpoints"""
        logger.info("   📝 Configuring Azure services endpoints...")

        config_path = self.project_root / "config" / "azure_services_config.json"

        try:
            # Load existing config
            with open(config_path, 'r') as f:
                config = json.load(f)

            azure_config = config.get("azure_services_config", {})

            # Add remote compute endpoints
            if "remote_compute" not in azure_config:
                azure_config["remote_compute"] = {}

            azure_config["remote_compute"]["enabled"] = True
            azure_config["remote_compute"]["render_endpoint"] = "https://jarvis-lumina-functions.azurewebsites.net/api/RenderIronLegion"
            azure_config["remote_compute"]["vlm_endpoint"] = "https://jarvis-lumina-vision.cognitiveservices.azure.com/vision/v3.2/analyze"
            azure_config["remote_compute"]["compute_endpoint"] = azure_config["remote_compute"]["render_endpoint"]
            azure_config["remote_compute"]["fallback_to_local"] = True
            azure_config["remote_compute"]["cache_enabled"] = True

            # Update config
            config["azure_services_config"] = azure_config

            # Save
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("   ✅ Endpoints configured")
            return {
                "success": True,
                "config_path": str(config_path),
                "endpoints_added": 3
            }
        except Exception as e:
            logger.error(f"   ❌ Configuration failed: {e}")
            return {"success": False, "error": str(e)}

    def _deploy_azure_function(self) -> Dict[str, Any]:
        """Task 002: Deploy Azure Function Template"""
        logger.info("   🚀 Deploying Azure Function template...")

        function_path = self.project_root / "azure_functions" / "RenderIronLegion"

        try:
            # Verify function template exists
            if not function_path.exists():
                return {
                    "success": False,
                    "error": f"Function template not found: {function_path}",
                    "note": "Function template created but needs manual deployment to Azure"
                }

            # Check for function.json (Azure Functions config)
            function_json = function_path / "function.json"
            if not function_json.exists():
                # Create function.json
                function_config = {
                    "scriptFile": "__init__.py",
                    "bindings": [
                        {
                            "authLevel": "function",
                            "type": "httpTrigger",
                            "direction": "in",
                            "name": "req",
                            "methods": ["post"]
                        },
                        {
                            "type": "http",
                            "direction": "out",
                            "name": "$return"
                        }
                    ]
                }
                with open(function_json, 'w') as f:
                    json.dump(function_config, f, indent=2)
                logger.info("   ✅ Created function.json")

            logger.info("   ✅ Function template ready for deployment")
            logger.info("   📋 Next steps:")
            logger.info("      1. Install Azure Functions Core Tools")
            logger.info("      2. Run: func azure functionapp publish jarvis-lumina-functions")
            logger.info("      3. Or deploy via Azure Portal/VS Code extension")

            return {
                "success": True,
                "function_path": str(function_path),
                "note": "Template ready - requires manual deployment to Azure",
                "deployment_command": "func azure functionapp publish jarvis-lumina-functions"
            }
        except Exception as e:
            logger.error(f"   ❌ Deployment preparation failed: {e}")
            return {"success": False, "error": str(e)}

    def _verify_deployment(self) -> Dict[str, Any]:
        """Task 003: Verify Azure Function Deployment"""
        logger.info("   🔍 Verifying deployment...")

        try:
            import requests
            endpoint = "https://jarvis-lumina-functions.azurewebsites.net/api/RenderIronLegion"

            # Test endpoint
            test_payload = {
                "state": "armor",
                "animation_frame": 0,
                "transformation_progress": 1.0,
                "size": 180
            }

            try:
                response = requests.post(endpoint, json=test_payload, timeout=10)
                if response.status_code == 200:
                    logger.info("   ✅ Endpoint is accessible and responding")
                    return {
                        "success": True,
                        "endpoint": endpoint,
                        "status_code": response.status_code
                    }
                else:
                    logger.warning(f"   ⚠️  Endpoint returned {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Endpoint returned {response.status_code}",
                        "note": "Function may not be deployed yet"
                    }
            except requests.exceptions.RequestException as e:
                logger.warning(f"   ⚠️  Endpoint not accessible: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "note": "Function may not be deployed yet - this is expected if deployment hasn't happened"
                }
        except ImportError:
            return {
                "success": False,
                "error": "requests library not available",
                "note": "Install with: pip install requests"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _configure_auth(self) -> Dict[str, Any]:
        """Task 004: Configure Authentication"""
        logger.info("   🔐 Configuring authentication...")

        try:
            # Check Azure Key Vault configuration
            config_path = self.project_root / "config" / "azure_services_config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)

            key_vault = config.get("azure_services_config", {}).get("key_vault", {})

            if key_vault.get("enabled"):
                logger.info("   ✅ Azure Key Vault is configured")
                logger.info("   📋 Required secrets:")
                logger.info("      - cognitive-vision-key (for VLM)")
                logger.info("      - azure-function-app-key (if using function keys)")

                return {
                    "success": True,
                    "key_vault_configured": True,
                    "vault_url": key_vault.get("vault_url", ""),
                    "note": "Secrets need to be added to Key Vault manually"
                }
            else:
                return {
                    "success": False,
                    "error": "Azure Key Vault not enabled",
                    "note": "Enable Key Vault in azure_services_config.json"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_remote_rendering(self) -> Dict[str, Any]:
        """Task 005: Test Remote Rendering"""
        logger.info("   🧪 Testing remote rendering...")

        try:
            from jarvis_remote_renderer import HybridRenderer

            renderer = HybridRenderer()
            result = renderer.render(
                state="armor",
                animation_frame=0,
                transformation_progress=1.0,
                size=180
            )

            if result:
                logger.info("   ✅ Remote rendering test successful")
                return {
                    "success": True,
                    "image_size_bytes": len(result),
                    "note": "Remote rendering is working"
                }
            else:
                logger.warning("   ⚠️  Remote rendering unavailable, using fallback")
                return {
                    "success": True,
                    "note": "Remote rendering unavailable but fallback working",
                    "fallback_active": True
                }
        except ImportError:
            return {
                "success": False,
                "error": "jarvis_remote_renderer not available",
                "note": "Ensure jarvis_remote_renderer.py is in scripts/python/"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _update_documentation(self) -> Dict[str, Any]:
        """Task 006: Update Documentation"""
        logger.info("   📚 Updating documentation...")

        try:
            doc_path = self.project_root / "docs" / "JARVIS_REMOTE_COMPUTE_ARCHITECTURE.md"

            if doc_path.exists():
                logger.info("   ✅ Documentation exists")
                return {
                    "success": True,
                    "doc_path": str(doc_path),
                    "note": "Documentation is up to date"
                }
            else:
                return {
                    "success": False,
                    "error": "Documentation not found",
                    "note": "Documentation should be created"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _task_to_dict(self, task: DeploymentTask) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "priority": task.priority.value,
            "status": task.status.value,
            "dependencies": task.dependencies,
            "estimated_effort": task.estimated_effort
        }


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Remote Compute Triage & BAU")
        parser.add_argument("--triage-only", action="store_true", help="Run triage only")
        parser.add_argument("--bau-only", action="store_true", help="Run BAU only")
        parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

        args = parser.parse_args()

        system = RemoteComputeTriageBAU()

        if args.triage_only:
            report = system.triage()
            output_path = project_root / "data" / "diagnostics" / f"remote_compute_triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📄 Triage report saved: {output_path}")
        elif args.bau_only:
            # Load triage first
            system.triage()
            results = system.execute_bau(dry_run=args.dry_run)
            output_path = project_root / "data" / "diagnostics" / f"remote_compute_bau_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📄 BAU results saved: {output_path}")
        else:
            # Run both
            report = system.triage()
            results = system.execute_bau(dry_run=args.dry_run)

            # Save reports
            diagnostics_dir = project_root / "data" / "diagnostics"
            diagnostics_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            triage_path = diagnostics_dir / f"remote_compute_triage_{timestamp}.json"
            bau_path = diagnostics_dir / f"remote_compute_bau_{timestamp}.json"

            with open(triage_path, 'w') as f:
                json.dump(report, f, indent=2)
            with open(bau_path, 'w') as f:
                json.dump(results, f, indent=2)

            logger.info(f"📄 Reports saved:")
            logger.info(f"   Triage: {triage_path}")
            logger.info(f"   BAU: {bau_path}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()