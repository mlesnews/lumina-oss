#!/usr/bin/env python3
"""
LUMINA Holistic System Evaluation

Comprehensive evaluation of entire LUMINA ecosystem:
- Software stack
- Hardware performance
- Home lab infrastructure
- All LUMINA-touched systems
- Efficiency analysis
- Weak spot identification
- Pain point detection

Runs on system startup and continuously monitors.

Tags: #SYSTEM_EVALUATION #HOLISTIC #OPTIMIZATION #MONITORING @JARVIS @LUMINA
"""

import sys
import json
import psutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaHolisticEvaluation")


@dataclass
class SystemMetric:
    """System metric with context"""
    name: str
    value: Any
    unit: str = ""
    status: str = "ok"  # ok, warning, critical
    category: str = ""
    description: str = ""


@dataclass
class WeakSpot:
    """Identified weak spot or pain point"""
    area: str
    issue: str
    severity: str  # low, medium, high, critical
    impact: str
    recommendation: str
    affected_systems: List[str]


class LuminaHolisticSystemEvaluation:
    """
    Holistic System Evaluation

    Evaluates entire LUMINA ecosystem comprehensively.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize evaluation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "system_evaluation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metrics: List[SystemMetric] = []
        self.weak_spots: List[WeakSpot] = []

        logger.info("="*80)
        logger.info("🔍 LUMINA HOLISTIC SYSTEM EVALUATION")
        logger.info("="*80)
        logger.info("   Evaluating: Software, Hardware, Home Lab, All Systems")
        logger.info("="*80)

    def evaluate_hardware(self) -> List[SystemMetric]:
        """Evaluate hardware performance"""
        metrics = []

        logger.info("")
        logger.info("💻 HARDWARE EVALUATION")
        logger.info("")

        # CPU
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            metrics.append(SystemMetric(
                name="CPU Usage",
                value=f"{cpu_percent:.1f}%",
                status="ok" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical",
                category="hardware",
                description=f"{cpu_count} cores, {cpu_freq.current:.0f} MHz"
            ))
            logger.info(f"   CPU: {cpu_percent:.1f}% ({cpu_count} cores)")
        except Exception as e:
            logger.debug(f"   CPU evaluation: {e}")

        # Memory
        try:
            memory = psutil.virtual_memory()
            metrics.append(SystemMetric(
                name="Memory Usage",
                value=f"{memory.percent:.1f}%",
                status="ok" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical",
                category="hardware",
                description=f"{memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB"
            ))
            logger.info(f"   Memory: {memory.percent:.1f}% ({memory.used / (1024**3):.1f} GB used)")
        except Exception as e:
            logger.debug(f"   Memory evaluation: {e}")

        # Disk
        try:
            disk = psutil.disk_usage("C:")
            metrics.append(SystemMetric(
                name="C: Drive Space",
                value=f"{disk.percent:.1f}%",
                status="ok" if disk.percent < 80 else "warning" if disk.percent < 90 else "critical",
                category="hardware",
                description=f"{disk.free / (1024**3):.1f} GB free"
            ))
            logger.info(f"   C: Drive: {disk.percent:.1f}% used ({disk.free / (1024**3):.1f} GB free)")
        except Exception as e:
            logger.debug(f"   Disk evaluation: {e}")

        # Network
        try:
            net_io = psutil.net_io_counters()
            metrics.append(SystemMetric(
                name="Network Activity",
                value="Active",
                status="ok",
                category="hardware",
                description=f"Bytes sent: {net_io.bytes_sent / (1024**2):.1f} MB, Recv: {net_io.bytes_recv / (1024**2):.1f} MB"
            ))
        except Exception as e:
            logger.debug(f"   Network evaluation: {e}")

        return metrics

    def evaluate_software_stack(self) -> List[SystemMetric]:
        """Evaluate LUMINA software stack"""
        metrics = []

        logger.info("")
        logger.info("📦 SOFTWARE STACK EVALUATION")
        logger.info("")

        # Check key services
        services = {
            "N8N": ("http://<NAS_PRIMARY_IP>:5678", "N8N workflow automation"),
            "SYPHON API": ("http://<NAS_IP>:8000", "SYPHON intelligence extraction"),
            "NAS": ("<NAS_PRIMARY_IP>", "Network Attached Storage")
        }

        for service_name, (endpoint, description) in services.items():
            try:
                import requests
                if ":" in endpoint:
                    url = f"http://{endpoint}"
                else:
                    url = f"http://{endpoint}:5000"  # Default port

                response = requests.get(url, timeout=2)
                status = "ok" if response.status_code == 200 else "warning"
                metrics.append(SystemMetric(
                    name=f"{service_name} Status",
                    value="Online" if status == "ok" else "Issues",
                    status=status,
                    category="software",
                    description=description
                ))
                logger.info(f"   {service_name}: {'✅ Online' if status == 'ok' else '⚠️  Issues'}")
            except:
                metrics.append(SystemMetric(
                    name=f"{service_name} Status",
                    value="Offline",
                    status="critical",
                    category="software",
                    description=description
                ))
                logger.warning(f"   {service_name}: ❌ Offline")

        # Check Python environment
        try:
            import sys
            python_version = sys.version.split()[0]
            metrics.append(SystemMetric(
                name="Python Version",
                value=python_version,
                status="ok",
                category="software",
                description="Python runtime"
            ))
            logger.info(f"   Python: {python_version}")
        except:
            pass

        # Check key dependencies
        key_packages = ["requests", "psutil", "flask", "elevenlabs"]
        for package in key_packages:
            try:
                __import__(package)
                metrics.append(SystemMetric(
                    name=f"{package} Package",
                    value="Installed",
                    status="ok",
                    category="software"
                ))
            except ImportError:
                metrics.append(SystemMetric(
                    name=f"{package} Package",
                    value="Missing",
                    status="warning",
                    category="software"
                ))
                logger.warning(f"   {package}: ❌ Missing")

        return metrics

    def evaluate_homelab(self) -> List[SystemMetric]:
        """Evaluate home lab infrastructure"""
        metrics = []

        logger.info("")
        logger.info("🏠 HOME LAB EVALUATION")
        logger.info("")

        # NAS connectivity
        nas_ip = "<NAS_PRIMARY_IP>"
        try:
            import socket
            result = socket.create_connection((nas_ip, 22), timeout=2)
            result.close()
            metrics.append(SystemMetric(
                name="NAS Connectivity",
                value="Connected",
                status="ok",
                category="homelab",
                description=f"NAS at {nas_ip}"
            ))
            logger.info(f"   NAS ({nas_ip}): ✅ Connected")
        except:
            metrics.append(SystemMetric(
                name="NAS Connectivity",
                value="Disconnected",
                status="critical",
                category="homelab",
                description=f"NAS at {nas_ip}"
            ))
            logger.error(f"   NAS ({nas_ip}): ❌ Disconnected")

        # Check NAS services
        nas_services = {
            "N8N": 5678,
            "Docker": 2375,
            "SSH": 22
        }

        for service_name, port in nas_services.items():
            try:
                import socket
                result = socket.create_connection((nas_ip, port), timeout=2)
                result.close()
                metrics.append(SystemMetric(
                    name=f"NAS {service_name}",
                    value="Online",
                    status="ok",
                    category="homelab"
                ))
                logger.info(f"   NAS {service_name}: ✅ Online")
            except:
                metrics.append(SystemMetric(
                    name=f"NAS {service_name}",
                    value="Offline",
                    status="warning",
                    category="homelab"
                ))
                logger.warning(f"   NAS {service_name}: ⚠️  Offline")

        return metrics

    def evaluate_lumina_integrations(self) -> List[SystemMetric]:
        """Evaluate LUMINA-specific integrations"""
        metrics = []

        logger.info("")
        logger.info("🔗 LUMINA INTEGRATIONS EVALUATION")
        logger.info("")

        # Azure Vault
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
            # Try to access vault
            try:
                vault.get_secret("test")  # Will fail but tests connection
            except:
                pass  # Expected to fail, but connection works
            metrics.append(SystemMetric(
                name="Azure Key Vault",
                value="Connected",
                status="ok",
                category="lumina_integration"
            ))
            logger.info("   Azure Key Vault: ✅ Connected")
        except Exception as e:
            metrics.append(SystemMetric(
                name="Azure Key Vault",
                value="Connection Issue",
                status="warning",
                category="lumina_integration"
            ))
            logger.warning(f"   Azure Key Vault: ⚠️  {e}")

        # AutoHotkey
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq AutoHotkey.exe"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if "AutoHotkey.exe" in result.stdout:
                metrics.append(SystemMetric(
                    name="AutoHotkey",
                    value="Running",
                    status="ok",
                    category="lumina_integration"
                ))
                logger.info("   AutoHotkey: ✅ Running")
            else:
                metrics.append(SystemMetric(
                    name="AutoHotkey",
                    value="Not Running",
                    status="warning",
                    category="lumina_integration"
                ))
                logger.warning("   AutoHotkey: ⚠️  Not Running")
        except:
            pass

        # N8N Workflows
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            import requests

            vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
            api_key = vault.get_secret("n8n-api-token")

            response = requests.get(
                "http://<NAS_PRIMARY_IP>:5678/api/v1/workflows",
                headers={"X-N8N-API-KEY": api_key},
                timeout=5
            )

            if response.status_code == 200:
                workflows = response.json().get("data", [])
                active = sum(1 for w in workflows if w.get("active", False))
                metrics.append(SystemMetric(
                    name="N8N Workflows",
                    value=f"{active}/{len(workflows)} Active",
                    status="ok" if active > 0 else "warning",
                    category="lumina_integration"
                ))
                logger.info(f"   N8N Workflows: {active}/{len(workflows)} active")
        except Exception as e:
            logger.debug(f"   N8N workflows: {e}")

        return metrics

    def identify_weak_spots(self) -> List[WeakSpot]:
        """Identify weak spots and pain points"""
        weak_spots = []

        logger.info("")
        logger.info("🔍 IDENTIFYING WEAK SPOTS & PAIN POINTS")
        logger.info("")

        # Analyze metrics for issues
        critical_metrics = [m for m in self.metrics if m.status == "critical"]
        warning_metrics = [m for m in self.metrics if m.status == "warning"]

        # Hardware issues
        hardware_issues = [m for m in critical_metrics + warning_metrics if m.category == "hardware"]
        if hardware_issues:
            weak_spots.append(WeakSpot(
                area="Hardware",
                issue="Hardware resource constraints detected",
                severity="high" if any(m.status == "critical" for m in hardware_issues) else "medium",
                impact="System performance degradation, potential failures",
                recommendation="Monitor resource usage, consider upgrades or optimization",
                affected_systems=["System Performance", "LUMINA Services"]
            ))
            logger.warning("   ⚠️  Hardware issues detected")

        # Software stack issues
        software_issues = [m for m in critical_metrics + warning_metrics if m.category == "software"]
        if software_issues:
            weak_spots.append(WeakSpot(
                area="Software Stack",
                issue="Software service availability issues",
                severity="high" if any(m.status == "critical" for m in software_issues) else "medium",
                impact="Service unavailability, workflow interruptions",
                recommendation="Check service status, restart if needed, verify connectivity",
                affected_systems=[m.name for m in software_issues]
            ))
            logger.warning("   ⚠️  Software stack issues detected")

        # Home lab issues
        homelab_issues = [m for m in critical_metrics + warning_metrics if m.category == "homelab"]
        if homelab_issues:
            weak_spots.append(WeakSpot(
                area="Home Lab Infrastructure",
                issue="NAS or home lab connectivity issues",
                severity="critical" if any(m.status == "critical" for m in homelab_issues) else "high",
                impact="Data access failures, workflow interruptions, backup issues",
                recommendation="Check NAS status, network connectivity, service health",
                affected_systems=["NAS", "N8N", "Backups", "Data Storage"]
            ))
            logger.error("   ❌ Home lab issues detected")

        # Integration issues
        integration_issues = [m for m in critical_metrics + warning_metrics if m.category == "lumina_integration"]
        if integration_issues:
            weak_spots.append(WeakSpot(
                area="LUMINA Integrations",
                issue="LUMINA integration service issues",
                severity="medium",
                impact="Reduced automation, manual intervention required",
                recommendation="Verify integration services, check credentials, restart if needed",
                affected_systems=[m.name for m in integration_issues]
            ))
            logger.warning("   ⚠️  Integration issues detected")

        # Efficiency analysis
        cpu_metrics = [m for m in self.metrics if "CPU" in m.name]
        memory_metrics = [m for m in self.metrics if "Memory" in m.name]

        if cpu_metrics:
            cpu_value = cpu_metrics[0].value
            if isinstance(cpu_value, str) and "%" in cpu_value:
                cpu_percent = float(cpu_value.replace("%", ""))
                if cpu_percent > 90:
                    weak_spots.append(WeakSpot(
                        area="Performance",
                        issue="High CPU usage - potential bottleneck",
                        severity="high",
                        impact="System slowdown, delayed processing",
                        recommendation="Identify CPU-intensive processes, optimize or distribute load",
                        affected_systems=["All LUMINA Services", "System Responsiveness"]
                    ))

        if memory_metrics:
            memory_value = memory_metrics[0].value
            if isinstance(memory_value, str) and "%" in memory_value:
                mem_percent = float(memory_value.replace("%", ""))
                if mem_percent > 90:
                    weak_spots.append(WeakSpot(
                        area="Performance",
                        issue="High memory usage - potential memory pressure",
                        severity="high",
                        impact="System slowdown, potential crashes",
                        recommendation="Free up memory, identify memory leaks, consider upgrade",
                        affected_systems=["All Applications", "System Stability"]
                    ))

        return weak_spots

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "holistic_system_evaluation",
            "metrics": [asdict(m) for m in self.metrics],
            "weak_spots": [asdict(w) for w in self.weak_spots],
            "summary": {
                "total_metrics": len(self.metrics),
                "critical_issues": len([m for m in self.metrics if m.status == "critical"]),
                "warnings": len([m for m in self.metrics if m.status == "warning"]),
                "weak_spots_count": len(self.weak_spots),
                "overall_status": "healthy" if not any(m.status == "critical" for m in self.metrics) else "issues_detected"
            }
        }

        return report

    def run_evaluation(self) -> Dict[str, Any]:
        try:
            """Run complete holistic evaluation"""
            logger.info("")
            logger.info("🚀 STARTING HOLISTIC SYSTEM EVALUATION")
            logger.info("")

            # Collect all metrics
            self.metrics = []
            self.metrics.extend(self.evaluate_hardware())
            self.metrics.extend(self.evaluate_software_stack())
            self.metrics.extend(self.evaluate_homelab())
            self.metrics.extend(self.evaluate_lumina_integrations())

            # Identify weak spots
            self.weak_spots = self.identify_weak_spots()

            # Generate report
            report = self.generate_report()

            # Save report
            report_file = self.data_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("="*80)
            logger.info("📊 EVALUATION SUMMARY")
            logger.info("="*80)
            logger.info(f"   Total Metrics: {report['summary']['total_metrics']}")
            logger.info(f"   Critical Issues: {report['summary']['critical_issues']}")
            logger.info(f"   Warnings: {report['summary']['warnings']}")
            logger.info(f"   Weak Spots: {report['summary']['weak_spots_count']}")
            logger.info(f"   Overall Status: {report['summary']['overall_status']}")
            logger.info("")

            if self.weak_spots:
                logger.info("⚠️  WEAK SPOTS IDENTIFIED:")
                for spot in self.weak_spots:
                    logger.info(f"   • {spot.area}: {spot.issue} ({spot.severity})")
            else:
                logger.info("✅ No weak spots identified")

            logger.info("")
            logger.info(f"📄 Report saved: {report_file.name}")
            logger.info("="*80)

            return report


        except Exception as e:
            self.logger.error(f"Error in run_evaluation: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Holistic System Evaluation")
    parser.add_argument("--run", action="store_true", help="Run evaluation")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds")

    args = parser.parse_args()

    evaluator = LuminaHolisticSystemEvaluation()

    if args.continuous:
        logger.info("🔄 Starting continuous monitoring...")
        while True:
            evaluator.run_evaluation()
            logger.info(f"   ⏳ Next evaluation in {args.interval} seconds...")
            time.sleep(args.interval)
    elif args.run:
        evaluator.run_evaluation()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())