#!/usr/bin/env python3
"""
PM Team Setup Tool - Create and configure PM team structure

Part of LUMINA @PEAK Project Management Team rollout.

Tags: #PM_TEAM #SETUP #CONFIGURATION #PEAK @LUMINA
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("PMTeamSetup")


class PMTeamSetup:
    """Setup and configure PM team structure"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.team_structure_file = project_root / "data" / "pm_team" / "pm_team_structure.json"
        self.team_structure_file.parent.mkdir(parents=True, exist_ok=True)
        
    def load_team_structure(self) -> Dict[str, Any]:
        """Load team structure"""
        if self.team_structure_file.exists():
            with open(self.team_structure_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def assign_team_member(self, role: str, member_name: str, member_email: str, 
                           member_skills: list, member_tools: list) -> bool:
        """Assign a team member to a role"""
        structure = self.load_team_structure()
        
        # Find role in structure
        role_path = self._find_role_path(structure, role)
        if not role_path:
            logger.error(f"Role '{role}' not found in team structure")
            return False
        
        # Update role assignment
        role_data = self._get_role_data(structure, role_path)
        role_data["assigned_member"] = {
            "name": member_name,
            "email": member_email,
            "assigned_date": datetime.now().isoformat(),
            "skills": member_skills,
            "tools_access": member_tools
        }
        role_data["status"] = "assigned"
        
        # Save structure
        self._save_structure(structure)
        
        logger.info(f"✅ Assigned {member_name} to {role}")
        return True
    
    def _find_role_path(self, structure: Dict[str, Any], role: str) -> Optional[list]:
        """Find path to role in structure"""
        # Search in team_structure
        if "team_structure" in structure:
            ts = structure["team_structure"]
            
            # Check program_manager
            if ts.get("program_manager", {}).get("role") == role:
                return ["team_structure", "program_manager"]
            
            # Check technical_pms
            if "technical_pms" in ts:
                for project, pm_data in ts["technical_pms"].items():
                    if pm_data.get("role") == role:
                        return ["team_structure", "technical_pms", project]
            
            # Check supporting_roles
            if "supporting_roles" in ts:
                for role_key, role_data in ts["supporting_roles"].items():
                    if role_data.get("role") == role:
                        return ["team_structure", "supporting_roles", role_key]
        
        return None
    
    def _get_role_data(self, structure: Dict[str, Any], path: list) -> Dict[str, Any]:
        """Get role data from path"""
        data = structure
        for key in path:
            data = data[key]
        return data
    
    def _save_structure(self, structure: Dict[str, Any]):
        """Save team structure"""
        with open(self.team_structure_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
    
    def generate_team_report(self) -> str:
        """Generate team status report"""
        structure = self.load_team_structure()
        
        if not structure:
            return "Team structure not found"
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("LUMINA @PEAK PROJECT MANAGEMENT TEAM STATUS")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        ts = structure.get("team_structure", {})
        
        # Program Manager
        pm = ts.get("program_manager", {})
        report_lines.append(f"Program Manager: {pm.get('status', 'pending_assignment')}")
        if "assigned_member" in pm:
            report_lines.append(f"  Assigned: {pm['assigned_member']['name']}")
        report_lines.append("")
        
        # Technical PMs
        report_lines.append("Technical Project Managers:")
        t_pms = ts.get("technical_pms", {})
        for project, pm_data in t_pms.items():
            status = pm_data.get("status", "pending_assignment")
            report_lines.append(f"  {project.upper()}: {status}")
            if "assigned_member" in pm_data:
                report_lines.append(f"    Assigned: {pm_data['assigned_member']['name']}")
        report_lines.append("")
        
        # Supporting Roles
        report_lines.append("Supporting Roles:")
        supporting = ts.get("supporting_roles", {})
        for role_key, role_data in supporting.items():
            status = role_data.get("status", "pending_assignment")
            role_name = role_data.get("role", role_key)
            report_lines.append(f"  {role_name}: {status}")
            if "assigned_member" in role_data:
                report_lines.append(f"    Assigned: {role_data['assigned_member']['name']}")
        report_lines.append("")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PM Team Setup Tool")
    parser.add_argument("--assign", help="Assign team member (format: role:name:email)")
    parser.add_argument("--report", action="store_true", help="Generate team report")
    parser.add_argument("--list-roles", action="store_true", help="List all available roles")
    
    args = parser.parse_args()
    
    setup = PMTeamSetup(project_root)
    
    if args.list_roles:
        structure = setup.load_team_structure()
        print("\nAvailable Roles:")
        print("-" * 80)
        ts = structure.get("team_structure", {})
        
        print("\n1. Program Manager")
        print("2. Technical PMs:")
        t_pms = ts.get("technical_pms", {})
        for project in t_pms.keys():
            print(f"   - Technical PM ({project.upper()})")
        
        print("\n3. Supporting Roles:")
        supporting = ts.get("supporting_roles", {})
        for role_key, role_data in supporting.items():
            print(f"   - {role_data.get('role', role_key)}")
    
    elif args.assign:
        parts = args.assign.split(":")
        if len(parts) < 3:
            print("Error: Format should be role:name:email")
            return
        
        role = parts[0]
        name = parts[1]
        email = parts[2]
        
        # For now, use default skills/tools (would be customized per role)
        skills = []
        tools = []
        
        setup.assign_team_member(role, name, email, skills, tools)
        print(f"✅ Assigned {name} to {role}")
    
    elif args.report:
        report = setup.generate_team_report()
        print(report)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
