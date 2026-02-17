#!/usr/bin/env python3
"""
SYPHON Blacklist Pattern Enforcer
Prevents blacklisted behavior patterns from recurring

Author: @marvin + @hk-47
Date: 2025-01-28
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SYPHONBlacklist")


class BlacklistEnforcer:
    """Enforces blacklist patterns to prevent recurring mistakes"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        # Try multiple possible paths
        possible_paths = [
            self.project_root / "data" / "syphon" / "blacklist_patterns",
            self.project_root.parent / "data" / "syphon" / "blacklist_patterns",
            Path(__file__).parent.parent.parent / "data" / "syphon" / "blacklist_patterns",
        ]

        self.blacklist_dir = None
        for path in possible_paths:
            if path.exists():
                self.blacklist_dir = path
                break

        if not self.blacklist_dir:
            # Use first path and create it
            self.blacklist_dir = possible_paths[0]
            self.blacklist_dir.mkdir(parents=True, exist_ok=True)

        self.blacklist_patterns: Dict[str, Dict] = {}
        self._load_blacklist_patterns()

    def _load_blacklist_patterns(self):
        """Load all blacklist patterns"""
        for pattern_file in self.blacklist_dir.glob("*.json"):
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    pattern = json.load(f)
                    if pattern.get("status") == "active":
                        self.blacklist_patterns[pattern["pattern_id"]] = pattern
                        logger.debug(f"Loaded blacklist pattern: {pattern['pattern_name']}")
            except Exception as e:
                logger.warning(f"Failed to load blacklist pattern {pattern_file}: {e}")

        logger.info(f"Loaded {len(self.blacklist_patterns)} active blacklist patterns")

    def check_assumption_without_verification(self, context: Dict) -> Dict:
        try:
            """
            Check if workflow is making assumptions without verification

            Returns:
                Dict with 'violated' (bool) and 'message' (str)
            """
            pattern_id = "blacklist-assumption-without-verification-20250128"

            if pattern_id not in self.blacklist_patterns:
                return {"violated": False, "message": "Pattern not found in blacklist"}

            pattern = self.blacklist_patterns[pattern_id]

            # Check for assumption indicators
            assumption_indicators = [
                "assume", "assumed", "assuming",
                "probably", "likely", "should be",
                "must be", "must have", "should have",
                "documentation says", "code exists",
                "architecture defined", "we thought",
                "we believed", "we expected"
            ]

            # Check context for assumption language
            context_text = json.dumps(context).lower()
            found_indicators = [ind for ind in assumption_indicators if ind in context_text]

            # Check if verification was performed
            verification_indicators = [
                "verify", "verified", "verification",
                "check", "checked", "test", "tested",
                "confirm", "confirmed", "validate", "validated",
                "ran verification", "executed verification"
            ]

            found_verification = [ind for ind in verification_indicators if ind in context_text]

            # Also check if verification_command was run
            verification_ran = "verification_report" in context_text or "verification_results" in context_text

            # Determine violation
            if found_indicators and not found_verification and not verification_ran:
                return {
                    "violated": True,
                    "message": f"BLACKLIST VIOLATION: Assumption without verification detected",
                    "pattern": pattern["pattern_name"],
                    "indicators_found": found_indicators,
                    "verification_missing": True,
                    "recommendation": "Run verification before proceeding",
                    "verification_command": pattern["prevention_pattern"]["verification_commands"][0] if pattern["prevention_pattern"].get("verification_commands") else None
                }

            return {"violated": False, "message": "No violation detected"}

        except Exception as e:
            self.logger.error(f"Error in check_assumption_without_verification: {e}", exc_info=True)
            raise
    def enforce_verification_first(self, workflow_step: str, context: Dict) -> Dict:
        try:
            """
            Enforce verification-first pattern

            Returns:
                Dict with 'allowed' (bool) and 'message' (str)
            """
            # Check if this step requires verification
            verification_required_keywords = [
                "infrastructure", "service", "setup", "configured",
                "exists", "operational", "implemented", "deployed"
            ]

            requires_verification = any(
                keyword in workflow_step.lower() 
                for keyword in verification_required_keywords
            )

            if not requires_verification:
                return {"allowed": True, "message": "Verification not required for this step"}

            # Check if verification was performed
            verification_performed = any(
                keyword in json.dumps(context).lower()
                for keyword in ["verify", "verified", "check", "checked", "test", "tested", "confirm", "validated"]
            )

            if not verification_performed:
                return {
                    "allowed": False,
                    "message": "BLACKLIST ENFORCEMENT: Verification required before proceeding",
                    "required_action": "Run verification script first",
                    "verification_command": "python scripts/python/verify_azure_security_granular.py"
                }

            return {"allowed": True, "message": "Verification performed, proceeding allowed"}


        except Exception as e:
            self.logger.error(f"Error in enforce_verification_first: {e}", exc_info=True)
            raise
def main():
    try:
        """Test blacklist enforcer"""
        script_path = Path(__file__).resolve()
        # Go up from scripts/python/ to project root
        project_root = script_path.parent.parent.parent

        enforcer = BlacklistEnforcer(project_root)

        # Test assumption detection
        test_context = {
            "action": "Assuming Azure Key Vault is set up",
            "reason": "Code exists that references it",
            "verification": None
        }

        result = enforcer.check_assumption_without_verification(test_context)
        print("=" * 80)
        print("SYPHON BLACKLIST ENFORCER TEST")
        print("=" * 80)
        print(f"\nTest Context: {test_context}")
        print(f"\nResult: {result}")

        if result["violated"]:
            print("\n🔴 BLACKLIST VIOLATION DETECTED!")
            print(f"   Pattern: {result['pattern']}")
            print(f"   Recommendation: {result['recommendation']}")
            if result.get("verification_command"):
                print(f"   Run: {result['verification_command']}")

        # Test verification enforcement
        workflow_step = "Check if Azure Key Vault is set up"
        context = {"assumption": "Key Vault should be set up"}

        enforcement = enforcer.enforce_verification_first(workflow_step, context)
        print(f"\n\nWorkflow Step: {workflow_step}")
        print(f"Context: {context}")
        print(f"Enforcement Result: {enforcement}")

        if not enforcement["allowed"]:
            print("\n🔴 WORKFLOW BLOCKED!")
            print(f"   Reason: {enforcement['message']}")
            print(f"   Action: {enforcement['required_action']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()