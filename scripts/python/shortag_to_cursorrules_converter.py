#!/usr/bin/env python3
"""
Short@Tag to Cursor Rules Converter
Converts short@tags from shortag_registry.json into .cursorrules format

This bridges the gap between short@tagging and Cursor's @rules feature
(pending Cursor team update for native support).

Tags: #SHORTAG #CURSORRULES #CONVERSION #RULES @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
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

logger = get_logger("ShortagToCursorRules")


class ShortagToCursorRulesConverter:
    """
    Converts short@tags to Cursor rules format

    This allows short@tags to function as @rules in Cursor IDE,
    bridging the gap until native support is available.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize converter"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Paths
        self.shortag_registry = self.project_root / "config" / "shortag_registry.json"
        self.cursorrules_file = self.project_root / ".cursorrules"

        # Load shortag registry
        self.shortags: Dict[str, Any] = {}
        self._load_shortags()

        logger.info("📋 Short@Tag to Cursor Rules Converter initialized")

    def _load_shortags(self) -> None:
        """Load shortag registry"""
        if not self.shortag_registry.exists():
            logger.warning(f"⚠️  Shortag registry not found: {self.shortag_registry}")
            return

        try:
            with open(self.shortag_registry, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Filter out metadata
                self.shortags = {
                    k: v for k, v in data.items() 
                    if not k.startswith("_")
                }
            logger.info(f"✅ Loaded {len(self.shortags)} short@tags")
        except Exception as e:
            logger.error(f"❌ Error loading shortag registry: {e}")

    def _convert_tag_to_rule(self, tag_name: str, tag_data: Dict[str, Any]) -> str:
        """Convert a single tag to Cursor rules format"""
        tag_type = tag_data.get("type", "mention")
        category = tag_data.get("category", "general")
        description = tag_data.get("description", "")
        usage = tag_data.get("usage", "")
        module = tag_data.get("module", "")
        class_name = tag_data.get("class", "")

        # Build rule text
        rule_lines = []

        # Rule header
        rule_lines.append(f"## {tag_name}")
        rule_lines.append("")

        # Description
        if description:
            rule_lines.append(f"**Description**: {description}")
            rule_lines.append("")

        # Type and category
        rule_lines.append(f"**Type**: {tag_type}")
        rule_lines.append(f"**Category**: {category}")
        rule_lines.append("")

        # Usage instructions
        if usage:
            rule_lines.append("**Usage**:")
            rule_lines.append(f"{usage}")
            rule_lines.append("")

        # Module/class information
        if module:
            rule_lines.append("**Implementation**:")
            rule_lines.append(f"- Module: `{module}`")
            if class_name:
                rule_lines.append(f"- Class: `{class_name}`")
            rule_lines.append("")

        # Context weights
        context_weight = tag_data.get("context_weight", 0.5)
        ai_weight = tag_data.get("ai_weight", 0.5)
        human_weight = tag_data.get("human_weight", 0.5)

        rule_lines.append("**Context Weights**:")
        rule_lines.append(f"- Context Weight: {context_weight}")
        rule_lines.append(f"- AI Weight: {ai_weight}")
        rule_lines.append(f"- Human Weight: {human_weight}")
        rule_lines.append("")

        # Examples
        examples = tag_data.get("examples", [])
        if examples:
            rule_lines.append("**Examples**:")
            for example in examples:
                rule_lines.append(f"- `{example}`")
            rule_lines.append("")

        # Precedence (if applicable)
        precedence = tag_data.get("precedence")
        if precedence:
            rule_lines.append(f"**Precedence**: {precedence}")
            rule_lines.append("")

        # Alias information
        alias_of = tag_data.get("alias_of")
        if alias_of:
            rule_lines.append(f"**Alias Of**: {alias_of}")
            rule_lines.append("")

        # Pipe information
        pipe_to = tag_data.get("pipe_to")
        if pipe_to:
            rule_lines.append(f"**Pipes To**: {pipe_to}")
            rule_lines.append("")

        # Rule enforcement
        rule_lines.append("**Rule**:")
        rule_lines.append(f"When `{tag_name}` is mentioned in chat or code:")
        rule_lines.append(f"1. Recognize it as a {tag_type} in the {category} category")
        rule_lines.append(f"2. Apply context weight of {context_weight}")
        rule_lines.append(f"3. Use AI weight of {ai_weight} and human weight of {human_weight}")
        if usage:
            rule_lines.append(f"4. Follow usage guidelines: {usage}")
        rule_lines.append("")

        return "\n".join(rule_lines)

    def generate_cursorrules_section(self) -> str:
        """Generate Cursor rules section from short@tags"""
        section_lines = []

        section_lines.append("# Short@Tag Rules")
        section_lines.append("")
        section_lines.append("This section contains rules derived from short@tags in `config/shortag_registry.json`.")
        section_lines.append("These rules enable short@tags to function as @rules in Cursor IDE.")
        section_lines.append("")
        section_lines.append(f"**Generated**: {datetime.now().isoformat()}")
        section_lines.append(f"**Total Tags**: {len(self.shortags)}")
        section_lines.append("")
        section_lines.append("---")
        section_lines.append("")

        # Group tags by category
        by_category: Dict[str, List[tuple]] = {}
        for tag_name, tag_data in self.shortags.items():
            category = tag_data.get("category", "general")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((tag_name, tag_data))

        # Generate rules by category
        for category in sorted(by_category.keys()):
            section_lines.append(f"## {category.title()} Tags")
            section_lines.append("")

            for tag_name, tag_data in sorted(by_category[category]):
                rule_text = self._convert_tag_to_rule(tag_name, tag_data)
                section_lines.append(rule_text)
                section_lines.append("---")
                section_lines.append("")

        return "\n".join(section_lines)

    def append_to_cursorrules(self, backup: bool = True) -> bool:
        """Append short@tag rules to .cursorrules file"""
        if not self.cursorrules_file.exists():
            logger.warning(f"⚠️  .cursorrules file not found: {self.cursorrules_file}")
            logger.info("   Creating new .cursorrules file...")

        # Backup existing file
        if backup and self.cursorrules_file.exists():
            backup_file = self.cursorrules_file.with_suffix('.cursorrules.bak')
            try:
                import shutil
                shutil.copy2(self.cursorrules_file, backup_file)
                logger.info(f"💾 Backed up existing .cursorrules to {backup_file.name}")
            except Exception as e:
                logger.warning(f"⚠️  Could not backup .cursorrules: {e}")

        # Generate rules section
        rules_section = self.generate_cursorrules_section()

        # Read existing content
        existing_content = ""
        if self.cursorrules_file.exists():
            try:
                with open(self.cursorrules_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            except Exception as e:
                logger.warning(f"⚠️  Error reading existing .cursorrules: {e}")

        # Check if section already exists
        if "# Short@Tag Rules" in existing_content:
            logger.info("📝 Short@Tag Rules section already exists in .cursorrules")
            logger.info("   Updating existing section...")

            # Replace existing section
            import re
            pattern = r"# Short@Tag Rules.*?(?=\n# |\Z)"
            new_content = re.sub(pattern, rules_section, existing_content, flags=re.DOTALL)
        else:
            # Append new section
            new_content = existing_content
            if new_content and not new_content.endswith("\n\n"):
                new_content += "\n\n"
            new_content += rules_section

        # Write updated content
        try:
            with open(self.cursorrules_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"✅ Updated .cursorrules with short@tag rules")
            return True
        except Exception as e:
            logger.error(f"❌ Error writing .cursorrules: {e}")
            return False

    def generate_standalone_rules_file(self, output_path: Optional[Path] = None) -> Path:
        """Generate standalone rules file"""
        if output_path is None:
            output_path = self.project_root / ".cursorrules.shortags"

        rules_content = self.generate_cursorrules_section()

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rules_content)
            logger.info(f"✅ Generated standalone rules file: {output_path.name}")
            return output_path
        except Exception as e:
            logger.error(f"❌ Error generating rules file: {e}")
            raise


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Short@Tag to Cursor Rules Converter")
        parser.add_argument("--append", action="store_true", 
                           help="Append rules to existing .cursorrules file")
        parser.add_argument("--standalone", action="store_true",
                           help="Generate standalone rules file")
        parser.add_argument("--output", type=str,
                           help="Output file path (for standalone mode)")
        parser.add_argument("--no-backup", action="store_true",
                           help="Don't backup existing .cursorrules")

        args = parser.parse_args()

        converter = ShortagToCursorRulesConverter()

        if args.append:
            success = converter.append_to_cursorrules(backup=not args.no_backup)
            if success:
                print("\n✅ Short@Tag rules appended to .cursorrules")
                print("   Cursor IDE will now recognize short@tags as @rules")
            else:
                print("\n❌ Failed to append rules")

        elif args.standalone:
            output_path = Path(args.output) if args.output else None
            converter.generate_standalone_rules_file(output_path)
            print(f"\n✅ Standalone rules file generated")

        else:
            # Preview mode
            rules_section = converter.generate_cursorrules_section()
            print(rules_section)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()