#!/usr/bin/env python3
"""
JARVIS SYPHON @moondev and @thetradingparrot
SYPHON all sources: YouTube, GitHub, Discord, Website, etc.

@JARVIS @SYPHON @MOONDEV @THETRADINGPARROT @YOUTUBE @GITHUB @DISCORD
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSyphonMoondevParrot")


class SyphonMoondevTradingParrot:
    """
    SYPHON @moondev and @thetradingparrot

    Extract from all sources:
    - YouTube channels
    - GitHub repositories
    - Discord servers
    - Websites
    - Social media
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON for moondev and tradingparrot"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # WOPR pattern matcher
        try:
            from scripts.python.jarvis_syphon_financial_strategies_wopr import WOPRPatternMatcher
            self.wopr = WOPRPatternMatcher()
        except Exception as e:
            logger.warning(f"WOPR not available: {e}")
            self.wopr = None

        # YouTube crawler
        try:
            from scripts.python.youtube_deep_crawl_sme_mapper import YouTubeDeepCrawler
            self.youtube_crawler = YouTubeDeepCrawler(project_root=self.project_root)
            logger.info("✅ YouTube Deep Crawler integrated")
        except Exception as e:
            logger.warning(f"YouTube crawler not available: {e}")
            self.youtube_crawler = None

        # Sources to SYPHON
        self.sources = {
            "moondev": {
                "name": "@moondev",
                "youtube": "moondev",  # Channel name/ID
                "github": "moondev",  # GitHub username
                "discord": "moondev",  # Discord server
                "website": "moondev.com",  # Website
                "type": "financial_creator"
            },
            "thetradingparrot": {
                "name": "@thetradingparrot",
                "youtube": "thetradingparrot",  # Channel name/ID
                "github": "thetradingparrot",  # GitHub username
                "discord": "thetradingparrot",  # Discord server
                "website": "thetradingparrot.com",  # Website
                "type": "trading_educator"
            }
        }

        # Output directory
        self.output_dir = self.project_root / "data" / "syphon_moondev_parrot"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ SYPHON Moondev & TradingParrot initialized")

    async def syphon_all_sources(self) -> Dict[str, Any]:
        """SYPHON all sources for both creators"""
        logger.info("=" * 70)
        logger.info("🔍 SYPHON @MOONDEV & @THETRADINGPARROT")
        logger.info("   All sources: YouTube, GitHub, Discord, Website")
        logger.info("=" * 70)
        logger.info("")

        results = {
            "syphon_started": datetime.now().isoformat(),
            "moondev": {},
            "thetradingparrot": {},
            "total_strategies": 0,
            "patterns_found": {}
        }

        # SYPHON @moondev
        logger.info("SYPHON @MOONDEV:")
        logger.info("-" * 70)
        moondev_results = await self._syphon_creator("moondev")
        results["moondev"] = moondev_results

        # SYPHON @thetradingparrot
        logger.info("\nSYPHON @THETRADINGPARROT:")
        logger.info("-" * 70)
        tradingparrot_results = await self._syphon_creator("thetradingparrot")
        results["thetradingparrot"] = tradingparrot_results

        # Aggregate strategies
        all_strategies = []
        all_strategies.extend(moondev_results.get("strategies", []))
        all_strategies.extend(tradingparrot_results.get("strategies", []))
        results["total_strategies"] = len(all_strategies)

        # Process with WOPR
        if self.wopr:
            logger.info("\nPROCESSING WITH WOPR PATTERN MATCHING...")
            for strategy in all_strategies:
                text = strategy.get("text", "")
                wopr_matches = self.wopr.match_patterns(text)
                strategy["wopr_patterns"] = wopr_matches

                # Aggregate patterns
                for pattern, matches in wopr_matches.items():
                    if pattern not in results["patterns_found"]:
                        results["patterns_found"][pattern] = []
                    results["patterns_found"][pattern].extend(matches)

        results["syphon_completed"] = datetime.now().isoformat()

        # Save results
        self._save_results(results)

        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 SYPHON RESULTS")
        logger.info("=" * 70)
        logger.info(f"@moondev strategies: {len(moondev_results.get('strategies', []))}")
        logger.info(f"@thetradingparrot strategies: {len(tradingparrot_results.get('strategies', []))}")
        logger.info(f"Total strategies: {results['total_strategies']}")
        logger.info(f"Patterns found: {len(results['patterns_found'])}")
        logger.info("=" * 70)

        return results

    async def _syphon_creator(self, creator_id: str) -> Dict[str, Any]:
        """SYPHON a specific creator from all sources"""
        creator_info = self.sources.get(creator_id, {})
        creator_name = creator_info.get("name", creator_id)

        logger.info(f"   SYPHON {creator_name}...")

        results = {
            "creator": creator_name,
            "sources": {},
            "strategies": [],
            "extraction_timestamp": datetime.now().isoformat()
        }

        # Source 1: YouTube
        logger.info(f"     YouTube: {creator_info.get('youtube', 'N/A')}")
        youtube_results = await self._syphon_youtube(creator_info)
        results["sources"]["youtube"] = youtube_results
        results["strategies"].extend(youtube_results.get("strategies", []))

        # Source 2: GitHub
        logger.info(f"     GitHub: {creator_info.get('github', 'N/A')}")
        github_results = await self._syphon_github(creator_info)
        results["sources"]["github"] = github_results
        results["strategies"].extend(github_results.get("strategies", []))

        # Source 3: Discord
        logger.info(f"     Discord: {creator_info.get('discord', 'N/A')}")
        discord_results = await self._syphon_discord(creator_info)
        results["sources"]["discord"] = discord_results
        results["strategies"].extend(discord_results.get("strategies", []))

        # Source 4: Website
        logger.info(f"     Website: {creator_info.get('website', 'N/A')}")
        website_results = await self._syphon_website(creator_info)
        results["sources"]["website"] = website_results
        results["strategies"].extend(website_results.get("strategies", []))

        return results

    async def _syphon_youtube(self, creator_info: Dict[str, Any]) -> Dict[str, Any]:
        """SYPHON YouTube channel"""
        strategies = []

        if not self.youtube_crawler:
            return {
                "source": "YouTube",
                "strategies": [],
                "status": "crawler_not_available"
            }

        youtube_handle = creator_info.get("youtube", "")

        # Try to discover channel
        try:
            channels = self.youtube_crawler.discover_channels_by_domain(youtube_handle, max_results=5)

            for channel in channels:
                channel_id = channel.get("channel_id")
                if not channel_id:
                    continue

                # Crawl channel
                videos = self.youtube_crawler.crawl_channel(channel_id, max_videos=10)

                for video in videos:
                    video_text = f"{video.get('title', '')} {video.get('description', '')}"

                    if self.wopr:
                        wopr_matches = self.wopr.match_patterns(video_text)
                        if wopr_matches:
                            strategies.append({
                                "source": f"YouTube: {channel.get('channel_name', 'Unknown')}",
                                "type": "youtube_video",
                                "video_id": video.get("id"),
                                "video_title": video.get("title"),
                                "text": video_text[:1000],
                                "wopr_patterns": wopr_matches,
                                "extracted_at": datetime.now().isoformat()
                            })
        except Exception as e:
            logger.warning(f"     Could not SYPHON YouTube: {e}")

        return {
            "source": "YouTube",
            "strategies": strategies,
            "videos_processed": len(strategies),
            "status": "complete"
        }

    async def _syphon_github(self, creator_info: Dict[str, Any]) -> Dict[str, Any]:
        """SYPHON GitHub repositories"""
        strategies = []

        github_username = creator_info.get("github", "")

        # In production, would use GitHub API
        # For now, simulate extraction
        logger.info(f"       (GitHub API integration required for: {github_username})")

        return {
            "source": "GitHub",
            "strategies": strategies,
            "status": "simulated",
            "note": "GitHub API integration required"
        }

    async def _syphon_discord(self, creator_info: Dict[str, Any]) -> Dict[str, Any]:
        """SYPHON Discord server"""
        strategies = []

        discord_server = creator_info.get("discord", "")

        # In production, would use Discord API or bot
        logger.info(f"       (Discord API integration required for: {discord_server})")

        return {
            "source": "Discord",
            "strategies": strategies,
            "status": "simulated",
            "note": "Discord API/bot integration required"
        }

    async def _syphon_website(self, creator_info: Dict[str, Any]) -> Dict[str, Any]:
        """SYPHON website"""
        strategies = []

        website = creator_info.get("website", "")

        # In production, would use web scraping
        logger.info(f"       (Web scraping required for: {website})")

        return {
            "source": "Website",
            "strategies": strategies,
            "status": "simulated",
            "note": "Web scraping implementation required"
        }

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save SYPHON results"""
        try:
            filename = self.output_dir / f"moondev_parrot_syphon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"✅ Results saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔍 SYPHON @MOONDEV & @THETRADINGPARROT")
    print("   All sources: YouTube, GitHub, Discord, Website")
    print("=" * 70)
    print()

    syphon = SyphonMoondevTradingParrot()
    results = await syphon.syphon_all_sources()

    print()
    print("=" * 70)
    print("✅ SYPHON COMPLETE")
    print("=" * 70)
    print(f"Total strategies: {results.get('total_strategies', 0)}")
    print(f"Patterns found: {len(results.get('patterns_found', {}))}")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())