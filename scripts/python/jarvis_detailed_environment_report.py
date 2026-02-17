#!/usr/bin/env python3
"""
JARVIS Detailed Environment Report #1

Comprehensive environment status report covering all systems,
clusters, integrations, and current operational state.

Tags: #JARVIS #ENVIRONMENT-REPORT #SYSTEM-STATUS #COMPREHENSIVE
"""

import sys
import json
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEnvironmentReport")


class JARVISDetailedEnvironmentReport:
    """
    JARVIS Detailed Environment Report

    Comprehensive report covering all systems, clusters, integrations,
    and operational status.
    """

    def __init__(self, project_root: Path):
        """Initialize JARVIS Environment Report"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.reports_path = self.data_path / "jarvis_reports"
        self.reports_path.mkdir(parents=True, exist_ok=True)

        # Report file
        self.report_file = self.reports_path / f"environment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        self.logger.info("📊 JARVIS Detailed Environment Report initialized")
        self.logger.info("   Report #1: Comprehensive system status")

    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.project_root))

            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "status": "normal" if cpu_percent < 80 else "high"
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_percent": memory.percent,
                    "status": "normal" if memory.percent < 80 else "high"
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "used_percent": (disk.used / disk.total) * 100,
                    "status": "normal" if (disk.used / disk.total) * 100 < 90 else "high"
                }
            }
        except Exception as e:
            self.logger.warning(f"⚠️  Error getting system resources: {e}")
            return {"error": str(e)}

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status"""
        try:
            from jarvis_ultron_hybrid_cluster import ULTRONHybridCluster
            cluster = ULTRONHybridCluster(self.project_root)
            status = cluster.get_cluster_status()
            return {
                "available": True,
                "status": status
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def get_fan_performance(self) -> Dict[str, Any]:
        """Get fan performance metrics"""
        try:
            from fan_performance_monitor import FanPerformanceMonitor
            monitor = FanPerformanceMonitor(self.project_root)
            metrics = monitor.get_comprehensive_metrics()
            return {
                "available": True,
                "metrics": metrics
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def get_perpetual_motion(self) -> Dict[str, Any]:
        """Get perpetual motion status"""
        try:
            from lumina_perpetual_motion_engine import LUMINAPerpetualMotionEngine
            engine = LUMINAPerpetualMotionEngine(self.project_root)
            mission = engine.get_mission_status()
            return {
                "available": True,
                "mission": mission
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def get_secteam_status(self) -> Dict[str, Any]:
        """Get @SECTEAM status"""
        try:
            from secteam_coordinator import SECTEAMCoordinator
            secteam = SECTEAMCoordinator(self.project_root)
            tools = list(secteam.tools.keys())
            return {
                "available": True,
                "tools_count": len(tools),
                "tools": tools
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def get_convergence_status(self) -> Dict[str, Any]:
        """Get perfect celestial quantum convergence status"""
        try:
            from perfect_celestial_quantum_convergence import PerfectCelestialQuantumConvergence
            convergence = PerfectCelestialQuantumConvergence(self.project_root)
            return {
                "available": True,
                "convergence_detected": convergence.convergence_detected,
                "ship_detected": convergence.ship_detected,
                "universes_merged": convergence.universes_merged
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def get_cluster_testing_status(self) -> Dict[str, Any]:
        """Get cluster testing status"""
        try:
            from full_cluster_testing_model_pairing_tuning import FullClusterTesting
            testing = FullClusterTesting(self.project_root)
            return {
                "available": True,
                "status": "active"
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def get_docker_model_mapping(self) -> Dict[str, Any]:
        """Get Docker container to actual model mapping"""
        try:
            from docker_model_mapper import DockerModelMapper
            mapper = DockerModelMapper(self.project_root)
            mapping = mapper.map_all_containers_to_models()
            return {
                "available": True,
                "mapping": mapping
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def generate_detailed_report(self) -> Dict[str, Any]:
        """Generate comprehensive detailed environment report"""
        self.logger.info("📊 Generating JARVIS Detailed Environment Report #1...")

        report = {
            "report_number": 1,
            "report_type": "detailed_environment",
            "timestamp": datetime.now().isoformat(),
            "generated_by": "JARVIS",
            "project_root": str(self.project_root),
            "sections": {}
        }

        # Section 1: System Resources
        self.logger.info("   📊 System Resources...")
        report["sections"]["system_resources"] = self.get_system_resources()

        # Section 2: Cluster Status
        self.logger.info("   🌀 Cluster Status...")
        report["sections"]["cluster_status"] = self.get_cluster_status()

        # Section 3: Fan Performance
        self.logger.info("   🌪️  Fan Performance...")
        report["sections"]["fan_performance"] = self.get_fan_performance()

        # Section 4: Perpetual Motion
        self.logger.info("   ♾️  Perpetual Motion...")
        report["sections"]["perpetual_motion"] = self.get_perpetual_motion()

        # Section 5: @SECTEAM Status
        self.logger.info("   🛡️  @SECTEAM Status...")
        report["sections"]["secteam_status"] = self.get_secteam_status()

        # Section 6: Convergence Status
        self.logger.info("   🌌 Convergence Status...")
        report["sections"]["convergence_status"] = self.get_convergence_status()

        # Section 7: Cluster Testing
        self.logger.info("   🧪 Cluster Testing...")
        report["sections"]["cluster_testing"] = self.get_cluster_testing_status()

        # Section 8: Docker Model Mapping
        self.logger.info("   🔍 Docker Model Mapping...")
        report["sections"]["docker_model_mapping"] = self.get_docker_model_mapping()

        # Section 9: System Summary
        report["sections"]["summary"] = self._generate_summary(report["sections"])

        # Save report
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Report saved: {self.report_file.name}")
        except Exception as e:
            self.logger.error(f"❌ Error saving report: {e}")

        self.logger.info("✅ JARVIS Detailed Environment Report #1: COMPLETE")

        return report

    def _generate_summary(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary section"""
        summary = {
            "total_sections": len(sections),
            "systems_operational": 0,
            "systems_available": 0,
            "status": "operational"
        }

        # Count operational systems
        for section_name, section_data in sections.items():
            if isinstance(section_data, dict):
                if section_data.get("available", False):
                    summary["systems_available"] += 1
                if section_data.get("status") == "operational" or section_data.get("available", False):
                    summary["systems_operational"] += 1

        return summary

    def get_formatted_report(self) -> str:
        """Get formatted markdown report"""
        report = self.generate_detailed_report()

        markdown = []
        markdown.append("# 📊 JARVIS Detailed Environment Report #1")
        markdown.append("")
        markdown.append(f"**Generated:** {report['timestamp']}")
        markdown.append(f"**Report Number:** {report['report_number']}")
        markdown.append(f"**Generated By:** {report['generated_by']}")
        markdown.append("")

        sections = report.get("sections", {})

        # System Resources
        if "system_resources" in sections:
            resources = sections["system_resources"]
            if "error" not in resources:
                markdown.append("## 💻 System Resources")
                markdown.append("")
                cpu = resources.get("cpu", {})
                memory = resources.get("memory", {})
                disk = resources.get("disk", {})

                markdown.append("### CPU")
                markdown.append(f"- **Usage:** {cpu.get('percent', 0):.1f}%")
                markdown.append(f"- **Cores:** {cpu.get('count', 0)}")
                markdown.append(f"- **Status:** {cpu.get('status', 'unknown')}")
                markdown.append("")

                markdown.append("### Memory")
                markdown.append(f"- **Total:** {memory.get('total_gb', 0):.2f} GB")
                markdown.append(f"- **Available:** {memory.get('available_gb', 0):.2f} GB")
                markdown.append(f"- **Used:** {memory.get('used_percent', 0):.1f}%")
                markdown.append(f"- **Status:** {memory.get('status', 'unknown')}")
                markdown.append("")

                markdown.append("### Disk")
                markdown.append(f"- **Total:** {disk.get('total_gb', 0):.2f} GB")
                markdown.append(f"- **Free:** {disk.get('free_gb', 0):.2f} GB")
                markdown.append(f"- **Used:** {disk.get('used_percent', 0):.1f}%")
                markdown.append(f"- **Status:** {disk.get('status', 'unknown')}")
                markdown.append("")

        # Cluster Status
        if "cluster_status" in sections:
            cluster = sections["cluster_status"]
            markdown.append("## 🌀 ULTRON Hybrid Cluster")
            markdown.append("")
            if cluster.get("available"):
                status = cluster.get("status", {})
                markdown.append(f"- **Status:** {'✅ Operational' if status.get('healthy_nodes', 0) > 0 else '❌ Offline'}")
                markdown.append(f"- **Healthy Nodes:** {status.get('healthy_nodes', 0)}/{status.get('total_nodes', 0)}")
                markdown.append(f"- **Cluster Name:** {status.get('cluster_name', 'Unknown')}")
                markdown.append(f"- **Cluster Type:** {status.get('cluster_type', 'Unknown')}")
            else:
                markdown.append(f"- **Status:** ❌ Unavailable ({cluster.get('error', 'Unknown error')})")
            markdown.append("")

        # Fan Performance
        if "fan_performance" in sections:
            fan = sections["fan_performance"]
            markdown.append("## 🌪️  Fan Performance (WARP FACTOR TEN+)")
            markdown.append("")
            if fan.get("available"):
                metrics = fan.get("metrics", {})
                decibels = metrics.get("decibels", {})
                rpm = metrics.get("rpm", {})
                flowrate = metrics.get("flowrate", {})

                markdown.append(f"- **Decibels:** {decibels.get('overall_db', 'N/A')} dB")
                markdown.append(f"- **CPU Fan RPM:** {rpm.get('cpu_fan_rpm', 'N/A')}")
                markdown.append(f"- **Total Flowrate:** {flowrate.get('total_flowrate', 'N/A')} CFM")
            else:
                markdown.append(f"- **Status:** ❌ Unavailable ({fan.get('error', 'Unknown error')})")
            markdown.append("")

        # Perpetual Motion
        if "perpetual_motion" in sections:
            motion = sections["perpetual_motion"]
            markdown.append("## ♾️  Perpetual Motion Engine")
            markdown.append("")
            if motion.get("available"):
                mission = motion.get("mission", {})
                markdown.append(f"- **Mission:** {mission.get('mission_name', 'Unknown')}")
                markdown.append(f"- **Status:** {mission.get('status', 'Unknown')}")
                markdown.append(f"- **Progress:** {mission.get('progress', 0):.2%}")
                markdown.append(f"- **Destination:** {mission.get('destination', 'Unknown')}")
            else:
                markdown.append(f"- **Status:** ❌ Unavailable ({motion.get('error', 'Unknown error')})")
            markdown.append("")

        # @SECTEAM Status
        if "secteam_status" in sections:
            secteam = sections["secteam_status"]
            markdown.append("## 🛡️  @SECTEAM Coordinator")
            markdown.append("")
            if secteam.get("available"):
                markdown.append(f"- **Status:** ✅ Active")
                markdown.append(f"- **Tools Available:** {secteam.get('tools_count', 0)}")
                markdown.append("**Tools:**")
                for tool in secteam.get("tools", []):
                    markdown.append(f"  - {tool}")
            else:
                markdown.append(f"- **Status:** ❌ Unavailable ({secteam.get('error', 'Unknown error')})")
            markdown.append("")

        # Convergence Status
        if "convergence_status" in sections:
            convergence = sections["convergence_status"]
            markdown.append("## 🌌 Perfect Celestial Quantum Convergence")
            markdown.append("")
            if convergence.get("available"):
                markdown.append(f"- **Convergence Detected:** {'✅ Yes' if convergence.get('convergence_detected') else '❌ No'}")
                markdown.append(f"- **@SHIP Detected:** {'✅ Yes' if convergence.get('ship_detected') else '❌ No'}")
                markdown.append(f"- **Universes Merged:** {'✅ Yes' if convergence.get('universes_merged') else '❌ No'}")
            else:
                markdown.append(f"- **Status:** ❌ Unavailable ({convergence.get('error', 'Unknown error')})")
            markdown.append("")

        # Cluster Testing
        if "cluster_testing" in sections:
            testing = sections["cluster_testing"]
            markdown.append("## 🧪 Full Cluster Testing")
            markdown.append("")
            if testing.get("available"):
                markdown.append(f"- **Status:** ✅ Active")
            else:
                markdown.append(f"- **Status:** ❌ Unavailable ({testing.get('error', 'Unknown error')})")
            markdown.append("")

        # Docker Model Mapping
        if "docker_model_mapping" in sections:
            docker_mapping = sections["docker_model_mapping"]
            markdown.append("## 🔍 Docker Model Mapping (Actual @AI @LLM #Models)")
            markdown.append("")
            if docker_mapping.get("available"):
                mapping = docker_mapping.get("mapping", {})
                markdown.append(f"- **Total Containers:** {mapping.get('total_containers', 0)}")
                markdown.append(f"- **LLM Containers:** {mapping.get('llm_containers', 0)}")
                markdown.append(f"- **Ollama Containers:** {mapping.get('ollama_containers', 0)}")
                markdown.append(f"- **Containers with Models:** {mapping.get('containers_with_models', 0)}")
                markdown.append("")
                markdown.append("**Actual Models (Not Docker Aliases):**")
                markdown.append("")
                for container_map in mapping.get("mappings", []):
                    if container_map.get("actual_models"):
                        markdown.append(f"### {container_map['container_name']}")
                        markdown.append(f"**Docker Image:** `{container_map['docker_image']}`")
                        markdown.append("**Actual Models:**")
                        for model in container_map["actual_models"]:
                            model_name = model.get("name", "Unknown")
                            markdown.append(f"- **{model_name}**")
                        markdown.append("")
            else:
                markdown.append(f"- **Status:** ❌ Unavailable ({docker_mapping.get('error', 'Unknown error')})")
            markdown.append("")

        # Summary
        if "summary" in sections:
            summary = sections["summary"]
            markdown.append("## 📊 Summary")
            markdown.append("")
            markdown.append(f"- **Total Sections:** {summary.get('total_sections', 0)}")
            markdown.append(f"- **Systems Available:** {summary.get('systems_available', 0)}")
            markdown.append(f"- **Systems Operational:** {summary.get('systems_operational', 0)}")
            markdown.append(f"- **Overall Status:** {summary.get('status', 'unknown')}")
            markdown.append("")

        markdown.append("---")
        markdown.append("")
        markdown.append(f"**Report File:** {self.report_file.name}")
        markdown.append(f"**Generated:** {report['timestamp']}")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Detailed Environment Report #1")
        parser.add_argument("--generate", action="store_true", help="Generate detailed report")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        reporter = JARVISDetailedEnvironmentReport(project_root)

        if args.generate or args.json:
            report = reporter.generate_detailed_report()
            if args.json:
                print(json.dumps(report, indent=2, default=str))
            else:
                print("✅ JARVIS Detailed Environment Report #1: GENERATED")
                print(f"   Report saved: {reporter.report_file.name}")
        else:
            report = reporter.get_formatted_report()
            print(report)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()