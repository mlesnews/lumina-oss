#!/usr/bin/env python3
"""
JARVIS Plan Influence Analyzer

Analyzes documentation input/feedback and determines how it influences our plans.
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

logger = get_logger("JARVISPlanInfluenceAnalyzer")


class JARVISPlanInfluenceAnalyzer:
    """
    Analyze documentation input/feedback and its influence on plans
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

    def load_analysis_docs(self) -> Dict[str, Any]:
        """Load all analysis documentation"""
        docs = {
            'session_asks_vs_roast': None,
            'roast_results': None,
            'action_plans': None,
            'workflow_plans': None
        }

        # Session @asks vs Roast analysis
        analysis_file = self.project_root / "docs" / "SESSION_ASKS_VS_ROAST_ANALYSIS.md"
        if analysis_file.exists():
            docs['session_asks_vs_roast'] = analysis_file.read_text()

        # Roast results
        roast_dir = self.project_root / "data" / "jarvis_marvin_roasts"
        if roast_dir.exists():
            roast_files = sorted(roast_dir.glob("roast_*.json"), reverse=True)
            if roast_files:
                try:
                    with open(roast_files[0], 'r') as f:
                        docs['roast_results'] = json.load(f)
                except:
                    pass

        # Action plans
        action_plan_dir = self.project_root / "data" / "action_plans"
        if action_plan_dir.exists():
            action_files = sorted(action_plan_dir.glob("jarvis_action_plan_*.json"), reverse=True)
            if action_files:
                try:
                    with open(action_files[0], 'r') as f:
                        docs['action_plans'] = json.load(f)
                except:
                    pass

        # Workflow plans
        workflow_dir = self.project_root / "data" / "workflows"
        if workflow_dir.exists():
            workflow_files = sorted(workflow_dir.glob("roast_generated_workflows.json"), reverse=True)
            if workflow_files:
                try:
                    with open(workflow_files[0], 'r') as f:
                        docs['workflow_plans'] = json.load(f)
                except:
                    pass

        return docs

    def extract_feedback(self, docs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key feedback from documentation"""
        feedback = {
            'alignment_score': None,
            'roast_issues_count': 0,
            'session_asks_count': 0,
            'recommendations': [],
            'warnings': [],
            'insights': []
        }

        # From session @asks vs roast analysis
        if docs.get('session_asks_vs_roast'):
            analysis = docs['session_asks_vs_roast']

            # Extract alignment score
            if 'Alignment Score: **40%**' in analysis:
                feedback['alignment_score'] = 40.0
            elif 'Alignment: 40%' in analysis:
                feedback['alignment_score'] = 40.0

            # Extract recommendations
            if '## 💡 RECOMMENDATIONS' in analysis:
                rec_section = analysis.split('## 💡 RECOMMENDATIONS')[1].split('##')[0]
                for line in rec_section.split('\n'):
                    if line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.'):
                        feedback['recommendations'].append(line.strip())

            # Extract warnings
            if '⚠️' in analysis:
                warnings = [line for line in analysis.split('\n') if '⚠️' in line]
                feedback['warnings'].extend(warnings[:5])  # Top 5

        # From roast results
        if docs.get('roast_results'):
            roast = docs['roast_results']

            feedback['roast_issues_count'] = len(roast.get('jarvis_findings', [])) + len(roast.get('marvin_findings', []))
            feedback['session_asks_count'] = 10  # From analysis

            # Extract next steps as recommendations
            next_steps = roast.get('next_steps', [])
            for step in next_steps[:5]:  # Top 5
                feedback['recommendations'].append(f"{step.get('title', '')}: {step.get('description', '')}")

        # Extract insights
        if docs.get('session_asks_vs_roast'):
            analysis = docs['session_asks_vs_roast']
            if '## 🎯 KEY INSIGHTS' in analysis:
                insights_section = analysis.split('## 🎯 KEY INSIGHTS')[1].split('##')[0]
                for line in insights_section.split('\n'):
                    if line.strip().startswith('###') or (line.strip().startswith('1.') and len(line.strip()) > 10):
                        feedback['insights'].append(line.strip())

        return feedback

    def analyze_plan_influence(self, feedback: Dict[str, Any], current_plans: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how feedback influences current plans"""
        influence = {
            'should_adjust_plans': False,
            'adjustment_reasons': [],
            'priority_changes': [],
            'new_actions_needed': [],
            'risk_assessment': {},
            'recommended_plan_changes': []
        }

        # Check alignment score
        if feedback.get('alignment_score') and feedback['alignment_score'] < 50:
            influence['should_adjust_plans'] = True
            influence['adjustment_reasons'].append(
                f"Low alignment ({feedback['alignment_score']}%) - roast and session @asks have different intents"
            )

        # Check roast issues vs plans
        roast_issues = feedback.get('roast_issues_count', 0)
        if roast_issues > 30:
            influence['should_adjust_plans'] = True
            influence['adjustment_reasons'].append(
                f"High number of roast issues ({roast_issues}) - code quality should be prioritized"
            )
            influence['priority_changes'].append({
                'action': 'Increase code quality priority',
                'current': 'Low',
                'recommended': 'High',
                'reason': f'{roast_issues} code quality issues found'
            })

        # Check recommendations
        recommendations = feedback.get('recommendations', [])
        if recommendations:
            influence['should_adjust_plans'] = True
            for rec in recommendations[:3]:  # Top 3
                influence['recommended_plan_changes'].append({
                    'type': 'recommendation',
                    'content': rec
                })

        # Risk assessment
        if feedback.get('alignment_score') and feedback['alignment_score'] < 50:
            influence['risk_assessment'] = {
                'level': 'medium',
                'description': 'Building new features on code with known quality issues',
                'mitigation': 'Balance feature development with code quality improvements'
            }

        # New actions needed
        if feedback.get('roast_issues_count', 0) > 0:
            influence['new_actions_needed'].append({
                'action': 'Address roast code quality issues',
                'priority': 'high',
                'count': feedback['roast_issues_count'],
                'estimated_effort': 'high'
            })

        return influence

    def generate_plan_adjustment_report(self) -> str:
        """Generate comprehensive plan adjustment report"""
        docs = self.load_analysis_docs()
        feedback = self.extract_feedback(docs)
        influence = self.analyze_plan_influence(feedback, {})

        report = []
        report.append("="*80)
        report.append("JARVIS PLAN INFLUENCE ANALYSIS")
        report.append("="*80)
        report.append("")

        # Documentation Input
        report.append("📋 DOCUMENTATION INPUT")
        report.append("-"*80)
        report.append(f"Alignment Score: {feedback.get('alignment_score', 'N/A')}%")
        report.append(f"Roast Issues: {feedback.get('roast_issues_count', 0)}")
        report.append(f"Session @Asks: {feedback.get('session_asks_count', 0)}")
        report.append("")

        # Feedback Summary
        report.append("💬 FEEDBACK SUMMARY")
        report.append("-"*80)

        if feedback.get('recommendations'):
            report.append("Recommendations:")
            for i, rec in enumerate(feedback['recommendations'][:5], 1):
                report.append(f"  {i}. {rec[:100]}...")

        if feedback.get('warnings'):
            report.append("")
            report.append("Warnings:")
            for warning in feedback['warnings'][:3]:
                report.append(f"  ⚠️  {warning[:100]}...")

        if feedback.get('insights'):
            report.append("")
            report.append("Key Insights:")
            for insight in feedback['insights'][:3]:
                report.append(f"  • {insight[:100]}...")

        report.append("")

        # Plan Influence
        report.append("🎯 PLAN INFLUENCE ANALYSIS")
        report.append("-"*80)

        if influence['should_adjust_plans']:
            report.append("✅ YES - Plans Should Be Adjusted")
            report.append("")
            report.append("Reasons:")
            for reason in influence['adjustment_reasons']:
                report.append(f"  • {reason}")
        else:
            report.append("❌ NO - Plans Are Fine")

        report.append("")

        # Priority Changes
        if influence['priority_changes']:
            report.append("📊 PRIORITY CHANGES RECOMMENDED")
            report.append("-"*80)
            for change in influence['priority_changes']:
                report.append(f"  • {change['action']}")
                report.append(f"    {change['current']} → {change['recommended']}")
                report.append(f"    Reason: {change['reason']}")
            report.append("")

        # Recommended Plan Changes
        if influence['recommended_plan_changes']:
            report.append("🔄 RECOMMENDED PLAN CHANGES")
            report.append("-"*80)
            for change in influence['recommended_plan_changes']:
                report.append(f"  • {change.get('content', change.get('type', 'Unknown'))[:100]}...")
            report.append("")

        # New Actions Needed
        if influence['new_actions_needed']:
            report.append("🆕 NEW ACTIONS NEEDED")
            report.append("-"*80)
            for action in influence['new_actions_needed']:
                report.append(f"  • [{action['priority'].upper()}] {action['action']}")
                report.append(f"    Count: {action.get('count', 'N/A')}")
                report.append(f"    Effort: {action.get('estimated_effort', 'N/A')}")
            report.append("")

        # Risk Assessment
        if influence.get('risk_assessment'):
            risk = influence['risk_assessment']
            report.append("⚠️  RISK ASSESSMENT")
            report.append("-"*80)
            report.append(f"Level: {risk.get('level', 'unknown').upper()}")
            report.append(f"Description: {risk.get('description', 'N/A')}")
            report.append(f"Mitigation: {risk.get('mitigation', 'N/A')}")
            report.append("")

        # Conclusion
        report.append("🎯 CONCLUSION")
        report.append("-"*80)

        if influence['should_adjust_plans']:
            report.append("✅ DOCUMENTATION INPUT INDICATES PLANS SHOULD BE ADJUSTED")
            report.append("")
            report.append("Key Factors:")
            report.append(f"  1. Low alignment ({feedback.get('alignment_score', 'N/A')}%)")
            report.append(f"  2. High roast issues ({feedback.get('roast_issues_count', 0)})")
            report.append(f"  3. Different intents (quality vs features)")
            report.append("")
            report.append("Recommended Action:")
            report.append("  Balance feature development with code quality improvements")
        else:
            report.append("❌ NO MAJOR PLAN ADJUSTMENTS NEEDED")

        report.append("")
        report.append("="*80)

        return "\n".join(report)


def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent
        analyzer = JARVISPlanInfluenceAnalyzer(project_root)

        report = analyzer.generate_plan_adjustment_report()
        print(report)

        # Save report
        report_file = project_root / "data" / "plan_analysis" / f"plan_influence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            f.write(report)

        print(f"\n✅ Report saved: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()