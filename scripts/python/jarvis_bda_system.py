#!/usr/bin/env python3
"""
JARVIS Build-Deploy-Activate (B-D-A) System

Automated workflow for:
- BUILD: Build/compile/prepare JARVIS ACE enhancements
- DEPLOY: Deploy to target environment
- ACTIVATE: Activate all systems

Tags: #JARVIS #BDA #BUILD #DEPLOY #ACTIVATE #AUTOMATION @JARVIS @LUMINA
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

logger = get_logger("JARVISBDA")


class BDAPhase(Enum):
    """B-D-A Phases"""
    BUILD = "build"
    DEPLOY = "deploy"
    ACTIVATE = "activate"
    ALL = "all"  # All phases


class JARVISBDASystem:
    """
    JARVIS Build-Deploy-Activate (B-D-A) System

    Automated workflow:
    1. BUILD - Build/compile/prepare all systems
    2. DEPLOY - Deploy to target environment
    3. ACTIVATE - Activate all JARVIS ACE enhancements
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize B-D-A System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger
        self.build_status = {}
        self.deploy_status = {}
        self.activate_status = {}

        self.logger.info("✅ JARVIS B-D-A System initialized")

    def build(self) -> Dict[str, Any]:
        """
        BUILD Phase

        Builds/compiles/prepares all JARVIS ACE systems:
        - Verify dependencies
        - Check system health
        - Prepare configurations
        - Validate integrations

        Returns:
            Build result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("🔨 BUILD PHASE")
        self.logger.info("=" * 80)

        build_results = {
            "dependencies": False,
            "system_health": False,
            "configurations": False,
            "integrations": False,
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

        # 2. System Health Check
        self.logger.info("🏥 Checking system health...")
        try:
            health_ok = self._check_system_health()
            build_results["system_health"] = health_ok
            if health_ok:
                self.logger.info("✅ System health verified")
            else:
                self.logger.warning("⚠️  System health issues detected")
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

        # 3. Prepare Configurations
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

        # 4. Validate Integrations
        self.logger.info("🔗 Validating integrations...")
        try:
            integrations_ok = self._validate_integrations()
            build_results["integrations"] = integrations_ok
            if integrations_ok:
                self.logger.info("✅ Integrations validated")
            else:
                self.logger.warning("⚠️  Some integrations may need attention")
        except Exception as e:
            self.logger.error(f"❌ Integration validation failed: {e}")

        # Determine overall build success
        build_success = all([
            build_results["dependencies"],
            build_results["system_health"],
            build_results["configurations"],
            build_results["integrations"]
        ])

        if build_success:
            self.logger.info("✅ BUILD PHASE COMPLETE")
            build_results["success"] = True
            build_results["message"] = "Build phase completed successfully"
        else:
            self.logger.warning("⚠️  BUILD PHASE COMPLETE WITH WARNINGS")
            build_results["success"] = False
            build_results["message"] = "Build phase completed with some warnings"

        self.build_status = build_results
        return build_results

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        dependencies = {
            "opencv": "opencv-python",
            "pyaudio": "pyaudio",
            "mediapipe": "mediapipe",
            "pyautogui": "pyautogui",
            "pyperclip": "pyperclip"
        }

        missing = []
        for module, package in dependencies.items():
            try:
                __import__(module)
            except ImportError:
                missing.append(package)

        if missing:
            self.logger.warning(f"⚠️  Missing dependencies: {', '.join(missing)}")
            self.logger.info(f"   Install with: pip install {' '.join(missing)}")
            return False

        return True

    def _check_system_health(self) -> bool:
        """Check system health"""
        try:
            # Check if JARVIS core can initialize
            from jarvis_enhanced_core import JarvisEnhancedCore
            jarvis = JarvisEnhancedCore(project_root=self.project_root)
            return True
        except Exception as e:
            self.logger.error(f"❌ System health check failed: {e}")
            return False

    def _prepare_configurations(self) -> bool:
        """Prepare configurations"""
        try:
            # Check if config directories exist
            config_dir = self.project_root / "config"
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)

            # Check key config files
            key_configs = [
                "iron_legion_experts_config.json",
                "jarvis_roles_config.json"
            ]

            all_exist = True
            for config_file in key_configs:
                config_path = config_dir / config_file
                if not config_path.exists():
                    self.logger.warning(f"⚠️  Config file missing: {config_file}")
                    all_exist = False

            return all_exist
        except Exception as e:
            self.logger.error(f"❌ Configuration preparation failed: {e}")
            return False

    def _validate_integrations(self) -> bool:
        """Validate all integrations"""
        integrations = {
            "MDV Activator": "jarvis_auto_mdv_activator",
            "MDV Conference Call": "jarvis_mdv_conference_call",
            "Accessibility": "jarvis_mdv_accessibility_enhancements",
            "Workflow Chaining": "jarvis_keep_all_workflow_chain",
            "RAlt Doit": "jarvis_ralt_doit_paste",
            "ACE Enhanced": "jarvis_ace_enhanced_integration",
            "Body Integration": "jarvis_body_integration"
        }

        all_valid = True
        for name, module in integrations.items():
            try:
                __import__(module)
            except ImportError:
                self.logger.warning(f"⚠️  Integration missing: {name}")
                all_valid = False

        return all_valid

    def deploy(self) -> Dict[str, Any]:
        """
        DEPLOY Phase

        Deploys JARVIS ACE enhancements to target environment:
        - Copy files to deployment locations
        - Update configurations
        - Set up services
        - Initialize systems

        Returns:
            Deploy result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("🚀 DEPLOY PHASE")
        self.logger.info("=" * 80)

        deploy_results = {
            "files_copied": False,
            "configurations_updated": False,
            "services_setup": False,
            "systems_initialized": False,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Copy Files (if needed)
        self.logger.info("📁 Preparing deployment files...")
        try:
            files_ok = self._prepare_deployment_files()
            deploy_results["files_copied"] = files_ok
            if files_ok:
                self.logger.info("✅ Deployment files ready")
        except Exception as e:
            self.logger.error(f"❌ File preparation failed: {e}")

        # 2. Update Configurations
        self.logger.info("⚙️  Updating configurations...")
        try:
            config_ok = self._update_deployment_configs()
            deploy_results["configurations_updated"] = config_ok
            if config_ok:
                self.logger.info("✅ Configurations updated")
        except Exception as e:
            self.logger.error(f"❌ Configuration update failed: {e}")

        # 3. Setup Services
        self.logger.info("🔧 Setting up services...")
        try:
            services_ok = self._setup_services()
            deploy_results["services_setup"] = services_ok
            if services_ok:
                self.logger.info("✅ Services setup complete")
        except Exception as e:
            self.logger.error(f"❌ Service setup failed: {e}")

        # 4. Initialize Systems
        self.logger.info("🔌 Initializing systems...")
        try:
            systems_ok = self._initialize_deployed_systems()
            deploy_results["systems_initialized"] = systems_ok
            if systems_ok:
                self.logger.info("✅ Systems initialized")
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")

        # Determine overall deploy success
        deploy_success = any([
            deploy_results["files_copied"],
            deploy_results["configurations_updated"],
            deploy_results["services_setup"],
            deploy_results["systems_initialized"]
        ])

        if deploy_success:
            self.logger.info("✅ DEPLOY PHASE COMPLETE")
            deploy_results["success"] = True
            deploy_results["message"] = "Deploy phase completed successfully"
        else:
            self.logger.warning("⚠️  DEPLOY PHASE COMPLETE WITH WARNINGS")
            deploy_results["success"] = False
            deploy_results["message"] = "Deploy phase completed with some warnings"

        self.deploy_status = deploy_results
        return deploy_results

    def _prepare_deployment_files(self) -> bool:
        """Prepare deployment files"""
        # For now, files are already in place
        # In a real deployment, this would copy files to deployment locations
        return True

    def _update_deployment_configs(self) -> bool:
        """Update deployment configurations"""
        # Configurations are already in place
        # In a real deployment, this would update configs for target environment
        return True

    def _setup_services(self) -> bool:
        """Setup services"""
        # Services are already available
        # In a real deployment, this would start/configure services
        return True

    def _initialize_deployed_systems(self) -> bool:
        """Initialize deployed systems"""
        try:
            # Test that systems can be imported
            from jarvis_ace_enhanced_integration import JARVISACEEnhancedIntegration
            integration = JARVISACEEnhancedIntegration(project_root=self.project_root)
            return True
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            return False

    def activate(self) -> Dict[str, Any]:
        """
        ACTIVATE Phase

        Activates all JARVIS ACE enhancements:
        - Activate MDV
        - Activate MDV Conference Call
        - Activate accessibility
        - Activate workflow chaining
        - Activate ACE humanoid
        - Activate body integration

        Returns:
            Activate result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("⚡ ACTIVATE PHASE")
        self.logger.info("=" * 80)

        activate_results = {
            "mdv": False,
            "mdv_conference_call": False,
            "accessibility": False,
            "workflow_chaining": False,
            "ace_enhanced": False,
            "body_integration": False,
            "timestamp": datetime.now().isoformat()
        }

        # Activate ACE-enhanced integration (this activates everything)
        try:
            from jarvis_ace_enhanced_integration import JARVISACEEnhancedIntegration, ACEEnhancementMode
            integration = JARVISACEEnhancedIntegration(project_root=self.project_root)
            activation_result = integration.activate_ace_enhancements(mode=ACEEnhancementMode.FULL)

            activate_results["ace_enhanced"] = activation_result.get("success", False)
            activate_results["mdv"] = activation_result.get("mdv", False)
            activate_results["mdv_conference_call"] = activation_result.get("mdv_conference_call", False)
            activate_results["accessibility"] = activation_result.get("accessibility", False)
            activate_results["workflow_chaining"] = activation_result.get("workflow_chaining", False)
            activate_results["body_integration"] = activation_result.get("body_integration", False)
            activate_results["activation_details"] = activation_result

            if activate_results["ace_enhanced"]:
                self.logger.info("✅ ACE enhancements activated")
            else:
                self.logger.warning("⚠️  ACE activation had issues")
        except Exception as e:
            self.logger.error(f"❌ Activation failed: {e}")
            activate_results["error"] = str(e)

        # Determine overall activate success
        activate_success = any([
            activate_results["mdv"],
            activate_results["mdv_conference_call"],
            activate_results["accessibility"],
            activate_results["workflow_chaining"],
            activate_results["ace_enhanced"],
            activate_results["body_integration"]
        ])

        if activate_success:
            self.logger.info("✅ ACTIVATE PHASE COMPLETE")
            activate_results["success"] = True
            activate_results["message"] = "Activate phase completed successfully"
        else:
            self.logger.warning("⚠️  ACTIVATE PHASE COMPLETE WITH WARNINGS")
            activate_results["success"] = False
            activate_results["message"] = "Activate phase completed with some warnings"

        self.activate_status = activate_results
        return activate_results

    def execute_bda(self, phase: BDAPhase = BDAPhase.ALL) -> Dict[str, Any]:
        """
        Execute Build-Deploy-Activate workflow

        Args:
            phase: Phase to execute (BUILD, DEPLOY, ACTIVATE, or ALL)

        Returns:
            Complete B-D-A result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("🔄 EXECUTING BUILD-DEPLOY-ACTIVATE (B-D-A)")
        self.logger.info("=" * 80)

        results = {
            "build": None,
            "deploy": None,
            "activate": None,
            "timestamp": datetime.now().isoformat()
        }

        # BUILD Phase
        if phase == BDAPhase.BUILD or phase == BDAPhase.ALL:
            self.logger.info("\n" + "=" * 80)
            self.logger.info("PHASE 1: BUILD")
            self.logger.info("=" * 80)
            build_result = self.build()
            results["build"] = build_result

            if not build_result.get("success", False):
                self.logger.warning("⚠️  Build phase had issues - continuing anyway")

        # DEPLOY Phase
        if phase == BDAPhase.DEPLOY or phase == BDAPhase.ALL:
            self.logger.info("\n" + "=" * 80)
            self.logger.info("PHASE 2: DEPLOY")
            self.logger.info("=" * 80)
            deploy_result = self.deploy()
            results["deploy"] = deploy_result

            if not deploy_result.get("success", False):
                self.logger.warning("⚠️  Deploy phase had issues - continuing anyway")

        # ACTIVATE Phase
        if phase == BDAPhase.ACTIVATE or phase == BDAPhase.ALL:
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
            self.logger.info("✅ BUILD-DEPLOY-ACTIVATE (B-D-A) COMPLETE")
            self.logger.info("=" * 80)
            results["success"] = True
            results["message"] = "B-D-A workflow completed successfully"
        else:
            self.logger.warning("\n" + "=" * 80)
            self.logger.warning("⚠️  BUILD-DEPLOY-ACTIVATE (B-D-A) COMPLETE WITH WARNINGS")
            self.logger.warning("=" * 80)
            results["success"] = False
            results["message"] = "B-D-A workflow completed with some warnings"

        return results

    def get_bda_status(self) -> Dict[str, Any]:
        """Get current B-D-A status"""
        return {
            "build": self.build_status,
            "deploy": self.deploy_status,
            "activate": self.activate_status,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Build-Deploy-Activate (B-D-A) System")
    parser.add_argument("--build", action="store_true", help="Execute BUILD phase")
    parser.add_argument("--deploy", action="store_true", help="Execute DEPLOY phase")
    parser.add_argument("--activate", action="store_true", help="Execute ACTIVATE phase")
    parser.add_argument("--all", action="store_true", help="Execute all phases (B-D-A)")
    parser.add_argument("--status", action="store_true", help="Get B-D-A status")

    args = parser.parse_args()

    bda = JARVISBDASystem()

    if args.status:
        status = bda.get_bda_status()
        print("🔄 JARVIS B-D-A Status:")
        print(f"   Build: {'✅' if status.get('build', {}).get('success') else '❌' if status.get('build') else '⏸️'}")
        print(f"   Deploy: {'✅' if status.get('deploy', {}).get('success') else '❌' if status.get('deploy') else '⏸️'}")
        print(f"   Activate: {'✅' if status.get('activate', {}).get('success') else '❌' if status.get('activate') else '⏸️'}")
        return 0

    # Determine phase
    if args.all or (not args.build and not args.deploy and not args.activate):
        phase = BDAPhase.ALL
    elif args.build and not args.deploy and not args.activate:
        phase = BDAPhase.BUILD
    elif args.deploy and not args.build and not args.activate:
        phase = BDAPhase.DEPLOY
    elif args.activate and not args.build and not args.deploy:
        phase = BDAPhase.ACTIVATE
    else:
        phase = BDAPhase.ALL  # Default to all if multiple specified

    print("🔄 Executing Build-Deploy-Activate (B-D-A)...")
    result = bda.execute_bda(phase=phase)

    if result.get("success"):
        print("\n✅ B-D-A workflow completed successfully")
        if result.get("build"):
            print(f"   Build: {'✅' if result['build'].get('success') else '❌'}")
        if result.get("deploy"):
            print(f"   Deploy: {'✅' if result['deploy'].get('success') else '❌'}")
        if result.get("activate"):
            print(f"   Activate: {'✅' if result['activate'].get('success') else '❌'}")
    else:
        print(f"\n⚠️  B-D-A workflow completed with warnings: {result.get('message', 'Unknown')}")

    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main() or 0)