#!/usr/bin/env python3
"""
@ask Ticket Pattern Analyzer

Analyzes ticket patterns, identifies recurrences, and collates similar tickets
to extract actionable insights and identify systemic issues.

Tags: #ASK #PATTERNS #RECURRENCE #ANALYSIS #SYPHON @JARVIS @LUMINA
"""

import difflib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ask_ticket_collation_system import AskTicketCollationSystem, AskTicketRecord
from lumina_core.paths import get_script_dir

script_dir = get_script_dir()
project_root_global = script_dir.parent.parent
from lumina_core.paths import setup_paths

setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name: str):
        """Fallback logger"""
        return logging.getLogger(name)

logger = get_logger("AskTicketPatternAnalyzer")


@dataclass
class PatternGroup:
    """Group of similar tickets forming a pattern"""
    pattern_id: str
    pattern_name: str
    pattern_type: str  # recurrence, similarity, systemic
    tickets: List[str]  # List of ask_ids
    common_tags: List[str]
    common_patterns: List[str]
    frequency: int
    first_occurrence: str
    last_occurrence: str
    affected_teams: List[str]
    severity: str  # low, medium, high, critical
    insights: List[str]
    recommendations: List[str]


@dataclass
class RecurrenceReport:
    """Report on ticket recurrences"""
    report_id: str
    generated_at: str
    time_period: str
    total_tickets: int
    unique_patterns: int
    pattern_groups: List[PatternGroup]
    area_breakdown: Dict[str, Any]  # Breakdown by team, tag, pattern type
    top_recurrences: List[Dict[str, Any]]
    systemic_issues: List[Dict[str, Any]]


class AskTicketPatternAnalyzer:
    """
    Pattern Analyzer for @ask tickets

    Identifies recurrences, collates similar tickets, and extracts patterns
    for reporting and systemic issue detection.
    """

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize pattern analyzer"""
        if root_path is None:
            from lumina_core.paths import get_project_root
            self.project_root = Path(get_project_root())
        else:
            self.project_root = Path(root_path)

        self.collation_system = AskTicketCollationSystem(self.project_root)
        self.data_dir = self.project_root / "data" / "ask_ticket_collation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ @ask Ticket Pattern Analyzer initialized")

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using sequence matching"""
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text for pattern matching"""
        # Remove common words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by'
        }
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = {w for w in words if len(w) > 3 and w not in stop_words}
        return keywords

    def _find_similar_tickets(
        self,
        records: List[AskTicketRecord],
        similarity_threshold: float = 0.6
    ) -> List[Tuple[str, str, float]]:
        """
        Find similar tickets based on text similarity

        Returns:
            List of tuples (ask_id1, ask_id2, similarity_score)
        """
        similar_pairs = []

        for i, record1 in enumerate(records):
            for record2 in records[i+1:]:
                # Calculate similarity on ask_text
                similarity = self._calculate_similarity(
                    record1.ask_text,
                    record2.ask_text
                )

                if similarity >= similarity_threshold:
                    similar_pairs.append((
                        record1.ask_id,
                        record2.ask_id,
                        similarity
                    ))

        return similar_pairs

    def _group_by_patterns(
        self,
        records: List[AskTicketRecord]
    ) -> Dict[str, List[AskTicketRecord]]:
        """Group records by syphon patterns"""
        pattern_groups = defaultdict(list)

        for record in records:
            if record.syphon_patterns:
                for pattern in record.syphon_patterns:
                    pattern_groups[pattern].append(record)
            else:
                pattern_groups["no_pattern"].append(record)

        return dict(pattern_groups)

    def _group_by_tags(
        self,
        records: List[AskTicketRecord]
    ) -> Dict[str, List[AskTicketRecord]]:
        """Group records by tags"""
        tag_groups = defaultdict(list)

        for record in records:
            for tag in record.tags:
                tag_groups[tag].append(record)

        return dict(tag_groups)

    def _group_by_team(
        self,
        records: List[AskTicketRecord]
    ) -> Dict[str, List[AskTicketRecord]]:
        """Group records by assigned team"""
        team_groups = defaultdict(list)

        for record in records:
            team = record.assigned_team or "UNASSIGNED"
            team_groups[team].append(record)

        return dict(team_groups)

    def _identify_recurrences(
        self,
        records: List[AskTicketRecord],
        time_window_days: int = 30
    ) -> List[PatternGroup]:
        """
        Identify recurring patterns in tickets

        Args:
            records: List of ticket records
            time_window_days: Time window for recurrence analysis

        Returns:
            List of PatternGroup objects
        """
        pattern_groups = []

        # Group by patterns
        pattern_dict = self._group_by_patterns(records)

        for pattern_type, pattern_records in pattern_dict.items():
            if len(pattern_records) < 2:  # Need at least 2 for recurrence
                continue

            # Find common elements
            common_tags = set(pattern_records[0].tags)
            for record in pattern_records[1:]:
                common_tags &= set(record.tags)

            common_patterns = set(pattern_records[0].syphon_patterns)
            for record in pattern_records[1:]:
                common_patterns &= set(record.syphon_patterns)

            # Get time range
            dates = [datetime.fromisoformat(r.created_at) for r in pattern_records]
            first_occurrence = min(dates).isoformat()
            last_occurrence = max(dates).isoformat()

            # Calculate frequency
            time_span = (max(dates) - min(dates)).days + 1
            frequency = len(pattern_records) / max(time_span, 1) * 30  # Per month

            # Get affected teams
            affected_teams = list(set(
                r.assigned_team for r in pattern_records if r.assigned_team
            ))

            # Determine severity
            if len(pattern_records) >= 10:
                severity = "critical"
            elif len(pattern_records) >= 5:
                severity = "high"
            elif len(pattern_records) >= 3:
                severity = "medium"
            else:
                severity = "low"

            # Generate insights
            insights = [
                f"Pattern '{pattern_type}' occurred {len(pattern_records)} times",
                f"Affects {len(affected_teams)} team(s): {', '.join(affected_teams)}",
                f"Time span: {time_span} days",
                f"Frequency: {frequency:.2f} occurrences per month"
            ]

            # Generate recommendations
            recommendations = []
            if severity in ["high", "critical"]:
                recommendations.append(
                    f"Investigate root cause of recurring {pattern_type} pattern"
                )
                recommendations.append(f"Consider systemic fix for {pattern_type} issues")
            if len(affected_teams) > 1:
                recommendations.append(
                    f"Coordinate across teams: {', '.join(affected_teams)}"
                )

            pattern_group = PatternGroup(
                pattern_id=f"pattern_{pattern_type}_{len(pattern_groups)}",
                pattern_name=f"{pattern_type} Recurrence",
                pattern_type="recurrence",
                tickets=[r.ask_id for r in pattern_records],
                common_tags=list(common_tags),
                common_patterns=list(common_patterns),
                frequency=len(pattern_records),
                first_occurrence=first_occurrence,
                last_occurrence=last_occurrence,
                affected_teams=affected_teams,
                severity=severity,
                insights=insights,
                recommendations=recommendations
            )

            pattern_groups.append(pattern_group)

        return pattern_groups

    def _identify_similar_tickets(
        self,
        records: List[AskTicketRecord],
        similarity_threshold: float = 0.7
    ) -> List[PatternGroup]:
        """
        Identify similar tickets based on text similarity

        Returns:
            List of PatternGroup objects for similar tickets
        """
        similar_pairs = self._find_similar_tickets(records, similarity_threshold)

        # Group similar tickets
        groups = {}
        group_id_counter = 0

        for ask_id1, ask_id2, similarity in similar_pairs:
            # Find existing group
            found_group = None
            for gid, group in groups.items():
                if ask_id1 in group["tickets"] or ask_id2 in group["tickets"]:
                    found_group = gid
                    break

            if found_group:
                groups[found_group]["tickets"].add(ask_id1)
                groups[found_group]["tickets"].add(ask_id2)
                groups[found_group]["similarities"].append(similarity)
            else:
                groups[group_id_counter] = {
                    "tickets": {ask_id1, ask_id2},
                    "similarities": [similarity]
                }
                group_id_counter += 1

        # Convert to PatternGroup objects
        pattern_groups = []
        records_dict = {r.ask_id: r for r in records}

        for gid, group_data in groups.items():
            ticket_ids = list(group_data["tickets"])
            if len(ticket_ids) < 2:
                continue

            group_records = [
                records_dict[tid] for tid in ticket_ids if tid in records_dict
            ]
            if not group_records:
                continue

            # Find common elements
            common_tags = set(group_records[0].tags)
            for record in group_records[1:]:
                common_tags &= set(record.tags)

            avg_sim = sum(group_data["similarities"]) / len(group_data["similarities"])

            dates = [datetime.fromisoformat(r.created_at) for r in group_records]
            first_occurrence = min(dates).isoformat()
            last_occurrence = max(dates).isoformat()

            affected_teams = list(set(
                r.assigned_team for r in group_records if r.assigned_team
            ))

            severity = ("high" if len(ticket_ids) >= 5
                        else "medium" if len(ticket_ids) >= 3 else "low")

            insights = [
                f"Found {len(ticket_ids)} similar tickets",
                f"Average similarity: {avg_sim:.2%}",
                f"Common tags: {', '.join(list(common_tags)[:5])}"
            ]

            recommendations = [
                "Review similar tickets for potential consolidation",
                "Identify common root cause",
                "Consider template or automation for similar requests"
            ]

            pattern_group = PatternGroup(
                pattern_id=f"similar_{gid}",
                pattern_name=f"Similar Tickets Group {gid}",
                pattern_type="similarity",
                tickets=ticket_ids,
                common_tags=list(common_tags),
                common_patterns=[],
                frequency=len(ticket_ids),
                first_occurrence=first_occurrence,
                last_occurrence=last_occurrence,
                affected_teams=affected_teams,
                severity=severity,
                insights=insights,
                recommendations=recommendations
            )

            pattern_groups.append(pattern_group)

        return pattern_groups

    def generate_recurrence_report(
        self,
        time_period_days: int = 30,
        area: Optional[str] = None,
        area_type: str = "team"  # team, tag, pattern
    ) -> RecurrenceReport:
        """
        Generate recurrence report for tickets

        Args:
            time_period_days: Number of days to analyze
            area: Specific area to analyze (team name, tag, pattern type)
            area_type: Type of area (team, tag, pattern)

        Returns:
            RecurrenceReport with analysis
        """
        logger.info("📊 Generating recurrence report (last %d days)", time_period_days)

        # Query records
        cutoff_date = (datetime.now() - timedelta(days=time_period_days)).isoformat()
        all_records = self.collation_system.query()

        # Filter by time period
        records = [
            r for r in all_records
            if r.created_at >= cutoff_date
        ]

        # Filter by area if specified
        if area:
            if area_type == "team":
                records = [r for r in records if r.assigned_team == area]
            elif area_type == "tag":
                records = [r for r in records if area in r.tags]
            elif area_type == "pattern":
                records = [r for r in records if area in r.syphon_patterns]

        logger.info("   Analyzing %d tickets", len(records))

        # Identify recurrences
        recurrence_patterns = self._identify_recurrences(records, time_period_days)

        # Identify similar tickets
        similar_patterns = self._identify_similar_tickets(records)

        # Combine patterns
        all_patterns = recurrence_patterns + similar_patterns

        # Area breakdown
        team_breakdown = self._group_by_team(records)
        tag_breakdown = self._group_by_tags(records)
        pattern_breakdown = self._group_by_patterns(records)

        area_breakdown = {
            "by_team": {
                team: {
                    "count": len(team_records),
                    "tickets": [r.ask_id for r in team_records]
                }
                for team, team_records in team_breakdown.items()
            },
            "by_tag": {
                tag: {
                    "count": len(tag_records),
                    "tickets": [r.ask_id for r in tag_records]
                }
                for tag, tag_records in tag_breakdown.items()
            },
            "by_pattern": {
                pattern: {
                    "count": len(pattern_records),
                    "tickets": [r.ask_id for r in pattern_records]
                }
                for pattern, pattern_records in pattern_breakdown.items()
            }
        }

        # Top recurrences
        top_recurrences = sorted(
            all_patterns,
            key=lambda p: p.frequency,
            reverse=True
        )[:10]

        # Systemic issues (high frequency, multiple teams)
        systemic_issues = [
            {
                "pattern_id": p.pattern_id,
                "pattern_name": p.pattern_name,
                "frequency": p.frequency,
                "affected_teams": p.affected_teams,
                "severity": p.severity,
                "insights": p.insights,
                "recommendations": p.recommendations
            }
            for p in all_patterns
            if p.frequency >= 5 and len(p.affected_teams) > 1
        ]

        report = RecurrenceReport(
            report_id=f"recurrence_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.now().isoformat(),
            time_period=f"Last {time_period_days} days",
            total_tickets=len(records),
            unique_patterns=len(all_patterns),
            pattern_groups=all_patterns,
            area_breakdown=area_breakdown,
            top_recurrences=[asdict(p) for p in top_recurrences],
            systemic_issues=systemic_issues
        )

        logger.info("✅ Generated recurrence report")
        logger.info("   Total tickets: %d", len(records))
        logger.info("   Unique patterns: %d", len(all_patterns))
        logger.info("   Systemic issues: %d", len(systemic_issues))

        return report

    def collate_similar_tickets(
        self,
        pattern_group: PatternGroup
    ) -> Dict[str, Any]:
        """
        Collate similar tickets from a pattern group

        Returns:
            Dictionary with collated analysis
        """
        records = [
            self.collation_system.query(ask_id=tid)[0]
            for tid in pattern_group.tickets
            if self.collation_system.query(ask_id=tid)
        ]

        if not records:
            return {"error": "No records found for pattern group"}

        # Extract commonalities
        common_tags = set(records[0].tags)
        for record in records[1:]:
            common_tags &= set(record.tags)

        common_patterns = set(records[0].syphon_patterns)
        for record in records[1:]:
            common_patterns &= set(record.syphon_patterns)

        # Extract keywords
        all_keywords = set()
        for record in records:
            all_keywords.update(self._extract_keywords(record.ask_text))

        # Find most common keywords
        keyword_counts = Counter()
        for record in records:
            keywords = self._extract_keywords(record.ask_text)
            keyword_counts.update(keywords)

        top_keywords = [word for word, count in keyword_counts.most_common(10)]

        # Time span calc
        max_date = datetime.fromisoformat(max(r.created_at for r in records))
        min_date = datetime.fromisoformat(min(r.created_at for r in records))
        time_span = (max_date - min_date).days + 1

        return {
            "pattern_group": asdict(pattern_group),
            "collated_analysis": {
                "total_tickets": len(records),
                "common_tags": list(common_tags),
                "common_patterns": list(common_patterns),
                "top_keywords": top_keywords,
                "affected_teams": list(set(
                    r.assigned_team for r in records if r.assigned_team
                )),
                "time_span_days": time_span,
                "tickets": [r.ask_id for r in records]
            }
        }

    def save_report(
        self,
        report: RecurrenceReport,
        output_path: Optional[Path] = None
    ) -> Path:
        """Save report to JSON file"""
        if output_path is None:
            output_path = self.data_dir / f"recurrence_report_{report.report_id}.json"

        report_dict = {
            "report_id": report.report_id,
            "generated_at": report.generated_at,
            "time_period": report.time_period,
            "total_tickets": report.total_tickets,
            "unique_patterns": report.unique_patterns,
            "pattern_groups": [asdict(pg) for pg in report.pattern_groups],
            "area_breakdown": report.area_breakdown,
            "top_recurrences": report.top_recurrences,
            "systemic_issues": report.systemic_issues
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info("✅ Saved report to %s", output_path)
        return output_path


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="@ask Ticket Pattern Analyzer - Recurrence and pattern analysis"
        )
        parser.add_argument("--report", type=int, default=30, metavar="DAYS",
                           help="Generate recurrence report for last N days")
        parser.add_argument("--area", metavar="AREA",
                            help="Filter by area (team, tag, or pattern)")
        parser.add_argument("--area-type", choices=["team", "tag", "pattern"],
                            default="team", help="Type of area filter")
        parser.add_argument("--collate", metavar="PATTERN_ID",
                            help="Collate similar tickets for pattern")
        parser.add_argument("--output", metavar="PATH", help="Output file path")

        args = parser.parse_args()

        analyzer = AskTicketPatternAnalyzer()

        if args.collate:
            # Collate specific pattern
            all_records = analyzer.collation_system.query()
            patterns = analyzer._identify_recurrences(all_records)
            pattern = next((p for p in patterns if p.pattern_id == args.collate), None)

            if pattern:
                result = analyzer.collate_similar_tickets(pattern)
                print(f"\n📋 Collated analysis for pattern: {args.collate}")
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Pattern not found: {args.collate}")

        else:
            # Generate report
            report = analyzer.generate_recurrence_report(
                time_period_days=args.report,
                area=args.area,
                area_type=args.area_type
            )

            output_path = analyzer.save_report(
                report, Path(args.output) if args.output else None
            )

            print("\n📊 Recurrence Report Generated")
            print(f"   Report ID: {report.report_id}")
            print(f"   Total tickets: {report.total_tickets}")
            print(f"   Unique patterns: {report.unique_patterns}")
            print(f"   Systemic issues: {len(report.systemic_issues)}")
            print(f"   Saved to: {output_path}")

            if report.top_recurrences:
                print("\n🔝 Top Recurrences:")
                for i, rec in enumerate(report.top_recurrences[:5], 1):
                    msg = f"   {i}. {rec['pattern_name']}: {rec['frequency']} " \
                          f"occurrences ({rec['severity']})"
                    print(msg)

            if report.systemic_issues:
                print("\n⚠️  Systemic Issues:")
                for issue in report.systemic_issues[:5]:
                    msg = f"   - {issue['pattern_name']}: {issue['frequency']} " \
                          f"occurrences across {len(issue['affected_teams'])} teams"
                    print(msg)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()