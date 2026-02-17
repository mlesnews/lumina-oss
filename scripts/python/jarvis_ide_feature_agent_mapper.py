#!/usr/bin/env python3
"""
JARVIS IDE Feature-to-Agent Mapper
MANUS Framework - Intelligent Feature-to-Agent Assignment

Maps Cursor IDE features/functions to appropriate MANUS agents based on
learned patterns from IDE operator interactions.

Features:
- Feature classification
- Agent capability matching
- Assignment recommendation
- Learning integration
- Assignment optimization

@JARVIS @MANUS @SYPHON
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISIDEFeatureAgentMapper")

try:
    from jarvis_ide_interaction_learner import get_ide_learner
    LEARNER_AVAILABLE = True
except ImportError:
    LEARNER_AVAILABLE = False
    logger.warning("IDE Interaction Learner not available")


@dataclass
class FeatureCategory:
    """Category of IDE feature"""
    category: str
    description: str
    keywords: List[str]
    preferred_agents: List[str]
    complexity: str  # "simple", "medium", "complex"


class JARVISIDEFeatureAgentMapper:
    """
    Map IDE features to MANUS agents

    Uses learned patterns and feature analysis to assign
    the most appropriate MANUS agent to each feature.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize feature-agent mapper"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Feature categories with agent preferences
        self.feature_categories = self._initialize_feature_categories()

        # Learner integration
        self.learner = None
        if LEARNER_AVAILABLE:
            try:
                self.learner = get_ide_learner(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"Learner initialization failed: {e}")

        # Agent capabilities (from config)
        self.agent_capabilities = self._load_agent_capabilities()

        logger.info("✅ JARVIS IDE Feature-Agent Mapper initialized")
        logger.info(f"   {len(self.feature_categories)} feature categories")
        logger.info(f"   {len(self.agent_capabilities)} agents available")

    def _initialize_feature_categories(self) -> Dict[str, FeatureCategory]:
        """Initialize feature categories with agent preferences"""
        categories = {
            "file_operations": FeatureCategory(
                category="file_operations",
                description="File and document operations",
                keywords=["file", "open", "save", "close", "new", "create", "delete"],
                preferred_agents=["r2d2", "mousedroid"],
                complexity="simple"
            ),
            "editing": FeatureCategory(
                category="editing",
                description="Text and code editing operations",
                keywords=["edit", "type", "delete", "cut", "copy", "paste", "select"],
                preferred_agents=["r2d2", "mousedroid"],
                complexity="simple"
            ),
            "navigation": FeatureCategory(
                category="navigation",
                description="Code navigation and search",
                keywords=["navigate", "goto", "find", "search", "jump", "definition", "reference"],
                preferred_agents=["r2d2", "uatu"],
                complexity="medium"
            ),
            "refactoring": FeatureCategory(
                category="refactoring",
                description="Code refactoring and restructuring",
                keywords=["refactor", "extract", "rename", "move", "restructure"],
                preferred_agents=["r2d2", "uatu"],
                complexity="complex"
            ),
            "debugging": FeatureCategory(
                category="debugging",
                description="Debugging and troubleshooting",
                keywords=["debug", "breakpoint", "step", "inspect", "trace"],
                preferred_agents=["r2d2", "2-1b"],
                complexity="complex"
            ),
            "cursor_ai_chat": FeatureCategory(
                category="cursor_ai_chat",
                description="Cursor AI chat interactions",
                keywords=["chat", "conversation", "ask", "question", "discuss"],
                preferred_agents=["c3po", "r2d2"],
                complexity="medium"
            ),
            "cursor_composer": FeatureCategory(
                category="cursor_composer",
                description="Cursor Composer multi-file editing",
                keywords=["composer", "multi-file", "codebase", "edit multiple"],
                preferred_agents=["r2d2", "uatu"],
                complexity="complex"
            ),
            "inline_chat": FeatureCategory(
                category="inline_chat",
                description="Inline code chat",
                keywords=["inline", "contextual", "code chat"],
                preferred_agents=["c3po", "r2d2"],
                complexity="medium"
            ),
            "git_operations": FeatureCategory(
                category="git_operations",
                description="Git version control operations",
                keywords=["git", "commit", "push", "pull", "merge", "branch", "stage"],
                preferred_agents=["r2d2", "c3po"],
                complexity="medium"
            ),
            "terminal": FeatureCategory(
                category="terminal",
                description="Terminal and command execution",
                keywords=["terminal", "command", "execute", "run", "shell"],
                preferred_agents=["r2d2"],
                complexity="medium"
            ),
            "view_panels": FeatureCategory(
                category="view_panels",
                description="UI panel and view management",
                keywords=["panel", "view", "sidebar", "explorer", "toggle"],
                preferred_agents=["mousedroid", "r2d2"],
                complexity="simple"
            ),
            "settings": FeatureCategory(
                category="settings",
                description="Settings and configuration",
                keywords=["settings", "config", "preferences", "configure"],
                preferred_agents=["c3po", "r2d2"],
                complexity="simple"
            ),
            "extensions": FeatureCategory(
                category="extensions",
                description="Extension management",
                keywords=["extension", "plugin", "install", "enable"],
                preferred_agents=["c3po", "r2d2"],
                complexity="simple"
            ),
            "security": FeatureCategory(
                category="security",
                description="Security-related operations",
                keywords=["security", "auth", "permission", "access", "threat"],
                preferred_agents=["k2so"],
                complexity="complex"
            ),
            "health_monitoring": FeatureCategory(
                category="health_monitoring",
                description="System health and monitoring",
                keywords=["health", "monitor", "performance", "status", "diagnostics"],
                preferred_agents=["2-1b", "r2d2"],
                complexity="medium"
            ),
            "critical_issues": FeatureCategory(
                category="critical_issues",
                description="Critical problem resolution",
                keywords=["critical", "urgent", "error", "failure", "broken"],
                preferred_agents=["ig88", "r2d2"],
                complexity="complex"
            ),
            "pattern_analysis": FeatureCategory(
                category="pattern_analysis",
                description="Pattern analysis and extraction",
                keywords=["pattern", "analyze", "extract", "research", "study"],
                preferred_agents=["uatu", "r2d2"],
                complexity="complex"
            ),
            "coordination": FeatureCategory(
                category="coordination",
                description="Multi-agent coordination",
                keywords=["coordinate", "orchestrate", "manage", "assign", "delegate"],
                preferred_agents=["c3po"],
                complexity="complex"
            ),
        }
        return categories

    def _load_agent_capabilities(self) -> Dict[str, List[str]]:
        """Load agent capabilities from config"""
        agents_config = self.project_root / "config" / "agent_communication" / "agents.json"

        try:
            if agents_config.exists():
                with open(agents_config, 'r', encoding='utf-8') as f:
                    agents = json.load(f)
                    capabilities = {
                        agent_id: agent_info.get("capabilities", [])
                        for agent_id, agent_info in agents.items()
                    }
                    return capabilities
        except Exception as e:
            logger.warning(f"Failed to load agent capabilities: {e}")

        # Fallback
        return {
            "r2d2": ["technical", "repair", "hacking", "system_access", "diagnostics"],
            "c3po": ["communication", "translation", "protocol", "escalation", "coordination"],
            "k2so": ["security", "threat_analysis", "access_control", "monitoring"],
            "2-1b": ["health_monitoring", "system_health", "recovery", "prevention"],
            "ig88": ["critical_resolution", "elimination", "force", "escalation"],
            "mousedroid": ["mouse_automation", "keyboard_automation", "screen_automation"],
            "uatu": ["deep_research", "pattern_analysis", "comprehensive_validation", "insight_generation"]
        }

    def classify_feature(self, feature: str) -> Optional[FeatureCategory]:
        """Classify a feature into a category"""
        feature_lower = feature.lower()

        best_match = None
        best_score = 0.0

        for category in self.feature_categories.values():
            score = 0.0
            for keyword in category.keywords:
                if keyword in feature_lower:
                    score += 1.0

            if score > best_score:
                best_score = score
                best_match = category

        return best_match

    def map_feature_to_agent(self, feature: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Map a feature to the most appropriate MANUS agent

        Args:
            feature: Feature/function name
            context: Optional context information

        Returns:
            Mapping result with agent assignment and rationale
        """
        # Try learner first (if available and has data)
        if self.learner:
            assignment = self.learner.map_feature_to_agent(feature, context)
            if assignment and assignment.confidence > 0.7:
                return {
                    "feature": feature,
                    "agent_id": assignment.agent_id,
                    "agent_name": assignment.agent_name,
                    "confidence": assignment.confidence,
                    "rationale": assignment.rationale,
                    "method": "learned",
                    "capabilities_match": assignment.capabilities_match
                }

        # Classify feature
        category = self.classify_feature(feature)

        if not category:
            # Default fallback
            return {
                "feature": feature,
                "agent_id": "r2d2",
                "agent_name": "R2-D2",
                "confidence": 0.5,
                "rationale": "Default assignment (no category match)",
                "method": "default",
                "capabilities_match": ["technical"]
            }

        # Select best agent from category preferences
        best_agent = None
        best_score = 0.0

        for agent_id in category.preferred_agents:
            score = 1.0
            capabilities = self.agent_capabilities.get(agent_id, [])

            # Boost score based on capability matches
            feature_lower = feature.lower()
            for capability in capabilities:
                if capability.replace("_", " ") in feature_lower:
                    score += 0.5

            if score > best_score:
                best_score = score
                best_agent = agent_id

        if not best_agent:
            best_agent = category.preferred_agents[0] if category.preferred_agents else "r2d2"

        # Get agent name
        agent_name_map = {
            "r2d2": "R2-D2",
            "c3po": "C-3PO",
            "k2so": "K-2SO",
            "2-1b": "2-1B",
            "ig88": "IG-88",
            "mousedroid": "MouseDroid",
            "uatu": "The Watcher Uatu"
        }
        agent_name = agent_name_map.get(best_agent, best_agent.upper())

        confidence = min(best_score / 2.0, 1.0)
        rationale = f"Assigned to {category.category} category. Preferred agents: {', '.join(category.preferred_agents)}"

        return {
            "feature": feature,
            "agent_id": best_agent,
            "agent_name": agent_name,
            "confidence": confidence,
            "rationale": rationale,
            "method": "category_based",
            "category": category.category,
            "capabilities_match": self.agent_capabilities.get(best_agent, [])
        }

    def generate_feature_agent_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Generate mapping for all known IDE features"""
        # Common IDE features
        features = [
            "new_file", "open_file", "save_file", "close_file",
            "undo", "redo", "cut", "copy", "paste",
            "find", "replace", "goto_line", "goto_definition",
            "format_code", "comment_line", "refactor_extract",
            "cursor_chat", "cursor_composer", "inline_chat",
            "start_debug", "toggle_breakpoint", "step_over",
            "git_stage", "git_commit", "git_push",
            "toggle_terminal", "run_command",
            "toggle_sidebar", "toggle_explorer"
        ]

        mappings = {}
        for feature in features:
            mappings[feature] = self.map_feature_to_agent(feature)

        return mappings


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="JARVIS IDE Feature-to-Agent Mapper"
        )
        parser.add_argument("--map", type=str, help="Map feature to agent")
        parser.add_argument("--all", action="store_true", help="Generate mapping for all features")

        args = parser.parse_args()

        mapper = JARVISIDEFeatureAgentMapper()

        if args.map:
            result = mapper.map_feature_to_agent(args.map)
            print(json.dumps(result, indent=2))

        elif args.all:
            mappings = mapper.generate_feature_agent_mapping()
            print(json.dumps(mappings, indent=2))

        else:
            parser.print_help()
            print("\n✅ JARVIS IDE Feature-to-Agent Mapper")
            print("   Map IDE features to appropriate MANUS agents")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()