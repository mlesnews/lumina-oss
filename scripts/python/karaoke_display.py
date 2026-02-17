#!/usr/bin/env python3
"""
Karaoke Display - Shows lyrics on screen karaoke-style

Displays lyrics on screen with highlighting as they're sung.

Tags: #KARAOKE #LYRICS #DISPLAY #GUI #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from tkinter import Tk, Label, Canvas, font, Text

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

logger = get_logger("KaraokeDisplay")


class KaraokeDisplay:
    """
    Karaoke-style lyrics display

    Shows lyrics on screen with highlighting as they're sung.
    """

    def __init__(self):
        """Initialize karaoke display"""
        self.root = None
        self.jarvis_label = None
        self.wanda_label = None
        self.title_label = None
        self.canvas = None
        self.ball = None
        self.running = False
        self.current_lyrics = ("", "")
        self.ball_position = 0  # 0.0 to 1.0 across the lyrics
        self.ball_animation_id = None

        logger.info("✅ Karaoke Display initialized")

    def _create_window(self):
        """Create karaoke display window"""
        self.root = Tk()
        self.root.title("Danny Boy - Karaoke")
        self.root.configure(bg='black')

        # Make window fullscreen or large
        self.root.attributes('-fullscreen', False)
        self.root.geometry('1200x800')
        self.root.configure(bg='black')

        # Title
        title_font = font.Font(family='Arial', size=24, weight='bold')
        self.title_label = Label(
            self.root,
            text="DANNY BOY - ACAPELLA DUET",
            font=title_font,
            fg='white',
            bg='black'
        )
        self.title_label.pack(pady=20)

        # JARVIS (Tenor 1 - Higher) label
        jarvis_font = font.Font(family='Arial', size=18, weight='bold')
        self.jarvis_label = Label(
            self.root,
            text="JARVIS (Tenor 1 - Higher):",
            font=jarvis_font,
            fg='cyan',
            bg='black',
            wraplength=1100,
            justify='center'
        )
        self.jarvis_label.pack(pady=10)

        # Wanda (Tenor 2 - Lower) label
        wanda_font = font.Font(family='Arial', size=18, weight='bold')
        self.wanda_label = Label(
            self.root,
            text="Wanda (Tenor 2 - Lower):",
            font=wanda_font,
            fg='magenta',
            bg='black',
            wraplength=1100,
            justify='center'
        )
        self.wanda_label.pack(pady=10)

        # Canvas for bouncing ball
        self.canvas = Canvas(
            self.root,
            bg='black',
            height=100,
            highlightthickness=0
        )
        self.canvas.pack(fill='x', padx=50, pady=20)

        # Create bouncing ball (initially hidden)
        self.ball = self.canvas.create_oval(0, 0, 0, 0, fill='yellow', outline='yellow', width=0)

        # Instructions
        instruction_font = font.Font(family='Arial', size=12)
        instruction_label = Label(
            self.root,
            text="Press ESC to close",
            font=instruction_font,
            fg='gray',
            bg='black'
        )
        instruction_label.pack(pady=20)

        # Bind ESC to close
        self.root.bind('<Escape>', lambda e: self.close())

        logger.info("✅ Karaoke window created")

    def show_lyrics(self, jarvis_lyrics: str, wanda_lyrics: str, highlight: str = "both", 
                   ball_progress: float = 0.0, duration: float = 4.0, current_word_index: int = -1):
        """
        Show lyrics on screen with bouncing ball and word-by-word highlighting

        Args:
            jarvis_lyrics: JARVIS's lyrics (Tenor 1)
            wanda_lyrics: Wanda's lyrics (Tenor 2)
            highlight: "jarvis", "wanda", or "both"
            ball_progress: Progress of ball (0.0 to 1.0)
            duration: Duration of phrase in seconds (for ball animation)
            current_word_index: Which word is currently being sung (-1 = none, 0+ = word index)
        """
        if not self.root:
            self._create_window()

        self.current_lyrics = (jarvis_lyrics, wanda_lyrics)

        # Split lyrics into words for word-by-word highlighting
        jarvis_words = jarvis_lyrics.split() if jarvis_lyrics else []
        wanda_words = wanda_lyrics.split() if wanda_lyrics else []

        # Format JARVIS lyrics with word highlighting (real karaoke style)
        jarvis_display = "JARVIS (Tenor 1 - Higher): "
        if highlight in ["jarvis", "both"] and current_word_index >= 0 and current_word_index < len(jarvis_words):
            # Build text with visual highlighting - current word in UPPERCASE and bold markers
            for i, word in enumerate(jarvis_words):
                if i == current_word_index:
                    jarvis_display += f">>> {word.upper()} <<< "  # Current word highlighted
                elif i < current_word_index:
                    jarvis_display += f"{word} "  # Past words (normal)
                else:
                    jarvis_display += f"{word} "  # Future words (normal)
        else:
            jarvis_display = f"JARVIS (Tenor 1 - Higher): {jarvis_lyrics}"

        # Format Wanda lyrics with word highlighting (real karaoke style)
        wanda_display = "Wanda (Tenor 2 - Lower): "
        if highlight in ["wanda", "both"] and current_word_index >= 0 and current_word_index < len(wanda_words):
            for i, word in enumerate(wanda_words):
                if i == current_word_index:
                    wanda_display += f">>> {word.upper()} <<< "  # Current word highlighted
                elif i < current_word_index:
                    wanda_display += f"{word} "  # Past words (normal)
                else:
                    wanda_display += f"{word} "  # Future words (normal)
        else:
            wanda_display = f"Wanda (Tenor 2 - Lower): {wanda_lyrics}"

        # Update JARVIS lyrics with color coding
        if highlight in ["jarvis", "both"]:
            # Use bright yellow when actively singing a word, cyan otherwise
            color = 'yellow' if current_word_index >= 0 else 'cyan'
            self.jarvis_label.config(
                text=jarvis_display,
                fg=color,
                font=('Arial', 18, 'bold' if current_word_index >= 0 else 'normal')
            )
        else:
            self.jarvis_label.config(
                text=f"JARVIS (Tenor 1 - Higher): {jarvis_lyrics}",
                fg='cyan',
                font=('Arial', 18, 'normal')
            )

        # Update Wanda lyrics with color coding
        if highlight in ["wanda", "both"]:
            # Use bright yellow when actively singing a word, magenta otherwise
            color = 'yellow' if current_word_index >= 0 else 'magenta'
            self.wanda_label.config(
                text=wanda_display,
                fg=color,
                font=('Arial', 18, 'bold' if current_word_index >= 0 else 'normal')
            )
        else:
            self.wanda_label.config(
                text=f"Wanda (Tenor 2 - Lower): {wanda_lyrics}",
                fg='magenta',
                font=('Arial', 18, 'normal')
            )

        # Update bouncing ball position (sync with word position)
        self._update_ball_position(ball_progress, jarvis_words if jarvis_words else wanda_words, current_word_index)

        # Update display
        if self.root:
            self.root.update()

    def _update_ball_position(self, progress: float, words: List[str] = None, current_word_index: int = -1):
        """Update bouncing ball position (0.0 to 1.0) with word-based positioning"""
        if not self.canvas or not self.ball:
            return

        self.ball_position = max(0.0, min(1.0, progress))

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized, schedule update
            if self.root:
                self.root.after(10, lambda: self._update_ball_position(progress, words, current_word_index))
            return

        # Ball size
        ball_radius = 15

        # Calculate ball position
        # If we have words and current word index, position ball over that word
        if words and current_word_index >= 0 and current_word_index < len(words):
            # Position ball over the current word (approximate based on word index)
            word_progress = current_word_index / max(1, len(words) - 1)
            x = 50 + (canvas_width - 100) * word_progress
        else:
            # Use progress-based positioning
            x = 50 + (canvas_width - 100) * self.ball_position

        y_center = canvas_height / 2

        # Bouncing effect (sine wave for bounce - more bounce when on a word)
        bounce_height = 25 if current_word_index >= 0 else 15
        bounce_freq = 6 if current_word_index >= 0 else 4
        bounce = bounce_height * abs(np.sin(self.ball_position * np.pi * bounce_freq)) if hasattr(self, 'np') else 0
        y = y_center - bounce

        # Update ball position
        self.canvas.coords(
            self.ball,
            x - ball_radius,
            y - ball_radius,
            x + ball_radius,
            y + ball_radius
        )

        # Make ball visible
        self.canvas.itemconfig(self.ball, state='normal')

    def animate_ball(self, duration: float, lyrics: str = "", start_progress: float = 0.0, end_progress: float = 1.0):
        """
        Animate bouncing ball across lyrics word-by-word (like real karaoke)

        Args:
            duration: Animation duration in seconds
            lyrics: Lyrics text to animate word-by-word
            start_progress: Starting position (0.0 to 1.0)
            end_progress: Ending position (0.0 to 1.0)
        """
        if not self.canvas:
            return

        import numpy as np
        self.np = np  # Store for bounce calculation

        # Split lyrics into words for word-by-word animation
        words = lyrics.split() if lyrics else []
        num_words = len(words)

        if num_words == 0:
            # Fallback to smooth progress animation
            self._animate_ball_smooth(duration, start_progress, end_progress)
            return

        # Calculate timing per word (distribute duration evenly across words)
        time_per_word = duration / num_words
        start_time = time.time()
        current_word_index = 0

        def animate_word():
            if not self.running or not self.canvas:
                return

            elapsed = time.time() - start_time
            current_time_in_phrase = elapsed % duration if duration > 0 else 0

            # Calculate which word we're on
            current_word_index = min(int(current_time_in_phrase / time_per_word), num_words - 1)

            # Calculate progress within current word
            time_in_word = current_time_in_phrase % time_per_word
            word_progress = time_in_word / time_per_word if time_per_word > 0 else 0

            # Overall progress (0.0 to 1.0)
            overall_progress = start_progress + (end_progress - start_progress) * (elapsed / duration) if duration > 0 else start_progress
            overall_progress = min(1.0, max(0.0, overall_progress))

            # Update display with current word highlighted
            if self.current_lyrics[0] or self.current_lyrics[1]:
                # Use the first lyrics that has words
                active_lyrics = self.current_lyrics[0] if self.current_lyrics[0] else self.current_lyrics[1]
                active_words = active_lyrics.split() if active_lyrics else []
                if current_word_index < len(active_words):
                    # Update with word highlighting
                    self.show_lyrics(
                        self.current_lyrics[0],
                        self.current_lyrics[1],
                        highlight="both",
                        ball_progress=overall_progress,
                        duration=duration,
                        current_word_index=current_word_index
                    )

            if elapsed < duration:
                # Continue animation
                self.ball_animation_id = self.root.after(16, animate_word)  # ~60fps
            else:
                # Animation complete
                self.ball_animation_id = None
                # Reset word index
                self.show_lyrics(
                    self.current_lyrics[0],
                    self.current_lyrics[1],
                    highlight="none",
                    ball_progress=1.0,
                    duration=0,
                    current_word_index=-1
                )

        # Start animation
        if self.root:
            self.root.after(0, animate_word)

    def _animate_ball_smooth(self, duration: float, start_progress: float = 0.0, end_progress: float = 1.0):
        """Fallback smooth animation if no words available"""
        if not self.canvas:
            return

        import numpy as np
        self.np = np

        start_time = time.time()
        total_progress = end_progress - start_progress

        def animate():
            if not self.running or not self.canvas:
                return

            elapsed = time.time() - start_time
            if elapsed >= duration:
                progress = end_progress
            else:
                t = elapsed / duration
                if t < 0.5:
                    eased = 4 * t * t * t
                else:
                    eased = 1 - pow(-2 * t + 2, 3) / 2
                progress = start_progress + total_progress * eased

            self._update_ball_position(progress)

            if elapsed < duration:
                self.ball_animation_id = self.root.after(16, animate)
            else:
                self.ball_animation_id = None

        if self.root:
            self.root.after(0, animate)

    def clear(self):
        """Clear lyrics display"""
        if self.jarvis_label:
            self.jarvis_label.config(text="JARVIS (Tenor 1 - Higher):")
        if self.wanda_label:
            self.wanda_label.config(text="Wanda (Tenor 2 - Lower):")
        if self.root:
            self.root.update()

    def start(self):
        """Start karaoke display"""
        # CRITICAL: Don't create window here - window should be created in main thread
        # This method is just for compatibility - actual window creation happens in main()
        if not self.root:
            # Don't create here - will be created in main thread
            logger.debug("Karaoke display not yet created - will be created in main thread")
            return

        self.running = True
        logger.info("✅ Karaoke display ready (main thread)")

    def close(self):
        """Close karaoke display"""
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
        logger.info("✅ Karaoke display closed")


def main():
    """Test karaoke display"""
    display = KaraokeDisplay()
    display.start()

    # Test display
    time.sleep(1)
    display.show_lyrics(
        "Oh Danny boy, the pipes, the pipes are calling",
        "Oh Danny boy, the pipes, the pipes are calling",
        highlight="both"
    )

    time.sleep(5)
    display.close()


if __name__ == "__main__":


    main()