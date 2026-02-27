"""
WakaTime API client for coding statistics.

Provides access to WakaTime's REST API for retrieving coding summaries,
project stats, language breakdowns, and editor usage data.

Pattern extracted from production: wakatime_integration.py

Example:
    client = WakaTimeClient(api_key="your-key-here")
    summary = client.get_summary(days=7)
    print(f"Total coding: {summary['grand_total']['text']}")

    projects = client.get_projects()
    for p in projects[:5]:
        print(f"  {p['name']}: {p.get('total_seconds', 0) / 3600:.1f}h")
"""

import base64
import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

BASE_URL = "https://wakatime.com/api/v1"


class WakaTimeClient:
    """
    WakaTime REST API client.

    Args:
        api_key: WakaTime API key (base64-encoded for Basic auth).
        timeout: Request timeout in seconds.
    """

    def __init__(self, api_key: str, timeout: int = 30):
        self._auth = base64.b64encode(api_key.encode()).decode()
        self._timeout = timeout

    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get coding summary for a date range.

        Args:
            days: Number of days to look back.

        Returns:
            Summary dict with grand_total, projects, languages, etc.
        """
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        data = self._get(f"/users/current/summaries?start={start}&end={end}")
        return data or {}

    def get_stats(self, range_type: str = "last_7_days") -> Dict[str, Any]:
        """
        Get stats for a time range.

        Args:
            range_type: One of: last_7_days, last_30_days, last_year, all_time.
        """
        data = self._get(f"/users/current/stats/{range_type}")
        return data.get("data", {}) if data else {}

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of projects."""
        data = self._get("/users/current/projects")
        return data.get("data", []) if data else []

    def get_languages(self, range_type: str = "last_7_days") -> List[Dict[str, Any]]:
        """Get language breakdown."""
        stats = self.get_stats(range_type)
        return stats.get("languages", [])

    def get_editors(self, range_type: str = "last_7_days") -> List[Dict[str, Any]]:
        """Get editor usage breakdown."""
        stats = self.get_stats(range_type)
        return stats.get("editors", [])

    def _get(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated GET request."""
        url = f"{BASE_URL}{endpoint}"
        headers = {"Authorization": f"Basic {self._auth}"}
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            logger.error("WakaTime API error %d: %s", exc.code, exc.reason)
            return None
        except (urllib.error.URLError, OSError) as exc:
            logger.error("WakaTime request failed: %s", exc)
            return None
