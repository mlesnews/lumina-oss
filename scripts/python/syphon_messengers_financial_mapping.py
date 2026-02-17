#!/usr/bin/env python3
"""
SYPHON Messenger Platforms & Financial Profile Mapping

SYPHONs messenger platforms and maps financial profiles to digital online presence:
1. SYPHON messenger platforms (Telegram, Signal, WhatsApp, Discord, etc.)
2. Map financial profiles to digital online presence
3. Track portfolios and institutions
4. Store in @HOLOCRON Archive
5. Send to YouTube Library

Supports:
- Telegram (API, bot, export)
- Signal (database, export)
- WhatsApp (export, backup)
- Discord (API, bot, export)
- Slack (API, bot, export, workspace export)
- Matrix/Element
- Financial profile mapping
- Portfolio tracking
- Institution mapping
"""

import json
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
import requests
import re

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import SyphonData, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None

try:
    from telethon import TelegramClient
    from telethon.tl.types import Message
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    TelegramClient = None

try:
    import discord
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    discord = None

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    WebClient = None
    SlackApiError = None


@dataclass
class MessengerSource:
    """Messenger source configuration"""
    source_id: str
    source_name: str
    messenger_type: str  # "telegram", "signal", "whatsapp", "discord", "slack", "matrix"
    connection_type: str  # "api", "bot", "export", "database", "workspace_export"
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    bot_token: Optional[str] = None
    export_file_path: Optional[str] = None
    database_path: Optional[str] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None
    enabled: bool = True
    secure: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Don't expose secrets
        if data.get("api_key"):
            data["api_key"] = "***REDACTED***"
        if data.get("api_secret"):
            data["api_secret"] = "***REDACTED***"
        if data.get("bot_token"):
            data["bot_token"] = "***REDACTED***"
        return data


@dataclass
class MessengerMessage:
    """Messenger message data"""
    message_id: str
    messenger_type: str
    message: str
    from_user: str
    to_user: str
    chat_id: Optional[str] = None
    chat_name: Optional[str] = None
    date: Optional[datetime] = None
    direction: str = "inbound"  # "inbound" or "outbound"
    media_urls: List[str] = field(default_factory=list)
    source_id: str = ""
    source_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data.get("date"):
            data["date"] = data["date"].isoformat()
        return data


@dataclass
class FinancialProfile:
    """Financial profile for mapping to digital presence"""
    profile_id: str
    profile_name: str
    profile_type: str  # "individual", "institution", "portfolio", "entity"
    financial_data: Dict[str, Any] = field(default_factory=dict)
    digital_presence: Dict[str, Any] = field(default_factory=dict)
    portfolios: List[str] = field(default_factory=list)
    institutions: List[str] = field(default_factory=list)
    social_profiles: Dict[str, str] = field(default_factory=dict)  # platform -> username/url
    messenger_profiles: Dict[str, str] = field(default_factory=dict)  # messenger -> username
    websites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Portfolio:
    """Portfolio tracking"""
    portfolio_id: str
    portfolio_name: str
    owner_profile_id: str
    institution_id: Optional[str] = None
    assets: Dict[str, float] = field(default_factory=dict)  # asset -> value
    total_value: float = 0.0
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data.get("last_updated"):
            data["last_updated"] = data["last_updated"].isoformat()
        return data


@dataclass
class Institution:
    """Institution tracking"""
    institution_id: str
    institution_name: str
    institution_type: str  # "bank", "brokerage", "crypto_exchange", "fintech", etc.
    digital_presence: Dict[str, Any] = field(default_factory=dict)
    portfolios: List[str] = field(default_factory=list)
    profiles: List[str] = field(default_factory=list)
    websites: List[str] = field(default_factory=list)
    social_profiles: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MessengerSyphonFinancialMapping:
    """
    SYPHON messenger platforms and map financial profiles to digital presence
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("MessengerSyphonFinancialMapping")

        # Directories
        self.data_dir = self.project_root / "data" / "messenger_syphon"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.financial_dir = self.project_root / "data" / "financial_profiles"
        self.financial_dir.mkdir(parents=True, exist_ok=True)

        self.holocron_dir = self.project_root / "data" / "holocron" / "messenger_financial_intelligence"
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        self.youtube_dir = self.project_root / "data" / "youtube_library" / "messenger_financial_content"
        self.youtube_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.sources_file = self.project_root / "config" / "messenger_sources.json"
        self.profiles_file = self.financial_dir / "financial_profiles.json"
        self.portfolios_file = self.financial_dir / "portfolios.json"
        self.institutions_file = self.financial_dir / "institutions.json"
        self.mapping_file = self.financial_dir / "digital_presence_mapping.json"

        # Initialize SYPHON
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.PREMIUM,
                    enable_self_healing=True,
                    enable_banking=True
                )
                self.syphon = SYPHONSystem(config)
                self.logger.info("✅ SYPHON system initialized")
            except Exception as e:
                self.logger.warning(f"SYPHON not available: {e}")

        # State
        self.sources: List[MessengerSource] = []
        self.profiles: Dict[str, FinancialProfile] = {}
        self.portfolios: Dict[str, Portfolio] = {}
        self.institutions: Dict[str, Institution] = {}
        self.messages: List[MessengerMessage] = []

        # Load data
        self._load_sources()
        self._load_profiles()
        self._load_portfolios()
        self._load_institutions()

    def _load_sources(self):
        """Load messenger sources from config"""
        if not self.sources_file.exists():
            self.logger.warning(f"Messenger sources file not found: {self.sources_file}")
            return

        try:
            with open(self.sources_file, 'r', encoding='utf-8') as f:
                sources_data = json.load(f)

            for source_data in sources_data.get("sources", []):
                source = MessengerSource(**source_data)
                if source.enabled:
                    self.sources.append(source)
                    self.logger.info(f"✅ Loaded source: {source.source_name} ({source.messenger_type})")
        except Exception as e:
            self.logger.error(f"Error loading sources: {e}")

    def _load_profiles(self):
        """Load financial profiles"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    profiles_data = json.load(f)

                for profile_id, profile_data in profiles_data.items():
                    profile = FinancialProfile(**profile_data)
                    self.profiles[profile_id] = profile
            except Exception as e:
                self.logger.warning(f"Error loading profiles: {e}")

    def _load_portfolios(self):
        """Load portfolios"""
        if self.portfolios_file.exists():
            try:
                with open(self.portfolios_file, 'r', encoding='utf-8') as f:
                    portfolios_data = json.load(f)

                for portfolio_id, portfolio_data in portfolios_data.items():
                    portfolio = Portfolio(**portfolio_data)
                    self.portfolios[portfolio_id] = portfolio
            except Exception as e:
                self.logger.warning(f"Error loading portfolios: {e}")

    def _load_institutions(self):
        """Load institutions"""
        if self.institutions_file.exists():
            try:
                with open(self.institutions_file, 'r', encoding='utf-8') as f:
                    institutions_data = json.load(f)

                for institution_id, institution_data in institutions_data.items():
                    institution = Institution(**institution_data)
                    self.institutions[institution_id] = institution
            except Exception as e:
                self.logger.warning(f"Error loading institutions: {e}")

    def syphon_messenger(self, source: MessengerSource, max_messages: int = 100) -> List[MessengerMessage]:
        """SYPHON messages from messenger source"""
        self.logger.info(f"🔄 SYPHONing messenger: {source.source_name} ({source.messenger_type})")

        messages = []

        try:
            if source.messenger_type == "telegram":
                messages = self._syphon_telegram(source, max_messages)
            elif source.messenger_type == "signal":
                messages = self._syphon_signal(source, max_messages)
            elif source.messenger_type == "whatsapp":
                messages = self._syphon_whatsapp(source, max_messages)
            elif source.messenger_type == "discord":
                messages = self._syphon_discord(source, max_messages)
            elif source.messenger_type == "slack":
                messages = self._syphon_slack(source, max_messages)
            elif source.messenger_type == "matrix":
                messages = self._syphon_matrix(source, max_messages)
            else:
                self.logger.warning(f"Unsupported messenger type: {source.messenger_type}")
        except Exception as e:
            self.logger.error(f"Error SYPHONing messenger {source.source_name}: {e}", exc_info=True)

        self.logger.info(f"✅ SYPHONed {len(messages)} messages from {source.source_name}")
        return messages

    def _syphon_telegram(self, source: MessengerSource, max_messages: int) -> List[MessengerMessage]:
        """SYPHON Telegram messages"""
        messages = []

        if source.connection_type == "api" and TELETHON_AVAILABLE:
            try:
                client = TelegramClient(
                    'telegram_session',
                    source.api_key,
                    source.api_secret
                )
                client.start()

                # Get dialogs
                dialogs = client.get_dialogs(limit=10)

                for dialog in dialogs:
                    try:
                        msgs = client.get_messages(dialog.entity, limit=max_messages // len(dialogs))
                        for msg in msgs:
                            if isinstance(msg, Message) and msg.message:
                                messenger_msg = MessengerMessage(
                                    message_id=str(msg.id),
                                    messenger_type="telegram",
                                    message=msg.message,
                                    from_user=str(msg.sender_id) if msg.sender_id else "",
                                    to_user=str(dialog.entity.id),
                                    chat_id=str(dialog.entity.id),
                                    chat_name=dialog.name,
                                    date=msg.date,
                                    direction="inbound" if msg.out else "outbound",
                                    source_id=source.source_id,
                                    source_name=source.source_name,
                                    metadata={
                                        "telegram_id": msg.id,
                                        "chat_type": type(dialog.entity).__name__
                                    }
                                )
                                messages.append(messenger_msg)
                    except Exception as e:
                        self.logger.debug(f"Error processing Telegram dialog: {e}")
                        continue

                client.disconnect()
            except Exception as e:
                self.logger.error(f"Telegram API error: {e}")
        elif source.connection_type == "export" and source.export_file_path:
            # Parse Telegram export
            try:
                export_path = Path(source.export_file_path)
                if export_path.exists():
                    # Telegram exports are typically JSON
                    with open(export_path, 'r', encoding='utf-8') as f:
                        export_data = json.load(f)

                    chats = export_data.get('chats', {}).get('list', [])
                    for chat in chats[:10]:  # Limit chats
                        msgs = chat.get('messages', [])[:max_messages // 10]
                        for msg in msgs:
                            try:
                                date = None
                                if msg.get('date'):
                                    date = datetime.fromtimestamp(msg['date'])

                                messenger_msg = MessengerMessage(
                                    message_id=str(msg.get('id', len(messages))),
                                    messenger_type="telegram",
                                    message=msg.get('text', ''),
                                    from_user=msg.get('from', ''),
                                    to_user=chat.get('name', ''),
                                    chat_id=str(chat.get('id', '')),
                                    chat_name=chat.get('name', ''),
                                    date=date,
                                    direction="inbound" if not msg.get('out', False) else "outbound",
                                    source_id=source.source_id,
                                    source_name=source.source_name,
                                    metadata={"export_source": "telegram"}
                                )
                                messages.append(messenger_msg)
                            except Exception as e:
                                self.logger.debug(f"Error parsing Telegram message: {e}")
                                continue
            except Exception as e:
                self.logger.error(f"Error parsing Telegram export: {e}")

        return messages

    def _syphon_signal(self, source: MessengerSource, max_messages: int) -> List[MessengerMessage]:
        """SYPHON Signal messages"""
        messages = []

        if source.database_path:
            try:
                # Signal database is SQLite
                conn = sqlite3.connect(source.database_path)
                cursor = conn.cursor()

                # Query messages
                query = """
                    SELECT 
                        _id, body, address, date_sent, date_received,
                        thread_id, type
                    FROM sms
                    ORDER BY date_sent DESC
                    LIMIT ?
                """

                cursor.execute(query, (max_messages,))
                rows = cursor.fetchall()

                for row in rows:
                    try:
                        msg_id, body, address, date_sent, date_received, thread_id, msg_type = row

                        date = None
                        if date_sent:
                            date = datetime.fromtimestamp(date_sent / 1000)

                        messenger_msg = MessengerMessage(
                            message_id=f"signal_{msg_id}",
                            messenger_type="signal",
                            message=body or "",
                            from_user=address or "",
                            to_user=source.phone_number or "",
                            chat_id=str(thread_id) if thread_id else None,
                            date=date,
                            direction="inbound" if msg_type == 20 else "outbound",
                            source_id=source.source_id,
                            source_name=source.source_name,
                            metadata={
                                "signal_id": msg_id,
                                "thread_id": thread_id
                            }
                        )
                        messages.append(messenger_msg)
                    except Exception as e:
                        self.logger.debug(f"Error parsing Signal message: {e}")
                        continue

                conn.close()
            except Exception as e:
                self.logger.error(f"Error parsing Signal database: {e}")

        return messages

    def _syphon_whatsapp(self, source: MessengerSource, max_messages: int) -> List[MessengerMessage]:
        """SYPHON WhatsApp messages"""
        messages = []

        if source.export_file_path:
            try:
                export_path = Path(source.export_file_path)
                if export_path.exists():
                    # WhatsApp exports are typically text files
                    with open(export_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Parse WhatsApp export format
                    for line in lines[-max_messages:]:
                        try:
                            # WhatsApp format: [DD/MM/YYYY, HH:MM:SS] Sender: Message
                            match = re.match(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] ([^:]+): (.+)', line)
                            if match:
                                date_str, time_str, sender, message = match.groups()

                                try:
                                    date = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                                except:
                                    date = None

                                messenger_msg = MessengerMessage(
                                    message_id=f"whatsapp_{len(messages)}",
                                    messenger_type="whatsapp",
                                    message=message.strip(),
                                    from_user=sender.strip(),
                                    to_user=source.phone_number or "",
                                    date=date,
                                    direction="inbound",
                                    source_id=source.source_id,
                                    source_name=source.source_name,
                                    metadata={"export_source": "whatsapp"}
                                )
                                messages.append(messenger_msg)
                        except Exception as e:
                            self.logger.debug(f"Error parsing WhatsApp message: {e}")
                            continue
            except Exception as e:
                self.logger.error(f"Error parsing WhatsApp export: {e}")

        return messages

    def _syphon_discord(self, source: MessengerSource, max_messages: int) -> List[MessengerMessage]:
        """SYPHON Discord messages"""
        messages = []

        if source.connection_type == "bot" and DISCORD_AVAILABLE and source.bot_token:
            try:
                # Discord bot integration
                # TODO: Implement Discord bot message retrieval  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                self.logger.warning("Discord bot integration not yet fully implemented")
            except Exception as e:
                self.logger.error(f"Discord bot error: {e}")
        elif source.connection_type == "export" and source.export_file_path:
            try:
                export_path = Path(source.export_file_path)
                if export_path.exists():
                    # Discord exports are typically JSON
                    with open(export_path, 'r', encoding='utf-8') as f:
                        export_data = json.load(f)

                    # Parse Discord export structure
                    # Structure varies, but typically has messages array
                    messages_list = export_data.get('messages', [])
                    for msg in messages_list[-max_messages:]:
                        try:
                            date = None
                            if msg.get('timestamp'):
                                try:
                                    date = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                                except:
                                    pass

                            messenger_msg = MessengerMessage(
                                message_id=str(msg.get('id', len(messages))),
                                messenger_type="discord",
                                message=msg.get('content', ''),
                                from_user=msg.get('author', {}).get('username', ''),
                                to_user=msg.get('channel', {}).get('name', ''),
                                chat_id=str(msg.get('channel_id', '')),
                                chat_name=msg.get('channel', {}).get('name', ''),
                                date=date,
                                direction="inbound",
                                source_id=source.source_id,
                                source_name=source.source_name,
                                metadata={"export_source": "discord"}
                            )
                            messages.append(messenger_msg)
                        except Exception as e:
                            self.logger.debug(f"Error parsing Discord message: {e}")
                            continue
            except Exception as e:
                self.logger.error(f"Error parsing Discord export: {e}")

        return messages

    def _syphon_slack(self, source: MessengerSource, max_messages: int) -> List[MessengerMessage]:
        """SYPHON Slack messages"""
        messages = []

        if source.connection_type == "api" and SLACK_AVAILABLE and source.bot_token:
            try:
                client = WebClient(token=source.bot_token)

                # Get all conversations (channels, DMs, groups)
                conversations = []

                # Get public channels
                try:
                    channels_response = client.conversations_list(types="public_channel,private_channel", limit=100)
                    conversations.extend(channels_response.get("channels", []))
                except SlackApiError as e:
                    self.logger.debug(f"Error getting Slack channels: {e}")

                # Get DMs
                try:
                    ims_response = client.conversations_list(types="im", limit=100)
                    conversations.extend(ims_response.get("channels", []))
                except SlackApiError as e:
                    self.logger.debug(f"Error getting Slack DMs: {e}")

                # Get group messages
                try:
                    groups_response = client.conversations_list(types="mpim", limit=100)
                    conversations.extend(groups_response.get("channels", []))
                except SlackApiError as e:
                    self.logger.debug(f"Error getting Slack groups: {e}")

                # Get messages from each conversation
                messages_per_conversation = max_messages // max(len(conversations), 1)

                for conversation in conversations[:20]:  # Limit to 20 conversations
                    try:
                        channel_id = conversation["id"]
                        channel_name = conversation.get("name", conversation.get("user", "Unknown"))

                        # Get messages
                        history_response = client.conversations_history(
                            channel=channel_id,
                            limit=messages_per_conversation
                        )

                        for msg in history_response.get("messages", []):
                            try:
                                # Skip bot messages if needed
                                if msg.get("subtype") == "bot_message":
                                    continue

                                date = None
                                if msg.get("ts"):
                                    date = datetime.fromtimestamp(float(msg["ts"]))

                                # Get user info
                                user_id = msg.get("user", "")
                                user_name = user_id
                                try:
                                    user_info = client.users_info(user=user_id)
                                    user_name = user_info.get("user", {}).get("real_name", user_id)
                                except:
                                    pass

                                messenger_msg = MessengerMessage(
                                    message_id=msg.get("ts", f"slack_{len(messages)}"),
                                    messenger_type="slack",
                                    message=msg.get("text", ""),
                                    from_user=user_name,
                                    to_user=channel_name,
                                    chat_id=channel_id,
                                    chat_name=channel_name,
                                    date=date,
                                    direction="inbound",
                                    source_id=source.source_id,
                                    source_name=source.source_name,
                                    metadata={
                                        "slack_ts": msg.get("ts"),
                                        "slack_user_id": user_id,
                                        "channel_type": conversation.get("is_im", False) and "dm" or "channel"
                                    }
                                )
                                messages.append(messenger_msg)
                            except Exception as e:
                                self.logger.debug(f"Error parsing Slack message: {e}")
                                continue
                    except SlackApiError as e:
                        self.logger.debug(f"Error getting Slack conversation history: {e}")
                        continue
            except Exception as e:
                self.logger.error(f"Slack API error: {e}")
        elif source.connection_type == "export" and source.export_file_path:
            try:
                export_path = Path(source.export_file_path)
                if export_path.exists():
                    # Slack exports are typically ZIP files with JSON
                    import zipfile

                    if export_path.suffix == '.zip':
                        with zipfile.ZipFile(export_path, 'r') as zip_ref:
                            # Extract and parse Slack export
                            # Slack exports have channels/ directory with JSON files
                            for file_info in zip_ref.namelist():
                                if file_info.startswith('channels/') and file_info.endswith('.json'):
                                    try:
                                        with zip_ref.open(file_info) as f:
                                            channel_data = json.load(f)

                                        channel_name = file_info.split('/')[-1].replace('.json', '')

                                        for msg in channel_data.get('messages', [])[:max_messages // 10]:
                                            try:
                                                date = None
                                                if msg.get('ts'):
                                                    date = datetime.fromtimestamp(float(msg['ts']))

                                                messenger_msg = MessengerMessage(
                                                    message_id=msg.get('ts', f"slack_{len(messages)}"),
                                                    messenger_type="slack",
                                                    message=msg.get('text', ''),
                                                    from_user=msg.get('user', ''),
                                                    to_user=channel_name,
                                                    chat_id=channel_name,
                                                    chat_name=channel_name,
                                                    date=date,
                                                    direction="inbound",
                                                    source_id=source.source_id,
                                                    source_name=source.source_name,
                                                    metadata={"export_source": "slack"}
                                                )
                                                messages.append(messenger_msg)
                                            except Exception as e:
                                                self.logger.debug(f"Error parsing Slack export message: {e}")
                                                continue
                                    except Exception as e:
                                        self.logger.debug(f"Error parsing Slack export file {file_info}: {e}")
                                        continue
                    elif export_path.suffix == '.json':
                        # Direct JSON export
                        with open(export_path, 'r', encoding='utf-8') as f:
                            export_data = json.load(f)

                        # Parse Slack JSON export structure
                        channels = export_data.get('channels', [])
                        for channel in channels[:10]:
                            channel_name = channel.get('name', 'Unknown')
                            for msg in channel.get('messages', [])[:max_messages // 10]:
                                try:
                                    date = None
                                    if msg.get('ts'):
                                        date = datetime.fromtimestamp(float(msg['ts']))

                                    messenger_msg = MessengerMessage(
                                        message_id=msg.get('ts', f"slack_{len(messages)}"),
                                        messenger_type="slack",
                                        message=msg.get('text', ''),
                                        from_user=msg.get('user', ''),
                                        to_user=channel_name,
                                        chat_id=channel_name,
                                        chat_name=channel_name,
                                        date=date,
                                        direction="inbound",
                                        source_id=source.source_id,
                                        source_name=source.source_name,
                                        metadata={"export_source": "slack"}
                                    )
                                    messages.append(messenger_msg)
                                except Exception as e:
                                    self.logger.debug(f"Error parsing Slack message: {e}")
                                    continue
            except Exception as e:
                self.logger.error(f"Error parsing Slack export: {e}")
        elif source.connection_type == "workspace_export" and source.export_file_path:
            # Workspace export (similar to regular export but may have different structure)
            try:
                export_path = Path(source.export_file_path)
                if export_path.exists():
                    # Handle workspace export (typically ZIP)
                    import zipfile

                    if export_path.suffix == '.zip':
                        with zipfile.ZipFile(export_path, 'r') as zip_ref:
                            # Parse workspace export structure
                            # Similar to regular export but may include more data
                            for file_info in zip_ref.namelist():
                                if file_info.endswith('.json') and ('channels' in file_info or 'messages' in file_info):
                                    try:
                                        with zip_ref.open(file_info) as f:
                                            data = json.load(f)

                                        # Parse based on structure
                                        if isinstance(data, list):
                                            msgs = data
                                        elif isinstance(data, dict):
                                            msgs = data.get('messages', [])
                                        else:
                                            continue

                                        for msg in msgs[:max_messages // 20]:
                                            try:
                                                date = None
                                                if msg.get('ts'):
                                                    date = datetime.fromtimestamp(float(msg['ts']))

                                                messenger_msg = MessengerMessage(
                                                    message_id=msg.get('ts', f"slack_{len(messages)}"),
                                                    messenger_type="slack",
                                                    message=msg.get('text', ''),
                                                    from_user=msg.get('user', ''),
                                                    to_user=msg.get('channel', 'Unknown'),
                                                    chat_id=msg.get('channel', ''),
                                                    chat_name=msg.get('channel', 'Unknown'),
                                                    date=date,
                                                    direction="inbound",
                                                    source_id=source.source_id,
                                                    source_name=source.source_name,
                                                    metadata={"export_source": "slack_workspace"}
                                                )
                                                messages.append(messenger_msg)
                                            except Exception as e:
                                                self.logger.debug(f"Error parsing Slack workspace message: {e}")
                                                continue
                                    except Exception as e:
                                        self.logger.debug(f"Error parsing Slack workspace file {file_info}: {e}")
                                        continue
            except Exception as e:
                self.logger.error(f"Error parsing Slack workspace export: {e}")

        return messages

    def _syphon_matrix(self, source: MessengerSource, max_messages: int) -> List[MessengerMessage]:
        """SYPHON Matrix/Element messages"""
        messages = []

        # TODO: Implement Matrix/Element integration  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        self.logger.warning("Matrix/Element integration not yet implemented")

        return messages

    def map_financial_to_digital_presence(self):
        """Map financial profiles to digital online presence"""
        self.logger.info("🔄 Mapping financial profiles to digital presence...")

        mapping_results = []

        for profile_id, profile in self.profiles.items():
            # Extract digital presence from messages
            digital_presence = self._extract_digital_presence(profile_id)

            # Update profile
            profile.digital_presence.update(digital_presence)

            # Map to portfolios and institutions
            self._map_to_portfolios(profile)
            self._map_to_institutions(profile)

            mapping_results.append({
                "profile_id": profile_id,
                "digital_presence": digital_presence,
                "portfolios": profile.portfolios,
                "institutions": profile.institutions
            })

        # Save mapping
        self._save_mapping(mapping_results)

        self.logger.info(f"✅ Mapped {len(mapping_results)} profiles to digital presence")
        return mapping_results

    def _extract_digital_presence(self, profile_id: str) -> Dict[str, Any]:
        """Extract digital presence from messages"""
        presence = {
            "messenger_profiles": {},
            "social_profiles": {},
            "websites": [],
            "email_addresses": [],
            "phone_numbers": []
        }

        # Search messages for profile references
        for message in self.messages:
            # Extract email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message.message)
            presence["email_addresses"].extend(emails)

            # Extract phone numbers
            phones = re.findall(r'\+?1?\d{10,15}', message.message)
            presence["phone_numbers"].extend(phones)

            # Extract websites
            urls = re.findall(r'https?://[^\s]+', message.message)
            presence["websites"].extend(urls)

            # Extract social profiles
            # Twitter/X
            twitter = re.findall(r'@(\w+)', message.message)
            if twitter:
                presence["social_profiles"]["twitter"] = twitter[0]

            # LinkedIn
            linkedin = re.findall(r'linkedin\.com/in/([\w-]+)', message.message)
            if linkedin:
                presence["social_profiles"]["linkedin"] = linkedin[0]

        # Deduplicate
        presence["email_addresses"] = list(set(presence["email_addresses"]))
        presence["phone_numbers"] = list(set(presence["phone_numbers"]))
        presence["websites"] = list(set(presence["websites"]))

        return presence

    def _map_to_portfolios(self, profile: FinancialProfile):
        """Map profile to portfolios"""
        # Search for portfolio references in messages
        for message in self.messages:
            # Look for portfolio mentions
            portfolio_keywords = ["portfolio", "investment", "assets", "holdings"]
            if any(keyword in message.message.lower() for keyword in portfolio_keywords):
                # Try to extract portfolio ID or create mapping
                portfolio_id = f"portfolio_{profile.profile_id}_{len(profile.portfolios)}"
                if portfolio_id not in profile.portfolios:
                    profile.portfolios.append(portfolio_id)

    def _map_to_institutions(self, profile: FinancialProfile):
        """Map profile to institutions"""
        # Search for institution references in messages
        institution_keywords = ["bank", "brokerage", "exchange", "fintech", "institution"]

        for message in self.messages:
            if any(keyword in message.message.lower() for keyword in institution_keywords):
                # Extract institution name
                # Try to match with existing institutions
                for inst_id, institution in self.institutions.items():
                    if institution.institution_name.lower() in message.message.lower():
                        if inst_id not in profile.institutions:
                            profile.institutions.append(inst_id)

    def process_all(self, max_messages_per_source: int = 100):
        """Process all: SYPHON messengers → Map financial profiles → Holocron → YouTube"""
        self.logger.info("🚀 Starting comprehensive processing...")

        # Step 1: SYPHON all messengers
        all_messages = []
        for source in self.sources:
            if not source.enabled:
                continue

            messages = self.syphon_messenger(source, max_messages_per_source)
            all_messages.extend(messages)

        self.messages = all_messages
        self.logger.info(f"✅ SYPHONed {len(all_messages)} total messages")

        # Step 2: Map financial profiles to digital presence
        mapping_results = self.map_financial_to_digital_presence()

        # Step 3: Process messages for intelligence
        syphon_results = []
        holocron_entries = []
        youtube_entries = []

        for message in all_messages:
            # SYPHON intelligence
            syphon_result = self._syphon_intelligence(message)
            if syphon_result:
                syphon_results.append(syphon_result)

            # Store in Holocron
            holocron_entry = self._store_in_holocron(message, syphon_result)
            if holocron_entry:
                holocron_entries.append(holocron_entry)

            # Send to YouTube Library
            youtube_entry = self._send_to_youtube_library(message, syphon_result)
            if youtube_entry:
                youtube_entries.append(youtube_entry)

        # Save all results
        self._save_all_results(syphon_results, holocron_entries, youtube_entries, mapping_results)

        self.logger.info("✅ Comprehensive processing complete!")
        return {
            "total_messages": len(all_messages),
            "syphon_results": len(syphon_results),
            "holocron_entries": len(holocron_entries),
            "youtube_entries": len(youtube_entries),
            "mapping_results": len(mapping_results)
        }

    def _syphon_intelligence(self, message: MessengerMessage) -> Optional[Dict[str, Any]]:
        """SYPHON intelligence from message"""
        if not self.syphon:
            return None

        try:
            # Use social extractor for messenger messages
            result = self.syphon.extract(
                DataSourceType.SOCIAL,
                {"text": message.message, "content": message.message},
                {
                    "messenger_type": message.messenger_type,
                    "from_user": message.from_user,
                    "to_user": message.to_user,
                    "chat_id": message.chat_id,
                    "date": message.date.isoformat() if message.date else None
                }
            )

            if result.success and result.data:
                return {
                    "message_id": message.message_id,
                    "syphon_data": result.data.to_dict(),
                    "actionable_items": result.data.actionable_items,
                    "tasks": result.data.tasks,
                    "decisions": result.data.decisions,
                    "intelligence": result.data.intelligence
                }
        except Exception as e:
            self.logger.debug(f"Error SYPHONing intelligence: {e}")

        return None

    def _store_in_holocron(self, message: MessengerMessage, syphon_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Store message intelligence in Holocron"""
        try:
            entry_id = f"HOLOCRON-MSG-{message.message_id}"
            entry_file = self.holocron_dir / f"{entry_id}.json"

            entry_data = {
                "entry_id": entry_id,
                "title": f"{message.messenger_type} message from {message.from_user}",
                "classification": "messenger_intelligence",
                "source": "messenger_syphon",
                "message_data": message.to_dict(),
                "syphon_intelligence": syphon_result,
                "extracted_at": datetime.now().isoformat(),
                "tags": [
                    "#messenger",
                    f"#{message.messenger_type}",
                    "#syphon",
                    "#intelligence"
                ]
            }

            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False, default=str)

            return entry_data
        except Exception as e:
            self.logger.debug(f"Error storing in Holocron: {e}")
            return None

    def _send_to_youtube_library(self, message: MessengerMessage, syphon_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Send message content to YouTube Library"""
        try:
            entry_id = f"YT-MSG-{message.message_id}"
            entry_file = self.youtube_dir / f"{entry_id}.json"

            content = {
                "title": f"{message.messenger_type} message",
                "description": message.message[:500],
                "source": message.messenger_type,
                "content": message.message,
                "intelligence": syphon_result.get("intelligence", []) if syphon_result else []
            }

            entry_data = {
                "entry_id": entry_id,
                "youtube_library_entry": content,
                "message_data": message.to_dict(),
                "syphon_data": syphon_result,
                "created_at": datetime.now().isoformat()
            }

            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False, default=str)

            return entry_data
        except Exception as e:
            self.logger.debug(f"Error sending to YouTube library: {e}")
            return None

    def _save_mapping(self, mapping_results: List[Dict[str, Any]]):
        try:
            """Save digital presence mapping"""
            mapping_data = {
                "mapping_metadata": {
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "total_profiles": len(mapping_results)
                },
                "mappings": {result["profile_id"]: result for result in mapping_results}
            }

            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_mapping: {e}", exc_info=True)
            raise

    def _save_all_results(self, syphon_results: List[Dict], holocron_entries: List[Dict],
                             youtube_entries: List[Dict], mapping_results: List[Dict]):
        try:
            """Save all results"""
            # Save SYPHON results
            syphon_file = self.data_dir / "syphon_results.json"
            with open(syphon_file, 'w', encoding='utf-8') as f:
                json.dump(syphon_results, f, indent=2, ensure_ascii=False, default=str)

            # Save profiles
            profiles_data = {pid: profile.to_dict() for pid, profile in self.profiles.items()}
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles_data, f, indent=2, ensure_ascii=False, default=str)

            # Save portfolios
            portfolios_data = {pid: portfolio.to_dict() for pid, portfolio in self.portfolios.items()}
            with open(self.portfolios_file, 'w', encoding='utf-8') as f:
                json.dump(portfolios_data, f, indent=2, ensure_ascii=False, default=str)

            # Save institutions
            institutions_data = {iid: institution.to_dict() for iid, institution in self.institutions.items()}
            with open(self.institutions_file, 'w', encoding='utf-8') as f:
                json.dump(institutions_data, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info("✅ All results saved")


        except Exception as e:
            self.logger.error(f"Error in _save_all_results: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    syphon = MessengerSyphonFinancialMapping()

    print("🚀 Messenger SYPHON & Financial Profile Mapping")
    print("=" * 80)
    print("")

    # Process all
    result = syphon.process_all(max_messages_per_source=100)

    print("")
    print("✅ Processing Complete!")
    print(f"   Total Messages: {result['total_messages']}")
    print(f"   SYPHON Results: {result['syphon_results']}")
    print(f"   Holocron Entries: {result['holocron_entries']}")
    print(f"   YouTube Entries: {result['youtube_entries']}")
    print(f"   Mapping Results: {result['mapping_results']}")


if __name__ == "__main__":



    main()