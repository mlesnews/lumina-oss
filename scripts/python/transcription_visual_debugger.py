#!/usr/bin/env python3
"""
Transcription Visual Debugger

Visual debugging overlay showing:
- Context confidence score
- Personage (user vs AI voice identification)
- Listening/Speaking state
- Metrics collection (success tracking)

Tags: #VISUAL_DEBUG #METRICS #CONFIDENCE #PERSONAGE @JARVIS @LUMINA
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

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

logger = get_logger("TranscriptionVisualDebugger")

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    logger.warning("⚠️  tkinter not available - visual debugger will use console output")


@dataclass
class DebugMetrics:
    """Debug metrics for tracking"""
    # Three-state confidence scores (as requested)
    ai_confidence: float = 0.0  # AI's confidence score
    human_confidence_vs_ai: float = 0.0  # Human operator's confidence against the AI
    human_confidence_vs_unknown: float = 0.0  # Human's confidence against the unknown (do they think they know the unknown?)

    # Legacy fields (kept for compatibility)
    context_confidence: float = 0.0
    personage: str = "unknown"  # "user" or "ai"
    state: str = "idle"  # "listening", "speaking", "processing", "idle"
    voice_match_confidence: float = 0.0
    transcription_confidence: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    consecutive_successes: int = 0
    last_update: str = field(default_factory=lambda: datetime.now().isoformat())

    # Voice filter training status
    voice_training_active: bool = False
    voice_samples_collected: int = 0
    voice_samples_needed: int = 3
    voice_profile_trained: bool = False

    # Listening mode (passive vs active)
    listening_mode: str = "passive"  # "passive" or "active"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TranscriptionVisualDebugger:
    """
    Visual debugging overlay for transcription system.

    Shows:
    - Context confidence score
    - Personage (user vs AI)
    - Listening/Speaking state
    - Success metrics
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize visual debugger"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "transcription_debug"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = DebugMetrics()
        self.metrics_file = self.data_dir / "debug_metrics.json"

        # Load existing metrics
        self._load_metrics()

        # Visual window
        self.root = None
        self.canvas = None
        if TKINTER_AVAILABLE:
            self._create_window()

    def _load_metrics(self):
        """Load metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics = DebugMetrics(**data)
            except Exception as e:
                logger.debug(f"Could not load metrics: {e}")

    def _save_metrics(self):
        """Save metrics to file"""
        try:
            self.metrics.last_update = datetime.now().isoformat()
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save metrics: {e}")

    def _create_window(self):
        """Create visual debugging window"""
        if not TKINTER_AVAILABLE:
            return

        self.root = tk.Tk()
        self.root.title("Transcription Visual Debugger")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9)  # Slightly transparent
        self.root.geometry("320x280+10+10")  # Top-left corner, larger for training status indicator

        # Create canvas
        self.canvas = tk.Canvas(self.root, width=320, height=280, bg='black')
        self.canvas.pack()

        # Update display
        self._update_display()

        # Auto-update every 100ms
        self.root.after(100, self._update_loop)

    def _update_display(self):
        """Update visual display"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        # Background
        self.canvas.create_rectangle(0, 0, 320, 280, fill='#1a1a1a', outline='#333')

        y = 20
        line_height = 22

        # Title - change color based on mode
        if self.metrics.listening_mode == "active":
            title_text = "🎤 ACTIVE Listening"
            title_color = '#00ff00'  # Bright green for active
        else:
            title_text = "⏸️  Passive Waiting"
            title_color = '#666666'  # Dim gray for passive

        self.canvas.create_text(150, y, text=title_text, 
                               fill=title_color, font=('Arial', 11, 'bold'))
        y += line_height

        # Three-State Confidence Scores (as requested)
        # 1. AI Confidence
        ai_conf_color = '#00ff00' if self.metrics.ai_confidence > 0.7 else '#ffff00' if self.metrics.ai_confidence > 0.5 else '#ff0000'
        self.canvas.create_text(10, y, text=f"AI Confidence: {self.metrics.ai_confidence:.2f}", 
                               fill=ai_conf_color, font=('Arial', 9), anchor='w')
        y += line_height

        # 2. Human Confidence (vs AI)
        human_ai_conf_color = '#00ff00' if self.metrics.human_confidence_vs_ai > 0.7 else '#ffff00' if self.metrics.human_confidence_vs_ai > 0.5 else '#ff0000'
        self.canvas.create_text(10, y, text=f"Human (vs AI): {self.metrics.human_confidence_vs_ai:.2f}", 
                               fill=human_ai_conf_color, font=('Arial', 9), anchor='w')
        y += line_height

        # 3. Human Confidence (vs Unknown)
        human_unk_conf_color = '#00ff00' if self.metrics.human_confidence_vs_unknown > 0.7 else '#ffff00' if self.metrics.human_confidence_vs_unknown > 0.5 else '#ff0000'
        self.canvas.create_text(10, y, text=f"Human (vs Unknown): {self.metrics.human_confidence_vs_unknown:.2f}", 
                               fill=human_unk_conf_color, font=('Arial', 9), anchor='w')
        y += line_height

        # Personage
        personage_color = '#00ffff' if self.metrics.personage == "user" else '#ff00ff' if self.metrics.personage == "ai" else '#888888'
        personage_text = f"Personage: {self.metrics.personage.upper()}"
        self.canvas.create_text(10, y, text=personage_text, 
                               fill=personage_color, font=('Arial', 10), anchor='w')
        y += line_height

        # Listening Mode (PASSIVE vs ACTIVE) - Different visual indicators
        if self.metrics.listening_mode == "passive":
            # PASSIVE MODE: Subtle "waiting" indicator (no confirmation needed)
            mode_color = '#666666'  # Dim gray - subtle, not distracting
            mode_text = "⏸️  PASSIVE: Waiting for 'Hey Jarvis'"
            mode_font = ('Arial', 9, 'normal')  # Smaller, less prominent
        else:
            # ACTIVE MODE: Clear "listening" confirmation
            mode_color = '#00ff00'  # Bright green - clear confirmation
            mode_text = "🎤 ACTIVE: Listening & Transcribing"
            mode_font = ('Arial', 10, 'bold')  # Larger, bold - prominent

        self.canvas.create_text(10, y, text=mode_text, 
                               fill=mode_color, font=mode_font, anchor='w')
        y += line_height

        # State (only show in active mode, or keep it subtle in passive)
        if self.metrics.listening_mode == "active":
            # Only show detailed state in active mode
            state_color = '#00ff00' if self.metrics.state == "listening" else '#ff8800' if self.metrics.state == "speaking" else '#888888'
            state_text = f"State: {self.metrics.state.upper()}"
            self.canvas.create_text(10, y, text=state_text, 
                                   fill=state_color, font=('Arial', 9), anchor='w')
            y += line_height
        else:
            # In passive mode, state is always "waiting" - don't show it (redundant)
            pass

        # Voice Match Confidence
        if self.metrics.voice_match_confidence > 0:
            voice_color = '#00ff00' if self.metrics.voice_match_confidence > 0.7 else '#ffff00'
            self.canvas.create_text(10, y, text=f"Voice Match: {self.metrics.voice_match_confidence:.2f}", 
                                   fill=voice_color, font=('Arial', 9), anchor='w')
            y += line_height

        # Success Metrics
        success_text = f"Success: {self.metrics.consecutive_successes} consecutive"
        success_color = '#00ff00' if self.metrics.consecutive_successes >= 3 else '#ffff00'
        self.canvas.create_text(10, y, text=success_text, 
                               fill=success_color, font=('Arial', 9), anchor='w')
        y += line_height

        # Total Stats (only show in active mode)
        if self.metrics.listening_mode == "active":
            total_text = f"Total: {self.metrics.success_count}✓ {self.metrics.failure_count}✗"
            self.canvas.create_text(10, y, text=total_text, 
                                   fill='#888888', font=('Arial', 8), anchor='w')
            y += line_height

        # Voice Training Status (only show in active mode)
        if self.metrics.listening_mode == "active" and self.metrics.voice_training_active:
            training_text = f"Training: {self.metrics.voice_samples_collected}/{self.metrics.voice_samples_needed}"
            training_color = '#ffff00' if not self.metrics.voice_profile_trained else '#00ff00'
            self.canvas.create_text(10, y, text=training_text, 
                                   fill=training_color, font=('Arial', 8), anchor='w')

    def _update_loop(self):
        """Update loop for visual display"""
        if self.root and self.root.winfo_exists():
            self._update_display()
            self.root.after(100, self._update_loop)

    def update_ai_confidence(self, confidence: float):
        """Update AI confidence score"""
        self.metrics.ai_confidence = max(0.0, min(1.0, confidence))
        self.metrics.context_confidence = confidence  # Legacy compatibility
        self._save_metrics()

    def update_human_confidence_vs_ai(self, confidence: float):
        """Update human operator's confidence against the AI"""
        self.metrics.human_confidence_vs_ai = max(0.0, min(1.0, confidence))
        self._save_metrics()

    def update_human_confidence_vs_unknown(self, confidence: float):
        """Update human operator's confidence against the unknown (do they think they know the unknown?)"""
        self.metrics.human_confidence_vs_unknown = max(0.0, min(1.0, confidence))
        self._save_metrics()

    def update_context_confidence(self, confidence: float):
        """Update context confidence score (legacy - maps to AI confidence)"""
        self.update_ai_confidence(confidence)

    def update_personage(self, personage: str, confidence: float = 0.0):
        """Update personage (user or AI)"""
        self.metrics.personage = personage.lower()
        self.metrics.voice_match_confidence = confidence
        self._save_metrics()

    def update_state(self, state: str):
        """Update state (listening, speaking, processing, idle)"""
        self.metrics.state = state.lower()
        self._save_metrics()

    def update_listening_mode(self, mode: str):
        """
        Update listening mode (passive or active)

        Args:
            mode: "passive" (waiting for trigger) or "active" (listening/transcribing)
        """
        self.metrics.listening_mode = mode.lower()
        # Auto-update state based on mode
        if mode.lower() == "passive":
            self.metrics.state = "waiting"  # Passive mode is always "waiting"
        elif mode.lower() == "active":
            if self.metrics.state == "waiting":
                self.metrics.state = "listening"  # Switch to listening when active
        self._save_metrics()

    def update_voice_training_status(self, training_active: bool, samples_collected: int = 0, 
                                     samples_needed: int = 3, profile_trained: bool = False):
        """
        Update voice filter training status (IMPORTANT: Operator needs visual feedback)

        Args:
            training_active: Whether training is currently active
            samples_collected: Number of voice samples collected
            samples_needed: Number of samples needed for training
            profile_trained: Whether the profile is fully trained
        """
        self.metrics.voice_training_active = training_active
        self.metrics.voice_samples_collected = samples_collected
        self.metrics.voice_samples_needed = samples_needed
        self.metrics.voice_profile_trained = profile_trained
        self._save_metrics()

    def record_success(self):
        """Record successful operation"""
        self.metrics.success_count += 1
        self.metrics.consecutive_successes += 1
        self.metrics.failure_count = 0  # Reset on success
        self._save_metrics()
        logger.info(f"✅ Success recorded (consecutive: {self.metrics.consecutive_successes})")

    def record_failure(self):
        """Record failed operation"""
        self.metrics.failure_count += 1
        self.metrics.consecutive_successes = 0  # Reset on failure
        self._save_metrics()
        logger.warning(f"❌ Failure recorded (consecutive successes reset)")

    def get_metrics(self) -> DebugMetrics:
        """Get current metrics"""
        return self.metrics

    def run(self):
        """Run visual debugger (blocking)"""
        if self.root:
            self.root.mainloop()
        else:
            # Console mode
            while True:
                self._print_metrics()
                time.sleep(1)

    def _print_metrics(self):
        """Print metrics to console"""
        print("\n" + "=" * 60)
        print("🎤 TRANSCRIPTION VISUAL DEBUGGER")
        print("=" * 60)
        print("Three-State Confidence Scores:")
        print(f"  AI Confidence: {self.metrics.ai_confidence:.2f}")
        print(f"  Human (vs AI): {self.metrics.human_confidence_vs_ai:.2f}")
        print(f"  Human (vs Unknown): {self.metrics.human_confidence_vs_unknown:.2f}")
        print(f"Personage: {self.metrics.personage.upper()}")
        print(f"State: {self.metrics.state.upper()}")
        print(f"Voice Match: {self.metrics.voice_match_confidence:.2f}")
        print(f"Consecutive Successes: {self.metrics.consecutive_successes}")
        print(f"Total: {self.metrics.success_count}✓ {self.metrics.failure_count}✗")
        print("=" * 60)


# Global debugger instance
_debugger_instance: Optional[TranscriptionVisualDebugger] = None


def get_debugger(project_root: Optional[Path] = None) -> TranscriptionVisualDebugger:
    """Get global debugger instance"""
    global _debugger_instance
    if _debugger_instance is None:
        _debugger_instance = TranscriptionVisualDebugger(project_root)
    return _debugger_instance


if __name__ == "__main__":
    debugger = TranscriptionVisualDebugger()
    debugger.run()
