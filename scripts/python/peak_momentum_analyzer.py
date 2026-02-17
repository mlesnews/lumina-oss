#!/usr/bin/env python3
"""
PEAK Momentum Analyzer

Identifies the "cresting wave" and "mountain peak summit" moment - that critical
inflection point where momentum accelerates, inertia is overcome, and maximum ROI
is achieved in a compressed timeframe.

Time waits for no one. The candle burns from both ends. The time is NOW.

Tags: #PEAK #MOMENTUM #SUMMIT #CRESTING-WAVE #ROI #TIME-COMPRESSION @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from master_jarvis_agent_chat_processor import MasterJARVISAgentChatProcessor
    from ai_system_service_prompts import AISystemServicePrompts
    from persistent_memory_gap_tracker import PersistentMemoryGapTracker
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("PEAKMomentumAnalyzer")
ts_logger = get_timestamp_logger()


@dataclass
class MomentumOpportunity:
    """Represents a momentum opportunity"""
    opportunity_id: str
    title: str
    description: str
    momentum_score: float  # 0.0 to 10.0
    roi_multiplier: float  # Expected ROI multiplier
    time_compression: float  # Time saved/compressed (hours)
    inertia_resistance: float  # Resistance to overcome (1.0 = easy, 10.0 = hard)
    dependencies: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    force_multipliers: List[str] = field(default_factory=list)
    execution_time: int = 0  # Estimated execution time (hours)
    critical_path: bool = False


@dataclass
class PeakMomentumPlan:
    """Peak momentum execution plan"""
    plan_id: str
    title: str
    opportunities: List[MomentumOpportunity]
    total_momentum_score: float
    total_roi_multiplier: float
    compressed_timeline: Dict[str, Any]
    critical_path: List[str]
    execution_order: List[str]


class PEAKMomentumAnalyzer:
    """
    PEAK Momentum Analyzer

    Identifies the "cresting wave" and "mountain peak summit" moment.
    Focuses on what will propel us in @peak fashion in a compressed time interval.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize PEAK Momentum Analyzer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.master_processor = MasterJARVISAgentChatProcessor(project_root=project_root)
        self.service_prompts = AISystemServicePrompts(project_root=project_root)
        self.gap_tracker = PersistentMemoryGapTracker(project_root=project_root)

        logger.info("⛰️  PEAK Momentum Analyzer initialized")
        logger.info("   Identifying the cresting wave and mountain peak summit")

    def analyze_momentum_opportunities(self) -> List[MomentumOpportunity]:
        """Analyze all opportunities for peak momentum"""
        opportunities = []

        # 1. Complete 5x Memory/XP System (CRITICAL - Requested 3+ times)
        opportunities.append(MomentumOpportunity(
            opportunity_id="memory_xp_system",
            title="Complete 5x Memory/XP System",
            description="Full implementation of XP/DKP system, JARVIS character progression, WoW World Atlas integration",
            momentum_score=9.5,  # Very high - unlocks character progression
            roi_multiplier=5.0,  # 5x ROI - requested 3+ times, high value
            time_compression=40.0,  # Saves 40+ hours of repeated requests
            inertia_resistance=6.0,  # Medium-high resistance (complex system)
            dependencies=[],
            blockers=["Partial implementation only"],
            force_multipliers=["Character progression", "Persistent memory", "Gamification"],
            execution_time=8,  # 8 hours to complete
            critical_path=True,
        ))

        # 2. Execute NAS Migration (READY - Credentials cached)
        opportunities.append(MomentumOpportunity(
            opportunity_id="nas_migration",
            title="Execute NAS Migration",
            description="Migrate .lumina project to NAS - credentials cached, ready to execute",
            momentum_score=8.5,  # High - unblocks storage
            roi_multiplier=3.0,  # 3x ROI - frees C: drive, enables growth
            time_compression=20.0,  # Saves 20+ hours of storage management
            inertia_resistance=3.0,  # Low resistance (ready to go)
            dependencies=["Network optimization"],
            blockers=["Network bandwidth (WiFi vs LAN)"],
            force_multipliers=["Storage freedom", "Scalability", "Backup"],
            execution_time=4,  # 4 hours (mostly automated)
            critical_path=True,
        ))

        # 3. Network Optimization (BLOCKER REMOVAL)
        opportunities.append(MomentumOpportunity(
            opportunity_id="network_optimization",
            title="Network Optimization - Switch to LAN/Homelab",
            description="Optimize network path for NAS migration - switch from WiFi to LAN",
            momentum_score=7.0,  # Medium-high - unblocks migration
            roi_multiplier=2.5,  # 2.5x ROI - enables faster transfers
            time_compression=10.0,  # Saves 10+ hours of transfer time
            inertia_resistance=2.0,  # Low resistance (simple config change)
            dependencies=[],
            blockers=[],
            force_multipliers=["Bandwidth", "Reliability", "Speed"],
            execution_time=1,  # 1 hour (configuration)
            critical_path=True,
        ))

        # 4. Master Agent Chat Integration (ONE RING)
        opportunities.append(MomentumOpportunity(
            opportunity_id="master_agent_integration",
            title="Master Agent Chat - One Ring Integration",
            description="Complete integration of Master Agent Chat as the One Ring binding all sessions",
            momentum_score=8.0,  # High - central coordination
            roi_multiplier=4.0,  # 4x ROI - eliminates duplication
            time_compression=30.0,  # Saves 30+ hours of duplicate work
            inertia_resistance=4.0,  # Medium resistance (integration work)
            dependencies=["AI System Service Prompts"],
            blockers=[],
            force_multipliers=["Coordination", "Consistency", "Memory"],
            execution_time=6,  # 6 hours
            critical_path=False,
        ))

        # 5. Resolve Hidden Memory Gaps (DEBT PAYMENT)
        opportunities.append(MomentumOpportunity(
            opportunity_id="resolve_memory_gaps",
            title="Resolve Hidden Memory Gaps",
            description="Detect and resolve 3 hidden memory gaps (-6 DKP penalty)",
            momentum_score=6.5,  # Medium-high - reduces technical debt
            roi_multiplier=2.0,  # 2x ROI - prevents future issues
            time_compression=8.0,  # Saves 8+ hours of debugging
            inertia_resistance=5.0,  # Medium resistance (hidden = hard to find)
            dependencies=["Memory/XP System"],
            blockers=["Hidden gaps are hard to detect"],
            force_multipliers=["Debt reduction", "Quality", "Reliability"],
            execution_time=4,  # 4 hours
            critical_path=False,
        ))

        # 6. AI System Service Prompts (FOUNDATION)
        opportunities.append(MomentumOpportunity(
            opportunity_id="service_prompts_foundation",
            title="AI System Service Prompts Foundation",
            description="Complete foundation of AI System Service Prompts with core values",
            momentum_score=7.5,  # High - foundational
            roi_multiplier=3.5,  # 3.5x ROI - guides all future work
            time_compression=25.0,  # Saves 25+ hours of decision-making
            inertia_resistance=3.0,  # Low resistance (already created)
            dependencies=[],
            blockers=[],
            force_multipliers=["Consistency", "Quality", "Values"],
            execution_time=2,  # 2 hours (mostly done)
            critical_path=False,
        ))

        logger.info(f"📊 Analyzed {len(opportunities)} momentum opportunities")
        return opportunities

    def calculate_critical_path(self, opportunities: List[MomentumOpportunity]) -> List[str]:
        """Calculate critical path to summit"""
        # Critical path: opportunities that are blockers or have highest momentum
        critical = []

        # Sort by momentum score and critical_path flag
        sorted_opps = sorted(
            opportunities,
            key=lambda x: (x.critical_path, x.momentum_score),
            reverse=True
        )

        for opp in sorted_opps:
            if opp.critical_path:
                critical.append(opp.opportunity_id)
            elif opp.momentum_score >= 8.0:
                critical.append(opp.opportunity_id)

        logger.info(f"🎯 Critical path: {len(critical)} opportunities")
        return critical

    def create_compressed_timeline(self, opportunities: List[MomentumOpportunity]) -> Dict[str, Any]:
        """Create compressed execution timeline"""
        # Group by execution time and dependencies
        timeline = {
            "immediate": [],  # 0-2 hours
            "short_term": [],  # 2-4 hours
            "medium_term": [],  # 4-8 hours
            "parallel": [],  # Can run in parallel
        }

        for opp in opportunities:
            if opp.execution_time <= 2:
                timeline["immediate"].append(opp.opportunity_id)
            elif opp.execution_time <= 4:
                timeline["short_term"].append(opp.opportunity_id)
            elif opp.execution_time <= 8:
                timeline["medium_term"].append(opp.opportunity_id)

            # Check if can run in parallel
            if not opp.dependencies:
                timeline["parallel"].append(opp.opportunity_id)

        # Calculate total time (with parallelization)
        max_parallel_time = max([opp.execution_time for opp in opportunities if not opp.dependencies], default=0)
        sequential_time = sum([opp.execution_time for opp in opportunities if opp.dependencies])
        total_time = max_parallel_time + sequential_time

        timeline["total_time_hours"] = total_time
        timeline["total_time_days"] = total_time / 8.0  # Assuming 8-hour workday

        return timeline

    def identify_cresting_wave(self, opportunities: List[MomentumOpportunity]) -> MomentumOpportunity:
        """Identify the cresting wave - highest momentum opportunity"""
        # The cresting wave is the opportunity with highest momentum_score * roi_multiplier
        # that has low inertia_resistance (can overcome gravity)

        best_opp = None
        best_score = 0.0

        for opp in opportunities:
            # Momentum score weighted by ROI and inverse of resistance
            score = (opp.momentum_score * opp.roi_multiplier) / (opp.inertia_resistance + 1.0)

            if score > best_score:
                best_score = score
                best_opp = opp

        if best_opp:
            logger.info(f"🌊 Cresting Wave: {best_opp.title} (Score: {best_score:.2f})")

        return best_opp

    def create_peak_plan(self) -> PeakMomentumPlan:
        """Create peak momentum execution plan"""
        logger.info("="*80)
        logger.info("⛰️  PEAK Momentum Analysis - Cresting Wave & Summit")
        logger.info("="*80)
        logger.info("   Time waits for no one. The candle burns from both ends.")
        logger.info("   The time is NOW.")

        # Analyze opportunities
        opportunities = self.analyze_momentum_opportunities()

        # Identify cresting wave
        cresting_wave = self.identify_cresting_wave(opportunities)

        # Calculate critical path
        critical_path = self.calculate_critical_path(opportunities)

        # Create compressed timeline
        timeline = self.create_compressed_timeline(opportunities)

        # Calculate totals
        total_momentum = sum([opp.momentum_score for opp in opportunities])
        total_roi = sum([opp.roi_multiplier for opp in opportunities])

        # Execution order: critical path first, then by momentum
        execution_order = critical_path.copy()
        remaining = [opp.opportunity_id for opp in opportunities if opp.opportunity_id not in execution_order]
        remaining_sorted = sorted(
            remaining,
            key=lambda x: next(opp.momentum_score for opp in opportunities if opp.opportunity_id == x),
            reverse=True
        )
        execution_order.extend(remaining_sorted)

        plan = PeakMomentumPlan(
            plan_id=f"peak_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title="PEAK Momentum Execution Plan - Cresting Wave & Summit",
            opportunities=opportunities,
            total_momentum_score=total_momentum,
            total_roi_multiplier=total_roi,
            compressed_timeline=timeline,
            critical_path=critical_path,
            execution_order=execution_order,
        )

        return plan


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="PEAK Momentum Analyzer")
    parser.add_argument("--analyze", action="store_true", help="Analyze momentum opportunities")
    parser.add_argument("--plan", action="store_true", help="Create peak momentum plan")
    parser.add_argument("--cresting-wave", action="store_true", help="Identify cresting wave")

    args = parser.parse_args()

    print("="*80)
    print("⛰️  PEAK MOMENTUM ANALYZER")
    print("="*80)
    print()
    print("Identifying the cresting wave and mountain peak summit")
    print("Time waits for no one. The time is NOW.")
    print()

    analyzer = PEAKMomentumAnalyzer()

    if args.plan or args.analyze or args.cresting_wave:
        plan = analyzer.create_peak_plan()

        print("📊 PEAK MOMENTUM PLAN:")
        print(f"   Total Opportunities: {len(plan.opportunities)}")
        print(f"   Total Momentum Score: {plan.total_momentum_score:.1f}")
        print(f"   Total ROI Multiplier: {plan.total_roi_multiplier:.1f}x")
        print(f"   Compressed Timeline: {plan.compressed_timeline['total_time_hours']:.1f} hours ({plan.compressed_timeline['total_time_days']:.1f} days)")
        print()

        if args.cresting_wave:
            cresting_wave = analyzer.identify_cresting_wave(plan.opportunities)
            if cresting_wave:
                print("🌊 CRESTING WAVE:")
                print(f"   {cresting_wave.title}")
                print(f"   Momentum Score: {cresting_wave.momentum_score:.1f}")
                print(f"   ROI Multiplier: {cresting_wave.roi_multiplier:.1f}x")
                print(f"   Time Compression: {cresting_wave.time_compression:.1f} hours")
                print(f"   Execution Time: {cresting_wave.execution_time} hours")
                print()

        print("🎯 CRITICAL PATH:")
        for opp_id in plan.critical_path:
            opp = next(opp for opp in plan.opportunities if opp.opportunity_id == opp_id)
            print(f"   {opp.title} (Momentum: {opp.momentum_score:.1f}, ROI: {opp.roi_multiplier:.1f}x)")
        print()

        print("📋 EXECUTION ORDER:")
        for i, opp_id in enumerate(plan.execution_order, 1):
            opp = next(opp for opp in plan.opportunities if opp.opportunity_id == opp_id)
            print(f"   {i}. {opp.title} ({opp.execution_time}h, Momentum: {opp.momentum_score:.1f})")
        print()

        print("⏱️  COMPRESSED TIMELINE:")
        print(f"   Immediate (0-2h): {len(plan.compressed_timeline['immediate'])}")
        print(f"   Short-term (2-4h): {len(plan.compressed_timeline['short_term'])}")
        print(f"   Medium-term (4-8h): {len(plan.compressed_timeline['medium_term'])}")
        print(f"   Parallelizable: {len(plan.compressed_timeline['parallel'])}")
        print()
    else:
        # Default: show summary
        plan = analyzer.create_peak_plan()
        cresting_wave = analyzer.identify_cresting_wave(plan.opportunities)

        print("🌊 CRESTING WAVE:")
        if cresting_wave:
            print(f"   {cresting_wave.title}")
            print(f"   Momentum: {cresting_wave.momentum_score:.1f} | ROI: {cresting_wave.roi_multiplier:.1f}x")
        print()
        print("Use --plan for full analysis")
        print("Use --cresting-wave to identify the cresting wave")
        print()


if __name__ == "__main__":


    main()