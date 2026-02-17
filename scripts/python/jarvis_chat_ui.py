#!/usr/bin/env python3
"""
JARVIS Chat UI - Customizable WoW-Style Chat Interface

A customizable chat interface with full UI/UX controls similar to World of Warcraft:
- Font size, family, colors
- Channel and level filtering
- Transparency and positioning
- Message history and search
- Customizable appearance

Tags: #CHAT-UI #WOW-STYLE #CUSTOMIZABLE #UI-UX @JARVIS @LUMINA
"""

import sys
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, colorchooser, messagebox
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_local_chat_system import (
        LocalChatClient, ChatChannel, ChatLevel, ChatUIConfig, ChatMessage
    )
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("JARVISChatUI")


class ChatUIWindow:
    """Main chat UI window with customizable controls"""

    def __init__(self, client: LocalChatClient, config_file: Optional[Path] = None):
        self.client = client
        self.config_file = config_file or (project_root / "data" / "local_chat" / "ui_config.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load saved config
        self.ui_config = self._load_config()
        client.update_ui_config(self.ui_config)

        # Create main window
        self.root = tk.Tk()
        self.root.title("JARVIS Local Chat - WoW Style")
        self.root.geometry(f"{self.ui_config.width}x{self.ui_config.height}")
        self.root.geometry(f"+{self.ui_config.position_x}+{self.ui_config.position_y}")

        # Make window semi-transparent
        if sys.platform == "win32":
            try:
                self.root.attributes('-alpha', self.ui_config.transparency)
            except:
                pass

        # Setup UI
        self._setup_ui()

        # Register message handler
        self.client.on_message(self._handle_message)

        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.bind('<Configure>', self._on_window_move)

        logger.info("✅ Chat UI initialized")

    def _load_config(self) -> ChatUIConfig:
        """Load UI configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ChatUIConfig(**data)
        except Exception as e:
            logger.warning(f"Error loading config: {e}")
        return ChatUIConfig()

    def _save_config(self):
        """Save UI configuration to file"""
        try:
            config_dict = {
                "font_size": self.ui_config.font_size,
                "font_family": self.ui_config.font_family,
                "background_color": self.ui_config.background_color,
                "text_color": self.ui_config.text_color,
                "channel_colors": self.ui_config.channel_colors,
                "level_colors": self.ui_config.level_colors,
                "transparency": self.ui_config.transparency,
                "position_x": self.root.winfo_x(),
                "position_y": self.root.winfo_y(),
                "width": self.root.winfo_width(),
                "height": self.root.winfo_height(),
                "show_timestamps": self.ui_config.show_timestamps,
                "show_channel": self.ui_config.show_channel,
                "show_level": self.ui_config.show_level,
                "max_messages": self.ui_config.max_messages,
                "auto_scroll": self.ui_config.auto_scroll,
                "filter_levels": self.ui_config.filter_levels
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def _setup_ui(self):
        """Setup the UI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=(self.ui_config.font_family, self.ui_config.font_size),
            bg=self.ui_config.background_color,
            fg=self.ui_config.text_color,
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(0, weight=1)

        # Configure text tags for colors
        self._setup_text_tags()

        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        input_frame.columnconfigure(0, weight=1)

        # Channel selector
        channel_label = ttk.Label(input_frame, text="Channel:")
        channel_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        self.channel_var = tk.StringVar(value=ChatChannel.LOCAL.value)
        channel_combo = ttk.Combobox(
            input_frame,
            textvariable=self.channel_var,
            values=[ch.value for ch in ChatChannel],
            state="readonly",
            width=10
        )
        channel_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))

        # Input field
        self.input_field = ttk.Entry(input_frame)
        self.input_field.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(0, 5))
        input_frame.columnconfigure(2, weight=1)
        self.input_field.bind('<Return>', self._on_send_message)
        self.input_field.bind('<Up>', self._on_history_up)
        self.input_field.bind('<Down>', self._on_history_down)

        # Send button
        send_button = ttk.Button(input_frame, text="Send", command=self._on_send_message)
        send_button.grid(row=0, column=3, padx=(0, 5))

        # Settings button
        settings_button = ttk.Button(input_frame, text="⚙ Settings", command=self._open_settings)
        settings_button.grid(row=0, column=4)

        # Message history for up/down arrow navigation
        self.message_history: List[str] = []
        self.history_index = -1

        # Focus on input field
        self.input_field.focus()

    def _setup_text_tags(self):
        """Setup text color tags for channels and levels"""
        # Channel colors
        for channel, color in self.ui_config.channel_colors.items():
            self.chat_display.tag_config(f"channel_{channel}", foreground=color)

        # Level colors
        for level, color in self.ui_config.level_colors.items():
            self.chat_display.tag_config(f"level_{level}", foreground=color)

        # Combined tags
        for channel in self.ui_config.channel_colors.keys():
            for level in self.ui_config.level_colors.keys():
                tag_name = f"{channel}_{level}"
                # Use channel color as primary
                self.chat_display.tag_config(tag_name, foreground=self.ui_config.channel_colors[channel])

    def _handle_message(self, message: ChatMessage):
        """Handle incoming message"""
        # Check if message should be displayed based on filters
        if message.level.value not in self.ui_config.filter_levels:
            return

        # Format message
        timestamp = ""
        if self.ui_config.show_timestamps:
            timestamp = message.timestamp.strftime("%H:%M:%S") + " "

        channel_tag = ""
        if self.ui_config.show_channel:
            channel_tag = f"[{message.channel.value.upper()}] "

        level_tag = ""
        if self.ui_config.show_level:
            level_tag = f"[{message.level.value.upper()}] "

        # Build message text
        message_text = f"{timestamp}{channel_tag}{level_tag}{message.username}: {message.content}\n"

        # Enable text widget for editing
        self.chat_display.config(state=tk.NORMAL)

        # Insert message with appropriate tags
        start_index = self.chat_display.index(tk.END + "-1c")
        self.chat_display.insert(tk.END, message_text)
        end_index = self.chat_display.index(tk.END + "-1c")

        # Apply color tags
        tag_name = f"{message.channel.value}_{message.level.value}"
        if tag_name in [f"{ch}_{lev}" for ch in self.ui_config.channel_colors.keys() 
                       for lev in self.ui_config.level_colors.keys()]:
            self.chat_display.tag_add(tag_name, start_index, end_index)
        else:
            # Fallback to channel color
            self.chat_display.tag_add(f"channel_{message.channel.value}", start_index, end_index)

        # Limit message count
        lines = int(self.chat_display.index('end-1c').split('.')[0])
        if lines > self.ui_config.max_messages:
            self.chat_display.delete('1.0', f'{lines - self.ui_config.max_messages}.0')

        # Auto-scroll
        if self.ui_config.auto_scroll:
            self.chat_display.see(tk.END)

        # Disable text widget
        self.chat_display.config(state=tk.DISABLED)

    def _on_send_message(self, event=None):
        """Send message"""
        content = self.input_field.get().strip()
        if not content:
            return

        # Add to history
        if not self.message_history or self.message_history[-1] != content:
            self.message_history.append(content)
            if len(self.message_history) > 50:
                self.message_history.pop(0)
        self.history_index = -1

        # Parse commands
        channel = ChatChannel(self.channel_var.get())
        level = ChatLevel.INFO

        if content.startswith('/'):
            parts = content.split(' ', 1)
            command = parts[0].lower()
            message_content = parts[1] if len(parts) > 1 else ""

            if command == '/say':
                channel = ChatChannel.SAY
                content = message_content
            elif command == '/yell':
                channel = ChatChannel.YELL
                level = ChatLevel.WARNING
                content = message_content
            elif command == '/whisper':
                channel = ChatChannel.WHISPER
                content = message_content
            elif command == '/party':
                channel = ChatChannel.PARTY
                content = message_content
            elif command == '/guild':
                channel = ChatChannel.GUILD
                content = message_content
            elif command == '/help':
                self._show_help()
                self.input_field.delete(0, tk.END)
                return

        # Send message
        if content:
            self.client.send_message(content, channel=channel, level=level)
            self.input_field.delete(0, tk.END)

    def _on_history_up(self, event):
        """Navigate message history up"""
        if self.message_history:
            if self.history_index == -1:
                self.history_index = len(self.message_history) - 1
            elif self.history_index > 0:
                self.history_index -= 1
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, self.message_history[self.history_index])
        return "break"

    def _on_history_down(self, event):
        """Navigate message history down"""
        if self.message_history:
            if self.history_index < len(self.message_history) - 1:
                self.history_index += 1
                self.input_field.delete(0, tk.END)
                self.input_field.insert(0, self.message_history[self.history_index])
            else:
                self.history_index = -1
                self.input_field.delete(0, tk.END)
        return "break"

    def _open_settings(self):
        """Open settings window"""
        settings_window = ChatSettingsWindow(self.root, self.ui_config, self._apply_settings)
        settings_window.show()

    def _apply_settings(self, new_config: ChatUIConfig):
        """Apply new settings"""
        self.ui_config = new_config
        self.client.update_ui_config(new_config)

        # Update UI
        self.chat_display.config(
            font=(self.ui_config.font_family, self.ui_config.font_size),
            bg=self.ui_config.background_color,
            fg=self.ui_config.text_color
        )

        # Update transparency
        if sys.platform == "win32":
            try:
                self.root.attributes('-alpha', self.ui_config.transparency)
            except:
                pass

        # Rebuild text tags
        self._setup_text_tags()

        # Save config
        self._save_config()

        logger.info("✅ Settings applied")

    def _on_window_move(self, event):
        """Handle window movement"""
        if event.widget == self.root:
            self.ui_config.position_x = self.root.winfo_x()
            self.ui_config.position_y = self.root.winfo_y()
            self._save_config()

    def _on_closing(self):
        """Handle window closing"""
        self._save_config()
        self.client.disconnect()
        self.root.destroy()

    def _show_help(self):
        """Show help message"""
        help_text = """
Chat Commands:
  /say <message>    - Send to Say channel
  /yell <message>  - Send to Yell channel (longer range)
  /whisper <msg>   - Send private whisper
  /party <message> - Send to Party channel
  /guild <message> - Send to Guild channel
  /help            - Show this help

Use Settings button (⚙) to customize:
  - Font size and family
  - Colors for channels and levels
  - Transparency
  - Message filtering
  - Display options
        """
        messagebox.showinfo("Chat Help", help_text.strip())

    def run(self):
        """Run the UI"""
        self.root.mainloop()


class ChatSettingsWindow:
    """Settings window for customizing chat UI"""

    def __init__(self, parent, config: ChatUIConfig, callback: callable):
        self.config = config
        self.callback = callback

        self.window = tk.Toplevel(parent)
        self.window.title("Chat Settings - Customize UI/UX")
        self.window.geometry("500x600")

        self._setup_settings_ui()

    def _setup_settings_ui(self):
        """Setup settings UI"""
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Appearance tab
        appearance_frame = ttk.Frame(notebook, padding="10")
        notebook.add(appearance_frame, text="Appearance")
        self._setup_appearance_tab(appearance_frame)

        # Colors tab
        colors_frame = ttk.Frame(notebook, padding="10")
        notebook.add(colors_frame, text="Colors")
        self._setup_colors_tab(colors_frame)

        # Display tab
        display_frame = ttk.Frame(notebook, padding="10")
        notebook.add(display_frame, text="Display")
        self._setup_display_tab(display_frame)

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Apply", command=self._apply).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)

    def _setup_appearance_tab(self, parent):
        """Setup appearance settings"""
        row = 0

        # Font size
        ttk.Label(parent, text="Font Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        font_size_var = tk.IntVar(value=self.config.font_size)
        font_size_scale = ttk.Scale(parent, from_=8, to=24, variable=font_size_var, orient=tk.HORIZONTAL)
        font_size_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        font_size_label = ttk.Label(parent, textvariable=font_size_var)
        font_size_label.grid(row=row, column=2, padx=5)
        parent.columnconfigure(1, weight=1)
        row += 1

        # Font family
        ttk.Label(parent, text="Font Family:").grid(row=row, column=0, sticky=tk.W, pady=5)
        font_family_var = tk.StringVar(value=self.config.font_family)
        font_family_combo = ttk.Combobox(parent, textvariable=font_family_var, 
                                        values=["Consolas", "Courier New", "Monaco", "Menlo", "Arial", "Helvetica"])
        font_family_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Transparency
        ttk.Label(parent, text="Transparency:").grid(row=row, column=0, sticky=tk.W, pady=5)
        transparency_var = tk.DoubleVar(value=self.config.transparency)
        transparency_scale = ttk.Scale(parent, from_=0.3, to=1.0, variable=transparency_var, orient=tk.HORIZONTAL)
        transparency_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        transparency_label = ttk.Label(parent, textvariable=transparency_var)
        transparency_label.grid(row=row, column=2, padx=5)
        row += 1

        # Background color
        ttk.Label(parent, text="Background:").grid(row=row, column=0, sticky=tk.W, pady=5)
        bg_color_var = tk.StringVar(value=self.config.background_color)
        ttk.Entry(parent, textvariable=bg_color_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(parent, text="Choose", command=lambda: self._choose_color(bg_color_var)).grid(row=row, column=2, padx=5)
        row += 1

        # Text color
        ttk.Label(parent, text="Text Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        text_color_var = tk.StringVar(value=self.config.text_color)
        ttk.Entry(parent, textvariable=text_color_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(parent, text="Choose", command=lambda: self._choose_color(text_color_var)).grid(row=row, column=2, padx=5)
        row += 1

        # Store variables
        self.font_size_var = font_size_var
        self.font_family_var = font_family_var
        self.transparency_var = transparency_var
        self.bg_color_var = bg_color_var
        self.text_color_var = text_color_var

    def _setup_colors_tab(self, parent):
        """Setup color settings"""
        row = 0

        # Channel colors
        ttk.Label(parent, text="Channel Colors:", font=("", 10, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=10)
        row += 1

        self.channel_color_vars = {}
        for channel in self.config.channel_colors.keys():
            ttk.Label(parent, text=f"{channel.title()}:").grid(row=row, column=0, sticky=tk.W, pady=2)
            var = tk.StringVar(value=self.config.channel_colors[channel])
            ttk.Entry(parent, textvariable=var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5)
            ttk.Button(parent, text="Choose", command=lambda v=var: self._choose_color(v)).grid(row=row, column=2, padx=5)
            self.channel_color_vars[channel] = var
            row += 1

        # Level colors
        ttk.Label(parent, text="Level Colors:", font=("", 10, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        row += 1

        self.level_color_vars = {}
        for level in self.config.level_colors.keys():
            ttk.Label(parent, text=f"{level.title()}:").grid(row=row, column=0, sticky=tk.W, pady=2)
            var = tk.StringVar(value=self.config.level_colors[level])
            ttk.Entry(parent, textvariable=var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5)
            ttk.Button(parent, text="Choose", command=lambda v=var: self._choose_color(v)).grid(row=row, column=2, padx=5)
            self.level_color_vars[level] = var
            row += 1

    def _setup_display_tab(self, parent):
        """Setup display settings"""
        row = 0

        # Show options
        ttk.Label(parent, text="Display Options:", font=("", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1

        show_timestamps_var = tk.BooleanVar(value=self.config.show_timestamps)
        ttk.Checkbutton(parent, text="Show Timestamps", variable=show_timestamps_var).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1

        show_channel_var = tk.BooleanVar(value=self.config.show_channel)
        ttk.Checkbutton(parent, text="Show Channel Tags", variable=show_channel_var).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1

        show_level_var = tk.BooleanVar(value=self.config.show_level)
        ttk.Checkbutton(parent, text="Show Level Tags", variable=show_level_var).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1

        auto_scroll_var = tk.BooleanVar(value=self.config.auto_scroll)
        ttk.Checkbutton(parent, text="Auto Scroll", variable=auto_scroll_var).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1

        # Max messages
        ttk.Label(parent, text="Max Messages:").grid(row=row, column=0, sticky=tk.W, pady=5)
        max_messages_var = tk.IntVar(value=self.config.max_messages)
        max_messages_scale = ttk.Scale(parent, from_=50, to=500, variable=max_messages_var, orient=tk.HORIZONTAL)
        max_messages_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        max_messages_label = ttk.Label(parent, textvariable=max_messages_var)
        max_messages_label.grid(row=row, column=2, padx=5)
        parent.columnconfigure(1, weight=1)
        row += 1

        # Filter levels
        ttk.Label(parent, text="Show Levels:", font=("", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        row += 1

        self.filter_level_vars = {}
        for level in ["debug", "info", "warning", "error", "critical"]:
            var = tk.BooleanVar(value=level in self.config.filter_levels)
            ttk.Checkbutton(parent, text=level.title(), variable=var).grid(row=row, column=0, sticky=tk.W, pady=2)
            self.filter_level_vars[level] = var
            row += 1

        # Store variables
        self.show_timestamps_var = show_timestamps_var
        self.show_channel_var = show_channel_var
        self.show_level_var = show_level_var
        self.auto_scroll_var = auto_scroll_var
        self.max_messages_var = max_messages_var

    def _choose_color(self, var: tk.StringVar):
        """Open color chooser"""
        color = colorchooser.askcolor(initialcolor=var.get())
        if color[1]:  # User didn't cancel
            var.set(color[1])

    def _apply(self):
        """Apply settings"""
        # Update config
        self.config.font_size = self.font_size_var.get()
        self.config.font_family = self.font_family_var.get()
        self.config.transparency = self.transparency_var.get()
        self.config.background_color = self.bg_color_var.get()
        self.config.text_color = self.text_color_var.get()

        # Update channel colors
        for channel, var in self.channel_color_vars.items():
            self.config.channel_colors[channel] = var.get()

        # Update level colors
        for level, var in self.level_color_vars.items():
            self.config.level_colors[level] = var.get()

        # Update display options
        self.config.show_timestamps = self.show_timestamps_var.get()
        self.config.show_channel = self.show_channel_var.get()
        self.config.show_level = self.show_level_var.get()
        self.config.auto_scroll = self.auto_scroll_var.get()
        self.config.max_messages = self.max_messages_var.get()

        # Update filter levels
        self.config.filter_levels = [
            level for level, var in self.filter_level_vars.items() if var.get()
        ]

        # Call callback
        self.callback(self.config)
        self.window.destroy()

    def show(self):
        """Show settings window"""
        self.window.wait_window()


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Chat UI")
        parser.add_argument("--host", default="localhost", help="Server host")
        parser.add_argument("--port", type=int, default=8888, help="Server port")
        parser.add_argument("--username", default="User", help="Username")

        args = parser.parse_args()

        # Create client
        client = LocalChatClient(
            server_host=args.host,
            server_port=args.port,
            username=args.username
        )

        # Connect
        if not client.connect():
            print("❌ Failed to connect to chat server")
            print("   Make sure the server is running:")
            print(f"   python jarvis_local_chat_system.py --server --host {args.host} --port {args.port}")
            return

        # Create and run UI
        ui = ChatUIWindow(client)
        ui.run()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()