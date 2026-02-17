#!/usr/bin/env python3
"""
JARVIS Company Team Structure

Defines and manages company teams, departments, and organizational structure.
Analyzes current job slots and recommends team structure.

Tags: #ORGANIZATIONAL #TEAMS #DEPARTMENTS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_virtual_employee_manager import VirtualEmployeeManager
    from jarvis_job_slot_platform_analysis import JARVISJobSlotPlatformAnalysis
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    VirtualEmployeeManager = None
    JARVISJobSlotPlatformAnalysis = None

logger = get_logger("JARVISCompanyTeams")


class JARVISCompanyTeamStructure:
    """
    JARVIS Company Team Structure

    Manages teams, departments, and organizational structure.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.employee_manager = None

        if VirtualEmployeeManager:
            try:
                self.employee_manager = VirtualEmployeeManager(project_root)
                self.logger.info("✅ Employee manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Employee manager not available: {e}")

        self.logger.info("✅ JARVIS Company Team Structure initialized")

    def get_current_team_structure(self) -> Dict[str, Any]:
        """Get current team structure from employees"""
        self.logger.info("📊 Analyzing current team structure...")

        if not self.employee_manager:
            return {"error": "Employee manager not available"}

        roster = self.employee_manager.get_company_roster()
        employees = roster.get("employees", [])

        # Group by department
        teams = {}
        for emp in employees:
            dept = emp.get("department") or "unassigned"
            if dept not in teams:
                teams[dept] = {
                    "department": dept,
                    "employees": [],
                    "job_slots": [],
                    "count": 0
                }

            teams[dept]["employees"].append({
                "name": emp.get("employee_name"),
                "job_slot": emp.get("job_slot"),
                "role": emp.get("role")
            })
            teams[dept]["job_slots"].append(emp.get("job_slot"))
            teams[dept]["count"] += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "current_teams": teams,
            "total_employees": len(employees),
            "total_teams": len(teams)
        }

    def get_recommended_team_structure(self) -> Dict[str, Any]:
        """Get recommended team structure based on best practices"""
        self.logger.info("🎯 Generating recommended team structure...")

        recommended_teams = {
            "Infrastructure": {
                "description": "Core infrastructure and systems management",
                "job_slots": [
                    "systems_engineer",
                    "storage_engineer",
                    "network_engineer",  # NEW
                    "cluster_fencing_engineer"
                ],
                "responsibilities": [
                    "System health and monitoring",
                    "Storage management",
                    "Network infrastructure",
                    "Cluster management",
                    "Infrastructure automation"
                ],
                "priority": "CRITICAL"
            },
            "Database": {
                "description": "Database engineering and administration",
                "job_slots": [
                    "database_engineer",
                    "database_administrator",
                    "memory_schema_engineer"
                ],
                "responsibilities": [
                    "Database design and optimization",
                    "Backup and recovery",
                    "Schema management",
                    "Performance tuning"
                ],
                "priority": "HIGH"
            },
            "AI Infrastructure": {
                "description": "AI and LLM infrastructure management",
                "job_slots": [
                    "llm_router_engineer",
                    "cluster_fencing_engineer"  # Shared with Infrastructure
                ],
                "responsibilities": [
                    "LLM routing and optimization",
                    "Local-first AI enforcement",
                    "Cluster management",
                    "AI resource allocation"
                ],
                "priority": "HIGH"
            },
            "Disaster Recovery": {
                "description": "Disaster recovery and system resilience",
                "job_slots": [
                    "disaster_recovery_engineer"
                ],
                "responsibilities": [
                    "Disaster recovery planning",
                    "Code validation",
                    "Rollback management",
                    "System resilience"
                ],
                "priority": "CRITICAL"
            },
            "Network": {
                "description": "Network infrastructure and connectivity",
                "job_slots": [
                    "network_engineer",  # NEW - Need to create
                    "network_administrator"  # NEW - Need to create
                ],
                "responsibilities": [
                    "Network infrastructure management",
                    "Network drive mapping",
                    "NAS connectivity",
                    "Network security",
                    "Bandwidth optimization",
                    "Network monitoring"
                ],
                "priority": "HIGH",
                "status": "MISSING"
            },
            "Security": {
                "description": "Security and threat management",
                "job_slots": [
                    "security_engineer",  # NEW - Need to create
                    "security_analyst"  # NEW - Need to create
                ],
                "responsibilities": [
                    "Security monitoring",
                    "Threat analysis",
                    "Access control",
                    "Security compliance",
                    "Vulnerability management"
                ],
                "priority": "HIGH",
                "status": "MISSING"
            },
            "DevOps": {
                "description": "Development operations and automation",
                "job_slots": [
                    "devops_engineer",  # NEW - Need to create
                    "automation_engineer"  # NEW - Need to create
                ],
                "responsibilities": [
                    "CI/CD pipelines",
                    "Deployment automation",
                    "Infrastructure as code",
                    "Workflow automation",
                    "MANUS integration"
                ],
                "priority": "MEDIUM",
                "status": "MISSING"
            },
            "Quality Assurance": {
                "description": "Quality assurance and testing",
                "job_slots": [
                    "qa_engineer",  # NEW - Need to create
                    "test_automation_engineer"  # NEW - Need to create
                ],
                "responsibilities": [
                    "Code quality validation",
                    "Testing automation",
                    "Quality metrics",
                    "Regression testing"
                ],
                "priority": "MEDIUM",
                "status": "MISSING"
            }
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "recommended_teams": recommended_teams,
            "total_recommended_teams": len(recommended_teams),
            "missing_teams": [
                "Network",
                "Security",
                "DevOps",
                "Quality Assurance"
            ]
        }

    def analyze_team_gaps(self) -> Dict[str, Any]:
        """Analyze gaps in current team structure"""
        self.logger.info("🔍 Analyzing team structure gaps...")

        current = self.get_current_team_structure()
        recommended = self.get_recommended_team_structure()

        gaps = {
            "timestamp": datetime.now().isoformat(),
            "missing_teams": [],
            "missing_job_slots": [],
            "understaffed_teams": [],
            "recommendations": []
        }

        # Check for missing teams
        current_teams = set(current.get("current_teams", {}).keys())
        recommended_teams = set(recommended.get("recommended_teams", {}).keys())

        missing_teams = recommended_teams - current_teams
        gaps["missing_teams"] = list(missing_teams)

        # Check for missing job slots
        current_job_slots = set()
        for team_data in current.get("current_teams", {}).values():
            current_job_slots.update(team_data.get("job_slots", []))

        recommended_job_slots = set()
        for team_data in recommended.get("recommended_teams", {}).values():
            recommended_job_slots.update(team_data.get("job_slots", []))

        missing_job_slots = recommended_job_slots - current_job_slots
        gaps["missing_job_slots"] = list(missing_job_slots)

        # Generate recommendations
        if missing_teams:
            gaps["recommendations"].append({
                "priority": "HIGH",
                "action": "Create missing teams",
                "teams": list(missing_teams),
                "details": "These teams are recommended but not yet created"
            })

        if missing_job_slots:
            gaps["recommendations"].append({
                "priority": "HIGH",
                "action": "Create missing job slots",
                "job_slots": list(missing_job_slots),
                "details": "These job slots are recommended but not yet created"
            })

        return gaps

    def generate_team_structure_report(self) -> Dict[str, Any]:
        """Generate comprehensive team structure report"""
        self.logger.info("📊 Generating comprehensive team structure report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "current_structure": self.get_current_team_structure(),
            "recommended_structure": self.get_recommended_team_structure(),
            "gaps_analysis": self.analyze_team_gaps(),
            "summary": {
                "current_teams": 0,
                "recommended_teams": 0,
                "missing_teams": 0,
                "missing_job_slots": 0
            }
        }

        # Calculate summary
        report["summary"]["current_teams"] = report["current_structure"].get("total_teams", 0)
        report["summary"]["recommended_teams"] = report["recommended_structure"].get("total_recommended_teams", 0)
        report["summary"]["missing_teams"] = len(report["gaps_analysis"].get("missing_teams", []))
        report["summary"]["missing_job_slots"] = len(report["gaps_analysis"].get("missing_job_slots", []))

        return report


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Company Team Structure")
        parser.add_argument("--current", action="store_true", help="Show current team structure")
        parser.add_argument("--recommended", action="store_true", help="Show recommended team structure")
        parser.add_argument("--gaps", action="store_true", help="Analyze team gaps")
        parser.add_argument("--report", action="store_true", help="Generate comprehensive report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        teams = JARVISCompanyTeamStructure(project_root)

        if args.current:
            result = teams.get_current_team_structure()
            print(json.dumps(result, indent=2, default=str))

        elif args.recommended:
            result = teams.get_recommended_team_structure()
            print(json.dumps(result, indent=2, default=str))

        elif args.gaps:
            result = teams.analyze_team_gaps()
            print(json.dumps(result, indent=2, default=str))

        elif args.report:
            result = teams.generate_team_structure_report()
            print(json.dumps(result, indent=2, default=str))

        else:
            # Default: comprehensive report
            result = teams.generate_team_structure_report()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()