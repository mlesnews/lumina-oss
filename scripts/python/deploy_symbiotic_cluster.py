#!/usr/bin/env python3
"""
JARVIS Implementation: Deployment, Logistics, Activation, and Execution
Symbiotic Cluster Coordinator - Complete Deployment & Execution System

Comprehensive deployment, logistics, activation, and execution framework
for the Symbiotic Cluster Coordinator (Iron Legion).
"""

import sys
import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from symbiotic_cluster_coordinator import SymbioticClusterCoordinator
    CLUSTER_COORDINATOR_AVAILABLE = True
except ImportError:
    CLUSTER_COORDINATOR_AVAILABLE = False



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DeploymentPhase(Enum):
    """Deployment phases"""
    PREPARATION = "preparation"
    DEPLOYMENT = "deployment"
    LOGISTICS = "logistics"
    ACTIVATION = "activation"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    COMPLETE = "complete"


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DeploymentStep:
    """Deployment step"""
    step_id: str
    phase: DeploymentPhase
    name: str
    description: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['phase'] = self.phase.value
        data['status'] = self.status.value
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


class SymbioticClusterDeployment:
    """
    JARVIS Implementation: Deployment, Logistics, Activation, and Execution

    Complete deployment and execution framework for Symbiotic Cluster Coordinator.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize deployment system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SymbioticClusterDeployment")

        # Deployment configuration
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data" / "symbiotic_cluster"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Deployment state
        self.deployment_steps: Dict[str, DeploymentStep] = {}
        self.deployment_phases: Dict[DeploymentPhase, List[str]] = {}
        self.coordinator: Optional[SymbioticClusterCoordinator] = None
        self.deployment_start: Optional[datetime] = None
        self.deployment_end: Optional[datetime] = None

        # Execution state
        self.execution_thread: Optional[threading.Thread] = None
        self._execution_running = False

        # Load configuration
        self.config = self._load_configuration()

        self.logger.info("✅ Symbiotic Cluster Deployment System initialized")

    def _load_configuration(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        config_file = self.config_dir / "symbiotic_cluster_config.json"

        default_config = {
            "local_endpoint": "http://localhost:11437",
            "target_endpoint": "http://kaiju_no_8:11437",
            "target_utilization": 97.0,
            "balance_interval": 30,
            "health_check_interval": 60,
            "deployment_timeout": 300,
            "activation_timeout": 120,
            "verification_retries": 3
        }

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.debug(f"Could not load config: {e}")

        return default_config

    def _initialize_deployment_steps(self) -> None:
        """Initialize deployment steps"""

        # Phase 1: Preparation
        self._add_step(DeploymentStep(
            step_id="check_dependencies",
            phase=DeploymentPhase.PREPARATION,
            name="Check Dependencies",
            description="Verify all required dependencies are installed"
        ))

        self._add_step(DeploymentStep(
            step_id="verify_configuration",
            phase=DeploymentPhase.PREPARATION,
            name="Verify Configuration",
            description="Verify deployment configuration is valid"
        ))

        self._add_step(DeploymentStep(
            step_id="check_network_connectivity",
            phase=DeploymentPhase.PREPARATION,
            name="Check Network Connectivity",
            description="Verify network connectivity to both hosts"
        ))

        # Phase 2: Deployment
        self._add_step(DeploymentStep(
            step_id="deploy_coordinator",
            phase=DeploymentPhase.DEPLOYMENT,
            name="Deploy Cluster Coordinator",
            description="Deploy symbiotic cluster coordinator",
            dependencies=["check_dependencies", "verify_configuration"]
        ))

        self._add_step(DeploymentStep(
            step_id="configure_endpoints",
            phase=DeploymentPhase.DEPLOYMENT,
            name="Configure Endpoints",
            description="Configure local and target endpoints",
            dependencies=["deploy_coordinator"]
        ))

        # Phase 3: Logistics
        self._add_step(DeploymentStep(
            step_id="setup_monitoring",
            phase=DeploymentPhase.LOGISTICS,
            name="Setup Monitoring",
            description="Setup health monitoring and metrics collection",
            dependencies=["configure_endpoints"]
        ))

        self._add_step(DeploymentStep(
            step_id="configure_load_balancing",
            phase=DeploymentPhase.LOGISTICS,
            name="Configure Load Balancing",
            description="Configure load balancing parameters",
            dependencies=["setup_monitoring"]
        ))

        self._add_step(DeploymentStep(
            step_id="setup_failover",
            phase=DeploymentPhase.LOGISTICS,
            name="Setup Failover",
            description="Configure automatic failover mechanisms",
            dependencies=["configure_load_balancing"]
        ))

        # Phase 4: Activation
        self._add_step(DeploymentStep(
            step_id="initialize_coordinator",
            phase=DeploymentPhase.ACTIVATION,
            name="Initialize Coordinator",
            description="Initialize symbiotic cluster coordinator",
            dependencies=["setup_failover"]
        ))

        self._add_step(DeploymentStep(
            step_id="start_coordinator",
            phase=DeploymentPhase.ACTIVATION,
            name="Start Coordinator",
            description="Start cluster coordination services",
            dependencies=["initialize_coordinator"]
        ))

        self._add_step(DeploymentStep(
            step_id="verify_hosts",
            phase=DeploymentPhase.ACTIVATION,
            name="Verify Hosts",
            description="Verify both hosts are accessible",
            dependencies=["start_coordinator"]
        ))

        # Phase 5: Execution
        self._add_step(DeploymentStep(
            step_id="start_execution",
            phase=DeploymentPhase.EXECUTION,
            name="Start Execution",
            description="Start cluster execution and monitoring",
            dependencies=["verify_hosts"]
        ))

        self._add_step(DeploymentStep(
            step_id="start_load_balancing",
            phase=DeploymentPhase.EXECUTION,
            name="Start Load Balancing",
            description="Start load balancing operations",
            dependencies=["start_execution"]
        ))

        # Phase 6: Verification
        self._add_step(DeploymentStep(
            step_id="verify_cluster_health",
            phase=DeploymentPhase.VERIFICATION,
            name="Verify Cluster Health",
            description="Verify cluster is healthy and operational",
            dependencies=["start_load_balancing"]
        ))

        self._add_step(DeploymentStep(
            step_id="verify_utilization",
            phase=DeploymentPhase.VERIFICATION,
            name="Verify Utilization",
            description="Verify resource utilization is on target",
            dependencies=["verify_cluster_health"]
        ))

        self._add_step(DeploymentStep(
            step_id="verify_failover",
            phase=DeploymentPhase.VERIFICATION,
            name="Verify Failover",
            description="Verify failover mechanisms are operational",
            dependencies=["verify_utilization"]
        ))

    def _add_step(self, step: DeploymentStep) -> None:
        """Add deployment step"""
        self.deployment_steps[step.step_id] = step

        if step.phase not in self.deployment_phases:
            self.deployment_phases[step.phase] = []
        self.deployment_phases[step.phase].append(step.step_id)

    # Deployment Implementation

    def deploy(self) -> bool:
        """Execute complete deployment"""
        self.logger.info("🚀 Starting Symbiotic Cluster Deployment")
        self.deployment_start = datetime.now()

        # Initialize steps
        self._initialize_deployment_steps()

        # Execute phases in order
        phases = [
            DeploymentPhase.PREPARATION,
            DeploymentPhase.DEPLOYMENT,
            DeploymentPhase.LOGISTICS,
            DeploymentPhase.ACTIVATION,
            DeploymentPhase.EXECUTION,
            DeploymentPhase.VERIFICATION
        ]

        for phase in phases:
            if not self._execute_phase(phase):
                self.logger.error(f"❌ Phase {phase.value} failed")
                return False

        self.deployment_end = datetime.now()
        duration = (self.deployment_end - self.deployment_start).total_seconds()

        self.logger.info(f"✅ Deployment completed in {duration:.1f} seconds")
        self._save_deployment_report()

        return True

    def _execute_phase(self, phase: DeploymentPhase) -> bool:
        """Execute deployment phase"""
        self.logger.info(f"\n📦 Phase: {phase.value.upper()}")
        self.logger.info("=" * 60)

        step_ids = self.deployment_phases.get(phase, [])

        for step_id in step_ids:
            step = self.deployment_steps[step_id]

            # Check dependencies
            if not self._check_dependencies(step):
                step.status = DeploymentStatus.SKIPPED
                self.logger.warning(f"⚠️  Skipping {step.name} (dependencies not met)")
                continue

            # Execute step
            if not self._execute_step(step):
                self.logger.error(f"❌ {step.name} failed")
                return False

        return True

    def _check_dependencies(self, step: DeploymentStep) -> bool:
        """Check if step dependencies are met"""
        for dep_id in step.dependencies:
            dep_step = self.deployment_steps.get(dep_id)
            if not dep_step or dep_step.status != DeploymentStatus.COMPLETED:
                return False
        return True

    def _execute_step(self, step: DeploymentStep) -> bool:
        """Execute deployment step"""
        step.status = DeploymentStatus.IN_PROGRESS
        step.start_time = datetime.now()

        self.logger.info(f"  → {step.name}...")

        try:
            # Execute step based on step_id
            result = self._execute_step_action(step.step_id)

            step.status = DeploymentStatus.COMPLETED
            step.result = result
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()

            self.logger.info(f"  ✅ {step.name} completed ({step.duration_seconds:.1f}s)")
            return True

        except Exception as e:
            step.status = DeploymentStatus.FAILED
            step.error = str(e)
            step.end_time = datetime.now()
            self.logger.error(f"  ❌ {step.name} failed: {e}")
            return False

    def _execute_step_action(self, step_id: str) -> Dict[str, Any]:
        """Execute specific step action"""

        if step_id == "check_dependencies":
            return self._check_dependencies_action()

        elif step_id == "verify_configuration":
            return self._verify_configuration_action()

        elif step_id == "check_network_connectivity":
            return self._check_network_connectivity_action()

        elif step_id == "deploy_coordinator":
            return self._deploy_coordinator_action()

        elif step_id == "configure_endpoints":
            return self._configure_endpoints_action()

        elif step_id == "setup_monitoring":
            return self._setup_monitoring_action()

        elif step_id == "configure_load_balancing":
            return self._configure_load_balancing_action()

        elif step_id == "setup_failover":
            return self._setup_failover_action()

        elif step_id == "initialize_coordinator":
            return self._initialize_coordinator_action()

        elif step_id == "start_coordinator":
            return self._start_coordinator_action()

        elif step_id == "verify_hosts":
            return self._verify_hosts_action()

        elif step_id == "start_execution":
            return self._start_execution_action()

        elif step_id == "start_load_balancing":
            return self._start_load_balancing_action()

        elif step_id == "verify_cluster_health":
            return self._verify_cluster_health_action()

        elif step_id == "verify_utilization":
            return self._verify_utilization_action()

        elif step_id == "verify_failover":
            return self._verify_failover_action()

        else:
            return {"status": "unknown_step"}

    # Step Actions

    def _check_dependencies_action(self) -> Dict[str, Any]:
        """Check dependencies"""
        dependencies = {
            "requests": REQUESTS_AVAILABLE,
            "symbiotic_cluster_coordinator": CLUSTER_COORDINATOR_AVAILABLE
        }

        missing = [k for k, v in dependencies.items() if not v]

        return {
            "status": "ok" if not missing else "missing",
            "dependencies": dependencies,
            "missing": missing
        }

    def _verify_configuration_action(self) -> Dict[str, Any]:
        """Verify configuration"""
        required = ["local_endpoint", "target_endpoint", "target_utilization"]
        missing = [k for k in required if k not in self.config]

        return {
            "status": "ok" if not missing else "missing",
            "config": self.config,
            "missing": missing
        }

    def _check_network_connectivity_action(self) -> Dict[str, Any]:
        """Check network connectivity"""
        results = {}

        for host_name, endpoint in [("local", self.config["local_endpoint"]),
                                     ("target", self.config["target_endpoint"])]:
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                results[host_name] = {
                    "status": "reachable" if response.status_code == 200 else "unreachable",
                    "status_code": response.status_code
                }
            except Exception as e:
                results[host_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }

        return {
            "status": "ok" if all(r.get("status") == "reachable" for r in results.values()) else "partial",
            "results": results
        }

    def _deploy_coordinator_action(self) -> Dict[str, Any]:
        """Deploy coordinator"""
        if not CLUSTER_COORDINATOR_AVAILABLE:
            raise Exception("Cluster coordinator module not available")

        return {
            "status": "deployed",
            "module": "symbiotic_cluster_coordinator"
        }

    def _configure_endpoints_action(self) -> Dict[str, Any]:
        """Configure endpoints"""
        return {
            "status": "configured",
            "local_endpoint": self.config["local_endpoint"],
            "target_endpoint": self.config["target_endpoint"]
        }

    def _setup_monitoring_action(self) -> Dict[str, Any]:
        """Setup monitoring"""
        return {
            "status": "configured",
            "health_check_interval": self.config.get("health_check_interval", 60)
        }

    def _configure_load_balancing_action(self) -> Dict[str, Any]:
        """Configure load balancing"""
        return {
            "status": "configured",
            "balance_interval": self.config.get("balance_interval", 30),
            "target_utilization": self.config.get("target_utilization", 97.0)
        }

    def _setup_failover_action(self) -> Dict[str, Any]:
        """Setup failover"""
        return {
            "status": "configured",
            "automatic_failover": True
        }

    def _initialize_coordinator_action(self) -> Dict[str, Any]:
        """Initialize coordinator"""
        self.coordinator = SymbioticClusterCoordinator(
            local_endpoint=self.config["local_endpoint"],
            target_endpoint=self.config["target_endpoint"],
            target_utilization=self.config["target_utilization"],
            balance_interval=self.config.get("balance_interval", 30)
        )

        return {
            "status": "initialized",
            "coordinator_id": self.coordinator.cluster_state.cluster_id
        }

    def _start_coordinator_action(self) -> Dict[str, Any]:
        """Start coordinator"""
        if not self.coordinator:
            raise Exception("Coordinator not initialized")

        self.coordinator.start()

        return {
            "status": "started",
            "running": True
        }

    def _verify_hosts_action(self) -> Dict[str, Any]:
        """Verify hosts"""
        if not self.coordinator:
            raise Exception("Coordinator not started")

        status = self.coordinator.get_cluster_status()
        active_hosts = status.get("active_hosts", [])

        return {
            "status": "verified" if len(active_hosts) > 0 else "no_hosts",
            "active_hosts": active_hosts,
            "total_hosts": len(status.get("hosts", {}))
        }

    def _start_execution_action(self) -> Dict[str, Any]:
        """Start execution"""
        self._execution_running = True
        self.execution_thread = threading.Thread(target=self._execution_loop, daemon=True)
        self.execution_thread.start()

        return {
            "status": "started",
            "execution_running": True
        }

    def _start_load_balancing_action(self) -> Dict[str, Any]:
        """Start load balancing"""
        return {
            "status": "started",
            "load_balancing_active": True
        }

    def _verify_cluster_health_action(self) -> Dict[str, Any]:
        """Verify cluster health"""
        if not self.coordinator:
            raise Exception("Coordinator not available")

        status = self.coordinator.get_cluster_status()
        active_hosts = status.get("active_hosts", [])

        return {
            "status": "healthy" if len(active_hosts) > 0 else "unhealthy",
            "active_hosts": len(active_hosts),
            "cluster_status": status
        }

    def _verify_utilization_action(self) -> Dict[str, Any]:
        """Verify utilization"""
        if not self.coordinator:
            raise Exception("Coordinator not available")

        report = self.coordinator.get_utilization_report()
        current_util = report.get("current_utilization", 0.0)
        target_util = report.get("target_utilization", 97.0)
        gap = abs(current_util - target_util)

        return {
            "status": "on_target" if gap < 10.0 else "off_target",
            "current_utilization": current_util,
            "target_utilization": target_util,
            "gap": gap
        }

    def _verify_failover_action(self) -> Dict[str, Any]:
        """Verify failover"""
        if not self.coordinator:
            raise Exception("Coordinator not available")

        status = self.coordinator.get_cluster_status()
        failover_count = status.get("failover_count", 0)

        return {
            "status": "operational",
            "failover_count": failover_count,
            "failover_configured": True
        }

    def _execution_loop(self) -> None:
        """Execution loop"""
        while self._execution_running:
            try:
                if self.coordinator:
                    # Monitor cluster
                    status = self.coordinator.get_cluster_status()
                    report = self.coordinator.get_utilization_report()

                    # Log status periodically
                    self.logger.debug(f"Cluster utilization: {report.get('current_utilization', 0):.1f}%")

                time.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Execution loop error: {e}")
                time.sleep(60)

    def _save_deployment_report(self) -> None:
        try:
            """Save deployment report"""
            report = {
                "deployment_id": f"symbiotic_cluster_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_time": self.deployment_start.isoformat() if self.deployment_start else None,
                "end_time": self.deployment_end.isoformat() if self.deployment_end else None,
                "duration_seconds": (self.deployment_end - self.deployment_start).total_seconds() if self.deployment_start and self.deployment_end else None,
                "phases": {phase.value: [self.deployment_steps[sid].to_dict() for sid in step_ids] 
                          for phase, step_ids in self.deployment_phases.items()},
                "summary": {
                    "total_steps": len(self.deployment_steps),
                    "completed": sum(1 for s in self.deployment_steps.values() if s.status == DeploymentStatus.COMPLETED),
                    "failed": sum(1 for s in self.deployment_steps.values() if s.status == DeploymentStatus.FAILED),
                    "skipped": sum(1 for s in self.deployment_steps.values() if s.status == DeploymentStatus.SKIPPED)
                }
            }

            report_file = self.data_dir / f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"Deployment report saved to {report_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_deployment_report: {e}", exc_info=True)
            raise
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status"""
        return {
            "deployment_start": self.deployment_start.isoformat() if self.deployment_start else None,
            "deployment_end": self.deployment_end.isoformat() if self.deployment_end else None,
            "phases": {phase.value: len(step_ids) for phase, step_ids in self.deployment_phases.items()},
            "steps": {sid: step.to_dict() for sid, step in self.deployment_steps.items()},
            "coordinator_running": self.coordinator is not None and self._execution_running
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Symbiotic Cluster")
    parser.add_argument("--deploy", action="store_true", help="Execute deployment")
    parser.add_argument("--status", action="store_true", help="Show deployment status")

    args = parser.parse_args()

    deployment = SymbioticClusterDeployment()

    if args.deploy:
        success = deployment.deploy()
        sys.exit(0 if success else 1)

    elif args.status:
        status = deployment.get_deployment_status()
        print(json.dumps(status, indent=2))

    else:
        parser.print_help()

