#!/usr/bin/env python3
"""
Lumina Chat Bubble Renderer - Visual Chat Representation

Renders chat bubbles for proximity messages in the Lumina ecosystem.
Provides visual representation of proximity-based communication.

Architectural Integration:
- Works with LuminaProximityChatService
- Programmatic API for UI integration
- Customizable bubble styling
- Position-aware rendering

Tags: #CHAT-BUBBLES #UI-RENDERING #LUMINA-ARCHITECTURE @LUMINA
"""

import sys
import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import threading
import time

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_proximity_chat_service import ChatBubble, get_proximity_chat_service
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("LuminaChatBubbles")


class ChatBubbleRenderer:
    """
    Chat Bubble Renderer

    Renders chat bubbles for proximity messages with customizable styling
    and position-aware display.
    """

    def __init__(self, parent_window=None, position: Tuple[int, int] = None):
        self.parent_window = parent_window
        self.default_position = position or (100, 100)

        # Active bubbles
        self.active_bubbles: Dict[str, tk.Toplevel] = {}
        self.bubble_data: Dict[str, ChatBubble] = {}

        # Styling
        self.default_style = {
            "bg_color": "#1E1E1E",
            "text_color": "#FFFFFF",
            "border_color": "#00D9FF",
            "font_family": "Consolas",
            "font_size": 12,
            "padding": 10,
            "border_width": 2,
            "corner_radius": 8
        }

        logger.info("✅ Chat Bubble Renderer initialized")

    def render_bubble(self, bubble: ChatBubble, style: Optional[Dict[str, Any]] = None):
        """
        Render a chat bubble

        Args:
            bubble: ChatBubble to render
            style: Optional custom styling
        """
        # Merge styles
        final_style = {**self.default_style, **(style or {})}

        # Create bubble window
        bubble_window = tk.Toplevel(self.parent_window if self.parent_window else None)
        bubble_window.overrideredirect(True)  # No window decorations
        bubble_window.attributes('-topmost', True)

        # Position
        position = bubble.position or self.default_position
        bubble_window.geometry(f"+{position[0]}+{position[1]}")

        # Make transparent background
        bubble_window.attributes('-alpha', 0.9)

        # Create frame for bubble
        bubble_frame = tk.Frame(
            bubble_window,
            bg=final_style["bg_color"],
            highlightbackground=final_style["border_color"],
            highlightthickness=final_style["border_width"],
            relief=tk.RAISED,
            bd=0
        )
        bubble_frame.pack(fill=tk.BOTH, expand=True, padx=final_style["padding"], pady=final_style["padding"])

        # Username label
        username_label = tk.Label(
            bubble_frame,
            text=bubble.username,
            bg=final_style["bg_color"],
            fg=final_style["border_color"],
            font=(final_style["font_family"], final_style["font_size"] - 2, "bold")
        )
        username_label.pack(anchor=tk.W, padx=5, pady=(0, 2))

        # Content label
        content_label = tk.Label(
            bubble_frame,
            text=bubble.content,
            bg=final_style["bg_color"],
            fg=final_style["text_color"],
            font=(final_style["font_family"], final_style["font_size"]),
            wraplength=300,
            justify=tk.LEFT
        )
        content_label.pack(anchor=tk.W, padx=5, pady=2)

        # Store bubble
        self.active_bubbles[bubble.message_id] = bubble_window
        self.bubble_data[bubble.message_id] = bubble

        # Auto-remove after duration
        duration = bubble.duration or 5.0
        bubble_window.after(int(duration * 1000), lambda: self.remove_bubble(bubble.message_id))

        logger.info(f"💬 Rendered bubble: {bubble.username} - {bubble.content[:30]}...")

    def remove_bubble(self, message_id: str):
        """Remove a chat bubble"""
        if message_id in self.active_bubbles:
            try:
                self.active_bubbles[message_id].destroy()
            except:
                pass
            del self.active_bubbles[message_id]
            if message_id in self.bubble_data:
                del self.bubble_data[message_id]

    def clear_all_bubbles(self):
        """Clear all active bubbles"""
        for message_id in list(self.active_bubbles.keys()):
            self.remove_bubble(message_id)

    def update_bubble_position(self, message_id: str, position: Tuple[int, int]):
        """Update bubble position"""
        if message_id in self.active_bubbles:
            self.active_bubbles[message_id].geometry(f"+{position[0]}+{position[1]}")


class LuminaChatBubbleManager:
    """
    Manager for chat bubbles in Lumina ecosystem

    Integrates with proximity chat service and manages bubble rendering.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.renderer = ChatBubbleRenderer()

        # Connect to proximity chat service
        self.chat_service = get_proximity_chat_service(self.project_root)
        self.chat_service.register_bubble_handler(self._handle_bubble)

        logger.info("✅ Lumina Chat Bubble Manager initialized")

    def _handle_bubble(self, bubble: ChatBubble):
        """Handle incoming bubble from chat service"""
        self.renderer.render_bubble(bubble)

    def render_custom_bubble(self, content: str, username: str = "Lumina", 
                           position: Optional[Tuple[int, int]] = None,
                           style: Optional[Dict[str, Any]] = None):
        """Render a custom bubble"""
        from lumina_proximity_chat_service import ChatBubble

        bubble = ChatBubble(
            message_id=f"custom_{int(time.time())}",
            user_id="system",
            username=username,
            content=content,
            timestamp=datetime.now(),
            position=position,
            duration=5.0,
            style=style
        )
        self.renderer.render_bubble(bubble, style)


def main():
    """Demo: Show chat bubbles"""
    root = tk.Tk()
    root.title("Lumina Chat Bubbles")
    root.geometry("800x600")
    root.withdraw()  # Hide main window

    # Create manager
    manager = LuminaChatBubbleManager()

    # Test bubbles
    def show_test_bubbles():
        time.sleep(1)
        manager.render_custom_bubble("Hello from Lumina!", "System", (100, 100))
        time.sleep(2)
        manager.render_custom_bubble("This is a proximity chat bubble", "User", (150, 200))
        time.sleep(2)
        manager.render_custom_bubble("Bubbles appear based on proximity", "Jarvis", (200, 300))

    # Start test in thread
    threading.Thread(target=show_test_bubbles, daemon=True).start()

    root.mainloop()


if __name__ == "__main__":


    main()