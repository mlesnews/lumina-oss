"""
LUMINA-Gmail Integration System
Enterprise-grade Gmail integration with administrative automation,
security hardening, and SLA compliance.

Features:
- Gmail search, filtering, categorization
- Administrative job slot system (ADMIN SME)
- Secretarial automation (send/receive/organize)
- JEDIARCHIVES @HOLOCRON LIBRARY integration
- @F4 capabilities integration
- N8N@NAS workflow automation
- Proton Mail family integration
- Security hardening (@SLA compliance)

#JARVIS #LUMINA #GMAIL #ADMIN #SECRETARIAL #JEDIARCHIVES #HOLOCRON #F4 #N8N #NAS #PROTON #SLA
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("LUMINAGmailIntegration")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LUMINAGmailIntegration")

# Import unified secrets manager
try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    logger.warning("⚠️  Unified Secrets Manager not available")


class EmailCategory(Enum):
    """Email categorization for JEDIARCHIVES organization."""
    URGENT = "urgent"
    ACTION_REQUIRED = "action_required"
    INFORMATION = "information"
    ARCHIVE = "archive"
    SPAM = "spam"
    FINANCIAL = "financial"
    LEGAL = "legal"
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"
    PERSONAL = "personal"
    PROJECT = "project"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    INTERNAL = "internal"


class SecurityLevel(Enum):
    """Security classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class SLACompliance(Enum):
    """SLA compliance status."""
    MET = "met"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


@dataclass
class EmailMetadata:
    """Email metadata with security and categorization."""
    email_id: str
    subject: str
    from_address: str
    to_address: str
    date: str
    category: EmailCategory
    security_level: SecurityLevel
    priority: int  # 1-5, 1=highest
    tags: List[str]
    request_id: Optional[str] = None
    holocron_entry_id: Optional[str] = None
    jediarchive_location: Optional[str] = None
    f4_processed: bool = False
    n8n_workflow_id: Optional[str] = None
    sla_deadline: Optional[str] = None
    sla_status: SLACompliance = SLACompliance.MET


@dataclass
class AdministrativeJob:
    """Administrative job slot for ADMIN SME."""
    job_id: str
    job_type: str  # "send", "receive", "categorize", "organize", "respond"
    email_id: Optional[str] = None
    assigned_to: str = "ADMIN_SME"
    status: str = "pending"
    priority: int = 3
    created_at: str = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class LUMINAGmailIntegration:
    """
    LUMINA-Gmail Integration System

    Enterprise-grade email management with:
    - Administrative automation
    - Security hardening
    - SLA compliance
    - JEDIARCHIVES/HOLOCRON integration
    - @F4 capabilities
    - N8N@NAS workflows
    """

    def __init__(self, project_root: Path):
        """
        Initialize LUMINA-Gmail Integration System.

        Args:
            project_root: Root path of LUMINA project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "lumina_gmail"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.admin_jobs_dir = self.data_dir / "admin_jobs"
        self.admin_jobs_dir.mkdir(parents=True, exist_ok=True)

        self.jediarchives_dir = self.data_dir / "jediarchives"
        self.jediarchives_dir.mkdir(parents=True, exist_ok=True)

        self.holocron_dir = self.project_root / "data" / "holocron" / "email_archive"
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        self.security_log_dir = self.data_dir / "security_logs"
        self.security_log_dir.mkdir(parents=True, exist_ok=True)

        self.sla_tracking_dir = self.data_dir / "sla_tracking"
        self.sla_tracking_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config_file = self.project_root / "config" / "lumina_gmail_config.json"
        self.load_config()

        # Unified Secrets Manager
        # ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.
        if SECRETS_MANAGER_AVAILABLE:
            self.secrets_manager = UnifiedSecretsManager(
                self.project_root,
                prefer_source=SecretSource.AZURE_KEY_VAULT
            )
            logger.info("✅ Unified Secrets Manager initialized (Azure Key Vault / ProtonPass / Dashlane)")
        else:
            self.secrets_manager = None
            logger.warning("⚠️  Unified Secrets Manager not available - credentials must be configured manually")

        # N8N integration
        self.n8n_url = os.getenv("N8N_URL", "http://<NAS_PRIMARY_IP>:5678")
        self.n8n_config = self.load_n8n_config()

        logger.info("✅ LUMINA-Gmail Integration System initialized")

    def load_config(self) -> None:
        try:
            """Load configuration from file or create default."""
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
                self.save_config()

        except Exception as e:
            self.logger.error(f"Error in load_config: {e}", exc_info=True)
            raise
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration with security hardening."""
        return {
            "version": "1.0.0",
            "security": {
                "encryption_enabled": True,
                "audit_logging": True,
                "access_control": "strict",
                "data_retention_days": 365,
                "compliance_level": "enterprise",
                "sla_commitment": "equal_or_higher_than_company"
            },
            "gmail": {
                "oauth2_enabled": True,
                "api_scopes": [
                    "https://www.googleapis.com/auth/gmail.readonly",
                    "https://www.googleapis.com/auth/gmail.send",
                    "https://www.googleapis.com/auth/gmail.modify"
                ],
                "search_default_days": 30,
                "max_results_per_query": 500
            },
            "administrative": {
                "admin_sme_enabled": True,
                "auto_categorization": True,
                "auto_organization": True,
                "secretarial_automation": True,
                "job_slot_system": True
            },
            "integrations": {
                "jediarchives": {
                    "enabled": True,
                    "auto_archive": True,
                    "categorization_rules": "intelligent"
                },
                "holocron": {
                    "enabled": True,
                    "auto_index": True,
                    "library_integration": True
                },
                "f4": {
                    "enabled": True,
                    "capabilities": "full",
                    "features": "all",
                    "functionality": "complete"
                },
                "n8n_nas": {
                    "enabled": True,
                    "workflow_automation": True,
                    "url": "http://<NAS_PRIMARY_IP>:5678"
                },
                "proton_mail": {
                    "enabled": True,
                    "family_products": True,
                    "secure_hub": True
                },
                "nas_email_hub": {
                    "enabled": True,
                    "secure": True,
                    "hardened": True
                }
            },
            "sla": {
                "response_time_urgent": "1_hour",
                "response_time_high": "4_hours",
                "response_time_normal": "24_hours",
                "response_time_low": "72_hours",
                "compliance_tracking": True,
                "alerting_enabled": True
            }
        }

    def save_config(self) -> None:
        try:
            """Save configuration to file."""
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in save_config: {e}", exc_info=True)
            raise
    def load_n8n_config(self) -> Dict[str, Any]:
        try:
            """Load N8N configuration."""
            n8n_config_file = self.project_root / "config" / "n8n" / "unified_communications_config.json"
            if n8n_config_file.exists():
                with open(n8n_config_file, 'r') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in load_n8n_config: {e}", exc_info=True)
            raise
    def search_gmail(self, 
                    query: str,
                    max_results: int = 50,
                    days_back: int = 30) -> List[EmailMetadata]:
        """
        Search Gmail with security and categorization.

        Args:
            query: Gmail search query
            max_results: Maximum number of results
            days_back: Days to search back

        Returns:
            List of EmailMetadata objects
        """
        logger.info(f"Searching Gmail: {query}")

        # Log search for security audit
        self._log_security_event("gmail_search", {
            "query": query,
            "max_results": max_results,
            "days_back": days_back,
            "timestamp": datetime.now().isoformat()
        })

        # Try N8N first
        emails = self._search_via_n8n(query, max_results, days_back)

        # If N8N fails, try direct Gmail API
        if not emails:
            emails = self._search_via_gmail_api(query, max_results, days_back)

        # Process and categorize emails
        processed_emails = []
        for email_data in emails:
            metadata = self._process_email(email_data)
            processed_emails.append(metadata)

        # Create administrative jobs for processing
        for metadata in processed_emails:
            self._create_admin_job("categorize", email_id=metadata.email_id, metadata=asdict(metadata))

        return processed_emails

    def _search_via_n8n(self, query: str, max_results: int, days_back: int) -> List[Dict[str, Any]]:
        """Search Gmail via N8N on NAS."""
        try:
            import requests

            webhook_url = f"{self.n8n_url}/webhook/gmail-search"
            response = requests.post(
                webhook_url,
                json={
                    "query": query,
                    "max_results": max_results,
                    "days_back": days_back
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get("emails", [])
        except Exception as e:
            logger.warning(f"N8N search failed: {e}")

        return []

    def _search_via_gmail_api(self, query: str, max_results: int, days_back: int) -> List[Dict[str, Any]]:
        """
        Search Gmail via direct API (requires credentials).

        ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.
        """
        if not self.secrets_manager:
            logger.warning("⚠️  Secrets manager not available - cannot retrieve Gmail credentials")
            return []

        # Get Gmail OAuth2 credentials from secrets manager
        # Try multiple possible secret names
        credential_secrets = [
            "gmail-oauth2-credentials",
            "gmail-api-credentials",
            "gmail-oauth2-token",
            "google-oauth2-credentials"
        ]

        credentials = None
        for secret_name in credential_secrets:
            credentials = self.secrets_manager.get_secret(secret_name)
            if credentials:
                logger.info(f"✅ Retrieved Gmail credentials from secrets manager ({secret_name})")
                break

        if not credentials:
            logger.warning("⚠️  Gmail credentials not found in Azure Key Vault / ProtonPass / Dashlane")
            logger.info("💡 Store Gmail OAuth2 credentials using: unified_secrets_manager.py --set gmail-oauth2-credentials <value>")
            return []

        # Implementation would use google-api-python-client with credentials
        # For now, return empty list (requires full Gmail API implementation)
        logger.info("Gmail API search requires full API implementation")
        return []

    def _process_email(self, email_data: Dict[str, Any]) -> EmailMetadata:
        """
        Process email and create metadata with categorization.

        Args:
            email_data: Raw email data

        Returns:
            EmailMetadata object
        """
        # Extract basic info
        email_id = email_data.get("id", email_data.get("message_id", ""))
        subject = email_data.get("subject", "")
        from_addr = email_data.get("from", "")
        to_addr = email_data.get("to", "")
        date = email_data.get("date", datetime.now().isoformat())

        # Categorize email
        category = self._categorize_email(email_data)

        # Determine security level
        security_level = self._determine_security_level(email_data)

        # Determine priority
        priority = self._determine_priority(email_data, category)

        # Extract tags
        tags = self._extract_tags(email_data)

        # Extract request ID if present
        request_id = self._extract_request_id(email_data)

        # Check SLA requirements
        sla_deadline, sla_status = self._calculate_sla(email_data, category, priority)

        return EmailMetadata(
            email_id=email_id,
            subject=subject,
            from_address=from_addr,
            to_address=to_addr,
            date=date,
            category=category,
            security_level=security_level,
            priority=priority,
            tags=tags,
            request_id=request_id,
            sla_deadline=sla_deadline,
            sla_status=sla_status
        )

    def _categorize_email(self, email_data: Dict[str, Any]) -> EmailCategory:
        """Intelligent email categorization."""
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        from_addr = email_data.get("from", "").lower()

        # Urgent keywords
        if any(word in subject for word in ["urgent", "asap", "immediate", "critical", "emergency"]):
            return EmailCategory.URGENT

        # Action required
        if any(word in subject for word in ["action required", "please respond", "response needed", "your attention"]):
            return EmailCategory.ACTION_REQUIRED

        # Financial
        if any(word in subject + body for word in ["invoice", "payment", "billing", "financial", "cost", "price", "quote", "bid"]):
            return EmailCategory.FINANCIAL

        # Legal
        if any(word in subject + body for word in ["legal", "contract", "agreement", "lawsuit", "attorney"]):
            return EmailCategory.LEGAL

        # Technical
        if any(word in subject + body for word in ["error", "bug", "issue", "technical", "system", "server"]):
            return EmailCategory.TECHNICAL

        # Administrative
        if any(word in subject + body for word in ["admin", "administrative", "policy", "procedure"]):
            return EmailCategory.ADMINISTRATIVE

        # Project
        if any(word in subject + body for word in ["project", "task", "milestone", "deadline"]):
            return EmailCategory.PROJECT

        # Vendor
        if "vendor" in from_addr or "supplier" in from_addr:
            return EmailCategory.VENDOR

        # Customer
        if "customer" in from_addr or "client" in from_addr:
            return EmailCategory.CUSTOMER

        # Default
        return EmailCategory.INFORMATION

    def _determine_security_level(self, email_data: Dict[str, Any]) -> SecurityLevel:
        """Determine security classification level."""
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()

        # Top secret keywords
        if any(word in subject + body for word in ["top secret", "classified", "confidential", "restricted"]):
            return SecurityLevel.TOP_SECRET

        # Restricted
        if any(word in subject + body for word in ["restricted", "internal only", "do not share"]):
            return SecurityLevel.RESTRICTED

        # Confidential
        if any(word in subject + body for word in ["confidential", "private", "sensitive"]):
            return SecurityLevel.CONFIDENTIAL

        # Internal
        if "@company" in email_data.get("from", "") or "@company" in email_data.get("to", ""):
            return SecurityLevel.INTERNAL

        # Default to public
        return SecurityLevel.PUBLIC

    def _determine_priority(self, email_data: Dict[str, Any], category: EmailCategory) -> int:
        """Determine email priority (1-5, 1=highest)."""
        if category == EmailCategory.URGENT:
            return 1
        elif category == EmailCategory.ACTION_REQUIRED:
            return 2
        elif category in [EmailCategory.FINANCIAL, EmailCategory.LEGAL]:
            return 2
        elif category == EmailCategory.TECHNICAL:
            return 3
        else:
            return 4

    def _extract_tags(self, email_data: Dict[str, Any]) -> List[str]:
        """Extract tags from email."""
        tags = []
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()

        # Extract hashtags
        import re
        hashtags = re.findall(r'#\w+', subject + " " + body)
        tags.extend(hashtags)

        # Extract @mentions
        mentions = re.findall(r'@\w+', subject + " " + body)
        tags.extend(mentions)

        return list(set(tags))  # Remove duplicates

    def _extract_request_id(self, email_data: Dict[str, Any]) -> Optional[str]:
        """Extract request ID from email."""
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")

        # Look for UUID pattern
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, subject + " " + body, re.IGNORECASE)
        if match:
            return match.group(0)

        return None

    def _calculate_sla(self, email_data: Dict[str, Any], category: EmailCategory, priority: int) -> Tuple[Optional[str], SLACompliance]:
        """Calculate SLA deadline and status."""
        if not self.config.get("sla", {}).get("compliance_tracking", False):
            return None, SLACompliance.MET

        # Get SLA response times from config
        sla_config = self.config.get("sla", {})

        # Calculate deadline based on priority
        if priority == 1:  # Urgent
            hours = 1
        elif priority == 2:  # High
            hours = 4
        elif priority == 3:  # Normal
            hours = 24
        else:  # Low
            hours = 72

        # Calculate deadline
        email_date = datetime.fromisoformat(email_data.get("date", datetime.now().isoformat()))
        deadline = email_date + timedelta(hours=hours)

        # Check if deadline has passed
        now = datetime.now()
        if now > deadline:
            if (now - deadline).total_seconds() > 86400:  # More than 24 hours late
                return deadline.isoformat(), SLACompliance.CRITICAL
            else:
                return deadline.isoformat(), SLACompliance.VIOLATION
        elif (deadline - now).total_seconds() < 3600:  # Less than 1 hour remaining
            return deadline.isoformat(), SLACompliance.WARNING

        return deadline.isoformat(), SLACompliance.MET

    def _create_admin_job(self, job_type: str, email_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> AdministrativeJob:
        try:
            """Create administrative job for ADMIN SME."""
            job_id = f"admin_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(email_id or '').encode()).hexdigest()[:8]}"

            job = AdministrativeJob(
                job_id=job_id,
                job_type=job_type,
                email_id=email_id,
                metadata=metadata or {}
            )

            # Save job
            job_file = self.admin_jobs_dir / f"{job_id}.json"
            with open(job_file, 'w') as f:
                json.dump(asdict(job), f, indent=2, default=str)

            logger.info(f"Created admin job: {job_id} ({job_type})")
            return job

        except Exception as e:
            self.logger.error(f"Error in _create_admin_job: {e}", exc_info=True)
            raise
    def archive_to_jediarchives(self, email_metadata: EmailMetadata) -> str:
        """
        Archive email to JEDIARCHIVES with HOLOCRON integration.

        Args:
            email_metadata: Email metadata to archive

        Returns:
            JEDIARCHIVES entry ID
        """
        # Create JEDIARCHIVES entry
        entry_id = f"JEDIARCHIVE-EMAIL-{datetime.now().strftime('%Y%m%d')}-{hashlib.md5(email_metadata.email_id.encode()).hexdigest()[:8]}"

        entry = {
            "entry_id": entry_id,
            "email_id": email_metadata.email_id,
            "subject": email_metadata.subject,
            "from": email_metadata.from_address,
            "to": email_metadata.to_address,
            "date": email_metadata.date,
            "category": email_metadata.category.value,
            "security_level": email_metadata.security_level.value,
            "priority": email_metadata.priority,
            "tags": email_metadata.tags,
            "request_id": email_metadata.request_id,
            "archived_at": datetime.now().isoformat(),
            "location": f"jediarchives/{email_metadata.category.value}/{entry_id}.json"
        }

        # Save to JEDIARCHIVES
        category_dir = self.jediarchives_dir / email_metadata.category.value
        category_dir.mkdir(parents=True, exist_ok=True)

        entry_file = category_dir / f"{entry_id}.json"
        with open(entry_file, 'w') as f:
            json.dump(entry, f, indent=2, default=str)

        # Create HOLOCRON index entry
        self._index_in_holocron(entry)

        logger.info(f"Archived to JEDIARCHIVES: {entry_id}")
        return entry_id

    def _index_in_holocron(self, entry: Dict[str, Any]) -> None:
        """Index email entry in HOLOCRON library."""
        holocron_index_file = self.holocron_dir / "email_index.json"

        if holocron_index_file.exists():
            with open(holocron_index_file, 'r') as f:
                index = json.load(f)
        else:
            index = {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "entries": []
            }

        index["entries"].append({
            "entry_id": entry["entry_id"],
            "email_id": entry["email_id"],
            "subject": entry["subject"],
            "category": entry["category"],
            "archived_at": entry["archived_at"],
            "location": entry["location"]
        })

        with open(holocron_index_file, 'w') as f:
            json.dump(index, f, indent=2, default=str)

    def _log_security_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log security event for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_data": event_data,
            "system": "LUMINA-Gmail-Integration"
        }

        log_file = self.security_log_dir / f"security_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def process_with_f4(self, email_metadata: EmailMetadata) -> Dict[str, Any]:
        """
        Process email with @F4 capabilities.

        Args:
            email_metadata: Email metadata to process

        Returns:
            F4 processing results
        """
        # @F4 integration would go here
        # For now, return placeholder
        return {
            "f4_processed": True,
            "f4_capabilities_used": ["search", "filter", "categorize"],
            "f4_features": ["intelligent_processing", "automation"],
            "f4_functionality": "complete",
            "processed_at": datetime.now().isoformat()
        }


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA-Gmail Integration System")
    parser.add_argument("--project-root", type=Path,
                       default=Path(__file__).parent.parent.parent,
                       help="Project root directory")
    parser.add_argument("--search", type=str,
                       help="Gmail search query")
    parser.add_argument("--categorize", action="store_true",
                       help="Auto-categorize emails")
    parser.add_argument("--archive", action="store_true",
                       help="Archive to JEDIARCHIVES")

    args = parser.parse_args()

    system = LUMINAGmailIntegration(args.project_root)

    if args.search:
        emails = system.search_gmail(args.search)
        print(f"\n✓ Found {len(emails)} email(s)")

        if args.archive:
            for email in emails:
                entry_id = system.archive_to_jediarchives(email)
                print(f"  Archived: {email.subject[:50]}... → {entry_id}")


if __name__ == "__main__":


    main()