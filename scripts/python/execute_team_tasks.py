#!/usr/bin/env python3
"""
Execute Team Tasks
Allows IT teams to execute their assigned tasks and track progress

Tags: #TEAMS #TASK_EXECUTION #AUTOMATION @JARVIS @LUMINA
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("ExecuteTeamTasks")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ExecuteTeamTasks")

from company_it_teams_ai_clustering import CompanyITTeams, TaskStatus, Task


class TaskExecutor:
    """Execute team tasks"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.teams = CompanyITTeams(project_root)
        self.execution_log = []

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a specific task"""
        # Ensure tasks are initialized
        if not self.teams.tasks:
            self.teams._create_initial_tasks()

        # Find task by ID (tasks are keyed by name, but have .id field)
        task = None
        for task_key, task_obj in self.teams.tasks.items():
            if task_obj.id == task_id:
                task = task_obj
                break

        if not task:
            available_ids = [t.id for t in self.teams.tasks.values()]
            return {"success": False, "error": f"Task {task_id} not found. Available IDs: {available_ids}"}

        logger.info("=" * 70)
        logger.info(f"🚀 EXECUTING TASK: {task_id}")
        logger.info(f"   Title: {task.title}")
        logger.info(f"   Assigned to: {task.assigned_to}")
        logger.info(f"   Team: {self.teams.teams[task.assigned_team].name}")
        logger.info("=" * 70)
        logger.info("")

        # Check dependencies
        if task.dependencies:
            logger.info("🔍 Checking dependencies...")
            for dep_id in task.dependencies:
                if dep_id in self.teams.tasks:
                    dep_task = self.teams.tasks[dep_id]
                    if dep_task.status != TaskStatus.COMPLETED:
                        logger.warning(f"   ⚠️  Dependency {dep_id} is not completed ({dep_task.status.value})")
                        return {
                            "success": False,
                            "error": f"Dependency {dep_id} not completed",
                            "blocked_by": dep_id
                        }
                else:
                    logger.warning(f"   ⚠️  Dependency {dep_id} not found")
            logger.info("   ✅ All dependencies satisfied")
            logger.info("")

        # Update task status
        task.status = TaskStatus.IN_PROGRESS

        # Execute based on task type
        result = self._execute_task_logic(task)

        if result.get("success"):
            task.status = TaskStatus.COMPLETED
            logger.info(f"✅ Task {task_id} completed successfully")
        else:
            task.status = TaskStatus.FAILED
            logger.error(f"❌ Task {task_id} failed: {result.get('error', 'Unknown error')}")

        # Log execution
        self.execution_log.append({
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })

        return result

    def _execute_task_logic(self, task: Task) -> Dict[str, Any]:
        """Execute task-specific logic"""
        task_id = task.id

        if task_id == "PP-001":
            return self._execute_protonpass_auth(task)
        elif task_id == "IL-001":
            return self._execute_iron_legion_main(task)
        elif task_id == "IL-002":
            return self._execute_iron_legion_models(task)
        elif task_id == "UL-001":
            return self._execute_ultron_optimization(task)
        elif task_id == "INF-001":
            return self._execute_network_connectivity(task)
        elif task_id == "SE-001":
            return self._execute_cluster_orchestration(task)
        elif task_id == "SEC-001":
            return self._execute_security_audit(task)
        elif task_id == "INT-001":
            return self._execute_unified_secrets(task)
        else:
            return {"success": False, "error": f"Unknown task type: {task_id}"}

    def _execute_protonpass_auth(self, task: Task) -> Dict[str, Any]:
        """Execute ProtonPass authentication task"""
        logger.info("🔐 Executing ProtonPass CLI authentication...")

        try:
            # Try authentication
            from protonpass_auto_login import main as auto_login
            result = auto_login()

            if result:
                # Test if we can list items
                import subprocess
                protonpass_path = Path(r"C:\Users\mlesn\AppData\Local\Programs\pass-cli.exe")
                test_result = subprocess.run(
                    [str(protonpass_path), "item", "list", "--output", "json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if test_result.returncode == 0:
                    return {
                        "success": True,
                        "message": "ProtonPass CLI authenticated and functional",
                        "details": {"items_accessible": True}
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Authentication succeeded but item listing failed: {test_result.stderr}",
                        "partial": True
                    }
            else:
                return {
                    "success": False,
                    "error": "Authentication failed - manual intervention may be required",
                    "requires_manual": True
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_iron_legion_main(self, task: Task) -> Dict[str, Any]:
        """Execute Iron Legion main cluster restoration"""
        logger.info("🔧 Executing Iron Legion main cluster restoration...")

        try:
            import requests

            # Check current status
            try:
                response = requests.get("http://<NAS_IP>:3000/health", timeout=5)
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Iron Legion main cluster is already online",
                        "details": {"status_code": response.status_code}
                    }
            except requests.exceptions.ConnectionError:
                pass

            # Try to start service (would need SSH access to KAIJU_NO_8)
            logger.info("   ⚠️  Requires SSH access to KAIJU_NO_8 to start service")
            logger.info("   💡 Manual intervention required or SSH automation needed")

            return {
                "success": False,
                "error": "Service not accessible - requires SSH access to KAIJU_NO_8 (<NAS_IP>)",
                "requires_ssh": True,
                "recommendation": "Check service status on KAIJU_NO_8 and restart if needed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_iron_legion_models(self, task: Task) -> Dict[str, Any]:
        """Execute Iron Legion model restoration"""
        logger.info("🔧 Executing Iron Legion model restoration...")

        offline_models = []
        online_models = []

        try:
            import requests

            for port in [3002, 3003, 3006, 3007]:
                model_name = f"Mark {port - 3000}"
                try:
                    response = requests.get(f"http://<NAS_IP>:{port}/health", timeout=3)
                    if response.status_code == 200:
                        online_models.append(model_name)
                    else:
                        offline_models.append({"model": model_name, "port": port, "status_code": response.status_code})
                except requests.exceptions.ConnectionError:
                    offline_models.append({"model": model_name, "port": port, "error": "Connection refused"})

            if not offline_models:
                return {
                    "success": True,
                    "message": "All Iron Legion models are online",
                    "details": {"online_models": online_models}
                }
            else:
                return {
                    "success": False,
                    "error": f"{len(offline_models)} models still offline",
                    "details": {
                        "online": online_models,
                        "offline": offline_models
                    },
                    "requires_ssh": True,
                    "recommendation": "Restart offline model services on KAIJU_NO_8"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_ultron_optimization(self, task: Task) -> Dict[str, Any]:
        """Execute ULTRON optimization"""
        logger.info("🔧 Executing ULTRON cluster optimization...")

        try:
            # Run battletest
            script_path = script_dir / "battletest_ultron_cluster.py"
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "ULTRON battletest passed",
                        "details": {"output": result.stdout[:500]}
                    }
                else:
                    return {
                        "success": False,
                        "error": "Battletest failed",
                        "details": {"stderr": result.stderr[:500]},
                        "recommendation": "Review battletest output and fix issues"
                    }
            else:
                return {"success": False, "error": "Battletest script not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_network_connectivity(self, task: Task) -> Dict[str, Any]:
        """Execute network connectivity verification"""
        logger.info("🔧 Executing network connectivity verification...")

        try:
            import socket

            # Test connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("<NAS_IP>", 3000))
            sock.close()

            if result == 0:
                return {
                    "success": True,
                    "message": "Network connectivity to KAIJU_NO_8 verified",
                    "details": {"port_3000": "open"}
                }
            else:
                return {
                    "success": False,
                    "error": f"Port 3000 not accessible (error code: {result})",
                    "recommendation": "Check firewall rules and network routing"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_cluster_orchestration(self, task: Task) -> Dict[str, Any]:
        """Execute cluster orchestration task"""
        logger.info("🔧 Executing cluster orchestration...")

        try:
            # Run cluster services startup
            script_path = script_dir / "start_all_cluster_services.py"
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                return {
                    "success": result.returncode == 0,
                    "message": "Cluster services orchestration executed",
                    "details": {
                        "return_code": result.returncode,
                        "output": result.stdout[:500] if result.stdout else None
                    }
                }
            else:
                return {"success": False, "error": "Cluster services script not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_security_audit(self, task: Task) -> Dict[str, Any]:
        """Execute security audit"""
        logger.info("🔧 Executing security audit...")

        try:
            # Run MARVIN security audit
            script_path = script_dir / "security_audit_marvin_teams.py"
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                return {
                    "success": result.returncode == 0,
                    "message": "Security audit completed",
                    "details": {"output": result.stdout[:500] if result.stdout else None}
                }
            else:
                return {"success": False, "error": "Security audit script not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_unified_secrets(self, task: Task) -> Dict[str, Any]:
        """Execute Unified Secrets Manager integration"""
        logger.info("🔧 Executing Unified Secrets Manager integration...")

        try:
            from unified_secrets_manager import UnifiedSecretsManager, SecretSource
            from pathlib import Path

            manager = UnifiedSecretsManager(project_root)

            # Verify ProtonPass is available and being used
            if not manager.protonpass_available:
                return {
                    "success": False,
                    "error": "ProtonPass CLI not available",
                    "recommendation": "Complete PP-001 first"
                }

            # Test source priority
            priority = manager._get_source_priority()
            protonpass_in_priority = any(s == SecretSource.PROTONPASS for s in priority)

            if protonpass_in_priority:
                return {
                    "success": True,
                    "message": "Unified Secrets Manager properly configured",
                    "details": {
                        "protonpass_available": True,
                        "in_priority": True,
                        "priority_order": [s.value for s in priority]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "ProtonPass not in priority list",
                    "recommendation": "Update source priority to include ProtonPass"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_team_tasks(self, team_name: str) -> Dict[str, Any]:
        """Execute all tasks for a specific team"""
        team_tasks = self.teams.get_team_tasks(team_name)

        logger.info(f"🚀 Executing tasks for: {self.teams.teams[team_name].name}")
        logger.info(f"   Total tasks: {len(team_tasks)}")
        logger.info("")

        results = {}
        for task in team_tasks:
            if task.status == TaskStatus.PENDING:
                result = self.execute_task(task.id)
                results[task.id] = result
                logger.info("")

        return results

    def execute_critical_path(self) -> Dict[str, Any]:
        """Execute critical path tasks"""
        critical_tasks = self.teams.get_critical_tasks()

        logger.info("=" * 70)
        logger.info("🔴 EXECUTING CRITICAL PATH")
        logger.info("=" * 70)
        logger.info("")

        results = {}
        for task in critical_tasks:
            result = self.execute_task(task.id)
            results[task.id] = result
            logger.info("")

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Execute IT team tasks")
    parser.add_argument("--team", help="Execute tasks for specific team")
    parser.add_argument("--task", help="Execute specific task ID")
    parser.add_argument("--critical", action="store_true", help="Execute critical path tasks")
    parser.add_argument("--all", action="store_true", help="Execute all pending tasks")

    args = parser.parse_args()

    print("Initializing TaskExecutor...")
    executor = TaskExecutor(project_root)
    print("TaskExecutor initialized")

    if args.task:
        print(f"Executing task: {args.task}")
        try:
            result = executor.execute_task(args.task)
            print(f"Task execution result: {result.get('success', False)}")
            if not result.get("success"):
                print(f"Error: {result.get('error', 'Unknown error')}")
            return 0 if result.get("success") else 1
        except Exception as e:
            print(f"Exception executing task: {e}")
            import traceback
            traceback.print_exc()
            return 1
    elif args.team:
        results = executor.execute_team_tasks(args.team)
        all_success = all(r.get("success") for r in results.values())
        return 0 if all_success else 1
    elif args.critical:
        results = executor.execute_critical_path()
        all_success = all(r.get("success") for r in results.values())
        return 0 if all_success else 1
    elif args.all:
        # Execute all pending tasks
        all_results = {}
        for team_name in executor.teams.teams.keys():
            results = executor.execute_team_tasks(team_name)
            all_results.update(results)
        all_success = all(r.get("success") for r in all_results.values())
        return 0 if all_success else 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":

    sys.exit(main())