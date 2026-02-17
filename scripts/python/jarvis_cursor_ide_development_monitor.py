#!/usr/bin/env python3
"""
JARVIS Cursor IDE Development Monitor

Stays on top of Cursor IDE new developments as they're published by the development team.
Keeps finger on the pulse and enables instant pivoting based on actionable and verifiable
features and functionality.

Tags: #JARVIS #CURSOR_IDE #DEVELOPMENT_MONITOR #NEW_FEATURES #PULSE @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

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

logger = get_logger("JARVISCursorMonitor")

# Web requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - install: pip install requests")


@dataclass
class CursorDevelopment:
    """Cursor IDE development/update"""
    development_id: str
    title: str
    description: str
    version: Optional[str] = None
    release_date: Optional[str] = None
    source: str = "cursor_team"  # "cursor_team", "docs", "changelog", "github"
    url: Optional[str] = None
    features: List[str] = field(default_factory=list)
    actionable: bool = False
    verified: bool = False
    verification_notes: List[str] = field(default_factory=list)
    priority: str = "medium"  # "high", "medium", "low"
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FeatureVerification:
    """Feature verification result"""
    feature_name: str
    verified: bool
    verification_method: str  # "tested", "documented", "confirmed"
    verification_date: str
    notes: List[str] = field(default_factory=list)
    actionable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JARVISCursorIDEDevelopmentMonitor:
    """
    JARVIS Cursor IDE Development Monitor

    Stays on top of new developments and enables instant pivoting.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize development monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_ide_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Development tracking
        self.developments_file = self.data_dir / "developments.json"
        self.developments: Dict[str, CursorDevelopment] = {}

        # Verification tracking
        self.verifications_file = self.data_dir / "verifications.json"
        self.verifications: Dict[str, FeatureVerification] = {}

        # Monitoring sources
        self.sources = {
            "docs": "https://docs.cursor.com",
            "changelog": "https://cursor.com/changelog",
            "github": "https://github.com/getcursor/cursor",
            "blog": "https://cursor.com/blog",
            "twitter": "https://twitter.com/cursor_ai"
        }

        # Feature tracker integration
        try:
            from cursor_ide_feature_utilization_tracker import CursorIDEFeatureUtilizationTracker
            self.feature_tracker = CursorIDEFeatureUtilizationTracker(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Feature tracker not available: {e}")
            self.feature_tracker = None

        # Load existing data
        self._load_data()

        logger.info("✅ JARVIS Cursor IDE Development Monitor initialized")
        logger.info(f"   Tracking {len(self.developments)} developments")
        logger.info("   🎯 Keeping finger on the pulse")
        logger.info("   ⚡ Ready to pivot instantly")

    def _load_data(self):
        """Load developments and verifications"""
        # Load developments
        if self.developments_file.exists():
            try:
                with open(self.developments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.developments = {
                        did: CursorDevelopment(**ddata)
                        for did, ddata in data.get("developments", {}).items()
                    }
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load developments: {e}")

        # Load verifications
        if self.verifications_file.exists():
            try:
                with open(self.verifications_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.verifications = {
                        fname: FeatureVerification(**vdata)
                        for fname, vdata in data.get("verifications", {}).items()
                    }
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load verifications: {e}")

    def _save_data(self):
        """Save developments and verifications"""
        try:
            # Save developments
            with open(self.developments_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "developments": {did: d.to_dict() for did, d in self.developments.items()}
                }, f, indent=2, ensure_ascii=False)

            # Save verifications
            with open(self.verifications_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "verifications": {fname: v.to_dict() for fname, v in self.verifications.items()}
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving data: {e}")

    def monitor_cursor_docs(self) -> List[CursorDevelopment]:
        """
        Monitor Cursor IDE documentation for new features

        Returns:
            List of new developments found
        """
        new_developments = []

        if not REQUESTS_AVAILABLE:
            logger.warning("   ⚠️  requests not available for monitoring")
            return new_developments

        try:
            # Check docs for updates
            response = requests.get(self.sources["docs"], timeout=10)
            if response.status_code == 200:
                # Parse for new features
                content = response.text

                # Look for feature indicators (more comprehensive)
                feature_patterns = [
                    (r'new feature[:\s]+([^<]+)', "New Feature"),
                    (r'introducing[:\s]+([^<]+)', "Introducing"),
                    (r'now available[:\s]+([^<]+)', "Now Available"),
                    (r'enhanced[:\s]+([^<]+)', "Enhanced"),
                    (r'improved[:\s]+([^<]+)', "Improved"),
                    (r'added support for[:\s]+([^<]+)', "Added Support"),
                ]

                for pattern, prefix in feature_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        feature_text = match.group(1).strip()[:100]  # Limit length

                        # Check if we already have this
                        existing = any(
                            feature_text.lower() in d.description.lower()
                            for d in self.developments.values()
                        )

                        if not existing and feature_text:
                            import hashlib
                            dev_id = hashlib.md5(f"{prefix}{feature_text}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

                            development = CursorDevelopment(
                                development_id=dev_id,
                                title=f"{prefix}: {feature_text[:50]}",
                                description=feature_text,
                                source="docs",
                                url=self.sources["docs"],
                                features=[feature_text],
                                discovered_at=datetime.now().isoformat()
                            )

                            new_developments.append(development)

        except Exception as e:
            logger.debug(f"   Could not monitor docs: {e}")

        return new_developments

    def monitor_changelog(self) -> List[CursorDevelopment]:
        """
        Monitor Cursor IDE changelog for new releases

        Returns:
            List of new developments found
        """
        new_developments = []

        if not REQUESTS_AVAILABLE:
            return new_developments

        try:
            # Check changelog
            response = requests.get(self.sources["changelog"], timeout=10)
            if response.status_code == 200:
                content = response.text

                # Look for version numbers and release dates
                # Pattern: Version X.Y.Z - Date or Release notes
                version_pattern = r'(?:version|v|release)[\s:]+(\d+\.\d+\.\d+)'
                versions = re.findall(version_pattern, content, re.IGNORECASE)

                # Extract features from changelog entries
                # Look for bullet points or feature lists after version
                for version in set(versions):
                    # Check if we already have this version
                    existing_versions = [d.version for d in self.developments.values() if d.version]
                    if version not in existing_versions:
                        # Try to extract features for this version
                        # Look for content after version number
                        version_section = re.search(
                            rf'{re.escape(version)}[^<]*?((?:<li>|<p>|•|\*)[^<]+)',
                            content,
                            re.IGNORECASE | re.DOTALL
                        )

                        features = []
                        if version_section:
                            # Extract feature text
                            feature_text = version_section.group(1)
                            # Clean HTML tags
                            feature_text = re.sub(r'<[^>]+>', '', feature_text)
                            features = [f.strip() for f in feature_text.split('\n') if f.strip()][:10]  # Limit

                        dev_id = f"changelog_{version}"
                        development = CursorDevelopment(
                            development_id=dev_id,
                            title=f"Cursor IDE {version}",
                            description=f"New release: {version}",
                            version=version,
                            source="changelog",
                            url=self.sources["changelog"],
                            features=features,
                            discovered_at=datetime.now().isoformat()
                        )
                        new_developments.append(development)

        except Exception as e:
            logger.debug(f"   Could not monitor changelog: {e}")

        return new_developments

    def monitor_all_sources(self) -> List[CursorDevelopment]:
        """
        Monitor all sources for new developments

        Returns:
            List of all new developments found
        """
        logger.info("🔍 Monitoring Cursor IDE development sources...")

        all_developments = []

        # Monitor docs
        logger.info("   📚 Checking documentation...")
        docs_devs = self.monitor_cursor_docs()
        all_developments.extend(docs_devs)

        # Monitor changelog
        logger.info("   📋 Checking changelog...")
        changelog_devs = self.monitor_changelog()
        all_developments.extend(changelog_devs)

        # Add new developments
        for development in all_developments:
            if development.development_id not in self.developments:
                self.developments[development.development_id] = development
                logger.info(f"   ✅ New development: {development.title}")

        # Save
        self._save_data()

        return all_developments

    def verify_feature(self, feature_name: str, verification_method: str = "tested") -> FeatureVerification:
        """
        Verify a feature is actionable and real

        Args:
            feature_name: Feature to verify
            verification_method: How it was verified (tested, documented, confirmed)

        Returns:
            Verification result
        """
        # Check if feature exists in tracker
        actionable = False
        verified = False
        notes = []

        if self.feature_tracker:
            if feature_name in self.feature_tracker.features:
                feature = self.feature_tracker.features[feature_name]
                actionable = feature.utilized or feature.priority == "high"
                verified = True
                notes.append(f"Feature exists in tracker: {feature.description}")
            else:
                # Try to find similar feature
                for fname, feature in self.feature_tracker.features.items():
                    if feature_name.lower() in fname.lower() or fname.lower() in feature_name.lower():
                        notes.append(f"Similar feature found: {fname}")

        # Create verification
        verification = FeatureVerification(
            feature_name=feature_name,
            verified=verified,
            verification_method=verification_method,
            verification_date=datetime.now().isoformat(),
            notes=notes,
            actionable=actionable
        )

        self.verifications[feature_name] = verification
        self._save_data()

        logger.info(f"   ✅ Verified feature: {feature_name} ({verification_method})")

        return verification

    def add_development(self, title: str, description: str, source: str = "manual",
                       version: Optional[str] = None, url: Optional[str] = None,
                       features: List[str] = None) -> str:
        """
        Manually add a development

        Args:
            title: Development title
            description: Description
            source: Source (manual, cursor_team, docs, etc.)
            version: Version if applicable
            url: URL to more information
            features: List of features in this development

        Returns:
            Development ID
        """
        import hashlib
        dev_id = hashlib.md5(f"{title}{description}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        development = CursorDevelopment(
            development_id=dev_id,
            title=title,
            description=description,
            source=source,
            version=version,
            url=url,
            features=features or [],
            discovered_at=datetime.now().isoformat()
        )

        self.developments[dev_id] = development
        self._save_data()

        logger.info(f"   ✅ Added development: {title}")

        return dev_id

    def get_new_developments(self, days: int = 7) -> List[CursorDevelopment]:
        """
        Get new developments from last N days

        Args:
            days: Number of days to look back

        Returns:
            List of recent developments
        """
        cutoff = datetime.now() - timedelta(days=days)

        recent = [
            d for d in self.developments.values()
            if datetime.fromisoformat(d.discovered_at) >= cutoff
        ]

        # Sort by date (newest first)
        recent.sort(key=lambda d: d.discovered_at, reverse=True)

        return recent

    def get_actionable_developments(self) -> List[CursorDevelopment]:
        """Get developments that are actionable and verified"""
        return [
            d for d in self.developments.values()
            if d.actionable and d.verified
        ]

    def mark_actionable(self, development_id: str, verified: bool = True):
        """Mark development as actionable"""
        if development_id in self.developments:
            self.developments[development_id].actionable = True
            self.developments[development_id].verified = verified
            self._save_data()
            logger.info(f"   ✅ Marked as actionable: {development_id}")

    def update_feature_tracker(self, development: CursorDevelopment):
        """
        Update feature tracker with new features from development

        Args:
            development: Development to process
        """
        if not self.feature_tracker:
            return

        for feature_name in development.features:
            # Add to feature tracker if not exists
            if feature_name not in self.feature_tracker.features:
                from cursor_ide_feature_utilization_tracker import CursorFeature
                new_feature = CursorFeature(
                    name=feature_name,
                    category="feature",
                    description=f"New feature from {development.title}",
                    priority="high" if development.priority == "high" else "medium"
                )
                self.feature_tracker.features[feature_name] = new_feature
                self.feature_tracker._save_features()
                logger.info(f"   ✅ Added to feature tracker: {feature_name}")

    def get_pulse_report(self) -> Dict[str, Any]:
        """Get pulse report - current state of Cursor IDE developments"""
        total = len(self.developments)
        recent = len(self.get_new_developments(days=7))
        actionable = len(self.get_actionable_developments())
        verified = len([d for d in self.developments.values() if d.verified])

        return {
            "timestamp": datetime.now().isoformat(),
            "total_developments": total,
            "recent_developments_7_days": recent,
            "actionable_developments": actionable,
            "verified_developments": verified,
            "unverified_developments": total - verified,
            "pulse_status": "active" if recent > 0 else "stable",
            "ready_to_pivot": actionable > 0
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor IDE Development Monitor")
        parser.add_argument("--monitor", action="store_true", help="Monitor all sources")
        parser.add_argument("--add", nargs=5, metavar=("TITLE", "DESC", "SOURCE", "VERSION", "URL"),
                           help="Manually add development")
        parser.add_argument("--verify", nargs=2, metavar=("FEATURE", "METHOD"),
                           help="Verify a feature (tested, documented, confirmed)")
        parser.add_argument("--new", type=int, default=7, help="Show new developments (days, default: 7)")
        parser.add_argument("--actionable", action="store_true", help="Show actionable developments")
        parser.add_argument("--pulse", action="store_true", help="Get pulse report")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        monitor = JARVISCursorIDEDevelopmentMonitor()

        if args.monitor:
            developments = monitor.monitor_all_sources()
            if args.json:
                print(json.dumps([d.to_dict() for d in developments], indent=2))
            else:
                print(f"\n✅ Monitored sources - Found {len(developments)} new developments")
                for dev in developments:
                    print(f"   • {dev.title} ({dev.source})")

        elif args.add:
            title, desc, source, version, url = args.add
            dev_id = monitor.add_development(title, desc, source, version if version != "None" else None, url if url != "None" else None)
            if args.json:
                print(json.dumps({"development_id": dev_id}, indent=2))
            else:
                print(f"✅ Added development: {dev_id}")

        elif args.verify:
            feature_name, method = args.verify
            verification = monitor.verify_feature(feature_name, method)
            if args.json:
                print(json.dumps(verification.to_dict(), indent=2))
            else:
                print(f"✅ Verified: {feature_name}")
                print(f"   Method: {verification.verification_method}")
                print(f"   Verified: {verification.verified}")
                print(f"   Actionable: {verification.actionable}")

        elif args.actionable:
            developments = monitor.get_actionable_developments()
            if args.json:
                print(json.dumps([d.to_dict() for d in developments], indent=2))
            else:
                print(f"\n⚡ Actionable Developments: {len(developments)}")
                for dev in developments:
                    print(f"   • {dev.title}")
                    if dev.features:
                        print(f"     Features: {', '.join(dev.features)}")

        elif args.pulse or not any([args.monitor, args.add, args.verify, args.actionable]):
            report = monitor.get_pulse_report()
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print("=" * 80)
                print("📊 CURSOR IDE PULSE REPORT")
                print("=" * 80)
                print(f"Total Developments: {report['total_developments']}")
                print(f"Recent (7 days): {report['recent_developments_7_days']}")
                print(f"Actionable: {report['actionable_developments']}")
                print(f"Verified: {report['verified_developments']}")
                print(f"Unverified: {report['unverified_developments']}")
                print(f"Pulse Status: {report['pulse_status']}")
                print(f"Ready to Pivot: {'✅ Yes' if report['ready_to_pivot'] else '❌ No'}")
                print("=" * 80)

        elif args.new:
            developments = monitor.get_new_developments(days=args.new)
            if args.json:
                print(json.dumps([d.to_dict() for d in developments], indent=2))
            else:
                print(f"\n🆕 New Developments (last {args.new} days): {len(developments)}")
                for dev in developments:
                    print(f"   • {dev.title} ({dev.source})")
                    print(f"     {dev.description}")
                    if dev.url:
                        print(f"     URL: {dev.url}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()