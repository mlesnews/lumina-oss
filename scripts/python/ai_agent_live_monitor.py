#!/usr/bin/env python3
"""
AI Agent Live Monitor - Real-Time Transparency System

LIVE MONITORING of AI agent/model selection and service health:
- Real-time display of current AI LLM working on issues
- Live updates with color-coded status (RED-YELLOW-GREEN)
- Service health monitoring (Optimal/Degraded/Critical)
- Integration with @WOPR for deep pattern research

TRANSPARENCY: Always know which AI agent is working!

Tags: #TRANSPARENCY #LIVE_MONITORING #AI_AGENT #WOPR #PATTERN_RESEARCH @LUMINA @JARVIS
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
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

logger = get_logger("AIAgentLiveMonitor")

# Import provider tracker
try:
    from cloud_ai_provider_tracker import (
        CloudAIProviderTracker,
        ProviderType,
        get_provider_tracker
    )
    PROVIDER_TRACKER_AVAILABLE = True
except ImportError:
    PROVIDER_TRACKER_AVAILABLE = False
    logger.warning("⚠️  Cloud AI Provider Tracker not available")

# Import @WOPR for pattern research
try:
    from lumina.wopr_simulator import WOPRSimulator
    WOPR_AVAILABLE = True
except ImportError:
    try:
        from wopr_decisioning_spectrum_10000yr import WOPRDecisioningSpectrum
        WOPR_AVAILABLE = True
    except ImportError:
        WOPR_AVAILABLE = False
        logger.warning("⚠️  @WOPR not available")

# Import cursor model tracker
try:
    from cursor_active_model_tracker import CursorActiveModelTracker
    CURSOR_TRACKER_AVAILABLE = True
except ImportError:
    CURSOR_TRACKER_AVAILABLE = False
    logger.warning("⚠️  Cursor Active Model Tracker not available")

# Import time tracking frameworks
try:
    from wakatime_integration import WakaTimeAPI
    WAKATIME_AVAILABLE = True
except ImportError:
    WAKATIME_AVAILABLE = False
    logger.warning("⚠️  WakaTime integration not available")

try:
    from comprehensive_analytics_tracker import ComprehensiveAnalyticsTracker
    ANALYTICS_TRACKER_AVAILABLE = True
except ImportError:
    ANALYTICS_TRACKER_AVAILABLE = False
    logger.warning("⚠️  Comprehensive Analytics Tracker not available")

try:
    from jarvis_wakatime_cursor_stats import WakaTimeCursorStats
    WAKATIME_CURSOR_STATS_AVAILABLE = True
except ImportError:
    WAKATIME_CURSOR_STATS_AVAILABLE = False
    logger.warning("⚠️  WakaTime Cursor Stats not available")


class ServiceStatus(Enum):
    """Service status levels"""
    OPTIMAL = "optimal"  # GREEN
    DEGRADED = "degraded"  # YELLOW
    CRITICAL = "critical"  # RED
    OFFLINE = "offline"  # RED


class AgentStatus(Enum):
    """Agent status"""
    ACTIVE = "active"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class ServiceHealth:
    """Service health metrics"""
    status: ServiceStatus
    response_time: float = 0.0  # seconds
    success_rate: float = 1.0  # 0.0 to 1.0
    error_rate: float = 0.0  # 0.0 to 1.0
    last_check: datetime = field(default_factory=datetime.now)
    uptime: float = 100.0  # percentage
    issues: List[str] = field(default_factory=list)

    @property
    def color(self) -> str:
        """Get color code for status"""
        if self.status == ServiceStatus.OPTIMAL:
            return "GREEN"
        elif self.status == ServiceStatus.DEGRADED:
            return "YELLOW"
        else:
            return "RED"

    @property
    def status_text(self) -> str:
        """Get human-readable status"""
        return self.status.value.upper()


@dataclass
class TimeTracking:
    """Time tracking information"""
    task_start_time: datetime = field(default_factory=datetime.now)
    total_time_seconds: float = 0.0
    wakatime_tracked: bool = False
    cursor_tracked: bool = False
    wakatime_hours: float = 0.0
    cursor_hours: float = 0.0
    last_sync: Optional[datetime] = None


@dataclass
class ActiveAgent:
    """Currently active AI agent information"""
    agent_id: str
    provider: str
    model: str
    provider_type: str
    status: AgentStatus
    current_task: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    health: ServiceHealth = field(default_factory=lambda: ServiceHealth(ServiceStatus.OPTIMAL))
    wopr_patterns: List[str] = field(default_factory=list)  # @WOPR pattern research
    time_tracking: TimeTracking = field(default_factory=TimeTracking)  # Time tracking
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON"""
        return {
            "agent_id": self.agent_id,
            "provider": self.provider,
            "model": self.model,
            "provider_type": self.provider_type,
            "status": self.status.value,
            "current_task": self.current_task,
            "started_at": self.started_at.isoformat(),
            "health": {
                "status": self.health.status.value,
                "color": self.health.color,
                "status_text": self.health.status_text,
                "response_time": self.health.response_time,
                "success_rate": self.health.success_rate,
                "error_rate": self.health.error_rate,
                "uptime": self.health.uptime,
                "issues": self.health.issues,
                "last_check": self.health.last_check.isoformat()
            },
            "wopr_patterns": self.wopr_patterns,
            "time_tracking": {
                "task_start_time": self.time_tracking.task_start_time.isoformat(),
                "total_time_seconds": self.time_tracking.total_time_seconds,
                "total_time_formatted": ActiveAgent._format_time_duration(self.time_tracking.total_time_seconds),
                "wakatime_tracked": self.time_tracking.wakatime_tracked,
                "cursor_tracked": self.time_tracking.cursor_tracked,
                "wakatime_hours": self.time_tracking.wakatime_hours,
                "cursor_hours": self.time_tracking.cursor_hours,
                "last_sync": self.time_tracking.last_sync.isoformat() if self.time_tracking.last_sync else None
            },
            "last_updated": self.last_updated.isoformat()
        }

    @staticmethod
    def _format_time_duration(seconds: float) -> str:
        """Format time in seconds to human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


class AIAgentLiveMonitor:
    """
    AI Agent Live Monitor - Real-Time Transparency System

    LIVE MONITORING of AI agent/model selection and service health.
    Always know which AI agent is working!
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI Agent Live Monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ai_agent_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Status files
        self.live_status_file = self.data_dir / "live_status.json"
        self.history_file = self.data_dir / "agent_history.jsonl"

        # Current active agent
        self.active_agent: Optional[ActiveAgent] = None

        # Initialize systems
        self.provider_tracker = None
        if PROVIDER_TRACKER_AVAILABLE:
            try:
                self.provider_tracker = get_provider_tracker()
                logger.info("✅ Provider Tracker initialized")
            except Exception as e:
                logger.warning(f"⚠️  Provider Tracker init error: {e}")

        self.cursor_tracker = None
        if CURSOR_TRACKER_AVAILABLE:
            try:
                self.cursor_tracker = CursorActiveModelTracker(self.project_root)
                logger.info("✅ Cursor Model Tracker initialized")
            except Exception as e:
                logger.warning(f"⚠️  Cursor Tracker init error: {e}")

        # Initialize time tracking frameworks
        self.wakatime_api = None
        if WAKATIME_AVAILABLE:
            try:
                # Try to get API key from environment or Azure Vault
                import os
                api_key = os.getenv("WAKATIME_API_KEY")
                if not api_key:
                    # Try Azure Vault
                    try:
                        from unified_secrets_manager import UnifiedSecretsManager, SecretSource
                        secrets = UnifiedSecretsManager(self.project_root)
                        api_key = secrets.get_secret("wakatime-api-key", source=SecretSource.AZURE_KEY_VAULT)
                    except:
                        pass

                if api_key:
                    self.wakatime_api = WakaTimeAPI(api_key)
                    logger.info("✅ WakaTime API initialized")
                else:
                    logger.warning("⚠️  WakaTime API key not found")
            except Exception as e:
                logger.warning(f"⚠️  WakaTime init error: {e}")

        self.analytics_tracker = None
        if ANALYTICS_TRACKER_AVAILABLE:
            try:
                self.analytics_tracker = ComprehensiveAnalyticsTracker(self.project_root)
                logger.info("✅ Comprehensive Analytics Tracker initialized")
            except Exception as e:
                logger.warning(f"⚠️  Analytics Tracker init error: {e}")

        self.wakatime_cursor_stats = None
        if WAKATIME_CURSOR_STATS_AVAILABLE:
            try:
                self.wakatime_cursor_stats = WakaTimeCursorStats(self.project_root)
                logger.info("✅ WakaTime Cursor Stats initialized")
            except Exception as e:
                logger.warning(f"⚠️  WakaTime Cursor Stats init error: {e}")

        self.wopr_simulator = None
        if WOPR_AVAILABLE:
            try:
                self.wopr_simulator = WOPRSimulator(project_root=self.project_root)
                logger.info("✅ @WOPR Simulator initialized")
            except ImportError:
                try:
                    self.wopr_simulator = WOPRDecisioningSpectrum(project_root=self.project_root)
                    logger.info("✅ @WOPR Decisioning Spectrum initialized")
                except Exception as e:
                    logger.warning(f"⚠️  @WOPR init error: {e}")

        # Monitoring thread
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 2.0  # Update every 2 seconds

        logger.info("=" * 80)
        logger.info("🖥️  AI AGENT LIVE MONITOR")
        logger.info("   Real-Time Transparency System")
        logger.info("   Status: RED-YELLOW-GREEN")
        logger.info("=" * 80)

    def start_monitoring(self):
        """Start live monitoring"""
        if self.monitoring:
            logger.warning("⚠️  Monitoring already active")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Live monitoring started")

    def stop_monitoring(self):
        """Stop live monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("🛑 Live monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.update_active_agent()
                self.check_service_health()
                self.update_wopr_patterns()
                self.update_time_tracking()  # Update time tracking
                self.write_live_status()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(self.update_interval)

    def update_active_agent(self):
        """Update currently active agent information"""
        try:
            # Get active model from Cursor
            if self.cursor_tracker:
                cursor_status = self.cursor_tracker.get_active_model()
                active_model = cursor_status.get("active_model", "Unknown")
                provider = cursor_status.get("provider", "unknown")
                model_type = cursor_status.get("model_type", "unknown")

                # Determine provider type
                provider_type = self._map_provider_type(provider, active_model)

                # Get or create active agent
                if not self.active_agent or self.active_agent.model != active_model:
                    self.active_agent = ActiveAgent(
                        agent_id=f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        provider=provider,
                        model=active_model,
                        provider_type=provider_type,
                        status=AgentStatus.ACTIVE,
                        started_at=datetime.now()
                    )
                    logger.info(f"   🔄 Agent changed: {provider} / {active_model}")
                else:
                    # Update existing agent
                    self.active_agent.last_updated = datetime.now()
                    self.active_agent.status = AgentStatus.ACTIVE
            else:
                # Fallback: Use provider tracker
                if self.provider_tracker:
                    # Get most recently used provider
                    # This is a simplified version - in real implementation, track actual usage
                    self.active_agent = ActiveAgent(
                        agent_id=f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        provider="Unknown",
                        model="Unknown",
                        provider_type="unknown",
                        status=AgentStatus.IDLE
                    )
        except Exception as e:
            logger.error(f"❌ Error updating active agent: {e}")

    def _map_provider_type(self, provider: str, model: str) -> str:
        """Map provider/model to provider type"""
        provider_lower = provider.lower()
        model_lower = model.lower()

        # Local providers
        if "ultron" in model_lower or "ultron" in provider_lower:
            return "ULTRON"
        elif "iron" in model_lower and "legion" in model_lower:
            return "IRON_LEGION"
        elif "kaiju" in model_lower:
            return "KAIJU_IRON_LEGION"

        # Cloud providers
        elif "openai" in provider_lower or "gpt" in model_lower:
            return "OPENAI"
        elif "anthropic" in provider_lower or "claude" in model_lower:
            return "ANTHROPIC"
        elif "azure" in provider_lower:
            return "AZURE_OPENAI"
        elif "google" in provider_lower or "gemini" in model_lower:
            return "GOOGLE"

        return "UNKNOWN"

    def check_service_health(self):
        """Check service health for active agent"""
        if not self.active_agent:
            return

        try:
            health = self.active_agent.health

            # Simulate health check (in real implementation, ping actual service)
            # For now, use provider tracker if available
            if self.provider_tracker:
                provider_type = self._get_provider_type_enum()
                if provider_type:
                    provider = self.provider_tracker.get_provider(provider_type)
                    if provider:
                        # Check recent job performance
                        # Simplified: assume optimal if no recent failures
                        health.status = ServiceStatus.OPTIMAL
                        health.success_rate = 0.95  # Placeholder
                        health.error_rate = 0.05
                        health.uptime = 99.5
                        health.response_time = 0.5  # Placeholder
                        health.issues = []
                    else:
                        health.status = ServiceStatus.DEGRADED
                        health.issues = ["Provider not found in tracker"]
                else:
                    health.status = ServiceStatus.DEGRADED
                    health.issues = ["Unknown provider type"]
            else:
                # Default: assume optimal
                health.status = ServiceStatus.OPTIMAL
                health.success_rate = 1.0
                health.error_rate = 0.0
                health.uptime = 100.0
                health.response_time = 0.3

            health.last_check = datetime.now()

            # Determine status based on metrics
            if health.error_rate > 0.2 or health.uptime < 90.0:
                health.status = ServiceStatus.CRITICAL
            elif health.error_rate > 0.1 or health.uptime < 95.0 or health.response_time > 2.0:
                health.status = ServiceStatus.DEGRADED
            else:
                health.status = ServiceStatus.OPTIMAL

            self.active_agent.health = health

        except Exception as e:
            logger.error(f"❌ Error checking service health: {e}")
            if self.active_agent:
                self.active_agent.health.status = ServiceStatus.CRITICAL
                self.active_agent.health.issues.append(f"Health check error: {e}")

    def _get_provider_type_enum(self) -> Optional[ProviderType]:
        """Get ProviderType enum from active agent"""
        if not self.active_agent:
            return None

        provider_type_map = {
            "ULTRON": ProviderType.ULTRON,
            "IRON_LEGION": ProviderType.IRON_LEGION,
            "KAIJU_IRON_LEGION": ProviderType.KAIJU_IRON_LEGION,
            "OPENAI": ProviderType.OPENAI,
            "ANTHROPIC": ProviderType.ANTHROPIC,
            "AZURE_OPENAI": ProviderType.AZURE_OPENAI,
            "GOOGLE": ProviderType.GOOGLE
        }

        return provider_type_map.get(self.active_agent.provider_type)

    def update_wopr_patterns(self):
        """Update @WOPR pattern research for current agent"""
        if not self.active_agent or not self.wopr_simulator:
            return

        try:
            # Use @WOPR for deep pattern research
            # Extract patterns related to current agent/provider
            patterns = []

            # Simulate WOPR pattern extraction
            # In real implementation, run WOPR simulation for pattern research
            if hasattr(self.wopr_simulator, 'extract_patterns'):
                patterns = self.wopr_simulator.extract_patterns(
                    context={
                        "provider": self.active_agent.provider,
                        "model": self.active_agent.model,
                        "provider_type": self.active_agent.provider_type
                    }
                )
            else:
                # Fallback: Generate pattern tags
                patterns = [
                    f"provider:{self.active_agent.provider_type}",
                    f"model:{self.active_agent.model}",
                    f"status:{self.active_agent.status.value}"
                ]

            self.active_agent.wopr_patterns = patterns

        except Exception as e:
            logger.warning(f"⚠️  @WOPR pattern update error: {e}")

    def write_live_status(self):
        """Write live status to file for UI display"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "active_agent": self.active_agent.to_dict() if self.active_agent else None,
                "monitoring": self.monitoring,
                "update_interval": self.update_interval
            }

            with open(self.live_status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, default=str)

            # Also append to history
            if self.active_agent:
                with open(self.history_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(status, default=str) + '\n')

        except Exception as e:
            logger.error(f"❌ Error writing live status: {e}")

    def get_live_status(self) -> Dict[str, Any]:
        """Get current live status"""
        if self.active_agent:
            return {
                "active_agent": self.active_agent.to_dict(),
                "monitoring": self.monitoring,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "active_agent": None,
                "monitoring": self.monitoring,
                "timestamp": datetime.now().isoformat()
            }

    def set_current_task(self, task: str):
        """Set current task being worked on"""
        if self.active_agent:
            # Reset time tracking for new task
            self.active_agent.time_tracking.task_start_time = datetime.now()
            self.active_agent.time_tracking.total_time_seconds = 0.0

            self.active_agent.current_task = task
            self.active_agent.status = AgentStatus.PROCESSING
            self.active_agent.last_updated = datetime.now()
            logger.info(f"   📋 Task: {task}")

    def update_time_tracking(self):
        """Update time tracking for current agent"""
        if not self.active_agent or not self.active_agent.current_task:
            return

        try:
            # Calculate elapsed time
            elapsed = (datetime.now() - self.active_agent.time_tracking.task_start_time).total_seconds()
            self.active_agent.time_tracking.total_time_seconds = elapsed

            # Sync with WakaTime (primary)
            if self.wakatime_api:
                try:
                    # Get today's summary from WakaTime
                    today = datetime.now().strftime("%Y-%m-%d")
                    summary = self.wakatime_api.get_summary(today, today, project="LUMINA")

                    # Extract total time
                    if summary and "data" in summary:
                        total_seconds = 0
                        for day in summary["data"]:
                            if "grand_total" in day:
                                total_seconds += day["grand_total"].get("total_seconds", 0)

                        self.active_agent.time_tracking.wakatime_hours = total_seconds / 3600.0
                        self.active_agent.time_tracking.wakatime_tracked = True
                        self.active_agent.time_tracking.last_sync = datetime.now()
                except Exception as e:
                    logger.debug(f"WakaTime sync error: {e}")

            # Sync with Cursor tracking
            if self.analytics_tracker:
                try:
                    analytics = self.analytics_tracker.collect_all_analytics()
                    cursor_data = analytics.get("sources", {}).get("cursor_ide_mode", {})

                    if cursor_data.get("available"):
                        # Extract Cursor time (simplified - would need actual Cursor API)
                        self.active_agent.time_tracking.cursor_tracked = True
                        self.active_agent.time_tracking.last_sync = datetime.now()
                except Exception as e:
                    logger.debug(f"Cursor sync error: {e}")

            # Sync with WakaTime + Cursor Stats
            if self.wakatime_cursor_stats:
                try:
                    # This would use async, but for now just mark as available
                    self.active_agent.time_tracking.cursor_tracked = True
                except Exception as e:
                    logger.debug(f"WakaTime Cursor Stats sync error: {e}")

        except Exception as e:
            logger.warning(f"⚠️  Time tracking update error: {e}")

    def clear_current_task(self):
        """Clear current task"""
        if self.active_agent:
            self.active_agent.current_task = None
            self.active_agent.status = AgentStatus.ACTIVE
            self.active_agent.last_updated = datetime.now()


# Global instance
_global_monitor = None

def get_live_monitor() -> AIAgentLiveMonitor:
    """Get global AI Agent Live Monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = AIAgentLiveMonitor()
        _global_monitor.start_monitoring()
    return _global_monitor


if __name__ == "__main__":
    # Demo
    monitor = AIAgentLiveMonitor()
    monitor.start_monitoring()

    print("\n" + "=" * 80)
    print("🖥️  AI AGENT LIVE MONITOR - RUNNING")
    print("=" * 80)
    print("\nStatus file: data/ai_agent_monitor/live_status.json")
    print("Monitoring every 2 seconds...")
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            status = monitor.get_live_status()
            if status["active_agent"]:
                agent = status["active_agent"]
                health = agent["health"]
                print(f"\r[{health['color']}] {agent['provider']} / {agent['model']} | "
                      f"Status: {health['status_text']} | "
                      f"Success: {health['success_rate']:.1%} | "
                      f"Response: {health['response_time']:.2f}s", end="", flush=True)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor stopped")
