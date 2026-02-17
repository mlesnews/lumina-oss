#!/usr/bin/env python3
"""
ASUS Armoury Crate Device Registration Checker/Fixer

Checks and fixes device registration with ASUS Armoury Crate.
Device shows up correctly with ASUS but not registered in Armoury Crate.

Tags: #ASUS #ARMOURYCRATE #DEVICE #REGISTRATION @JARVIS @DOIT @RR
"""

import sys
import os
import json
import subprocess
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

logger = get_logger("ASUSArmouryCrateDeviceRegistration")


class ASUSArmouryCrateDeviceRegistration:
    """
    Check and fix ASUS Armoury Crate device registration

    Issues:
    - Device registered with ASUS but not in Armoury Crate
    - Device not showing up in Armoury Crate device list
    - Registration sync issues
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Armoury Crate paths
        self.armoury_paths = [
            Path("C:/Program Files/ASUS/ARMOURY CRATE Service"),
            Path("C:/Program Files (x86)/ASUS/ARMOURY CRATE Service"),
            Path(os.environ.get("LOCALAPPDATA", "")) / "ASUS" / "ARMOURY CRATE Service"
        ]

        # Registry paths
        self.registry_paths = {
            "device_info": r"SOFTWARE\ASUS\ARMOURY CRATE",
            "device_registration": r"SOFTWARE\ASUS\ARMOURY CRATE\Device",
            "asus_registration": r"SOFTWARE\ASUS\DeviceRegistration"
        }

    def check_device_registration(self) -> Dict[str, Any]:
        """Check device registration status"""
        status = {
            "asus_registered": False,
            "armoury_crate_registered": False,
            "device_info": {},
            "issues": [],
            "recommendations": []
        }

        try:
            # Check ASUS registration
            asus_reg = self._check_asus_registration()
            status["asus_registered"] = asus_reg.get("registered", False)
            status["device_info"].update(asus_reg.get("device_info", {}))

            # Check Armoury Crate registration
            armoury_reg = self._check_armoury_crate_registration()
            status["armoury_crate_registered"] = armoury_reg.get("registered", False)
            status["device_info"].update(armoury_reg.get("device_info", {}))

            # Identify issues
            if status["asus_registered"] and not status["armoury_crate_registered"]:
                status["issues"].append(
                    "Device registered with ASUS but not in Armoury Crate"
                )
                status["recommendations"].append(
                    "Sync device registration from ASUS to Armoury Crate"
                )

            if not status["asus_registered"]:
                status["issues"].append("Device not registered with ASUS")
                status["recommendations"].append("Register device with ASUS first")

            return status

        except Exception as e:
            self.logger.error(f"❌ Failed to check device registration: {e}", exc_info=True)
            status["error"] = str(e)
            return status

    def _check_asus_registration(self) -> Dict[str, Any]:
        """Check ASUS device registration"""
        result = {
            "registered": False,
            "device_info": {}
        }

        try:
            # Check registry
            reg_path = self.registry_paths["asus_registration"]
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    reg_path,
                    0,
                    winreg.KEY_READ
                )

                # Read device info
                try:
                    device_id = winreg.QueryValueEx(key, "DeviceID")[0]
                    device_name = winreg.QueryValueEx(key, "DeviceName")[0]
                    registration_date = winreg.QueryValueEx(key, "RegistrationDate")[0]

                    result["registered"] = True
                    result["device_info"] = {
                        "device_id": device_id,
                        "device_name": device_name,
                        "registration_date": registration_date
                    }

                    self.logger.info(f"✅ Device registered with ASUS: {device_name}")
                except FileNotFoundError:
                    self.logger.warning("⚠️  Device registration keys not found in ASUS registry")
                finally:
                    key.Close()

            except FileNotFoundError:
                self.logger.warning(f"⚠️  ASUS registration registry path not found: {reg_path}")
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to read ASUS registry: {e}")

            # Check via PowerShell (alternative method)
            ps_command = """
            Get-ItemProperty -Path "HKLM:\\SOFTWARE\\ASUS\\DeviceRegistration" -ErrorAction SilentlyContinue |
            Select-Object DeviceID, DeviceName, RegistrationDate
            """

            ps_result = self._run_powershell(ps_command)
            if ps_result.get("success") and ps_result.get("stdout"):
                result["registered"] = True
                self.logger.info("✅ Device registration found via PowerShell")

        except Exception as e:
            self.logger.error(f"❌ Failed to check ASUS registration: {e}")

        return result

    def _check_armoury_crate_registration(self) -> Dict[str, Any]:
        """Check Armoury Crate device registration"""
        result = {
            "registered": False,
            "device_info": {}
        }

        try:
            # Check registry
            reg_path = self.registry_paths["device_registration"]
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    reg_path,
                    0,
                    winreg.KEY_READ
                )

                # Read device info
                try:
                    device_id = winreg.QueryValueEx(key, "DeviceID")[0]
                    device_name = winreg.QueryValueEx(key, "DeviceName")[0]

                    result["registered"] = True
                    result["device_info"] = {
                        "device_id": device_id,
                        "device_name": device_name
                    }

                    self.logger.info(f"✅ Device registered in Armoury Crate: {device_name}")
                except FileNotFoundError:
                    self.logger.warning("⚠️  Device registration keys not found in Armoury Crate registry")
                finally:
                    key.Close()

            except FileNotFoundError:
                self.logger.warning(f"⚠️  Armoury Crate registration registry path not found: {reg_path}")
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to read Armoury Crate registry: {e}")

            # Check if Armoury Crate service is running
            service_running = self._check_armoury_service()
            result["service_running"] = service_running

        except Exception as e:
            self.logger.error(f"❌ Failed to check Armoury Crate registration: {e}")

        return result

    def _check_armoury_service(self) -> bool:
        """Check if Armoury Crate service is running"""
        try:
            ps_command = "Get-Service -Name '*Armoury*' | Select-Object Name, Status"
            result = self._run_powershell(ps_command)

            if result.get("success") and result.get("stdout"):
                output = result["stdout"]
                if "Running" in output:
                    self.logger.info("✅ Armoury Crate service is running")
                    return True
                else:
                    self.logger.warning("⚠️  Armoury Crate service is not running")
                    return False
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to check service: {e}")

        return False

    def _run_powershell(self, command: str) -> Dict[str, Any]:
        """Execute PowerShell command"""
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def fix_device_registration(self) -> Dict[str, Any]:
        """Attempt to fix device registration"""
        result = {
            "success": False,
            "steps_taken": [],
            "errors": []
        }

        try:
            # Step 1: Check current status
            status = self.check_device_registration()
            result["steps_taken"].append("Checked current registration status")

            if status["asus_registered"] and not status["armoury_crate_registered"]:
                # Step 2: Sync registration from ASUS to Armoury Crate
                self.logger.info("🔄 Syncing device registration from ASUS to Armoury Crate...")

                sync_result = self._sync_registration()
                if sync_result.get("success"):
                    result["steps_taken"].append("Synced registration from ASUS to Armoury Crate")
                else:
                    result["errors"].append(f"Failed to sync registration: {sync_result.get('error')}")

                # Step 3: Restart Armoury Crate service
                self.logger.info("🔄 Restarting Armoury Crate service...")
                restart_result = self._restart_armoury_service()
                if restart_result.get("success"):
                    result["steps_taken"].append("Restarted Armoury Crate service")
                else:
                    result["errors"].append(f"Failed to restart service: {restart_result.get('error')}")

                # Step 4: Verify registration
                verify_status = self.check_device_registration()
                if verify_status["armoury_crate_registered"]:
                    result["success"] = True
                    result["steps_taken"].append("Verified registration - device now registered")
                else:
                    result["errors"].append("Registration sync completed but verification failed")
            else:
                result["errors"].append("Device registration status does not require fixing")

        except Exception as e:
            self.logger.error(f"❌ Failed to fix device registration: {e}", exc_info=True)
            result["errors"].append(str(e))

        return result

    def _sync_registration(self) -> Dict[str, Any]:
        """Sync device registration from ASUS to Armoury Crate"""
        try:
            # Get ASUS registration info
            asus_reg = self._check_asus_registration()
            if not asus_reg.get("registered"):
                return {"success": False, "error": "Device not registered with ASUS"}

            device_info = asus_reg.get("device_info", {})

            # Write to Armoury Crate registry
            reg_path = self.registry_paths["device_registration"]
            try:
                key = winreg.CreateKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    reg_path
                )

                winreg.SetValueEx(key, "DeviceID", 0, winreg.REG_SZ, device_info.get("device_id", ""))
                winreg.SetValueEx(key, "DeviceName", 0, winreg.REG_SZ, device_info.get("device_name", ""))
                winreg.SetValueEx(key, "SyncDate", 0, winreg.REG_SZ, datetime.now().isoformat())

                key.Close()

                self.logger.info("✅ Synced device registration to Armoury Crate registry")
                return {"success": True}

            except Exception as e:
                self.logger.error(f"❌ Failed to write to registry: {e}")
                return {"success": False, "error": str(e)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _restart_armoury_service(self) -> Dict[str, Any]:
        """Restart Armoury Crate service"""
        try:
            ps_command = """
            $service = Get-Service -Name '*Armoury*' | Select-Object -First 1
            if ($service) {
                Restart-Service -Name $service.Name -Force
                Write-Output "Service restarted: $($service.Name)"
            } else {
                Write-Output "No Armoury Crate service found"
            }
            """

            result = self._run_powershell(ps_command)
            if result.get("success"):
                self.logger.info("✅ Armoury Crate service restarted")
                return {"success": True}
            else:
                return {"success": False, "error": result.get("stderr", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Check and fix ASUS Armoury Crate device registration"
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Check device registration status"
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Attempt to fix device registration"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        checker = ASUSArmouryCrateDeviceRegistration(project_root)

        if args.check:
            status = checker.check_device_registration()
            print("\n" + "="*80)
            print("ASUS ARMOURY CRATE DEVICE REGISTRATION STATUS")
            print("="*80)
            print(f"ASUS Registered: {'✅' if status['asus_registered'] else '❌'}")
            print(f"Armoury Crate Registered: {'✅' if status['armoury_crate_registered'] else '❌'}")

            if status.get("device_info"):
                print("\nDevice Info:")
                for key, value in status["device_info"].items():
                    print(f"  {key}: {value}")

            if status.get("issues"):
                print("\nIssues:")
                for issue in status["issues"]:
                    print(f"  ⚠️  {issue}")

            if status.get("recommendations"):
                print("\nRecommendations:")
                for rec in status["recommendations"]:
                    print(f"  💡 {rec}")

            print("="*80)

        if args.fix:
            result = checker.fix_device_registration()
            print("\n" + "="*80)
            print("DEVICE REGISTRATION FIX RESULT")
            print("="*80)
            print(f"Success: {'✅' if result['success'] else '❌'}")

            if result.get("steps_taken"):
                print("\nSteps Taken:")
                for step in result["steps_taken"]:
                    print(f"  ✅ {step}")

            if result.get("errors"):
                print("\nErrors:")
                for error in result["errors"]:
                    print(f"  ❌ {error}")

            print("="*80)

        if not args.check and not args.fix:
            parser.print_help()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import os


    sys.exit(main())