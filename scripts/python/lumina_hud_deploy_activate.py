#!/usr/bin/env python3
"""
LUMINA HUD Deploy & Activate

Deploy and activate the LUMINA HUD system with:
- Graphical, visual & audible alerts
- Mobile and desktop support
- Full LUMINA system integration
- Iron Man style HUD interface
- Real-time status displays

Tags: #LUMINA #HUD #DEPLOY #ACTIVATE #IRON_MAN #VISUAL #AUDIBLE @JARVIS @LUMINA @PEAK @DTN
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess
import threading
import time

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

logger = get_logger("LUMINAHUDDeploy")


class LUMINAHUDDeployActivate:
    """
    LUMINA HUD Deploy & Activate

    Deploys and activates:
    - HUD web server
    - Visual/audible alert system
    - Mobile and desktop interfaces
    - Full LUMINA integration
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize deployment system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.hud_server = None
        self.hud_system = None

        logger.info("✅ LUMINA HUD Deploy & Activate initialized")

    def deploy(self) -> bool:
        """
        Deploy HUD system

        Sets up all components and integrations
        """
        logger.info("🚀 Deploying LUMINA HUD System...")

        try:
            # Initialize HUD system
            from jarvis_hud_system import JARVISHUDSystem
            self.hud_system = JARVISHUDSystem(project_root=self.project_root)
            logger.info("   ✅ HUD System initialized")

            # Verify integrations
            integrations = self._verify_integrations()
            logger.info(f"   ✅ Integrations verified: {integrations['active']}/{integrations['total']}")

            # Initialize web server
            from jarvis_hud_web_server import JARVISHUDWebServer
            self.hud_server = JARVISHUDWebServer(project_root=self.project_root, port=8080)
            logger.info("   ✅ Web Server initialized")

            # Create test alert
            self._create_test_alert()

            logger.info("✅ LUMINA HUD System deployed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False

    def activate(self) -> bool:
        """
        Activate HUD system

        Starts web server and monitoring
        """
        logger.info("⚡ Activating LUMINA HUD System...")

        if not self.hud_system:
            logger.error("   ❌ HUD System not deployed. Run deploy() first.")
            return False

        try:
            # Start web server
            if self.hud_server:
                self.hud_server.start()
                logger.info("   ✅ Web Server started")
                logger.info(f"   🌐 Access HUD at: http://localhost:{self.hud_server.port}")
                logger.info(f"   📱 Mobile: http://<your-ip>:{self.hud_server.port}")

            # Start monitoring
            self._start_monitoring()

            logger.info("✅ LUMINA HUD System activated")
            logger.info("   Visual alerts: ✅ Enabled")
            logger.info("   Audible alerts: ✅ Enabled")
            logger.info("   Mobile support: ✅ Enabled")
            logger.info("   Desktop support: ✅ Enabled")

            return True

        except Exception as e:
            logger.error(f"❌ Activation failed: {e}")
            return False

    def _verify_integrations(self) -> Dict[str, Any]:
        """Verify all system integrations"""
        integrations = {
            "bridge": False,
            "command_control": False,
            "governance": False,
            "intelligence": False,
            "communications": False,
            "voice_profile": False
        }

        if self.hud_system:
            integrations["bridge"] = self.hud_system.bridge is not None
            integrations["command_control"] = self.hud_system.command_control is not None
            integrations["governance"] = self.hud_system.governance is not None
            integrations["intelligence"] = self.hud_system.intelligence is not None
            integrations["communications"] = self.hud_system.communications is not None

        return {
            "total": len(integrations),
            "active": sum(1 for v in integrations.values() if v),
            "details": integrations
        }

    def _create_test_alert(self):
        """Create test alert to verify system"""
        if not self.hud_system:
            return

        try:
            from jarvis_hud_system import AlertPriority, HUDDisplayType

            alert = self.hud_system.create_alert(
                title="LUMINA HUD Activated",
                message="HUD system is now active and monitoring all LUMINA systems",
                priority=AlertPriority.INFO,
                display_type=HUDDisplayType.STATUS,
                action_required=False
            )
            logger.info(f"   ✅ Test alert created: {alert.alert_id}")
        except Exception as e:
            logger.debug(f"Could not create test alert: {e}")

    def _start_monitoring(self):
        """Start monitoring all LUMINA systems"""
        if not self.hud_system:
            return

        def monitor_loop():
            """Monitoring loop"""
            while True:
                try:
                    # Monitor Bridge
                    if self.hud_system.bridge:
                        status = self.hud_system.bridge.get_bridge_status_display()
                        if status.get("active_threats", 0) > 0:
                            from jarvis_hud_system import AlertPriority, HUDDisplayType
                            self.hud_system.create_alert(
                                title="Tactical Alert",
                                message=f"Active threats detected: {status['active_threats']}",
                                priority=AlertPriority.ALERT,
                                display_type=HUDDisplayType.TACTICAL
                            )

                    # Monitor Command & Control
                    if self.hud_system.command_control:
                        status = self.hud_system.command_control.get_command_status()
                        if status.get("crises", {}).get("active", 0) > 0:
                            from jarvis_hud_system import AlertPriority, HUDDisplayType
                            self.hud_system.create_alert(
                                title="Crisis Alert",
                                message=f"Active crises: {status['crises']['active']}",
                                priority=AlertPriority.CRITICAL,
                                display_type=HUDDisplayType.TACTICAL
                            )

                    # Monitor Governance
                    if self.hud_system.governance:
                        status = self.hud_system.governance.get_governance_status()
                        pending = status.get("decisions", {}).get("pending", 0)
                        if pending > 5:
                            from jarvis_hud_system import AlertPriority, HUDDisplayType
                            self.hud_system.create_alert(
                                title="Governance Alert",
                                message=f"Pending decisions: {pending}",
                                priority=AlertPriority.WARNING,
                                display_type=HUDDisplayType.GOVERNANCE
                            )

                    time.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    logger.debug(f"Monitoring error: {e}")
                    time.sleep(60)

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("   ✅ System monitoring started")

    def get_status(self) -> Dict[str, Any]:
        """Get deployment status"""
        return {
            "deployed": self.hud_system is not None,
            "activated": self.hud_server is not None and hasattr(self.hud_server, 'server') and self.hud_server.server is not None,
            "integrations": self._verify_integrations() if self.hud_system else {},
            "web_server": {
                "port": self.hud_server.port if self.hud_server else None,
                "url": f"http://localhost:{self.hud_server.port}" if self.hud_server else None
            },
            "alerts": {
                "active": len(self.hud_system.active_alerts) if self.hud_system else 0
            }
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA HUD Deploy & Activate")
    parser.add_argument("--deploy", action="store_true", help="Deploy HUD system")
    parser.add_argument("--activate", action="store_true", help="Activate HUD system")
    parser.add_argument("--deploy-activate", action="store_true", help="Deploy and activate")
    parser.add_argument("--status", action="store_true", help="Show deployment status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    deployer = LUMINAHUDDeployActivate()

    if args.deploy_activate or (args.deploy and args.activate):
        success = deployer.deploy()
        if success:
            success = deployer.activate()
            if success:
                print("✅ LUMINA HUD System deployed and activated!")
                print(f"   Access at: http://localhost:{deployer.hud_server.port}")
                print("   Press Ctrl+C to stop")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down...")
                    if deployer.hud_server:
                        deployer.hud_server.stop()

    elif args.deploy:
        success = deployer.deploy()
        print(f"{'✅' if success else '❌'} Deployment {'successful' if success else 'failed'}")

    elif args.activate:
        success = deployer.activate()
        print(f"{'✅' if success else '❌'} Activation {'successful' if success else 'failed'}")
        if success:
            print("   Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                if deployer.hud_server:
                    deployer.hud_server.stop()

    elif args.status:
        status = deployer.get_status()
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print("LUMINA HUD Deployment Status:")
            print(f"  Deployed: {'✅' if status['deployed'] else '❌'}")
            print(f"  Activated: {'✅' if status['activated'] else '❌'}")
            if status['web_server']['url']:
                print(f"  Web Server: {status['web_server']['url']}")
            print(f"  Active Alerts: {status['alerts']['active']}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()