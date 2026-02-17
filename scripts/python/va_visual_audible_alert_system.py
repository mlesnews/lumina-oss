#!/usr/bin/env python3
"""
Virtual Assistant Visual/Audible Alert System

Provides visual and audible alerts for VA status, problems, and critical events.
Applies lessons from Kenny B-D-A experiment:
- BUILD: Verify dependencies, components, configurations
- DEPLOY: Proper window management, process handling
- ACTIVATE: Start monitoring and alerting

Tags: #VA_ALERTS #VISUAL #AUDIBLE #BDA #KENNY_LESSONS @JARVIS @LUMINA
"""

import sys
import threading
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
    from va_health_monitoring import VAHealthMonitoring
    from defcon_monitoring_system import DEFCONMonitoringSystem
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    VAHealthMonitoring = None
    DEFCONMonitoringSystem = None

logger = get_logger("VAAlertSystem")


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"           # Blue - Informational
    WARNING = "warning"     # Yellow - Warning
    ERROR = "error"         # Orange - Error
    CRITICAL = "critical"   # Red - Critical


class AlertType(Enum):
    """Types of alerts"""
    VA_HEALTH = "va_health"           # VA health issues
    VA_ACTIVATION = "va_activation"   # VA activated/deactivated
    SYSTEM_ERROR = "system_error"     # System errors
    SECURITY = "security"             # Security alerts
    DEFCON = "defcon"                # DEFCON level changes
    TASK_COMPLETE = "task_complete"      # Task completion
    TASK_FAILED = "task_failed"        # Task failure


@dataclass
class VAAlert:
    """A visual/audible alert"""
    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    va_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged: bool = False
    visual: bool = True
    audible: bool = True
    sound_file: Optional[str] = None
    duration: float = 5.0  # Seconds to display
    persistent: bool = False  # Stay until acknowledged


class VAVisualAudibleAlertSystem:
    """
    Virtual Assistant Visual/Audible Alert System

    Applies Kenny B-D-A lessons:
    - BUILD: Verify all components
    - DEPLOY: Proper initialization
    - ACTIVATE: Start monitoring
    """

    def __init__(self):
        """Initialize alert system - BUILD phase"""
        self.project_root = project_root
        self.data_dir = project_root / "data" / "va_alerts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # BUILD Phase - Verify dependencies
        if not self._build_verify():
            raise RuntimeError("BUILD phase failed - dependencies not met")

        # Initialize components
        self.registry = CharacterAvatarRegistry()
        self.health_monitor = VAHealthMonitoring(self.registry) if VAHealthMonitoring else None
        self.defcon_monitor = DEFCONMonitoringSystem() if DEFCONMonitoringSystem else None

        # Alert storage
        self.active_alerts: Dict[str, VAAlert] = {}
        self.alert_history: List[VAAlert] = []
        self.alert_counter = 0

        # Visual components
        self.alert_window = None
        self.alert_frames: Dict[str, tk.Frame] = {}

        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None

        # Sound system
        self.sound_enabled = True
        self.last_audible_alert_time: Dict[str, float] = {}  # To throttle sounds
        self.alert_cooldown = 300  # 5 minutes default cooldown for same alert type
        self.tactical_silence = True  # Default to True given current crisis

        logger.info("=" * 80)
        logger.info("🔔 VA VISUAL/AUDIBLE ALERT SYSTEM")
        logger.info("=" * 80)
        logger.info("   BUILD Phase: ✅ Complete")

    def _build_verify(self) -> bool:
        """BUILD Phase - Verify dependencies and components"""
        logger.info("🔨 BUILD Phase: Verifying dependencies...")

        # Check tkinter
        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available")
            return False

        # Check registry
        try:
            from character_avatar_registry import CharacterAvatarRegistry
            test_registry = CharacterAvatarRegistry()
            logger.info("✅ Character registry verified")
        except Exception as e:
            logger.error(f"❌ Character registry failed: {e}")
            return False

        logger.info("✅ BUILD Phase: All dependencies verified")
        return True

    def deploy(self) -> bool:
        """DEPLOY Phase - Initialize visual components"""
        logger.info("🚀 DEPLOY Phase: Initializing visual components...")

        if not TKINTER_AVAILABLE:
            logger.warning("⚠️  tkinter not available - alerts will be console-only")
            return False

        try:
            # Create alert window (initially hidden)
            self.alert_window = tk.Toplevel()
            self.alert_window.title("VA Alert System")
            self.alert_window.overrideredirect(True)  # No window decorations
            self.alert_window.attributes('-topmost', True)
            self.alert_window.configure(bg='#000000')

            # Position at top-right
            screen_width = self.alert_window.winfo_screenwidth()
            self.alert_window.geometry(f"400x600+{screen_width - 420}+20")

            # Alert container
            self.alert_container = tk.Frame(self.alert_window, bg='#000000')
            self.alert_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Initially hide window (will show when alerts appear)
            self.alert_window.withdraw()

            logger.info("✅ DEPLOY Phase: Visual components initialized")
            return True
        except Exception as e:
            logger.error(f"❌ DEPLOY Phase failed: {e}")
            return False

    def activate(self) -> bool:
        """ACTIVATE Phase - Start monitoring and alerting"""
        logger.info("⚡ ACTIVATE Phase: Starting monitoring...")

        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("✅ ACTIVATE Phase: Monitoring started")
            return True
        return False

    def _monitoring_loop(self):
        """Main monitoring loop - checks for alerts"""
        logger.info("👁️  Alert monitoring loop started")

        while self.monitoring_active:
            try:
                # Check VA health
                if self.health_monitor:
                    self._check_va_health()

                # Check DEFCON level
                if self.defcon_monitor:
                    self._check_defcon_alerts()

                # Check for system errors
                self._check_system_errors()

                # Clean up old alerts
                self._cleanup_old_alerts()

                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def _check_va_health(self):
        """Check VA health and create alerts"""
        try:
            for va in self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT):
                health = self.health_monitor.health_metrics.get(va.character_id)
                if health and health.status.value not in ["healthy", "normal"]:
                    self.create_alert(
                        AlertType.VA_HEALTH,
                        AlertLevel.WARNING,
                        f"{va.name} Health Issue",
                        f"{va.name} status: {health.status.value}",
                        va_id=va.character_id
                    )
        except Exception as e:
            logger.debug(f"Health check error: {e}")

    def _check_defcon_alerts(self):
        """Check DEFCON level and create alerts"""
        try:
            status = self.defcon_monitor.get_current_status()
            defcon_level = status["defcon_level"]

            if defcon_level <= 2:  # High alert or critical
                self.create_alert(
                    AlertType.DEFCON,
                    AlertLevel.CRITICAL if defcon_level == 1 else AlertLevel.ERROR,
                    f"DEFCON {defcon_level} Alert",
                    f"System alert level: {status['defcon_name']}. {status['total_issues']} issues detected.",
                    persistent=True
                )
        except Exception as e:
            logger.debug(f"DEFCON check error: {e}")

    def _check_system_errors(self):
        try:
            """Check for system errors"""
            # Check error logs
            error_log_dir = self.project_root / "data" / "logs"
            if error_log_dir.exists():
                error_files = list(error_log_dir.glob("*error*.log")) + list(error_log_dir.glob("*error*.jsonl"))
                if error_files:
                    # Check most recent error file
                    latest_file = max(error_files, key=lambda p: p.stat().st_mtime)
                    if (datetime.now().timestamp() - latest_file.stat().st_mtime) < 60:  # Last minute
                        self.create_alert(
                            AlertType.SYSTEM_ERROR,
                            AlertLevel.ERROR,
                            "System Error Detected",
                            f"Recent error in {latest_file.name}",
                            persistent=False
                        )

        except Exception as e:
            self.logger.error(f"Error in _check_system_errors: {e}", exc_info=True)
            raise
    def create_alert(self, alert_type: AlertType, level: AlertLevel, title: str, 
                    message: str, va_id: Optional[str] = None, persistent: bool = False,
                    visual: bool = True, audible: bool = True) -> str:
        """Create a new alert"""
        self.alert_counter += 1
        alert_id = f"alert_{self.alert_counter:06d}"

        alert = VAAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            level=level,
            title=title,
            message=message,
            va_id=va_id,
            persistent=persistent,
            visual=visual,
            audible=audible
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # Keep only last 100 alerts in history
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        # Display alert
        if visual:
            self._display_alert(alert)

        if audible:
            self._play_alert_sound(alert)

        logger.info(f"🔔 Alert created: {title} ({level.value})")
        return alert_id

    def _display_alert(self, alert: VAAlert):
        """Display visual alert"""
        if not self.alert_window or not TKINTER_AVAILABLE:
            # Console fallback
            level_icons = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.ERROR: "❌",
                AlertLevel.CRITICAL: "🚨"
            }
            icon = level_icons.get(alert.level, "🔔")
            print(f"{icon} {alert.title}: {alert.message}")
            return

        try:
            # Show window if hidden
            if not self.alert_window.winfo_viewable():
                self.alert_window.deiconify()

            # Create alert frame
            alert_frame = tk.Frame(
                self.alert_container,
                bg='#1a1a1a',
                relief=tk.RAISED,
                borderwidth=2
            )
            alert_frame.pack(fill=tk.X, padx=2, pady=2)
            self.alert_frames[alert.alert_id] = alert_frame

            # Color based on level
            level_colors = {
                AlertLevel.INFO: "#0066cc",
                AlertLevel.WARNING: "#ffcc00",
                AlertLevel.ERROR: "#ff6600",
                AlertLevel.CRITICAL: "#ff0000"
            }
            border_color = level_colors.get(alert.level, "#666666")
            alert_frame.configure(highlightbackground=border_color, highlightthickness=2)

            # Title
            title_label = tk.Label(
                alert_frame,
                text=alert.title,
                font=('Arial', 10, 'bold'),
                bg='#1a1a1a',
                fg='#ffffff',
                anchor='w'
            )
            title_label.pack(fill=tk.X, padx=5, pady=2)

            # Message
            message_label = tk.Label(
                alert_frame,
                text=alert.message,
                font=('Arial', 9),
                bg='#1a1a1a',
                fg='#cccccc',
                anchor='w',
                wraplength=380
            )
            message_label.pack(fill=tk.X, padx=5, pady=2)

            # Timestamp
            timestamp = datetime.fromisoformat(alert.timestamp).strftime("%H:%M:%S")
            time_label = tk.Label(
                alert_frame,
                text=timestamp,
                font=('Arial', 7),
                bg='#1a1a1a',
                fg='#666666'
            )
            time_label.pack(side=tk.RIGHT, padx=5, pady=2)

            # Dismiss button
            if not alert.persistent:
                dismiss_btn = tk.Button(
                    alert_frame,
                    text="✕",
                    font=('Arial', 8),
                    bg='#333333',
                    fg='#ffffff',
                    width=2,
                    height=1,
                    command=lambda aid=alert.alert_id: self.dismiss_alert(aid),
                    relief=tk.FLAT
                )
                dismiss_btn.pack(side=tk.RIGHT, padx=2, pady=2)

            # Auto-dismiss non-persistent alerts
            if not alert.persistent:
                self.alert_window.after(int(alert.duration * 1000), 
                                      lambda aid=alert.alert_id: self.dismiss_alert(aid))
        except Exception as e:
            logger.error(f"Error displaying alert: {e}")

    def _play_alert_sound(self, alert: VAAlert):
        """Play audible alert - with Tactical Silence and Throttling"""
        if not self.sound_enabled or self.tactical_silence:
            return

        # Throttling: Check if we've played this alert type/title recently
        current_time = time.time()
        alert_key = f"{alert.alert_type.value}_{alert.title}"
        last_time = self.last_audible_alert_time.get(alert_key, 0)

        # Only beep if cooldown has passed OR if it's a CRITICAL escalation
        if (current_time - last_time < self.alert_cooldown) and (alert.level != AlertLevel.CRITICAL):
            logger.debug(f"🔇 Throttling audible alert: {alert.title}")
            return

        self.last_audible_alert_time[alert_key] = current_time

        try:
            import winsound

            # Different sounds for different levels
            sound_map = {
                AlertLevel.INFO: winsound.MB_ICONASTERISK,      # System asterisk
                AlertLevel.WARNING: winsound.MB_ICONEXCLAMATION, # System exclamation
                AlertLevel.ERROR: winsound.MB_ICONHAND,          # System hand/stop
                AlertLevel.CRITICAL: winsound.MB_ICONHAND       # System critical
            }

            sound_type = sound_map.get(alert.level, winsound.MB_ICONASTERISK)
            winsound.MessageBeep(sound_type)
        except ImportError:
            # Fallback: use print
            level_sounds = {
                AlertLevel.INFO: "🔔",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.ERROR: "🚨",
                AlertLevel.CRITICAL: "🚨🚨🚨"
            }
            sound = level_sounds.get(alert.level, "🔔")
            print(f"{sound} {alert.title}")
        except Exception as e:
            logger.debug(f"Sound playback error: {e}")

    def dismiss_alert(self, alert_id: str):
        """Dismiss an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            del self.active_alerts[alert_id]

            # Remove from display
            if alert_id in self.alert_frames:
                self.alert_frames[alert_id].destroy()
                del self.alert_frames[alert_id]

            # Hide window if no alerts
            if not self.active_alerts and self.alert_window:
                self.alert_window.withdraw()

            logger.info(f"✅ Alert dismissed: {alert_id}")

    def _cleanup_old_alerts(self):
        """Clean up old, non-persistent alerts"""
        current_time = datetime.now()
        to_remove = []

        for alert_id, alert in self.active_alerts.items():
            if not alert.persistent:
                alert_time = datetime.fromisoformat(alert.timestamp)
                age = (current_time - alert_time).total_seconds()
                if age > alert.duration:
                    to_remove.append(alert_id)

        for alert_id in to_remove:
            self.dismiss_alert(alert_id)

    def execute_bda(self) -> Dict[str, Any]:
        """Execute BUILD-DEPLOY-ACTIVATE workflow"""
        logger.info("=" * 80)
        logger.info("🔄 EXECUTING VA ALERT SYSTEM B-D-A")
        logger.info("=" * 80)

        results = {
            "build": self._build_verify(),
            "deploy": self.deploy(),
            "activate": self.activate(),
            "timestamp": datetime.now().isoformat()
        }

        success = all([results["build"], results["deploy"], results["activate"]])
        results["success"] = success

        if success:
            logger.info("✅ VA ALERT SYSTEM B-D-A COMPLETE")
        else:
            logger.warning("⚠️  VA ALERT SYSTEM B-D-A COMPLETE WITH WARNINGS")

        return results


def main():
    """Main entry point"""
    try:
        alert_system = VAVisualAudibleAlertSystem()

        # Execute B-D-A workflow
        results = alert_system.execute_bda()

        if results["success"]:
            # Create test alert
            alert_system.create_alert(
                AlertType.VA_ACTIVATION,
                AlertLevel.INFO,
                "Alert System Active",
                "Visual and audible alert system is now monitoring VAs",
                persistent=False
            )

            # Keep running
            if TKINTER_AVAILABLE:
                alert_system.alert_window.mainloop()
            else:
                # Console mode - keep monitoring
                while True:
                    time.sleep(1)

        return 0 if results["success"] else 1
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":


    sys.exit(main())