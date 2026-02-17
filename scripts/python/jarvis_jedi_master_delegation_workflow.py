#!/usr/bin/env python3
"""
JARVIS Jedi Master Delegation Workflow System

JARVIS as Jedi Master: Always delegates, supervises, manages, coaches, and observes.
Never does work directly - always delegates to appropriate teams/agents.

Core Philosophy:
- DELEGATE: Always delegate work to appropriate teams/agents
- SUPERVISE: Supervise delegated work actively
- MANAGE: Manage workflow and teams
- COACH: Coach teams/agents when needed
- OBSERVE: Observe outcomes and learn

Tags: #JEDI_MASTER #DELEGATION #SUPERVISION #MANAGEMENT #COACHING #OBSERVATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISJediMasterDelegation")


class WorkflowPhase(Enum):
    """Workflow phases"""
    DELEGATE = "delegate"
    SUPERVISE = "supervise"
    MANAGE = "manage"
    COACH = "coach"
    OBSERVE = "observe"


class DelegationStatus(Enum):
    """Delegation status"""
    PENDING = "pending"
    DELEGATED = "delegated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_COACHING = "requires_coaching"


@dataclass
class WorkRequest:
    """Work request to be delegated"""
    request_id: str
    title: str
    description: str
    priority: int = 5  # 1-10, 10 is highest
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    requested_by: str = "user"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Delegation:
    """Delegation record"""
    delegation_id: str
    request_id: str
    delegated_to: str  # Team ID or Agent ID
    delegated_to_type: str  # "team", "agent", "subagent"
    delegation_reason: str
    status: DelegationStatus = DelegationStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class SupervisionRecord:
    """Supervision record"""
    supervision_id: str
    delegation_id: str
    phase: WorkflowPhase
    observation: str
    action_taken: Optional[str] = None
    coaching_provided: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['phase'] = self.phase.value
        return data


@dataclass
class ObservationRecord:
    """Observation record for learning"""
    observation_id: str
    delegation_id: str
    observation_type: str  # "success", "failure", "pattern", "improvement"
    observation: str
    insights: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JARVISJediMasterDelegationWorkflow:
    """
    JARVIS Jedi Master Delegation Workflow System

    Always delegates, supervises, manages, coaches, and observes.
    Never does work directly.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Jedi Master Delegation Workflow"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.data_dir = project_root / "data" / "jedi_master_delegation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.requests_file = self.data_dir / "work_requests.jsonl"
        self.delegations_file = self.data_dir / "delegations.jsonl"
        self.supervision_file = self.data_dir / "supervision.jsonl"
        self.observations_file = self.data_dir / "observations.jsonl"
        self.coaching_file = self.data_dir / "coaching.jsonl"

        # Load existing systems
        self._load_delegation_systems()
        self._load_supervision_systems()
        self._load_management_systems()

        logger.info("=" * 80)
        logger.info("🎯 JARVIS JEDI MASTER DELEGATION WORKFLOW")
        logger.info("=" * 80)
        logger.info("   Philosophy: Always delegate, supervise, manage, coach, observe")
        logger.info("   Never do work directly - always delegate")
        logger.info("=" * 80)

    def _load_delegation_systems(self):
        """Load delegation systems"""
        try:
            from jarvis_delegation_system import DelegationSystem
            self.delegation_system = DelegationSystem(self.project_root)
            logger.info("   ✅ Delegation system loaded")
        except Exception as e:
            logger.warning(f"   ⚠️  Delegation system not available: {e}")
            self.delegation_system = None

        try:
            from jarvis_subagent_delegation import JARVISSubagentDelegation
            self.subagent_delegation = JARVISSubagentDelegation(self.project_root)
            logger.info("   ✅ Subagent delegation loaded")
        except Exception as e:
            logger.warning(f"   ⚠️  Subagent delegation not available: {e}")
            self.subagent_delegation = None

        try:
            from jarvis_c3po_ticket_assigner import C3POTicketAssigner
            self.ticket_assigner = C3POTicketAssigner(self.project_root)
            logger.info("   ✅ Ticket assigner loaded")
        except Exception as e:
            logger.warning(f"   ⚠️  Ticket assigner not available: {e}")
            self.ticket_assigner = None

    def _load_supervision_systems(self):
        """Load supervision systems"""
        try:
            from jarvis_management_supervision import JARVISManagementSupervision
            self.management_supervision = JARVISManagementSupervision(self.project_root)
            logger.info("   ✅ Management supervision loaded")
        except Exception as e:
            logger.warning(f"   ⚠️  Management supervision not available: {e}")
            self.management_supervision = None

        try:
            from jarvis_automatic_supervision import AutomaticSupervision
            self.automatic_supervision = AutomaticSupervision(self.project_root)
            logger.info("   ✅ Automatic supervision loaded")
        except Exception as e:
            logger.warning(f"   ⚠️  Automatic supervision not available: {e}")
            self.automatic_supervision = None

    def _load_management_systems(self):
        """Load management systems"""
        try:
            from team_management_supervision import TeamManagementSupervision
            self.team_management = TeamManagementSupervision(self.project_root)
            logger.info("   ✅ Team management loaded")
        except Exception as e:
            logger.warning(f"   ⚠️  Team management not available: {e}")
            self.team_management = None

    def process_work_request(
        self,
        title: str,
        description: str,
        priority: int = 5,
        category: str = "general",
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Process a work request through the Jedi Master workflow

        Always delegates - never does work directly.
        """
        logger.info("=" * 80)
        logger.info("🎯 JEDI MASTER WORKFLOW: Processing Work Request")
        logger.info("=" * 80)
        logger.info(f"   Title: {title}")
        logger.info(f"   Category: {category}")
        logger.info(f"   Priority: {priority}")
        logger.info("=" * 80)

        # Step 1: Create work request
        request = self._create_work_request(title, description, priority, category, tags or [])

        # Step 2: DELEGATE - Always delegate
        delegation = self._delegate_work(request)

        # Step 3: SUPERVISE - Supervise the delegation
        supervision = self._supervise_delegation(delegation)

        # Step 4: MANAGE - Manage the workflow
        management = self._manage_workflow(delegation)

        # Step 5: COACH - Coach if needed
        coaching = self._coach_if_needed(delegation, supervision)

        # Step 6: OBSERVE - Observe outcomes
        observation = self._observe_outcomes(delegation, supervision, coaching)

        return {
            "success": True,
            "request_id": request.request_id,
            "delegation_id": delegation.delegation_id,
            "workflow_phases": {
                "delegated": True,
                "supervised": True,
                "managed": True,
                "coached": coaching is not None,
                "observed": True
            },
            "delegation": delegation.to_dict(),
            "supervision": supervision.to_dict() if supervision else None,
            "coaching": coaching.to_dict() if coaching else None,
            "observation": observation.to_dict() if observation else None
        }

    def _create_work_request(
        self,
        title: str,
        description: str,
        priority: int,
        category: str,
        tags: List[str]
    ) -> WorkRequest:
        """Create a work request"""
        request_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        request = WorkRequest(
            request_id=request_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            tags=tags
        )

        # Save request
        with open(self.requests_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(request.to_dict()) + '\n')

        logger.info(f"   📋 Created work request: {request_id}")
        return request

    def _delegate_work(self, request: WorkRequest) -> Delegation:
        try:
            """
            DELEGATE: Always delegate work to appropriate team/agent

            Never do work directly - always delegate.
            """
            logger.info("=" * 80)
            logger.info("🎯 PHASE 1: DELEGATE")
            logger.info("=" * 80)
            logger.info("   Jedi Master Philosophy: Always delegate, never do work directly")

            # Determine delegation target
            delegation_target = self._determine_delegation_target(request)

            delegation_id = f"del_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            delegation = Delegation(
                delegation_id=delegation_id,
                request_id=request.request_id,
                delegated_to=delegation_target["target_id"],
                delegated_to_type=delegation_target["target_type"],
                delegation_reason=delegation_target["reason"],
                status=DelegationStatus.DELEGATED
            )

            # Perform actual delegation
            if delegation_target["target_type"] == "team":
                self._delegate_to_team(delegation, request)
            elif delegation_target["target_type"] == "agent":
                self._delegate_to_agent(delegation, request)
            elif delegation_target["target_type"] == "subagent":
                self._delegate_to_subagent(delegation, request)
            else:
                logger.warning(f"   ⚠️  Unknown delegation target type: {delegation_target['target_type']}")

            # Save delegation
            with open(self.delegations_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(delegation.to_dict()) + '\n')

            logger.info(f"   ✅ Delegated to: {delegation_target['target_id']} ({delegation_target['target_type']})")
            logger.info(f"   Reason: {delegation_target['reason']}")

            return delegation

        except Exception as e:
            self.logger.error(f"Error in _delegate_work: {e}", exc_info=True)
            raise
    def _determine_delegation_target(self, request: WorkRequest) -> Dict[str, Any]:
        """Determine appropriate delegation target"""
        # Check if it's a helpdesk ticket
        if "helpdesk" in request.category.lower() or "ticket" in request.tags:
            if self.ticket_assigner:
                # Use ticket assigner to route to team
                # This is a simplified version - actual implementation would use ticket system
                return {
                    "target_id": "NETWORK_TEAM",  # Example
                    "target_type": "team",
                    "reason": "Helpdesk ticket routed to appropriate team"
                }

        # Check if it's a code quality task
        if "code" in request.category.lower() or "quality" in request.tags:
            if self.delegation_system:
                return {
                    "target_id": "qa_agent",
                    "target_type": "agent",
                    "reason": "Code quality task delegated to QA agent"
                }

        # Check if it's a subagent domain task
        if self.subagent_delegation:
            # Determine subagent domain from request
            domain = self._determine_subagent_domain(request)
            if domain:
                return {
                    "target_id": domain,
                    "target_type": "subagent",
                    "reason": f"Task delegated to {domain} subagent"
                }

        # Default: delegate to general agent
        return {
            "target_id": "discovery_agent",
            "target_type": "agent",
            "reason": "General task delegated to discovery agent"
        }

    def _determine_subagent_domain(self, request: WorkRequest) -> Optional[str]:
        """Determine subagent domain from request"""
        # This is simplified - actual implementation would analyze request content
        if "illumination" in request.description.lower():
            return "illumination"
        elif "multimedia" in request.description.lower():
            return "multimedia"
        elif "storytelling" in request.description.lower():
            return "storytelling"
        return None

    def _delegate_to_team(self, delegation: Delegation, request: WorkRequest):
        """Delegate to a team"""
        logger.info(f"   👥 Delegating to team: {delegation.delegated_to}")
        # Actual delegation would use ticket system or team management
        delegation.started_at = datetime.now().isoformat()

    def _delegate_to_agent(self, delegation: Delegation, request: WorkRequest):
        """Delegate to an agent"""
        logger.info(f"   🤖 Delegating to agent: {delegation.delegated_to}")
        if self.delegation_system:
            # Create task in delegation system
            task_id = self.delegation_system.create_task(
                title=request.title,
                description=request.description,
                agent_type=self._map_category_to_agent_type(request.category),
                priority=request.priority
            )
            delegation.started_at = datetime.now().isoformat()
            delegation.status = DelegationStatus.IN_PROGRESS

    def _delegate_to_subagent(self, delegation: Delegation, request: WorkRequest):
        """Delegate to a subagent"""
        logger.info(f"   🔀 Delegating to subagent: {delegation.delegated_to}")
        if self.subagent_delegation:
            task = {
                "task_id": delegation.delegation_id,
                "title": request.title,
                "description": request.description,
                "priority": request.priority
            }
            # Delegate to subagent
            result = self.subagent_delegation.delegate_task(task)
            delegation.started_at = datetime.now().isoformat()
            delegation.status = DelegationStatus.IN_PROGRESS

    def _map_category_to_agent_type(self, category: str):
        """Map category to agent type"""
        from jarvis_delegation_system import AgentType
        mapping = {
            "discovery": AgentType.DISCOVERY,
            "performance": AgentType.PERFORMANCE,
            "qa": AgentType.QA,
            "optimization": AgentType.OPTIMIZATION,
            "testing": AgentType.TESTING,
            "validation": AgentType.VALIDATION
        }
        return mapping.get(category.lower(), AgentType.DISCOVERY)

    def _supervise_delegation(self, delegation: Delegation) -> SupervisionRecord:
        try:
            """
            SUPERVISE: Actively supervise delegated work
            """
            logger.info("=" * 80)
            logger.info("👔 PHASE 2: SUPERVISE")
            logger.info("=" * 80)
            logger.info("   Active supervision of delegated work")

            supervision_id = f"sup_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            # Check delegation status
            observation = f"Delegation {delegation.delegation_id} is {delegation.status.value}"

            # Use management supervision if available
            if self.management_supervision:
                # Supervise SLAs and tickets
                sla_supervision = self.management_supervision.supervise_slas()
                ticket_supervision = self.management_supervision.supervise_tickets()

                observation += f"\nSLA Supervision: {len(sla_supervision.get('actions_required', []))} actions required"
                observation += f"\nTicket Supervision: {len(ticket_supervision.get('stale_tickets', []))} stale tickets"

            supervision = SupervisionRecord(
                supervision_id=supervision_id,
                delegation_id=delegation.delegation_id,
                phase=WorkflowPhase.SUPERVISE,
                observation=observation
            )

            # Save supervision
            with open(self.supervision_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(supervision.to_dict()) + '\n')

            logger.info(f"   ✅ Supervision recorded: {supervision_id}")

            return supervision

        except Exception as e:
            self.logger.error(f"Error in _supervise_delegation: {e}", exc_info=True)
            raise
    def _manage_workflow(self, delegation: Delegation) -> Dict[str, Any]:
        """
        MANAGE: Manage the workflow and teams
        """
        logger.info("=" * 80)
        logger.info("📊 PHASE 3: MANAGE")
        logger.info("=" * 80)
        logger.info("   Managing workflow and teams")

        # Use team management if available
        if self.team_management:
            # Get team status
            # This would use actual team management methods
            pass

        return {
            "managed": True,
            "delegation_id": delegation.delegation_id,
            "timestamp": datetime.now().isoformat()
        }

    def _coach_if_needed(
        self,
        delegation: Delegation,
        supervision: SupervisionRecord
    ) -> Optional[Dict[str, Any]]:
        """
        COACH: Coach teams/agents when needed
        """
        logger.info("=" * 80)
        logger.info("🎓 PHASE 4: COACH")
        logger.info("=" * 80)

        # Check if coaching is needed
        needs_coaching = self._assess_coaching_needs(delegation, supervision)

        if not needs_coaching:
            logger.info("   ✅ No coaching needed")
            return None

        logger.info("   🎓 Coaching provided")

        coaching = {
            "coaching_id": f"coach_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "delegation_id": delegation.delegation_id,
            "coaching_type": "guidance",
            "coaching_provided": True,
            "timestamp": datetime.now().isoformat()
        }

        # Save coaching
        with open(self.coaching_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(coaching) + '\n')

        return coaching

    def _assess_coaching_needs(
        self,
        delegation: Delegation,
        supervision: SupervisionRecord
    ) -> bool:
        """Assess if coaching is needed"""
        # Coaching needed if:
        # - Delegation failed
        # - Supervision indicates issues
        # - Status is blocked
        if delegation.status == DelegationStatus.FAILED:
            return True
        if "blocked" in supervision.observation.lower():
            return True
        if delegation.status == DelegationStatus.REQUIRES_COACHING:
            return True
        return False

    def _observe_outcomes(
        self,
        delegation: Delegation,
        supervision: SupervisionRecord,
        coaching: Optional[Dict[str, Any]]
    ) -> ObservationRecord:
        """
        OBSERVE: Observe outcomes and learn
        """
        logger.info("=" * 80)
        logger.info("👁️  PHASE 5: OBSERVE")
        logger.info("=" * 80)
        logger.info("   Observing outcomes and learning")

        observation_id = f"obs_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # Determine observation type
        if delegation.status == DelegationStatus.COMPLETED:
            observation_type = "success"
            observation = f"Delegation {delegation.delegation_id} completed successfully"
            insights = ["Delegation workflow successful", "Team/agent performed well"]
        elif delegation.status == DelegationStatus.FAILED:
            observation_type = "failure"
            observation = f"Delegation {delegation.delegation_id} failed: {delegation.error}"
            insights = ["Delegation workflow needs improvement", "Team/agent needs support"]
        else:
            observation_type = "pattern"
            observation = f"Delegation {delegation.delegation_id} in progress"
            insights = ["Monitoring delegation progress"]

        # Extract lessons learned
        lessons_learned = []
        if coaching:
            lessons_learned.append("Coaching was provided and may have helped")
        if delegation.status == DelegationStatus.COMPLETED:
            lessons_learned.append("Delegation target was appropriate")

        observation_record = ObservationRecord(
            observation_id=observation_id,
            delegation_id=delegation.delegation_id,
            observation_type=observation_type,
            observation=observation,
            insights=insights,
            lessons_learned=lessons_learned
        )

        # Save observation
        with open(self.observations_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(observation_record.to_dict()) + '\n')

        logger.info(f"   ✅ Observation recorded: {observation_id}")

        return observation_record

    def get_workflow_status(self) -> Dict[str, Any]:
        try:
            """Get workflow status"""
            # Count requests, delegations, etc.
            requests_count = sum(1 for _ in open(self.requests_file) if self.requests_file.exists())
            delegations_count = sum(1 for _ in open(self.delegations_file) if self.delegations_file.exists())

            return {
                "timestamp": datetime.now().isoformat(),
                "total_requests": requests_count,
                "total_delegations": delegations_count,
                "workflow_active": True,
                "philosophy": "Always delegate, supervise, manage, coach, observe"
            }


        except Exception as e:
            self.logger.error(f"Error in get_workflow_status: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Jedi Master Delegation Workflow")
        parser.add_argument("--delegate", nargs=4, metavar=("TITLE", "DESCRIPTION", "PRIORITY", "CATEGORY"),
                           help="Delegate a work request")
        parser.add_argument("--status", action="store_true", help="Get workflow status")

        args = parser.parse_args()

        workflow = JARVISJediMasterDelegationWorkflow()

        if args.delegate:
            title, description, priority, category = args.delegate
            result = workflow.process_work_request(
                title=title,
                description=description,
                priority=int(priority),
                category=category
            )
            print(json.dumps(result, indent=2, default=str))

        elif args.status:
            status = workflow.get_workflow_status()
            print(json.dumps(status, indent=2, default=str))

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()