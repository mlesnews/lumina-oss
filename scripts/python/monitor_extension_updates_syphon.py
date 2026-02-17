"""
Extension Update Monitor with @SYPHON Integration

Monitors VS Code extension updates (anthropic, spark-monitor, cfs, lumina)
and uses @SYPHON to extract actionable items before deactivation/removal.

"I drink your milkshake!" - Extract all valuable updates before removal.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
sys.path.insert(0, str(Path(__file__).parent))

# Try multiple import paths for syphon_system
try:
    from syphon_system import SYPHONSystem, SyphonData, DataSourceType
except ImportError:
    try:
        import sys
        from pathlib import Path
        # Add scripts/python to path
        scripts_python = Path(__file__).parent.parent.parent.parent / "scripts" / "python"
        if scripts_python.exists():
            sys.path.insert(0, str(scripts_python))
        from syphon_system import SYPHONSystem, SyphonData, DataSourceType
    except ImportError:
        # Create minimal stubs if syphon_system not available

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

        class DataSourceType:
            CODE = "code"
            OTHER = "other"

        class SyphonData:
            def __init__(self, **kwargs):
                self.data_id = kwargs.get('data_id', '')
                self.source_type = kwargs.get('source_type')
                self.source_id = kwargs.get('source_id', '')
                self.content = kwargs.get('content', '')
                self.metadata = kwargs.get('metadata', {})
                self.extracted_at = kwargs.get('extracted_at')

            def to_dict(self):
                return {
                    "data_id": self.data_id,
                    "source_type": self.source_type.value if hasattr(self.source_type, 'value') else str(self.source_type),
                    "source_id": self.source_id,
                    "content": self.content,
                    "metadata": self.metadata,
                    "extracted_at": self.extracted_at.isoformat() if hasattr(self.extracted_at, 'isoformat') else str(self.extracted_at)
                }

        class SYPHONSystem:
            def __init__(self, project_root):
                self.project_root = project_root
                self.extracted_data = []

            def _save_extracted_data(self):
                pass

try:
    from lumina_logger import get_logger
    logger = get_logger("ExtensionMonitor", agent_id="monitor", server_id="local")
except ImportError:
    import logging
    logger = logging.getLogger("ExtensionMonitor")


class UpdateType(Enum):
    """Types of extension updates"""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DEPRECATION = "deprecation"
    BREAKING = "breaking"
    DOCUMENTATION = "documentation"
    OTHER = "other"


@dataclass
class ExtensionUpdate:
    """Represents an extension update"""
    extension_id: str
    extension_name: str
    current_version: str
    latest_version: str
    update_type: UpdateType
    changelog: str
    release_notes: str
    actionable_items: List[str] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)
    syphoned: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "extension_id": self.extension_id,
            "extension_name": self.extension_name,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "update_type": self.update_type.value,
            "changelog": self.changelog,
            "release_notes": self.release_notes,
            "actionable_items": self.actionable_items,
            "extracted_at": self.extracted_at.isoformat(),
            "syphoned": self.syphoned
        }


@dataclass
class ExtensionMonitorReport:
    """Report of extension monitoring"""
    report_id: str
    monitored_extensions: List[str]
    updates_found: List[ExtensionUpdate]
    syphoned_items: List[SyphonData]
    actionable_count: int
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.report_id,
            "monitored_extensions": self.monitored_extensions,
            "updates_found": [u.to_dict() for u in self.updates_found],
            "syphoned_items": [s.to_dict() for s in self.syphoned_items] if SyphonData else [],
            "actionable_count": self.actionable_count,
            "created_at": self.created_at.isoformat()
        }


class ExtensionUpdateMonitor:
    """Monitor extension updates and syphon actionable items"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.monitored_extensions = {
            "anthropic": "Anthropic Extension",
            "spark-monitor": "Spark Monitor",
            "cfs": "<COMPANY_ABBR> Publisher",
            "lumina": "LUMINA Extension"
        }
        self.data_dir = self.workspace_root / "data" / "extension_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.syphon_system = SYPHONSystem(self.workspace_root) if SYPHONSystem else None

    def check_extension_updates(self) -> List[ExtensionUpdate]:
        """Check for extension updates"""
        print("\n" + "=" * 60)
        print("CHECKING EXTENSION UPDATES")
        print("=" * 60)

        updates = []

        # Try multiple ways to find VS Code CLI
        code_path = None

        # First, try common VS Code installation paths on Windows
        if sys.platform == "win32":
            common_paths = [
                r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
                r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
                os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"),
                r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd".format(os.getenv('USERNAME', ''))
            ]
            for path in common_paths:
                if os.path.exists(path):
                    code_path = path
                    break

        # Try to find via PATH
        if not code_path:
            code_commands = ["code", "code.cmd"]
            for cmd in code_commands:
                try:
                    # Test if command works
                    result = subprocess.run(
                        [cmd, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        code_path = cmd
                        break
                except:
                    continue

        if not code_path:
            print("[!] VS Code CLI not found in standard locations")
            print("[TIP] Install VS Code CLI: In VS Code, press Ctrl+Shift+P, type 'Shell Command: Install code command in PATH'")
            # Try anyway - might work if in PATH
            code_path = "code"

        try:
            # Get installed extensions with versions
            result = subprocess.run(
                [code_path, "--list-extensions", "--show-versions"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"[!] Could not list extensions: {result.stderr}")
                # Try without --show-versions
                result = subprocess.run(
                    [code_path, "--list-extensions"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    return updates

            installed_extensions = {}
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                if '@' in line:
                    parts = line.split('@')
                    if len(parts) >= 2:
                        ext_id = parts[0].strip()
                        version = parts[1].strip()
                        installed_extensions[ext_id] = version
                else:
                    # Extension without version
                    installed_extensions[line] = "unknown"

            # Check each monitored extension
            for ext_id, ext_name in self.monitored_extensions.items():
                # Try exact match and partial matches
                found = False
                installed_version = None

                # Exact match
                if ext_id in installed_extensions:
                    found = True
                    installed_version = installed_extensions[ext_id]
                else:
                    # Partial match (e.g., "anthropic" might be "publisher.anthropic")
                    for installed_id in installed_extensions.keys():
                        if ext_id.lower() in installed_id.lower() or installed_id.lower() in ext_id.lower():
                            found = True
                            installed_version = installed_extensions[installed_id]
                            ext_id = installed_id  # Use the actual installed ID
                            break

                if found:
                    print(f"\n  Checking {ext_name} ({ext_id})...")
                    print(f"    Current version: {installed_version}")

                    # Check for updates
                    update = self._check_extension_update(ext_id, ext_name, installed_version)
                    if update:
                        updates.append(update)
                        print(f"    [UPDATE FOUND] {update.latest_version}")
                    else:
                        print(f"    [OK] Up to date (or update check unavailable)")
                else:
                    print(f"\n  {ext_name} ({ext_id}): Not installed")

        except FileNotFoundError:
            print("[!] VS Code CLI not found - extensions may not be checkable")
            print("[TIP] Install VS Code CLI: In VS Code, press Ctrl+Shift+P, type 'Shell Command: Install code command in PATH'")
        except subprocess.TimeoutExpired:
            print("[!] Timeout checking extensions")
        except Exception as e:
            print(f"[!] Error checking extensions: {e}")
            if logger:
                logger.error(f"Error checking extensions: {e}", exc_info=True)

        return updates

    def _check_extension_update(
        self,
        ext_id: str,
        ext_name: str,
        current_version: str
    ) -> Optional[ExtensionUpdate]:
        """Check for update for a specific extension"""
        # Try to query VS Code Marketplace API for extension info
        import urllib.request
        import urllib.error

        try:
            # VS Code Marketplace API endpoint
            marketplace_url = f"https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"

            # Create request payload
            payload = {
                "filters": [{
                    "criteria": [{
                        "filterType": 7,
                        "value": ext_id
                    }]
                }],
                "flags": 0x200  # Include versions, files, etc.
            }

            # Make API request
            req = urllib.request.Request(
                marketplace_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'Accept': 'application/json;api-version=3.0-preview.1'}
            )

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))

                    if data.get('results') and len(data['results']) > 0:
                        extension = data['results'][0].get('extensions', [{}])[0]
                        versions = extension.get('versions', [])

                        if versions:
                            latest_version = versions[0].get('version', 'unknown')

                            # Compare versions
                            if latest_version != current_version and latest_version != "unknown":
                                # Get release notes
                                release_notes = versions[0].get('properties', [])
                                changelog = ""
                                release_notes_text = ""

                                for prop in release_notes:
                                    if prop.get('key') == 'Microsoft.VisualStudio.Services.ReleaseNotes':
                                        release_notes_text = prop.get('value', '')
                                    elif prop.get('key') == 'Microsoft.VisualStudio.Services.Changelog':
                                        changelog = prop.get('value', '')

                                # Determine update type
                                update_type = UpdateType.OTHER
                                content_lower = (changelog + release_notes_text).lower()
                                if 'security' in content_lower or 'vulnerability' in content_lower:
                                    update_type = UpdateType.SECURITY
                                elif 'breaking' in content_lower or 'deprecated' in content_lower:
                                    update_type = UpdateType.BREAKING
                                elif 'performance' in content_lower or 'optimization' in content_lower:
                                    update_type = UpdateType.PERFORMANCE
                                elif 'fix' in content_lower or 'bug' in content_lower:
                                    update_type = UpdateType.BUGFIX
                                elif 'feature' in content_lower or 'new' in content_lower:
                                    update_type = UpdateType.FEATURE

                                return ExtensionUpdate(
                                    extension_id=ext_id,
                                    extension_name=ext_name,
                                    current_version=current_version,
                                    latest_version=latest_version,
                                    update_type=update_type,
                                    changelog=changelog,
                                    release_notes=release_notes_text
                                )
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
                if logger:
                    logger.debug(f"Could not fetch marketplace data for {ext_id}: {e}")
                # Continue to return None - no update found or API unavailable
                pass

        except Exception as e:
            if logger:
                logger.debug(f"Error checking update for {ext_id}: {e}")

        return None  # No update found

    def syphon_update_content(self, update: ExtensionUpdate) -> List[SyphonData]:
        """Syphon actionable items from extension update"""
        if not self.syphon_system or not SyphonData:
            print(f"[!] Syphon system not available")
            return []

        print(f"\n  Syphoning {update.extension_name} update...")

        syphoned_items = []

        # Extract actionable items from changelog and release notes
        content_to_analyze = f"""
Extension: {update.extension_name}
Version: {update.current_version} -> {update.latest_version}
Type: {update.update_type.value}

Changelog:
{update.changelog}

Release Notes:
{update.release_notes}
"""

        # Use Syphon to extract actionable items
        actionable_items = self._extract_actionable_items(content_to_analyze)
        update.actionable_items = actionable_items

        # Create SyphonData entry
        syphon_data = SyphonData(
            data_id=f"extension_update_{update.extension_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.CODE if DataSourceType else None,
            source_id=f"vscode_extension_{update.extension_id}",
            content=content_to_analyze,
            metadata={
                "extension_id": update.extension_id,
                "extension_name": update.extension_name,
                "current_version": update.current_version,
                "latest_version": update.latest_version,
                "update_type": update.update_type.value,
                "actionable_items": actionable_items,
                "actionable_count": len(actionable_items)
            }
        )

        syphoned_items.append(syphon_data)
        update.syphoned = True

        print(f"    [OK] Extracted {len(actionable_items)} actionable items")

        return syphoned_items

    def _extract_actionable_items(self, content: str) -> List[str]:
        """Extract actionable items from update content"""
        actionable_items = []

        # Look for patterns that indicate actionable items:
        # - "New feature:", "Added:", "Introducing"
        # - "Fix:", "Fixed:", "Resolved"
        # - "Breaking change:", "Deprecated:"
        # - "Security:", "Performance:"
        # - "Action required:", "Migration:"

        lines = content.split('\n')
        current_section = None

        # Keywords that indicate actionable content
        action_keywords = [
            'action required', 'migration', 'upgrade', 'breaking',
            'security', 'fix', 'new feature', 'deprecated', 'removed',
            'change', 'update', 'important', 'warning', 'note'
        ]

        for line in lines:
            line_lower = line.lower().strip()
            line_original = line.strip()

            if not line_original:
                continue

            # Detect sections
            if any(keyword in line_lower for keyword in ['new feature', 'added', 'introducing']):
                current_section = 'feature'
            elif any(keyword in line_lower for keyword in ['fix', 'fixed', 'resolved', 'bug']):
                current_section = 'bugfix'
            elif any(keyword in line_lower for keyword in ['breaking', 'deprecated', 'removed']):
                current_section = 'breaking'
            elif any(keyword in line_lower for keyword in ['security', 'vulnerability', 'cve']):
                current_section = 'security'
            elif any(keyword in line_lower for keyword in ['performance', 'optimization', 'speed']):
                current_section = 'performance'
            elif any(keyword in line_lower for keyword in ['action required', 'migration', 'upgrade']):
                current_section = 'action_required'

            # Extract actionable items from bullet points
            if line_original.startswith(('-', '*', '•', '→', '▶')):
                item = line_original.lstrip('-*•→▶').strip()
                if item and len(item) > 10:  # Filter out very short items
                    actionable_items.append(item)
            # Extract from numbered lists
            elif line_original and line_original[0].isdigit() and ('.' in line_original[:3] or ')' in line_original[:3]):
                item = line_original.split('.', 1)[-1].split(')', 1)[-1].strip()
                if item and len(item) > 10:
                    actionable_items.append(item)
            # Extract lines with action keywords
            elif any(keyword in line_lower for keyword in action_keywords):
                if len(line_original) > 15:  # Avoid very short lines
                    actionable_items.append(line_original)
            # Extract from markdown headers (##, ###)
            elif line_original.startswith('#'):
                item = line_original.lstrip('#').strip()
                if item and len(item) > 5:
                    actionable_items.append(f"Section: {item}")

        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in actionable_items:
            item_lower = item.lower()
            if item_lower not in seen and len(item) > 10:
                seen.add(item_lower)
                unique_items.append(item)

        return unique_items[:20]  # Limit to top 20 items

    def monitor_and_syphon(self) -> ExtensionMonitorReport:
        """Monitor extensions and syphon all updates"""
        print("\n" + "=" * 60)
        print("EXTENSION UPDATE MONITOR & SYPHON")
        print("=" * 60)

        # Check for updates
        updates = self.check_extension_updates()

        # Syphon each update
        all_syphoned = []
        total_actionable = 0

        for update in updates:
            syphoned = self.syphon_update_content(update)
            all_syphoned.extend(syphoned)
            total_actionable += len(update.actionable_items)

        # Create report
        report = ExtensionMonitorReport(
            report_id=f"extension_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            monitored_extensions=list(self.monitored_extensions.keys()),
            updates_found=updates,
            syphoned_items=all_syphoned,
            actionable_count=total_actionable
        )

        # Save report
        self._save_report(report)

        # Integrate with Syphon system
        if self.syphon_system:
            for item in all_syphoned:
                self.syphon_system.extracted_data.append(item)
            self.syphon_system._save_extracted_data()

        print("\n" + "=" * 60)
        print("MONITORING COMPLETE")
        print("=" * 60)
        print(f"Extensions monitored: {len(self.monitored_extensions)}")
        print(f"Updates found: {len(updates)}")
        print(f"Actionable items extracted: {total_actionable}")
        print(f"Items syphoned: {len(all_syphoned)}")
        print("=" * 60)

        return report

    def _save_report(self, report: ExtensionMonitorReport):
        try:
            """Save monitoring report"""
            report_file = self.data_dir / f"{report.report_id}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
            print(f"\n[OK] Report saved to: {report_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_report: {e}", exc_info=True)
            raise
    def get_actionable_items_summary(self) -> Dict[str, Any]:
        """Get summary of all actionable items from recent reports"""
        reports_dir = self.data_dir
        if not reports_dir.exists():
            return {"error": "No reports found"}

        # Find all report files
        report_files = sorted(reports_dir.glob("extension_monitor_*.json"), reverse=True)

        if not report_files:
            return {"error": "No report files found"}

        # Load most recent report
        try:
            with open(report_files[0], 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            summary = {
                "last_report": report_data.get("report_id"),
                "created_at": report_data.get("created_at"),
                "updates_found": len(report_data.get("updates_found", [])),
                "total_actionable": report_data.get("actionable_count", 0),
                "actionable_by_extension": {}
            }

            # Group actionable items by extension
            for update in report_data.get("updates_found", []):
                ext_name = update.get("extension_name")
                items = update.get("actionable_items", [])
                summary["actionable_by_extension"][ext_name] = {
                    "count": len(items),
                    "items": items[:5]  # Top 5 items
                }

            return summary

        except Exception as e:
            return {"error": f"Error reading report: {e}"}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Monitor VS Code extension updates and syphon actionable items"
        )
        parser.add_argument(
            "--workspace",
            type=str,
            default=".",
            help="Workspace root path"
        )
        parser.add_argument(
            "--summary",
            action="store_true",
            help="Show summary of actionable items"
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Run in test mode with mock data"
        )

        args = parser.parse_args()

        workspace_root = Path(args.workspace).resolve()

        monitor = ExtensionUpdateMonitor(workspace_root)

        if args.test:
            # Test mode: Create mock update to demonstrate functionality
            print("\n" + "=" * 60)
            print("TEST MODE - DEMONSTRATING FUNCTIONALITY")
            print("=" * 60)

            mock_update = ExtensionUpdate(
                extension_id="test-extension",
                extension_name="Test Extension",
                current_version="1.0.0",
                latest_version="1.1.0",
                update_type=UpdateType.FEATURE,
                changelog="""
## What's New in 1.1.0

### New Features
- Added support for new API endpoints
- Introduced dark mode theme
- New keyboard shortcuts for faster workflow

### Bug Fixes
- Fixed memory leak in extension host
- Resolved issue with file watcher
- Fixed crash when opening large files

### Security
- Security patch for CVE-2024-12345
- Updated dependencies to latest secure versions

### Breaking Changes
- Removed deprecated API: `oldMethod()` - use `newMethod()` instead
- Configuration format changed - migration required

### Action Required
- Users must update configuration file format
- Migration script available at: https://example.com/migrate
            """,
            release_notes="This update includes important security fixes and new features. Action required for configuration migration."
        )

        # Syphon the mock update
        syphoned = monitor.syphon_update_content(mock_update)
        print(f"\n[OK] Extracted {len(mock_update.actionable_items)} actionable items from test update")
        print("\nActionable Items Extracted:")
        for i, item in enumerate(mock_update.actionable_items[:10], 1):
            print(f"  {i}. {item}")

        # Create test report
        test_report = ExtensionMonitorReport(
            report_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            monitored_extensions=list(monitor.monitored_extensions.keys()),
            updates_found=[mock_update],
            syphoned_items=syphoned,
            actionable_count=len(mock_update.actionable_items)
        )
        monitor._save_report(test_report)
        print(f"\n[OK] Test report saved")
        return 0

        if args.summary:
            summary = monitor.get_actionable_items_summary()
            print("\n" + "=" * 60)
            print("ACTIONABLE ITEMS SUMMARY")
            print("=" * 60)
            print(json.dumps(summary, indent=2, default=str))
            return 0

        # Run monitoring and syphoning
        report = monitor.monitor_and_syphon()

        # Show actionable items
        if report.actionable_count > 0:
            print("\n" + "=" * 60)
            print("ACTIONABLE ITEMS EXTRACTED")
            print("=" * 60)
            for update in report.updates_found:
                if update.actionable_items:
                    print(f"\n{update.extension_name}:")
                    for item in update.actionable_items[:5]:  # Show top 5
                        print(f"  - {item}")

        return 0
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":



    sys.exit(main())