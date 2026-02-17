#!/usr/bin/env python3
"""
IMVA Mark Avatar Viewer - Visual Progression

Visual GUI viewer showing Mark I-VII to ULTRON avatars with increasing complexity,
mirroring ASUS Armoury Crate's virtual assistant progression system.

Features:
- Visual avatar representation for each Mark
- Progressive complexity visualization
- Skill level indicators
- Feature comparison
- Live status monitoring
- Interactive progression

Tags: #IMVA #AVATAR #VISUAL #ARMOURY_CRATE #ULTRON @JARVIS @LUMINA
"""

import sys
import time
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
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

try:
    import tkinter as tk
    from tkinter import ttk, Canvas
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = get_logger("IMVAMarkAvatarViewer")

from imva_mark_progression_viewer import IMVAMarkProgressionViewer, MarkLevel, MarkSpecification


class IMVAMarkAvatarViewer:
    """Visual GUI viewer for IMVA Mark progression"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.progression_viewer = IMVAMarkProgressionViewer(project_root)
        self.root = None
        self.canvas = None
        self.current_mark_index = 0
        self.marks = list(sorted(self.progression_viewer.marks.items(), key=lambda x: x[0].value))

    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def draw_mark_avatar(self, canvas: Canvas, mark: MarkSpecification, x: int, y: int, size: int = 120):
        """Draw a Mark avatar with visual complexity"""
        # Base circle (body)
        body_color = self.hex_to_rgb(mark.visual_style.get("color", "#DC143C"))
        glow_color = self.hex_to_rgb(mark.visual_style.get("glow", "#FFD700"))

        # Complexity affects size and detail
        complexity_scale = 0.7 + (mark.complexity_level / 10) * 0.3  # 0.7 to 1.0
        actual_size = int(size * complexity_scale)

        # Draw glow (outer ring)
        if mark.complexity_level >= 5:
            glow_width = max(2, mark.complexity_level - 3)
            canvas.create_oval(
                x - actual_size//2 - glow_width,
                y - actual_size//2 - glow_width,
                x + actual_size//2 + glow_width,
                y + actual_size//2 + glow_width,
                outline=f"#{glow_color[0]:02x}{glow_color[1]:02x}{glow_color[2]:02x}",
                width=glow_width
            )

        # Draw body
        canvas.create_oval(
            x - actual_size//2,
            y - actual_size//2,
            x + actual_size//2,
            y + actual_size//2,
            fill=f"#{body_color[0]:02x}{body_color[1]:02x}{body_color[2]:02x}",
            outline="black",
            width=2
        )

        # Draw arc reactor (center)
        reactor_size = actual_size // 4
        reactor_color = "#00D9FF"  # Cyan
        canvas.create_oval(
            x - reactor_size//2,
            y - reactor_size//2,
            x + reactor_size//2,
            y + reactor_size//2,
            fill=reactor_color,
            outline="white",
            width=1
        )

        # Draw complexity indicators (rings)
        if mark.complexity_level >= 4:
            for i in range(min(3, mark.complexity_level - 3)):
                ring_size = actual_size // 3 + i * 5
                canvas.create_oval(
                    x - ring_size//2,
                    y - ring_size//2,
                    x + ring_size//2,
                    y + ring_size//2,
                    outline=f"#{glow_color[0]:02x}{glow_color[1]:02x}{glow_color[2]:02x}",
                    width=1
                )

        # Draw skill level (stars or indicators)
        skill_y = y + actual_size//2 + 15
        for i in range(mark.skill_level):
            star_x = x - actual_size//2 + i * 8
            if star_x < x + actual_size//2:
                canvas.create_text(star_x, skill_y, text="★", fill="gold", font=("Arial", 8))

        # Mark name
        canvas.create_text(x, y + actual_size//2 + 30, text=mark.name, fill="white", font=("Arial", 10, "bold"))

        # Complexity/Skill text
        canvas.create_text(
            x, y + actual_size//2 + 45,
            text=f"C:{mark.complexity_level}/10 S:{mark.skill_level}/10",
            fill="lightgray",
            font=("Arial", 8)
        )

    def create_progression_view(self):
        """Create the progression view window"""
        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available")
            return

        self.root = tk.Tk()
        self.root.title("IMVA Mark Progression - Mark I to ULTRON")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a1a")

        # Header
        header = tk.Label(
            self.root,
            text="IRON MAN VIRTUAL ASSISTANT - MARK PROGRESSION",
            font=("Arial", 16, "bold"),
            bg="#1a1a1a",
            fg="#FFD700"
        )
        header.pack(pady=10)

        # Canvas for avatars
        canvas_frame = tk.Frame(self.root, bg="#1a1a1a")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas = Canvas(canvas_frame, bg="#2a2a2a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw all marks in progression
        self.draw_all_marks()

        # Controls
        controls = tk.Frame(self.root, bg="#1a1a1a")
        controls.pack(pady=10)

        # Navigation buttons
        prev_btn = tk.Button(
            controls,
            text="◀ Previous",
            command=self.show_previous_mark,
            bg="#333",
            fg="white",
            font=("Arial", 10)
        )
        prev_btn.pack(side=tk.LEFT, padx=5)

        next_btn = tk.Button(
            controls,
            text="Next ▶",
            command=self.show_next_mark,
            bg="#333",
            fg="white",
            font=("Arial", 10)
        )
        next_btn.pack(side=tk.LEFT, padx=5)

        # Info panel
        self.info_panel = tk.Text(
            self.root,
            height=8,
            bg="#2a2a2a",
            fg="white",
            font=("Arial", 9),
            wrap=tk.WORD
        )
        self.info_panel.pack(fill=tk.X, padx=20, pady=10)

        # Update info for current mark
        self.update_info_panel()

        # Auto-cycle
        self.auto_cycle()

    def draw_all_marks(self):
        """Draw all marks in progression view"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        # Calculate layout (2 rows, 4 columns)
        cols = 4
        rows = 2
        spacing_x = 280
        spacing_y = 350
        start_x = 150
        start_y = 100

        for idx, (level, mark) in enumerate(self.marks):
            col = idx % cols
            row = idx // cols

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y

            self.draw_mark_avatar(self.canvas, mark, x, y, size=100)

            # Status indicator
            status = self.progression_viewer.check_mark_status(mark)
            status_color = "green" if status.get("available") else "red"
            status_text = "●" if status.get("available") else "○"
            self.canvas.create_text(
                x, y - 70,
                text=status_text,
                fill=status_color,
                font=("Arial", 20)
            )

    def show_current_mark_detail(self):
        """Show detailed view of current mark"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        level, mark = self.marks[self.current_mark_index]

        # Draw large avatar in center
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2 - 50

        if center_x > 0 and center_y > 0:
            self.draw_mark_avatar(self.canvas, mark, center_x, center_y, size=200)

            # Draw progression line
            self.canvas.create_line(50, center_y, center_x - 120, center_y, fill="gray", width=2)
            self.canvas.create_line(center_x + 120, center_y, self.canvas.winfo_width() - 50, center_y, fill="gray", width=2)

            # Mark position indicator
            position = f"{self.current_mark_index + 1} of {len(self.marks)}"
            self.canvas.create_text(
                center_x, center_y + 150,
                text=position,
                fill="white",
                font=("Arial", 12)
            )

        self.update_info_panel()

    def show_previous_mark(self):
        """Show previous mark"""
        self.current_mark_index = (self.current_mark_index - 1) % len(self.marks)
        self.show_current_mark_detail()

    def show_next_mark(self):
        """Show next mark"""
        self.current_mark_index = (self.current_mark_index + 1) % len(self.marks)
        self.show_current_mark_detail()

    def update_info_panel(self):
        """Update info panel with current mark details"""
        if not self.info_panel:
            return

        level, mark = self.marks[self.current_mark_index]
        status = self.progression_viewer.check_mark_status(mark)

        info_text = f"""
{mark.name} - {mark.description}

Model: {mark.model_name}
System: {mark.system}
Endpoint: {mark.endpoint}

Complexity: {mark.complexity_level}/10 | Skill: {mark.skill_level}/10
Status: {'✅ Available' if status.get('available') else '❌ Not Available'}

Features: {', '.join(mark.features[:5])}
        """

        self.info_panel.delete(1.0, tk.END)
        self.info_panel.insert(1.0, info_text.strip())

    def auto_cycle(self):
        """Auto-cycle through marks"""
        if self.root and self.canvas:
            # Switch between overview and detail view
            if hasattr(self, '_show_detail') and self._show_detail:
                self.show_current_mark_detail()
            else:
                self.draw_all_marks()

            self.root.after(5000, self.auto_cycle)  # Update every 5 seconds

    def run(self):
        """Run the viewer"""
        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available - cannot display GUI")
            logger.info("Run with --text-only for text output")
            return

        self.create_progression_view()
        self.root.mainloop()


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="IMVA Mark Avatar Viewer")
    parser.add_argument("--gui", action="store_true", help="Show GUI viewer")
    parser.add_argument("--text-only", action="store_true", help="Text output only")

    args = parser.parse_args()

    viewer = IMVAMarkAvatarViewer(project_root)

    if args.gui or not args.text_only:
        viewer.run()
    else:
        # Text output
        viewer.progression_viewer.display_progression()


if __name__ == "__main__":


    main()