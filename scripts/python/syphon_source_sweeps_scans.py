#!/usr/bin/env python3
"""
SYPHON Source Sweeps & Scans - Comprehensive Source Intelligence Gathering

Comprehensive system for sweeping and scanning all sources (internal and external)
using SYPHON to extract actionable intelligence.

Features:
- Source discovery and cataloging
- Deep scanning and analysis
- Intelligence extraction
- Holocron archive integration
- Unified queue integration
- Triage/BAU coordination

Tags: #SYPHON #SOURCE #SWEEPS #SCANS #INTELLIGENCE #HOLOCRON @JARVIS @LUMINA
"""

import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import urllib.request
import urllib.parse
import urllib.error

# Web scraping and RSS parsing
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available, using urllib fallback")

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    logger.warning("feedparser not available - RSS feeds will use basic parsing")

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    logger.warning("BeautifulSoup not available - HTML parsing will be basic")

# Intelligence value assessment
try:
    from analyze_todays_intelligence import IntelligenceAnalyzer, IntelligenceValue, IntelligenceTemperature
    INTELLIGENCE_ANALYZER_AVAILABLE = True
except ImportError:
    INTELLIGENCE_ANALYZER_AVAILABLE = False
    IntelligenceAnalyzer = None
    logger.warning("Intelligence value assessment not available")

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

logger = get_logger("SyphonSourceSweepsScans")

# SYPHON system integration
try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import SyphonData, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None
    logger.warning("SYPHON system not available")

# Unified queue integration
try:
    from unified_queue_adapter import UnifiedQueueAdapter, QueueItemType, QueueItemStatus
    UNIFIED_QUEUE_AVAILABLE = True
except ImportError:
    UNIFIED_QUEUE_AVAILABLE = False
    UnifiedQueueAdapter = None
    logger.warning("Unified Queue Adapter not available")


class ScanType(Enum):
    """Types of source scans"""
    QUICK = "quick"  # Fast surface scan
    DEEP = "deep"  # Deep comprehensive scan
    TARGETED = "targeted"  # Targeted scan of specific sources
    FULL = "full"  # Full system scan


class SourceCategory(Enum):
    """Source categories"""
    INTERNAL_EMAIL = "internal_email"
    INTERNAL_SMS = "internal_sms"
    INTERNAL_MESSENGER = "internal_messenger"
    INTERNAL_DOCUMENTATION = "internal_documentation"
    INTERNAL_HOLOCRON = "internal_holocron"
    EXTERNAL_WEB = "external_web"
    EXTERNAL_API = "external_api"
    EXTERNAL_SOCIAL = "external_social"
    EXTERNAL_NEWS = "external_news"
    EXTERNAL_RSS = "external_rss"
    EXTERNAL_EMAIL_SOURCES = "external_email_sources"
    EXTERNAL_SMS_SOURCES = "external_sms_sources"
    EXTERNAL_MESSENGER_SOURCES = "external_messenger_sources"
    EXTERNAL_DOCUMENTATION_SOURCES = "external_documentation_sources"
    EXTERNAL_HOLOCRON_SOURCES = "external_holocron_sources"


@dataclass
class SourceDefinition:
    """Source definition for scanning"""
    source_id: str
    name: str
    category: SourceCategory
    url: Optional[str] = None
    api_endpoint: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    enabled: bool = True
    priority: int = 5  # 1-10, 1 is highest
    scan_interval_minutes: int = 60  # How often to scan
    last_scan: Optional[str] = None
    scan_count: int = 0
    items_found: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(data.get("category"), Enum):
            data["category"] = data["category"].value
        # Don't expose credentials
        if data.get("credentials"):
            data["credentials"] = "***REDACTED***"
        return data


@dataclass
class ScanResult:
    """Result of a source scan"""
    scan_id: str
    source_id: str
    source_name: str
    scan_type: ScanType
    timestamp: datetime
    duration_seconds: float
    items_found: int
    items_processed: int
    intelligence_extracted: int
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(data.get("scan_type"), Enum):
            data["scan_type"] = data["scan_type"].value
        if isinstance(data.get("timestamp"), datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data


class SyphonSourceSweepsScans:
    """
    SYPHON Source Sweeps & Scans

    Comprehensive system for sweeping and scanning all sources
    using SYPHON to extract actionable intelligence.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON source sweeps and scans"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon_source_sweeps_scans"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.sources_file = self.data_dir / "sources.json"
        self.scan_history_file = self.data_dir / "scan_history.json"
        self.intelligence_hashes_file = self.data_dir / "intelligence_hashes.json"

        # SYPHON system
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True
                )
                self.syphon = SYPHONSystem(config)
                logger.info("✅ SYPHON System initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON System not available: {e}")

        # Unified queue adapter
        self.queue_adapter = None
        if UNIFIED_QUEUE_AVAILABLE:
            try:
                self.queue_adapter = UnifiedQueueAdapter(project_root)
                logger.info("✅ Unified Queue Adapter initialized")
            except Exception as e:
                logger.warning(f"⚠️  Unified Queue Adapter not available: {e}")

        # Intelligence analyzer
        self.intelligence_analyzer = None
        if INTELLIGENCE_ANALYZER_AVAILABLE:
            try:
                self.intelligence_analyzer = IntelligenceAnalyzer()
                logger.info("✅ Intelligence Value Assessment initialized")
            except Exception as e:
                logger.warning(f"⚠️  Intelligence Analyzer not available: {e}")

        # Sources and scan history
        self.sources: Dict[str, SourceDefinition] = {}
        self.scan_history: List[ScanResult] = []

        # Intelligence deduplication tracking
        self.intelligence_hashes: Dict[str, Dict[str, Any]] = {}  # {hash: {source_id, timestamp, version, content_hash}}

        # Load existing data
        self._load_sources()
        self._load_scan_history()
        self._load_intelligence_hashes()

        # Initialize default sources
        self._initialize_default_sources()

        # Save sources
        self._save_sources()

        logger.info("✅ SYPHON Source Sweeps & Scans initialized")
        logger.info(f"   Sources: {len(self.sources)}")
        logger.info(f"   Scan History: {len(self.scan_history)}")

    def _load_sources(self):
        """Load source definitions"""
        if self.sources_file.exists():
            try:
                with open(self.sources_file, 'r') as f:
                    data = json.load(f)
                    for source_id, source_data in data.items():
                        source_data["category"] = SourceCategory(source_data["category"])
                        self.sources[source_id] = SourceDefinition(**source_data)
            except Exception as e:
                logger.debug(f"   Could not load sources: {e}")

    def _save_sources(self):
        """Save source definitions"""
        try:
            with open(self.sources_file, 'w') as f:
                json.dump({
                    source_id: source.to_dict()
                    for source_id, source in self.sources.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving sources: {e}")

    def _load_scan_history(self):
        """Load scan history"""
        if self.scan_history_file.exists():
            try:
                with open(self.scan_history_file, 'r') as f:
                    data = json.load(f)
                    for scan_data in data:
                        scan_data["scan_type"] = ScanType(scan_data["scan_type"])
                        scan_data["timestamp"] = datetime.fromisoformat(scan_data["timestamp"])
                        self.scan_history.append(ScanResult(**scan_data))
            except Exception as e:
                logger.debug(f"   Could not load scan history: {e}")

    def _save_scan_history(self):
        """Save scan history"""
        try:
            with open(self.scan_history_file, 'w') as f:
                json.dump([
                    scan.to_dict()
                    for scan in self.scan_history[-1000:]  # Keep last 1000 scans
                ], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving scan history: {e}")

    def _load_intelligence_hashes(self):
        """Load intelligence hash tracking"""
        if self.intelligence_hashes_file.exists():
            try:
                with open(self.intelligence_hashes_file, 'r') as f:
                    self.intelligence_hashes = json.load(f)
            except Exception as e:
                logger.debug(f"   Could not load intelligence hashes: {e}")

    def _save_intelligence_hashes(self):
        """Save intelligence hash tracking"""
        try:
            with open(self.intelligence_hashes_file, 'w') as f:
                json.dump(self.intelligence_hashes, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving intelligence hashes: {e}")

    def _hash_intelligence(self, intelligence_data: Dict[str, Any]) -> str:
        try:
            """Generate hash for intelligence data"""
            # Create hash from key intelligence fields
            hash_data = {
                "content": intelligence_data.get("content", ""),
                "title": intelligence_data.get("title", ""),
                "summary": intelligence_data.get("summary", ""),
                "url": intelligence_data.get("url", ""),
                "source": intelligence_data.get("source", "")
            }

            # Create deterministic JSON string
            hash_string = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)

            # Generate SHA256 hash
            return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

        except Exception as e:
            self.logger.error(f"Error in _hash_intelligence: {e}", exc_info=True)
            raise
    def _hash_intelligence_content(self, intelligence_data: Dict[str, Any]) -> str:
        """Generate content hash for change detection (major/minor updates)"""
        # Hash just the content for change detection
        content = intelligence_data.get("content", "")
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _check_intelligence_duplicate(self, intelligence_data: Dict[str, Any], source_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Check if intelligence is duplicate or has substantial updates

        Returns:
            (is_duplicate, existing_hash, update_type)
            - is_duplicate: True if exact duplicate
            - existing_hash: Hash of existing intelligence if found
            - update_type: "major", "minor", or None
        """
        intelligence_hash = self._hash_intelligence(intelligence_data)
        content_hash = self._hash_intelligence_content(intelligence_data)

        # Check for exact duplicate
        if intelligence_hash in self.intelligence_hashes:
            existing = self.intelligence_hashes[intelligence_hash]

            # Check if same source
            if existing.get("source_id") == source_id:
                existing_content_hash = existing.get("content_hash", "")

                # Exact duplicate (same content hash)
                if existing_content_hash == content_hash:
                    return (True, intelligence_hash, None)

                # Check for substantial updates
                # Major update: >30% content change
                # Minor update: 5-30% content change
                # We'll use content hash difference as proxy
                # If content hash is different, it's an update
                if existing_content_hash != content_hash:
                    # Calculate similarity (simplified - in production, use more sophisticated diff)
                    old_content = existing.get("content", "")
                    new_content = intelligence_data.get("content", "")

                    if old_content and new_content:
                        # Simple similarity check
                        old_words = set(old_content.lower().split())
                        new_words = set(new_content.lower().split())

                        if old_words and new_words:
                            common_words = old_words.intersection(new_words)
                            similarity = len(common_words) / max(len(old_words), len(new_words))

                            # Major update: <70% similarity
                            if similarity < 0.70:
                                return (False, intelligence_hash, "major")
                            # Minor update: 70-95% similarity
                            elif similarity < 0.95:
                                return (False, intelligence_hash, "minor")
                            # No substantial update: >95% similarity
                            else:
                                return (True, intelligence_hash, None)

                    # If we can't calculate similarity, assume minor update
                    return (False, intelligence_hash, "minor")

            # Different source - not a duplicate
            return (False, None, None)

        # New intelligence
        return (False, None, None)

    def _register_intelligence(self, intelligence_data: Dict[str, Any], source_id: str, update_type: Optional[str] = None):
        """Register intelligence hash for deduplication"""
        intelligence_hash = self._hash_intelligence(intelligence_data)
        content_hash = self._hash_intelligence_content(intelligence_data)

        # Get or create version
        if intelligence_hash in self.intelligence_hashes:
            existing = self.intelligence_hashes[intelligence_hash]
            version = existing.get("version", 1)
            if update_type:
                version += 1
        else:
            version = 1

        # Register intelligence
        self.intelligence_hashes[intelligence_hash] = {
            "source_id": source_id,
            "timestamp": datetime.now().isoformat(),
            "version": version,
            "content_hash": content_hash,
            "content": intelligence_data.get("content", "")[:500],  # Store first 500 chars for reference
            "title": intelligence_data.get("title", ""),
            "url": intelligence_data.get("url", ""),
            "update_type": update_type or "new"
        }

        self._save_intelligence_hashes()

    def _initialize_default_sources(self):
        """Initialize default source definitions"""
        # Internal sources
        internal_sources = [
            ("internal_email_all", "All Email Accounts", SourceCategory.INTERNAL_EMAIL, 60),
            ("internal_sms_all", "All SMS Messages", SourceCategory.INTERNAL_SMS, 180),
            ("internal_messenger_all", "All Messenger Platforms", SourceCategory.INTERNAL_MESSENGER, 240),
            ("internal_documentation_all", "All Documentation", SourceCategory.INTERNAL_DOCUMENTATION, 1440),
            ("internal_holocron_all", "All Holocrons", SourceCategory.INTERNAL_HOLOCRON, 480),
        ]

        # External sources
        external_sources = [
            ("external_web_sources", "Web Sources", SourceCategory.EXTERNAL_WEB, 240),
            ("external_api_sources", "API Sources", SourceCategory.EXTERNAL_API, 30),
            ("external_social_sources", "Social Media Sources", SourceCategory.EXTERNAL_SOCIAL, 120),
            ("external_news_sources", "News Feed Sources", SourceCategory.EXTERNAL_NEWS, 180),
            ("external_rss_sources", "RSS Feed Sources", SourceCategory.EXTERNAL_RSS, 120),
            ("external_email_sources", "External Email Sources", SourceCategory.EXTERNAL_EMAIL_SOURCES, 360),
            ("external_sms_sources", "External SMS Sources", SourceCategory.EXTERNAL_SMS_SOURCES, 480),
            ("external_messenger_sources", "External Messenger Sources", SourceCategory.EXTERNAL_MESSENGER_SOURCES, 240),
            ("external_documentation_sources", "External Documentation Sources", SourceCategory.EXTERNAL_DOCUMENTATION_SOURCES, 1440),
            ("external_holocron_sources", "External Holocron Sources", SourceCategory.EXTERNAL_HOLOCRON_SOURCES, 1440),
        ]

        # Add internal sources
        for source_id, name, category, interval in internal_sources:
            if source_id not in self.sources:
                self.sources[source_id] = SourceDefinition(
                    source_id=source_id,
                    name=name,
                    category=category,
                    enabled=True,
                    priority=5,
                    scan_interval_minutes=interval
                )

        # Add external sources
        for source_id, name, category, interval in external_sources:
            if source_id not in self.sources:
                self.sources[source_id] = SourceDefinition(
                    source_id=source_id,
                    name=name,
                    category=category,
                    enabled=True,
                    priority=5,
                    scan_interval_minutes=interval
                )

    def scan_source(self, source_id: str, scan_type: ScanType = ScanType.QUICK) -> Optional[ScanResult]:
        """
        Scan a specific source

        Args:
            source_id: Source ID to scan
            scan_type: Type of scan to perform

        Returns:
            ScanResult or None if failed
        """
        if source_id not in self.sources:
            logger.error(f"❌ Source not found: {source_id}")
            return None

        source = self.sources[source_id]
        if not source.enabled:
            logger.warning(f"⚠️  Source disabled: {source_id}")
            return None

        logger.info(f"🔍 Scanning source: {source.name} ({scan_type.value})")
        start_time = time.time()
        scan_id = f"scan_{source_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = ScanResult(
            scan_id=scan_id,
            source_id=source_id,
            source_name=source.name,
            scan_type=scan_type,
            timestamp=datetime.now(),
            duration_seconds=0.0,
            items_found=0,
            items_processed=0,
            intelligence_extracted=0
        )

        try:
            # Perform scan based on category
            if source.category in [SourceCategory.INTERNAL_EMAIL, SourceCategory.EXTERNAL_EMAIL_SOURCES]:
                scan_data = self._scan_email_source(source, scan_type)
            elif source.category in [SourceCategory.INTERNAL_SMS, SourceCategory.EXTERNAL_SMS_SOURCES]:
                scan_data = self._scan_sms_source(source, scan_type)
            elif source.category in [SourceCategory.INTERNAL_MESSENGER, SourceCategory.EXTERNAL_MESSENGER_SOURCES]:
                scan_data = self._scan_messenger_source(source, scan_type)
            elif source.category in [SourceCategory.INTERNAL_DOCUMENTATION, SourceCategory.EXTERNAL_DOCUMENTATION_SOURCES]:
                scan_data = self._scan_documentation_source(source, scan_type)
            elif source.category in [SourceCategory.INTERNAL_HOLOCRON, SourceCategory.EXTERNAL_HOLOCRON_SOURCES]:
                scan_data = self._scan_holocron_source(source, scan_type)
            elif source.category == SourceCategory.EXTERNAL_WEB:
                scan_data = self._scan_web_source(source, scan_type)
            elif source.category == SourceCategory.EXTERNAL_API:
                scan_data = self._scan_api_source(source, scan_type)
            elif source.category == SourceCategory.EXTERNAL_SOCIAL:
                scan_data = self._scan_social_source(source, scan_type)
            elif source.category == SourceCategory.EXTERNAL_NEWS:
                scan_data = self._scan_news_source(source, scan_type)
            elif source.category == SourceCategory.EXTERNAL_RSS:
                scan_data = self._scan_rss_source(source, scan_type)
            else:
                logger.warning(f"⚠️  Unknown source category: {source.category}")
                scan_data = {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0}

            # Update result
            result.items_found = scan_data.get("items_found", 0)
            result.items_processed = scan_data.get("items_processed", 0)
            result.intelligence_extracted = scan_data.get("intelligence_extracted", 0)
            result.metadata = scan_data.get("metadata", {})

            # Add deduplication stats to metadata
            result.metadata["duplicates_skipped"] = scan_data.get("duplicates_skipped", 0)
            result.metadata["updates_found"] = scan_data.get("updates_found", 0)

            # Log deduplication stats
            if scan_data.get("duplicates_skipped", 0) > 0:
                logger.info(f"   ⏭️  Skipped {scan_data['duplicates_skipped']} duplicates")
            if scan_data.get("updates_found", 0) > 0:
                logger.info(f"   ✅ Found {scan_data['updates_found']} substantial updates")

            # Update source stats
            source.last_scan = datetime.now().isoformat()
            source.scan_count += 1
            source.items_found += result.items_found

            # Add to queue if items found
            if result.items_found > 0 and self.queue_adapter:
                self._add_to_queue(source, result)

        except Exception as e:
            error_msg = f"Error scanning source {source_id}: {e}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            result.errors.append(error_msg)

        finally:
            result.duration_seconds = time.time() - start_time
            self.scan_history.append(result)
            self._save_scan_history()
            self._save_sources()

            duplicates_skipped = result.metadata.get("duplicates_skipped", 0)
            updates_found = result.metadata.get("updates_found", 0)

            logger.info(
                f"✅ Scan complete: {source.name} - "
                f"{result.items_found} items, "
                f"{result.intelligence_extracted} intelligence, "
                f"{duplicates_skipped} duplicates skipped, "
                f"{updates_found} updates, "
                f"{result.duration_seconds:.2f}s"
            )

        return result

    def _filter_intelligence_for_duplicates(self, intelligence_list: List[Dict[str, Any]], source_id: str) -> tuple[List[Dict[str, Any]], int, int]:
        """
        Filter intelligence list for duplicates and substantial updates

        Returns:
            (filtered_intelligence, duplicates_skipped, updates_found)
        """
        filtered = []
        duplicates_skipped = 0
        updates_found = 0

        for intelligence in intelligence_list:
            is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                intelligence, source_id
            )

            if is_duplicate:
                duplicates_skipped += 1
                logger.debug(f"   ⏭️  Skipped duplicate: {intelligence.get('title', 'Unknown')[:50]}")
            elif update_type:
                filtered.append(intelligence)
                self._register_intelligence(intelligence, source_id, update_type)
                updates_found += 1
                logger.info(f"   ✅ {update_type.upper()} update: {intelligence.get('title', 'Unknown')[:50]}")
            else:
                filtered.append(intelligence)
                self._register_intelligence(intelligence, source_id, "new")

        return filtered, duplicates_skipped, updates_found

    def _scan_email_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan email source - integrates with NAS Mail Hub email syphon"""
        try:
            # Try to import and use existing email syphon system
            try:
                from jarvis_syphon_all_emails_nas_hub import JARVISEmailSyphonNASHub
                email_syphon = JARVISEmailSyphonNASHub()
                email_syphon.load_email_accounts()

                all_intelligence = []
                items_found = 0

                # Determine how many emails to fetch based on scan type
                max_emails = 10 if scan_type == ScanType.QUICK else 100 if scan_type == ScanType.DEEP else 50

                # Fetch emails from NAS Mail Hub
                for account in email_syphon.email_accounts[:5]:  # Limit to 5 accounts
                    try:
                        # Use IMAP to fetch emails
                        import imaplib
                        import email
                        from email.header import decode_header

                        imap_server = account.get("imap_server", "<NAS_PRIMARY_IP>")
                        imap_port = account.get("imap_port", 993)
                        username = account.get("username", "")
                        password = account.get("password", "")

                        if not username or not password:
                            continue

                        # Connect to IMAP server
                        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
                        mail.login(username, password)
                        mail.select("INBOX")

                        # Search for recent emails
                        status, messages = mail.search(None, "ALL")
                        if status != "OK":
                            mail.close()
                            mail.logout()
                            continue

                        email_ids = messages[0].split()
                        # Get most recent emails
                        recent_ids = email_ids[-max_emails:] if len(email_ids) > max_emails else email_ids

                        for email_id in recent_ids:
                            try:
                                status, msg_data = mail.fetch(email_id, "(RFC822)")
                                if status != "OK":
                                    continue

                                email_body = msg_data[0][1]
                                email_message = email.message_from_bytes(email_body)

                                # Extract email fields
                                subject = email_message["Subject"]
                                if subject:
                                    subject, encoding = decode_header(subject)[0]
                                    if isinstance(subject, bytes):
                                        subject = subject.decode(encoding or "utf-8", errors="ignore")

                                from_addr = email_message["From"]
                                date_str = email_message["Date"]

                                # Extract body
                                body = ""
                                if email_message.is_multipart():
                                    for part in email_message.walk():
                                        content_type = part.get_content_type()
                                        if content_type == "text/plain":
                                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                            break
                                else:
                                    body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")

                                # Create intelligence item
                                intelligence = {
                                    "title": subject or "No Subject",
                                    "content": body[:5000] if body else "",
                                    "summary": body[:500] if body else "",
                                    "url": f"email://{account.get('account_id', 'unknown')}/{email_id.decode()}",
                                    "source": source.source_id,
                                    "source_name": source.name,
                                    "timestamp": date_str or datetime.now().isoformat(),
                                    "scan_type": scan_type.value,
                                    "from": from_addr,
                                    "account": account.get("account_name", "")
                                }

                                all_intelligence.append(intelligence)
                                items_found += 1

                            except Exception as e:
                                logger.debug(f"Error processing email {email_id}: {e}")
                                continue

                        mail.close()
                        mail.logout()

                    except Exception as e:
                        logger.error(f"Error connecting to email account {account.get('account_name', 'unknown')}: {e}")
                        continue

            except ImportError:
                # Fallback: check for email files in data directory
                email_data_dir = self.project_root / "data" / "lumina_gmail"
                if email_data_dir.exists():
                    # Look for recent email log files
                    for log_file in sorted(email_data_dir.glob("**/*.jsonl"), reverse=True)[:1]:
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if items_found >= max_emails:
                                        break
                                    try:
                                        email_data = json.loads(line.strip())
                                        intelligence = {
                                            "title": email_data.get("subject", "Email"),
                                            "content": email_data.get("body", email_data.get("text", "")),
                                            "summary": email_data.get("snippet", "")[:500],
                                            "url": email_data.get("id", ""),
                                            "source": source.source_id,
                                            "source_name": source.name,
                                            "timestamp": email_data.get("date", datetime.now().isoformat()),
                                            "scan_type": scan_type.value
                                        }
                                        all_intelligence.append(intelligence)
                                        items_found += 1
                                    except:
                                        continue
                        except Exception as e:
                            logger.debug(f"Error reading email log {log_file}: {e}")
                            continue

            # Filter for duplicates
            new_intelligence = []
            duplicates_skipped = 0
            updates_found = 0

            for intelligence in all_intelligence:
                is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                    intelligence, source.source_id
                )

                if is_duplicate:
                    duplicates_skipped += 1
                elif update_type:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, update_type)
                    updates_found += 1
                else:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, "new")

            # Assess intelligence value
            intelligence_assessments = []
            mission_critical_count = 0
            high_value_count = 0
            informational_count = 0

            if self.intelligence_analyzer:
                for intelligence in new_intelligence:
                    assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                    intelligence_assessments.append({
                        "title": intelligence.get("title", "Unknown"),
                        "value": assessment.value.value,
                        "temperature": assessment.temperature.value,
                        "score": assessment.score,
                        "actionable": assessment.actionable,
                        "time_sensitive": assessment.time_sensitive
                    })

                    if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                        mission_critical_count += 1
                    elif assessment.value == IntelligenceValue.HIGH_VALUE:
                        high_value_count += 1
                    else:
                        informational_count += 1

            return {
                "items_found": items_found,
                "items_processed": items_found,
                "intelligence_extracted": len(new_intelligence),
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "metadata": {
                    "duplicates_skipped": duplicates_skipped,
                    "updates_found": updates_found,
                    "intelligence": new_intelligence,
                    "intelligence_assessments": intelligence_assessments,
                    "mission_critical_count": mission_critical_count,
                    "high_value_count": high_value_count,
                    "informational_count": informational_count
                }
            }

        except Exception as e:
            logger.error(f"Error scanning email source: {e}", exc_info=True)
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

    def _scan_sms_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan SMS source - reads local SMS data files"""
        # TODO: SMS via ElevenLabs (Twilio removed per directive)
        try:
            all_intelligence = []
            items_found = 0

            # Determine how many messages to fetch
            max_messages = 10 if scan_type == ScanType.QUICK else 100 if scan_type == ScanType.DEEP else 50

            # Check for SMS data files
            sms_data_dir = self.project_root / "data" / "temp"
            sms_files = list(sms_data_dir.glob("*sms*.json")) if sms_data_dir.exists() else []

            for sms_file in sms_files[:1]:  # Check most recent file
                try:
                    with open(sms_file, 'r', encoding='utf-8') as f:
                        sms_data = json.load(f)
                        if isinstance(sms_data, list):
                            for msg in sms_data[:max_messages]:
                                intelligence = {
                                    "title": f"SMS from {msg.get('from', 'Unknown')}",
                                    "content": msg.get("body", msg.get("message", "")),
                                    "summary": (msg.get("body", msg.get("message", "")) or "")[:500],
                                    "url": f"sms://{msg.get('sid', msg.get('id', ''))}",
                                    "source": source.source_id,
                                    "source_name": source.name,
                                    "timestamp": msg.get("date", msg.get("timestamp", datetime.now().isoformat())),
                                    "scan_type": scan_type.value
                                }
                                all_intelligence.append(intelligence)
                                items_found += 1
                        elif isinstance(sms_data, dict):
                            # Single message or status file
                            if "body" in sms_data or "message" in sms_data:
                                intelligence = {
                                    "title": f"SMS from {sms_data.get('from', 'Unknown')}",
                                    "content": sms_data.get("body", sms_data.get("message", "")),
                                    "summary": (sms_data.get("body", sms_data.get("message", "")) or "")[:500],
                                    "url": f"sms://{sms_data.get('sid', sms_data.get('id', ''))}",
                                    "source": source.source_id,
                                    "source_name": source.name,
                                    "timestamp": sms_data.get("date", sms_data.get("timestamp", datetime.now().isoformat())),
                                    "scan_type": scan_type.value
                                }
                                all_intelligence.append(intelligence)
                                items_found += 1
                except Exception as e:
                    logger.debug(f"Error reading SMS file {sms_file}: {e}")
                    continue

            # Filter for duplicates
            new_intelligence = []
            duplicates_skipped = 0
            updates_found = 0

            for intelligence in all_intelligence:
                is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                    intelligence, source.source_id
                )

                if is_duplicate:
                    duplicates_skipped += 1
                elif update_type:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, update_type)
                    updates_found += 1
                else:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, "new")

            # Assess intelligence value
            intelligence_assessments = []
            mission_critical_count = 0
            high_value_count = 0
            informational_count = 0

            if self.intelligence_analyzer:
                for intelligence in new_intelligence:
                    assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                    intelligence_assessments.append({
                        "title": intelligence.get("title", "Unknown"),
                        "value": assessment.value.value,
                        "temperature": assessment.temperature.value,
                        "score": assessment.score,
                        "actionable": assessment.actionable,
                        "time_sensitive": assessment.time_sensitive
                    })

                    if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                        mission_critical_count += 1
                    elif assessment.value == IntelligenceValue.HIGH_VALUE:
                        high_value_count += 1
                    else:
                        informational_count += 1

            return {
                "items_found": items_found,
                "items_processed": items_found,
                "intelligence_extracted": len(new_intelligence),
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "metadata": {
                    "duplicates_skipped": duplicates_skipped,
                    "updates_found": updates_found,
                    "intelligence": new_intelligence,
                    "intelligence_assessments": intelligence_assessments,
                    "mission_critical_count": mission_critical_count,
                    "high_value_count": high_value_count,
                    "informational_count": informational_count
                }
            }

        except Exception as e:
            logger.error(f"Error scanning SMS source: {e}", exc_info=True)
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

    def _scan_messenger_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan messenger source - checks for messenger data files and integrations"""
        try:
            all_intelligence = []
            items_found = 0

            max_items = 10 if scan_type == ScanType.QUICK else 100 if scan_type == ScanType.DEEP else 50

            # Check for messenger data files
            messenger_data_dirs = [
                self.project_root / "data" / "messenger",
                self.project_root / "data" / "chat",
                self.project_root / "data" / "discord",
                self.project_root / "data" / "slack",
                self.project_root / "data" / "telegram"
            ]

            for data_dir in messenger_data_dirs:
                if not data_dir.exists():
                    continue

                # Look for JSON/JSONL files with recent messages
                for msg_file in sorted(data_dir.glob("**/*.json*"), reverse=True)[:2]:
                    try:
                        if msg_file.suffix == ".jsonl":
                            with open(msg_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if items_found >= max_items:
                                        break
                                    try:
                                        msg_data = json.loads(line.strip())
                                        intelligence = {
                                            "title": f"Message from {msg_data.get('from', msg_data.get('author', 'Unknown'))}",
                                            "content": msg_data.get("content", msg_data.get("text", msg_data.get("message", ""))),
                                            "summary": (msg_data.get("content", msg_data.get("text", msg_data.get("message", ""))) or "")[:500],
                                            "url": f"messenger://{msg_data.get('id', msg_data.get('message_id', ''))}",
                                            "source": source.source_id,
                                            "source_name": source.name,
                                            "timestamp": msg_data.get("timestamp", msg_data.get("date", datetime.now().isoformat())),
                                            "scan_type": scan_type.value,
                                            "platform": msg_data.get("platform", data_dir.name)
                                        }
                                        all_intelligence.append(intelligence)
                                        items_found += 1
                                    except:
                                        continue
                        else:
                            with open(msg_file, 'r', encoding='utf-8') as f:
                                msg_data = json.load(f)
                                if isinstance(msg_data, list):
                                    for msg in msg_data[:max_items]:
                                        intelligence = {
                                            "title": f"Message from {msg.get('from', msg.get('author', 'Unknown'))}",
                                            "content": msg.get("content", msg.get("text", msg.get("message", ""))),
                                            "summary": (msg.get("content", msg.get("text", msg.get("message", ""))) or "")[:500],
                                            "url": f"messenger://{msg.get('id', msg.get('message_id', ''))}",
                                            "source": source.source_id,
                                            "source_name": source.name,
                                            "timestamp": msg.get("timestamp", msg.get("date", datetime.now().isoformat())),
                                            "scan_type": scan_type.value,
                                            "platform": msg.get("platform", data_dir.name)
                                        }
                                        all_intelligence.append(intelligence)
                                        items_found += 1
                                elif isinstance(msg_data, dict):
                                    intelligence = {
                                        "title": f"Message from {msg_data.get('from', msg_data.get('author', 'Unknown'))}",
                                        "content": msg_data.get("content", msg_data.get("text", msg_data.get("message", ""))),
                                        "summary": (msg_data.get("content", msg_data.get("text", msg_data.get("message", ""))) or "")[:500],
                                        "url": f"messenger://{msg_data.get('id', msg_data.get('message_id', ''))}",
                                        "source": source.source_id,
                                        "source_name": source.name,
                                        "timestamp": msg_data.get("timestamp", msg_data.get("date", datetime.now().isoformat())),
                                        "scan_type": scan_type.value,
                                        "platform": msg_data.get("platform", data_dir.name)
                                    }
                                    all_intelligence.append(intelligence)
                                    items_found += 1
                    except Exception as e:
                        logger.debug(f"Error reading messenger file {msg_file}: {e}")
                        continue

            # Filter for duplicates
            new_intelligence = []
            duplicates_skipped = 0
            updates_found = 0

            for intelligence in all_intelligence:
                is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                    intelligence, source.source_id
                )

                if is_duplicate:
                    duplicates_skipped += 1
                elif update_type:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, update_type)
                    updates_found += 1
                else:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, "new")

            # Assess intelligence value
            intelligence_assessments = []
            mission_critical_count = 0
            high_value_count = 0
            informational_count = 0

            if self.intelligence_analyzer:
                for intelligence in new_intelligence:
                    assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                    intelligence_assessments.append({
                        "title": intelligence.get("title", "Unknown"),
                        "value": assessment.value.value,
                        "temperature": assessment.temperature.value,
                        "score": assessment.score,
                        "actionable": assessment.actionable,
                        "time_sensitive": assessment.time_sensitive
                    })

                    if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                        mission_critical_count += 1
                    elif assessment.value == IntelligenceValue.HIGH_VALUE:
                        high_value_count += 1
                    else:
                        informational_count += 1

            return {
                "items_found": items_found,
                "items_processed": items_found,
                "intelligence_extracted": len(new_intelligence),
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "metadata": {
                    "duplicates_skipped": duplicates_skipped,
                    "updates_found": updates_found,
                    "intelligence": new_intelligence,
                    "intelligence_assessments": intelligence_assessments,
                    "mission_critical_count": mission_critical_count,
                    "high_value_count": high_value_count,
                    "informational_count": informational_count
                }
            }

        except Exception as e:
            logger.error(f"Error scanning messenger source: {e}", exc_info=True)
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

    def _scan_documentation_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan documentation source - scans docs directory for new/updated files"""
        try:
            all_intelligence = []
            items_found = 0

            max_items = 20 if scan_type == ScanType.QUICK else 200 if scan_type == ScanType.DEEP else 100

            # Documentation directories to scan
            doc_dirs = [
                self.project_root / "docs",
                self.project_root / "data" / "docs",
                self.project_root / "data" / "documentation"
            ]

            # Add any custom paths from source metadata
            if source.metadata.get("doc_paths"):
                doc_dirs.extend([Path(p) for p in source.metadata["doc_paths"]])

            # File patterns to look for
            doc_patterns = ["*.md", "*.txt", "*.rst", "*.pdf", "*.doc", "*.docx"]

            for doc_dir in doc_dirs:
                if not doc_dir.exists():
                    continue

                # Find documentation files
                for pattern in doc_patterns:
                    for doc_file in list(doc_dir.glob(f"**/{pattern}"))[:max_items]:
                        if items_found >= max_items:
                            break

                        try:
                            # Get file metadata
                            stat = doc_file.stat()
                            file_size = stat.st_size
                            modified_time = datetime.fromtimestamp(stat.st_mtime)

                            # Only process recently modified files (last 30 days for quick, all for deep)
                            if scan_type == ScanType.QUICK:
                                if (datetime.now() - modified_time).days > 30:
                                    continue

                            # Read file content
                            content = ""
                            title = doc_file.stem

                            if doc_file.suffix in [".md", ".txt", ".rst"]:
                                try:
                                    with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                        # Extract title from markdown if available
                                        if doc_file.suffix == ".md":
                                            first_line = content.split('\n')[0] if content else ""
                                            if first_line.startswith('#'):
                                                title = first_line.lstrip('#').strip()
                                except Exception as e:
                                    logger.debug(f"Error reading {doc_file}: {e}")
                                    continue

                            # Create intelligence item
                            intelligence = {
                                "title": title,
                                "content": content[:10000] if content else f"Document: {doc_file.name}",
                                "summary": content[:500] if content else f"Document file: {doc_file.name}",
                                "url": f"file://{doc_file}",
                                "source": source.source_id,
                                "source_name": source.name,
                                "timestamp": modified_time.isoformat(),
                                "scan_type": scan_type.value,
                                "file_path": str(doc_file.relative_to(self.project_root)),
                                "file_size": file_size
                            }

                            all_intelligence.append(intelligence)
                            items_found += 1

                        except Exception as e:
                            logger.debug(f"Error processing doc file {doc_file}: {e}")
                            continue

            # Filter for duplicates
            new_intelligence = []
            duplicates_skipped = 0
            updates_found = 0

            for intelligence in all_intelligence:
                is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                    intelligence, source.source_id
                )

                if is_duplicate:
                    duplicates_skipped += 1
                elif update_type:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, update_type)
                    updates_found += 1
                else:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, "new")

            # Assess intelligence value
            intelligence_assessments = []
            mission_critical_count = 0
            high_value_count = 0
            informational_count = 0

            if self.intelligence_analyzer:
                for intelligence in new_intelligence:
                    assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                    intelligence_assessments.append({
                        "title": intelligence.get("title", "Unknown"),
                        "value": assessment.value.value,
                        "temperature": assessment.temperature.value,
                        "score": assessment.score,
                        "actionable": assessment.actionable,
                        "time_sensitive": assessment.time_sensitive
                    })

                    if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                        mission_critical_count += 1
                    elif assessment.value == IntelligenceValue.HIGH_VALUE:
                        high_value_count += 1
                    else:
                        informational_count += 1

            return {
                "items_found": items_found,
                "items_processed": items_found,
                "intelligence_extracted": len(new_intelligence),
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "metadata": {
                    "duplicates_skipped": duplicates_skipped,
                    "updates_found": updates_found,
                    "intelligence": new_intelligence,
                    "intelligence_assessments": intelligence_assessments,
                    "mission_critical_count": mission_critical_count,
                    "high_value_count": high_value_count,
                    "informational_count": informational_count
                }
            }

        except Exception as e:
            logger.error(f"Error scanning documentation source: {e}", exc_info=True)
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

    def _scan_holocron_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan holocron source - queries holocron databases for new intelligence"""
        try:
            all_intelligence = []
            items_found = 0

            max_items = 20 if scan_type == ScanType.QUICK else 200 if scan_type == ScanType.DEEP else 100

            # Holocron directory
            holocron_dir = self.project_root / "data" / "holocrons"

            if not holocron_dir.exists():
                return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

            # Try to use holocron query interface
            try:
                from holocron_query import HolocronQuery

                # Find holocron database files
                holocron_dbs = list(holocron_dir.glob("*.holocron.db"))
                holocron_jsons = list(holocron_dir.glob("HOLO-*.json"))

                # Query database holocrons
                for holocron_db in holocron_dbs[:5]:  # Limit to 5 databases
                    try:
                        query = HolocronQuery(holocron_db)

                        # Get all tables
                        tables = query.list_tables()

                        for table in tables[:3]:  # Limit to 3 tables per holocron
                            try:
                                # Get recent entries
                                results = query.execute_query(
                                    f'SELECT * FROM "{table}" ORDER BY rowid DESC LIMIT {max_items // len(holocron_dbs)}',
                                    limit=max_items
                                )

                                for row in results:
                                    if items_found >= max_items:
                                        break

                                    # Convert row to intelligence
                                    row_dict = dict(row)
                                    content = json.dumps(row_dict, default=str)

                                    intelligence = {
                                        "title": row_dict.get("title", row_dict.get("name", f"Holocron Entry from {table}")),
                                        "content": content[:10000],
                                        "summary": content[:500],
                                        "url": f"holocron://{holocron_db.name}/{table}/{row_dict.get('id', row_dict.get('rowid', ''))}",
                                        "source": source.source_id,
                                        "source_name": source.name,
                                        "timestamp": row_dict.get("timestamp", row_dict.get("created_at", row_dict.get("date", datetime.now().isoformat()))),
                                        "scan_type": scan_type.value,
                                        "holocron": holocron_db.name,
                                        "table": table
                                    }

                                    all_intelligence.append(intelligence)
                                    items_found += 1

                                query.close()

                            except Exception as e:
                                logger.debug(f"Error querying table {table} in {holocron_db}: {e}")
                                continue

                    except Exception as e:
                        logger.debug(f"Error opening holocron {holocron_db}: {e}")
                        continue

                # Also check JSON holocrons
                for holocron_json in sorted(holocron_jsons, reverse=True)[:10]:  # Most recent 10
                    try:
                        with open(holocron_json, 'r', encoding='utf-8') as f:
                            holocron_data = json.load(f)

                            if isinstance(holocron_data, dict):
                                content = json.dumps(holocron_data, default=str, indent=2)
                                intelligence = {
                                    "title": holocron_data.get("title", holocron_data.get("name", holocron_json.stem)),
                                    "content": content[:10000],
                                    "summary": holocron_data.get("summary", content[:500]),
                                    "url": f"holocron://{holocron_json.name}",
                                    "source": source.source_id,
                                    "source_name": source.name,
                                    "timestamp": holocron_data.get("timestamp", holocron_data.get("date", datetime.fromtimestamp(holocron_json.stat().st_mtime).isoformat())),
                                    "scan_type": scan_type.value,
                                    "holocron": holocron_json.name
                                }
                                all_intelligence.append(intelligence)
                                items_found += 1

                    except Exception as e:
                        logger.debug(f"Error reading JSON holocron {holocron_json}: {e}")
                        continue

            except ImportError:
                # Fallback: just read JSON holocrons
                for holocron_json in sorted(holocron_dir.glob("HOLO-*.json"), reverse=True)[:max_items]:
                    try:
                        with open(holocron_json, 'r', encoding='utf-8') as f:
                            holocron_data = json.load(f)
                            content = json.dumps(holocron_data, default=str)
                            intelligence = {
                                "title": holocron_data.get("title", holocron_json.stem),
                                "content": content[:10000],
                                "summary": content[:500],
                                "url": f"holocron://{holocron_json.name}",
                                "source": source.source_id,
                                "source_name": source.name,
                                "timestamp": datetime.fromtimestamp(holocron_json.stat().st_mtime).isoformat(),
                                "scan_type": scan_type.value
                            }
                            all_intelligence.append(intelligence)
                            items_found += 1
                    except Exception as e:
                        logger.debug(f"Error reading holocron {holocron_json}: {e}")
                        continue

            # Filter for duplicates
            new_intelligence = []
            duplicates_skipped = 0
            updates_found = 0

            for intelligence in all_intelligence:
                is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                    intelligence, source.source_id
                )

                if is_duplicate:
                    duplicates_skipped += 1
                elif update_type:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, update_type)
                    updates_found += 1
                else:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, "new")

            # Assess intelligence value
            intelligence_assessments = []
            mission_critical_count = 0
            high_value_count = 0
            informational_count = 0

            if self.intelligence_analyzer:
                for intelligence in new_intelligence:
                    assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                    intelligence_assessments.append({
                        "title": intelligence.get("title", "Unknown"),
                        "value": assessment.value.value,
                        "temperature": assessment.temperature.value,
                        "score": assessment.score,
                        "actionable": assessment.actionable,
                        "time_sensitive": assessment.time_sensitive
                    })

                    if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                        mission_critical_count += 1
                    elif assessment.value == IntelligenceValue.HIGH_VALUE:
                        high_value_count += 1
                    else:
                        informational_count += 1

            return {
                "items_found": items_found,
                "items_processed": items_found,
                "intelligence_extracted": len(new_intelligence),
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "metadata": {
                    "duplicates_skipped": duplicates_skipped,
                    "updates_found": updates_found,
                    "intelligence": new_intelligence,
                    "intelligence_assessments": intelligence_assessments,
                    "mission_critical_count": mission_critical_count,
                    "high_value_count": high_value_count,
                    "informational_count": informational_count
                }
            }

        except Exception as e:
            logger.error(f"Error scanning holocron source: {e}", exc_info=True)
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

    def _scan_web_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan web source with real web scraping"""
        if not source.url:
            # Try to get URL from metadata or use default discovery
            urls_to_scan = source.metadata.get("urls", [])
            if not urls_to_scan:
                logger.warning(f"No URLs configured for {source.source_id}")
                return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}
        else:
            urls_to_scan = [source.url]

        all_intelligence = []
        items_found = 0

        for url in urls_to_scan:
            try:
                # Fetch web content
                if REQUESTS_AVAILABLE:
                    response = requests.get(url, timeout=30, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    html_content = response.text
                    status_code = response.status_code
                else:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=30) as response:
                        html_content = response.read().decode('utf-8', errors='ignore')
                        status_code = response.getcode()

                if status_code != 200:
                    logger.warning(f"HTTP {status_code} for {url}")
                    continue

                # Parse HTML
                if BEAUTIFULSOUP_AVAILABLE:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else "Untitled"

                    # Extract main content
                    main_content = soup.find('main') or soup.find('article') or soup.find('body')
                    if main_content:
                        content_text = main_content.get_text(separator=' ', strip=True)
                    else:
                        content_text = soup.get_text(separator=' ', strip=True)
                else:
                    # Basic text extraction
                    title_text = "Web Page"
                    content_text = html_content[:5000]  # Limit for basic parsing

                # Create intelligence item
                intelligence = {
                    "title": title_text,
                    "content": content_text[:5000],  # Limit content size
                    "summary": content_text[:500] if len(content_text) > 500 else content_text,
                    "url": url,
                    "source": source.source_id,
                    "source_name": source.name,
                    "timestamp": datetime.now().isoformat(),
                    "scan_type": scan_type.value
                }

                all_intelligence.append(intelligence)
                items_found += 1

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                continue

        # Filter for duplicates and updates
        new_intelligence = []
        duplicates_skipped = 0
        updates_found = 0

        for intelligence in all_intelligence:
            is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                intelligence, source.source_id
            )

            if is_duplicate:
                duplicates_skipped += 1
                logger.debug(f"   ⏭️  Skipped duplicate: {intelligence.get('title', 'Unknown')[:50]}")
            elif update_type:
                new_intelligence.append(intelligence)
                self._register_intelligence(intelligence, source.source_id, update_type)
                updates_found += 1
                logger.info(f"   ✅ {update_type.upper()} update: {intelligence.get('title', 'Unknown')[:50]}")
            else:
                new_intelligence.append(intelligence)
                self._register_intelligence(intelligence, source.source_id, "new")

        # Assess intelligence value
        intelligence_assessments = []
        mission_critical_count = 0
        high_value_count = 0
        informational_count = 0

        if self.intelligence_analyzer:
            for intelligence in new_intelligence:
                assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                intelligence_assessments.append({
                    "title": intelligence.get("title", "Unknown"),
                    "value": assessment.value.value,
                    "temperature": assessment.temperature.value,
                    "score": assessment.score,
                    "actionable": assessment.actionable,
                    "time_sensitive": assessment.time_sensitive
                })

                if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                    mission_critical_count += 1
                elif assessment.value == IntelligenceValue.HIGH_VALUE:
                    high_value_count += 1
                else:
                    informational_count += 1

        return {
            "items_found": items_found,
            "items_processed": items_found,
            "intelligence_extracted": len(new_intelligence),
            "duplicates_skipped": duplicates_skipped,
            "updates_found": updates_found,
            "metadata": {
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "intelligence": new_intelligence,
                "intelligence_assessments": intelligence_assessments,
                "mission_critical_count": mission_critical_count,
                "high_value_count": high_value_count,
                "informational_count": informational_count
            }
        }

    def _scan_api_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan API source with real API calls"""
        api_endpoint = source.api_endpoint or source.metadata.get("api_endpoint")
        if not api_endpoint:
            logger.warning(f"No API endpoint configured for {source.source_id}")
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

        try:
            headers = {"User-Agent": "LUMINA-SYPHON/1.0"}
            if source.credentials:
                # Add authentication if credentials provided
                auth_type = source.credentials.get("type", "bearer")
                if auth_type == "bearer":
                    headers["Authorization"] = f"Bearer {source.credentials.get('token', '')}"
                elif auth_type == "api_key":
                    api_key_name = source.credentials.get("key_name", "api_key")
                    if "?" in api_endpoint:
                        api_endpoint += f"&{api_key_name}={source.credentials.get('key', '')}"
                    else:
                        api_endpoint += f"?{api_key_name}={source.credentials.get('key', '')}"

            if REQUESTS_AVAILABLE:
                response = requests.get(api_endpoint, headers=headers, timeout=30)
                if response.status_code != 200:
                    logger.warning(f"API returned {response.status_code} for {api_endpoint}")
                    return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}
                data = response.json()
            else:
                req = urllib.request.Request(api_endpoint, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as response:
                    import json
                    data = json.loads(response.read().decode('utf-8'))

            # Extract intelligence from API response
            all_intelligence = []
            items_found = 0

            # Handle different API response formats
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # Common API response patterns
                items = data.get("items", data.get("data", data.get("results", [data])))

            for item in items[:50]:  # Limit items
                if isinstance(item, dict):
                    intelligence = {
                        "title": item.get("title", item.get("name", "API Item")),
                        "content": str(item),
                        "summary": str(item)[:500],
                        "url": item.get("url", item.get("link", api_endpoint)),
                        "source": source.source_id,
                        "source_name": source.name,
                        "timestamp": item.get("timestamp", item.get("created_at", datetime.now().isoformat())),
                        "scan_type": scan_type.value,
                        "raw_data": item
                    }
                    all_intelligence.append(intelligence)
                    items_found += 1

            # Filter for duplicates
            new_intelligence = []
            duplicates_skipped = 0
            updates_found = 0

            for intelligence in all_intelligence:
                is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                    intelligence, source.source_id
                )

                if is_duplicate:
                    duplicates_skipped += 1
                elif update_type:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, update_type)
                    updates_found += 1
                else:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, "new")

            # Assess intelligence value
            intelligence_assessments = []
            mission_critical_count = 0
            high_value_count = 0
            informational_count = 0

            if self.intelligence_analyzer:
                for intelligence in new_intelligence:
                    assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                    intelligence_assessments.append({
                        "title": intelligence.get("title", "Unknown"),
                        "value": assessment.value.value,
                        "temperature": assessment.temperature.value,
                        "score": assessment.score,
                        "actionable": assessment.actionable,
                        "time_sensitive": assessment.time_sensitive
                    })

                    if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                        mission_critical_count += 1
                    elif assessment.value == IntelligenceValue.HIGH_VALUE:
                        high_value_count += 1
                    else:
                        informational_count += 1

            return {
                "items_found": items_found,
                "items_processed": items_found,
                "intelligence_extracted": len(new_intelligence),
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "metadata": {
                    "duplicates_skipped": duplicates_skipped,
                    "updates_found": updates_found,
                    "intelligence": new_intelligence,
                    "intelligence_assessments": intelligence_assessments,
                    "mission_critical_count": mission_critical_count,
                    "high_value_count": high_value_count,
                    "informational_count": informational_count
                }
            }

        except Exception as e:
            logger.error(f"Error scanning API source {api_endpoint}: {e}")
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

    def _scan_social_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan social media source - integrates with existing SYPHON scripts"""
        # Check for existing social media SYPHON integration
        social_scripts = source.metadata.get("syphon_scripts", [])

        if social_scripts:
            # Use existing SYPHON scripts if configured
            all_intelligence = []
            items_found = 0

            for script_path in social_scripts:
                try:
                    # Import and run SYPHON script
                    script_module = source.metadata.get("script_module")
                    if script_module:
                        import importlib
                        module = importlib.import_module(script_module)
                        if hasattr(module, "syphon"):
                            result = module.syphon()
                            if isinstance(result, list):
                                all_intelligence.extend(result)
                                items_found += len(result)
                except Exception as e:
                    logger.error(f"Error running social SYPHON script {script_path}: {e}")
                    continue

            # Filter and assess
            new_intelligence = []
            duplicates_skipped = 0
            updates_found = 0

            for intelligence in all_intelligence:
                if not isinstance(intelligence, dict):
                    intelligence = {"content": str(intelligence), "title": "Social Media Post"}

                intelligence.setdefault("source", source.source_id)
                intelligence.setdefault("source_name", source.name)
                intelligence.setdefault("timestamp", datetime.now().isoformat())

                is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                    intelligence, source.source_id
                )

                if is_duplicate:
                    duplicates_skipped += 1
                elif update_type:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, update_type)
                    updates_found += 1
                else:
                    new_intelligence.append(intelligence)
                    self._register_intelligence(intelligence, source.source_id, "new")

            return {
                "items_found": items_found,
                "items_processed": items_found,
                "intelligence_extracted": len(new_intelligence),
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "metadata": {
                    "duplicates_skipped": duplicates_skipped,
                    "updates_found": updates_found,
                    "intelligence": new_intelligence
                }
            }
        else:
            # Fallback: treat as web source if URL provided
            if source.url:
                return self._scan_web_source(source, scan_type)
            else:
                logger.warning(f"No social media SYPHON scripts or URLs configured for {source.source_id}")
                return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

    def _scan_news_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan news feed source - uses RSS parsing"""
        # News feeds are typically RSS, so reuse RSS scanning
        return self._scan_rss_source(source, scan_type)

    def _scan_rss_source(self, source: SourceDefinition, scan_type: ScanType) -> Dict[str, Any]:
        """Scan RSS feed source with real RSS parsing"""
        rss_urls = source.metadata.get("rss_urls", [])
        if source.url:
            rss_urls.append(source.url)

        if not rss_urls:
            logger.warning(f"No RSS URLs configured for {source.source_id}")
            return {"items_found": 0, "items_processed": 0, "intelligence_extracted": 0, "duplicates_skipped": 0, "updates_found": 0}

        all_intelligence = []
        items_found = 0

        for rss_url in rss_urls:
            try:
                if FEEDPARSER_AVAILABLE:
                    feed = feedparser.parse(rss_url)

                    # Limit items based on scan type
                    max_items = 10 if scan_type == ScanType.QUICK else 50 if scan_type == ScanType.DEEP else 25
                    entries = feed.entries[:max_items]

                    for entry in entries:
                        intelligence = {
                            "title": entry.get("title", "Untitled"),
                            "content": entry.get("summary", entry.get("description", "")),
                            "summary": entry.get("summary", "")[:500] if entry.get("summary") else "",
                            "url": entry.get("link", rss_url),
                            "source": source.source_id,
                            "source_name": source.name,
                            "timestamp": entry.get("published", datetime.now().isoformat()) if entry.get("published") else datetime.now().isoformat(),
                            "scan_type": scan_type.value,
                            "author": entry.get("author", ""),
                            "tags": [tag.get("term", "") for tag in entry.get("tags", [])]
                        }
                        all_intelligence.append(intelligence)
                        items_found += 1
                else:
                    # Basic RSS parsing without feedparser
                    if REQUESTS_AVAILABLE:
                        response = requests.get(rss_url, timeout=30)
                        xml_content = response.text
                    else:
                        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=30) as response:
                            xml_content = response.read().decode('utf-8', errors='ignore')

                    # Basic XML parsing for RSS
                    import xml.etree.ElementTree as ET
                    try:
                        root = ET.fromstring(xml_content)
                        # Simple RSS 2.0 parsing
                        for item in root.findall('.//item')[:10]:
                            title = item.find('title')
                            link = item.find('link')
                            description = item.find('description')

                            intelligence = {
                                "title": title.text if title is not None else "Untitled",
                                "content": description.text if description is not None else "",
                                "summary": (description.text[:500] if description is not None else ""),
                                "url": link.text if link is not None else rss_url,
                                "source": source.source_id,
                                "source_name": source.name,
                                "timestamp": datetime.now().isoformat(),
                                "scan_type": scan_type.value
                            }
                            all_intelligence.append(intelligence)
                            items_found += 1
                    except ET.ParseError as e:
                        logger.error(f"Error parsing RSS XML for {rss_url}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error fetching RSS feed {rss_url}: {e}")
                continue

        # Filter for duplicates
        new_intelligence = []
        duplicates_skipped = 0
        updates_found = 0

        for intelligence in all_intelligence:
            is_duplicate, existing_hash, update_type = self._check_intelligence_duplicate(
                intelligence, source.source_id
            )

            if is_duplicate:
                duplicates_skipped += 1
            elif update_type:
                new_intelligence.append(intelligence)
                self._register_intelligence(intelligence, source.source_id, update_type)
                updates_found += 1
            else:
                new_intelligence.append(intelligence)
                self._register_intelligence(intelligence, source.source_id, "new")

        # Assess intelligence value
        intelligence_assessments = []
        mission_critical_count = 0
        high_value_count = 0
        informational_count = 0

        if self.intelligence_analyzer:
            for intelligence in new_intelligence:
                assessment = self.intelligence_analyzer.assess_intelligence(intelligence)
                intelligence_assessments.append({
                    "title": intelligence.get("title", "Unknown"),
                    "value": assessment.value.value,
                    "temperature": assessment.temperature.value,
                    "score": assessment.score,
                    "actionable": assessment.actionable,
                    "time_sensitive": assessment.time_sensitive
                })

                if assessment.value == IntelligenceValue.MISSION_CRITICAL:
                    mission_critical_count += 1
                elif assessment.value == IntelligenceValue.HIGH_VALUE:
                    high_value_count += 1
                else:
                    informational_count += 1

        return {
            "items_found": items_found,
            "items_processed": items_found,
            "intelligence_extracted": len(new_intelligence),
            "duplicates_skipped": duplicates_skipped,
            "updates_found": updates_found,
            "metadata": {
                "duplicates_skipped": duplicates_skipped,
                "updates_found": updates_found,
                "intelligence": new_intelligence,
                "intelligence_assessments": intelligence_assessments,
                "mission_critical_count": mission_critical_count,
                "high_value_count": high_value_count,
                "informational_count": informational_count
            }
        }

    def _add_to_queue(self, source: SourceDefinition, result: ScanResult):
        """Add scan results to unified queue"""
        if not self.queue_adapter:
            return

        try:
            self.queue_adapter.add_source(
                url=source.url or f"source://{source.source_id}",
                source_type=source.category.value,
                metadata={
                    "source_id": source.source_id,
                    "source_name": source.name,
                    "scan_id": result.scan_id,
                    "items_found": result.items_found,
                    "intelligence_extracted": result.intelligence_extracted,
                    "scan_type": result.scan_type.value
                },
                priority=source.priority
            )
        except Exception as e:
            logger.warning(f"⚠️  Failed to add to queue: {e}")

    def execute_sweep(self, scan_type: ScanType = ScanType.QUICK, categories: Optional[List[SourceCategory]] = None) -> Dict[str, Any]:
        """
        Execute a comprehensive sweep of all sources

        Args:
            scan_type: Type of scan to perform
            categories: Optional list of categories to scan (None = all)

        Returns:
            Dict with sweep results
        """
        logger.info("="*80)
        logger.info(f"🔍 Executing SYPHON Source Sweep ({scan_type.value})")
        logger.info("="*80)

        sweep_result = {
            "timestamp": datetime.now().isoformat(),
            "scan_type": scan_type.value,
            "sources_scanned": 0,
            "sources_succeeded": 0,
            "sources_failed": 0,
            "total_items_found": 0,
            "total_intelligence_extracted": 0,
            "scan_results": []
        }

        # Get sources to scan
        sources_to_scan = [
            source for source in self.sources.values()
            if source.enabled
            and (categories is None or source.category in categories)
        ]

        logger.info(f"   Scanning {len(sources_to_scan)} sources...")

        for source in sources_to_scan:
            try:
                result = self.scan_source(source.source_id, scan_type)
                if result:
                    sweep_result["sources_scanned"] += 1
                    sweep_result["sources_succeeded"] += 1
                    sweep_result["total_items_found"] += result.items_found
                    sweep_result["total_intelligence_extracted"] += result.intelligence_extracted
                    sweep_result["scan_results"].append(result.to_dict())
                else:
                    sweep_result["sources_failed"] += 1
            except Exception as e:
                logger.error(f"❌ Error scanning {source.name}: {e}")
                sweep_result["sources_failed"] += 1

        logger.info("="*80)
        logger.info(f"✅ Sweep complete: {sweep_result['sources_succeeded']}/{sweep_result['sources_scanned']} succeeded")
        logger.info(f"   Items found: {sweep_result['total_items_found']}")
        logger.info(f"   Intelligence: {sweep_result['total_intelligence_extracted']}")
        logger.info("="*80)

        return sweep_result

    def get_sources_due_for_scan(self) -> List[SourceDefinition]:
        """Get sources that are due for scanning"""
        now = datetime.now()
        due_sources = []

        for source in self.sources.values():
            if not source.enabled:
                continue

            if not source.last_scan:
                due_sources.append(source)
                continue

            last_scan = datetime.fromisoformat(source.last_scan)
            time_since_scan = (now - last_scan).total_seconds() / 60  # minutes

            if time_since_scan >= source.scan_interval_minutes:
                due_sources.append(source)

        # Sort by priority
        due_sources.sort(key=lambda s: s.priority)

        return due_sources

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        enabled_sources = [s for s in self.sources.values() if s.enabled]
        recent_scans = [s for s in self.scan_history if (datetime.now() - s.timestamp).days < 7]

        # Group by category
        by_category = {}
        for source in enabled_sources:
            cat = source.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(source.source_id)

        # Calculate deduplication stats
        total_intelligence = len(self.intelligence_hashes)
        unique_intelligence = len(set(h.get("content_hash") for h in self.intelligence_hashes.values() if h.get("content_hash")))
        duplicates_prevented = total_intelligence - unique_intelligence

        return {
            "timestamp": datetime.now().isoformat(),
            "total_sources": len(self.sources),
            "enabled_sources": len(enabled_sources),
            "disabled_sources": len(self.sources) - len(enabled_sources),
            "total_scans": len(self.scan_history),
            "recent_scans_7d": len(recent_scans),
            "sources_by_category": by_category,
            "sources_due_for_scan": len(self.get_sources_due_for_scan()),
            "intelligence_tracking": {
                "total_registered": total_intelligence,
                "unique_intelligence": unique_intelligence,
                "duplicates_prevented": duplicates_prevented
            }
        }


def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("🔍 SYPHON SOURCE SWEEPS & SCANS")
    logger.info("="*80)
    logger.info("")

    sweeps_scans = SyphonSourceSweepsScans()

    # Generate report
    report = sweeps_scans.generate_report()
    logger.info("📊 REPORT")
    logger.info(f"   Total Sources: {report['total_sources']}")
    logger.info(f"   Enabled: {report['enabled_sources']}")
    logger.info(f"   Total Scans: {report['total_scans']}")
    logger.info(f"   Recent Scans (7d): {report['recent_scans_7d']}")
    logger.info(f"   Due for Scan: {report['sources_due_for_scan']}")
    logger.info("")
    logger.info("📊 DEDUPLICATION STATS")
    intel_stats = report.get("intelligence_tracking", {})
    logger.info(f"   Total Registered: {intel_stats.get('total_registered', 0)}")
    logger.info(f"   Unique Intelligence: {intel_stats.get('unique_intelligence', 0)}")
    logger.info(f"   Duplicates Prevented: {intel_stats.get('duplicates_prevented', 0)}")
    logger.info("")

    # Execute sweep of due sources
    due_sources = sweeps_scans.get_sources_due_for_scan()
    if due_sources:
        logger.info(f"🔍 Executing sweep of {len(due_sources)} due sources...")
        sweep_result = sweeps_scans.execute_sweep(scan_type=ScanType.QUICK)
        logger.info(f"   ✅ Sweep complete: {sweep_result['sources_succeeded']} succeeded")
    else:
        logger.info("   ℹ️  No sources due for scanning")

    logger.info("")
    logger.info("="*80)
    logger.info("✅ SYPHON SOURCE SWEEPS & SCANS - COMPLETE")
    logger.info("="*80)


if __name__ == "__main__":


    main()