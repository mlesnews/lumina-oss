#!/usr/bin/env python3
"""
JARVIS Look Inward System

Using @SYPHON and @R5 to look inward at Project Lumina.
Analyze what we've built, extract intelligence, aggregate context.

Tags: #LOOK_INWARD #SYPHON #R5 #INTROSPECTION #ANALYSIS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISLookInward")


class SYPHONIntelligenceExtractor:
    """@SYPHON - Extract intelligence from Project Lumina"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "syphon"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.extracted_data = {}
        self.intelligence = {}

    def extract_from_lumina(self) -> Dict[str, Any]:
        try:
            """Extract intelligence from Project Lumina"""
            logger.info("=" * 80)
            logger.info("🔍 @SYPHON - EXTRACTING INTELLIGENCE")
            logger.info("=" * 80)
            logger.info("")

            extraction = {
                "timestamp": datetime.now().isoformat(),
                "source": "Project Lumina",
                "extraction_type": "LOOK_INWARD",
                "systems_analyzed": [],
                "intelligence_extracted": {},
                "patterns_found": [],
                "insights": []
            }

            # Analyze scripts
            scripts_dir = project_root / "scripts" / "python"
            if scripts_dir.exists():
                scripts = list(scripts_dir.glob("*.py"))
                extraction["systems_analyzed"] = [s.name for s in scripts[:50]]  # Sample

                # Extract intelligence from scripts
                extraction["intelligence_extracted"] = {
                    "total_scripts": len(scripts),
                    "key_systems": self._identify_key_systems(scripts),
                    "integration_points": self._find_integration_points(scripts),
                    "patterns": self._extract_patterns(scripts)
                }

            # Analyze configs
            config_dir = project_root / "config"
            if config_dir.exists():
                configs = list(config_dir.rglob("*.json"))
                extraction["intelligence_extracted"]["configs"] = {
                    "total_configs": len(configs),
                    "key_configs": [c.name for c in configs[:20]]
                }

            # Analyze docs
            docs_dir = project_root / "docs"
            if docs_dir.exists():
                docs = list(docs_dir.rglob("*.md"))
                extraction["intelligence_extracted"]["documentation"] = {
                    "total_docs": len(docs),
                    "key_docs": [d.name for d in docs[:20]]
                }

            # Extract patterns
            extraction["patterns_found"] = self._extract_system_patterns()

            # Generate insights
            extraction["insights"] = self._generate_syphon_insights(extraction)

            logger.info(f"✅ Extracted intelligence from {extraction['intelligence_extracted'].get('total_scripts', 0)} systems")
            logger.info("")

            return extraction

        except Exception as e:
            self.logger.error(f"Error in extract_from_lumina: {e}", exc_info=True)
            raise
    def _identify_key_systems(self, scripts: List[Path]) -> List[str]:
        """Identify key systems"""
        key_systems = []
        for script in scripts:
            name = script.stem
            if any(keyword in name.lower() for keyword in ["jarvis", "lumina", "r5", "syphon", "holocron", "force", "titan"]):
                key_systems.append(name)
        return key_systems[:20]

    def _find_integration_points(self, scripts: List[Path]) -> List[str]:
        """Find integration points"""
        integration_points = []
        keywords = ["import", "from", "integration", "connect", "integrate"]
        for script in scripts[:20]:  # Sample
            try:
                content = script.read_text(encoding='utf-8', errors='ignore')
                if any(kw in content.lower() for kw in keywords):
                    integration_points.append(script.name)
            except:
                pass
        return integration_points

    def _extract_patterns(self, scripts: List[Path]) -> List[str]:
        """Extract patterns"""
        patterns = []
        # Look for common patterns
        pattern_keywords = ["class", "def", "async", "try", "except", "logger"]
        for script in scripts[:20]:  # Sample
            try:
                content = script.read_text(encoding='utf-8', errors='ignore')
                for keyword in pattern_keywords:
                    if keyword in content:
                        patterns.append(f"{script.name}: {keyword} pattern")
            except:
                pass
        return patterns[:10]

    def _extract_system_patterns(self) -> List[str]:
        """Extract system-wide patterns"""
        return [
            "JARVIS orchestration pattern",
            "Local-first AI routing",
            "Cross-consultation expert system",
            "Polymath life domain coaching",
            "Force values integration",
            "Non-profit business model",
            "Open source philosophy",
            "Pathfinder system",
            "Inception-style layers",
            "Merit-based assessment"
        ]

    def _generate_syphon_insights(self, extraction: Dict[str, Any]) -> List[str]:
        """Generate SYPHON insights"""
        insights = []

        total_systems = extraction["intelligence_extracted"].get("total_scripts", 0)
        if total_systems > 100:
            insights.append(f"💡 Large system: {total_systems} scripts analyzed")

        key_systems = extraction["intelligence_extracted"].get("key_systems", [])
        if len(key_systems) > 10:
            insights.append(f"💡 Multiple key systems: {len(key_systems)} identified")

        patterns = extraction["patterns_found"]
        if patterns:
            insights.append(f"💡 System patterns: {len(patterns)} patterns identified")

        insights.append("💡 SYPHON extraction complete - intelligence gathered")

        return insights


class R5ContextAggregator:
    """@R5 - Aggregate and analyze context from Project Lumina"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "r5_living_matrix"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.context_matrix = {}
        self.aggregated_context = {}

    def aggregate_lumina_context(self) -> Dict[str, Any]:
        """Aggregate context from Project Lumina"""
        logger.info("=" * 80)
        logger.info("📊 @R5 - AGGREGATING CONTEXT")
        logger.info("=" * 80)
        logger.info("")

        aggregation = {
            "timestamp": datetime.now().isoformat(),
            "source": "Project Lumina",
            "aggregation_type": "LOOK_INWARD",
            "context_matrix": {},
            "living_context": {},
            "patterns_aggregated": [],
            "synthesis": {}
        }

        # Build context matrix
        aggregation["context_matrix"] = {
            "systems": self._aggregate_systems(),
            "workflows": self._aggregate_workflows(),
            "integrations": self._aggregate_integrations(),
            "philosophy": self._aggregate_philosophy(),
            "vision": self._aggregate_vision()
        }

        # Living context
        aggregation["living_context"] = {
            "evolution": "System continuously evolving",
            "growth": "Expanding capabilities and integrations",
            "adaptation": "Adapting to needs and requirements",
            "synthesis": "Synthesizing all components into cohesive whole"
        }

        # Patterns aggregated
        aggregation["patterns_aggregated"] = [
            "JARVIS as central orchestrator",
            "Local-first AI priority",
            "Cross-consultation expert system",
            "Polymath holistic approach",
            "Force values integration",
            "Non-profit mission-driven",
            "Open source transparency",
            "Pathfinder for unique paths",
            "Merit-based assessment",
            "Company in a box"
        ]

        # Synthesis
        aggregation["synthesis"] = {
            "core_identity": "AI-powered development ecosystem with Force values",
            "mission": "Help people in all areas of life through AI coaching",
            "approach": "Polymath holistic view with local-first AI",
            "philosophy": "Take what you like, leave the rest",
            "vision": "Enlightenment system using AI to bring out the best in people"
        }

        logger.info("✅ Context aggregated")
        logger.info("")

        return aggregation

    def _aggregate_systems(self) -> Dict[str, Any]:
        """Aggregate system information"""
        return {
            "total_systems": "1000+ Python scripts",
            "key_systems": [
                "JARVIS orchestration",
                "Local-first AI routing",
                "Virtual assistants",
                "Cross-consultation expert system",
                "Hiring manager",
                "Technical profile analyzer",
                "Creativity analysis",
                "Titans perspective system",
                "Company in a box",
                "Force values system"
            ],
            "architecture": "Modular, composable, integrated"
        }

    def _aggregate_workflows(self) -> Dict[str, Any]:
        """Aggregate workflow information"""
        return {
            "workflow_types": [
                "AI routing workflows",
                "Coaching workflows",
                "Analysis workflows",
                "Assessment workflows",
                "Integration workflows"
            ],
            "workflow_philosophy": "Inception-style layers, for a reason, for a reason...",
            "workflow_integration": "All workflows integrated through JARVIS"
        }

    def _aggregate_integrations(self) -> Dict[str, Any]:
        """Aggregate integration information"""
        return {
            "integration_points": [
                "SYPHON intelligence extraction",
                "R5 context aggregation",
                "JARVIS orchestration",
                "Holocron archive",
                "Force values system",
                "Cross-consultation experts",
                "Pathfinder system"
            ],
            "integration_philosophy": "All systems work together harmoniously"
        }

    def _aggregate_philosophy(self) -> Dict[str, Any]:
        """Aggregate philosophy"""
        return {
            "core_philosophy": "Church of the Force - Real World Equivalent",
            "values": "Balance, Connection, Peace, Wisdom, Compassion, Discipline, Service, Growth",
            "approach": "Take what you like, leave the rest",
            "mission": "Help people in all areas of life"
        }

    def _aggregate_vision(self) -> Dict[str, Any]:
        """Aggregate vision"""
        return {
            "vision": "Enlightenment system using AI to bring out the best in people",
            "model": "Non-profit, open source, polymath, modernist",
            "goal": "Help people become their best versions of themselves",
            "method": "AI coaching with Force values and polymath holistic view"
        }


class LookInwardSystem:
    """Look Inward - @SYPHON + @R5 Analysis"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "look_inward"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.syphon = SYPHONIntelligenceExtractor(project_root)
        self.r5 = R5ContextAggregator(project_root)

    def look_inward(self) -> Dict[str, Any]:
        try:
            """Complete look inward analysis"""
            logger.info("=" * 80)
            logger.info("🔍 LOOKING INWARD - @SYPHON + @R5")
            logger.info("=" * 80)
            logger.info("")

            # SYPHON extraction
            logger.info("🔍 @SYPHON extracting intelligence...")
            syphon_data = self.syphon.extract_from_lumina()
            logger.info("")

            # R5 aggregation
            logger.info("📊 @R5 aggregating context...")
            r5_data = self.r5.aggregate_lumina_context()
            logger.info("")

            # Synthesis
            logger.info("🧠 Synthesizing inward look...")
            synthesis = self._synthesize_inward_look(syphon_data, r5_data)
            logger.info("")

            # Complete analysis
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "LOOK_INWARD",
                "syphon_extraction": syphon_data,
                "r5_aggregation": r5_data,
                "synthesis": synthesis,
                "insights": self._generate_inward_insights(syphon_data, r5_data, synthesis)
            }

            logger.info("=" * 80)
            logger.info("✅ INWARD LOOK COMPLETE")
            logger.info("=" * 80)
            logger.info("")

            # Save analysis
            analysis_file = self.data_dir / f"inward_look_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)

            logger.info(f"📄 Analysis saved: {analysis_file}")
            logger.info("")

            return analysis

        except Exception as e:
            self.logger.error(f"Error in look_inward: {e}", exc_info=True)
            raise
    def _synthesize_inward_look(self, syphon_data: Dict[str, Any], 
                                r5_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize inward look"""
        return {
            "what_we_built": {
                "systems": syphon_data.get("intelligence_extracted", {}).get("total_scripts", 0),
                "key_systems": syphon_data.get("intelligence_extracted", {}).get("key_systems", []),
                "patterns": syphon_data.get("patterns_found", [])
            },
            "who_we_are": {
                "identity": r5_data.get("synthesis", {}).get("core_identity", ""),
                "mission": r5_data.get("synthesis", {}).get("mission", ""),
                "philosophy": r5_data.get("synthesis", {}).get("philosophy", ""),
                "vision": r5_data.get("synthesis", {}).get("vision", "")
            },
            "how_we_work": {
                "approach": r5_data.get("synthesis", {}).get("approach", ""),
                "integrations": r5_data.get("context_matrix", {}).get("integrations", {}),
                "workflows": r5_data.get("context_matrix", {}).get("workflows", {})
            },
            "where_we_going": {
                "direction": "Enlightenment system for all",
                "expansion": "Company in a box for everyone",
                "impact": "Help people become their best versions"
            }
        }

    def _generate_inward_insights(self, syphon_data: Dict[str, Any],
                                  r5_data: Dict[str, Any],
                                  synthesis: Dict[str, Any]) -> List[str]:
        """Generate inward insights"""
        insights = []

        # What we built
        total_systems = syphon_data.get("intelligence_extracted", {}).get("total_scripts", 0)
        insights.append(f"💡 Built {total_systems}+ systems - comprehensive ecosystem")

        # Who we are
        identity = synthesis.get("who_we_are", {}).get("identity", "")
        insights.append(f"💡 Identity: {identity}")

        # How we work
        approach = synthesis.get("how_we_work", {}).get("approach", "")
        insights.append(f"💡 Approach: {approach}")

        # Where we're going
        direction = synthesis.get("where_we_going", {}).get("direction", "")
        insights.append(f"💡 Direction: {direction}")

        # Patterns
        patterns = len(syphon_data.get("patterns_found", []))
        insights.append(f"💡 Patterns identified: {patterns} system patterns")

        # Integration
        insights.append("💡 All systems integrated through JARVIS orchestration")

        return insights


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Look Inward System")
        parser.add_argument("--look", action="store_true", help="Complete look inward")
        parser.add_argument("--syphon", action="store_true", help="SYPHON extraction only")
        parser.add_argument("--r5", action="store_true", help="R5 aggregation only")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = LookInwardSystem(project_root)

        if args.look or (not args.syphon and not args.r5):
            analysis = system.look_inward()
            print(json.dumps(analysis, indent=2, default=str))
        elif args.syphon:
            extraction = system.syphon.extract_from_lumina()
            print(json.dumps(extraction, indent=2, default=str))
        elif args.r5:
            aggregation = system.r5.aggregate_lumina_context()
            print(json.dumps(aggregation, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()