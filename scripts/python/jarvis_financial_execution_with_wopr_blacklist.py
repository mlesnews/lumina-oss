#!/usr/bin/env python3
"""
JARVIS Financial Execution with WOPR & Blacklist
Integrates SYPHON financial strategies with WOPR pattern matching
Enforces Leroy Jenkins blacklist and paper trading requirement

@JARVIS @FINANCIAL @WOPR @BLACKLIST @PAPER_TRADING
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFinancialWOPR")


class JARVISFinancialExecutionWOPR:
    """
    Financial Execution with WOPR Pattern Matching & Blacklist

    Features:
    - SYPHON financial strategies
    - WOPR pattern matching
    - Leroy Jenkins blacklist enforcement
    - Paper trading requirement
    """

    def __init__(self):
        """Initialize financial execution with WOPR"""
        # Import systems
        from scripts.python.jarvis_syphon_financial_strategies_wopr import SyphonFinancialStrategiesWOPR
        from scripts.python.jarvis_leroy_jenkins_blacklist import LeroyJenkinsBlacklist

        self.syphon = SyphonFinancialStrategiesWOPR()
        self.blacklist = LeroyJenkinsBlacklist()

        logger.info("✅ JARVIS Financial Execution WOPR initialized")

    async def execute_with_wopr_validation(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trade with WOPR validation and blacklist check

        Args:
            trade_data: Trade data including description, paper_trading, etc.
        """
        logger.info("=" * 70)
        logger.info("💰 FINANCIAL EXECUTION WITH WOPR VALIDATION")
        logger.info("=" * 70)
        logger.info("")

        # Step 1: Blacklist validation
        logger.info("STEP 1: Blacklist Validation...")
        validation = self.blacklist.validate_trade(trade_data)

        if not validation.get("valid", False):
            logger.error("❌ TRADE BLOCKED BY BLACKLIST")
            logger.error(f"   Reason: {validation.get('reason', 'Unknown')}")
            return {
                "success": False,
                "blocked": True,
                "reason": validation.get("reason"),
                "action": "BLOCK"
            }

        logger.info("✅ Trade passed blacklist validation")
        logger.info("")

        # Step 2: WOPR pattern matching
        logger.info("STEP 2: WOPR Pattern Matching...")
        trade_description = str(trade_data.get("description", ""))
        wopr_matches = self.syphon.wopr.match_patterns(trade_description)

        if wopr_matches:
            logger.info(f"   Patterns found: {list(wopr_matches.keys())}")
            for pattern, matches in wopr_matches.items():
                logger.info(f"     {pattern}: {len(matches)} matches")
        else:
            logger.info("   No WOPR patterns matched")

        logger.info("")

        # Step 3: Strategy extraction
        logger.info("STEP 3: Strategy Extraction...")
        strategy = self.syphon.wopr.extract_strategy(trade_description)

        if strategy.get("strategy_type"):
            logger.info(f"   Strategy Type: {strategy['strategy_type']}")
            logger.info(f"   Risk Level: {strategy['risk_level']}")
        else:
            logger.info("   No specific strategy type identified")

        logger.info("")

        # Step 4: Execute (if paper trading)
        if trade_data.get("paper_trading", False):
            logger.info("STEP 4: Paper Trading Execution...")
            logger.info("   ✅ Paper trading mode - Safe to execute")
            logger.info("   📊 Simulating trade execution...")

            # Simulate execution
            execution_result = {
                "success": True,
                "mode": "paper_trading",
                "strategy": strategy.get("strategy_type"),
                "risk_level": strategy.get("risk_level"),
                "wopr_patterns": wopr_matches,
                "executed_at": datetime.now().isoformat()
            }

            logger.info("   ✅ Trade executed (paper trading)")
        else:
            logger.error("❌ Real money execution blocked - Paper trading required")
            return {
                "success": False,
                "blocked": True,
                "reason": "Paper trading required before real money",
                "action": "BLOCK"
            }

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ EXECUTION COMPLETE")
        logger.info("=" * 70)

        return execution_result

    async def get_recommended_strategies(self) -> List[Dict[str, Any]]:
        """Get recommended strategies from SYPHON results"""
        logger.info("🔍 Loading recommended strategies from SYPHON...")

        # Load latest SYPHON results
        syphon_dir = self.syphon.output_dir
        if not syphon_dir.exists():
            return []

        # Find latest results file
        result_files = sorted(syphon_dir.glob("financial_strategies_*.json"), reverse=True)
        if not result_files:
            return []

        try:
            import json
            with open(result_files[0], 'r', encoding='utf-8') as f:
                results = json.load(f)

            # Extract unique strategies
            strategies = []
            seen = set()

            for strategy in results.get("strategies_extracted", []):
                strategy_type = strategy.get("wopr_patterns", {})
                if strategy_type and strategy.get("source") not in seen:
                    seen.add(strategy.get("source"))
                    strategies.append({
                        "source": strategy.get("source"),
                        "type": strategy.get("type"),
                        "patterns": list(strategy_type.keys()),
                        "text_preview": strategy.get("text", "")[:200]
                    })

            logger.info(f"✅ Loaded {len(strategies)} recommended strategies")
            return strategies[:10]  # Top 10

        except Exception as e:
            logger.error(f"Failed to load strategies: {e}")
            return []


async def main():
    """Main execution"""
    print("=" * 70)
    print("💰 JARVIS FINANCIAL EXECUTION WITH WOPR & BLACKLIST")
    print("=" * 70)
    print()

    executor = JARVISFinancialExecutionWOPR()

    # Test trade
    test_trade = {
        "description": "DCA Bitcoin with stop-loss and profit target",
        "paper_trading": True,
        "stop_loss": True,
        "profit_target": True,
        "position_size_percent": 3
    }

    result = await executor.execute_with_wopr_validation(test_trade)

    print()
    print("=" * 70)
    print("✅ EXECUTION TEST COMPLETE")
    print("=" * 70)
    print(f"Success: {result.get('success', False)}")
    print(f"Blocked: {result.get('blocked', False)}")
    print(f"Mode: {result.get('mode', 'N/A')}")
    print("=" * 70)

    # Get recommended strategies
    print()
    strategies = await executor.get_recommended_strategies()
    print(f"Recommended strategies: {len(strategies)}")
    for i, strategy in enumerate(strategies[:5], 1):
        print(f"  {i}. {strategy.get('type', 'unknown')} - {len(strategy.get('patterns', []))} patterns")


if __name__ == "__main__":


    asyncio.run(main())