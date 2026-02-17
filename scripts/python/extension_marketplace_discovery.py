#!/usr/bin/env python3
"""
Extension Marketplace Discovery & Monitoring System

Discovers, monitors, and tracks extensions across:
- VS Code Marketplace
- Docker Extension Marketplace
- Third-party marketplaces (Open VSX, etc.)

Tags: #EXTENSIONS #MARKETPLACE #MONITORING #DISCOVERY #AUTOMATION @JARVIS @LUMINA
"""

import sys
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

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

logger = get_logger("ExtensionMarketplaceDiscovery")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - install: pip install requests")


@dataclass
class Extension:
    """Extension information"""
    id: str
    name: str
    publisher: str
    version: str
    marketplace: str  # "vscode", "docker", "openvsx", "third-party"
    description: str
    last_updated: str
    install_count: Optional[int] = None
    rating: Optional[float] = None
    repository: Optional[str] = None
    homepage: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    changelog_url: Optional[str] = None
    api_url: Optional[str] = None


@dataclass
class ExtensionUpdate:
    """Extension update information"""
    extension_id: str
    old_version: str
    new_version: str
    update_date: str
    changelog: Optional[str] = None
    breaking_changes: bool = False
    new_features: List[str] = field(default_factory=list)
    bug_fixes: List[str] = field(default_factory=list)


class ExtensionMarketplaceDiscovery:
    """
    Extension Marketplace Discovery & Monitoring

    Discovers and monitors extensions across all marketplaces.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize marketplace discovery"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "extension_marketplaces"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Marketplace APIs
        self.marketplaces = {
            "vscode": {
                "name": "VS Code Marketplace",
                "api_base": "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
                "web_base": "https://marketplace.visualstudio.com/items",
                "enabled": True
            },
            "docker": {
                "name": "Docker Extension Marketplace",
                "api_base": "https://hub.docker.com/v2/search/repositories",
                "web_base": "https://hub.docker.com/extensions",
                "enabled": True
            },
            "openvsx": {
                "name": "Open VSX Registry",
                "api_base": "https://open-vsx.org/api/-/search",
                "web_base": "https://open-vsx.org",
                "enabled": True
            },
            "github": {
                "name": "GitHub Marketplace",
                "api_base": "https://api.github.com/search/repositories",
                "web_base": "https://github.com/marketplace",
                "enabled": True
            }
        }

        # Known extensions database
        self.known_extensions_file = self.data_dir / "known_extensions.json"
        self.known_extensions: Dict[str, Extension] = {}

        # Update tracking
        self.updates_file = self.data_dir / "extension_updates.json"
        self.updates: List[ExtensionUpdate] = []

        # Load existing data
        self._load_known_extensions()
        self._load_updates()

        logger.info("✅ Extension Marketplace Discovery initialized")
        logger.info(f"   Marketplaces: {len(self.marketplaces)}")
        logger.info(f"   Known extensions: {len(self.known_extensions)}")
        logger.info(f"   Tracked updates: {len(self.updates)}")

    def _load_known_extensions(self):
        """Load known extensions"""
        if self.known_extensions_file.exists():
            try:
                with open(self.known_extensions_file, 'r') as f:
                    data = json.load(f)
                    self.known_extensions = {
                        ext_id: Extension(**ext_data)
                        for ext_id, ext_data in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load known extensions: {e}")

    def _save_known_extensions(self):
        """Save known extensions"""
        try:
            with open(self.known_extensions_file, 'w') as f:
                json.dump({
                    ext_id: {
                        "id": ext.id,
                        "name": ext.name,
                        "publisher": ext.publisher,
                        "version": ext.version,
                        "marketplace": ext.marketplace,
                        "description": ext.description,
                        "last_updated": ext.last_updated,
                        "install_count": ext.install_count,
                        "rating": ext.rating,
                        "repository": ext.repository,
                        "homepage": ext.homepage,
                        "categories": ext.categories,
                        "tags": ext.tags,
                        "changelog_url": ext.changelog_url,
                        "api_url": ext.api_url
                    }
                    for ext_id, ext in self.known_extensions.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving extensions: {e}")

    def _load_updates(self):
        """Load extension updates"""
        if self.updates_file.exists():
            try:
                with open(self.updates_file, 'r') as f:
                    data = json.load(f)
                    self.updates = [ExtensionUpdate(**update) for update in data]
            except Exception as e:
                logger.debug(f"   Could not load updates: {e}")

    def _save_updates(self):
        """Save extension updates"""
        try:
            with open(self.updates_file, 'w') as f:
                json.dump([
                    {
                        "extension_id": update.extension_id,
                        "old_version": update.old_version,
                        "new_version": update.new_version,
                        "update_date": update.update_date,
                        "changelog": update.changelog,
                        "breaking_changes": update.breaking_changes,
                        "new_features": update.new_features,
                        "bug_fixes": update.bug_fixes
                    }
                    for update in self.updates
                ], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving updates: {e}")

    def discover_vscode_extensions(self, query: str = "", category: str = "", max_results: int = 100) -> List[Extension]:
        """Discover VS Code extensions"""
        if not REQUESTS_AVAILABLE:
            logger.error("   ❌ requests library not available")
            return []

        logger.info(f"   🔍 Discovering VS Code extensions: query='{query}', category='{category}'")

        extensions = []

        try:
            # VS Code Marketplace API
            api_url = self.marketplaces["vscode"]["api_base"]

            # Build query
            filters = []
            if query:
                filters.append({
                    "criteria": [{"filterType": 7, "value": query}]
                })
            if category:
                filters.append({
                    "criteria": [{"filterType": 12, "value": category}]
                })

            payload = {
                "filters": filters if filters else [{"criteria": []}],
                "flags": 0x1 | 0x2 | 0x4  # IncludeVersions, IncludeFiles, IncludeCategoryAndTags
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json;api-version=3.0-preview.1"
            }

            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for result in results[:max_results]:
                    extensions_list = result.get("extensions", [])
                    for ext_data in extensions_list:
                        ext = Extension(
                            id=f"{ext_data.get('publisher', {}).get('publisherName', 'unknown')}.{ext_data.get('extensionName', 'unknown')}",
                            name=ext_data.get("displayName", ""),
                            publisher=ext_data.get("publisher", {}).get("publisherName", ""),
                            version=ext_data.get("versions", [{}])[0].get("version", ""),
                            marketplace="vscode",
                            description=ext_data.get("shortDescription", ""),
                            last_updated=ext_data.get("publishedDate", ""),
                            install_count=ext_data.get("statistics", [{}])[0].get("install", 0) if ext_data.get("statistics") else None,
                            rating=ext_data.get("statistics", [{}])[0].get("averagerating", 0) if ext_data.get("statistics") else None,
                            repository=ext_data.get("repository", ""),
                            homepage=ext_data.get("homepage", ""),
                            categories=[cat.get("name", "") for cat in ext_data.get("categories", [])],
                            tags=ext_data.get("tags", []),
                            api_url=f"{self.marketplaces['vscode']['web_base']}?itemName={ext_data.get('publisher', {}).get('publisherName', '')}.{ext_data.get('extensionName', '')}"
                        )
                        extensions.append(ext)

                logger.info(f"   ✅ Found {len(extensions)} VS Code extensions")
            else:
                logger.warning(f"   ⚠️  VS Code API returned status {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ Error discovering VS Code extensions: {e}")

        return extensions

    def discover_docker_extensions(self, query: str = "", max_results: int = 100) -> List[Extension]:
        """Discover Docker extensions"""
        if not REQUESTS_AVAILABLE:
            logger.error("   ❌ requests library not available")
            return []

        logger.info(f"   🔍 Discovering Docker extensions: query='{query}'")

        extensions = []

        try:
            api_url = self.marketplaces["docker"]["api_base"]
            params = {
                "q": query or "extension",
                "type": "image",
                "page_size": min(max_results, 100)
            }

            response = requests.get(api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for result in results[:max_results]:
                    ext = Extension(
                        id=result.get("name", ""),
                        name=result.get("name", ""),
                        publisher=result.get("namespace", ""),
                        version=result.get("tag", "latest"),
                        marketplace="docker",
                        description=result.get("description", ""),
                        last_updated=result.get("last_updated", ""),
                        install_count=result.get("pull_count", 0),
                        rating=None,
                        repository=result.get("repo_url", ""),
                        homepage=result.get("homepage", ""),
                        tags=result.get("tags", []),
                        api_url=f"{self.marketplaces['docker']['web_base']}/{result.get('name', '')}"
                    )
                    extensions.append(ext)

                logger.info(f"   ✅ Found {len(extensions)} Docker extensions")
            else:
                logger.warning(f"   ⚠️  Docker API returned status {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ Error discovering Docker extensions: {e}")

        return extensions

    def discover_openvsx_extensions(self, query: str = "", max_results: int = 100) -> List[Extension]:
        """Discover Open VSX extensions"""
        if not REQUESTS_AVAILABLE:
            logger.error("   ❌ requests library not available")
            return []

        logger.info(f"   🔍 Discovering Open VSX extensions: query='{query}'")

        extensions = []

        try:
            api_url = self.marketplaces["openvsx"]["api_base"]
            params = {
                "query": query,
                "size": min(max_results, 100)
            }

            response = requests.get(api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get("extensions", [])

                for result in results[:max_results]:
                    ext = Extension(
                        id=result.get("namespace", "") + "." + result.get("name", ""),
                        name=result.get("displayName", result.get("name", "")),
                        publisher=result.get("namespace", ""),
                        version=result.get("version", ""),
                        marketplace="openvsx",
                        description=result.get("description", ""),
                        last_updated=result.get("timestamp", ""),
                        install_count=result.get("downloadCount", 0),
                        rating=result.get("averageRating", None),
                        repository=result.get("repository", ""),
                        homepage=result.get("homepage", ""),
                        categories=result.get("categories", []),
                        tags=result.get("tags", []),
                        api_url=f"{self.marketplaces['openvsx']['web_base']}/extension/{result.get('namespace', '')}/{result.get('name', '')}"
                    )
                    extensions.append(ext)

                logger.info(f"   ✅ Found {len(extensions)} Open VSX extensions")
            else:
                logger.warning(f"   ⚠️  Open VSX API returned status {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ Error discovering Open VSX extensions: {e}")

        return extensions

    def discover_all_marketplaces(self, query: str = "", max_results_per_marketplace: int = 50) -> Dict[str, List[Extension]]:
        """Discover extensions from all marketplaces"""
        logger.info("=" * 80)
        logger.info("🔍 DISCOVERING EXTENSIONS FROM ALL MARKETPLACES")
        logger.info("=" * 80)

        results = {}

        # VS Code
        if self.marketplaces["vscode"]["enabled"]:
            results["vscode"] = self.discover_vscode_extensions(query, max_results=max_results_per_marketplace)

        # Docker
        if self.marketplaces["docker"]["enabled"]:
            results["docker"] = self.discover_docker_extensions(query, max_results=max_results_per_marketplace)

        # Open VSX
        if self.marketplaces["openvsx"]["enabled"]:
            results["openvsx"] = self.discover_openvsx_extensions(query, max_results=max_results_per_marketplace)

        total = sum(len(exts) for exts in results.values())
        logger.info(f"   ✅ Total extensions discovered: {total}")

        return results

    def check_for_updates(self) -> List[ExtensionUpdate]:
        """Check for extension updates"""
        logger.info("=" * 80)
        logger.info("🔄 CHECKING FOR EXTENSION UPDATES")
        logger.info("=" * 80)

        updates = []

        for ext_id, ext in self.known_extensions.items():
            try:
                # Check current version from marketplace
                current_ext = None

                if ext.marketplace == "vscode":
                    # Query VS Code API for latest version
                    current_exts = self.discover_vscode_extensions(query=ext.name, max_results=1)
                    if current_exts:
                        current_ext = current_exts[0]

                elif ext.marketplace == "openvsx":
                    # Query Open VSX API
                    current_exts = self.discover_openvsx_extensions(query=ext.name, max_results=1)
                    if current_exts:
                        current_ext = current_exts[0]

                if current_ext and current_ext.version != ext.version:
                    # Update found!
                    update = ExtensionUpdate(
                        extension_id=ext_id,
                        old_version=ext.version,
                        new_version=current_ext.version,
                        update_date=datetime.now().isoformat(),
                        changelog=None,  # Would need to fetch from changelog_url
                        breaking_changes=False,  # Would need to analyze changelog
                        new_features=[],
                        bug_fixes=[]
                    )
                    updates.append(update)

                    # Update known extension
                    ext.version = current_ext.version
                    ext.last_updated = current_ext.last_updated

                    logger.info(f"   🔄 Update found: {ext.name} {ext.version} → {current_ext.version}")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.debug(f"   Error checking {ext_id}: {e}")

        # Save updates
        if updates:
            self.updates.extend(updates)
            self._save_updates()
            self._save_known_extensions()

        logger.info(f"   ✅ Found {len(updates)} updates")

        return updates

    def compare_extensions(self, installed_extensions: List[str]) -> Dict[str, Any]:
        """Compare installed extensions with available extensions"""
        logger.info("=" * 80)
        logger.info("📊 COMPARING INSTALLED VS AVAILABLE EXTENSIONS")
        logger.info("=" * 80)

        comparison = {
            "installed": [],
            "available_updates": [],
            "missing_recommended": [],
            "new_extensions": []
        }

        # Check installed extensions
        for ext_id in installed_extensions:
            if ext_id in self.known_extensions:
                ext = self.known_extensions[ext_id]
                comparison["installed"].append({
                    "id": ext_id,
                    "name": ext.name,
                    "version": ext.version,
                    "marketplace": ext.marketplace
                })
            else:
                comparison["installed"].append({
                    "id": ext_id,
                    "name": ext_id,
                    "version": "unknown",
                    "marketplace": "unknown"
                })

        # Check for updates
        for update in self.updates:
            if update.extension_id in installed_extensions:
                comparison["available_updates"].append({
                    "extension_id": update.extension_id,
                    "old_version": update.old_version,
                    "new_version": update.new_version,
                    "update_date": update.update_date
                })

        logger.info(f"   ✅ Comparison complete")
        logger.info(f"      Installed: {len(comparison['installed'])}")
        logger.info(f"      Updates available: {len(comparison['available_updates'])}")

        return comparison


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Extension Marketplace Discovery")
        parser.add_argument("--discover", action="store_true", help="Discover extensions from all marketplaces")
        parser.add_argument("--query", type=str, default="", help="Search query")
        parser.add_argument("--marketplace", type=str, choices=["vscode", "docker", "openvsx", "all"], default="all", help="Marketplace to search")
        parser.add_argument("--check-updates", action="store_true", help="Check for extension updates")
        parser.add_argument("--compare", type=str, nargs="+", help="Compare installed extensions (provide extension IDs)")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        discovery = ExtensionMarketplaceDiscovery()

        if args.discover:
            if args.marketplace == "all":
                results = discovery.discover_all_marketplaces(query=args.query)
            elif args.marketplace == "vscode":
                results = {"vscode": discovery.discover_vscode_extensions(query=args.query)}
            elif args.marketplace == "docker":
                results = {"docker": discovery.discover_docker_extensions(query=args.query)}
            elif args.marketplace == "openvsx":
                results = {"openvsx": discovery.discover_openvsx_extensions(query=args.query)}

            if args.json:
                print(json.dumps({
                    marketplace: [
                        {
                            "id": ext.id,
                            "name": ext.name,
                            "publisher": ext.publisher,
                            "version": ext.version,
                            "marketplace": ext.marketplace
                        }
                        for ext in extensions
                    ]
                    for marketplace, extensions in results.items()
                }, indent=2, default=str))

        elif args.check_updates:
            updates = discovery.check_for_updates()
            if args.json:
                print(json.dumps([
                    {
                        "extension_id": update.extension_id,
                        "old_version": update.old_version,
                        "new_version": update.new_version,
                        "update_date": update.update_date
                    }
                    for update in updates
                ], indent=2, default=str))
            else:
                print(f"✅ Found {len(updates)} updates")

        elif args.compare:
            comparison = discovery.compare_extensions(args.compare)
            if args.json:
                print(json.dumps(comparison, indent=2, default=str))
            else:
                print(f"Installed: {len(comparison['installed'])}")
                print(f"Updates: {len(comparison['available_updates'])}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()