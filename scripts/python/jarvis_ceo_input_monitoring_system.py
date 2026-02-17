#!/usr/bin/env python3
"""
JARVIS CEO Input Monitoring & Data Extraction System
All teams watch CEO inputs and siphon relevant data for their scope

Tags: #JARVIS #CEO_MONITORING #DATA_EXTRACTION #TEAM_ROUTING @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCEOMonitoring")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class Division(Enum):
    """Company divisions"""
    BUSINESS = "business"
    TECHNICAL = "technical"


class Team(Enum):
    """Company teams"""
    # Business Division
    FINANCE = "finance"
    OPERATIONS = "operations"
    STRATEGY = "strategy"
    SALES_MARKETING = "sales_marketing"
    HR = "hr"

    # Technical Division
    DEVELOPMENT = "development"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    QA = "qa"
    DEVOPS = "devops"


@dataclass
class TeamScope:
    """Team scope definition"""
    team: Team
    division: Division
    keywords: List[str]
    data_types: List[str]
    description: str


@dataclass
class CEOInput:
    """CEO input entry"""
    input_id: str
    timestamp: str
    source: str  # voice, text, keyboard, file, system
    raw_input: str
    parsed_data: Dict[str, Any]
    relevant_teams: List[Team]
    extracted_data: Dict[str, Dict[str, Any]]  # Team name -> data


class CEOInputMonitor:
    """Monitor and capture all CEO inputs"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "jarvis" / "ceo_inputs"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Team scopes
        self.team_scopes = self._initialize_team_scopes()

        self.logger = logger
        self.inputs: List[CEOInput] = []

    def _initialize_team_scopes(self) -> Dict[Team, TeamScope]:
        """Initialize team scope definitions"""
        scopes = {
            # Business Division
            Team.FINANCE: TeamScope(
                team=Team.FINANCE,
                division=Division.BUSINESS,
                keywords=["money", "budget", "cost", "revenue", "investment", "financial", "payment", "invoice", "expense", "profit", "loss", "accounting", "billing"],
                data_types=["financial_metrics", "budget_allocations", "cost_analysis", "revenue_data"],
                description="Financial data, budgets, costs, revenue, investments"
            ),
            Team.OPERATIONS: TeamScope(
                team=Team.OPERATIONS,
                division=Division.BUSINESS,
                keywords=["operations", "process", "workflow", "efficiency", "productivity", "daily", "routine", "procedure", "operational"],
                data_types=["process_improvements", "operational_metrics", "workflow_data", "efficiency_data"],
                description="Day-to-day operations, processes, workflows, efficiency"
            ),
            Team.STRATEGY: TeamScope(
                team=Team.STRATEGY,
                division=Division.BUSINESS,
                keywords=["strategy", "goal", "vision", "direction", "plan", "decision", "roadmap", "objective", "target", "mission"],
                data_types=["strategic_plans", "goals", "decisions", "roadmaps", "objectives"],
                description="Strategic planning, goals, vision, direction, decisions"
            ),
            Team.SALES_MARKETING: TeamScope(
                team=Team.SALES_MARKETING,
                division=Division.BUSINESS,
                keywords=["sales", "marketing", "customer", "product", "campaign", "market", "client", "revenue", "advertising", "promotion"],
                data_types=["sales_data", "marketing_campaigns", "customer_feedback", "market_data"],
                description="Sales, marketing, customers, products, campaigns"
            ),
            Team.HR: TeamScope(
                team=Team.HR,
                division=Division.BUSINESS,
                keywords=["hire", "team", "people", "culture", "performance", "employee", "talent", "recruit", "staff", "personnel", "workforce"],
                data_types=["hiring_needs", "team_feedback", "performance_data", "culture_data"],
                description="People, hiring, team, culture, performance, development"
            ),

            # Technical Division
            Team.DEVELOPMENT: TeamScope(
                team=Team.DEVELOPMENT,
                division=Division.TECHNICAL,
                keywords=["code", "feature", "develop", "implement", "technical", "build", "create", "programming", "software", "application", "functionality"],
                data_types=["feature_requests", "technical_requirements", "code_changes", "implementation_data"],
                description="Code, features, development, implementation, technical solutions"
            ),
            Team.INFRASTRUCTURE: TeamScope(
                team=Team.INFRASTRUCTURE,
                division=Division.TECHNICAL,
                keywords=["infrastructure", "server", "deploy", "scale", "system", "architecture", "network", "hardware", "cloud", "hosting"],
                data_types=["infrastructure_needs", "system_requirements", "scaling_data", "architecture_data"],
                description="Infrastructure, systems, servers, deployment, scaling"
            ),
            Team.SECURITY: TeamScope(
                team=Team.SECURITY,
                division=Division.TECHNICAL,
                keywords=["security", "compliance", "risk", "vulnerability", "access", "secure", "encryption", "authentication", "authorization", "threat"],
                data_types=["security_concerns", "compliance_requirements", "risk_assessments", "vulnerability_data"],
                description="Security, compliance, risks, vulnerabilities, access"
            ),
            Team.QA: TeamScope(
                team=Team.QA,
                division=Division.TECHNICAL,
                keywords=["test", "quality", "bug", "validate", "verify", "check", "ensure", "testing", "quality_assurance", "defect"],
                data_types=["test_requirements", "quality_metrics", "bug_reports", "validation_data"],
                description="Testing, quality, bugs, validation, verification"
            ),
            Team.DEVOPS: TeamScope(
                team=Team.DEVOPS,
                division=Division.TECHNICAL,
                keywords=["deploy", "CI/CD", "automate", "monitor", "reliable", "pipeline", "continuous", "integration", "delivery", "devops"],
                data_types=["deployment_needs", "automation_requirements", "monitoring_data", "pipeline_data"],
                description="Deployment, CI/CD, automation, monitoring, reliability"
            )
        }

        return scopes

    def capture_input(self, raw_input: str, source: str = "text") -> CEOInput:
        """Capture and process CEO input"""
        input_id = f"input_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        timestamp = datetime.now().isoformat()

        # Parse input
        parsed_data = self._parse_input(raw_input)

        # Find relevant teams
        relevant_teams = self._find_relevant_teams(raw_input, parsed_data)

        # Extract data for each team
        extracted_data = {}
        for team in relevant_teams:
            extracted_data[team.value] = self._extract_team_data(raw_input, parsed_data, team)

        # Create input entry
        ceo_input = CEOInput(
            input_id=input_id,
            timestamp=timestamp,
            source=source,
            raw_input=raw_input,
            parsed_data=parsed_data,
            relevant_teams=relevant_teams,
            extracted_data=extracted_data
        )

        self.inputs.append(ceo_input)
        self._save_input(ceo_input)
        self._route_to_teams(ceo_input)

        self.logger.info(f"📥 Captured CEO input: {raw_input[:50]}...")
        self.logger.info(f"   Relevant teams: {[t.value for t in relevant_teams]}")

        return ceo_input

    def _parse_input(self, raw_input: str) -> Dict[str, Any]:
        """Parse input for analysis"""
        # Convert to lowercase for keyword matching
        lower_input = raw_input.lower()

        # Extract entities (simplified - could use NLP)
        entities = {
            "numbers": re.findall(r'\d+', raw_input),
            "dates": re.findall(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}', raw_input),
            "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw_input),
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', raw_input),
        }

        # Detect questions
        is_question = raw_input.strip().endswith('?') or any(q in lower_input for q in ['what', 'why', 'how', 'when', 'where', 'who'])

        # Detect commands
        is_command = any(cmd in lower_input for cmd in ['@doit', '@do', 'create', 'build', 'implement', 'deploy'])

        return {
            "text": raw_input,
            "lowercase": lower_input,
            "word_count": len(raw_input.split()),
            "entities": entities,
            "is_question": is_question,
            "is_command": is_command,
            "topics": self._extract_topics(lower_input)
        }

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        # Simple topic extraction based on keywords
        # Could be enhanced with NLP
        return topics

    def _find_relevant_teams(self, raw_input: str, parsed_data: Dict[str, Any]) -> List[Team]:
        """Find teams relevant to this input"""
        relevant_teams = []
        lower_input = parsed_data["lowercase"]

        for team, scope in self.team_scopes.items():
            # Check if any keywords match
            matches = sum(1 for keyword in scope.keywords if keyword in lower_input)

            if matches > 0:
                relevant_teams.append(team)
                self.logger.debug(f"   Team {team.value} matched ({matches} keywords)")

        return relevant_teams

    def _extract_team_data(self, raw_input: str, parsed_data: Dict[str, Any], team: Team) -> Dict[str, Any]:
        """Extract data relevant to specific team"""
        scope = self.team_scopes[team]

        # Extract relevant portions
        relevant_text = []
        for keyword in scope.keywords:
            if keyword in parsed_data["lowercase"]:
                # Find context around keyword
                idx = parsed_data["lowercase"].find(keyword)
                start = max(0, idx - 50)
                end = min(len(raw_input), idx + len(keyword) + 50)
                relevant_text.append(raw_input[start:end])

        return {
            "team": team.value,
            "division": scope.division.value,
            "relevant_text": relevant_text,
            "keywords_found": [kw for kw in scope.keywords if kw in parsed_data["lowercase"]],
            "entities": parsed_data["entities"],
            "is_question": parsed_data["is_question"],
            "is_command": parsed_data["is_command"],
            "extracted_at": datetime.now().isoformat()
        }

    def _save_input(self, ceo_input: CEOInput):
        try:
            """Save input to storage"""
            # Save raw input
            raw_dir = self.data_dir / "raw_inputs"
            raw_dir.mkdir(parents=True, exist_ok=True)

            raw_file = raw_dir / f"{ceo_input.input_id}.json"
            with open(raw_file, 'w') as f:
                json.dump(asdict(ceo_input), f, indent=2, default=str)

            # Save parsed input
            parsed_dir = self.data_dir / "parsed_inputs"
            parsed_dir.mkdir(parents=True, exist_ok=True)

            parsed_file = parsed_dir / f"{ceo_input.input_id}.json"
            with open(parsed_file, 'w') as f:
                json.dump({
                    "input_id": ceo_input.input_id,
                    "timestamp": ceo_input.timestamp,
                    "source": ceo_input.source,
                    "parsed_data": ceo_input.parsed_data,
                    "relevant_teams": [t.value for t in ceo_input.relevant_teams]
                }, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_input: {e}", exc_info=True)
            raise
    def _route_to_teams(self, ceo_input: CEOInput):
        try:
            """Route extracted data to teams"""
            for team_name, data in ceo_input.extracted_data.items():
                team = Team(team_name)
                scope = self.team_scopes[team]

                # Save to team-specific store
                team_dir = self.data_dir / scope.division.value / team.value
                team_dir.mkdir(parents=True, exist_ok=True)

                team_file = team_dir / f"{ceo_input.input_id}.json"
                with open(team_file, 'w') as f:
                    json.dump({
                        "input_id": ceo_input.input_id,
                        "timestamp": ceo_input.timestamp,
                        "source": ceo_input.source,
                        "raw_input": ceo_input.raw_input,
                        "extracted_data": data
                    }, f, indent=2, default=str)

                self.logger.info(f"   📤 Routed to {team.value} team")

            # Log routing decision
            routing_log = self.data_dir / "routing_log.jsonl"
            with open(routing_log, 'a') as f:
                f.write(json.dumps({
                    "input_id": ceo_input.input_id,
                    "timestamp": ceo_input.timestamp,
                    "routed_to": [t.value for t in ceo_input.relevant_teams],
                    "routing_reason": "keyword_match"
                }) + "\n")


        except Exception as e:
            self.logger.error(f"Error in _route_to_teams: {e}", exc_info=True)
            raise
def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS CEO Input Monitoring System")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--input', type=str, help='Process a CEO input')
    parser.add_argument('--source', type=str, default='text', help='Input source (voice, text, keyboard, etc.)')

    args = parser.parse_args()

    monitor = CEOInputMonitor(project_root=args.project_root or PROJECT_ROOT)

    if args.input:
        ceo_input = monitor.capture_input(args.input, source=args.source)
        print(f"✅ Processed input: {ceo_input.input_id}")
        print(f"   Relevant teams: {[t.value for t in ceo_input.relevant_teams]}")
    else:
        print("CEO Input Monitoring System initialized")
        print("Ready to monitor CEO inputs and route to teams")


if __name__ == "__main__":


    main()