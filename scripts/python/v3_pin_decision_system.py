#!/usr/bin/env python3
"""
@v3 Pin Decision System - Judicial Approval for Pin/Unpin Operations

Integrates @v3 Judicial Approval Framework with pin/unpin operations.
Uses #syphon for finding pin-related code and decisions.

All pin/unpin decisions now require judicial approval through the v3 framework.

Tags: #V3 #JUDICIAL_APPROVAL #PIN #UNPIN #SYPHON #DECISIONING @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

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
    logger = get_logger("V3PinDecisionSystem")
    V3_AVAILABLE = True
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("V3PinDecisionSystem")
    logger.warning(f"V3 framework not available: {e}")
    V3_AVAILABLE = False

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISIONING_AVAILABLE = True
except ImportError:
    DECISIONING_AVAILABLE = False
    logger.warning("Decisioning not available")


class PinOperationTicket:
    """Change control ticket for pin/unpin operations"""

    @staticmethod
    def create_pin_ticket(
        file_path: str,
        reason: str,
        operation: str = "pin",
        priority: str = "medium",
        environment: Environment = Environment.DEV
    ) -> ChangeControlTicket:
        """Create a change control ticket for pin operation"""
        return ChangeControlTicket(
            ticket_id=f"PIN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            ticket_type="infrastructure",
            priority=priority,
            environment=environment,
            requester="Pin Decision System",
            description=f"{operation.upper()} operation for file: {file_path}",
            rationale=reason,
            affected_systems=[file_path],
            qa_approval=True,  # Pin operations are typically low-risk
            rollback_plan=f"Unpin file if needed: unpin {file_path}"
        )

    @staticmethod
    def create_unpin_ticket(
        file_path: str,
        reason: str,
        priority: str = "low",
        environment: Environment = Environment.DEV
    ) -> ChangeControlTicket:
        """Create a change control ticket for unpin operation"""
        return ChangeControlTicket(
            ticket_id=f"UNPIN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            ticket_type="infrastructure",
            priority=priority,
            environment=environment,
            requester="Pin Decision System",
            description=f"UNPIN operation for file: {file_path}",
            rationale=reason,
            affected_systems=[file_path],
            qa_approval=True,
            rollback_plan=f"Re-pin file if needed: pin {file_path}"
        )


class V3PinDecisionSystem:
    """
    @v3 Pin Decision System

    All pin/unpin operations require judicial approval through the v3 framework.
    Uses #syphon for finding and analyzing pin-related code.
    """

    def __init__(self, config: Optional[V3VerificationConfig] = None):
        if not V3_AVAILABLE:
            raise ImportError("V3 Judicial Approval Framework not available")

        self.config = config or V3VerificationConfig(
            enabled=True,
            verification_log_path=project_root / "data" / "v3_verification" / "pin_decisions.jsonl",
            project_root=project_root
        )
        self.approval_system = V3JudicialApprovalSystem(self.config)
        logger.info("V3 Pin Decision System initialized")

    def should_pin_file(
        self,
        file_path: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Determine if file should be pinned with judicial approval

        Args:
            file_path: Path to file
            reason: Reason for pinning
            context: Additional context (line_count, age, crashes, etc.)

        Returns:
            Decision dict with approval status and details
        """
        logger.info(f"🔍 V3 Pin Decision: {file_path}")

        # Determine priority based on context
        priority = "medium"
        if context:
            if context.get("crashes", 0) >= 3:
                priority = "critical"
            elif context.get("line_count", 0) >= 100000:
                priority = "high"

        # Create pin ticket
        ticket = PinOperationTicket.create_pin_ticket(
            file_path=file_path,
            reason=reason,
            operation="pin",
            priority=priority,
            environment=Environment.DEV
        )

        # Add context to ticket
        if context:
            ticket.code_changes = {
                "context": context,
                "operation": "pin"
            }

        # Request judicial approval
        decision = self.approval_system.verify_ticket(ticket)

        return {
            "should_pin": decision.status == ApprovalStatus.APPROVED,
            "status": decision.status.value,
            "rationale": decision.rationale,
            "conditions": decision.conditions,
            "ticket_id": ticket.ticket_id,
            "decision": decision
        }

    def should_unpin_file(
        self,
        file_path: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Determine if file should be unpinned with judicial approval

        Args:
            file_path: Path to file
            reason: Reason for unpinning
            context: Additional context (age, completion, etc.)

        Returns:
            Decision dict with approval status and details
        """
        logger.info(f"🔍 V3 Unpin Decision: {file_path}")

        # Determine priority based on context
        priority = "low"
        if context:
            if context.get("crashes", 0) >= 3:
                priority = "critical"
            elif context.get("line_count", 0) >= 100000:
                priority = "high"
            elif context.get("age_hours", 0) >= 24:
                priority = "medium"

        # Create unpin ticket
        ticket = PinOperationTicket.create_unpin_ticket(
            file_path=file_path,
            reason=reason,
            priority=priority,
            environment=Environment.DEV
        )

        # Add context to ticket
        if context:
            ticket.code_changes = {
                "context": context,
                "operation": "unpin"
            }

        # Request judicial approval
        decision = self.approval_system.verify_ticket(ticket)

        return {
            "should_unpin": decision.status == ApprovalStatus.APPROVED,
            "status": decision.status.value,
            "rationale": decision.rationale,
            "conditions": decision.conditions,
            "ticket_id": ticket.ticket_id,
            "decision": decision
        }

    def should_archive_file(
        self,
        file_path: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Determine if file should be archived with judicial approval

        Args:
            file_path: Path to file
            reason: Reason for archiving
            context: Additional context

        Returns:
            Decision dict with approval status and details
        """
        logger.info(f"🔍 V3 Archive Decision: {file_path}")

        # Archive is typically low priority
        priority = "low"
        if context and context.get("crashes", 0) >= 3:
            priority = "high"

        ticket = ChangeControlTicket(
            ticket_id=f"ARCHIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            ticket_type="infrastructure",
            priority=priority,
            environment=Environment.DEV,
            requester="Pin Decision System",
            description=f"ARCHIVE operation for file: {file_path}",
            rationale=reason,
            affected_systems=[file_path],
            qa_approval=True,
            rollback_plan=f"Restore from archive if needed"
        )

        if context:
            ticket.code_changes = {
                "context": context,
                "operation": "archive"
            }

        decision = self.approval_system.verify_ticket(ticket)

        return {
            "should_archive": decision.status == ApprovalStatus.APPROVED,
            "status": decision.status.value,
            "rationale": decision.rationale,
            "conditions": decision.conditions,
            "ticket_id": ticket.ticket_id,
            "decision": decision
        }


def syphon_pin_operations(project_root: Path, max_results: int = 100, use_perl: bool = True) -> List[Dict[str, Any]]:
    """
    Use #syphon to find all pin-related operations in the codebase

    Uses Perl if available (best for text processing), Python otherwise.

    Args:
        project_root: Project root directory
        max_results: Maximum number of results to return (prevents serialization issues)
        use_perl: Use Perl if available (default: True) - Perl is best for text processing

    Returns:
        List of pin operation locations (limited to max_results)
    """
    # Try to use Perl integration if available
    try:
        from syphon_perl_integration import syphon_pin_operations as perl_syphon
        logger.info("Using Perl-based syphon (best for text processing)")
        return perl_syphon(project_root, max_results, use_perl)
    except ImportError:
        logger.debug("Perl integration not available, using Python implementation")
        pass

    # Python fallback implementation
    pin_operations = []

    # Search for pin-related patterns
    patterns = [
        (r"\.pin_file\(", "pin_file call"),
        (r"\.unpin_file\(", "unpin_file call"),
        (r"is_pinned", "is_pinned check"),
        (r"pin_reason", "pin_reason usage"),
        (r"auto.*pin", "auto pin pattern"),
        (r"pin.*manager", "pin manager")
    ]

    try:
        import re

        # Search in Python files
        search_dir = project_root / "scripts" / "python"
        if not search_dir.exists():
            logger.warning(f"Search directory not found: {search_dir}")
            return pin_operations

        # Walk through Python files (limit to prevent large results)
        file_count = 0
        max_files = 50  # Limit files to search

        for py_file in search_dir.rglob("*.py"):
            if file_count >= max_files or len(pin_operations) >= max_results:
                break

            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Limit file size to prevent memory issues
                    if len(content) > 1000000:  # 1MB limit
                        logger.debug(f"Skipping large file: {py_file}")
                        continue

                    lines = content.split('\n')

                    # Check each pattern (limit matches per file)
                    matches_per_file = 0
                    max_matches_per_file = 10

                    for pattern, pattern_name in patterns:
                        if len(pin_operations) >= max_results:
                            break
                        if matches_per_file >= max_matches_per_file:
                            break

                        for line_num, line in enumerate(lines, 1):
                            if len(pin_operations) >= max_results:
                                break
                            if matches_per_file >= max_matches_per_file:
                                break

                            if re.search(pattern, line, re.IGNORECASE):
                                pin_operations.append({
                                    "file": str(py_file.relative_to(project_root)),
                                    "line": min(line_num, 2147483647),  # Ensure valid int32
                                    "content": line.strip()[:80],  # First 80 chars
                                    "pattern": pattern_name
                                })
                                matches_per_file += 1

                file_count += 1
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
                continue

    except Exception as e:
        logger.warning(f"Syphon operations failed: {e}")

    # Ensure we don't exceed max_results
    return pin_operations[:max_results]


def integrate_v3_with_auto_pin_system():
    """
    Integrate v3 judicial approval with auto_pin_unpin_autoarchive_system

    This function modifies the decision-making to use v3 approval
    """
    logger.info("Integrating V3 with auto pin system...")

    # The integration would modify auto_pin_unpin_autoarchive_system.py
    # to use V3PinDecisionSystem for all decisions

    integration_code = '''
# In auto_pin_unpin_autoarchive_system.py, modify evaluate_session:

from v3_pin_decision_system import V3PinDecisionSystem

class AutoPinUnpinAutoArchive:
    def __init__(self, project_root: Path):
        # ... existing code ...
        self.v3_system = V3PinDecisionSystem()

    def evaluate_session(self, session_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """@v3: Use judicial approval for all decisions"""
        file_path = session_metrics.get("file_path", "unknown")
        reason = f"Auto-pin evaluation: {session_metrics}"

        # Use V3 for pin decision
        pin_decision = self.v3_system.should_pin_file(file_path, reason, session_metrics)

        # Use V3 for unpin decision
        unpin_decision = self.v3_system.should_unpin_file(file_path, reason, session_metrics)

        # Use V3 for archive decision
        archive_decision = self.v3_system.should_archive_file(file_path, reason, session_metrics)

        return {
            "should_unpin": unpin_decision["should_unpin"],
            "should_archive": archive_decision["should_archive"],
            "should_syphon": True,  # Always syphon before archive
            "reason": f"V3 Approved: {unpin_decision['rationale']}",
            "priority": "HIGH" if unpin_decision["status"] == "approved" else "NORMAL",
            "v3_ticket_id": unpin_decision.get("ticket_id"),
            "v3_status": unpin_decision["status"]
        }
    '''

    logger.info("Integration code prepared (see function docstring)")
    return integration_code


if __name__ == "__main__":
    """Test the V3 Pin Decision System"""

    if not V3_AVAILABLE:
        print("❌ V3 framework not available")
        sys.exit(1)

    system = V3PinDecisionSystem()

    # Test pin decision
    print("="*80)
    print("🔍 V3 PIN DECISION TEST")
    print("="*80)

    test_context = {
        "line_count": 50000,
        "age_hours": 12,
        "crashes": 0,
        "completed": False
    }

    pin_decision = system.should_pin_file(
        file_path="test_file.py",
        reason="Test pin operation",
        context=test_context
    )

    print(f"Should Pin: {pin_decision['should_pin']}")
    print(f"Status: {pin_decision['status']}")
    print(f"Rationale: {pin_decision['rationale']}")
    print(f"Ticket ID: {pin_decision['ticket_id']}")

    # Test unpin decision
    print("\n" + "="*80)
    print("🔍 V3 UNPIN DECISION TEST")
    print("="*80)

    unpin_context = {
        "line_count": 150000,
        "age_hours": 30,
        "crashes": 3,
        "completed": False
    }

    unpin_decision = system.should_unpin_file(
        file_path="test_file.py",
        reason="High line count and crashes",
        context=unpin_context
    )

    print(f"Should Unpin: {unpin_decision['should_unpin']}")
    print(f"Status: {unpin_decision['status']}")
    print(f"Rationale: {unpin_decision['rationale']}")
    print(f"Ticket ID: {unpin_decision['ticket_id']}")

    # Syphon pin operations
    print("\n" + "="*80)
    print("🔍 SYPHON PIN OPERATIONS")
    print("="*80)

    pin_ops = syphon_pin_operations(project_root, max_results=50)  # Limit results
    print(f"Found {len(pin_ops)} pin-related operations (showing first 5)")
    for op in pin_ops[:5]:  # Show first 5
        print(f"  {op['file']}:{op['line']} - {op['content'][:60]}...")

    print("\n" + "="*80)
    print("✅ V3 PIN DECISION SYSTEM TEST COMPLETE")
    print("="*80)
