#!/usr/bin/env python3
"""
JARVIS GAZE SYNC System

Detects when JARVIS and operator are in GAZE SYNC (>3 seconds) and provides:
- Visual cue: Subtle iris twinkle
- Audible cue: JARVIS-inspired "chime" informational alert
- Flow state detection: Optimal state where AI is in full control, operator is idle/observer
- Automatic control relinquishing: JARVIS ALWAYS relinquishes control when operator actively interrupts

Tags: #GAZE_SYNC #FLOW_STATE #VISUAL_CUE #AUDIBLE_CUE #CONTROL_RELINQUISH @JARVIS @LUMINA
"""

import sys
import time
import threading
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("JARVISGazeSync")


class GazeSyncState(Enum):
    """Gaze sync state"""
    NO_SYNC = "no_sync"
    SYNCING = "syncing"
    IN_SYNC = "in_sync"
    FLOW_STATE = "flow_state"
    INTERRUPTED = "interrupted"


class ControlState(Enum):
    """Control state"""
    OPERATOR_CONTROL = "operator_control"
    AI_CONTROL = "ai_control"
    TRANSITIONING = "transitioning"


@dataclass
class GazeSyncConfig:
    """Gaze sync configuration"""
    sync_threshold_seconds: float = 3.0  # Minimum time for gaze sync
    flow_state_threshold_seconds: float = 5.0  # Time in sync before flow state
    check_interval_seconds: float = 0.1  # How often to check gaze
    iris_twinkle_duration: float = 0.5  # Duration of iris twinkle animation
    chime_duration: float = 0.3  # Duration of chime sound
    enable_visual_cues: bool = True
    enable_audible_cues: bool = True


@dataclass
class GazeSyncEvent:
    """Gaze sync event"""
    timestamp: datetime
    event_type: str  # "sync_started", "sync_achieved", "flow_state", "interrupted"
    duration_seconds: float
    state: GazeSyncState
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISGazeSyncSystem:
    """
    JARVIS GAZE SYNC System

    Detects gaze sync between JARVIS and operator, provides visual/audible cues,
    detects optimal flow state, and manages control relinquishing.

    Features:
    - Gaze sync detection (>3 seconds)
    - Visual cue: Iris twinkle
    - Audible cue: JARVIS-inspired chime
    - Flow state detection (AI in control, operator idle/observer)
    - Automatic control relinquishing on operator interruption
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize GAZE SYNC system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "gaze_sync"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.config = GazeSyncConfig()
        self.logger = logger

        # State tracking
        self.gaze_sync_start_time: Optional[datetime] = None
        self.current_state: GazeSyncState = GazeSyncState.NO_SYNC
        self.control_state: ControlState = ControlState.OPERATOR_CONTROL
        self.in_gaze_sync: bool = False
        self.in_flow_state: bool = False

        # Event history
        self.event_history: list[GazeSyncEvent] = []

        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_running = False
        self.lock = threading.Lock()

        # Callbacks
        self.visual_cue_callback: Optional[Callable] = None
        self.audible_cue_callback: Optional[Callable] = None
        self.flow_state_callback: Optional[Callable] = None
        self.control_relinquish_callback: Optional[Callable] = None

        # Integration with operator monitoring
        try:
            from operator_idleness_restriction import get_operator_idleness_restriction
            self.operator_monitor = get_operator_idleness_restriction(project_root)
        except ImportError:
            self.operator_monitor = None
            self.logger.warning("⚠️  Operator idleness monitor not available")

        # Integration with IR camera for gaze detection
        # CRITICAL: Use IR camera ONLY - regular camera emits bright white light
        try:
            from ir_camera_helper import capture_operator_state
            self.capture_operator_state = capture_operator_state
            self.camera_available = True
            self.logger.info("✅ IR camera available for gaze detection (no bright light)")
        except ImportError:
            self.capture_operator_state = None
            self.camera_available = False
            self.logger.warning("⚠️  IR camera not available for gaze detection")

        self.logger.info("✅ JARVIS GAZE SYNC System initialized")
        self.logger.info(f"   Sync threshold: {self.config.sync_threshold_seconds}s")
        self.logger.info(f"   Flow state threshold: {self.config.flow_state_threshold_seconds}s")

    def set_visual_cue_callback(self, callback: Callable):
        """Set callback for visual cues (iris twinkle)"""
        self.visual_cue_callback = callback

    def set_audible_cue_callback(self, callback: Callable):
        """Set callback for audible cues (chime)"""
        self.audible_cue_callback = callback

    def set_flow_state_callback(self, callback: Callable):
        """Set callback for flow state detection"""
        self.flow_state_callback = callback

    def set_control_relinquish_callback(self, callback: Callable):
        """Set callback for control relinquishing"""
        self.control_relinquish_callback = callback

    def detect_gaze_sync(self) -> bool:
        """
        Detect if operator and JARVIS are in gaze sync

        Uses IR camera for actual gaze detection (no bright light).
        Falls back to operator idleness as proxy if camera unavailable.

        Returns:
            True if in gaze sync, False otherwise
        """
        # Try IR camera for actual gaze detection (no bright light)
        if self.capture_operator_state and self.camera_available:
            try:
                success, frame, camera_type = self.capture_operator_state(use_backup=False)
                if success and camera_type == "ir":
                    # IR camera available - can implement actual gaze detection here
                    # For now, use operator idleness as proxy
                    if self.operator_monitor:
                        status = self.operator_monitor.get_status()
                        is_idle = status.get('state') in ['idle', 'active']
                        return is_idle
            except Exception as e:
                self.logger.debug(f"IR camera detection error: {e}")

        # Fallback: use operator idleness as proxy for gaze sync
        if self.operator_monitor:
            status = self.operator_monitor.get_status()
            # Operator is idle/observer = likely in gaze sync
            # This is a simplified detection - can be enhanced with actual gaze tracking
            is_idle = status.get('state') in ['idle', 'active']  # Active but not actively controlling
            return is_idle

        # Fallback: assume no sync if monitoring unavailable
        return False

    def check_gaze_sync(self):
        """Check current gaze sync state and update accordingly"""
        with self.lock:
            in_sync = self.detect_gaze_sync()
            now = datetime.now()

            if in_sync:
                if not self.in_gaze_sync:
                    # Just entered gaze sync
                    self.gaze_sync_start_time = now
                    self.in_gaze_sync = True
                    self.current_state = GazeSyncState.SYNCING
                    self.logger.info("👁️  Gaze sync initiated...")

                # Calculate duration
                if self.gaze_sync_start_time:
                    duration = (now - self.gaze_sync_start_time).total_seconds()

                    # Check if exceeded sync threshold
                    if duration >= self.config.sync_threshold_seconds:
                        if self.current_state == GazeSyncState.SYNCING:
                            # Just achieved sync - trigger cues
                            self.current_state = GazeSyncState.IN_SYNC
                            self._trigger_sync_cues()
                            self._log_event("sync_achieved", duration)
                            self.logger.info(f"✅ GAZE SYNC achieved ({duration:.1f}s)")

                        # Check if in flow state
                        if duration >= self.config.flow_state_threshold_seconds:
                            if not self.in_flow_state:
                                # Entered flow state
                                self.in_flow_state = True
                                self.current_state = GazeSyncState.FLOW_STATE
                                self.control_state = ControlState.AI_CONTROL
                                self._trigger_flow_state_cue()
                                self._log_event("flow_state", duration)
                                self.logger.info(f"🌟 OPTIMAL FLOW STATE - AI in full control, operator in observer mode ({duration:.1f}s)")
            else:
                # Not in sync
                if self.in_gaze_sync:
                    # Just lost sync
                    duration = 0.0
                    if self.gaze_sync_start_time:
                        duration = (now - self.gaze_sync_start_time).total_seconds()

                    self.in_gaze_sync = False
                    self.in_flow_state = False
                    self.gaze_sync_start_time = None

                    # Check if was interrupted (operator took control)
                    if self.control_state == ControlState.AI_CONTROL:
                        # Operator interrupted - relinquish control
                        self._relinquish_control()
                        self.current_state = GazeSyncState.INTERRUPTED
                        self._log_event("interrupted", duration)
                        self.logger.info("🔄 Operator interrupted - JARVIS relinquishing control")
                    else:
                        self.current_state = GazeSyncState.NO_SYNC
                        self._log_event("sync_lost", duration)

    def _trigger_sync_cues(self):
        """Trigger visual and audible cues for gaze sync"""
        # Visual cue: Iris twinkle
        if self.config.enable_visual_cues:
            self._trigger_iris_twinkle()

        # Audible cue: JARVIS chime
        if self.config.enable_audible_cues:
            self._trigger_chime()

    def _trigger_iris_twinkle(self):
        """Trigger subtle iris twinkle visual cue"""
        self.logger.info("✨ Triggering iris twinkle...")

        if self.visual_cue_callback:
            try:
                self.visual_cue_callback("iris_twinkle", {
                    "duration": self.config.iris_twinkle_duration,
                    "intensity": 0.3,  # Subtle
                    "color": "#00D4FF"  # JARVIS cyan
                })
            except Exception as e:
                self.logger.error(f"Error triggering visual cue: {e}")
        else:
            # Default implementation - can integrate with avatar system
            self._default_iris_twinkle()

    def _trigger_chime(self):
        """Trigger JARVIS-inspired chime audible cue"""
        self.logger.info("🔔 Triggering JARVIS chime...")

        if self.audible_cue_callback:
            try:
                self.audible_cue_callback("jarvis_chime", {
                    "duration": self.config.chime_duration,
                    "frequency": 800,  # Hz
                    "tone": "informational"
                })
            except Exception as e:
                self.logger.error(f"Error triggering audible cue: {e}")
        else:
            # Default implementation
            self._default_chime()

    def _trigger_flow_state_cue(self):
        """Trigger flow state notification (iris twinkle + chime)"""
        self.logger.info("🌟 Triggering flow state cue...")

        # Subtle iris twinkle
        if self.config.enable_visual_cues:
            self._trigger_iris_twinkle()

        # JARVIS chime
        if self.config.enable_audible_cues:
            self._trigger_chime()

        # Notify flow state callback
        if self.flow_state_callback:
            try:
                self.flow_state_callback({
                    "state": "flow_state",
                    "ai_control": True,
                    "operator_mode": "observer",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error in flow state callback: {e}")

    def _relinquish_control(self):
        """Relinquish control back to operator"""
        self.logger.info("🔄 JARVIS relinquishing control to operator...")

        # Update control state
        self.control_state = ControlState.OPERATOR_CONTROL
        self.in_flow_state = False

        # Notify callback
        if self.control_relinquish_callback:
            try:
                self.control_relinquish_callback({
                    "state": "operator_control",
                    "reason": "operator_interrupted",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Error in control relinquish callback: {e}")

    def _default_iris_twinkle(self):
        """Default iris twinkle implementation"""
        # Can integrate with avatar rendering system
        # For now, just log
        self.logger.debug("✨ Iris twinkle (default implementation)")

    def _default_chime(self):
        """Default chime implementation"""
        # Can use system beep or audio library
        try:
            import winsound
            # JARVIS-inspired chime: two-tone ascending
            winsound.Beep(800, 150)  # First tone
            time.sleep(0.05)
            winsound.Beep(1000, 150)  # Second tone (higher)
        except ImportError:
            # Fallback: just log
            self.logger.debug("🔔 JARVIS chime (default implementation - winsound not available)")
        except Exception as e:
            self.logger.warning(f"Error playing chime: {e}")

    def _log_event(self, event_type: str, duration: float):
        """Log gaze sync event"""
        event = GazeSyncEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            duration_seconds=duration,
            state=self.current_state,
            metadata={
                "control_state": self.control_state.value,
                "in_flow_state": self.in_flow_state
            }
        )
        self.event_history.append(event)

        # Keep only last 1000 events
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]

        # Save to file
        self._save_event(event)

    def _save_event(self, event: GazeSyncEvent):
        """Save event to file"""
        try:
            event_file = self.data_dir / f"gaze_sync_events_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(event_file, 'a', encoding='utf-8') as f:
                event_data = {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "duration_seconds": event.duration_seconds,
                    "state": event.state.value,
                    "metadata": event.metadata
                }
                f.write(json.dumps(event_data) + '\n')
        except Exception as e:
            self.logger.warning(f"Failed to save event: {e}")

    def start_monitoring(self):
        """Start gaze sync monitoring"""
        if self.monitor_running:
            return

        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("✅ Gaze sync monitoring started")

    def stop_monitoring(self):
        """Stop gaze sync monitoring"""
        self.monitor_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("⏹️  Gaze sync monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitor_running:
            try:
                self.check_gaze_sync()
                time.sleep(self.config.check_interval_seconds)
            except Exception as e:
                self.logger.error(f"Error in gaze sync monitoring: {e}")
                time.sleep(self.config.check_interval_seconds)

    def get_status(self) -> Dict[str, Any]:
        """Get current gaze sync status"""
        with self.lock:
            duration = 0.0
            if self.gaze_sync_start_time:
                duration = (datetime.now() - self.gaze_sync_start_time).total_seconds()

            return {
                "state": self.current_state.value,
                "control_state": self.control_state.value,
                "in_gaze_sync": self.in_gaze_sync,
                "in_flow_state": self.in_flow_state,
                "sync_duration_seconds": duration if self.in_gaze_sync else 0.0,
                "sync_threshold_seconds": self.config.sync_threshold_seconds,
                "flow_state_threshold_seconds": self.config.flow_state_threshold_seconds,
                "visual_cues_enabled": self.config.enable_visual_cues,
                "audible_cues_enabled": self.config.enable_audible_cues
            }

    def operator_interrupted(self):
        """Call this when operator actively interrupts"""
        with self.lock:
            if self.control_state == ControlState.AI_CONTROL:
                self._relinquish_control()
                self.current_state = GazeSyncState.INTERRUPTED
                self.in_gaze_sync = False
                self.in_flow_state = False
                self.gaze_sync_start_time = None
                self.logger.info("🔄 Operator actively interrupted - control relinquished")


# Global instance
_global_gaze_sync: Optional[JARVISGazeSyncSystem] = None


def get_gaze_sync_system(project_root: Optional[Path] = None) -> JARVISGazeSyncSystem:
    try:
        """Get or create global gaze sync system instance"""
        global _global_gaze_sync

        if _global_gaze_sync is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_gaze_sync = JARVISGazeSyncSystem(project_root)
            _global_gaze_sync.start_monitoring()

        return _global_gaze_sync


    except Exception as e:
        logger.error(f"Error in get_gaze_sync_system: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test the system
    print("=" * 80)
    print("JARVIS GAZE SYNC SYSTEM TEST")
    print("=" * 80)
    print()

    system = JARVISGazeSyncSystem()
    system.start_monitoring()

    print("Monitoring gaze sync... (Ctrl+C to stop)")
    try:
        while True:
            status = system.get_status()
            print(f"\rState: {status['state']} | Sync: {status['sync_duration_seconds']:.1f}s | Flow: {status['in_flow_state']}", end='')
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        system.stop_monitoring()
        print("✅ Stopped")
