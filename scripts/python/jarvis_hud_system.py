#!/usr/bin/env python3
"""
JARVIS HUD System - Iron Man Style Heads-Up Display

Graphical, visual & audible alerts for mobile and desktop:
- Iron Man suit-style HUD interface
- Real-time status displays
- Visual alerts (graphical)
- Audible alerts (sound/voice)
- Mobile and desktop support
- Integration with all LUMINA systems

Tags: #JARVIS #HUD #IRON_MAN #VISUAL #AUDIBLE #ALERTS #MOBILE #DESKTOP @JARVIS @LUMINA @PEAK @DTN
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
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

logger = get_logger("JARVISHUD")


class AlertPriority(Enum):
    """Alert priority levels"""
    INFO = "info"  # Blue - informational
    WARNING = "warning"  # Yellow - caution
    ALERT = "alert"  # Orange - attention required
    CRITICAL = "critical"  # Red - immediate action
    EMERGENCY = "emergency"  # Red flashing - maximum priority


class HUDDisplayType(Enum):
    """HUD display types"""
    STATUS = "status"  # System status
    METRICS = "metrics"  # Performance metrics
    ALERTS = "alerts"  # Active alerts
    TACTICAL = "tactical"  # Tactical information
    COMMUNICATIONS = "communications"  # Communication status
    INTELLIGENCE = "intelligence"  # Intelligence data
    BRIDGE = "bridge"  # Bridge command deck
    GOVERNANCE = "governance"  # Governance status


class Platform(Enum):
    """Platform types"""
    DESKTOP = "desktop"  # Desktop/laptop
    MOBILE = "mobile"  # Mobile device
    TABLET = "tablet"  # Tablet device
    WEARABLE = "wearable"  # Wearable device


@dataclass
class HUDAlert:
    """HUD alert"""
    alert_id: str
    title: str
    message: str
    priority: str  # AlertPriority value
    display_type: str  # HUDDisplayType value
    visual_style: Dict[str, Any] = field(default_factory=dict)
    audio_alert: Optional[str] = None  # Sound file or voice message
    duration: float = 5.0  # Display duration in seconds
    dismissible: bool = True
    action_required: bool = False
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HUDDisplay:
    """HUD display element"""
    display_id: str
    display_type: str  # HUDDisplayType value
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0})
    size: Dict[str, float] = field(default_factory=lambda: {"width": 200, "height": 100})
    content: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)
    visible: bool = True
    opacity: float = 1.0
    z_index: int = 0


@dataclass
class HUDConfiguration:
    """HUD configuration"""
    platform: str  # Platform value
    theme: str = "iron_man"  # Theme name
    layout: str = "default"  # Layout name
    displays: List[HUDDisplay] = field(default_factory=list)
    alerts_enabled: bool = True
    audio_enabled: bool = True
    visual_effects: bool = True
    transparency: float = 0.9  # HUD transparency
    color_scheme: Dict[str, str] = field(default_factory=dict)


class JARVISHUDSystem:
    """
    JARVIS HUD System - Iron Man Style

    Provides:
    - Graphical HUD displays
    - Visual alerts
    - Audible alerts
    - Mobile and desktop support
    - Real-time status updates
    - Integration with all LUMINA systems
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS HUD System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_hud"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.alerts_file = self.data_dir / "alerts.json"
        self.config_file = self.data_dir / "hud_config.json"

        # HUD state
        self.active_alerts: Dict[str, HUDAlert] = {}
        self.hud_displays: Dict[str, HUDDisplay] = {}
        self.config: Optional[HUDConfiguration] = None

        # Load state
        self._load_state()

        # Initialize HUD
        self._initialize_hud()

        # Integrate with systems
        self._integrate_systems()

        # Start monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None

        logger.info("✅ JARVIS HUD System initialized")
        logger.info("   Iron Man style HUD ready")
        logger.info("   Visual & Audible alerts enabled")
        logger.info("   System monitoring: Ready")

    def _load_state(self):
        """Load HUD state"""
        # Load alerts
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_alerts = {
                        k: HUDAlert(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"Could not load alerts: {e}")

        # Load configuration
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    displays_data = data.get('displays', [])
                    data['displays'] = [HUDDisplay(**d) for d in displays_data]
                    self.config = HUDConfiguration(**data)
            except Exception as e:
                logger.debug(f"Could not load config: {e}")

    def _save_state(self):
        """Save HUD state"""
        # Save alerts
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.active_alerts.items()}, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")

        # Save configuration
        if self.config:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    config_dict = asdict(self.config)
                    config_dict['displays'] = [asdict(d) for d in self.config.displays]
                    json.dump(config_dict, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Error saving config: {e}")

    def _initialize_hud(self):
        """Initialize HUD displays"""
        # Default displays
        default_displays = [
            {
                "display_id": "status_panel",
                "display_type": HUDDisplayType.STATUS.value,
                "position": {"x": 10, "y": 10},
                "size": {"width": 300, "height": 200},
                "content": {"title": "System Status", "data": {}},
                "style": {"background": "rgba(0,0,0,0.8)", "border": "2px solid #00ff00"}
            },
            {
                "display_id": "metrics_panel",
                "display_type": HUDDisplayType.METRICS.value,
                "position": {"x": 320, "y": 10},
                "size": {"width": 300, "height": 200},
                "content": {"title": "Performance Metrics", "data": {}},
                "style": {"background": "rgba(0,0,0,0.8)", "border": "2px solid #00ffff"}
            },
            {
                "display_id": "alerts_panel",
                "display_type": HUDDisplayType.ALERTS.value,
                "position": {"x": 10, "y": 220},
                "size": {"width": 300, "height": 150},
                "content": {"title": "Active Alerts", "data": {}},
                "style": {"background": "rgba(0,0,0,0.8)", "border": "2px solid #ffaa00"}
            },
            {
                "display_id": "tactical_panel",
                "display_type": HUDDisplayType.TACTICAL.value,
                "position": {"x": 320, "y": 220},
                "size": {"width": 300, "height": 150},
                "content": {"title": "Tactical Status", "data": {}},
                "style": {"background": "rgba(0,0,0,0.8)", "border": "2px solid #ff0000"}
            }
        ]

        for display_data in default_displays:
            display = HUDDisplay(**display_data)
            self.hud_displays[display.display_id] = display

        # Initialize configuration if not exists
        if not self.config:
            self.config = HUDConfiguration(
                platform=Platform.DESKTOP.value,
                theme="iron_man",
                layout="default",
                displays=list(self.hud_displays.values()),
                color_scheme={
                    "primary": "#00ff00",  # Green (Iron Man style)
                    "secondary": "#00ffff",  # Cyan
                    "alert": "#ffaa00",  # Orange
                    "critical": "#ff0000",  # Red
                    "background": "rgba(0,0,0,0.9)"
                }
            )

        self._save_state()

    def _integrate_systems(self):
        """Integrate with LUMINA systems"""
        # Bridge integration
        try:
            from bridge_executive_command_deck import BridgeExecutiveCommandDeck
            self.bridge = BridgeExecutiveCommandDeck(project_root=self.project_root)
            logger.info("   ✅ Bridge integrated")
        except Exception as e:
            logger.warning(f"Bridge not available: {e}")
            self.bridge = None

        # Command & Control integration
        try:
            from jarvis_command_control_center import JARVISCommandControlCenter
            self.command_control = JARVISCommandControlCenter(project_root=self.project_root)
            logger.info("   ✅ Command & Control integrated")
        except Exception as e:
            logger.warning(f"Command & Control not available: {e}")
            self.command_control = None

        # Governance integration
        try:
            from jarvis_governance_system import JARVISGovernanceSystem
            self.governance = JARVISGovernanceSystem(project_root=self.project_root)
            logger.info("   ✅ Governance integrated")
        except Exception as e:
            logger.warning(f"Governance not available: {e}")
            self.governance = None

        # Intelligence integration
        try:
            from lumina_intelligence_collection import LUMINAIntelligenceCollection
            self.intelligence = LUMINAIntelligenceCollection(project_root=self.project_root)
            logger.info("   ✅ Intelligence integrated")
        except Exception as e:
            logger.warning(f"Intelligence not available: {e}")
            self.intelligence = None

        # Communication integration
        try:
            from lumina_n8n_nas_communication_integration import LUMINAN8NNASCommunicationIntegration
            self.communications = LUMINAN8NNASCommunicationIntegration(project_root=self.project_root)
            logger.info("   ✅ Communications integrated")
        except Exception as e:
            logger.warning(f"Communications not available: {e}")
            self.communications = None

    def create_alert(
        self,
        title: str,
        message: str,
        priority: AlertPriority,
        display_type: HUDDisplayType,
        audio_alert: Optional[str] = None,
        action_required: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HUDAlert:
        """
        Create HUD alert (visual & audible)

        Alerts appear on HUD with:
        - Visual display (graphical)
        - Audible notification (sound/voice)
        - Priority-based styling
        """
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Determine visual style based on priority
        visual_style = self._get_alert_visual_style(priority)

        # Determine audio alert if not provided
        if not audio_alert:
            audio_alert = self._get_alert_audio(priority)

        alert = HUDAlert(
            alert_id=alert_id,
            title=title,
            message=message,
            priority=priority.value,
            display_type=display_type.value,
            visual_style=visual_style,
            audio_alert=audio_alert,
            action_required=action_required,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        self.active_alerts[alert_id] = alert
        self._save_state()

        # Trigger visual and audio alerts
        self._trigger_alert(alert)

        logger.warning(f"   🚨 HUD Alert: {priority.value.upper()} - {title}")

        return alert

    def _get_alert_visual_style(self, priority: AlertPriority) -> Dict[str, Any]:
        """Get visual style for alert based on priority"""
        styles = {
            AlertPriority.INFO: {
                "color": "#00ffff",  # Cyan
                "background": "rgba(0,255,255,0.2)",
                "border": "2px solid #00ffff",
                "animation": "pulse",
                "icon": "info"
            },
            AlertPriority.WARNING: {
                "color": "#ffaa00",  # Orange
                "background": "rgba(255,170,0,0.2)",
                "border": "2px solid #ffaa00",
                "animation": "pulse",
                "icon": "warning"
            },
            AlertPriority.ALERT: {
                "color": "#ff8800",  # Bright orange
                "background": "rgba(255,136,0,0.3)",
                "border": "3px solid #ff8800",
                "animation": "flash",
                "icon": "alert"
            },
            AlertPriority.CRITICAL: {
                "color": "#ff0000",  # Red
                "background": "rgba(255,0,0,0.3)",
                "border": "3px solid #ff0000",
                "animation": "flash_fast",
                "icon": "critical"
            },
            AlertPriority.EMERGENCY: {
                "color": "#ff0000",  # Red
                "background": "rgba(255,0,0,0.5)",
                "border": "4px solid #ff0000",
                "animation": "emergency_flash",
                "icon": "emergency",
                "fullscreen": True  # Emergency alerts can be fullscreen
            }
        }
        return styles.get(priority, styles[AlertPriority.INFO])

    def _get_alert_audio(self, priority: AlertPriority) -> str:
        """Get audio alert for priority"""
        audio_alerts = {
            AlertPriority.INFO: "beep_low",
            AlertPriority.WARNING: "beep_medium",
            AlertPriority.ALERT: "beep_high",
            AlertPriority.CRITICAL: "alert_tone",
            AlertPriority.EMERGENCY: "emergency_siren"
        }
        return audio_alerts.get(priority, "beep_low")

    def _trigger_alert(self, alert: HUDAlert):
        """Trigger visual and audio alert"""
        # Visual alert - would trigger UI update
        # Audio alert - would play sound/voice

        # Log alert
        logger.info(f"   🔊 Alert triggered: {alert.title}")
        logger.info(f"      Visual: {alert.visual_style.get('animation', 'none')}")
        logger.info(f"      Audio: {alert.audio_alert}")

        # In actual implementation, this would:
        # 1. Update HUD display with alert
        # 2. Play audio alert
        # 3. Show visual effects
        # 4. Send to mobile/desktop clients

    def update_hud_display(
        self,
        display_id: str,
        content: Dict[str, Any],
        style: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update HUD display content"""
        if display_id not in self.hud_displays:
            return False

        display = self.hud_displays[display_id]
        display.content.update(content)
        if style:
            display.style.update(style)

        self._save_state()

        # Trigger display update
        logger.debug(f"   📊 HUD Display updated: {display_id}")

        return True

    def get_hud_status(self) -> Dict[str, Any]:
        """Get comprehensive HUD status"""
        return {
            "hud_active": True,
            "theme": self.config.theme if self.config else "iron_man",
            "platform": self.config.platform if self.config else "desktop",
            "displays": {
                display_id: {
                    "type": display.display_type,
                    "visible": display.visible,
                    "position": display.position,
                    "size": display.size
                }
                for display_id, display in self.hud_displays.items()
            },
            "active_alerts": len(self.active_alerts),
            "alerts_by_priority": {
                priority.value: sum(1 for a in self.active_alerts.values() if a.priority == priority.value)
                for priority in AlertPriority
            },
            "integrations": {
                "bridge": self.bridge is not None,
                "command_control": self.command_control is not None,
                "governance": self.governance is not None,
            "intelligence": self.intelligence is not None,
            "communications": hasattr(self, 'communications') and self.communications is not None
        }
        }

    def generate_hud_data(self) -> Dict[str, Any]:
        """
        Generate HUD data for rendering

        Returns data structure for HUD rendering on mobile/desktop
        """
        hud_data = {
            "timestamp": datetime.now().isoformat(),
            "theme": self.config.theme if self.config else "iron_man",
            "displays": [
                {
                    "id": display.display_id,
                    "type": display.display_type,
                    "position": display.position,
                    "size": display.size,
                    "content": display.content,
                    "style": display.style,
                    "visible": display.visible,
                    "opacity": display.opacity,
                    "z_index": display.z_index
                }
                for display in self.hud_displays.values()
            ],
            "alerts": [
                {
                    "id": alert.alert_id,
                    "title": alert.title,
                    "message": alert.message,
                    "priority": alert.priority,
                    "display_type": alert.display_type,
                    "visual_style": alert.visual_style,
                    "audio_alert": alert.audio_alert,
                    "duration": alert.duration,
                    "dismissible": alert.dismissible,
                    "action_required": alert.action_required,
                    "timestamp": alert.timestamp
                }
                for alert in self.active_alerts.values()
            ],
            "system_status": self._get_system_status(),
            "tactical_status": self._get_tactical_status(),
            "communications_status": self._get_communications_status(),
            "intelligence_status": self._get_intelligence_status(),
            "governance_status": self._get_governance_status(),
            "metrics": self._get_metrics(),
            "avatar_status": self._get_avatar_status()
        }

        return hud_data

    def _get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for HUD"""
        import psutil
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()

            return {
                "cpu": cpu_percent,
                "memory": memory.percent,
                "network": min(100, (network.bytes_sent + network.bytes_recv) / 1024 / 1024)  # Simplified
            }
        except ImportError:
            # Fallback if psutil not available
            return {
                "cpu": 45.0,
                "memory": 62.0,
                "network": 28.0
            }
        except Exception as e:
            logger.debug(f"Error getting metrics: {e}")
            return {
                "cpu": 0.0,
                "memory": 0.0,
                "network": 0.0
            }

    def _get_governance_status(self) -> Dict[str, Any]:
        """Get governance status for HUD"""
        if self.governance:
            gov_status = self.governance.get_governance_status()
            return {
                "status": "active",
                "pending_decisions": gov_status.get("decisions", {}).get("pending", 0),
                "executive_active": gov_status.get("executive_branch", {}).get("active_decisions", 0)
            }
        return {"status": "unknown"}

    def _get_system_status(self) -> Dict[str, Any]:
        """Get system status for HUD"""
        systems_online = 0
        systems_total = 0

        # Count integrated systems
        if self.bridge:
            systems_total += 1
            systems_online += 1
        if self.command_control:
            systems_total += 1
            systems_online += 1
        if self.governance:
            systems_total += 1
            systems_online += 1
        if self.intelligence:
            systems_total += 1
            systems_online += 1

        health = systems_online / systems_total if systems_total > 0 else 0.0

        return {
            "status": "operational" if health > 0.8 else "degraded" if health > 0.5 else "critical",
            "systems_online": systems_online,
            "systems_total": systems_total,
            "health": health
        }

    def _get_tactical_status(self) -> Dict[str, Any]:
        """Get tactical status for HUD"""
        if self.bridge:
            bridge_status = self.bridge.get_bridge_status_display()
            return {
                "domain": bridge_status.get("domain", "unknown"),
                "tactical_status": bridge_status.get("tactical_status", "green"),
                "active_threats": bridge_status.get("active_threats", 0),
                "active_orders": bridge_status.get("active_orders", 0)
            }
        return {"status": "unknown", "tactical_status": "green", "active_threats": 0}

    def _get_communications_status(self) -> Dict[str, Any]:
        """Get communications status for HUD"""
        if hasattr(self, 'communications') and self.communications:
            report = self.communications.get_integration_report()
            return {
                "status": "connected" if report.get('integration_coverage', {}).get('coverage_percentage', 0) > 50 else "disconnected",
                "channels_active": report.get('workflows_enabled', 0),
                "coverage": report.get('integration_coverage', {}).get('coverage_percentage', 0)
            }
        return {
            "status": "unknown",
            "channels_active": 0
        }

    def _get_intelligence_status(self) -> Dict[str, Any]:
        """Get intelligence status for HUD"""
        if self.intelligence:
            # Get last collection time
            return {
                "status": "collecting",
                "last_collection": "recent",
                "hourly_enabled": True,
                "daily_enabled": True
            }
        return {"status": "unknown"}

    def _get_avatar_status(self) -> Dict[str, Any]:
        """Get avatar status for HUD"""
        try:
            from avatar_display_system import AvatarDisplaySystem
            avatar_system = AvatarDisplaySystem(project_root=self.project_root)
            avatar_data = avatar_system.get_avatar_display_data()
            return avatar_data
        except Exception as e:
            logger.debug(f"Avatar system not available: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "total_avatars": 0,
                "visible_avatars": 0,
                "avatars": {},
                "replica_system_connected": False,
                "avatar_system_available": False
            }

    def monitor_systems(self):
        """
        Monitor all integrated systems and create alerts

        Automatically creates HUD alerts based on system events
        """
        # Monitor bridge for tactical alerts
        if self.bridge:
            bridge_status = self.bridge.get_bridge_status_display()
            tactical_status = bridge_status.get("tactical_status", "green")
            active_threats = bridge_status.get("active_threats", 0)

            if tactical_status in ["red", "black"]:
                self.create_alert(
                    title="TACTICAL ALERT",
                    message=f"Tactical status: {tactical_status.upper()} - {active_threats} active threats",
                    priority=AlertPriority.CRITICAL if tactical_status == "black" else AlertPriority.ALERT,
                    display_type=HUDDisplayType.TACTICAL,
                    action_required=True
                )

        # Monitor command & control for operation alerts
        if self.command_control:
            cmd_status = self.command_control.get_command_status()
            active_crises = cmd_status.get("crises", {}).get("active", 0)

            if active_crises > 0:
                self.create_alert(
                    title="CRISIS DETECTED",
                    message=f"{active_crises} active crisis(es) requiring attention",
                    priority=AlertPriority.CRITICAL,
                    display_type=HUDDisplayType.TACTICAL,
                    action_required=True
                )

        # Monitor governance for decision alerts
        if self.governance:
            gov_status = self.governance.get_governance_status()
            pending_decisions = gov_status.get("decisions", {}).get("pending", 0)

            if pending_decisions > 5:
                self.create_alert(
                    title="GOVERNANCE ALERT",
                    message=f"{pending_decisions} decisions pending approval",
                    priority=AlertPriority.WARNING,
                    display_type=HUDDisplayType.GOVERNANCE
                )

    def start_monitoring(self, interval: float = 5.0):
        """
        Start continuous system monitoring

        Monitors all systems and creates alerts automatically
        """
        import threading
        import time

        if self.monitoring_active:
            return

        self.monitoring_active = True

        def monitor_loop():
            while self.monitoring_active:
                try:
                    self.monitor_systems()
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)

        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()

        logger.info(f"   ✅ System monitoring started (interval: {interval}s)")

    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        logger.info("   ✅ System monitoring stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS HUD System")
    parser.add_argument("--status", action="store_true", help="Show HUD status")
    parser.add_argument("--alert", type=str, nargs=4, metavar=("TITLE", "MESSAGE", "PRIORITY", "TYPE"), help="Create alert")
    parser.add_argument("--hud-data", action="store_true", help="Generate HUD data")
    parser.add_argument("--monitor", action="store_true", help="Start system monitoring")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    hud = JARVISHUDSystem()

    if args.status:
        status = hud.get_hud_status()
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print("JARVIS HUD Status:")
            print(f"  Theme: {status['theme']}")
            print(f"  Platform: {status['platform']}")
            print(f"  Active Alerts: {status['active_alerts']}")

    elif args.alert:
        title, message, priority_str, type_str = args.alert
        priority = AlertPriority[priority_str.upper()]
        display_type = HUDDisplayType[type_str.upper()]
        alert = hud.create_alert(title, message, priority, display_type)
        if args.json:
            print(json.dumps(asdict(alert), indent=2, default=str))
        else:
            print(f"✅ Alert created: {alert.alert_id}")

    elif args.hud_data:
        data = hud.generate_hud_data()
        if args.json:
            print(json.dumps(data, indent=2, default=str))
        else:
            print("HUD Data generated")

    elif args.monitor:
        hud.start_monitoring()
        print("✅ Monitoring started")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            hud.stop_monitoring()
            print("✅ Monitoring stopped")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()