#!/usr/bin/env python3
"""
Cursor IDE "+ADD NEW RULE?" Feature Integration

Integrates with Cursor IDE's new "+ADD NEW RULE?" feature to:
1. Capture new rules added via the UI
2. Sync rules to .cursorrules file
3. Manage rule templates
4. Provide rule suggestions based on project context

Tags: #CURSOR_IDE #RULES #.CURSORRULES #NEW_FEATURE @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorAddNewRule")


class CursorAddNewRuleIntegration:
    """
    Cursor IDE "+ADD NEW RULE?" Feature Integration

    Handles:
    - Capturing new rules from Cursor IDE UI
    - Syncing to .cursorrules file
    - Rule template management
    - Context-aware rule suggestions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize rule integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursorrules_file = self.project_root / ".cursorrules"
        self.data_dir = self.project_root / "data" / "cursor_rules"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Rule templates
        self.rule_templates = self._load_rule_templates()

        logger.info("✅ Cursor Add New Rule Integration initialized")
        logger.info(f"   .cursorrules: {self.cursorrules_file}")

    def _load_rule_templates(self) -> Dict[str, Any]:
        """Load rule templates for suggestions"""
        templates = {
            "code_style": [
                "Always use type hints in Python functions",
                "Use descriptive variable names",
                "Follow PEP 8 style guide",
                "Add docstrings to all functions and classes"
            ],
            "project_specific": [
                "Use lumina_logger for all logging",
                "Include tags in file headers",
                "Follow LUMINA project structure",
                "Use Path objects instead of strings for file paths"
            ],
            "security": [
                "Never commit API keys or secrets",
                "Use environment variables for sensitive data",
                "Validate all user inputs",
                "Use secure authentication methods"
            ],
            "testing": [
                "Write unit tests for all new functions",
                "Use pytest for Python tests",
                "Maintain >80% code coverage",
                "Test error cases and edge conditions"
            ],
            "documentation": [
                "Update README when adding features",
                "Document all public APIs",
                "Include usage examples in docstrings",
                "Keep CHANGELOG updated"
            ]
        }
        return templates

    def parse_cursorrules(self) -> Dict[str, Any]:
        """
        Parse existing .cursorrules file.

        Returns:
            Parsed rules structure
        """
        logger.info("=" * 80)
        logger.info("📋 PARSING .CURSORRULES FILE")
        logger.info("=" * 80)
        logger.info("")

        rules = {
            "timestamp": datetime.now().isoformat(),
            "file_exists": False,
            "rules": [],
            "sections": {},
            "line_count": 0
        }

        if not self.cursorrules_file.exists():
            logger.warning("   ⚠️  .cursorrules file not found")
            logger.info(f"      Expected: {self.cursorrules_file}")
            return rules

        rules["file_exists"] = True

        try:
            with open(self.cursorrules_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                rules["line_count"] = len(lines)

                # Parse rules by sections
                current_section = "general"
                current_rules = []

                for line in lines:
                    line = line.strip()

                    # Detect sections
                    if line.startswith('#') and len(line) > 1:
                        # Save previous section
                        if current_rules:
                            rules["sections"][current_section] = current_rules.copy()
                            current_rules = []

                        # New section
                        current_section = line[1:].strip().lower().replace(' ', '_')
                        rules["sections"][current_section] = []

                    # Detect rules (non-empty, non-comment lines)
                    elif line and not line.startswith('#'):
                        current_rules.append(line)
                        rules["rules"].append({
                            "section": current_section,
                            "rule": line
                        })

                # Save last section
                if current_rules:
                    rules["sections"][current_section] = current_rules

                logger.info(f"   ✅ Parsed {len(rules['rules'])} rules")
                logger.info(f"   Sections: {', '.join(rules['sections'].keys())}")

        except Exception as e:
            logger.error(f"   ❌ Error parsing .cursorrules: {e}")
            rules["error"] = str(e)

        return rules

    def add_new_rule(self, rule_text: str, section: Optional[str] = None, 
                     source: str = "manual") -> Dict[str, Any]:
        """
        Add a new rule to .cursorrules file.

        Args:
            rule_text: The rule text to add
            section: Optional section name
            source: Source of the rule (manual, ui, template, etc.)

        Returns:
            Add result
        """
        logger.info("=" * 80)
        logger.info("➕ ADDING NEW RULE")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   Rule: {rule_text}")
        logger.info(f"   Section: {section or 'general'}")
        logger.info(f"   Source: {source}")
        logger.info("")

        result = {
            "timestamp": datetime.now().isoformat(),
            "rule_text": rule_text,
            "section": section or "general",
            "source": source,
            "added": False,
            "backup_created": False
        }

        # Create backup
        if self.cursorrules_file.exists():
            backup_file = self.data_dir / f".cursorrules.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(self.cursorrules_file, backup_file)
                result["backup_created"] = True
                result["backup_file"] = str(backup_file)
                logger.info(f"   ✅ Backup created: {backup_file.name}")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not create backup: {e}")

        # Read existing content
        existing_content = ""
        if self.cursorrules_file.exists():
            try:
                with open(self.cursorrules_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            except Exception as e:
                logger.error(f"   ❌ Error reading .cursorrules: {e}")
                result["error"] = str(e)
                return result

        # Add new rule
        try:
            # If section specified, find or create section
            if section:
                section_header = f"# {section.replace('_', ' ').title()}"

                # Check if section exists
                if section_header in existing_content:
                    # Add rule to existing section
                    pattern = f"({re.escape(section_header)}[\\s\\S]*?)(?=\\n# |$)"
                    replacement = f"\\1\\n{rule_text}"
                    new_content = re.sub(pattern, replacement, existing_content, flags=re.MULTILINE)
                else:
                    # Add new section
                    new_content = f"{existing_content}\\n\\n{section_header}\\n{rule_text}"
            else:
                # Add to end
                if existing_content and not existing_content.endswith('\\n'):
                    new_content = f"{existing_content}\\n{rule_text}"
                else:
                    new_content = f"{existing_content}{rule_text}"

            # Write updated content
            with open(self.cursorrules_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            result["added"] = True
            logger.info("   ✅ Rule added successfully")

            # Log rule addition
            self._log_rule_addition(result)

        except Exception as e:
            logger.error(f"   ❌ Error adding rule: {e}")
            result["error"] = str(e)

        return result

    def suggest_rules(self, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Suggest rules based on project context.

        Args:
            context: Optional context (file type, project area, etc.)

        Returns:
            List of suggested rules
        """
        logger.info("=" * 80)
        logger.info("💡 SUGGESTING RULES")
        logger.info("=" * 80)
        logger.info("")

        suggestions = []

        # Get existing rules to avoid duplicates
        existing_rules = self.parse_cursorrules()
        existing_rule_texts = {r["rule"].lower() for r in existing_rules.get("rules", [])}

        # Context-based suggestions
        if context:
            file_type = context.get("file_type", "").lower()
            project_area = context.get("project_area", "").lower()

            # Python-specific
            if file_type == "python":
                suggestions.extend([
                    "Use type hints for all function parameters and return types",
                    "Follow PEP 8 naming conventions",
                    "Add docstrings using Google or NumPy style",
                    "Use pathlib.Path instead of os.path for file operations"
                ])

            # JavaScript/TypeScript
            elif file_type in ["javascript", "typescript"]:
                suggestions.extend([
                    "Use TypeScript for new files when possible",
                    "Use const/let instead of var",
                    "Use async/await instead of promises",
                    "Add JSDoc comments for all exported functions"
                ])

            # Documentation
            if project_area == "docs":
                suggestions.extend([
                    "Use Markdown format for documentation",
                    "Include code examples in documentation",
                    "Keep documentation up to date with code changes"
                ])

        # General suggestions from templates
        for category, template_rules in self.rule_templates.items():
            for rule in template_rules:
                if rule.lower() not in existing_rule_texts:
                    suggestions.append(rule)

        # Remove duplicates
        suggestions = list(dict.fromkeys(suggestions))

        logger.info(f"   ✅ Generated {len(suggestions)} suggestions")
        if suggestions:
            logger.info("   Top suggestions:")
            for i, suggestion in enumerate(suggestions[:5], 1):
                logger.info(f"      {i}. {suggestion}")

        return suggestions

    def _log_rule_addition(self, result: Dict[str, Any]):
        """Log rule addition for tracking"""
        log_file = self.data_dir / "rule_additions.jsonl"

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\\n')
        except Exception as e:
            logger.debug(f"Could not log rule addition: {e}")

    def get_rule_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about rules.

        Returns:
            Rule statistics
        """
        rules = self.parse_cursorrules()

        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_rules": len(rules.get("rules", [])),
            "sections": len(rules.get("sections", {})),
            "file_exists": rules.get("file_exists", False),
            "line_count": rules.get("line_count", 0),
            "sections_breakdown": {
                section: len(rules_list)
                for section, rules_list in rules.get("sections", {}).items()
            }
        }

        return stats

    def export_rules_template(self, output_file: Optional[Path] = None) -> Path:
        try:
            """
            Export rules as a template for other projects.

            Args:
                output_file: Optional output file path

            Returns:
                Path to exported template
            """
            if output_file is None:
                output_file = self.data_dir / f"cursorrules_template_{datetime.now().strftime('%Y%m%d')}.txt"

            rules = self.parse_cursorrules()

            template_content = "# Cursor IDE Rules Template\\n"
            template_content += f"# Generated: {datetime.now().isoformat()}\\n"
            template_content += f"# Total Rules: {len(rules.get('rules', []))}\\n\\n"

            for section, rules_list in rules.get("sections", {}).items():
                template_content += f"# {section.replace('_', ' ').title()}\\n"
                for rule in rules_list:
                    template_content += f"{rule}\\n"
                template_content += "\\n"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template_content)

            logger.info(f"✅ Template exported: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in export_rules_template: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Add New Rule Integration")
        parser.add_argument("--add-rule", help="Add a new rule")
        parser.add_argument("--section", help="Section for the rule")
        parser.add_argument("--suggest", action="store_true", help="Suggest rules")
        parser.add_argument("--parse", action="store_true", help="Parse existing rules")
        parser.add_argument("--stats", action="store_true", help="Show rule statistics")
        parser.add_argument("--export-template", help="Export rules template (optional filename)")

        args = parser.parse_args()

        integration = CursorAddNewRuleIntegration()

        if args.add_rule:
            result = integration.add_new_rule(args.add_rule, section=args.section, source="cli")
            if result.get("added"):
                print(f"✅ Rule added: {args.add_rule}")
            else:
                print(f"❌ Failed to add rule: {result.get('error', 'Unknown error')}")

        elif args.suggest:
            suggestions = integration.suggest_rules()
            print("\\n💡 Suggested Rules:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")

        elif args.parse:
            rules = integration.parse_cursorrules()
            print(f"\\n📋 Parsed {len(rules.get('rules', []))} rules")
            print(f"Sections: {', '.join(rules.get('sections', {}).keys())}")

        elif args.stats:
            stats = integration.get_rule_statistics()
            print("\\n📊 Rule Statistics:")
            print(f"  Total Rules: {stats['total_rules']}")
            print(f"  Sections: {stats['sections']}")
            print(f"  Line Count: {stats['line_count']}")
            print("\\n  Sections Breakdown:")
            for section, count in stats['sections_breakdown'].items():
                print(f"    {section}: {count} rules")

        elif args.export_template:
            output_file = Path(args.export_template) if args.export_template else None
            template_file = integration.export_rules_template(output_file)
            print(f"✅ Template exported: {template_file}")

        else:
            # Default: show stats
            stats = integration.get_rule_statistics()
            print("\\n📊 Cursor IDE Rules Status:")
            print(f"  File Exists: {stats['file_exists']}")
            print(f"  Total Rules: {stats['total_rules']}")
            print(f"  Sections: {stats['sections']}")
            print("\\nUse --help for more options")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())