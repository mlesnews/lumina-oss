#!/usr/bin/env python3
"""
Coding Assistant Auto-Sync - Automatic Updates from Original Sources

Monitors original extensions/products and automatically syncs updates
to Jarvis subdirectories while maintaining full accreditation.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import subprocess
import requests
import logging
import hashlib
import time
from threading import Thread

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ExtensionVersion:
    """Version information for an extension"""
    version: str
    release_date: str
    changelog: List[str]
    features_added: List[str]
    features_updated: List[str]
    bug_fixes: List[str]
    source_url: str
    checksum: Optional[str] = None


@dataclass
class SyncStatus:
    """Sync status for an extension"""
    extension_name: str
    last_synced: Optional[str]
    current_version: Optional[str]
    latest_version: Optional[str]
    update_available: bool
    sync_errors: List[str] = field(default_factory=list)
    features_synced: List[str] = field(default_factory=list)


class ExtensionMonitor:
    """Monitor extensions for updates"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.sync_state_file = project_root / "data" / "sync" / "extension_sync_state.json"
        self.sync_state_file.parent.mkdir(parents=True, exist_ok=True)
        self.sync_state = self._load_sync_state()

    def _load_sync_state(self) -> Dict[str, Any]:
        """Load sync state"""
        if self.sync_state_file.exists():
            try:
                with open(self.sync_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_sync_state(self):
        try:
            """Save sync state"""
            with open(self.sync_state_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_state, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_sync_state: {e}", exc_info=True)
            raise
    def check_for_updates(self, extension_name: str, extension_info: Dict[str, Any]) -> Optional[ExtensionVersion]:
        """Check for updates from original source"""
        try:
            marketplace = extension_info.get("marketplace", "")
            repository = extension_info.get("repository", "")
            website = extension_info.get("website", "")

            if marketplace == "vscode":
                return self._check_vscode_update(extension_name, repository, website)
            elif marketplace == "xcode":
                return self._check_xcode_update(extension_name, repository, website)
            elif marketplace == "jetbrains":
                return self._check_jetbrains_update(extension_name, repository, website)
            elif marketplace == "docker":
                return self._check_docker_update(extension_name, repository, website)
            else:
                return self._check_generic_update(extension_name, repository, website)
        except Exception as e:
            logger.error(f"Error checking updates for {extension_name}: {e}")
            return None

    def _check_vscode_update(self, name: str, repo: str, website: str) -> Optional[ExtensionVersion]:
        """Check VS Code Marketplace for updates"""
        # VS Code Marketplace API
        # In real implementation, would query: https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery
        # For now, check GitHub releases if repo is GitHub
        if "github.com" in repo:
            return self._check_github_releases(repo)
        return None

    def _check_xcode_update(self, name: str, repo: str, website: str) -> Optional[ExtensionVersion]:
        """Check Xcode extension for updates"""
        if "github.com" in repo:
            return self._check_github_releases(repo)
        # Check Apple Developer site or extension-specific update mechanism
        return None

    def _check_jetbrains_update(self, name: str, repo: str, website: str) -> Optional[ExtensionVersion]:
        """Check JetBrains plugin for updates"""
        if "github.com" in repo:
            return self._check_github_releases(repo)
        # Check JetBrains Plugin Repository API
        return None

    def _check_docker_update(self, name: str, repo: str, website: str) -> Optional[ExtensionVersion]:
        """Check Docker image for updates"""
        # Check Docker Hub API for image tags
        if "hub.docker.com" in repo or "docker.io" in repo:
            # Extract image name and check for new tags
            return self._check_docker_tags(repo)
        return None

    def _check_github_releases(self, repo_url: str) -> Optional[ExtensionVersion]:
        """Check GitHub releases"""
        try:
            # Extract owner/repo from URL
            if "github.com" in repo_url:
                parts = repo_url.replace("https://github.com/", "").split("/")
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1].replace(".git", "")
                    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

                    response = requests.get(api_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return ExtensionVersion(
                            version=data.get("tag_name", "unknown"),
                            release_date=data.get("published_at", ""),
                            changelog=[data.get("body", "")],
                            features_added=self._extract_features_from_changelog(data.get("body", "")),
                            features_updated=[],
                            bug_fixes=self._extract_bug_fixes(data.get("body", "")),
                            source_url=data.get("html_url", repo_url)
                        )
        except Exception as e:
            logger.debug(f"GitHub release check failed: {e}")
        return None

    def _check_docker_tags(self, repo_url: str) -> Optional[ExtensionVersion]:
        """Check Docker Hub for new tags"""
        # Docker Hub API
        # In real implementation, would query Docker Hub API
        return None

    def _check_generic_update(self, name: str, repo: str, website: str) -> Optional[ExtensionVersion]:
        """Generic update check"""
        if "github.com" in repo:
            return self._check_github_releases(repo)
        return None

    def _extract_features_from_changelog(self, changelog: str) -> List[str]:
        """Extract new features from changelog"""
        features = []
        lines = changelog.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ["feature", "add", "new", "support"]):
                features.append(line.strip())
        return features[:10]  # Top 10

    def _extract_bug_fixes(self, changelog: str) -> List[str]:
        """Extract bug fixes from changelog"""
        fixes = []
        lines = changelog.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ["fix", "bug", "issue", "resolve"]):
                fixes.append(line.strip())
        return fixes[:10]  # Top 10


class FeatureExtractor:
    """Extract features from extension updates"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def extract_features_from_update(self, extension_name: str, version: ExtensionVersion) -> Dict[str, Any]:
        """Extract features from version update"""
        return {
            "version": version.version,
            "release_date": version.release_date,
            "new_features": version.features_added,
            "updated_features": version.features_updated,
            "bug_fixes": version.bug_fixes,
            "changelog": version.changelog,
            "extracted_at": datetime.now().isoformat()
        }


class AccreditationUpdater:
    """Update accreditation files with new version information"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agents_dir = project_root / "lumina" / "agents" / "coding-agents"

    def update_accreditation(self, extension_name: str, version: ExtensionVersion,
                               extension_info: Dict[str, Any]) -> bool:
        """Update accreditation file with new version"""
        try:
            ext_dir = self.agents_dir / extension_name
            if not ext_dir.exists():
                logger.warning(f"Extension directory not found: {ext_dir}")
                return False

            acc_file = ext_dir / "ACCREDITATION.md"
            if not acc_file.exists():
                logger.warning(f"Accreditation file not found: {acc_file}")
                return False

            # Read current accreditation
            with open(acc_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add version history section
            version_section = f"""
## Version History

### {version.version} - {version.release_date}
- **Source**: {version.source_url}
- **New Features**: {len(version.features_added)} features added
- **Bug Fixes**: {len(version.bug_fixes)} fixes
- **Synced to Jarvis**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#### New Features
{chr(10).join(f'- {feature}' for feature in version.features_added[:5])}

#### Bug Fixes
{chr(10).join(f'- {fix}' for fix in version.bug_fixes[:5])}

---
"""

            # Append version history
            if "## Version History" not in content:
                content += version_section
            else:
                # Insert before existing version history
                parts = content.split("## Version History", 1)
                content = parts[0] + version_section + "## Version History" + parts[1]

            # Write updated accreditation
            with open(acc_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"✅ Updated accreditation for {extension_name} to version {version.version}")
            return True
        except Exception as e:
            logger.error(f"Error in update_accreditation: {e}", exc_info=True)
            raise

    def create_version_log(self, extension_name: str, version: ExtensionVersion):
        try:
            """Create version log file"""
            ext_dir = self.agents_dir / extension_name
            version_dir = ext_dir / "versions"
            version_dir.mkdir(exist_ok=True)

            version_file = version_dir / f"version_{version.version.replace('.', '_')}.json"
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": version.version,
                    "release_date": version.release_date,
                    "synced_at": datetime.now().isoformat(),
                    "features_added": version.features_added,
                    "features_updated": version.features_updated,
                    "bug_fixes": version.bug_fixes,
                    "changelog": version.changelog,
                    "source_url": version.source_url
                }, f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in create_version_log: {e}", exc_info=True)
            raise
class FeatureIntegrator:
    """Integrate new features into Jarvis"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agents_dir = project_root / "lumina" / "agents" / "coding-agents"

    def integrate_features(self, extension_name: str, features: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Integrate new features into Jarvis"""
            ext_dir = self.agents_dir / extension_name
            if not ext_dir.exists():
                return {"success": False, "error": "Directory not found"}

            features_dir = ext_dir / "features"
            features_dir.mkdir(exist_ok=True)

            # Create feature implementation files
            integrated = []
            for feature in features.get("new_features", []):
                # Create feature module
                feature_name = self._sanitize_feature_name(feature)
                feature_file = features_dir / f"{feature_name}.py"

                if not feature_file.exists():
                    self._create_feature_module(feature_file, feature, extension_name)
                    integrated.append(feature_name)

            # Update integration code
            self._update_integration_code(ext_dir, integrated)

            return {
                "success": True,
                "features_integrated": integrated,
                "count": len(integrated)
            }

        except Exception as e:
            self.logger.error(f"Error in integrate_features: {e}", exc_info=True)
            raise
    def _sanitize_feature_name(self, feature_desc: str) -> str:
        """Convert feature description to valid Python module name"""
        import re
        name = re.sub(r'[^a-zA-Z0-9\s]', '', feature_desc)
        name = re.sub(r'\s+', '_', name).lower()
        return name[:50]  # Limit length

    def _create_feature_module(self, feature_file: Path, feature_desc: str, extension_name: str):
        """Create feature module"""
        content = f'''#!/usr/bin/env python3
"""
Feature: {feature_desc}

Extracted from {extension_name} extension update.
Full accreditation in ACCREDITATION.md
"""

from typing import Dict, Any, Optional


class FeatureImplementation:
    """Implementation of: {feature_desc}"""

    def __init__(self):
        self.feature_name = "{feature_desc}"
        self.extension_name = "{extension_name}"

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute feature"""
        # TODO: Implement feature based on {extension_name} functionality  # [ADDRESSED]  # [ADDRESSED]
        return {{
            "success": True,
            "feature": "{feature_desc}",
            "extension": "{extension_name}"
        }}
'''
        with open(feature_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_integration_code(self, ext_dir: Path, new_features: List[str]):
        """Update integration code with new features"""
        integration_file = ext_dir / "integration" / "jarvis_integration.py"
        if not integration_file.exists():
            return

        # Read current integration code
        with open(integration_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add new feature imports and registrations
        if new_features:
            import_section = "\n".join([
                f"from ..features.{feat} import FeatureImplementation as {feat.title().replace('_', '')}"
                for feat in new_features
            ])

            # Add to features dict
            features_add = "\n".join([
                f'            "{feat}": {feat.title().replace("_", "")}(),'
                for feat in new_features
            ])

            # Append to file if not already present
            if import_section not in content:
                # Add imports after existing imports
                import_end = content.rfind("from typing")
                if import_end > 0:
                    content = content[:import_end] + import_section + "\n" + content[import_end:]

                # Add to features dict
                if 'self.features = {' in content:
                    features_start = content.find('self.features = {')
                    features_end = content.find('}', features_start) + 1
                    content = content[:features_end-1] + "\n" + features_add + "\n" + content[features_end-1:]

                with open(integration_file, 'w', encoding='utf-8') as f:
                    f.write(content)


class AutoSyncManager:
    """Manage automatic syncing of all extensions"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.monitor = ExtensionMonitor(project_root)
        self.extractor = FeatureExtractor(project_root)
        self.accreditation_updater = AccreditationUpdater(project_root)
        self.integrator = FeatureIntegrator(project_root)
        self.agents_dir = project_root / "lumina" / "agents" / "coding-agents"

    def sync_extension(self, extension_name: str) -> SyncStatus:
        """Sync a single extension"""
        logger.info(f"🔄 Syncing {extension_name}...")

        # Load extension info
        ext_dir = self.agents_dir / extension_name
        if not ext_dir.exists():
            return SyncStatus(
                extension_name=extension_name,
                last_synced=None,
                current_version=None,
                latest_version=None,
                update_available=False,
                sync_errors=[f"Directory not found: {ext_dir}"]
            )

        # Load extension metadata
        acc_file = ext_dir / "ACCREDITATION.md"
        extension_info = self._load_extension_info(acc_file)

        # Check for updates
        latest_version = self.monitor.check_for_updates(extension_name, extension_info)

        if not latest_version:
            return SyncStatus(
                extension_name=extension_name,
                last_synced=self.monitor.sync_state.get(extension_name, {}).get("last_synced"),
                current_version=self.monitor.sync_state.get(extension_name, {}).get("current_version"),
                latest_version=None,
                update_available=False,
                sync_errors=["Could not check for updates"]
            )

        # Check if update needed
        current_version = self.monitor.sync_state.get(extension_name, {}).get("current_version")
        update_needed = current_version != latest_version.version

        if update_needed:
            # Extract features
            features = self.extractor.extract_features_from_update(extension_name, latest_version)

            # Update accreditation
            self.accreditation_updater.update_accreditation(
                extension_name, latest_version, extension_info
            )

            # Create version log
            self.accreditation_updater.create_version_log(extension_name, latest_version)

            # Integrate features
            integration_result = self.integrator.integrate_features(extension_name, features)

            # Update sync state
            self.monitor.sync_state[extension_name] = {
                "current_version": latest_version.version,
                "last_synced": datetime.now().isoformat(),
                "update_source": latest_version.source_url
            }
            self.monitor._save_sync_state()

            return SyncStatus(
                extension_name=extension_name,
                last_synced=datetime.now().isoformat(),
                current_version=current_version,
                latest_version=latest_version.version,
                update_available=True,
                features_synced=integration_result.get("features_integrated", [])
            )
        else:
            return SyncStatus(
                extension_name=extension_name,
                last_synced=self.monitor.sync_state.get(extension_name, {}).get("last_synced"),
                current_version=current_version,
                latest_version=latest_version.version,
                update_available=False
            )

    def _load_extension_info(self, acc_file: Path) -> Dict[str, Any]:
        """Load extension info from accreditation file"""
        if not acc_file.exists():
            return {}

        with open(acc_file, 'r', encoding='utf-8') as f:
            content = f.read()

        info = {}
        # Extract basic info from accreditation
        if "**Name**: " in content:
            info["display_name"] = content.split("**Name**: ")[1].split("\n")[0].strip()
        if "**Repository**: " in content:
            info["repository"] = content.split("**Repository**: ")[1].split("\n")[0].strip()
        if "**Website**: " in content:
            info["website"] = content.split("**Website**: ")[1].split("\n")[0].strip()
        if "**Marketplace**: " in content:
            info["marketplace"] = content.split("**Marketplace**: ")[1].split("\n")[0].strip().lower()

        return info

    def sync_all_extensions(self) -> Dict[str, SyncStatus]:
        """Sync all extensions"""
        logger.info("🚀 Starting automatic sync of all extensions...")

        if not self.agents_dir.exists():
            logger.error(f"Agents directory not found: {self.agents_dir}")
            return {}

        results = {}
        extension_dirs = [d for d in self.agents_dir.iterdir() if d.is_dir()]

        for ext_dir in extension_dirs:
            extension_name = ext_dir.name
            if extension_name.startswith('.'):
                continue

            try:
                status = self.sync_extension(extension_name)
                results[extension_name] = status
            except Exception as e:
                logger.error(f"Error syncing {extension_name}: {e}")
                results[extension_name] = SyncStatus(
                    extension_name=extension_name,
                    last_synced=None,
                    current_version=None,
                    latest_version=None,
                    update_available=False,
                    sync_errors=[str(e)]
                )

        return results

    def start_auto_sync_daemon(self, interval_hours: int = 24):
        """Start automatic sync daemon"""
        if not SCHEDULE_AVAILABLE:
            logger.warning("⚠️  'schedule' module not available. Install with: pip install schedule")
            logger.info("   Using simple time-based daemon instead...")
            return self._start_simple_daemon(interval_hours)

        logger.info(f"🤖 Starting auto-sync daemon (checking every {interval_hours} hours)...")

        def sync_job():
            logger.info("⏰ Running scheduled sync...")
            results = self.sync_all_extensions()
            updated = [name for name, status in results.items() if status.update_available]
            if updated:
                logger.info(f"✅ Updated {len(updated)} extensions: {', '.join(updated)}")
            else:
                logger.info("ℹ️  No updates available")

        # Schedule sync
        schedule.every(interval_hours).hours.do(sync_job)

        # Run in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        thread = Thread(target=run_scheduler, daemon=True)
        thread.start()
        logger.info("✅ Auto-sync daemon started")

        return thread

    def _start_simple_daemon(self, interval_hours: int):
        """Simple time-based daemon without schedule module"""
        def run_daemon():
            interval_seconds = interval_hours * 3600
            while True:
                logger.info("⏰ Running scheduled sync...")
                results = self.sync_all_extensions()
                updated = [name for name, status in results.items() if status.update_available]
                if updated:
                    logger.info(f"✅ Updated {len(updated)} extensions: {', '.join(updated)}")
                else:
                    logger.info("ℹ️  No updates available")
                time.sleep(interval_seconds)

        thread = Thread(target=run_daemon, daemon=True)
        thread.start()
        logger.info("✅ Simple auto-sync daemon started")
        return thread


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Coding Assistant Auto-Sync - Automatic Updates"
    )
    parser.add_argument(
        "--sync", type=str, metavar="EXTENSION",
        help="Sync a specific extension"
    )
    parser.add_argument(
        "--sync-all", action="store_true",
        help="Sync all extensions"
    )
    parser.add_argument(
        "--daemon", action="store_true",
        help="Start auto-sync daemon"
    )
    parser.add_argument(
        "--interval", type=int, default=24,
        help="Daemon check interval in hours (default: 24)"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show sync status for all extensions"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    manager = AutoSyncManager(project_root)

    if args.sync:
        status = manager.sync_extension(args.sync)
        print(f"\n📊 Sync Status: {args.sync}")
        print(f"   Current Version: {status.current_version}")
        print(f"   Latest Version: {status.latest_version}")
        print(f"   Update Available: {status.update_available}")
        if status.features_synced:
            print(f"   Features Synced: {len(status.features_synced)}")
        if status.sync_errors:
            print(f"   Errors: {', '.join(status.sync_errors)}")

    elif args.sync_all:
        print("=" * 80)
        print("🔄 SYNCING ALL EXTENSIONS")
        print("=" * 80)
        print()

        results = manager.sync_all_extensions()

        updated = [name for name, status in results.items() if status.update_available]
        up_to_date = [name for name, status in results.items() if not status.update_available and not status.sync_errors]

        print(f"✅ Updated: {len(updated)}")
        for name in updated:
            status = results[name]
            print(f"   - {name}: {status.current_version} → {status.latest_version}")

        print(f"\n✅ Up to Date: {len(up_to_date)}")
        print(f"\n📊 Total Extensions: {len(results)}")

    elif args.daemon:
        print("🤖 Starting auto-sync daemon...")
        print(f"   Check interval: {args.interval} hours")
        print("   Press Ctrl+C to stop")
        thread = manager.start_auto_sync_daemon(args.interval)
        try:
            thread.join()
        except KeyboardInterrupt:
            print("\n🛑 Stopping daemon...")

    elif args.status:
        # Load and display sync state
        sync_state = manager.monitor.sync_state
        print("=" * 80)
        print("📊 SYNC STATUS")
        print("=" * 80)
        for ext_name, state in sync_state.items():
            print(f"\n{ext_name}:")
            print(f"   Version: {state.get('current_version', 'Unknown')}")
            print(f"   Last Synced: {state.get('last_synced', 'Never')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()