#!/usr/bin/env python3
"""
LUMINA Headless Startup Daemon
==============================
Consolidated single-process startup that runs headlessly (no visible terminals).
Aggregates all startup tasks and monitors logs for errors.

Replaces:
- Multiple startup folder .bat files
- Multiple Task Scheduler tasks
- Separate lighting/VA/router processes

Features:
- Single headless daemon
- Aggregated logging with error monitoring
- EST timezone-aware lighting control
- FN key testing REMOVED (lighting via registry/@MANUS only)
- Efficient startup sequence

@LUMINA @STARTUP @HEADLESS @DAEMON @OPTIMIZED
"""

import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import unified logger
from lumina_unified_logger import LuminaUnifiedLogger
logger = get_logger("lumina_headless_startup_daemon")


# ============================================================================
# LOGGING SETUP - Unified Logger Integration
# ============================================================================
# Uses lumina_unified_logger for NAS (L: drive) integration
# HeadlessLogger wraps it with custom methods (phase, success, error tracking)
# ============================================================================


class HeadlessLogger:
    """
    Custom logger wrapper for startup daemon.
    Uses unified logger internally for NAS integration.
    Provides custom methods (phase, success) and error tracking.
    """

    def __init__(self):
        # Use unified logger for NAS integration
        self._unified_logger = LuminaUnifiedLogger("Application", "Startup")
        self._logger = self._unified_logger.get_logger()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self._lock = threading.Lock()
        self.using_nas = self._unified_logger.nas_available

    def _write(self, level: str, message: str):
        """Write log message using unified logger"""
        with self._lock:
            # Map custom levels to standard logging levels
            if level == "SUCCESS":
                self._logger.info(f"✅ {message}")
            elif level == "PHASE":
                self._logger.info(f"📋 {message}")
            elif level == "ERROR":
                self._logger.error(message)
                self.errors.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
            elif level == "WARN":
                self._logger.warning(message)
                self.warnings.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
            else:
                self._logger.info(message)

    def info(self, message: str):
        self._write("INFO", message)

    def success(self, message: str):
        self._write("SUCCESS", message)

    def warn(self, message: str):
        self._write("WARN", message)

    def error(self, message: str):
        self._write("ERROR", message)

    def phase(self, message: str):
        self._write("PHASE", message)

    def get_errors(self) -> List[str]:
        return self.errors.copy()

    def get_warnings(self) -> List[str]:
        return self.warnings.copy()


@dataclass
class StartupConfig:
    """Startup configuration"""

    # Timing
    stabilization_delay_seconds: int = 5
    phase_delay_seconds: int = 2
    # Network drives: wait at boot so scripts don't timeout when drives are slow to connect
    wait_for_network_drives: bool = True
    wait_for_drives_timeout_seconds: int = 90
    wait_for_drives_check_interval_seconds: int = 5

    # Lighting (EST timezone). USER POLICY: Keyboard always 100%; external ON during day.
    keyboard_brightness_daylight: int = 100  # Daylight: 100%
    keyboard_brightness_night: int = 100  # Night: 100% (no dim — user policy)
    external_lighting_always_off: bool = False  # External ON during day, off at night

    # Features (FN key testing removed per user request - lighting via registry/@MANUS only)
    enable_secrets: bool = True
    enable_lighting: bool = True
    enable_router: bool = True
    enable_vas: bool = True


class LuminaHeadlessStartupDaemon:
    """
    Headless startup daemon - consolidates all startup into one process.
    No visible terminals. Aggregated logging with error monitoring.
    """

    def __init__(self, config: Optional[StartupConfig] = None):
        self.config = config or StartupConfig()
        self.logger = HeadlessLogger()
        self.start_time = datetime.now()
        self.python_exe = sys.executable
        self.results: Dict[str, Any] = {}
        self._shortcut_daemon: Optional[Any] = None  # Shortcut maintenance daemon reference

    def _get_est_time(self) -> datetime:
        """Get current time in EST"""
        est = timezone(timedelta(hours=-5))
        return datetime.now(est)

    def _is_daylight_hours_est(self) -> bool:
        """Check if daylight hours (6 AM - 8 PM EST)"""
        est_time = self._get_est_time()
        return 6 <= est_time.hour < 20

    def _run_script(
        self, script_path: Path, args: List[str] = None, wait: bool = True, timeout: int = 60
    ) -> Dict[str, Any]:
        """Run a Python script headlessly"""
        if not script_path.exists():
            return {"success": False, "error": f"Script not found: {script_path}"}

        cmd = [self.python_exe, str(script_path)]
        if args:
            cmd.extend(args)

        try:
            if wait:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(PROJECT_ROOT),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            else:
                # Start in background
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=str(PROJECT_ROOT),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
                return {"success": True, "pid": process.pid, "background": True}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_powershell(
        self, script_path: Path, args: List[str] = None, wait: bool = True, timeout: int = 60
    ) -> Dict[str, Any]:
        """Run a PowerShell script headlessly"""
        if not script_path.exists():
            return {"success": False, "error": f"Script not found: {script_path}"}

        cmd = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-WindowStyle",
            "Hidden",
            "-File",
            str(script_path),
        ]
        if args:
            cmd.extend(args)

        try:
            if wait:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(PROJECT_ROOT),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=str(PROJECT_ROOT),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
                return {"success": True, "pid": process.pid, "background": True}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # PHASE 0: WAIT FOR NETWORK DRIVES (prevents timeout on reboot when drives are slow)
    # =========================================================================
    def phase0_wait_for_network_drives(self) -> Dict[str, Any]:
        """Wait for configured network drives before running phases that use NAS/drives."""
        if not self.config.wait_for_network_drives:
            return {"success": True, "skipped": True}

        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 0: WAIT FOR NETWORK DRIVES")
        self.logger.phase("=" * 70)

        wait_script = PROJECT_ROOT / "scripts" / "powershell" / "Wait-ForNetworkDrives.ps1"
        if not wait_script.exists():
            self.logger.warn("   Wait-ForNetworkDrives.ps1 not found; skipping drive wait")
            return {"success": True, "skipped": True, "reason": "script not found"}

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-WindowStyle",
                    "Hidden",
                    "-File",
                    str(wait_script),
                    "-Silent",
                    "-TimeoutSeconds",
                    str(self.config.wait_for_drives_timeout_seconds),
                    "-CheckIntervalSeconds",
                    str(self.config.wait_for_drives_check_interval_seconds),
                ],
                capture_output=True,
                text=True,
                timeout=self.config.wait_for_drives_timeout_seconds + 10,
                cwd=str(PROJECT_ROOT),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            if result.returncode == 0:
                self.logger.success("   Network drives ready")
                return {"success": True}
            self.logger.warn("   Some drives not ready; continuing anyway")
            return {"success": True, "drives_ready": False}
        except subprocess.TimeoutExpired:
            self.logger.warn("   Wait for drives timed out; continuing anyway")
            return {"success": True, "timeout": True}
        except Exception as e:
            self.logger.warn(f"   Wait-ForNetworkDrives had issues: {e}")
            return {"success": True, "error": str(e)}

    # =========================================================================
    # PHASE 1: SECRETS & ENVIRONMENT
    # =========================================================================
    def phase1_secrets(self) -> Dict[str, Any]:
        """Load secrets from Azure Key Vault"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 1: SECRETS & ENVIRONMENT")
        self.logger.phase("=" * 70)

        if not self.config.enable_secrets:
            self.logger.info("   Skipping secrets (disabled)")
            return {"success": True, "skipped": True}

        script = PROJECT_ROOT / "scripts" / "startup" / "lumina_secure_startup.ps1"
        result = self._run_powershell(script, ["-Silent"], timeout=30)

        if result.get("success"):
            self.logger.success("   Azure Key Vault secrets loaded")
        else:
            self.logger.warn(f"   Secrets loading had issues: {result.get('error', 'unknown')}")

        return result

    # =========================================================================
    # PHASE 2: LIGHTING CONTROL (single system — JARVIS Smart Lighting)
    # =========================================================================
    def phase2_lighting(self) -> Dict[str, Any]:
        """Configure lighting via JARVIS Smart Lighting Day/Night Sync (single source of truth)."""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 2: LIGHTING CONTROL (JARVIS Smart Lighting, EST Timezone)")
        self.logger.phase("=" * 70)

        if not self.config.enable_lighting:
            self.logger.info("   Skipping lighting (disabled)")
            return {"success": True, "skipped": True}

        # Single-run guard: skip if lighting already ran recently (unified or another path)
        try:
            from lighting_startup_guard import (
                mark_lighting_startup_done,
                should_skip_lighting_startup,
            )

            if should_skip_lighting_startup(PROJECT_ROOT):
                self.logger.info("   Lighting already run recently (single-run guard); skipping.")
                return {"success": True, "skipped": True, "reason": "single_run_guard"}
            mark_lighting_startup_done(PROJECT_ROOT)
        except ImportError:
            pass

        self.logger.info("   Using JARVIS Smart Lighting (single lighting system)")

        try:
            from scripts.python.jarvis_smart_lighting_day_night_sync import (
                SmartLightingDayNightSync,
            )

            sync = SmartLightingDayNightSync(PROJECT_ROOT)
            result = sync.setup_smart_lighting()
            settings = result.get("settings", {})
            return {
                "success": True,
                "keyboard_brightness": settings.get("keyboard_brightness", 100),
                "external_enabled": 1 if (settings.get("external_lighting", 0) > 0) else 0,
                "is_daylight_hours": None,
                "method": "jarvis_smart_lighting",
                "manus_used": False,
                "steps_completed": list(settings.keys()) if settings else [],
            }
        except ImportError as e:
            self.logger.warn("   JARVIS Smart Lighting not available: %s", e)
            return {"success": False, "skipped": False, "error": str(e)}
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("   JARVIS Smart Lighting failed: %s", e)
            return {"success": False, "skipped": False, "error": str(e)}

    def _fallback_registry_lighting(
        self, keyboard_brightness: int, external_enabled: bool, is_daylight: bool
    ) -> Dict[str, Any]:
        """Fallback to direct registry control if @MANUS unavailable"""
        external_val = 1 if external_enabled else 0
        ps_script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura'
)

foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }}
        Set-ItemProperty -Path $path -Name 'Brightness' -Value {keyboard_brightness} -Type DWord -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value {keyboard_brightness} -Type DWord -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value {external_val} -Type DWord -ErrorAction SilentlyContinue
    }} catch {{}}
}}
Write-Output "OK"
"""
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            self.logger.success(
                f"   Keyboard: {keyboard_brightness}% (always ON — user policy) [registry fallback]"
            )
            self.logger.success(
                f"   External lighting: {'ON (daytime)' if external_enabled else 'OFF (night)'}"
            )

            return {
                "success": True,
                "keyboard_brightness": keyboard_brightness,
                "external_enabled": external_val,
                "is_daylight_hours": is_daylight,
                "method": "registry_fallback",
                "manus_used": False,
            }
        except Exception as e:
            self.logger.error(f"   Registry fallback failed: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # PHASE 3: CORE SERVICES (ULTRON ROUTER)
    # =========================================================================
    def phase3_services(self) -> Dict[str, Any]:
        """Start Ultron Router"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 3: CORE SERVICES")
        self.logger.phase("=" * 70)

        if not self.config.enable_router:
            self.logger.info("   Skipping router (disabled)")
            return {"success": True, "skipped": True}

        script = PROJECT_ROOT / "scripts" / "python" / "auto_start_ultron_router.py"
        result = self._run_script(script, ["--once"], wait=False, timeout=60)

        if result.get("success"):
            self.logger.success(f"   Ultron Router started (PID: {result.get('pid', 'N/A')})")
        else:
            self.logger.warn(f"   Router startup had issues: {result.get('error', 'unknown')}")

        return result

    # =========================================================================
    # PHASE 4: VIRTUAL ASSISTANTS (JARVIS FIRST IMPRESSION)
    # =========================================================================
    def phase4_virtual_assistants(self) -> Dict[str, Any]:
        try:
            """Start Virtual Assistants - JARVIS First"""
            self.logger.phase("=" * 70)
            self.logger.phase("PHASE 4: VIRTUAL ASSISTANTS (JARVIS First Impression)")
            self.logger.phase("=" * 70)

            if not self.config.enable_vas:
                self.logger.info("   Skipping VAs (disabled)")
                return {"success": True, "skipped": True}

            vas_started = []

            # Priority 1: JARVIS (THE FIRST IMPRESSION)
            jarvis_script = PROJECT_ROOT / "scripts" / "python" / "jarvis_default_va.py"
            if jarvis_script.exists():
                result = self._run_script(jarvis_script, wait=False)
                if result.get("success"):
                    vas_started.append("JARVIS")
                    self.logger.success("   JARVIS Virtual Assistant started (FIRST IMPRESSION)")
                else:
                    self.logger.error(f"   JARVIS failed to start: {result.get('error')}")

            time.sleep(2)

            # Priority 2: JARVIS Chat Coordinator
            chat_script = PROJECT_ROOT / "scripts" / "python" / "jarvis_va_chat_coordinator.py"
            if chat_script.exists():
                result = self._run_script(chat_script, wait=False)
                if result.get("success"):
                    vas_started.append("JARVIS_CHAT")
                    self.logger.success("   JARVIS Chat Coordinator started")

            # Priority 3: IMVA (optional)
            imva_script = PROJECT_ROOT / "scripts" / "python" / "jarvis_ironman_bobblehead_gui.py"
            if imva_script.exists():
                result = self._run_script(imva_script, wait=False)
                if result.get("success"):
                    vas_started.append("IMVA")
                    self.logger.success("   IMVA started")

            return {"success": len(vas_started) > 0, "vas_started": vas_started}

        except Exception as e:
            self.logger.error(f"Error in phase4_virtual_assistants: {e}", exc_info=True)
            raise

    # =========================================================================
    # PHASE 5: SHORTCUT MAINTENANCE
    # =========================================================================
    def phase5_shortcut_maintenance(self) -> Dict[str, Any]:
        """Start Shortcut Maintenance Daemon"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 5: SHORTCUT MAINTENANCE")
        self.logger.phase("=" * 70)

        try:
            # Import shortcut maintenance daemon
            from lumina_shortcut_maintenance_daemon import ShortcutMaintenanceDaemon

            # Initialize and start daemon
            daemon = ShortcutMaintenanceDaemon()
            daemon.start(background=True)

            # Get initial status
            status = daemon.get_status()

            self.logger.success("   Shortcut Maintenance Daemon started")
            self.logger.info(f"   Registered shortcuts: {status['shortcuts_registered']}")
            self.logger.info(f"   Check interval: {status['check_interval_minutes']} minutes")
            self.logger.info("   Monitoring: Active (background)")

            # Store daemon reference for potential future use
            self._shortcut_daemon = daemon

            return {
                "success": True,
                "shortcuts_registered": status["shortcuts_registered"],
                "check_interval_minutes": status["check_interval_minutes"],
            }
        except ImportError as e:
            self.logger.warn(f"   Shortcut maintenance module not available: {e}")
            return {"success": False, "error": "Module not found", "skipped": True}
        except Exception as e:
            self.logger.error(f"   Shortcut maintenance failed: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # PHASE 6: MYASUS HEALTH CHECK
    # =========================================================================
    def phase6_myasus_health_check(self) -> Dict[str, Any]:
        """Run MyASUS diagnostics on startup"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 6: MYASUS HEALTH CHECK")
        self.logger.phase("=" * 70)

        try:
            # Import MyASUS integration
            import asyncio

            from src.cfservices.services.jarvis_core.integrations.armoury_crate_myasus_hybrid import (
                create_hybrid_integration,
            )

            # Initialize integration
            integration = create_hybrid_integration(project_root=PROJECT_ROOT)

            if not integration.myasus_available:
                self.logger.info("   MyASUS: ❌ Not available (skipping health check)")
                return {"success": True, "skipped": True, "reason": "MyASUS not available"}

            self.logger.success("   MyASUS: ✅ Available")

            # Run diagnostics asynchronously
            async def run_diagnostics():
                try:
                    response = await integration.process_request(
                        {"action": "myasus_diagnostics", "source": "myasus"}
                    )
                    return response
                except Exception as e:
                    logger.error(f"   Diagnostics error: {e}")
                    return None

            # Run in event loop (or create new one if needed)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            response = loop.run_until_complete(run_diagnostics())

            if response and response.success:
                diagnostics = response.data.get("diagnostics", {})
                self.logger.success("   ✅ Diagnostics completed")

                # Log key system info
                if "system_info" in diagnostics:
                    sys_info = diagnostics["system_info"]
                    self.logger.info(f"   OS: {sys_info.get('os', 'Unknown')}")
                    self.logger.info(f"   Version: {sys_info.get('version', 'Unknown')}")

                if "hardware" in diagnostics:
                    hw = diagnostics["hardware"]
                    if "cpu" in hw:
                        self.logger.info(f"   CPU: {hw['cpu']}")
                    if "ram" in hw:
                        self.logger.info(f"   RAM: {hw['ram']} GB")

                return {
                    "success": True,
                    "diagnostics": diagnostics,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                error_msg = response.error if response else "Unknown error"
                self.logger.warn(f"   ⚠️  Diagnostics had issues: {error_msg}")
                return {"success": False, "error": error_msg}

        except ImportError as e:
            self.logger.warn(f"   MyASUS integration module not available: {e}")
            return {"success": False, "error": "Module not found", "skipped": True}
        except Exception as e:
            self.logger.error(f"   MyASUS health check failed: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    def run(self) -> Dict[str, Any]:
        """Execute all startup phases"""
        self.logger.phase("╔" + "═" * 68 + "╗")
        self.logger.phase("║     LUMINA HEADLESS STARTUP DAEMON                                 ║")
        self.logger.phase("║     Single-process startup - No visible terminals                  ║")
        self.logger.phase("║     FN Key Testing: DISABLED                                       ║")
        self.logger.phase("║     Logging: NAS L: Drive + Local (Dual-write)                     ║")
        self.logger.phase("╚" + "═" * 68 + "╝")
        self.logger.info("")
        self.logger.info(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        log_paths = self.logger._unified_logger.log_paths
        self.logger.info(f"Local log: {log_paths['local']}")
        if log_paths["nas_available"]:
            self.logger.info(f"NAS log: {log_paths['nas']} (L: drive connected)")
        else:
            self.logger.info("NAS log: Not available (L: drive not connected)")
        self.logger.info("")

        # Phase 0: Wait for network drives (avoids timeout when drives are slow at reboot)
        self.results["phase0"] = self.phase0_wait_for_network_drives()
        time.sleep(self.config.phase_delay_seconds)

        # Wait for system stabilization
        self.logger.info(
            f"Waiting {self.config.stabilization_delay_seconds}s for system stabilization..."
        )
        time.sleep(self.config.stabilization_delay_seconds)

        # Execute phases
        self.results["phase1"] = self.phase1_secrets()
        time.sleep(self.config.phase_delay_seconds)

        self.results["phase2"] = self.phase2_lighting()
        time.sleep(self.config.phase_delay_seconds)

        self.results["phase3"] = self.phase3_services()
        time.sleep(self.config.phase_delay_seconds)

        self.results["phase4"] = self.phase4_virtual_assistants()
        time.sleep(self.config.phase_delay_seconds)

        self.results["phase5"] = self.phase5_shortcut_maintenance()
        time.sleep(self.config.phase_delay_seconds)

        self.results["phase6"] = self.phase6_myasus_health_check()

        # Summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.logger.phase("")
        self.logger.phase("╔" + "═" * 68 + "╗")
        self.logger.phase("║                    STARTUP SUMMARY                                 ║")
        self.logger.phase("╚" + "═" * 68 + "╝")
        self.logger.info("")

        for phase_name, result in self.results.items():
            status = "✓" if result.get("success") else "✗"
            self.logger.info(f"   {phase_name}: {status}")

        self.logger.info("")
        self.logger.info(f"   Duration: {duration:.1f} seconds")
        self.logger.info(f"   Errors: {len(self.logger.get_errors())}")
        self.logger.info(f"   Warnings: {len(self.logger.get_warnings())}")
        self.logger.info(
            f"   NAS Logging: {'Active (L: drive)' if self.logger.using_nas else 'Local only'}"
        )

        # Report errors
        errors = self.logger.get_errors()
        if errors:
            self.logger.phase("")
            self.logger.phase("ERRORS DETECTED:")
            for err in errors:
                self.logger.error(f"   {err}")

        self.logger.phase("")
        self.logger.success("═" * 70)
        self.logger.success("LUMINA HEADLESS STARTUP COMPLETE")
        self.logger.success("═" * 70)

        log_paths = self.logger._unified_logger.log_paths
        return {
            "success": all(r.get("success", False) for r in self.results.values()),
            "duration": duration,
            "results": self.results,
            "errors": errors,
            "warnings": self.logger.get_warnings(),
            "log_file": log_paths["local"],
            "nas_log_file": log_paths["nas"],
            "nas_connected": log_paths["nas_available"],
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Headless Startup Daemon")
        parser.add_argument("--skip-secrets", action="store_true", help="Skip secrets loading")
        parser.add_argument(
            "--skip-lighting", action="store_true", help="Skip lighting configuration"
        )
        parser.add_argument("--skip-router", action="store_true", help="Skip router startup")
        parser.add_argument("--skip-vas", action="store_true", help="Skip VA startup")
        parser.add_argument(
            "--tail-log", action="store_true", help="Tail the log file after startup"
        )
        parser.add_argument("--install", action="store_true", help="Install as Task Scheduler task")

        args = parser.parse_args()

        if args.install:
            # Install as Task Scheduler task
            print("Installing LUMINA Headless Startup Daemon as Task Scheduler task...")
            script_path = Path(__file__).resolve()

            ps_install = f'''
$TaskName = "LUMINA-Headless-Startup-Daemon"
$TaskDesc = "LUMINA Headless Startup - Single process, no visible terminals"
$Action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument '"{script_path}"' -WorkingDirectory "{PROJECT_ROOT}"
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Trigger.Delay = "PT1M"
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\\$env:USERNAME" -LogonType Interactive -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description $TaskDesc -Force
Write-Output "Installed: $TaskName"
'''
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_install],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        return

        # Configure
        config = StartupConfig(
            enable_secrets=not args.skip_secrets,
            enable_lighting=not args.skip_lighting,
            enable_router=not args.skip_router,
            enable_vas=not args.skip_vas,
        )

        # Run
        daemon = LuminaHeadlessStartupDaemon(config)
        result = daemon.run()

        # Tail log if requested
        if args.tail_log:
            print("\n" + "=" * 70)
            print("TAILING LOG FOR ERRORS:")
            print("=" * 70)

            if result.get("errors"):
                for err in result["errors"]:
                    print(f"  ERROR: {err}")
            else:
                print("  No errors detected!")

            if result.get("warnings"):
                print("\nWARNINGS:")
                for warn in result["warnings"]:
                    print(f"  WARN: {warn}")

        # Exit code
        return 0 if result.get("success") else 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
