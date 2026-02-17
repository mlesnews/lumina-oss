#!/usr/bin/env python3
"""
JARVIS Next Steps Prioritizer

Systematically prioritizes next steps based on all assessments,
roast findings, and vision analysis.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISNextSteps")


@dataclass
class NextStep:
    """A prioritized next step"""
    step_id: str
    priority: str  # critical, high, medium, low
    category: str
    title: str
    description: str
    readiness: float  # 0-100
    effort: str  # short, medium, long
    dependencies: List[str] = field(default_factory=list)
    impact: str = ""
    estimated_time: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_id': self.step_id,
            'priority': self.priority,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'readiness': self.readiness,
            'effort': self.effort,
            'dependencies': self.dependencies,
            'impact': self.impact,
            'estimated_time': self.estimated_time
        }


class JARVISNextStepsPrioritizer:
    """
    JARVIS's systematic prioritization of next steps

    Integrates all assessments, roast findings, and vision analysis
    to create a clear, prioritized action plan.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.analysis_dir = project_root / "data" / "lumina_analysis"
        self.workflows_dir = project_root / "data" / "workflows"
        self.roast_dir = project_root / "data" / "jarvis_marvin_roasts"

    def load_all_assessments(self) -> Dict[str, Any]:
        """Load all recent assessments"""
        assessments = {}

        if not self.analysis_dir.exists():
            return assessments

        # Find all assessment files
        assessment_files = {
            'storytelling': 'godmode_storytelling_assessment_*.json',
            'multimedia': 'multimedia_storytelling_assessment_*.json',
            'life_domain': 'life_domain_assistant_assessment_*.json',
            'anime': 'anime_generation_assessment_*.json',
            'illumination': 'illumination_teaching_assessment_*.json'
        }

        for key, pattern in assessment_files.items():
            files = list(self.analysis_dir.glob(pattern))
            if files:
                latest = sorted(files, reverse=True)[0]
                try:
                    with open(latest, 'r') as f:
                        assessments[key] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Failed to load {key} assessment: {e}")

        return assessments

    def load_roast_findings(self) -> Dict[str, Any]:
        """Load latest roast findings"""
        if not self.roast_dir.exists():
            return {}

        roast_files = sorted(self.roast_dir.glob("roast_*.json"), reverse=True)
        if roast_files:
            try:
                with open(roast_files[0], 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load roast: {e}")

        return {}

    def generate_prioritized_steps(self) -> List[NextStep]:
        """Generate prioritized next steps from all assessments"""
        self.logger.info("="*80)
        self.logger.info("JARVIS PRIORITIZING NEXT STEPS")
        self.logger.info("="*80)

        steps = []

        # Load all data
        assessments = self.load_all_assessments()
        roast = self.load_roast_findings()

        # 1. CRITICAL: Fix immediate issues from roast
        steps.extend(self._extract_roast_steps(roast))

        # 2. HIGH: Illumination Teaching (100% ready, high impact)
        if 'illumination' in assessments:
            steps.extend(self._extract_illumination_steps(assessments['illumination']))

        # 3. HIGH: Multimedia completion (75% ready)
        if 'multimedia' in assessments:
            steps.extend(self._extract_multimedia_steps(assessments['multimedia']))

        # 4. MEDIUM: Storytelling engine (50% ready)
        if 'storytelling' in assessments:
            steps.extend(self._extract_storytelling_steps(assessments['storytelling']))

        # 5. MEDIUM: Anime generation (50% ready)
        if 'anime' in assessments:
            steps.extend(self._extract_anime_steps(assessments['anime']))

        # 6. LONG-TERM: Life domain expansion (20% ready)
        if 'life_domain' in assessments:
            steps.extend(self._extract_life_domain_steps(assessments['life_domain']))

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        steps.sort(key=lambda s: (priority_order.get(s.priority, 99), -s.readiness))

        return steps

    def _extract_roast_steps(self, roast: Dict[str, Any]) -> List[NextStep]:
        """Extract steps from roast findings"""
        steps = []

        if not roast:
            return steps

        next_steps = roast.get('next_steps', [])
        for step_data in next_steps:
            if step_data.get('priority') in ['critical', 'high']:
                steps.append(NextStep(
                    step_id=step_data.get('step_id', ''),
                    priority=step_data.get('priority', 'medium'),
                    category='code_quality',
                    title=step_data.get('title', ''),
                    description=step_data.get('description', ''),
                    readiness=50.0,  # Needs implementation
                    effort=step_data.get('estimated_effort', 'medium'),
                    impact='Fixes issues identified by roast system',
                    estimated_time=self._estimate_time(step_data.get('estimated_effort', 'medium'))
                ))

        return steps

    def _extract_illumination_steps(self, assessment: Dict[str, Any]) -> List[NextStep]:
        """Extract steps from Illumination assessment"""
        steps = []

        recommendations = assessment.get('recommendations', [])
        for rec in recommendations:
            if rec.get('priority') == 'high':
                steps.append(NextStep(
                    step_id=f"illumination_{rec.get('action', '').lower().replace(' ', '_')}",
                    priority='high',
                    category='illumination',
                    title=rec.get('action', ''),
                    description=rec.get('reason', ''),
                    readiness=100.0,  # Foundation ready
                    effort='short',
                    impact='Enables teaching the masses in Illumination',
                    estimated_time='1-2 weeks'
                ))

        return steps

    def _extract_multimedia_steps(self, assessment: Dict[str, Any]) -> List[NextStep]:
        """Extract steps from multimedia assessment"""
        steps = []

        recommendations = assessment.get('recommendations', [])
        for rec in recommendations:
            if rec.get('priority') == 'high':
                steps.append(NextStep(
                    step_id=f"multimedia_{rec.get('action', '').lower().replace(' ', '_')}",
                    priority='high',
                    category='multimedia',
                    title=rec.get('action', ''),
                    description=rec.get('reason', ''),
                    readiness=75.0,
                    effort='short',
                    impact='Completes multimedia storytelling capability',
                    estimated_time='1-2 weeks'
                ))

        return steps

    def _extract_storytelling_steps(self, assessment: Dict[str, Any]) -> List[NextStep]:
        """Extract steps from storytelling assessment"""
        steps = []

        recommendations = assessment.get('recommendations', [])
        for rec in recommendations[:3]:  # Top 3
            steps.append(NextStep(
                step_id=f"storytelling_{rec.get('action', '').lower().replace(' ', '_')}",
                priority='medium',
                category='storytelling',
                title=rec.get('action', ''),
                description=rec.get('reason', ''),
                readiness=50.0,
                effort='medium',
                impact='Enables GODMODE storytelling',
                estimated_time='2-4 weeks'
            ))

        return steps

    def _extract_anime_steps(self, assessment: Dict[str, Any]) -> List[NextStep]:
        """Extract steps from anime assessment"""
        steps = []

        recommendations = assessment.get('recommendations', [])
        for rec in recommendations:
            if rec.get('priority') == 'high':
                steps.append(NextStep(
                    step_id=f"anime_{rec.get('action', '').lower().replace(' ', '_')}",
                    priority='medium',
                    category='anime',
                    title=rec.get('action', ''),
                    description=rec.get('reason', ''),
                    readiness=50.0,
                    effort='long',
                    impact='Enables anime generation',
                    estimated_time='4-8 weeks'
                ))

        return steps

    def _extract_life_domain_steps(self, assessment: Dict[str, Any]) -> List[NextStep]:
        """Extract steps from life domain assessment"""
        steps = []

        recommendations = assessment.get('recommendations', [])
        for rec in recommendations[:3]:  # Top 3
            steps.append(NextStep(
                step_id=f"life_domain_{rec.get('action', '').lower().replace(' ', '_')}",
                priority='low',
                category='life_domain',
                title=rec.get('action', ''),
                description=rec.get('reason', ''),
                readiness=20.0,
                effort='very_long',
                impact='Expands life domain coverage',
                estimated_time='3-6 months'
            ))

        return steps

    def _estimate_time(self, effort: str) -> str:
        """Estimate time from effort level"""
        time_map = {
            'short': '1-2 weeks',
            'medium': '2-4 weeks',
            'high': '4-8 weeks',
            'long': '2-3 months',
            'very_long': '3-6 months'
        }
        return time_map.get(effort, 'TBD')

    def generate_action_plan(self) -> Dict[str, Any]:
        """Generate comprehensive action plan"""
        self.logger.info("="*80)
        self.logger.info("JARVIS GENERATING ACTION PLAN")
        self.logger.info("="*80)

        steps = self.generate_prioritized_steps()

        # Organize by priority
        by_priority = {
            'critical': [s for s in steps if s.priority == 'critical'],
            'high': [s for s in steps if s.priority == 'high'],
            'medium': [s for s in steps if s.priority == 'medium'],
            'low': [s for s in steps if s.priority == 'low']
        }

        plan = {
            'timestamp': datetime.now().isoformat(),
            'total_steps': len(steps),
            'by_priority': {k: len(v) for k, v in by_priority.items()},
            'steps': [s.to_dict() for s in steps],
            'immediate_actions': [s.to_dict() for s in steps if s.priority in ['critical', 'high']][:10],
            'summary': self._generate_summary(steps, by_priority)
        }

        return plan

    def _generate_summary(self, steps: List[NextStep], by_priority: Dict[str, List[NextStep]]) -> str:
        """Generate summary of action plan"""
        critical = len(by_priority.get('critical', []))
        high = len(by_priority.get('high', []))
        medium = len(by_priority.get('medium', []))
        low = len(by_priority.get('low', []))

        summary = f"""
JARVIS ACTION PLAN SUMMARY

Total Next Steps: {len(steps)}
  - Critical: {critical}
  - High: {high}
  - Medium: {medium}
  - Low: {low}

IMMEDIATE FOCUS (Next 30 Days):
  1. Fix critical issues from roast system
  2. Implement Illumination teaching systems (100% ready)
  3. Complete multimedia integration (75% ready)

SHORT-TERM (Next 90 Days):
  4. Build storytelling engine (50% ready)
  5. Develop anime generation (50% ready)
  6. Expand life domain coverage (20% ready)

LONG-TERM (6+ Months):
  7. Complete life domain expansion
  8. Global multilingual support
  9. Community platform development
"""
        return summary

    def save_action_plan(self, plan: Dict[str, Any]) -> Path:
        """Save action plan"""
        plans_dir = self.project_root / "data" / "action_plans"
        plans_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_file = plans_dir / f"jarvis_action_plan_{timestamp}.json"

        try:
            with open(plan_file, 'w') as f:
                json.dump(plan, f, indent=2)
            self.logger.info(f"✅ Action plan saved: {plan_file}")
            return plan_file
        except Exception as e:
            self.logger.error(f"Failed to save action plan: {e}")
            return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Next Steps Prioritizer")
    parser.add_argument("--plan", action="store_true", help="Generate action plan")
    parser.add_argument("--priority", type=str, choices=['critical', 'high', 'medium', 'low'], 
                       help="Show steps by priority")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    prioritizer = JARVISNextStepsPrioritizer(project_root)

    try:
        plan = prioritizer.generate_action_plan()

        # Save
        plan_file = prioritizer.save_action_plan(plan)

        # Print summary
        print("\n" + "="*80)
        print("JARVIS ACTION PLAN - WHAT IS NEXT")
        print("="*80)

        print(plan['summary'])

        if args.priority:
            filtered = [s for s in plan['steps'] if s['priority'] == args.priority]
            print(f"\n{args.priority.upper()} PRIORITY STEPS:")
            for i, step in enumerate(filtered, 1):
                print(f"\n{i}. {step['title']}")
                print(f"   Category: {step['category']}")
                print(f"   Readiness: {step['readiness']:.1f}%")
                print(f"   Effort: {step['effort']}")
                print(f"   Time: {step['estimated_time']}")
                print(f"   Impact: {step['impact']}")
        else:
            print("\nIMMEDIATE ACTIONS (Next 30 Days):")
            for i, step in enumerate(plan['immediate_actions'][:10], 1):
                print(f"\n{i}. [{step['priority'].upper()}] {step['title']}")
                print(f"   {step['description']}")
                print(f"   Readiness: {step['readiness']:.1f}% | Time: {step['estimated_time']}")

        print(f"\n📄 Full action plan: {plan_file}")
        print("="*80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()