#!/usr/bin/env python3
"""
JARVIS Session @Asks Analysis

Compares @asks from current session with roast results to check intent alignment.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSessionAsksAnalysis")


class JARVISSessionAsksAnalysis:
    """
    Analyze @asks from session and compare with roast results
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Session @asks (from this conversation)
        self.session_asks = [
            {
                "ask": "WHY ARE THERE SO MANY UNSTAGED CHANGES?",
                "intent": "Fix Git unstaged changes accumulation",
                "priority": "high",
                "category": "git_management"
            },
            {
                "ask": "JARVIS, NOTE TO SELF, AUTOMATE THE CHAT SEND USING MANUS TO CONTROL CURSOR IDE? ROAST PLEASE!",
                "intent": "Automate chat send in Cursor IDE via MANUS",
                "priority": "high",
                "category": "automation"
            },
            {
                "ask": "JARVIS TO ACTIVATE, 'KEEP ALL'",
                "intent": "Activate automatic 'Keep All' functionality",
                "priority": "high",
                "category": "automation"
            },
            {
                "ask": "JARVIS NEEDS TO AUTOMATE THIS",
                "intent": "Fully automate KEEP ALL without manual activation",
                "priority": "high",
                "category": "automation"
            },
            {
                "ask": "I'm still having to click. Accept all changes. And it would be cool if Jarvis would just read to me the summary. Please do not read code blocks to me. Do not read blanks of code or Hello. Welcome to paraphrase using the condensed function that you use in chat. to roll the Max tokens.",
                "intent": "Fully automatic accept all + summary reader with code filtering",
                "priority": "critical",
                "category": "automation_tts"
            },
            {
                "ask": "So we already have a virtual assistant with the AI armory. software Is there any way that we can interact with that? I mean, because that's kind of cool. He just like wanders around. He's just a little figure that just wanders around the screen. Sometimes he talks to you and stuff. So, you know, Maybe if we came up with our own that looked like Jarvis, that would be sweet.",
                "intent": "Create JARVIS-themed virtual assistant like AI Armory",
                "priority": "medium",
                "category": "virtual_assistant"
            },
            {
                "ask": "HOW ARE YOU JARVIS GOING TO REMEMBER EVERYTHING PERSISTANTLY THOUGHOUT THE ENTIRE ECOSYSTEM",
                "intent": "Implement persistent memory system across ecosystem",
                "priority": "critical",
                "category": "memory_persistence"
            },
            {
                "ask": "I DIDN'T HEAR ANYTHING ELEVENLAB'ISH?",
                "intent": "Fix ElevenLabs voice output not working",
                "priority": "high",
                "category": "tts_voice"
            },
            {
                "ask": "I HAVE THE PAGE OPEN TO ELEVENLABS IN NEO BROWSER, PLEASE USE THIS TO RECONFIGURE FOR LUMINA.",
                "intent": "Use MANUS to extract ElevenLabs API key from Neo browser",
                "priority": "high",
                "category": "automation_integration"
            },
            {
                "ask": "JARVIS, PLEASE COMPARE THE @ASKS IN THIS SESSION AND DOES THE INTENT MATCH THE ROAST OR VISA-VERSA?",
                "intent": "Compare session @asks with roast results for intent alignment",
                "priority": "medium",
                "category": "analysis"
            }
        ]

    def load_roast_results(self) -> Optional[Dict[str, Any]]:
        """Load most recent roast results"""
        roast_dir = self.project_root / "data" / "jarvis_marvin_roasts"

        if not roast_dir.exists():
            return None

        # Find most recent roast
        roast_files = sorted(roast_dir.glob("roast_*.json"), reverse=True)

        if not roast_files:
            return None

        try:
            with open(roast_files[0], 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading roast: {e}")
            return None

    def analyze_intent_alignment(self) -> Dict[str, Any]:
        """Compare session @asks with roast results"""
        roast = self.load_roast_results()

        if not roast:
            return {
                'success': False,
                'error': 'No roast results found'
            }

        # Extract roast findings
        jarvis_findings = roast.get('jarvis_findings', [])
        marvin_findings = roast.get('marvin_findings', [])
        next_steps = roast.get('next_steps', [])

        # Analyze alignment
        alignment_analysis = {
            'session_asks_count': len(self.session_asks),
            'roast_issues_count': len(jarvis_findings) + len(marvin_findings),
            'roast_next_steps_count': len(next_steps),
            'intent_matches': [],
            'intent_mismatches': [],
            'roast_issues_not_addressed': [],
            'session_asks_not_in_roast': []
        }

        # Compare each session ask with roast
        for ask in self.session_asks:
            ask_intent = ask['intent'].lower()
            ask_category = ask['category']

            # Check if roast addresses this
            addressed = False
            matching_issues = []

            # Check JARVIS findings
            for issue in jarvis_findings:
                issue_title = issue.get('title', '').lower()
                issue_category = issue.get('category', '').lower()

                # Check for keyword matches
                if (ask_category in issue_category or 
                    any(word in issue_title for word in ask_intent.split() if len(word) > 4)):
                    addressed = True
                    matching_issues.append(issue)

            # Check MARVIN findings
            for issue in marvin_findings:
                issue_title = issue.get('title', '').lower()
                if any(word in issue_title for word in ask_intent.split() if len(word) > 4):
                    addressed = True
                    matching_issues.append(issue)

            # Check next steps
            for step in next_steps:
                step_title = step.get('title', '').lower()
                if any(word in step_title for word in ask_intent.split() if len(word) > 4):
                    addressed = True
                    matching_issues.append(step)

            if addressed:
                alignment_analysis['intent_matches'].append({
                    'ask': ask['ask'][:50] + '...',
                    'intent': ask['intent'],
                    'matching_issues': len(matching_issues)
                })
            else:
                alignment_analysis['intent_mismatches'].append({
                    'ask': ask['ask'][:50] + '...',
                    'intent': ask['intent'],
                    'category': ask_category
                })

        # Find roast issues not addressed in session
        all_roast_issues = jarvis_findings + marvin_findings
        for issue in all_roast_issues:
            issue_title = issue.get('title', '').lower()
            addressed_in_session = False

            for ask in self.session_asks:
                ask_intent = ask['intent'].lower()
                if any(word in issue_title for word in ask_intent.split() if len(word) > 4):
                    addressed_in_session = True
                    break

            if not addressed_in_session:
                alignment_analysis['roast_issues_not_addressed'].append({
                    'title': issue.get('title', ''),
                    'category': issue.get('category', ''),
                    'severity': issue.get('severity', '')
                })

        # Find session asks not in roast
        for ask in self.session_asks:
            ask_intent = ask['intent'].lower()
            in_roast = False

            for issue in all_roast_issues:
                issue_title = issue.get('title', '').lower()
                if any(word in issue_title for word in ask_intent.split() if len(word) > 4):
                    in_roast = True
                    break

            if not in_roast:
                alignment_analysis['session_asks_not_in_roast'].append({
                    'ask': ask['ask'][:50] + '...',
                    'intent': ask['intent'],
                    'category': ask['category']
                })

        return {
            'success': True,
            'analysis': alignment_analysis,
            'roast_summary': {
                'jarvis_issues': len(jarvis_findings),
                'marvin_issues': len(marvin_findings),
                'next_steps': len(next_steps),
                'overall_severity': roast.get('overall_severity', 'unknown')
            }
        }

    def generate_report(self) -> str:
        """Generate human-readable report"""
        result = self.analyze_intent_alignment()

        if not result.get('success'):
            return f"❌ Error: {result.get('error', 'unknown')}"

        analysis = result['analysis']
        roast_summary = result['roast_summary']

        report = []
        report.append("="*80)
        report.append("JARVIS SESSION @ASKS vs ROAST ANALYSIS")
        report.append("="*80)
        report.append("")

        # Summary
        report.append("📊 SUMMARY")
        report.append("-"*80)
        report.append(f"Session @Asks: {analysis['session_asks_count']}")
        report.append(f"Roast Issues: {roast_summary['jarvis_issues']} (JARVIS) + {roast_summary['marvin_issues']} (MARVIN)")
        report.append(f"Roast Next Steps: {roast_summary['next_steps']}")
        report.append(f"Overall Severity: {roast_summary['overall_severity']}")
        report.append("")

        # Intent Matches
        report.append("✅ INTENT MATCHES (Roast addressed session @asks)")
        report.append("-"*80)
        if analysis['intent_matches']:
            for match in analysis['intent_matches']:
                report.append(f"  • {match['intent']}")
                report.append(f"    Matched {match['matching_issues']} roast issue(s)")
        else:
            report.append("  (None found)")
        report.append("")

        # Intent Mismatches
        report.append("⚠️  INTENT MISMATCHES (Session @asks not in roast)")
        report.append("-"*80)
        if analysis['intent_mismatches']:
            for mismatch in analysis['intent_mismatches']:
                report.append(f"  • {mismatch['intent']}")
                report.append(f"    Category: {mismatch['category']}")
        else:
            report.append("  (All addressed)")
        report.append("")

        # Roast Issues Not Addressed
        report.append("📋 ROAST ISSUES NOT ADDRESSED IN SESSION")
        report.append("-"*80)
        if analysis['roast_issues_not_addressed']:
            for issue in analysis['roast_issues_not_addressed'][:10]:  # Top 10
                report.append(f"  • [{issue['severity'].upper()}] {issue['title']}")
                report.append(f"    Category: {issue['category']}")
        else:
            report.append("  (All addressed)")
        report.append("")

        # Session Asks Not in Roast
        report.append("🆕 SESSION @ASKS NOT IN ROAST (New requests)")
        report.append("-"*80)
        if analysis['session_asks_not_in_roast']:
            for ask in analysis['session_asks_not_in_roast']:
                report.append(f"  • {ask['intent']}")
                report.append(f"    Category: {ask['category']}")
        else:
            report.append("  (All in roast)")
        report.append("")

        # Alignment Score
        total_asks = analysis['session_asks_count']
        matched = len(analysis['intent_matches'])
        alignment_score = (matched / total_asks * 100) if total_asks > 0 else 0

        report.append("📈 ALIGNMENT SCORE")
        report.append("-"*80)
        report.append(f"Intent Alignment: {alignment_score:.1f}%")
        report.append(f"  Matched: {matched}/{total_asks}")
        report.append("")

        # Conclusion
        report.append("🎯 CONCLUSION")
        report.append("-"*80)
        if alignment_score >= 80:
            report.append("✅ HIGH ALIGNMENT - Roast and session @asks are well aligned")
        elif alignment_score >= 50:
            report.append("⚠️  MODERATE ALIGNMENT - Some gaps between roast and session")
        else:
            report.append("❌ LOW ALIGNMENT - Significant gaps between roast and session")

        report.append("")
        report.append("="*80)

        return "\n".join(report)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Session @Asks Analysis")
        parser.add_argument("--analyze", action="store_true", help="Analyze intent alignment")
        parser.add_argument("--report", action="store_true", help="Generate report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        analyzer = JARVISSessionAsksAnalysis(project_root)

        if args.analyze or args.report or not args:
            report = analyzer.generate_report()
            print(report)

            # Save report
            report_file = project_root / "data" / "session_analysis" / f"asks_vs_roast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w') as f:
                f.write(report)

            print(f"\n✅ Report saved: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()