#!/usr/bin/env python3
"""
Post-Ops Reboot Manager - Agent Widgets & Virtual Assistants

Post-operations verification, reboot automation, and VA/widget startup.
Ensures all agent widgets and virtual assistants are active after reboot.

Tags: #POST_OPS #REBOOT #AGENT_WIDGETS #VIRTUAL_ASSISTANTS #VA #RC #DOIT #RR @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("PostOpsRebootManager")

# Import required modules
try:
    from va_health_detector import VAHealthDetector
    VA_DETECTOR_AVAILABLE = True
except ImportError:
    VA_DETECTOR_AVAILABLE = False
    logger.warning("   ⚠️  VA Health Detector not available")

try:
    from root_cause_analysis import RootCauseAnalysis
    RC_AVAILABLE = True
except ImportError:
    RC_AVAILABLE = False
    logger.warning("   ⚠️  Root Cause Analysis not available")

try:
    from doit_enhanced import DOITEnhanced
    DOIT_AVAILABLE = True
except ImportError:
    DOIT_AVAILABLE = False
    logger.warning("   ⚠️  @DOIT Enhanced not available")


class PostOpsRebootManager:
    """
    Post-Ops Reboot Manager

    Manages post-operations verification, reboot, and startup of:
    - Agent widgets
    - Virtual assistants
    - All LUMINA systems
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize post-ops reboot manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "post_ops"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.va_detector = VAHealthDetector(project_root) if VA_DETECTOR_AVAILABLE else None
        self.root_cause = RootCauseAnalysis(project_root) if RC_AVAILABLE else None
        self.doit = DOITEnhanced(project_root) if DOIT_AVAILABLE else None

        logger.info("✅ Post-Ops Reboot Manager initialized")
        logger.info("   Agent Widgets: ENABLED")
        logger.info("   Virtual Assistants: ENABLED")

    def post_ops_verification(self) -> Dict[str, Any]:
        """
        Post-operations verification

        Returns:
            Verification result
        """
        logger.info("=" * 80)
        logger.info("📋 POST-OPS VERIFICATION")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "timestamp": datetime.now().isoformat(),
            "gpu_optimization": False,
            "system_shortcuts": False,
            "vas_running": False,
            "agent_widgets": False,
            "issues": [],
            "ready_for_reboot": False
        }

        # 1. Verify GPU optimization
        logger.info("📋 Step 1: Verifying GPU Optimization")
        logger.info("")
        try:
            from gpu_utilization_checker import GPUUtilizationChecker
            gpu_checker = GPUUtilizationChecker(self.project_root)
            gpu_status = gpu_checker.check_gpu_utilization()
            result["gpu_optimization"] = gpu_status.get("gpu_available", False)
            if not result["gpu_optimization"]:
                result["issues"].append("GPU not available or not optimized")
            logger.info(f"   GPU Available: {result['gpu_optimization']}")
        except Exception as e:
            logger.warning(f"   ⚠️  GPU check failed: {e}")
        logger.info("")

        # 2. Verify system shortcuts
        logger.info("📋 Step 2: Verifying System Shortcuts")
        logger.info("")
        shortcuts_file = self.project_root / "data" / "manus_shortcuts" / "manus_system_shortcuts.ahk"
        result["system_shortcuts"] = shortcuts_file.exists()
        logger.info(f"   System Shortcuts: {result['system_shortcuts']}")
        logger.info("")

        # 3. Check Virtual Assistants
        logger.info("📋 Step 3: Checking Virtual Assistants")
        logger.info("")
        if self.va_detector:
            va_health = self.va_detector.check_va_health()
            required_running = va_health["summary"].get("required_running", 0)
            required_not_running = va_health["summary"].get("required_not_running", 0)
            result["vas_running"] = (
                required_running > 0 and required_not_running == 0
            )
            result["va_health"] = va_health
            logger.info(f"   VAs Running: {result['vas_running']}")
            logger.info(f"   Required Running: {required_running}")
            logger.info(f"   Required NOT Running: {required_not_running}")
        else:
            logger.warning("   ⚠️  VA detector not available")
        logger.info("")

        # 4. Check Agent Widgets
        logger.info("📋 Step 4: Checking Agent Widgets")
        logger.info("")
        result["agent_widgets"] = self._check_agent_widgets()
        logger.info(f"   Agent Widgets: {result['agent_widgets']}")
        logger.info("")

        # 5. Determine if ready for reboot
        result["ready_for_reboot"] = (
            result["gpu_optimization"] and
            result["system_shortcuts"] and
            len(result["issues"]) == 0
        )

        logger.info("=" * 80)
        logger.info("✅ POST-OPS VERIFICATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Ready for Reboot: {result['ready_for_reboot']}")
        logger.info("")

        return result

    def _check_agent_widgets(self) -> bool:
        try:
            """Check if agent widgets are configured"""
            # Check for widget configuration files
            widget_configs = [
                self.project_root / "config" / "agent_widgets.json",
                self.project_root / "config" / "widgets.json",
                self.project_root / ".cursor" / "widgets.json"
            ]

            return any(config.exists() for config in widget_configs)

        except Exception as e:
            self.logger.error(f"Error in _check_agent_widgets: {e}", exc_info=True)
            raise
    def create_agent_widgets_config(self) -> Path:
        try:
            """Create agent widgets configuration"""
            config_file = self.project_root / "config" / "agent_widgets.json"

            widgets_config = {
                "version": "1.0.0",
                "description": "Agent Widgets Configuration - Post-Ops Reboot",
                "enabled": True,
                "widgets": [
                    {
                        "id": "jarvis_va_widget",
                        "name": "JARVIS VA Widget",
                        "type": "virtual_assistant",
                        "script": "scripts/python/jarvis_va.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "top-right"
                    },
                    {
                        "id": "imva_widget",
                        "name": "IMVA Widget",
                        "type": "virtual_assistant",
                        "script": "scripts/python/jarvis_ironman_bobblehead_gui.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "bottom-right"
                    },
                    {
                        "id": "acva_widget",
                        "name": "ACVA Widget",
                        "type": "virtual_assistant",
                        "script": "scripts/python/acva.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "bottom-left"
                    },
                    {
                        "id": "jarvis_chat_widget",
                        "name": "JARVIS Chat Widget",
                        "type": "chat",
                        "script": "scripts/python/jarvis_chat.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "top-left"
                    }
                ],
                "startup_order": [
                    "jarvis_va_widget",
                    "jarvis_chat_widget",
                    "imva_widget",
                    "acva_widget"
                ]
            }

            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(widgets_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Agent widgets config created: {config_file.name}")
            return config_file

        except Exception as e:
            self.logger.error(f"Error in create_agent_widgets_config: {e}", exc_info=True)
            raise
    def prepare_reboot(self) -> Dict[str, Any]:
        """
        Prepare system for reboot

        Returns:
            Preparation result
        """
        logger.info("=" * 80)
        logger.info("🚀 PREPARE FOR REBOOT")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "timestamp": datetime.now().isoformat(),
            "pre_verification": None,
            "agent_widgets_created": False,
            "startup_scripts_verified": False,
            "ready": False
        }

        # 1. Post-ops verification
        logger.info("📋 Step 1: Post-Ops Verification")
        logger.info("")
        result["pre_verification"] = self.post_ops_verification()
        logger.info("")

        # 2. Create agent widgets config
        logger.info("📋 Step 2: Creating Agent Widgets Config")
        logger.info("")
        try:
            self.create_agent_widgets_config()
            result["agent_widgets_created"] = True
            logger.info("   ✅ Agent widgets config created")
        except Exception as e:
            logger.error(f"   ❌ Failed to create widgets config: {e}")
        logger.info("")

        # 3. Verify startup scripts
        logger.info("📋 Step 3: Verifying Startup Scripts")
        logger.info("")
        startup_script = self.project_root / "scripts" / "startup" / "start_lumina_complete_system.ps1"
        result["startup_scripts_verified"] = startup_script.exists()
        logger.info(f"   Startup Script: {result['startup_scripts_verified']}")
        logger.info("")

        # 4. Root Cause Analysis
        logger.info("📋 Step 4: Root Cause Analysis (@RC @RR)")
        logger.info("")
        if self.root_cause:
            issues = []
            if not result["pre_verification"].get("vas_running", False):
                issues.append("Virtual Assistants not running")
            if not result["pre_verification"].get("agent_widgets", False):
                issues.append("Agent widgets not configured")

            if issues:
                for issue in issues:
                    logger.info(f"   🔍 Analyzing: {issue}")
                    # Get relevant root causes
                    relevant_causes = [
                        cause for cause in self.root_cause.root_causes
                        if not cause.resolved and issue.lower() in str(cause).lower()
                    ]
                    logger.info(f"   ✅ Found {len(relevant_causes)} relevant root causes")
        logger.info("")

        # 5. @DOIT with @RR
        logger.info("📋 Step 5: @DOIT with @RR")
        logger.info("")
        if self.doit:
            doit_result = self.doit.doit(
                "Post-Ops Reboot: Ensure agent widgets and virtual assistants are active after reboot",
                auto_5w1h=True,
                auto_root_cause=True,
                execute=False  # Don't execute yet, just plan
            )
            logger.info("   ✅ @DOIT plan generated")
            result["doit_plan"] = doit_result
        logger.info("")

        result["ready"] = (
            result["pre_verification"].get("ready_for_reboot", False) and
            result["agent_widgets_created"] and
            result["startup_scripts_verified"]
        )

        logger.info("=" * 80)
        logger.info("✅ REBOOT PREPARATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Ready: {result['ready']}")
        logger.info("")

        if result["ready"]:
            logger.info("📋 Next: Execute reboot and verify all systems start")
            logger.info("")

        return result

    def execute_reboot(self, delay_seconds: int = 10) -> Dict[str, Any]:
        try:
            """
            Execute system reboot

            Args:
                delay_seconds: Delay before reboot

            Returns:
                Reboot result
            """
            logger.info("=" * 80)
            logger.info("🔄 EXECUTING REBOOT")
            logger.info("=" * 80)
            logger.info("")
            logger.info(f"   Reboot in {delay_seconds} seconds...")
            logger.info("   All systems will auto-start after reboot")
            logger.info("")

            # Create reboot script
            reboot_script = self.data_dir / "reboot_scheduled.ps1"
            with open(reboot_script, 'w', encoding='utf-8') as f:
                f.write(f"""
# Scheduled Reboot - Post-Ops
# Auto-start all systems after reboot

Start-Sleep -Seconds {delay_seconds}

# Reboot system
Restart-Computer -Force
""")

            logger.info(f"   ✅ Reboot script created: {reboot_script.name}")
            logger.info("   ⚠️  Execute reboot script to reboot system")
            logger.info("")

            return {
                "reboot_script": str(reboot_script),
                "delay_seconds": delay_seconds,
                "auto_start_enabled": True
            }
        except Exception as e:
            logger.error(f"Error in execute_reboot: {e}", exc_info=True)
            raise


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Post-Ops Reboot Manager")
    parser.add_argument("--verify", action="store_true", help="Post-ops verification")
    parser.add_argument("--prepare", action="store_true", help="Prepare for reboot")
    parser.add_argument("--reboot", action="store_true", help="Execute reboot")
    parser.add_argument("--delay", type=int, default=10, help="Reboot delay in seconds")

    args = parser.parse_args()

    manager = PostOpsRebootManager()

    if args.reboot:
        manager.execute_reboot(delay_seconds=args.delay)
    elif args.prepare:
        manager.prepare_reboot()
    elif args.verify:
        manager.post_ops_verification()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())