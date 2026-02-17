#!/usr/bin/env python3
"""
JARVIS PR & Ticket Coordinator
Automatically generates GitLens PR references and helpdesk tickets for major/minor issues and changes.
Cross-references PR# and ticket numbers for tracking.

Tags: #PR #TICKET #HELPDESK #GITLENS #AUTOMATION @AUTO @TEAM
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging
import hashlib

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

logger = get_logger("JARVISPRTicketCoordinator")


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    TRIVIAL = "trivial"


class ChangeType(Enum):
    """Type of change"""
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"
    REFACTOR = "refactor"
    CONFIG = "config"
    DOCS = "docs"
    SECURITY = "security"
    PERFORMANCE = "performance"


class PRTicketCoordinator:
    """
    Coordinates PR and ticket generation for issues and changes.

    Automatically:
    - Generates GitLens PR references (PR-XXX format)
    - Generates helpdesk tickets (@helpdesk)
    - Cross-references PR# and ticket numbers
    - Tracks relationships between PRs and tickets
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Storage paths
        self.data_dir = project_root / "data" / "pr_tickets"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pr_ticket_map_file = self.data_dir / "pr_ticket_map.json"
        self.ticket_counter_file = self.data_dir / "ticket_counter.json"
        self.pr_counter_file = self.data_dir / "pr_counter.json"

        # Load existing data
        self.pr_ticket_map = self._load_pr_ticket_map()
        self.ticket_counter = self._load_counter(self.ticket_counter_file, "PM")
        self.pr_counter = self._load_counter(self.pr_counter_file, "PR")

        # Helpdesk configuration
        self.helpdesk_config = self._load_helpdesk_config()

        # Organizational structure for team assignment
        if LuminaOrganizationalStructure:
            try:
                self.org_structure = LuminaOrganizationalStructure(project_root)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load organizational structure: {e}")
                self.org_structure = None
        else:
            self.org_structure = None

        self.logger.info("✅ PR & Ticket Coordinator initialized")
        self.logger.info(f"   Next Ticket: PM{self.ticket_counter:09d}")
        self.logger.info(f"   Next PR: PR-{self.pr_counter}")
        if self.org_structure:
            self.logger.info(f"   Organizational Structure: {len(self.org_structure.teams)} teams available")

    def _load_helpdesk_config(self) -> Dict[str, Any]:
        """Load helpdesk configuration"""
        config_file = self.project_root / "config" / "helpdesk" / "helpdesk_structure.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load helpdesk config: {e}")
        return {}

    def _load_pr_ticket_map(self) -> Dict[str, Any]:
        """Load PR-Ticket mapping"""
        if self.pr_ticket_map_file.exists():
            try:
                with open(self.pr_ticket_map_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load PR-Ticket map: {e}")
        return {
            "pr_to_ticket": {},
            "ticket_to_pr": {},
            "entries": []
        }

    def _load_counter(self, counter_file: Path, prefix: str) -> int:
        """Load counter from file"""
        if counter_file.exists():
            try:
                with open(counter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("counter", 1)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load {prefix} counter: {e}")
        return 1

    def _save_counter(self, counter_file: Path, counter: int) -> None:
        """Save counter to file"""
        try:
            with open(counter_file, 'w', encoding='utf-8') as f:
                json.dump({"counter": counter, "last_updated": datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Failed to save counter: {e}")

    def _save_pr_ticket_map(self) -> None:
        """Save PR-Ticket mapping"""
        try:
            with open(self.pr_ticket_map_file, 'w', encoding='utf-8') as f:
                json.dump(self.pr_ticket_map, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"❌ Failed to save PR-Ticket map: {e}")

    def _generate_ticket_number(self) -> str:
        """Generate next Problem Management ticket number (9 digits)"""
        ticket_num = f"PM{self.ticket_counter:09d}"
        self.ticket_counter += 1
        self._save_counter(self.ticket_counter_file, self.ticket_counter)
        return ticket_num

    def _generate_pr_number(self) -> str:
        """Generate next PR number"""
        pr_num = f"PR-{self.pr_counter}"
        self.pr_counter += 1
        self._save_counter(self.pr_counter_file, self.pr_counter)
        return pr_num

    def _determine_severity(self, issue_type: str, description: str) -> IssueSeverity:
        """Determine issue severity from description"""
        description_lower = description.lower()

        # Critical indicators
        if any(keyword in description_lower for keyword in [
            "critical", "crash", "data loss", "security breach", "down", "outage",
            "cannot start", "broken", "fatal", "emergency"
        ]):
            return IssueSeverity.CRITICAL

        # Major indicators
        if any(keyword in description_lower for keyword in [
            "major", "significant", "important", "blocking", "error", "failed",
            "not working", "broken", "issue", "problem"
        ]):
            return IssueSeverity.MAJOR

        # Minor indicators
        if any(keyword in description_lower for keyword in [
            "minor", "small", "cosmetic", "typo", "formatting", "style"
        ]):
            return IssueSeverity.MINOR

        # Default based on issue type
        if issue_type in ["bug_fix", "security"]:
            return IssueSeverity.MAJOR
        elif issue_type in ["feature", "enhancement"]:
            return IssueSeverity.MINOR

        return IssueSeverity.MINOR

    def _route_to_helpdesk_team(self, issue_type: str, severity: IssueSeverity, description: str) -> Dict[str, Any]:
        """
        Route issue to appropriate team with proper team structure.

        Returns:
            Dict with team_id, team_name, team_manager, technical_lead, business_lead
        """
        description_lower = description.lower()

        # Use organizational structure if available
        if self.org_structure:
            # JARVIS Superagent issues -> JARVIS Superagent Team (highest priority for escalation/orchestration)
            if any(keyword in description_lower for keyword in ["@jarvis", "jarvis", "superagent", "orchestration", "escalation", "cross-domain", "strategic", "system-wide"]):
                team = self.org_structure.teams.get("jarvis_superagent")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@jarvis",
                        "business_lead": "JARVIS Superagent Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@jarvis"
                    }
            # Security issues -> Security & Threat Analysis Team
            if "security" in description_lower or issue_type == "security":
                team = self.org_structure.teams.get("security_analysis")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": None,  # Security team may not have business lead
                        "division": team.division,
                        "assignee": team.team_lead or "@k2so"
                    }

            # Docker/Container issues -> Docker Engineering Team
            if any(keyword in description_lower for keyword in ["docker", "container", "ollama", "ultron", "kaiju"]):
                team = self.org_structure.teams.get("docker_engineering")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": "Docker Engineering Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@r2d2"
                    }

            # Storage/NAS issues -> Storage Engineering Team
            if any(keyword in description_lower for keyword in ["storage", "nas", "disk", "space", "capacity"]):
                team = self.org_structure.teams.get("storage_engineering")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": "Storage Engineering Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@r2d2"
                    }

            # Network issues -> Network Support Team
            if any(keyword in description_lower for keyword in ["network", "connectivity", "ssh", "vpn", "firewall"]):
                team = self.org_structure.teams.get("network_support")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": None,
                        "division": team.division,
                        "assignee": team.team_lead or "@r2d2"
                    }

            # Health/system issues -> System Health & Operations Team
            if any(keyword in description_lower for keyword in ["health", "monitoring", "recovery", "system"]):
                team = self.org_structure.teams.get("system_health")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@2-1b",
                        "business_lead": None,
                        "division": team.division,
                        "assignee": team.team_lead or "@2-1b"
                    }

            # AI/Intelligence issues -> AI & Intelligence Team
            if any(keyword in description_lower for keyword in ["ai", "intelligence", "model", "llm", "machine learning"]):
                team = self.org_structure.teams.get("ai_intelligence")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@marvin",
                        "business_lead": None,
                        "division": team.division,
                        "assignee": team.team_lead or "@marvin"
                    }

            # Environmental/IDE issues -> IDE & Environmental Engineering Team
            if any(keyword in description_lower for keyword in ["environmental", "cursor", "vscode", "api alert", "notification", "ide ui", "ui alert"]):
                team = self.org_structure.teams.get("ide_environmental_engineering")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": "Environmental Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@r2d2"
                    }

            # Gemini/Project Review issues -> Gemini Project Review Team
            if any(keyword in description_lower for keyword in ["gemini", "project review", "my_project", "entire project", "project-wide"]):
                team = self.org_structure.teams.get("gemini_project_review")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@marvin",
                        "business_lead": "Gemini Analysis Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@marvin"
                    }

            # Problem Management issues -> Problem Management Team
            if any(keyword in description_lower for keyword in ["problem", "root cause", "issue", "bug", "error", "failure"]):
                team = self.org_structure.teams.get("problem_management")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": "Problem Management Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@r2d2"
                    }

            # Change Management issues -> Change Management Team
            if any(keyword in description_lower for keyword in ["change", "deployment", "update", "modification", "release", "rollout"]):
                team = self.org_structure.teams.get("change_management")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": "Change Management Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@r2d2"
                    }

            # Helpdesk/Support issues -> Helpdesk Support Team
            if any(keyword in description_lower for keyword in ["helpdesk", "support", "ticket", "workflow", "coordination"]):
                team = self.org_structure.teams.get("helpdesk_support")
                if team:
                    return {
                        "team_id": team.team_id,
                        "team_name": team.team_name,
                        "team_manager": team.helpdesk_manager or "@c3po",
                        "technical_lead": team.team_lead or "@r2d2",
                        "business_lead": "Helpdesk Support Lead",
                        "division": team.division,
                        "assignee": team.team_lead or "@r2d2"
                    }

        # Fallback to individual droid routing (legacy)
        routing_logic = self.helpdesk_config.get("workflow_routing", {}).get("routing_logic", {})

        # Security issues -> K-2SO
        if "security" in description_lower or issue_type == "security":
            return {
                "team_id": "security_analysis",
                "team_name": "Security & Threat Analysis Team",
                "team_manager": "@c3po",
                "technical_lead": "@k2so",
                "business_lead": None,
                "division": "Security & Threat Analysis",
                "assignee": "@k2so"
            }

        # Health/system issues -> 2-1B
        if any(keyword in description_lower for keyword in ["health", "monitoring", "recovery", "system"]):
            return {
                "team_id": "system_health",
                "team_name": "System Health & Operations Team",
                "team_manager": "@c3po",
                "technical_lead": "@2-1b",
                "business_lead": None,
                "division": "System Health & Operations",
                "assignee": "@2-1b"
            }

        # Technical issues -> R2-D2
        if any(keyword in description_lower for keyword in ["technical", "system", "repair", "diagnostic"]):
            return {
                "team_id": "network_support",
                "team_name": "Network Support Team",
                "team_manager": "@c3po",
                "technical_lead": "@r2d2",
                "business_lead": None,
                "division": "Network Support",
                "assignee": "@r2d2"
            }

        # Knowledge/context -> R5
        if any(keyword in description_lower for keyword in ["knowledge", "context", "pattern", "matrix"]):
            return {
                "team_id": "ai_intelligence",
                "team_name": "AI & Intelligence Team",
                "team_manager": "@c3po",
                "technical_lead": "@r5",
                "business_lead": None,
                "division": "AI & Intelligence",
                "assignee": "@r5"
            }

        # Analysis -> Marvin
        if any(keyword in description_lower for keyword in ["analysis", "deep", "philosophy"]):
            return {
                "team_id": "ai_intelligence",
                "team_name": "AI & Intelligence Team",
                "team_manager": "@c3po",
                "technical_lead": "@marvin",
                "business_lead": None,
                "division": "AI & Intelligence",
                "assignee": "@marvin"
            }

        # Problem Management -> Problem Management Team
        if any(keyword in description_lower for keyword in ["problem", "root cause", "issue", "bug", "error"]):
            return {
                "team_id": "problem_management",
                "team_name": "Problem Management Team",
                "team_manager": "@c3po",
                "technical_lead": "@r2d2",
                "business_lead": "Problem Management Lead",
                "division": "Problem Management",
                "assignee": "@r2d2"
            }

        # Change Management -> Change Management Team
        if any(keyword in description_lower for keyword in ["change", "deployment", "update", "modification"]):
            return {
                "team_id": "change_management",
                "team_name": "Change Management Team",
                "team_manager": "@c3po",
                "technical_lead": "@r2d2",
                "business_lead": "Change Management Lead",
                "division": "Change Management",
                "assignee": "@r2d2"
            }

        # Helpdesk/Support -> Helpdesk Support Team
        if any(keyword in description_lower for keyword in ["helpdesk", "support", "ticket", "workflow"]):
            return {
                "team_id": "helpdesk_support",
                "team_name": "Helpdesk Support Team",
                "team_manager": "@c3po",
                "technical_lead": "@r2d2",
                "business_lead": "Helpdesk Support Lead",
                "division": "Helpdesk Support",
                "assignee": "@r2d2"
            }

        # Default -> Helpdesk Support Team (supports droid team)
        return {
            "team_id": "helpdesk_support",
            "team_name": "Helpdesk Support Team",
            "team_manager": "@c3po",
            "technical_lead": "@r2d2",
            "business_lead": "Helpdesk Support Lead",
            "division": "Helpdesk Support",
            "assignee": "@c3po"
        }

    def create_pr_and_ticket(
        self,
        title: str,
        description: str,
        change_type: ChangeType,
        severity: Optional[IssueSeverity] = None,
        files_changed: Optional[List[str]] = None,
        related_issues: Optional[List[str]] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create both PR and ticket for an issue/change.

        Returns:
            Dict with pr_number, ticket_number, and cross-reference info
        """
        self.logger.info("="*80)
        self.logger.info("CREATING PR & TICKET")
        self.logger.info("="*80)

        # Determine severity if not provided
        if severity is None:
            severity = self._determine_severity(change_type.value, description)

        # Generate numbers
        pr_number = self._generate_pr_number()
        ticket_number = self._generate_ticket_number()

        # Route to helpdesk team (with team structure)
        if assignee:
            # If assignee provided, create minimal team structure
            team_info = {
                "team_id": "assigned",
                "team_name": "Assigned Team",
                "team_manager": "@c3po",
                "technical_lead": assignee if assignee.startswith("@") else f"@{assignee}",
                "business_lead": None,
                "division": "Assigned",
                "assignee": assignee if assignee.startswith("@") else f"@{assignee}"
            }
        else:
            team_info = self._route_to_helpdesk_team(change_type.value, severity, description)

        # Create PR entry
        pr_entry = {
            "pr_number": pr_number,
            "title": title,
            "description": description,
            "change_type": change_type.value,
            "severity": severity.value,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "files_changed": files_changed or [],
            "related_issues": related_issues or [],
            "ticket_number": ticket_number,
            "gitlens_reference": f"PR-{pr_number.split('-')[1]}",  # PR-123 format
            "github_url": f"https://github.com/mlesnews/lumina-ai/pull/{pr_number.split('-')[1]}"
        }

        # Create ticket entry with team structure
        ticket_entry = {
            "ticket_number": ticket_number,
            "title": title,
            "description": description,
            "change_type": change_type.value,
            "severity": severity.value,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "assigned_by": "@c3po",  # C-3PO assigns all tickets
            "location": "@helpdesk",
            "pr_number": pr_number,
            "files_changed": files_changed or [],
            "related_issues": related_issues or [],
            # Team structure (required for team management)
            "team_assignment": {
                "team_id": team_info["team_id"],
                "team_name": team_info["team_name"],
                "division": team_info["division"],
                "team_manager": team_info["team_manager"],  # Required: Team Manager
                "technical_lead": team_info["technical_lead"],  # Required: Technical Lead
                "business_lead": team_info.get("business_lead"),  # Optional: Business Lead
                "primary_assignee": team_info["assignee"]  # Primary team member to work on ticket
            }
        }

        # Cross-reference
        self.pr_ticket_map["pr_to_ticket"][pr_number] = ticket_number
        self.pr_ticket_map["ticket_to_pr"][ticket_number] = pr_number

        # Add to entries
        entry = {
            "pr_number": pr_number,
            "ticket_number": ticket_number,
            "title": title,
            "change_type": change_type.value,
            "severity": severity.value,
            "created_at": datetime.now().isoformat(),
            "status": "open"
        }
        self.pr_ticket_map["entries"].append(entry)

        # Save mapping
        self._save_pr_ticket_map()

        # Save individual entries
        self._save_pr_entry(pr_entry)
        self._save_ticket_entry(ticket_entry)

        # C-3PO assigns ticket to team (ensures proper team structure)
        self.logger.info("")
        self.logger.info("📋 C-3PO assigning ticket to team...")
        try:
            from jarvis_c3po_ticket_assigner import C3POTicketAssigner
            assigner = C3POTicketAssigner(self.project_root)
            assignment_result = assigner.assign_ticket_to_team(ticket_number, team_id=team_info["team_id"], auto_detect=False)
            if assignment_result.get("success"):
                # Reload ticket to get updated assignment
                ticket_file = self.data_dir / "tickets" / f"{ticket_number}.json"
                if ticket_file.exists():
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket_entry = json.load(f)
                self.logger.info("   ✅ Ticket assigned by C-3PO")
            else:
                self.logger.warning(f"   ⚠️  Assignment warning: {assignment_result.get('error')}")
        except Exception as e:
            self.logger.debug(f"Assignment system not available: {e}")

        # Migrate to Holocron and Database
        self.logger.info("")
        self.logger.info("📚 Migrating ticket to Holocron & Database...")
        try:
            from jarvis_tickets_to_holocron_db import TicketsToHolocronDB
            migrator = TicketsToHolocronDB(self.project_root)
            migration_result = migrator.migrate_ticket(ticket_number)
            if migration_result.get("success"):
                self.logger.info(f"   ✅ Ticket migrated to Holocron: {migration_result.get('holocron_entry_id')}")
                self.logger.info(f"   ✅ Ticket imported to database")
            else:
                self.logger.warning(f"   ⚠️  Migration warning: {migration_result.get('error')}")
        except Exception as e:
            self.logger.debug(f"Migration system not available: {e}")

        self.logger.info("")
        self.logger.info(f"✅ Created PR: {pr_number}")
        self.logger.info(f"✅ Created Ticket: {ticket_number}")
        self.logger.info(f"🔗 Cross-reference: {pr_number} ↔ {ticket_number}")
        self.logger.info(f"📋 GitLens Reference: {pr_entry['gitlens_reference']}")
        self.logger.info(f"👥 Assigned to Team: {team_info['team_name']}")
        self.logger.info(f"   📋 Team Manager: {team_info['team_manager']} (@c3po)")
        self.logger.info(f"   🔧 Technical Lead: {team_info['technical_lead']}")
        if team_info.get('business_lead'):
            self.logger.info(f"   💼 Business Lead: {team_info['business_lead']}")
        self.logger.info(f"   👤 Primary Assignee: {team_info['assignee']}")

        return {
            "success": True,
            "pr_number": pr_number,
            "ticket_number": ticket_number,
            "gitlens_reference": pr_entry['gitlens_reference'],
            "cross_reference": {
                "pr_to_ticket": f"{pr_number} → {ticket_number}",
                "ticket_to_pr": f"{ticket_number} → {pr_number}"
            },
            "pr_entry": pr_entry,
            "ticket_entry": ticket_entry
        }

    def _save_pr_entry(self, pr_entry: Dict[str, Any]) -> None:
        """Save PR entry to file"""
        pr_dir = self.data_dir / "prs"
        pr_dir.mkdir(parents=True, exist_ok=True)

        pr_file = pr_dir / f"{pr_entry['pr_number']}.json"
        try:
            with open(pr_file, 'w', encoding='utf-8') as f:
                json.dump(pr_entry, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"❌ Failed to save PR entry: {e}")

    def _save_ticket_entry(self, ticket_entry: Dict[str, Any]) -> None:
        """Save ticket entry to file"""
        ticket_dir = self.data_dir / "tickets"
        ticket_dir.mkdir(parents=True, exist_ok=True)

        ticket_file = ticket_dir / f"{ticket_entry['ticket_number']}.json"
        try:
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket_entry, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"❌ Failed to save ticket entry: {e}")

    def get_cross_reference(self, pr_number: Optional[str] = None, ticket_number: Optional[str] = None) -> Dict[str, Any]:
        """Get cross-reference information"""
        if pr_number:
            ticket = self.pr_ticket_map["pr_to_ticket"].get(pr_number)
            if ticket:
                return {
                    "pr_number": pr_number,
                    "ticket_number": ticket,
                    "reference": f"PR {pr_number} → Ticket {ticket}"
                }

        if ticket_number:
            pr = self.pr_ticket_map["ticket_to_pr"].get(ticket_number)
            if pr:
                return {
                    "ticket_number": ticket_number,
                    "pr_number": pr,
                    "reference": f"Ticket {ticket_number} → PR {pr}"
                }

        return {"error": "No cross-reference found"}

    def annotate_with_references(self, text: str, pr_number: str, ticket_number: str) -> str:
        """
        Annotate text with PR and ticket references.

        Adds GitLens PR reference and helpdesk ticket reference in a format
        that can be cross-referenced.
        """
        gitlens_ref = f"PR-{pr_number.split('-')[1]}"

        annotation = f"""
---
**Cross-References:**
- GitLens PR: {gitlens_ref} (GitHub: {pr_number})
- Helpdesk Ticket: {ticket_number}
- Cross-Reference: {pr_number} ↔ {ticket_number}
---
"""
        return text + annotation

    def generate_commit_message(self, pr_number: str, ticket_number: str, title: str) -> str:
        """Generate commit message with PR and ticket references"""
        gitlens_ref = f"PR-{pr_number.split('-')[1]}"
        return f"[{gitlens_ref}] {title}\n\nRelated: {ticket_number}"


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="PR & Ticket Coordinator")
        parser.add_argument("--create", action="store_true", help="Create PR and ticket")
        parser.add_argument("--title", type=str, help="Issue/change title")
        parser.add_argument("--description", type=str, help="Issue/change description")
        parser.add_argument("--type", type=str, choices=[ct.value for ct in ChangeType], help="Change type")
        parser.add_argument("--severity", type=str, choices=[s.value for s in IssueSeverity], help="Severity")
        parser.add_argument("--files", type=str, nargs="+", help="Files changed")
        parser.add_argument("--lookup", type=str, help="Lookup cross-reference (PR-XXX or HELPDESK-XXXX)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        coordinator = PRTicketCoordinator(project_root)

        if args.lookup:
            result = coordinator.get_cross_reference(
                pr_number=args.lookup if args.lookup.startswith("PR-") else None,
                ticket_number=args.lookup if args.lookup.startswith("HELPDESK-") else None
            )
            print(json.dumps(result, indent=2, default=str))

        elif args.create:
            if not args.title or not args.description or not args.type:
                parser.error("--create requires --title, --description, and --type")

            change_type = ChangeType(args.type)
            severity = IssueSeverity(args.severity) if args.severity else None

            result = coordinator.create_pr_and_ticket(
                title=args.title,
                description=args.description,
                change_type=change_type,
                severity=severity,
                files_changed=args.files
            )
            print(json.dumps(result, indent=2, default=str))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()