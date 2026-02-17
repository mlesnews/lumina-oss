#!/usr/bin/env python3
"""
JARVIS #HOMELAB Body Health Audit

Focused audit of all #HOMELAB infrastructure systems that make up the body.
@BODY = #HOMELAB

Tags: #JARVIS #HOMELAB #BODY_HEALTH #AUDIT #BODY @JARVIS @LUMINA @DOIT
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISHomelabBodyHealthAudit")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class HomelabSystemType(Enum):
    """Homelab system types"""
    AI_CLUSTER = "ai_cluster"  # ULTRON, KAIJU
    STORAGE = "storage"  # NAS
    NETWORK = "network"  # Network infrastructure
    SERVICE = "service"  # Services (n8n, etc.)
    CONTAINER = "container"  # Docker containers
    MCP_SERVER = "mcp_server"  # MCP servers


@dataclass
class HomelabSystemHealth:
    """Health status of a homelab system"""
    system_id: str
    system_name: str
    system_type: HomelabSystemType
    status: str  # healthy, degraded, down, unknown
    health_score: float  # 0-100
    endpoint: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    last_checked: str = ""
    issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HomelabBodyHealthAuditResult:
    """Homelab body health audit result"""
    timestamp: str
    overall_health_score: float
    overall_status: str
    total_systems: int
    healthy_systems: int
    degraded_systems: int
    down_systems: int
    unknown_systems: int
    systems: Dict[str, HomelabSystemHealth]
    critical_issues: List[str]
    recommendations: List[str]
    action_plan: List[str]


class JARVISHomelabBodyHealthAudit:
    """
    JARVIS #HOMELAB Body Health Audit

    @BODY = #HOMELAB
    Focused audit of all homelab infrastructure systems.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "jarvis_homelab_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

        # Homelab systems registry
        self.homelab_systems: Dict[str, HomelabSystemHealth] = {}

        # Initialize homelab systems
        self._initialize_homelab_systems()

    def _initialize_homelab_systems(self):
        """Initialize all #HOMELAB systems"""
        self.logger.info("=" * 80)
        self.logger.info("🏠 INITIALIZING #HOMELAB BODY SYSTEMS")
        self.logger.info("=" * 80)
        self.logger.info("")

        # ULTRON - Local AI Cluster
        self.homelab_systems["ultron"] = HomelabSystemHealth(
            system_id="ultron",
            system_name="ULTRON - Local AI Cluster",
            system_type=HomelabSystemType.AI_CLUSTER,
            status="unknown",
            health_score=0.0,
            endpoint="http://localhost:11434",
            capabilities=["local_ai_processing", "ollama_server", "model_hosting"],
            last_checked=""
        )

        # KAIJU - Network AI Cluster
        self.homelab_systems["kaiju"] = HomelabSystemHealth(
            system_id="kaiju",
            system_name="KAIJU Number Eight - Network AI Cluster",
            system_type=HomelabSystemType.AI_CLUSTER,
            status="unknown",
            health_score=0.0,
            endpoint="http://<NAS_IP>:11434",
            capabilities=["network_ai_processing", "iron_legion_host", "ollama_server"],
            last_checked=""
        )

        # NAS - Storage System
        self.homelab_systems["nas"] = HomelabSystemHealth(
            system_id="nas",
            system_name="NAS DS2118+ - Storage System",
            system_type=HomelabSystemType.STORAGE,
            status="unknown",
            health_score=0.0,
            endpoint="\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups",
            capabilities=["network_storage", "backup_storage", "data_archival"],
            last_checked=""
        )

        # Docker Desktop MCP Toolkit
        self.homelab_systems["docker_desktop"] = HomelabSystemHealth(
            system_id="docker_desktop",
            system_name="Docker Desktop - Container Platform",
            system_type=HomelabSystemType.CONTAINER,
            status="unknown",
            health_score=0.0,
            endpoint="docker://localhost",
            capabilities=["container_management", "volume_management", "mcp_servers"],
            last_checked=""
        )

        # n8n - Workflow Automation
        self.homelab_systems["n8n"] = HomelabSystemHealth(
            system_id="n8n",
            system_name="n8n - Workflow Automation",
            system_type=HomelabSystemType.SERVICE,
            status="unknown",
            health_score=0.0,
            endpoint="http://localhost:5678",
            capabilities=["workflow_automation", "api_integration", "webhook_processing"],
            last_checked=""
        )

        # MCP Servers
        self.homelab_systems["mcp_servers"] = HomelabSystemHealth(
            system_id="mcp_servers",
            system_name="MCP Servers - Model Context Protocol",
            system_type=HomelabSystemType.MCP_SERVER,
            status="unknown",
            health_score=0.0,
            endpoint="mcp://localhost",
            capabilities=["model_context", "tool_execution", "resource_management"],
            last_checked=""
        )

        self.logger.info(f"✅ Initialized {len(self.homelab_systems)} #HOMELAB systems")
        self.logger.info("")

    def check_system_health(self, system: HomelabSystemHealth) -> HomelabSystemHealth:
        """Check health of a specific homelab system"""
        system.last_checked = datetime.now().isoformat()

        try:
            # Check based on system type
            if system.system_type == HomelabSystemType.AI_CLUSTER:
                health = self._check_ai_cluster(system)
            elif system.system_type == HomelabSystemType.STORAGE:
                health = self._check_storage(system)
            elif system.system_type == HomelabSystemType.CONTAINER:
                health = self._check_container(system)
            elif system.system_type == HomelabSystemType.SERVICE:
                health = self._check_service(system)
            elif system.system_type == HomelabSystemType.MCP_SERVER:
                health = self._check_mcp_server(system)
            else:
                health = system

            return health

        except Exception as e:
            self.logger.warning(f"⚠️  Error checking {system.system_name}: {e}")
            system.status = "unknown"
            system.health_score = 0.0
            system.issues.append(f"Check error: {str(e)}")
            return system

    def _check_ai_cluster(self, system: HomelabSystemHealth) -> HomelabSystemHealth:
        """Check AI cluster health"""
        import requests

        try:
            # Try to ping Ollama endpoint
            response = requests.get(f"{system.endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                system.status = "healthy"
                system.health_score = 100.0
                models = response.json().get("models", [])
                system.metadata["model_count"] = len(models)
            else:
                system.status = "degraded"
                system.health_score = 50.0
                system.issues.append(f"HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            system.status = "down"
            system.health_score = 0.0
            system.issues.append("Connection refused")
        except requests.exceptions.Timeout:
            system.status = "degraded"
            system.health_score = 30.0
            system.issues.append("Connection timeout")
        except Exception as e:
            system.status = "unknown"
            system.health_score = 0.0
            system.issues.append(f"Error: {str(e)}")

        return system

    def _check_storage(self, system: HomelabSystemHealth) -> HomelabSystemHealth:
        """Check storage system health"""
        try:
            # Check if NAS path is accessible
            if system.endpoint.startswith("\\\\"):
                # Windows network path
                import os
                if os.path.exists(system.endpoint):
                    system.status = "healthy"
                    system.health_score = 100.0
                else:
                    system.status = "down"
                    system.health_score = 0.0
                    system.issues.append("Path not accessible")
            else:
                # Try HTTP/HTTPS
                import requests
                try:
                    response = requests.get(system.endpoint, timeout=5)
                    if response.status_code == 200:
                        system.status = "healthy"
                        system.health_score = 100.0
                    else:
                        system.status = "degraded"
                        system.health_score = 50.0
                        system.issues.append(f"HTTP {response.status_code}")
                except:
                    system.status = "unknown"
                    system.health_score = 0.0
                    system.issues.append("Connection failed")
        except Exception as e:
            system.status = "unknown"
            system.health_score = 0.0
            system.issues.append(f"Error: {str(e)}")

        return system

    def _check_container(self, system: HomelabSystemHealth) -> HomelabSystemHealth:
        """Check container platform health"""
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                container_count = len(containers) - 1  # Subtract header
                system.status = "healthy"
                system.health_score = 100.0
                system.metadata["container_count"] = container_count
            else:
                system.status = "degraded"
                system.health_score = 50.0
                system.issues.append("Docker command failed")
        except FileNotFoundError:
            system.status = "down"
            system.health_score = 0.0
            system.issues.append("Docker not installed")
        except Exception as e:
            system.status = "unknown"
            system.health_score = 0.0
            system.issues.append(f"Error: {str(e)}")

        return system

    def _check_service(self, system: HomelabSystemHealth) -> HomelabSystemHealth:
        """Check service health"""
        try:
            import requests
            response = requests.get(system.endpoint, timeout=5)
            if response.status_code == 200:
                system.status = "healthy"
                system.health_score = 100.0
            else:
                system.status = "degraded"
                system.health_score = 50.0
                system.issues.append(f"HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            system.status = "down"
            system.health_score = 0.0
            system.issues.append("Service not running")
        except Exception as e:
            system.status = "unknown"
            system.health_score = 0.0
            system.issues.append(f"Error: {str(e)}")

        return system

    def _check_mcp_server(self, system: HomelabSystemHealth) -> HomelabSystemHealth:
        """Check MCP server health"""
        try:
            # Check MCP server status via config
            mcp_config_dir = self.project_root / "config" / "mcp"
            if mcp_config_dir.exists():
                config_files = list(mcp_config_dir.glob("*.json"))
                system.status = "healthy"
                system.health_score = 100.0
                system.metadata["config_count"] = len(config_files)
            else:
                system.status = "degraded"
                system.health_score = 50.0
                system.issues.append("MCP config directory not found")
        except Exception as e:
            system.status = "unknown"
            system.health_score = 0.0
            system.issues.append(f"Error: {str(e)}")

        return system

    def audit_homelab_body_health(self) -> HomelabBodyHealthAuditResult:
        """
        Perform comprehensive audit of all #HOMELAB body systems

        @BODY = #HOMELAB
        """
        self.logger.info("=" * 80)
        self.logger.info("🏠 #HOMELAB BODY HEALTH AUDIT")
        self.logger.info("   @BODY = #HOMELAB")
        self.logger.info("=" * 80)
        self.logger.info("")

        # Check all systems
        self.logger.info("Checking #HOMELAB systems...")
        self.logger.info("")

        for system_id, system in self.homelab_systems.items():
            self.logger.info(f"Checking {system.system_name}...")
            checked_system = self.check_system_health(system)
            self.homelab_systems[system_id] = checked_system

            status_icon = "✅" if checked_system.status == "healthy" else "⚠️" if checked_system.status == "degraded" else "❌"
            self.logger.info(f"   {status_icon} {checked_system.status.upper()} - Score: {checked_system.health_score:.0f}/100")
            if checked_system.issues:
                for issue in checked_system.issues:
                    self.logger.info(f"      Issue: {issue}")

        self.logger.info("")

        # Calculate overall health
        healthy_count = sum(1 for s in self.homelab_systems.values() if s.status == "healthy")
        degraded_count = sum(1 for s in self.homelab_systems.values() if s.status == "degraded")
        down_count = sum(1 for s in self.homelab_systems.values() if s.status == "down")
        unknown_count = sum(1 for s in self.homelab_systems.values() if s.status == "unknown")

        total_systems = len(self.homelab_systems)

        if total_systems > 0:
            overall_health_score = (healthy_count / total_systems) * 100
        else:
            overall_health_score = 0.0

        # Adjust for degraded/down systems
        overall_health_score -= (degraded_count * 10) + (down_count * 20)
        overall_health_score = max(0, min(100, overall_health_score))

        overall_status = "healthy" if overall_health_score >= 80 else "degraded" if overall_health_score >= 50 else "critical"

        # Collect critical issues
        critical_issues = []
        for system in self.homelab_systems.values():
            if system.status == "down" or (system.status == "degraded" and system.health_score < 50):
                critical_issues.append(f"{system.system_name}: {', '.join(system.issues) if system.issues else 'Status: ' + system.status}")

        # Generate recommendations
        recommendations = self._generate_recommendations()
        action_plan = self._generate_action_plan()

        # Create result
        result = HomelabBodyHealthAuditResult(
            timestamp=datetime.now().isoformat(),
            overall_health_score=overall_health_score,
            overall_status=overall_status,
            total_systems=total_systems,
            healthy_systems=healthy_count,
            degraded_systems=degraded_count,
            down_systems=down_count,
            unknown_systems=unknown_count,
            systems={k: v for k, v in self.homelab_systems.items()},
            critical_issues=critical_issues,
            recommendations=recommendations,
            action_plan=action_plan
        )

        # Save result
        self._save_audit_result(result)

        # Display summary
        self._display_summary(result)

        return result

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        down_count = sum(1 for s in self.homelab_systems.values() if s.status == "down")
        degraded_count = sum(1 for s in self.homelab_systems.values() if s.status == "degraded")

        if down_count > 0:
            recommendations.append(f"🚨 URGENT: {down_count} systems are DOWN - immediate attention required")

        if degraded_count > 0:
            recommendations.append(f"⚠️  HIGH PRIORITY: {degraded_count} systems are DEGRADED - investigate and restore")

        if not recommendations:
            recommendations.append("✅ All #HOMELAB systems are healthy - continue monitoring")

        return recommendations

    def _generate_action_plan(self) -> List[str]:
        """Generate action plan"""
        actions = []

        for system in self.homelab_systems.values():
            if system.status == "down":
                actions.append(f"URGENT: Restore {system.system_name} - {', '.join(system.issues[:2])}")
            elif system.status == "degraded" and system.health_score < 50:
                actions.append(f"HIGH: Fix {system.system_name} - {', '.join(system.issues[:2])}")

        if not actions:
            actions.append("No immediate actions required - all systems healthy")

        return actions[:10]  # Top 10 actions

    def _save_audit_result(self, result: HomelabBodyHealthAuditResult):
        """Save audit result"""
        try:
            audit_file = self.data_dir / f"homelab_body_health_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Convert to dict
            result_dict = {
                "timestamp": result.timestamp,
                "overall_health_score": result.overall_health_score,
                "overall_status": result.overall_status,
                "total_systems": result.total_systems,
                "healthy_systems": result.healthy_systems,
                "degraded_systems": result.degraded_systems,
                "down_systems": result.down_systems,
                "unknown_systems": result.unknown_systems,
                "systems": {
                    k: {
                        "system_id": v.system_id,
                        "system_name": v.system_name,
                        "system_type": v.system_type.value,
                        "status": v.status,
                        "health_score": v.health_score,
                        "endpoint": v.endpoint,
                        "capabilities": v.capabilities,
                        "last_checked": v.last_checked,
                        "issues": v.issues,
                        "metadata": v.metadata
                    }
                    for k, v in result.systems.items()
                },
                "critical_issues": result.critical_issues,
                "recommendations": result.recommendations,
                "action_plan": result.action_plan
            }

            with open(audit_file, 'w') as f:
                json.dump(result_dict, f, indent=2, default=str)

            self.logger.info(f"📄 Audit result saved: {audit_file}")

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to save audit result: {e}")

    def _display_summary(self, result: HomelabBodyHealthAuditResult):
        """Display audit summary"""
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("📊 #HOMELAB BODY HEALTH AUDIT SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info("")
        self.logger.info(f"Overall Health Score: {result.overall_health_score:.1f}/100")
        self.logger.info(f"Overall Status: {result.overall_status.upper()}")
        self.logger.info("")
        self.logger.info(f"#HOMELAB Systems:")
        self.logger.info(f"   Total: {result.total_systems}")
        self.logger.info(f"   Healthy: {result.healthy_systems}")
        self.logger.info(f"   Degraded: {result.degraded_systems}")
        self.logger.info(f"   Down: {result.down_systems}")
        self.logger.info(f"   Unknown: {result.unknown_systems}")
        self.logger.info("")

        if result.critical_issues:
            self.logger.info("🚨 CRITICAL ISSUES:")
            for issue in result.critical_issues[:5]:
                self.logger.info(f"   - {issue}")
            self.logger.info("")

        if result.recommendations:
            self.logger.info("💡 RECOMMENDATIONS:")
            for rec in result.recommendations:
                self.logger.info(f"   {rec}")
            self.logger.info("")

        self.logger.info("=" * 80)
        self.logger.info("")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS #HOMELAB Body Health Audit")
    parser.add_argument('--project-root', type=Path, help='Project root directory')

    args = parser.parse_args()

    auditor = JARVISHomelabBodyHealthAudit(project_root=args.project_root or PROJECT_ROOT)
    result = auditor.audit_homelab_body_health()

    return 0 if result.overall_status != "critical" else 1


if __name__ == "__main__":


    sys.exit(main())