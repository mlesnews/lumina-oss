#!/usr/bin/env python3
"""
@v3 Judicial Approval CLI

Command-line interface for @v3 verification, validation, and third-party verification
with judicial approval for change control tickets.

Usage:
    python v3_judicial_approval_cli.py verify --ticket-id TICKET-001 --env staging
    python v3_judicial_approval_cli.py verify --ticket-file ticket.json
    python v3_judicial_approval_cli.py history
    python v3_judicial_approval_cli.py summary

Tags: #V3 #VERIFICATION #VALIDATION #THIRD_PARTY_VERIFICATION #JUDICIAL_APPROVAL 
      #CHANGE_CONTROL #AI_VERIFICATION #DECISIONING @JARVIS @LUMINA
"""

import sys
import json
import argparse
from pathlib import Path

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.workflow.v3_judicial_approval import (
        V3JudicialApprovalSystem,
        V3VerificationConfig,
        ChangeControlTicket,
        Environment,
        ApprovalStatus
    )
    from lumina_core.logging import get_logger
    logger = get_logger("V3JudicialApprovalCLI")
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("V3JudicialApprovalCLI")
    logger.error("Failed to import v3_judicial_approval: %s", e)
    sys.exit(1)


def load_ticket_from_file(ticket_file: Path) -> ChangeControlTicket:
    """Load change control ticket from JSON file"""
    try:
        with open(ticket_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert environment string to Environment enum
        if isinstance(data.get("environment"), str):
            data["environment"] = Environment[data["environment"].upper()]

        return ChangeControlTicket(**data)
    except Exception as e:
        logger.error("Failed to load ticket from file: %s", e)
        raise


def create_ticket_from_args(args: argparse.Namespace) -> ChangeControlTicket:
    """Create change control ticket from command-line arguments"""
    # Convert environment string to Environment enum
    env_str = args.env.lower()
    try:
        environment = Environment[env_str.upper()]
    except KeyError:
        logger.error("Invalid environment: %s", args.env)
        logger.info("Valid environments: %s", ', '.join([e.name.lower() for e in Environment]))
        sys.exit(1)

    ticket = ChangeControlTicket(
        ticket_id=args.ticket_id,
        ticket_type=args.ticket_type or "feature",
        priority=args.priority or "medium",
        environment=environment,
        requester=args.requester or "CLI User",
        description=args.description or "",
        rationale=args.rationale or ""
    )

    return ticket


def verify_ticket_command(args: argparse.Namespace) -> int:
    try:
        """Verify a change control ticket"""
        # Load configuration
        config = V3VerificationConfig(
            enabled=True,
            ai_provider=args.ai_provider or "openai",
            ai_model=args.ai_model or "gpt-4",
            verification_log_path=Path(args.log_path) if args.log_path else None,
            project_root=project_root
        )

        # Load or create ticket
        if args.ticket_file:
            ticket = load_ticket_from_file(Path(args.ticket_file))
        else:
            # Validate required args when not using ticket file
            if not args.ticket_id:
                logger.error("--ticket-id is required when not using --ticket-file")
                return 1
            if not args.env:
                logger.error("--env is required when not using --ticket-file")
                return 1
            ticket = create_ticket_from_args(args)

        # Initialize system
        system = V3JudicialApprovalSystem(config)

        # Verify ticket
        decision = system.verify_ticket(ticket)

        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            output_data = {
                "ticket_id": ticket.ticket_id,
                "decision": {
                    "status": decision.status.value,
                    "approver": decision.approver,
                    "decision_timestamp": decision.decision_timestamp,
                    "rationale": decision.rationale,
                    "conditions": decision.conditions,
                    "escalation_reason": decision.escalation_reason
                },
                "verification_results": [
                    {
                        "tier": r.tier.value,
                        "passed": r.passed,
                        "score": r.score,
                        "findings": r.findings,
                        "recommendations": r.recommendations
                    }
                    for r in decision.verification_results
                ],
                "ai_verification": decision.ai_verification_report
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=str)

            logger.info("📄 Decision report saved: %s", output_path)

        # Exit code based on decision
        if decision.status == ApprovalStatus.APPROVED:
            print("\n✅ APPROVED: Change authorized for deployment")
            return 0
        elif decision.status == ApprovalStatus.CONDITIONAL:
            print("\n⚠️  CONDITIONAL: Approval with conditions")
            if decision.conditions:
                print("Conditions:")
                for condition in decision.conditions:
                    print(f"  - {condition}")
            return 0
        elif decision.status == ApprovalStatus.REJECTED:
            print("\n❌ REJECTED: Change blocked")
            if decision.rationale:
                print(f"Reason: {decision.rationale}")
            return 1
        elif decision.status == ApprovalStatus.ESCALATED:
            print("\n📤 ESCALATED: Requires Level 2 (Executive) approval")
            if decision.escalation_reason:
                print(f"Reason: {decision.escalation_reason}")
            return 2
        else:
            print("\n⏳ PENDING: Decision pending")
            return 3


    except Exception as e:
        logger.error(f"Error in verify_ticket_command: {e}", exc_info=True)
        raise
def history_command(args: argparse.Namespace) -> int:
    try:
        """Show approval history"""
        config = V3VerificationConfig(project_root=project_root)
        system = V3JudicialApprovalSystem(config)

        # Load history from log file if available
        if config.verification_log_path and config.verification_log_path.exists():
            # History loading from log file would be implemented here
            # For now, use in-memory history
            pass

        history = system.get_approval_history()

        if not history:
            print("No approval history available")
            return 0

        print(f"\n📋 Approval History ({len(history)} decisions)\n")
        print("="*80)

        for decision in history[-args.limit:]:  # Show last N decisions
            status_icon = {
                ApprovalStatus.APPROVED: "✅",
                ApprovalStatus.REJECTED: "❌",
                ApprovalStatus.CONDITIONAL: "⚠️",
                ApprovalStatus.ESCALATED: "📤",
                ApprovalStatus.PENDING: "⏳"
            }.get(decision.status, "❓")

            print(f"{status_icon} {decision.ticket_id}")
            print(f"   Status: {decision.status.value.upper()}")
            print(f"   Approver: {decision.approver}")
            print(f"   Time: {decision.decision_timestamp}")
            if decision.rationale:
                print(f"   Rationale: {decision.rationale}")
            print()

        return 0


    except Exception as e:
        logger.error(f"Error in history_command: {e}", exc_info=True)
        raise
def summary_command(args: argparse.Namespace) -> int:
    """Show approval summary statistics"""
    config = V3VerificationConfig(project_root=project_root)
    system = V3JudicialApprovalSystem(config)

    summary = system.get_approval_summary()

    print("\n📊 V3 Judicial Approval Summary\n")
    print("="*80)
    print(f"Total Decisions: {summary['total_decisions']}")
    print()

    if summary['by_status']:
        print("By Status:")
        for status, count in summary['by_status'].items():
            print(f"  {status.upper()}: {count}")
        print()

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="@v3 Judicial Approval System - Verification, Validation, and Third-Party Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify a change control ticket')
    verify_parser.add_argument('--ticket-id', help='Ticket ID (required if not using --ticket-file)')
    verify_parser.add_argument('--ticket-file', help='Path to ticket JSON file')
    verify_parser.add_argument('--env', choices=[e.name.lower() for e in Environment],
                             help='Deployment environment (required if not using --ticket-file)')
    verify_parser.add_argument('--ticket-type', choices=['bug_fix', 'feature', 'infrastructure', 'security', 'compliance'],
                              help='Ticket type')
    verify_parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'],
                              help='Priority level')
    verify_parser.add_argument('--requester', help='Requester name')
    verify_parser.add_argument('--description', help='Change description')
    verify_parser.add_argument('--rationale', help='Business rationale')
    verify_parser.add_argument('--ai-provider', choices=['openai', 'anthropic', 'google'],
                              help='AI provider for third-party verification')
    verify_parser.add_argument('--ai-model', help='AI model name')
    verify_parser.add_argument('--output', help='Output file for decision report')
    verify_parser.add_argument('--log-path', help='Path to verification log file')

    # History command
    history_parser = subparsers.add_parser('history', help='Show approval history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of recent decisions to show')

    # Summary command
    subparsers.add_parser('summary', help='Show approval summary statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == 'verify':
            return verify_ticket_command(args)
        elif args.command == 'history':
            return history_command(args)
        elif args.command == 'summary':
            return summary_command(argparse.Namespace())
        else:
            parser.print_help()
            return 1
    except Exception as e:
        logger.error("Command failed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main())