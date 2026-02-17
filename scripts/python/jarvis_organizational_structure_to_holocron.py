#!/usr/bin/env python3
"""
JARVIS Organizational Structure to Holocron
Moves organizational structure data into Holocron Archive.

Tags: #ORGANIZATIONAL #HOLOCRON #KNOWLEDGE @AUTO
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from lumina_organizational_structure import LuminaOrganizationalStructure
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    LuminaOrganizationalStructure = None

logger = get_logger("JARVISOrgToHolocron")


class OrganizationalStructureToHolocron:
    """Move organizational structure to Holocron Archive"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.org = LuminaOrganizationalStructure(project_root) if LuminaOrganizationalStructure else None
        self.holocron_dir = project_root / "data" / "holocron"
        self.holocron_index = self.holocron_dir / "HOLOCRON_INDEX.json"
        self.org_dir = self.holocron_dir / "organizational_structure"
        self.org_dir.mkdir(parents=True, exist_ok=True)

    def create_holocron_entry(self) -> Dict[str, Any]:
        try:
            """Create Holocron entry for organizational structure"""
            if not self.org:
                return {}

            # Get organizational chart
            chart = self.org.get_organizational_chart()

            # Save organizational structure JSON
            org_file = self.org_dir / f"organizational_structure_{datetime.now().strftime('%Y%m%d')}.json"
            with open(org_file, 'w', encoding='utf-8') as f:
                json.dump(chart, f, indent=2, default=str)

            # Create markdown documentation
            md_file = self.org_dir / "organizational_structure.md"
            md_content = self._generate_markdown_documentation(chart)
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)

            # Create Holocron entry
            entry = {
                "entry_id": "HOLOCRON-ORG-001",
                "title": "Lumina Organizational Structure - Complete Company Organization",
                "location": str(md_file.relative_to(self.project_root)),
                "json_location": str(org_file.relative_to(self.project_root)),
                "classification": "Organizational Structure",
                "helpdesk_location": "@helpdesk",
                "associated_droids": [
                    "@c3po",
                    "@r2d2",
                    "@r5"
                ],
                "tags": [
                    "#organizational",
                    "#structure",
                    "#teams",
                    "#divisions",
                    "#it",
                    "#business",
                    "#management",
                    "#helpdesk"
                ],
                "status": "active",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "integration_points": {
                    "primary_droid": "@c3po",
                    "supporting_droids": [
                        "@r2d2",
                        "@r5"
                    ],
                    "workflow_triggers": [
                        "@helpdesk",
                        "@team",
                        "@organizational"
                    ],
                    "related_entries": []
                },
                "metadata": {
                    "total_divisions": chart['summary']['total_divisions'],
                    "total_teams": chart['summary']['total_teams'],
                    "total_members": chart['summary']['total_members'],
                    "it_divisions": len([d for d in chart['divisions'] if any(kw in d['division_name'].lower() for kw in ['it', 'engineering', 'technical', 'network', 'security', 'system', 'docker', 'storage', 'database', 'devops', 'monitoring', 'backup', 'quality', 'performance', 'ai', 'intelligence'])]),
                    "business_divisions": len([d for d in chart['divisions'] if any(kw in d['division_name'].lower() for kw in ['business', 'product', 'project', 'customer', 'finance', 'compliance', 'documentation'])]),
                    "generated_by": "jarvis_organizational_structure_to_holocron.py",
                    "generated_at": datetime.now().isoformat()
                }
            }

            return entry

        except Exception as e:
            self.logger.error(f"Error in create_holocron_entry: {e}", exc_info=True)
            raise
    def _generate_markdown_documentation(self, chart: Dict[str, Any]) -> str:
        """Generate markdown documentation for organizational structure"""
        md = []
        md.append("# Lumina Organizational Structure")
        md.append("")
        md.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"**Entry ID:** HOLOCRON-ORG-001")
        md.append("")
        md.append("## Overview")
        md.append("")
        md.append("Complete organizational structure of Lumina, including all IT and Business divisions, teams, and members.")
        md.append("")

        # Summary
        summary = chart['summary']
        md.append("## Summary")
        md.append("")
        md.append(f"- **Total Divisions:** {summary['total_divisions']}")
        md.append(f"- **Total Teams:** {summary['total_teams']}")
        md.append(f"- **Total Members:** {summary['total_members']}")
        md.append(f"- **Analysts:** {summary['analysts']}")
        md.append(f"- **Engineers:** {summary['engineers']}")
        md.append(f"- **Droids:** {summary['droids']}")
        md.append(f"- **Agents:** {summary['agents']}")
        md.append("")

        # Divisions
        divisions = chart['divisions']

        # Separate IT and Business
        it_divisions = []
        business_divisions = []
        other_divisions = []

        for div in divisions:
            div_name = div['division_name'].lower()
            if any(keyword in div_name for keyword in ['it', 'engineering', 'technical', 'infrastructure', 'network', 'security', 'system', 'docker', 'storage', 'database', 'devops', 'monitoring', 'backup', 'quality', 'performance', 'ai', 'intelligence']):
                it_divisions.append(div)
            elif any(keyword in div_name for keyword in ['business', 'product', 'project', 'customer', 'finance', 'compliance', 'documentation']):
                business_divisions.append(div)
            else:
                other_divisions.append(div)

        # IT Divisions
        if it_divisions:
            md.append("## IT & Technical Divisions")
            md.append("")

            for div in sorted(it_divisions, key=lambda x: x['division_name']):
                md.append(f"### {div['division_name']}")
                md.append("")
                md.append(f"- **Division Head:** {div.get('division_head', 'N/A')}")
                md.append(f"- **Teams:** {div['team_count']}")
                md.append(f"- **Members:** {div['total_members']}")
                md.append(f"- **Description:** {div.get('description', 'N/A')}")
                md.append("")

                # Teams
                for team_data in div.get('teams', []):
                    md.append(f"#### {team_data.get('team_name', 'Unknown Team')}")
                    md.append("")
                    md.append(f"- **Team Lead:** {team_data.get('team_lead', 'N/A')}")
                    md.append(f"- **Manager:** {team_data.get('helpdesk_manager', 'N/A')}")
                    md.append(f"- **Members:** {team_data.get('member_count', 0)}")
                    md.append("")

        # Business Divisions
        if business_divisions:
            md.append("## Business Divisions")
            md.append("")

            for div in sorted(business_divisions, key=lambda x: x['division_name']):
                md.append(f"### {div['division_name']}")
                md.append("")
                md.append(f"- **Division Head:** {div.get('division_head', 'N/A')}")
                md.append(f"- **Teams:** {div['team_count']}")
                md.append(f"- **Members:** {div['total_members']}")
                md.append("")

        md.append("## Team Structure Pattern")
        md.append("")
        md.append("All teams follow the established pattern:")
        md.append("- **Team Manager:** `@c3po` (Helpdesk Coordinator)")
        md.append("- **Technical Lead:** `@r2d2` (Technical Lead Engineer)")
        md.append("- **Business Lead:** [Domain-specific lead]")
        md.append("")

        md.append("## Related Files")
        md.append("")
        md.append("- Organizational Chart Generator: `scripts/python/jarvis_org_chart_generator.py`")
        md.append("- Organizational Structure: `scripts/python/lumina_organizational_structure.py`")
        md.append("")

        return "\n".join(md)

    def update_holocron_index(self, entry: Dict[str, Any]) -> bool:
        """Update HOLOCRON_INDEX.json with organizational structure entry"""
        try:
            # Read existing index
            if self.holocron_index.exists():
                with open(self.holocron_index, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {
                    "archive_metadata": {
                        "name": "Holocron Archive - Master Index",
                        "version": "1.0.0",
                        "last_updated": datetime.now().isoformat(),
                        "status": "operational",
                        "classification": "general_access",
                        "purpose": "Central catalog of all @helpdesk tagged entries and system documentation",
                        "location": "data/holocron/",
                        "maintained_by": "@r5 (Knowledge & Context Matrix Specialist)"
                    },
                    "archive_philosophy": {
                        "core_principle": "All knowledge must be accessible, verifiable, and actionable",
                        "defense_philosophy": "Proactive optimization through intelligent resource management",
                        "mission": "Catalog and optimize system performance through @helpdesk coordination"
                    },
                    "entries": {}
                }

            # Add organizational structure entry
            if "entries" not in index:
                index["entries"] = {}

            if "organizational_structure" not in index["entries"]:
                index["entries"]["organizational_structure"] = {}

            index["entries"]["organizational_structure"]["organizational_structure"] = entry

            # Update metadata
            index["archive_metadata"]["last_updated"] = datetime.now().isoformat()

            # Write back
            with open(self.holocron_index, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Updated HOLOCRON_INDEX.json with organizational structure entry")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to update HOLOCRON_INDEX.json: {e}", exc_info=True)
            return False

    def migrate_to_holocron(self) -> Dict[str, Any]:
        """Complete migration to Holocron"""
        self.logger.info("="*80)
        self.logger.info("MIGRATING ORGANIZATIONAL STRUCTURE TO HOLOCRON")
        self.logger.info("="*80)

        if not self.org:
            return {"success": False, "error": "Organizational structure not available"}

        # Create entry
        self.logger.info("1. Creating Holocron entry...")
        entry = self.create_holocron_entry()

        if not entry:
            return {"success": False, "error": "Failed to create entry"}

        self.logger.info(f"   ✅ Created entry: {entry['entry_id']}")
        self.logger.info(f"   📄 Markdown: {entry['location']}")
        self.logger.info(f"   📊 JSON: {entry['json_location']}")

        # Update index
        self.logger.info("2. Updating HOLOCRON_INDEX.json...")
        success = self.update_holocron_index(entry)

        if success:
            self.logger.info("   ✅ HOLOCRON_INDEX.json updated")
        else:
            self.logger.warning("   ⚠️  Failed to update index")

        return {
            "success": success,
            "entry": entry,
            "entry_id": entry.get("entry_id"),
            "markdown_file": entry.get("location"),
            "json_file": entry.get("json_location")
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Migrate organizational structure to Holocron")
        parser.add_argument("--migrate", action="store_true", help="Complete migration to Holocron")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        migrator = OrganizationalStructureToHolocron(project_root)

        if args.migrate:
            result = migrator.migrate_to_holocron()
            print(json.dumps(result, indent=2, default=str))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()