#!/usr/bin/env python3
"""
JARVIS: Diagnose Partial Device Registration in Armoury Crate

Investigates why laptop shows up in AC but cannot be fully added/configured.
This is a common issue where device is detected but not fully registered.

@JARVIS @ARMOURY_CRATE @DEVICE_REGISTRATION @DIAGNOSTIC
"""

import sys
import subprocess
import json
import winreg
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_PartialDeviceReg")


class JARVISPartialDeviceRegistrationDiagnostic:
    """
    Diagnose partial device registration in Armoury Crate

    Issue: Device shows up in AC but cannot be fully added/configured
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "armoury_crate_diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info("✅ JARVIS Partial Device Registration Diagnostic initialized")

    def run_diagnostic(self) -> Dict[str, Any]:
        try:
            """Run comprehensive diagnostic"""
            print("=" * 70)
            print("🔍 JARVIS: PARTIAL DEVICE REGISTRATION DIAGNOSTIC")
            print("   Issue: Laptop shows up in AC but cannot be fully added")
            print("=" * 70)
            print()

            results = {
                "timestamp": datetime.now().isoformat(),
                "issue": "Device shows up in AC but cannot be fully added/configured",
                "findings": {},
                "root_causes": [],
                "recommendations": []
            }

            # Check 1: Device Detection Status
            print("CHECK 1: Device Detection Status...")
            detection = self._check_device_detection()
            results["findings"]["detection"] = detection
            print(f"   Status: {detection.get('status', 'unknown')}")
            print()

            # Check 2: Device Registration Completeness
            print("CHECK 2: Device Registration Completeness...")
            registration = self._check_registration_completeness()
            results["findings"]["registration"] = registration
            print(f"   Complete: {registration.get('complete', False)}")
            if registration.get("missing_fields"):
                print(f"   Missing Fields: {', '.join(registration['missing_fields'])}")
            print()

            # Check 3: Device Profile Status
            print("CHECK 3: Device Profile Status...")
            profile = self._check_device_profile()
            results["findings"]["profile"] = profile
            print(f"   Profile Exists: {profile.get('exists', False)}")
            print(f"   Profile Complete: {profile.get('complete', False)}")
            print()

            # Check 4: Device Drivers
            print("CHECK 4: Device Drivers...")
            drivers = self._check_device_drivers()
            results["findings"]["drivers"] = drivers
            print(f"   Drivers Installed: {drivers.get('installed', False)}")
            if drivers.get("missing_drivers"):
                print(f"   Missing Drivers: {', '.join(drivers['missing_drivers'])}")
            print()

            # Check 5: Service Integration
            print("CHECK 5: Service Integration...")
            services = self._check_service_integration()
            results["findings"]["services"] = services
            print(f"   Services OK: {services.get('all_running', False)}")
            print()

            # Check 6: Registry Consistency
            print("CHECK 6: Registry Consistency...")
            registry = self._check_registry_consistency()
            results["findings"]["registry"] = registry
            print(f"   Consistent: {registry.get('consistent', False)}")
            if registry.get("inconsistencies"):
                print(f"   Inconsistencies: {len(registry['inconsistencies'])}")
            print()

            # Check 7: Device Manager Status
            print("CHECK 7: Device Manager Status...")
            device_mgr = self._check_device_manager_status()
            results["findings"]["device_manager"] = device_mgr
            print(f"   Devices Found: {len(device_mgr.get('devices', []))}")
            print()

            # Analyze root causes
            print("ANALYZING ROOT CAUSES...")
            root_causes = self._analyze_root_causes(results["findings"])
            results["root_causes"] = root_causes
            for cause in root_causes:
                print(f"   • {cause}")
            print()

            # Generate recommendations
            print("GENERATING RECOMMENDATIONS...")
            recommendations = self._generate_recommendations(results["findings"], root_causes)
            results["recommendations"] = recommendations
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. [{rec['priority']}] {rec['action']}")
            print()

            # Save report
            report_file = self.data_dir / f"partial_registration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"✅ Report saved: {report_file}")
            print()

            return results

        except Exception as e:
            self.logger.error(f"Error in run_diagnostic: {e}", exc_info=True)
            raise
    def _check_device_detection(self) -> Dict[str, Any]:
        """Check if device is detected by AC"""
        result = {
            "status": "unknown",
            "detected": False,
            "details": {}
        }

        try:
            # Check if device appears in AC registry
            reg_paths = [
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\ASUS\ARMOURY CRATE Service\Device"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ASUS\ArmouryDevice"),
            ]

            for hkey, path in reg_paths:
                try:
                    key = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
                    result["detected"] = True
                    result["status"] = "detected"
                    result["details"][path] = "exists"

                    # Try to enumerate devices
                    try:
                        i = 0
                        devices = []
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                devices.append(subkey_name)
                                i += 1
                            except OSError:
                                break
                        result["details"]["device_count"] = len(devices)
                    except:
                        pass

                    winreg.CloseKey(key)
                except FileNotFoundError:
                    result["details"][path] = "not_found"
                except Exception as e:
                    result["details"][path] = f"error: {e}"

            if not result["detected"]:
                result["status"] = "not_detected"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _check_registration_completeness(self) -> Dict[str, Any]:
        """Check if device registration is complete"""
        result = {
            "complete": False,
            "missing_fields": [],
            "required_fields": [
                "DeviceID", "DeviceName", "DeviceType", "SerialNumber",
                "Model", "RegistrationDate", "ProfileID"
            ]
        }

        try:
            # Check HKCU registry
            reg_path = r"SOFTWARE\ASUS\ARMOURY CRATE Service\Device"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)

                found_fields = []
                for field in result["required_fields"]:
                    try:
                        value = winreg.QueryValueEx(key, field)[0]
                        found_fields.append(field)
                        result[field] = str(value)[:50]  # Truncate
                    except FileNotFoundError:
                        result["missing_fields"].append(field)
                    except:
                        pass

                winreg.CloseKey(key)

                if len(found_fields) == len(result["required_fields"]):
                    result["complete"] = True
            except FileNotFoundError:
                result["missing_fields"] = result["required_fields"]
            except Exception as e:
                result["error"] = str(e)
        except Exception as e:
            result["error"] = str(e)

        return result

    def _check_device_profile(self) -> Dict[str, Any]:
        """Check if device profile exists and is complete"""
        result = {
            "exists": False,
            "complete": False,
            "profile_path": None
        }

        try:
            # Check for device profile in AC data
            appdata = Path(os.environ.get("LOCALAPPDATA", ""))
            profile_paths = [
                appdata / "Packages" / "B9ECED6F.ArmouryCrate_qmba6cd70vzyy" / "LocalState" / "Device",
                appdata / "ASUS" / "ARMOURY CRATE Service" / "Device",
            ]

            for path in profile_paths:
                if path.exists():
                    result["exists"] = True
                    result["profile_path"] = str(path)

                    # Check if profile files exist
                    profile_files = list(path.glob("*.json")) + list(path.glob("*.xml"))
                    if profile_files:
                        result["complete"] = True
                    break
        except Exception as e:
            result["error"] = str(e)

        return result

    def _check_device_drivers(self) -> Dict[str, Any]:
        """Check if required device drivers are installed"""
        result = {
            "installed": False,
            "missing_drivers": [],
            "required_drivers": [
                "ASUS System Control Interface",
                "ASUS Aura",
                "ASUS Keyboard",
                "ASUS Mouse"
            ]
        }

        try:
            ps_command = """
            $drivers = Get-PnpDevice | Where-Object {
                $_.FriendlyName -like '*ASUS*' -or 
                $_.FriendlyName -like '*ROG*' -or
                $_.Manufacturer -like '*ASUS*'
            } | Select-Object FriendlyName, Status, Class;
            $drivers | ConvertTo-Json
            """

            proc_result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if proc_result.stdout:
                try:
                    drivers_data = json.loads(proc_result.stdout)
                    if isinstance(drivers_data, list) and len(drivers_data) > 0:
                        result["installed"] = True
                        result["drivers_found"] = [d.get("FriendlyName", "") for d in drivers_data if isinstance(d, dict)]
                    elif isinstance(drivers_data, dict):
                        result["installed"] = True
                        result["drivers_found"] = [drivers_data.get("FriendlyName", "")]
                except:
                    # If JSON parse fails, check if output contains ASUS
                    if "ASUS" in proc_result.stdout or "ROG" in proc_result.stdout:
                        result["installed"] = True
        except Exception as e:
            result["error"] = str(e)

        return result

    def _check_service_integration(self) -> Dict[str, Any]:
        """Check if services are properly integrated"""
        result = {
            "all_running": False,
            "services": {},
            "required_services": [
                "ArmouryCrateService",
                "ASUS System Control Interface",
                "LightingService"
            ]
        }

        try:
            for service in result["required_services"]:
                try:
                    proc_result = subprocess.run(
                        ["sc", "query", service],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if "RUNNING" in proc_result.stdout:
                        result["services"][service] = "running"
                    elif "STOPPED" in proc_result.stdout:
                        result["services"][service] = "stopped"
                    else:
                        result["services"][service] = "not_found"
                except:
                    result["services"][service] = "error"

            running_count = sum(1 for s in result["services"].values() if s == "running")
            result["all_running"] = running_count == len(result["required_services"])
        except Exception as e:
            result["error"] = str(e)

        return result

    def _check_registry_consistency(self) -> Dict[str, Any]:
        """Check registry consistency between HKCU and HKLM"""
        result = {
            "consistent": True,
            "inconsistencies": []
        }

        try:
            # Compare device info between HKCU and HKLM
            hkcu_path = r"SOFTWARE\ASUS\ARMOURY CRATE Service\Device"
            hklm_path = r"SOFTWARE\ASUS\ArmouryDevice"

            hkcu_data = {}
            hklm_data = {}

            # Read HKCU
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, hkcu_path, 0, winreg.KEY_READ)
                try:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            hkcu_data[name] = str(value)
                            i += 1
                        except OSError:
                            break
                finally:
                    winreg.CloseKey(key)
            except:
                pass

            # Read HKLM
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, hklm_path, 0, winreg.KEY_READ)
                try:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            hklm_data[name] = str(value)
                            i += 1
                        except OSError:
                            break
                finally:
                    winreg.CloseKey(key)
            except:
                pass

            # Compare
            common_keys = set(hkcu_data.keys()) & set(hklm_data.keys())
            for key in common_keys:
                if hkcu_data[key] != hklm_data[key]:
                    result["inconsistencies"].append(f"{key}: HKCU={hkcu_data[key][:20]} vs HKLM={hklm_data[key][:20]}")

            if result["inconsistencies"]:
                result["consistent"] = False
        except Exception as e:
            result["error"] = str(e)

        return result

    def _check_device_manager_status(self) -> Dict[str, Any]:
        """Check Device Manager for ASUS devices"""
        result = {
            "devices": []
        }

        try:
            ps_command = """
            Get-PnpDevice | Where-Object {
                $_.FriendlyName -like '*ASUS*' -or 
                $_.FriendlyName -like '*ROG*' -or
                $_.Manufacturer -like '*ASUS*'
            } | Select-Object FriendlyName, Status, Class, InstanceId | ConvertTo-Json
            """

            proc_result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if proc_result.stdout:
                try:
                    devices = json.loads(proc_result.stdout)
                    if isinstance(devices, list):
                        result["devices"] = devices
                    elif isinstance(devices, dict):
                        result["devices"] = [devices]
                except:
                    pass
        except Exception as e:
            result["error"] = str(e)

        return result

    def _analyze_root_causes(self, findings: Dict[str, Any]) -> List[str]:
        """Analyze findings to identify root causes"""
        causes = []

        # Check registration completeness
        reg = findings.get("registration", {})
        if not reg.get("complete") and reg.get("missing_fields"):
            causes.append(f"Incomplete registration: Missing fields {', '.join(reg['missing_fields'][:3])}")

        # Check device profile
        profile = findings.get("profile", {})
        if not profile.get("complete"):
            causes.append("Device profile incomplete or missing")

        # Check drivers
        drivers = findings.get("drivers", {})
        if not drivers.get("installed"):
            causes.append("Required ASUS device drivers not installed")

        # Check services
        services = findings.get("services", {})
        if not services.get("all_running"):
            stopped = [s for s, status in services.get("services", {}).items() if status != "running"]
            if stopped:
                causes.append(f"Required services not running: {', '.join(stopped[:2])}")

        # Check registry consistency
        registry = findings.get("registry", {})
        if not registry.get("consistent"):
            causes.append("Registry inconsistencies between HKCU and HKLM")

        if not causes:
            causes.append("Device detected but configuration incomplete - may need manual AC setup")

        return causes

    def _generate_recommendations(self, findings: Dict[str, Any], root_causes: List[str]) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings"""
        recommendations = []

        # Registration completeness
        reg = findings.get("registration", {})
        if not reg.get("complete"):
            recommendations.append({
                "priority": "HIGH",
                "action": "Complete device registration",
                "details": f"Missing fields: {', '.join(reg.get('missing_fields', [])[:3])}. Try logging into ASUS account in Armoury Crate."
            })

        # Device profile
        profile = findings.get("profile", {})
        if not profile.get("complete"):
            recommendations.append({
                "priority": "HIGH",
                "action": "Create/complete device profile",
                "details": "Open Armoury Crate → Device → Add Device, or re-sync device registration"
            })

        # Drivers
        drivers = findings.get("drivers", {})
        if not drivers.get("installed"):
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Install/update ASUS device drivers",
                "details": "Download latest drivers from ASUS support website for your model"
            })

        # Services
        services = findings.get("services", {})
        if not services.get("all_running"):
            stopped = [s for s, status in services.get("services", {}).items() if status != "running"]
            if stopped:
                recommendations.append({
                    "priority": "HIGH",
                    "action": "Start required services",
                    "details": f"Start services: {', '.join(stopped)}. Use: sc start <service_name>"
                })

        # Registry consistency
        registry = findings.get("registry", {})
        if not registry.get("consistent"):
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Fix registry inconsistencies",
                "details": "Sync device registration between HKCU and HKLM registries"
            })

        # General recommendation
        recommendations.append({
            "priority": "LOW",
            "action": "Re-register device in Armoury Crate",
            "details": "Open Armoury Crate → Settings → Device → Remove and re-add device"
        })

        return recommendations


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        diagnostic = JARVISPartialDeviceRegistrationDiagnostic(project_root)
        results = diagnostic.run_diagnostic()

        print("=" * 70)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 70)
        print(f"Root Causes Found: {len(results['root_causes'])}")
        print(f"Recommendations: {len(results['recommendations'])}")
        print()
        print("KEY FINDINGS:")
        print(f"  • Device Detected: {results['findings']['detection'].get('detected', False)}")
        print(f"  • Registration Complete: {results['findings']['registration'].get('complete', False)}")
        print(f"  • Profile Complete: {results['findings']['profile'].get('complete', False)}")
        print(f"  • Drivers Installed: {results['findings']['drivers'].get('installed', False)}")
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import os


    main()