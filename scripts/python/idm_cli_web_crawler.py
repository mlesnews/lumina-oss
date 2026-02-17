#!/usr/bin/env python3
"""
IDM-CLI Web Crawler & Scraper
Uses Internet Download Manager CLI for web crawling and content scraping

Adapt, Improvise, Overcome - Alternative to yt-dlp and traditional scrapers

@IDM @IDM-CLI @WEB-CRAWLER @SCRAPER @SOURCES @ADAPT-IMPROVISE-OVERCOME
"""

import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse
import logging

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IDMCLIWebCrawler")


class IDMCLIWebCrawler:
    """
    Web crawler using IDM-CLI (Internet Download Manager CLI)

    Features:
    - Download web pages
    - Download videos
    - Download entire websites
    - Batch processing
    - Resume capability
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize IDM-CLI crawler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "idm_crawler"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Check if IDM-CLI is available
        self.idm_cli_path = self._find_idm_cli()
        self.idm_available = self.idm_cli_path is not None

        if self.idm_available:
            logger.info(f"✅ IDM found: {self.idm_cli_path}")
        else:
            logger.warning("⚠️  IDM not found - will use fallback methods")
            logger.info("   Install IDM or configure IDM path")
            logger.info("   Common locations:")
            logger.info("     - D:/Program Files (x86)/Internet Download Manager/IDMan.exe")
            logger.info("     - C:/Program Files (x86)/Internet Download Manager/IDMan.exe")

    def _find_idm_cli(self) -> Optional[Path]:
        """Find IDM executable (IDMan.exe)"""
        # Common IDM installation paths (checking both C and D drives)
        possible_paths = [
            Path("D:/Program Files (x86)/Internet Download Manager/IDMan.exe"),  # D drive prioritized
            Path("D:/Program Files/Internet Download Manager/IDMan.exe"),
            Path("C:/Program Files (x86)/Internet Download Manager/IDMan.exe"),
            Path("C:/Program Files/Internet Download Manager/IDMan.exe"),
            Path("C:/IDM/IDMan.exe"),
            Path("D:/IDM/IDMan.exe"),
            Path.home() / "AppData/Local/Programs/IDM/IDMan.exe"
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"   ✅ Found IDM at: {path}")
                return path

        # Check if IDM-CLI (npm package) is in PATH
        try:
            result = subprocess.run(['idm-cli', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("   ✅ Found IDM-CLI in PATH")
                return Path('idm-cli')  # Available in PATH
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Try PowerShell IDM script as fallback
        idm_ps_script = self.project_root / "scripts" / "powershell" / "Invoke-IDMDownload.ps1"
        if idm_ps_script.exists():
            logger.info(f"   ✅ Found IDM PowerShell script: {idm_ps_script}")
            return idm_ps_script  # Return script path for PowerShell execution

        return None

    def crawl_website(self, base_url: str, max_pages: int = 1000, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Crawl a website using IDM-CLI

        Args:
            base_url: Base URL to crawl
            max_pages: Maximum pages to download
            output_dir: Output directory for downloaded content

        Returns:
            Crawl results
        """
        logger.info(f"🕷️  Crawling website: {base_url}")
        logger.info(f"   Max pages: {max_pages}")

        if output_dir is None:
            output_dir = self.data_dir / urlparse(base_url).netloc.replace('.', '_')
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "base_url": base_url,
            "started_at": datetime.now().isoformat(),
            "pages_downloaded": 0,
            "files_downloaded": [],
            "errors": []
        }

        if not self.idm_available:
            logger.warning("⚠️  IDM-CLI not available - using fallback web scraping")
            return self._crawl_fallback(base_url, max_pages, output_dir)

        try:
            # Use IDM-CLI to download website
            # IDM can download entire websites with proper configuration
            command = [
                str(self.idm_cli_path),
                '/d', base_url,  # Download URL
                '/n',  # Don't start download immediately (queue it)
                '/a'   # Add to queue
            ]

            # For website crawling, we need to discover links first
            # Then queue them in IDM
            discovered_urls = self._discover_website_urls(base_url, max_pages)

            logger.info(f"   📋 Discovered {len(discovered_urls)} URLs")

            # Queue URLs in IDM
            queued = 0
            for url in discovered_urls[:max_pages]:
                try:
                    self._queue_download(url, output_dir)
                    queued += 1
                    if queued % 10 == 0:
                        logger.info(f"   📥 Queued {queued}/{len(discovered_urls)} URLs")
                except Exception as e:
                    logger.warning(f"   ⚠️  Error queueing {url}: {e}")
                    results["errors"].append({"url": url, "error": str(e)})

            results["pages_downloaded"] = queued
            results["completed_at"] = datetime.now().isoformat()

            logger.info(f"✅ Queued {queued} URLs in IDM")

        except Exception as e:
            logger.error(f"❌ IDM crawling failed: {e}")
            results["errors"].append({"error": str(e)})
            # Fallback to traditional scraping
            return self._crawl_fallback(base_url, max_pages, output_dir)

        return results

    def _discover_website_urls(self, base_url: str, max_urls: int = 1000) -> List[str]:
        """Discover URLs from a website"""
        import requests
        from bs4 import BeautifulSoup

        discovered: Set[str] = set()
        to_visit: List[str] = [base_url]
        visited: Set[str] = set()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        while to_visit and len(discovered) < max_urls:
            url = to_visit.pop(0)
            if url in visited:
                continue

            visited.add(url)

            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract all links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urljoin(url, href)

                        # Only include URLs from same domain
                        if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                            if absolute_url not in discovered:
                                discovered.add(absolute_url)
                                if len(discovered) < max_urls:
                                    to_visit.append(absolute_url)

                if len(discovered) % 50 == 0:
                    logger.debug(f"   Discovered {len(discovered)} URLs...")

            except Exception as e:
                logger.warning(f"   ⚠️  Error discovering {url}: {e}")
                continue

        return list(discovered)

    def _queue_download(self, url: str, output_dir: Path):
        """Queue a download in IDM using IDMan.exe or PowerShell script"""
        if not self.idm_available:
            return

        try:
            # Check if it's PowerShell script or IDMan.exe
            if str(self.idm_cli_path).endswith('.ps1'):
                # Use PowerShell script
                command = [
                    'powershell.exe',
                    '-ExecutionPolicy', 'Bypass',
                    '-File', str(self.idm_cli_path),
                    '-Url', url,
                    '-Destination', str(output_dir),
                    '-Description', f'Web crawl: {url}'
                ]
            else:
                # Use IDMan.exe directly
                command = [
                    str(self.idm_cli_path),
                    '/d', url,  # Download URL
                    '/p', str(output_dir),  # Save path
                    '/f', self._get_filename_from_url(url),  # Filename
                    '/n',  # Don't start immediately
                    '/a'   # Add to queue
                ]

            result = subprocess.run(command, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                raise Exception(f"IDM command failed: {result.stderr}")

        except Exception as e:
            logger.warning(f"   ⚠️  Error queueing download: {e}")
            raise

    def _get_filename_from_url(self, url: str) -> str:
        try:
            """Extract filename from URL"""
            parsed = urlparse(url)
            path = parsed.path

            # Get filename from path
            filename = Path(path).name

            # If no filename, use index.html
            if not filename or '.' not in filename:
                if path.endswith('/'):
                    filename = 'index.html'
                else:
                    filename = 'page.html'

            # Sanitize filename
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

            return filename

        except Exception as e:
            self.logger.error(f"Error in _get_filename_from_url: {e}", exc_info=True)
            raise
    def _crawl_fallback(self, base_url: str, max_pages: int, output_dir: Path) -> Dict[str, Any]:
        """Fallback crawling method using requests/BeautifulSoup"""
        logger.info("   🔄 Using fallback web scraping method")

        import requests
        from bs4 import BeautifulSoup

        results = {
            "base_url": base_url,
            "method": "fallback",
            "pages_downloaded": 0,
            "files_downloaded": [],
            "errors": []
        }

        # Use existing SYPHON web extraction
        try:
            from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
            from syphon.models import DataSourceType

            syphon = SYPHONSystem(SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE
            ))

            # Extract website content
            result = syphon.extract(
                DataSourceType.WEB,
                base_url,
                {
                    "url": base_url,
                    "max_pages": max_pages,
                    "output_dir": str(output_dir)
                }
            )

            if result.success:
                results["pages_downloaded"] = 1
                results["files_downloaded"].append(str(output_dir / "extracted_content.json"))

        except Exception as e:
            logger.error(f"   ❌ Fallback crawling failed: {e}")
            results["errors"].append({"error": str(e)})

        return results

    def download_video(self, video_url: str, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Download a video using IDM"""
        logger.info(f"📥 Downloading video: {video_url}")

        if output_dir is None:
            output_dir = self.data_dir / "videos"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self.idm_available:
            logger.warning("⚠️  IDM not available - using fallback")
            return {"success": False, "error": "IDM not available"}

        try:
            command = [
                str(self.idm_cli_path),
                '/d', video_url,
                '/p', str(output_dir),
                '/n',  # Don't start immediately
                '/a'   # Add to queue
            ]

            result = subprocess.run(command, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                logger.info(f"✅ Video queued in IDM: {video_url}")
                return {
                    "success": True,
                    "url": video_url,
                    "output_dir": str(output_dir),
                    "queued": True
                }
            else:
                raise Exception(f"IDM command failed: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Video download failed: {e}")
            return {"success": False, "error": str(e)}

    def batch_download_urls(self, urls: List[str], output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Batch download multiple URLs using IDM"""
        logger.info(f"📥 Batch downloading {len(urls)} URLs")

        if output_dir is None:
            output_dir = self.data_dir / "batch_downloads"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "total_urls": len(urls),
            "queued": 0,
            "failed": 0,
            "errors": []
        }

        for i, url in enumerate(urls, 1):
            try:
                result = self.download_video(url, output_dir)
                if result.get("success"):
                    results["queued"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({"url": url, "error": result.get("error")})

                if i % 10 == 0:
                    logger.info(f"   Progress: {i}/{len(urls)} URLs processed")

            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"url": url, "error": str(e)})

        logger.info(f"✅ Batch download complete: {results['queued']} queued, {results['failed']} failed")

        return results

    def crawl_youtube_channel(self, channel_url: str, max_videos: int = 500) -> Dict[str, Any]:
        """
        Crawl YouTube channel using IDM-CLI approach

        Adapt, Improvise, Overcome - Alternative to yt-dlp for YouTube channels

        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum videos to discover

        Returns:
            Channel crawl results with discovered videos
        """
        logger.info(f"📺 Crawling YouTube channel: {channel_url}")
        logger.info(f"   Max videos: {max_videos}")

        results = {
            "channel_url": channel_url,
            "started_at": datetime.now().isoformat(),
            "videos_discovered": 0,
            "videos": [],
            "errors": []
        }

        try:
            import requests
            from bs4 import BeautifulSoup

            # Get channel page HTML
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            # Try different channel page URLs
            channel_urls_to_try = [
                channel_url + '/videos',
                channel_url + '/playlists',
                channel_url
            ]

            videos = []
            for url_to_try in channel_urls_to_try:
                try:
                    logger.info(f"   🔍 Trying: {url_to_try}")
                    response = requests.get(url_to_try, headers=headers, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Extract video links from page
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            if '/watch?v=' in href:
                                video_id = href.split('watch?v=')[1].split('&')[0].split('#')[0]
                                title = link.get_text(strip=True) or f"Video {video_id}"
                                if video_id and len(video_id) == 11:  # Valid YouTube video ID
                                    videos.append({
                                        'id': video_id,
                                        'title': title,
                                        'url': f"https://www.youtube.com/watch?v={video_id}",
                                        'duration': 'unknown'
                                    })

                        # Also look for data attributes
                        for element in soup.find_all(attrs={'data-video-id': True}):
                            video_id = element.get('data-video-id')
                            title = element.get_text(strip=True) or f"Video {video_id}"
                            if video_id and len(video_id) == 11:
                                videos.append({
                                    'id': video_id,
                                    'title': title,
                                    'url': f"https://www.youtube.com/watch?v={video_id}",
                                    'duration': 'unknown'
                                })

                        if videos:
                            logger.info(f"   ✅ Found {len(videos)} videos from {url_to_try}")
                            break  # Found videos, no need to try other URLs

                except Exception as e:
                    logger.debug(f"   ⚠️  Error fetching {url_to_try}: {e}")
                    continue

            # Deduplicate by video ID
            seen = set()
            unique_videos = []
            for video in videos:
                if video['id'] not in seen:
                    seen.add(video['id'])
                    unique_videos.append(video)
                    if len(unique_videos) >= max_videos:
                        break

            results["videos_discovered"] = len(unique_videos)
            results["videos"] = unique_videos
            results["completed_at"] = datetime.now().isoformat()

            logger.info(f"✅ Discovered {len(unique_videos)} unique videos")

        except Exception as e:
            logger.error(f"❌ YouTube channel crawl failed: {e}")
            results["errors"].append({"error": str(e)})

        return results


def main():
    try:
        """CLI entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="IDM-CLI Web Crawler")
        parser.add_argument("--crawl", help="Website URL to crawl")
        parser.add_argument("--download", help="Video/URL to download")
        parser.add_argument("--batch", help="File with URLs (one per line)")
        parser.add_argument("--max-pages", type=int, default=1000, help="Max pages to crawl")
        parser.add_argument("--output", help="Output directory")

        args = parser.parse_args()

        crawler = IDMCLIWebCrawler()

        if args.crawl:
            output_dir = Path(args.output) if args.output else None
            results = crawler.crawl_website(args.crawl, args.max_pages, output_dir)
            print(json.dumps(results, indent=2))

        elif args.download:
            output_dir = Path(args.output) if args.output else None
            results = crawler.download_video(args.download, output_dir)
            print(json.dumps(results, indent=2))

        elif args.batch:
            with open(args.batch, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            output_dir = Path(args.output) if args.output else None
            results = crawler.batch_download_urls(urls, output_dir)
            print(json.dumps(results, indent=2))

        else:
            parser.print_help()
            return 1

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())