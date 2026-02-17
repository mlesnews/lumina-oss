#!/usr/bin/env python3
"""
JARVIS Reverse Stoplight Alert System

Reverse stoplight: Critical messages at top (right under JARVIS)
- More critical = bigger font, wider, draws attention
- Visual effects (pulsing, glow, animation)
- Audio effects through ElevenLabs

Tags: #JARVIS #ALERTS #STOPLIGHT #VISUAL_EFFECTS #AUDIO @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

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

logger = get_logger("JARVISReverseStoplight")


class AlertLevel(Enum):
    """Alert severity levels - reverse stoplight (critical at top)"""
    CRITICAL = "critical"  # Red - biggest, most attention
    WARNING = "warning"    # Yellow/Orange - medium
    INFO = "info"         # Green - normal
    STATUS = "status"     # Cyan - informational


@dataclass
class Alert:
    """Alert message with visual/audio properties"""
    level: AlertLevel
    message: str
    duration: float = 5.0  # How long to display
    audio_enabled: bool = True
    visual_effects: bool = True
    font_size: int = None  # Auto-calculated based on level if None
    width_multiplier: float = 1.0  # Width scaling for attention


class JARVISReverseStoplightAlerts:
    """Reverse stoplight alert system for JARVIS"""

    def __init__(self, canvas=None, text_positions: Optional[Dict] = None):
        self.canvas = canvas
        self.text_positions = text_positions or {}
        self.current_alert: Optional[Alert] = None
        self.alert_animation_active = False
        self.alert_thread = None

        # Visual effect state
        self.pulse_phase = 0.0
        self.glow_intensity = 1.0

        # Audio system (ElevenLabs)
        self.elevenlabs_voice = None
        self._initialize_elevenlabs()

        # Alert level properties (reverse stoplight - critical = biggest)
        self.alert_properties = {
            AlertLevel.CRITICAL: {
                "color": "#ff0000",  # Red
                "font_size": 14,     # Biggest
                "width_multiplier": 1.5,  # Widest
                "glow_color": "#ff4444",
                "pulse_speed": 0.3,  # Fast pulse
                "audio_priority": "high"
            },
            AlertLevel.WARNING: {
                "color": "#ffaa00",  # Orange/Yellow
                "font_size": 12,     # Medium
                "width_multiplier": 1.2,
                "glow_color": "#ffcc44",
                "pulse_speed": 0.2,
                "audio_priority": "medium"
            },
            AlertLevel.INFO: {
                "color": "#00ff00",  # Green
                "font_size": 10,     # Normal
                "width_multiplier": 1.0,
                "glow_color": "#44ff44",
                "pulse_speed": 0.1,
                "audio_priority": "low"
            },
            AlertLevel.STATUS: {
                "color": "#00ccff",  # Cyan (JARVIS color)
                "font_size": 9,      # Smallest
                "width_multiplier": 0.9,
                "glow_color": "#44ccff",
                "pulse_speed": 0.05,
                "audio_priority": "low"
            }
        }

    def _initialize_elevenlabs(self):
        """Initialize ElevenLabs for audio alerts"""
        try:
            from jarvis_elevenlabs_voice import JARVISElevenLabsVoice
            self.elevenlabs_voice = JARVISElevenLabsVoice()
            if self.elevenlabs_voice.api_key:
                logger.info("✅ ElevenLabs initialized for alert audio")
            else:
                logger.warning("⚠️  ElevenLabs API key not available - alert audio disabled")
        except ImportError:
            logger.debug("ElevenLabs not available for alert audio")
            self.elevenlabs_voice = None

    def show_alert(self, level: AlertLevel, message: str, duration: float = 5.0, 
                   audio_enabled: bool = True, visual_effects: bool = True):
        """Show alert with reverse stoplight system"""
        if not self.canvas:
            logger.warning("⚠️  No canvas available for alerts")
            return

        # Create alert
        alert = Alert(
            level=level,
            message=message,
            duration=duration,
            audio_enabled=audio_enabled,
            visual_effects=visual_effects
        )

        # Get properties for this alert level
        props = self.alert_properties[level]
        alert.font_size = props["font_size"]
        alert.width_multiplier = props["width_multiplier"]

        self.current_alert = alert

        # Display alert
        self._display_alert(alert)

        # Play audio through ElevenLabs
        if audio_enabled and self.elevenlabs_voice:
            self._play_alert_audio(alert, props)

        # Start visual effects animation
        if visual_effects:
            self._start_alert_animation(alert, props)

        # Auto-dismiss after duration
        if duration > 0:
            threading.Timer(duration, self.dismiss_alert).start()

    def _display_alert(self, alert: Alert):
        """Display alert text on canvas"""
        if not self.canvas:
            return

        try:
            # Clear previous alert
            self.canvas.delete("alert_text")
            self.canvas.delete("alert_glow")
            self.canvas.delete("alert_background")

            # Get position (right under JARVIS name)
            center_x = 150
            status_y = self.text_positions.get("status_y", 84)

            # Get properties
            props = self.alert_properties[alert.level]
            color = props["color"]
            font_size = alert.font_size
            width_mult = alert.width_multiplier

            # Calculate text width (approximate)
            # Font size affects width, so we scale accordingly
            base_width = len(alert.message) * (font_size * 0.6)  # Approximate char width
            text_width = base_width * width_mult

            # Draw background/glow for attention (if critical/warning)
            if alert.level in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                glow_color = props["glow_color"]
                glow_alpha = 0.3
                glow_r = int(int(glow_color[1:3], 16) * glow_alpha)
                glow_g = int(int(glow_color[3:5], 16) * glow_alpha)
                glow_b = int(int(glow_color[5:7], 16) * glow_alpha)
                glow_hex = f"#{glow_r:02x}{glow_g:02x}{glow_b:02x}"

                # Draw glow background (wider for critical)
                glow_width = text_width * 1.2
                glow_height = font_size * 1.5
                self.canvas.create_rectangle(
                    center_x - glow_width // 2, status_y - glow_height // 2,
                    center_x + glow_width // 2, status_y + glow_height // 2,
                    fill=glow_hex,
                    outline='',
                    tags="alert_background"
                )

            # Draw shadow for legibility
            for offset_x, offset_y in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
                self.canvas.create_text(
                    center_x + offset_x, status_y + offset_y,
                    text=alert.message,
                    font=('Arial', font_size, 'bold'),
                    fill='#000000',
                    tags="alert_text_shadow"
                )

            # Draw main text (bigger font for critical)
            self.canvas.create_text(
                center_x, status_y,
                text=alert.message,
                font=('Arial', font_size, 'bold'),
                fill=color,
                tags="alert_text"
            )

            self.canvas.update()
        except Exception as e:
            logger.error(f"Error displaying alert: {e}")

    def _play_alert_audio(self, alert: Alert, props: Dict):
        """Play alert audio through ElevenLabs"""
        if not self.elevenlabs_voice:
            return

        try:
            # Generate audio message based on level
            if alert.level == AlertLevel.CRITICAL:
                audio_text = f"CRITICAL ALERT: {alert.message}"
            elif alert.level == AlertLevel.WARNING:
                audio_text = f"WARNING: {alert.message}"
            else:
                audio_text = alert.message

            # Play through ElevenLabs (non-blocking)
            def play_audio():
                try:
                    self.elevenlabs_voice.speak(audio_text)
                except Exception as e:
                    logger.debug(f"Alert audio error: {e}")

            audio_thread = threading.Thread(target=play_audio, daemon=True)
            audio_thread.start()
        except Exception as e:
            logger.debug(f"Error playing alert audio: {e}")

    def _start_alert_animation(self, alert: Alert, props: Dict):
        """Start visual effects animation (pulsing, glow)"""
        if self.alert_animation_active:
            return

        self.alert_animation_active = True
        pulse_speed = props["pulse_speed"]
        glow_color = props["glow_color"]

        def animate():
            while self.alert_animation_active and self.current_alert == alert:
                try:
                    # Pulse effect
                    self.pulse_phase += pulse_speed
                    if self.pulse_phase > 6.28:  # 2*pi
                        self.pulse_phase = 0.0

                    # Calculate pulse intensity (0.8 to 1.0)
                    pulse_intensity = 0.8 + 0.2 * (1 + (self.pulse_phase / 3.14)) / 2

                    # Update glow intensity
                    if self.canvas and alert.level in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                        # Update background glow
                        try:
                            glow_alpha = 0.2 + 0.1 * pulse_intensity
                            glow_r = int(int(glow_color[1:3], 16) * glow_alpha)
                            glow_g = int(int(glow_color[3:5], 16) * glow_alpha)
                            glow_b = int(int(glow_color[5:7], 16) * glow_alpha)
                            glow_hex = f"#{glow_r:02x}{glow_g:02x}{glow_b:02x}"

                            self.canvas.itemconfig("alert_background", fill=glow_hex)
                            self.canvas.update()
                        except:
                            pass

                    time.sleep(0.05)  # ~20 FPS for smooth animation
                except:
                    break

        self.alert_thread = threading.Thread(target=animate, daemon=True)
        self.alert_thread.start()

    def dismiss_alert(self):
        """Dismiss current alert"""
        if self.canvas:
            self.canvas.delete("alert_text")
            self.canvas.delete("alert_text_shadow")
            self.canvas.delete("alert_glow")
            self.canvas.delete("alert_background")
            self.canvas.update()

        self.alert_animation_active = False
        self.current_alert = None

    def update_canvas(self, canvas):
        """Update canvas reference"""
        self.canvas = canvas

    def update_text_positions(self, text_positions: Dict):
        """Update text position references"""
        self.text_positions = text_positions


# Singleton instance
_alert_system_instance = None

def get_jarvis_reverse_stoplight_alerts(canvas=None, text_positions: Optional[Dict] = None):
    """Get singleton instance of reverse stoplight alert system"""
    global _alert_system_instance
    if _alert_system_instance is None:
        _alert_system_instance = JARVISReverseStoplightAlerts(canvas, text_positions)
    else:
        if canvas:
            _alert_system_instance.update_canvas(canvas)
        if text_positions:
            _alert_system_instance.update_text_positions(text_positions)
    return _alert_system_instance
