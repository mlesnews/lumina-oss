#!/usr/bin/env python3
"""
Setup Lumina Data Mining Feedback Loop

Quick setup script to initialize and run the first data mining cycle.

@LUMINA @SETUP @DATA_MINING
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_data_mining_feedback_loop import LuminaFeedbackLoop

def main():
    """Setup and run initial data mining"""
    print("="*60)
    print("Lumina Data Mining Feedback Loop - Initial Setup")
    print("="*60)
    print()

    feedback_loop = LuminaFeedbackLoop(project_root)

    print("🔍 Step 1: Mining data from Lumina...")
    mining_results = feedback_loop.data_miner.mine_all()
    print(f"   ✅ Mined {mining_results['intents']} intents")
    print(f"   ✅ Mined {mining_results['outcomes']} outcomes")
    print(f"   ✅ Created {mining_results['ots']} OTS entries")
    print()

    print("📊 Step 2: Running initial feedback cycle...")
    report = feedback_loop.run_feedback_cycle()
    print(f"   ✅ Cycle {report['cycle_number']} complete")
    print()

    print("📈 Step 3: Generating improvement report...")
    improvement_report = feedback_loop.scaling.get_improvement_report()
    print(f"   ✅ Overall improvement: {improvement_report['overall_improvement']:.2f}x")
    print(f"   ✅ Metrics tracked: {improvement_report['total_metrics']}")
    print()

    print("="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Review feedback report: data/lumina_feedback_loop/feedback_history.json")
    print("2. Run analysis: python scripts/python/analyze_lumina_ots_scaling.py --full")
    print("3. Set up continuous loop: python scripts/python/lumina_data_mining_feedback_loop.py --continuous")
    print()

if __name__ == "__main__":


    main()