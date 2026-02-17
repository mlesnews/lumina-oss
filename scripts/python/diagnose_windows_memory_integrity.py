#!/usr/bin/env python3
"""
Windows Memory Integrity Diagnostic and Remediation Tool

Diagnoses and attempts to fix Windows Memory Integrity (Core Isolation) issues
where the setting won't stay enabled after reboot.

Author: <COMPANY_NAME> LLC
Date: 2025-01-XX
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MemoryIntegrityDiagnostic")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class MemoryIntegrityStatus(Enum):
    """Memory Integrity status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNKNOWN = "unknown"
    ERROR = "error"


class DiagnosticResult(Enum):
    """Diagnostic result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INFO = "info"


@dataclass
class MemoryIntegrityDiagnostic:
    """Memory Integrity diagnostic results"""

    memory_integrity_enabled: bool
    status: MemoryIntegrityStatus
    incompatible_drivers: List[str]
    virtualization_enabled: bool
    hyper_v_enabled: bool
    bios_virtualization: Optional[bool]
    registry_value: Optional[int]
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class WindowsMemoryIntegrityDiagnostic:
    """Diagnostic tool for Windows Memory Integrity"""

    def __init__(self) -> None:
        """Initialize diagnostic tool"""
        self.logger = logger
        self.results = MemoryIntegrityDiagnostic(
            memory_integrity_enabled=False,
            status=MemoryIntegrityStatus.UNKNOWN,
            incompatible_drivers=[],
            virtualization_enabled=False,
            hyper_v_enabled=False,
            bios_virtualization=None,
            registry_value=None,
            errors=[],
            warnings=[],
            recommendations=[]
        )

    def check_memory_integrity_status(self) -> bool:
        """
        Check if Memory Integrity is enabled via registry and PowerShell.

        Returns:
            True if enabled, False otherwise
        """
        try:
            # Method 1: Check registry key
            cmd = [
                "reg", "query",
                r"HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity",
                "/v", "Enabled",
                "/t", "REG_DWORD"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            registry_enabled = False
            if result.returncode == 0:
                # Parse the output to find Enabled value
                for line in result.stdout.split('\n'):
                    if 'Enabled' in line and 'REG_DWORD' in line:
                        # Extract hex value (0x1 = enabled, 0x0 = disabled)
                        parts = line.split()
                        for part in parts:
                            if part.startswith('0x'):
                                value = int(part, 16)
                                self.results.registry_value = value
                                registry_enabled = value == 1
                                break
            else:
                # Registry key doesn't exist or inaccessible
                self.results.registry_value = 0

            # Method 2: Check via PowerShell Get-CimInstance (more reliable)
            ps_cmd = (
                "$ci = Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root/Microsoft/Windows/DeviceGuard; "
                "if ($ci -ne $null -and $ci.VirtualizationBasedSecurityStatus -ne $null) { "
                "  $status = $ci.VirtualizationBasedSecurityStatus; "
                "  Write-Host $status; "
                "} else { Write-Host '0' }"
            )

            ps_result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                check=False
            )

            # Check Windows Security Center directly
            ps_cmd2 = (
                "Get-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\CI\\Config' -Name 'VulnerableDriverBlocklistEnable' -ErrorAction SilentlyContinue | "
                "Select-Object -ExpandProperty VulnerableDriverBlocklistEnable"
            )

            ps_result2 = subprocess.run(
                ["powershell", "-Command", ps_cmd2],
                capture_output=True,
                text=True,
                check=False
            )

            # Determine actual status
            is_enabled = registry_enabled

            # If registry says enabled but user reports it's not persisting, there may be a driver conflict
            if is_enabled:
                self.results.warnings.append(
                    "Memory Integrity is enabled in registry but may not persist after reboot. "
                    "This typically indicates incompatible drivers or virtualization conflicts."
                )

            self.results.memory_integrity_enabled = is_enabled
            self.results.status = (
                MemoryIntegrityStatus.ENABLED if is_enabled
                else MemoryIntegrityStatus.DISABLED
            )
            return is_enabled

        except Exception as e:
            self.results.errors.append(f"Failed to check registry: {e}")
            self.results.status = MemoryIntegrityStatus.ERROR
            self.logger.error(f"Error checking registry: {e}")
            return False

    def check_virtualization_enabled(self) -> bool:
        """
        Check if virtualization is enabled in Windows.

        Returns:
            True if virtualization features are available
        """
        try:
            # Check via systeminfo
            result = subprocess.run(
                ["systeminfo"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                # Check for hyper-v requirements
                hyper_v_requirements_met = (
                    "a hypervisor has been detected" in output or
                    "hyper-v requirements" in output
                )
                self.results.virtualization_enabled = hyper_v_requirements_met
                return hyper_v_requirements_met
            else:
                # Try alternative method using PowerShell
                ps_cmd = "Get-ComputerInfo -Property 'HyperV*' | ConvertTo-Json"
                result = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    check=False
                )

                if result.returncode == 0:
                    # Check if virtualization is available
                    self.results.virtualization_enabled = True
                    return True

        except Exception as e:
            self.results.warnings.append(f"Could not verify virtualization status: {e}")
            self.logger.warning(f"Error checking virtualization: {e}")

        return False

    def check_hyper_v_status(self) -> bool:
        """
        Check if Hyper-V is enabled.

        Returns:
            True if Hyper-V is enabled
        """
        try:
            # Check via DISM or Get-WindowsOptionalFeature
            ps_cmd = (
                "Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All | "
                "Select-Object -ExpandProperty State"
            )
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                output = result.stdout.strip().lower()
                is_enabled = "enabled" in output
                self.results.hyper_v_enabled = is_enabled
                return is_enabled
        except Exception as e:
            self.results.warnings.append(f"Could not check Hyper-V status: {e}")
            self.logger.warning(f"Error checking Hyper-V: {e}")

        return False

    def find_incompatible_drivers(self) -> List[str]:
        """
        Find drivers incompatible with Memory Integrity.

        Returns:
            List of incompatible driver names
        """
        incompatible: List[str] = []

        try:
            # Method 1: Check Event Viewer for Memory Integrity blocking events (Event ID 3076)
            # This is the most reliable method - shows what Memory Integrity actually blocked
            ps_cmd = (
                "$events = Get-WinEvent -FilterHashtable @{"
                "LogName='Microsoft-Windows-CodeIntegrity/Operational'; "
                "ID=3076,3077"
                "} -MaxEvents 100 -ErrorAction SilentlyContinue; "
                "$drivers = @(); "
                "$events | ForEach-Object { "
                "  $msg = $_.Message; "
                "  if ($msg -match 'Driver:\\s+([^\\r\\n]+)') { "
                "    $drivers += $matches[1]; "
                "  } "
                "  if ($msg -match 'Image Path:\\s+([^\\r\\n]+)') { "
                "    $drivers += $matches[1]; "
                "  } "
                "}; "
                "$drivers | Sort-Object -Unique | ForEach-Object { Write-Host $_ }"
            )

            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse driver names from output
                lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
                incompatible.extend(lines)

            # Method 2: Check System logs for Hyper-V related errors
            ps_cmd2 = (
                "Get-WinEvent -FilterHashtable @{"
                "LogName='System'; "
                "ProviderName='Microsoft-Windows-Hyper-V-Hypervisor'"
                "} -MaxEvents 20 -ErrorAction SilentlyContinue | "
                "Where-Object { $_.LevelDisplayName -eq 'Error' -or $_.LevelDisplayName -eq 'Warning' } | "
                "Select-Object -First 5 -ExpandProperty Message"
            )

            result2 = subprocess.run(
                ["powershell", "-Command", ps_cmd2],
                capture_output=True,
                text=True,
                check=False
            )

            if result2.returncode == 0 and result2.stdout.strip():
                self.results.warnings.append(
                    "Found Hyper-V related errors in System log - may indicate Memory Integrity conflicts"
                )

            # Method 3: Check for unsigned/legacy drivers using driverquery
            driver_result = subprocess.run(
                ["driverquery", "/v", "/fo", "csv"],
                capture_output=True,
                text=True,
                check=False
            )

            if driver_result.returncode == 0:
                # Parse CSV output to find unsigned drivers
                lines = driver_result.stdout.split('\n')
                for line in lines[1:]:  # Skip header
                    if 'Not Available' in line or 'N/A' in line:
                        # Extract driver name
                        parts = line.split(',')
                        if len(parts) > 0:
                            driver_name = parts[0].strip('"')
                            if driver_name and driver_name not in incompatible:
                                incompatible.append(driver_name)

            if incompatible:
                self.results.incompatible_drivers = incompatible
                self.results.warnings.append(
                    f"Found {len(incompatible)} potentially incompatible drivers or blocked operations"
                )

        except Exception as e:
            self.results.warnings.append(f"Could not fully scan for incompatible drivers: {e}")
            self.logger.warning(f"Error finding incompatible drivers: {e}")

        return incompatible

    def check_bios_virtualization(self) -> Optional[bool]:
        """
        Attempt to determine if BIOS virtualization is enabled.

        Returns:
            True if enabled, False if disabled, None if unknown
        """
        try:
            # Check via WMI
            ps_cmd = (
                "$proc = Get-WmiObject -Class Win32_Processor; "
                "$proc | Select-Object -ExpandProperty VirtualizationFirmwareEnabled"
            )

            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                output = result.stdout.strip().lower()
                if "true" in output:
                    self.results.bios_virtualization = True
                    return True
                elif "false" in output:
                    self.results.bios_virtualization = False
                    self.results.errors.append(
                        "BIOS virtualization (VT-x/AMD-V) appears to be disabled. "
                        "Enable it in BIOS/UEFI settings."
                    )
                    return False

        except Exception as e:
            self.results.warnings.append(f"Could not verify BIOS virtualization: {e}")
            self.logger.warning(f"Error checking BIOS: {e}")

        return None

    def generate_recommendations(self) -> None:
        """Generate recommendations based on diagnostic results"""
        recommendations: List[str] = []

        # If Memory Integrity is enabled but not persisting, this is a specific issue
        if self.results.memory_integrity_enabled:
            recommendations.append(
                "[CRITICAL] Memory Integrity IS enabled in registry but not persisting after reboot. "
                "This indicates a driver conflict or policy override."
            )
            recommendations.append(
                "Check Windows Event Viewer > Applications and Services Logs > "
                "Microsoft > Windows > CodeIntegrity > Operational for Event ID 3076 or 3077 "
                "(these indicate blocked drivers that prevent Memory Integrity from starting)"
            )
            recommendations.append(
                "Also check System log for Hyper-V or Virtualization Based Security errors "
                "around the time of boot/shutdown"
            )

        if not self.results.memory_integrity_enabled:
            recommendations.append("Enable Memory Integrity in Windows Security settings")

        if not self.results.virtualization_enabled:
            recommendations.append(
                "Enable virtualization features in BIOS/UEFI (VT-x for Intel or AMD-V for AMD). "
                "Memory Integrity requires hardware virtualization support."
            )

        if self.results.bios_virtualization is False:
            recommendations.append(
                "CRITICAL: BIOS/UEFI virtualization is disabled. Reboot and enable VT-x (Intel) "
                "or AMD-V (AMD) in BIOS settings. Memory Integrity cannot work without this."
            )

        if self.results.incompatible_drivers:
            recommendations.append(
                f"Found {len(self.results.incompatible_drivers)} potentially incompatible driver(s):"
            )
            for driver in self.results.incompatible_drivers[:5]:  # Show first 5
                recommendations.append(f"  - {driver}")
            recommendations.append(
                "Update or remove incompatible drivers. Common culprits: "
                "older VPN clients, virtualization software (VMware, VirtualBox), "
                "anti-cheat software, some security tools, or outdated hardware drivers"
            )
            recommendations.append(
                "Check Windows Update for driver updates. Run: "
                "Settings > Update & Security > Windows Update > Check for updates"
            )

        # Check for Group Policy conflicts
        recommendations.append(
            "Check if Group Policy is overriding Memory Integrity settings. Run: "
            "'gpedit.msc' > Computer Configuration > Administrative Templates > "
            "System > Device Guard > Verify 'Turn On Virtualization Based Security' setting"
        )

        # Specific fix for persistence issue
        if self.results.memory_integrity_enabled:
            recommendations.append(
                "To force Memory Integrity to persist: "
                "1. Update all drivers to latest versions "
                "2. Remove or disable any incompatible software "
                "3. Enable Memory Integrity via Windows Security (not just registry) "
                "4. Restart immediately - do NOT let the system sleep/hibernate "
                "5. After reboot, verify it's still enabled in Windows Security"
            )

        recommendations.append(
            "If issue persists, try disabling then re-enabling Core Isolation: "
            "Windows Security > Device security > Core isolation > Memory integrity OFF, "
            "restart, then turn it back ON"
        )

        self.results.recommendations = recommendations

    def enable_memory_integrity(self) -> bool:
        """
        Attempt to enable Memory Integrity via registry.

        WARNING: This requires administrator privileges and may cause system instability
        if incompatible drivers are present.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Set registry value to enable Memory Integrity
            cmd = [
                "reg", "add",
                r"HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity",
                "/v", "Enabled",
                "/t", "REG_DWORD",
                "/d", "1",
                "/f"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.info("Memory Integrity registry value set successfully")
                return True
            else:
                self.results.errors.append(
                    f"Failed to set registry value: {result.stderr}"
                )
                self.logger.error(f"Failed to enable Memory Integrity: {result.stderr}")
                return False

        except Exception as e:
            self.results.errors.append(f"Exception enabling Memory Integrity: {e}")
            self.logger.error(f"Error enabling Memory Integrity: {e}")
            return False

    def run_full_diagnostic(self) -> MemoryIntegrityDiagnostic:
        """
        Run complete diagnostic suite.

        Returns:
            Diagnostic results
        """
        self.logger.info("Starting Windows Memory Integrity diagnostic...")

        # Run all diagnostic checks
        self.check_memory_integrity_status()
        self.check_virtualization_enabled()
        self.check_hyper_v_status()
        self.check_bios_virtualization()
        self.find_incompatible_drivers()
        self.generate_recommendations()

        self.logger.info("Diagnostic complete")
        return self.results

    def save_report(self, output_path: Path) -> None:
        try:
            """Save diagnostic report to JSON file"""
            report_dict = self.results.to_dict()
            # Convert Enum values to strings for JSON serialization
            report_dict["status"] = self.results.status.value
            report = {
                "timestamp": str(Path(__file__).stat().st_mtime),
                "diagnostic": report_dict
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"Report saved to {output_path}")


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main() -> int:
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Diagnose and fix Windows Memory Integrity issues"
        )
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Attempt to enable Memory Integrity (requires admin privileges)"
        )
        parser.add_argument(
            "--report",
            type=Path,
            default=Path("data/memory_integrity_diagnostic.json"),
            help="Path to save diagnostic report"
        )

        args = parser.parse_args()

        diagnostic = WindowsMemoryIntegrityDiagnostic()
        results = diagnostic.run_full_diagnostic()

        # Print summary
        print("\n" + "="*70)
        print("WINDOWS MEMORY INTEGRITY DIAGNOSTIC REPORT")
        print("="*70 + "\n")

        print(f"Status: {results.status.value.upper()}")
        print(f"Memory Integrity Enabled: {results.memory_integrity_enabled}")
        print(f"Registry Value: {hex(results.registry_value) if results.registry_value is not None else 'N/A'}")
        print(f"Virtualization Enabled: {results.virtualization_enabled}")
        print(f"Hyper-V Enabled: {results.hyper_v_enabled}")
        print(f"BIOS Virtualization: {results.bios_virtualization}")
        print(f"Incompatible Drivers Found: {len(results.incompatible_drivers)}")

        if results.incompatible_drivers:
            print("\nIncompatible Drivers:")
            for driver in results.incompatible_drivers:
                print(f"  - {driver}")

        if results.errors:
            print("\nErrors:")
            for error in results.errors:
                print(f"  [ERROR] {error}")

        if results.warnings:
            print("\nWarnings:")
            for warning in results.warnings:
                print(f"  [WARNING] {warning}")

        if results.recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(results.recommendations, 1):
                print(f"  {i}. {rec}")

        print("\n" + "="*70 + "\n")

        # Save report
        args.report.parent.mkdir(parents=True, exist_ok=True)
        diagnostic.save_report(args.report)

        # Attempt to enable if requested
        if args.enable:
            print("Attempting to enable Memory Integrity...")
            print("WARNING: This requires administrator privileges and may require a reboot.")
            print("Ensure all incompatible drivers are updated before enabling.\n")

            if diagnostic.enable_memory_integrity():
                print("[SUCCESS] Memory Integrity enabled in registry.")
                print("[WARNING] RESTART YOUR COMPUTER for changes to take effect.")
                print("[WARNING] If the setting reverts after reboot, check for incompatible drivers.")
            else:
                print("[ERROR] Failed to enable Memory Integrity. Check error messages above.")
                return 1

        return 0 if results.status != MemoryIntegrityStatus.ERROR else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())