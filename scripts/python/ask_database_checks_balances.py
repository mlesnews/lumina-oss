#!/usr/bin/env python3
"""
@ask Database with US Government-Style Checks and Balances
<COMPANY_NAME> LLC

Maintains an "@ask" database with separation of powers:
- Executive Branch: Executes asks, implements changes
- Legislative Branch: Creates/modifies asks, approves changes
- Judicial Branch: Reviews asks, validates compliance, resolves conflicts

Integrated with:
- Master Blueprint evaluation and maintenance
- Master/Padawan ToDoLists (concurrent maintenance)

@JARVIS @MARVIN @SYPHON @R5 @BLUEPRINT
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AskDatabaseChecksBalances")


class AskStatus(Enum):
    """Status of an ask"""
    DRAFT = "draft"  # Created but not submitted
    SUBMITTED = "submitted"  # Submitted to Legislative
    IN_REVIEW = "in_review"  # Under Legislative review
    APPROVED = "approved"  # Approved by Legislative
    REJECTED = "rejected"  # Rejected by Legislative
    IN_EXECUTION = "in_execution"  # Being executed by Executive
    EXECUTED = "executed"  # Completed by Executive
    UNDER_REVIEW = "under_review"  # Under Judicial review
    VALIDATED = "validated"  # Validated by Judicial
    INVALIDATED = "invalidated"  # Invalidated by Judicial
    CONFLICT = "conflict"  # Conflict detected, needs resolution
    RESOLVED = "resolved"  # Conflict resolved


class Branch(Enum):
    """Government branches"""
    EXECUTIVE = "executive"  # Executes asks
    LEGISLATIVE = "legislative"  # Creates/approves asks
    JUDICIAL = "judicial"  # Reviews/validates asks


class Priority(Enum):
    """Priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Ask:
    """An @ask entry"""
    ask_id: str
    ask_text: str
    submitted_by: str = "user"
    submitted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: AskStatus = AskStatus.DRAFT
    priority: Priority = Priority.MEDIUM
    branch: Branch = Branch.LEGISLATIVE

    # Legislative fields
    legislative_reviewer: Optional[str] = None
    legislative_notes: List[str] = field(default_factory=list)
    approved_at: Optional[str] = None
    rejected_reason: Optional[str] = None

    # Executive fields
    executive_assignee: Optional[str] = None
    execution_plan: Optional[str] = None
    execution_started_at: Optional[str] = None
    execution_completed_at: Optional[str] = None
    execution_result: Optional[str] = None

    # Judicial fields
    judicial_reviewer: Optional[str] = None
    judicial_notes: List[str] = field(default_factory=list)
    blueprint_compliance: Optional[bool] = None
    blueprint_notes: List[str] = field(default_factory=list)
    validation_result: Optional[str] = None
    validated_at: Optional[str] = None

    # Blueprint integration
    blueprint_impact: List[str] = field(default_factory=list)
    blueprint_changes_required: List[str] = field(default_factory=list)

    # Todo integration  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
    master_todo_id: Optional[str] = None
    padawan_todo_id: Optional[str] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    related_asks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['branch'] = self.branch.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ask':
        """Create Ask from dictionary"""
        data['status'] = AskStatus(data['status'])
        data['priority'] = Priority(data['priority'])
        data['branch'] = Branch(data['branch'])
        return cls(**data)


@dataclass
class ChecksAndBalances:
    """Checks and balances system"""
    ask_id: str
    executive_check: bool = False
    legislative_check: bool = False
    judicial_check: bool = False
    blueprint_check: bool = False
    todo_check: bool = False

    executive_notes: List[str] = field(default_factory=list)
    legislative_notes: List[str] = field(default_factory=list)
    judicial_notes: List[str] = field(default_factory=list)
    blueprint_notes: List[str] = field(default_factory=list)
    todo_notes: List[str] = field(default_factory=list)

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def all_checks_passed(self) -> bool:
        """Check if all checks passed"""
        return (self.executive_check and 
                self.legislative_check and 
                self.judicial_check and 
                self.blueprint_check and 
                self.todo_check)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MasterPadawanTodo:
    """Master/Padawan todo entry"""
    todo_id: str
    ask_id: str
    master_todo: str
    padawan_todo: str
    master_status: str = "pending"
    padawan_status: str = "pending"
    master_assignee: Optional[str] = None
    padawan_assignee: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AskDatabase:
    """
    @ask Database with US Government-Style Checks and Balances

    Separation of Powers:
    - Executive: Executes approved asks
    - Legislative: Creates and approves asks
    - Judicial: Reviews and validates asks
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("AskDatabase")

        # Data directories
        self.data_dir = self.project_root / "data" / "ask_database"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.asks_file = self.data_dir / "asks.json"
        self.checks_file = self.data_dir / "checks_balances.json"
        self.todos_file = self.data_dir / "master_padawan_todos.json"

        # Load existing data
        self.asks: Dict[str, Ask] = {}
        self.checks: Dict[str, ChecksAndBalances] = {}
        self.todos: Dict[str, MasterPadawanTodo] = {}

        self._load_data()

    def _load_data(self):
        """Load existing data"""
        # Load asks
        if self.asks_file.exists():
            try:
                with open(self.asks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.asks = {ask_id: Ask.from_dict(ask_data) 
                                for ask_id, ask_data in data.items()}
            except Exception as e:
                self.logger.error(f"Could not load asks: {e}")

        # Load checks
        if self.checks_file.exists():
            try:
                with open(self.checks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.checks = {ask_id: ChecksAndBalances(**check_data)
                                  for ask_id, check_data in data.items()}
            except Exception as e:
                self.logger.error(f"Could not load checks: {e}")

        # Load todos
        if self.todos_file.exists():
            try:
                with open(self.todos_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.todos = {todo_id: MasterPadawanTodo(**todo_data)
                                 for todo_id, todo_data in data.items()}
            except Exception as e:
                self.logger.error(f"Could not load todos: {e}")

    def _save_data(self):
        """Save all data"""
        # Save asks
        try:
            with open(self.asks_file, 'w', encoding='utf-8') as f:
                json.dump({ask_id: ask.to_dict() 
                          for ask_id, ask in self.asks.items()}, 
                         f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Could not save asks: {e}")

        # Save checks
        try:
            with open(self.checks_file, 'w', encoding='utf-8') as f:
                json.dump({ask_id: check.to_dict() 
                          for ask_id, check in self.checks.items()}, 
                         f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Could not save checks: {e}")

        # Save todos
        try:
            with open(self.todos_file, 'w', encoding='utf-8') as f:
                json.dump({todo_id: todo.to_dict() 
                          for todo_id, todo in self.todos.items()}, 
                         f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Could not save todos: {e}")

    def create_ask(self, ask_text: str, priority: Priority = Priority.MEDIUM,
                   submitted_by: str = "user", tags: List[str] = None) -> Ask:
        """
        LEGISLATIVE: Create a new ask

        Creates an ask in DRAFT status, ready for Legislative review
        """
        ask_id = f"ask_{hashlib.md5(ask_text.encode()).hexdigest()[:12]}_{int(datetime.now().timestamp())}"

        ask = Ask(
            ask_id=ask_id,
            ask_text=ask_text,
            submitted_by=submitted_by,
            status=AskStatus.DRAFT,
            priority=priority,
            branch=Branch.LEGISLATIVE,
            tags=tags or []
        )

        self.asks[ask_id] = ask
        self._save_data()

        self.logger.info(f"✅ Created ask: {ask_id}")
        return ask

    def submit_ask(self, ask_id: str, reviewer: str = "legislative") -> bool:
        """
        LEGISLATIVE: Submit ask for review

        Moves ask from DRAFT to SUBMITTED status
        """
        if ask_id not in self.asks:
            self.logger.error(f"Ask not found: {ask_id}")
            return False

        ask = self.asks[ask_id]
        if ask.status != AskStatus.DRAFT:
            self.logger.error(f"Ask not in DRAFT status: {ask_id}")
            return False

        ask.status = AskStatus.SUBMITTED
        ask.legislative_reviewer = reviewer
        self._save_data()

        self.logger.info(f"✅ Submitted ask: {ask_id}")
        return True

    def review_ask(self, ask_id: str, reviewer: str, approve: bool,
                   notes: List[str] = None, reason: Optional[str] = None) -> bool:
        """
        LEGISLATIVE: Review and approve/reject ask

        Moves ask to APPROVED or REJECTED status
        """
        if ask_id not in self.asks:
            self.logger.error(f"Ask not found: {ask_id}")
            return False

        ask = self.asks[ask_id]
        if ask.status not in [AskStatus.SUBMITTED, AskStatus.IN_REVIEW]:
            self.logger.error(f"Ask not ready for review: {ask_id}")
            return False

        ask.legislative_reviewer = reviewer
        if notes:
            ask.legislative_notes.extend(notes)

        if approve:
            ask.status = AskStatus.APPROVED
            ask.approved_at = datetime.now().isoformat()
            ask.branch = Branch.EXECUTIVE  # Move to Executive
            self.logger.info(f"✅ Approved ask: {ask_id}")
        else:
            ask.status = AskStatus.REJECTED
            ask.rejected_reason = reason or "Rejected by Legislative review"
            self.logger.info(f"❌ Rejected ask: {ask_id}")

        self._save_data()
        return True

    def execute_ask(self, ask_id: str, assignee: str, execution_plan: str) -> bool:
        """
        EXECUTIVE: Execute an approved ask

        Moves ask to IN_EXECUTION status
        """
        if ask_id not in self.asks:
            self.logger.error(f"Ask not found: {ask_id}")
            return False

        ask = self.asks[ask_id]
        if ask.status != AskStatus.APPROVED:
            self.logger.error(f"Ask not approved: {ask_id}")
            return False

        ask.status = AskStatus.IN_EXECUTION
        ask.executive_assignee = assignee
        ask.execution_plan = execution_plan
        ask.execution_started_at = datetime.now().isoformat()
        ask.branch = Branch.EXECUTIVE
        self._save_data()

        self.logger.info(f"✅ Executing ask: {ask_id}")
        return True

    def complete_execution(self, ask_id: str, result: str) -> bool:
        """
        EXECUTIVE: Complete execution of ask

        Moves ask to EXECUTED status, ready for Judicial review
        """
        if ask_id not in self.asks:
            self.logger.error(f"Ask not found: {ask_id}")
            return False

        ask = self.asks[ask_id]
        if ask.status != AskStatus.IN_EXECUTION:
            self.logger.error(f"Ask not in execution: {ask_id}")
            return False

        ask.status = AskStatus.EXECUTED
        ask.execution_result = result
        ask.execution_completed_at = datetime.now().isoformat()
        ask.branch = Branch.JUDICIAL  # Move to Judicial
        self._save_data()

        self.logger.info(f"✅ Completed execution: {ask_id}")
        return True

    def validate_ask(self, ask_id: str, reviewer: str, 
                    blueprint_compliance: bool, validation_result: str,
                    notes: List[str] = None) -> bool:
        """
        JUDICIAL: Validate executed ask

        Reviews execution and validates compliance with blueprint
        """
        if ask_id not in self.asks:
            self.logger.error(f"Ask not found: {ask_id}")
            return False

        ask = self.asks[ask_id]
        if ask.status != AskStatus.EXECUTED:
            self.logger.error(f"Ask not executed: {ask_id}")
            return False

        ask.judicial_reviewer = reviewer
        ask.blueprint_compliance = blueprint_compliance
        ask.validation_result = validation_result
        if notes:
            ask.judicial_notes.extend(notes)

        if blueprint_compliance:
            ask.status = AskStatus.VALIDATED
            ask.validated_at = datetime.now().isoformat()
            self.logger.info(f"✅ Validated ask: {ask_id}")
        else:
            ask.status = AskStatus.INVALIDATED
            self.logger.warning(f"⚠️ Invalidated ask: {ask_id}")

        self._save_data()
        return True

    def evaluate_blueprint_impact(self, ask_id: str) -> Dict[str, Any]:
        """
        Evaluate impact of ask on master blueprint

        Returns blueprint changes required
        """
        if ask_id not in self.asks:
            return {}

        ask = self.asks[ask_id]

        # Import blueprint evaluator
        try:
            from living_blueprint_sync import LivingBlueprintSync
            blueprint_sync = LivingBlueprintSync(self.project_root)

            # Evaluate impact
            impact = blueprint_sync.evaluate_ask_impact(ask.ask_text)

            ask.blueprint_impact = impact.get('impact_areas', [])
            ask.blueprint_changes_required = impact.get('changes_required', [])
            ask.blueprint_notes = impact.get('notes', [])

            self._save_data()
            return impact
        except Exception as e:
            self.logger.error(f"Could not evaluate blueprint impact: {e}")
            return {}

    def create_master_padawan_todos(self, ask_id: str, 
                                   master_todo: str, padawan_todo: str) -> MasterPadawanTodo:
        """
        Create Master/Padawan todo entries for an ask
        """
        if ask_id not in self.asks:
            raise ValueError(f"Ask not found: {ask_id}")

        todo_id = f"todo_{ask_id}_{int(datetime.now().timestamp())}"

        todo = MasterPadawanTodo(
            todo_id=todo_id,
            ask_id=ask_id,
            master_todo=master_todo,
            padawan_todo=padawan_todo
        )

        self.todos[todo_id] = todo

        # Link to ask
        ask = self.asks[ask_id]
        ask.master_todo_id = todo_id
        ask.padawan_todo_id = todo_id

        self._save_data()
        self.logger.info(f"✅ Created Master/Padawan todos: {todo_id}")
        return todo

    def update_checks_balances(self, ask_id: str) -> ChecksAndBalances:
        """
        Update checks and balances for an ask

        Verifies all branches have completed their checks
        """
        if ask_id not in self.asks:
            raise ValueError(f"Ask not found: {ask_id}")

        ask = self.asks[ask_id]

        # Initialize or get existing checks
        if ask_id not in self.checks:
            self.checks[ask_id] = ChecksAndBalances(ask_id=ask_id)

        checks = self.checks[ask_id]

        # Executive check
        checks.executive_check = ask.status in [
            AskStatus.EXECUTED, AskStatus.VALIDATED, AskStatus.INVALIDATED
        ]
        if checks.executive_check:
            checks.executive_notes.append(f"Execution completed: {ask.execution_result}")

        # Legislative check
        checks.legislative_check = ask.status in [
            AskStatus.APPROVED, AskStatus.REJECTED, AskStatus.EXECUTED,
            AskStatus.VALIDATED, AskStatus.INVALIDATED
        ]
        if checks.legislative_check:
            checks.legislative_notes.append(f"Legislative review completed: {ask.status.value}")

        # Judicial check
        checks.judicial_check = ask.status in [
            AskStatus.VALIDATED, AskStatus.INVALIDATED
        ]
        if checks.judicial_check:
            checks.judicial_notes.append(f"Judicial validation: {ask.validation_result}")

        # Blueprint check
        checks.blueprint_check = ask.blueprint_compliance is not None
        if checks.blueprint_check:
            checks.blueprint_notes = ask.blueprint_notes

        # Todo check  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        checks.todo_check = ask.master_todo_id is not None and ask.padawan_todo_id is not None
        if checks.todo_check:
            checks.todo_notes.append(f"Master/Padawan todos created: {ask.master_todo_id}")

        checks.timestamp = datetime.now().isoformat()
        self._save_data()

        return checks

    def get_ask(self, ask_id: str) -> Optional[Ask]:
        """Get an ask by ID"""
        return self.asks.get(ask_id)

    def list_asks(self, status: Optional[AskStatus] = None,
                  branch: Optional[Branch] = None,
                  priority: Optional[Priority] = None) -> List[Ask]:
        """List asks with optional filters"""
        asks = list(self.asks.values())

        if status:
            asks = [a for a in asks if a.status == status]
        if branch:
            asks = [a for a in asks if a.branch == branch]
        if priority:
            asks = [a for a in asks if a.priority == priority]

        return asks

    def get_checks_balances(self, ask_id: str) -> Optional[ChecksAndBalances]:
        """Get checks and balances for an ask"""
        return self.checks.get(ask_id)


def main():
    try:
        """Main function - demonstrate the system"""
        print("=" * 80)
        print("@ASK DATABASE - US GOVERNMENT CHECKS & BALANCES")
        print("=" * 80)
        print()

        project_root = Path(__file__).parent.parent.parent
        db = AskDatabase(project_root)

        # Example: Create an ask
        ask = db.create_ask(
            "Implement comprehensive system audit with Marvin roast",
            priority=Priority.HIGH,
            tags=["audit", "marvin", "system"]
        )

        print(f"Created ask: {ask.ask_id}")
        print(f"Status: {ask.status.value}")
        print(f"Branch: {ask.branch.value}")
        print()

        # Submit for review
        db.submit_ask(ask.ask_id)
        print(f"Submitted ask: {ask.ask_id}")
        print()

        # Legislative review and approval
        db.review_ask(ask.ask_id, "legislative_reviewer", approve=True,
                     notes=["Approved for execution"])
        print(f"Approved ask: {ask.ask_id}")
        print()

        # Executive execution
        db.execute_ask(ask.ask_id, "executive_agent", 
                      "Execute comprehensive system audit using Marvin")
        print(f"Executing ask: {ask.ask_id}")
        print()

        # Complete execution
        db.complete_execution(ask.ask_id, "Marvin roast completed successfully")
        print(f"Completed execution: {ask.ask_id}")
        print()

        # Judicial validation
        db.validate_ask(ask.ask_id, "judicial_reviewer", 
                       blueprint_compliance=True,
                       validation_result="Execution validated, blueprint compliant",
                       notes=["All checks passed"])
        print(f"Validated ask: {ask.ask_id}")
        print()

        # Update checks and balances
        checks = db.update_checks_balances(ask.ask_id)
        print(f"Checks and Balances:")
        print(f"  Executive: {checks.executive_check}")
        print(f"  Legislative: {checks.legislative_check}")
        print(f"  Judicial: {checks.judicial_check}")
        print(f"  Blueprint: {checks.blueprint_check}")
        print(f"  Todos: {checks.todo_check}")
        print(f"  All Passed: {checks.all_checks_passed()}")
        print()

        print("=" * 80)
        print("SYSTEM READY")
        print("=" * 80)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())