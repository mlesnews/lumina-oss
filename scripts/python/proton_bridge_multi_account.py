#!/usr/bin/env python3
"""
Proton Bridge Multi-Account Support
Handles multiple ProtonMail accounts via Proton Bridge

Accounts:
- mlesn@protonmail.com - Primary account (has emails)
- glesn@protonmail.com - Glenda's account (newly created, no emails yet)

Tags: #PROTON_BRIDGE #PROTONMAIL #MULTI_ACCOUNT #EMAIL @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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

try:
    from protonbridge_integration import ProtonBridgeIntegration
    PROTON_BRIDGE_AVAILABLE = True
except ImportError:
    PROTON_BRIDGE_AVAILABLE = False
    logger = get_logger("ProtonBridgeMultiAccount")
    logger.warning("⚠️  ProtonBridge integration not available")

logger = get_logger("ProtonBridgeMultiAccount")


class ProtonBridgeMultiAccount:
    """
    Manage multiple ProtonMail accounts via Proton Bridge

    Supports:
    - mlesn@protonmail.com (has emails)
    - glesn@protonmail.com (newly created, no emails yet)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize multi-account Proton Bridge manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "proton_bridge_accounts.json"
        self.config = self._load_config()

        # Account bridges
        self.bridges: Dict[str, ProtonBridgeIntegration] = {}

        logger.info("✅ Proton Bridge Multi-Account initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load Proton Bridge accounts configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Error loading config: {e}")

        # Default configuration
        return {
            "proton_bridge": {
                "accounts": {
                    "mlesn": {"enabled": True},
                    "glesn": {"enabled": True}
                }
            }
        }

    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get list of configured accounts"""
        accounts = self.config.get("proton_bridge", {}).get("accounts", {})
        return [
            {
                "account_id": account_id,
                **account_config
            }
            for account_id, account_config in accounts.items()
            if account_config.get("enabled", True)
        ]

    def get_bridge(self, account_id: str) -> Optional[ProtonBridgeIntegration]:
        """Get or create Proton Bridge connection for account"""
        if not PROTON_BRIDGE_AVAILABLE:
            logger.error("❌ ProtonBridge integration not available")
            return None

        if account_id in self.bridges:
            return self.bridges[account_id]

        # Create new bridge connection
        try:
            bridge = ProtonBridgeIntegration(self.project_root, account_name=account_id)
            self.bridges[account_id] = bridge
            return bridge
        except Exception as e:
            logger.error(f"❌ Failed to create bridge for {account_id}: {e}")
            return None

    def sync_account(self, account_id: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Sync emails from a specific ProtonMail account

        Args:
            account_id: Account ID (mlesn or glesn)
            days_back: Days to sync back

        Returns:
            Sync results
        """
        logger.info(f"📧 Syncing ProtonMail account: {account_id}")

        bridge = self.get_bridge(account_id)
        if not bridge:
            return {
                "account_id": account_id,
                "success": False,
                "error": "Bridge not available",
                "emails_found": 0
            }

        try:
            # Search emails
            messages = bridge.search_emails(query="ALL", days_back=days_back)

            result = {
                "account_id": account_id,
                "success": True,
                "emails_found": len(messages),
                "timestamp": datetime.now().isoformat()
            }

            if len(messages) == 0:
                logger.info(f"   ℹ️  No emails found (account may be empty or new)")
                result["note"] = "Account is empty or has no emails in date range"
            else:
                logger.info(f"   ✅ Found {len(messages)} emails")

            return result

        except Exception as e:
            logger.error(f"   ❌ Error syncing account {account_id}: {e}")
            return {
                "account_id": account_id,
                "success": False,
                "error": str(e),
                "emails_found": 0
            }

    def sync_all_accounts(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Sync all enabled ProtonMail accounts

        Args:
            days_back: Days to sync back

        Returns:
            Complete sync results
        """
        logger.info("=" * 80)
        logger.info("📧 Syncing All ProtonMail Accounts via Proton Bridge")
        logger.info("=" * 80)
        logger.info("")

        accounts = self.get_accounts()
        results = {
            "timestamp": datetime.now().isoformat(),
            "accounts_synced": 0,
            "total_emails": 0,
            "account_results": []
        }

        for account in accounts:
            account_id = account["account_id"]
            account_result = self.sync_account(account_id, days_back)
            results["account_results"].append(account_result)

            if account_result["success"]:
                results["accounts_synced"] += 1
                results["total_emails"] += account_result["emails_found"]

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 SYNC SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Accounts synced: {results['accounts_synced']}/{len(accounts)}")
        logger.info(f"Total emails found: {results['total_emails']}")
        logger.info("")

        for result in results["account_results"]:
            status = "✅" if result["success"] else "❌"
            emails = result.get("emails_found", 0)
            account_id = result["account_id"]
            logger.info(f"   {status} {account_id}: {emails} emails")
            if result.get("note"):
                logger.info(f"      ℹ️  {result['note']}")

        logger.info("=" * 80)

        return results

    def disconnect_all(self):
        """Disconnect all bridge connections"""
        for bridge in self.bridges.values():
            try:
                bridge.disconnect()
            except:
                pass
        self.bridges.clear()
        logger.info("✅ Disconnected all Proton Bridge connections")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Proton Bridge Multi-Account Support")
    parser.add_argument("--account", help="Sync specific account (mlesn or glesn)")
    parser.add_argument("--all", action="store_true", help="Sync all accounts")
    parser.add_argument("--days", type=int, default=30, help="Days to sync back")
    parser.add_argument("--list", action="store_true", help="List configured accounts")

    args = parser.parse_args()

    manager = ProtonBridgeMultiAccount()

    try:
        if args.list:
            accounts = manager.get_accounts()
            print("\n📧 Configured ProtonMail Accounts:")
            for account in accounts:
                print(f"   • {account['account_id']}: {account.get('protonmail_email', 'N/A')}")
                print(f"     Status: {account.get('status', 'unknown')}")
                print(f"     Enabled: {account.get('enabled', False)}")
                if account.get('note'):
                    print(f"     Note: {account['note']}")
                print()

        elif args.account:
            result = manager.sync_account(args.account, args.days)
            print(f"\n{'✅' if result['success'] else '❌'} {args.account}: {result.get('emails_found', 0)} emails")
            if result.get('note'):
                print(f"   ℹ️  {result['note']}")

        elif args.all:
            manager.sync_all_accounts(args.days)

        else:
            parser.print_help()

    finally:
        manager.disconnect_all()


if __name__ == "__main__":


    main()