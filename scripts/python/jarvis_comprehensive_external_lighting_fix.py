#!/usr/bin/env python3
"""
JARVIS Comprehensive External Lighting Fix

"EXTERNAL LIGHTING ISSUES NOT PREVIOUSLY RESOLVED."

Comprehensive diagnostic and solution system for persistent external lighting issues.
AacAmbientLighting process keeps restarting - this system attempts all known methods
and identifies root causes.

@JARVIS @EXTERNAL_LIGHTING @AacAmbientLighting @COMPREHENSIVE @DIAGNOSTIC @FIX
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ComprehensiveExternalLightingFix")


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check"""
    check_name: str
    status: str  # "PASS", "FAIL", "WARNING", "UNKNOWN"
    details: str
    actionable: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "check_name": self.check_name,
            "status": self.status,
            "details": self.details,
            "actionable": self.actionable,
            "metadata": self.metadata
        }


@dataclass
class SolutionAttempt:
    """Record of a solution attempt"""
    solution_id: str
    method: str
    description: str
    executed: bool = False
    success: bool = False
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "solution_id": self.solution_id,
            "method": self.method,
            "description": self.description,
            "executed": self.executed,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }


class ComprehensiveExternalLightingFix:
    """
    Comprehensive External Lighting Fix

    "EXTERNAL LIGHTING ISSUES NOT PREVIOUSLY RESOLVED."

    Comprehensive diagnostic and solution system for persistent external lighting issues.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "external_lighting_fix"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("ComprehensiveExternalLightingFix")

        self.diagnostics: List[DiagnosticResult] = []
        self.solution_attempts: List[SolutionAttempt] = []

        self.logger.info("=" * 70)
        self.logger.info("🔧 COMPREHENSIVE EXTERNAL LIGHTING FIX")
        self.logger.info("   EXTERNAL LIGHTING ISSUES NOT PREVIOUSLY RESOLVED")
        self.logger.info("=" * 70)
        self.logger.info("")

    def run_comprehensive_diagnostics(self) -> List[DiagnosticResult]:
        """Run comprehensive diagnostics"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🔍 RUNNING COMPREHENSIVE DIAGNOSTICS")
        self.logger.info("=" * 70)
        self.logger.info("")

        diagnostics = []

        # 1. Check if AacAmbientLighting is running
        self.logger.info("   🔍 Check 1: Is AacAmbientLighting running?")
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.stdout.strip():
                diagnostics.append(DiagnosticResult(
                    check_name="AacAmbientLighting_Running",
                    status="FAIL",
                    details=f"AacAmbientLighting is running: {result.stdout.strip()}",
                    actionable=True,
                    metadata={"process_running": True, "output": result.stdout.strip()}
                ))
                self.logger.info(f"      ❌ FAIL: AacAmbientLighting is running")
            else:
                diagnostics.append(DiagnosticResult(
                    check_name="AacAmbientLighting_Running",
                    status="PASS",
                    details="AacAmbientLighting is not running",
                    actionable=False,
                    metadata={"process_running": False}
                ))
                self.logger.info(f"      ✅ PASS: AacAmbientLighting is not running")
        except Exception as e:
            diagnostics.append(DiagnosticResult(
                check_name="AacAmbientLighting_Running",
                status="UNKNOWN",
                details=f"Could not check: {str(e)}",
                actionable=False,
                metadata={"error": str(e)}
            ))
            self.logger.info(f"      ⚠️  UNKNOWN: Could not check: {str(e)}")

        # 2. Check for parent services
        self.logger.info("   🔍 Check 2: Are parent services running?")
        services_to_check = [
            "ArmouryCrateService",
            "LightingService",
            "AuraWallpaperService",
            "AuraService"
        ]
        running_services = []
        for service in services_to_check:
            try:
                result = subprocess.run(
                    ["powershell", "-Command", f"Get-Service -Name '{service}' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Status"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "Running" in result.stdout:
                    running_services.append(service)
            except Exception:
                pass

        if running_services:
            diagnostics.append(DiagnosticResult(
                check_name="Parent_Services_Running",
                status="WARNING",
                details=f"Parent services running: {', '.join(running_services)}",
                actionable=True,
                metadata={"running_services": running_services}
            ))
            self.logger.info(f"      ⚠️  WARNING: Parent services running: {', '.join(running_services)}")
        else:
            diagnostics.append(DiagnosticResult(
                check_name="Parent_Services_Running",
                status="PASS",
                details="No parent services running",
                actionable=False,
                metadata={"running_services": []}
            ))
            self.logger.info(f"      ✅ PASS: No parent services running")

        # 3. Check for scheduled tasks
        self.logger.info("   🔍 Check 3: Are there scheduled tasks?")
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-ScheduledTask | Where-Object {$_.TaskName -like '*Lighting*' -or $_.TaskName -like '*Aac*' -or $_.TaskName -like '*Ambient*'} | Select-Object -ExpandProperty TaskName"],
                capture_output=True,
                text=True,
                timeout=10
            )
            tasks = [t.strip() for t in result.stdout.strip().split('\n') if t.strip()]
            if tasks:
                diagnostics.append(DiagnosticResult(
                    check_name="Scheduled_Tasks",
                    status="WARNING",
                    details=f"Scheduled tasks found: {', '.join(tasks)}",
                    actionable=True,
                    metadata={"tasks": tasks}
                ))
                self.logger.info(f"      ⚠️  WARNING: Scheduled tasks found: {', '.join(tasks)}")
            else:
                diagnostics.append(DiagnosticResult(
                    check_name="Scheduled_Tasks",
                    status="PASS",
                    details="No relevant scheduled tasks found",
                    actionable=False,
                    metadata={"tasks": []}
                ))
                self.logger.info(f"      ✅ PASS: No relevant scheduled tasks found")
        except Exception as e:
            diagnostics.append(DiagnosticResult(
                check_name="Scheduled_Tasks",
                status="UNKNOWN",
                details=f"Could not check: {str(e)}",
                actionable=False,
                metadata={"error": str(e)}
            ))
            self.logger.info(f"      ⚠️  UNKNOWN: Could not check: {str(e)}")

        # 4. Check for startup programs
        self.logger.info("   🔍 Check 4: Are there startup programs?")
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-CimInstance Win32_StartupCommand | Where-Object {$_.Name -like '*Lighting*' -or $_.Name -like '*Aac*' -or $_.Name -like '*Ambient*'} | Select-Object -ExpandProperty Name"],
                capture_output=True,
                text=True,
                timeout=10
            )
            startup_programs = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
            if startup_programs:
                diagnostics.append(DiagnosticResult(
                    check_name="Startup_Programs",
                    status="WARNING",
                    details=f"Startup programs found: {', '.join(startup_programs)}",
                    actionable=True,
                    metadata={"startup_programs": startup_programs}
                ))
                self.logger.info(f"      ⚠️  WARNING: Startup programs found: {', '.join(startup_programs)}")
            else:
                diagnostics.append(DiagnosticResult(
                    check_name="Startup_Programs",
                    status="PASS",
                    details="No relevant startup programs found",
                    actionable=False,
                    metadata={"startup_programs": []}
                ))
                self.logger.info(f"      ✅ PASS: No relevant startup programs found")
        except Exception as e:
            diagnostics.append(DiagnosticResult(
                check_name="Startup_Programs",
                status="UNKNOWN",
                details=f"Could not check: {str(e)}",
                actionable=False,
                metadata={"error": str(e)}
            ))
            self.logger.info(f"      ⚠️  UNKNOWN: Could not check: {str(e)}")

        # 5. Check registry for auto-start entries
        self.logger.info("   🔍 Check 5: Registry auto-start entries?")
        registry_paths = [
            r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        ]
        registry_entries = []
        for reg_path in registry_paths:
            try:
                result = subprocess.run(
                    ["powershell", "-Command", f"Get-ItemProperty -Path 'Registry::{reg_path}' -ErrorAction SilentlyContinue | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                entries = [e.strip() for e in result.stdout.strip().split('\n') if e.strip() and ('Lighting' in e or 'Aac' in e or 'Ambient' in e)]
                registry_entries.extend(entries)
            except Exception:
                pass

        if registry_entries:
            diagnostics.append(DiagnosticResult(
                check_name="Registry_AutoStart",
                status="WARNING",
                details=f"Registry auto-start entries found: {', '.join(registry_entries)}",
                actionable=True,
                metadata={"registry_entries": registry_entries}
            ))
            self.logger.info(f"      ⚠️  WARNING: Registry auto-start entries found: {', '.join(registry_entries)}")
        else:
            diagnostics.append(DiagnosticResult(
                check_name="Registry_AutoStart",
                status="PASS",
                details="No relevant registry auto-start entries found",
                actionable=False,
                metadata={"registry_entries": []}
            ))
            self.logger.info(f"      ✅ PASS: No relevant registry auto-start entries found")

        # 6. Check for driver-level processes
        self.logger.info("   🔍 Check 6: Driver-level processes?")
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*Lighting*' -or $_.ProcessName -like '*Aac*' -or $_.ProcessName -like '*Ambient*'} | Select-Object -ExpandProperty ProcessName"],
                capture_output=True,
                text=True,
                timeout=10
            )
            processes = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
            if processes:
                diagnostics.append(DiagnosticResult(
                    check_name="Driver_Level_Processes",
                    status="WARNING",
                    details=f"Driver-level processes found: {', '.join(processes)}",
                    actionable=False,  # May be hardware-level
                    metadata={"processes": processes}
                ))
                self.logger.info(f"      ⚠️  WARNING: Driver-level processes found: {', '.join(processes)}")
            else:
                diagnostics.append(DiagnosticResult(
                    check_name="Driver_Level_Processes",
                    status="PASS",
                    details="No driver-level processes found",
                    actionable=False,
                    metadata={"processes": []}
                ))
                self.logger.info(f"      ✅ PASS: No driver-level processes found")
        except Exception as e:
            diagnostics.append(DiagnosticResult(
                check_name="Driver_Level_Processes",
                status="UNKNOWN",
                details=f"Could not check: {str(e)}",
                actionable=False,
                metadata={"error": str(e)}
            ))
            self.logger.info(f"      ⚠️  UNKNOWN: Could not check: {str(e)}")

        self.diagnostics = diagnostics
        return diagnostics

    def attempt_solutions(self) -> List[SolutionAttempt]:
        """Attempt all known solutions"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🔧 ATTEMPTING SOLUTIONS")
        self.logger.info("=" * 70)
        self.logger.info("")

        attempts = []

        # Solution 1: Kill AacAmbientLighting process
        self.logger.info("   🔧 Solution 1: Kill AacAmbientLighting process")
        attempt = SolutionAttempt(
            solution_id="KILL_PROCESS",
            method="Kill AacAmbientLighting process",
            description="Kill AacAmbientLighting process directly",
            timestamp=datetime.now()
        )
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue | Stop-Process -Force"],
                capture_output=True,
                text=True,
                timeout=10
            )
            time.sleep(2)  # Wait for restart

            # Check if it restarted
            check = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if check.stdout.strip():
                attempt.executed = True
                attempt.success = False
                attempt.error = "Process restarted immediately"
                self.logger.info(f"      ❌ FAILED: Process restarted immediately")
            else:
                attempt.executed = True
                attempt.success = True
                self.logger.info(f"      ✅ SUCCESS: Process killed and stayed dead")
        except Exception as e:
            attempt.executed = True
            attempt.success = False
            attempt.error = str(e)
            self.logger.info(f"      ❌ ERROR: {str(e)}")

        attempts.append(attempt)

        # Solution 2: Stop parent services
        self.logger.info("   🔧 Solution 2: Stop parent services")
        attempt = SolutionAttempt(
            solution_id="STOP_SERVICES",
            method="Stop parent services",
            description="Stop all parent services that might restart AacAmbientLighting",
            timestamp=datetime.now()
        )
        try:
            services = ["ArmouryCrateService", "LightingService", "AuraWallpaperService", "AuraService"]
            stopped = []
            for service in services:
                try:
                    subprocess.run(
                        ["powershell", "-Command", f"Stop-Service -Name '{service}' -Force -ErrorAction SilentlyContinue"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    stopped.append(service)
                except Exception:
                    pass

            time.sleep(3)  # Wait for restart

            # Check if AacAmbientLighting restarted
            check = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if check.stdout.strip():
                attempt.executed = True
                attempt.success = False
                attempt.error = "Process restarted despite stopping services"
                attempt.metadata = {"stopped_services": stopped}
                self.logger.info(f"      ❌ FAILED: Process restarted despite stopping {len(stopped)} services")
            else:
                attempt.executed = True
                attempt.success = True
                attempt.metadata = {"stopped_services": stopped}
                self.logger.info(f"      ✅ SUCCESS: Process stayed dead after stopping {len(stopped)} services")
        except Exception as e:
            attempt.executed = True
            attempt.success = False
            attempt.error = str(e)
            self.logger.info(f"      ❌ ERROR: {str(e)}")

        attempts.append(attempt)

        # Solution 3: Disable scheduled tasks
        self.logger.info("   🔧 Solution 3: Disable scheduled tasks")
        attempt = SolutionAttempt(
            solution_id="DISABLE_TASKS",
            method="Disable scheduled tasks",
            description="Disable scheduled tasks that might restart AacAmbientLighting",
            timestamp=datetime.now()
        )
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-ScheduledTask | Where-Object {$_.TaskName -like '*Lighting*' -or $_.TaskName -like '*Aac*' -or $_.TaskName -like '*Ambient*'} | Disable-ScheduledTask"],
                capture_output=True,
                text=True,
                timeout=10
            )

            attempt.executed = True
            attempt.success = True  # Assume success if no error
            attempt.metadata = {"output": result.stdout}
            self.logger.info(f"      ✅ SUCCESS: Scheduled tasks disabled")
        except Exception as e:
            attempt.executed = True
            attempt.success = False
            attempt.error = str(e)
            self.logger.info(f"      ❌ ERROR: {str(e)}")

        attempts.append(attempt)

        # Solution 4: Kill process tree
        self.logger.info("   🔧 Solution 4: Kill process tree")
        attempt = SolutionAttempt(
            solution_id="KILL_TREE",
            method="Kill process tree",
            description="Kill AacAmbientLighting and all child processes",
            timestamp=datetime.now()
        )
        try:
            # Get process ID first
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.stdout.strip():
                pid = result.stdout.strip()
                # Kill process tree
                subprocess.run(
                    ["powershell", "-Command", f"Stop-Process -Id {pid} -Force"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

            time.sleep(2)

            # Check if it restarted
            check = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if check.stdout.strip():
                attempt.executed = True
                attempt.success = False
                attempt.error = "Process restarted after killing tree"
                self.logger.info(f"      ❌ FAILED: Process restarted after killing tree")
            else:
                attempt.executed = True
                attempt.success = True
                self.logger.info(f"      ✅ SUCCESS: Process tree killed and stayed dead")
        except Exception as e:
            attempt.executed = True
            attempt.success = False
            attempt.error = str(e)
            self.logger.info(f"      ❌ ERROR: {str(e)}")

        attempts.append(attempt)

        self.solution_attempts = attempts
        return attempts

    def create_comprehensive_report(self) -> Dict[str, Any]:
        try:
            """Create comprehensive report"""
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 CREATING COMPREHENSIVE REPORT")
            self.logger.info("=" * 70)
            self.logger.info("")

            # Run diagnostics
            diagnostics = self.run_comprehensive_diagnostics()

            # Attempt solutions
            attempts = self.attempt_solutions()

            # Calculate statistics
            total_diagnostics = len(diagnostics)
            actionable_diagnostics = len([d for d in diagnostics if d.actionable])
            total_attempts = len(attempts)
            successful_attempts = len([a for a in attempts if a.success])

            # Final check
            self.logger.info("")
            self.logger.info("   🔍 Final Check: Is AacAmbientLighting still running?")
            final_check = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=10
            )

            final_status = "RUNNING" if final_check.stdout.strip() else "STOPPED"

            # Create report
            report = {
                "report_id": f"external_lighting_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "issue": "EXTERNAL LIGHTING ISSUES NOT PREVIOUSLY RESOLVED",
                "final_status": final_status,
                "diagnostics": [d.to_dict() for d in diagnostics],
                "solution_attempts": [a.to_dict() for a in attempts],
                "statistics": {
                    "total_diagnostics": total_diagnostics,
                    "actionable_diagnostics": actionable_diagnostics,
                    "total_attempts": total_attempts,
                    "successful_attempts": successful_attempts,
                    "success_rate": successful_attempts / total_attempts if total_attempts > 0 else 0.0
                },
                "root_cause_analysis": {
                    "if_process_restarts": "Process is restarting at hardware/firmware level - beyond software control",
                    "if_services_restart": "Services are restarting - may be managed by Windows or hardware",
                    "if_tasks_exist": "Scheduled tasks may be restarting the process",
                    "if_registry_entries": "Registry auto-start entries may be restarting the process",
                    "if_driver_level": "Driver-level processes may be restarting - hardware/firmware control"
                },
                "recommendations": {
                    "if_software_fails": [
                        "1. Check BIOS/UEFI settings for lighting control",
                        "2. Disable lighting in BIOS/UEFI if possible",
                        "3. Reinstall/update Armoury Crate drivers",
                        "4. Physically disconnect external lighting if possible",
                        "5. Contact ASUS support for hardware-level control"
                    ],
                    "if_hardware_level": [
                        "1. BIOS/UEFI settings are the only software-accessible hardware control",
                        "2. Physical disconnection may be required",
                        "3. Driver reinstallation may help",
                        "4. Contact ASUS support for firmware-level control"
                    ]
                },
                "escalation_path": {
                    "level_1": "Software-level fixes (process kill, service stop, task disable)",
                    "level_2": "Registry and startup program fixes",
                    "level_3": "BIOS/UEFI settings",
                    "level_4": "Driver reinstallation",
                    "level_5": "Physical disconnection or ASUS support"
                }
            }

            # Save report
            filename = self.data_dir / f"external_lighting_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 REPORT SUMMARY")
            self.logger.info("=" * 70)
            self.logger.info(f"   🔍 Total Diagnostics: {total_diagnostics}")
            self.logger.info(f"   🔍 Actionable Diagnostics: {actionable_diagnostics}")
            self.logger.info(f"   🔧 Total Attempts: {total_attempts}")
            self.logger.info(f"   ✅ Successful Attempts: {successful_attempts}")
            self.logger.info(f"   📊 Success Rate: {report['statistics']['success_rate']:.0%}")
            self.logger.info(f"   🎯 Final Status: {final_status}")
            self.logger.info("")

            if final_status == "RUNNING":
                self.logger.info("   ⚠️  RECOMMENDATIONS:")
                self.logger.info("      1. Check BIOS/UEFI settings for lighting control")
                self.logger.info("      2. Disable lighting in BIOS/UEFI if possible")
                self.logger.info("      3. Reinstall/update Armoury Crate drivers")
                self.logger.info("      4. Physically disconnect external lighting if possible")
                self.logger.info("      5. Contact ASUS support for hardware-level control")
            else:
                self.logger.info("   ✅ SUCCESS: External lighting is disabled")

            self.logger.info("")
            self.logger.info(f"✅ Report saved: {filename}")
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✅ COMPREHENSIVE EXTERNAL LIGHTING FIX COMPLETE")
            self.logger.info("=" * 70)
            self.logger.info("")

            return report


        except Exception as e:
            self.logger.error(f"Error in create_comprehensive_report: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        fixer = ComprehensiveExternalLightingFix(project_root)
        report = fixer.create_comprehensive_report()

        print()
        print("=" * 70)
        print("🔧 COMPREHENSIVE EXTERNAL LIGHTING FIX")
        print("=" * 70)
        print(f"   🔍 Total Diagnostics: {report['statistics']['total_diagnostics']}")
        print(f"   🔧 Total Attempts: {report['statistics']['total_attempts']}")
        print(f"   ✅ Successful Attempts: {report['statistics']['successful_attempts']}")
        print(f"   📊 Success Rate: {report['statistics']['success_rate']:.0%}")
        print(f"   🎯 Final Status: {report['final_status']}")
        print()
        if report['final_status'] == "RUNNING":
            print("   ⚠️  RECOMMENDATIONS:")
            for rec in report['recommendations']['if_software_fails']:
                print(f"      {rec}")
        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()