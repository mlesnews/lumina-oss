#!/usr/bin/env python3
"""
VA Build-Deploy-Activate (B-D-A) Workflow

Applies lessons from Kenny experiment to ensure all VAs are properly:
- BUILD: Verify dependencies, files, components, configurations
- DEPLOY: Proper window management, process handling
- ACTIVATE: Start monitoring, ensure visibility

Tags: #BDA #VA #BUILD #DEPLOY #ACTIVATE #KENNY_LESSONS @JARVIS @LUMINA
"""

import sys
import subprocess
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VABDA")


class BDAPhase(Enum):
    """B-D-A Phases"""
    BUILD = "build"
    DEPLOY = "deploy"
    ACTIVATE = "activate"
    ALL = "all"


class VABDAWorkflow:
    """
    VA Build-Deploy-Activate Workflow

    Applies Kenny B-D-A lessons to all VAs:
    1. BUILD - Verify all components are ready
    2. DEPLOY - Deploy VAs to desktop
    3. ACTIVATE - Activate and ensure visibility
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VA B-D-A Workflow"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger

        # VA scripts to manage
        self.va_scripts = {
            "jarvis_narrator": {
                "script": "jarvis_narrator_avatar.py",
                "description": "JARVIS Narrator Avatar - monitors notifications",
                "required": True
            },
            "kenny_avatar": {
                "script": "kenny_imva_enhanced.py",
                "description": "Kenny IMVA Enhanced Avatar",
                "required": False
            },
            "va_renderer": {
                "script": "render_va_desktop_widgets.py",
                "description": "VA Desktop Widget Renderer",
                "required": True
            },
            "notification_monitor": {
                "script": "cursor_notification_handler.py",
                "description": "Notification Monitor for JARVIS",
                "required": True,
                "args": ["--monitor"]
            }
        }

        self.build_status = {}
        self.deploy_status = {}
        self.activate_status = {}
        self.processes = {}

        self.logger.info("✅ VA B-D-A Workflow initialized")

    def build(self) -> Dict[str, Any]:
        """
        BUILD Phase - Verify all components are ready

        - Check dependencies
        - Verify VA files exist
        - Validate components
        - Prepare configurations
        """
        self.logger.info("=" * 80)
        self.logger.info("🔨 VA BUILD PHASE")
        self.logger.info("=" * 80)

        build_results = {
            "dependencies": False,
            "va_files": False,
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

        # 2. Check VA Files
        self.logger.info("📁 Checking VA files...")
        try:
            files_ok = self._check_va_files()
            build_results["va_files"] = files_ok
            if files_ok:
                self.logger.info("✅ VA files verified")
            else:
                self.logger.warning("⚠️  Some VA files may be missing")
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
            build_results["va_files"],
            build_results["components"],
            build_results["configurations"]
        ])

        if build_success:
            self.logger.info("✅ VA BUILD PHASE COMPLETE")
            build_results["success"] = True
        else:
            self.logger.warning("⚠️  VA BUILD PHASE COMPLETE WITH WARNINGS")
            build_results["success"] = False

        self.build_status = build_results
        return build_results

    def deploy(self) -> Dict[str, Any]:
        """
        DEPLOY Phase - Deploy VAs to desktop

        - Kill existing processes (like "Killing Kenny")
        - Start VA processes
        - Ensure windows are created
        """
        self.logger.info("=" * 80)
        self.logger.info("🚀 VA DEPLOY PHASE")
        self.logger.info("=" * 80)

        deploy_results = {
            "processes_killed": False,
            "processes_started": {},
            "windows_created": False,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Kill existing processes (Kenny lesson: kill before deploy)
        self.logger.info("🔪 Killing existing VA processes...")
        try:
            killed = self._kill_existing_processes()
            deploy_results["processes_killed"] = True
            deploy_results["killed_count"] = killed
            self.logger.info(f"✅ Killed {killed} existing processes")
            time.sleep(1)  # Give processes time to die
        except Exception as e:
            self.logger.error(f"❌ Process kill failed: {e}")

        # 2. Start VA processes
        self.logger.info("🚀 Starting VA processes...")
        for va_name, va_config in self.va_scripts.items():
            if not va_config.get("required", False):
                continue  # Skip optional VAs for now

            try:
                script_path = script_dir / va_config["script"]
                if not script_path.exists():
                    self.logger.warning(f"⚠️  {va_name}: Script not found ({va_config['script']})")
                    deploy_results["processes_started"][va_name] = False
                    continue

                # Build command
                cmd = [sys.executable, str(script_path)]
                if "args" in va_config:
                    cmd.extend(va_config["args"])

                # Start process (NO CREATE_NO_WINDOW - windows need to show!)
                process = subprocess.Popen(
                    cmd,
                    cwd=str(project_root)
                    # No CREATE_NO_WINDOW - VAs need to show their windows
                )

                deploy_results["processes_started"][va_name] = {
                    "pid": process.pid,
                    "started": True
                }
                self.processes[va_name] = process
                self.logger.info(f"✅ {va_name}: Started (PID: {process.pid})")
                time.sleep(0.5)  # Stagger starts

            except Exception as e:
                self.logger.error(f"❌ {va_name}: Failed to start - {e}")
                deploy_results["processes_started"][va_name] = False

        # 3. Verify windows created
        self.logger.info("🪟 Verifying windows created...")
        try:
            windows_ok = self._verify_windows()
            deploy_results["windows_created"] = windows_ok
            if windows_ok:
                self.logger.info("✅ Windows verified")
            else:
                self.logger.warning("⚠️  Some windows may not be visible")
        except Exception as e:
            self.logger.error(f"❌ Window verification failed: {e}")

        deploy_success = (
            deploy_results["processes_killed"] and
            any(v.get("started", False) if isinstance(v, dict) else v 
                for v in deploy_results["processes_started"].values())
        )

        if deploy_success:
            self.logger.info("✅ VA DEPLOY PHASE COMPLETE")
            deploy_results["success"] = True
        else:
            self.logger.warning("⚠️  VA DEPLOY PHASE COMPLETE WITH WARNINGS")
            deploy_results["success"] = False

        self.deploy_status = deploy_results
        return deploy_results

    def activate(self) -> Dict[str, Any]:
        """
        ACTIVATE Phase - Activate and ensure visibility

        - Verify processes are running
        - Check widget visibility
        - Start monitoring
        """
        self.logger.info("=" * 80)
        self.logger.info("⚡ VA ACTIVATE PHASE")
        self.logger.info("=" * 80)

        activate_results = {
            "processes_running": {},
            "widgets_visible": False,
            "monitoring_active": False,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Verify processes are running
        self.logger.info("🔍 Verifying processes are running...")
        for va_name, process in self.processes.items():
            try:
                if process and process.poll() is None:
                    activate_results["processes_running"][va_name] = True
                    self.logger.info(f"✅ {va_name}: Running (PID: {process.pid})")
                else:
                    activate_results["processes_running"][va_name] = False
                    self.logger.warning(f"⚠️  {va_name}: Process not running")
            except Exception as e:
                self.logger.error(f"❌ {va_name}: Check failed - {e}")
                activate_results["processes_running"][va_name] = False

        # 2. Check widget visibility
        self.logger.info("👁️  Checking widget visibility...")
        try:
            widgets_ok = self._check_widget_visibility()
            activate_results["widgets_visible"] = widgets_ok
            if widgets_ok:
                self.logger.info("✅ Widgets visible")
            else:
                self.logger.warning("⚠️  Some widgets may not be visible")
        except Exception as e:
            self.logger.error(f"❌ Widget check failed: {e}")

        # 3. Start monitoring
        self.logger.info("📡 Starting monitoring...")
        try:
            monitoring_ok = self._start_monitoring()
            activate_results["monitoring_active"] = monitoring_ok
            if monitoring_ok:
                self.logger.info("✅ Monitoring active")
            else:
                self.logger.warning("⚠️  Monitoring may not be active")
        except Exception as e:
            self.logger.error(f"❌ Monitoring start failed: {e}")

        activate_success = (
            any(activate_results["processes_running"].values()) and
            activate_results["widgets_visible"]
        )

        if activate_success:
            self.logger.info("✅ VA ACTIVATE PHASE COMPLETE")
            activate_results["success"] = True
        else:
            self.logger.warning("⚠️  VA ACTIVATE PHASE COMPLETE WITH WARNINGS")
            activate_results["success"] = False

        self.activate_status = activate_results
        return activate_results

    def execute_bda(self) -> Dict[str, Any]:
        """Execute full B-D-A workflow"""
        self.logger.info("=" * 80)
        self.logger.info("🌟 VA B-D-A WORKFLOW - APPLYING KENNY LESSONS")
        self.logger.info("=" * 80)
        self.logger.info("")

        # BUILD
        build_result = self.build()
        if not build_result.get("success"):
            self.logger.warning("⚠️  Build phase had warnings, but continuing...")

        self.logger.info("")

        # DEPLOY
        deploy_result = self.deploy()
        if not deploy_result.get("success"):
            self.logger.error("❌ Deploy phase failed!")
            return {"success": False, "build": build_result, "deploy": deploy_result}

        self.logger.info("")
        time.sleep(2)  # Give processes time to start

        # ACTIVATE
        activate_result = self.activate()

        overall_success = (
            build_result.get("success", False) and
            deploy_result.get("success", False) and
            activate_result.get("success", False)
        )

        self.logger.info("")
        self.logger.info("=" * 80)
        if overall_success:
            self.logger.info("✅ VA B-D-A WORKFLOW COMPLETE")
        else:
            self.logger.warning("⚠️  VA B-D-A WORKFLOW COMPLETE WITH WARNINGS")
        self.logger.info("=" * 80)

        return {
            "success": overall_success,
            "build": build_result,
            "deploy": deploy_result,
            "activate": activate_result
        }

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        dependencies = {
            "tkinter": "tkinter",
            "PIL": "Pillow",
            "cv2": "opencv-python",
            "numpy": "numpy"
        }

        all_ok = True
        for dep_name, module_name in dependencies.items():
            try:
                __import__(module_name)
                self.logger.debug(f"  ✅ {dep_name}")
            except ImportError:
                self.logger.warning(f"  ⚠️  {dep_name} not available")
                all_ok = False

        return all_ok

    def _check_va_files(self) -> bool:
        try:
            """Check if all VA script files exist"""
            all_ok = True
            for va_name, va_config in self.va_scripts.items():
                script_path = script_dir / va_config["script"]
                if script_path.exists():
                    self.logger.debug(f"  ✅ {va_name}: {va_config['script']}")
                else:
                    if va_config.get("required", False):
                        self.logger.warning(f"  ⚠️  {va_name}: Missing required script {va_config['script']}")
                        all_ok = False
                    else:
                        self.logger.debug(f"  ℹ️  {va_name}: Optional script not found")

            return all_ok

        except Exception as e:
            self.logger.error(f"Error in _check_va_files: {e}", exc_info=True)
            raise
    def _validate_components(self) -> bool:
        """Validate VA components"""
        try:
            from character_avatar_registry import CharacterAvatarRegistry
            from va_visibility_system import VAVisibilitySystem

            registry = CharacterAvatarRegistry()
            visibility = VAVisibilitySystem()

            self.logger.debug(f"  ✅ Registry: {len(registry.get_all_characters())} characters")
            self.logger.debug(f"  ✅ Visibility: {len(visibility.vas)} VAs to display")

            return True
        except Exception as e:
            self.logger.error(f"  ❌ Component validation failed: {e}")
            return False

    def _prepare_configurations(self) -> bool:
        """Prepare configurations"""
        # Ensure data directories exist
        data_dirs = [
            project_root / "data" / "va_sessions",
            project_root / "data" / "va_widgets"
        ]

        for dir_path in data_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

        return True

    def _kill_existing_processes(self) -> int:
        """Kill existing VA processes (Kenny lesson)"""
        killed = 0
        for va_name, va_config in self.va_scripts.items():
            script_path = script_dir / va_config["script"]
            if not script_path.exists():
                continue

            # Find and kill processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any(str(script_path) in str(arg) for arg in cmdline):
                            try:
                                proc.terminate()
                                proc.wait(timeout=2)
                                killed += 1
                                self.logger.debug(f"  ✅ Killed {va_name} (PID: {proc.info['pid']})")
                            except psutil.TimeoutExpired:
                                proc.kill()
                                killed += 1
                                self.logger.debug(f"  ✅ Force-killed {va_name} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        return killed

    def _verify_windows(self) -> bool:
        """Verify windows are created (basic check)"""
        # Give processes time to create windows
        time.sleep(2)

        # Check if processes are still running (indicates windows likely created)
        running = 0
        for va_name, process in self.processes.items():
            if process and process.poll() is None:
                running += 1

        return running > 0

    def _check_widget_visibility(self) -> bool:
        """Check if widgets are visible"""
        try:
            from va_visibility_system import VAVisibilitySystem

            visibility = VAVisibilitySystem()
            widgets = visibility.viz.widgets

            visible_count = sum(1 for w in widgets.values() if w.visible)

            self.logger.info(f"  📊 Widgets: {visible_count}/{len(widgets)} visible")

            return visible_count > 0
        except Exception as e:
            self.logger.error(f"  ❌ Widget check failed: {e}")
            return False

    def _start_monitoring(self) -> bool:
        """Start monitoring systems"""
        # Monitoring is handled by notification monitor process
        # Just verify it's running
        if "notification_monitor" in self.processes:
            process = self.processes["notification_monitor"]
            if process and process.poll() is None:
                return True

        return False


def main():
    """Main B-D-A workflow execution"""
    workflow = VABDAWorkflow()
    result = workflow.execute_bda()

    if result.get("success"):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()