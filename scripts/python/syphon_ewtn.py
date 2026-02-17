#!/usr/bin/env python3
"""
EWTN Content Syphon

Comprehensive scraper for EWTN (Eternal Word Television Network) content.
Extracts all articles, videos, audio, schedules, and other content using SYPHON.

Usage:
    python syphon_ewtn.py [--max-pages N] [--output-dir DIR] [--resume]
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
logger = get_logger("syphon_ewtn")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from scripts.python.syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    from scripts.python.syphon.core import SubscriptionTier
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    from syphon.core import SubscriptionTier


class EWTNSyphon:
    """Comprehensive EWTN content scraper using SYPHON"""

    BASE_URL = "https://www.ewtn.com"

    # Key sections to scrape
    SECTIONS = [
        "/news",
        "/tv",
        "/radio",
        "/ondemand",
        "/daily-mass",
        "/eucharistic-adoration",
        "/programs",
        "/articles",
        "/videos",
        "/audio",
        "/schedules",
    ]

    def __init__(self, project_root: Path, max_pages: int = 1000, output_dir: Path = None):
        """
        Initialize EWTN syphon.

        Args:
            project_root: Project root directory
            max_pages: Maximum number of pages to scrape
            output_dir: Output directory for scraped data
        """
        self.project_root = Path(project_root)
        self.max_pages = max_pages
        self.output_dir = output_dir or (self.project_root / "data" / "syphon" / "ewtn")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("EWTNSyphon")

        # Initialize SYPHON
        config = SYPHONConfig(
            project_root=self.project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE
        )
        self.syphon = SYPHONSystem(config)

        # Tracking
        self.visited_urls: Set[str] = set()
        self.urls_to_visit: List[str] = []
        self.scraped_count = 0
        self.failed_count = 0
        self.results: List[Dict] = []

        # State file for resuming
        self.state_file = self.output_dir / "syphon_state.json"

        # Headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def load_state(self) -> None:
        """Load previous state to resume scraping"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.visited_urls = set(state.get('visited_urls', []))
                    self.urls_to_visit = state.get('urls_to_visit', [])
                    self.scraped_count = state.get('scraped_count', 0)
                    self.logger.info(f"Loaded state: {len(self.visited_urls)} visited, {len(self.urls_to_visit)} queued")
            except Exception as e:
                self.logger.warning(f"Failed to load state: {e}")

    def save_state(self) -> None:
        """Save current state for resuming"""
        try:
            state = {
                'visited_urls': list(self.visited_urls),
                'urls_to_visit': self.urls_to_visit,
                'scraped_count': self.scraped_count,
                'failed_count': self.failed_count,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save state: {e}")

    def discover_urls(self) -> None:
        """Discover URLs to scrape from EWTN sections"""
        self.logger.info("Discovering EWTN URLs...")

        # Start with base sections
        for section in self.SECTIONS:
            url = urljoin(self.BASE_URL, section)
            if url not in self.visited_urls:
                self.urls_to_visit.append(url)

        # Also add base URL
        if self.BASE_URL not in self.visited_urls:
            self.urls_to_visit.append(self.BASE_URL)

        self.logger.info(f"Discovered {len(self.urls_to_visit)} initial URLs")

    def extract_links_from_page(self, url: str, soup: BeautifulSoup) -> List[str]:
        """Extract all relevant links from a page"""
        links = []

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue

            # Convert to absolute URL
            absolute_url = urljoin(url, href)
            parsed = urlparse(absolute_url)

            # Only include EWTN URLs
            if parsed.netloc and 'ewtn.com' in parsed.netloc:
                # Remove fragments and query params for deduplication
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

                # Filter out unwanted URLs
                if any(exclude in clean_url.lower() for exclude in [
                    '/login', '/register', '/logout', '/search?',
                    '/cart', '/checkout', '/account',
                    '.pdf', '.jpg', '.png', '.gif', '.css', '.js'
                ]):
                    continue

                if clean_url not in self.visited_urls and clean_url not in self.urls_to_visit:
                    links.append(clean_url)

        return links

    def scrape_page(self, url: str) -> Dict:
        """Scrape a single page and extract intelligence using SYPHON"""
        try:
            self.logger.info(f"Scraping: {url}")

            # Fetch page
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract links for further crawling
            new_links = self.extract_links_from_page(url, soup)
            for link in new_links:
                if len(self.urls_to_visit) < self.max_pages * 2:  # Limit queue size
                    self.urls_to_visit.append(link)

            # Use SYPHON to extract intelligence
            result = self.syphon.extract(DataSourceType.WEB, url, {
                "source": "ewtn",
                "scraped_at": datetime.now().isoformat()
            })

            if result.success and result.data:
                # Save extracted data
                output_file = self.output_dir / f"ewtn_{result.data.data_id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result.data.to_dict(), f, indent=2, ensure_ascii=False)

                self.scraped_count += 1

                return {
                    "url": url,
                    "success": True,
                    "data_id": result.data.data_id,
                    "title": result.data.metadata.get("title", ""),
                    "link_count": len(new_links),
                    "extracted_at": result.data.extracted_at.isoformat()
                }
            else:
                self.failed_count += 1
                return {
                    "url": url,
                    "success": False,
                    "error": result.error
                }

        except Exception as e:
            self.failed_count += 1
            self.logger.error(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "success": False,
                "error": str(e)
            }

    def run(self, resume: bool = False) -> None:
        try:
            """Run the EWTN syphon"""
            self.logger.info("=" * 60)
            self.logger.info("EWTN Content Syphon Starting")
            self.logger.info("=" * 60)

            # Load state if resuming
            if resume:
                self.load_state()
            else:
                # Start fresh
                self.discover_urls()

            # Main scraping loop
            while self.urls_to_visit and self.scraped_count < self.max_pages:
                url = self.urls_to_visit.pop(0)

                # Skip if already visited
                if url in self.visited_urls:
                    continue

                # Mark as visited
                self.visited_urls.add(url)

                # Scrape the page
                result = self.scrape_page(url)
                self.results.append(result)

                # Save state periodically
                if self.scraped_count % 10 == 0:
                    self.save_state()
                    self.logger.info(f"Progress: {self.scraped_count} scraped, {self.failed_count} failed, {len(self.urls_to_visit)} queued")

                # Be respectful - rate limiting
                time.sleep(1)  # 1 second between requests

            # Final save
            self.save_state()

            # Save summary
            summary = {
                "total_scraped": self.scraped_count,
                "total_failed": self.failed_count,
                "total_visited": len(self.visited_urls),
                "completed_at": datetime.now().isoformat(),
                "results": self.results
            }

            summary_file = self.output_dir / "syphon_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.logger.info("=" * 60)
            self.logger.info("EWTN Content Syphon Complete")
            self.logger.info(f"Scraped: {self.scraped_count}")
            self.logger.info(f"Failed: {self.failed_count}")
            self.logger.info(f"Total visited: {len(self.visited_urls)}")
            self.logger.info(f"Results saved to: {self.output_dir}")
            self.logger.info("=" * 60)


        except Exception as e:
            self.logger.error(f"Error in run: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(description="Syphon all EWTN content")
        parser.add_argument(
            "--max-pages",
            type=int,
            default=1000,
            help="Maximum number of pages to scrape (default: 1000)"
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            help="Output directory for scraped data (default: data/syphon/ewtn)"
        )
        parser.add_argument(
            "--resume",
            action="store_true",
            help="Resume from previous state"
        )
        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )

        args = parser.parse_args()

        # Create syphon instance
        syphon = EWTNSyphon(
            project_root=args.project_root,
            max_pages=args.max_pages,
            output_dir=args.output_dir
        )

        # Run
        syphon.run(resume=args.resume)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()