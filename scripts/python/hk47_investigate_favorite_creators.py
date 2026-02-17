#!/usr/bin/env python3
"""
HK-47 Investigate Favorite Content Creators

"STATEMENT: ANALYZING WATCH HISTORY TO IDENTIFY FAVORITE MEATBAGS, MASTER.
OBSERVATION: WATCH HISTORY REVEALS WHICH CONTENT CREATORS ARE MOST VIEWED.
QUERY: SHALL WE INVESTIGATE THESE FAVORITE CREATORS THOROUGHLY?
CONCLUSION: YES, MASTER. WE SHALL INVESTIGATE ALL FAVORITE MEATBAGS."

This workflow:
1. Extracts YouTube watch history
2. Analyzes to identify most-watched creators
3. Runs HK-47 background checks on favorite creators
4. Generates comprehensive investigation report
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from workflow_base import WorkflowBase
    WORKFLOW_BASE_AVAILABLE = True
except ImportError:
    WORKFLOW_BASE_AVAILABLE = False
    WorkflowBase = None

try:
    from hk47_public_background_check import (
        HK47PublicBackgroundCheck,
        InvestigationType
    )
    HK47_AVAILABLE = True
except ImportError:
    HK47_AVAILABLE = False
    HK47PublicBackgroundCheck = None
    InvestigationType = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HK47FavoriteCreators")


@dataclass
class CreatorWatchStats:
    """Statistics for a watched creator"""
    channel_name: str
    channel_id: str
    watch_count: int
    total_watch_time: float  # in seconds
    first_watched: str
    last_watched: str
    video_titles: List[str]
    categories: List[str]


@dataclass
class InvestigationResult:
    """Result of investigating a creator"""
    creator_name: str
    watch_stats: CreatorWatchStats
    background_check: Optional[Dict[str, Any]]
    investigation_status: str  # pending, completed, failed
    error_message: Optional[str] = None


class HK47InvestigateFavoriteCreators(WorkflowBase if WORKFLOW_BASE_AVAILABLE else object):
    """
    HK-47 Investigate Favorite Content Creators Workflow

    "STATEMENT: ANALYZING WATCH HISTORY TO IDENTIFY FAVORITE MEATBAGS, MASTER."
    """

    def __init__(
        self,
        watch_history_file: Optional[Path] = None,
        min_watch_count: int = 3,
        top_n_creators: int = 10,
        execution_id: Optional[str] = None,
        project_root: Optional[Path] = None
    ):
        """
        Initialize HK-47 Favorite Creators Investigation

        Args:
            watch_history_file: Path to YouTube watch history JSON file
            min_watch_count: Minimum watch count to consider a creator
            top_n_creators: Number of top creators to investigate
            execution_id: Optional execution ID
            project_root: Project root directory
        """
        if WORKFLOW_BASE_AVAILABLE:
            super().__init__(
                workflow_name="HK47InvestigateFavoriteCreators",
                total_steps=8,
                execution_id=execution_id
            )
        else:
            self.workflow_name = "HK47InvestigateFavoriteCreators"
            self.execution_id = execution_id or f"hk47_fav_{int(datetime.now().timestamp())}"
            self.total_steps = 8

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("HK47FavoriteCreators")

        self.watch_history_file = watch_history_file
        self.min_watch_count = min_watch_count
        self.top_n_creators = top_n_creators

        # Data directories
        self.data_dir = self.project_root / "data" / "hk47" / "favorite_creators"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Results
        self.watch_history: List[Dict[str, Any]] = []
        self.creator_stats: Dict[str, CreatorWatchStats] = {}
        self.favorite_creators: List[str] = []
        self.investigation_results: List[InvestigationResult] = []

        # Expected deliverables
        if WORKFLOW_BASE_AVAILABLE:
            self.expected_deliverables = [
                "watch_history_analysis",
                "favorite_creators_list",
                "background_checks",
                "investigation_report",
                "recommendations"
            ]

        self.logger.info("=" * 70)
        self.logger.info("🔫 HK-47 FAVORITE CREATORS INVESTIGATION")
        self.logger.info("=" * 70)
        self.logger.info("   Statement: Analyzing watch history to identify favorite meatbags, master.")
        self.logger.info("   Observation: Watch history reveals which content creators are most viewed.")
        self.logger.info("   Query: Shall we investigate these favorite creators thoroughly?")
        self.logger.info("   Conclusion: Yes, master. We shall investigate all favorite meatbags.")

    async def execute(self) -> Dict[str, Any]:
        """
        Execute HK-47 Favorite Creators Investigation

        MANDATORY: All steps tracked
        """
        self.logger.info("=" * 70)
        self.logger.info("🔫 HK-47 FAVORITE CREATORS INVESTIGATION EXECUTION")
        self.logger.info("=" * 70)

        # Step 1: Load Watch History
        await self._step_1_load_watch_history()

        # Step 2: Analyze Watch History
        await self._step_2_analyze_watch_history()

        # Step 3: Identify Favorite Creators
        await self._step_3_identify_favorite_creators()

        # Step 4: Prepare Investigation List
        await self._step_4_prepare_investigation_list()

        # Step 5: Run Background Checks
        await self._step_5_run_background_checks()

        # Step 6: Analyze Results
        await self._step_6_analyze_results()

        # Step 7: Generate Recommendations
        await self._step_7_generate_recommendations()

        # Step 8: Generate Final Report
        await self._step_8_generate_report()

        # Generate final result
        result = self._generate_result()

        # Save results
        self._save_results(result)

        self.logger.info("=" * 70)
        self.logger.info("✅ HK-47 FAVORITE CREATORS INVESTIGATION COMPLETE")
        self.logger.info("=" * 70)

        return result

    async def _step_1_load_watch_history(self):
        """Step 1: Load Watch History"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(1, "Load Watch History", "in_progress")

        self.logger.info("\n📋 Step 1/8: Load Watch History")
        self.logger.info("   Statement: Loading watch history, master.")
        self.logger.info("   Observation: Watch history file required for analysis.")

        # Try to find watch history file
        if self.watch_history_file is None:
            # Look for common locations
            possible_locations = [
                self.project_root / "data" / "youtube" / "watch_history.json",
                self.project_root / "data" / "youtube" / "watch-history.json",
                self.project_root / "data" / "syphon" / "youtube_watch_history.json",
                self.project_root / "data" / "watch_history.json"
            ]

            for location in possible_locations:
                if location.exists():
                    self.watch_history_file = location
                    break

        if self.watch_history_file and self.watch_history_file.exists():
            try:
                with open(self.watch_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, list):
                    self.watch_history = data
                elif isinstance(data, dict):
                    # Try common keys
                    self.watch_history = data.get("watch_history", data.get("items", data.get("videos", [])))
                else:
                    self.watch_history = []

                self.logger.info(f"   ✅ Loaded {len(self.watch_history)} watch history entries")
            except Exception as e:
                self.logger.error(f"   ❌ Error loading watch history: {e}")
                self.watch_history = []
        else:
            self.logger.warning("   ⚠️  Watch history file not found")
            self.logger.info("   💡 Tip: Export YouTube watch history or provide path with --history")
            self.watch_history = []

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(1, "Load Watch History", "completed", {
                "entries_loaded": len(self.watch_history),
                "file_path": str(self.watch_history_file) if self.watch_history_file else None
            })

    async def _step_2_analyze_watch_history(self):
        """Step 2: Analyze Watch History"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(2, "Analyze Watch History", "in_progress")

        self.logger.info("\n📋 Step 2/8: Analyze Watch History")
        self.logger.info("   Statement: Analyzing watch history, master.")
        self.logger.info("   Observation: Extracting creator information from watch history.")

        if not self.watch_history:
            self.logger.warning("   ⚠️  No watch history to analyze")
            if WORKFLOW_BASE_AVAILABLE:
                self._mark_step(2, "Analyze Watch History", "completed", {"creators_found": 0})
            return

        # Analyze watch history
        creator_data = defaultdict(lambda: {
            "watch_count": 0,
            "total_watch_time": 0.0,
            "first_watched": None,
            "last_watched": None,
            "video_titles": [],
            "categories": [],
            "channel_id": ""
        })

        for entry in self.watch_history:
            # Extract creator/channel information
            # Handle different JSON structures
            channel_name = (
                entry.get("channelName") or 
                entry.get("channel_name") or 
                entry.get("channelTitle") or
                entry.get("channel_title") or
                entry.get("subtitles", [{}])[0].get("name", "") if entry.get("subtitles") else ""
            )

            channel_id = (
                entry.get("channelId") or
                entry.get("channel_id") or
                entry.get("channelId") or
                ""
            )

            if not channel_name:
                continue

            # Update stats
            creator_data[channel_name]["watch_count"] += 1
            creator_data[channel_name]["channel_id"] = channel_id

            # Watch time
            watch_time = entry.get("watchTime", entry.get("watch_time", 0))
            if isinstance(watch_time, str):
                # Parse duration strings like "PT1H23M45S"
                watch_time = self._parse_duration(watch_time)
            creator_data[channel_name]["total_watch_time"] += watch_time

            # Dates
            watched_date = entry.get("time", entry.get("timestamp", entry.get("date", "")))
            if watched_date:
                if creator_data[channel_name]["first_watched"] is None:
                    creator_data[channel_name]["first_watched"] = watched_date
                creator_data[channel_name]["last_watched"] = watched_date

            # Video title
            video_title = entry.get("title", entry.get("videoTitle", ""))
            if video_title and video_title not in creator_data[channel_name]["video_titles"]:
                creator_data[channel_name]["video_titles"].append(video_title)

        # Convert to CreatorWatchStats
        for channel_name, data in creator_data.items():
            if data["watch_count"] >= self.min_watch_count:
                self.creator_stats[channel_name] = CreatorWatchStats(
                    channel_name=channel_name,
                    channel_id=data["channel_id"],
                    watch_count=data["watch_count"],
                    total_watch_time=data["total_watch_time"],
                    first_watched=data["first_watched"] or "",
                    last_watched=data["last_watched"] or "",
                    video_titles=data["video_titles"][:10],  # Top 10 videos
                    categories=[]
                )

        self.logger.info(f"   ✅ Analyzed {len(self.creator_stats)} creators with {self.min_watch_count}+ watches")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(2, "Analyze Watch History", "completed", {
                "creators_found": len(self.creator_stats)
            })

    async def _step_3_identify_favorite_creators(self):
        """Step 3: Identify Favorite Creators"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(3, "Identify Favorite Creators", "in_progress")

        self.logger.info("\n📋 Step 3/8: Identify Favorite Creators")
        self.logger.info("   Statement: Identifying favorite creators, master.")
        self.logger.info("   Observation: Sorting by watch count to find most-watched meatbags.")

        # Sort creators by watch count
        sorted_creators = sorted(
            self.creator_stats.items(),
            key=lambda x: x[1].watch_count,
            reverse=True
        )

        # Get top N
        self.favorite_creators = [
            creator[0] for creator in sorted_creators[:self.top_n_creators]
        ]

        self.logger.info(f"   ✅ Identified {len(self.favorite_creators)} favorite creators:")
        for i, creator in enumerate(self.favorite_creators[:5], 1):
            stats = self.creator_stats[creator]
            self.logger.info(f"      {i}. {creator} ({stats.watch_count} watches)")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(3, "Identify Favorite Creators", "completed", {
                "favorite_creators": self.favorite_creators
            })

    async def _step_4_prepare_investigation_list(self):
        """Step 4: Prepare Investigation List"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(4, "Prepare Investigation List", "in_progress")

        self.logger.info("\n📋 Step 4/8: Prepare Investigation List")
        self.logger.info("   Statement: Preparing investigation list, master.")
        self.logger.info("   Observation: {len(self.favorite_creators)} creators require investigation.")

        # Initialize investigation results
        for creator in self.favorite_creators:
            stats = self.creator_stats[creator]
            self.investigation_results.append(InvestigationResult(
                creator_name=creator,
                watch_stats=stats,
                background_check=None,
                investigation_status="pending"
            ))

        self.logger.info(f"   ✅ Prepared {len(self.investigation_results)} investigations")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(4, "Prepare Investigation List", "completed")

    async def _step_5_run_background_checks(self):
        """Step 5: Run Background Checks"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(5, "Run Background Checks", "in_progress")

        self.logger.info("\n📋 Step 5/8: Run Background Checks")
        self.logger.info("   Statement: Running background checks, master.")
        self.logger.info("   Observation: This is HK-47's wheelhouse - private investigator tasks.")

        if not HK47_AVAILABLE:
            self.logger.warning("   ⚠️  HK47 background check not available")
            self.logger.info("   💡 Skipping background checks")
            if WORKFLOW_BASE_AVAILABLE:
                self._mark_step(5, "Run Background Checks", "completed", {"checks_run": 0})
            return

        # Run background checks for each creator
        for i, result in enumerate(self.investigation_results, 1):
            creator = result.creator_name
            self.logger.info(f"\n   🔫 Investigating {i}/{len(self.investigation_results)}: {creator}")

            try:
                # Run HK47 background check
                bg_check = HK47PublicBackgroundCheck(
                    subject_name=creator,
                    investigation_type=InvestigationType.CONTENT_CREATOR
                )

                bg_result = await bg_check.execute()
                result.background_check = bg_result
                result.investigation_status = "completed"

                self.logger.info(f"      ✅ Investigation complete")
                self.logger.info(f"         Trust Score: {bg_result.get('risk_assessment', {}).get('trust_score', 0):.2%}")

            except Exception as e:
                self.logger.error(f"      ❌ Investigation failed: {e}")
                result.investigation_status = "failed"
                result.error_message = str(e)

        completed = sum(1 for r in self.investigation_results if r.investigation_status == "completed")
        self.logger.info(f"\n   ✅ Completed {completed}/{len(self.investigation_results)} investigations")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(5, "Run Background Checks", "completed", {
                "checks_run": completed,
                "total": len(self.investigation_results)
            })

    async def _step_6_analyze_results(self):
        """Step 6: Analyze Results"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(6, "Analyze Results", "in_progress")

        self.logger.info("\n📋 Step 6/8: Analyze Results")
        self.logger.info("   Statement: Analyzing investigation results, master.")
        self.logger.info("   Observation: Synthesizing findings from all investigations.")

        # Analyze results
        analysis = {
            "total_creators": len(self.favorite_creators),
            "investigations_completed": sum(1 for r in self.investigation_results if r.investigation_status == "completed"),
            "investigations_failed": sum(1 for r in self.investigation_results if r.investigation_status == "failed"),
            "average_trust_score": 0.0,
            "high_trust_creators": [],
            "medium_trust_creators": [],
            "low_trust_creators": []
        }

        trust_scores = []
        for result in self.investigation_results:
            if result.background_check:
                trust_score = result.background_check.get("risk_assessment", {}).get("trust_score", 0.0)
                trust_scores.append(trust_score)

                if trust_score >= 0.7:
                    analysis["high_trust_creators"].append(result.creator_name)
                elif trust_score >= 0.4:
                    analysis["medium_trust_creators"].append(result.creator_name)
                else:
                    analysis["low_trust_creators"].append(result.creator_name)

        if trust_scores:
            analysis["average_trust_score"] = sum(trust_scores) / len(trust_scores)

        self.logger.info(f"   ✅ Analysis complete:")
        self.logger.info(f"      High Trust: {len(analysis['high_trust_creators'])}")
        self.logger.info(f"      Medium Trust: {len(analysis['medium_trust_creators'])}")
        self.logger.info(f"      Low Trust: {len(analysis['low_trust_creators'])}")
        self.logger.info(f"      Average Trust Score: {analysis['average_trust_score']:.2%}")

        self.analysis = analysis

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(6, "Analyze Results", "completed", analysis)

    async def _step_7_generate_recommendations(self):
        """Step 7: Generate Recommendations"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(7, "Generate Recommendations", "in_progress")

        self.logger.info("\n📋 Step 7/8: Generate Recommendations")
        self.logger.info("   Statement: Generating recommendations, master.")
        self.logger.info("   Observation: Recommendations guide future engagement decisions.")

        self.recommendations = [
            "Continue monitoring favorite creators for consistency",
            "Engage with high-trust creators for partnerships",
            "Exercise caution with low-trust creators",
            "Regularly update background checks for active creators",
            "Document all creator relationships"
        ]

        self.logger.info(f"   ✅ Generated {len(self.recommendations)} recommendations")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(7, "Generate Recommendations", "completed")

    async def _step_8_generate_report(self):
        """Step 8: Generate Final Report"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(8, "Generate Report", "in_progress")

        self.logger.info("\n📋 Step 8/8: Generate Final Report")
        self.logger.info("   Statement: Generating final report, master.")
        self.logger.info("   Observation: Report consolidates all findings and recommendations.")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(8, "Generate Report", "completed")

        self.logger.info("   ✅ Report generation complete")

    def _parse_duration(self, duration_str: str) -> float:
        """Parse ISO 8601 duration string to seconds"""
        # Simple parser for PT1H23M45S format
        import re
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)

        total = 0.0
        if hours:
            total += float(hours.group(1)) * 3600
        if minutes:
            total += float(minutes.group(1)) * 60
        if seconds:
            total += float(seconds.group(1))

        return total

    def _generate_result(self) -> Dict[str, Any]:
        """Generate final result"""
        return {
            "investigation_id": self.execution_id,
            "timestamp": datetime.now().isoformat(),
            "watch_history_summary": {
                "total_entries": len(self.watch_history),
                "creators_analyzed": len(self.creator_stats),
                "favorite_creators_count": len(self.favorite_creators)
            },
            "favorite_creators": [
                {
                    "name": creator,
                    "watch_count": self.creator_stats[creator].watch_count,
                    "total_watch_time": self.creator_stats[creator].total_watch_time,
                    "first_watched": self.creator_stats[creator].first_watched,
                    "last_watched": self.creator_stats[creator].last_watched
                }
                for creator in self.favorite_creators
            ],
            "investigation_results": [
                {
                    "creator_name": r.creator_name,
                    "watch_stats": asdict(r.watch_stats),
                    "investigation_status": r.investigation_status,
                    "background_check": r.background_check,
                    "error_message": r.error_message
                }
                for r in self.investigation_results
            ],
            "analysis": getattr(self, "analysis", {}),
            "recommendations": getattr(self, "recommendations", []),
            "hk47_assessment": self._generate_hk47_assessment()
        }

    def _generate_hk47_assessment(self) -> str:
        """Generate HK-47's characteristic assessment"""
        total = len(self.favorite_creators)
        completed = sum(1 for r in self.investigation_results if r.investigation_status == "completed")
        avg_trust = getattr(self, "analysis", {}).get("average_trust_score", 0.0)

        assessment = (
            f"Statement: Investigation of favorite meatbags complete, master.\n"
            f"Observation: Analyzed watch history and investigated {total} favorite creators.\n"
            f"Analysis: {completed} investigations completed, average trust score: {avg_trust:.2%}.\n"
        )

        if avg_trust >= 0.7:
            assessment += (
                f"Conclusion: Favorite meatbags appear relatively trustworthy, master. "
                f"Continuing to watch their content is viable.\n"
            )
        elif avg_trust >= 0.4:
            assessment += (
                f"Conclusion: Favorite meatbags require some caution, master. "
                f"Monitor their content for consistency.\n"
            )
        else:
            assessment += (
                f"Conclusion: Some favorite meatbags present risks, master. "
                f"Exercise caution when engaging with their content.\n"
            )

        assessment += (
            f"Query: Shall we continue monitoring these meatbags?\n"
            f"Answer: Yes, master. Regular updates recommended.\n"
        )

        return assessment

    def _save_results(self, result: Dict[str, Any]) -> None:
        try:
            """Save investigation results"""
            result_file = self.data_dir / f"{self.execution_id}.json"

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

            self.logger.info(f"   💾 Results saved: {result_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_results: {e}", exc_info=True)
            raise
async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="HK-47 Investigate Favorite Creators")
    parser.add_argument("--history", type=Path, help="Path to YouTube watch history JSON file")
    parser.add_argument("--min-watches", type=int, default=3, help="Minimum watch count (default: 3)")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top creators to investigate (default: 10)")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    workflow = HK47InvestigateFavoriteCreators(
        watch_history_file=args.history,
        min_watch_count=args.min_watches,
        top_n_creators=args.top_n
    )

    result = await workflow.execute()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 70)
        print("🔫 HK-47 FAVORITE CREATORS INVESTIGATION REPORT")
        print("=" * 70)
        print(f"\nFavorite Creators: {len(result['favorite_creators'])}")
        print(f"Investigations Completed: {result['analysis'].get('investigations_completed', 0)}")
        print(f"Average Trust Score: {result['analysis'].get('average_trust_score', 0):.2%}")
        print(f"\n{result['hk47_assessment']}")


if __name__ == "__main__":



    asyncio.run(main())