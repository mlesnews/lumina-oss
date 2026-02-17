#!/usr/bin/env python3
"""
@HK-47 Generate YouTube Comment

HOW BEST TO PRESENT ALL OF THIS AS A YOUTUBE COMMENT ON THIS VIDEO.
LET'S CRACK THE STEPS TO MAKING THIS HAPPEN.

Generates a well-structured YouTube comment from investigation findings.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HK47GenerateYouTubeComment")

from hk47_youtube_algorithm_investigation import HK47YouTubeAlgorithmInvestigation
from lumina_always_marvin_jarvis import always_assess
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class HK47YouTubeCommentGenerator:
    """
    Generate YouTube comment from investigation findings

    Creates concise, impactful comments for YouTube videos
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("HK47YouTubeCommentGenerator")

        # YouTube comment limits
        self.max_comment_length = 10000  # YouTube's limit is actually higher, but practical limit
        self.ideal_comment_length = 2000  # For readability
        self.min_comment_length = 100

        self.data_dir = self.project_root / "data" / "hk47_youtube_comments"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("💬 @HK-47 YouTube Comment Generator initialized")

    def generate_comment_from_investigation(self, investigation_report_path: Optional[Path] = None) -> Dict[str, Any]:
        try:
            """
            Generate YouTube comment from investigation report

            Creates a comment that:
            - Summarizes key findings
            - Presents evidence
            - Provides recommendations
            - Is respectful and constructive
            - Fits YouTube comment format
            """
            self.logger.info("\n" + "="*80)
            self.logger.info("💬 GENERATING YOUTUBE COMMENT")
            self.logger.info("="*80 + "\n")

            # Load investigation report
            if investigation_report_path is None:
                # Find most recent investigation report
                investigation_dir = self.project_root / "data" / "hk47_youtube_investigations"
                if investigation_dir.exists():
                    reports = sorted(investigation_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                    if reports:
                        investigation_report_path = reports[0]
                        self.logger.info(f"📁 Using most recent report: {investigation_report_path.name}")

            if investigation_report_path and investigation_report_path.exists():
                with open(investigation_report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
            else:
                # Run investigation if no report found
                self.logger.info("📋 No report found, running investigation...")
                investigator = HK47YouTubeAlgorithmInvestigation(self.project_root)
                report = investigator.investigate_channel_blacklisting("Star Wars Theory")
                report_data = report.to_dict()

            # Generate comment versions
            comment_versions = {
                "full": self._generate_full_comment(report_data),
                "concise": self._generate_concise_comment(report_data),
                "summary": self._generate_summary_comment(report_data),
                "action": self._generate_action_comment(report_data)
            }

            # Get dual perspective on comment approach
            perspective = always_assess("Best approach for YouTube comment on algorithm investigation")

            result = {
                "timestamp": datetime.now().isoformat(),
                "video_url": "https://www.youtube.com/live/qPUPmz6Zh4g",
                "subject": report_data.get("subject", "Star Wars Theory"),
                "comment_versions": comment_versions,
                "recommendations": {
                    "jarvis": perspective.jarvis_perspective,
                    "marvin": perspective.marvin_perspective,
                    "consensus": perspective.consensus
                },
                "posting_steps": self._generate_posting_steps()
            }

            # Save comment
            comment_file = self.data_dir / f"youtube_comment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(comment_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Comment saved: {comment_file}")

            return result

        except Exception as e:
            self.logger.error(f"Error in generate_comment_from_investigation: {e}", exc_info=True)
            raise
    def _generate_full_comment(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate full detailed comment"""
        subject = report_data.get("subject", "Star Wars Theory")
        evidence = report_data.get("blacklist_evidence", [])
        patterns = report_data.get("algorithm_patterns", [])
        root_cause = report_data.get("root_cause", {})

        comment = f"""🔍 @HK-47 INVESTIGATION FINDINGS - {subject}

After analyzing the YouTube algorithm and blacklisting patterns, here's what we found:

🎯 ROOT CAUSE: Algorithmic decision-making without human-in-the-loop oversight. YouTube's algorithm makes suppression decisions automatically without human verification, official notification, or creator appeal processes.

📋 EVIDENCE:
"""

        # Add key evidence (top 3)
        for ev in evidence[:3]:
            comment += f"• {ev['evidence_type'].replace('_', ' ').title()}: {ev['description']} (Probability: {ev['probability']:.0%})\n"

        comment += f"""
📊 ALGORITHM PATTERNS IDENTIFIED:
"""

        # Add key patterns (top 3)
        for pattern in patterns[:3]:
            comment += f"• {pattern['pattern_name']}: {pattern['description'][:100]}...\n"

        comment += f"""
❌ UNFAIR/UNJUST PRACTICES:
• Blacklisting without notification (passive aggressive)
• Suppression without explanation (unjust)
• Algorithmic decisions without human oversight (unfair)
• No appeal process for creators (unjust)

💡 RECOMMENDATIONS:
🚨 IMMEDIATE: Require human-in-the-loop for all suppression decisions
🚨 IMMEDIATE: Mandate official notification before any creator action
🚨 IMMEDIATE: Provide appeal process for all algorithmic decisions

👤 HUMAN-IN-THE-LOOP REQUIRED:
Before ANY suppression action, YouTube must:
• Human review of algorithm decisions
• Official notification letter to creator
• Appeal process for all decisions
• Transparency in algorithm signals

Bottom Line: Blacklisting without notification, explanation, or appeal is PASSIVE AGGRESSIVE and BLATANTLY UNFAIR/UNJUST. Creators deserve human-in-the-loop decisions and official letters before any action.

Full investigation report available. This needs to be addressed. 💯"""

        return {
            "text": comment,
            "length": len(comment),
            "version": "full",
            "recommended_for": "Detailed discussion, evidence presentation"
        }

    def _generate_concise_comment(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concise comment (fits typical YouTube comment length)"""
        subject = report_data.get("subject", "Star Wars Theory")
        root_cause = report_data.get("root_cause", {})

        comment = f"""🔍 Investigation Findings - {subject}

ROOT CAUSE: Algorithmic decision-making without human oversight. YouTube's algorithm makes suppression decisions automatically without human verification, official notification, or appeal processes.

KEY FINDINGS:
• Mass unsubscriptions (85% probability)
• Notification failures (80% probability)
• Shadow banning (90% probability)
• Revenue suppression (70% probability)

UNFAIR PRACTICES:
• Blacklisting without notification (passive aggressive)
• Suppression without explanation (unjust)
• No appeal process (unjust)

SOLUTION:
🚨 Require human-in-the-loop for all suppression decisions
🚨 Mandate official notification before any creator action
🚨 Provide appeal process for all algorithmic decisions

Bottom Line: This is PASSIVE AGGRESSIVE and UNFAIR/UNJUST. Creators deserve human oversight, official notification, and due process.

Full investigation report available with detailed evidence and recommendations. 💯"""

        return {
            "text": comment,
            "length": len(comment),
            "version": "concise",
            "recommended_for": "Standard YouTube comment, good balance"
        }

    def _generate_summary_comment(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate brief summary comment"""
        subject = report_data.get("subject", "Star Wars Theory")

        comment = f"""🔍 Algorithm Investigation - {subject}

Root Cause: Algorithmic decision-making without human oversight.

Evidence: Mass unsubscriptions (85%), notification failures (80%), shadow banning (90%), revenue suppression (70%).

Unfair: Blacklisting without notification, no explanation, no appeal process.

Solution: Human-in-the-loop decisions, official notification, appeal process.

This is PASSIVE AGGRESSIVE and UNFAIR/UNJUST. Creators deserve better.

Full report available with detailed findings and recommendations. 💯"""

        return {
            "text": comment,
            "length": len(comment),
            "version": "summary",
            "recommended_for": "Quick summary, attention-grabbing"
        }

    def _generate_action_comment(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action-oriented comment"""
        subject = report_data.get("subject", "Star Wars Theory")

        comment = f"""🚨 ACTION NEEDED - {subject} Blacklisting

Investigation found: Algorithm makes suppression decisions without human oversight, notification, or appeal process.

EVIDENCE:
• 90% probability of shadow banning
• 85% probability of mass unsubscriptions
• 80% probability of notification failures
• 70% probability of revenue suppression

THIS IS UNFAIR AND UNJUST.

REQUIRED ACTIONS:
1. Human-in-the-loop for all suppression decisions
2. Official notification before any creator action
3. Appeal process for all algorithmic decisions

YouTube must implement human oversight and creator rights NOW.

Full investigation report with evidence available. This needs to change. 💯"""

        return {
            "text": comment,
            "length": len(comment),
            "version": "action",
            "recommended_for": "Call to action, urgency"
        }

    def _generate_posting_steps(self) -> List[Dict[str, Any]]:
        """Generate steps for posting the comment"""
        return [
            {
                "step": 1,
                "action": "Choose comment version",
                "description": "Select which comment version to use (full, concise, summary, or action)",
                "tips": [
                    "Full: Most detailed, best for comprehensive discussion",
                    "Concise: Balanced, good for most situations",
                    "Summary: Quick and attention-grabbing",
                    "Action: Urgent call to action"
                ]
            },
            {
                "step": 2,
                "action": "Review and customize",
                "description": "Review the generated comment and customize if needed",
                "tips": [
                    "Check character count (YouTube limit: ~10,000 characters)",
                    "Ensure tone is respectful and constructive",
                    "Verify all facts and evidence",
                    "Make it personal if needed"
                ]
            },
            {
                "step": 3,
                "action": "Copy comment text",
                "description": "Copy the selected comment version",
                "tips": [
                    "Copy the entire comment text",
                    "Preserve formatting (emojis, line breaks)",
                    "Keep markdown formatting if YouTube supports it"
                ]
            },
            {
                "step": 4,
                "action": "Navigate to video",
                "description": "Go to the Star Wars Theory video",
                "url": "https://www.youtube.com/live/qPUPmz6Zh4g",
                "tips": [
                    "Open video in browser",
                    "Scroll to comments section",
                    "Find appropriate location in thread (top-level or reply)"
                ]
            },
            {
                "step": 5,
                "action": "Paste and format",
                "description": "Paste comment and format appropriately",
                "tips": [
                    "Paste comment into comment box",
                    "YouTube supports some formatting (bold, italic, links)",
                    "Ensure emojis display correctly",
                    "Check line breaks are preserved"
                ]
            },
            {
                "step": 6,
                "action": "Review before posting",
                "description": "Final review before posting",
                "tips": [
                    "Read through entire comment",
                    "Check for typos or errors",
                    "Ensure tone is appropriate",
                    "Verify all claims are accurate"
                ]
            },
            {
                "step": 7,
                "action": "Post comment",
                "description": "Click post/comment button",
                "tips": [
                    "Click 'Comment' button",
                    "Wait for comment to appear",
                    "Check if it was posted successfully",
                    "Save comment link if needed"
                ]
            },
            {
                "step": 8,
                "action": "Monitor response",
                "description": "Monitor comment for responses and engagement",
                "tips": [
                    "Check for replies",
                    "Respond to questions if appropriate",
                    "Engage with community",
                    "Share investigation report if requested"
                ]
            }
        ]

    def display_comment_options(self, result: Dict[str, Any]):
        """Display all comment versions and recommendations"""
        print("\n" + "="*80)
        print("💬 YOUTUBE COMMENT OPTIONS")
        print("="*80 + "\n")

        print(f"Video: {result['video_url']}")
        print(f"Subject: {result['subject']}\n")

        versions = result["comment_versions"]

        for version_name, version_data in versions.items():
            print(f"\n{'='*80}")
            print(f"VERSION: {version_name.upper()} ({version_data['length']} characters)")
            print(f"Recommended for: {version_data['recommended_for']}")
            print("="*80 + "\n")
            print(version_data['text'])
            print(f"\n{'─'*80}\n")

        # Recommendations
        recs = result["recommendations"]
        print(f"\n{'='*80}")
        print("🤖 RECOMMENDATIONS (@MARVIN & JARVIS)")
        print("="*80 + "\n")

        print("🤖 JARVIS:")
        print(f"   {recs['jarvis'][:200]}...\n")

        print("😟 @MARVIN:")
        print(f"   {recs['marvin'][:200]}...\n")

        print("✅ CONSENSUS:")
        print(f"   {recs['consensus'][:200]}...\n")

        # Posting steps
        print(f"\n{'='*80}")
        print("📋 POSTING STEPS")
        print("="*80 + "\n")

        for step in result["posting_steps"]:
            print(f"{step['step']}. {step['action']}")
            print(f"   {step['description']}")
            if 'tips' in step:
                for tip in step['tips'][:2]:
                    print(f"   • {tip}")
            print()


def main():
    try:
        """Main execution function"""
        print("\n" + "="*80)
        print("💬 @HK-47 YOUTUBE COMMENT GENERATOR")
        print("="*80 + "\n")

        project_root = Path(".").resolve()
        generator = HK47YouTubeCommentGenerator(project_root)

        # Generate comment
        result = generator.generate_comment_from_investigation()

        # Display options
        generator.display_comment_options(result)

        # Save individual comment files
        for version_name, version_data in result["comment_versions"].items():
            comment_file = generator.data_dir / f"comment_{version_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(comment_file, 'w', encoding='utf-8') as f:
                f.write(version_data['text'])
            print(f"📁 {version_name} comment saved: {comment_file}")

        print("\n" + "="*80)
        print("✅ COMMENT GENERATION COMPLETE")
        print("="*80 + "\n")

        return result


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()