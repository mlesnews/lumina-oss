#!/usr/bin/env python3
"""
@ask Ticket Multi-Channel Notifier

Sends notifications to multiple channels when tickets are created:
- Gmail (TEST) - via NAS MailPlus company email
- ProtonMail (PRODUCTION) - via ProtonBridge secure email
- SMS (PRODUCTION) - via ElevenLabs (pending integration)

Notifies about ticket type, area, team assignment, and individual assignment.

Tags: #ASK #HELPDESK #EMAIL #NOTIFICATION #GMAIL #PROTONMAIL #SMS #NAS #MAILPLUS #ELEVENLABS @JARVIS @LUMINA
"""

import sys
import os
import smtplib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Setup paths first
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try to import standardized modules
try:
    from lumina_core.paths import get_project_root, setup_paths
    from lumina_core.logging import get_logger
    from lumina_core.config import ConfigLoader
    setup_paths()
    project_root = get_project_root()
except ImportError:
    # Fallback
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    project_root = script_dir.parent.parent

    # Simple config loader fallback
    class ConfigLoader:
        def __init__(self, project_root):
            self.project_root = Path(project_root)
        def load_json(self, config_file):
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

            except Exception as e:
                self.logger.error(f"Error in load_json: {e}", exc_info=True)
                raise
logger = get_logger("AskTicketEmailNotifier")

# Config loader will be initialized in class


class AskTicketEmailNotifier:
    """
    Email notification system for @ask ticket creation

    Sends email notifications via NAS MailPlus company email system when tickets are created with:
    - Ticket type (problem, change, task)
    - Area assignment
    - Team assignment
    - Individual assignment (Analyst/Engineer)
    - Priority and status
    """

    def __init__(self, nas_email_config: Optional[Dict[str, Any]] = None):
        """
        Initialize email notifier

        Args:
            nas_email_config: NAS MailPlus email configuration dict with:
                - from_email: Company email address (e.g., user@company.local)
                - to_email: Recipient Gmail address
                - password: NAS MailPlus account password
                - smtp_server: NAS SMTP server (default: <NAS_PRIMARY_IP>)
                - smtp_port: SMTP port (default: 587)
        """
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Initialize config loader
        try:
            from lumina_core.config import ConfigLoader
            self.config_loader = ConfigLoader(self.project_root)
        except ImportError:
            # Fallback
            class SimpleConfigLoader:
                def __init__(self, project_root):
                    self.project_root = Path(project_root)
                def load_json(self, config_file):
                    try:
                        import json
                        with open(config_file, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception as e:
                        self.logger.error(f"Error in load_json: {e}", exc_info=True)
                        raise
            self.config_loader = SimpleConfigLoader(self.project_root)

        # Initialize Unified Secrets Manager for Azure Vault
        try:
            from unified_secrets_manager import UnifiedSecretsManager, SecretSource
            self.secrets_manager = UnifiedSecretsManager(
                self.project_root,
                prefer_source=SecretSource.AZURE_KEY_VAULT
            )
            logger.info("✅ Unified Secrets Manager initialized (Azure Key Vault)")
        except Exception as e:
            logger.warning(f"⚠️  Unified Secrets Manager not available: {e}")
            self.secrets_manager = None

        # Load NAS email config
        if nas_email_config is None:
            nas_email_config = self._load_nas_email_config()

        self.notification_config = nas_email_config
        self.gmail_config = nas_email_config.get("gmail", {})
        self.protonmail_config = nas_email_config.get("protonmail", {})
        self.sms_config = nas_email_config.get("sms", {})

        # Initialize ProtonBridge client
        self.protonbridge = None
        self._init_protonbridge()

        logger.info("✅ Ask Ticket Multi-Channel Notifier initialized")
        logger.info(f"   📧 Gmail (TEST): {self.gmail_config.get('to_email', 'Not configured')}")
        logger.info(f"   🔒 ProtonMail (PRODUCTION): {self.protonmail_config.get('to_email', 'Not configured')}")
        logger.info(f"   📱 SMS (PRODUCTION): {self.sms_config.get('phone_number', 'Not configured')}")

    def _init_protonbridge(self):
        """Initialize ProtonBridge integration for ProtonMail"""
        try:
            from protonbridge_integration import ProtonBridgeIntegration
            self.protonbridge = ProtonBridgeIntegration(
                project_root=self.project_root,
                account_name=self.protonmail_config.get("account_name", "default")
            )
            logger.info("   ✅ ProtonBridge integration ready")
        except Exception as e:
            logger.warning(f"   ⚠️  ProtonBridge not available: {e}")

    def _load_nas_email_config(self) -> Dict[str, Any]:
        """Load multi-channel notification configuration from config file or environment"""
        # Try config file first
        config_file = self.config_dir / "ticket_notifications.json"
        if config_file.exists():
            try:
                return self.config_loader.load_json(config_file)
            except Exception as e:
                logger.warning(f"Could not load notification config file: {e}")

        # Default multi-channel configuration
        config = {
            # Gmail (TEST) - via NAS MailPlus
            "gmail": {
                "enabled": True,
                "from_email": os.getenv("NAS_EMAIL_FROM", "user@company.local"),
                "to_email": None,
                "password": None,
                "smtp_server": os.getenv("NAS_SMTP_SERVER", "<NAS_PRIMARY_IP>"),
                "smtp_port": int(os.getenv("NAS_SMTP_PORT", "587")),
                "channel": "test"
            },
            # ProtonMail (PRODUCTION) - via ProtonBridge
            "protonmail": {
                "enabled": True,
                "to_email": None,
                "account_name": os.getenv("PROTONMAIL_ACCOUNT", "default"),
                "channel": "production"
            },
            # SMS (PRODUCTION) - via ElevenLabs
            "sms": {
                "enabled": True,
                "phone_number": None,
                "channel": "production"
            }
        }

        # Retrieve credentials from Triad system (Azure Vault -> ProtonPass -> Environment)
        if self.secrets_manager:
            logger.info("🔐 Retrieving credentials from Triad system (Azure Vault → ProtonPass → Environment)...")

            # Gmail (TEST) credentials - Triad system will try Azure Vault, then ProtonPass, then env vars
            gmail_password = self.secrets_manager.get_secret("nas-email-password") or os.getenv("NAS_EMAIL_PASSWORD")
            gmail_to = self.secrets_manager.get_secret("gmail-test-email") or os.getenv("GMAIL_TEST_EMAIL") or os.getenv("GMAIL_RECIPIENT_EMAIL")

            if gmail_password:
                config["gmail"]["password"] = gmail_password
                logger.info("   ✅ NAS email password retrieved from Triad system")
            if gmail_to:
                config["gmail"]["to_email"] = gmail_to
                logger.info(f"   ✅ Gmail test email retrieved from Triad system: {gmail_to[:20]}...")

            # ProtonMail (PRODUCTION) credentials - Triad system
            protonmail_to = self.secrets_manager.get_secret("protonmail-email") or os.getenv("PROTONMAIL_EMAIL")
            if protonmail_to:
                config["protonmail"]["to_email"] = protonmail_to
                logger.info(f"   ✅ ProtonMail email retrieved from Triad system: {protonmail_to[:20]}...")

            # SMS (PRODUCTION) credentials - Triad system
            # Try multiple secret names for mobile phone
            sms_phone = (
                self.secrets_manager.get_secret("sms-phone-number") or
                self.secrets_manager.get_secret("mobile") or
                self.secrets_manager.get_secret("phone") or
                os.getenv("SMS_PHONE_NUMBER")
            )
            if sms_phone:
                config["sms"]["phone_number"] = sms_phone
                logger.info(f"   ✅ SMS phone number retrieved from Triad system (user account)")

        else:
            # Fallback to environment variables only
            logger.warning("⚠️  Unified Secrets Manager not available - using environment variables only")

            config["gmail"]["to_email"] = os.getenv("GMAIL_TEST_EMAIL") or os.getenv("GMAIL_RECIPIENT_EMAIL")
            config["gmail"]["password"] = os.getenv("NAS_EMAIL_PASSWORD")
            config["protonmail"]["to_email"] = os.getenv("PROTONMAIL_EMAIL")
            config["sms"]["phone_number"] = os.getenv("SMS_PHONE_NUMBER")

            # Log what was found from environment variables
            if config["gmail"].get("to_email"):
                gmail_to = config["gmail"]["to_email"]
                logger.info(f"   ✅ Gmail (TEST) email (env): {gmail_to[:3]}***@{gmail_to.split('@')[1] if '@' in gmail_to else '***'}")
            if config["gmail"].get("password"):
                logger.info(f"   ✅ NAS email password (env): {'*' * len(config['gmail']['password'])}")
            if config["protonmail"].get("to_email"):
                protonmail_to = config["protonmail"]["to_email"]
                logger.info(f"   ✅ ProtonMail (PRODUCTION) email (env): {protonmail_to[:3]}***@{protonmail_to.split('@')[1] if '@' in protonmail_to else '***'}")
            if config["sms"].get("phone_number"):
                sms_phone = config["sms"]["phone_number"]
                logger.info(f"   ✅ SMS (PRODUCTION) phone (env): {sms_phone[:3]}***{sms_phone[-4:] if len(sms_phone) > 4 else '***'}")

        # Warnings for missing credentials
        if not config["gmail"].get("password"):
            logger.warning("⚠️  NAS email password not configured.")
            logger.warning("   💡 Store in Azure Key Vault as: nas-email-password or nas-mailplus-password")
            logger.warning("   💡 Or set environment variable: NAS_EMAIL_PASSWORD")
        if not config["gmail"].get("to_email"):
            logger.warning("⚠️  Gmail test email not configured.")
            logger.warning("   💡 Store in Azure Key Vault as: gmail-test-email or gmail-email")
            logger.warning("   💡 Or set environment variable: GMAIL_TEST_EMAIL")
        if not config["protonmail"].get("to_email"):
            logger.warning("⚠️  ProtonMail email not configured.")
            logger.warning("   💡 Store in Azure Key Vault as: protonmail-email or protonmail-username")
            logger.warning("   💡 Or set environment variable: PROTONMAIL_EMAIL")
        if not config["sms"].get("phone_number"):
            logger.warning("⚠️  SMS phone number not configured.")
            logger.warning("   💡 Store in Azure Key Vault as: sms-phone-number")
            logger.warning("   💡 Or set environment variable: SMS_PHONE_NUMBER")

        return config

    def _determine_ticket_type(self, tags: list, ask_text: str) -> str:
        """
        Determine ticket type from tags and text

        Returns:
            "problem", "change", "task", or "general"
        """
        ask_lower = ask_text.lower()
        tags_lower = [tag.lower() for tag in tags]

        # Problem indicators
        if any(keyword in ask_lower for keyword in ["error", "bug", "fix", "issue", "problem", "broken", "fail"]):
            return "problem"
        if "problem" in tags_lower or "bug" in tags_lower or "error" in tags_lower:
            return "problem"

        # Change indicators
        if any(keyword in ask_lower for keyword in ["change", "update", "modify", "implement", "create", "add"]):
            return "change"
        if "change" in tags_lower or "implementation" in tags_lower:
            return "change"

        # Task indicators
        if any(keyword in ask_lower for keyword in ["task", "todo", "work", "do"]):
            return "task"
        if "task" in tags_lower:
            return "task"

        return "general"

    def _determine_area(self, tags: list, assigned_team: Optional[str]) -> str:
        """
        Determine area from tags and team assignment

        Returns:
            Area name (e.g., "APICLI", "Standardization", "Core Systems")
        """
        tags_lower = [tag.lower() for tag in tags]

        # Area mapping from tags
        area_map = {
            "apicli": "APICLI Endpoints",
            "standardization": "Standardization & Modularization",
            "ask_ticket": "Ask Ticket System",
            "v3": "V3 Verification",
            "health_check": "Health & Welfare",
            "logging": "Core Logging",
            "paths": "Path Management",
            "config": "Configuration",
            "daemon": "Daemon Management",
            "cron": "Cron Scheduling",
            "helpdesk": "Helpdesk",
            "gitlens": "GitLens Integration"
        }

        for tag in tags_lower:
            if tag in area_map:
                return area_map[tag]

        # Fallback to team name
        if assigned_team:
            return assigned_team.replace("_", " ").title()

        return "General"

    def _determine_role(self, assigned_individual: Optional[str], tags: list) -> str:
        """
        Determine role (Analyst/Engineer) from assignment and tags

        Returns:
            "Analyst", "Engineer", or "Unassigned"
        """
        if not assigned_individual:
            return "Unassigned"

        tags_lower = [tag.lower() for tag in tags]
        individual_lower = assigned_individual.lower()

        # Engineer indicators
        if any(keyword in individual_lower for keyword in ["engineer", "dev", "developer", "programmer"]):
            return "Engineer"
        if "engineer" in tags_lower or "development" in tags_lower:
            return "Engineer"

        # Analyst indicators
        if any(keyword in individual_lower for keyword in ["analyst", "analyst", "business"]):
            return "Analyst"
        if "analyst" in tags_lower or "analysis" in tags_lower:
            return "Analyst"

        # Default based on ticket type
        ticket_type = self._determine_ticket_type(tags, "")
        if ticket_type in ["problem", "change"]:
            return "Engineer"
        else:
            return "Analyst"

    def _create_email_content(self, ticket_record: Any) -> tuple[str, str]:
        """
        Create email subject and body from ticket record

        Returns:
            (subject, html_body)
        """
        # Determine ticket details
        ticket_type = self._determine_ticket_type(ticket_record.tags, ticket_record.ask_text)
        area = self._determine_area(ticket_record.tags, ticket_record.assigned_team)
        role = self._determine_role(ticket_record.assigned_individual, ticket_record.tags)

        # Subject
        ticket_type_emoji = {
            "problem": "🚨",
            "change": "🔄",
            "task": "📋",
            "general": "📝"
        }
        emoji = ticket_type_emoji.get(ticket_type, "📝")

        subject = f"{emoji} New {ticket_type.title()} Ticket: {area} - {ticket_record.ask_id[:8]}"

        # HTML Body
        priority_color = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#28a745"
        }
        priority_bg = {
            "critical": "#f8d7da",
            "high": "#fff3cd",
            "medium": "#fff3cd",
            "low": "#d4edda"
        }

        status_color = {
            "pending": "#6c757d",
            "assigned": "#007bff",
            "in_progress": "#17a2b8",
            "resolved": "#28a745",
            "closed": "#6c757d"
        }

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
        .ticket-info {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
        .badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; margin: 2px; }}
        .priority-critical {{ background: {priority_bg.get('critical', '#f8d7da')}; color: {priority_color.get('critical', '#dc3545')}; }}
        .priority-high {{ background: {priority_bg.get('high', '#fff3cd')}; color: {priority_color.get('high', '#fd7e14')}; }}
        .priority-medium {{ background: {priority_bg.get('medium', '#fff3cd')}; color: {priority_color.get('medium', '#ffc107')}; }}
        .priority-low {{ background: {priority_bg.get('low', '#d4edda')}; color: {priority_color.get('low', '#28a745')}; }}
        .status {{ background: {status_color.get(ticket_record.status, '#6c757d')}; color: white; }}
        .section {{ margin: 15px 0; }}
        .section-title {{ font-weight: bold; color: #667eea; margin-bottom: 8px; }}
        .footer {{ background: #6c757d; color: white; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }}
        .tags {{ margin-top: 10px; }}
        .tag {{ background: #e9ecef; padding: 3px 8px; border-radius: 3px; font-size: 11px; margin: 2px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📋 New @ask Ticket Created</h2>
            <p style="margin: 5px 0;">LUMINA Helpdesk & Change Management System</p>
        </div>

        <div class="content">
            <div class="ticket-info">
                <div class="section">
                    <div class="section-title">Ticket Information</div>
                    <p><strong>Request ID:</strong> {ticket_record.ask_id}</p>
                    <p><strong>Type:</strong> <span class="badge">{ticket_type.upper()}</span></p>
                    <p><strong>Status:</strong> <span class="badge status">{ticket_record.status.upper()}</span></p>
                    <p><strong>Priority:</strong> <span class="badge priority-{ticket_record.priority}">{ticket_record.priority.upper()}</span></p>
                </div>

                <div class="section">
                    <div class="section-title">Assignment</div>
                    <p><strong>Area:</strong> {area}</p>
                    <p><strong>Team:</strong> {ticket_record.assigned_team or 'Unassigned'}</p>
                    <p><strong>Individual:</strong> {ticket_record.assigned_individual or 'Unassigned'}</p>
                    <p><strong>Role:</strong> {role}</p>
                </div>

                <div class="section">
                    <div class="section-title">Ticket Details</div>
                    <p><strong>@ask Text:</strong></p>
                    <p style="background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace;">{ticket_record.ask_text}</p>

                    {f'<p><strong>Description:</strong><br>{ticket_record.description}</p>' if ticket_record.description and ticket_record.description != ticket_record.ask_text else ''}
                </div>

                <div class="section">
                    <div class="section-title">Related Tickets</div>
                    <p><strong>Helpdesk Ticket:</strong> {ticket_record.helpdesk_ticket or 'None'}</p>
                    <p><strong>GitLens Ticket:</strong> {ticket_record.gitlens_ticket or 'None'}</p>
                    <p><strong>GitLens PR:</strong> {ticket_record.gitlens_pr or 'None'}</p>
                </div>

                {f'''
                <div class="section">
                    <div class="section-title">Tags</div>
                    <div class="tags">
                        {' '.join([f'<span class="tag">#{tag}</span>' for tag in ticket_record.tags[:10]])}
                    </div>
                </div>
                ''' if ticket_record.tags else ''}

                {f'''
                <div class="section">
                    <div class="section-title">@SYPHON Patterns</div>
                    <p>{', '.join(ticket_record.syphon_patterns[:5])}</p>
                </div>
                ''' if ticket_record.syphon_patterns else ''}

                <div class="section">
                    <div class="section-title">Timestamps</div>
                    <p><strong>Created:</strong> {ticket_record.created_at}</p>
                    <p><strong>Updated:</strong> {ticket_record.updated_at}</p>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>LUMINA Helpdesk & Change Management System</p>
            <p>This is an automated notification. Do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """

        return subject, html_body

    def _create_sms_text(self, ticket_record: Any) -> str:
        """Create concise SMS text for ticket notification"""
        ticket_type = self._determine_ticket_type(ticket_record.tags, ticket_record.ask_text)
        area = self._determine_area(ticket_record.tags, ticket_record.assigned_team)
        role = self._determine_role(ticket_record.assigned_individual, ticket_record.tags)

        emoji = {"problem": "🚨", "change": "🔄", "task": "📋", "general": "📝"}.get(ticket_type, "📝")

        # Concise SMS format (max 160 chars ideal, but can be longer for modern phones)
        sms_text = f"""{emoji} New {ticket_type.upper()} Ticket
ID: {ticket_record.ask_id[:8]}
Area: {area}
Team: {ticket_record.assigned_team or 'Unassigned'}
Individual: {ticket_record.assigned_individual or 'Unassigned'} ({role})
Priority: {ticket_record.priority.upper()}
Status: {ticket_record.status.upper()}

{ticket_record.ask_text[:100]}{'...' if len(ticket_record.ask_text) > 100 else ''}"""

        return sms_text

    def _send_gmail_notification(self, ticket_record: Any) -> bool:
        """Send notification to Gmail (TEST) via NAS MailPlus"""
        if not self.gmail_config.get("enabled", True):
            return False

        gmail_to = self.gmail_config.get("to_email")
        gmail_password = self.gmail_config.get("password")
        from_email = self.gmail_config.get("from_email", "user@company.local")

        if not gmail_to or not gmail_password:
            logger.warning("⚠️  Gmail (TEST) credentials not configured. Skipping.")
            return False

        try:
            subject, html_body = self._create_email_content(ticket_record)

            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = gmail_to
            msg['Subject'] = f"[TEST] {subject}"
            msg.attach(MIMEText(html_body, 'html'))

            smtp_server = self.gmail_config.get("smtp_server", "<NAS_PRIMARY_IP>")
            smtp_port = self.gmail_config.get("smtp_port", 587)

            logger.info(f"📧 [TEST] Sending to Gmail: {gmail_to}")

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(from_email, gmail_password)
                server.send_message(msg)

            logger.info(f"✅ Gmail (TEST) notification sent")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending Gmail (TEST) notification: {e}")
            return False

    def _send_protonmail_notification(self, ticket_record: Any) -> bool:
        """Send notification to ProtonMail (PRODUCTION) via ProtonBridge"""
        if not self.protonmail_config.get("enabled", True):
            return False

        if not self.protonbridge:
            logger.warning("⚠️  ProtonBridge not available. Skipping ProtonMail notification.")
            return False

        protonmail_to = self.protonmail_config.get("to_email")
        if not protonmail_to:
            logger.warning("⚠️  ProtonMail email not configured. Skipping.")
            return False

        try:
            subject, html_body = self._create_email_content(ticket_record)

            # Connect to ProtonBridge SMTP
            if not self.protonbridge.smtp_connection:
                if not self.protonbridge.connect_smtp():
                    logger.error("❌ Could not connect to ProtonBridge SMTP")
                    return False

            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = protonmail_to  # Send from ProtonMail account
            msg['To'] = protonmail_to
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))

            logger.info(f"🔒 [PRODUCTION] Sending to ProtonMail: {protonmail_to}")

            # Send via ProtonBridge SMTP
            self.protonbridge.smtp_connection.send_message(msg)

            logger.info(f"✅ ProtonMail (PRODUCTION) notification sent")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending ProtonMail (PRODUCTION) notification: {e}")
            return False

    def _send_sms_notification(self, ticket_record: Any) -> bool:
        """Send notification via SMS (PRODUCTION)"""
        # TODO: SMS via ElevenLabs (Twilio removed per directive)
        if not self.sms_config.get("enabled", True):
            return False

        phone_number = self.sms_config.get("phone_number")
        if not phone_number:
            logger.warning("⚠️  SMS phone number not configured. Skipping.")
            return False

        logger.warning("⚠️  SMS sending not yet implemented via ElevenLabs. Skipping.")
        return False

    def send_ticket_notification(self, ticket_record: Any) -> Dict[str, bool]:
        """
        Send multi-channel notifications for ticket creation:
        - Gmail (TEST) via NAS MailPlus
        - ProtonMail (PRODUCTION) via ProtonBridge
        - SMS (PRODUCTION) via ElevenLabs

        Args:
            ticket_record: AskTicketRecord object

        Returns:
            Dict with channel results: {"gmail": bool, "protonmail": bool, "sms": bool}
        """
        logger.info("="*80)
        logger.info("📬 Sending Multi-Channel Ticket Notifications")
        logger.info("="*80)

        results = {
            "gmail": False,
            "protonmail": False,
            "sms": False
        }

        # Send to Gmail (TEST)
        results["gmail"] = self._send_gmail_notification(ticket_record)

        # Send to ProtonMail (PRODUCTION)
        results["protonmail"] = self._send_protonmail_notification(ticket_record)

        # Send SMS (PRODUCTION)
        results["sms"] = self._send_sms_notification(ticket_record)

        # Summary
        logger.info("="*80)
        logger.info("📊 Notification Results:")
        logger.info(f"   📧 Gmail (TEST): {'✅ Sent' if results['gmail'] else '❌ Failed'}")
        logger.info(f"   🔒 ProtonMail (PRODUCTION): {'✅ Sent' if results['protonmail'] else '❌ Failed'}")
        logger.info(f"   📱 SMS (PRODUCTION): {'✅ Sent' if results['sms'] else '❌ Failed'}")
        logger.info("="*80)

        return results

    def test_notifications(self) -> Dict[str, bool]:
        """Test all notification channels"""
        logger.info("🧪 Testing Multi-Channel Notification Configuration...")
        logger.info("="*80)

        results = {
            "gmail": False,
            "protonmail": False,
            "sms": False
        }

        # Test Gmail (TEST)
        logger.info("📧 Testing Gmail (TEST) via NAS MailPlus...")
        gmail_password = self.gmail_config.get("password")
        gmail_to = self.gmail_config.get("to_email")
        from_email = self.gmail_config.get("from_email", "user@company.local")

        if gmail_password and gmail_to:
            try:
                smtp_server = self.gmail_config.get("smtp_server", "<NAS_PRIMARY_IP>")
                smtp_port = self.gmail_config.get("smtp_port", 587)
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(from_email, gmail_password)
                results["gmail"] = True
                logger.info("   ✅ Gmail (TEST) configuration OK")
            except Exception as e:
                logger.error(f"   ❌ Gmail (TEST) test failed: {e}")
        else:
            logger.warning("   ⚠️  Gmail (TEST) not configured")

        # Test ProtonMail (PRODUCTION)
        logger.info("🔒 Testing ProtonMail (PRODUCTION) via ProtonBridge...")
        if self.protonbridge:
            try:
                if self.protonbridge.connect_smtp():
                    results["protonmail"] = True
                    logger.info("   ✅ ProtonMail (PRODUCTION) configuration OK")
                else:
                    logger.error("   ❌ ProtonMail (PRODUCTION) connection failed")
            except Exception as e:
                logger.error(f"   ❌ ProtonMail (PRODUCTION) test failed: {e}")
        else:
            logger.warning("   ⚠️  ProtonBridge not available")

        # Test SMS (PRODUCTION)
        # TODO: SMS via ElevenLabs (Twilio removed per directive)
        logger.info("📱 Testing SMS (PRODUCTION) via ElevenLabs...")
        logger.warning("   ⚠️  SMS via ElevenLabs not yet implemented")

        logger.info("="*80)
        logger.info("📊 Test Results:")
        logger.info(f"   📧 Gmail (TEST): {'✅ OK' if results['gmail'] else '❌ Failed'}")
        logger.info(f"   🔒 ProtonMail (PRODUCTION): {'✅ OK' if results['protonmail'] else '❌ Failed'}")
        logger.info(f"   📱 SMS (PRODUCTION): {'✅ OK' if results['sms'] else '❌ Failed'}")
        logger.info("="*80)

        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="@ask Ticket Multi-Channel Notifier - Gmail (TEST), ProtonMail (PRODUCTION), SMS via ElevenLabs (PRODUCTION)"
    )
    parser.add_argument("--test", action="store_true", help="Test all notification channels")
    parser.add_argument("--gmail", type=str, help="Gmail test email address")
    parser.add_argument("--protonmail", type=str, help="ProtonMail production email address")
    parser.add_argument("--sms", type=str, help="SMS production phone number")
    parser.add_argument("--config", type=str, help="Path to notification config JSON file")

    args = parser.parse_args()

    notification_config = None
    if args.config:
        config_loader = ConfigLoader(project_root)
        notification_config = config_loader.load_json(args.config)
    else:
        # Load from default location
        config_file = project_root / "config" / "ticket_notifications.json"
        if config_file.exists():
            try:
                config_loader = ConfigLoader(project_root)
                notification_config = config_loader.load_json(config_file)
            except:
                pass

    # Override with command line args
    if notification_config is None:
        notification_config = {}

    if args.gmail:
        if "gmail" not in notification_config:
            notification_config["gmail"] = {}
        notification_config["gmail"]["to_email"] = args.gmail

    if args.protonmail:
        if "protonmail" not in notification_config:
            notification_config["protonmail"] = {}
        notification_config["protonmail"]["to_email"] = args.protonmail

    if args.sms:
        if "sms" not in notification_config:
            notification_config["sms"] = {}
        notification_config["sms"]["phone_number"] = args.sms

    notifier = AskTicketEmailNotifier(nas_email_config=notification_config)

    if args.test:
        results = notifier.test_notifications()
        all_ok = all(results.values())
        if all_ok:
            print("✅ All notification channels are working!")
        else:
            print("⚠️  Some notification channels failed. Check configuration.")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()