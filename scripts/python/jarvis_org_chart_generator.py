#!/usr/bin/env python3
"""
JARVIS Organizational Chart Generator
Generates visual organizational charts from organizational structure.

Tags: #ORGANIZATIONAL #CHART #VISUALIZATION @AUTO
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
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

logger = get_logger("JARVISOrgChart")


class OrgChartGenerator:
    """Generate organizational charts in various formats"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.org = LuminaOrganizationalStructure(project_root) if LuminaOrganizationalStructure else None

    def generate_text_chart(self) -> str:
        """Generate text-based organizational chart"""
        if not self.org:
            return "❌ Organizational structure not available"

        chart = []
        chart.append("=" * 80)
        chart.append("LUMINA ORGANIZATIONAL CHART")
        chart.append("=" * 80)
        chart.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        chart.append("")

        # Summary
        summary = self.org.get_organizational_chart()['summary']
        chart.append("📊 SUMMARY")
        chart.append("-" * 80)
        chart.append(f"  Total Divisions: {summary['total_divisions']}")
        chart.append(f"  Total Teams: {summary['total_teams']}")
        chart.append(f"  Total Members: {summary['total_members']}")
        chart.append(f"  Analysts: {summary['analysts']}")
        chart.append(f"  Engineers: {summary['engineers']}")
        chart.append(f"  Droids: {summary['droids']}")
        chart.append(f"  Agents: {summary['agents']}")
        chart.append("")

        # Divisions and Teams
        divisions = self.org.get_all_divisions()

        # Separate IT and Business divisions
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
            chart.append("=" * 80)
            chart.append("IT & TECHNICAL DIVISIONS")
            chart.append("=" * 80)
            chart.append("")

            for div in sorted(it_divisions, key=lambda x: x['division_name']):
                chart.append(f"🏢 {div['division_name']}")
                chart.append(f"   Division Head: {div.get('division_head', 'N/A')}")
                chart.append(f"   Teams: {div['team_count']}, Members: {div['total_members']}")
                chart.append(f"   Description: {div.get('description', 'N/A')}")
                chart.append("")

                # Teams in this division
                for team_data in div.get('teams', []):
                    chart.append(f"   👥 {team_data.get('team_name', 'Unknown Team')}")
                    chart.append(f"      Team Lead: {team_data.get('team_lead', 'N/A')}")
                    chart.append(f"      Manager: {team_data.get('helpdesk_manager', 'N/A')}")
                    chart.append(f"      Members: {team_data.get('member_count', 0)}")

                    # Key members
                    members = team_data.get('members', [])
                    if members:
                        chart.append("      Key Members:")
                        for member in members[:5]:  # Show first 5
                            member_type_icon = {
                                'droid': '🤖',
                                'engineer': '🔧',
                                'analyst': '📊',
                                'manager': '👔',
                                'coordinator': '📋',
                                'specialist': '🎯'
                            }.get(member.get('member_type', '').lower(), '👤')
                            chart.append(f"         {member_type_icon} {member.get('name', 'Unknown')} - {member.get('role', 'N/A')}")
                    chart.append("")

        # Business Divisions
        if business_divisions:
            chart.append("=" * 80)
            chart.append("BUSINESS DIVISIONS")
            chart.append("=" * 80)
            chart.append("")

            for div in sorted(business_divisions, key=lambda x: x['division_name']):
                chart.append(f"🏢 {div['division_name']}")
                chart.append(f"   Division Head: {div.get('division_head', 'N/A')}")
                chart.append(f"   Teams: {div['team_count']}, Members: {div['total_members']}")
                chart.append(f"   Description: {div.get('description', 'N/A')}")
                chart.append("")

                # Teams in this division
                for team_data in div.get('teams', []):
                    chart.append(f"   👥 {team_data.get('team_name', 'Unknown Team')}")
                    chart.append(f"      Team Lead: {team_data.get('team_lead', 'N/A')}")
                    chart.append(f"      Manager: {team_data.get('helpdesk_manager', 'N/A')}")
                    chart.append(f"      Members: {team_data.get('member_count', 0)}")

                    # Key members
                    members = team_data.get('members', [])
                    if members:
                        chart.append("      Key Members:")
                        for member in members[:5]:  # Show first 5
                            member_type_icon = {
                                'droid': '🤖',
                                'engineer': '🔧',
                                'analyst': '📊',
                                'manager': '👔',
                                'coordinator': '📋',
                                'specialist': '🎯'
                            }.get(member.get('member_type', '').lower(), '👤')
                            chart.append(f"         {member_type_icon} {member.get('name', 'Unknown')} - {member.get('role', 'N/A')}")
                    chart.append("")

        # Other Divisions
        if other_divisions:
            chart.append("=" * 80)
            chart.append("OTHER DIVISIONS")
            chart.append("=" * 80)
            chart.append("")

            for div in sorted(other_divisions, key=lambda x: x['division_name']):
                chart.append(f"🏢 {div['division_name']}")
                chart.append(f"   Division Head: {div.get('division_head', 'N/A')}")
                chart.append(f"   Teams: {div['team_count']}, Members: {div['total_members']}")
                chart.append("")

        chart.append("=" * 80)
        chart.append("END OF ORGANIZATIONAL CHART")
        chart.append("=" * 80)

        return "\n".join(chart)

    def generate_markdown_chart(self) -> str:
        """Generate markdown organizational chart"""
        if not self.org:
            return "❌ Organizational structure not available"

        md = []
        md.append("# Lumina Organizational Chart")
        md.append("")
        md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")

        # Summary
        summary = self.org.get_organizational_chart()['summary']
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
        divisions = self.org.get_all_divisions()

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

                    # Key members
                    members = team_data.get('members', [])
                    if members:
                        md.append("**Key Members:**")
                        md.append("")
                        for member in members[:10]:  # Show first 10
                            member_type = member.get('member_type', '').title()
                            md.append(f"- **{member.get('name', 'Unknown')}** ({member_type}) - {member.get('role', 'N/A')}")
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

        return "\n".join(md)

    def save_chart(self, format: str = "text") -> Path:
        try:
            """Save organizational chart to file"""
            if format == "markdown":
                content = self.generate_markdown_chart()
                ext = "md"
            else:
                content = self.generate_text_chart()
                ext = "txt"

            output_dir = self.project_root / "docs" / "organizational"
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = output_dir / f"org_chart_{timestamp}.{ext}"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"✅ Organizational chart saved to {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in save_chart: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Generate organizational charts")
        parser.add_argument("--format", choices=["text", "markdown"], default="text", help="Chart format")
        parser.add_argument("--save", action="store_true", help="Save chart to file")
        parser.add_argument("--display", action="store_true", help="Display chart")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        generator = OrgChartGenerator(project_root)

        if args.save:
            output_file = generator.save_chart(format=args.format)
            print(f"✅ Chart saved to: {output_file}")

        if args.display or not args.save:
            if args.format == "markdown":
                print(generator.generate_markdown_chart())
            else:
                print(generator.generate_text_chart())


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()