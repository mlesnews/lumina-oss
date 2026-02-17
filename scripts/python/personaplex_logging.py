#!/usr/bin/env python3
"""PERSONAPLEX Logging - MariaDB + Slack Notifications"""
import json, logging, time, os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

@dataclass
class LogEntry:
    entry_id: str
    timestamp: datetime
    level: LogLevel
    source: str
    message: str
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

class MariaDBHandler:
    def __init__(self, host: str = "<NAS_PRIMARY_IP>", port: int = 8097, database: str = "lumina_logs"):
        self.host = host
        self.port = port
        self.database = database
        self._connection = None

    def connect(self) -> bool:
        try:
            import pymysql
            import subprocess
            pw = subprocess.run(
                ["az", "keyvault", "secret", "show", "--vault-name", "jarvis-lumina",
                 "--name", "mariadb-dbadmin-password", "--query", "value", "-o", "tsv"],
                capture_output=True, text=True, timeout=30
            ).stdout.strip().replace("\r", "")
            self._connection = pymysql.connect(host=self.host, port=self.port, user="dbadmin", password=pw, database=self.database, autocommit=True)
            return True
        except Exception:
            return False

    def log(self, entry: LogEntry) -> bool:
        if not self._connection and not self.connect():
            return False
        try:
            import pymysql
            with self._connection.cursor() as cursor:
                cursor.execute("INSERT INTO log_entries (entry_id, timestamp, level, source, message, category, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", (entry.entry_id, entry.timestamp, entry.level.name, entry.source, entry.message, entry.category, json.dumps(entry.metadata)))
            return True
        except:
            return False

class SlackHandler:
    def __init__(self, webhook_url: Optional[str] = None, channel: str = "#personaplex"):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        self.channel = channel

    def log(self, entry: LogEntry) -> bool:
        if not self.webhook_url:
            return False
        try:
            import requests
            emoji = {LogLevel.DEBUG: ":mag:", LogLevel.INFO: ":information_source:", LogLevel.WARNING: ":warning:", LogLevel.ERROR: ":x:", LogLevel.CRITICAL: ":rotating_light:"}
            payload = {"channel": self.channel, "username": "PERSONAPLEX Logger", "icon_emoji": emoji.get(entry.level, ":information_source:"), "text": f"[{entry.level.name}] {entry.source}: {entry.message}"}
            r = requests.post(self.webhook_url, json=payload, timeout=10)
            return r.status_code == 200
        except:
            return False

class PersonaplexLogger:
    def __init__(self, source: str = "personaplex", use_mariadb: bool = True, use_slack: bool = True):
        self.source = source
        self.log_level = LogLevel.INFO
        self._maria = MariaDBHandler() if use_mariadb else None
        self._slack = SlackHandler() if use_slack else None
        self._history: List[LogEntry] = []
        logger.info("PersonaplexLogger initialized")

    def log(self, message: str, level: LogLevel = LogLevel.INFO, category: str = "general", metadata: Optional[Dict] = None) -> LogEntry:
        entry = LogEntry(entry_id=f"log-{int(time.time()*1000)}", timestamp=datetime.utcnow(), level=level, source=self.source, message=message, category=category, metadata=metadata or {})
        self._history.append(entry)
        self._history = self._history[-1000:]
        if self._maria:
            self._maria.log(entry)
        if self._slack and level.value >= LogLevel.WARNING.value:
            self._slack.log(entry)
        log_msg = f"[{level.name}] {self.source}: {message}"
        if level.value >= LogLevel.ERROR.value:
            logger.error(log_msg)
        elif level.value >= LogLevel.WARNING.value:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        return entry

    def info(self, message: str, **kwargs) -> LogEntry:
        return self.log(message, level=LogLevel.INFO, **kwargs)

    def warning(self, message: str, **kwargs) -> LogEntry:
        return self.log(message, level=LogLevel.WARNING, **kwargs)

    def error(self, message: str, **kwargs) -> LogEntry:
        return self.log(message, level=LogLevel.ERROR, **kwargs)

    def get_statistics(self) -> dict:
        by_level = {}
        by_category = {}
        for e in self._history:
            by_level[e.level.name] = by_level.get(e.level.name, 0) + 1
            by_category[e.category] = by_category.get(e.category, 0) + 1
        return {"total": len(self._history), "by_level": by_level, "by_category": by_category}

def create_logger(source: str = "personaplex", use_mariadb: bool = True, use_slack: bool = True) -> PersonaplexLogger:
    return PersonaplexLogger(source=source, use_mariadb=use_mariadb, use_slack=use_slack)

if __name__ == "__main__":
    l = create_logger()
    l.info("Test info", category="test")
    l.warning("Test warning", category="test")
    l.error("Test error", category="test")
    print(f"Stats: {l.get_statistics()}")
    print("PERSONAPLEX Logging initialized!")
