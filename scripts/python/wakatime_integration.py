"""
PUBLIC: WakaTime API Integration
Location: scripts/python/wakatime_integration.py
License: MIT

WakaTime API client for LUMINA project integration.
Provides methods to fetch coding statistics, summaries, and project data.
"""

import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import base64
import logging
from pathlib import Path
import json


# Initialize logger
logger = logging.getLogger(__name__)


class WakaTimeAPI:
    """WakaTime API client for LUMINA project."""

    def __init__(self, api_key: str):
        """
        Initialize WakaTime API client.

        Args:
            api_key: WakaTime API key (should be retrieved from Azure Key Vault)
        """
        self.api_key = api_key
        self.base_url = "https://wakatime.com/api/v1"
        self.headers = {
            "Authorization": f"Basic {base64.b64encode(api_key.encode()).decode()}",
            "Content-Type": "application/json"
        }

    def get_summary(
        self,
        start_date: str,
        end_date: str,
        project: Optional[str] = "LUMINA"
    ) -> Dict[str, Any]:
        """
        Get coding summary for date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            project: Optional project name filter

        Returns:
            Summary data dictionary

        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/users/current/summaries"
        params = {
            "start": start_date,
            "end": end_date
        }

        if project:
            params["project"] = project

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch WakaTime summary: {e}", exc_info=True)
            raise

    def get_stats(self, range_type: str = "last_7_days") -> Dict[str, Any]:
        """
        Get coding statistics.

        Args:
            range_type: Time range (last_7_days, last_30_days, last_year, all_time)

        Returns:
            Stats data dictionary

        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/users/current/stats/{range_type}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch WakaTime stats: {e}", exc_info=True)
            raise

    def get_projects(self) -> Dict[str, Any]:
        """
        Get all projects.

        Returns:
            Projects data dictionary

        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/users/current/projects"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch WakaTime projects: {e}", exc_info=True)
            raise

    def get_languages(self, range_type: str = "last_7_days") -> Dict[str, Any]:
        """
        Get language statistics.

        Args:
            range_type: Time range

        Returns:
            Language stats dictionary
        """
        stats = self.get_stats(range_type)
        return stats.get("data", {}).get("languages", [])

    def get_editors(self, range_type: str = "last_7_days") -> Dict[str, Any]:
        """
        Get editor statistics.

        Args:
            range_type: Time range

        Returns:
            Editor stats dictionary
        """
        stats = self.get_stats(range_type)
        return stats.get("data", {}).get("editors", [])

    def create_custom_chart_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Create custom chart data for LUMINA project.

        Args:
            days: Number of days to include

        Returns:
            Chart-ready data structure
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        summary = self.get_summary(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            project="LUMINA"
        )

        # Process data for charting
        chart_data = {
            "labels": [],
            "datasets": [{
                "label": "Coding Hours (LUMINA)",
                "data": [],
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            }]
        }

        # Extract daily data from summary
        for day in summary.get("data", []):
            date_str = day.get("range", {}).get("date", "")
            total_seconds = day.get("grand_total", {}).get("total_seconds", 0)
            hours = total_seconds / 3600

            chart_data["labels"].append(date_str)
            chart_data["datasets"][0]["data"].append(round(hours, 2))

        return chart_data

    def get_lumina_project_stats(self) -> Dict[str, Any]:
        """
        Get LUMINA-specific project statistics.

        Returns:
            Dictionary with LUMINA project stats
        """
        projects = self.get_projects()

        # Find LUMINA project
        lumina_project = None
        for project in projects.get("data", []):
            if project.get("name", "").upper() == "LUMINA":
                lumina_project = project
                break

        if not lumina_project:
            logger.warning("LUMINA project not found in WakaTime")
            return {}

        # Get detailed stats for LUMINA
        stats = self.get_stats("last_30_days")

        return {
            "project": lumina_project,
            "total_time": stats.get("data", {}).get("total_seconds", 0) / 3600,
            "languages": self.get_languages("last_30_days"),
            "editors": self.get_editors("last_30_days")
        }


def load_config(project_root: Path) -> Dict[str, Any]:
    """
    Load WakaTime configuration.

    Args:
        project_root: Path to project root

    Returns:
        Configuration dictionary
    """
    config_path = project_root / "config" / "wakatime_config.json"

    if not config_path.exists():
        logger.warning(f"WakaTime config not found at {config_path}")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load WakaTime config: {e}", exc_info=True)
        return {}


def main():
    """
    Example usage of WakaTime API.

    Note: API key should be retrieved from Azure Key Vault in production.
    """
    import os

    # Get API key from environment or config
    api_key = os.getenv("WAKATIME_API_KEY")

    if not api_key:
        print("⚠️  WAKATIME_API_KEY environment variable not set")
        print("   Set it or retrieve from Azure Key Vault")
        return

    try:
        client = WakaTimeAPI(api_key)

        # Get last 7 days stats
        print("📊 Fetching last 7 days statistics...")
        stats = client.get_stats("last_7_days")
        total_hours = stats.get("data", {}).get("total_seconds", 0) / 3600
        print(f"   Total coding time: {total_hours:.2f} hours")

        # Get LUMINA project stats
        print("\n🔍 Fetching LUMINA project statistics...")
        lumina_stats = client.get_lumina_project_stats()
        if lumina_stats:
            print(f"   LUMINA project time: {lumina_stats.get('total_time', 0):.2f} hours")

        # Get top languages
        print("\n💻 Top languages (last 7 days):")
        languages = client.get_languages("last_7_days")
        for lang in languages[:5]:
            name = lang.get("name", "Unknown")
            hours = lang.get("total_seconds", 0) / 3600
            print(f"   {name}: {hours:.2f} hours")

    except Exception as e:
        logger.error(f"Error using WakaTime API: {e}", exc_info=True)
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


    main()