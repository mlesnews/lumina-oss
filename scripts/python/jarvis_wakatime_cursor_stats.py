#!/usr/bin/env python3
"""
JARVIS WakaTime + Cursor Statistics Integration
Retrieves WakaTime API key from Azure Vault and integrates with Cursor stats

@JARVIS @WAKATIME @CURSOR @STATS @AZURE_VAULT
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWakaTimeCursor")


class WakaTimeCursorStats:
    """
    WakaTime + Cursor Statistics Integration

    Features:
    - WakaTime API integration (key from Azure Vault)
    - Cursor IDE statistics
    - Combined analytics
    - Memory integration
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize WakaTime + Cursor stats"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Azure Key Vault for WakaTime API key
        try:
            from scripts.python.azure_service_bus_integration import get_key_vault_client
            self.key_vault = get_key_vault_client(
                vault_url="https://jarvis-lumina.vault.azure.net/"
            )
            logger.info("✅ Azure Key Vault initialized")
        except Exception as e:
            logger.warning(f"Azure Key Vault not available: {e}")
            self.key_vault = None

        # WakaTime API key
        self.wakatime_api_key = None
        self._load_wakatime_api_key()

        # WakaTime API base URL
        self.wakatime_base_url = "https://wakatime.com/api/v1"

        # Stats storage
        self.stats_dir = self.project_root / "data" / "wakatime_cursor_stats"
        self.stats_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ WakaTime + Cursor Stats initialized")

    def _load_wakatime_api_key(self) -> None:
        """Load WakaTime API key from Azure Vault"""
        if not self.key_vault:
            logger.warning("Azure Key Vault not available - cannot load WakaTime API key")
            return

        try:
            # Try multiple secret names
            secret_names = [
                "wakatime-api-key",
                "wakatime_api_key",
                "WakaTime-API-Key",
                "WAKATIME_API_KEY"
            ]

            for secret_name in secret_names:
                try:
                    self.wakatime_api_key = self.key_vault.get_secret(secret_name)
                    logger.info(f"✅ WakaTime API key loaded from Azure Vault: {secret_name}")
                    return
                except Exception:
                    continue

            logger.warning("WakaTime API key not found in Azure Vault")
        except Exception as e:
            logger.error(f"Failed to load WakaTime API key: {e}")

    async def get_wakatime_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get WakaTime statistics

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        if not self.wakatime_api_key:
            return {
                "success": False,
                "error": "WakaTime API key not available"
            }

        logger.info("📊 Fetching WakaTime statistics...")

        try:
            # Try aiohttp first
            try:
                import aiohttp
                aiohttp_available = True
            except ImportError:
                aiohttp_available = False
                logger.warning("aiohttp not available, using requests fallback")

            # Default to last 7 days
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")

            if aiohttp_available:
                # Use aiohttp
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Basic {self.wakatime_api_key}"
                    }

                    # Get current user
                    async with session.get(
                        f"{self.wakatime_base_url}/users/current",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            user_data = await response.json()
                            user_id = user_data.get("data", {}).get("id", "")
                        else:
                            logger.warning(f"Failed to get user info: {response.status}")
                            user_id = ""

                    # Get stats
                    stats_url = f"{self.wakatime_base_url}/users/{user_id}/stats"
                    params = {
                        "start": start_date,
                        "end": end_date
                    }

                    async with session.get(stats_url, headers=headers, params=params) as response:
                        if response.status == 200:
                            stats_data = await response.json()
                            logger.info("✅ WakaTime stats retrieved")
                            return {
                                "success": True,
                                "data": stats_data,
                                "start_date": start_date,
                                "end_date": end_date
                            }
                        else:
                            logger.error(f"Failed to get WakaTime stats: {response.status}")
                            return {
                                "success": False,
                                "error": f"API returned status {response.status}"
                            }
            else:
                # Fallback to requests (sync)
                try:
                    import requests
                    import base64
                    requests_available = True
                except ImportError:
                    requests_available = False
                    logger.warning("requests not available, WakaTime API calls will fail")

                if not requests_available:
                    return {
                        "success": False,
                        "error": "Neither aiohttp nor requests available. Install: pip install aiohttp requests"
                    }

                headers = {
                    "Authorization": f"Basic {base64.b64encode(self.wakatime_api_key.encode()).decode()}"
                }

                # Get current user
                response = requests.get(
                    f"{self.wakatime_base_url}/users/current",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    user_data = response.json()
                    user_id = user_data.get("data", {}).get("id", "")
                else:
                    logger.warning(f"Failed to get user info: {response.status_code}")
                    user_id = ""

                # Get stats
                stats_url = f"{self.wakatime_base_url}/users/{user_id}/stats"
                params = {
                    "start": start_date,
                    "end": end_date
                }

                response = requests.get(stats_url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    stats_data = response.json()
                    logger.info("✅ WakaTime stats retrieved")
                    return {
                        "success": True,
                        "data": stats_data,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                else:
                    logger.error(f"Failed to get WakaTime stats: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }

        except Exception as e:
            logger.error(f"WakaTime API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_cursor_stats(self) -> Dict[str, Any]:
        """Get Cursor IDE statistics"""
        logger.info("📊 Fetching Cursor IDE statistics...")

        stats = {
            "cursor_version": None,
            "extensions": [],
            "settings": {},
            "keyboard_shortcuts": {}
        }

        try:
            # Check Cursor settings
            cursor_settings_path = self.project_root / ".cursor" / "settings.json"
            if cursor_settings_path.exists():
                with open(cursor_settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    stats["settings"] = settings

            # Check keyboard shortcuts
            shortcuts_path = self.project_root / "config" / "cursor_ide_keyboard_shortcuts.json"
            if shortcuts_path.exists():
                with open(shortcuts_path, 'r', encoding='utf-8') as f:
                    shortcuts = json.load(f)
                    stats["keyboard_shortcuts"] = shortcuts

            logger.info("✅ Cursor stats retrieved")
            return {
                "success": True,
                "data": stats
            }

        except Exception as e:
            logger.error(f"Failed to get Cursor stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_combined_stats(self) -> Dict[str, Any]:
        """Get combined WakaTime + Cursor statistics"""
        logger.info("=" * 70)
        logger.info("📊 COMBINED STATISTICS")
        logger.info("=" * 70)
        logger.info("")

        results = {
            "wakatime": None,
            "cursor": None,
            "combined": {}
        }

        # Get WakaTime stats
        logger.info("Fetching WakaTime statistics...")
        results["wakatime"] = await self.get_wakatime_stats()

        # Get Cursor stats
        logger.info("Fetching Cursor statistics...")
        results["cursor"] = self.get_cursor_stats()

        # Combine stats
        if results["wakatime"].get("success") and results["cursor"].get("success"):
            wakatime_data = results["wakatime"].get("data", {})
            cursor_data = results["cursor"].get("data", {})

            results["combined"] = {
                "timestamp": datetime.now().isoformat(),
                "wakatime": {
                    "total_seconds": wakatime_data.get("data", {}).get("total_seconds", 0),
                    "languages": wakatime_data.get("data", {}).get("languages", []),
                    "projects": wakatime_data.get("data", {}).get("projects", [])
                },
                "cursor": {
                    "settings_count": len(cursor_data.get("settings", {})),
                    "shortcuts_count": len(cursor_data.get("keyboard_shortcuts", {}))
                }
            }

        # Save combined stats
        stats_file = self.stats_dir / f"combined_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"✅ Combined stats saved: {stats_file}")
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ COMBINED STATISTICS COMPLETE")
        logger.info("=" * 70)

        return results


async def main():
    """Main execution"""
    print("=" * 70)
    print("📊 JARVIS WAKATIME + CURSOR STATISTICS")
    print("   API key from Azure Vault")
    print("=" * 70)
    print()

    stats = WakaTimeCursorStats()
    results = await stats.get_combined_stats()

    print()
    print("=" * 70)
    print("✅ STATISTICS COMPLETE")
    print("=" * 70)
    print(f"WakaTime: {'✅' if results.get('wakatime', {}).get('success') else '❌'}")
    print(f"Cursor: {'✅' if results.get('cursor', {}).get('success') else '❌'}")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())