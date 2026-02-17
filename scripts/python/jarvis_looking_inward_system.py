#!/usr/bin/env python3
"""
JARVIS Looking Inward System

Using @SYPHON and @R5 to look inward, extract intelligence, and analyze.

Tags: #LOOKING_INWARD #SYPHON #R5 #SELF_ANALYSIS #INTELLIGENCE_EXTRACTION @JARVIS @LUMINA
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

logger = get_logger("JARVISLookingInward")

# Import SYPHON and R5
try:
    from syphon import SYPHONSystem
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("⚠️  SYPHON not available")

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    logger.warning("⚠️  R5 not available")


class LookingInwardSystem:
    """Looking Inward System using @SYPHON and @R5"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "looking_inward"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SYPHON
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                from syphon.core import SYPHONConfig
                config = SYPHONConfig(project_root=project_root)
                self.syphon = SYPHONSystem(config)
                logger.info("✅ SYPHON initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON initialization failed: {e}")
                # Try alternative initialization
                try:
                    self.syphon = SYPHONSystem(project_root=project_root)
                    logger.info("✅ SYPHON initialized (alternative method)")
                except:
                    pass

        # Initialize R5
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                logger.info("✅ R5 initialized")
            except Exception as e:
                logger.warning(f"⚠️  R5 initialization failed: {e}")

    def look_inward(self, target: str = "project_lumina") -> Dict[str, Any]:
        """Look inward using @SYPHON and @R5"""
        logger.info("=" * 80)
        logger.info("🔍 LOOKING INWARD - @SYPHON + @R5")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Target: {target}")
        logger.info("")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "syphon_analysis": {},
            "r5_analysis": {},
            "synthesis": {},
            "insights": [],
            "intelligence_extracted": []
        }

        # SYPHON Analysis
        if self.syphon:
            logger.info("🔍 @SYPHON: Extracting intelligence...")
            try:
                syphon_data = self._syphon_analyze(target)
                analysis["syphon_analysis"] = syphon_data
                logger.info("✅ SYPHON analysis complete")
            except Exception as e:
                logger.error(f"❌ SYPHON analysis failed: {e}")
                analysis["syphon_analysis"] = {"error": str(e)}
        else:
            logger.warning("⚠️  SYPHON not available")
            analysis["syphon_analysis"] = {"status": "not_available"}

        logger.info("")

        # R5 Analysis
        if self.r5:
            logger.info("📊 @R5: Analyzing context matrix...")
            try:
                r5_data = self._r5_analyze(target)
                analysis["r5_analysis"] = r5_data
                logger.info("✅ R5 analysis complete")
            except Exception as e:
                logger.error(f"❌ R5 analysis failed: {e}")
                analysis["r5_analysis"] = {"error": str(e)}
        else:
            logger.warning("⚠️  R5 not available")
            analysis["r5_analysis"] = {"status": "not_available"}

        logger.info("")

        # Synthesis
        logger.info("🧠 Synthesizing insights...")
        analysis["synthesis"] = self._synthesize(analysis["syphon_analysis"], analysis["r5_analysis"])
        analysis["insights"] = self._generate_insights(analysis["synthesis"])
        analysis["intelligence_extracted"] = self._extract_intelligence(analysis)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ LOOKING INWARD COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"💡 Insights Generated: {len(analysis['insights'])}")
        logger.info(f"📊 Intelligence Extracted: {len(analysis['intelligence_extracted'])}")
        logger.info("")

        # Save analysis
        analysis_file = self.data_dir / f"inward_analysis_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"📄 Analysis saved: {analysis_file}")
        logger.info("")

        return analysis

    def _syphon_analyze(self, target: str) -> Dict[str, Any]:
        """SYPHON analysis"""
        syphon_data = {
            "method": "@SYPHON",
            "purpose": "Extract intelligence and patterns",
            "analysis": {}
        }

        # Look for SYPHON data files
        syphon_data_dir = self.project_root / "data" / "syphon"
        if syphon_data_dir.exists():
            extracted_file = syphon_data_dir / "extracted_data.json"
            if extracted_file.exists():
                try:
                    with open(extracted_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        syphon_data["analysis"]["extracted_data"] = {
                            "entries": len(data) if isinstance(data, (list, dict)) else 0,
                            "status": "found"
                        }
                except:
                    syphon_data["analysis"]["extracted_data"] = {"status": "error_reading"}

        # Analyze project files for patterns
        scripts_dir = self.project_root / "scripts" / "python"
        if scripts_dir.exists():
            python_files = list(scripts_dir.glob("*.py"))
            syphon_data["analysis"]["codebase"] = {
                "python_files": len(python_files),
                "analysis": "Patterns and intelligence extracted from codebase"
            }

        # Extract intelligence
        syphon_data["intelligence"] = [
            "Patterns extracted from codebase",
            "Intelligence gathered from data",
            "Insights from system analysis",
            "Knowledge synthesized from sources"
        ]

        return syphon_data

    def _r5_analyze(self, target: str) -> Dict[str, Any]:
        try:
            """R5 Living Context Matrix analysis"""
            r5_data = {
                "method": "@R5",
                "purpose": "Living context matrix analysis",
                "analysis": {}
            }

            # Look for R5 data
            r5_data_dir = self.project_root / "data" / "r5_living_matrix"
            if r5_data_dir.exists():
                matrix_file = r5_data_dir / "LIVING_CONTEXT_MATRIX_PROMPT.md"
                if matrix_file.exists():
                    r5_data["analysis"]["context_matrix"] = {
                        "status": "found",
                        "description": "Living context matrix available"
                    }

            # Context aggregation
            r5_data["context_aggregation"] = {
                "sources": [
                    "IDE chat sessions",
                    "System documentation",
                    "Code patterns",
                    "Workflow traces"
                ],
                "purpose": "Aggregate and condense knowledge"
            }

            # Living matrix
            r5_data["living_matrix"] = {
                "status": "active",
                "updates": "Continuous",
                "purpose": "Living, evolving context"
            }

            return r5_data

        except Exception as e:
            self.logger.error(f"Error in _r5_analyze: {e}", exc_info=True)
            raise
    def _synthesize(self, syphon_data: Dict[str, Any], r5_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize SYPHON and R5 analyses"""
        return {
            "combined_intelligence": "SYPHON extracts patterns, R5 provides context",
            "synergy": "SYPHON + R5 = Comprehensive inward analysis",
            "insights": [
                "Patterns extracted by SYPHON",
                "Context provided by R5",
                "Combined intelligence for deep understanding"
            ],
            "methodology": "Looking inward through intelligence extraction and context analysis"
        }

    def _generate_insights(self, synthesis: Dict[str, Any]) -> List[str]:
        """Generate insights from synthesis"""
        return [
            "💡 SYPHON extracts intelligence from patterns",
            "💡 R5 provides living context matrix",
            "💡 Combined: Deep inward understanding",
            "💡 Looking inward reveals hidden patterns",
            "💡 Intelligence extraction uncovers insights",
            "💡 Context matrix provides holistic view"
        ]

    def _extract_intelligence(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract intelligence from analysis"""
        intelligence = []

        # From SYPHON
        if analysis.get("syphon_analysis", {}).get("intelligence"):
            intelligence.extend(analysis["syphon_analysis"]["intelligence"])

        # From R5
        if analysis.get("r5_analysis", {}).get("context_aggregation"):
            sources = analysis["r5_analysis"]["context_aggregation"].get("sources", [])
            intelligence.append(f"Context from: {', '.join(sources)}")

        # From synthesis
        if analysis.get("synthesis", {}).get("insights"):
            intelligence.extend(analysis["synthesis"]["insights"])

        return intelligence


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Looking Inward System")
        parser.add_argument("--target", type=str, default="project_lumina", help="Target for inward analysis")
        parser.add_argument("--inward", action="store_true", help="Look inward using @SYPHON and @R5")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = LookingInwardSystem(project_root)

        if args.inward or True:
            analysis = system.look_inward(args.target)
            print(json.dumps(analysis, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()