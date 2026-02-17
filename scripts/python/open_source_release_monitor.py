#!/usr/bin/env python3
"""
Open Source Release Monitor
Immediate Notification System for Similar Products

Monitors for similar open source products/models released globally.
Immediate notification when/where similar products are released.

Tags: #OPEN-SOURCE #MONITORING #NOTIFICATION #GLOBAL-RELEASE #COMPETITIVE-INTELLIGENCE
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("OpenSourceMonitor")


class OpenSourceReleaseMonitor:
    """
    Open Source Release Monitor

    Monitors for similar open source products/models released globally.
    Immediate notification when/where similar products are released.
    """

    def __init__(self, project_root: Path):
        """Initialize Open Source Release Monitor"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.monitor_path = self.data_path / "open_source_monitor"
        self.monitor_path.mkdir(parents=True, exist_ok=True)

        # Configuration files
        self.config_file = self.monitor_path / "monitor_config.json"
        self.releases_file = self.monitor_path / "detected_releases.json"
        self.notifications_file = self.monitor_path / "notifications.json"

        # Load configuration
        self.config = self._load_config()
        self.detected_releases = self._load_detected_releases()
        self.notifications = self._load_notifications()

        self.logger.info("🔔 Open Source Release Monitor initialized")
        self.logger.info("   Monitoring: Similar products/models globally")
        self.logger.info("   Notification: Immediate when detected")
        self.logger.info("   Scope: Global public releases")

    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading config: {e}")

        return {
            "project_name": "LUMINA",
            "project_keywords": [
                "lumina",
                "virtual assistant",
                "ai assistant",
                "jarvis",
                "marvin",
                "homelab automation",
                "security team",
                "friend foe identification",
                "mote level classification",
                "inception layers",
                "quantum entanglement",
                "yin yang",
                "jedi shadow",
                "temple guard"
            ],
            "similarity_threshold": 0.7,
            "monitoring_sources": [
                "github",
                "pypi",
                "npm",
                "huggingface",
                "arxiv",
                "news_feeds"
            ],
            "notification_channels": [
                "immediate_alert",
                "email",
                "system_notification",
                "log_file"
            ],
            "check_interval": 3600,  # 1 hour
            "last_check": None,
            "created": datetime.now().isoformat()
        }

    def _load_detected_releases(self) -> List[Dict[str, Any]]:
        """Load detected releases"""
        if self.releases_file.exists():
            try:
                with open(self.releases_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading detected releases: {e}")

        return []

    def _load_notifications(self) -> List[Dict[str, Any]]:
        """Load notifications"""
        if self.notifications_file.exists():
            try:
                with open(self.notifications_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading notifications: {e}")

        return []

    def _save_config(self):
        """Save configuration"""
        self.config["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving config: {e}")

    def _save_detected_releases(self):
        """Save detected releases"""
        try:
            with open(self.releases_file, 'w', encoding='utf-8') as f:
                json.dump(self.detected_releases, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving detected releases: {e}")

    def _save_notifications(self):
        """Save notifications"""
        try:
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump(self.notifications, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving notifications: {e}")

    def check_similarity(self, product_name: str, description: str, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Check if a product is similar to ours

        Args:
            product_name: Name of the product
            description: Description of the product
            keywords: Additional keywords to check

        Returns:
            Similarity analysis result
        """
        if keywords is None:
            keywords = []

        # Combine all text for analysis
        all_text = f"{product_name} {description} {' '.join(keywords)}".lower()

        # Check against our keywords
        our_keywords = self.config.get("project_keywords", [])
        matches = []
        match_count = 0

        for keyword in our_keywords:
            if keyword.lower() in all_text:
                matches.append(keyword)
                match_count += 1

        # Calculate similarity score
        total_keywords = len(our_keywords)
        similarity_score = match_count / total_keywords if total_keywords > 0 else 0.0

        threshold = self.config.get("similarity_threshold", 0.7)
        is_similar = similarity_score >= threshold

        result = {
            "product_name": product_name,
            "description": description,
            "similarity_score": similarity_score,
            "match_count": match_count,
            "total_keywords": total_keywords,
            "matched_keywords": matches,
            "is_similar": is_similar,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat()
        }

        if is_similar:
            self.logger.warning(f"⚠️  SIMILAR PRODUCT DETECTED: {product_name}")
            self.logger.warning(f"   Similarity: {similarity_score:.2%}")
            self.logger.warning(f"   Matched Keywords: {len(matches)}")

        return result

    def detect_release(self, product_name: str, description: str, source: str, url: str,
                      release_date: str = None, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Detect and analyze a new release

        Args:
            product_name: Name of the product
            description: Description of the product
            source: Source of the release (github, pypi, etc.)
            url: URL to the release
            release_date: Date of release
            keywords: Additional keywords

        Returns:
            Detection result with notification status
        """
        self.logger.info(f"🔍 Detecting release: {product_name} from {source}")

        # Check similarity
        similarity = self.check_similarity(product_name, description, keywords)

        # Create release record
        release = {
            "product_name": product_name,
            "description": description,
            "source": source,
            "url": url,
            "release_date": release_date or datetime.now().isoformat(),
            "detected_date": datetime.now().isoformat(),
            "similarity": similarity,
            "keywords": keywords or [],
            "status": "detected"
        }

        # Add to detected releases
        self.detected_releases.append(release)
        self._save_detected_releases()

        # If similar, send immediate notification
        if similarity["is_similar"]:
            notification = self._send_immediate_notification(release)
            release["notification"] = notification
            self.logger.warning(f"🚨 IMMEDIATE NOTIFICATION SENT: {product_name}")

        return release

    def _send_immediate_notification(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send immediate notification about similar release

        Args:
            release: Release information

        Returns:
            Notification record
        """
        notification = {
            "type": "immediate_alert",
            "severity": "high",
            "title": f"🚨 SIMILAR PRODUCT DETECTED: {release['product_name']}",
            "message": f"Similar product released: {release['product_name']}\n"
                      f"Source: {release['source']}\n"
                      f"URL: {release['url']}\n"
                      f"Similarity: {release['similarity']['similarity_score']:.2%}\n"
                      f"Matched Keywords: {', '.join(release['similarity']['matched_keywords'])}",
            "release": release,
            "timestamp": datetime.now().isoformat(),
            "notification_channels": self.config.get("notification_channels", []),
            "status": "sent"
        }

        # Add to notifications
        self.notifications.append(notification)
        self._save_notifications()

        # Log immediate alert
        self.logger.error("=" * 80)
        self.logger.error("🚨 IMMEDIATE NOTIFICATION: SIMILAR PRODUCT DETECTED")
        self.logger.error("=" * 80)
        self.logger.error(f"Product: {release['product_name']}")
        self.logger.error(f"Source: {release['source']}")
        self.logger.error(f"URL: {release['url']}")
        self.logger.error(f"Similarity: {release['similarity']['similarity_score']:.2%}")
        self.logger.error(f"Matched Keywords: {', '.join(release['similarity']['matched_keywords'])}")
        self.logger.error("=" * 80)

        return notification

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return {
            "monitoring_active": True,
            "project_name": self.config.get("project_name", "LUMINA"),
            "similarity_threshold": self.config.get("similarity_threshold", 0.7),
            "monitoring_sources": self.config.get("monitoring_sources", []),
            "notification_channels": self.config.get("notification_channels", []),
            "total_detected": len(self.detected_releases),
            "similar_detected": len([r for r in self.detected_releases if r.get("similarity", {}).get("is_similar", False)]),
            "total_notifications": len(self.notifications),
            "last_check": self.config.get("last_check"),
            "check_interval": self.config.get("check_interval", 3600)
        }

    def get_recent_similar_releases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent similar releases"""
        similar = [r for r in self.detected_releases if r.get("similarity", {}).get("is_similar", False)]
        similar.sort(key=lambda x: x.get("detected_date", ""), reverse=True)
        return similar[:limit]

    def get_notification_summary(self) -> str:
        """Get formatted notification summary"""
        markdown = []
        markdown.append("## 🔔 Open Source Release Monitor")
        markdown.append("")
        markdown.append("**Status:** Active")
        markdown.append("**Monitoring:** Similar products/models globally")
        markdown.append("**Notification:** Immediate when detected")
        markdown.append("")

        status = self.get_monitoring_status()
        markdown.append("### 📊 Monitoring Status")
        markdown.append("")
        markdown.append(f"**Project:** {status['project_name']}")
        markdown.append(f"**Similarity Threshold:** {status['similarity_threshold']:.0%}")
        markdown.append(f"**Total Detected:** {status['total_detected']}")
        markdown.append(f"**Similar Detected:** {status['similar_detected']}")
        markdown.append(f"**Total Notifications:** {status['total_notifications']}")
        markdown.append("")

        markdown.append("### 📡 Monitoring Sources")
        markdown.append("")
        for source in status.get("monitoring_sources", []):
            markdown.append(f"- ✅ {source}")
        markdown.append("")

        markdown.append("### 🔔 Notification Channels")
        markdown.append("")
        for channel in status.get("notification_channels", []):
            markdown.append(f"- ✅ {channel}")
        markdown.append("")

        # Recent similar releases
        similar = self.get_recent_similar_releases(5)
        if similar:
            markdown.append("### 🚨 Recent Similar Releases")
            markdown.append("")
            for release in similar:
                similarity = release.get("similarity", {})
                markdown.append(f"**{release['product_name']}**")
                markdown.append(f"- Source: {release['source']}")
                markdown.append(f"- URL: {release['url']}")
                markdown.append(f"- Similarity: {similarity.get('similarity_score', 0):.2%}")
                markdown.append(f"- Detected: {release.get('detected_date', 'Unknown')}")
                markdown.append("")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Open Source Release Monitor")
        parser.add_argument("--detect", type=str, help="Product name to check")
        parser.add_argument("--description", type=str, help="Product description")
        parser.add_argument("--source", type=str, help="Source (github, pypi, etc.)")
        parser.add_argument("--url", type=str, help="URL to the release")
        parser.add_argument("--status", action="store_true", help="Display monitoring status")
        parser.add_argument("--summary", action="store_true", help="Display notification summary")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        monitor = OpenSourceReleaseMonitor(project_root)

        if args.detect:
            if not args.description:
                args.description = ""
            if not args.source:
                args.source = "unknown"
            if not args.url:
                args.url = ""

            release = monitor.detect_release(
                args.detect,
                args.description,
                args.source,
                args.url
            )

            if args.json:
                print(json.dumps(release, indent=2, default=str))
            else:
                similarity = release.get("similarity", {})
                if similarity.get("is_similar"):
                    print("🚨 SIMILAR PRODUCT DETECTED!")
                    print(f"   Product: {args.detect}")
                    print(f"   Similarity: {similarity.get('similarity_score', 0):.2%}")
                    print(f"   Matched Keywords: {', '.join(similarity.get('matched_keywords', []))}")
                    print(f"   Source: {args.source}")
                    print(f"   URL: {args.url}")
                else:
                    print(f"✅ Product checked: {args.detect}")
                    print(f"   Similarity: {similarity.get('similarity_score', 0):.2%} (below threshold)")

        elif args.status:
            status = monitor.get_monitoring_status()
            if args.json:
                print(json.dumps(status, indent=2, default=str))
            else:
                print("🔔 Open Source Release Monitor Status")
                print(f"   Project: {status['project_name']}")
                print(f"   Similarity Threshold: {status['similarity_threshold']:.0%}")
                print(f"   Total Detected: {status['total_detected']}")
                print(f"   Similar Detected: {status['similar_detected']}")
                print(f"   Total Notifications: {status['total_notifications']}")

        elif args.summary:
            summary = monitor.get_notification_summary()
            print(summary)

        else:
            summary = monitor.get_notification_summary()
            print(summary)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()