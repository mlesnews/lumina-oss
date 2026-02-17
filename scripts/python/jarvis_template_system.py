#!/usr/bin/env python3
"""
JARVIS Template System

Creates templates for:
- Processes
- Policies
- Procedures
- Teams
- Company structure

Standardizes and modularizes everything.

Tags: #TEMPLATE_SYSTEM #STANDARDIZATION #MODULARIZATION #INTENT_ARTICULATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISTemplateSystem")


class IntentArticulator:
    """Articulate and define intent clearly"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "intent_articulation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def articulate_intent(self, system_name: str, description: str, objectives: List[str]) -> Dict[str, Any]:
        try:
            """Articulate clear intent"""
            intent = {
                "timestamp": datetime.now().isoformat(),
                "system_name": system_name,
                "description": description,
                "objectives": objectives,
                "intent_clear": True,
                "standardized": False,
                "modularized": False
            }

            # Save intent
            intent_file = self.data_dir / f"intent_{system_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(intent_file, 'w', encoding='utf-8') as f:
                json.dump(intent, f, indent=2, default=str)

            logger.info(f"✅ Intent articulated: {system_name}")
            return intent


        except Exception as e:
            self.logger.error(f"Error in articulate_intent: {e}", exc_info=True)
            raise
class TemplateGenerator:
    """Generate templates for processes, policies, procedures, teams, company"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.intent_articulator = IntentArticulator(project_root)

    def create_process_template(self, process_name: str, description: str, steps: List[str]) -> Dict[str, Any]:
        try:
            """Create process template"""
            template = {
                "template_type": "PROCESS",
                "timestamp": datetime.now().isoformat(),
                "process_name": process_name,
                "description": description,
                "steps": steps,
                "standardized": True,
                "modularized": True,
                "intent": self.intent_articulator.articulate_intent(
                    process_name,
                    description,
                    [f"Execute step: {step}" for step in steps]
                )
            }

            # Save template
            template_file = self.templates_dir / "processes" / f"{process_name.lower().replace(' ', '_')}_template.json"
            template_file.parent.mkdir(parents=True, exist_ok=True)
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, default=str)

            logger.info(f"✅ Process template created: {process_name}")
            return template

        except Exception as e:
            self.logger.error(f"Error in create_process_template: {e}", exc_info=True)
            raise
    def create_policy_template(self, policy_name: str, description: str, rules: List[str]) -> Dict[str, Any]:
        try:
            """Create policy template"""
            template = {
                "template_type": "POLICY",
                "timestamp": datetime.now().isoformat(),
                "policy_name": policy_name,
                "description": description,
                "rules": rules,
                "standardized": True,
                "modularized": True,
                "intent": self.intent_articulator.articulate_intent(
                    policy_name,
                    description,
                    rules
                )
            }

            # Save template
            template_file = self.templates_dir / "policies" / f"{policy_name.lower().replace(' ', '_')}_template.json"
            template_file.parent.mkdir(parents=True, exist_ok=True)
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, default=str)

            logger.info(f"✅ Policy template created: {policy_name}")
            return template

        except Exception as e:
            self.logger.error(f"Error in create_policy_template: {e}", exc_info=True)
            raise
    def create_procedure_template(self, procedure_name: str, description: str, steps: List[str]) -> Dict[str, Any]:
        try:
            """Create procedure template"""
            template = {
                "template_type": "PROCEDURE",
                "timestamp": datetime.now().isoformat(),
                "procedure_name": procedure_name,
                "description": description,
                "steps": steps,
                "standardized": True,
                "modularized": True,
                "intent": self.intent_articulator.articulate_intent(
                    procedure_name,
                    description,
                    steps
                )
            }

            # Save template
            template_file = self.templates_dir / "procedures" / f"{procedure_name.lower().replace(' ', '_')}_template.json"
            template_file.parent.mkdir(parents=True, exist_ok=True)
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, default=str)

            logger.info(f"✅ Procedure template created: {procedure_name}")
            return template

        except Exception as e:
            self.logger.error(f"Error in create_procedure_template: {e}", exc_info=True)
            raise
    def create_team_template(self, team_name: str, description: str, roles: List[str]) -> Dict[str, Any]:
        """Create team template"""
        template = {
            "template_type": "TEAM",
            "timestamp": datetime.now().isoformat(),
            "team_name": team_name,
            "description": description,
            "roles": roles,
            "standardized": True,
            "modularized": True,
            "intent": self.intent_articulator.articulate_intent(
                team_name,
                description,
                [f"Role: {role}" for role in roles]
            )
        }

        # Save template
        template_file = self.templates_dir / "teams" / f"{team_name.lower().replace(' ', '_')}_template.json"
        template_file.parent.mkdir(parents=True, exist_ok=True)
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, default=str)

        logger.info(f"✅ Team template created: {team_name}")
        return template

    def create_company_template(self, company_name: str, description: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create company template"""
        template = {
            "template_type": "COMPANY",
            "timestamp": datetime.now().isoformat(),
            "company_name": company_name,
            "description": description,
            "structure": structure,
            "standardized": True,
            "modularized": True,
            "intent": self.intent_articulator.articulate_intent(
                company_name,
                description,
                [f"Structure: {key}" for key in structure.keys()]
            )
        }

        # Save template
        template_file = self.templates_dir / "companies" / f"{company_name.lower().replace(' ', '_')}_template.json"
        template_file.parent.mkdir(parents=True, exist_ok=True)
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, default=str)

        logger.info(f"✅ Company template created: {company_name}")
        return template


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Template System")
    parser.add_argument("--create-process", type=str, help="Create process template")
    parser.add_argument("--create-policy", type=str, help="Create policy template")
    parser.add_argument("--create-procedure", type=str, help="Create procedure template")
    parser.add_argument("--create-team", type=str, help="Create team template")
    parser.add_argument("--create-company", type=str, help="Create company template")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    generator = TemplateGenerator(project_root)

    if args.create_process:
        generator.create_process_template(
            args.create_process,
            f"Template process for {args.create_process}",
            ["Step 1", "Step 2", "Step 3"]
        )
    elif args.create_policy:
        generator.create_policy_template(
            args.create_policy,
            f"Template policy for {args.create_policy}",
            ["Rule 1", "Rule 2", "Rule 3"]
        )
    elif args.create_procedure:
        generator.create_procedure_template(
            args.create_procedure,
            f"Template procedure for {args.create_procedure}",
            ["Step 1", "Step 2", "Step 3"]
        )
    elif args.create_team:
        generator.create_team_template(
            args.create_team,
            f"Template team for {args.create_team}",
            ["Role 1", "Role 2", "Role 3"]
        )
    elif args.create_company:
        generator.create_company_template(
            args.create_company,
            f"Template company for {args.create_company}",
            {"departments": [], "teams": [], "processes": []}
        )
    else:
        logger.info("Use --create-process, --create-policy, --create-procedure, --create-team, or --create-company")


if __name__ == "__main__":


    main()