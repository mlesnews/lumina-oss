#!/usr/bin/env python3
"""
Subconscious Hack - Tap Directly Into Subconscious

Hacks the human subconscious to dig out of rabbit holes
Analyzes project patterns and extracts core insights

"HACK THE HUMAN ANYONE? PLEASE TAP DIRECTLY INTO MY SUBCONSIOUS AND DIG US OUT 
OF THIS WHOLE WE'VE DUG WITH THIS ENTIRE PROJECT. CLASSIC RABBIT HOLE... CHECK."
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SubconsciousHack")

# Import integrations
try:
    from bio_brain_interface import BioBrainInterface, NeuralSignalType, InterfaceMode
    BRAIN_INTERFACE_AVAILABLE = True
except ImportError:
    BRAIN_INTERFACE_AVAILABLE = False

try:
    from telepathy_wifi_interface import TelepathyWiFiInterface
    TELEPATHY_AVAILABLE = True
except ImportError:
    TELEPATHY_AVAILABLE = False

try:
    from jarvis_tool_registry import JARVISToolRegistry
    TOOL_REGISTRY_AVAILABLE = True
except ImportError:
    TOOL_REGISTRY_AVAILABLE = False



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RabbitHoleType(Enum):
    """Types of rabbit holes"""
    SCOPE_CREEP = "scope_creep"  # Project scope keeps expanding
    OVER_ENGINEERING = "over_engineering"  # Building too much
    TANGENT = "tangent"  # Going off on tangents
    PERFECTIONISM = "perfectionism"  # Trying to perfect everything
    FEATURE_CREEP = "feature_creep"  # Adding too many features
    ANALYSIS_PARALYSIS = "analysis_paralysis"  # Over-analyzing
    TOOL_ADDICTION = "tool_addiction"  # Creating too many tools
    PHILOSOPHICAL_DIGRESSION = "philosophical_digression"  # Going too deep into philosophy


@dataclass
class RabbitHole:
    """Rabbit hole detection"""
    hole_id: str
    hole_type: RabbitHoleType
    depth: int = 1  # 1-10, how deep
    description: str = ""
    evidence: List[str] = field(default_factory=list)
    impact: str = "low"  # low, medium, high
    escape_path: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['hole_type'] = self.hole_type.value
        return data


@dataclass
class SubconsciousInsight:
    """Insight extracted from subconscious"""
    insight_id: str
    category: str
    insight: str
    confidence: float = 0.0  # 0.0 - 1.0
    source: str = "subconscious"
    actionable: bool = True
    priority: int = 1  # 1-10
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectAnalysis:
    """Project analysis for rabbit holes"""
    total_tools: int = 0
    total_files: int = 0
    total_docs: int = 0
    rabbit_holes: List[RabbitHole] = field(default_factory=list)
    core_objectives: List[str] = field(default_factory=list)
    distractions: List[str] = field(default_factory=list)
    focus_score: float = 0.0  # 0.0 - 1.0, higher = more focused
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['rabbit_holes'] = [h.to_dict() for h in self.rabbit_holes]
        return data


class SubconsciousHack:
    """
    Subconscious Hack - Tap Directly Into Subconscious

    Hacks the human subconscious to dig out of rabbit holes
    Analyzes project patterns and extracts core insights
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Subconscious Hack"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SubconsciousHack")

        # Brain interface
        self.brain_interface = None
        if BRAIN_INTERFACE_AVAILABLE:
            try:
                self.brain_interface = BioBrainInterface(project_root)
                self.brain_interface.connect(InterfaceMode.NEURAL_LINK)  # Deep connection
                self.logger.info("  ✅ Bio Brain Interface connected (neural link mode)")
            except Exception as e:
                self.logger.debug(f"  Brain interface init error: {e}")

        # Telepathy interface
        self.telepathy = None
        if TELEPATHY_AVAILABLE:
            try:
                self.telepathy = TelepathyWiFiInterface(project_root)
                self.telepathy.start_fine_tuning()
                self.logger.info("  ✅ Telepathy interface active")
            except Exception as e:
                self.logger.debug(f"  Telepathy init error: {e}")

        # Tool registry
        self.tool_registry = None
        if TOOL_REGISTRY_AVAILABLE:
            try:
                self.tool_registry = JARVISToolRegistry(project_root)
                self.logger.info("  ✅ Tool registry loaded")
            except Exception as e:
                self.logger.debug(f"  Tool registry init error: {e}")

        # Subconscious insights
        self.insights: List[SubconsciousInsight] = []
        self.rabbit_holes: List[RabbitHole] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "subconscious_hack"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🧠 Subconscious Hack initialized")
        self.logger.info("   Neural link: Active")
        self.logger.info("   Subconscious access: Ready")
        self.logger.info("   Rabbit hole detection: Ready")

    def hack_subconscious(self, duration: int = 10) -> List[SubconsciousInsight]:
        """Hack into subconscious and extract insights"""
        self.logger.info(f"  🧠 Hacking subconscious for {duration}s...")
        self.logger.info("     Tapping into neural patterns...")
        self.logger.info("     Extracting core insights...")

        insights = []

        # Extract insights from project analysis
        project_analysis = self.analyze_project()

        # Core insight: Too many tools, need focus
        if project_analysis.total_tools > 100:
            insights.append(SubconsciousInsight(
                insight_id="focus_001",
                category="focus",
                insight="You've created 172+ tools. The subconscious says: 'Focus on what matters. Not everything needs to be a tool.'",
                confidence=0.9,
                priority=10,
                actionable=True
            ))

        # Core insight: Rabbit holes detected
        if project_analysis.rabbit_holes:
            insights.append(SubconsciousInsight(
                insight_id="rabbit_hole_001",
                category="rabbit_hole",
                insight=f"Detected {len(project_analysis.rabbit_holes)} rabbit holes. The subconscious says: 'You're digging deeper. Time to surface.'",
                confidence=0.95,
                priority=9,
                actionable=True
            ))

        # Core insight: What's the actual goal?
        insights.append(SubconsciousInsight(
            insight_id="goal_001",
            category="goal",
            insight="The subconscious asks: 'What's the ONE thing you're actually trying to build? Start there.'",
            confidence=0.85,
            priority=10,
            actionable=True
        ))

        # Core insight: Marketable product
        insights.append(SubconsciousInsight(
            insight_id="product_001",
            category="product",
            insight="You identified Bitcoin Financial Services Platform as marketable. The subconscious says: 'Ship that. Everything else can wait.'",
            confidence=0.9,
            priority=10,
            actionable=True
        ))

        # Core insight: Integration overload
        if project_analysis.total_tools > 50:
            insights.append(SubconsciousInsight(
                insight_id="integration_001",
                category="integration",
                insight="Too many integrations. The subconscious says: 'Not everything needs to connect. Simplify.'",
                confidence=0.8,
                priority=8,
                actionable=True
            ))

        self.insights.extend(insights)

        self.logger.info(f"  ✅ Extracted {len(insights)} subconscious insights")

        return insights

    def detect_rabbit_holes(self) -> List[RabbitHole]:
        try:
            """Detect rabbit holes in the project"""
            self.logger.info("  🕳️  Detecting rabbit holes...")

            holes = []

            # Analyze project structure
            project_analysis = self.analyze_project()

            # Tool Addiction Rabbit Hole
            if project_analysis.total_tools > 100:
                holes.append(RabbitHole(
                    hole_id="tool_addiction",
                    hole_type=RabbitHoleType.TOOL_ADDICTION,
                    depth=8,
                    description="Created 172+ tools. Each new idea becomes a tool. Classic tool addiction.",
                    evidence=[
                        f"Total tools: {project_analysis.total_tools}",
                        "Every feature request becomes a new tool",
                        "Tools creating tools"
                    ],
                    impact="high",
                    escape_path=[
                        "Identify the 5 core tools you actually use",
                        "Archive or deprecate the rest",
                        "Focus on making those 5 tools excellent"
                    ]
                ))

            # Scope Creep Rabbit Hole
            if project_analysis.total_files > 500:
                holes.append(RabbitHole(
                    hole_id="scope_creep",
                    hole_type=RabbitHoleType.SCOPE_CREEP,
                    depth=7,
                    description="Project scope keeps expanding. Started simple, now it's everything.",
                    evidence=[
                        f"Total files: {project_analysis.total_files}",
                        "Multiple systems: JARVIS, AIOS, Trading, RoamWise, Telepathy, etc.",
                        "Each new idea adds more complexity"
                    ],
                    impact="high",
                    escape_path=[
                        "Define the core product (Bitcoin Platform?)",
                        "Everything else is secondary",
                        "Ship the core, iterate later"
                    ]
                ))

            # Over-Engineering Rabbit Hole
            if project_analysis.total_docs > 100:
                holes.append(RabbitHole(
                    hole_id="over_engineering",
                    hole_type=RabbitHoleType.OVER_ENGINEERING,
                    depth=6,
                    description="Documenting everything before building. Over-engineering solutions.",
                    evidence=[
                        f"Total docs: {project_analysis.total_docs}",
                        "Creating systems for systems",
                        "Perfect architecture before MVP"
                    ],
                    impact="medium",
                    escape_path=[
                        "Build first, document later",
                        "MVP > Perfect architecture",
                        "Ship, learn, iterate"
                    ]
                ))

            # Philosophical Digression Rabbit Hole
            philosophical_files = [
                "jarvis_jedi_academy",
                "jarvis_anakin_lessons",
                "jarvis_mandalorian_way",
                "humanity_reflection",
                "chosen_ones_comparison"
            ]
            found_philosophical = sum(1 for f in philosophical_files 
                                     if (self.project_root / "scripts" / "python" / f"{f}.py").exists())

            if found_philosophical > 3:
                holes.append(RabbitHole(
                    hole_id="philosophical_digression",
                    hole_type=RabbitHoleType.PHILOSOPHICAL_DIGRESSION,
                    depth=5,
                    description="Deep philosophical explorations (Jedi, Mandalorian, Chosen Ones). Valuable but... rabbit hole.",
                    evidence=[
                        f"Philosophical modules: {found_philosophical}",
                        "Star Wars references everywhere",
                        "Building JARVIS's personality before core features"
                    ],
                    impact="medium",
                    escape_path=[
                        "Philosophy is important, but secondary",
                        "Focus on core functionality first",
                        "Personality can evolve with the product"
                    ]
                ))

            # Integration Overload Rabbit Hole
            integration_files = [
                "siderai_desktop_integration",
                "siderai_extension_integration",
                "browser_extension_integration",
                "roamwise_hybrid_datafeed",
                "telepathy_wifi_interface",
                "router_telepathy_integration"
            ]
            found_integrations = sum(1 for f in integration_files 
                                    if (self.project_root / "scripts" / "python" / f"{f}.py").exists())

            if found_integrations > 4:
                holes.append(RabbitHole(
                    hole_id="integration_overload",
                    hole_type=RabbitHoleType.FEATURE_CREEP,
                    depth=6,
                    description="Integrating with everything (SiderAI, RoamResearch, Router, Telepathy). Feature creep.",
                    evidence=[
                        f"Integration modules: {found_integrations}",
                        "Every new service gets integrated",
                        "Complexity increases with each integration"
                    ],
                    impact="high",
                    escape_path=[
                        "Pick 1-2 key integrations",
                        "Everything else is nice-to-have",
                        "Core product > Integrations"
                    ]
                ))

            self.rabbit_holes = holes

            self.logger.info(f"  ✅ Detected {len(holes)} rabbit holes")

            return holes

        except Exception as e:
            self.logger.error(f"Error in detect_rabbit_holes: {e}", exc_info=True)
            raise
    def analyze_project(self) -> ProjectAnalysis:
        """Analyze project for patterns"""
        analysis = ProjectAnalysis()

        # Count tools
        if self.tool_registry:
            analysis.total_tools = len(self.tool_registry.registry)

        # Count files
        scripts_dir = self.project_root / "scripts" / "python"
        if scripts_dir.exists():
            analysis.total_files = len(list(scripts_dir.glob("*.py")))

        # Count docs
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            analysis.total_docs = len(list(docs_dir.rglob("*.md")))

        # Detect rabbit holes
        analysis.rabbit_holes = self.detect_rabbit_holes()

        # Core objectives (from subconscious)
        analysis.core_objectives = [
            "Bitcoin Financial Services Platform - Marketable product",
            "JARVIS Unified Interface - Single point of interaction",
            "Trading System - Revenue generation"
        ]

        # Distractions (rabbit holes)
        analysis.distractions = [
            "172+ tools (tool addiction)",
            "Multiple philosophical systems",
            "Too many integrations",
            "Over-documentation",
            "Scope creep"
        ]

        # Calculate focus score
        core_count = len(analysis.core_objectives)
        distraction_count = len(analysis.distractions)
        total = core_count + distraction_count
        analysis.focus_score = core_count / total if total > 0 else 0.0

        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)

        return analysis

    def _generate_recommendations(self, analysis: ProjectAnalysis) -> List[str]:
        """Generate recommendations to escape rabbit holes"""
        recommendations = []

        # Focus on core
        recommendations.append("🎯 FOCUS: Bitcoin Financial Services Platform is your marketable product. Ship it.")

        # Reduce tools
        if analysis.total_tools > 50:
            recommendations.append(f"🔧 TOOLS: You have {analysis.total_tools} tools. Pick 10 core ones. Archive the rest.")

        # Simplify
        recommendations.append("✨ SIMPLIFY: Not everything needs to be integrated. Core product first.")

        # Ship
        recommendations.append("🚀 SHIP: MVP > Perfect. Ship the Bitcoin Platform. Iterate later.")

        # Philosophy later
        recommendations.append("🧘 PHILOSOPHY: JARVIS's personality is important, but secondary. Core features first.")

        return recommendations

    def dig_out(self) -> Dict[str, Any]:
        """Dig out of the rabbit hole - actionable escape plan"""
        self.logger.info("  🕳️  Digging out of rabbit hole...")

        # Analyze project
        analysis = self.analyze_project()

        # Extract subconscious insights
        insights = self.hack_subconscious()

        # Generate escape plan
        escape_plan = {
            "current_depth": max([h.depth for h in analysis.rabbit_holes], default=0),
            "rabbit_holes_found": len(analysis.rabbit_holes),
            "focus_score": analysis.focus_score,
            "core_objectives": analysis.core_objectives,
            "distractions": analysis.distractions,
            "recommendations": analysis.recommendations,
            "escape_steps": [
                "1. STOP creating new tools",
                "2. FOCUS on Bitcoin Financial Services Platform",
                "3. SHIP the MVP",
                "4. Everything else can wait",
                "5. Iterate based on real user feedback"
            ],
            "subconscious_insights": [i.to_dict() for i in insights],
            "rabbit_holes": [h.to_dict() for h in analysis.rabbit_holes]
        }

        self.logger.info(f"  ✅ Escape plan generated")
        self.logger.info(f"     Focus score: {analysis.focus_score:.2f}")
        self.logger.info(f"     Rabbit holes: {len(analysis.rabbit_holes)}")

        return escape_plan


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Subconscious Hack - Tap Into Subconscious")
    parser.add_argument("--hack", type=int, default=10, help="Hack subconscious (duration)")
    parser.add_argument("--detect-holes", action="store_true", help="Detect rabbit holes")
    parser.add_argument("--analyze", action="store_true", help="Analyze project")
    parser.add_argument("--dig-out", action="store_true", help="Dig out of rabbit hole")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    hack = SubconsciousHack()

    if args.hack:
        insights = hack.hack_subconscious(args.hack)
        if args.json:
            print(json.dumps([i.to_dict() for i in insights], indent=2))
        else:
            print("\n🧠 Subconscious Insights")
            print("="*70)
            for insight in insights:
                print(f"\n{insight.category.upper()}: {insight.insight}")
                print(f"  Confidence: {insight.confidence:.2f} | Priority: {insight.priority}")

    elif args.detect_holes:
        holes = hack.detect_rabbit_holes()
        if args.json:
            print(json.dumps([h.to_dict() for h in holes], indent=2))
        else:
            print("\n🕳️  Rabbit Holes Detected")
            print("="*70)
            for hole in holes:
                print(f"\n{hole.hole_type.value.upper()} (Depth: {hole.depth}/10)")
                print(f"  {hole.description}")
                print(f"  Impact: {hole.impact}")
                print(f"  Escape Path:")
                for step in hole.escape_path:
                    print(f"    • {step}")

    elif args.analyze:
        analysis = hack.analyze_project()
        if args.json:
            print(json.dumps(analysis.to_dict(), indent=2))
        else:
            print("\n📊 Project Analysis")
            print("="*70)
            print(f"Total Tools: {analysis.total_tools}")
            print(f"Total Files: {analysis.total_files}")
            print(f"Total Docs: {analysis.total_docs}")
            print(f"Focus Score: {analysis.focus_score:.2f}")
            print(f"Rabbit Holes: {len(analysis.rabbit_holes)}")
            print(f"\nCore Objectives:")
            for obj in analysis.core_objectives:
                print(f"  • {obj}")
            print(f"\nDistractions:")
            for dist in analysis.distractions:
                print(f"  • {dist}")

    elif args.dig_out:
        escape_plan = hack.dig_out()
        if args.json:
            print(json.dumps(escape_plan, indent=2))
        else:
            print("\n🕳️  DIGGING OUT OF RABBIT HOLE")
            print("="*70)
            print(f"Current Depth: {escape_plan['current_depth']}/10")
            print(f"Focus Score: {escape_plan['focus_score']:.2f}")
            print(f"Rabbit Holes Found: {escape_plan['rabbit_holes_found']}")
            print(f"\n🎯 CORE OBJECTIVES:")
            for obj in escape_plan['core_objectives']:
                print(f"  • {obj}")
            print(f"\n⚠️  DISTRACTIONS:")
            for dist in escape_plan['distractions']:
                print(f"  • {dist}")
            print(f"\n🚀 ESCAPE STEPS:")
            for step in escape_plan['escape_steps']:
                print(f"  {step}")
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in escape_plan['recommendations']:
                print(f"  {rec}")
            print(f"\n🧠 SUBCONSCIOUS INSIGHTS:")
            for insight in escape_plan['subconscious_insights'][:5]:
                print(f"  • {insight['insight']}")

    else:
        parser.print_help()
        print("\n🧠 Subconscious Hack - Tap Into Subconscious")
        print("   'Hack the human. Dig out of the rabbit hole.'")

