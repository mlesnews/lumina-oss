#!/usr/bin/env python3
"""
LUMINA N8N@NAS.LESNEWSKI.LOCAL Communication Integration

Comprehensive integration of ALL inbound/outbound communications:
- Email (inbound/outbound)
- SMS (inbound/outbound)
- Voice/Phone (inbound/outbound)
- Chat (Discord, Telegram, Slack)
- Webhooks (inbound/outbound)
- API calls (inbound/outbound)
- File transfers
- Notifications

ALL communications route through @N8N@NAS.LESNEWSKI.LOCAL

Tags: #LUMINA #N8N #NAS #COMMUNICATION #INTEGRATION #INBOUND #OUTBOUND @N8N @NAS @JARVIS @LUMINA @PEAK @DTN
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
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

logger = get_logger("LUMINAN8NNASComm")


class CommunicationType(Enum):
    """Communication types"""
    EMAIL = "email"
    SMS = "sms"
    VOICE = "voice"
    CHAT = "chat"
    WEBHOOK = "webhook"
    API = "api"
    FILE = "file"
    NOTIFICATION = "notification"


class CommunicationDirection(Enum):
    """Communication direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class CommunicationChannel(Enum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WEBHOOK = "webhook"
    API = "api"
    VOICE = "voice"
    FILE_TRANSFER = "file_transfer"


@dataclass
class CommunicationMessage:
    """A communication message"""
    message_id: str
    type: str  # CommunicationType value
    direction: str  # CommunicationDirection value
    channel: str  # CommunicationChannel value
    source: str
    destination: str
    content: Dict[str, Any]
    timestamp: str
    routed_through_n8n: bool = False
    routed_through_nas: bool = False
    n8n_workflow_id: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class N8NWorkflowConfig:
    """N8N workflow configuration"""
    workflow_id: str
    name: str
    description: str
    webhook_url: str
    enabled: bool = True
    communication_types: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LUMINAN8NNASCommunicationIntegration:
    """
    LUMINA N8N@NAS.LESNEWSKI.LOCAL Communication Integration

    Ensures ALL inbound/outbound communications route through:
    - @N8N (workflow automation)
    - @NAS.LESNEWSKI.LOCAL (infrastructure)

    Comprehensive integration covering:
    - Email (inbound/outbound)
    - SMS (inbound/outbound)
    - Voice/Phone
    - Chat platforms
    - Webhooks
    - API calls
    - File transfers
    - Notifications
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize communication integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "n8n_nas_communication"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config_file = self.project_root / "config" / "n8n_nas_communication_config.json"
        self._load_config()

        # N8N Configuration
        self.n8n_host = self.config.get("n8n_host", "<NAS_PRIMARY_IP>")
        self.n8n_port = self.config.get("n8n_port", 5678)
        self.n8n_base_url = f"http://{self.n8n_host}:{self.n8n_port}"
        self.n8n_webhook_base = f"{self.n8n_base_url}/webhook"

        # NAS Configuration
        self.nas_host = self.config.get("nas_host", "<LOCAL_HOSTNAME>")
        self.nas_n8n_url = self.config.get("nas_n8n_url", f"http://{self.nas_host}:5678")

        # Workflow registry
        self.workflows: Dict[str, N8NWorkflowConfig] = {}
        self._load_workflows()

        # Communication tracking
        self.communications: Dict[str, CommunicationMessage] = {}
        self.communications_file = self.data_dir / "communications.json"
        self._load_communications()

        # Integration status
        self.integration_status = {
            "email_inbound": False,
            "email_outbound": False,
            "sms_inbound": False,
            "sms_outbound": False,
            "voice_inbound": False,
            "voice_outbound": False,
            "chat_inbound": False,
            "chat_outbound": False,
            "webhook_inbound": False,
            "webhook_outbound": False,
            "api_inbound": False,
            "api_outbound": False,
            "file_inbound": False,
            "file_outbound": False,
            "notification_outbound": False
        }

        # Verify integrations
        self._verify_integrations()

        logger.info("✅ LUMINA N8N@NAS Communication Integration initialized")
        logger.info(f"   N8N URL: {self.n8n_base_url}")
        logger.info(f"   NAS N8N URL: {self.nas_n8n_url}")
        self._log_integration_status()

    def _load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
                self.config = {}
        else:
            self.config = {}
            self._save_config()

    def _save_config(self):
        """Save configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def _load_workflows(self):
        """Load N8N workflow configurations"""
        workflows_file = self.data_dir / "workflows.json"
        if workflows_file.exists():
            try:
                with open(workflows_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.workflows = {
                        k: N8NWorkflowConfig(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"Could not load workflows: {e}")

        # Initialize default workflows if none exist
        if not self.workflows:
            self._initialize_default_workflows()

    def _save_workflows(self):
        """Save workflow configurations"""
        workflows_file = self.data_dir / "workflows.json"
        try:
            with open(workflows_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.workflows.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving workflows: {e}")

    def _load_communications(self):
        """Load communication history"""
        if self.communications_file.exists():
            try:
                with open(self.communications_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.communications = {
                        k: CommunicationMessage(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"Could not load communications: {e}")

    def _save_communications(self):
        """Save communication history"""
        try:
            with open(self.communications_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.communications.items()}, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving communications: {e}")

    def _initialize_default_workflows(self):
        """Initialize default N8N workflows"""
        default_workflows = [
            {
                "workflow_id": "email_inbound",
                "name": "Email Inbound Handler",
                "description": "Handles all inbound email via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/email/inbound",
                "communication_types": [CommunicationType.EMAIL.value],
                "channels": [CommunicationChannel.EMAIL.value]
            },
            {
                "workflow_id": "email_outbound",
                "name": "Email Outbound Handler",
                "description": "Handles all outbound email via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/email/outbound",
                "communication_types": [CommunicationType.EMAIL.value],
                "channels": [CommunicationChannel.EMAIL.value]
            },
            {
                "workflow_id": "sms_inbound",
                "name": "SMS Inbound Handler",
                "description": "Handles all inbound SMS via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/sms/inbound",
                "communication_types": [CommunicationType.SMS.value],
                "channels": [CommunicationChannel.SMS.value]
            },
            {
                "workflow_id": "sms_outbound",
                "name": "SMS Outbound Handler",
                "description": "Handles all outbound SMS via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/sms/outbound",
                "communication_types": [CommunicationType.SMS.value],
                "channels": [CommunicationChannel.SMS.value]
            },
            {
                "workflow_id": "chat_inbound",
                "name": "Chat Inbound Handler",
                "description": "Handles all inbound chat (Discord, Telegram, Slack) via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/chat/inbound",
                "communication_types": [CommunicationType.CHAT.value],
                "channels": [
                    CommunicationChannel.DISCORD.value,
                    CommunicationChannel.TELEGRAM.value,
                    CommunicationChannel.SLACK.value
                ]
            },
            {
                "workflow_id": "chat_outbound",
                "name": "Chat Outbound Handler",
                "description": "Handles all outbound chat via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/chat/outbound",
                "communication_types": [CommunicationType.CHAT.value],
                "channels": [
                    CommunicationChannel.DISCORD.value,
                    CommunicationChannel.TELEGRAM.value,
                    CommunicationChannel.SLACK.value
                ]
            },
            {
                "workflow_id": "webhook_inbound",
                "name": "Webhook Inbound Handler",
                "description": "Handles all inbound webhooks via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/webhook/inbound",
                "communication_types": [CommunicationType.WEBHOOK.value],
                "channels": [CommunicationChannel.WEBHOOK.value]
            },
            {
                "workflow_id": "webhook_outbound",
                "name": "Webhook Outbound Handler",
                "description": "Handles all outbound webhooks via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/webhook/outbound",
                "communication_types": [CommunicationType.WEBHOOK.value],
                "channels": [CommunicationChannel.WEBHOOK.value]
            },
            {
                "workflow_id": "api_inbound",
                "name": "API Inbound Handler",
                "description": "Handles all inbound API calls via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/api/inbound",
                "communication_types": [CommunicationType.API.value],
                "channels": [CommunicationChannel.API.value]
            },
            {
                "workflow_id": "api_outbound",
                "name": "API Outbound Handler",
                "description": "Handles all outbound API calls via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/api/outbound",
                "communication_types": [CommunicationType.API.value],
                "channels": [CommunicationChannel.API.value]
            },
            {
                "workflow_id": "voice_inbound",
                "name": "Voice Inbound Handler",
                "description": "Handles all inbound voice calls via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/voice/inbound",
                "communication_types": [CommunicationType.VOICE.value],
                "channels": [CommunicationChannel.VOICE.value]
            },
            {
                "workflow_id": "voice_outbound",
                "name": "Voice Outbound Handler",
                "description": "Handles all outbound voice calls via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/voice/outbound",
                "communication_types": [CommunicationType.VOICE.value],
                "channels": [CommunicationChannel.VOICE.value]
            },
            {
                "workflow_id": "file_inbound",
                "name": "File Inbound Handler",
                "description": "Handles all inbound file transfers via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/file/inbound",
                "communication_types": [CommunicationType.FILE.value],
                "channels": [CommunicationChannel.FILE_TRANSFER.value]
            },
            {
                "workflow_id": "file_outbound",
                "name": "File Outbound Handler",
                "description": "Handles all outbound file transfers via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/file/outbound",
                "communication_types": [CommunicationType.FILE.value],
                "channels": [CommunicationChannel.FILE_TRANSFER.value]
            },
            {
                "workflow_id": "notification_outbound",
                "name": "Notification Outbound Handler",
                "description": "Handles all outbound notifications via N8N@NAS",
                "webhook_url": f"{self.n8n_webhook_base}/notification/outbound",
                "communication_types": [CommunicationType.NOTIFICATION.value],
                "channels": [
                    CommunicationChannel.EMAIL.value,
                    CommunicationChannel.SMS.value,
                    CommunicationChannel.TELEGRAM.value,
                    CommunicationChannel.DISCORD.value,
                    CommunicationChannel.SLACK.value
                ]
            }
        ]

        for workflow_data in default_workflows:
            workflow = N8NWorkflowConfig(**workflow_data)
            self.workflows[workflow.workflow_id] = workflow

        self._save_workflows()
        logger.info(f"   ✅ Initialized {len(self.workflows)} default workflows")

    def _verify_integrations(self):
        """Verify all communication integrations"""
        # Check N8N connectivity
        try:
            response = requests.get(f"{self.n8n_base_url}/healthz", timeout=5)
            n8n_available = response.status_code == 200
        except:
            n8n_available = False

        if not n8n_available:
            logger.warning(f"   ⚠️  N8N not reachable at {self.n8n_base_url}")

        # Verify each workflow
        for workflow_id, workflow in self.workflows.items():
            if workflow.enabled:
                # Check if workflow webhook is accessible
                # This would verify the workflow exists in N8N
                pass

        # Update integration status based on workflow availability
        self._update_integration_status()

    def _update_integration_status(self):
        """Update integration status based on workflows"""
        # Email
        self.integration_status["email_inbound"] = "email_inbound" in self.workflows and self.workflows["email_inbound"].enabled
        self.integration_status["email_outbound"] = "email_outbound" in self.workflows and self.workflows["email_outbound"].enabled

        # SMS
        self.integration_status["sms_inbound"] = "sms_inbound" in self.workflows and self.workflows["sms_inbound"].enabled
        self.integration_status["sms_outbound"] = "sms_outbound" in self.workflows and self.workflows["sms_outbound"].enabled

        # Voice
        self.integration_status["voice_inbound"] = "voice_inbound" in self.workflows and self.workflows["voice_inbound"].enabled
        self.integration_status["voice_outbound"] = "voice_outbound" in self.workflows and self.workflows["voice_outbound"].enabled

        # Chat
        self.integration_status["chat_inbound"] = "chat_inbound" in self.workflows and self.workflows["chat_inbound"].enabled
        self.integration_status["chat_outbound"] = "chat_outbound" in self.workflows and self.workflows["chat_outbound"].enabled

        # Webhook
        self.integration_status["webhook_inbound"] = "webhook_inbound" in self.workflows and self.workflows["webhook_inbound"].enabled
        self.integration_status["webhook_outbound"] = "webhook_outbound" in self.workflows and self.workflows["webhook_outbound"].enabled

        # API
        self.integration_status["api_inbound"] = "api_inbound" in self.workflows and self.workflows["api_inbound"].enabled
        self.integration_status["api_outbound"] = "api_outbound" in self.workflows and self.workflows["api_outbound"].enabled

        # File
        self.integration_status["file_inbound"] = "file_inbound" in self.workflows and self.workflows["file_inbound"].enabled
        self.integration_status["file_outbound"] = "file_outbound" in self.workflows and self.workflows["file_outbound"].enabled

        # Notification
        self.integration_status["notification_outbound"] = "notification_outbound" in self.workflows and self.workflows["notification_outbound"].enabled

    def _log_integration_status(self):
        """Log integration status"""
        logger.info("   Integration Status:")
        for key, status in self.integration_status.items():
            icon = "✅" if status else "❌"
            logger.info(f"      {icon} {key}: {'Enabled' if status else 'Disabled'}")

    def route_communication(
        self,
        comm_type: CommunicationType,
        direction: CommunicationDirection,
        channel: CommunicationChannel,
        source: str,
        destination: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CommunicationMessage:
        """
        Route communication through N8N@NAS

        ALL communications MUST route through N8N@NAS.LESNEWSKI.LOCAL
        """
        message_id = f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Find appropriate workflow
        workflow = self._find_workflow(comm_type, direction, channel)

        if not workflow:
            logger.error(f"   ❌ No workflow found for {comm_type.value} {direction.value} {channel.value}")
            # Create message but mark as failed
            message = CommunicationMessage(
                message_id=message_id,
                type=comm_type.value,
                direction=direction.value,
                channel=channel.value,
                source=source,
                destination=destination,
                content=content,
                timestamp=datetime.now().isoformat(),
                routed_through_n8n=False,
                routed_through_nas=False,
                status="failed",
                metadata={"error": "No workflow found", **(metadata or {})}
            )
            self.communications[message_id] = message
            self._save_communications()
            return message

        # Route through N8N webhook
        try:
            response = requests.post(
                workflow.webhook_url,
                json={
                    "message_id": message_id,
                    "type": comm_type.value,
                    "direction": direction.value,
                    "channel": channel.value,
                    "source": source,
                    "destination": destination,
                    "content": content,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat()
                },
                timeout=30
            )

            routed_successfully = response.status_code in [200, 201, 202]

            message = CommunicationMessage(
                message_id=message_id,
                type=comm_type.value,
                direction=direction.value,
                channel=channel.value,
                source=source,
                destination=destination,
                content=content,
                timestamp=datetime.now().isoformat(),
                routed_through_n8n=routed_successfully,
                routed_through_nas=True,  # N8N is on NAS
                n8n_workflow_id=workflow.workflow_id,
                status="completed" if routed_successfully else "failed",
                metadata={
                    "n8n_response_status": response.status_code,
                    "n8n_response": response.text if not routed_successfully else None,
                    **(metadata or {})
                }
            )

            if routed_successfully:
                logger.info(f"   ✅ Communication routed: {comm_type.value} {direction.value} via {workflow.name}")
            else:
                logger.warning(f"   ⚠️  Communication routing failed: {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ Error routing communication: {e}")
            message = CommunicationMessage(
                message_id=message_id,
                type=comm_type.value,
                direction=direction.value,
                channel=channel.value,
                source=source,
                destination=destination,
                content=content,
                timestamp=datetime.now().isoformat(),
                routed_through_n8n=False,
                routed_through_nas=False,
                status="failed",
                metadata={"error": str(e), **(metadata or {})}
            )

        self.communications[message_id] = message
        self._save_communications()

        return message

    def _find_workflow(
        self,
        comm_type: CommunicationType,
        direction: CommunicationDirection,
        channel: CommunicationChannel
    ) -> Optional[N8NWorkflowConfig]:
        """Find appropriate workflow for communication"""
        # Try exact match first
        workflow_key = f"{comm_type.value}_{direction.value}"
        if workflow_key in self.workflows:
            workflow = self.workflows[workflow_key]
            if workflow.enabled and channel.value in workflow.channels:
                return workflow

        # Try type + direction match
        for workflow_id, workflow in self.workflows.items():
            if (comm_type.value in workflow.communication_types and
                direction.value in workflow_id and
                workflow.enabled and
                channel.value in workflow.channels):
                return workflow

        return None

    def get_integration_report(self) -> Dict[str, Any]:
        """Get comprehensive integration report"""
        total_integrations = len(self.integration_status)
        enabled_integrations = sum(1 for v in self.integration_status.values() if v)

        return {
            "n8n_url": self.n8n_base_url,
            "nas_n8n_url": self.nas_n8n_url,
            "workflows_configured": len(self.workflows),
            "workflows_enabled": sum(1 for w in self.workflows.values() if w.enabled),
            "integration_status": self.integration_status,
            "integration_coverage": {
                "total": total_integrations,
                "enabled": enabled_integrations,
                "disabled": total_integrations - enabled_integrations,
                "coverage_percentage": (enabled_integrations / total_integrations * 100) if total_integrations > 0 else 0
            },
            "communications_routed": len(self.communications),
            "recent_communications": [
                {
                    "message_id": msg.message_id,
                    "type": msg.type,
                    "direction": msg.direction,
                    "channel": msg.channel,
                    "routed_through_n8n": msg.routed_through_n8n,
                    "status": msg.status,
                    "timestamp": msg.timestamp
                }
                for msg in list(self.communications.values())[-10:]
            ]
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA N8N@NAS Communication Integration")
    parser.add_argument("--report", action="store_true", help="Show integration report")
    parser.add_argument("--route", type=str, nargs=6, metavar=("TYPE", "DIRECTION", "CHANNEL", "SOURCE", "DEST", "CONTENT"), help="Route communication")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    integration = LUMINAN8NNASCommunicationIntegration()

    if args.report:
        report = integration.get_integration_report()
        if args.json:
            print(json.dumps(report, indent=2, default=str))
        else:
            print("N8N@NAS Communication Integration Report:")
            print(f"  N8N URL: {report['n8n_url']}")
            print(f"  NAS N8N URL: {report['nas_n8n_url']}")
            print(f"  Workflows: {report['workflows_enabled']}/{report['workflows_configured']} enabled")
            print(f"  Integration Coverage: {report['integration_coverage']['coverage_percentage']:.1f}%")
            print(f"  Communications Routed: {report['communications_routed']}")

    elif args.route:
        comm_type_str, direction_str, channel_str, source, dest, content_str = args.route
        try:
            comm_type = CommunicationType[comm_type_str.upper()]
            direction = CommunicationDirection[direction_str.upper()]
            channel = CommunicationChannel[channel_str.upper()]
            content = json.loads(content_str) if content_str.startswith("{") else {"text": content_str}

            message = integration.route_communication(
                comm_type=comm_type,
                direction=direction,
                channel=channel,
                source=source,
                destination=dest,
                content=content
            )

            if args.json:
                print(json.dumps(asdict(message), indent=2, default=str))
            else:
                print(f"{'✅' if message.routed_through_n8n else '❌'} Communication routed: {message.message_id}")
        except Exception as e:
            print(f"❌ Error: {e}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()