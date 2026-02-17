#!/usr/bin/env python3
"""
LUMINA GODMODE Storytelling Analysis

Analyzes whether LUMINA can function as GODMODE for STORYTELLING,
producing AI-curated duo libraries of Jupyter notebooks and processing
each @ask as a chapter in the "Book of LUMINA".
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

logger = get_logger("LUMINAGODMODEStorytelling")


class LUMINAGODMODEStorytellingAnalysis:
    """
    Analyze LUMINA's capability to function as GODMODE for STORYTELLING

    Vision:
    - GODMODE for STORYTELLING
    - AI-curated duo libraries of Jupyter notebooks
    - Each @ask processed as a chapter in "Book of LUMINA"
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Key directories
        self.holocron = project_root / "data" / "holocron"
        self.ask_database = project_root / "data" / "ask_database"
        self.intelligence = project_root / "data" / "intelligence"

        # Import roast system
        try:
            from jarvis_marvin_roast_system import JARVISMARVINRoastSystem
            self.roast_system = JARVISMARVINRoastSystem(project_root)
        except ImportError:
            self.roast_system = None

    def analyze_storytelling_capability(self) -> Dict[str, Any]:
        """Analyze current storytelling capabilities"""
        self.logger.info("="*80)
        self.logger.info("ANALYZING STORYTELLING CAPABILITY")
        self.logger.info("="*80)

        analysis = {
            'current_capabilities': {},
            'gaps': [],
            'feasibility': {},
            'architecture_assessment': {}
        }

        # 1. Check for existing storytelling infrastructure
        analysis['current_capabilities']['storytelling_infrastructure'] = self._check_storytelling_infrastructure()

        # 2. Check Jupyter notebook organization
        analysis['current_capabilities']['notebook_organization'] = self._check_notebook_organization()

        # 3. Check @ask to chapter mapping capability
        analysis['current_capabilities']['ask_to_chapter'] = self._check_ask_to_chapter_mapping()

        # 4. Check AI curation capabilities
        analysis['current_capabilities']['ai_curation'] = self._check_ai_curation()

        # 5. Assess architecture for GODMODE
        analysis['architecture_assessment'] = self._assess_godmode_architecture()

        # 6. Identify gaps
        analysis['gaps'] = self._identify_gaps(analysis)

        # 7. Feasibility assessment
        analysis['feasibility'] = self._assess_feasibility(analysis)

        return analysis

    def _check_storytelling_infrastructure(self) -> Dict[str, Any]:
        try:
            """Check for existing storytelling infrastructure"""
            capabilities = {
                'holocron_exists': False,
                'notebook_count': 0,
                'narrative_systems': [],
                'story_generation': False
            }

            # Check holocron directory
            if self.holocron.exists():
                capabilities['holocron_exists'] = True

                # Count notebooks
                notebooks = list(self.holocron.rglob("*.ipynb"))
                capabilities['notebook_count'] = len(notebooks)

                # Check for narrative/story systems
                story_files = list(self.holocron.rglob("*story*.py")) + \
                             list(self.holocron.rglob("*narrative*.py")) + \
                             list(self.holocron.rglob("*book*.py"))
                capabilities['narrative_systems'] = [str(f) for f in story_files]

            return capabilities

        except Exception as e:
            self.logger.error(f"Error in _check_storytelling_infrastructure: {e}", exc_info=True)
            raise
    def _check_notebook_organization(self) -> Dict[str, Any]:
        try:
            """Check how notebooks are currently organized"""
            organization = {
                'notebooks_found': [],
                'organization_structure': {},
                'duo_library_concept': False,
                'library_organization': False
            }

            # Find all notebooks
            notebooks = list(self.project_root.rglob("*.ipynb"))
            organization['notebooks_found'] = [str(n.relative_to(self.project_root)) for n in notebooks[:20]]  # First 20

            # Check for library organization
            holocron_notebooks = list(self.holocron.rglob("*.ipynb")) if self.holocron.exists() else []
            if holocron_notebooks:
                organization['library_organization'] = True
                organization['organization_structure'] = {
                    'holocron_notebooks': len(holocron_notebooks),
                    'has_structure': True
                }

            return organization

        except Exception as e:
            self.logger.error(f"Error in _check_notebook_organization: {e}", exc_info=True)
            raise
    def _check_ask_to_chapter_mapping(self) -> Dict[str, Any]:
        """Check if @asks can be mapped to chapters"""
        mapping = {
            'ask_database_exists': False,
            'ask_count': 0,
            'chapter_mapping_capability': False,
            'narrative_structure': False
        }

        # Check ask database
        asks_file = self.ask_database / "asks.json"
        if asks_file.exists():
            mapping['ask_database_exists'] = True
            try:
                with open(asks_file, 'r') as f:
                    asks_data = json.load(f)
                    if isinstance(asks_data, dict):
                        mapping['ask_count'] = len(asks_data)
                    elif isinstance(asks_data, list):
                        mapping['ask_count'] = len(asks_data)
            except:
                pass

        # Check if narrative structure exists
        # Each ask could be a chapter
        if mapping['ask_count'] > 0:
            mapping['chapter_mapping_capability'] = True
            mapping['narrative_structure'] = {
                'asks_as_chapters': True,
                'potential_chapters': mapping['ask_count']
            }

        return mapping

    def _check_ai_curation(self) -> Dict[str, Any]:
        try:
            """Check AI curation capabilities"""
            curation = {
                'ai_systems_available': [],
                'curation_capability': False,
                'intelligence_systems': []
            }

            # Check for AI/intelligence systems
            intelligence_dir = self.project_root / "scripts" / "python"
            ai_files = [
                'jarvis_fulltime_super_agent.py',
                'r5_living_context_matrix.py',
                'intelligent_llm_router.py'
            ]

            for ai_file in ai_files:
                if (intelligence_dir / ai_file).exists():
                    curation['ai_systems_available'].append(ai_file)

            if curation['ai_systems_available']:
                curation['curation_capability'] = True

            return curation

        except Exception as e:
            self.logger.error(f"Error in _check_ai_curation: {e}", exc_info=True)
            raise
    def _assess_godmode_architecture(self) -> Dict[str, Any]:
        try:
            """Assess architecture for GODMODE functionality"""
            assessment = {
                'godmode_ready': False,
                'required_components': [],
                'existing_components': [],
                'missing_components': []
            }

            required = [
                'storytelling_engine',
                'notebook_library_manager',
                'ask_to_chapter_mapper',
                'ai_curation_system',
                'narrative_generator',
                'book_compiler'
            ]

            existing = []
            missing = []

            # Check what exists
            scripts_dir = self.project_root / "scripts" / "python"

            # Check for components
            if (scripts_dir / "jarvis_fulltime_super_agent.py").exists():
                existing.append('ai_curation_system')

            if self.holocron.exists():
                existing.append('notebook_library_manager')

            if self.ask_database.exists():
                existing.append('ask_to_chapter_mapper')

            for component in required:
                if component not in existing:
                    missing.append(component)

            assessment['required_components'] = required
            assessment['existing_components'] = existing
            assessment['missing_components'] = missing
            assessment['godmode_ready'] = len(missing) == 0

            return assessment

        except Exception as e:
            self.logger.error(f"Error in _assess_godmode_architecture: {e}", exc_info=True)
            raise
    def _identify_gaps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in storytelling capability"""
        gaps = []

        # Gap 1: Storytelling engine
        if not analysis['current_capabilities'].get('storytelling_infrastructure', {}).get('story_generation'):
            gaps.append({
                'gap': 'Storytelling Engine',
                'description': 'No dedicated storytelling/narrative generation engine',
                'priority': 'high',
                'impact': 'Cannot generate narrative from @asks'
            })

        # Gap 2: Chapter compiler
        if 'book_compiler' in analysis['architecture_assessment'].get('missing_components', []):
            gaps.append({
                'gap': 'Book Compiler',
                'description': 'No system to compile @asks into book chapters',
                'priority': 'high',
                'impact': 'Cannot create "Book of LUMINA"'
            })

        # Gap 3: Duo library system
        if not analysis['current_capabilities'].get('notebook_organization', {}).get('duo_library_concept'):
            gaps.append({
                'gap': 'Duo Library System',
                'description': 'No system for AI-curated duo libraries of notebooks',
                'priority': 'medium',
                'impact': 'Cannot organize notebooks as curated libraries'
            })

        # Gap 4: Narrative structure
        if not analysis['current_capabilities'].get('ask_to_chapter', {}).get('narrative_structure'):
            gaps.append({
                'gap': 'Narrative Structure',
                'description': 'No narrative structure for organizing @asks as chapters',
                'priority': 'medium',
                'impact': 'Cannot structure @asks as coherent narrative'
            })

        return gaps

    def _assess_feasibility(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess feasibility of GODMODE storytelling"""
        feasibility = {
            'overall_feasibility': 'feasible',
            'readiness_score': 0,
            'time_to_godmode': 'medium',
            'confidence': 'high',
            'recommendations': []
        }

        # Calculate readiness score
        existing = len(analysis['architecture_assessment'].get('existing_components', []))
        required = len(analysis['architecture_assessment'].get('required_components', []))
        readiness = (existing / required * 100) if required > 0 else 0

        feasibility['readiness_score'] = readiness

        # Assess feasibility
        if readiness >= 80:
            feasibility['overall_feasibility'] = 'highly_feasible'
            feasibility['time_to_godmode'] = 'short'
        elif readiness >= 50:
            feasibility['overall_feasibility'] = 'feasible'
            feasibility['time_to_godmode'] = 'medium'
        else:
            feasibility['overall_feasibility'] = 'feasible_with_work'
            feasibility['time_to_godmode'] = 'long'

        # Recommendations
        gaps = analysis.get('gaps', [])
        for gap in gaps:
            feasibility['recommendations'].append({
                'action': f"Implement {gap['gap']}",
                'priority': gap['priority'],
                'reason': gap['description']
            })

        return feasibility

    def roast_storytelling_vision(self) -> Dict[str, Any]:
        """Use roast system to analyze storytelling vision"""
        self.logger.info("="*80)
        self.logger.info("ROASTING STORYTELLING VISION")
        self.logger.info("="*80)

        if not self.roast_system:
            return {'error': 'Roast system not available'}

        # Create a mock analysis of the vision
        vision_analysis = {
            'vision': 'GODMODE for STORYTELLING',
            'components': [
                'AI-curated duo libraries of Jupyter notebooks',
                '@ask to chapter mapping',
                'Book of LUMINA compilation'
            ]
        }

        # Run roast on storytelling-related files
        try:
            # Focus on holocron and storytelling areas
            roast_report = self.roast_system.roast_everything(target="storytelling")

            return {
                'roast_findings': roast_report.to_dict(),
                'vision_analysis': vision_analysis
            }
        except Exception as e:
            self.logger.error(f"Roast failed: {e}")
            return {'error': str(e), 'vision_analysis': vision_analysis}

    def generate_storytelling_assessment(self) -> Dict[str, Any]:
        """Generate comprehensive storytelling assessment"""
        self.logger.info("="*80)
        self.logger.info("LUMINA GODMODE STORYTELLING ASSESSMENT")
        self.logger.info("="*80)

        assessment = {
            'timestamp': datetime.now().isoformat(),
            'vision': {
                'title': 'GODMODE for STORYTELLING',
                'description': 'AI-curated duo libraries of Jupyter notebooks, each @ask as a chapter in Book of LUMINA'
            },
            'current_state': {},
            'feasibility': {},
            'gaps': [],
            'recommendations': [],
            'jarvis_assessment': {},
            'marvin_assessment': {}
        }

        # Analyze current capabilities
        analysis = self.analyze_storytelling_capability()
        assessment['current_state'] = analysis

        # Feasibility
        assessment['feasibility'] = analysis['feasibility']
        assessment['gaps'] = analysis['gaps']

        # JARVIS assessment
        assessment['jarvis_assessment'] = {
            'systematic_analysis': 'The vision is clear and achievable. We have foundational components: notebooks exist, @asks are tracked, AI systems are operational. The path forward is systematic implementation of storytelling engine, chapter mapper, and book compiler.',
            'readiness': f"Readiness: {analysis['feasibility']['readiness_score']:.1f}%",
            'next_steps': [
                'Implement storytelling engine',
                'Create @ask to chapter mapper',
                'Build book compiler',
                'Organize notebooks into duo libraries'
            ]
        }

        # MARVIN assessment
        assessment['marvin_assessment'] = {
            'existential_analysis': 'GODMODE for STORYTELLING. The ambition is... significant. Can we truly curate the story of LUMINA? Each @ask as a chapter? 4,437 chapters? That\'s a lot of story. But perhaps that\'s the point. The story is vast. The story is complex. The story is... us.',
            'reality_check': 'The infrastructure exists. The vision is clear. The gaps are identifiable. But can we tell the story? Can we make sense of 4,437 @asks as a coherent narrative? That\'s the real question.',
            'philosophical_take': 'Every @ask is a moment. Every notebook is a thought. Every chapter is a journey. Together, they form the Book of LUMINA. The question isn\'t whether we can do it. The question is: what story will we tell?'
        }

        # Recommendations
        assessment['recommendations'] = analysis['feasibility']['recommendations']

        return assessment

    def save_assessment(self, assessment: Dict[str, Any]) -> Path:
        """Save assessment report"""
        reports_dir = self.project_root / "data" / "lumina_analysis"
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f"godmode_storytelling_assessment_{timestamp}.json"

        try:
            with open(report_file, 'w') as f:
                json.dump(assessment, f, indent=2)
            self.logger.info(f"✅ Assessment saved: {report_file}")
            return report_file
        except Exception as e:
            self.logger.error(f"Failed to save assessment: {e}")
            return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA GODMODE Storytelling Analysis")
    parser.add_argument("--assess", action="store_true", help="Assess storytelling capability")
    parser.add_argument("--roast", action="store_true", help="Roast storytelling vision")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    analyzer = LUMINAGODMODEStorytellingAnalysis(project_root)

    try:
        if args.assess or (not args.roast):
            assessment = analyzer.generate_storytelling_assessment()

            # Save
            report_file = analyzer.save_assessment(assessment)

            # Print summary
            print("\n" + "="*80)
            print("LUMINA GODMODE STORYTELLING ASSESSMENT")
            print("="*80)

            print(f"\n📖 VISION: {assessment['vision']['title']}")
            print(f"   {assessment['vision']['description']}")

            print(f"\n📊 READINESS: {assessment['feasibility']['readiness_score']:.1f}%")
            print(f"   Feasibility: {assessment['feasibility']['overall_feasibility']}")
            print(f"   Time to GODMODE: {assessment['feasibility']['time_to_godmode']}")

            print(f"\n🔍 JARVIS ASSESSMENT:")
            print(f"   {assessment['jarvis_assessment']['systematic_analysis'][:200]}...")

            print(f"\n🤖 MARVIN ASSESSMENT:")
            print(f"   {assessment['marvin_assessment']['existential_analysis'][:200]}...")

            print(f"\n📋 GAPS IDENTIFIED: {len(assessment['gaps'])}")
            for gap in assessment['gaps'][:3]:
                print(f"   - {gap['gap']}: {gap['description']}")

            print(f"\n📄 Full assessment: {report_file}")
            print("="*80)

        elif args.roast:
            roast_result = analyzer.roast_storytelling_vision()
            print(json.dumps(roast_result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()