#!/usr/bin/env python3
"""
JARVIS SYPHON Decisioning System
@PEAK Intelligence-Driven Decision Making

JARVIS consumes SYPHON actor feeds from all spectrums and personas
to make intelligent, data-driven decisions for system orchestration.

Features:
- Multi-spectrum intelligence analysis
- Actor consensus evaluation
- Risk-weighted decision making
- Automated action orchestration
- Decision quality assessment
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import queue
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import SYPHON aggregator
try:
    from syphon_actor_feed_aggregator import SYPHONActorFeedAggregator, JARVISDecisionFeed
    AGGREGATOR_AVAILABLE = True
except ImportError:
    AGGREGATOR_AVAILABLE = False

@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DecisionContext:
    """Context for JARVIS decision making"""
    decision_id: str
    decision_type: str
    trigger_spectrum: str
    trigger_actor: str
    intelligence_feed: JARVISDecisionFeed
    system_state: Dict[str, Any]
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    consensus_analysis: Dict[str, Any] = field(default_factory=dict)
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    decision_confidence: float = 0.0
    decision_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DecisionOutcome:
    """Result of JARVIS decision process"""
    decision_context: DecisionContext
    final_decision: str
    action_plan: List[Dict[str, Any]]
    expected_outcomes: List[str]
    risk_mitigation: List[str]
    monitoring_plan: List[str]
    execution_status: str = "pending"
    outcome_timestamp: Optional[datetime] = None

class JARVISSYPHONDecisioning:
    """
    JARVIS SYPHON Decisioning Engine
    @PEAK Intelligence-Driven Orchestration
    """

    def __init__(self):
        self.feed_aggregator = None
        self.decision_history: List[DecisionOutcome] = []
        self.active_decisions: Dict[str, DecisionContext] = {}
        self.decision_queue = queue.Queue()
        self.decision_thread = threading.Thread(
            target=self._decision_processing_loop,
            daemon=True
        )

        # Initialize components
        if AGGREGATOR_AVAILABLE:
            self.feed_aggregator = SYPHONActorFeedAggregator()

        # Decision-making parameters
        self.confidence_threshold = 0.75
        self.risk_tolerance = {
            'critical': 0.9,  # High confidence required for critical decisions
            'high': 0.8,
            'medium': 0.7,
            'low': 0.6
        }

        self.decision_weights = {
            'security': 1.5,      # Security decisions get highest weight
            'technical': 1.2,     # Technical decisions important
            'scientific': 1.1,    # Scientific validation matters
            'operational': 1.0,   # Baseline operational decisions
            'knowledge': 0.9,     # Knowledge management less critical
            'decision': 1.3,      # Decision support is key
            'user_experience': 0.7 # UX less critical for core operations
        }

        print("🎯 JARVIS SYPHON Decisioning initialized")

    def start_decisioning(self):
        """Start the decisioning process"""
        if self.feed_aggregator:
            self.feed_aggregator.start_aggregation()

        self.decision_thread.start()
        print("🚀 JARVIS SYPHON Decisioning active")

    def analyze_feed_for_decisions(self, feed: JARVISDecisionFeed) -> List[DecisionContext]:
        """
        Analyze SYPHON feed and identify decision opportunities
        """
        decision_contexts = []

        # Get current system state
        system_state = {
            'health_score': feed.system_status.get('health_score', 1.0),
            'total_intelligence': feed.system_status.get('total_intelligence_items', 0),
            'critical_items': feed.system_status.get('critical_items', 0),
            'active_spectrums': feed.active_spectrums,
            'timestamp': datetime.now()
        }

        # Analyze critical alerts
        for alert in feed.critical_alerts:
            context = DecisionContext(
                decision_id=f"critical_{alert['spectrum']}_{int(time.time())}",
                decision_type="crisis_response",
                trigger_spectrum=alert['spectrum'],
                trigger_actor=alert.get('actors_involved', ['unknown'])[0],
                intelligence_feed=feed,
                system_state=system_state
            )
            decision_contexts.append(context)

        # Analyze decision recommendations
        for recommendation in feed.decision_recommendations:
            if recommendation['priority'] in ['critical', 'high']:
                context = DecisionContext(
                    decision_id=f"recommend_{recommendation['type']}_{int(time.time())}",
                    decision_type="strategic_improvement",
                    trigger_spectrum=recommendation['spectrum'],
                    trigger_actor="aggregated_intelligence",
                    intelligence_feed=feed,
                    system_state=system_state
                )
                decision_contexts.append(context)

        # Analyze required actions
        for action in feed.action_required:
            context = DecisionContext(
                decision_id=f"action_{action['action_type']}_{int(time.time())}",
                decision_type="corrective_action",
                trigger_spectrum=action.get('spectrum', 'system'),
                trigger_actor="system_analysis",
                intelligence_feed=feed,
                system_state=system_state
            )
            decision_contexts.append(context)

        # Analyze system health issues
        system_status = feed.system_status
        if system_status.get('health_score', 1.0) < 0.8:
            context = DecisionContext(
                decision_id=f"health_system_{int(time.time())}",
                decision_type="system_health",
                trigger_spectrum="operational",
                trigger_actor="system_monitor",
                intelligence_feed=feed,
                system_state=system_state
            )
            decision_contexts.append(context)

        return decision_contexts

    def evaluate_decision_context(self, context: DecisionContext) -> DecisionContext:
        """
        Evaluate decision context with risk assessment and consensus analysis
        """
        feed = context.intelligence_feed

        # Risk assessment
        context.risk_assessment = self._assess_decision_risk(context)

        # Consensus analysis
        context.consensus_analysis = self._analyze_actor_consensus(context)

        # Generate recommendations
        context.recommended_actions = self._generate_action_recommendations(context)

        # Calculate decision confidence
        context.decision_confidence = self._calculate_decision_confidence(context)

        return context

    def _assess_decision_risk(self, context: DecisionContext) -> Dict[str, Any]:
        """Assess risk level of the decision"""
        feed = context.intelligence_feed

        risk_factors = {
            'critical_items': feed.system_status.get('critical_items', 0),
            'decision_type_risk': self._get_decision_type_risk(context.decision_type),
            'spectrum_sensitivity': self.decision_weights.get(context.trigger_spectrum, 1.0),
            'actor_reliability': self._assess_actor_reliability(context.trigger_actor),
            'system_health': feed.system_status.get('health_score', 1.0)
        }

        # Calculate overall risk score (0-1, higher = riskier)
        risk_score = (
            risk_factors['critical_items'] * 0.1 +  # 10% weight
            risk_factors['decision_type_risk'] * 0.3 +  # 30% weight
            (2 - risk_factors['spectrum_sensitivity']) * 0.2 +  # 20% weight (inverted)
            (1 - risk_factors['actor_reliability']) * 0.2 +  # 20% weight (inverted)
            (1 - risk_factors['system_health']) * 0.2  # 20% weight (inverted)
        ) / 5

        risk_level = "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high" if risk_score < 0.8 else "critical"

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'mitigation_required': risk_score > 0.5
        }

    def _get_decision_type_risk(self, decision_type: str) -> float:
        """Get risk level for decision type"""
        risk_levels = {
            'crisis_response': 1.0,      # Highest risk
            'system_health': 0.8,       # High risk
            'strategic_improvement': 0.6, # Medium-high risk
            'corrective_action': 0.5,   # Medium risk
            'routine_optimization': 0.2  # Low risk
        }
        return risk_levels.get(decision_type, 0.5)

    def _assess_actor_reliability(self, actor: str) -> float:
        """Assess reliability of triggering actor"""
        reliability_scores = {
            '@WOPR': 0.95,        # High reliability security monitoring
            '@MARVIN': 0.90,      # High reliability verification
            'SYPHON': 0.85,       # Good reliability intelligence
            'JARVIS': 0.88,       # Good reliability orchestration
            'system_monitor': 0.80, # Moderate reliability
            'aggregated_intelligence': 0.75, # Moderate reliability
            'unknown': 0.5        # Low reliability
        }
        return reliability_scores.get(actor, 0.5)

    def _analyze_actor_consensus(self, context: DecisionContext) -> Dict[str, Any]:
        """Analyze consensus among actors in the spectrum"""
        feed = context.intelligence_feed
        spectrum_feed = feed.spectrum_feeds.get(context.trigger_spectrum)

        if not spectrum_feed:
            return {'consensus_level': 'none', 'supporting_actors': 0, 'total_actors': 0}

        # Count actors providing intelligence
        active_actors = len([intel for intel in spectrum_feed.intelligence_stream])

        # Analyze agreement level (simplified)
        confidence_scores = [intel.confidence_score for intel in spectrum_feed.intelligence_stream]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        consensus_level = "strong" if avg_confidence > 0.8 else "moderate" if avg_confidence > 0.6 else "weak" if avg_confidence > 0.4 else "none"

        return {
            'consensus_level': consensus_level,
            'supporting_actors': active_actors,
            'total_actors': len(spectrum_feed.actors),
            'average_confidence': avg_confidence,
            'confidence_variance': sum((x - avg_confidence) ** 2 for x in confidence_scores) / len(confidence_scores) if confidence_scores else 0
        }

    def _generate_action_recommendations(self, context: DecisionContext) -> List[Dict[str, Any]]:
        """Generate action recommendations based on context"""
        recommendations = []

        # Critical alerts require immediate action
        if context.decision_type == "crisis_response":
            recommendations.append({
                'action_type': 'immediate_response',
                'description': f'Execute immediate response protocol for {context.trigger_spectrum} crisis',
                'priority': 'critical',
                'estimated_effort': '30 minutes',
                'risk_level': 'high'
            })

        # System health issues
        elif context.decision_type == "system_health":
            recommendations.append({
                'action_type': 'health_restoration',
                'description': 'Implement system health restoration procedures',
                'priority': 'high',
                'estimated_effort': '2 hours',
                'risk_level': 'medium'
            })

        # Strategic improvements
        elif context.decision_type == "strategic_improvement":
            recommendations.append({
                'action_type': 'capability_enhancement',
                'description': f'Enhance {context.trigger_spectrum} capabilities based on intelligence analysis',
                'priority': 'medium',
                'estimated_effort': '4 hours',
                'risk_level': 'low'
            })

        # Corrective actions
        elif context.decision_type == "corrective_action":
            recommendations.append({
                'action_type': 'problem_resolution',
                'description': 'Execute corrective actions to resolve identified issues',
                'priority': 'high',
                'estimated_effort': '1 hour',
                'risk_level': 'medium'
            })

        return recommendations

    def _calculate_decision_confidence(self, context: DecisionContext) -> float:
        """Calculate overall decision confidence"""
        weights = {
            'risk_assessment': 0.3,
            'consensus_analysis': 0.4,
            'actor_reliability': 0.2,
            'spectrum_importance': 0.1
        }

        # Risk factor (lower risk = higher confidence)
        risk_factor = 1 - context.risk_assessment['risk_score']

        # Consensus factor
        consensus_scores = {'strong': 1.0, 'moderate': 0.7, 'weak': 0.4, 'none': 0.1}
        consensus_factor = consensus_scores.get(context.consensus_analysis['consensus_level'], 0.1)

        # Actor reliability
        actor_reliability = self._assess_actor_reliability(context.trigger_actor)

        # Spectrum importance
        spectrum_importance = self.decision_weights.get(context.trigger_spectrum, 1.0) / 1.5  # Normalize

        confidence = (
            risk_factor * weights['risk_assessment'] +
            consensus_factor * weights['consensus_analysis'] +
            actor_reliability * weights['actor_reliability'] +
            spectrum_importance * weights['spectrum_importance']
        )

        return min(confidence, 1.0)  # Cap at 1.0

    def make_decision(self, context: DecisionContext) -> DecisionOutcome:
        """
        Make final decision based on evaluated context
        """
        # Evaluate context if not already done
        if not context.risk_assessment:
            context = self.evaluate_decision_context(context)

        # Decision logic based on context
        outcome = DecisionOutcome(
            decision_context=context,
            final_decision=self._determine_final_decision(context),
            action_plan=context.recommended_actions,
            expected_outcomes=self._predict_outcomes(context),
            risk_mitigation=self._generate_risk_mitigation(context),
            monitoring_plan=self._create_monitoring_plan(context)
        )

        # Store decision
        self.decision_history.append(outcome)
        self.active_decisions[context.decision_id] = context

        return outcome

    def _determine_final_decision(self, context: DecisionContext) -> str:
        """Determine final decision based on context analysis"""
        confidence = context.decision_confidence
        risk_level = context.risk_assessment['risk_level']
        consensus = context.consensus_analysis['consensus_level']

        # Decision matrix
        if confidence >= self.confidence_threshold:
            if risk_level == 'critical' and confidence >= self.risk_tolerance['critical']:
                return "APPROVE_HIGH_RISK"
            elif risk_level in ['high', 'medium'] and confidence >= self.risk_tolerance[risk_level]:
                return "APPROVE_STANDARD"
            elif risk_level == 'low':
                return "APPROVE_LOW_RISK"
            else:
                return "REQUIRES_HUMAN_REVIEW"
        else:
            if consensus == 'strong' and risk_level != 'critical':
                return "APPROVE_WITH_MONITORING"
            else:
                return "REJECT_INSUFFICIENT_CONFIDENCE"

    def _predict_outcomes(self, context: DecisionContext) -> List[str]:
        """Predict expected outcomes of the decision"""
        outcomes = []

        if context.decision_type == "crisis_response":
            outcomes.extend([
                "Immediate threat mitigation",
                "System stability restoration",
                "Reduced risk exposure",
                "Enhanced monitoring capabilities"
            ])
        elif context.decision_type == "strategic_improvement":
            outcomes.extend([
                "Improved system capabilities",
                "Enhanced performance metrics",
                "Increased operational efficiency",
                "Better resource utilization"
            ])
        elif context.decision_type == "system_health":
            outcomes.extend([
                "Restored system health",
                "Improved stability metrics",
                "Reduced error rates",
                "Enhanced reliability"
            ])

        return outcomes

    def _generate_risk_mitigation(self, context: DecisionContext) -> List[str]:
        """Generate risk mitigation strategies"""
        mitigation = []

        risk_level = context.risk_assessment['risk_level']

        if risk_level in ['critical', 'high']:
            mitigation.extend([
                "Implement rollback procedures",
                "Establish monitoring checkpoints",
                "Prepare contingency plans",
                "Schedule post-implementation review"
            ])

        if risk_level == 'medium':
            mitigation.extend([
                "Add progress monitoring",
                "Prepare phased implementation",
                "Document decision rationale"
            ])

        mitigation.extend([
            "Track key performance indicators",
            "Establish success criteria",
            "Plan for iterative improvements"
        ])

        return mitigation

    def _create_monitoring_plan(self, context: DecisionContext) -> List[str]:
        """Create monitoring plan for decision execution"""
        monitoring = [
            "Track decision execution progress",
            "Monitor key performance indicators",
            "Log system health metrics",
            "Record user feedback and issues"
        ]

        if context.decision_type == "crisis_response":
            monitoring.extend([
                "Real-time threat monitoring",
                "Immediate impact assessment",
                "Rapid response capability verification"
            ])

        if context.trigger_spectrum == "security":
            monitoring.extend([
                "Security incident tracking",
                "Compliance verification",
                "Audit trail maintenance"
            ])

        return monitoring

    def _decision_processing_loop(self):
        """Main decision processing loop"""
        while True:
            try:
                # Get latest SYPHON feed
                if self.feed_aggregator:
                    feed = self.feed_aggregator.get_latest_feed()
                    if feed:
                        # Analyze feed for decision opportunities
                        decision_contexts = self.analyze_feed_for_decisions(feed)

                        # Process each decision context
                        for context in decision_contexts:
                            # Queue for processing
                            self.decision_queue.put(context)

                # Process queued decisions
                while not self.decision_queue.empty():
                    context = self.decision_queue.get()
                    outcome = self.make_decision(context)

                    # Log decision outcome
                    self._log_decision_outcome(outcome)

                    # Execute decision if approved
                    if outcome.final_decision.startswith("APPROVE"):
                        self._execute_decision(outcome)

                time.sleep(60)  # Process decisions every minute

            except Exception as e:
                print(f"❌ Decision processing error: {e}")
                time.sleep(30)

    def _log_decision_outcome(self, outcome: DecisionOutcome):
        """Log decision outcome"""
        context = outcome.decision_context

        print(f"🎯 JARVIS Decision: {outcome.final_decision}")
        print(f"   Type: {context.decision_type}")
        print(f"   Spectrum: {context.trigger_spectrum}")
        print(f"   Actor: {context.trigger_actor}")
        print(f"   Confidence: {context.decision_confidence:.2f}")
        print(f"   Risk Level: {context.risk_assessment['risk_level']}")
        print(f"   Actions: {len(outcome.action_plan)}")

    def _execute_decision(self, outcome: DecisionOutcome):
        """Execute approved decision"""
        print(f"⚡ Executing decision: {outcome.decision_context.decision_id}")

        # Placeholder for actual execution logic
        # This would integrate with various system components

        outcome.execution_status = "executing"
        outcome.outcome_timestamp = datetime.now()

        # Mark as completed (simplified)
        time.sleep(2)  # Simulate execution time
        outcome.execution_status = "completed"

    def get_decision_history(self, limit: int = 10) -> List[DecisionOutcome]:
        """Get recent decision history"""
        return self.decision_history[-limit:] if limit > 0 else self.decision_history

    def get_active_decisions(self) -> Dict[str, DecisionContext]:
        """Get currently active decisions"""
        return self.active_decisions

def main():
    """JARVIS SYPHON Decisioning CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS SYPHON Decisioning System")
    parser.add_argument("--start", action="store_true", help="Start decisioning system")
    parser.add_argument("--analyze", action="store_true", help="Analyze current SYPHON feed")
    parser.add_argument("--history", action="store_true", help="Show decision history")
    parser.add_argument("--active", action="store_true", help="Show active decisions")

    args = parser.parse_args()

    decisioning = JARVISSYPHONDecisioning()

    if args.start:
        print("🎯 Starting JARVIS SYPHON Decisioning...")
        decisioning.start_decisioning()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping decisioning system...")

    elif args.analyze:
        print("🔍 Analyzing SYPHON feed for decisions...")
        if decisioning.feed_aggregator:
            feed = decisioning.feed_aggregator.get_latest_feed()
            if feed:
                contexts = decisioning.analyze_feed_for_decisions(feed)
                print(f"Found {len(contexts)} decision opportunities")

                for context in contexts:
                    evaluated = decisioning.evaluate_decision_context(context)
                    outcome = decisioning.make_decision(evaluated)

                    print(f"\n🎯 Decision: {outcome.final_decision}")
                    print(f"   Context: {context.decision_type} ({context.trigger_spectrum})")
                    print(f"   Confidence: {context.decision_confidence:.2f}")
                    print(f"   Risk: {context.risk_assessment['risk_level']}")
            else:
                print("No SYPHON feed available")
        else:
            print("SYPHON aggregator not available")

    elif args.history:
        history = decisioning.get_decision_history(5)
        print("📚 Recent Decision History:")
        for outcome in history:
            context = outcome.decision_context
            print(f"  {context.decision_id}: {outcome.final_decision} ({context.decision_type})")

    elif args.active:
        active = decisioning.get_active_decisions()
        print(f"🎯 Active Decisions: {len(active)}")
        for decision_id, context in active.items():
            print(f"  {decision_id}: {context.decision_type} ({context.trigger_spectrum})")

    else:
        print("🎯 JARVIS SYPHON Decisioning System")
        print("Use --help for available options")

if __name__ == "__main__":


    main()