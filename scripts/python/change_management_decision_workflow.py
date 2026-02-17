#!/usr/bin/env python3
"""
Change Management Decision Workflow

Runs version increment and house ordering through:
- Decision tree
- Helpdesk workflows
- Problem management
- Change management processes

Creates teams with backstories from IPs if they don't exist.

Tags: #CHANGE_MANAGEMENT #DECISION_TREE #HELPDESK #PROBLEM_MANAGEMENT @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("ChangeManagementDecision")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ChangeManagementDecision")


class ChangeManagementDecisionWorkflow:
    """
    Change Management Decision Workflow

    Routes through decision tree, helpdesk, problem management,
    and change management processes.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "change_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.teams_dir = self.project_root / "data" / "change_management" / "teams"
        self.teams_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("🔄 CHANGE MANAGEMENT DECISION WORKFLOW")
        logger.info("=" * 80)
        logger.info("   Running through decision tree")
        logger.info("   Helpdesk & Problem Management workflows")
        logger.info("   Change Management section")
        logger.info("")

    def load_or_create_teams(self) -> Dict[str, Dict[str, Any]]:
        """
        Load existing teams or create with backstories from IPs

        Pulls from all IPs: Star Wars, Marvel, etc.
        """
        teams_file = self.teams_dir / "change_management_teams.json"

        if teams_file.exists():
            try:
                with open(teams_file, 'r', encoding='utf-8') as f:
                    teams = json.load(f)
                logger.info(f"✅ Loaded {len(teams)} existing teams")
                return teams
            except Exception as e:
                logger.warning(f"Failed to load teams: {e}")

        # Create teams with backstories from IPs
        logger.info("👥 Creating change management teams with backstories...")
        logger.info("")

        teams = {
            "change_management_board": {
                "name": "Change Management Board",
                "section": "Change Management",
                "responsibility": "Approve and oversee all changes",
                "members": [
                    {
                        "name": "Moff Tarkin",
                        "role": "Change Management Director",
                        "ip_source": "Star Wars",
                        "backstory": "Imperial officer known for decisive action and strategic oversight. Brings order and discipline to change management.",
                        "personality": "Decisive, strategic, no-nonsense",
                        "perspective": "Ensures all changes follow proper procedures and maintain system stability"
                    },
                    {
                        "name": "Nick Fury",
                        "role": "Change Coordinator",
                        "ip_source": "Marvel",
                        "backstory": "S.H.I.E.L.D. director with experience managing complex operations. Knows when to approve and when to hold.",
                        "personality": "Pragmatic, experienced, cautious",
                        "perspective": "Balances innovation with risk management"
                    },
                    {
                        "name": "Admiral Ackbar",
                        "role": "Change Review Officer",
                        "ip_source": "Star Wars",
                        "backstory": "Mon Calamari admiral known for tactical analysis. It's a trap! - but also knows when it's not.",
                        "personality": "Analytical, cautious, thorough",
                        "perspective": "Identifies risks and potential issues before approval"
                    }
                ]
            },
            "helpdesk_team": {
                "name": "Helpdesk Change Review Team",
                "section": "Helpdesk",
                "responsibility": "Review changes from helpdesk perspective",
                "members": [
                    {
                        "name": "C-3PO",
                        "role": "Helpdesk Protocol Officer",
                        "ip_source": "Star Wars",
                        "backstory": "Protocol droid fluent in over 6 million forms of communication. Ensures all changes follow proper protocols.",
                        "personality": "Protocol-focused, detail-oriented, anxious",
                        "perspective": "Ensures changes don't break existing protocols and workflows"
                    },
                    {
                        "name": "R2-D2",
                        "role": "Technical Support Specialist",
                        "ip_source": "Star Wars",
                        "backstory": "Astromech droid known for technical expertise and problem-solving. Beeps and whistles translate to technical insights.",
                        "personality": "Technical, resourceful, determined",
                        "perspective": "Technical feasibility and impact assessment"
                    },
                    {
                        "name": "BB-8",
                        "role": "Change Impact Analyst",
                        "ip_source": "Star Wars",
                        "backstory": "Spherical astromech droid with modern technical capabilities. Quick to identify impacts.",
                        "personality": "Energetic, quick, analytical",
                        "perspective": "Rapid impact assessment and user experience"
                    }
                ]
            },
            "problem_management_team": {
                "name": "Problem Management Team",
                "section": "Problem Management",
                "responsibility": "Identify and prevent problems from changes",
                "members": [
                    {
                        "name": "Vision",
                        "role": "Problem Prevention Analyst",
                        "ip_source": "Marvel",
                        "backstory": "Synthezoid with ability to see potential futures. Identifies problems before they occur.",
                        "personality": "Analytical, foresight, philosophical",
                        "perspective": "Predicts potential problems from changes"
                    },
                    {
                        "name": "The Watcher",
                        "role": "Change Observer",
                        "ip_source": "Marvel",
                        "backstory": "Cosmic entity that observes but does not interfere. Provides objective analysis.",
                        "personality": "Objective, observant, non-interfering",
                        "perspective": "Unbiased observation of change impacts"
                    },
                    {
                        "name": "Oracle",
                        "role": "Problem Prediction Specialist",
                        "ip_source": "DC Comics",
                        "backstory": "Seer with ability to predict outcomes. Warns of potential issues.",
                        "personality": "Mystical, warning, protective",
                        "perspective": "Predicts long-term consequences"
                    }
                ]
            },
            "technical_review_team": {
                "name": "Technical Review Team",
                "section": "Technical",
                "responsibility": "Technical feasibility and architecture review",
                "members": [
                    {
                        "name": "Tony Stark",
                        "role": "Technical Architect",
                        "ip_source": "Marvel",
                        "backstory": "Genius inventor and engineer. Reviews technical feasibility and architecture.",
                        "personality": "Brilliant, innovative, sometimes reckless",
                        "perspective": "Technical excellence and innovation"
                    },
                    {
                        "name": "Shuri",
                        "role": "Systems Engineer",
                        "ip_source": "Marvel",
                        "backstory": "Wakandan princess and brilliant engineer. Ensures systems are properly designed.",
                        "personality": "Brilliant, methodical, forward-thinking",
                        "perspective": "System design and integration"
                    },
                    {
                        "name": "Banner/Hulk",
                        "role": "Quality Assurance Lead",
                        "ip_source": "Marvel",
                        "backstory": "Scientist with dual nature. Calm analysis and thorough testing.",
                        "personality": "Analytical, thorough, careful",
                        "perspective": "Quality and testing requirements"
                    }
                ]
            },
            "security_team": {
                "name": "Security Review Team",
                "section": "Security",
                "responsibility": "Security and compliance review",
                "members": [
                    {
                        "name": "Black Widow",
                        "role": "Security Analyst",
                        "ip_source": "Marvel",
                        "backstory": "Master spy and security expert. Identifies security vulnerabilities.",
                        "personality": "Vigilant, thorough, strategic",
                        "perspective": "Security implications and vulnerabilities"
                    },
                    {
                        "name": "Fury (Maria Hill)",
                        "role": "Compliance Officer",
                        "ip_source": "Marvel",
                        "backstory": "S.H.I.E.L.D. deputy director. Ensures compliance with regulations.",
                        "personality": "Compliance-focused, thorough, no-nonsense",
                        "perspective": "Regulatory compliance and standards"
                    }
                ]
            }
        }

        # Save teams
        with open(teams_file, 'w', encoding='utf-8') as f:
            json.dump(teams, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Created {len(teams)} change management teams")
        logger.info("")

        return teams

    def route_through_decision_tree(self, change_request: Dict[str, Any]) -> Dict[str, Any]:
        """Route change request through decision tree"""
        logger.info("🌳 Routing through decision tree...")
        logger.info("")

        decision_result = {
            "routed_through": "decision_tree",
            "timestamp": datetime.now().isoformat(),
            "decisions": [],
            "path": []
        }

        # Decision 1: Change Type
        change_type = change_request.get("type", "standard")
        if change_type == "version_increment":
            decision_result["decisions"].append({
                "node": "change_type",
                "decision": "version_increment",
                "route": "change_management_board"
            })
            decision_result["path"].append("Change Management Board")

        # Decision 2: Impact Assessment
        impact = change_request.get("impact", "medium")
        if impact == "high":
            decision_result["decisions"].append({
                "node": "impact_assessment",
                "decision": "high_impact",
                "route": "problem_management + technical_review"
            })
            decision_result["path"].append("Problem Management")
            decision_result["path"].append("Technical Review")

        # Decision 3: Security Implications
        has_security = change_request.get("security_implications", False)
        if has_security:
            decision_result["decisions"].append({
                "node": "security_check",
                "decision": "security_review_required",
                "route": "security_team"
            })
            decision_result["path"].append("Security Review")

        logger.info(f"   Decision path: {' → '.join(decision_result['path'])}")
        logger.info("")

        return decision_result

    def get_team_feedback(
        self,
        teams: Dict[str, Dict[str, Any]],
        change_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get feedback from all relevant teams"""
        logger.info("👥 Gathering team feedback...")
        logger.info("")

        feedback = {
            "timestamp": datetime.now().isoformat(),
            "teams_consulted": [],
            "questions": [],
            "suggestions": [],
            "concerns": [],
            "approvals": [],
            "recommendations": []
        }

        # Change Management Board
        board = teams.get("change_management_board", {})
        logger.info("   📋 Change Management Board:")
        for member in board.get("members", []):
            member_feedback = self._get_member_feedback(member, change_request, "approval")
            feedback["teams_consulted"].append({
                "team": "Change Management Board",
                "member": member["name"],
                "feedback": member_feedback
            })
            if member_feedback.get("questions"):
                feedback["questions"].extend(member_feedback["questions"])
            if member_feedback.get("concerns"):
                feedback["concerns"].extend(member_feedback["concerns"])
            if member_feedback.get("approval"):
                feedback["approvals"].append({
                    "member": member["name"],
                    "status": member_feedback["approval"]
                })
            logger.info(f"      {member['name']}: {member_feedback.get('summary', 'Reviewing...')}")

        # Helpdesk Team
        helpdesk = teams.get("helpdesk_team", {})
        logger.info("")
        logger.info("   🎫 Helpdesk Team:")
        for member in helpdesk.get("members", []):
            member_feedback = self._get_member_feedback(member, change_request, "helpdesk")
            feedback["teams_consulted"].append({
                "team": "Helpdesk",
                "member": member["name"],
                "feedback": member_feedback
            })
            if member_feedback.get("suggestions"):
                feedback["suggestions"].extend(member_feedback["suggestions"])
            logger.info(f"      {member['name']}: {member_feedback.get('summary', 'Reviewing...')}")

        # Problem Management Team
        problem_mgmt = teams.get("problem_management_team", {})
        logger.info("")
        logger.info("   ⚠️  Problem Management Team:")
        for member in problem_mgmt.get("members", []):
            member_feedback = self._get_member_feedback(member, change_request, "problem")
            feedback["teams_consulted"].append({
                "team": "Problem Management",
                "member": member["name"],
                "feedback": member_feedback
            })
            if member_feedback.get("concerns"):
                feedback["concerns"].extend(member_feedback["concerns"])
            logger.info(f"      {member['name']}: {member_feedback.get('summary', 'Reviewing...')}")

        # Technical Review Team
        technical = teams.get("technical_review_team", {})
        logger.info("")
        logger.info("   🔧 Technical Review Team:")
        for member in technical.get("members", []):
            member_feedback = self._get_member_feedback(member, change_request, "technical")
            feedback["teams_consulted"].append({
                "team": "Technical Review",
                "member": member["name"],
                "feedback": member_feedback
            })
            if member_feedback.get("suggestions"):
                feedback["suggestions"].extend(member_feedback["suggestions"])
            logger.info(f"      {member['name']}: {member_feedback.get('summary', 'Reviewing...')}")

        # Security Team
        security = teams.get("security_team", {})
        logger.info("")
        logger.info("   🔒 Security Team:")
        for member in security.get("members", []):
            member_feedback = self._get_member_feedback(member, change_request, "security")
            feedback["teams_consulted"].append({
                "team": "Security",
                "member": member["name"],
                "feedback": member_feedback
            })
            if member_feedback.get("concerns"):
                feedback["concerns"].extend(member_feedback["concerns"])
            logger.info(f"      {member['name']}: {member_feedback.get('summary', 'Reviewing...')}")

        logger.info("")

        return feedback

    def _get_member_feedback(
        self,
        member: Dict[str, Any],
        change_request: Dict[str, Any],
        context: str
    ) -> Dict[str, Any]:
        """Get feedback from a team member based on their personality and role"""
        feedback = {
            "member": member["name"],
            "role": member["role"],
            "perspective": member["perspective"],
            "questions": [],
            "suggestions": [],
            "concerns": [],
            "approval": None,
            "summary": ""
        }

        name = member["name"].lower()
        personality = member.get("personality", "").lower()
        change_type = change_request.get("type", "")

        # Moff Tarkin - Decisive, strategic
        if "tarkin" in name:
            if change_type == "version_increment":
                feedback["approval"] = "conditional"
                feedback["concerns"].append({
                    "concern": "Version increment must follow proper change management process",
                    "details": "Ensure all approvals are in place before incrementing"
                })
                feedback["summary"] = "Conditional approval - follow process"

        # Nick Fury - Pragmatic, cautious
        elif "fury" in name and "nick" in name:
            feedback["approval"] = "pending_review"
            feedback["questions"].append({
                "question": "Have all risks been assessed?",
                "priority": "high"
            })
            feedback["summary"] = "Pending - need risk assessment"

        # Admiral Ackbar - Analytical, cautious
        elif "ackbar" in name:
            feedback["concerns"].append({
                "concern": "Potential trap - large number of changes",
                "details": "3,032 modified files could hide issues"
            })
            feedback["summary"] = "It's a trap! - Review carefully"

        # C-3PO - Protocol-focused
        elif "c-3po" in name or "3po" in name:
            feedback["suggestions"].append({
                "suggestion": "Ensure all protocols are followed",
                "details": "Version increment must follow established protocols"
            })
            feedback["summary"] = "Protocols must be followed"

        # R2-D2 - Technical
        elif "r2" in name or "r2-d2" in name:
            feedback["suggestions"].append({
                "suggestion": "Technical validation required",
                "details": "Verify technical feasibility before proceeding"
            })
            feedback["summary"] = "*beeps* Technical validation needed"

        # Vision - Foresight
        elif "vision" in name:
            feedback["concerns"].append({
                "concern": "Potential future problems",
                "details": "Large change set may cause downstream issues"
            })
            feedback["summary"] = "Foresees potential issues"

        # Tony Stark - Technical excellence
        elif "stark" in name or "tony" in name:
            feedback["approval"] = "conditional"
            feedback["suggestions"].append({
                "suggestion": "Ensure technical excellence",
                "details": "Version increment should maintain code quality"
            })
            feedback["summary"] = "Conditional - maintain quality"

        # Black Widow - Security
        elif "widow" in name or "black widow" in name:
            feedback["concerns"].append({
                "concern": "Security implications of large change",
                "details": "3,032 files need security review"
            })
            feedback["summary"] = "Security review required"

        # Default feedback
        else:
            feedback["approval"] = "pending"
            feedback["questions"].append({
                "question": f"Review required from {member['role']} perspective",
                "priority": "medium"
            })
            feedback["summary"] = "Reviewing..."

        return feedback

    def generate_decision_report(
        self,
        change_request: Dict[str, Any],
        decision_tree: Dict[str, Any],
        team_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive decision report"""
        logger.info("📊 Generating decision report...")
        logger.info("")

        # Count approvals
        approvals = team_feedback.get("approvals", [])
        approved = len([a for a in approvals if a.get("status") == "approved"])
        conditional = len([a for a in approvals if a.get("status") == "conditional"])
        pending = len([a for a in approvals if a.get("status") == "pending"])

        report = {
            "change_request": change_request,
            "decision_tree_result": decision_tree,
            "team_feedback": team_feedback,
            "summary": {
                "teams_consulted": len(team_feedback.get("teams_consulted", [])),
                "questions": len(team_feedback.get("questions", [])),
                "suggestions": len(team_feedback.get("suggestions", [])),
                "concerns": len(team_feedback.get("concerns", [])),
                "approvals": {
                    "approved": approved,
                    "conditional": conditional,
                    "pending": pending
                }
            },
            "recommendation": self._generate_recommendation(team_feedback),
            "next_steps": self._generate_next_steps(team_feedback)
        }

        return report

    def _generate_recommendation(self, feedback: Dict[str, Any]) -> str:
        """Generate overall recommendation"""
        concerns = len(feedback.get("concerns", []))
        approvals = feedback.get("approvals", [])
        approved_count = len([a for a in approvals if a.get("status") == "approved"])

        if concerns > 5:
            return "HOLD - Address concerns before proceeding"
        elif approved_count >= 2:
            return "PROCEED - With conditions"
        else:
            return "PENDING - More review needed"

    def _generate_next_steps(self, feedback: Dict[str, Any]) -> List[str]:
        """Generate next steps"""
        steps = []

        if feedback.get("concerns"):
            steps.append("Address concerns raised by teams")

        if feedback.get("questions"):
            steps.append("Answer questions from team members")

        steps.append("Obtain final approvals")
        steps.append("Proceed with change implementation")

        return steps

    def save_report(self, report: Dict[str, Any]) -> Path:
        try:
            """Save decision report"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.data_dir / f"change_decision_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"📁 Report saved: {report_file}")

            return report_file

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
    def print_report(self, report: Dict[str, Any]):
        """Print formatted report"""
        summary = report["summary"]
        recommendation = report["recommendation"]

        print("=" * 80)
        print("🔄 CHANGE MANAGEMENT DECISION REPORT")
        print("=" * 80)
        print("")
        print("TEAMS CONSULTED:")
        print(f"   Teams: {summary['teams_consulted']}")
        print(f"   Questions: {summary['questions']}")
        print(f"   Suggestions: {summary['suggestions']}")
        print(f"   Concerns: {summary['concerns']}")
        print("")
        print("APPROVALS:")
        approvals = summary["approvals"]
        print(f"   ✅ Approved: {approvals['approved']}")
        print(f"   ⚠️  Conditional: {approvals['conditional']}")
        print(f"   ⏳ Pending: {approvals['pending']}")
        print("")
        print(f"RECOMMENDATION: {recommendation}")
        print("")
        print("NEXT STEPS:")
        for i, step in enumerate(report["next_steps"], 1):
            print(f"   {i}. {step}")
        print("")
        print("=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Change management decision workflow")
    parser.add_argument("--save", action="store_true", help="Save report")

    args = parser.parse_args()

    workflow = ChangeManagementDecisionWorkflow()

    # Load or create teams
    teams = workflow.load_or_create_teams()

    # Create change request
    change_request = {
        "type": "version_increment",
        "description": "Version increment 7.0.0 → 7.1.0 and house ordering",
        "impact": "high",
        "security_implications": True,
        "files_affected": 3032,
        "untracked_files": 585,
        "sub_repos": 2
    }

    # Route through decision tree
    decision_tree = workflow.route_through_decision_tree(change_request)

    # Get team feedback
    team_feedback = workflow.get_team_feedback(teams, change_request)

    # Generate report
    report = workflow.generate_decision_report(change_request, decision_tree, team_feedback)

    # Print report
    workflow.print_report(report)

    # Save if requested
    if args.save:
        workflow.save_report(report)

    return report


if __name__ == "__main__":

    main()