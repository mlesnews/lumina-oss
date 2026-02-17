#!/usr/bin/env python3
"""
AI Technology Heartbeat Watchdog

"WE MUST ESTABLISH A HEARTBEAT WATCHDOG ON 'AI TECHNOLOGY' FROM ALL @ASKS AND @SOURCES."

This system:
- Monitors all @ASKS and @SOURCES for "AI Technology" mentions
- Implements heartbeat/watchdog pattern
- Tracks status and alerts on issues
- Provides real-time monitoring dashboard
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AITechnologyHeartbeatWatchdog")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class HeartbeatStatus(Enum):
    """Heartbeat status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DEAD = "dead"
    UNKNOWN = "unknown"


class SourceType(Enum):
    """Source types"""
    ASKS = "asks"
    SOURCES = "sources"
    BOTH = "both"


@dataclass
class Heartbeat:
    """Heartbeat record"""
    heartbeat_id: str
    source_id: str
    source_type: SourceType
    timestamp: datetime
    status: HeartbeatStatus
    ai_technology_mentioned: bool = False
    ai_technology_context: Optional[str] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["source_type"] = self.source_type.value
        data["status"] = self.status.value
        return data


@dataclass
class WatchdogConfig:
    """Watchdog configuration"""
    heartbeat_interval_seconds: float = 30.0
    timeout_seconds: float = 60.0
    warning_threshold_seconds: float = 45.0
    critical_threshold_seconds: float = 90.0
    max_missed_heartbeats: int = 3
    monitor_ai_technology: bool = True
    ai_technology_keywords: List[str] = field(default_factory=lambda: [
        "AI Technology",
        "artificial intelligence",
        "machine learning",
        "AI",
        "ML",
        "deep learning",
        "neural network",
        "GPT",
        "LLM",
        "AI model",
        "AI system"
    ])
    enabled: bool = True


@dataclass
class SourceStatus:
    """Source status"""
    source_id: str
    source_type: SourceType
    last_heartbeat: Optional[datetime] = None
    status: HeartbeatStatus = HeartbeatStatus.UNKNOWN
    consecutive_misses: int = 0
    total_heartbeats: int = 0
    ai_technology_mentions: int = 0
    last_ai_technology_mention: Optional[datetime] = None
    average_response_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["last_heartbeat"] = self.last_heartbeat.isoformat() if self.last_heartbeat else None
        data["source_type"] = self.source_type.value
        data["status"] = self.status.value
        data["last_ai_technology_mention"] = self.last_ai_technology_mention.isoformat() if self.last_ai_technology_mention else None
        return data


class AITechnologyHeartbeatWatchdog:
    """
    AI Technology Heartbeat Watchdog

    "WE MUST ESTABLISH A HEARTBEAT WATCHDOG ON 'AI TECHNOLOGY' FROM ALL @ASKS AND @SOURCES."
    """

    def __init__(self, project_root: Optional[Path] = None, config: Optional[WatchdogConfig] = None):
        """Initialize AI Technology Heartbeat Watchdog"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("AITechnologyHeartbeatWatchdog")
        self.config = config or WatchdogConfig()

        # Source tracking
        self.sources: Dict[str, SourceStatus] = {}
        self.heartbeats: List[Heartbeat] = []

        # Monitoring
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Data storage
        self.data_dir = self.project_root / "data" / "ai_technology_heartbeat_watchdog"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Discover sources
        self._discover_sources()

        self.logger.info("💓 AI Technology Heartbeat Watchdog initialized")
        self.logger.info("   Monitoring all @ASKS and @SOURCES for 'AI Technology'")

    def _discover_sources(self):
        """Discover all @ASKS and @SOURCES"""
        # Discover @ASKS sources
        asks_sources = self._discover_asks_sources()
        for source_id in asks_sources:
            self.sources[source_id] = SourceStatus(
                source_id=source_id,
                source_type=SourceType.ASKS
            )

        # Discover @SOURCES
        sources_list = self._discover_sources_list()
        for source_id in sources_list:
            if source_id not in self.sources:
                self.sources[source_id] = SourceStatus(
                    source_id=source_id,
                    source_type=SourceType.SOURCES
                )

        self.logger.info(f"  ✅ Discovered {len(self.sources)} sources")
        self.logger.info(f"     @ASKS: {len([s for s in self.sources.values() if s.source_type == SourceType.ASKS])}")
        self.logger.info(f"     @SOURCES: {len([s for s in self.sources.values() if s.source_type == SourceType.SOURCES])}")

    def _discover_asks_sources(self) -> List[str]:
        """Discover @ASKS sources"""
        asks_sources = []

        # Look for ASKS-related files and systems
        asks_patterns = [
            "asks",
            "ask",
            "query",
            "request",
            "prompt"
        ]

        # Check for common ASKS implementations
        potential_sources = [
            "jarvis_asks",
            "lumina_asks",
            "ai_asks",
            "system_asks",
            "user_asks"
        ]

        for source in potential_sources:
            asks_sources.append(source)

        return asks_sources

    def _discover_sources_list(self) -> List[str]:
        """Discover @SOURCES"""
        sources = []

        # Look for SOURCES-related files and systems
        potential_sources = [
            "syphon_sources",
            "data_sources",
            "intelligence_sources",
            "knowledge_sources",
            "r5_sources",
            "external_sources",
            "api_sources"
        ]

        for source in potential_sources:
            sources.append(source)

        return sources

    def register_source(self, source_id: str, source_type: SourceType):
        """Register a source for monitoring"""
        with self.lock:
            if source_id not in self.sources:
                self.sources[source_id] = SourceStatus(
                    source_id=source_id,
                    source_type=source_type
                )
                self.logger.info(f"  ✅ Registered source: {source_id} ({source_type.value})")
            else:
                self.logger.debug(f"  Source already registered: {source_id}")

    def record_heartbeat(self, source_id: str, content: Optional[str] = None,
                        response_time_ms: Optional[float] = None,
                        error: Optional[str] = None) -> Heartbeat:
        """Record a heartbeat from a source"""
        with self.lock:
            if source_id not in self.sources:
                self.register_source(source_id, SourceType.BOTH)

            source_status = self.sources[source_id]
            now = datetime.now()

            # Check for AI Technology mentions
            ai_technology_mentioned = False
            ai_technology_context = None

            if self.config.monitor_ai_technology and content:
                ai_technology_mentioned, ai_technology_context = self._check_ai_technology(content)

            # Determine status
            if error:
                status = HeartbeatStatus.CRITICAL
            elif response_time_ms and response_time_ms > self.config.critical_threshold_seconds * 1000:
                status = HeartbeatStatus.CRITICAL
            elif response_time_ms and response_time_ms > self.config.warning_threshold_seconds * 1000:
                status = HeartbeatStatus.WARNING
            else:
                status = HeartbeatStatus.HEALTHY

            # Create heartbeat
            heartbeat = Heartbeat(
                heartbeat_id=f"heartbeat_{int(now.timestamp())}_{source_id}",
                source_id=source_id,
                source_type=source_status.source_type,
                timestamp=now,
                status=status,
                ai_technology_mentioned=ai_technology_mentioned,
                ai_technology_context=ai_technology_context,
                response_time_ms=response_time_ms,
                error=error
            )

            # Update source status
            source_status.last_heartbeat = now
            source_status.status = status
            source_status.total_heartbeats += 1
            source_status.consecutive_misses = 0

            if ai_technology_mentioned:
                source_status.ai_technology_mentions += 1
                source_status.last_ai_technology_mention = now

            if response_time_ms:
                # Update average response time
                if source_status.average_response_time_ms == 0:
                    source_status.average_response_time_ms = response_time_ms
                else:
                    source_status.average_response_time_ms = (
                        source_status.average_response_time_ms * 0.9 + response_time_ms * 0.1
                    )

            if error:
                source_status.errors.append(f"{now.isoformat()}: {error}")
                if len(source_status.errors) > 10:
                    source_status.errors.pop(0)

            # Store heartbeat
            self.heartbeats.append(heartbeat)
            if len(self.heartbeats) > 1000:
                self.heartbeats.pop(0)

            # Save heartbeat
            self._save_heartbeat(heartbeat)

            self.logger.debug(f"  💓 Heartbeat recorded: {source_id} ({status.value})")
            if ai_technology_mentioned:
                self.logger.info(f"  🤖 AI Technology mentioned in {source_id}")

            return heartbeat

    def _check_ai_technology(self, content: str) -> tuple[bool, Optional[str]]:
        """Check if content mentions AI Technology"""
        content_lower = content.lower()

        for keyword in self.config.ai_technology_keywords:
            if keyword.lower() in content_lower:
                # Extract context (surrounding text)
                keyword_index = content_lower.find(keyword.lower())
                start = max(0, keyword_index - 50)
                end = min(len(content), keyword_index + len(keyword) + 50)
                context = content[start:end]

                return True, context

        return False, None

    def check_heartbeats(self):
        """Check all sources for missed heartbeats"""
        with self.lock:
            now = datetime.now()
            for source_id, source_status in self.sources.items():
                if source_status.last_heartbeat:
                    time_since_last = (now - source_status.last_heartbeat).total_seconds()

                    if time_since_last > self.config.critical_threshold_seconds:
                        source_status.status = HeartbeatStatus.CRITICAL
                        source_status.consecutive_misses += 1
                        self.logger.warning(f"  ⚠️  CRITICAL: {source_id} missed heartbeat ({time_since_last:.1f}s)")
                    elif time_since_last > self.config.warning_threshold_seconds:
                        source_status.status = HeartbeatStatus.WARNING
                        source_status.consecutive_misses += 1
                        self.logger.warning(f"  ⚠️  WARNING: {source_id} missed heartbeat ({time_since_last:.1f}s)")
                    elif time_since_last > self.config.timeout_seconds:
                        source_status.status = HeartbeatStatus.DEAD
                        source_status.consecutive_misses += 1
                        self.logger.error(f"  ❌ DEAD: {source_id} no heartbeat ({time_since_last:.1f}s)")
                    else:
                        source_status.status = HeartbeatStatus.HEALTHY
                        source_status.consecutive_misses = 0
                else:
                    # Never received a heartbeat
                    source_status.status = HeartbeatStatus.UNKNOWN
                    self.logger.debug(f"  ❓ UNKNOWN: {source_id} never sent heartbeat")

    def start_monitoring(self):
        """Start heartbeat monitoring"""
        if self.monitoring_active:
            self.logger.warning("  ⚠️  Monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("  ✅ Heartbeat monitoring started")
        self.logger.info(f"     Interval: {self.config.heartbeat_interval_seconds}s")
        self.logger.info(f"     Timeout: {self.config.timeout_seconds}s")

    def stop_monitoring(self):
        """Stop heartbeat monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        self.logger.info("  ⏹️  Heartbeat monitoring stopped")

    def _monitor_loop(self):
        """Monitor loop"""
        while self.monitoring_active:
            try:
                self.check_heartbeats()
                time.sleep(self.config.heartbeat_interval_seconds)
            except Exception as e:
                self.logger.error(f"  ❌ Monitor loop error: {e}")
                time.sleep(self.config.heartbeat_interval_seconds)

    def get_status(self) -> Dict[str, Any]:
        """Get watchdog status"""
        with self.lock:
            healthy = len([s for s in self.sources.values() if s.status == HeartbeatStatus.HEALTHY])
            warning = len([s for s in self.sources.values() if s.status == HeartbeatStatus.WARNING])
            critical = len([s for s in self.sources.values() if s.status == HeartbeatStatus.CRITICAL])
            dead = len([s for s in self.sources.values() if s.status == HeartbeatStatus.DEAD])
            unknown = len([s for s in self.sources.values() if s.status == HeartbeatStatus.UNKNOWN])

            total_ai_mentions = sum(s.ai_technology_mentions for s in self.sources.values())

            return {
                "monitoring_active": self.monitoring_active,
                "total_sources": len(self.sources),
                "healthy": healthy,
                "warning": warning,
                "critical": critical,
                "dead": dead,
                "unknown": unknown,
                "total_heartbeats": sum(s.total_heartbeats for s in self.sources.values()),
                "total_ai_technology_mentions": total_ai_mentions,
                "sources": {sid: s.to_dict() for sid, s in self.sources.items()},
                "config": asdict(self.config)
            }

    def _save_heartbeat(self, heartbeat: Heartbeat) -> None:
        try:
            """Save heartbeat"""
            heartbeat_file = self.data_dir / "heartbeats" / f"{heartbeat.heartbeat_id}.json"
            heartbeat_file.parent.mkdir(parents=True, exist_ok=True)
            with open(heartbeat_file, 'w', encoding='utf-8') as f:
                json.dump(heartbeat.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_heartbeat: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Technology Heartbeat Watchdog")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--heartbeat", nargs=3, metavar=("SOURCE_ID", "CONTENT", "RESPONSE_TIME_MS"),
                       help="Record heartbeat (SOURCE_ID CONTENT RESPONSE_TIME_MS)")
    parser.add_argument("--register", nargs=2, metavar=("SOURCE_ID", "TYPE"),
                       help="Register source (SOURCE_ID ASKS|SOURCES|BOTH)")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    watchdog = AITechnologyHeartbeatWatchdog()

    if args.start:
        watchdog.start_monitoring()
        print("\n💓 AI Technology Heartbeat Watchdog started")
        print("   Monitoring all @ASKS and @SOURCES for 'AI Technology'")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            watchdog.stop_monitoring()
            print("\n⏹️  Monitoring stopped")

    elif args.stop:
        watchdog.stop_monitoring()
        print("\n⏹️  Monitoring stopped")

    elif args.heartbeat:
        source_id, content, response_time = args.heartbeat
        heartbeat = watchdog.record_heartbeat(
            source_id,
            content=content if content != "None" else None,
            response_time_ms=float(response_time) if response_time != "None" else None
        )
        if args.json:
            print(json.dumps(heartbeat.to_dict(), indent=2))
        else:
            print(f"\n💓 Heartbeat recorded")
            print(f"   Source: {heartbeat.source_id}")
            print(f"   Status: {heartbeat.status.value}")
            print(f"   AI Technology Mentioned: {heartbeat.ai_technology_mentioned}")

    elif args.register:
        source_id, source_type_str = args.register
        source_type = SourceType[source_type_str.upper()]
        watchdog.register_source(source_id, source_type)
        print(f"\n✅ Source registered: {source_id} ({source_type.value})")

    elif args.status:
        status = watchdog.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n💓 AI Technology Heartbeat Watchdog Status")
            print(f"   Monitoring Active: {status['monitoring_active']}")
            print(f"   Total Sources: {status['total_sources']}")
            print(f"   Healthy: {status['healthy']}")
            print(f"   Warning: {status['warning']}")
            print(f"   Critical: {status['critical']}")
            print(f"   Dead: {status['dead']}")
            print(f"   Unknown: {status['unknown']}")
            print(f"   Total Heartbeats: {status['total_heartbeats']}")
            print(f"   AI Technology Mentions: {status['total_ai_technology_mentions']}")

    else:
        parser.print_help()
        print("\n💓 AI Technology Heartbeat Watchdog")
        print("   'WE MUST ESTABLISH A HEARTBEAT WATCHDOG ON 'AI TECHNOLOGY' FROM ALL @ASKS AND @SOURCES.'")

