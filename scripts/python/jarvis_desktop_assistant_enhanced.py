#!/usr/bin/env python3
"""
JARVIS Desktop Assistant Enhanced - With Role Management & Interactive Features

Enhanced version of JARVIS desktop assistant with:
- Role switching (JARVIS, Ultron, Ultimate Iron Man)
- Interactive command interface
- Iron Legion expert integration
- Right-click context menu
- Status display

Tags: #JARVIS #ENHANCED #ROLE_MANAGEMENT #INTERACTIVE @JARVIS @LUMINA
"""

import sys
import time
import threading
import random
import math
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

logger = get_logger("JARVISDesktopEnhanced")

# Import enhanced core
try:
    from jarvis_enhanced_core import JarvisEnhancedCore, JarvisRole
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    logger.warning("⚠️  Enhanced core not available - limited functionality")


class JARVISDesktopAssistantEnhanced:
    """
    Enhanced JARVIS Desktop Assistant

    Features:
    - Role switching (JARVIS, Ultron, Ultimate)
    - Interactive command interface
    - Right-click context menu
    - Status display
    - Iron Legion integration
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Enhanced JARVIS Desktop Assistant"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        if not TKINTER_AVAILABLE:
            logger.error("❌ tkinter not available")
            raise ImportError("tkinter is required")

        # Enhanced core
        self.core = None
        if CORE_AVAILABLE:
            try:
                self.core = JarvisEnhancedCore(project_root=project_root)
                logger.info("✅ Enhanced core initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize enhanced core: {e}")

        # Window properties
        self.window_size = 120
        self.root = None
        self.canvas = None
        self.status_label = None
        self.context_menu = None

        # Position
        screen_width = 1920
        screen_height = 1080
        self.x = random.randint(100, screen_width - 220)
        self.y = random.randint(100, screen_height - 220)

        # Animation
        self.animation_running = False
        self.eye_glow = 0.0
        self.eye_dir = 1
        self.arc_reactor_pulse = 0.0

        # Role-based colors
        self.role_colors = {
            JarvisRole.JARVIS: {
                "primary": "#00ccff",  # JARVIS blue
                "secondary": "#006699",
                "glow": "#00ffff",
                "outline": "#ffffff"
            },
            JarvisRole.ULTRON: {
                "primary": "#ff0000",  # Ultron red
                "secondary": "#990000",
                "glow": "#ff3333",
                "outline": "#ffffff"
            },
            JarvisRole.ULTIMATE: {
                "primary": "#C0C0C0",  # Ultimate silver
                "secondary": "#808080",
                "glow": "#00D9FF",  # Cyan
                "outline": "#ffffff"
            }
        }

        # Current colors (default to JARVIS)
        self.colors = self.role_colors.get(JarvisRole.JARVIS, self.role_colors[JarvisRole.JARVIS])

        # Register with Iron Man Assistant Manager
        self.manager = None
        try:
            from iron_man_assistant_manager import IronManAssistantManager
            self.manager = IronManAssistantManager(project_root=project_root)
        except ImportError:
            logger.debug("Iron Man Assistant Manager not available")
        except Exception as e:
            logger.debug(f"Manager error: {e}")

        logger.info("✅ JARVIS Desktop Assistant Enhanced initialized")

    def _update_colors_for_role(self):
        """Update colors based on current role"""
        if self.core:
            current_role = self.core.get_current_role()
            self.colors = self.role_colors.get(current_role, self.role_colors[JarvisRole.JARVIS])
        else:
            self.colors = self.role_colors[JarvisRole.JARVIS]

    def create_window(self):
        """Create enhanced window with interactive features"""
        self.root = tk.Tk()
        self.root.title("JARVIS Enhanced")

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Update position
        self.x = max(50, min(int(self.x), screen_width - self.window_size - 50))
        self.y = max(50, min(int(self.y), screen_height - self.window_size - 50))

        # Position window
        self.root.geometry(f"{self.window_size}x{self.window_size}+{self.x}+{self.y}")

        # Window properties
        self.root.configure(bg='black')
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)

        # Transparency (Windows)
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = self.root.winfo_id()
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x80000
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)

                LWA_COLORKEY = 0x1
                LWA_ALPHA = 0x2
                alpha_value = 255
                ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, alpha_value, LWA_COLORKEY | LWA_ALPHA)
            except Exception:
                self.root.attributes('-transparentcolor', 'black')
        else:
            self.root.attributes('-transparentcolor', 'black')

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.window_size,
            height=self.window_size,
            bg='black',
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack()

        # Activate with manager
        if self.manager:
            import os
            activated = self.manager.activate("jarvis", os.getpid(), bypass_magic_words=False)
            if activated:
                logger.info("✅ Registered with Iron Man Assistant Manager")
            else:
                logger.warning("⚠️  Magic words not detected")
                logger.warning("   Say 'Jarvis Iron Legion' to activate")
                self.root.quit()
                return

        # Bind events
        self.canvas.bind('<Button-1>', self._on_left_click)
        self.canvas.bind('<Button-3>', self._on_right_click)  # Right-click
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<Double-Button-1>', self._on_double_click)

        # Update colors for current role
        self._update_colors_for_role()

        # Draw JARVIS
        self._draw_jarvis()

        # Start animation
        self.start_animation()

        logger.info("✅ JARVIS Desktop Assistant Enhanced window created")

    def _draw_jarvis(self):
        """Draw JARVIS with role-based appearance"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        center_x = self.window_size // 2
        center_y = self.window_size // 2

        # Update colors for current role
        self._update_colors_for_role()

        # Helmet/Head
        head_radius = 35
        self.canvas.create_oval(
            center_x - head_radius,
            center_y - head_radius - 10,
            center_x + head_radius,
            center_y + head_radius - 10,
            fill=self.colors["primary"],
            outline=self.colors["outline"],
            width=2
        )

        # Eyes (glowing)
        eye_y = center_y - 5
        eye_size = 8 + int(self.eye_glow * 3)
        eye_color = self.colors["glow"] if self.eye_glow > 0.5 else self.colors["primary"]

        # Left eye
        self.canvas.create_oval(
            center_x - 20 - eye_size // 2,
            eye_y - eye_size // 2,
            center_x - 20 + eye_size // 2,
            eye_y + eye_size // 2,
            fill=eye_color,
            outline=self.colors["outline"],
            width=1
        )

        # Right eye
        self.canvas.create_oval(
            center_x + 20 - eye_size // 2,
            eye_y - eye_size // 2,
            center_x + 20 + eye_size // 2,
            eye_y + eye_size // 2,
            fill=eye_color,
            outline=self.colors["outline"],
            width=1
        )

        # Arc Reactor
        reactor_y = center_y + 25
        reactor_radius = 12 + int(self.arc_reactor_pulse * 3)
        reactor_color = self.colors["glow"] if self.arc_reactor_pulse > 0.5 else self.colors["primary"]

        self.canvas.create_oval(
            center_x - reactor_radius,
            reactor_y - reactor_radius // 2,
            center_x + reactor_radius,
            reactor_y + reactor_radius // 2,
            fill=reactor_color,
            outline=self.colors["outline"],
            width=2
        )

        # Inner reactor core
        inner_radius = reactor_radius // 2
        self.canvas.create_oval(
            center_x - inner_radius,
            reactor_y - inner_radius // 2,
            center_x + inner_radius,
            reactor_y + inner_radius // 2,
            fill="#ffffff",
            outline=reactor_color,
            width=1
        )

        # Role indicator (small dot in corner)
        if self.core:
            role = self.core.get_current_role()
            role_indicator = {
                JarvisRole.JARVIS: "J",
                JarvisRole.ULTRON: "U",
                JarvisRole.ULTIMATE: "★"
            }
            indicator_text = role_indicator.get(role, "?")
            self.canvas.create_text(
                10, 10,
                text=indicator_text,
                fill=self.colors["glow"],
                font=("Arial", 8, "bold")
            )

    def _on_left_click(self, event):
        """Handle left click - toggle eye glow"""
        self.eye_glow = 1.0 if self.eye_glow < 0.5 else 0.0
        self._draw_jarvis()

    def _on_double_click(self, event):
        """Handle double click - show command dialog"""
        self._show_command_dialog()

    def _on_right_click(self, event):
        """Handle right click - show context menu"""
        self._show_context_menu(event.x_root, event.y_root)

    def _on_drag(self, event):
        """Handle drag - move window"""
        self.root.geometry(f"+{event.x_root - self.window_size // 2}+{event.y_root - self.window_size // 2}")

    def _show_context_menu(self, x, y):
        """Show right-click context menu"""
        menu = tk.Menu(self.root, tearoff=0)

        # Role switching
        if self.core:
            menu.add_command(label="Switch Role...", command=self._show_role_switch_dialog)
            menu.add_separator()
            current_role = self.core.get_current_role()
            menu.add_command(label=f"Current: {current_role.value.title()}", state="disabled")

        # Commands
        menu.add_separator()
        menu.add_command(label="Command...", command=self._show_command_dialog)
        menu.add_command(label="Status", command=self._show_status)
        menu.add_command(label="Help", command=self._show_help)

        # System
        menu.add_separator()
        menu.add_command(label="Exit", command=self.root.quit)

        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _show_role_switch_dialog(self):
        """Show role switching dialog"""
        if not self.core:
            messagebox.showinfo("Role Switch", "Enhanced core not available")
            return

        roles = [r.value for r in JarvisRole]
        current_role = self.core.get_current_role().value

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Switch JARVIS Role")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Select Role:", font=("Arial", 10, "bold")).pack(pady=10)

        role_var = tk.StringVar(value=current_role)
        for role in roles:
            rb = tk.Radiobutton(
                dialog,
                text=role.title(),
                variable=role_var,
                value=role,
                font=("Arial", 9)
            )
            rb.pack(anchor="w", padx=20)

        def switch():
            role_name = role_var.get()
            result = self.core.execute_capability("switch_role", role_name)
            if result.get("success"):
                self._update_colors_for_role()
                self._draw_jarvis()
                messagebox.showinfo("Role Switched", f"JARVIS is now {role_name}")
            else:
                messagebox.showerror("Error", result.get("error", "Failed to switch role"))
            dialog.destroy()

        tk.Button(dialog, text="Switch", command=switch, font=("Arial", 9)).pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy, font=("Arial", 9)).pack()

    def _show_command_dialog(self):
        """Show command input dialog"""
        command = simpledialog.askstring(
            "JARVIS Command",
            "Enter command:\n(status, switch <role>, query <text>, help)",
            parent=self.root
        )

        if command:
            self._process_command(command)

    def _process_command(self, command: str):
        try:
            """Process a command"""
            if not self.core:
                messagebox.showinfo("Command", "Enhanced core not available")
                return

            result = self.core.process_command(command)

            # Format result for display
            if "error" in result:
                messagebox.showerror("Error", result["error"])
            else:
                result_text = json.dumps(result, indent=2)
                messagebox.showinfo("Command Result", result_text)

        except Exception as e:
            self.logger.error(f"Error in _process_command: {e}", exc_info=True)
            raise
    def _show_status(self):
        """Show system status"""
        if not self.core:
            messagebox.showinfo("Status", "Enhanced core not available")
            return

        status = self.core.execute_capability("system_status")
        status_text = f"Role: {status.get('role', 'unknown')}\n"
        status_text += f"Experts Available: {status.get('experts_available', 0)}/{status.get('total_experts', 0)}\n"
        status_text += f"Capabilities: {status.get('capabilities', 0)}"

        messagebox.showinfo("JARVIS Status", status_text)

    def _show_help(self):
        """Show help information"""
        if not self.core:
            help_text = "Enhanced core not available"
        else:
            help_info = self.core.execute_capability("help")
            commands = help_info.get("commands", [])
            help_text = "Available Commands:\n\n"
            help_text += "\n".join(commands)
            help_text += "\n\nRight-click for context menu\nDouble-click for command dialog"

        messagebox.showinfo("JARVIS Help", help_text)

    def start_animation(self):
        """Start animation loop"""
        self.animation_running = True

        def animate():
            while self.animation_running and self.root:
                try:
                    # Animate eye glow
                    self.eye_glow += 0.1 * self.eye_dir
                    if self.eye_glow >= 1.0:
                        self.eye_glow = 1.0
                        self.eye_dir = -1
                    elif self.eye_glow <= 0.0:
                        self.eye_glow = 0.0
                        self.eye_dir = 1

                    # Animate arc reactor pulse
                    self.arc_reactor_pulse = (math.sin(time.time() * 2) + 1) / 2

                    # Redraw
                    self._draw_jarvis()
                    self.root.update()
                    time.sleep(0.05)
                except:
                    break

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def run(self):
        """Run Enhanced JARVIS Desktop Assistant"""
        try:
            self.create_window()
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("🛑 JARVIS Desktop Assistant Enhanced stopped")
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
        finally:
            self.animation_running = False
            if self.manager:
                self.manager.deactivate()


if __name__ == "__main__":
    assistant = JARVISDesktopAssistantEnhanced()
    assistant.run()
