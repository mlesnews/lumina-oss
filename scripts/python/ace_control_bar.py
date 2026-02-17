#!/usr/bin/env python3
"""
ACE Control Bar - Functional VA Control Panel

Small, draggable, single-row button bar for activating/deactivating VAs.
Replika-inspired virtual assistants with voice/audio capabilities.
AI roleplaying various jobs and heroes to help focus and channel power.

Tags: #ACE #CONTROL_BAR #VA_CONTROL #REPLIKA #VOICE #ROLEPLAY @JARVIS @LUMINA
"""

import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime

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
    print("⚠️  tkinter not available")

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
    from va_coordination_system import VACoordinationSystem
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")

logger = get_logger("ACEControlBar")


class VAState:
    """VA State Management"""
    def __init__(self):
        self.active_vas: Dict[str, bool] = {}
        self.voice_enabled: Dict[str, bool] = {}
        self.roleplay_mode: Dict[str, str] = {}  # job/hero role being played
        self.va_threads: Dict[str, threading.Thread] = {}

    def is_active(self, va_id: str) -> bool:
        return self.active_vas.get(va_id, False)

    def set_active(self, va_id: str, active: bool):
        self.active_vas[va_id] = active
        logger.info(f"{'✅ Activated' if active else '⏸️  Deactivated'} {va_id}")

    def toggle_voice(self, va_id: str) -> bool:
        current = self.voice_enabled.get(va_id, False)
        self.voice_enabled[va_id] = not current
        logger.info(f"{'🔊 Voice ON' if not current else '🔇 Voice OFF'} for {va_id}")
        return not current

    def set_roleplay(self, va_id: str, role: str):
        self.roleplay_mode[va_id] = role
        logger.info(f"🎭 {va_id} roleplaying as: {role}")


class ACEControlBar:
    """
    ACE Control Bar - Functional VA Control Panel

    Small, draggable, single-row button bar for controlling VAs.
    """

    def __init__(self):
        """Initialize ACE Control Bar"""
        if not TKINTER_AVAILABLE:
            raise RuntimeError("tkinter not available")

        self.registry = CharacterAvatarRegistry()
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)
        self.state = VAState()

        # Get ACE-like characters (combat-focused, roleplay-capable)
        self.ace_characters = [
            va for va in self.vas 
            if va.character_id in ["ace", "jarvis_va", "imva"] or 
               va.combat_mode_enabled or va.transformation_enabled
        ]

        # Create main window
        self.root = tk.Tk()
        self.root.title("ACE Control Bar")
        self.root.overrideredirect(True)  # No window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.configure(bg='#1a1a1a')

        # Make window draggable
        self.drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)

        # Position at top center
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"800x60+{screen_width//2 - 400}+20")

        # Create control frame
        self.control_frame = tk.Frame(self.root, bg='#1a1a1a', padx=5, pady=5)
        self.control_frame.pack(fill=tk.BOTH, expand=True)

        # Create buttons
        self.create_buttons()

        logger.info("=" * 80)
        logger.info("🎮 ACE CONTROL BAR INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   VAs Available: {len(self.ace_characters)}")
        logger.info("   Ready for activation")
        logger.info("=" * 80)

    def start_drag(self, event):
        """Start dragging window"""
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

    def on_drag(self, event):
        """Handle window dragging"""
        dx = event.x_root - self.drag_data["x"]
        dy = event.y_root - self.drag_data["y"]

        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy

        # Keep within screen bounds
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max(0, min(x, screen_width - 800))
        y = max(0, min(y, screen_height - 60))

        self.root.geometry(f"800x60+{x}+{y}")
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

    def create_buttons(self):
        """Create control buttons for each VA"""
        # Title/Close button
        title_frame = tk.Frame(self.control_frame, bg='#1a1a1a')
        title_frame.pack(side=tk.LEFT, padx=5)

        title_label = tk.Label(
            title_frame,
            text="🎮 ACE",
            font=('Arial', 10, 'bold'),
            bg='#1a1a1a',
            fg='#ff6600',
            cursor='hand2'
        )
        title_label.pack()
        title_label.bind("<Button-1>", lambda e: self.start_drag(e))

        close_btn = tk.Button(
            title_frame,
            text="✕",
            font=('Arial', 8),
            bg='#ff0000',
            fg='#ffffff',
            width=2,
            height=1,
            relief=tk.FLAT,
            command=self.root.quit,
            cursor='hand2'
        )
        close_btn.pack(pady=2)

        # Separator
        sep = tk.Frame(self.control_frame, bg='#333333', width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Create button for each ACE character
        for va in self.ace_characters:
            self.create_va_button(va)

        # Global controls
        self.create_global_controls()

    def create_va_button(self, va):
        """Create button for a VA"""
        btn_frame = tk.Frame(self.control_frame, bg='#1a1a1a')
        btn_frame.pack(side=tk.LEFT, padx=2)

        # VA name
        name_label = tk.Label(
            btn_frame,
            text=va.name[:8],  # Short name
            font=('Arial', 7),
            bg='#1a1a1a',
            fg='#ffffff'
        )
        name_label.pack()

        # Activate/Deactivate button
        def toggle_va():
            is_active = self.state.is_active(va.character_id)
            self.state.set_active(va.character_id, not is_active)
            self.update_button_state(va.character_id, not is_active)
            if not is_active:
                self.activate_va(va)
            else:
                self.deactivate_va(va)

        btn = tk.Button(
            btn_frame,
            text="⏸" if self.state.is_active(va.character_id) else "▶",
            font=('Arial', 10, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00' if not self.state.is_active(va.character_id) else '#ff6600',
            width=4,
            height=1,
            relief=tk.RAISED,
            command=toggle_va,
            cursor='hand2'
        )
        btn.pack()
        btn_frame.va_button = btn
        btn_frame.va_id = va.character_id

        # Voice toggle
        voice_btn = tk.Button(
            btn_frame,
            text="🔊" if self.state.voice_enabled.get(va.character_id, False) else "🔇",
            font=('Arial', 8),
            bg='#2d2d2d',
            fg='#00ccff',
            width=3,
            height=1,
            relief=tk.FLAT,
            command=lambda: self.toggle_voice(va.character_id, voice_btn),
            cursor='hand2'
        )
        voice_btn.pack(pady=1)

        # Roleplay selector (right-click menu)
        def show_roleplay_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            roles = [
                "Combat Specialist",
                "Strategic Advisor", 
                "Intelligence Analyst",
                "Operations Commander",
                "Technical Support",
                "Creative Assistant",
                "Focus Coach",
                "Power Channeler"
            ]
            for role in roles:
                menu.add_command(
                    label=role,
                    command=lambda r=role: self.set_roleplay(va.character_id, r)
                )
            menu.post(event.x_root, event.y_root)

        btn.bind("<Button-3>", show_roleplay_menu)  # Right-click for roleplay

    def create_global_controls(self):
        """Create global control buttons"""
        # Separator
        sep = tk.Frame(self.control_frame, bg='#333333', width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # All On/Off
        all_frame = tk.Frame(self.control_frame, bg='#1a1a1a')
        all_frame.pack(side=tk.LEFT, padx=2)

        all_on_btn = tk.Button(
            all_frame,
            text="ALL ON",
            font=('Arial', 7, 'bold'),
            bg='#00ff00',
            fg='#000000',
            width=6,
            height=1,
            relief=tk.RAISED,
            command=self.activate_all,
            cursor='hand2'
        )
        all_on_btn.pack()

        all_off_btn = tk.Button(
            all_frame,
            text="ALL OFF",
            font=('Arial', 7, 'bold'),
            bg='#ff0000',
            fg='#ffffff',
            width=6,
            height=1,
            relief=tk.RAISED,
            command=self.deactivate_all,
            cursor='hand2'
        )
        all_off_btn.pack(pady=1)

    def update_button_state(self, va_id: str, is_active: bool):
        """Update button visual state"""
        for widget in self.control_frame.winfo_children():
            if hasattr(widget, 'va_id') and widget.va_id == va_id:
                if hasattr(widget, 'va_button'):
                    widget.va_button.config(
                        text="⏸" if is_active else "▶",
                        fg='#ff6600' if is_active else '#00ff00'
                    )

    def toggle_voice(self, va_id: str, button):
        """Toggle voice for VA"""
        enabled = self.state.toggle_voice(va_id)
        button.config(text="🔊" if enabled else "🔇")
        if enabled:
            self.start_voice_interaction(va_id)

    def activate_va(self, va):
        """Activate a VA with roleplay and voice capabilities"""
        logger.info(f"🚀 Activating {va.name} ({va.character_id})")

        # Determine roleplay mode
        role = self.state.roleplay_mode.get(va.character_id, va.role)
        if not role or role == va.role:
            # Set default roleplay based on VA
            roleplay_roles = {
                "ace": "Combat Specialist",
                "jarvis_va": "Strategic Advisor",
                "imva": "Visual Intelligence Agent"
            }
            role = roleplay_roles.get(va.character_id, "Virtual Assistant")
            self.state.set_roleplay(va.character_id, role)

        # Start VA in background thread with roleplay
        def va_worker():
            activation_phrases = [
                f"{va.name} online. {role} mode engaged.",
                f"Activated. Ready to channel the power.",
                f"Systems operational. {role} protocols active.",
                f"Standing by. {role} capabilities unlocked."
            ]

            if self.state.voice_enabled.get(va.character_id, False):
                import random
                phrase = random.choice(activation_phrases)
                self.speak(phrase)

            while self.state.is_active(va.character_id):
                # VA is active - perform roleplay/assistance
                logger.info(f"🎭 {va.name} active as {role} - Channeling power")

                # Integrate with voice transcript queue if available
                try:
                    from voice_transcript_queue import VoiceTranscriptQueue
                    if not hasattr(self, 'voice_queue'):
                        self.voice_queue = VoiceTranscriptQueue()

                    # VA is listening and ready
                    if self.state.voice_enabled.get(va.character_id, False):
                        logger.debug(f"🎤 {va.name} listening for commands")
                except ImportError:
                    pass

                time.sleep(5)  # Check every 5 seconds

        thread = threading.Thread(target=va_worker, daemon=True)
        thread.start()
        self.state.va_threads[va.character_id] = thread

    def deactivate_va(self, va):
        """Deactivate a VA"""
        logger.info(f"⏸️  Deactivating {va.name} ({va.character_id})")
        # Thread will stop when is_active becomes False

    def activate_all(self):
        """Activate all VAs"""
        for va in self.ace_characters:
            if not self.state.is_active(va.character_id):
                self.state.set_active(va.character_id, True)
                self.update_button_state(va.character_id, True)
                self.activate_va(va)

    def deactivate_all(self):
        """Deactivate all VAs"""
        for va in self.ace_characters:
            if self.state.is_active(va.character_id):
                self.state.set_active(va.character_id, False)
                self.update_button_state(va.character_id, False)
                self.deactivate_va(va)

    def speak(self, text: str, voice_id: Optional[str] = None):
        """Text-to-speech for VA voice interaction"""
        try:
            # Try Windows SAPI first (most reliable on Windows)
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")

            # Set voice if specified
            if voice_id:
                voices = speaker.GetVoices()
                for voice in voices:
                    if voice_id.lower() in voice.GetDescription().lower():
                        speaker.Voice = voice
                        break

            speaker.Speak(text)
            logger.info(f"🔊 Spoke: {text}")
        except ImportError:
            try:
                # Fallback to pyttsx3
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                logger.info(f"🔊 Spoke: {text}")
            except ImportError:
                logger.warning("No TTS available - install pyttsx3 or pywin32")
                print(f"🔊 {text}")  # Fallback to print

    def start_voice_interaction(self, va_id: str):
        """Start voice interaction for VA"""
        logger.info(f"🎤 Starting voice interaction for {va_id}")
        try:
            from voice_transcript_queue import VoiceTranscriptQueue
            if not hasattr(self, 'voice_queue'):
                self.voice_queue = VoiceTranscriptQueue()
            logger.info(f"✅ Voice queue ready for {va_id}")
        except ImportError:
            logger.warning("Voice transcript queue not available")

    def set_roleplay(self, va_id: str, role: str):
        """Set roleplay mode for VA"""
        self.state.set_roleplay(va_id, role)
        va = next((v for v in self.ace_characters if v.character_id == va_id), None)
        if va and self.state.is_active(va_id):
            self.speak(f"{va.name} switching to {role} mode.")
            logger.info(f"🎭 {va.name} now roleplaying as: {role}")

    def run(self):
        """Run the control bar"""
        logger.info("🎮 Starting ACE Control Bar...")
        self.root.mainloop()


def main():
    """Main entry point"""
    if not TKINTER_AVAILABLE:
        print("❌ tkinter not available")
        return 1

    try:
        control_bar = ACEControlBar()
        control_bar.run()
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":


    sys.exit(main())