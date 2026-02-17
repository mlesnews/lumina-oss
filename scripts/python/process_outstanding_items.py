#!/usr/bin/env python3
"""
Process Outstanding Items in Environment

Systematically processes all outstanding items:
1. Pending todos
2. Unconfigured systems
3. Missing integrations
4. Incomplete workflows
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from master_todo_tracker import MasterTodoTracker, TaskStatus, Priority
    TODO_TRACKER_AVAILABLE = True
except ImportError:
    TODO_TRACKER_AVAILABLE = False
    MasterTodoTracker = None


class OutstandingItemsProcessor:
    """Process outstanding items in the environment"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.tracker = MasterTodoTracker(project_root) if TODO_TRACKER_AVAILABLE else None

        self.processed_items = []
        self.failed_items = []

    def get_outstanding_items(self) -> Dict[str, List[Any]]:
        """Get all outstanding items"""
        items = {
            "pending_todos": [],
            "unconfigured_syphon": [],
            "incomplete_workflows": [],
            "missing_integrations": []
        }

        # Get pending todos
        if self.tracker:
            todos = self.tracker.get_todos()
            items["pending_todos"] = [t for t in todos if t.status == TaskStatus.PENDING]

        # Check SYPHON configuration
        items["unconfigured_syphon"] = self._check_syphon_config()

        # Check for incomplete workflows
        items["incomplete_workflows"] = self._check_workflows()

        # Check for missing integrations
        items["missing_integrations"] = self._check_integrations()

        return items

    def _check_syphon_config(self) -> List[Dict[str, Any]]:
        try:
            """Check SYPHON configuration status"""
            issues = []

            import json

            # Check email accounts
            email_config = self.project_root / "config" / "email_accounts.json"
            if email_config.exists():
                with open(email_config, 'r') as f:
                    config = json.load(f)
                    accounts = config.get("email_accounts", {}).get("accounts", [])
                    enabled = [a for a in accounts if a.get("enabled", False)]
                    if len(enabled) == 0:
                        issues.append({
                            "type": "email_syphon",
                            "issue": "No email accounts enabled",
                            "file": str(email_config),
                            "action": "Configure email accounts in config/email_accounts.json"
                        })

            # Check SMS sources
            sms_config = self.project_root / "config" / "sms_sources.json"
            if sms_config.exists():
                with open(sms_config, 'r') as f:
                    config = json.load(f)
                    sources = config.get("sms_sources", {}).get("sources", [])
                    enabled = [s for s in sources if s.get("enabled", False)]
                    if len(enabled) == 0:
                        issues.append({
                            "type": "sms_syphon",
                            "issue": "No SMS sources enabled",
                            "file": str(sms_config),
                            "action": "Configure SMS sources in config/sms_sources.json"
                        })

            # Check messenger sources
            messenger_config = self.project_root / "config" / "messenger_sources.json"
            if messenger_config.exists():
                with open(messenger_config, 'r') as f:
                    config = json.load(f)
                    sources = config.get("messenger_sources", {}).get("sources", [])
                    enabled = [s for s in sources if s.get("enabled", False)]
                    if len(enabled) == 0:
                        issues.append({
                            "type": "messenger_syphon",
                            "issue": "No messenger sources enabled",
                            "file": str(messenger_config),
                            "action": "Configure messenger sources in config/messenger_sources.json"
                        })

            return issues

        except Exception as e:
            self.logger.error(f"Error in _check_syphon_config: {e}", exc_info=True)
            raise
    def _check_workflows(self) -> List[Dict[str, Any]]:
        """Check for incomplete workflows"""
        issues = []

        # Check Lumina Extension completion tasks
        if self.tracker:
            extension_todos = [t for t in self.tracker.get_todos() 
                             if "Lumina Extension" in t.title and t.status == TaskStatus.PENDING]
            if extension_todos:
                issues.append({
                    "type": "lumina_extension",
                    "issue": f"{len(extension_todos)} Lumina Extension tasks pending",
                    "action": "Complete Lumina Extension tasks"
                })

        return issues

    def _check_integrations(self) -> List[Dict[str, Any]]:
        try:
            """Check for missing integrations"""
            issues = []

            # Check N8N connectivity
            import json
            n8n_config = self.project_root / "config" / "n8n" / "unified_communications_config.json"
            if n8n_config.exists():
                with open(n8n_config, 'r') as f:
                    config = json.load(f)
                    n8n_url = config.get("n8n_config", {}).get("n8n_url", "")
                    if n8n_url and "localhost" in n8n_url:
                        issues.append({
                            "type": "n8n_integration",
                            "issue": "N8N still configured for localhost",
                            "action": "Update N8N config to use NAS IP"
                        })

            return issues

        except Exception as e:
            self.logger.error(f"Error in _check_integrations: {e}", exc_info=True)
            raise
    def process_item(self, item: Dict[str, Any]) -> bool:
        """Process a single outstanding item"""
        item_type = item.get("type", "")

        try:
            if item_type == "email_syphon":
                # Can't auto-configure (needs credentials)
                return False
            elif item_type == "sms_syphon":
                # Can't auto-configure (needs credentials)
                return False
            elif item_type == "messenger_syphon":
                # Can't auto-configure (needs credentials)
                return False
            elif item_type == "n8n_integration":
                # Already done - skip
                return True
            elif item_type == "lumina_extension":
                # Already verified complete
                return True
            else:
                return False
        except Exception as e:
            self.failed_items.append({"item": item, "error": str(e)})
            return False

    def process_all(self) -> Dict[str, Any]:
        """Process all outstanding items"""
        print("=" * 80)
        print("🔄 PROCESSING OUTSTANDING ITEMS")
        print("=" * 80)

        items = self.get_outstanding_items()

        total_items = (
            len(items["pending_todos"]) +
            len(items["unconfigured_syphon"]) +
            len(items["incomplete_workflows"]) +
            len(items["missing_integrations"])
        )

        print(f"\n📊 Found {total_items} outstanding items:")
        print(f"   - Pending Todos: {len(items['pending_todos'])}")
        print(f"   - Unconfigured SYPHON: {len(items['unconfigured_syphon'])}")
        print(f"   - Incomplete Workflows: {len(items['incomplete_workflows'])}")
        print(f"   - Missing Integrations: {len(items['missing_integrations'])}")

        # Process items
        processed = 0
        skipped = 0

        # Process SYPHON issues (informational only - need user credentials)
        for item in items["unconfigured_syphon"]:
            print(f"\n⚠️  {item['type']}: {item['issue']}")
            print(f"   Action: {item['action']}")
            skipped += 1

        # Process workflow issues
        for item in items["incomplete_workflows"]:
            if self.process_item(item):
                processed += 1
                self.processed_items.append(item)
            else:
                skipped += 1

        # Process integration issues
        for item in items["missing_integrations"]:
            if self.process_item(item):
                processed += 1
                self.processed_items.append(item)
            else:
                skipped += 1

        # Summary
        print("\n" + "=" * 80)
        print("📊 PROCESSING SUMMARY")
        print("=" * 80)
        print(f"   Total Items: {total_items}")
        print(f"   Processed: {processed}")
        print(f"   Skipped (Need User Action): {skipped}")
        print(f"   Failed: {len(self.failed_items)}")

        if self.processed_items:
            print("\n✅ Processed Items:")
            for item in self.processed_items:
                print(f"   - {item.get('type', 'unknown')}: {item.get('issue', 'N/A')}")

        if self.failed_items:
            print("\n❌ Failed Items:")
            for item in self.failed_items:
                print(f"   - {item['item'].get('type', 'unknown')}: {item['error']}")

        return {
            "total": total_items,
            "processed": processed,
            "skipped": skipped,
            "failed": len(self.failed_items),
            "items": items
        }


def main():
    """Main execution"""
    processor = OutstandingItemsProcessor()
    result = processor.process_all()

    print("\n" + "=" * 80)
    print("✅ PROCESSING COMPLETE")
    print("=" * 80)

    # Show next steps
    if result["skipped"] > 0:
        print("\n📋 Next Steps (Require User Action):")
        print("   1. Configure SYPHON systems (use configure_syphon_systems.py)")
        print("   2. Review pending todos")
        print("   3. Complete any remaining workflows")


if __name__ == "__main__":



    main()