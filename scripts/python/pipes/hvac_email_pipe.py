"""
HVAC Email Pipe
Complete pipe for HVAC bid emails: Siphon → Extract → Analyze → Compare → Store

#JARVIS #LUMINA #PIPES #HVAC #EMAIL
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .core import Pipe, PipeStage, PipeStageType, PipeContext
from .syphon_stage import SyphonStage

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("HVACEmailPipe")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HVACEmailPipe")


class BidExtractionStage(PipeStage):
    """Extract bid data from siphoned emails."""

    def __init__(self, project_root: Path):
        """Initialize bid extraction stage."""
        super().__init__("bid_extraction", PipeStageType.TRANSFORM)
        self.project_root = Path(project_root)

    def process(self, context: PipeContext) -> PipeContext:
        """Extract bid data from emails."""
        from scripts.python.hvac_bid_extractor import BidExtractor

        siphoned_data = context.get_data("siphoned_data", {})
        emails = siphoned_data.get("emails", [])

        if not emails:
            context.add_warning("No emails found to extract bids from")
            return context

        extractor = BidExtractor(self.project_root)
        bids = []

        for email in emails:
            # Check for attachments
            attachments = getattr(email, 'attachments', []) or []

            for attachment in attachments:
                try:
                    # Download attachment if needed
                    attachment_path = self._get_attachment_path(attachment, email)

                    if attachment_path and attachment_path.exists():
                        # Extract bid data
                        contractor_name = self._identify_contractor(email)
                        bid_data = extractor.extract_from_file(attachment_path, contractor_name)

                        if bid_data:
                            bid_data["email_metadata"] = {
                                "from": email.from_address,
                                "subject": email.subject,
                                "date": email.date
                            }
                            bids.append(bid_data)

                except Exception as e:
                    context.add_warning(f"Failed to extract bid from attachment: {e}")

        context.add_data("extracted_bids", bids)
        context.add_data("bid_count", len(bids))

        logger.info(f"[{context.pipe_name}] ✅ Extracted {len(bids)} bid(s)")

        return context

    def _get_attachment_path(self, attachment: Dict, email) -> Optional[Path]:
        try:
            """Get attachment file path."""
            # If attachment has path, use it
            if isinstance(attachment, dict) and "path" in attachment:
                return Path(attachment["path"])

            # Otherwise, check if already downloaded
            # This would need to be implemented based on how attachments are stored
            return None

        except Exception as e:
            self.logger.error(f"Error in _get_attachment_path: {e}", exc_info=True)
            raise
    def _identify_contractor(self, email) -> str:
        """Identify contractor from email."""
        from_address = email.from_address.lower()
        subject = email.subject.lower()

        if "fletcher" in from_address or "fletcher" in subject:
            return "Brian Fletcher - Fletcher's Heating & Plumbing"
        elif "carl" in from_address or "king" in from_address or "griffet" in from_address:
            return "Carl-King| Griffet Energy Services"
        else:
            return "Unknown Contractor"


class HVACSMEAnalysisStage(PipeStage):
    """Analyze bids with HVAC SME expertise."""

    def __init__(self, project_root: Path):
        """Initialize HVAC SME analysis stage."""
        super().__init__("hvac_sme_analysis", PipeStageType.ANALYZE)
        self.project_root = Path(project_root)

    def process(self, context: PipeContext) -> PipeContext:
        """Analyze bids with HVAC SME."""
        from scripts.python.hvac_sme_analysis import HVACSMEAnalyzer

        bids = context.get_data("extracted_bids", [])

        if not bids:
            context.add_warning("No bids to analyze")
            return context

        analyzer = HVACSMEAnalyzer(self.project_root)
        analyses = []

        for bid in bids:
            contractor_name = bid.get("contractor_name", "Unknown")
            analysis = analyzer.analyze_bid(bid, contractor_name)
            analyses.append(analysis)

        context.add_data("sme_analyses", analyses)
        context.add_data("analysis_count", len(analyses))

        logger.info(f"[{context.pipe_name}] ✅ Analyzed {len(analyses)} bid(s) with HVAC SME")

        return context


class BidComparisonStage(PipeStage):
    """Compare all bids."""

    def __init__(self, project_root: Path, budget: float = 20000):
        """Initialize bid comparison stage."""
        super().__init__("bid_comparison", PipeStageType.ANALYZE)
        self.project_root = Path(project_root)
        self.budget = budget

    def process(self, context: PipeContext) -> PipeContext:
        """Compare all bids."""
        from scripts.python.hvac_bid_comparison import HVACBidComparator

        bids = context.get_data("extracted_bids", [])

        if not bids:
            context.add_warning("No bids to compare")
            return context

        comparator = HVACBidComparator(self.project_root)
        comparator.set_budget(self.budget)

        for bid in bids:
            comparator.import_bid_from_dict(bid)

        # Generate comparison
        comparison = comparator.get_comparison_summary()

        context.add_data("bid_comparison", comparison)
        context.add_data("budget", self.budget)

        logger.info(f"[{context.pipe_name}] ✅ Compared {len(bids)} bid(s)")

        return context


class StoreResultsStage(PipeStage):
    """Store results to filesystem."""

    def __init__(self, project_root: Path):
        """Initialize store results stage."""
        super().__init__("store_results", PipeStageType.STORE)
        self.project_root = Path(project_root)

    def process(self, context: PipeContext) -> PipeContext:
        try:
            """Store results."""
            import json
            from datetime import datetime

            data_dir = self.project_root / "data" / "hvac_bids"
            data_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Store bids
            bids = context.get_data("extracted_bids", [])
            if bids:
                bids_file = data_dir / f"bids_{timestamp}.json"
                with open(bids_file, 'w') as f:
                    json.dump(bids, f, indent=2, ensure_ascii=False, default=str)
                context.add_data("bids_file", str(bids_file))

            # Store analyses
            analyses = context.get_data("sme_analyses", [])
            if analyses:
                analyses_file = data_dir / f"sme_analyses_{timestamp}.json"
                with open(analyses_file, 'w') as f:
                    json.dump(analyses, f, indent=2, ensure_ascii=False, default=str)
                context.add_data("analyses_file", str(analyses_file))

            # Store comparison
            comparison = context.get_data("bid_comparison", {})
            if comparison:
                comparison_file = data_dir / f"comparison_{timestamp}.json"
                with open(comparison_file, 'w') as f:
                    json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)
                context.add_data("comparison_file", str(comparison_file))

            logger.info(f"[{context.pipe_name}] ✅ Stored results to {data_dir}")

            return context


        except Exception as e:
            self.logger.error(f"Error in process: {e}", exc_info=True)
            raise
class HVACEmailPipe(Pipe):
    """
    HVAC Email Pipe

    Complete pipe for HVAC bid emails:
    1. SYPHON: Siphon emails from source
    2. EXTRACT: Extract bid data from attachments
    3. ANALYZE: HVAC SME analysis
    4. COMPARE: Compare all bids
    5. STORE: Store results
    """

    def __init__(self, project_root: Path, budget: float = 20000):
        """
        Initialize HVAC Email Pipe.

        Args:
            project_root: Project root directory
            budget: Budget for comparison
        """
        super().__init__(
            name="hvac_email_pipe",
            project_root=project_root,
            description="HVAC bid email processing pipe: Siphon → Extract → Analyze → Compare → Store"
        )

        self.budget = budget

        # Build pipe stages
        self._build_pipe()

    def _build_pipe(self):
        """Build the pipe with all stages."""
        # Stage 1: SYPHON - Siphon emails from source
        syphon_stage = SyphonStage(
            name="siphon_emails",
            source_type="email",
            source_config={
                "project_root": str(self.project_root),
                "query": "hvac OR furnace OR \"air conditioning\" OR bid OR quote OR proposal",
                "days_back": 90
            }
        )

        # Stage 2: Extract bid data
        extraction_stage = BidExtractionStage(self.project_root)

        # Stage 3: HVAC SME analysis
        analysis_stage = HVACSMEAnalysisStage(self.project_root)

        # Stage 4: Compare bids
        comparison_stage = BidComparisonStage(self.project_root, self.budget)

        # Stage 5: Store results
        store_stage = StoreResultsStage(self.project_root)

        # Add all stages
        self.add_stages([
            syphon_stage,
            extraction_stage,
            analysis_stage,
            comparison_stage,
            store_stage
        ])

        logger.info(f"✅ HVAC Email Pipe built with {len(self.stages)} stages")


def create_hvac_email_pipe(project_root: Path, budget: float = 20000) -> HVACEmailPipe:
    """
    Factory function to create HVAC Email Pipe.

    Args:
        project_root: Project root directory
        budget: Budget for comparison

    Returns:
        Configured HVAC Email Pipe
    """
    return HVACEmailPipe(project_root, budget)
