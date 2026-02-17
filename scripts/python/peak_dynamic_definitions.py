#!/usr/bin/env python3
"""
@PEAK Dynamic Definitions System

Allows @PEAK to define primary, secondary, tertiary, etc. definitions for terms
like @RR, with dynamic modification on the fly.

@RR Primary: "Roast & Repair"
@RR Secondary: "Rapid Response"
@RR Tertiary: [User-defined]

Tags: #PEAK #DEFINITIONS #DYNAMIC #RR #ROAST_REPAIR #RAPID_RESPONSE @JARVIS @LUMINA @PEAK
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

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

logger = get_logger("PEAKDynamicDefinitions")


class DefinitionPriority(Enum):
    """Definition priority/order"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    QUATERNARY = "quaternary"
    QUINARY = "quinary"
    SENARY = "senary"
    SEPTENARY = "septenary"
    OCTONARY = "octonary"
    NONARY = "nonary"
    DENARY = "denary"


@dataclass
class TermDefinition:
    """Term definition with priority"""
    term: str
    priority: DefinitionPriority
    definition: str
    description: str
    context: str  # When this definition applies
    usage_examples: List[str] = field(default_factory=list)
    created_by: str = "@PEAK"
    created_at: str = ""
    modified_at: str = ""
    usage_count: int = 0
    effectiveness_score: float = 0.0  # @PEAK quantification
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TermRegistry:
    """Registry of all definitions for a term"""
    term: str
    definitions: Dict[DefinitionPriority, TermDefinition] = field(default_factory=dict)
    active_priority: DefinitionPriority = DefinitionPriority.PRIMARY
    dynamic_modifications: List[Dict[str, Any]] = field(default_factory=list)
    peak_quantification: Dict[str, float] = field(default_factory=dict)


class PEAKDynamicDefinitions:
    """
    @PEAK Dynamic Definitions System

    Manages multiple definitions for terms with @PEAK quantification.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @PEAK definitions system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "peak_definitions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Definitions database
        self.definitions_file = self.data_dir / "definitions.json"
        self.registries: Dict[str, TermRegistry] = {}

        # Load existing definitions
        self._load_definitions()

        # Initialize default @RR definitions
        self._initialize_rr_definitions()

        # Initialize @DTN definition
        self._initialize_dtn_definition()

        logger.info("✅ @PEAK Dynamic Definitions System initialized")
        logger.info(f"   Terms registered: {len(self.registries)}")

    def _load_definitions(self):
        """Load existing definitions"""
        if self.definitions_file.exists():
            try:
                with open(self.definitions_file, 'r') as f:
                    data = json.load(f)
                    for term, registry_data in data.items():
                        registry = TermRegistry(term=term)
                        for priority_str, def_data in registry_data.get("definitions", {}).items():
                            priority = DefinitionPriority(priority_str)
                            registry.definitions[priority] = TermDefinition(**def_data)
                        registry.active_priority = DefinitionPriority(registry_data.get("active_priority", "primary"))
                        registry.dynamic_modifications = registry_data.get("dynamic_modifications", [])
                        registry.peak_quantification = registry_data.get("peak_quantification", {})
                        self.registries[term] = registry
            except Exception as e:
                logger.debug(f"   Could not load definitions: {e}")

    def _save_definitions(self):
        """Save definitions"""
        try:
            with open(self.definitions_file, 'w') as f:
                json.dump({
                    term: {
                        "term": registry.term,
                        "definitions": {
                            str(priority.value): {
                                "term": defn.term,
                                "priority": defn.priority.value if hasattr(defn.priority, 'value') else str(defn.priority),
                                "definition": defn.definition,
                                "description": defn.description,
                                "context": defn.context,
                                "usage_examples": defn.usage_examples,
                                "created_by": defn.created_by,
                                "created_at": defn.created_at,
                                "modified_at": defn.modified_at,
                                "usage_count": defn.usage_count,
                                "effectiveness_score": defn.effectiveness_score,
                                "metadata": defn.metadata
                            }
                            for priority, defn in registry.definitions.items()
                        },
                        "active_priority": registry.active_priority.value,
                        "dynamic_modifications": registry.dynamic_modifications,
                        "peak_quantification": registry.peak_quantification
                    }
                    for term, registry in self.registries.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving definitions: {e}")

    def _initialize_rr_definitions(self):
        """Initialize @RR definitions"""
        if "@RR" not in self.registries:
            registry = TermRegistry(term="@RR")

            # Primary: Roast & Repair
            registry.definitions[DefinitionPriority.PRIMARY] = TermDefinition(
                term="@RR",
                priority=DefinitionPriority.PRIMARY,
                definition="Roast & Repair",
                description="Primary definition: Identify issues (roast) and fix them (repair). Critical analysis followed by corrective action.",
                context="Primary operational mode - default @RR behavior",
                usage_examples=[
                    "@RR this code - roast the problems and repair them",
                    "Use @RR to identify and fix issues"
                ],
                created_by="@PEAK",
                created_at=datetime.now().isoformat(),
                effectiveness_score=1.0  # Primary = 100% effectiveness baseline
            )

            # Secondary: Rapid Response
            registry.definitions[DefinitionPriority.SECONDARY] = TermDefinition(
                term="@RR",
                priority=DefinitionPriority.SECONDARY,
                definition="Rapid Response",
                description="Secondary definition: Fastest possible execution path. Speed-optimized response for time-critical operations.",
                context="@COMPUSEC-DYNAMIC-DUO strategy - rapid response to threats",
                usage_examples=[
                    "@RR deploy systems - rapid response mode",
                    "Use @RR for fastest execution"
                ],
                created_by="@PEAK",
                created_at=datetime.now().isoformat(),
                effectiveness_score=0.95  # High effectiveness for speed
            )

            # Tertiary: [Can be defined dynamically]
            # Will be added by user or system as needed

            registry.active_priority = DefinitionPriority.PRIMARY
            self.registries["@RR"] = registry
            self._save_definitions()

    def _initialize_dtn_definition(self):
        """Initialize @DTN definition with dynamic scaling"""
        if "@DTN" not in self.registries:
            registry = TermRegistry(term="@DTN")

            # Primary: Do The Needful
            registry.definitions[DefinitionPriority.PRIMARY] = TermDefinition(
                term="@DTN",
                priority=DefinitionPriority.PRIMARY,
                definition="Do The Needful",
                description="Execute what's needed with @DYNAMICALLY-SCALING-MODULE logic. Adapts based on system load, urgency, resources, and effectiveness. NOT a fixed static solution - evolves with @EVO.",
                context="Dynamic scaling module - adapts to conditions",
                usage_examples=[
                    "@DTN execute this task - do what's needed with dynamic scaling",
                    "Use @DTN for adaptive execution based on conditions"
                ],
                created_by="@PEAK",
                created_at=datetime.now().isoformat(),
                effectiveness_score=1.0,
                metadata={
                    "scaling_module": "dynamic",
                    "evolution_type": "adaptive",
                    "learning_enabled": True,
                    "not_static": True
                }
            )

            registry.active_priority = DefinitionPriority.PRIMARY
            self.registries["@DTN"] = registry
            self._save_definitions()

    def add_definition(
        self,
        term: str,
        priority: DefinitionPriority,
        definition: str,
        description: str,
        context: str,
        usage_examples: List[str] = None,
        created_by: str = "@PEAK"
    ) -> TermDefinition:
        """Add or update definition"""
        if term not in self.registries:
            self.registries[term] = TermRegistry(term=term)

        registry = self.registries[term]

        term_def = TermDefinition(
            term=term,
            priority=priority,
            definition=definition,
            description=description,
            context=context,
            usage_examples=usage_examples or [],
            created_by=created_by,
            created_at=datetime.now().isoformat(),
            modified_at=datetime.now().isoformat()
        )

        registry.definitions[priority] = term_def

        # Log dynamic modification
        registry.dynamic_modifications.append({
            "timestamp": datetime.now().isoformat(),
            "action": "add_definition",
            "priority": priority.value,
            "definition": definition,
            "modified_by": created_by
        })

        self._save_definitions()

        logger.info(f"   ✅ Added {priority.value} definition for {term}: {definition}")

        return term_def

    def modify_definition_on_fly(
        self,
        term: str,
        priority: DefinitionPriority,
        new_definition: str = None,
        new_description: str = None,
        new_context: str = None,
        modified_by: str = "@PEAK"
    ) -> TermDefinition:
        """Modify definition on the fly"""
        if term not in self.registries:
            logger.error(f"   ❌ Term not found: {term}")
            return None

        registry = self.registries[term]

        if priority not in registry.definitions:
            logger.error(f"   ❌ Priority not found: {priority.value}")
            return None

        term_def = registry.definitions[priority]

        # Modify fields
        if new_definition:
            term_def.definition = new_definition
        if new_description:
            term_def.description = new_description
        if new_context:
            term_def.context = new_context

        term_def.modified_at = datetime.now().isoformat()

        # Log dynamic modification
        registry.dynamic_modifications.append({
            "timestamp": datetime.now().isoformat(),
            "action": "modify_definition",
            "priority": priority.value,
            "changes": {
                "definition": new_definition,
                "description": new_description,
                "context": new_context
            },
            "modified_by": modified_by
        })

        self._save_definitions()

        logger.info(f"   ✅ Modified {priority.value} definition for {term}")

        return term_def

    def get_definition(self, term: str, priority: Optional[DefinitionPriority] = None) -> Optional[TermDefinition]:
        """Get definition for term"""
        if term not in self.registries:
            return None

        registry = self.registries[term]

        if priority:
            return registry.definitions.get(priority)
        else:
            # Return active priority
            return registry.definitions.get(registry.active_priority)

    def get_all_definitions(self, term: str) -> Dict[DefinitionPriority, TermDefinition]:
        """Get all definitions for term"""
        if term not in self.registries:
            return {}

        return self.registries[term].definitions

    def set_active_priority(self, term: str, priority: DefinitionPriority):
        """Set active priority for term"""
        if term not in self.registries:
            logger.error(f"   ❌ Term not found: {term}")
            return

        registry = self.registries[term]
        registry.active_priority = priority

        # Log change
        registry.dynamic_modifications.append({
            "timestamp": datetime.now().isoformat(),
            "action": "set_active_priority",
            "priority": priority.value,
            "modified_by": "@PEAK"
        })

        self._save_definitions()

        logger.info(f"   ✅ Set active priority for {term}: {priority.value}")

    def quantify_definition_effectiveness(self, term: str, priority: DefinitionPriority) -> float:
        """@PEAK quantification of definition effectiveness"""
        if term not in self.registries:
            return 0.0

        registry = self.registries[term]

        if priority not in registry.definitions:
            return 0.0

        term_def = registry.definitions[priority]

        # Calculate effectiveness based on:
        # - Usage count
        # - Success rate
        # - Context appropriateness
        # - User feedback

        effectiveness = term_def.effectiveness_score

        # Update based on usage
        if term_def.usage_count > 0:
            # Effectiveness increases with successful usage
            effectiveness = min(1.0, effectiveness + (term_def.usage_count * 0.01))

        # Store in peak_quantification
        registry.peak_quantification[f"{priority.value}_effectiveness"] = effectiveness

        self._save_definitions()

        return effectiveness

    def record_usage(self, term: str, priority: DefinitionPriority, success: bool = True):
        """Record usage of definition"""
        if term not in self.registries:
            return

        registry = self.registries[term]

        if priority not in registry.definitions:
            return

        term_def = registry.definitions[priority]
        term_def.usage_count += 1

        # Update effectiveness based on success
        if success:
            term_def.effectiveness_score = min(1.0, term_def.effectiveness_score + 0.01)
        else:
            term_def.effectiveness_score = max(0.0, term_def.effectiveness_score - 0.02)

        self._save_definitions()


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="@PEAK Dynamic Definitions")
        parser.add_argument("--add", type=str, nargs=4, metavar=("TERM", "PRIORITY", "DEFINITION", "DESCRIPTION"), help="Add definition")
        parser.add_argument("--modify", type=str, nargs=3, metavar=("TERM", "PRIORITY", "NEW_DEFINITION"), help="Modify definition on the fly")
        parser.add_argument("--get", type=str, help="Get definition for term")
        parser.add_argument("--get-all", type=str, help="Get all definitions for term")
        parser.add_argument("--set-active", type=str, nargs=2, metavar=("TERM", "PRIORITY"), help="Set active priority")
        parser.add_argument("--quantify", type=str, nargs=2, metavar=("TERM", "PRIORITY"), help="Quantify definition effectiveness")
        parser.add_argument("--list", action="store_true", help="List all terms")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        system = PEAKDynamicDefinitions()

        if args.add:
            term, priority_str, definition, description = args.add
            priority = DefinitionPriority(priority_str.lower())
            term_def = system.add_definition(term, priority, definition, description, "")
            if args.json:
                print(json.dumps({
                    "term": term_def.term,
                    "priority": term_def.priority.value,
                    "definition": term_def.definition
                }, indent=2))
            else:
                print(f"✅ Added {priority.value} definition: {definition}")

        elif args.modify:
            term, priority_str, new_def = args.modify
            priority = DefinitionPriority(priority_str.lower())
            term_def = system.modify_definition_on_fly(term, priority, new_definition=new_def)
            if args.json and term_def:
                print(json.dumps({
                    "term": term_def.term,
                    "priority": term_def.priority.value,
                    "definition": term_def.definition
                }, indent=2))
            else:
                print(f"✅ Modified {priority.value} definition: {new_def}")

        elif args.get:
            term_def = system.get_definition(args.get)
            if args.json:
                if term_def:
                    print(json.dumps({
                        "term": term_def.term,
                        "priority": term_def.priority.value,
                        "definition": term_def.definition,
                        "description": term_def.description
                    }, indent=2))
                else:
                    print(json.dumps({"error": "Definition not found"}, indent=2))
            else:
                if term_def:
                    print(f"{term_def.term} ({term_def.priority.value}): {term_def.definition}")
                else:
                    print("❌ Definition not found")

        elif args.get_all:
            definitions = system.get_all_definitions(args.get_all)
            if args.json:
                print(json.dumps({
                    priority.value: {
                        "definition": defn.definition,
                        "description": defn.description,
                        "context": defn.context
                    }
                    for priority, defn in definitions.items()
                }, indent=2))
            else:
                print(f"All definitions for {args.get_all}:")
                for priority, defn in sorted(definitions.items(), key=lambda x: x[0].value):
                    print(f"  {priority.value}: {defn.definition}")

        elif args.set_active:
            term, priority_str = args.set_active
            priority = DefinitionPriority(priority_str.lower())
            system.set_active_priority(term, priority)
            print(f"✅ Set active priority: {priority.value}")

        elif args.quantify:
            term, priority_str = args.quantify
            priority = DefinitionPriority(priority_str.lower())
            effectiveness = system.quantify_definition_effectiveness(term, priority)
            if args.json:
                print(json.dumps({"effectiveness": effectiveness}, indent=2))
            else:
                print(f"Effectiveness: {effectiveness:.2%}")

        elif args.list:
            if args.json:
                print(json.dumps({
                    term: {
                        "definitions_count": len(registry.definitions),
                        "active_priority": registry.active_priority.value
                    }
                    for term, registry in system.registries.items()
                }, indent=2))
            else:
                print("Registered terms:")
                for term, registry in system.registries.items():
                    print(f"  {term}: {len(registry.definitions)} definitions (active: {registry.active_priority.value})")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()