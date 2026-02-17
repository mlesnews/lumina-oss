#!/usr/bin/env python3
"""
TPS Reports - Daily Morning Briefing Generator

Generates daily morning briefing reports with:
- All major/minor events from previous day (before midnight)
- @PEAK references and quantification
- Internal URLs to holocrons (copy-paste friendly)
- Integration with lumina-complete extension

Tags: #TPS-REPORTS #DAILY-BRIEFING #PEAK #HOLOCRON #URLS #LUMINA
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

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

logger = get_logger("TPSReports")


@dataclass
class HolocronReference:
    """Holocron reference with internal URL"""
    holocron_id: str
    title: str
    timestamp: str
    importance_score: int
    internal_url: str  # file:// URL for copy-paste
    peak_reference: Optional[str] = None  # @PEAK reference if applicable


@dataclass
class EventEntry:
    """Event entry for TPS report"""
    event_id: str
    timestamp: str
    title: str
    category: str  # major, minor
    description: str
    holocron_refs: List[HolocronReference]
    peak_percentage: Optional[float] = None
    tags: List[str] = None


@dataclass
class TPSReport:
    """TPS Report structure"""
    report_date: str
    report_id: str
    previous_day: str
    generated_at: str
    summary: Dict[str, Any]
    major_events: List[EventEntry]
    minor_events: List[EventEntry]
    holocron_references: List[HolocronReference]
    peak_summary: Dict[str, float]
    internal_urls: List[str]  # All copy-paste friendly URLs


class TPSReportsGenerator:
    """TPS Reports Generator"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.holocrons_dir = self.project_root / "data" / "holocrons"
        self.captains_log_dir = self.project_root / "data" / "captains_log"
        self.secret_holocron_dir = self.project_root / "data" / "secret_holocron" / "blackbox"
        self.reports_dir = self.project_root / "data" / "tps_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_internal_url(self, file_path: Path) -> str:
        """
        Generate internal file:// URL for copy-paste

        Args:
            file_path: Path to file

        Returns:
            file:// URL string
        """
        # Convert to absolute path
        abs_path = file_path.resolve()

        # Generate file:// URL
        # Windows: file:///C:/path/to/file
        # Unix: file:///path/to/file
        if sys.platform == "win32":
            # Windows: file:///C:/Users/...
            path_str = str(abs_path)
            path_str = path_str.replace('\\', '/')
            url = f"file:///{path_str}"
        else:
            # Unix: file:///home/...
            url = f"file://{abs_path}"

        return url

    def load_holocron(self, holocron_file: Path) -> Optional[Dict[str, Any]]:
        """Load holocron JSON file"""
        try:
            with open(holocron_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load holocron {holocron_file}: {e}")
            return None

    def get_holocrons_from_date(self, target_date: datetime) -> List[HolocronReference]:
        """
        Get all holocrons from a specific date (before midnight)

        Args:
            target_date: Target date

        Returns:
            List of HolocronReference objects
        """
        holocrons = []
        date_str = target_date.strftime('%Y%m%d')

        # Find all holocron files from that date
        for holocron_file in self.holocrons_dir.glob(f"HOLO-{date_str}-*.json"):
            holocron_data = self.load_holocron(holocron_file)
            if holocron_data:
                # Extract timestamp
                timestamp_str = holocron_data.get("timestamp", "")
                try:
                    holocron_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    # Check if before midnight of target date
                    midnight = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    if holocron_timestamp <= midnight:
                        # Create internal URL
                        internal_url = self.generate_internal_url(holocron_file)

                        # Extract title from data
                        data = holocron_data.get("data", {})
                        title = data.get("title", holocron_data.get("holocron_id", "Unknown"))

                        holocron_ref = HolocronReference(
                            holocron_id=holocron_data.get("holocron_id", ""),
                            title=title,
                            timestamp=timestamp_str,
                            importance_score=holocron_data.get("importance_score", 0),
                            internal_url=internal_url
                        )
                        holocrons.append(holocron_ref)
                except Exception as e:
                    logger.warning(f"Failed to parse timestamp for {holocron_file}: {e}")

        # Sort by timestamp
        holocrons.sort(key=lambda x: x.timestamp)
        return holocrons

    def extract_peak_reference(self, holocron_data: Dict[str, Any]) -> Optional[str]:
        """Extract @PEAK reference from holocron data"""
        data = holocron_data.get("data", {})

        # Look for peak references in various fields
        if "peak_percentage" in data:
            return f"@PEAK: {data['peak_percentage']}%"
        if "peak" in str(data).lower():
            # Try to find peak mentions
            for key, value in data.items():
                if "peak" in str(key).lower() or "peak" in str(value).lower():
                    return f"@PEAK referenced in {key}"

        return None

    def categorize_event(self, holocron_ref: HolocronReference) -> str:
        """
        Categorize event as major or minor

        Args:
            holocron_ref: Holocron reference

        Returns:
            "major" or "minor"
        """
        # Major events: high importance score or specific tags
        if holocron_ref.importance_score >= 80:
            return "major"

        # Check title for major keywords
        title_lower = holocron_ref.title.lower()
        major_keywords = ["matrix", "reality", "physics", "mission", "engage", "kobayashi", "initiative"]
        if any(keyword in title_lower for keyword in major_keywords):
            return "major"

        return "minor"

    def generate_tps_report(self, target_date: Optional[datetime] = None) -> TPSReport:
        """
        Generate TPS report for a specific date

        Args:
            target_date: Target date (default: yesterday)

        Returns:
            TPSReport object
        """
        if target_date is None:
            # Default to yesterday
            target_date = datetime.now() - timedelta(days=1)

        # Get all holocrons from previous day
        holocrons = self.get_holocrons_from_date(target_date)

        # Categorize events
        major_events = []
        minor_events = []

        for holocron_ref in holocrons:
            # Load full holocron data for peak extraction
            holocron_file = self.holocrons_dir / f"{holocron_ref.holocron_id}.json"
            holocron_data = self.load_holocron(holocron_file)

            if holocron_data:
                peak_ref = self.extract_peak_reference(holocron_data)
                holocron_ref.peak_reference = peak_ref

            # Create event entry
            category = self.categorize_event(holocron_ref)
            event = EventEntry(
                event_id=holocron_ref.holocron_id,
                timestamp=holocron_ref.timestamp,
                title=holocron_ref.title,
                category=category,
                description=f"Holocron entry: {holocron_ref.title}",
                holocron_refs=[holocron_ref],
                peak_percentage=float(holocron_ref.peak_reference.split(':')[1].replace('%', '').strip()) if holocron_ref.peak_reference and ':' in holocron_ref.peak_reference else None,
                tags=holocron_data.get("tags", []) if holocron_data else []
            )

            if category == "major":
                major_events.append(event)
            else:
                minor_events.append(event)

        # Generate summary
        summary = {
            "total_events": len(holocrons),
            "major_events_count": len(major_events),
            "minor_events_count": len(minor_events),
            "holocrons_created": len(holocrons),
            "date": target_date.strftime('%Y-%m-%d')
        }

        # Calculate peak summary
        peak_values = [e.peak_percentage for e in major_events + minor_events if e.peak_percentage is not None]
        peak_summary = {
            "average_peak": sum(peak_values) / len(peak_values) if peak_values else 0.0,
            "max_peak": max(peak_values) if peak_values else 0.0,
            "min_peak": min(peak_values) if peak_values else 0.0,
            "events_with_peak": len(peak_values)
        }

        # Collect all internal URLs
        internal_urls = [ref.internal_url for ref in holocrons]

        # Generate report
        report_id = f"TPS-{target_date.strftime('%Y%m%d')}"
        report = TPSReport(
            report_date=target_date.strftime('%Y-%m-%d'),
            report_id=report_id,
            previous_day=target_date.strftime('%Y-%m-%d'),
            generated_at=datetime.now().isoformat(),
            summary=summary,
            major_events=major_events,
            minor_events=minor_events,
            holocron_references=holocrons,
            peak_summary=peak_summary,
            internal_urls=internal_urls
        )

        return report

    def format_report_for_display(self, report: TPSReport) -> str:
        """Format TPS report for display with copy-paste friendly URLs"""
        lines = []

        lines.append("=" * 80)
        lines.append("📋 TPS REPORTS - DAILY MORNING BRIEFING")
        lines.append("=" * 80)
        lines.append(f"Report Date: {report.report_date}")
        lines.append(f"Previous Day: {report.previous_day}")
        lines.append(f"Generated At: {report.generated_at}")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append("SUMMARY:")
        lines.append(f"  Total Events: {report.summary['total_events']}")
        lines.append(f"  Major Events: {report.summary['major_events_count']}")
        lines.append(f"  Minor Events: {report.summary['minor_events_count']}")
        lines.append(f"  Holocrons Created: {report.summary['holocrons_created']}")
        lines.append("")

        # @PEAK Summary
        lines.append("@PEAK SUMMARY:")
        lines.append(f"  Average @PEAK: {report.peak_summary['average_peak']:.2f}%")
        lines.append(f"  Max @PEAK: {report.peak_summary['max_peak']:.2f}%")
        lines.append(f"  Min @PEAK: {report.peak_summary['min_peak']:.2f}%")
        lines.append(f"  Events with @PEAK: {report.peak_summary['events_with_peak']}")
        lines.append("")

        # Major Events
        if report.major_events:
            lines.append("MAJOR EVENTS:")
            for event in report.major_events:
                lines.append(f"  [{event.timestamp}] {event.title}")
                if event.peak_reference:
                    lines.append(f"    {event.peak_reference}")
                for ref in event.holocron_refs:
                    lines.append(f"    📎 {ref.holocron_id}")
                    lines.append(f"       {ref.internal_url}")
                lines.append("")

        # Minor Events
        if report.minor_events:
            lines.append("MINOR EVENTS:")
            for event in report.minor_events:
                lines.append(f"  [{event.timestamp}] {event.title}")
                if event.peak_reference:
                    lines.append(f"    {event.peak_reference}")
                for ref in event.holocron_refs:
                    lines.append(f"    📎 {ref.holocron_id}")
                    lines.append(f"       {ref.internal_url}")
                lines.append("")

        # All Holocron URLs (Copy-Paste Section)
        lines.append("=" * 80)
        lines.append("📋 ALL HOLOCRON INTERNAL URLs (COPY-PASTE READY):")
        lines.append("=" * 80)
        for i, url in enumerate(report.internal_urls, 1):
            lines.append(f"{i}. {url}")
        lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def save_report(self, report: TPSReport) -> Path:
        try:
            """Save TPS report to JSON file"""
            report_file = self.reports_dir / f"{report.report_id}.json"

            # Convert dataclasses to dicts
            report_dict = {
                "report_id": report.report_id,
                "report_date": report.report_date,
                "previous_day": report.previous_day,
                "generated_at": report.generated_at,
                "summary": report.summary,
                "major_events": [
                    {
                        "event_id": e.event_id,
                        "timestamp": e.timestamp,
                        "title": e.title,
                        "category": e.category,
                        "description": e.description,
                        "holocron_refs": [
                            {
                                "holocron_id": r.holocron_id,
                                "title": r.title,
                                "timestamp": r.timestamp,
                                "importance_score": r.importance_score,
                                "internal_url": r.internal_url,
                                "peak_reference": r.peak_reference
                            }
                            for r in e.holocron_refs
                        ],
                        "peak_percentage": e.peak_percentage,
                        "tags": e.tags or []
                    }
                    for e in report.major_events
                ],
                "minor_events": [
                    {
                        "event_id": e.event_id,
                        "timestamp": e.timestamp,
                        "title": e.title,
                        "category": e.category,
                        "description": e.description,
                        "holocron_refs": [
                            {
                                "holocron_id": r.holocron_id,
                                "title": r.title,
                                "timestamp": r.timestamp,
                                "importance_score": r.importance_score,
                                "internal_url": r.internal_url,
                                "peak_reference": r.peak_reference
                            }
                            for r in e.holocron_refs
                        ],
                        "peak_percentage": e.peak_percentage,
                        "tags": e.tags or []
                    }
                    for e in report.minor_events
                ],
                "holocron_references": [
                    {
                        "holocron_id": r.holocron_id,
                        "title": r.title,
                        "timestamp": r.timestamp,
                        "importance_score": r.importance_score,
                        "internal_url": r.internal_url,
                        "peak_reference": r.peak_reference
                    }
                    for r in report.holocron_references
                ],
                "peak_summary": report.peak_summary,
                "internal_urls": report.internal_urls
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ TPS Report saved: {report_file}")
            return report_file

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
    def generate_daily_briefing(self, target_date: Optional[datetime] = None) -> TPSReport:
        """
        Generate daily morning briefing

        Args:
            target_date: Target date (default: yesterday)

        Returns:
            TPSReport object
        """
        logger.info("=" * 80)
        logger.info("📋 GENERATING TPS REPORTS - DAILY MORNING BRIEFING")
        logger.info("=" * 80)

        report = self.generate_tps_report(target_date)
        report_file = self.save_report(report)

        # Format and print
        formatted_report = self.format_report_for_display(report)
        print(formatted_report)

        logger.info(f"✅ TPS Report generated: {report.report_id}")
        logger.info(f"   Report file: {report_file}")
        logger.info("=" * 80)

        return report


def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent
        generator = TPSReportsGenerator(project_root)

        # Generate report for yesterday
        report = generator.generate_daily_briefing()

        return report


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()