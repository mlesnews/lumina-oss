#!/usr/bin/env python3
"""
LUMINA Deep Analysis - Magnifying Lens

Uses JARVIS + MARVIN roast system as a magnifying lens to deeply analyze
Project LUMINA, tracing "@asks" back to inception and walking the entire stack.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("LUMINADeepAnalysis")


class LUMINADeepAnalysis:
    """
    Deep analysis of Project LUMINA using roast system as magnifying lens

    Traces @asks back to inception and analyzes the entire project evolution.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Key data directories
        self.ask_database = project_root / "data" / "ask_database"
        self.intelligence = project_root / "data" / "intelligence"
        self.ultimate_goal = project_root / "data" / "lumina_ultimate_goal"
        self.roast_reports = project_root / "data" / "jarvis_marvin_roasts"

        # Import roast system
        try:
            from jarvis_marvin_roast_system import JARVISMARVINRoastSystem
            self.roast_system = JARVISMARVINRoastSystem(project_root)
        except ImportError:
            self.logger.error("Roast system not available")
            self.roast_system = None

    def trace_ask_stack(self) -> Dict[str, Any]:
        """Trace @asks back to inception"""
        self.logger.info("="*80)
        self.logger.info("TRACING @ASK STACK TO INCEPTION")
        self.logger.info("="*80)

        analysis = {
            'inception': {},
            'ask_evolution': [],
            'ask_categories': {},
            'ask_timeline': [],
            'key_milestones': []
        }

        # Load the ultimate ask
        ultimate_ask_file = self.ultimate_goal / "the_ask.json"
        if ultimate_ask_file.exists():
            try:
                with open(ultimate_ask_file, 'r') as f:
                    ultimate_ask = json.load(f)
                analysis['inception'] = {
                    'the_ask': ultimate_ask,
                    'source': str(ultimate_ask_file)
                }
                self.logger.info("✅ Found 'The Ask' - Project inception")
            except Exception as e:
                self.logger.error(f"Failed to load ultimate ask: {e}")

        # Load all asks
        asks_file = self.ask_database / "asks.json"
        if asks_file.exists():
            try:
                with open(asks_file, 'r') as f:
                    asks_data = json.load(f)

                # Organize asks
                if isinstance(asks_data, dict):
                    asks = asks_data.get('asks', [])
                elif isinstance(asks_data, list):
                    asks = asks_data
                else:
                    asks = []

                self.logger.info(f"Found {len(asks)} asks in database")

                # Analyze asks
                for ask in asks:
                    ask_id = ask.get('id', 'unknown')
                    ask_text = ask.get('ask', '')
                    timestamp = ask.get('timestamp', '')
                    category = ask.get('category', 'uncategorized')

                    analysis['ask_evolution'].append({
                        'id': ask_id,
                        'ask': ask_text,
                        'timestamp': timestamp,
                        'category': category,
                        'full_data': ask
                    })

                    # Categorize
                    if category not in analysis['ask_categories']:
                        analysis['ask_categories'][category] = []
                    analysis['ask_categories'][category].append(ask_id)

                # Sort by timestamp if available
                analysis['ask_evolution'].sort(
                    key=lambda x: x.get('timestamp', ''),
                    reverse=False
                )

            except Exception as e:
                self.logger.error(f"Failed to load asks: {e}")

        # Load ordered asks
        ordered_asks_file = self.intelligence / "LUMINA_ALL_ASKS_ORDERED.json"
        if ordered_asks_file.exists():
            try:
                with open(ordered_asks_file, 'r') as f:
                    ordered_asks = json.load(f)
                analysis['ask_timeline'] = ordered_asks
                self.logger.info(f"Found ordered asks timeline")
            except Exception as e:
                self.logger.error(f"Failed to load ordered asks: {e}")

        return analysis

    def analyze_project_evolution(self, ask_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how Project LUMINA evolved from inception"""
        self.logger.info("="*80)
        self.logger.info("ANALYZING PROJECT EVOLUTION")
        self.logger.info("="*80)

        evolution = {
            'phases': [],
            'key_decisions': [],
            'architectural_shifts': [],
            'complexity_growth': {},
            'patterns': []
        }

        # Analyze ask evolution
        asks = ask_analysis.get('ask_evolution', [])

        if asks:
            # Identify phases
            early_asks = asks[:10] if len(asks) > 10 else asks
            middle_asks = asks[10:30] if len(asks) > 30 else asks[10:]
            recent_asks = asks[-10:] if len(asks) > 10 else asks

            evolution['phases'] = [
                {
                    'phase': 'Inception',
                    'asks': len(early_asks),
                    'characteristics': self._analyze_phase_characteristics(early_asks)
                },
                {
                    'phase': 'Development',
                    'asks': len(middle_asks),
                    'characteristics': self._analyze_phase_characteristics(middle_asks) if middle_asks else {}
                },
                {
                    'phase': 'Maturation',
                    'asks': len(recent_asks),
                    'characteristics': self._analyze_phase_characteristics(recent_asks)
                }
            ]

            # Identify patterns
            all_ask_texts = [a.get('ask', '').lower() for a in asks]

            # Common themes
            themes = {
                'automation': sum(1 for t in all_ask_texts if 'automate' in t or 'automatic' in t),
                'integration': sum(1 for t in all_ask_texts if 'integrate' in t or 'integration' in t),
                'jarvis': sum(1 for t in all_ask_texts if 'jarvis' in t),
                'workflow': sum(1 for t in all_ask_texts if 'workflow' in t),
                'error': sum(1 for t in all_ask_texts if 'error' in t or 'fix' in t),
                'system': sum(1 for t in all_ask_texts if 'system' in t),
            }

            evolution['patterns'] = {
                'common_themes': themes,
                'most_common': max(themes.items(), key=lambda x: x[1]) if themes else None
            }

        return evolution

    def _analyze_phase_characteristics(self, asks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze characteristics of a phase"""
        if not asks:
            return {}

        characteristics = {
            'avg_length': sum(len(a.get('ask', '')) for a in asks) / len(asks) if asks else 0,
            'categories': {},
            'complexity_indicators': []
        }

        # Categorize
        for ask in asks:
            category = ask.get('category', 'uncategorized')
            characteristics['categories'][category] = characteristics['categories'].get(category, 0) + 1

        # Complexity indicators
        for ask in asks:
            ask_text = ask.get('ask', '').lower()
            if any(word in ask_text for word in ['system', 'architecture', 'integrate', 'complex']):
                characteristics['complexity_indicators'].append(ask.get('id', 'unknown'))

        return characteristics

    def roast_entire_project(self) -> Dict[str, Any]:
        """Run roast system on entire project"""
        self.logger.info("="*80)
        self.logger.info("ROASTING ENTIRE PROJECT")
        self.logger.info("="*80)

        if not self.roast_system:
            return {'error': 'Roast system not available'}

        try:
            roast_report = self.roast_system.roast_everything()
            return roast_report.to_dict()
        except Exception as e:
            self.logger.error(f"Roast failed: {e}")
            return {'error': str(e)}

    def correlate_asks_with_roast(self, ask_analysis: Dict[str, Any], roast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate @asks with roast findings"""
        self.logger.info("="*80)
        self.logger.info("CORRELATING @ASKS WITH ROAST FINDINGS")
        self.logger.info("="*80)

        correlation = {
            'ask_to_issue_mapping': [],
            'recurring_problems': [],
            'evolution_insights': []
        }

        # Get roast findings
        jarvis_findings = roast_data.get('jarvis_findings', [])
        marvin_findings = roast_data.get('marvin_findings', [])

        # Get asks
        asks = ask_analysis.get('ask_evolution', [])

        # Map asks to issues
        for ask in asks:
            ask_text = ask.get('ask', '').lower()
            ask_id = ask.get('id', '')

            related_findings = []

            # Find related findings
            for finding in jarvis_findings + marvin_findings:
                finding_title = finding.get('title', '').lower()
                finding_desc = finding.get('description', '').lower()

                # Simple keyword matching
                ask_keywords = set(ask_text.split())
                finding_keywords = set((finding_title + ' ' + finding_desc).split())

                if ask_keywords & finding_keywords:  # Intersection
                    related_findings.append({
                        'finding': finding.get('title', ''),
                        'severity': finding.get('severity', ''),
                        'category': finding.get('category', '')
                    })

            if related_findings:
                correlation['ask_to_issue_mapping'].append({
                    'ask_id': ask_id,
                    'ask': ask.get('ask', ''),
                    'related_findings': related_findings
                })

        # Identify recurring problems
        all_categories = {}
        for finding in jarvis_findings + marvin_findings:
            category = finding.get('category', 'unknown')
            all_categories[category] = all_categories.get(category, 0) + 1

        correlation['recurring_problems'] = sorted(
            all_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return correlation

    def generate_deep_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive deep analysis report"""
        self.logger.info("="*80)
        self.logger.info("LUMINA DEEP ANALYSIS - MAGNIFYING LENS")
        self.logger.info("="*80)
        self.logger.info("")

        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'deep_analysis_magnifying_lens',
            'sections': {}
        }

        # 1. Trace @asks to inception
        self.logger.info("Section 1: Tracing @asks to inception...")
        ask_analysis = self.trace_ask_stack()
        report['sections']['ask_stack'] = ask_analysis

        # 2. Analyze project evolution
        self.logger.info("Section 2: Analyzing project evolution...")
        evolution = self.analyze_project_evolution(ask_analysis)
        report['sections']['evolution'] = evolution

        # 3. Roast entire project
        self.logger.info("Section 3: Roasting entire project...")
        roast_data = self.roast_entire_project()
        report['sections']['roast'] = roast_data

        # 4. Correlate asks with roast
        self.logger.info("Section 4: Correlating asks with roast findings...")
        correlation = self.correlate_asks_with_roast(ask_analysis, roast_data)
        report['sections']['correlation'] = correlation

        # 5. Generate insights
        self.logger.info("Section 5: Generating insights...")
        insights = self._generate_insights(ask_analysis, evolution, roast_data, correlation)
        report['sections']['insights'] = insights

        return report

    def _generate_insights(self, ask_analysis: Dict, evolution: Dict, roast_data: Dict, correlation: Dict) -> Dict[str, Any]:
        """Generate insights from all analyses"""
        insights = {
            'inception_insights': [],
            'evolution_insights': [],
            'roast_insights': [],
            'correlation_insights': [],
            'recommendations': []
        }

        # Inception insights
        if ask_analysis.get('inception'):
            insights['inception_insights'].append(
                "Project LUMINA has a clear 'The Ask' - ultimate goal defined at inception"
            )

        # Evolution insights
        phases = evolution.get('phases', [])
        if phases:
            insights['evolution_insights'].append(
                f"Project evolved through {len(phases)} distinct phases"
            )

            most_common = evolution.get('patterns', {}).get('most_common')
            if most_common:
                insights['evolution_insights'].append(
                    f"Most common theme in asks: {most_common[0]} ({most_common[1]} occurrences)"
                )

        # Roast insights
        if not roast_data.get('error'):
            total_findings = len(roast_data.get('jarvis_findings', [])) + len(roast_data.get('marvin_findings', []))
            insights['roast_insights'].append(
                f"Roast system found {total_findings} issues across the project"
            )

            debate_points = len(roast_data.get('debate', []))
            if debate_points > 0:
                insights['roast_insights'].append(
                    f"JARVIS and MARVIN engaged in {debate_points} debate points, showing balanced analysis"
                )

        # Correlation insights
        recurring = correlation.get('recurring_problems', [])
        if recurring:
            top_problem = recurring[0]
            insights['correlation_insights'].append(
                f"Most recurring problem category: {top_problem[0]} ({top_problem[1]} occurrences)"
            )

        # Recommendations
        insights['recommendations'] = [
            "Address recurring problems identified in correlation analysis",
            "Review architectural concerns raised by MARVIN",
            "Implement systematic fixes identified by JARVIS",
            "Balance philosophical understanding (MARVIN) with practical action (JARVIS)"
        ]

        return insights

    def save_report(self, report: Dict[str, Any]) -> Path:
        """Save analysis report"""
        reports_dir = self.project_root / "data" / "lumina_analysis"
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f"deep_analysis_{timestamp}.json"

        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"✅ Report saved: {report_file}")
            return report_file
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Deep Analysis - Magnifying Lens")
    parser.add_argument("--analyze", action="store_true", help="Run deep analysis")
    parser.add_argument("--trace-asks", action="store_true", help="Trace @asks to inception")
    parser.add_argument("--roast", action="store_true", help="Roast entire project")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    analyzer = LUMINADeepAnalysis(project_root)

    try:
        if args.analyze or (not any([args.trace_asks, args.roast])):
            # Full deep analysis
            report = analyzer.generate_deep_analysis_report()

            # Save report
            report_file = analyzer.save_report(report)

            # Print summary
            print("\n" + "="*80)
            print("LUMINA DEEP ANALYSIS SUMMARY")
            print("="*80)

            if report.get('sections', {}).get('ask_stack', {}).get('inception'):
                print("\n✅ INCEPTION FOUND")
                inception = report['sections']['ask_stack']['inception']
                if 'the_ask' in inception:
                    the_ask = inception['the_ask']
                    print(f"   The Ask: {the_ask.get('ask', 'N/A')[:100]}...")

            ask_count = len(report.get('sections', {}).get('ask_stack', {}).get('ask_evolution', []))
            print(f"\n📋 ASK STACK: {ask_count} asks traced")

            phases = len(report.get('sections', {}).get('evolution', {}).get('phases', []))
            print(f"📈 EVOLUTION: {phases} phases identified")

            roast_data = report.get('sections', {}).get('roast', {})
            if not roast_data.get('error'):
                total_findings = len(roast_data.get('jarvis_findings', [])) + len(roast_data.get('marvin_findings', []))
                print(f"🔥 ROAST: {total_findings} issues found")

            print(f"\n📄 Full report: {report_file}")
            print("="*80)

        elif args.trace_asks:
            ask_analysis = analyzer.trace_ask_stack()
            print(json.dumps(ask_analysis, indent=2))

        elif args.roast:
            roast_data = analyzer.roast_entire_project()
            print(json.dumps(roast_data, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()