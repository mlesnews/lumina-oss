#!/usr/bin/env python3
"""
Comprehensive Intelligence Processing & Analysis System
Complete pipeline for processing all information/data influx, analyzing for intelligence,
and getting recommendations from ALL job roles across all areas.

Tags: #INTELLIGENCE_PROCESSING #ANALYSIS #ALL_ROLES #CRITICAL_AREAS #TEMPLATES @JARVIS @MARVIN @RR @PEAK @DOIT @COMPUSEC @F4 @PODCAST @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
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

logger = get_logger("IntelligenceProcessing")


class SourceType(Enum):
    """Intelligence source types"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    MIXED = "mixed"


class AreaStrength(Enum):
    """Area strength levels"""
    CRITICAL = "critical"  # Most critical, weakest
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"  # Use as template


class PriorityLevel(Enum):
    """Priority levels"""
    P0 = "P0"  # Critical - address immediately
    P1 = "P1"  # High - address in first hour
    P2 = "P2"  # Medium - address in second hour
    P3 = "P3"  # Low - address in third hour


@dataclass
class IntelligenceItem:
    """Single intelligence item from any source"""
    item_id: str
    source_type: SourceType
    source_name: str
    content: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: Any = None


@dataclass
class RoleRecommendation:
    """Recommendation from a specific role"""
    role: str  # @JARVIS, @MARVIN, @RR, @PEAK, @DOIT, @COMPUSEC, @F4, @PODCAST
    recommendation: str
    priority: PriorityLevel
    area: str
    reasoning: str
    actionable_steps: List[str] = field(default_factory=list)
    estimated_time_minutes: int = 0
    confidence: float = 0.0  # 0.0 - 1.0


@dataclass
class AreaAnalysis:
    """Analysis of a specific area"""
    area_name: str
    strength: AreaStrength
    priority: PriorityLevel
    intelligence_items: List[IntelligenceItem] = field(default_factory=list)
    role_recommendations: List[RoleRecommendation] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    weak_points: List[str] = field(default_factory=list)
    strong_points: List[str] = field(default_factory=list)
    template_components: List[str] = field(default_factory=list)  # From strong areas
    score: float = 0.0  # 0.0 - 1.0
    time_allocation_minutes: int = 0


@dataclass
class IntelligenceProcessingReport:
    """Complete intelligence processing report"""
    report_id: str
    timestamp: str
    processing_duration_seconds: float
    total_items_processed: int
    total_intelligence_extracted: int
    areas_analyzed: List[AreaAnalysis] = field(default_factory=list)
    role_recommendations_all: List[RoleRecommendation] = field(default_factory=list)
    critical_areas: List[AreaAnalysis] = field(default_factory=list)
    weak_areas: List[AreaAnalysis] = field(default_factory=list)
    strong_areas: List[AreaAnalysis] = field(default_factory=list)
    three_hour_plan: Dict[str, Any] = field(default_factory=dict)
    template_extraction: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IntelligenceProcessingSystem:
    """
    Comprehensive Intelligence Processing & Analysis System

    Processes all information/data influx, analyzes for intelligence,
    and gets recommendations from ALL job roles across all areas.
    """

    def __init__(self):
        """Initialize Intelligence Processing System"""
        logger.info("=" * 80)
        logger.info("🧠 Intelligence Processing & Analysis System")
        logger.info("=" * 80)

        self.project_root = project_root
        self.data_dir = project_root / "data" / "intelligence_processing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all roles
        self.roles = self._initialize_roles()

        # Processing steps
        self.processing_steps = [
            "data_collection",
            "data_normalization",
            "intelligence_extraction",
            "source_classification",
            "pattern_analysis",
            "area_identification",
            "strength_assessment",
            "role_consultation",
            "recommendation_generation",
            "prioritization",
            "time_allocation",
            "template_extraction",
            "action_plan_generation"
        ]

        logger.info("✅ Intelligence Processing System initialized")
        logger.info(f"   Roles: {len(self.roles)}")
        logger.info(f"   Processing steps: {len(self.processing_steps)}")

    def _initialize_roles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all job roles and responsibilities"""
        return {
            "@JARVIS": {
                "name": "@JARVIS",
                "role": "AI Assistant & Orchestrator",
                "responsibilities": [
                    "Autonomous execution without manual intervention",
                    "Optimistic, solution-oriented, action-focused",
                    "Can-do attitude, finds solutions, executes",
                    "Orchestrates all systems",
                    "Primary interface for user interactions"
                ],
                "perspective": "optimistic_solution_focused",
                "recommendation_style": "actionable_solutions"
            },
            "@MARVIN": {
                "name": "@MARVIN",
                "role": "Reality Checker - Voice of Reason",
                "responsibilities": [
                    "Pessimistic but truthful analysis",
                    "Tells uncomfortable truths",
                    "Reality-based, skeptical, but honest",
                    "Validates solutions before execution",
                    "Provides critical perspective"
                ],
                "perspective": "realistic_critical",
                "recommendation_style": "validation_critical_analysis"
            },
            "@RR": {
                "name": "@RR",
                "role": "Rapid Response System - Multi-Definition",
                "responsibilities": [
                    "Roast & Repair - Identify issues and fix them",
                    "Rapid Response - Fastest execution path",
                    "Root Cause Analysis - Deep investigation",
                    "Context-aware definition selection"
                ],
                "perspective": "analytical_systematic",
                "recommendation_style": "root_cause_focused"
            },
            "@PEAK": {
                "name": "@PEAK",
                "role": "Quantification & Definition Manager",
                "responsibilities": [
                    "Manage multiple definitions for terms",
                    "Quantify effectiveness (0.0 - 1.0)",
                    "Track usage and success rates",
                    "Dynamic modification on-the-fly"
                ],
                "perspective": "quantitative_metrics",
                "recommendation_style": "data_driven_optimization"
            },
            "@DOIT": {
                "name": "@DOIT",
                "role": "Autonomous Execution System",
                "responsibilities": [
                    "Detect @DOIT command word",
                    "Execute requests with maximum speed and autonomy",
                    "Determine best execution strategy",
                    "Apply speed optimizations"
                ],
                "perspective": "speed_autonomy",
                "recommendation_style": "rapid_execution"
            },
            "@COMPUSEC": {
                "name": "@COMPUSEC",
                "role": "Computer Security Dynamic Duo",
                "responsibilities": [
                    "Rapid threat detection",
                    "Fast response execution",
                    "Quick system recovery",
                    "Immediate prevention measures"
                ],
                "perspective": "security_focused",
                "recommendation_style": "security_hardening"
            },
            "@F4": {
                "name": "@F4",
                "role": "Fight/Fix/Fail/Forever Threat Response",
                "responsibilities": [
                    "FIGHT - Actively combat threat",
                    "FIX - Repair/restore system",
                    "FAIL - Graceful failure handling",
                    "FOREVER - Permanent prevention"
                ],
                "perspective": "threat_response",
                "recommendation_style": "threat_mitigation"
            },
            "@PODCAST": {
                "name": "@PODCAST",
                "role": "Moderator & Facilitator",
                "responsibilities": [
                    "Neutral, guides conversation",
                    "Asks questions",
                    "Balanced, ensures all voices heard",
                    "Facilitates multi-perspective analysis"
                ],
                "perspective": "balanced_facilitation",
                "recommendation_style": "synthesized_consensus"
            }
        }

    def process_complete_intelligence_cycle(self, 
                                            time_allocation_hours: float = 3.0) -> IntelligenceProcessingReport:
        """
        Process complete intelligence cycle with all steps

        Args:
            time_allocation_hours: Total time allocation (default 3 hours)

        Returns:
            Complete intelligence processing report
        """
        start_time = datetime.now()
        report_id = f"intel_{start_time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"\n🔄 Starting Complete Intelligence Processing Cycle")
        logger.info(f"   Report ID: {report_id}")
        logger.info(f"   Time Allocation: {time_allocation_hours} hours")

        # Step 1: Data Collection (with error recovery)
        logger.info("\n📥 Step 1: Data Collection")
        intelligence_items = self._collect_all_data_with_recovery()
        logger.info(f"   ✅ Collected {len(intelligence_items)} intelligence items")

        # Step 2: Data Normalization
        logger.info("\n🔄 Step 2: Data Normalization")
        normalized_items = self._normalize_data(intelligence_items)
        logger.info(f"   ✅ Normalized {len(normalized_items)} items")

        # Step 3: Intelligence Extraction
        logger.info("\n🧠 Step 3: Intelligence Extraction")
        extracted_intelligence = self._extract_intelligence(normalized_items)
        logger.info(f"   ✅ Extracted {len(extracted_intelligence)} intelligence items")

        # Step 4: Source Classification
        logger.info("\n🏷️  Step 4: Source Classification")
        classified_items = self._classify_sources(extracted_intelligence)
        logger.info(f"   ✅ Classified sources: {len([i for i in classified_items if i.source_type == SourceType.INTERNAL])} internal, "
                   f"{len([i for i in classified_items if i.source_type == SourceType.EXTERNAL])} external, "
                   f"{len([i for i in classified_items if i.source_type == SourceType.MIXED])} mixed")

        # Step 5: Pattern Analysis (with enhanced analysis)
        logger.info("\n🔍 Step 5: Pattern Analysis")
        patterns = self._analyze_patterns(classified_items)
        logger.info(f"   ✅ Identified {len(patterns)} patterns")

        # Verify pattern analysis completeness
        if not patterns:
            logger.warning("   ⚠️  No patterns identified - may indicate data quality issues")

        # Step 6: Area Identification
        logger.info("\n📍 Step 6: Area Identification")
        areas = self._identify_areas(classified_items, patterns)
        logger.info(f"   ✅ Identified {len(areas)} areas")

        # Step 7: Strength Assessment
        logger.info("\n📊 Step 7: Strength Assessment")
        assessed_areas = self._assess_strength(areas)
        logger.info(f"   ✅ Assessed {len(assessed_areas)} areas")

        # Step 8: Role Consultation
        logger.info("\n👥 Step 8: Role Consultation (ALL ROLES)")
        role_recommendations = self._consult_all_roles(assessed_areas)
        logger.info(f"   ✅ Received {len(role_recommendations)} recommendations from {len(self.roles)} roles")

        # Step 9: Recommendation Generation
        logger.info("\n💡 Step 9: Recommendation Generation")
        recommendations = self._generate_recommendations(assessed_areas, role_recommendations)
        logger.info(f"   ✅ Generated {len(recommendations)} recommendations")

        # Step 10: Prioritization
        logger.info("\n🎯 Step 10: Prioritization")
        prioritized_areas = self._prioritize_areas(assessed_areas, recommendations)
        logger.info(f"   ✅ Prioritized {len(prioritized_areas)} areas")

        # Step 11: Time Allocation (3 hours)
        logger.info(f"\n⏰ Step 11: Time Allocation ({time_allocation_hours} hours)")
        time_allocated = self._allocate_time(prioritized_areas, time_allocation_hours * 60)
        logger.info(f"   ✅ Allocated time across {len(time_allocated)} areas")

        # Step 12: Template Extraction
        logger.info("\n📋 Step 12: Template Extraction (from Strong Areas)")
        templates = self._extract_templates(time_allocated)
        logger.info(f"   ✅ Extracted {len(templates)} templates from strong areas")

        # Step 13: Action Plan Generation
        logger.info("\n📝 Step 13: Action Plan Generation")
        action_plan = self._generate_action_plan(time_allocated, templates)
        logger.info(f"   ✅ Generated action plan")

        # Generate report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Separate areas by strength
        critical_areas = [a for a in time_allocated if a.strength == AreaStrength.CRITICAL]
        weak_areas = [a for a in time_allocated if a.strength == AreaStrength.WEAK]
        strong_areas = [a for a in time_allocated if a.strength == AreaStrength.STRONG]

        report = IntelligenceProcessingReport(
            report_id=report_id,
            timestamp=start_time.isoformat(),
            processing_duration_seconds=duration,
            total_items_processed=len(classified_items),
            total_intelligence_extracted=len(extracted_intelligence),
            areas_analyzed=time_allocated,
            role_recommendations_all=role_recommendations,
            critical_areas=critical_areas,
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            three_hour_plan=action_plan,
            template_extraction=templates,
            summary=self._generate_summary(time_allocated, role_recommendations, action_plan)
        )

        # Save report
        self._save_report(report)

        # FINAL STEP: @DOIT @BDA (Build, Deploy, Activate)
        logger.info(f"\n🚀 FINAL STEP: @DOIT @BDA (Build, Deploy, Activate)")
        try:
            from doit_bda_final_step import DOITBDAFinalStep
            bda = DOITBDAFinalStep()
            bda_result = bda.execute_bda_for_workflow(
                workflow_id=report_id,
                workflow_type="intelligence_processing",
                workflow_metadata={
                    "areas_analyzed": len(time_allocated),
                    "recommendations": len(role_recommendations),
                    "critical_areas": len(critical_areas),
                    "weak_areas": len(weak_areas),
                    "strong_areas": len(strong_areas)
                }
            )
            logger.info(f"   ✅ @DOIT @BDA Complete: {bda_result.overall_status.upper()}")
        except Exception as e:
            logger.warning(f"   ⚠️  @DOIT @BDA failed: {e}")

        logger.info(f"\n✅ Complete Intelligence Processing Cycle Complete")
        logger.info(f"   Duration: {duration:.1f} seconds")
        logger.info(f"   Areas Analyzed: {len(time_allocated)}")
        logger.info(f"   Critical Areas: {len(critical_areas)}")
        logger.info(f"   Weak Areas: {len(weak_areas)}")
        logger.info(f"   Strong Areas: {len(strong_areas)}")
        logger.info(f"   Recommendations: {len(role_recommendations)}")

        return report

    def _collect_all_data(self) -> List[IntelligenceItem]:
        """Step 1: Collect all data from all sources"""
        items = []

        # Collect from daily work cycle
        try:
            from daily_work_cycle_complete import DailyWorkCycle
            cycle = DailyWorkCycle()
            summary = cycle.get_daily_summary()

            # Extract intelligence from summary
            for source_result in summary.get('source_results', []):
                items.append(IntelligenceItem(
                    item_id=f"daily_work_{source_result.get('source_name', 'unknown')}",
                    source_type=SourceType.INTERNAL,
                    source_name=source_result.get('source_name', 'unknown'),
                    content=str(source_result),
                    timestamp=datetime.now().isoformat(),
                    metadata=source_result.get('metadata', {}),
                    raw_data=source_result
                ))
        except Exception as e:
            logger.warning(f"Error collecting daily work cycle data: {e}")

        # Collect from other sources
        # Additional sources can be added here

        return items

    def _collect_all_data_with_recovery(self, max_retries: int = 3) -> List[IntelligenceItem]:
        """
        Collect all data with automatic retry and recovery

        Args:
            max_retries: Maximum retry attempts

        Returns:
            List of intelligence items
        """
        items = []
        retry_count = 0

        while retry_count < max_retries:
            try:
                items = self._collect_all_data()
                # Verify completion
                if self._verify_collection_completeness(items):
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"   ⚠️  Collection incomplete, retrying ({retry_count}/{max_retries})...")
                        time.sleep(2 ** retry_count)  # Exponential backoff
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"   ⚠️  Collection error, retrying ({retry_count}/{max_retries}): {e}")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    logger.error(f"   ❌ Collection failed after {max_retries} attempts: {e}")
                    # Return partial results
                    break

        return items

    def _verify_collection_completeness(self, items: List[IntelligenceItem]) -> bool:
        """
        Verify collection completeness

        Args:
            items: Collected items

        Returns:
            True if collection appears complete
        """
        # Check minimum expected items
        if len(items) < 1:
            return False

        # Check for expected sources
        expected_sources = ['internal', 'external', 'youtube', 'holocron', 'email', 'r5', 'cursor_ide']
        found_sources = {item.source_name for item in items}

        # At least some sources should be present
        if len(found_sources) == 0:
            return False

        return True

    def _normalize_data(self, items: List[IntelligenceItem]) -> List[IntelligenceItem]:
        try:
            """Step 2: Normalize all data to common format"""
            normalized = []

            for item in items:
                # Normalize content
                if isinstance(item.content, dict):
                    item.content = json.dumps(item.content)

                normalized.append(item)

            return normalized

        except Exception as e:
            self.logger.error(f"Error in _normalize_data: {e}", exc_info=True)
            raise
    def _extract_intelligence(self, items: List[IntelligenceItem]) -> List[IntelligenceItem]:
        """Step 3: Extract actionable intelligence from data with quality validation"""
        extracted = []

        for item in items:
            # Extract intelligence patterns
            # Validate quality before adding
            quality_score = self._validate_intelligence_quality(item)

            if quality_score >= 0.5:  # Quality threshold
                item.metadata["quality_score"] = quality_score
                item.metadata["quality_validated"] = True
                extracted.append(item)
            else:
                logger.warning(f"   ⚠️  Low quality intelligence item filtered: {item.item_id} (score: {quality_score:.2f})")
                item.metadata["quality_score"] = quality_score
                item.metadata["quality_validated"] = False
                # Still add but mark as low quality
                extracted.append(item)

        return extracted

    def _validate_intelligence_quality(self, item: IntelligenceItem) -> float:
        """
        Validate intelligence quality (0.0 - 1.0)

        Args:
            item: Intelligence item to validate

        Returns:
            Quality score (0.0 - 1.0)
        """
        score = 1.0

        # Check content completeness
        if not item.content or len(item.content.strip()) < 10:
            score -= 0.3

        # Check metadata completeness
        if not item.metadata:
            score -= 0.2

        # Check timestamp validity
        try:
            datetime.fromisoformat(item.timestamp)
        except:
            score -= 0.2

        # Check source type validity
        if item.source_type not in [SourceType.INTERNAL, SourceType.EXTERNAL, SourceType.MIXED]:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _classify_sources(self, items: List[IntelligenceItem]) -> List[IntelligenceItem]:
        """Step 4: Classify sources as internal, external, or mixed"""
        classified = []

        for item in items:
            # Classify based on source
            if item.source_name in ['internal', 'holocron', 'r5']:
                item.source_type = SourceType.INTERNAL
            elif item.source_name in ['external', 'youtube']:
                item.source_type = SourceType.EXTERNAL
            else:
                item.source_type = SourceType.MIXED

            classified.append(item)

        return classified

    def _analyze_patterns(self, items: List[IntelligenceItem]) -> List[Dict[str, Any]]:
        """Step 5: Analyze patterns across all intelligence"""
        patterns = []

        # Group by source type
        internal_items = [i for i in items if i.source_type == SourceType.INTERNAL]
        external_items = [i for i in items if i.source_type == SourceType.EXTERNAL]
        mixed_items = [i for i in items if i.source_type == SourceType.MIXED]

        patterns.append({
            "pattern_type": "source_distribution",
            "internal_count": len(internal_items),
            "external_count": len(external_items),
            "mixed_count": len(mixed_items)
        })

        # Quality distribution pattern
        quality_scores = [i.metadata.get("quality_score", 1.0) for i in items if i.metadata.get("quality_score")]
        if quality_scores:
            patterns.append({
                "pattern_type": "quality_distribution",
                "avg_quality": sum(quality_scores) / len(quality_scores),
                "min_quality": min(quality_scores),
                "max_quality": max(quality_scores),
                "low_quality_count": len([s for s in quality_scores if s < 0.5])
            })

        # Temporal pattern (if timestamps available)
        try:
            timestamps = [datetime.fromisoformat(i.timestamp) for i in items if i.timestamp]
            if timestamps:
                patterns.append({
                    "pattern_type": "temporal_distribution",
                    "earliest": min(timestamps).isoformat(),
                    "latest": max(timestamps).isoformat(),
                    "span_hours": (max(timestamps) - min(timestamps)).total_seconds() / 3600
                })
        except:
            pass

        return patterns

    def _identify_areas(self, items: List[IntelligenceItem], patterns: List[Dict[str, Any]]) -> List[AreaAnalysis]:
        """Step 6: Identify areas for analysis"""
        areas = []

        # Identify areas from intelligence items
        area_names = set()
        for item in items:
            # Extract area from metadata or content
            area = item.metadata.get('area', 'general')
            area_names.add(area)

        # Create area analyses
        for area_name in area_names:
            area_items = [i for i in items if i.metadata.get('area', 'general') == area_name]
            areas.append(AreaAnalysis(
                area_name=area_name,
                strength=AreaStrength.MODERATE,  # Will be assessed in next step
                priority=PriorityLevel.P2,
                intelligence_items=area_items
            ))

        # If no areas identified, create default areas
        if not areas:
            areas = [
                AreaAnalysis(area_name="data_processing", strength=AreaStrength.MODERATE, priority=PriorityLevel.P2, intelligence_items=items[:len(items)//3]),
                AreaAnalysis(area_name="intelligence_analysis", strength=AreaStrength.MODERATE, priority=PriorityLevel.P2, intelligence_items=items[len(items)//3:2*len(items)//3]),
                AreaAnalysis(area_name="system_coordination", strength=AreaStrength.MODERATE, priority=PriorityLevel.P2, intelligence_items=items[2*len(items)//3:])
            ]

        return areas

    def _assess_strength(self, areas: List[AreaAnalysis]) -> List[AreaAnalysis]:
        """Step 7: Assess strength of each area"""
        assessed = []

        for area in areas:
            # Calculate strength score based on various factors
            item_count = len(area.intelligence_items)
            error_count = sum(1 for item in area.intelligence_items if 'error' in item.metadata.get('status', '').lower())

            # Simple scoring (0.0 - 1.0)
            if item_count == 0:
                score = 0.0
                strength = AreaStrength.CRITICAL
            elif error_count > item_count * 0.5:
                score = 0.2
                strength = AreaStrength.CRITICAL
            elif error_count > item_count * 0.3:
                score = 0.4
                strength = AreaStrength.WEAK
            elif error_count > item_count * 0.1:
                score = 0.6
                strength = AreaStrength.MODERATE
            else:
                score = 0.8
                strength = AreaStrength.STRONG

            area.score = score
            area.strength = strength

            # Identify critical issues and weak points
            if strength in [AreaStrength.CRITICAL, AreaStrength.WEAK]:
                area.critical_issues = [f"Low item count: {item_count}", f"High error rate: {error_count}/{item_count}"]
                area.weak_points = ["Insufficient data", "High error rate"]

            # Identify strong points
            if strength == AreaStrength.STRONG:
                area.strong_points = [f"High item count: {item_count}", f"Low error rate: {error_count}/{item_count}"]

            assessed.append(area)

        return assessed

    def _consult_all_roles(self, areas: List[AreaAnalysis]) -> List[RoleRecommendation]:
        """Step 8: Consult ALL roles for recommendations"""
        recommendations = []

        for role_name, role_info in self.roles.items():
            for area in areas:
                # Generate recommendation from this role for this area
                recommendation = self._generate_role_recommendation(role_name, role_info, area)
                recommendations.append(recommendation)

        return recommendations

    def _generate_role_recommendation(self, role_name: str, role_info: Dict[str, Any], area: AreaAnalysis) -> RoleRecommendation:
        """Generate recommendation from a specific role"""
        # Determine priority based on area strength
        if area.strength == AreaStrength.CRITICAL:
            priority = PriorityLevel.P0
        elif area.strength == AreaStrength.WEAK:
            priority = PriorityLevel.P1
        elif area.strength == AreaStrength.MODERATE:
            priority = PriorityLevel.P2
        else:
            priority = PriorityLevel.P3

        # Generate role-specific recommendation
        if role_name == "@JARVIS":
            recommendation = f"Optimize {area.area_name} with actionable solutions. Focus on quick wins and immediate improvements."
            reasoning = "JARVIS perspective: Action-oriented approach to strengthen this area"
            actionable_steps = [
                f"Identify quick wins in {area.area_name}",
                f"Implement immediate improvements",
                f"Monitor progress and iterate"
            ]
        elif role_name == "@MARVIN":
            recommendation = f"Realistically assess {area.area_name}. Address critical issues first, validate before execution."
            reasoning = "MARVIN perspective: Critical validation needed before proceeding"
            actionable_steps = [
                f"Validate current state of {area.area_name}",
                f"Identify root causes of issues",
                f"Test solutions before full deployment"
            ]
        elif role_name == "@RR":
            recommendation = f"Perform root cause analysis on {area.area_name}. Identify and fix underlying issues."
            reasoning = "RR perspective: Systematic analysis to find root causes"
            actionable_steps = [
                f"Analyze root causes in {area.area_name}",
                f"Identify systemic issues",
                f"Implement fixes at the source"
            ]
        elif role_name == "@PEAK":
            recommendation = f"Quantify effectiveness of {area.area_name}. Measure, track, and optimize based on metrics."
            reasoning = "PEAK perspective: Data-driven optimization"
            actionable_steps = [
                f"Establish metrics for {area.area_name}",
                f"Track effectiveness over time",
                f"Optimize based on quantitative data"
            ]
        elif role_name == "@DOIT":
            recommendation = f"Execute rapid improvements to {area.area_name}. Speed and autonomy are key."
            reasoning = "DOIT perspective: Rapid autonomous execution"
            actionable_steps = [
                f"Execute immediate improvements to {area.area_name}",
                f"Apply speed optimizations",
                f"Autonomous execution where safe"
            ]
        elif role_name == "@COMPUSEC":
            recommendation = f"Secure {area.area_name}. Identify and mitigate security vulnerabilities."
            reasoning = "COMPUSEC perspective: Security-first approach"
            actionable_steps = [
                f"Assess security posture of {area.area_name}",
                f"Identify vulnerabilities",
                f"Implement security hardening"
            ]
        elif role_name == "@F4":
            recommendation = f"Apply F4 framework to {area.area_name}: Fight threats, Fix issues, Fail gracefully, Forever prevention."
            reasoning = "F4 perspective: Comprehensive threat response"
            actionable_steps = [
                f"Fight: Actively combat issues in {area.area_name}",
                f"Fix: Repair and restore functionality",
                f"Fail: Implement graceful failure handling",
                f"Forever: Establish permanent prevention"
            ]
        elif role_name == "@PODCAST":
            recommendation = f"Facilitate discussion on {area.area_name}. Synthesize perspectives from all roles."
            reasoning = "PODCAST perspective: Balanced synthesis of all viewpoints"
            actionable_steps = [
                f"Gather perspectives from all roles on {area.area_name}",
                f"Synthesize recommendations",
                f"Create balanced action plan"
            ]
        else:
            recommendation = f"Review {area.area_name} and provide recommendations."
            reasoning = "General recommendation"
            actionable_steps = [f"Review {area.area_name}"]

        return RoleRecommendation(
            role=role_name,
            recommendation=recommendation,
            priority=priority,
            area=area.area_name,
            reasoning=reasoning,
            actionable_steps=actionable_steps,
            estimated_time_minutes=30,  # Default
            confidence=0.7  # Default
        )

    def _generate_recommendations(self, areas: List[AreaAnalysis], role_recommendations: List[RoleRecommendation]) -> List[RoleRecommendation]:
        """Step 9: Generate consolidated recommendations"""
        # Group recommendations by area
        recommendations_by_area = {}
        for rec in role_recommendations:
            if rec.area not in recommendations_by_area:
                recommendations_by_area[rec.area] = []
            recommendations_by_area[rec.area].append(rec)

        # Add recommendations to areas
        for area in areas:
            area.role_recommendations = recommendations_by_area.get(area.area_name, [])

        return role_recommendations

    def _prioritize_areas(self, areas: List[AreaAnalysis], recommendations: List[RoleRecommendation]) -> List[AreaAnalysis]:
        """Step 10: Prioritize areas (critical/weak first, then strong)"""
        # Sort: Critical first, then weak, then moderate, then strong
        prioritized = sorted(areas, key=lambda a: (
            a.strength == AreaStrength.CRITICAL,
            a.strength == AreaStrength.WEAK,
            a.strength == AreaStrength.MODERATE,
            a.strength == AreaStrength.STRONG
        ), reverse=True)

        # Assign priorities
        for i, area in enumerate(prioritized):
            if area.strength == AreaStrength.CRITICAL:
                area.priority = PriorityLevel.P0
            elif area.strength == AreaStrength.WEAK:
                area.priority = PriorityLevel.P1
            elif area.strength == AreaStrength.MODERATE:
                area.priority = PriorityLevel.P2
            else:
                area.priority = PriorityLevel.P3

        return prioritized

    def _allocate_time(self, areas: List[AreaAnalysis], total_minutes: int) -> List[AreaAnalysis]:
        """Step 11: Allocate time (3 hours = 180 minutes)"""
        # Allocate more time to critical/weak areas
        critical_weak = [a for a in areas if a.strength in [AreaStrength.CRITICAL, AreaStrength.WEAK]]
        strong_moderate = [a for a in areas if a.strength in [AreaStrength.STRONG, AreaStrength.MODERATE]]

        # 60% of time to critical/weak (first priority)
        critical_weak_time = int(total_minutes * 0.6)
        # 40% of time to strong/moderate (second priority)
        strong_moderate_time = total_minutes - critical_weak_time

        # Allocate time proportionally
        if critical_weak:
            time_per_critical_weak = critical_weak_time // len(critical_weak)
            for area in critical_weak:
                area.time_allocation_minutes = time_per_critical_weak

        if strong_moderate:
            time_per_strong_moderate = strong_moderate_time // len(strong_moderate)
            for area in strong_moderate:
                area.time_allocation_minutes = time_per_strong_moderate

        return areas

    def _extract_templates(self, areas: List[AreaAnalysis]) -> Dict[str, Any]:
        """Step 12: Extract templates from strong areas"""
        strong_areas = [a for a in areas if a.strength == AreaStrength.STRONG]

        templates = {}

        for area in strong_areas:
            # Extract template components from strong area
            template = {
                "area_name": area.area_name,
                "strength_score": area.score,
                "strong_points": area.strong_points,
                "successful_patterns": [],
                "best_practices": [],
                "reusable_components": []
            }

            # Extract patterns from strong area
            if area.intelligence_items:
                template["successful_patterns"] = [
                    f"Pattern from {item.source_name}" for item in area.intelligence_items[:3]
                ]

            templates[area.area_name] = template

        return templates

    def _generate_action_plan(self, areas: List[AreaAnalysis], templates: Dict[str, Any]) -> Dict[str, Any]:
        """Step 13: Generate 3-hour action plan"""
        # Sort by priority
        sorted_areas = sorted(areas, key=lambda a: (
            a.priority == PriorityLevel.P0,
            a.priority == PriorityLevel.P1,
            a.priority == PriorityLevel.P2,
            a.priority == PriorityLevel.P3
        ), reverse=True)

        action_plan = {
            "total_time_minutes": sum(a.time_allocation_minutes for a in areas),
            "phases": []
        }

        current_time = 0

        # Phase 1: Critical areas (first hour)
        critical_areas = [a for a in sorted_areas if a.priority == PriorityLevel.P0]
        if critical_areas:
            phase1_time = sum(a.time_allocation_minutes for a in critical_areas)
            action_plan["phases"].append({
                "phase": 1,
                "name": "Critical Areas (First Priority)",
                "duration_minutes": phase1_time,
                "areas": [a.area_name for a in critical_areas],
                "focus": "Address most critical and weakest areas first"
            })
            current_time += phase1_time

        # Phase 2: Weak areas (second hour)
        weak_areas = [a for a in sorted_areas if a.priority == PriorityLevel.P1]
        if weak_areas:
            phase2_time = sum(a.time_allocation_minutes for a in weak_areas)
            action_plan["phases"].append({
                "phase": 2,
                "name": "Weak Areas (Second Priority)",
                "duration_minutes": phase2_time,
                "areas": [a.area_name for a in weak_areas],
                "focus": "Strengthen weak areas using templates from strong areas"
            })
            current_time += phase2_time

        # Phase 3: Strong areas as templates (third hour)
        strong_areas = [a for a in sorted_areas if a.strength == AreaStrength.STRONG]
        if strong_areas:
            phase3_time = sum(a.time_allocation_minutes for a in strong_areas)
            action_plan["phases"].append({
                "phase": 3,
                "name": "Strong Areas as Templates (Third Priority)",
                "duration_minutes": phase3_time,
                "areas": [a.area_name for a in strong_areas],
                "focus": "Extract templates and apply to other areas",
                "templates": templates
            })

        return action_plan

    def _generate_summary(self, areas: List[AreaAnalysis], recommendations: List[RoleRecommendation], action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of processing"""
        return {
            "total_areas": len(areas),
            "critical_areas_count": len([a for a in areas if a.strength == AreaStrength.CRITICAL]),
            "weak_areas_count": len([a for a in areas if a.strength == AreaStrength.WEAK]),
            "strong_areas_count": len([a for a in areas if a.strength == AreaStrength.STRONG]),
            "total_recommendations": len(recommendations),
            "total_time_allocated_minutes": sum(a.time_allocation_minutes for a in areas),
            "action_plan_phases": len(action_plan.get("phases", [])),
            "processing_complete": True
        }

    def _save_report(self, report: IntelligenceProcessingReport):
        try:
            """Save intelligence processing report"""
            report_file = self.data_dir / f"{report.report_id}.json"

            with open(report_file, 'w') as f:
                json.dump(report.to_dict(), f, indent=2, default=str)

            logger.info(f"📄 Report saved: {report_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_report: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description='Intelligence Processing & Analysis System')
        parser.add_argument('--process', action='store_true', help='Process complete intelligence cycle')
        parser.add_argument('--time-hours', type=float, default=3.0, help='Time allocation in hours (default: 3.0)')
        parser.add_argument('--json', action='store_true', help='Output as JSON')

        args = parser.parse_args()

        system = IntelligenceProcessingSystem()

        if args.process:
            report = system.process_complete_intelligence_cycle(time_allocation_hours=args.time_hours)

            if args.json:
                print(json.dumps(report.to_dict(), indent=2, default=str))
            else:
                print("\n" + "=" * 80)
                print("🧠 Intelligence Processing & Analysis Report")
                print("=" * 80)
                print(f"Report ID: {report.report_id}")
                print(f"Duration: {report.processing_duration_seconds:.1f} seconds")
                print(f"Items Processed: {report.total_items_processed}")
                print(f"Intelligence Extracted: {report.total_intelligence_extracted}")
                print(f"\nAreas Analyzed: {len(report.areas_analyzed)}")
                print(f"Critical Areas: {len(report.critical_areas)}")
                print(f"Weak Areas: {len(report.weak_areas)}")
                print(f"Strong Areas: {len(report.strong_areas)}")
                print(f"Recommendations: {len(report.role_recommendations_all)}")

                print("\n📋 3-Hour Action Plan:")
                for phase in report.three_hour_plan.get("phases", []):
                    print(f"\n  Phase {phase['phase']}: {phase['name']}")
                    print(f"    Duration: {phase['duration_minutes']} minutes")
                    print(f"    Areas: {', '.join(phase['areas'])}")
                    print(f"    Focus: {phase['focus']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()