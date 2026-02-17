#!/usr/bin/env python3
"""
JARVIS Project-Wide Balanced Development Plan

Applies 50/50 balanced development strategy to entire project:
- Scans all modules
- Identifies code quality issues
- Queues feature work
- Maintains balance across entire project
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

logger = get_logger("JARVISProjectWidePlan")


class JARVISProjectWideBalancedPlan:
    """
    Create and execute project-wide balanced development plan
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.balance_ratio = 0.5  # 50/50

    def scan_entire_project(self) -> Dict[str, Any]:
        """Scan entire project for code quality and feature work"""
        project_scan = {
            'code_quality_issues': [],
            'feature_work': [],
            'modules': {},
            'stats': {}
        }

        # Load roast issues
        roast_dir = self.project_root / "data" / "jarvis_marvin_roasts"
        if roast_dir.exists():
            roast_files = sorted(roast_dir.glob("roast_*.json"), reverse=True)
            if roast_files:
                try:
                    import json
                    with open(roast_files[0], 'r') as f:
                        roast = json.load(f)

                    # All code quality issues
                    for finding in roast.get('jarvis_findings', []):
                        project_scan['code_quality_issues'].append({
                            'severity': finding.get('severity', 'medium'),
                            'category': finding.get('category', ''),
                            'title': finding.get('title', ''),
                            'location': finding.get('location', ''),
                            'line_number': finding.get('line_number', 0)
                        })

                    for finding in roast.get('marvin_findings', []):
                        project_scan['code_quality_issues'].append({
                            'severity': finding.get('severity', 'medium'),
                            'category': finding.get('category', ''),
                            'title': finding.get('title', ''),
                            'location': finding.get('location', '')
                        })
                except:
                    pass

        # Load feature work
        action_plan_dir = self.project_root / "data" / "action_plans"
        if action_plan_dir.exists():
            action_files = sorted(action_plan_dir.glob("jarvis_action_plan_*.json"), reverse=True)
            if action_files:
                try:
                    import json
                    with open(action_files[0], 'r') as f:
                        action_plan = json.load(f)

                    for step in action_plan.get('steps', []):
                        project_scan['feature_work'].append({
                            'priority': step.get('priority', 'medium'),
                            'title': step.get('title', ''),
                            'description': step.get('description', ''),
                            'category': step.get('category', '')
                        })
                except:
                    pass

        # Organize by module
        for issue in project_scan['code_quality_issues']:
            location = issue.get('location', '')
            if location:
                module = Path(location).parent.name
                if module not in project_scan['modules']:
                    project_scan['modules'][module] = {
                        'code_quality_issues': [],
                        'feature_work': []
                    }
                project_scan['modules'][module]['code_quality_issues'].append(issue)

        # Stats
        project_scan['stats'] = {
            'total_code_quality_issues': len(project_scan['code_quality_issues']),
            'total_feature_work': len(project_scan['feature_work']),
            'modules_count': len(project_scan['modules']),
            'critical_issues': len([i for i in project_scan['code_quality_issues'] if i.get('severity') == 'critical']),
            'high_issues': len([i for i in project_scan['code_quality_issues'] if i.get('severity') == 'high']),
            'medium_issues': len([i for i in project_scan['code_quality_issues'] if i.get('severity') == 'medium'])
        }

        return project_scan

    def create_project_wide_plan(self) -> Dict[str, Any]:
        """Create balanced development plan for entire project"""
        scan = self.scan_entire_project()

        # Calculate balanced split
        total_work = scan['stats']['total_code_quality_issues'] + scan['stats']['total_feature_work']
        code_quality_target = int(total_work * self.balance_ratio)
        feature_target = total_work - code_quality_target

        # Prioritize issues
        code_quality_work = sorted(
            scan['code_quality_issues'],
            key=lambda x: {
                'critical': 4,
                'high': 3,
                'medium': 2,
                'low': 1
            }.get(x.get('severity', 'medium'), 2),
            reverse=True
        )[:code_quality_target]

        # Prioritize features
        feature_work = sorted(
            scan['feature_work'],
            key=lambda x: {
                'critical': 4,
                'high': 3,
                'medium': 2,
                'low': 1
            }.get(x.get('priority', 'medium'), 2),
            reverse=True
        )[:feature_target]

        plan = {
            'created_at': datetime.now().isoformat(),
            'project_wide': True,
            'balance_ratio': self.balance_ratio,
            'code_quality_work': {
                'total': len(code_quality_work),
                'critical': len([i for i in code_quality_work if i.get('severity') == 'critical']),
                'high': len([i for i in code_quality_work if i.get('severity') == 'high']),
                'medium': len([i for i in code_quality_work if i.get('severity') == 'medium']),
                'items': code_quality_work
            },
            'feature_work': {
                'total': len(feature_work),
                'critical': len([i for i in feature_work if i.get('priority') == 'critical']),
                'high': len([i for i in feature_work if i.get('priority') == 'high']),
                'items': feature_work
            },
            'modules': scan['modules'],
            'stats': scan['stats'],
            'execution_strategy': {
                'approach': 'module_by_module',
                'description': 'Process each module with 50/50 balance',
                'quality_gates': True,
                'parallel_execution': True
            }
        }

        return plan

    def generate_project_wide_report(self) -> str:
        """Generate project-wide balanced development report"""
        plan = self.create_project_wide_plan()

        report = []
        report.append("="*80)
        report.append("JARVIS PROJECT-WIDE BALANCED DEVELOPMENT PLAN")
        report.append("="*80)
        report.append("")

        # Project Stats
        report.append("📊 PROJECT STATISTICS")
        report.append("-"*80)
        report.append(f"Total Code Quality Issues: {plan['stats']['total_code_quality_issues']}")
        report.append(f"  - Critical: {plan['stats']['critical_issues']}")
        report.append(f"  - High: {plan['stats']['high_issues']}")
        report.append(f"  - Medium: {plan['stats']['medium_issues']}")
        report.append(f"Total Feature Work: {plan['stats']['total_feature_work']}")
        report.append(f"Modules: {plan['stats']['modules_count']}")
        report.append("")

        # Balanced Plan
        report.append("🎯 BALANCED PLAN (50/50)")
        report.append("-"*80)
        report.append(f"Code Quality Work: {plan['code_quality_work']['total']} items")
        report.append(f"  - Critical: {plan['code_quality_work']['critical']}")
        report.append(f"  - High: {plan['code_quality_work']['high']}")
        report.append(f"  - Medium: {plan['code_quality_work']['medium']}")
        report.append(f"Feature Work: {plan['feature_work']['total']} items")
        report.append(f"  - Critical: {plan['feature_work']['critical']}")
        report.append(f"  - High: {plan['feature_work']['high']}")
        report.append("")

        # Module Breakdown
        report.append("📁 MODULE BREAKDOWN")
        report.append("-"*80)
        for module, data in list(plan['modules'].items())[:10]:  # Top 10
            issues_count = len(data.get('code_quality_issues', []))
            if issues_count > 0:
                report.append(f"  {module}: {issues_count} issues")
        report.append("")

        # Execution Strategy
        report.append("🚀 EXECUTION STRATEGY")
        report.append("-"*80)
        report.append(f"Approach: {plan['execution_strategy']['approach']}")
        report.append(f"Description: {plan['execution_strategy']['description']}")
        report.append(f"Quality Gates: {'Enabled' if plan['execution_strategy']['quality_gates'] else 'Disabled'}")
        report.append(f"Parallel Execution: {'Enabled' if plan['execution_strategy']['parallel_execution'] else 'Disabled'}")
        report.append("")

        # Next Steps
        report.append("📋 NEXT STEPS")
        report.append("-"*80)
        report.append("1. Apply fixes module by module")
        report.append("2. Maintain 50/50 balance per module")
        report.append("3. Use quality gates before adding features")
        report.append("4. Track progress project-wide")
        report.append("")

        report.append("="*80)

        return "\n".join(report)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Project-Wide Balanced Plan")
        parser.add_argument("--plan", action="store_true", help="Create project-wide plan")
        parser.add_argument("--report", action="store_true", help="Generate report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        planner = JARVISProjectWideBalancedPlan(project_root)

        if args.plan or args.report or not args:
            report = planner.generate_project_wide_report()
            print(report)

            # Save report
            report_file = project_root / "data" / "project_wide_plan" / f"project_wide_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w') as f:
                f.write(report)

            print(f"\n✅ Report saved: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()