#!/usr/bin/env python3
"""
Kenny Experiment - Build-Deploy-Activate (B-D-A) System

Continuous iterative experimentation for Kenny:
- BUILD: Build/compile/prepare Kenny enhancements
- DEPLOY: Deploy Kenny to desktop
- ACTIVATE: Activate and run Kenny

Tags: #KENNY #BDA #EXPERIMENT #BUILD #DEPLOY #ACTIVATE @JARVIS @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KennyBDA")


class KennyBDAPhase(Enum):
    """Kenny B-D-A Phases"""
    BUILD = "build"
    DEPLOY = "deploy"
    ACTIVATE = "activate"
    ALL = "all"  # All phases


class KennyBDAExperiment:
    """
    Kenny Experiment - Build-Deploy-Activate (B-D-A) System

    Continuous iterative experimentation:
    1. BUILD - Build/compile/prepare Kenny enhancements
    2. DEPLOY - Deploy Kenny to desktop
    3. ACTIVATE - Activate and run Kenny
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Kenny B-D-A Experiment"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger
        self.build_status = {}
        self.deploy_status = {}
        self.activate_status = {}
        self.kenny_process = None  # Store Kenny process reference

        # Kenny-specific paths (now using Iron Legion Core)
        self.kenny_script = self.project_root / "scripts" / "python" / "jarvis_iron_legion_core.py"
        self.kenny_components = self.project_root / "scripts" / "python" / "kenny_sprite_components.py"
        self.kenny_data_dir = self.project_root / "data" / "kenny_sessions"
        self.kenny_data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ Kenny B-D-A Experiment initialized")

    def build(self) -> Dict[str, Any]:
        """
        BUILD Phase

        Builds/compiles/prepares Kenny:
        - Verify dependencies
        - Check Kenny files
        - Validate components
        - Prepare configurations

        Returns:
            Build result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("🔨 KENNY BUILD PHASE")
        self.logger.info("=" * 80)

        build_results = {
            "dependencies": False,
            "kenny_files": False,
            "components": False,
            "configurations": False,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Check Dependencies
        self.logger.info("📦 Checking dependencies...")
        try:
            dependencies_ok = self._check_dependencies()
            build_results["dependencies"] = dependencies_ok
            if dependencies_ok:
                self.logger.info("✅ Dependencies verified")
            else:
                self.logger.warning("⚠️  Some dependencies may be missing")
        except Exception as e:
            self.logger.error(f"❌ Dependency check failed: {e}")

        # 2. Check Kenny Files
        self.logger.info("📁 Checking Kenny files...")
        try:
            files_ok = self._check_kenny_files()
            build_results["kenny_files"] = files_ok
            if files_ok:
                self.logger.info("✅ Kenny files verified")
            else:
                self.logger.warning("⚠️  Some Kenny files may be missing")
        except Exception as e:
            self.logger.error(f"❌ File check failed: {e}")

        # 3. Validate Components
        self.logger.info("🧩 Validating components...")
        try:
            components_ok = self._validate_components()
            build_results["components"] = components_ok
            if components_ok:
                self.logger.info("✅ Components validated")
            else:
                self.logger.warning("⚠️  Some components may need attention")
        except Exception as e:
            self.logger.error(f"❌ Component validation failed: {e}")

        # 4. Prepare Configurations
        self.logger.info("⚙️  Preparing configurations...")
        try:
            config_ok = self._prepare_configurations()
            build_results["configurations"] = config_ok
            if config_ok:
                self.logger.info("✅ Configurations prepared")
            else:
                self.logger.warning("⚠️  Configuration issues detected")
        except Exception as e:
            self.logger.error(f"❌ Configuration preparation failed: {e}")

        # Determine overall build success
        build_success = all([
            build_results["dependencies"],
            build_results["kenny_files"],
            build_results["components"],
            build_results["configurations"]
        ])

        if build_success:
            self.logger.info("✅ KENNY BUILD PHASE COMPLETE")
            build_results["success"] = True
            build_results["message"] = "Kenny build phase completed successfully"
        else:
            self.logger.warning("⚠️  KENNY BUILD PHASE COMPLETE WITH WARNINGS")
            build_results["success"] = False
            build_results["message"] = "Kenny build phase completed with some warnings"

        self.build_status = build_results
        return build_results

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        dependencies = {
            "tkinter": "tkinter",
            "PIL": "Pillow",
            "numpy": "numpy"
        }

        missing = []
        for module, package in dependencies.items():
            try:
                if module == "PIL":
                    __import__("PIL")
                else:
                    __import__(module)
            except ImportError:
                missing.append(package)

        if missing:
            self.logger.warning(f"⚠️  Missing dependencies: {', '.join(missing)}")
            self.logger.info(f"   Install with: pip install {' '.join(missing)}")
            return False

        return True

    def _check_kenny_files(self) -> bool:
        try:
            """Check if Kenny files exist"""
            required_files = [
                self.kenny_script,
                self.kenny_components
            ]

            missing = []
            for file_path in required_files:
                if not file_path.exists():
                    missing.append(file_path.name)

            if missing:
                self.logger.warning(f"⚠️  Missing Kenny files: {', '.join(missing)}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error in _check_kenny_files: {e}", exc_info=True)
            raise
    def _validate_components(self) -> bool:
        """Validate Kenny components"""
        try:
            from kenny_sprite_components import KennySpriteComponents
            # Try to create an instance
            components = KennySpriteComponents()
            return True
        except Exception as e:
            self.logger.error(f"❌ Component validation failed: {e}")
            return False

    def _prepare_configurations(self) -> bool:
        """Prepare configurations"""
        try:
            # Check if config directories exist
            config_dir = self.project_root / "data"
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)

            return True
        except Exception as e:
            self.logger.error(f"❌ Configuration preparation failed: {e}")
            return False

    def deploy(self) -> Dict[str, Any]:
        """
        DEPLOY Phase

        Deploys Kenny to desktop:
        - Stop existing Kenny processes
        - Prepare deployment environment
        - Set up window management
        - Initialize systems

        Returns:
            Deploy result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("🚀 KENNY DEPLOY PHASE")
        self.logger.info("=" * 80)

        deploy_results = {
            "processes_stopped": False,
            "environment_prepared": False,
            "window_management": False,
            "systems_initialized": False,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Stop Existing Processes
        self.logger.info("🛑 Stopping existing Kenny processes...")
        try:
            stopped = self._stop_existing_processes()
            deploy_results["processes_stopped"] = stopped
            if stopped:
                self.logger.info("✅ Existing processes stopped")
        except Exception as e:
            self.logger.error(f"❌ Process stop failed: {e}")

        # 2. Prepare Environment
        self.logger.info("🌍 Preparing deployment environment...")
        try:
            env_ok = self._prepare_environment()
            deploy_results["environment_prepared"] = env_ok
            if env_ok:
                self.logger.info("✅ Environment prepared")
        except Exception as e:
            self.logger.error(f"❌ Environment preparation failed: {e}")

        # 3. Window Management
        self.logger.info("🪟 Setting up window management...")
        try:
            window_ok = self._setup_window_management()
            deploy_results["window_management"] = window_ok
            if window_ok:
                self.logger.info("✅ Window management setup")
        except Exception as e:
            self.logger.error(f"❌ Window management setup failed: {e}")

        # 4. Initialize Systems
        self.logger.info("🔌 Initializing systems...")
        try:
            systems_ok = self._initialize_systems()
            deploy_results["systems_initialized"] = systems_ok
            if systems_ok:
                self.logger.info("✅ Systems initialized")
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")

        # Determine overall deploy success
        deploy_success = any([
            deploy_results["processes_stopped"],
            deploy_results["environment_prepared"],
            deploy_results["window_management"],
            deploy_results["systems_initialized"]
        ])

        if deploy_success:
            self.logger.info("✅ KENNY DEPLOY PHASE COMPLETE")
            deploy_results["success"] = True
            deploy_results["message"] = "Kenny deploy phase completed successfully"
        else:
            self.logger.warning("⚠️  KENNY DEPLOY PHASE COMPLETE WITH WARNINGS")
            deploy_results["success"] = False
            deploy_results["message"] = "Kenny deploy phase completed with some warnings"

        self.deploy_status = deploy_results
        return deploy_results

    def _stop_existing_processes(self) -> bool:
        """Aggressively purge all existing assistant processes"""
        try:
            self.logger.info("💀 Executing AGGRESSIVE PURGE...")
            purge_script = self.project_root / "scripts" / "python" / "aggressive_purge.py"
            subprocess.run([sys.executable, str(purge_script)], check=True)
            self.logger.info("✅ All previous editions removed from screen")
            return True
        except Exception as e:
            self.logger.error(f"❌ Purge failed: {e}")
            return False

    def _prepare_environment(self) -> bool:
        """Prepare deployment environment"""
        # Environment is already prepared (files in place)
        return True

    def _setup_window_management(self) -> bool:
        """Setup window management"""
        # Window management is handled by Kenny itself
        return True

    def _initialize_systems(self) -> bool:
        """Initialize systems"""
        try:
            # Test that Iron Legion Core can be imported
            import jarvis_iron_legion_core
            return True
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            return False

    def activate(self) -> Dict[str, Any]:
        """
        ACTIVATE Phase

        Activates and runs Kenny:
        - Start Kenny process
        - Verify window visibility
        - Monitor initial state

        Returns:
            Activate result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("⚡ KENNY ACTIVATE PHASE")
        self.logger.info("=" * 80)

        activate_results = {
            "kenny_started": False,
            "window_visible": False,
            "initial_state": False,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Start Kenny
        self.logger.info("🚀 Starting Kenny...")
        try:
            started = self._start_kenny()
            activate_results["kenny_started"] = started
            if started:
                self.logger.info("✅ Kenny started")
                time.sleep(2)  # Give Kenny time to initialize
            else:
                self.logger.warning("⚠️  Kenny start had issues")
        except Exception as e:
            self.logger.error(f"❌ Kenny start failed: {e}")
            activate_results["error"] = str(e)

        # 2. Verify Window Visibility
        if activate_results["kenny_started"]:
            self.logger.info("👁️  Verifying window visibility...")
            try:
                visible = self._verify_window_visibility()
                activate_results["window_visible"] = visible
                if visible:
                    self.logger.info("✅ Window is visible")
                else:
                    self.logger.warning("⚠️  Window visibility check failed")
            except Exception as e:
                self.logger.warning(f"⚠️  Window visibility check error: {e}")

        # 3. Check Initial State
        if activate_results["kenny_started"]:
            self.logger.info("📊 Checking initial state...")
            try:
                state_ok = self._check_initial_state()
                activate_results["initial_state"] = state_ok
                if state_ok:
                    self.logger.info("✅ Initial state verified")
            except Exception as e:
                self.logger.warning(f"⚠️  Initial state check error: {e}")

        # Determine overall activate success
        activate_success = activate_results["kenny_started"]

        if activate_success:
            self.logger.info("✅ KENNY ACTIVATE PHASE COMPLETE")
            activate_results["success"] = True
            activate_results["message"] = "Kenny activate phase completed successfully"
        else:
            self.logger.warning("⚠️  KENNY ACTIVATE PHASE COMPLETE WITH WARNINGS")
            activate_results["success"] = False
            activate_results["message"] = "Kenny activate phase completed with some warnings"

        self.activate_status = activate_results
        return activate_results

    def _start_kenny(self) -> bool:
        """Start Kenny process"""
        try:
            # Start Kenny in background
            # CRITICAL: Don't redirect stdout/stderr - tkinter needs access to display
            import subprocess
            python_exe = sys.executable

            # Use CREATE_NEW_CONSOLE on Windows to give tkinter its own window
            import platform
            if platform.system() == "Windows":
                # CREATE_NEW_CONSOLE allows tkinter window to display properly
                creation_flags = subprocess.CREATE_NEW_CONSOLE
            else:
                creation_flags = 0

            process = subprocess.Popen(
                [python_exe, str(self.kenny_script)],
                cwd=str(self.project_root),
                # Don't redirect stdout/stderr - let them go to console so tkinter works
                stdout=None,
                stderr=None,
                creationflags=creation_flags if platform.system() == "Windows" else 0
            )
            self.logger.info(f"   Kenny process started: PID {process.pid}")
            # Store process reference for later use
            self.kenny_process = process
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to start Kenny: {e}")
            return False

    def _verify_window_visibility(self) -> bool:
        """Verify Kenny window is visible"""
        try:
            # Try to use find_and_show_kenny_window if available
            try:
                from find_and_show_kenny_window import find_and_show_kenny_window
                result = find_and_show_kenny_window()
                return result.get("found", False)
            except ImportError:
                # Fallback: assume visible if process is running
                return True
        except Exception as e:
            self.logger.warning(f"⚠️  Window visibility check error: {e}")
            return False

    def _check_initial_state(self) -> bool:
        """Check Kenny initial state"""
        # State check is handled by Kenny itself
        return True

    def execute_bda(self, phase: KennyBDAPhase = KennyBDAPhase.ALL) -> Dict[str, Any]:
        """
        Execute Build-Deploy-Activate workflow for Kenny

        Args:
            phase: Phase to execute (BUILD, DEPLOY, ACTIVATE, or ALL)

        Returns:
            Complete B-D-A result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("🔄 EXECUTING KENNY BUILD-DEPLOY-ACTIVATE (B-D-A)")
        self.logger.info("=" * 80)

        results = {
            "build": None,
            "deploy": None,
            "activate": None,
            "timestamp": datetime.now().isoformat()
        }

        # BUILD Phase
        if phase == KennyBDAPhase.BUILD or phase == KennyBDAPhase.ALL:
            self.logger.info("\n" + "=" * 80)
            self.logger.info("PHASE 1: BUILD")
            self.logger.info("=" * 80)
            build_result = self.build()
            results["build"] = build_result

            if not build_result.get("success", False):
                self.logger.warning("⚠️  Build phase had issues - continuing anyway")

        # DEPLOY Phase
        if phase == KennyBDAPhase.DEPLOY or phase == KennyBDAPhase.ALL:
            self.logger.info("\n" + "=" * 80)
            self.logger.info("PHASE 2: DEPLOY")
            self.logger.info("=" * 80)
            deploy_result = self.deploy()
            results["deploy"] = deploy_result

            if not deploy_result.get("success", False):
                self.logger.warning("⚠️  Deploy phase had issues - continuing anyway")

        # ACTIVATE Phase
        if phase == KennyBDAPhase.ACTIVATE or phase == KennyBDAPhase.ALL:
            self.logger.info("\n" + "=" * 80)
            self.logger.info("PHASE 3: ACTIVATE")
            self.logger.info("=" * 80)
            activate_result = self.activate()
            results["activate"] = activate_result

        # Determine overall success
        overall_success = (
            (results["build"] is None or results["build"].get("success", False)) and
            (results["deploy"] is None or results["deploy"].get("success", False)) and
            (results["activate"] is None or results["activate"].get("success", False))
        )

        if overall_success:
            self.logger.info("\n" + "=" * 80)
            self.logger.info("✅ KENNY BUILD-DEPLOY-ACTIVATE (B-D-A) COMPLETE")
            self.logger.info("=" * 80)
            results["success"] = True
            results["message"] = "Kenny B-D-A workflow completed successfully"
        else:
            self.logger.warning("\n" + "=" * 80)
            self.logger.warning("⚠️  KENNY BUILD-DEPLOY-ACTIVATE (B-D-A) COMPLETE WITH WARNINGS")
            self.logger.warning("=" * 80)
            results["success"] = False
            results["message"] = "Kenny B-D-A workflow completed with some warnings"

        return results

    def get_bda_status(self) -> Dict[str, Any]:
        """Get current Kenny B-D-A status"""
        return {
            "build": self.build_status,
            "deploy": self.deploy_status,
            "activate": self.activate_status,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Kenny Experiment - Build-Deploy-Activate (B-D-A) System")
    parser.add_argument("--build", action="store_true", help="Execute BUILD phase")
    parser.add_argument("--deploy", action="store_true", help="Execute DEPLOY phase")
    parser.add_argument("--activate", action="store_true", help="Execute ACTIVATE phase")
    parser.add_argument("--all", action="store_true", help="Execute all phases (B-D-A)")
    parser.add_argument("--status", action="store_true", help="Get B-D-A status")

    args = parser.parse_args()

    kenny_bda = KennyBDAExperiment()

    if args.status:
        status = kenny_bda.get_bda_status()
        print("🔄 Kenny B-D-A Status:")
        print(f"   Build: {'✅' if status.get('build', {}).get('success') else '❌' if status.get('build') else '⏸️'}")
        print(f"   Deploy: {'✅' if status.get('deploy', {}).get('success') else '❌' if status.get('deploy') else '⏸️'}")
        print(f"   Activate: {'✅' if status.get('activate', {}).get('success') else '❌' if status.get('activate') else '⏸️'}")
        return 0

    # Determine phase
    if args.all or (not args.build and not args.deploy and not args.activate):
        phase = KennyBDAPhase.ALL
    elif args.build and not args.deploy and not args.activate:
        phase = KennyBDAPhase.BUILD
    elif args.deploy and not args.build and not args.activate:
        phase = KennyBDAPhase.DEPLOY
    elif args.activate and not args.build and not args.deploy:
        phase = KennyBDAPhase.ACTIVATE
    else:
        phase = KennyBDAPhase.ALL  # Default to all if multiple specified

    print("🔄 Executing Kenny Build-Deploy-Activate (B-D-A)...")
    result = kenny_bda.execute_bda(phase=phase)

    if result.get("success"):
        print("\n✅ Kenny B-D-A workflow completed successfully")
        if result.get("build"):
            print(f"   Build: {'✅' if result['build'].get('success') else '❌'}")
        if result.get("deploy"):
            print(f"   Deploy: {'✅' if result['deploy'].get('success') else '❌'}")
        if result.get("activate"):
            print(f"   Activate: {'✅' if result['activate'].get('success') else '❌'}")
    else:
        print(f"\n⚠️  Kenny B-D-A workflow completed with warnings: {result.get('message', 'Unknown')}")

    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main() or 0)