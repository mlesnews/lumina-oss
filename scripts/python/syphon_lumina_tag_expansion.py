#!/usr/bin/env python3
"""
@SYPHON + @LUMINA Tag Expansion System

Expands and expounds upon dynamic tag scaling logic using:
- @SYPHON: Intelligence extraction from code, usage patterns, effectiveness data
- @LUMINA: Knowledge base expansion, pattern recognition, context understanding

Extracts intelligence about tag behaviors, expands definitions, and builds comprehensive
knowledge base of tag scaling patterns.

Tags: #SYPHON #LUMINA #TAG_EXPANSION #INTELLIGENCE_EXTRACTION #KNOWLEDGE_BASE #DYNAMIC_SCALING #EVO @JARVIS @LUMINA @SYPHON @PEAK @DTN @EVO
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

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

logger = get_logger("SyphonLuminaTagExpansion")


@dataclass
class ExtractedIntelligence:
    """Intelligence extracted by @SYPHON"""
    source: str  # "code", "usage", "logs", "patterns"
    tag: str
    intelligence_type: str  # "pattern", "effectiveness", "context", "scaling"
    extracted_data: Dict[str, Any]
    confidence: float = 0.0  # 0.0 - 1.0
    timestamp: str = ""


@dataclass
class ExpandedTagKnowledge:
    """Expanded knowledge from @LUMINA"""
    tag: str
    base_definition: str
    expanded_definitions: List[str] = field(default_factory=list)
    usage_patterns: Dict[str, Any] = field(default_factory=dict)
    effectiveness_patterns: Dict[str, Any] = field(default_factory=dict)
    scaling_patterns: Dict[str, Any] = field(default_factory=dict)
    context_patterns: Dict[str, Any] = field(default_factory=dict)
    related_tags: List[str] = field(default_factory=list)
    knowledge_metadata: Dict[str, Any] = field(default_factory=dict)


class SyphonLuminaTagExpansion:
    """
    @SYPHON + @LUMINA Tag Expansion System

    Expands and expounds upon dynamic tag scaling logic by:
    1. @SYPHON: Extracting intelligence from various sources
    2. @LUMINA: Expanding knowledge base with patterns and insights
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @SYPHON + @LUMINA expansion system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon_lumina_tag_expansion"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.intelligence_file = self.data_dir / "extracted_intelligence.json"
        self.knowledge_file = self.data_dir / "expanded_knowledge.json"
        self.patterns_file = self.data_dir / "tag_patterns.json"

        # Intelligence and knowledge
        self.extracted_intelligence: List[ExtractedIntelligence] = []
        self.expanded_knowledge: Dict[str, ExpandedTagKnowledge] = {}
        self.tag_patterns: Dict[str, Dict[str, Any]] = {}

        # Load existing data
        self._load_data()

        # Initialize with dynamic tag scaling system
        try:
            from dynamic_tag_scaling_system import DynamicTagScalingSystem
            self.tag_scaling_system = DynamicTagScalingSystem(project_root)
        except:
            self.tag_scaling_system = None
            logger.debug("   Dynamic tag scaling system not available")

        logger.info("✅ @SYPHON + @LUMINA Tag Expansion System initialized")
        logger.info(f"   Extracted intelligence items: {len(self.extracted_intelligence)}")
        logger.info(f"   Expanded knowledge entries: {len(self.expanded_knowledge)}")

    def _load_data(self):
        """Load existing intelligence and knowledge"""
        # Load extracted intelligence
        if self.intelligence_file.exists():
            try:
                with open(self.intelligence_file, 'r') as f:
                    data = json.load(f)
                    self.extracted_intelligence = [
                        ExtractedIntelligence(**item) for item in data
                    ]
            except Exception as e:
                logger.debug(f"   Could not load intelligence: {e}")

        # Load expanded knowledge
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r') as f:
                    data = json.load(f)
                    self.expanded_knowledge = {
                        k: ExpandedTagKnowledge(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load knowledge: {e}")

        # Load patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    self.tag_patterns = json.load(f)
            except Exception as e:
                logger.debug(f"   Could not load patterns: {e}")

    def _save_data(self):
        """Save all data"""
        # Save intelligence
        try:
            with open(self.intelligence_file, 'w') as f:
                json.dump([
                    {
                        "source": item.source,
                        "tag": item.tag,
                        "intelligence_type": item.intelligence_type,
                        "extracted_data": item.extracted_data,
                        "confidence": item.confidence,
                        "timestamp": item.timestamp
                    }
                    for item in self.extracted_intelligence[-1000:]  # Keep last 1000
                ], f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving intelligence: {e}")

        # Save knowledge
        try:
            with open(self.knowledge_file, 'w') as f:
                json.dump({
                    k: {
                        "tag": v.tag,
                        "base_definition": v.base_definition,
                        "expanded_definitions": v.expanded_definitions,
                        "usage_patterns": v.usage_patterns,
                        "effectiveness_patterns": v.effectiveness_patterns,
                        "scaling_patterns": v.scaling_patterns,
                        "context_patterns": v.context_patterns,
                        "related_tags": v.related_tags,
                        "knowledge_metadata": v.knowledge_metadata
                    }
                    for k, v in self.expanded_knowledge.items()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving knowledge: {e}")

        # Save patterns
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.tag_patterns, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving patterns: {e}")

    def syphon_extract_intelligence(
        self,
        source: str,
        tag: str,
        intelligence_type: str,
        data: Dict[str, Any],
        confidence: float = 0.8
    ) -> ExtractedIntelligence:
        """
        @SYPHON: Extract intelligence about tag usage/behavior

        Sources: code, usage logs, effectiveness data, patterns
        """
        intelligence = ExtractedIntelligence(
            source=source,
            tag=tag,
            intelligence_type=intelligence_type,
            extracted_data=data,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )

        self.extracted_intelligence.append(intelligence)
        self._save_data()

        logger.info(f"   📊 @SYPHON extracted intelligence: {tag} ({intelligence_type})")

        return intelligence

    def syphon_extract_from_code(self, tag: str, code_path: Path) -> List[ExtractedIntelligence]:
        """@SYPHON: Extract tag usage patterns from code"""
        if not code_path.exists():
            return []

        intelligence_items = []

        try:
            content = code_path.read_text()

            # Find tag usage patterns
            tag_pattern = re.compile(rf'\b{re.escape(tag)}\b', re.IGNORECASE)
            matches = tag_pattern.findall(content)

            if matches:
                # Extract context around tag usage
                lines = content.split('\n')
                tag_contexts = []

                for i, line in enumerate(lines):
                    if tag_pattern.search(line):
                        context_start = max(0, i - 3)
                        context_end = min(len(lines), i + 4)
                        context = '\n'.join(lines[context_start:context_end])
                        tag_contexts.append({
                            "line": i + 1,
                            "context": context,
                            "line_content": line.strip()
                        })

                intelligence = self.syphon_extract_intelligence(
                    source="code",
                    tag=tag,
                    intelligence_type="usage_pattern",
                    data={
                        "file": str(code_path),
                        "occurrences": len(matches),
                        "contexts": tag_contexts,
                        "usage_density": len(matches) / max(len(lines), 1)
                    },
                    confidence=0.9
                )
                intelligence_items.append(intelligence)

            # Extract scaling-related patterns
            scaling_patterns = re.findall(
                r'(scale|scaling|dynamic|adaptive|factor)',
                content,
                re.IGNORECASE
            )

            if scaling_patterns:
                intelligence = self.syphon_extract_intelligence(
                    source="code",
                    tag=tag,
                    intelligence_type="scaling_pattern",
                    data={
                        "file": str(code_path),
                        "scaling_references": len(scaling_patterns),
                        "scaling_keywords": list(set(scaling_patterns))
                    },
                    confidence=0.7
                )
                intelligence_items.append(intelligence)

        except Exception as e:
            logger.debug(f"   Could not extract from {code_path}: {e}")

        return intelligence_items

    def syphon_extract_from_usage_logs(self, tag: str) -> List[ExtractedIntelligence]:
        """@SYPHON: Extract tag usage patterns from logs"""
        intelligence_items = []

        if not self.tag_scaling_system:
            return intelligence_items

        tag_def = self.tag_scaling_system.tag_definitions.get(tag)
        if not tag_def:
            return intelligence_items

        # Extract effectiveness patterns
        if tag_def.effectiveness_history:
            avg_effectiveness = sum(tag_def.effectiveness_history) / len(tag_def.effectiveness_history)
            trend = "improving" if len(tag_def.effectiveness_history) > 1 and \
                tag_def.effectiveness_history[-1] > tag_def.effectiveness_history[0] else "declining"

            intelligence = self.syphon_extract_intelligence(
                source="usage_logs",
                tag=tag,
                intelligence_type="effectiveness_pattern",
                data={
                    "average_effectiveness": avg_effectiveness,
                    "trend": trend,
                    "usage_count": tag_def.usage_count,
                    "success_rate": tag_def.success_rate,
                    "current_scale_factor": tag_def.current_scale_factor
                },
                confidence=0.85
            )
            intelligence_items.append(intelligence)

        return intelligence_items

    def lumina_expand_knowledge(self, tag: str) -> ExpandedTagKnowledge:
        """
        @LUMINA: Expand knowledge base about tag

        Builds comprehensive understanding from extracted intelligence
        """
        # Get base definition
        base_def = ""
        if self.tag_scaling_system:
            tag_def = self.tag_scaling_system.tag_definitions.get(tag)
            if tag_def:
                base_def = tag_def.base_definition

        # Initialize knowledge
        if tag not in self.expanded_knowledge:
            self.expanded_knowledge[tag] = ExpandedTagKnowledge(
                tag=tag,
                base_definition=base_def
            )

        knowledge = self.expanded_knowledge[tag]

        # Extract intelligence for this tag
        tag_intelligence = [
            item for item in self.extracted_intelligence
            if item.tag == tag
        ]

        # Build expanded definitions from intelligence
        expanded_defs = []
        for intel in tag_intelligence:
            if intel.intelligence_type == "usage_pattern":
                expanded_defs.append(
                    f"Used {intel.extracted_data.get('occurrences', 0)} times in code"
                )
            elif intel.intelligence_type == "effectiveness_pattern":
                eff = intel.extracted_data.get('average_effectiveness', 0)
                expanded_defs.append(
                    f"Effectiveness: {eff:.1%} ({intel.extracted_data.get('trend', 'stable')})"
                )

        knowledge.expanded_definitions = expanded_defs

        # Build usage patterns
        usage_intelligence = [
            item for item in tag_intelligence
            if item.intelligence_type == "usage_pattern"
        ]
        if usage_intelligence:
            knowledge.usage_patterns = {
                "total_occurrences": sum(
                    item.extracted_data.get('occurrences', 0)
                    for item in usage_intelligence
                ),
                "files_analyzed": len(usage_intelligence),
                "average_density": sum(
                    item.extracted_data.get('usage_density', 0)
                    for item in usage_intelligence
                ) / len(usage_intelligence) if usage_intelligence else 0
            }

        # Build effectiveness patterns
        eff_intelligence = [
            item for item in tag_intelligence
            if item.intelligence_type == "effectiveness_pattern"
        ]
        if eff_intelligence:
            knowledge.effectiveness_patterns = {
                "average_effectiveness": sum(
                    item.extracted_data.get('average_effectiveness', 0)
                    for item in eff_intelligence
                ) / len(eff_intelligence) if eff_intelligence else 0,
                "trend": eff_intelligence[-1].extracted_data.get('trend', 'stable')
                if eff_intelligence else 'unknown',
                "usage_count": eff_intelligence[-1].extracted_data.get('usage_count', 0)
                if eff_intelligence else 0
            }

        # Build scaling patterns
        scaling_intelligence = [
            item for item in tag_intelligence
            if item.intelligence_type == "scaling_pattern"
        ]
        if scaling_intelligence:
            knowledge.scaling_patterns = {
                "scaling_references": sum(
                    item.extracted_data.get('scaling_references', 0)
                    for item in scaling_intelligence
                ),
                "scaling_keywords": list(set(
                    keyword
                    for item in scaling_intelligence
                    for keyword in item.extracted_data.get('scaling_keywords', [])
                ))
            }

        # Find related tags
        if self.tag_scaling_system:
            for other_tag, other_def in self.tag_scaling_system.tag_definitions.items():
                if other_tag != tag:
                    # Check if tags are used together
                    if tag in other_def.context_adaptations or \
                       other_tag in knowledge.context_patterns:
                        if other_tag not in knowledge.related_tags:
                            knowledge.related_tags.append(other_tag)

        # Update metadata
        knowledge.knowledge_metadata = {
            "last_expanded": datetime.now().isoformat(),
            "intelligence_sources": len(tag_intelligence),
            "confidence": sum(item.confidence for item in tag_intelligence) / len(tag_intelligence)
            if tag_intelligence else 0.0
        }

        self._save_data()

        logger.info(f"   📚 @LUMINA expanded knowledge for {tag}")

        return knowledge

    def expand_all_tags(self):
        """Expand knowledge for all tags"""
        if not self.tag_scaling_system:
            logger.warning("   ⚠️  Tag scaling system not available")
            return

        for tag in self.tag_scaling_system.tag_definitions.keys():
            # Extract intelligence
            self.syphon_extract_from_usage_logs(tag)

            # Expand knowledge
            self.lumina_expand_knowledge(tag)

        logger.info(f"   ✅ Expanded knowledge for {len(self.tag_scaling_system.tag_definitions)} tags")

    def syphon_scan_codebase(self, tag: str):
        try:
            """@SYPHON: Scan codebase for tag usage"""
            scripts_dir = self.project_root / "scripts" / "python"

            if not scripts_dir.exists():
                return

            intelligence_items = []

            for py_file in scripts_dir.rglob("*.py"):
                items = self.syphon_extract_from_code(tag, py_file)
                intelligence_items.extend(items)

            logger.info(f"   📊 @SYPHON scanned codebase for {tag}: {len(intelligence_items)} intelligence items")

            return intelligence_items

        except Exception as e:
            self.logger.error(f"Error in syphon_scan_codebase: {e}", exc_info=True)
            raise
    def get_expanded_knowledge(self, tag: str) -> Optional[ExpandedTagKnowledge]:
        """Get expanded knowledge for tag"""
        return self.expanded_knowledge.get(tag)

    def generate_comprehensive_report(self, tag: str) -> Dict[str, Any]:
        """Generate comprehensive report combining @SYPHON + @LUMINA"""
        report = {
            "tag": tag,
            "timestamp": datetime.now().isoformat(),
            "base_definition": "",
            "expanded_knowledge": {},
            "extracted_intelligence": [],
            "patterns": {},
            "recommendations": []
        }

        # Get base definition
        if self.tag_scaling_system:
            tag_def = self.tag_scaling_system.tag_definitions.get(tag)
            if tag_def:
                report["base_definition"] = tag_def.base_definition
                report["current_scale_factor"] = tag_def.current_scale_factor
                report["effectiveness"] = tag_def.success_rate

        # Get expanded knowledge
        knowledge = self.expanded_knowledge.get(tag)
        if knowledge:
            report["expanded_knowledge"] = {
                "expanded_definitions": knowledge.expanded_definitions,
                "usage_patterns": knowledge.usage_patterns,
                "effectiveness_patterns": knowledge.effectiveness_patterns,
                "scaling_patterns": knowledge.scaling_patterns,
                "context_patterns": knowledge.context_patterns,
                "related_tags": knowledge.related_tags
            }

        # Get extracted intelligence
        tag_intelligence = [
            {
                "source": item.source,
                "type": item.intelligence_type,
                "data": item.extracted_data,
                "confidence": item.confidence
            }
            for item in self.extracted_intelligence
            if item.tag == tag
        ]
        report["extracted_intelligence"] = tag_intelligence

        # Generate recommendations
        if knowledge and knowledge.effectiveness_patterns:
            avg_eff = knowledge.effectiveness_patterns.get("average_effectiveness", 0)
            if avg_eff < 0.5:
                report["recommendations"].append(
                    "Low effectiveness detected - consider adjusting scaling rules"
                )
            elif avg_eff > 0.9:
                report["recommendations"].append(
                    "High effectiveness - can increase scale factor for better performance"
                )

        return report


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="@SYPHON + @LUMINA Tag Expansion System")
        parser.add_argument("--expand", type=str, help="Expand knowledge for tag")
        parser.add_argument("--expand-all", action="store_true", help="Expand all tags")
        parser.add_argument("--syphon-scan", type=str, help="@SYPHON scan codebase for tag")
        parser.add_argument("--get-knowledge", type=str, help="Get expanded knowledge for tag")
        parser.add_argument("--report", type=str, help="Generate comprehensive report for tag")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        system = SyphonLuminaTagExpansion()

        if args.expand:
            knowledge = system.lumina_expand_knowledge(args.expand)
            if args.json:
                print(json.dumps({
                    "tag": knowledge.tag,
                    "base_definition": knowledge.base_definition,
                    "expanded_definitions": knowledge.expanded_definitions,
                    "usage_patterns": knowledge.usage_patterns,
                    "effectiveness_patterns": knowledge.effectiveness_patterns
                }, indent=2))
            else:
                print(f"Expanded Knowledge for {knowledge.tag}:")
                print(f"  Base: {knowledge.base_definition}")
                print(f"  Expanded: {len(knowledge.expanded_definitions)} definitions")
                print(f"  Usage Patterns: {knowledge.usage_patterns}")

        elif args.expand_all:
            system.expand_all_tags()
            print("✅ Expanded knowledge for all tags")

        elif args.syphon_scan:
            items = system.syphon_scan_codebase(args.syphon_scan)
            if args.json:
                print(json.dumps([
                    {
                        "source": item.source,
                        "type": item.intelligence_type,
                        "data": item.extracted_data
                    }
                    for item in items
                ], indent=2))
            else:
                print(f"✅ @SYPHON scanned codebase: {len(items)} intelligence items")

        elif args.get_knowledge:
            knowledge = system.get_expanded_knowledge(args.get_knowledge)
            if knowledge:
                if args.json:
                    print(json.dumps({
                        "tag": knowledge.tag,
                        "expanded_definitions": knowledge.expanded_definitions,
                        "usage_patterns": knowledge.usage_patterns,
                        "effectiveness_patterns": knowledge.effectiveness_patterns
                    }, indent=2))
                else:
                    print(f"Knowledge for {knowledge.tag}:")
                    for defn in knowledge.expanded_definitions:
                        print(f"  - {defn}")
            else:
                print(f"❌ No knowledge found for {args.get_knowledge}")

        elif args.report:
            report = system.generate_comprehensive_report(args.report)
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print(f"Comprehensive Report for {report['tag']}:")
                print(f"  Base Definition: {report['base_definition']}")
                print(f"  Intelligence Items: {len(report['extracted_intelligence'])}")
                print(f"  Recommendations: {len(report['recommendations'])}")
                for rec in report['recommendations']:
                    print(f"    - {rec}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()