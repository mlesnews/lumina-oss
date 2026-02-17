#!/usr/bin/env python3
"""
JARVIS Enhanced Summary Generator
Creates summaries with BOTH Helpdesk (PM123456789) and Git ticket numbers
Integrated with SYPHON, HOLOCRON, and JEDIARCHIVES for tracking

Tags: #JARVIS #SUMMARIES #SYPHON #HOLOCRON #JEDIARCHIVES @JARVIS @SYPHON @R5
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEnhancedSummaryGenerator")

try:
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem
    TICKET_SYSTEM_AVAILABLE = True
except ImportError:
    TICKET_SYSTEM_AVAILABLE = False
    logger.warning("Helpdesk ticket system not available")

try:
    from jarvis_gitlens_automation import JARVISGitLensAutomation
    GITLENS_AVAILABLE = True
except ImportError:
    GITLENS_AVAILABLE = False
    logger.debug("GitLens automation not available")

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.debug("SYPHON not available")

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    logger.debug("R5 not available")


class JARVISEnhancedSummaryGenerator:
    """
    Enhanced summary generator with dual ticket tracking (Helpdesk + Git)
    and full SYPHON/HOLOCRON/JEDIARCHIVES integration
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize enhanced summary generator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize systems
        self.ticket_system = None
        if TICKET_SYSTEM_AVAILABLE:
            try:
                self.ticket_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"Ticket system init failed: {e}")

        self.gitlens = None
        if GITLENS_AVAILABLE:
            try:
                self.gitlens = JARVISGitLensAutomation(repo_path=self.project_root, auto_commit=False)
            except Exception as e:
                logger.debug(f"GitLens init failed: {e}")

        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True
                )
                self.syphon = SYPHONSystem(config)
            except Exception as e:
                logger.debug(f"SYPHON init failed: {e}")

        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root=self.project_root)
            except Exception as e:
                logger.debug(f"R5 init failed: {e}")

        # Output directories
        self.summaries_dir = self.project_root / "data" / "summaries"
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Enhanced Summary Generator initialized")

    def create_enhanced_summary(
        self,
        title: str,
        content: str,
        helpdesk_ticket_id: Optional[str] = None,
        git_ticket_ref: Optional[str] = None,
        git_pr_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ingest_to_syphon: bool = True,
        ingest_to_holocron: bool = True,
        ingest_to_jediarchives: bool = True
    ) -> Dict[str, Any]:
        """
        Create enhanced summary with dual ticket tracking

        Args:
            title: Summary title
            content: Summary content
            helpdesk_ticket_id: PM123456789 format ticket ID
            git_ticket_ref: Git/GitLens ticket reference
            git_pr_number: GitHub PR number
            metadata: Additional metadata
            ingest_to_syphon: Ingest to SYPHON for tracking
            ingest_to_holocron: Ingest to HOLOCRON for archival
            ingest_to_jediarchives: Ingest to JEDIARCHIVES for organization

        Returns:
            Summary metadata
        """
        timestamp = datetime.now()
        summary_id = f"SUMMARY_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        # Build enhanced summary document
        summary_doc = {
            "summary_id": summary_id,
            "title": title,
            "content": content,
            "created_at": timestamp.isoformat(),
            "tickets": {
                "helpdesk_ticket": helpdesk_ticket_id,
                "git_ticket_ref": git_ticket_ref,
                "git_pr_number": git_pr_number
            },
            "tracking": {
                "syphon_ingested": False,
                "holocron_ingested": False,
                "jediarchives_ingested": False
            },
            "metadata": metadata or {}
        }

        # Generate formatted summary with ticket references
        formatted_summary = self._format_summary(summary_doc)

        # Save summary file
        summary_file = self.summaries_dir / f"{summary_id}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(formatted_summary)

        summary_json_file = self.summaries_dir / f"{summary_id}.json"
        with open(summary_json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_doc, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ Created summary: {summary_id}")

        # Ingest to SYPHON
        if ingest_to_syphon and self.syphon:
            try:
                syphon_result = self.syphon.extract(
                    source_type=DataSourceType.DOCUMENT,
                    content={
                        "title": title,
                        "content": content,
                        "tickets": summary_doc["tickets"],
                        "metadata": summary_doc["metadata"]
                    },
                    metadata={
                        "source": "jarvis_enhanced_summary",
                        "summary_id": summary_id,
                        "helpdesk_ticket": helpdesk_ticket_id,
                        "git_ticket_ref": git_ticket_ref,
                        "git_pr_number": git_pr_number
                    }
                )
                if syphon_result.success:
                    summary_doc["tracking"]["syphon_ingested"] = True
                    logger.info(f"   ✅ Ingested to SYPHON: {summary_id}")
            except Exception as e:
                logger.warning(f"   ⚠️  SYPHON ingestion failed: {e}")

        # Ingest to R5
        if self.r5:
            try:
                self.r5.ingest_session({
                    "session_id": summary_id,
                    "session_type": "enhanced_summary",
                    "timestamp": timestamp.isoformat(),
                    "content": formatted_summary,
                    "metadata": {
                        "tickets": summary_doc["tickets"],
                        **summary_doc["metadata"]
                    }
                })
                logger.info(f"   ✅ Ingested to R5: {summary_id}")
            except Exception as e:
                logger.debug(f"R5 ingestion failed: {e}")

        # Ingest to HOLOCRON
        if ingest_to_holocron:
            try:
                holocron_entry = self._create_holocron_entry(summary_doc)
                if holocron_entry:
                    summary_doc["tracking"]["holocron_ingested"] = True
                    logger.info(f"   ✅ Ingested to HOLOCRON: {summary_id}")
            except Exception as e:
                logger.warning(f"   ⚠️  HOLOCRON ingestion failed: {e}")

        # Update JSON file with tracking status
        with open(summary_json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_doc, f, indent=2, ensure_ascii=False, default=str)

        return summary_doc

    def _format_summary(self, summary_doc: Dict[str, Any]) -> str:
        try:
            """Format summary with ticket references"""
            lines = []

            lines.append(f"# {summary_doc['title']}")
            lines.append("")
            lines.append(f"**Summary ID:** {summary_doc['summary_id']}")
            lines.append(f"**Created:** {summary_doc['created_at']}")
            lines.append("")

            # Ticket references section
            tickets = summary_doc.get("tickets", {})
            if any(tickets.values()):
                lines.append("## Ticket References")
                lines.append("")

                if tickets.get("helpdesk_ticket"):
                    lines.append(f"- **Helpdesk Ticket:** `{tickets['helpdesk_ticket']}`")
                    # Get ticket details if available
                    if self.ticket_system:
                        ticket = self.ticket_system.get_ticket(tickets['helpdesk_ticket'])
                        if ticket:
                            lines.append(f"  - Title: {ticket.title}")
                            lines.append(f"  - Status: {ticket.status.value}")
                            lines.append(f"  - Priority: {ticket.priority.value}")

                if tickets.get("git_ticket_ref"):
                    lines.append(f"- **Git Ticket Reference:** `{tickets['git_ticket_ref']}`")

                if tickets.get("git_pr_number"):
                    lines.append(f"- **GitHub PR Number:** `#{tickets['git_pr_number']}`")
                    if self.gitlens:
                        # Try to get PR URL
                        repo_path = self._get_repo_path()
                        if repo_path:
                            lines.append(f"  - PR URL: https://github.com/{repo_path}/pull/{tickets['git_pr_number']}")

                lines.append("")

            # Content
            lines.append("## Summary")
            lines.append("")
            lines.append(summary_doc['content'])
            lines.append("")

            # Metadata
            if summary_doc.get("metadata"):
                lines.append("## Metadata")
                lines.append("")
                for key, value in summary_doc["metadata"].items():
                    if isinstance(value, (dict, list)):
                        lines.append(f"- **{key}:**")
                        lines.append(f"  ```json")
                        lines.append(f"  {json.dumps(value, indent=2)}")
                        lines.append(f"  ```")
                    else:
                        lines.append(f"- **{key}:** {value}")
                lines.append("")

            # Tracking status
            tracking = summary_doc.get("tracking", {})
            if any(tracking.values()):
                lines.append("## Tracking Status")
                lines.append("")
                lines.append(f"- **SYPHON Ingested:** {'✅' if tracking.get('syphon_ingested') else '❌'}")
                lines.append(f"- **HOLOCRON Ingested:** {'✅' if tracking.get('holocron_ingested') else '❌'}")
                lines.append(f"- **JEDIARCHIVES Ingested:** {'✅' if tracking.get('jediarchives_ingested') else '❌'}")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            self.logger.error(f"Error in _format_summary: {e}", exc_info=True)
            raise
    def _create_holocron_entry(self, summary_doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create HOLOCRON entry for summary"""
        try:
            from jarvis_tickets_to_holocron_db import TicketsToHolocronDB

            holocron_dir = self.project_root / "data" / "holocron" / "summaries"
            holocron_dir.mkdir(parents=True, exist_ok=True)

            entry_id = f"HOLOCRON-SUMMARY-{summary_doc['summary_id']}"

            # Create entry
            entry = {
                "entry_id": entry_id,
                "title": summary_doc['title'],
                "summary_id": summary_doc['summary_id'],
                "tickets": summary_doc.get("tickets", {}),
                "content": summary_doc['content'],
                "classification": "Enhanced Summary",
                "location": str(holocron_dir.relative_to(self.project_root)),
                "tags": [
                    "#summary",
                    "#enhanced",
                    "#syphon",
                    "#holocron"
                ],
                "metadata": {
                    "created_at": summary_doc['created_at'],
                    "tracking": summary_doc.get("tracking", {}),
                    **summary_doc.get("metadata", {})
                }
            }

            # Save entry
            entry_file = holocron_dir / f"{summary_doc['summary_id']}.json"
            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump(entry, f, indent=2, ensure_ascii=False, default=str)

            # Update HOLOCRON index
            index_file = self.project_root / "data" / "holocron" / "HOLOCRON_INDEX.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"entries": {}}

            if "summaries" not in index["entries"]:
                index["entries"]["summaries"] = {}

            index["entries"]["summaries"][entry_id] = entry
            index["archive_metadata"] = {
                "last_updated": datetime.now().isoformat()
            }

            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)

            return entry

        except Exception as e:
            logger.warning(f"HOLOCRON entry creation failed: {e}")
            return None

    def _get_repo_path(self) -> Optional[str]:
        """Get GitHub repo path"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                import re
                match = re.search(r'github\.com[:/]([^/]+/[^/]+)', url)
                if match:
                    return match.group(1).replace('.git', '')
        except Exception:
            pass
        return None


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Enhanced Summary Generator")
        parser.add_argument("--title", type=str, required=True, help="Summary title")
        parser.add_argument("--content", type=str, required=True, help="Summary content")
        parser.add_argument("--helpdesk-ticket", type=str, help="Helpdesk ticket ID (PM123456789)")
        parser.add_argument("--git-ticket", type=str, help="Git ticket reference")
        parser.add_argument("--git-pr", type=int, help="GitHub PR number")

        args = parser.parse_args()

        generator = JARVISEnhancedSummaryGenerator()

        summary = generator.create_enhanced_summary(
            title=args.title,
            content=args.content,
            helpdesk_ticket_id=args.helpdesk_ticket,
            git_ticket_ref=args.git_ticket,
            git_pr_number=args.git_pr
        )

        print(json.dumps(summary, indent=2, default=str))
        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())