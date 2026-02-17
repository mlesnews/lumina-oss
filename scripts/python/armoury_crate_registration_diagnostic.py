#!/usr/bin/env python3
"""
Armoury Crate Registration Diagnostic

Investigates why a laptop device shows as registered with ASUS but not in Armoury Crate.
Uses @RR (Read & Run) for comprehensive analysis and @SYPHON for telemetry tracking.

@JARVIS @RR @SYPHON @MARVIN
"""

import sys
import json
import subprocess
import os
import winreg
from pathlib import Path
from typing import Dict, List, Any, Optional
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

# Import @RR
try:
    from jarvis_rr_godloop import JARVISRRGodLoop
    RR_AVAILABLE = True
except ImportError:
    RR_AVAILABLE = False
    JARVISRRGodLoop = None

# Import @SYPHON
try:
    from syphon_workflow_telemetry_system import SYPHONWorkflowTelemetrySystem
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONWorkflowTelemetrySystem = None

logger = get_logger("ArmouryCrateDiagnostic")


class ArmouryCrateRegistrationDiagnostic:
    """
    Diagnostic system for Armoury Crate device registration issues.

    Investigates:
    - ASUS registration status
    - Armoury Crate device detection
    - Registry entries
    - Service status
    - Process status
    - Device manager entries
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.data_dir = project_root / "data" / "armoury_crate_diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize @RR
        self.rr_system = None
        if RR_AVAILABLE:
            try:
                self.rr_system = JARVISRRGodLoop(project_root)
                self.logger.info("✅ @RR initialized for diagnostic analysis")
            except Exception as e:
                self.logger.warning(f"⚠️  @RR initialization failed: {e}")

        # Initialize @SYPHON
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONWorkflowTelemetrySystem(project_root)
                self.logger.info("✅ @SYPHON initialized for telemetry tracking")
            except Exception as e:
                self.logger.warning(f"⚠️  @SYPHON initialization failed: {e}")

    def run_full_diagnostic(self) -> Dict[str, Any]:
        """
        Run comprehensive diagnostic for Armoury Crate registration issue.

        Returns:
            Complete diagnostic report with findings and recommendations
        """
        self.logger.info("="*80)
        self.logger.info("🔍 ARMOURY CRATE REGISTRATION DIAGNOSTIC")
        self.logger.info("="*80)

        # @SYPHON: Start workflow tracking
        workflow_id = None
        if self.syphon:
            try:
                workflow_id = self.syphon.start_workflow(
                    workflow_name="Armoury Crate Registration Diagnostic",
                    workflow_type="diagnostic",
                    metadata={"issue": "Device registered with ASUS but not in Armoury Crate"}
                )
            except Exception as e:
                self.logger.warning(f"⚠️  @SYPHON workflow start failed: {e}")

        diagnostic_results = {
            "timestamp": datetime.now().isoformat(),
            "issue": "Device shows as registered with ASUS but not in Armoury Crate",
            "checks": {}
        }

        # Check 1: ASUS Registration Status
        self.logger.info("\n📋 Check 1: ASUS Registration Status")
        asus_registration = self._check_asus_registration()
        diagnostic_results["checks"]["asus_registration"] = asus_registration

        # Check 2: Armoury Crate Installation
        self.logger.info("\n📋 Check 2: Armoury Crate Installation")
        armoury_installation = self._check_armoury_installation()
        diagnostic_results["checks"]["armoury_installation"] = armoury_installation

        # Check 3: Registry Entries
        self.logger.info("\n📋 Check 3: Registry Entries")
        registry_entries = self._check_registry_entries()
        diagnostic_results["checks"]["registry_entries"] = registry_entries

        # Check 4: Service Status
        self.logger.info("\n📋 Check 4: ASUS Services Status")
        service_status = self._check_services()
        diagnostic_results["checks"]["services"] = service_status

        # Check 5: Process Status
        self.logger.info("\n📋 Check 5: Armoury Crate Processes")
        process_status = self._check_processes()
        diagnostic_results["checks"]["processes"] = process_status

        # Check 6: Device Manager
        self.logger.info("\n📋 Check 6: Device Manager Entries")
        device_manager = self._check_device_manager()
        diagnostic_results["checks"]["device_manager"] = device_manager

        # Check 7: Armoury Crate Device Detection
        self.logger.info("\n📋 Check 7: Armoury Crate Device Detection")
        device_detection = self._check_device_detection()
        diagnostic_results["checks"]["device_detection"] = device_detection

        # @RR: Analyze findings
        if self.rr_system:
            self.logger.info("\n📖 @RR: Analyzing diagnostic findings...")
            try:
                analysis = self._rr_analyze_findings(diagnostic_results)
                diagnostic_results["rr_analysis"] = analysis
            except Exception as e:
                self.logger.warning(f"⚠️  @RR analysis failed: {e}")

        # Generate recommendations
        recommendations = self._generate_recommendations(diagnostic_results)
        diagnostic_results["recommendations"] = recommendations

        # Save diagnostic report
        report_file = self.data_dir / f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(diagnostic_results, f, indent=2)
            self.logger.info(f"\n✅ Diagnostic report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save diagnostic report: {e}")

        # @SYPHON: Complete workflow
        if self.syphon and workflow_id:
            try:
                self.syphon.complete_workflow(
                    workflow_id=workflow_id,
                    success=True,
                    metrics={
                        "checks_performed": len(diagnostic_results["checks"]),
                        "issues_found": len([c for c in diagnostic_results["checks"].values() if not c.get("status") == "ok"])
                    }
                )
            except Exception as e:
                self.logger.warning(f"⚠️  @SYPHON workflow completion failed: {e}")

        # Print summary
        self._print_summary(diagnostic_results)

        return diagnostic_results

    def _check_asus_registration(self) -> Dict[str, Any]:
        """Check ASUS registration status"""
        result = {
            "status": "unknown",
            "details": {},
            "issues": []
        }

        try:
            # Check registry for ASUS account info
            asus_reg_keys = [
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\ASUS\ArmouryDevice"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ASUS\ArmouryDevice"),
            ]

            for hkey, key_path in asus_reg_keys:
                try:
                    key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
                    result["details"][f"{hkey}_{key_path}"] = "exists"

                    # Try to read account info
                    try:
                        account = winreg.QueryValueEx(key, "Account")[0]
                        result["details"]["account"] = account
                        result["status"] = "registered"
                    except:
                        pass

                    winreg.CloseKey(key)
                except FileNotFoundError:
                    result["details"][f"{hkey}_{key_path}"] = "not_found"
                except Exception as e:
                    result["issues"].append(f"Error reading {key_path}: {e}")

            if result["status"] == "unknown":
                result["status"] = "not_found"
                result["issues"].append("ASUS registration not found in registry")
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error checking ASUS registration: {e}")

        self.logger.info(f"   Status: {result['status']}")
        if result["issues"]:
            for issue in result["issues"]:
                self.logger.warning(f"   ⚠️  {issue}")

        return result

    def _check_armoury_installation(self) -> Dict[str, Any]:
        """Check Armoury Crate installation"""
        result = {
            "status": "unknown",
            "installed": False,
            "version": None,
            "paths": [],
            "issues": []
        }

        try:
            # Check common installation paths
            paths_to_check = [
                Path(os.environ.get("ProgramFiles", "")) / "ASUS" / "ArmouryDevice",
                Path(os.environ.get("ProgramFiles(x86)", "")) / "ASUS" / "ArmouryDevice",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "ArmouryCrate.exe",
            ]

            for path in paths_to_check:
                if path.exists():
                    result["installed"] = True
                    result["paths"].append(str(path))
                    result["status"] = "installed"

                    # Try to get version
                    exe_path = path / "dpt" / "ArmouryCrate.exe"
                    if exe_path.exists():
                        try:
                            import win32api
                            version_info = win32api.GetFileVersionInfo(str(exe_path), "\\")
                            version = f"{version_info['FileVersionMS'] >> 16}.{version_info['FileVersionMS'] & 0xFFFF}.{version_info['FileVersionLS'] >> 16}.{version_info['FileVersionLS'] & 0xFFFF}"
                            result["version"] = version
                        except:
                            pass

            if not result["installed"]:
                result["status"] = "not_installed"
                result["issues"].append("Armoury Crate not found in standard installation paths")
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error checking installation: {e}")

        self.logger.info(f"   Installed: {result['installed']}")
        if result["version"]:
            self.logger.info(f"   Version: {result['version']}")
        if result["issues"]:
            for issue in result["issues"]:
                self.logger.warning(f"   ⚠️  {issue}")

        return result

    def _check_registry_entries(self) -> Dict[str, Any]:
        """Check relevant registry entries"""
        result = {
            "status": "unknown",
            "entries": {},
            "issues": []
        }

        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\ASUS\ArmouryDevice"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ASUS\ArmouryDevice"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\ASUS\ArmouryDevice"),
        ]

        for hkey, key_path in registry_paths:
            try:
                key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
                result["entries"][key_path] = "exists"

                # Try to enumerate values
                try:
                    i = 0
                    while True:
                        name, value, _ = winreg.EnumValue(key, i)
                        result["entries"][f"{key_path}\\{name}"] = str(value)[:100]  # Truncate long values
                        i += 1
                except WindowsError:
                    pass

                winreg.CloseKey(key)
                result["status"] = "found"
            except FileNotFoundError:
                result["entries"][key_path] = "not_found"
            except Exception as e:
                result["issues"].append(f"Error reading {key_path}: {e}")

        if not result["entries"]:
            result["status"] = "not_found"
            result["issues"].append("No registry entries found")

        self.logger.info(f"   Registry entries found: {len([e for e in result['entries'].values() if e == 'exists'])}")

        return result

    def _check_services(self) -> Dict[str, Any]:
        """Check ASUS service status"""
        result = {
            "status": "unknown",
            "services": {},
            "issues": []
        }

        asus_services = [
            "ArmouryCrateService",
            "ASUS System Control Interface",
            "ASUS Aura Service",
            "LightingService",
        ]

        try:
            import subprocess
            for service in asus_services:
                try:
                    output = subprocess.run(
                        ["sc", "query", service],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if "RUNNING" in output.stdout:
                        result["services"][service] = "running"
                    elif "STOPPED" in output.stdout:
                        result["services"][service] = "stopped"
                        result["issues"].append(f"{service} is stopped")
                    else:
                        result["services"][service] = "not_found"
                        result["issues"].append(f"{service} not found")
                except Exception as e:
                    result["services"][service] = "error"
                    result["issues"].append(f"Error checking {service}: {e}")

            running_count = len([s for s in result["services"].values() if s == "running"])
            if running_count > 0:
                result["status"] = "partial" if running_count < len(asus_services) else "ok"
            else:
                result["status"] = "error"
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error checking services: {e}")

        self.logger.info(f"   Services running: {len([s for s in result['services'].values() if s == 'running'])}/{len(asus_services)}")

        return result

    def _check_processes(self) -> Dict[str, Any]:
        """Check Armoury Crate processes"""
        result = {
            "status": "unknown",
            "processes": {},
            "issues": []
        }

        processes_to_check = [
            "ArmouryCrate.exe",
            "ArmouryCrateControlInterface.exe",
            "AuraService.exe",
            "LightingService.exe",
        ]

        try:
            import psutil
            running_processes = {p.info['name']: p.info for p in psutil.process_iter(['name', 'pid', 'status'])}

            for proc_name in processes_to_check:
                found = False
                for name, info in running_processes.items():
                    if proc_name.lower() in name.lower():
                        result["processes"][proc_name] = {
                            "running": True,
                            "pid": info.get('pid'),
                            "status": info.get('status')
                        }
                        found = True
                        break

                if not found:
                    result["processes"][proc_name] = {"running": False}
                    result["issues"].append(f"{proc_name} not running")

            running_count = len([p for p in result["processes"].values() if p.get("running")])
            if running_count > 0:
                result["status"] = "partial" if running_count < len(processes_to_check) else "ok"
            else:
                result["status"] = "error"
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error checking processes: {e}")

        self.logger.info(f"   Processes running: {len([p for p in result['processes'].values() if p.get('running')])}/{len(processes_to_check)}")

        return result

    def _check_device_manager(self) -> Dict[str, Any]:
        """Check Device Manager for ASUS devices"""
        result = {
            "status": "unknown",
            "devices": [],
            "issues": []
        }

        try:
            import subprocess
            output = subprocess.run(
                ["powershell", "-Command", "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*ASUS*' -or $_.FriendlyName -like '*ROG*'} | Select-Object FriendlyName, Status, Class"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if output.returncode == 0:
                lines = output.stdout.strip().split('\n')
                for line in lines[3:]:  # Skip header
                    if line.strip():
                        result["devices"].append(line.strip())
                        result["status"] = "found"
            else:
                result["issues"].append("Failed to query Device Manager")
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error checking Device Manager: {e}")

        self.logger.info(f"   ASUS devices found: {len(result['devices'])}")

        return result

    def _check_device_detection(self) -> Dict[str, Any]:
        """Check if Armoury Crate can detect the device"""
        result = {
            "status": "unknown",
            "detected": False,
            "issues": []
        }

        # This would require actually opening Armoury Crate and checking
        # For now, we'll check if the device appears in Armoury Crate logs/config
        try:
            appdata = Path(os.environ.get("LOCALAPPDATA", ""))
            armoury_data = appdata / "Packages" / "B9ECED6F.ArmouryCrate_qmba6cd70vzyy"

            if armoury_data.exists():
                result["detected"] = True
                result["status"] = "data_found"
            else:
                result["issues"].append("Armoury Crate data directory not found")
                result["status"] = "not_found"
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error checking device detection: {e}")

        self.logger.info(f"   Device detection data: {result['status']}")

        return result

    def _rr_analyze_findings(self, diagnostic_results: Dict[str, Any]) -> Dict[str, Any]:
        """Use @RR to analyze diagnostic findings"""
        analysis = {
            "summary": "",
            "root_causes": [],
            "confidence": 0.0
        }

        # Analyze patterns in findings
        issues = []
        for check_name, check_result in diagnostic_results["checks"].items():
            if check_result.get("issues"):
                issues.extend(check_result["issues"])

        if issues:
            analysis["root_causes"] = issues[:5]  # Top 5 issues
            analysis["summary"] = f"Found {len(issues)} potential issues across {len(diagnostic_results['checks'])} diagnostic checks"
            analysis["confidence"] = min(1.0, len(issues) / 10.0)

        return analysis

    def _generate_recommendations(self, diagnostic_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings"""
        recommendations = []

        # Check installation
        installation = diagnostic_results["checks"].get("armoury_installation", {})
        if not installation.get("installed"):
            recommendations.append({
                "priority": "high",
                "action": "Install Armoury Crate",
                "details": "Armoury Crate is not installed. Download and install from ASUS website."
            })

        # Check services
        services = diagnostic_results["checks"].get("services", {})
        stopped_services = [s for s, status in services.get("services", {}).items() if status == "stopped"]
        if stopped_services:
            recommendations.append({
                "priority": "high",
                "action": "Start ASUS services",
                "details": f"The following services are stopped: {', '.join(stopped_services)}. Start them using: sc start <service_name>"
            })

        # Check registration
        registration = diagnostic_results["checks"].get("asus_registration", {})
        if registration.get("status") == "not_found":
            recommendations.append({
                "priority": "medium",
                "action": "Re-register device with ASUS",
                "details": "Device registration not found. Try logging into ASUS account in Armoury Crate."
            })

        # Check processes
        processes = diagnostic_results["checks"].get("processes", {})
        if processes.get("status") == "error":
            recommendations.append({
                "priority": "high",
                "action": "Restart Armoury Crate",
                "details": "Armoury Crate processes are not running. Restart Armoury Crate application."
            })

        return recommendations

    def _print_summary(self, diagnostic_results: Dict[str, Any]):
        """Print diagnostic summary"""
        self.logger.info("\n" + "="*80)
        self.logger.info("DIAGNOSTIC SUMMARY")
        self.logger.info("="*80)

        for check_name, check_result in diagnostic_results["checks"].items():
            status = check_result.get("status", "unknown")
            icon = "✅" if status == "ok" else "⚠️" if status == "partial" else "❌"
            self.logger.info(f"{icon} {check_name}: {status}")

        recommendations = diagnostic_results.get("recommendations", [])
        if recommendations:
            self.logger.info(f"\n📋 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                self.logger.info(f"   {i}. [{rec['priority'].upper()}] {rec['action']}")
                self.logger.info(f"      {rec['details']}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Armoury Crate Registration Diagnostic")
        parser.add_argument("--full", action="store_true", help="Run full diagnostic")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        diagnostic = ArmouryCrateRegistrationDiagnostic(project_root)

        if args.full:
            result = diagnostic.run_full_diagnostic()
            print("\n✅ Diagnostic complete!")
        else:
            print("Usage: python armoury_crate_registration_diagnostic.py --full")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import os


    main()