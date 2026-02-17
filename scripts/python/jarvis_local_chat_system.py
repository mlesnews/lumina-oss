#!/usr/bin/env python3
"""
JARVIS Local Chat System - WoW-Style Chat Interface

A local network chat system similar to World of Warcraft's chat interface with:
- Local proximity chat (users on same network)
- Multiple chat channels/levels
- Customizable UI/UX controls
- Jarvis autonomous lead role management

Features:
- Chat channels: Local, Say, Yell, Whisper, Party, Guild, System
- Chat levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Customizable UI: Font size, colors, transparency, position
- Jarvis moderation and autonomous management
- Message filtering and search
- Chat history and logging

Tags: #CHAT #LOCAL-NETWORK #WOW-STYLE #UI-UX #JARVIS-LEAD @JARVIS @LUMINA
"""

import sys
import json
import socket
import threading
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLocalChat")


class ChatChannel(Enum):
    """Chat channels similar to WoW"""
    LOCAL = "local"  # Proximity chat (default)
    SAY = "say"  # Normal speech
    YELL = "yell"  # Shout (longer range)
    WHISPER = "whisper"  # Private message
    PARTY = "party"  # Group chat
    GUILD = "guild"  # Organization chat
    SYSTEM = "system"  # System messages
    JARVIS = "jarvis"  # Jarvis autonomous messages


class ChatLevel(Enum):
    """Message importance/visibility levels"""
    DEBUG = "debug"  # Debug messages (lowest)
    INFO = "info"  # Normal information
    WARNING = "warning"  # Warnings
    ERROR = "error"  # Errors
    CRITICAL = "critical"  # Critical messages (highest)


@dataclass
class ChatMessage:
    """Chat message structure"""
    message_id: str
    user_id: str
    username: str
    channel: ChatChannel
    level: ChatLevel
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "message_id": self.message_id,
            "user_id": self.user_id,
            "username": self.username,
            "channel": self.channel.value,
            "level": self.level.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create from dictionary"""
        return cls(
            message_id=data["message_id"],
            user_id=data["user_id"],
            username=data["username"],
            channel=ChatChannel(data["channel"]),
            level=ChatLevel(data["level"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class ChatUIConfig:
    """UI/UX configuration for chat interface"""
    font_size: int = 14
    font_family: str = "Consolas"
    background_color: str = "#1E1E1E"
    text_color: str = "#FFFFFF"
    channel_colors: Dict[str, str] = None
    level_colors: Dict[str, str] = None
    transparency: float = 0.9
    position_x: int = 0
    position_y: int = 0
    width: int = 400
    height: int = 300
    show_timestamps: bool = True
    show_channel: bool = True
    show_level: bool = True
    max_messages: int = 100
    auto_scroll: bool = True
    filter_levels: List[str] = None  # Which levels to show

    def __post_init__(self):
        """Initialize default colors"""
        if self.channel_colors is None:
            self.channel_colors = {
                "local": "#00FF00",
                "say": "#FFFFFF",
                "yell": "#FF6600",
                "whisper": "#FF00FF",
                "party": "#00FFFF",
                "guild": "#FFFF00",
                "system": "#FF0000",
                "jarvis": "#00D9FF"
            }
        if self.level_colors is None:
            self.level_colors = {
                "debug": "#808080",
                "info": "#FFFFFF",
                "warning": "#FFFF00",
                "error": "#FF0000",
                "critical": "#FF00FF"
            }
        if self.filter_levels is None:
            self.filter_levels = ["info", "warning", "error", "critical"]


class JARVISChatModerator:
    """JARVIS autonomous chat moderation and management"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.moderated_users = set()
        self.auto_responses = {}
        self.lead_mode = True  # Jarvis takes lead role

    def should_moderate(self, message: ChatMessage) -> bool:
        """Check if message should be moderated"""
        # Jarvis takes lead - moderate all messages
        return self.lead_mode

    def process_message(self, message: ChatMessage) -> Optional[ChatMessage]:
        """Process message with Jarvis moderation"""
        if not self.should_moderate(message):
            return message

        # Jarvis autonomous processing
        # Add context, enhance, or respond
        if message.channel == ChatChannel.JARVIS:
            # Jarvis messages are already processed
            return message

        # Check for auto-responses
        content_lower = message.content.lower()
        for trigger, response in self.auto_responses.items():
            if trigger in content_lower:
                # Create Jarvis response
                jarvis_msg = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    user_id="jarvis",
                    username="JARVIS",
                    channel=ChatChannel.JARVIS,
                    level=ChatLevel.INFO,
                    content=response,
                    timestamp=datetime.now(),
                    metadata={"auto_response": True, "trigger": trigger}
                )
                return jarvis_msg

        return message

    def add_auto_response(self, trigger: str, response: str):
        """Add auto-response for Jarvis"""
        self.auto_responses[trigger.lower()] = response
        self.logger.info(f"JARVIS: Added auto-response for '{trigger}'")


class LocalChatServer:
    """Local network chat server (like WoW's local chat)"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8888, project_root: Optional[Path] = None):
        self.host = host
        self.port = port
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger

        # Server state
        self.running = False
        self.server_socket = None
        self.clients: Dict[str, socket.socket] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.message_history: List[ChatMessage] = []
        self.max_history = 1000

        # Jarvis moderator
        self.moderator = JARVISChatModerator(self.project_root)

        # Data directory
        self.data_dir = self.project_root / "data" / "local_chat"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "chat_history.jsonl"

        self.logger.info("✅ Local Chat Server initialized")

    def start(self):
        """Start the chat server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True

            self.logger.info(f"🚀 Chat server started on {self.host}:{self.port}")

            # Start Jarvis welcome message
            self._send_system_message("JARVIS Local Chat Server is online. Jarvis is taking the lead role.")

            # Accept connections
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_id = str(uuid.uuid4())
                    self.clients[client_id] = client_socket

                    # Start client handler thread
                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_id, client_socket, address),
                        daemon=True
                    )
                    thread.start()

                    self.logger.info(f"✅ Client connected: {address} (ID: {client_id})")
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connection: {e}")
        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            raise

    def stop(self):
        """Stop the chat server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

        # Close all client connections
        for client_id, client_socket in self.clients.items():
            try:
                client_socket.close()
            except:
                pass

        self.clients.clear()
        self.logger.info("🛑 Chat server stopped")

    def _handle_client(self, client_id: str, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle client connection"""
        try:
            while self.running:
                # Receive message
                data = client_socket.recv(4096)
                if not data:
                    break

                try:
                    message_data = json.loads(data.decode('utf-8'))
                    message = ChatMessage.from_dict(message_data)

                    # Process with Jarvis moderator
                    processed = self.moderator.process_message(message)

                    if processed:
                        # Add to history
                        self.message_history.append(processed)
                        if len(self.message_history) > self.max_history:
                            self.message_history.pop(0)

                        # Save to file
                        self._save_message(processed)

                        # Broadcast to all clients
                        self._broadcast_message(processed)

                        # Jarvis auto-response if needed
                        if processed.channel != ChatChannel.JARVIS:
                            jarvis_response = self.moderator.process_message(processed)
                            if jarvis_response and jarvis_response.user_id == "jarvis":
                                self.message_history.append(jarvis_response)
                                self._save_message(jarvis_response)
                                self._broadcast_message(jarvis_response)

                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON from client {client_id}")
                except Exception as e:
                    self.logger.error(f"Error handling message from {client_id}: {e}")

        except Exception as e:
            self.logger.error(f"Error in client handler for {client_id}: {e}")
        finally:
            # Remove client
            if client_id in self.clients:
                del self.clients[client_id]
            try:
                client_socket.close()
            except:
                pass
            self.logger.info(f"Client disconnected: {address}")

    def _broadcast_message(self, message: ChatMessage):
        """Broadcast message to all connected clients"""
        message_json = json.dumps(message.to_dict())
        message_bytes = message_json.encode('utf-8')

        disconnected_clients = []
        for client_id, client_socket in self.clients.items():
            try:
                client_socket.sendall(message_bytes + b'\n')
            except Exception as e:
                self.logger.warning(f"Error sending to client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Remove disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.clients:
                del self.clients[client_id]

    def _send_system_message(self, content: str):
        """Send system message"""
        system_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id="system",
            username="SYSTEM",
            channel=ChatChannel.SYSTEM,
            level=ChatLevel.INFO,
            content=content,
            timestamp=datetime.now()
        )
        self.message_history.append(system_msg)
        self._save_message(system_msg)
        self._broadcast_message(system_msg)

    def _save_message(self, message: ChatMessage):
        """Save message to history file"""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Error saving message: {e}")


class LocalChatClient:
    """Local chat client for connecting to server"""

    def __init__(self, server_host: str = "localhost", server_port: int = 8888, 
                 username: str = "User", user_id: Optional[str] = None):
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.user_id = user_id or str(uuid.uuid4())
        self.logger = logger

        # Client state
        self.connected = False
        self.socket = None
        self.receive_thread = None
        self.message_callbacks: List[callable] = []

        # UI config
        self.ui_config = ChatUIConfig()

        self.logger.info(f"✅ Chat client initialized: {username} ({self.user_id})")

    def connect(self) -> bool:
        """Connect to chat server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True

            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()

            self.logger.info(f"✅ Connected to chat server at {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.logger.info("Disconnected from chat server")

    def send_message(self, content: str, channel: ChatChannel = ChatChannel.LOCAL, 
                    level: ChatLevel = ChatLevel.INFO, metadata: Optional[Dict] = None):
        """Send message to server"""
        if not self.connected:
            self.logger.warning("Not connected to server")
            return False

        message = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id=self.user_id,
            username=self.username,
            channel=channel,
            level=level,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )

        try:
            message_json = json.dumps(message.to_dict())
            self.socket.sendall(message_json.encode('utf-8') + b'\n')
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False

    def _receive_messages(self):
        """Receive messages from server"""
        buffer = ""
        try:
            while self.connected:
                data = self.socket.recv(4096)
                if not data:
                    break

                buffer += data.decode('utf-8')

                # Process complete messages (separated by \n)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message_data = json.loads(line)
                            message = ChatMessage.from_dict(message_data)

                            # Call callbacks
                            for callback in self.message_callbacks:
                                try:
                                    callback(message)
                                except Exception as e:
                                    self.logger.error(f"Error in message callback: {e}")
                        except json.JSONDecodeError:
                            self.logger.warning(f"Invalid JSON received: {line}")
        except Exception as e:
            if self.connected:
                self.logger.error(f"Error receiving messages: {e}")
            self.connected = False

    def on_message(self, callback: callable):
        """Register callback for received messages"""
        self.message_callbacks.append(callback)

    def update_ui_config(self, config: ChatUIConfig):
        """Update UI configuration"""
        self.ui_config = config


def main():
    """Main function - demo/test"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Local Chat System")
    parser.add_argument("--server", action="store_true", help="Run as server")
    parser.add_argument("--client", action="store_true", help="Run as client")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8888, help="Server port")
    parser.add_argument("--username", default="User", help="Username for client")

    args = parser.parse_args()

    if args.server:
        print("\n" + "=" * 80)
        print("🚀 JARVIS LOCAL CHAT SERVER")
        print("=" * 80)
        print(f"Starting server on {args.host}:{args.port}")
        print("Jarvis is taking the lead role in chat management")
        print("=" * 80 + "\n")

        server = LocalChatServer(host=args.host, port=args.port)
        try:
            server.start()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server.stop()

    elif args.client:
        print("\n" + "=" * 80)
        print("💬 JARVIS LOCAL CHAT CLIENT")
        print("=" * 80)
        print(f"Connecting as: {args.username}")
        print("=" * 80 + "\n")

        client = LocalChatClient(
            server_host=args.host,
            server_port=args.port,
            username=args.username
        )

        if client.connect():
            # Message handler
            def handle_message(message: ChatMessage):
                channel_color = client.ui_config.channel_colors.get(message.channel.value, "#FFFFFF")
                level_color = client.ui_config.level_colors.get(message.level.value, "#FFFFFF")

                timestamp = message.timestamp.strftime("%H:%M:%S") if client.ui_config.show_timestamps else ""
                channel_tag = f"[{message.channel.value.upper()}]" if client.ui_config.show_channel else ""
                level_tag = f"[{message.level.value.upper()}]" if client.ui_config.show_level else ""

                print(f"{timestamp} {channel_tag} {level_tag} {message.username}: {message.content}")

            client.on_message(handle_message)

            # Interactive input
            print("💡 Type messages and press Enter. Commands: /quit, /say, /yell, /whisper")
            print()

            try:
                while client.connected:
                    user_input = input(f"{args.username}> ").strip()

                    if not user_input:
                        continue

                    if user_input.lower() in ['/quit', '/exit', '/q']:
                        break

                    # Parse commands
                    if user_input.startswith('/say '):
                        content = user_input[5:]
                        client.send_message(content, channel=ChatChannel.SAY)
                    elif user_input.startswith('/yell '):
                        content = user_input[6:]
                        client.send_message(content, channel=ChatChannel.YELL, level=ChatLevel.WARNING)
                    elif user_input.startswith('/whisper '):
                        content = user_input[9:]
                        client.send_message(content, channel=ChatChannel.WHISPER)
                    else:
                        # Default to local chat
                        client.send_message(user_input, channel=ChatChannel.LOCAL)

                    time.sleep(0.1)  # Small delay
            except KeyboardInterrupt:
                pass
            finally:
                client.disconnect()
        else:
            print("❌ Failed to connect to server")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()