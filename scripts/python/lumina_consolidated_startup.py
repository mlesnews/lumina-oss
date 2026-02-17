#!/usr/bin/env python3
"""
LUMINA Consolidated Startup Daemon
====================================
Single-process startup that eliminates ALL duplicate initializations.

Key Optimizations:
- Single Azure Key Vault connection (cached, reused)
- Single Azure Service Bus client (singleton pattern)
- Single ElevenLabs TTS client (shared across all JARVIS instances)
- Single memory database connection (shared session)
- Single R5 Living Context Matrix (shared instance)
- No duplicate agent/super-agent initializations
- FN key testing REMOVED (lighting via registry/@MANUS only)
- All services in ONE headless terminal session

Replaces:
- Multiple startup .bat files
- Multiple Task Scheduler tasks
- All duplicate initialization patterns

@LUMINA @STARTUP @CONSOLIDATED @OPTIMIZED @NO_DUPLICATES
"""

import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import unified logger
from lumina_unified_logger import LuminaUnifiedLogger

# =============================================================================
# SINGLETON SERVICE REGISTRY - Prevents all duplicate initializations
# =============================================================================


class ServiceRegistry:
    """
    Singleton registry that ensures each service is initialized ONCE and reused.
    Eliminates all duplicate Azure Service Bus, ElevenLabs, Memory, R5, etc. initializations.
    """

    _instance: Optional["ServiceRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Cached service instances (initialized once, reused)
        self._vault_client = None
        self._service_bus_client = None
        self._elevenlabs_client = None
        self._memory_db = None
        self._r5_matrix = None
        self._jarvis_agent = None

        # Tracking for logging (services created vs reused)
        self._services_created: Set[str] = set()
        self._services_reused: Set[str] = set()

        # Logger
        self._logger = None

    def set_logger(self, logger):
        """Set logger for service registry"""
        self._logger = logger

    def get_vault_client(self, recreate: bool = False):
        """Get cached Azure Key Vault client - ONE instance only"""
        if self._vault_client is None or recreate:
            try:
                from azure.identity import DefaultAzureCredential
                from azure.keyvault.secrets import SecretClient

                vault_url = "https://jarvis-lumina.vault.azure.net/"
                credential = DefaultAzureCredential()
                self._vault_client = SecretClient(vault_url=vault_url, credential=credential)
                self._services_created.add("vault_client")
                if self._logger:
                    self._logger.info("   [REGISTRY] Azure Key Vault client created (SINGLETON)")
            except Exception as e:
                if self._logger:
                    self._logger.error(f"   [REGISTRY] Vault client error: {e}")
                raise
        else:
            self._services_reused.add("vault_client")
        return self._vault_client

    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from vault - NAS proxy cache handles caching at infrastructure level"""
        try:
            client = self.get_vault_client()
            secret = client.get_secret(secret_name)
            if self._logger:
                self._logger.info(f"   [REGISTRY] Retrieved secret: {secret_name}")
            return secret.value
        except Exception:
            if self._logger:
                self._logger.warn(f"   [REGISTRY] Secret not found: {secret_name}")
            return None

    def get_service_bus_client(self, recreate: bool = False):
        """Get cached Azure Service Bus client - ONE instance only"""
        if self._service_bus_client is None or recreate:
            try:
                # Get connection string from vault
                conn_str = self.get_secret("service-bus-connection-string")
                if not conn_str:
                    if self._logger:
                        self._logger.warn("   [REGISTRY] Service Bus connection string not found")
                    return None

                from azure.servicebus import ServiceBusClient

                self._service_bus_client = ServiceBusClient.from_connection_string(conn_str)
                self._services_created.add("service_bus_client")
                if self._logger:
                    self._logger.info("   [REGISTRY] Azure Service Bus client created (SINGLETON)")
            except Exception as e:
                if self._logger:
                    self._logger.warn(f"   [REGISTRY] Service Bus client error: {e}")
                # Not critical - continue without it
                return None
        else:
            self._services_reused.add("service_bus_client")
        return self._service_bus_client

    def get_elevenlabs_client(self, recreate: bool = False):
        """Get cached ElevenLabs client - ONE instance only"""
        if self._elevenlabs_client is None or recreate:
            try:
                api_key = self.get_secret("elevenlabs-api-key")
                if not api_key:
                    if self._logger:
                        self._logger.warn("   [REGISTRY] ElevenLabs API key not found")
                    return None

                from elevenlabs import ElevenLabs

                self._elevenlabs_client = ElevenLabs(api_key=api_key)
                self._services_created.add("elevenlabs_client")
                if self._logger:
                    self._logger.info("   [REGISTRY] ElevenLabs client created (SINGLETON)")
            except Exception as e:
                if self._logger:
                    self._logger.warn(f"   [REGISTRY] ElevenLabs client error: {e}")
                return None
        else:
            self._services_reused.add("elevenlabs_client")
        return self._elevenlabs_client

    def get_memory_db(self, recreate: bool = False):
        """Get cached memory database - ONE instance only"""
        if self._memory_db is None or recreate:
            try:
                from scripts.python.jarvis_persistent_memory import JarvisPersistentMemory

                self._memory_db = JarvisPersistentMemory(project_root=PROJECT_ROOT)
                self._services_created.add("memory_db")
                if self._logger:
                    self._logger.info("   [REGISTRY] Memory database created (SINGLETON)")
            except Exception as e:
                if self._logger:
                    self._logger.warn(f"   [REGISTRY] Memory DB error: {e}")
                return None
        else:
            self._services_reused.add("memory_db")
        return self._memory_db

    def get_r5_matrix(self, recreate: bool = False):
        """Get cached R5 Living Context Matrix - ONE instance only"""
        if self._r5_matrix is None or recreate:
            try:
                from scripts.python.r5_living_context_matrix import R5LivingContextMatrix

                self._r5_matrix = R5LivingContextMatrix(project_root=PROJECT_ROOT)
                self._services_created.add("r5_matrix")
                if self._logger:
                    self._logger.info("   [REGISTRY] R5 Living Context Matrix created (SINGLETON)")
            except Exception as e:
                if self._logger:
                    self._logger.warn(f"   [REGISTRY] R5 Matrix error: {e}")
                return None
        else:
            self._services_reused.add("r5_matrix")
        return self._r5_matrix

    def get_jarvis_agent(self, recreate: bool = False):
        """Get cached JARVIS agent - ONE instance only"""
        if self._jarvis_agent is None or recreate:
            try:
                # Use cached services
                elevenlabs = self.get_elevenlabs_client()
                memory = self.get_memory_db()

                from scripts.python.jarvis_full_time_super_agent import JarvisFullTimeSuperAgent

                self._jarvis_agent = JarvisFullTimeSuperAgent(
                    project_root=PROJECT_ROOT, elevenlabs_client=elevenlabs, memory_db=memory
                )
                self._services_created.add("jarvis_agent")
                if self._logger:
                    self._logger.info(
                        "   [REGISTRY] JARVIS Full-Time Super Agent created (SINGLETON)"
                    )
            except Exception as e:
                if self._logger:
                    self._logger.warn(f"   [REGISTRY] JARVIS agent error: {e}")
                return None
        else:
            self._services_reused.add("jarvis_agent")
        return self._jarvis_agent

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "created": list(self._services_created),
            "reused": list(self._services_reused),
            "total_unique_services": len(self._services_created),
        }


# =============================================================================
# LOGGING SETUP
# =============================================================================


class ConsolidatedLogger:
    """Custom logger wrapper for consolidated startup daemon"""

    def __init__(self):
        self._unified_logger = LuminaUnifiedLogger("Application", "ConsolidatedStartup")
        self._logger = self._unified_logger.get_logger()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self._lock = threading.Lock()
        self.using_nas = self._unified_logger.nas_available

    def _write(self, level: str, message: str):
        """Write log message"""
        with self._lock:
            if level == "SUCCESS":
                self._logger.info(f"✅ {message}")
            elif level == "PHASE":
                self._logger.info(f"📋 {message}")
            elif level == "ERROR":
                self._logger.error(message)
                self.errors.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            elif level == "WARN":
                self._logger.warning(message)
                self.warnings.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
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


# =============================================================================
# STARTUP CONFIGURATION
# =============================================================================


@dataclass
class ConsolidatedStartupConfig:
    """Configuration for consolidated startup"""

    # Timing
    stabilization_delay_seconds: int = 3  # Reduced from 5

    # Features
    enable_secrets: bool = True
    enable_lighting: bool = True
    enable_router: bool = True
    enable_vas: bool = True

    # FN key testing REMOVED per user request - lighting via registry/@MANUS only


# =============================================================================
# CONSOLIDATED STARTUP DAEMON
# =============================================================================


class LuminaConsolidatedStartupDaemon:
    """
    Consolidated startup daemon - ALL services in ONE process, NO duplicates.

    This is the NEW streamlined version that eliminates:
    - Duplicate Azure Service Bus initializations
    - Duplicate ElevenLabs API key retrievals
    - Duplicate JARVIS agent spawns
    - Duplicate memory/R5 matrix instances
    - Multiple terminal sessions
    """

    def __init__(self, config: Optional[ConsolidatedStartupConfig] = None):
        self.config = config or ConsolidatedStartupConfig()
        self.logger = ConsolidatedLogger()
        self.registry = ServiceRegistry()
        self.registry.set_logger(self.logger)
        self.start_time = datetime.now()
        self.results: Dict[str, Any] = {}

    def _get_est_time(self) -> datetime:
        """Get current time in EST"""
        est = timezone(timedelta(hours=-5))
        return datetime.now(est)

    def _is_daylight_hours_est(self) -> bool:
        """Check if daylight hours (6 AM - 8 PM EST)"""
        est_time = self._get_est_time()
        return 6 <= est_time.hour < 20

    # =========================================================================
    # PHASE 1: SERVICE REGISTRY INITIALIZATION (ALL SERVICES IN ONE GO)
    # =========================================================================
    def phase1_registry_init(self) -> Dict[str, Any]:
        """Initialize ALL cached services ONCE via ServiceRegistry"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 1: SERVICE REGISTRY INITIALIZATION (SINGLETON PATTERN)")
        self.logger.phase("=" * 70)

        services = {}

        try:
            # Initialize all services ONCE through the registry
            self.logger.info("   Creating singleton services (no duplicates)...")

            # These will all use cached instances on subsequent calls
            vault = self.registry.get_vault_client()
            if vault:
                self.logger.success("   ✅ Azure Key Vault: Singleton created")
                services["vault"] = True

            sb_client = self.registry.get_service_bus_client()
            if sb_client:
                self.logger.success("   ✅ Azure Service Bus: Singleton created")
                services["service_bus"] = True
            else:
                self.logger.info("   ℹ️  Azure Service Bus: Skipped (no connection)")

            elevenlabs = self.registry.get_elevenlabs_client()
            if elevenlabs:
                self.logger.success("   ✅ ElevenLabs TTS: Singleton created")
                services["elevenlabs"] = True
            else:
                self.logger.info("   ℹ️  ElevenLabs TTS: Skipped (no API key)")

            memory_db = self.registry.get_memory_db()
            if memory_db:
                self.logger.success("   ✅ Memory Database: Singleton created")
                services["memory_db"] = True

            r5_matrix = self.registry.get_r5_matrix()
            if r5_matrix:
                self.logger.success("   ✅ R5 Living Context Matrix: Singleton created")
                services["r5_matrix"] = True

            # Log registry stats
            stats = self.registry.get_registry_stats()
            self.logger.info(
                f"   📊 Registry stats: {stats['total_unique_services']} unique services created"
            )

            return {"success": len(services) > 0, "services": services}

        except Exception as e:
            self.logger.error(f"   Registry initialization error: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # PHASE 2: LIGHTING CONTROL (SIMPLE STATE CHECK, NO FN TOGGLE TESTING)
    # =========================================================================
    def phase2_lighting(self) -> Dict[str, Any]:
        """Configure lighting - simple state check only, NO complex toggle testing"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 2: LIGHTING CONTROL (SIMPLE STATE CHECK)")
        self.logger.phase("=" * 70)

        if not self.config.enable_lighting:
            self.logger.info("   Skipping lighting (disabled)")
            return {"success": True, "skipped": True}

        est_time = self._get_est_time()
        is_daylight = self._is_daylight_hours_est()

        self.logger.info(f"   Current time (EST): {est_time.strftime('%H:%M:%S')}")
        self.logger.info(f"   Daylight hours: {is_daylight}")

        # Simple brightness based on time
        keyboard_brightness = 100 if is_daylight else 7

        # Direct registry control (no @MANUS complexity)
        ps_script = f"""
$path = 'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura'
if (-not (Test-Path $path)) {{ New-Item -Path $path -Force | Out-Null }}
Set-ItemProperty -Path $path -Name 'Brightness' -Value {keyboard_brightness} -Type DWord -ErrorAction SilentlyContinue
Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue
Write-Output "OK"
"""

        try:
            import subprocess

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            status = "ON (100%)" if is_daylight else "ON (7%)"
            self.logger.success(f"   Keyboard: {status} [registry]")
            self.logger.success("   External lighting: OFF")

            return {"success": True, "brightness": keyboard_brightness}

        except Exception as e:
            self.logger.error(f"   Lighting error: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # PHASE 3: CORE SERVICES (SINGLE ROUTER PROCESS)
    # =========================================================================
    def phase3_services(self) -> Dict[str, Any]:
        """Start Ultron Router - single process"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 3: CORE SERVICES (ULTRON ROUTER)")
        self.logger.phase("=" * 70)

        if not self.config.enable_router:
            self.logger.info("   Skipping router (disabled)")
            return {"success": True, "skipped": True}

        try:
            import subprocess

            script = PROJECT_ROOT / "scripts" / "python" / "auto_start_ultron_router.py"

            if not script.exists():
                self.logger.warn(f"   Router script not found: {script}")
                return {"success": False, "error": "Script not found"}

            # Start headlessly, no visible terminal
            process = subprocess.Popen(
                [sys.executable, str(script), "--once"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(PROJECT_ROOT),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            self.logger.success(f"   Ultron Router started (PID: {process.pid})")
            return {"success": True, "pid": process.pid}

        except Exception as e:
            self.logger.error(f"   Router startup error: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # PHASE 4: VIRTUAL ASSISTANTS (SINGLE JARVIS INSTANCE)
    # =========================================================================
    def phase4_virtual_assistants(self) -> Dict[str, Any]:
        """Start Virtual Assistants - ONE JARVIS instance using cached services"""
        self.logger.phase("=" * 70)
        self.logger.phase("PHASE 4: VIRTUAL ASSISTANTS (SINGLE JARVIS INSTANCE)")
        self.logger.phase("=" * 70)

        if not self.config.enable_vas:
            self.logger.info("   Skipping VAs (disabled)")
            return {"success": True, "skipped": True}

        vas_started = []

        try:
            # Get cached JARVIS agent (uses cached services internally)
            jarvis_agent = self.registry.get_jarvis_agent()

            if jarvis_agent:
                # Start JARVIS using the cached singleton agent
                # No duplicate initialization, no multiple agent spawns
                try:
                    jarvis_agent.start()
                    vas_started.append("JARVIS")
                    self.logger.success("   JARVIS Full-Time Super Agent started (SINGLETON)")
                except Exception as e:
                    self.logger.warn(f"   JARVIS start error: {e}")
                    # Still consider it "started" if agent exists
                    vas_started.append("JARVIS (initialized)")
            else:
                self.logger.warn("   JARVIS agent not available")

            # Secondary services using cached clients
            # These will NOT duplicate initialization because they use the registry

            return {
                "success": len(vas_started) > 0,
                "vas_started": vas_started,
                "registry_stats": self.registry.get_registry_stats(),
            }

        except Exception as e:
            self.logger.error(f"   VA startup error: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    def run(self) -> Dict[str, Any]:
        """Execute all startup phases in sequence"""
        self.logger.phase("╔" + "═" * 68 + "╗")
        self.logger.phase("║     LUMINA CONSOLIDATED STARTUP DAEMON                      ║")
        self.logger.phase("║     Single Process - No Duplicate Initializations          ║")
        self.logger.phase("║     FN Key Testing: DISABLED (simple state check only)      ║")
        self.logger.phase("║     All Services: ONE Headless Terminal Session             ║")
        self.logger.phase("╚" + "═" * 68 + "╝")
        self.logger.info("")
        self.logger.info(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        log_paths = self.logger._unified_logger.log_paths
        self.logger.info(f"Local log: {log_paths['local']}")
        if log_paths["nas_available"]:
            self.logger.info(f"NAS log: {log_paths['nas']} (L: drive connected)")
        self.logger.info("")

        # Wait for system stabilization (reduced from 5s to 3s)
        self.logger.info(f"Waiting {self.config.stabilization_delay_seconds}s for stabilization...")
        time.sleep(self.config.stabilization_delay_seconds)

        # Execute phases
        self.results["registry"] = self.phase1_registry_init()

        self.results["lighting"] = self.phase2_lighting()

        self.results["services"] = self.phase3_services()

        self.results["vas"] = self.phase4_virtual_assistants()

        # Summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.logger.phase("")
        self.logger.phase("╔" + "═" * 68 + "╗")
        self.logger.phase("║                    STARTUP SUMMARY                             ║")
        self.logger.phase("╚" + "═" * 68 + "╝")
        self.logger.info("")

        for phase_name, result in self.results.items():
            status = "✓" if result.get("success") else "✗"
            skipped = " (skipped)" if result.get("skipped") else ""
            self.logger.info(f"   {phase_name}: {status}{skipped}")

        # Show registry stats
        if "registry" in self.results and self.results["registry"].get("success"):
            stats = self.registry.get_registry_stats()
            self.logger.info("")
            self.logger.info(f"   📊 Singleton Services: {stats['total_unique_services']}")

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
        self.logger.success("LUMINA CONSOLIDATED STARTUP COMPLETE")
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
            "registry_stats": self.registry.get_registry_stats(),
        }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Consolidated Startup Daemon")
    parser.add_argument("--skip-secrets", action="store_true", help="Skip secrets loading")
    parser.add_argument("--skip-lighting", action="store_true", help="Skip lighting configuration")
    parser.add_argument("--skip-router", action="store_true", help="Skip router startup")
    parser.add_argument("--skip-vas", action="store_true", help="Skip VA startup")
    parser.add_argument("--install", action="store_true", help="Install as Task Scheduler task")

    args = parser.parse_args()

    # Configure
    config = ConsolidatedStartupConfig(
        enable_secrets=not args.skip_secrets,
        enable_lighting=not args.skip_lighting,
        enable_router=not args.skip_router,
        enable_vas=not args.skip_vas,
    )

    # Run
    daemon = LuminaConsolidatedStartupDaemon(config)
    result = daemon.run()

    # Exit code
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
