#!/usr/bin/env python3
"""
AI Agent Status Display - Color-Coded Live Status Display

Displays AI agent status with color coding:
- GREEN: Optimal service
- YELLOW: Degraded service
- RED: Critical/Offline service

Tags: #TRANSPARENCY #DISPLAY #STATUS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import time

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

logger = get_logger("AIAgentStatusDisplay")


class ColorCode:
    """ANSI color codes for terminal display"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class AIAgentStatusDisplay:
    """Display AI agent status with color coding"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize status display"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.status_file = self.project_root / "data" / "ai_agent_monitor" / "live_status.json"

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current status from file"""
        try:
            if not self.status_file.exists():
                return None

            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error reading status: {e}")
            return None

    def display_status(self, use_colors: bool = True):
        """Display current status with color coding"""
        status = self.get_status()

        if not status or not status.get("active_agent"):
            print(f"{ColorCode.YELLOW}⚠️  No active agent detected{ColorCode.RESET}")
            return

        agent = status["active_agent"]
        health = agent["health"]

        # Determine color
        if health["status"] == "optimal":
            color = ColorCode.GREEN
            status_icon = "✅"
        elif health["status"] == "degraded":
            color = ColorCode.YELLOW
            status_icon = "⚠️"
        else:
            color = ColorCode.RED
            status_icon = "❌"

        if not use_colors:
            color = ""
            ColorCode.RESET = ""

        # Display header
        print("\n" + "=" * 80)
        print(f"{ColorCode.BOLD}{ColorCode.CYAN}🖥️  AI AGENT LIVE STATUS{ColorCode.RESET}")
        print("=" * 80)

        # Display agent info
        print(f"\n{ColorCode.BOLD}Active Agent:{ColorCode.RESET}")
        print(f"  Provider: {agent['provider']}")
        print(f"  Model: {agent['model']}")
        print(f"  Type: {agent['provider_type']}")
        print(f"  Status: {agent['status']}")

        if agent.get("current_task"):
            print(f"  Current Task: {agent['current_task']}")

        # Display health
        print(f"\n{ColorCode.BOLD}Service Health:{ColorCode.RESET}")
        print(f"  {status_icon} Status: {color}{health['status_text']}{ColorCode.RESET}")
        print(f"  Success Rate: {health['success_rate']:.1%}")
        print(f"  Error Rate: {health['error_rate']:.1%}")
        print(f"  Response Time: {health['response_time']:.2f}s")
        print(f"  Uptime: {health['uptime']:.1f}%")

        if health.get("issues"):
            print(f"\n{ColorCode.BOLD}Issues:{ColorCode.RESET}")
            for issue in health["issues"]:
                print(f"  {ColorCode.YELLOW}⚠️  {issue}{ColorCode.RESET}")

        # Display @WOPR patterns
        if agent.get("wopr_patterns"):
            print(f"\n{ColorCode.BOLD}@WOPR Patterns:{ColorCode.RESET}")
            for pattern in agent["wopr_patterns"]:
                print(f"  {ColorCode.BLUE}🔍 {pattern}{ColorCode.RESET}")

        # Display time tracking
        time_tracking = agent.get("time_tracking", {})
        if time_tracking:
            print(f"\n{ColorCode.BOLD}Time Tracking:{ColorCode.RESET}")
            print(f"  Current Task Time: {time_tracking.get('total_time_formatted', '0s')}")

            if time_tracking.get("wakatime_tracked"):
                print(f"  {ColorCode.GREEN}✅ WakaTime:{ColorCode.RESET} {time_tracking.get('wakatime_hours', 0):.2f} hours")
            else:
                print(f"  {ColorCode.YELLOW}⚠️  WakaTime:{ColorCode.RESET} Not synced")

            if time_tracking.get("cursor_tracked"):
                print(f"  {ColorCode.GREEN}✅ Cursor:{ColorCode.RESET} Tracked")
            else:
                print(f"  {ColorCode.YELLOW}⚠️  Cursor:{ColorCode.RESET} Not synced")

            if time_tracking.get("last_sync"):
                print(f"  Last Sync: {time_tracking['last_sync']}")

        # Display timestamp
        print(f"\n{ColorCode.BOLD}Last Updated:{ColorCode.RESET} {agent['last_updated']}")
        print("=" * 80 + "\n")

    def display_compact(self, use_colors: bool = True):
        """Display compact one-line status"""
        status = self.get_status()

        if not status or not status.get("active_agent"):
            return

        agent = status["active_agent"]
        health = agent["health"]

        # Determine color
        if health["status"] == "optimal":
            color = ColorCode.GREEN
            status_icon = "✅"
        elif health["status"] == "degraded":
            color = ColorCode.YELLOW
            status_icon = "⚠️"
        else:
            color = ColorCode.RED
            status_icon = "❌"

        if not use_colors:
            color = ""
            ColorCode.RESET = ""

        time_tracking = agent.get("time_tracking", {})
        time_str = time_tracking.get("total_time_formatted", "0s") if time_tracking else "0s"

        print(f"\r{status_icon} [{color}{health['status_text']}{ColorCode.RESET}] "
              f"{agent['provider']} / {agent['model']} | "
              f"Time: {time_str} | "
              f"Success: {health['success_rate']:.1%} | "
              f"Response: {health['response_time']:.2f}s", end="", flush=True)


if __name__ == "__main__":
    display = AIAgentStatusDisplay()

    print("🖥️  AI Agent Status Display")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            display.display_compact()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\n✅ Display stopped")
