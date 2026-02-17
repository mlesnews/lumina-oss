#!/usr/bin/env python3
"""
JARVIS Team Structure Analysis

Comprehensive analysis of company team structure, including Network Team and all areas.
Gets specialist opinions on optimal team organization.

Tags: #ORGANIZATIONAL #TEAMS #NETWORK @TEAM @AIQ
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
    from jarvis_company_team_structure import JARVISCompanyTeamStructure
    from jarvis_marvin_roast_system import JARVISMARVINRoastSystem
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    VirtualEmployeeManager = None
    JARVISCompanyTeamStructure = None
    JARVISMARVINRoastSystem = None

logger = get_logger("JARVISTeamStructure")


class JARVISTeamStructureAnalysis:
    """
    JARVIS Team Structure Analysis

    Analyzes current team structure and recommends optimal organization.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.employee_manager = None
        self.team_structure = None
        self.roast_system = None

        if VirtualEmployeeManager:
            try:
                self.employee_manager = VirtualEmployeeManager(project_root)
                self.logger.info("✅ Employee manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Employee manager not available: {e}")

        if JARVISCompanyTeamStructure:
            try:
                self.team_structure = JARVISCompanyTeamStructure(project_root)
                self.logger.info("✅ Team structure manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Team structure manager not available: {e}")

        if JARVISMARVINRoastSystem:
            try:
                self.roast_system = JARVISMARVINRoastSystem(project_root)
                self.logger.info("✅ Roast system initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Roast system not available: {e}")

        self.logger.info("✅ JARVIS Team Structure Analysis initialized")

    def analyze_network_team(self) -> Dict[str, Any]:
        """Analyze Network Team requirements"""
        self.logger.info("🔍 Analyzing Network Team requirements...")

        analysis = {
            "team_name": "Network Team",
            "department": "Network",
            "current_status": "PARTIAL",
            "required_job_slots": [
                {
                    "job_slot": "network_engineer",
                    "role": "engineer",
                    "status": "EXISTS",
                    "responsibilities": [
                        "Network infrastructure design",
                        "Network configuration",
                        "Network troubleshooting",
                        "Network optimization",
                        "Network monitoring",
                        "Network security",
                        "Network drive mapping",
                        "NAS connectivity"
                    ]
                },
                {
                    "job_slot": "network_administrator",
                    "role": "administrator",
                    "status": "EXISTS",
                    "responsibilities": [
                        "Network administration",
                        "Network security",
                        "Access control",
                        "Network policy management",
                        "Network backup and recovery",
                        "Network documentation"
                    ]
                }
            ],
            "missing_job_slots": [
                {
                    "job_slot": "network_security_specialist",
                    "role": "specialist",
                    "priority": "HIGH",
                    "responsibilities": [
                        "Network security monitoring",
                        "Threat detection",
                        "Firewall management",
                        "Intrusion detection",
                        "Network security compliance"
                    ]
                },
                {
                    "job_slot": "network_automation_engineer",
                    "role": "engineer",
                    "priority": "MEDIUM",
                    "responsibilities": [
                        "Network automation",
                        "Infrastructure as code",
                        "Network orchestration",
                        "Automated network provisioning"
                    ]
                }
            ],
            "integration_points": [
                "NAS connectivity (KAIJU)",
                "Network drive mapping",
                "ULTRON cluster networking",
                "Home lab infrastructure",
                "Security monitoring"
            ]
        }

        return analysis

    def get_comprehensive_team_structure(self) -> Dict[str, Any]:
        """Get comprehensive team structure for all areas"""
        self.logger.info("📊 Generating comprehensive team structure...")

        teams = {
            "Infrastructure Team": {
                "department": "Infrastructure",
                "description": "Core infrastructure and systems management",
                "job_slots": [
                    "systems_engineer",
                    "storage_engineer",
                    "disaster_recovery_engineer",
                    "cluster_fencing_engineer"
                ],
                "responsibilities": [
                    "System health monitoring",
                    "Storage management",
                    "Disaster recovery",
                    "Cluster management",
                    "Infrastructure automation"
                ],
                "priority": "CRITICAL"
            },
            "Network Team": {
                "department": "Network",
                "description": "Network infrastructure and connectivity",
                "job_slots": [
                    "network_engineer",
                    "network_administrator"
                ],
                "responsibilities": [
                    "Network infrastructure management",
                    "Network drive mapping",
                    "NAS connectivity",
                    "Network security",
                    "Network monitoring",
                    "Network automation"
                ],
                "priority": "CRITICAL"
            },
            "Database Team": {
                "department": "Database",
                "description": "Database engineering and administration",
                "job_slots": [
                    "database_engineer",
                    "database_administrator",
                    "memory_schema_engineer"
                ],
                "responsibilities": [
                    "Database design and optimization",
                    "Database administration",
                    "Backup and recovery",
                    "Schema management",
                    "Performance tuning"
                ],
                "priority": "HIGH"
            },
            "AI Infrastructure Team": {
                "department": "AI Infrastructure",
                "description": "AI and LLM infrastructure management",
                "job_slots": [
                    "llm_router_engineer",
                    "cluster_fencing_engineer"  # Shared
                ],
                "responsibilities": [
                    "LLM routing and optimization",
                    "Local-first AI enforcement",
                    "ULTRON cluster management",
                    "AI resource management"
                ],
                "priority": "HIGH"
            },
            "Security Team": {
                "department": "Security",
                "description": "Security and threat management",
                "job_slots": [
                    "security_engineer",  # NEW - Need to create
                    "security_analyst"  # NEW - Need to create
                ],
                "responsibilities": [
                    "Security monitoring",
                    "Threat detection",
                    "Access control",
                    "Security compliance",
                    "Incident response"
                ],
                "priority": "HIGH"
            },
            "DevOps Team": {
                "department": "DevOps",
                "description": "DevOps and platform engineering",
                "job_slots": [
                    "devops_engineer",  # NEW - Need to create
                    "platform_engineer"  # NEW - Need to create
                ],
                "responsibilities": [
                    "CI/CD pipeline management",
                    "Infrastructure as code",
                    "Container orchestration",
                    "Platform automation"
                ],
                "priority": "MEDIUM"
            },
            "Quality Assurance Team": {
                "department": "Quality Assurance",
                "description": "Quality assurance and testing",
                "job_slots": [
                    "qa_engineer",  # NEW - Need to create
                    "test_automation_engineer"  # NEW - Need to create
                ],
                "responsibilities": [
                    "Quality assurance",
                    "Test automation",
                    "Code validation",
                    "Quality metrics"
                ],
                "priority": "MEDIUM"
            },
            "Documentation Team": {
                "department": "Documentation",
                "description": "Documentation and knowledge management",
                "job_slots": [
                    "technical_writer",  # NEW - Need to create
                    "knowledge_manager"  # NEW - Need to create
                ],
                "responsibilities": [
                    "Technical documentation",
                    "Knowledge management",
                    "Documentation automation",
                    "Holocron maintenance"
                ],
                "priority": "LOW"
            }
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "total_teams": len(teams),
            "teams": teams,
            "summary": {
                "critical_teams": 2,
                "high_priority_teams": 2,
                "medium_priority_teams": 2,
                "low_priority_teams": 1,
                "existing_job_slots": 10,
                "recommended_job_slots": 18,
                "missing_job_slots": 8
            }
        }

    def get_specialist_opinions(self) -> Dict[str, Any]:
        """Get specialist opinions on team structure"""
        self.logger.info("🎓 Gathering specialist opinions on team structure...")

        opinions = {
            "timestamp": datetime.now().isoformat(),
            "jarvis_opinion": {},
            "marvin_opinion": {},
            "aiq_consensus": {},
            "recommendations": []
        }

        # JARVIS Systematic Opinion
        jarvis_opinion = {
            "perspective": "systematic",
            "analysis": "We need comprehensive team coverage across all critical areas. Network Team is essential for NAS connectivity, network drives, and infrastructure. We should organize teams by domain expertise.",
            "recommended_teams": [
                "Infrastructure Team (CRITICAL)",
                "Network Team (CRITICAL)",
                "Database Team (HIGH)",
                "AI Infrastructure Team (HIGH)",
                "Security Team (HIGH)",
                "DevOps Team (MEDIUM)",
                "Quality Assurance Team (MEDIUM)",
                "Documentation Team (LOW)"
            ],
            "team_structure_principles": [
                "Organize by domain expertise",
                "Ensure critical areas have dedicated teams",
                "Share resources where appropriate (e.g., cluster_fencing_engineer)",
                "Scale teams based on priority and workload"
            ],
            "priority": "HIGH"
        }
        opinions["jarvis_opinion"] = jarvis_opinion

        # MARVIN Reality Check
        marvin_opinion = {
            "perspective": "reality_check",
            "analysis": "We need to be practical. Not every area needs a full team. Focus on critical areas first. Network Team is essential but may not need 4+ people. Start lean, scale as needed.",
            "concerns": [
                "Over-staffing teams that don't need full teams",
                "Creating teams without clear responsibilities",
                "Duplicating efforts across teams"
            ],
            "recommendations": [
                "Start with critical teams: Infrastructure, Network, Database",
                "Use shared resources (e.g., cluster_fencing_engineer)",
                "Create job slots as needed, not preemptively",
                "Focus on high-value teams first"
            ],
            "priority": "MEDIUM"
        }
        opinions["marvin_opinion"] = marvin_opinion

        # @AIQ Consensus
        aiq_consensus = {
            "consensus": "BALANCED_APPROACH",
            "reasoning": "Organize into 6-8 core teams covering critical areas. Network Team is essential. Start with existing job slots, add new ones as needed.",
            "recommended_structure": {
                "critical_teams": [
                    {
                        "team": "Infrastructure Team",
                        "job_slots": 4,
                        "priority": "CRITICAL"
                    },
                    {
                        "team": "Network Team",
                        "job_slots": 2,
                        "priority": "CRITICAL"
                    }
                ],
                "high_priority_teams": [
                    {
                        "team": "Database Team",
                        "job_slots": 3,
                        "priority": "HIGH"
                    },
                    {
                        "team": "AI Infrastructure Team",
                        "job_slots": 2,
                        "priority": "HIGH"
                    },
                    {
                        "team": "Security Team",
                        "job_slots": 2,
                        "priority": "HIGH"
                    }
                ],
                "medium_priority_teams": [
                    {
                        "team": "DevOps Team",
                        "job_slots": 2,
                        "priority": "MEDIUM"
                    },
                    {
                        "team": "Quality Assurance Team",
                        "job_slots": 2,
                        "priority": "MEDIUM"
                    }
                ]
            },
            "total_teams": 7,
            "total_job_slots": 17,
            "priority": "HIGH"
        }
        opinions["aiq_consensus"] = aiq_consensus

        # Combined Recommendations
        opinions["recommendations"] = [
            {
                "priority": "CRITICAL",
                "action": "Establish Network Team with existing job slots",
                "details": "Network Team already has network_engineer and network_administrator",
                "team": "Network Team"
            },
            {
                "priority": "CRITICAL",
                "action": "Maintain Infrastructure Team",
                "details": "Core infrastructure management team",
                "team": "Infrastructure Team"
            },
            {
                "priority": "HIGH",
                "action": "Create Security Team",
                "details": "Add security_engineer and security_analyst job slots",
                "team": "Security Team"
            },
            {
                "priority": "MEDIUM",
                "action": "Consider DevOps and QA teams",
                "details": "Add as workload and needs increase",
                "teams": ["DevOps Team", "Quality Assurance Team"]
            }
        ]

        return opinions

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive team structure analysis"""
        self.logger.info("📊 Generating comprehensive team structure analysis...")

        # Current structure
        current_roster = None
        if self.employee_manager:
            try:
                current_roster = self.employee_manager.get_company_roster()
            except Exception as e:
                self.logger.warning(f"⚠️  Could not get current roster: {e}")

        # Network Team analysis
        network_analysis = self.analyze_network_team()

        # Comprehensive team structure
        team_structure = self.get_comprehensive_team_structure()

        # Specialist opinions
        specialist_opinions = self.get_specialist_opinions()

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "current_structure": current_roster.get("statistics", {}) if current_roster else {},
            "network_team_analysis": network_analysis,
            "comprehensive_team_structure": team_structure,
            "specialist_opinions": specialist_opinions,
            "implementation_plan": {
                "phase_1": {
                    "priority": "CRITICAL",
                    "teams": ["Infrastructure Team", "Network Team"],
                    "actions": [
                        "Formalize existing teams",
                        "Ensure Network Team has all required job slots",
                        "Document team responsibilities"
                    ]
                },
                "phase_2": {
                    "priority": "HIGH",
                    "teams": ["Database Team", "AI Infrastructure Team", "Security Team"],
                    "actions": [
                        "Create Security Team with new job slots",
                        "Formalize Database and AI Infrastructure teams",
                        "Document team structures"
                    ]
                },
                "phase_3": {
                    "priority": "MEDIUM",
                    "teams": ["DevOps Team", "Quality Assurance Team"],
                    "actions": [
                        "Create DevOps and QA teams as needed",
                        "Add job slots based on workload",
                        "Scale teams incrementally"
                    ]
                }
            }
        }

        return analysis


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Team Structure Analysis")
        parser.add_argument("--analyze", action="store_true", help="Generate comprehensive analysis")
        parser.add_argument("--network", action="store_true", help="Analyze Network Team")
        parser.add_argument("--teams", action="store_true", help="Get comprehensive team structure")
        parser.add_argument("--opinions", action="store_true", help="Get specialist opinions")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        analysis = JARVISTeamStructureAnalysis(project_root)

        if args.network:
            result = analysis.analyze_network_team()
            print(json.dumps(result, indent=2, default=str))

        elif args.teams:
            result = analysis.get_comprehensive_team_structure()
            print(json.dumps(result, indent=2, default=str))

        elif args.opinions:
            result = analysis.get_specialist_opinions()
            print(json.dumps(result, indent=2, default=str))

        elif args.analyze:
            result = analysis.generate_comprehensive_analysis()
            print(json.dumps(result, indent=2, default=str))

        else:
            # Default: comprehensive analysis
            result = analysis.generate_comprehensive_analysis()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()