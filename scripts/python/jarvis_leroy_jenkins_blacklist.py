#!/usr/bin/env python3
"""
JARVIS Leroy Jenkins Blacklist
Blacklist material/content/transactions
Paper trading required before real money

@JARVIS @BLACKLIST @LEROY_JENKINS @PAPER_TRADING @REAL_MONEY
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLeroyBlacklist")


class LeroyJenkinsBlacklist:
    """
    Leroy Jenkins Blacklist System

    Blacklist material/content/transactions:
    - All-in trades
    - Reckless behavior
    - YOLO moves
    - No risk management
    - Paper trading required before real money
    """

    def __init__(self, project_root: Path = None):
        """Initialize Leroy Jenkins blacklist"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Blacklist patterns
        self.blacklist_patterns = [
            r"(?i)(all\s*in|yolo|go\s*big|maximum\s*leverage)",
            r"(?i)(no\s*stop\s*loss|ignore\s*risk|reckless)",
            r"(?i)(bet\s*everything|risk\s*it\s*all|full\s*send)",
            r"(?i)(skip\s*paper\s*trading|real\s*money\s*first|no\s*paper)",
            r"(?i)(leroy\s*jenkins|leroy|jenkins)",
            r"(?i)(fuck\s*it|send\s*it|let\s*it\s*ride)",
            r"(?i)(no\s*risk\s*management|ignore\s*stop\s*loss)",
            r"(?i)(all\s*or\s*nothing|bet\s*the\s*house)"
        ]

        # Blacklist actions
        self.blacklist_actions = [
            "all_in_trade",
            "yolo_trade",
            "no_stop_loss",
            "skip_paper_trading",
            "maximum_leverage",
            "reckless_behavior",
            "ignore_risk_management",
            "bet_everything"
        ]

        # Blacklist storage
        self.blacklist_file = self.project_root / "data" / "leroy_jenkins_blacklist.json"
        self._load_blacklist()

        logger.info("✅ Leroy Jenkins Blacklist initialized")
        logger.info("   Paper trading required before real money")

    def _load_blacklist(self) -> None:
        """Load blacklist from file"""
        try:
            import json
            if self.blacklist_file.exists():
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    self.blacklist_data = json.load(f)
            else:
                self.blacklist_data = {
                    "blacklisted_content": [],
                    "blacklisted_actions": [],
                    "paper_trading_required": True,
                    "last_updated": None
                }
        except Exception as e:
            logger.warning(f"Could not load blacklist: {e}")
            self.blacklist_data = {
                "blacklisted_content": [],
                "blacklisted_actions": [],
                "paper_trading_required": True,
                "last_updated": None
            }

    def _save_blacklist(self) -> None:
        """Save blacklist to file"""
        try:
            import json
            self.blacklist_data["last_updated"] = datetime.now().isoformat()
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(self.blacklist_data, f, indent=2, default=str)
            logger.info("✅ Blacklist saved")
        except Exception as e:
            logger.error(f"Failed to save blacklist: {e}")

    def check_blacklist(self, text: str) -> Dict[str, Any]:
        """Check if text contains blacklisted content"""
        blacklisted = False
        matches = []
        matched_patterns = []

        for i, pattern in enumerate(self.blacklist_patterns):
            found = re.findall(pattern, text)
            if found:
                blacklisted = True
                matches.extend(found)
                matched_patterns.append(f"pattern_{i+1}")

        result = {
            "blacklisted": blacklisted,
            "matches": matches,
            "matched_patterns": matched_patterns,
            "action": "BLOCK" if blacklisted else "ALLOW",
            "reason": "Leroy Jenkins behavior detected" if blacklisted else None,
            "timestamp": datetime.now().isoformat()
        }

        if blacklisted:
            # Add to blacklist
            self.blacklist_data["blacklisted_content"].append({
                "text": text[:200],
                "matches": matches,
                "timestamp": datetime.now().isoformat()
            })
            self._save_blacklist()

        return result

    def validate_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade against blacklist"""
        logger.info("=" * 70)
        logger.info("🚫 TRADE VALIDATION AGAINST BLACKLIST")
        logger.info("=" * 70)
        logger.info("")

        # Check 1: Paper trading requirement
        paper_trading = trade_data.get("paper_trading", False)
        if not paper_trading:
            logger.error("❌ BLOCKED: Paper trading required before real money")
            return {
                "valid": False,
                "reason": "Paper trading required before real money",
                "action": "BLOCK",
                "blacklist": True,
                "paper_trading_required": True
            }

        logger.info("✅ Paper trading requirement met")

        # Check 2: Blacklist content check
        trade_description = str(trade_data.get("description", ""))
        blacklist_check = self.check_blacklist(trade_description)

        if blacklist_check["blacklisted"]:
            logger.error(f"❌ BLOCKED: {blacklist_check['reason']}")
            logger.error(f"   Matches: {blacklist_check['matches']}")
            return {
                "valid": False,
                "reason": blacklist_check["reason"],
                "action": "BLOCK",
                "blacklist": True,
                "matches": blacklist_check["matches"]
            }

        logger.info("✅ No blacklisted content detected")

        # Check 3: Risk management check
        has_stop_loss = trade_data.get("stop_loss", False)
        has_profit_target = trade_data.get("profit_target", False)
        position_size = trade_data.get("position_size_percent", 0)

        if not has_stop_loss:
            logger.warning("⚠️  WARNING: No stop-loss specified")
        if not has_profit_target:
            logger.warning("⚠️  WARNING: No profit target specified")
        if position_size > 5:
            logger.error(f"❌ BLOCKED: Position size {position_size}% exceeds 5% limit")
            return {
                "valid": False,
                "reason": f"Position size {position_size}% exceeds 5% limit",
                "action": "BLOCK",
                "blacklist": True
            }

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ TRADE VALIDATED")
        logger.info("=" * 70)

        return {
            "valid": True,
            "action": "ALLOW",
            "blacklist": False,
            "paper_trading": paper_trading,
            "risk_management": {
                "stop_loss": has_stop_loss,
                "profit_target": has_profit_target,
                "position_size": position_size
            }
        }

    def get_blacklist_summary(self) -> Dict[str, Any]:
        """Get blacklist summary"""
        return {
            "total_blacklisted": len(self.blacklist_data.get("blacklisted_content", [])),
            "paper_trading_required": self.blacklist_data.get("paper_trading_required", True),
            "blacklist_patterns": len(self.blacklist_patterns),
            "blacklist_actions": len(self.blacklist_actions),
            "last_updated": self.blacklist_data.get("last_updated")
        }


def main():
    """Main execution"""
    print("=" * 70)
    print("🚫 JARVIS LEROY JENKINS BLACKLIST")
    print("   Paper trading required before real money")
    print("=" * 70)
    print()

    blacklist = LeroyJenkinsBlacklist()

    # Test validation
    test_trade = {
        "description": "DCA Bitcoin with stop-loss",
        "paper_trading": True,
        "stop_loss": True,
        "profit_target": True,
        "position_size_percent": 3
    }

    result = blacklist.validate_trade(test_trade)

    print()
    print("=" * 70)
    print("✅ BLACKLIST SYSTEM READY")
    print("=" * 70)
    print(f"Trade Valid: {result.get('valid', False)}")
    print(f"Action: {result.get('action', 'UNKNOWN')}")
    print("=" * 70)


if __name__ == "__main__":


    main()