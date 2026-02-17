#!/usr/bin/env python3
"""
Dynamic Tag Scaling System - @EVO

All tag definitions (@RR, @DTN, @DOIT, etc.) now use @DYNAMICALLY-SCALING-MODULE logic
instead of fixed static solutions. Tags evolve, adapt, and scale based on context,
system load, effectiveness metrics, and real-time conditions.

@DTN = "Do The Needful" - Execute what's needed with dynamic scaling

Tags: #DYNAMIC_SCALING #EVO #TAG_SYSTEM #ADAPTIVE #EVOLUTIONARY @JARVIS @LUMINA @PEAK @DTN @EVO
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import math

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DynamicTagScaling")


class ScalingFactor(Enum):
    """Dynamic scaling factors"""
    MINIMAL = 0.1  # Minimal response
    REDUCED = 0.5  # Reduced capacity
    NORMAL = 1.0  # Normal operation
    ELEVATED = 1.5  # Elevated response
    MAXIMUM = 2.0  # Maximum response
    CRITICAL = 3.0  # Critical emergency


@dataclass
class DynamicTagDefinition:
    """Dynamic tag definition with scaling logic"""
    tag: str
    base_definition: str
    scaling_rules: Dict[str, Any] = field(default_factory=dict)
    context_adaptations: Dict[str, str] = field(default_factory=dict)
    effectiveness_history: List[float] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 0.0
    current_scale_factor: float = 1.0
    last_updated: str = ""
    evolution_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TagScalingContext:
    """Context for tag scaling decisions"""
    system_load: float = 0.0  # 0.0 - 1.0
    urgency: float = 0.0  # 0.0 - 1.0
    resource_availability: float = 1.0  # 0.0 - 1.0
    historical_effectiveness: float = 0.0  # 0.0 - 1.0
    tag_combinations: List[str] = field(default_factory=list)
    current_conditions: Dict[str, Any] = field(default_factory=dict)


class DynamicTagScalingSystem:
    """
    Dynamic Tag Scaling System - @EVO

    All tags use dynamically-scaling-module logic instead of fixed static solutions.
    Tags evolve, adapt, and scale based on real-time conditions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize dynamic tag scaling system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "dynamic_tag_scaling"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.definitions_file = self.data_dir / "tag_definitions.json"
        self.scaling_history_file = self.data_dir / "scaling_history.json"

        # Tag definitions
        self.tag_definitions: Dict[str, DynamicTagDefinition] = {}

        # Load existing definitions
        self._load_definitions()

        # Initialize default tags with dynamic scaling
        self._initialize_dynamic_tags()

        logger.info("✅ Dynamic Tag Scaling System (@EVO) initialized")
        logger.info(f"   Tags registered: {len(self.tag_definitions)}")

    def _load_definitions(self):
        """Load existing tag definitions"""
        if self.definitions_file.exists():
            try:
                with open(self.definitions_file, 'r') as f:
                    data = json.load(f)
                    self.tag_definitions = {
                        k: DynamicTagDefinition(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load definitions: {e}")

    def _save_definitions(self):
        """Save tag definitions"""
        try:
            with open(self.definitions_file, 'w') as f:
                json.dump({
                    k: {
                        "tag": v.tag,
                        "base_definition": v.base_definition,
                        "scaling_rules": v.scaling_rules,
                        "context_adaptations": v.context_adaptations,
                        "effectiveness_history": v.effectiveness_history[-100:],  # Keep last 100
                        "usage_count": v.usage_count,
                        "success_rate": v.success_rate,
                        "current_scale_factor": v.current_scale_factor,
                        "last_updated": v.last_updated,
                        "evolution_metadata": v.evolution_metadata
                    }
                    for k, v in self.tag_definitions.items()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving definitions: {e}")

    def _initialize_dynamic_tags(self):
        """Initialize tags with dynamic scaling logic"""
        # @DTN - Do The Needful
        if "@DTN" not in self.tag_definitions:
            self.tag_definitions["@DTN"] = DynamicTagDefinition(
                tag="@DTN",
                base_definition="Do The Needful - Execute what's needed with dynamic scaling",
                scaling_rules={
                    "min_load": 0.0,
                    "max_load": 1.0,
                    "urgency_multiplier": 1.5,
                    "resource_aware": True,
                    "adaptive": True
                },
                context_adaptations={
                    "low_load": "Normal execution",
                    "high_load": "Prioritized execution",
                    "urgent": "Maximum speed execution",
                    "resource_constrained": "Efficient execution"
                },
                current_scale_factor=1.0,
                last_updated=datetime.now().isoformat(),
                evolution_metadata={
                    "evolution_type": "adaptive",
                    "learning_enabled": True,
                    "scaling_module": "dynamic"
                }
            )

        # @RR - Rapid Response (now dynamic)
        if "@RR" not in self.tag_definitions:
            self.tag_definitions["@RR"] = DynamicTagDefinition(
                tag="@RR",
                base_definition="Rapid Response - Adapts between Roast & Repair and Rapid Response",
                scaling_rules={
                    "context_switch_threshold": 0.7,
                    "security_context": "secondary",
                    "execution_context": "secondary",
                    "default_context": "primary",
                    "adaptive": True
                },
                context_adaptations={
                    "@COMPUSEC": "Switches to Rapid Response (security)",
                    "@DOIT": "Switches to Rapid Response (execution)",
                    "@F4": "Switches to Rapid Response (threat)",
                    "standalone": "Roast & Repair (default)"
                },
                current_scale_factor=1.0,
                last_updated=datetime.now().isoformat(),
                evolution_metadata={
                    "evolution_type": "context_adaptive",
                    "learning_enabled": True,
                    "scaling_module": "dynamic"
                }
            )

        # @DOIT - Autonomous Execution (now dynamic)
        if "@DOIT" not in self.tag_definitions:
            self.tag_definitions["@DOIT"] = DynamicTagDefinition(
                tag="@DOIT",
                base_definition="Autonomous Execution - Scales based on system conditions",
                scaling_rules={
                    "autonomy_level": "adaptive",
                    "speed_optimization": "dynamic",
                    "safety_override": "context_dependent",
                    "adaptive": True
                },
                context_adaptations={
                    "normal": "Standard autonomous execution",
                    "high_load": "Reduced autonomy, more validation",
                    "urgent": "Maximum autonomy, speed priority",
                    "critical": "Full autonomy, emergency mode"
                },
                current_scale_factor=1.0,
                last_updated=datetime.now().isoformat(),
                evolution_metadata={
                    "evolution_type": "load_adaptive",
                    "learning_enabled": True,
                    "scaling_module": "dynamic"
                }
            )

        # @PEAK - Quantification (now dynamic)
        if "@PEAK" not in self.tag_definitions:
            self.tag_definitions["@PEAK"] = DynamicTagDefinition(
                tag="@PEAK",
                base_definition="Quantification - Dynamically adjusts quantification depth",
                scaling_rules={
                    "quantification_depth": "adaptive",
                    "sample_size": "dynamic",
                    "precision": "context_dependent",
                    "adaptive": True
                },
                context_adaptations={
                    "normal": "Standard quantification",
                    "detailed": "Deep quantification",
                    "quick": "Lightweight quantification",
                    "critical": "Maximum precision quantification"
                },
                current_scale_factor=1.0,
                last_updated=datetime.now().isoformat(),
                evolution_metadata={
                    "evolution_type": "precision_adaptive",
                    "learning_enabled": True,
                    "scaling_module": "dynamic"
                }
            )

        # @COMPUSEC - Security (now dynamic)
        if "@COMPUSEC" not in self.tag_definitions:
            self.tag_definitions["@COMPUSEC"] = DynamicTagDefinition(
                tag="@COMPUSEC",
                base_definition="Security Response - Scales threat response dynamically",
                scaling_rules={
                    "threat_level": "dynamic",
                    "response_intensity": "adaptive",
                    "resource_allocation": "context_dependent",
                    "adaptive": True
                },
                context_adaptations={
                    "low_threat": "Standard security",
                    "medium_threat": "Elevated security",
                    "high_threat": "Maximum security",
                    "critical_threat": "Emergency security"
                },
                current_scale_factor=1.0,
                last_updated=datetime.now().isoformat(),
                evolution_metadata={
                    "evolution_type": "threat_adaptive",
                    "learning_enabled": True,
                    "scaling_module": "dynamic"
                }
            )

        # @JARVIS - Orchestrator (now dynamic)
        if "@JARVIS" not in self.tag_definitions:
            self.tag_definitions["@JARVIS"] = DynamicTagDefinition(
                tag="@JARVIS",
                base_definition="Orchestrator - Dynamically coordinates based on system state",
                scaling_rules={
                    "coordination_level": "adaptive",
                    "agent_allocation": "dynamic",
                    "priority_routing": "context_dependent",
                    "adaptive": True
                },
                context_adaptations={
                    "normal": "Standard coordination",
                    "complex": "Enhanced coordination",
                    "urgent": "Maximum coordination",
                    "critical": "Emergency coordination"
                },
                current_scale_factor=1.0,
                last_updated=datetime.now().isoformat(),
                evolution_metadata={
                    "evolution_type": "coordination_adaptive",
                    "learning_enabled": True,
                    "scaling_module": "dynamic"
                }
            )

        # @MARVIN - Validator (now dynamic)
        if "@MARVIN" not in self.tag_definitions:
            self.tag_definitions["@MARVIN"] = DynamicTagDefinition(
                tag="@MARVIN",
                base_definition="Reality Checker - Scales validation depth dynamically",
                scaling_rules={
                    "validation_depth": "adaptive",
                    "skepticism_level": "dynamic",
                    "check_frequency": "context_dependent",
                    "adaptive": True
                },
                context_adaptations={
                    "normal": "Standard validation",
                    "critical": "Deep validation",
                    "urgent": "Quick validation",
                    "trusted": "Light validation"
                },
                current_scale_factor=1.0,
                last_updated=datetime.now().isoformat(),
                evolution_metadata={
                    "evolution_type": "validation_adaptive",
                    "learning_enabled": True,
                    "scaling_module": "dynamic"
                }
            )

        self._save_definitions()

    def calculate_scale_factor(
        self,
        tag: str,
        context: TagScalingContext
    ) -> float:
        """
        Calculate dynamic scale factor for tag based on context

        Uses dynamically-scaling-module logic instead of fixed rules.
        """
        if tag not in self.tag_definitions:
            return 1.0  # Default scale

        tag_def = self.tag_definitions[tag]

        # Base scale factor
        base_scale = 1.0

        # Factor 1: System Load
        # Higher load = reduce scale (efficiency), lower load = increase scale (performance)
        load_factor = 1.0 - (context.system_load * 0.3)  # Reduce by up to 30% under high load

        # Factor 2: Urgency
        # Higher urgency = increase scale (speed), lower urgency = normal scale
        urgency_factor = 1.0 + (context.urgency * 0.5)  # Increase by up to 50% for urgency

        # Factor 3: Resource Availability
        # More resources = increase scale, fewer resources = decrease scale
        resource_factor = context.resource_availability

        # Factor 4: Historical Effectiveness
        # Higher effectiveness = maintain/increase scale, lower = decrease scale
        effectiveness_factor = 0.8 + (context.historical_effectiveness * 0.4)  # 0.8 - 1.2 range

        # Factor 5: Tag Combinations
        # Multiple tags = adjust scale based on combination effectiveness
        combination_factor = self._calculate_combination_factor(tag, context.tag_combinations)

        # Calculate final scale factor
        scale_factor = base_scale * load_factor * urgency_factor * resource_factor * effectiveness_factor * combination_factor

        # Apply scaling rules from tag definition
        if "min_scale" in tag_def.scaling_rules:
            scale_factor = max(scale_factor, tag_def.scaling_rules["min_scale"])
        if "max_scale" in tag_def.scaling_rules:
            scale_factor = min(scale_factor, tag_def.scaling_rules["max_scale"])

        # Update tag definition
        tag_def.current_scale_factor = scale_factor
        tag_def.last_updated = datetime.now().isoformat()

        return scale_factor

    def _calculate_combination_factor(self, tag: str, combinations: List[str]) -> float:
        """Calculate scale factor adjustment based on tag combinations"""
        if not combinations:
            return 1.0

        # Known effective combinations get boost
        effective_combos = {
            ("@RR", "@DOIT"): 1.2,  # Rapid execution
            ("@RR", "@COMPUSEC"): 1.3,  # Security rapid response
            ("@DOIT", "@PEAK"): 1.1,  # Quantified execution
            ("@JARVIS", "@RR"): 1.15,  # Coordinated rapid response
        }

        for combo in effective_combos:
            if tag in combo and all(c in combinations for c in combo):
                return effective_combos[combo]

        # Multiple tags generally increase complexity, slight reduction
        if len(combinations) > 3:
            return 0.95  # Slight reduction for complexity

        return 1.0

    def get_tag_definition(
        self,
        tag: str,
        context: Optional[TagScalingContext] = None
    ) -> Tuple[str, float]:
        """
        Get tag definition with dynamic scaling applied

        Returns: (definition, scale_factor)
        """
        if tag not in self.tag_definitions:
            return (f"{tag} - Unknown tag", 1.0)

        tag_def = self.tag_definitions[tag]
        base_def = tag_def.base_definition

        # Apply context adaptations if context provided
        if context:
            scale_factor = self.calculate_scale_factor(tag, context)

            # Find best context adaptation
            adaptation = self._find_context_adaptation(tag_def, context)
            if adaptation:
                return (f"{base_def} - {adaptation}", scale_factor)

        return (base_def, tag_def.current_scale_factor)

    def _find_context_adaptation(
        self,
        tag_def: DynamicTagDefinition,
        context: TagScalingContext
    ) -> Optional[str]:
        """Find appropriate context adaptation"""
        # Check tag combinations first
        for combo_tag in context.tag_combinations:
            if combo_tag in tag_def.context_adaptations:
                return tag_def.context_adaptations[combo_tag]

        # Check system load
        if context.system_load > 0.8:
            return tag_def.context_adaptations.get("high_load")
        elif context.system_load < 0.2:
            return tag_def.context_adaptations.get("low_load")

        # Check urgency
        if context.urgency > 0.7:
            return tag_def.context_adaptations.get("urgent")

        # Default
        return tag_def.context_adaptations.get("normal")

    def record_tag_usage(
        self,
        tag: str,
        success: bool,
        effectiveness: float = None
    ):
        """Record tag usage for evolutionary learning"""
        if tag not in self.tag_definitions:
            return

        tag_def = self.tag_definitions[tag]
        tag_def.usage_count += 1

        # Update success rate
        if effectiveness is None:
            effectiveness = 1.0 if success else 0.0

        # Moving average of effectiveness
        tag_def.effectiveness_history.append(effectiveness)
        if len(tag_def.effectiveness_history) > 100:
            tag_def.effectiveness_history.pop(0)

        tag_def.success_rate = sum(tag_def.effectiveness_history) / len(tag_def.effectiveness_history)

        # Evolutionary learning
        tag_def.evolution_metadata["last_effectiveness"] = effectiveness
        tag_def.evolution_metadata["total_usage"] = tag_def.usage_count
        tag_def.evolution_metadata["average_effectiveness"] = tag_def.success_rate

        self._save_definitions()

    def evolve_tag_definition(self, tag: str):
        """Evolve tag definition based on usage patterns (@EVO)"""
        if tag not in self.tag_definitions:
            return

        tag_def = self.tag_definitions[tag]

        # Evolutionary adjustments based on effectiveness
        if tag_def.success_rate < 0.5:
            # Low effectiveness - adjust scaling rules
            if "min_scale" not in tag_def.scaling_rules:
                tag_def.scaling_rules["min_scale"] = 0.5
            tag_def.evolution_metadata["evolution_note"] = "Reduced scale due to low effectiveness"

        elif tag_def.success_rate > 0.9:
            # High effectiveness - can increase scale
            tag_def.scaling_rules["max_scale"] = 2.5
            tag_def.evolution_metadata["evolution_note"] = "Increased scale due to high effectiveness"

        tag_def.last_updated = datetime.now().isoformat()
        self._save_definitions()

        logger.info(f"   🔄 Evolved {tag} definition (effectiveness: {tag_def.success_rate:.1%})")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Dynamic Tag Scaling System (@EVO)")
        parser.add_argument("--get", type=str, help="Get tag definition")
        parser.add_argument("--scale", type=str, help="Calculate scale factor for tag")
        parser.add_argument("--record", type=str, nargs=3, metavar=("TAG", "SUCCESS", "EFFECTIVENESS"), help="Record tag usage")
        parser.add_argument("--evolve", type=str, help="Evolve tag definition")
        parser.add_argument("--list", action="store_true", help="List all tags")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        system = DynamicTagScalingSystem()

        if args.get:
            context = TagScalingContext(
                system_load=0.5,
                urgency=0.5,
                resource_availability=1.0,
                historical_effectiveness=0.8
            )
            definition, scale = system.get_tag_definition(args.get, context)
            if args.json:
                print(json.dumps({
                    "tag": args.get,
                    "definition": definition,
                    "scale_factor": scale
                }, indent=2))
            else:
                print(f"{args.get}: {definition}")
                print(f"  Scale Factor: {scale:.2f}x")

        elif args.scale:
            context = TagScalingContext(
                system_load=0.6,
                urgency=0.7,
                resource_availability=0.8,
                historical_effectiveness=0.85
            )
            scale = system.calculate_scale_factor(args.scale, context)
            if args.json:
                print(json.dumps({"tag": args.scale, "scale_factor": scale}, indent=2))
            else:
                print(f"{args.scale} Scale Factor: {scale:.2f}x")

        elif args.record:
            tag, success_str, eff_str = args.record
            success = success_str.lower() == "true"
            effectiveness = float(eff_str) if eff_str else None
            system.record_tag_usage(tag, success, effectiveness)
            print(f"✅ Recorded usage for {tag}")

        elif args.evolve:
            system.evolve_tag_definition(args.evolve)
            print(f"✅ Evolved {args.evolve} definition")

        elif args.list:
            if args.json:
                print(json.dumps({
                    tag: {
                        "base_definition": defn.base_definition,
                        "current_scale_factor": defn.current_scale_factor,
                        "success_rate": defn.success_rate,
                        "usage_count": defn.usage_count
                    }
                    for tag, defn in system.tag_definitions.items()
                }, indent=2))
            else:
                print("Dynamic Tags:")
                for tag, defn in system.tag_definitions.items():
                    print(f"  {tag}: {defn.base_definition}")
                    print(f"    Scale: {defn.current_scale_factor:.2f}x | Effectiveness: {defn.success_rate:.1%}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()