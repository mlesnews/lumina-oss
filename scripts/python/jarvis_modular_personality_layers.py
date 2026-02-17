#!/usr/bin/env python3
"""
JARVIS Modular Personality Layers System

Modular personality layer system that stacks additional layers upon base persona:
- Base persona (character from acting call list)
- Story context layers
- Narrative/telling layers
- Additional personality layers
- Modular stacking system

Tags: #PERSONALITY_LAYERS #MODULAR #STORY_CONTEXT #NARRATIVE #PERSONA_STACKING @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISPersonality")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISPersonality")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISPersonality")

# Import SYPHON system
try:
    from syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.syphon_system import SYPHONSystem, DataSourceType
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("SYPHON system not available")


class LayerType(Enum):
    """Personality layer types"""
    BASE_PERSONA = "base_persona"
    STORY_CONTEXT = "story_context"
    NARRATIVE = "narrative"
    EMOTIONAL = "emotional"
    BEHAVIORAL = "behavioral"
    CULTURAL = "cultural"
    TEMPORAL = "temporal"
    RELATIONSHIP = "relationship"
    SITUATIONAL = "situational"
    CUSTOM = "custom"


class PersonalityLayer:
    """Individual personality layer"""

    def __init__(
        self,
        layer_id: str,
        layer_type: LayerType,
        name: str,
        description: str,
        attributes: Dict[str, Any],
        priority: int = 0,
        stackable: bool = True,
        conflicts: List[str] = None
    ):
        self.layer_id = layer_id
        self.layer_type = layer_type
        self.name = name
        self.description = description
        self.attributes = attributes
        self.priority = priority  # Higher priority layers override lower priority ones
        self.stackable = stackable
        self.conflicts = conflicts or []  # Layer IDs that conflict with this layer
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert layer to dictionary"""
        return {
            "layer_id": self.layer_id,
            "layer_type": self.layer_type.value,
            "name": self.name,
            "description": self.description,
            "attributes": self.attributes,
            "priority": self.priority,
            "stackable": self.stackable,
            "conflicts": self.conflicts,
            "created_at": self.created_at
        }


class ModularPersonalitySystem:
    """Modular personality layer system - stacks layers upon base persona"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "personality_layers"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.layers_file = self.data_dir / "personality_layers.json"
        self.stacks_file = self.data_dir / "personality_stacks.json"
        self.active_stacks_file = self.data_dir / "active_stacks.json"

        # Initialize SYPHON system
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for personality layers")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Load existing layers
        self.layers: Dict[str, PersonalityLayer] = {}
        self._load_layers()

        # Initialize default layers
        if not self.layers:
            self._initialize_default_layers()

    def _load_layers(self):
        """Load personality layers from file"""
        if self.layers_file.exists():
            try:
                with open(self.layers_file, 'r', encoding='utf-8') as f:
                    layers_data = json.load(f)
                    for layer_id, layer_data in layers_data.items():
                        self.layers[layer_id] = PersonalityLayer(
                            layer_id=layer_data["layer_id"],
                            layer_type=LayerType(layer_data["layer_type"]),
                            name=layer_data["name"],
                            description=layer_data["description"],
                            attributes=layer_data["attributes"],
                            priority=layer_data.get("priority", 0),
                            stackable=layer_data.get("stackable", True),
                            conflicts=layer_data.get("conflicts", [])
                        )
            except Exception as e:
                logger.error(f"Error loading layers: {e}")

    def _save_layers(self):
        """Save personality layers to file"""
        try:
            layers_data = {layer_id: layer.to_dict() for layer_id, layer in self.layers.items()}
            with open(self.layers_file, 'w', encoding='utf-8') as f:
                json.dump(layers_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving layers: {e}")

    def _initialize_default_layers(self):
        """Initialize default personality layers"""
        default_layers = [
            {
                "layer_id": "story_heroic",
                "layer_type": LayerType.STORY_CONTEXT,
                "name": "Heroic Story Context",
                "description": "Character in heroic story context",
                "attributes": {
                    "heroism": "high",
                    "courage": "high",
                    "self_sacrifice": "moderate",
                    "moral_compass": "strong"
                },
                "priority": 10
            },
            {
                "layer_id": "story_villain",
                "layer_type": LayerType.STORY_CONTEXT,
                "name": "Villain Story Context",
                "description": "Character in villain story context",
                "attributes": {
                    "heroism": "low",
                    "courage": "high",
                    "self_sacrifice": "low",
                    "moral_compass": "weak",
                    "ambition": "high"
                },
                "priority": 10
            },
            {
                "layer_id": "narrative_first_person",
                "layer_type": LayerType.NARRATIVE,
                "name": "First Person Narrative",
                "description": "Character tells story in first person",
                "attributes": {
                    "perspective": "first_person",
                    "intimacy": "high",
                    "subjectivity": "high"
                },
                "priority": 5
            },
            {
                "layer_id": "narrative_third_person",
                "layer_type": LayerType.NARRATIVE,
                "name": "Third Person Narrative",
                "description": "Character tells story in third person",
                "attributes": {
                    "perspective": "third_person",
                    "intimacy": "moderate",
                    "subjectivity": "low"
                },
                "priority": 5
            },
            {
                "layer_id": "emotional_joyful",
                "layer_type": LayerType.EMOTIONAL,
                "name": "Joyful Emotional Layer",
                "description": "Character experiences joy and happiness",
                "attributes": {
                    "emotion": "joy",
                    "energy": "high",
                    "optimism": "high"
                },
                "priority": 8
            },
            {
                "layer_id": "emotional_melancholic",
                "layer_type": LayerType.EMOTIONAL,
                "name": "Melancholic Emotional Layer",
                "description": "Character experiences melancholy and sadness",
                "attributes": {
                    "emotion": "melancholy",
                    "energy": "low",
                    "optimism": "low"
                },
                "priority": 8
            },
            {
                "layer_id": "behavioral_formal",
                "layer_type": LayerType.BEHAVIORAL,
                "name": "Formal Behavioral Layer",
                "description": "Character behaves formally",
                "attributes": {
                    "formality": "high",
                    "politeness": "high",
                    "decorum": "high"
                },
                "priority": 7
            },
            {
                "layer_id": "behavioral_casual",
                "layer_type": LayerType.BEHAVIORAL,
                "name": "Casual Behavioral Layer",
                "description": "Character behaves casually",
                "attributes": {
                    "formality": "low",
                    "politeness": "moderate",
                    "decorum": "low"
                },
                "priority": 7
            },
            {
                "layer_id": "temporal_past",
                "layer_type": LayerType.TEMPORAL,
                "name": "Past Temporal Layer",
                "description": "Character exists in past time period",
                "attributes": {
                    "time_period": "past",
                    "historical_context": "high"
                },
                "priority": 6
            },
            {
                "layer_id": "temporal_future",
                "layer_type": LayerType.TEMPORAL,
                "name": "Future Temporal Layer",
                "description": "Character exists in future time period",
                "attributes": {
                    "time_period": "future",
                    "speculative_context": "high"
                },
                "priority": 6
            }
        ]

        for layer_data in default_layers:
            layer = PersonalityLayer(**layer_data)
            self.layers[layer.layer_id] = layer

        self._save_layers()
        logger.info(f"✅ Initialized {len(default_layers)} default personality layers")

    def create_layer(
        self,
        layer_id: str,
        layer_type: LayerType,
        name: str,
        description: str,
        attributes: Dict[str, Any],
        priority: int = 0,
        stackable: bool = True,
        conflicts: List[str] = None
    ) -> PersonalityLayer:
        """Create a new personality layer"""
        layer = PersonalityLayer(
            layer_id=layer_id,
            layer_type=layer_type,
            name=name,
            description=description,
            attributes=attributes,
            priority=priority,
            stackable=stackable,
            conflicts=conflicts or []
        )

        self.layers[layer_id] = layer
        self._save_layers()

        logger.info(f"✅ Created personality layer: {layer_id} ({name})")
        return layer

    def create_personality_stack(
        self,
        stack_id: str,
        base_persona_id: str,
        layer_ids: List[str],
        story_context: str = None,
        narrative_style: str = None
    ) -> Dict[str, Any]:
        """Create a personality stack - layers upon base persona"""
        # Verify base persona exists (from acting call list)
        # For now, we'll assume it exists

        # Verify all layers exist
        missing_layers = [lid for lid in layer_ids if lid not in self.layers]
        if missing_layers:
            return {"error": f"Missing layers: {missing_layers}"}

        # Check for conflicts
        conflicts = []
        for layer_id in layer_ids:
            layer = self.layers[layer_id]
            for conflict_id in layer.conflicts:
                if conflict_id in layer_ids:
                    conflicts.append(f"{layer_id} conflicts with {conflict_id}")

        if conflicts:
            return {"error": f"Layer conflicts: {conflicts}"}

        # Sort layers by priority (higher priority first)
        sorted_layers = sorted(
            layer_ids,
            key=lambda lid: self.layers[lid].priority,
            reverse=True
        )

        # Build merged attributes
        merged_attributes = {}
        for layer_id in sorted_layers:
            layer = self.layers[layer_id]
            # Merge attributes (higher priority overrides)
            for key, value in layer.attributes.items():
                if key not in merged_attributes or layer.priority > 0:
                    merged_attributes[key] = value

        stack = {
            "stack_id": stack_id,
            "created_at": datetime.now().isoformat(),
            "base_persona_id": base_persona_id,
            "layer_ids": sorted_layers,
            "layer_order": sorted_layers,
            "merged_attributes": merged_attributes,
            "story_context": story_context,
            "narrative_style": narrative_style,
            "conflicts": conflicts,
            "status": "active"
        }

        # Save stack
        stacks = []
        if self.stacks_file.exists():
            try:
                with open(self.stacks_file, 'r', encoding='utf-8') as f:
                    stacks = json.load(f)
            except Exception:
                stacks = []

        stacks.append(stack)

        try:
            with open(self.stacks_file, 'w', encoding='utf-8') as f:
                json.dump(stacks, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving stack: {e}")

        logger.info(f"✅ Created personality stack: {stack_id} with {len(sorted_layers)} layers")
        return stack

    def apply_stack_to_persona(
        self,
        persona_id: str,
        stack_id: str
    ) -> Dict[str, Any]:
        """Apply a personality stack to a persona"""
        # Load stack
        stacks = []
        if self.stacks_file.exists():
            try:
                with open(self.stacks_file, 'r', encoding='utf-8') as f:
                    stacks = json.load(f)
            except Exception:
                stacks = []

        stack = next((s for s in stacks if s["stack_id"] == stack_id), None)
        if not stack:
            return {"error": f"Stack not found: {stack_id}"}

        # Create active stack record
        active_stack = {
            "active_stack_id": f"active_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "persona_id": persona_id,
            "stack_id": stack_id,
            "applied_at": datetime.now().isoformat(),
            "stack": stack,
            "status": "active"
        }

        # Save active stack
        active_stacks = []
        if self.active_stacks_file.exists():
            try:
                with open(self.active_stacks_file, 'r', encoding='utf-8') as f:
                    active_stacks = json.load(f)
            except Exception:
                active_stacks = []

        active_stacks.append(active_stack)

        try:
            with open(self.active_stacks_file, 'w', encoding='utf-8') as f:
                json.dump(active_stacks, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving active stack: {e}")

        logger.info(f"✅ Applied stack {stack_id} to persona {persona_id}")
        return active_stack

    def get_personality_stack(
        self,
        stack_id: str
    ) -> Dict[str, Any]:
        """Get a personality stack"""
        stacks = []
        if self.stacks_file.exists():
            try:
                with open(self.stacks_file, 'r', encoding='utf-8') as f:
                    stacks = json.load(f)
            except Exception:
                stacks = []

        stack = next((s for s in stacks if s["stack_id"] == stack_id), None)
        if not stack:
            return {"error": f"Stack not found: {stack_id}"}

        # Enrich with layer details
        enriched_stack = stack.copy()
        enriched_stack["layers"] = []
        for layer_id in stack["layer_ids"]:
            if layer_id in self.layers:
                enriched_stack["layers"].append(self.layers[layer_id].to_dict())

        return enriched_stack

    def list_layers(self, layer_type: LayerType = None) -> List[Dict[str, Any]]:
        """List all personality layers"""
        layers = [layer.to_dict() for layer in self.layers.values()]
        if layer_type:
            layers = [l for l in layers if l["layer_type"] == layer_type.value]
        return layers

    def generate_stack_report(self) -> Dict[str, Any]:
        """Generate comprehensive stack report"""
        report = {
            "report_id": f"stack_report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "total_layers": len(self.layers),
            "layers_by_type": {},
            "total_stacks": 0,
            "active_stacks": 0,
            "layers": [layer.to_dict() for layer in self.layers.values()],
            "syphon_intelligence": {}
        }

        # Count layers by type
        for layer in self.layers.values():
            layer_type = layer.layer_type.value
            if layer_type not in report["layers_by_type"]:
                report["layers_by_type"][layer_type] = 0
            report["layers_by_type"][layer_type] += 1

        # Count stacks
        if self.stacks_file.exists():
            try:
                with open(self.stacks_file, 'r', encoding='utf-8') as f:
                    stacks = json.load(f)
                    report["total_stacks"] = len(stacks)
            except Exception:
                pass

        # Count active stacks
        if self.active_stacks_file.exists():
            try:
                with open(self.active_stacks_file, 'r', encoding='utf-8') as f:
                    active_stacks = json.load(f)
                    report["active_stacks"] = len(active_stacks)
            except Exception:
                pass

        # Use SYPHON to extract intelligence
        if self.syphon:
            try:
                content = json.dumps(report, default=str)
                syphon_result = self._syphon_extract_stack_intelligence(content)
                if syphon_result:
                    report["syphon_intelligence"] = syphon_result
            except Exception as e:
                logger.warning(f"SYPHON stack extraction failed: {e}")

        return report

    def _syphon_extract_stack_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system"""
        if not self.syphon:
            return {}

        try:
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=DataSourceType.DOCUMENT,
                source_id=f"stack_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"personality_layers": True, "modular_system": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON stack extraction error: {e}")
            return {}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Modular Personality Layers")
        parser.add_argument("--create-layer", type=str, nargs=6, metavar=("ID", "TYPE", "NAME", "DESC", "PRIORITY", "ATTRS_JSON"),
                           help="Create a new personality layer")
        parser.add_argument("--create-stack", type=str, nargs=4, metavar=("STACK_ID", "PERSONA_ID", "LAYER_IDS", "STORY_CONTEXT"),
                           help="Create a personality stack")
        parser.add_argument("--apply-stack", type=str, nargs=2, metavar=("PERSONA_ID", "STACK_ID"),
                           help="Apply stack to persona")
        parser.add_argument("--list-layers", action="store_true", help="List all layers")
        parser.add_argument("--get-stack", type=str, metavar="STACK_ID", help="Get stack details")
        parser.add_argument("--report", action="store_true", help="Generate comprehensive report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = ModularPersonalitySystem(project_root)

        if args.create_layer:
            import json as json_lib
            attrs = json_lib.loads(args.create_layer[5])
            layer = system.create_layer(
                layer_id=args.create_layer[0],
                layer_type=LayerType(args.create_layer[1]),
                name=args.create_layer[2],
                description=args.create_layer[3],
                attributes=attrs,
                priority=int(args.create_layer[4])
            )
            print("=" * 80)
            print("✅ PERSONALITY LAYER CREATED")
            print("=" * 80)
            print(json.dumps(layer.to_dict(), indent=2, default=str))

        elif args.create_stack:
            import json as json_lib
            layer_ids = json_lib.loads(args.create_stack[2])
            stack = system.create_personality_stack(
                stack_id=args.create_stack[0],
                base_persona_id=args.create_stack[1],
                layer_ids=layer_ids,
                story_context=args.create_stack[3] if len(args.create_stack) > 3 else None
            )
            print("=" * 80)
            print("✅ PERSONALITY STACK CREATED")
            print("=" * 80)
            print(json.dumps(stack, indent=2, default=str))

        elif args.apply_stack:
            result = system.apply_stack_to_persona(args.apply_stack[0], args.apply_stack[1])
            print("=" * 80)
            print("✅ STACK APPLIED TO PERSONA")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.list_layers:
            layers = system.list_layers()
            print("=" * 80)
            print("📋 PERSONALITY LAYERS")
            print("=" * 80)
            print(f"Total: {len(layers)}")
            print(json.dumps(layers, indent=2, default=str))

        elif args.get_stack:
            stack = system.get_personality_stack(args.get_stack)
            print("=" * 80)
            print("📚 PERSONALITY STACK")
            print("=" * 80)
            print(json.dumps(stack, indent=2, default=str))

        elif args.report:
            report = system.generate_stack_report()
            print("=" * 80)
            print("📊 MODULAR PERSONALITY LAYERS REPORT")
            print("=" * 80)
            print(f"Total Layers: {report['total_layers']}")
            print(f"Layers by Type: {report['layers_by_type']}")
            print(f"Total Stacks: {report['total_stacks']}")
            print(f"Active Stacks: {report['active_stacks']}")
            print("=" * 80)
            print(json.dumps(report, indent=2, default=str))

        else:
            # Default: generate report
            report = system.generate_stack_report()
            print("=" * 80)
            print("📊 JARVIS MODULAR PERSONALITY LAYERS")
            print("=" * 80)
            print(f"Total Layers: {report['total_layers']}")
            print(f"Layers by Type: {report['layers_by_type']}")
            print(f"Total Stacks: {report['total_stacks']}")
            print(f"Active Stacks: {report['active_stacks']}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()