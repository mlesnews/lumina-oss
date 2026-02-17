#!/usr/bin/env python3
"""
Affiliate Network Platform

Unified platform for EWTN, Magis Center, and their affiliates.
Provides content aggregation, analytics, and cross-affiliate services.

Usage:
    python affiliate_network_platform.py --add-affiliate "Organization Name" --url "https://..."
    python affiliate_network_platform.py --sync-all
    python affiliate_network_platform.py --analytics
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
logger = get_logger("affiliate_network_platform")


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


@dataclass
class Affiliate:
    """Represents an affiliate organization"""
    name: str
    url: str
    description: str = ""
    contact_email: str = ""
    tags: List[str] = None
    enabled: bool = True
    added_at: str = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.added_at is None:
            self.added_at = datetime.now().isoformat()


class AffiliateNetworkPlatform:
    """Unified platform for managing affiliate network"""

    def __init__(self, project_root: Path, data_dir: Path = None):
        """
        Initialize Affiliate Network Platform.

        Args:
            project_root: Project root directory
            data_dir: Data directory for platform data
        """
        self.project_root = Path(project_root)
        self.data_dir = data_dir or (self.project_root / "data" / "affiliate_network")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("AffiliateNetworkPlatform")

        # Affiliates registry
        self.affiliates_file = self.data_dir / "affiliates.json"
        self.affiliates: Dict[str, Affiliate] = {}

        # Content index
        self.content_index_file = self.data_dir / "content_index.json"
        self.content_index: List[Dict] = []

        # Analytics
        self.analytics_file = self.data_dir / "analytics.json"

        # Initialize SYPHON
        config = SYPHONConfig(
            project_root=self.project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE
        )
        self.syphon = SYPHONSystem(config)

        # Load existing data
        self.load_affiliates()
        self.load_content_index()

    def load_affiliates(self) -> None:
        """Load affiliates from file"""
        if self.affiliates_file.exists():
            try:
                with open(self.affiliates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, aff_data in data.items():
                        self.affiliates[name] = Affiliate(**aff_data)
                self.logger.info(f"Loaded {len(self.affiliates)} affiliates")
            except Exception as e:
                self.logger.warning(f"Failed to load affiliates: {e}")
        else:
            # Initialize with EWTN and Magis Center
            self.add_affiliate(
                name="EWTN",
                url="https://www.ewtn.com",
                description="Eternal Word Television Network - Global Catholic media network",
                tags=["media", "television", "radio", "catholic"]
            )
            self.add_affiliate(
                name="Magis Center",
                url="https://www.magiscenter.com",
                description="Faith, science, and philosophy education - magisAI app",
                tags=["education", "faith-science", "philosophy", "ai"]
            )

    def save_affiliates(self) -> None:
        """Save affiliates to file"""
        try:
            data = {name: asdict(aff) for name, aff in self.affiliates.items()}
            with open(self.affiliates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save affiliates: {e}")

    def load_content_index(self) -> None:
        """Load content index"""
        if self.content_index_file.exists():
            try:
                with open(self.content_index_file, 'r', encoding='utf-8') as f:
                    self.content_index = json.load(f)
                self.logger.info(f"Loaded {len(self.content_index)} content items")
            except Exception as e:
                self.logger.warning(f"Failed to load content index: {e}")

    def save_content_index(self) -> None:
        """Save content index"""
        try:
            with open(self.content_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.content_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save content index: {e}")

    def add_affiliate(
        self,
        name: str,
        url: str,
        description: str = "",
        contact_email: str = "",
        tags: List[str] = None
    ) -> bool:
        """
        Add a new affiliate to the network.

        Args:
            name: Affiliate name
            url: Affiliate website URL
            description: Description of the affiliate
            contact_email: Contact email
            tags: Tags for categorization

        Returns:
            True if added successfully
        """
        if name in self.affiliates:
            self.logger.warning(f"Affiliate '{name}' already exists")
            return False

        affiliate = Affiliate(
            name=name,
            url=url,
            description=description,
            contact_email=contact_email,
            tags=tags or []
        )

        self.affiliates[name] = affiliate
        self.save_affiliates()

        self.logger.info(f"Added affiliate: {name} ({url})")
        return True

    def sync_affiliate_content(self, affiliate_name: str) -> Dict:
        """
        Sync content from an affiliate.

        Args:
            affiliate_name: Name of the affiliate to sync

        Returns:
            Sync results dictionary
        """
        if affiliate_name not in self.affiliates:
            return {"success": False, "error": f"Affiliate '{affiliate_name}' not found"}

        affiliate = self.affiliates[affiliate_name]

        if not affiliate.enabled:
            return {"success": False, "error": f"Affiliate '{affiliate_name}' is disabled"}

        self.logger.info(f"Syncing content from {affiliate_name}...")

        # Use SYPHON to extract content
        result = self.syphon.extract(DataSourceType.WEB, affiliate.url, {
            "affiliate": affiliate_name,
            "source": "affiliate_network",
            "synced_at": datetime.now().isoformat()
        })

        if result.success and result.data:
            # Add to content index
            content_item = {
                "affiliate": affiliate_name,
                "data_id": result.data.data_id,
                "url": result.data.source_id,
                "title": result.data.metadata.get("title", ""),
                "content": result.data.content[:500],  # Preview
                "metadata": result.data.metadata,
                "extracted_at": result.data.extracted_at.isoformat(),
                "tags": affiliate.tags
            }

            # Check if already indexed
            existing = next(
                (item for item in self.content_index 
                 if item.get("data_id") == content_item["data_id"]),
                None
            )

            if not existing:
                self.content_index.append(content_item)
                self.save_content_index()

            return {
                "success": True,
                "affiliate": affiliate_name,
                "content_items": 1,
                "data_id": result.data.data_id
            }
        else:
            return {
                "success": False,
                "affiliate": affiliate_name,
                "error": result.error
            }

    def sync_all_affiliates(self) -> Dict:
        """Sync content from all enabled affiliates"""
        self.logger.info("Syncing all affiliates...")

        results = {
            "total": len(self.affiliates),
            "synced": 0,
            "failed": 0,
            "details": []
        }

        for name, affiliate in self.affiliates.items():
            if affiliate.enabled:
                result = self.sync_affiliate_content(name)
                results["details"].append(result)

                if result["success"]:
                    results["synced"] += 1
                else:
                    results["failed"] += 1

        self.logger.info(f"Sync complete: {results['synced']} synced, {results['failed']} failed")
        return results

    def search_content(self, query: str, affiliate: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search content across affiliates.

        Args:
            query: Search query
            affiliate: Optional affiliate name to filter by
            limit: Maximum results to return

        Returns:
            List of matching content items
        """
        query_lower = query.lower()
        results = []

        for item in self.content_index:
            # Filter by affiliate if specified
            if affiliate and item.get("affiliate") != affiliate:
                continue

            score = 0

            # Score based on title
            if query_lower in item.get("title", "").lower():
                score += 10

            # Score based on content
            if query_lower in item.get("content", "").lower():
                score += 5

            # Score based on tags
            for tag in item.get("tags", []):
                if query_lower in tag.lower():
                    score += 3

            if score > 0:
                results.append({
                    "score": score,
                    "item": item
                })

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return [r["item"] for r in results[:limit]]

    def get_analytics(self) -> Dict:
        """Get network analytics"""
        analytics = {
            "total_affiliates": len(self.affiliates),
            "enabled_affiliates": sum(1 for a in self.affiliates.values() if a.enabled),
            "total_content_items": len(self.content_index),
            "content_by_affiliate": {},
            "tags_distribution": {},
            "recent_content": []
        }

        # Content by affiliate
        for item in self.content_index:
            affiliate = item.get("affiliate", "unknown")
            analytics["content_by_affiliate"][affiliate] = \
                analytics["content_by_affiliate"].get(affiliate, 0) + 1

        # Tags distribution
        for item in self.content_index:
            for tag in item.get("tags", []):
                analytics["tags_distribution"][tag] = \
                    analytics["tags_distribution"].get(tag, 0) + 1

        # Recent content (last 10)
        sorted_content = sorted(
            self.content_index,
            key=lambda x: x.get("extracted_at", ""),
            reverse=True
        )
        analytics["recent_content"] = [
            {
                "title": item.get("title", ""),
                "affiliate": item.get("affiliate", ""),
                "url": item.get("url", ""),
                "extracted_at": item.get("extracted_at", "")
            }
            for item in sorted_content[:10]
        ]

        return analytics

    def generate_network_report(self) -> str:
        """Generate a network status report"""
        analytics = self.get_analytics()

        report = f"""
=== Affiliate Network Platform Report ===
Generated: {datetime.now().isoformat()}

AFFILIATES:
  Total: {analytics['total_affiliates']}
  Enabled: {analytics['enabled_affiliates']}

CONTENT:
  Total Items: {analytics['total_content_items']}

  By Affiliate:
"""
        for affiliate, count in sorted(
            analytics['content_by_affiliate'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            report += f"    {affiliate}: {count} items\n"

        report += f"\n  Top Tags:\n"
        for tag, count in sorted(
            analytics['tags_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            report += f"    {tag}: {count}\n"

        report += f"\n  Recent Content:\n"
        for item in analytics['recent_content'][:5]:
            report += f"    - {item['title']} ({item['affiliate']})\n"

        return report


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(description="Affiliate Network Platform")
        parser.add_argument(
            "--add-affiliate",
            type=str,
            help="Add a new affiliate (requires --url)"
        )
        parser.add_argument(
            "--url",
            type=str,
            help="Affiliate URL"
        )
        parser.add_argument(
            "--description",
            type=str,
            default="",
            help="Affiliate description"
        )
        parser.add_argument(
            "--tags",
            type=str,
            help="Comma-separated tags"
        )
        parser.add_argument(
            "--sync-all",
            action="store_true",
            help="Sync content from all affiliates"
        )
        parser.add_argument(
            "--sync",
            type=str,
            help="Sync content from specific affiliate"
        )
        parser.add_argument(
            "--analytics",
            action="store_true",
            help="Show network analytics"
        )
        parser.add_argument(
            "--report",
            action="store_true",
            help="Generate network report"
        )
        parser.add_argument(
            "--search",
            type=str,
            help="Search content across affiliates"
        )
        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )

        args = parser.parse_args()

        # Create platform
        platform = AffiliateNetworkPlatform(project_root=args.project_root)

        if args.add_affiliate:
            if not args.url:
                print("Error: --url required when adding affiliate")
                return

            tags = args.tags.split(',') if args.tags else []
            platform.add_affiliate(
                name=args.add_affiliate,
                url=args.url,
                description=args.description,
                tags=[t.strip() for t in tags]
            )

        elif args.sync_all:
            results = platform.sync_all_affiliates()
            print(json.dumps(results, indent=2))

        elif args.sync:
            result = platform.sync_affiliate_content(args.sync)
            print(json.dumps(result, indent=2))

        elif args.analytics:
            analytics = platform.get_analytics()
            print(json.dumps(analytics, indent=2))

        elif args.report:
            report = platform.generate_network_report()
            print(report)

        elif args.search:
            results = platform.search_content(args.search)
            print(json.dumps(results, indent=2))

        else:
            # Show status
            analytics = platform.get_analytics()
            print(f"Affiliate Network Platform")
            print(f"  Affiliates: {analytics['total_affiliates']}")
            print(f"  Content Items: {analytics['total_content_items']}")
            print("\nUse --help for available commands")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()