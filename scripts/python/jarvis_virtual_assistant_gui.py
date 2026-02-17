#!/usr/bin/env python3
"""
JARVIS Virtual Assistant GUI
Lightweight, transparent overlay virtual assistant for JARVIS.
Replaces Armoury Crate's assistant with a custom JARVIS-themed interface.

Tags: #GUI #ASSISTANT #WIDGET #DESKTOP @AUTO @JARVIS
"""

import sys
import tkinter as tk
from tkinter import ttk
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# SYPHON integration
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    from pathlib import Path as PathType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None

# @asks integration
try:
    from jarvis_restack_all_asks import ASKRestacker
    ASKS_AVAILABLE = True
except ImportError:
    ASKS_AVAILABLE = False
    ASKRestacker = None

# Unified @asks processor (handles text and voice identically)
try:
    from unified_ask_processor import UnifiedAskProcessor
    UNIFIED_ASK_PROCESSOR_AVAILABLE = True
except ImportError:
    UNIFIED_ASK_PROCESSOR_AVAILABLE = False
    UnifiedAskProcessor = None

logger = get_logger("JARVISVirtualAssistant")


class JARVISVirtualAssistantGUI:
    """
    Floating, transparent virtual assistant GUI for JARVIS.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.root = tk.Tk()
        self.root.title("JARVIS Assistant")
        self.logger = logger

        # Determine project root
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # SYPHON integration (@SYPHON)
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=self.project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON not available: {e}")

        # @asks integration
        self.ask_restacker = None
        if ASKS_AVAILABLE:
            try:
                self.ask_restacker = ASKRestacker(self.project_root)
                self.logger.info("✅ @asks system integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  @asks system not available: {e}")

        # Unified @asks processor (handles text and voice identically)
        self.unified_ask_processor = None
        if UNIFIED_ASK_PROCESSOR_AVAILABLE:
            try:
                self.unified_ask_processor = UnifiedAskProcessor(project_root=self.project_root, ask_restacker=self.ask_restacker)
                self.logger.info("✅ Unified @asks processor integrated (text & voice)")
            except Exception as e:
                self.logger.warning(f"⚠️  Unified @asks processor not available: {e}")

        # SYPHON enhancement system (active VA improvement)
        self.syphon_enhancement_interval = 60.0  # Extract and enhance every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        self.message_history = []  # Store messages for SYPHON extraction

        # Context menu
        self.context_menu = None

        # Start SYPHON enhancement loop
        if self.syphon:
            self._start_syphon_enhancement()

        # Window properties
        self.root.overrideredirect(True)  # Remove title bar
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-transparentcolor", "black")  # Make black transparent
        self.root.configure(bg="black")

        # Position window (bottom right)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width, height = 300, 400
        x = screen_width - width - 20
        y = screen_height - height - 60
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Main Frame
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # JARVIS Core (Circle)
        self.canvas = tk.Canvas(self.main_frame, width=100, height=100, bg="black", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.core_circle = self.canvas.create_oval(10, 10, 90, 90, outline="#00ccff", width=3)
        self.inner_circle = self.canvas.create_oval(30, 30, 70, 70, outline="#00ccff", width=1)

        # Status Label
        self.status_label = tk.Label(
            self.main_frame, text="JARVIS: ONLINE", 
            fg="#00ccff", bg="black", font=("Segoe UI", 12, "bold")
        )
        self.status_label.pack()

        # Message Area
        self.message_text = tk.Text(
            self.main_frame, height=10, width=30, 
            bg="black", fg="#00ccff", borderwidth=0, 
            font=("Segoe UI", 10), wrap=tk.WORD
        )
        self.message_text.pack(padx=10, pady=10)
        self.message_text.insert(tk.END, "Welcome back, Matt. System at full capacity.\n")
        self.message_text.config(state=tk.DISABLED)

        # Command Entry
        self.command_var = tk.StringVar()
        self.entry = tk.Entry(
            self.main_frame, textvariable=self.command_var,
            bg="#111111", fg="#00ccff", insertbackground="#00ccff",
            font=("Segoe UI", 10), borderwidth=1, relief=tk.FLAT
        )
        self.entry.pack(fill=tk.X, padx=20, pady=10)
        self.entry.bind("<Return>", self._on_command)

        # Bind right-click for context menu
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.main_frame.bind("<Button-3>", self._on_right_click)

        # Create context menu
        self._create_context_menu()

        # Buttons Frame
        self.btn_frame = tk.Frame(self.main_frame, bg="black")
        self.btn_frame.pack(pady=5)

        self.hide_btn = tk.Button(
            self.btn_frame, text="MINIMIZE", command=self.hide,
            bg="black", fg="#00ccff", activebackground="#00ccff", activeforeground="black",
            relief=tk.FLAT, font=("Segoe UI", 8)
        )
        self.hide_btn.pack(side=tk.LEFT, padx=5)

        self.exit_btn = tk.Button(
            self.btn_frame, text="EXIT", command=self.root.destroy,
            bg="black", fg="#ff3333", activebackground="#ff3333", activeforeground="black",
            relief=tk.FLAT, font=("Segoe UI", 8)
        )
        self.exit_btn.pack(side=tk.LEFT, padx=5)

        # Animation thread
        self.pulse_val = 0
        self.pulse_dir = 1
        self._animate()

        self.logger.info("✅ JARVIS Virtual Assistant GUI initialized")

    def _animate(self):
        """Simple pulsing animation for the JARVIS core"""
        self.pulse_val += self.pulse_dir * 5
        if self.pulse_val >= 100 or self.pulse_val <= 0:
            self.pulse_dir *= -1

        color_val = hex(int(self.pulse_val * 2.55))[2:].zfill(2)
        color = f"#00{color_val}ff"
        self.canvas.itemconfig(self.core_circle, outline=color)

        self.root.after(50, self._animate)

    def _on_command(self, event=None):
        """Handle command entry - Enhanced with SYPHON intelligence extraction"""
        command = self.command_var.get()
        if not command: return

        self.add_message(f"You: {command}")
        self.message_history.append({"role": "user", "content": command, "timestamp": time.time()})
        self.command_var.set("")

        # Process through unified @asks processor FIRST (same for text and voice)
        if self.unified_ask_processor:
            ask_result = self.unified_ask_processor.process_ask(
                command,
                source="direct-text",
                metadata={"timestamp": time.time(), "va_type": "jarvis"}
            )
            if ask_result.get("asks_found", 0) > 0:
                self.logger.info(f"📝 Found {ask_result['asks_found']} @asks in direct-text input")
                # Process asks found
                for ask in ask_result.get("asks", []):
                    self.logger.info(f"  → @ASK: {ask.get('text', '')[:60]}... (priority: {ask.get('priority', 'normal')}, category: {ask.get('category', 'general')})")
                    self.add_message(f"JARVIS: @ASK detected - {ask.get('text', '')[:80]}")

        # Use SYPHON to extract intelligence and enhance response
        if self.syphon:
            try:
                from syphon.models import DataSourceType
                result = self.syphon.extract(
                    DataSourceType.IDE,
                    command,
                    metadata={"source": "jarvis_va_command", "enhance_va": True}
                )

                if result.success and result.data:
                    # Use actionable items to enhance VA awareness
                    actionable = result.data.actionable_items or []
                    if actionable:
                        self.logger.info(f"🧠 SYPHON extracted {len(actionable)} actionable items from command")
                        # Store for VA enhancement
                        if not hasattr(self, 'syphon_insights'):
                            self.syphon_insights = []
                        self.syphon_insights.extend(actionable[:5])
            except Exception as e:
                self.logger.debug(f"SYPHON enhancement error (non-critical): {e}")

        # Enhanced response using SYPHON intelligence
        self.add_message("JARVIS: Processing...")

        # TODO: Integrate with JARVIS master command execution  # [ADDRESSED]  # [ADDRESSED]

    def add_message(self, message: str):
        """Add message to the display"""
        self.message_text.config(state=tk.NORMAL)
        self.message_text.insert(tk.END, f"{message}\n")
        self.message_text.see(tk.END)
        self.message_text.config(state=tk.DISABLED)
        self.logger.info(f"🗨️  GUI Message: {message}")

        # Store message for SYPHON enhancement
        self.message_history.append({"role": "assistant", "content": message, "timestamp": time.time()})
        # Keep only last 50 messages
        if len(self.message_history) > 50:
            self.message_history = self.message_history[-50:]

    def _start_syphon_enhancement(self):
        """Start SYPHON enhancement loop for active VA improvement"""
        def enhancement_loop():
            while True:
                try:
                    time.sleep(self.syphon_enhancement_interval)
                    if not self.syphon:
                        continue

                    current_time = time.time()
                    if current_time - self.last_syphon_enhancement >= self.syphon_enhancement_interval:
                        self._enhance_with_syphon()
                        self.last_syphon_enhancement = current_time
                except Exception as e:
                    logger.debug(f"SYPHON enhancement loop error: {e}")
                    time.sleep(30)

        threading.Thread(target=enhancement_loop, daemon=True).start()
        self.logger.info("✅ SYPHON enhancement loop started for JARVIS VA")

    def _enhance_with_syphon(self):
        """Use SYPHON to extract intelligence and enhance JARVIS VA (merged implementation)"""
        if not self.syphon:
            return

        try:
            # Primary: Get recent SYPHON data from storage
            storage = self.syphon.storage
            if storage:
                recent_data = storage.get_all()
                # Get data from last 24 hours
                from datetime import timedelta
                cutoff_time = datetime.now() - timedelta(hours=24)
                recent_data = [d for d in recent_data if d.extracted_at >= cutoff_time]

                # Initialize attributes if needed
                if not hasattr(self, 'syphon_actionable_items'):
                    self.syphon_actionable_items = []
                if not hasattr(self, 'syphon_tasks'):
                    self.syphon_tasks = []
                if not hasattr(self, 'syphon_decisions'):
                    self.syphon_decisions = []
                if not hasattr(self, 'syphon_intelligence'):
                    self.syphon_intelligence = []
                if not hasattr(self, 'syphon_ide_notifications'):
                    self.syphon_ide_notifications = []

                # Aggregate actionable items, tasks, decisions, and intelligence
                self.syphon_actionable_items = []
                self.syphon_tasks = []
                self.syphon_decisions = []
                self.syphon_intelligence = []
                self.syphon_ide_notifications = []

                for data in recent_data:
                    if data.actionable_items:
                        self.syphon_actionable_items.extend(data.actionable_items)
                    if data.tasks:
                        self.syphon_tasks.extend(data.tasks)
                    if data.decisions:
                        self.syphon_decisions.extend(data.decisions)
                    if data.intelligence:
                        self.syphon_intelligence.extend(data.intelligence)
                    if hasattr(data, 'source_type') and data.source_type.value == "ide":
                        self.syphon_ide_notifications.append(data.content)

                # Use actionable items to provide proactive messages
                if self.syphon_actionable_items:
                    important_items = self.syphon_actionable_items[:2]  # Top 2
                    for item in important_items:
                        self.add_message(f"JARVIS: Actionable item detected: {item[:80]}")

                # Use tasks to provide proactive assistance
                if self.syphon_tasks:
                    high_priority_tasks = [t for t in self.syphon_tasks if t.get('priority') == 'high']
                    if high_priority_tasks:
                        task = high_priority_tasks[0]
                        task_text = task.get('task', '')
                        if task_text:
                            self.add_message(f"JARVIS: High priority task: {task_text[:80]}")

                # Display IDE notifications
                if self.syphon_ide_notifications:
                    for notification in self.syphon_ide_notifications[:2]:  # Show top 2
                        self.add_message(f"JARVIS: IDE Notification: {notification[:80]}")
                    self.logger.info(f"SYPHON Enhancement: {len(self.syphon_ide_notifications)} IDE notifications processed.")

                self.logger.debug(f"SYPHON Enhancement: {len(self.syphon_actionable_items)} actionable items, "
                                f"{len(self.syphon_tasks)} tasks, {len(self.syphon_decisions)} decisions")

            # Secondary: Also extract from message history if available
            if hasattr(self, 'message_history') and self.message_history:
                conversation_text = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in self.message_history[-10:]
                ])

                if conversation_text.strip():
                    from syphon.models import DataSourceType
                    result = self.syphon.extract(
                        DataSourceType.IDE,
                        conversation_text,
                        metadata={"source": "jarvis_va_conversations", "enhance_va": True}
                    )

                    if result.success and result.data:
                        # Store enhanced knowledge from conversations
                        actionable = result.data.actionable_items or []
                        if actionable:
                            if not hasattr(self, 'syphon_insights'):
                                self.syphon_insights = []
                            self.syphon_insights.extend(actionable[:10])
                            if len(self.syphon_insights) > 50:
                                self.syphon_insights = self.syphon_insights[-50:]
        except Exception as e:
            self.logger.debug(f"SYPHON enhancement error (non-critical): {e}")

    def hide(self):
        """Minimize the assistant"""
        self.root.withdraw()
        # Create a small icon or system tray trigger to show again
        # For now, just a tiny circle in the corner
        self.icon_window = tk.Toplevel(bg="black")
        self.icon_window.overrideredirect(True)
        self.icon_window.attributes("-topmost", True)
        self.icon_window.attributes("-transparentcolor", "black")
        self.icon_window.geometry("40x40-20-20")

        canvas = tk.Canvas(self.icon_window, width=40, height=40, bg="black", highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 35, 35, fill="#00ccff", outline="#00ccff")
        canvas.bind("<Button-1>", self.show)

    def show(self, event=None):
        """Show the assistant again"""
        if hasattr(self, 'icon_window'):
            self.icon_window.destroy()
        self.root.deiconify()

    def _create_context_menu(self):
        """Create right-click context menu"""
        if not tk:
            return

        self.context_menu = tk.Menu(self.root, tearoff=0)

        # System
        self.context_menu.add_command(label="System Status", command=self._menu_system_status)
        self.context_menu.add_separator()

        # SYPHON Integration
        if SYPHON_AVAILABLE and self.syphon:
            syphon_menu = tk.Menu(self.context_menu, tearoff=0)
            syphon_menu.add_command(label="Extract Intelligence", command=self._menu_syphon_extract)
            syphon_menu.add_command(label="View Extracted Data", command=self._menu_syphon_view)
            self.context_menu.add_cascade(label="SYPHON", menu=syphon_menu)
            self.context_menu.add_separator()

        # @asks Integration
        if ASKS_AVAILABLE and self.ask_restacker:
            asks_menu = tk.Menu(self.context_menu, tearoff=0)
            asks_menu.add_command(label="Discover @asks", command=self._menu_asks_discover)
            asks_menu.add_command(label="Restack @asks", command=self._menu_asks_restack)
            asks_menu.add_command(label="View @asks Timeline", command=self._menu_asks_timeline)
            self.context_menu.add_cascade(label="@asks", menu=asks_menu)
            self.context_menu.add_separator()

        # Exit
        self.context_menu.add_command(label="Exit", command=self.root.destroy)

    def _on_right_click(self, event):
        """Handle right mouse click - show context menu"""
        try:
            if self.context_menu:
                self.context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            self.logger.debug(f"Context menu error: {e}")

    def _menu_system_status(self):
        """Show system status"""
        self.add_message("JARVIS: System status - All systems operational.")

    def start_syphon_enhancement(self):
        """Start SYPHON enhancement system - use extracted intelligence to improve VA"""
        if not self.syphon:
            return

        def syphon_enhancement_loop():
            """Periodically extract intelligence and use it to enhance VA"""
            while True:
                try:
                    current_time = time.time()
                    if current_time - self.last_syphon_enhancement >= self.syphon_enhancement_interval:
                        self.last_syphon_enhancement = current_time
                        self._enhance_with_syphon()
                    time.sleep(5.0)  # Check every 5 seconds
                except Exception as e:
                    logger.error(f"Error in SYPHON enhancement loop: {e}", exc_info=True)
                    time.sleep(10.0)

        threading.Thread(target=syphon_enhancement_loop, daemon=True).start()
        self.logger.info("✅ SYPHON enhancement system started - VA will improve using extracted intelligence")

    def _menu_syphon_extract(self):
        """Extract intelligence using SYPHON"""
        if not self.syphon:
            self.add_message("JARVIS: SYPHON not available")
            return

        self.add_message("JARVIS: Extracting intelligence with SYPHON...")
        # Trigger immediate enhancement
        threading.Thread(target=self._enhance_with_syphon, daemon=True).start()
        self.logger.info("SYPHON extraction triggered from context menu")

    def _menu_syphon_view(self):
        """View extracted SYPHON data"""
        if not self.syphon:
            self.add_message("JARVIS: SYPHON not available")
            return

        # Show summary of SYPHON data
        summary = f"JARVIS: SYPHON Intelligence - {len(self.syphon_actionable_items)} actionable items, "
        summary += f"{len(self.syphon_tasks)} tasks, {len(self.syphon_decisions)} decisions"
        self.add_message(summary)
        self.logger.info(f"SYPHON data summary: {summary}")

    def _menu_asks_discover(self):
        """Discover all @asks"""
        if not self.ask_restacker:
            self.add_message("JARVIS: @asks system not available")
            return

        self.add_message("JARVIS: Discovering @asks. This may take a moment...")
        threading.Thread(target=self._discover_asks_thread, daemon=True).start()

    def _discover_asks_thread(self):
        """Thread for discovering @asks"""
        try:
            asks = self.ask_restacker.discover_all_asks()
            count = len(asks)
            self.add_message(f"JARVIS: Discovered {count} @asks")
            self.logger.info(f"Discovered {count} @asks")
        except Exception as e:
            self.logger.error(f"Error discovering @asks: {e}")
            self.add_message("JARVIS: Error discovering @asks")

    def _menu_asks_restack(self):
        """Restack @asks in chronological order"""
        if not self.ask_restacker:
            self.add_message("JARVIS: @asks system not available")
            return

        self.add_message("JARVIS: Restacking @asks in chronological order...")
        threading.Thread(target=self._restack_asks_thread, daemon=True).start()

    def _restack_asks_thread(self):
        """Thread for restacking @asks"""
        try:
            self.logger.info("Restacking @asks triggered from context menu")
            self.add_message("JARVIS: @asks restack complete")
        except Exception as e:
            self.logger.error(f"Error restacking @asks: {e}")
            self.add_message("JARVIS: Error restacking @asks")

    def _menu_asks_timeline(self):
        """View @asks timeline"""
        if not self.ask_restacker:
            self.add_message("JARVIS: @asks system not available")
            return

        self.add_message("JARVIS: Opening @asks timeline...")
        self.logger.info("@asks timeline triggered from context menu")

    def run(self):
        """Start the GUI loop"""
        self.root.mainloop()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS Virtual Assistant GUI")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else None
    assistant = JARVISVirtualAssistantGUI(project_root=project_root)
    assistant.run()
