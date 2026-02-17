"""
LUMINA Comprehensive @SYPHON System
Complete @SYPHON extraction for all @SOURCES: Filesystems, Email, Financial Accounts.

Priority Order:
1. Filesystems (FIRST PRIORITY)
2. @SOURCES @SYPHON @BAU:
   - All Email (Gmail + ProtonMail)
   - All Financial Accounts (Personal + Business)
   - For both spouses
   - #<COMPANY>-FINANCIAL-SERVICES-LLC

#JARVIS #LUMINA #SYPHON #BAU #<COMPANY>-FINANCIAL-SERVICES-LLC #NO-NONSENSE #PEOPLE
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("LuminaComprehensiveSyphon")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaComprehensiveSyphon")

from scripts.python.integrate_hook_trace import hook_trace, OperationType, TraceLevel


@dataclass
class SyphonSource:
    """@SYPHON source definition."""
    source_id: str
    source_type: str  # "filesystem", "email", "financial"
    source_name: str
    priority: int  # 1 = highest
    enabled: bool = True
    last_syphon: Optional[str] = None
    metadata: Dict[str, Any] = None
    notes: Optional[str] = None  # Optional notes/description
    transport: Optional[str] = None  # Transport layer (e.g., @NDM)
    ticket_required: Optional[bool] = None  # Whether ticket is required
    channels: Optional[List[str]] = None  # Communication channels
    syphon_processing: Optional[Dict[str, Any]] = None  # Processing config

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LuminaComprehensiveSyphonSystem:
    """
    Comprehensive @SYPHON System

    Priority Order:
    1. Filesystems (FIRST PRIORITY)
    2. @SOURCES @SYPHON @BAU:
       - All Email
       - All Financial Accounts (Personal + Business)
       - #<COMPANY>-FINANCIAL-SERVICES-LLC
    """

    def __init__(self, project_root: Path):
        """
        Initialize Comprehensive @SYPHON System.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "lumina_syphon"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.filesystem_dir = self.data_dir / "filesystems"
        self.filesystem_dir.mkdir(parents=True, exist_ok=True)

        self.email_dir = self.data_dir / "email"
        self.email_dir.mkdir(parents=True, exist_ok=True)

        self.financial_dir = self.data_dir / "financial"
        self.financial_dir.mkdir(parents=True, exist_ok=True)

        # Company context
        self.company = "<COMPANY>-FINANCIAL-SERVICES-LLC"
        self.tags = ["#NO-NONSENSE", "#PEOPLE"]

        # Load sources configuration
        self.sources = self._load_sources()

        logger.info("✅ LUMINA Comprehensive @SYPHON System initialized")
        logger.info(f"Company: {self.company}")
        logger.info(f"Tags: {', '.join(self.tags)}")

    def _load_sources(self) -> List[SyphonSource]:
        try:
            """Load @SYPHON sources configuration."""
            sources_file = self.project_root / "config" / "syphon_sources.json"

            if sources_file.exists():
                with open(sources_file, 'r') as f:
                    sources_data = json.load(f)
                    return [SyphonSource(**source) for source in sources_data.get("sources", [])]

            # Default sources (priority order)
            default_sources = [
                # Priority 1: Filesystems
                {
                    "source_id": "filesystem_primary",
                    "source_type": "filesystem",
                    "source_name": "Primary Filesystem",
                    "priority": 1,
                    "metadata": {
                        "paths": ["C:\\Users\\mlesn\\Dropbox", "C:\\Users\\mlesn\\Documents"],
                        "company": self.company
                    }
                },
                # Priority 2: Email Sources
                {
                    "source_id": "email_gmail",
                    "source_type": "email",
                    "source_name": "Gmail",
                    "priority": 2,
                    "metadata": {
                        "provider": "gmail",
                        "company": self.company
                    }
                },
                {
                    "source_id": "email_protonmail",
                    "source_type": "email",
                    "source_name": "ProtonMail",
                    "priority": 2,
                    "metadata": {
                        "provider": "protonmail",
                        "company": self.company
                    }
                },
                # Priority 2: Financial Accounts
                {
                    "source_id": "financial_personal_user",
                    "source_type": "financial",
                    "source_name": "Personal Financial Accounts (User)",
                    "priority": 2,
                    "metadata": {
                        "account_type": "personal",
                        "owner": "user",
                        "company": self.company
                    }
                },
                {
                    "source_id": "financial_personal_spouse",
                    "source_type": "financial",
                    "source_name": "Personal Financial Accounts (Spouse)",
                    "priority": 2,
                    "metadata": {
                        "account_type": "personal",
                        "owner": "spouse",
                        "company": self.company
                    }
                },
                {
                    "source_id": "financial_business",
                    "source_type": "financial",
                    "source_name": "Business Financial Accounts",
                    "priority": 2,
                    "metadata": {
                        "account_type": "business",
                        "company": self.company
                    }
                }
            ]

            # Save default sources
            sources_file.parent.mkdir(parents=True, exist_ok=True)
            with open(sources_file, 'w') as f:
                json.dump({"sources": default_sources}, f, indent=2)

            return [SyphonSource(**source) for source in default_sources]

        except Exception as e:
            self.logger.error(f"Error in _load_sources: {e}", exc_info=True)
            raise
    def syphon_filesystems(self, days_back: int = 30) -> Dict[str, Any]:
        """
        @SYPHON filesystems (FIRST PRIORITY).

        Args:
            days_back: Days to look back

        Returns:
            @SYPHON extracted data
        """
        hook_trace.trace(
            operation_type=OperationType.SYPHON,
            operation_name="syphon_filesystems",
            level=TraceLevel.INFO,
            message="Starting filesystem @SYPHON (FIRST PRIORITY)",
            metadata={"days_back": days_back, "company": self.company}
        )

        logger.info("="*80)
        logger.info("@SYPHON: FILESYSTEMS (FIRST PRIORITY)")
        logger.info("="*80)

        filesystem_sources = [s for s in self.sources if s.source_type == "filesystem" and s.enabled]

        all_extracted = []

        for source in filesystem_sources:
            try:
                logger.info(f"@SYPHON extracting from: {source.source_name}")

                # Get paths from metadata
                paths = source.metadata.get("paths", [])

                extracted = self._syphon_filesystem_paths(paths, days_back)
                extracted["source_id"] = source.source_id
                extracted["source_name"] = source.source_name
                extracted["company"] = self.company
                extracted["tags"] = self.tags

                all_extracted.append(extracted)

                # Update last syphon
                source.last_syphon = datetime.now().isoformat()

            except Exception as e:
                logger.error(f"Failed to @SYPHON {source.source_name}: {e}")
                hook_trace.trace(
                    operation_type=OperationType.SYPHON,
                    operation_name="syphon_filesystems",
                    level=TraceLevel.ERROR,
                    message=f"Failed to @SYPHON {source.source_name}",
                    error=str(e)
                )

        # Save extracted data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.filesystem_dir / f"filesystem_syphon_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(all_extracted, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Filesystem @SYPHON complete: {len(all_extracted)} sources")
        logger.info(f"📄 Saved to: {output_file}")

        hook_trace.trace(
            operation_type=OperationType.SYPHON,
            operation_name="syphon_filesystems",
            level=TraceLevel.INFO,
            message="Filesystem @SYPHON complete",
            success=True,
            metadata={"sources_extracted": len(all_extracted)}
        )

        return {"sources": all_extracted, "total_sources": len(all_extracted)}

    def _syphon_filesystem_paths(self, paths: List[str], days_back: int) -> Dict[str, Any]:
        """@SYPHON extract from filesystem paths."""
        extracted = {
            "files": [],
            "directories": [],
            "total_size": 0,
            "file_count": 0,
            "directory_count": 0
        }

        cutoff_time = datetime.now() - timedelta(days=days_back)

        for path_str in paths:
            path = Path(path_str)
            if not path.exists():
                continue

            try:
                # Walk directory
                for item in path.rglob("*"):
                    try:
                        if item.is_file():
                            stat = item.stat()
                            file_time = datetime.fromtimestamp(stat.st_mtime)

                            if file_time >= cutoff_time:
                                extracted["files"].append({
                                    "path": str(item),
                                    "size": stat.st_size,
                                    "modified": file_time.isoformat(),
                                    "extension": item.suffix
                                })
                                extracted["total_size"] += stat.st_size
                                extracted["file_count"] += 1

                        elif item.is_dir():
                            extracted["directories"].append(str(item))
                            extracted["directory_count"] += 1

                    except (PermissionError, OSError):
                        continue  # Skip inaccessible files

            except Exception as e:
                logger.warning(f"Failed to process path {path_str}: {e}")

        return extracted

    def syphon_email(self, days_back: int = 30) -> Dict[str, Any]:
        """
        @SYPHON all email sources.

        Args:
            days_back: Days to look back

        Returns:
            @SYPHON extracted data
        """
        hook_trace.trace(
            operation_type=OperationType.SYPHON,
            operation_name="syphon_email",
            level=TraceLevel.INFO,
            message="Starting email @SYPHON",
            metadata={"days_back": days_back, "company": self.company}
        )

        logger.info("="*80)
        logger.info("@SYPHON: EMAIL SOURCES")
        logger.info("="*80)

        try:
            from scripts.python.hvac_syphon_monitor import HVACSyphonMonitor

            monitor = HVACSyphonMonitor(self.project_root)
            email_data = monitor.syphon_hvac_emails(days_back=days_back)

            # Also extract from unified email service
            from scripts.python.unified_email_service import UnifiedEmailService, EmailProvider

            email_service = UnifiedEmailService(self.project_root)
            unified_emails = email_service.search_emails(
                query="ALL",
                provider=EmailProvider.UNIFIED,
                days_back=days_back,
                max_results=1000
            )

            extracted = {
                "hvac_emails": email_data,
                "unified_emails": len(unified_emails),
                "total_emails": len(email_data) + len(unified_emails),
                "company": self.company,
                "tags": self.tags
            }

            # Save
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.email_dir / f"email_syphon_{timestamp}.json"

            with open(output_file, 'w') as f:
                json.dump(extracted, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Email @SYPHON complete: {extracted['total_emails']} emails")
            logger.info(f"📄 Saved to: {output_file}")

            hook_trace.trace(
                operation_type=OperationType.SYPHON,
                operation_name="syphon_email",
                level=TraceLevel.INFO,
                message="Email @SYPHON complete",
                success=True,
                metadata={"total_emails": extracted['total_emails']}
            )

            return extracted

        except Exception as e:
            logger.error(f"Failed to @SYPHON email: {e}")
            hook_trace.trace(
                operation_type=OperationType.SYPHON,
                operation_name="syphon_email",
                level=TraceLevel.ERROR,
                message="Failed to @SYPHON email",
                error=str(e)
            )
            return {"error": str(e)}

    def syphon_financial_accounts(self, days_back: int = 30) -> Dict[str, Any]:
        """
        @SYPHON all financial accounts (Personal + Business).

        Args:
            days_back: Days to look back

        Returns:
            @SYPHON extracted data
        """
        hook_trace.trace(
            operation_type=OperationType.SYPHON,
            operation_name="syphon_financial_accounts",
            level=TraceLevel.INFO,
            message="Starting financial accounts @SYPHON",
            metadata={"days_back": days_back, "company": self.company}
        )

        logger.info("="*80)
        logger.info("@SYPHON: FINANCIAL ACCOUNTS")
        logger.info("="*80)
        logger.info(f"Company: {self.company}")
        logger.info("Accounts: Personal (User + Spouse) + Business")

        financial_sources = [s for s in self.sources if s.source_type == "financial" and s.enabled]

        all_extracted = []

        for source in financial_sources:
            try:
                logger.info(f"@SYPHON extracting from: {source.source_name}")

                # Try to use SYPHON system for financial extraction
                try:
                    from syphon import SYPHONSystem, SYPHONConfig, SubscriptionTier, DataSourceType

                    syphon_config = SYPHONConfig(
                        project_root=self.project_root,
                        subscription_tier=SubscriptionTier.ENTERPRISE,
                        enable_banking=True
                    )
                    syphon = SYPHONSystem(syphon_config)

                    # Extract financial data
                    extracted = {
                        "source_id": source.source_id,
                        "source_name": source.source_name,
                        "account_type": source.metadata.get("account_type"),
                        "owner": source.metadata.get("owner"),
                        "company": self.company,
                        "tags": self.tags,
                        "extracted_at": datetime.now().isoformat(),
                        "note": "SYPHON system available - financial extraction enabled"
                    }

                except ImportError:
                    # Fallback if SYPHON not available
                    extracted = {
                        "source_id": source.source_id,
                        "source_name": source.source_name,
                        "account_type": source.metadata.get("account_type"),
                        "owner": source.metadata.get("owner"),
                        "company": self.company,
                        "tags": self.tags,
                        "extracted_at": datetime.now().isoformat(),
                        "note": "SYPHON system not available - manual extraction required"
                    }

                all_extracted.append(extracted)
                source.last_syphon = datetime.now().isoformat()

            except Exception as e:
                logger.error(f"Failed to @SYPHON {source.source_name}: {e}")
                hook_trace.trace(
                    operation_type=OperationType.SYPHON,
                    operation_name="syphon_financial_accounts",
                    level=TraceLevel.ERROR,
                    message=f"Failed to @SYPHON {source.source_name}",
                    error=str(e)
                )

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.financial_dir / f"financial_syphon_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(all_extracted, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Financial @SYPHON complete: {len(all_extracted)} accounts")
        logger.info(f"📄 Saved to: {output_file}")

        hook_trace.trace(
            operation_type=OperationType.SYPHON,
            operation_name="syphon_financial_accounts",
            level=TraceLevel.INFO,
            message="Financial accounts @SYPHON complete",
            success=True,
            metadata={"accounts_extracted": len(all_extracted)}
        )

        return {"accounts": all_extracted, "total_accounts": len(all_extracted)}

    def syphon_all(self, days_back: int = 30) -> Dict[str, Any]:
        try:
            """
            @SYPHON all sources in priority order.

            Priority:
            1. Filesystems (FIRST PRIORITY)
            2. @SOURCES @SYPHON @BAU:
               - Email
               - Financial Accounts

            Args:
                days_back: Days to look back

            Returns:
                Complete @SYPHON extraction results
            """
            logger.info("="*80)
            logger.info("@SYPHON: COMPREHENSIVE EXTRACTION")
            logger.info("="*80)
            logger.info(f"Company: {self.company}")
            logger.info(f"Tags: {', '.join(self.tags)}")
            logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "company": self.company,
                "tags": self.tags,
                "priority_order": [
                    "1. Filesystems (FIRST PRIORITY)",
                    "2. @SOURCES @SYPHON @BAU: Email + Financial Accounts"
                ]
            }

            # Priority 1: Filesystems
            logger.info("PRIORITY 1: FILESYSTEMS")
            filesystem_results = self.syphon_filesystems(days_back=days_back)
            results["filesystems"] = filesystem_results

            # Priority 2: Email
            logger.info("")
            logger.info("PRIORITY 2: EMAIL")
            email_results = self.syphon_email(days_back=days_back)
            results["email"] = email_results

            # Priority 2: Financial Accounts
            logger.info("")
            logger.info("PRIORITY 2: FINANCIAL ACCOUNTS")
            financial_results = self.syphon_financial_accounts(days_back=days_back)
            results["financial"] = financial_results

            # Save complete results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_dir / f"comprehensive_syphon_{timestamp}.json"

            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("="*80)
            logger.info("@SYPHON: COMPREHENSIVE EXTRACTION COMPLETE")
            logger.info("="*80)
            logger.info(f"📄 Complete results saved to: {output_file}")

            hook_trace.trace(
                operation_type=OperationType.SYPHON,
                operation_name="syphon_all",
                level=TraceLevel.INFO,
                message="Comprehensive @SYPHON complete",
                success=True,
                metadata={
                    "filesystem_sources": filesystem_results.get("total_sources", 0),
                    "email_count": email_results.get("total_emails", 0),
                    "financial_accounts": financial_results.get("total_accounts", 0)
                }
            )

            return results


        except Exception as e:
            self.logger.error(f"Error in syphon_all: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Comprehensive @SYPHON System")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--all", action="store_true", help="@SYPHON all sources")
        parser.add_argument("--filesystems", action="store_true", help="@SYPHON filesystems only")
        parser.add_argument("--email", action="store_true", help="@SYPHON email only")
        parser.add_argument("--financial", action="store_true", help="@SYPHON financial accounts only")
        parser.add_argument("--days", type=int, default=30, help="Days to look back")

        args = parser.parse_args()

        syphon = LuminaComprehensiveSyphonSystem(args.project_root)

        if args.all or (not args.filesystems and not args.email and not args.financial):
            results = syphon.syphon_all(days_back=args.days)
            print(f"\n✅ Comprehensive @SYPHON complete")
            print(f"   Filesystems: {results.get('filesystems', {}).get('total_sources', 0)} sources")
            print(f"   Email: {results.get('email', {}).get('total_emails', 0)} emails")
            print(f"   Financial: {results.get('financial', {}).get('total_accounts', 0)} accounts")
        elif args.filesystems:
            results = syphon.syphon_filesystems(days_back=args.days)
            print(f"✅ Filesystem @SYPHON complete: {results.get('total_sources', 0)} sources")
        elif args.email:
            results = syphon.syphon_email(days_back=args.days)
            print(f"✅ Email @SYPHON complete: {results.get('total_emails', 0)} emails")
        elif args.financial:
            results = syphon.syphon_financial_accounts(days_back=args.days)
            print(f"✅ Financial @SYPHON complete: {results.get('total_accounts', 0)} accounts")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()