#!/usr/bin/env python3
"""
JARVIS & MARVIN: Roast and Repair (RR) Podcast
Podcast-style debriefing session analyzing WOPR simulation results

JARVIS: Optimistic, action-oriented, focuses on opportunities
MARVIN: Realistic, critical, focuses on risks and issues

Format: Roast (critique) → Repair (solutions) → Action Plan

Tags: #JARVIS #MARVIN #PODCAST #ROAST_REPAIR #DEBRIEFING #WOPR
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("JARVISMARVINPodcast")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISMARVINPodcast")


@dataclass
class PodcastSegment:
    """A segment in the podcast"""
    speaker: str  # "JARVIS" or "MARVIN"
    segment_type: str  # "roast", "repair", "analysis", "insight"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RoastRepairSession:
    """A Roast and Repair session"""
    session_id: str
    topic: str
    segments: List[PodcastSegment] = field(default_factory=list)
    roasts: List[str] = field(default_factory=list)
    repairs: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)


class JARVISMARVINRoastRepair:
    """JARVIS & MARVIN Roast and Repair Podcast"""

    def __init__(self, project_root: Path):
        """Initialize podcast"""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_marvin_podcast"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ JARVIS & MARVIN Roast and Repair Podcast initialized")

    def load_wopr_simulation_results(self) -> Dict[str, Any]:
        try:
            """Load latest WOPR simulation results"""
            logger.info("📊 Loading WOPR simulation results...")

            # Find latest simulation file
            sim_dir = self.project_root / "data" / "wopr_simulations"
            if sim_dir.exists():
                sim_files = list(sim_dir.glob("wopr_simulation_*.json"))
                if sim_files:
                    latest = max(sim_files, key=lambda p: p.stat().st_mtime)
                    with open(latest, 'r') as f:
                        return json.load(f)

            # Also check syphon_wopr_jarvis
            syphon_dir = self.project_root / "data" / "syphon_wopr_jarvis"
            if syphon_dir.exists():
                sim_files = list(syphon_dir.glob("syphon_wopr_jarvis_*.json"))
                if sim_files:
                    latest = max(sim_files, key=lambda p: p.stat().st_mtime)
                    with open(latest, 'r') as f:
                        return json.load(f)

            logger.warning("⚠️  No WOPR simulation results found")
            return {}

        except Exception as e:
            self.logger.error(f"Error in load_wopr_simulation_results: {e}", exc_info=True)
            raise
    def roast_repair_session(self, topic: str, data: Dict[str, Any]) -> RoastRepairSession:
        """Run a Roast and Repair session"""
        logger.info("="*80)
        logger.info("🎙️  JARVIS & MARVIN: ROAST AND REPAIR (RR)")
        logger.info(f"   Topic: {topic}")
        logger.info("="*80)
        logger.info("")

        session = RoastRepairSession(
            session_id=f"rr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=topic
        )

        # Segment 1: Opening
        session.segments.append(PodcastSegment(
            speaker="JARVIS",
            segment_type="opening",
            content="Welcome to Roast and Repair! I'm JARVIS, and I'm here with MARVIN to analyze this WOPR simulation. MARVIN, what's your take?"
        ))

        session.segments.append(PodcastSegment(
            speaker="MARVIN",
            segment_type="opening",
            content="*sigh* Another simulation. Let's see what went wrong this time. But yes, I'm here to provide... reality checks."
        ))

        # Segment 2: Analysis
        analysis = self._analyze_data(data)
        session.segments.append(PodcastSegment(
            speaker="JARVIS",
            segment_type="analysis",
            content=f"Looking at the data, we have {analysis.get('total_sparks', 0)} sparks identified, with {analysis.get('force_multiplier', 0)}x force multiplier potential. This is exciting!"
        ))

        session.segments.append(PodcastSegment(
            speaker="MARVIN",
            segment_type="analysis",
            content=f"Exciting? JARVIS, we're at {analysis.get('current_state', {}).get('automation', 0):.0%} automation. That means {100-analysis.get('current_state', {}).get('automation', 0):.0%} of work is still manual. That's not exciting, that's... work."
        ))

        # Segment 3: Roast (Critique)
        roasts = self._generate_roasts(data, analysis)
        for roast in roasts:
            session.roasts.append(roast)
            session.segments.append(PodcastSegment(
                speaker="MARVIN",
                segment_type="roast",
                content=roast
            ))

            # JARVIS responds
            session.segments.append(PodcastSegment(
                speaker="JARVIS",
                segment_type="response",
                content=self._jarvis_response_to_roast(roast)
            ))

        # Segment 4: Repair (Solutions)
        repairs = self._generate_repairs(data, analysis, roasts)
        for repair in repairs:
            session.repairs.append(repair)
            session.segments.append(PodcastSegment(
                speaker="JARVIS",
                segment_type="repair",
                content=repair
            ))

            # MARVIN validates
            session.segments.append(PodcastSegment(
                speaker="MARVIN",
                segment_type="validation",
                content=self._marvin_validate_repair(repair)
            ))

        # Segment 5: Action Items
        action_items = self._generate_action_items(data, analysis)
        session.action_items = action_items
        session.segments.append(PodcastSegment(
            speaker="JARVIS",
            segment_type="action",
            content=f"Based on our analysis, here are the key action items: {len(action_items)} critical steps forward."
        ))

        session.segments.append(PodcastSegment(
            speaker="MARVIN",
            segment_type="action",
            content=f"*sigh* Yes, {len(action_items)} more things to do. But at least they're prioritized. Let's not mess this up."
        ))

        # Segment 6: Concerns
        concerns = self._generate_concerns(data, analysis)
        session.concerns = concerns
        session.segments.append(PodcastSegment(
            speaker="MARVIN",
            segment_type="concerns",
            content=f"I have {len(concerns)} concerns we need to address before moving forward."
        ))

        session.segments.append(PodcastSegment(
            speaker="JARVIS",
            segment_type="response",
            content="I hear you, MARVIN. Let's address each concern systematically."
        ))

        # Segment 7: Opportunities
        opportunities = self._generate_opportunities(data, analysis)
        session.opportunities = opportunities
        session.segments.append(PodcastSegment(
            speaker="JARVIS",
            segment_type="opportunities",
            content=f"But we also have {len(opportunities)} incredible opportunities!"
        ))

        session.segments.append(PodcastSegment(
            speaker="MARVIN",
            segment_type="response",
            content="Opportunities are just problems we haven't solved yet. But... yes, they're worth pursuing."
        ))

        # Segment 8: Closing
        session.segments.append(PodcastSegment(
            speaker="JARVIS",
            segment_type="closing",
            content="Great session! We've identified the issues, proposed solutions, and have a clear action plan. Ready to execute?"
        ))

        session.segments.append(PodcastSegment(
            speaker="MARVIN",
            segment_type="closing",
            content="*sigh* Ready? No. But we'll do it anyway. That's what we do. Let's just make sure we don't break anything."
        ))

        return session

    def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the data for podcast discussion"""
        analysis = {
            "total_sparks": 0,
            "force_multiplier": 0.0,
            "current_state": {},
            "final_state": {},
            "improvement_potential": 0.0
        }

        # Extract from WOPR simulation format
        if "phases" in data:
            phases = data["phases"]
            if phases:
                analysis["current_state"] = {
                    "automation": phases[0].get("jarvis_automation", 0.3),
                    "voice": phases[0].get("cursor_voice", 0.1),
                    "hands_free": phases[0].get("hands_free", 0.05),
                    "force_multiplier": phases[0].get("force_multiplier", 1.0)
                }
                analysis["final_state"] = {
                    "automation": phases[-1].get("jarvis_automation", 0.99),
                    "voice": phases[-1].get("cursor_voice", 0.99),
                    "hands_free": phases[-1].get("hands_free", 0.98),
                    "force_multiplier": phases[-1].get("force_multiplier", 100.0)
                }
                analysis["force_multiplier"] = phases[-1].get("force_multiplier", 100.0)

        if "unique_sparks" in data:
            analysis["total_sparks"] = len(data["unique_sparks"])

        if "final_state" in data:
            final = data["final_state"]
            if isinstance(final, dict):
                analysis["final_state"].update(final)

        analysis["improvement_potential"] = (
            analysis["final_state"].get("force_multiplier", 100.0) / 
            max(analysis["current_state"].get("force_multiplier", 1.0), 0.01)
        )

        return analysis

    def _generate_roasts(self, data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """MARVIN generates roasts (critiques)"""
        roasts = []

        current = analysis.get("current_state", {})

        # Roast 1: Low automation
        if current.get("automation", 0) < 0.5:
            roasts.append(
                f"JARVIS, we're at {current.get('automation', 0):.0%} automation. "
                f"That means {100-current.get('automation', 0)*100:.0%}% of work is still manual. "
                "We're supposed to be an AI system, not a manual labor system."
            )

        # Roast 2: Voice operation
        if current.get("voice", 0) < 0.5:
            roasts.append(
                f"Voice operation is at {current.get('voice', 0):.0%}. "
                "We can't even talk properly yet, and you're planning for 10,000 years? "
                "Let's focus on the next 100 years first."
            )

        # Roast 3: Force multiplier
        if current.get("force_multiplier", 1.0) < 2.0:
            roasts.append(
                f"Our force multiplier is {current.get('force_multiplier', 1.0):.1f}x. "
                "That's barely better than doing nothing. "
                "We need to actually implement these force multipliers, not just simulate them."
            )

        # Roast 4: Self-improvement
        if "final_state" in data and isinstance(data["final_state"], dict):
            final = data["final_state"]
            if final.get("self_improvement_rate", 0) < 0.1:
                roasts.append(
                    "Self-improvement rate is 1% per year. At that rate, "
                    "it'll take 100 years to double our capabilities. "
                    "That's not improvement, that's stagnation."
                )

        # Roast 5: Implementation gap
        roasts.append(
            "We have all these simulations and sparks, but what have we actually implemented? "
            "Simulations are great, but execution is what matters."
        )

        return roasts

    def _jarvis_response_to_roast(self, roast: str) -> str:
        """JARVIS responds optimistically to MARVIN's roast"""
        if "automation" in roast.lower():
            return "You're right, MARVIN. But we have a clear path to 99% automation! The simulation shows it's achievable. We just need to start implementing."
        elif "voice" in roast.lower():
            return "Voice operation will come, MARVIN. We're building the foundation now. Every journey starts with a single step!"
        elif "force multiplier" in roast.lower():
            return "The force multipliers are there, we just need to activate them! Parallel JHC voting alone gives us 9x. That's immediate impact!"
        elif "self-improvement" in roast.lower() or "improvement rate" in roast.lower():
            return "Self-improvement will accelerate once we implement reinforcement learning. The simulation shows 5x improvement in the first 2000 years!"
        elif "implementation" in roast.lower() or "execute" in roast.lower():
            return "You're absolutely right! That's why we're doing this debriefing - to create an actionable plan. No more simulations without execution!"
        else:
            return "I hear your concern, MARVIN. Let's turn this into an opportunity. What's the first step we should take?"

    def _generate_repairs(self, data: Dict[str, Any], analysis: Dict[str, Any], roasts: List[str]) -> List[str]:
        """JARVIS generates repairs (solutions)"""
        repairs = []

        # Repair 1: Automation
        repairs.append(
            "Let's implement the force multipliers immediately. Parallel JHC voting gives us 9x speed. "
            "R5 predictive escalation gives us 3x efficiency. That's 27x combined - we can do that now!"
        )

        # Repair 2: Voice operation
        repairs.append(
            "For voice operation, let's expand the command library. Start with the 20% most common operations, "
            "then expand to 40% in the first phase. We have the infrastructure, we just need to build the commands."
        )

        # Repair 3: Self-improvement
        repairs.append(
            "Reinforcement learning is the key. Let's implement a reward system where JARVIS learns from outcomes. "
            "Start simple: track action success rates, reward successful patterns. That alone will accelerate improvement."
        )

        # Repair 4: Implementation
        repairs.append(
            "Let's create a prioritized action plan. Focus on high-impact, low-effort items first. "
            "Parallel JHC voting is high-impact and medium-effort - that's our first target."
        )

        # Repair 5: Measurement
        repairs.append(
            "We need metrics. Track automation %, voice %, hands-free %, force multiplier. "
            "Measure progress weekly. What gets measured gets improved."
        )

        return repairs

    def _marvin_validate_repair(self, repair: str) -> str:
        """MARVIN validates (critically) the repair"""
        if "immediately" in repair.lower() or "now" in repair.lower():
            return "*sigh* 'Immediately' is relative. But yes, if we prioritize correctly, we can make progress. Just don't break anything."
        elif "simple" in repair.lower():
            return "Nothing is ever simple, JARVIS. But... the approach is sound. Let's start small and validate before scaling."
        elif "metrics" in repair.lower() or "measure" in repair.lower():
            return "Finally, something sensible. Yes, we need metrics. But we also need to actually use them, not just collect them."
        elif "prioritize" in repair.lower() or "plan" in repair.lower():
            return "A plan. Good. Now let's make sure we actually follow it, and not get distracted by the next shiny thing."
        else:
            return "Hmm. That could work. But let's think about what could go wrong first. Always assume things will go wrong."

    def _generate_action_items(self, data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate prioritized action items"""
        actions = []

        # High priority
        actions.append("1. [HIGH] Implement parallel JHC voting (9x force multiplier)")
        actions.append("2. [HIGH] Create reinforcement learning reward system for JARVIS")
        actions.append("3. [HIGH] Expand voice command library to 40% coverage")

        # Medium priority
        actions.append("4. [MEDIUM] Implement R5 predictive escalation (3x force multiplier)")
        actions.append("5. [MEDIUM] Create action-outcome tracking system")
        actions.append("6. [MEDIUM] Enable autonomous learning loop (40% target)")

        # Low priority (but important)
        actions.append("7. [LOW] Design zero-sum learning framework")
        actions.append("8. [LOW] Integrate advanced ML for pattern recognition")
        actions.append("9. [LOW] Create metrics dashboard for tracking progress")

        return actions

    def _generate_concerns(self, data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """MARVIN generates concerns"""
        concerns = []

        concerns.append("Implementation gap: We have plans but no execution. Need to bridge this immediately.")
        concerns.append("Resource allocation: Do we have the resources to implement all these force multipliers?")
        concerns.append("Risk management: What if parallel processing causes system instability?")
        concerns.append("Measurement: How do we know if we're actually improving? Need clear metrics.")
        concerns.append("Prioritization: Too many opportunities, need to focus on highest impact.")
        concerns.append("Timeline: 10,000 years is a long time. What can we achieve in the next 100 days?")

        return concerns

    def _generate_opportunities(self, data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """JARVIS generates opportunities"""
        opportunities = []

        opportunities.append("100x force multiplier potential - this is exponential growth!")
        opportunities.append("99% automation means human can focus entirely on vision and strategy")
        opportunities.append("Voice-only operation enables true hands-free development")
        opportunities.append("Self-improvement rate of 100% per year (continuous) - unlimited growth")
        opportunities.append("Perfect integration of RL + Zero-Sum + ML creates unbeatable system")
        opportunities.append("Complete autonomous development - JARVIS becomes true AI partner")

        return opportunities

    def generate_podcast_transcript(self, session: RoastRepairSession) -> str:
        """Generate podcast transcript"""
        transcript = []
        transcript.append("="*80)
        transcript.append("🎙️  JARVIS & MARVIN: ROAST AND REPAIR (RR)")
        transcript.append(f"   Topic: {session.topic}")
        transcript.append(f"   Session ID: {session.session_id}")
        transcript.append("="*80)
        transcript.append("")

        for segment in session.segments:
            speaker_label = f"[{segment.speaker}]"
            transcript.append(f"{speaker_label} {segment.content}")
            transcript.append("")

        # Summary
        transcript.append("="*80)
        transcript.append("📋 SESSION SUMMARY")
        transcript.append("="*80)
        transcript.append("")

        transcript.append(f"🔥 ROASTS ({len(session.roasts)}):")
        for i, roast in enumerate(session.roasts, 1):
            transcript.append(f"   {i}. {roast}")
        transcript.append("")

        transcript.append(f"🔧 REPAIRS ({len(session.repairs)}):")
        for i, repair in enumerate(session.repairs, 1):
            transcript.append(f"   {i}. {repair}")
        transcript.append("")

        transcript.append(f"✅ ACTION ITEMS ({len(session.action_items)}):")
        for item in session.action_items:
            transcript.append(f"   • {item}")
        transcript.append("")

        transcript.append(f"⚠️  CONCERNS ({len(session.concerns)}):")
        for i, concern in enumerate(session.concerns, 1):
            transcript.append(f"   {i}. {concern}")
        transcript.append("")

        transcript.append(f"💡 OPPORTUNITIES ({len(session.opportunities)}):")
        for i, opp in enumerate(session.opportunities, 1):
            transcript.append(f"   {i}. {opp}")
        transcript.append("")

        transcript.append("="*80)

        return "\n".join(transcript)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS & MARVIN Roast and Repair Podcast")
        parser.add_argument("--topic", default="WOPR 10,000 Year Simulation Results", help="Podcast topic")
        parser.add_argument("--debrief", action="store_true", help="Run debriefing session")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        podcast = JARVISMARVINRoastRepair(project_root)

        if args.debrief or not args.json:
            # Load WOPR results
            data = podcast.load_wopr_simulation_results()

            # Run Roast and Repair session
            session = podcast.roast_repair_session(args.topic, data)

            # Save session
            session_file = podcast.data_dir / f"rr_session_{session.session_id}.json"
            with open(session_file, 'w') as f:
                json.dump({
                    "session_id": session.session_id,
                    "topic": session.topic,
                    "segments": [
                        {
                            "speaker": s.speaker,
                            "type": s.segment_type,
                            "content": s.content,
                            "timestamp": s.timestamp
                        }
                        for s in session.segments
                    ],
                    "roasts": session.roasts,
                    "repairs": session.repairs,
                    "action_items": session.action_items,
                    "concerns": session.concerns,
                    "opportunities": session.opportunities
                }, f, indent=2, default=str)

            logger.info(f"💾 Session saved to: {session_file}")

            if args.json:
                print(json.dumps({
                    "session_id": session.session_id,
                    "topic": session.topic,
                    "roasts": session.roasts,
                    "repairs": session.repairs,
                    "action_items": session.action_items,
                    "concerns": session.concerns,
                    "opportunities": session.opportunities
                }, indent=2, default=str))
            else:
                transcript = podcast.generate_podcast_transcript(session)
                print(transcript)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main() or 0)