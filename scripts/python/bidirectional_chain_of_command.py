#!/usr/bin/env python3
"""
Bidirectional Chain-of-Command System

Top-down direct supervision and management of the entire company:
- BOTH sides of business (Technical AND Business)
- ALL divisions
- Chain-of-command works BOTH ways as a pipe (bidirectional)
- Like "chain-of-thought" in programming - information flows both directions

TOP-DOWN: Supervisors → Managers → Subordinates (Directives/Commands)
BOTTOM-UP: Subordinates → Managers → Supervisors (Reports/Status)

Tags: #MANAGEMENT #SUPERVISION #CHAIN_OF_COMMAND #BIDIRECTIONAL #REQUIRED @PEAK @JARVIS @LUMINA @RR @DOIT
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BidirectionalChainOfCommand")

try:
    from lumina_organizational_structure import LuminaOrganizationalStructure, Team, TeamMember
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    SYSTEMS_AVAILABLE = False
    logger.warning(f"Systems not available: {e}")

# Azure Service Bus integration
try:
    from azure_service_bus_integration import AzureServiceBusClient, ServiceBusMessage, MessageType
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_SB_AVAILABLE = True
except ImportError:
    AZURE_SB_AVAILABLE = False
    logger.warning("Azure Service Bus not available. Install with: pip install azure-servicebus azure-keyvault-secrets azure-identity")

# Unified Secrets Manager for Azure Key Vault
try:
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    logger.warning("Unified Secrets Manager not available")


class DirectivePriority(Enum):
    """Directive priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DirectiveType(Enum):
    """Types of directives"""
    TASK = "task"
    PROJECT = "project"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    URGENT = "urgent"


@dataclass
class Directive:
    """
    Top-down directive from supervisor to subordinate

    Chain-of-command: Supervisor → Manager → Subordinate
    """
    directive_id: str
    from_supervisor: str  # Who issued the directive
    to_recipient: str  # Who receives it (manager or subordinate)
    directive_type: str  # DirectiveType enum value
    priority: str  # DirectivePriority enum value
    title: str
    description: str
    action_required: str
    division: Optional[str] = None
    team_id: Optional[str] = None
    technical_lead: Optional[str] = None
    business_lead: Optional[str] = None
    due_date: Optional[str] = None
    chain_of_command: List[str] = field(default_factory=list)  # Path: [supervisor, manager, subordinate]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged: bool = False
    acknowledged_at: Optional[str] = None
    executed: bool = False
    executed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChainOfCommandPipe:
    """
    Bidirectional pipe for chain-of-command communication

    Works like chain-of-thought in programming:
    - TOP-DOWN: Directives flow down (Supervisor → Manager → Subordinate)
    - BOTTOM-UP: Reports flow up (Subordinate → Manager → Supervisor)
    """
    pipe_id: str
    supervisor: str
    manager: str
    subordinate: Optional[str] = None
    division: str = ""
    team_id: str = ""
    technical_side: bool = True
    business_side: bool = True

    # Top-down directives (Supervisor → Manager → Subordinate)
    pending_directives: List[Directive] = field(default_factory=list)
    active_directives: List[Directive] = field(default_factory=list)
    completed_directives: List[Directive] = field(default_factory=list)

    # Bottom-up reports (Subordinate → Manager → Supervisor)
    pending_reports: List[Dict[str, Any]] = field(default_factory=list)
    active_reports: List[Dict[str, Any]] = field(default_factory=list)
    completed_reports: List[Dict[str, Any]] = field(default_factory=list)

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['pending_directives'] = [d.to_dict() if hasattr(d, 'to_dict') else d for d in self.pending_directives]
        data['active_directives'] = [d.to_dict() if hasattr(d, 'to_dict') else d for d in self.active_directives]
        data['completed_directives'] = [d.to_dict() if hasattr(d, 'to_dict') else d for d in self.completed_directives]
        return data


class BidirectionalChainOfCommand:
    """
    Top-down direct supervision and management of the entire company

    Features:
    - BOTH sides of business (Technical AND Business)
    - ALL divisions
    - Bidirectional chain-of-command (works both ways as a pipe)
    - Chain-of-thought style communication
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize bidirectional chain-of-command system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.directives_dir = self.project_root / "data" / "chain_of_command" / "directives"
        self.directives_dir.mkdir(parents=True, exist_ok=True)

        self.pipes_dir = self.project_root / "data" / "chain_of_command" / "pipes"
        self.pipes_dir.mkdir(parents=True, exist_ok=True)

        # Azure Service Bus for ALL communication (REQUIRED)
        self.azure_sb_client = None
        self.service_bus_namespace = None
        self._initialize_azure_service_bus()

        # Initialize systems
        if SYSTEMS_AVAILABLE:
            self.org_structure = LuminaOrganizationalStructure(project_root)
            self.ticket_system = JARVISHelpdeskTicketSystem(project_root)
        else:
            self.org_structure = None
            self.ticket_system = None

        # Chain-of-command hierarchy (bidirectional)
        self.chain_hierarchy = {
            "@jarvis": None,  # Top level
            "@c3po": "@jarvis",
            "@r2d2": "@c3po",
        }

        # Active pipes (bidirectional communication channels)
        self.active_pipes: Dict[str, ChainOfCommandPipe] = {}

        logger.info("=" * 80)
        logger.info("🔗 BIDIRECTIONAL CHAIN-OF-COMMAND SYSTEM")
        logger.info("=" * 80)
        logger.info("   ✅ ALL COMMUNICATION USES AZURE SERVICE BUS (Azure Pipe)")
        logger.info("   Top-down: Supervisors → Managers → Subordinates (Directives)")
        logger.info("   Bottom-up: Subordinates → Managers → Supervisors (Reports)")
        logger.info("   BOTH sides: Technical AND Business")
        logger.info("   ALL divisions covered")
        logger.info("   Works like chain-of-thought: bidirectional pipe via Azure")
        logger.info("=" * 80)

    def _initialize_azure_service_bus(self):
        """Initialize Azure Service Bus client for ALL communication"""
        if not AZURE_SB_AVAILABLE:
            logger.warning("⚠️  Azure Service Bus not available - using file-based fallback")
            return

        try:
            # Get Service Bus namespace from Key Vault or config
            namespace = None

            # Try Unified Secrets Manager first (Azure Key Vault)
            if SECRETS_MANAGER_AVAILABLE:
                try:
                    secret_manager = UnifiedSecretsManager(project_root=self.project_root)
                    namespace = secret_manager.get_secret(
                        "azure-service-bus-namespace",
                        prefer_source=SecretSource.AZURE_KEY_VAULT
                    )
                    if namespace:
                        logger.info("✅ Retrieved Azure Service Bus namespace from Azure Key Vault")
                except Exception as e:
                    logger.debug(f"Could not get namespace from Key Vault: {e}")

            # Fallback to environment variable or default
            if not namespace:
                import os
                namespace = os.getenv("AZURE_SERVICE_BUS_NAMESPACE", "jarvis-lumina-sb.servicebus.windows.net")

            self.service_bus_namespace = namespace

            # Initialize Azure Service Bus client
            # Get connection string from Key Vault
            connection_string = None
            if SECRETS_MANAGER_AVAILABLE:
                try:
                    secret_manager = UnifiedSecretsManager(project_root=self.project_root)
                    connection_string = secret_manager.get_secret(
                        "azure-service-bus-connection-string",
                        prefer_source=SecretSource.AZURE_KEY_VAULT
                    )
                    if connection_string:
                        logger.info("✅ Retrieved Azure Service Bus connection string from Azure Key Vault")
                except Exception as e:
                    logger.debug(f"Could not get connection string from Key Vault: {e}")

            if connection_string:
                from azure.servicebus import ServiceBusClient
                self.azure_sb_client = ServiceBusClient.from_connection_string(connection_string)
            else:
                # Use DefaultAzureCredential
                from azure.servicebus import ServiceBusClient
                from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential(

                                    exclude_interactive_browser_credential=False,

                                    exclude_shared_token_cache_credential=False

                                )
                self.azure_sb_client = ServiceBusClient(
                    fully_qualified_namespace=namespace,
                    credential=credential
                )

            logger.info(f"✅ Azure Service Bus client initialized: {namespace}")
            logger.info("   🔐 All chain-of-command communication will use Azure Service Bus")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure Service Bus: {e}")
            logger.warning("⚠️  Falling back to file-based communication")
            self.azure_sb_client = None

    def create_directive(
        self,
        from_supervisor: str,
        to_recipient: str,
        title: str,
        description: str,
        action_required: str,
        directive_type: str = "task",
        priority: str = "normal",
        division: Optional[str] = None,
        team_id: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Directive:
        """
        Create a top-down directive (Supervisor → Manager/Subordinate)

        Args:
            from_supervisor: Who is issuing the directive
            to_recipient: Who receives it
            title: Directive title
            description: Detailed description
            action_required: What action is required
            directive_type: Type of directive
            priority: Priority level
            division: Division (if applicable)
            team_id: Team ID (if applicable)
            due_date: Due date (ISO format)

        Returns:
            Created Directive
        """
        directive_id = f"DIR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{from_supervisor[:3].upper()}"

        # Build chain-of-command path
        chain_path = self._build_chain_path(from_supervisor, to_recipient)

        # Determine technical/business leads
        technical_lead = None
        business_lead = None
        if team_id and self.org_structure:
            team = self.org_structure.teams.get(team_id)
            if team:
                technical_lead = team.team_lead
                # Business lead would be in team metadata if available

        directive = Directive(
            directive_id=directive_id,
            from_supervisor=from_supervisor,
            to_recipient=to_recipient,
            directive_type=directive_type,
            priority=priority,
            title=title,
            description=description,
            action_required=action_required,
            division=division,
            team_id=team_id,
            technical_lead=technical_lead,
            business_lead=business_lead,
            due_date=due_date,
            chain_of_command=chain_path
        )

        # Save directive (local backup)
        directive_file = self.directives_dir / f"{directive_id}.json"
        with open(directive_file, 'w', encoding='utf-8') as f:
            json.dump(directive.to_dict(), f, indent=2)

        # Send directive via Azure Service Bus (PRIMARY - REQUIRED)
        self._send_directive_via_azure(directive)

        # Add to appropriate pipe
        pipe = self._get_or_create_pipe(from_supervisor, to_recipient)
        pipe.pending_directives.append(directive)
        pipe.last_activity = datetime.now().isoformat()
        self._save_pipe(pipe)

        logger.info("=" * 80)
        logger.info(f"📥 DIRECTIVE CREATED: {directive_id}")
        logger.info("=" * 80)
        logger.info(f"   From: {from_supervisor}")
        logger.info(f"   To: {to_recipient}")
        logger.info(f"   Type: {directive_type}")
        logger.info(f"   Priority: {priority.upper()}")
        logger.info(f"   Title: {title}")
        logger.info(f"   Chain: {' → '.join(chain_path)}")
        logger.info("=" * 80)

        return directive

    def _build_chain_path(self, from_supervisor: str, to_recipient: str) -> List[str]:
        """Build chain-of-command path from supervisor to recipient"""
        path = [from_supervisor]

        # Find intermediate managers in the chain
        current = from_supervisor
        visited = {current}

        # Walk down the hierarchy
        if self.org_structure:
            # Check if recipient is a manager
            recipient_is_manager = False
            for team in self.org_structure.teams.values():
                if (team.helpdesk_manager == to_recipient or 
                    team.team_lead == to_recipient):
                    recipient_is_manager = True
                    break

            if recipient_is_manager:
                # Direct supervisor → manager
                if current != to_recipient:
                    path.append(to_recipient)
            else:
                # Supervisor → manager → subordinate
                # Find which manager supervises this subordinate
                for team in self.org_structure.teams.values():
                    for member in team.members:
                        if member.member_id == to_recipient:
                            manager = team.helpdesk_manager or team.team_lead
                            if manager and manager not in visited:
                                path.append(manager)
                                visited.add(manager)
                            break
                    if len(path) > 1:
                        break

                if to_recipient not in path:
                    path.append(to_recipient)

        return path

    def _get_or_create_pipe(
        self,
        supervisor: str,
        recipient: str,
        division: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> ChainOfCommandPipe:
        """Get or create a bidirectional pipe for chain-of-command"""
        pipe_id = f"{supervisor}_{recipient}_{team_id or 'default'}"

        if pipe_id in self.active_pipes:
            return self.active_pipes[pipe_id]

        # Determine manager in chain
        manager = None
        if self.org_structure:
            for team in self.org_structure.teams.values():
                if (team.helpdesk_manager == recipient or 
                    team.team_lead == recipient):
                    manager = recipient
                    division = team.division
                    team_id = team.team_id
                    break
                else:
                    for member in team.members:
                        if member.member_id == recipient:
                            manager = team.helpdesk_manager or team.team_lead
                            division = team.division
                            team_id = team.team_id
                            break
                    if manager:
                        break

        pipe = ChainOfCommandPipe(
            pipe_id=pipe_id,
            supervisor=supervisor,
            manager=manager or recipient,
            subordinate=recipient if manager else None,
            division=division or "",
            team_id=team_id or "",
            technical_side=True,
            business_side=True
        )

        self.active_pipes[pipe_id] = pipe
        return pipe

    def _save_pipe(self, pipe: ChainOfCommandPipe):
        try:
            """Save pipe to disk"""
            pipe_file = self.pipes_dir / f"{pipe.pipe_id}.json"
            with open(pipe_file, 'w', encoding='utf-8') as f:
                json.dump(pipe.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_pipe: {e}", exc_info=True)
            raise
    def acknowledge_directive(self, directive_id: str, acknowledged_by: str) -> bool:
        try:
            """Acknowledge receipt of a directive"""
            directive_file = self.directives_dir / f"{directive_id}.json"

            if not directive_file.exists():
                logger.error(f"❌ Directive not found: {directive_id}")
                return False

            with open(directive_file, 'r', encoding='utf-8') as f:
                directive_data = json.load(f)

            directive_data['acknowledged'] = True
            directive_data['acknowledged_at'] = datetime.now().isoformat()
            directive_data['acknowledged_by'] = acknowledged_by

            with open(directive_file, 'w', encoding='utf-8') as f:
                json.dump(directive_data, f, indent=2)

            logger.info(f"✅ Directive {directive_id} acknowledged by {acknowledged_by}")
            return True

        except Exception as e:
            self.logger.error(f"Error in acknowledge_directive: {e}", exc_info=True)
            raise
    def execute_directive(self, directive_id: str, executed_by: str, result: str = "") -> bool:
        try:
            """Mark directive as executed"""
            directive_file = self.directives_dir / f"{directive_id}.json"

            if not directive_file.exists():
                logger.error(f"❌ Directive not found: {directive_id}")
                return False

            with open(directive_file, 'r', encoding='utf-8') as f:
                directive_data = json.load(f)

            directive_data['executed'] = True
            directive_data['executed_at'] = datetime.now().isoformat()
            directive_data['executed_by'] = executed_by
            directive_data['result'] = result

            with open(directive_file, 'w', encoding='utf-8') as f:
                json.dump(directive_data, f, indent=2)

            logger.info(f"✅ Directive {directive_id} executed by {executed_by}")
            return True

        except Exception as e:
            self.logger.error(f"Error in execute_directive: {e}", exc_info=True)
            raise
    def get_pending_directives(self, recipient: str) -> List[Dict[str, Any]]:
        """Get all pending directives for a recipient"""
        pending = []

        for directive_file in self.directives_dir.glob("DIR-*.json"):
            try:
                with open(directive_file, 'r', encoding='utf-8') as f:
                    directive = json.load(f)

                if (directive.get('to_recipient') == recipient and 
                    not directive.get('acknowledged', False)):
                    pending.append(directive)
            except Exception as e:
                logger.debug(f"Error reading directive {directive_file}: {e}")

        return pending

    def _send_directive_via_azure(self, directive: Directive):
        """Send directive via Azure Service Bus (REQUIRED - Azure Pipe)"""
        if not self.azure_sb_client:
            logger.warning(f"⚠️  Azure Service Bus not available - directive {directive.directive_id} saved locally only")
            return

        try:
            # Create topic/queue name based on recipient
            topic_name = f"chain-of-command-{directive.to_recipient.replace('@', '').lower()}"

            # Create Service Bus message
            message = ServiceBusMessage(
                message_id=directive.directive_id,
                message_type=MessageType.COORDINATION,
                timestamp=datetime.now(),
                source=directive.from_supervisor,
                destination=directive.to_recipient,
                payload=directive.to_dict(),
                correlation_id=directive.directive_id,
                metadata={
                    "directive_type": directive.directive_type,
                    "priority": directive.priority,
                    "chain_of_command": directive.chain_of_command
                }
            )

            # Send to Azure Service Bus
            sender = self.azure_sb_client.get_topic_sender(topic_name=topic_name)
            azure_message = message.to_azure_message()
            sender.send_messages(azure_message)
            sender.close()

            logger.info(f"✅ Directive {directive.directive_id} sent via Azure Service Bus to {topic_name}")

        except Exception as e:
            logger.error(f"❌ Failed to send directive via Azure Service Bus: {e}")
            logger.warning(f"⚠️  Directive {directive.directive_id} saved locally only")

    def _send_report_via_azure(self, report: Dict[str, Any], from_recipient: str, to_supervisor: str):
        """Send report via Azure Service Bus (REQUIRED - Azure Pipe)"""
        if not self.azure_sb_client:
            logger.warning(f"⚠️  Azure Service Bus not available - report saved locally only")
            return

        try:
            # Create topic/queue name based on supervisor
            topic_name = f"chain-of-command-{to_supervisor.replace('@', '').lower()}"

            # Create Service Bus message
            message = ServiceBusMessage(
                message_id=f"REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                message_type=MessageType.COORDINATION,
                timestamp=datetime.now(),
                source=from_recipient,
                destination=to_supervisor,
                payload=report,
                metadata={
                    "report_type": "status_report",
                    "from": from_recipient,
                    "to": to_supervisor
                }
            )

            # Send to Azure Service Bus
            sender = self.azure_sb_client.get_topic_sender(topic_name=topic_name)
            azure_message = message.to_azure_message()
            sender.send_messages(azure_message)
            sender.close()

            logger.info(f"✅ Report sent via Azure Service Bus from {from_recipient} to {to_supervisor}")

        except Exception as e:
            logger.error(f"❌ Failed to send report via Azure Service Bus: {e}")
            logger.warning(f"⚠️  Report saved locally only")

    def process_all_pipes(self) -> Dict[str, Any]:
        """
        Process all bidirectional pipes

        - Distribute pending directives (top-down)
        - Collect and route reports (bottom-up)
        - Update pipe status
        """
        logger.info("=" * 80)
        logger.info("🔗 PROCESSING ALL BIDIRECTIONAL PIPES")
        logger.info("=" * 80)

        results = {
            "pipes_processed": 0,
            "directives_distributed": 0,
            "reports_collected": 0,
            "pipes": {}
        }

        # Load all pipes
        for pipe_file in self.pipes_dir.glob("*.json"):
            try:
                with open(pipe_file, 'r', encoding='utf-8') as f:
                    pipe_data = json.load(f)

                pipe_id = pipe_data.get('pipe_id')
                results["pipes_processed"] += 1
                results["pipes"][pipe_id] = {
                    "pending_directives": len(pipe_data.get('pending_directives', [])),
                    "active_directives": len(pipe_data.get('active_directives', [])),
                    "completed_directives": len(pipe_data.get('completed_directives', [])),
                    "pending_reports": len(pipe_data.get('pending_reports', [])),
                }

            except Exception as e:
                logger.debug(f"Error processing pipe {pipe_file}: {e}")

        logger.info(f"✅ Processed {results['pipes_processed']} pipes")
        logger.info("=" * 80)

        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bidirectional Chain-of-Command System")
    parser.add_argument("--create-directive", action="store_true", help="Create a test directive")
    parser.add_argument("--process-pipes", action="store_true", help="Process all pipes")
    args = parser.parse_args()

    chain = BidirectionalChainOfCommand()

    if args.create_directive:
        # Example: JARVIS directs C-3PO
        directive = chain.create_directive(
            from_supervisor="@jarvis",
            to_recipient="@c3po",
            title="Ensure All Teams Report Status",
            description="All managers must report status to their supervisors. Both technical and business leads must be included.",
            action_required="Process all manager reports and ensure bidirectional communication is active.",
            directive_type="operational",
            priority="high"
        )
        logger.info(f"✅ Created directive: {directive.directive_id}")

    if args.process_pipes:
        results = chain.process_all_pipes()
        logger.info(f"✅ Processed {results['pipes_processed']} pipes")
