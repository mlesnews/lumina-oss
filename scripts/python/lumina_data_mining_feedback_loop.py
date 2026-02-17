#!/usr/bin/env python3
"""
Lumina Data Mining Feedback Loop with Progressive Infinite Scaling

Data mines Lumina to differentiate Outcomes of Intent (OTS) and uses
progressive infinite scaling as a measuring stick for improvement.

@LUMINA @DATA_MINING @FEEDBACK_LOOP @PROGRESSIVE_SCALING @OUTCOMES_OF_INTENT
"""

import sys
import json
import re
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaDataMiningFeedbackLoop")


@dataclass
class Intent:
    """Captured intent from Lumina data"""
    intent_id: str
    source: str  # @ASK, workflow, chat, etc.
    source_id: str
    intent_text: str
    intent_type: str  # feature_request, bug_fix, improvement, etc.
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(self.timestamp, datetime):
            data['timestamp'] = self.timestamp.isoformat()
        elif isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data


@dataclass
class Outcome:
    """Actual outcome/result from implementation"""
    outcome_id: str
    intent_id: str  # Links back to original intent
    outcome_type: str  # success, partial, failure, deviation
    outcome_text: str
    metrics: Dict[str, float] = field(default_factory=dict)  # Performance metrics
    timestamp: datetime = field(default_factory=datetime.now)
    implementation_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(self.timestamp, datetime):
            data['timestamp'] = self.timestamp.isoformat()
        elif isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data


@dataclass
class OutcomeOfIntent:
    """Outcome of Intent (OTS) - Links intent to actual outcome"""
    ots_id: str
    intent: Intent
    outcome: Optional[Outcome]
    alignment_score: float  # 0.0 to 1.0 - how well outcome matches intent
    deviation_analysis: Dict[str, Any] = field(default_factory=dict)
    scaling_factor: float = 1.0  # Progressive scaling measurement
    improvement_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['intent'] = self.intent.to_dict()
        data['outcome'] = self.outcome.to_dict() if self.outcome else None
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ProgressiveScalingMetric:
    """Progressive infinite scaling metric for improvement measurement"""
    metric_name: str
    current_value: float
    baseline_value: float
    scaling_factor: float  # Current / Baseline
    trend: str  # increasing, decreasing, stable
    improvement_rate: float  # Rate of improvement over time
    infinite_scaling_potential: float  # Theoretical maximum scaling
    measurements: deque = field(default_factory=lambda: deque(maxlen=1000))
    timestamp: datetime = field(default_factory=datetime.now)

    def calculate_scaling_factor(self) -> float:
        """Calculate current scaling factor"""
        if self.baseline_value == 0:
            return 1.0
        return self.current_value / self.baseline_value

    def calculate_improvement_rate(self) -> float:
        """Calculate rate of improvement (slope)"""
        if len(self.measurements) < 2:
            return 0.0

        values = [m['value'] for m in self.measurements]
        times = [m['timestamp'] for m in self.measurements]

        # Calculate linear regression slope
        n = len(values)
        if n < 2:
            return 0.0

        # Simple linear regression
        sum_x = sum(i for i in range(n))
        sum_y = sum(values)
        sum_xy = sum(i * values[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))

        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['measurements'] = list(self.measurements)
        return data


class LuminaDataMiner:
    """Data mining system for Lumina project"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaDataMiner")

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_data_mining"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Mined data
        self.intents: List[Intent] = []
        self.outcomes: List[Outcome] = []
        self.ots_list: List[OutcomeOfIntent] = []

        # Load existing data
        self._load_mined_data()

    def _load_mined_data(self) -> None:
        """Load previously mined data"""
        intents_file = self.data_dir / "intents.json"
        outcomes_file = self.data_dir / "outcomes.json"
        ots_file = self.data_dir / "outcomes_of_intent.json"

        if intents_file.exists():
            try:
                with open(intents_file, 'r') as f:
                    data = json.load(f)
                    self.intents = [Intent(**item) for item in data]
                self.logger.info(f"Loaded {len(self.intents)} intents")
            except Exception as e:
                self.logger.error(f"Error loading intents: {e}")

        if outcomes_file.exists():
            try:
                with open(outcomes_file, 'r') as f:
                    data = json.load(f)
                    self.outcomes = [Outcome(**item) for item in data]
                self.logger.info(f"Loaded {len(self.outcomes)} outcomes")
            except Exception as e:
                self.logger.error(f"Error loading outcomes: {e}")

        if ots_file.exists():
            try:
                with open(ots_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct OTS objects
                    for item in data:
                        intent = Intent(**item['intent'])
                        outcome = Outcome(**item['outcome']) if item['outcome'] else None
                        ots = OutcomeOfIntent(
                            ots_id=item['ots_id'],
                            intent=intent,
                            outcome=outcome,
                            alignment_score=item['alignment_score'],
                            deviation_analysis=item.get('deviation_analysis', {}),
                            scaling_factor=item.get('scaling_factor', 1.0),
                            improvement_metrics=item.get('improvement_metrics', {})
                        )
                        self.ots_list.append(ots)
                self.logger.info(f"Loaded {len(self.ots_list)} OTS entries")
            except Exception as e:
                self.logger.error(f"Error loading OTS: {e}")

    def _save_mined_data(self) -> None:
        """Save mined data to disk"""
        intents_file = self.data_dir / "intents.json"
        outcomes_file = self.data_dir / "outcomes.json"
        ots_file = self.data_dir / "outcomes_of_intent.json"

        try:
            with open(intents_file, 'w') as f:
                json.dump([i.to_dict() for i in self.intents], f, indent=2, default=str)

            with open(outcomes_file, 'w') as f:
                json.dump([o.to_dict() for o in self.outcomes], f, indent=2, default=str)

            with open(ots_file, 'w') as f:
                json.dump([ots.to_dict() for ots in self.ots_list], f, indent=2, default=str)

            self.logger.info("Saved mined data")
        except Exception as e:
            self.logger.error(f"Error saving mined data: {e}")

    def mine_ask_intents(self) -> List[Intent]:
        """Mine intents from @ASK entries"""
        intents = []
        ask_pattern = re.compile(r'@ASK\s+(.+?)(?=\n|$|@)', re.IGNORECASE | re.MULTILINE)

        # Search all Python files
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                matches = ask_pattern.findall(content)
                for match in matches:
                    intent_text = match.strip()
                    if len(intent_text) > 10:  # Filter out very short matches
                        intent = Intent(
                            intent_id=f"ask_{len(intents)}_{datetime.now().timestamp()}",
                            source="@ASK",
                            source_id=str(py_file.relative_to(self.project_root)),
                            intent_text=intent_text,
                            intent_type=self._classify_intent(intent_text),
                            timestamp=datetime.now(),
                            context={"file": str(py_file), "line": content[:content.find(match)].count('\n') + 1}
                        )
                        intents.append(intent)
            except Exception as e:
                self.logger.debug(f"Error reading {py_file}: {e}")

        self.intents.extend(intents)
        self.logger.info(f"Mined {len(intents)} intents from @ASK entries")
        return intents

    def mine_workflow_outcomes(self) -> List[Outcome]:
        """Mine outcomes from workflow executions"""
        outcomes = []

        # Look for workflow result files
        workflow_dirs = [
            self.project_root / "data" / "workflows",
            self.project_root / "data" / "master_feedback_loop",
            self.project_root / "data" / "executions"
        ]

        for workflow_dir in workflow_dirs:
            if not workflow_dir.exists():
                continue

            for result_file in workflow_dir.rglob("*.json"):
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)

                    # Extract outcome information
                    if 'success' in data or 'result' in data or 'outcome' in data:
                        outcome = Outcome(
                            outcome_id=f"workflow_{len(outcomes)}_{datetime.now().timestamp()}",
                            intent_id=data.get('intent_id', 'unknown'),
                            outcome_type='success' if data.get('success', False) else 'failure',
                            outcome_text=str(data.get('result', data.get('outcome', 'No details'))),
                            metrics=self._extract_metrics(data),
                            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
                            implementation_details=data
                        )
                        outcomes.append(outcome)
                except Exception as e:
                    self.logger.debug(f"Error reading {result_file}: {e}")

        self.outcomes.extend(outcomes)
        self.logger.info(f"Mined {len(outcomes)} outcomes from workflows")
        return outcomes

    def mine_code_implementation_outcomes(self) -> List[Outcome]:
        """Mine outcomes from code implementations (file creation, modifications)"""
        outcomes = []

        # Look for implementation markers in code
        implementation_patterns = [
            (re.compile(r'#\s*IMPLEMENTED:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'implementation'),
            (re.compile(r'#\s*COMPLETED:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'completion'),
            (re.compile(r'#\s*FIXED:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'fix'),
        ]

        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_stat = py_file.stat()

                for pattern, outcome_type in implementation_patterns:
                    matches = pattern.findall(content)
                    for match in matches:
                        outcome = Outcome(
                            outcome_id=f"code_{len(outcomes)}_{datetime.now().timestamp()}",
                            intent_id='unknown',
                            outcome_type=outcome_type,
                            outcome_text=match.strip(),
                            metrics={
                                'file_size': file_stat.st_size,
                                'lines': content.count('\n'),
                                'last_modified': file_stat.st_mtime
                            },
                            timestamp=datetime.fromtimestamp(file_stat.st_mtime),
                            implementation_details={"file": str(py_file)}
                        )
                        outcomes.append(outcome)
            except Exception as e:
                self.logger.debug(f"Error reading {py_file}: {e}")

        self.outcomes.extend(outcomes)
        self.logger.info(f"Mined {len(outcomes)} outcomes from code implementations")
        return outcomes

    def _classify_intent(self, intent_text: str) -> str:
        """Classify intent type"""
        intent_lower = intent_text.lower()

        if any(word in intent_lower for word in ['fix', 'bug', 'error', 'issue']):
            return 'bug_fix'
        elif any(word in intent_lower for word in ['add', 'create', 'implement', 'new']):
            return 'feature_request'
        elif any(word in intent_lower for word in ['improve', 'enhance', 'optimize', 'better']):
            return 'improvement'
        elif any(word in intent_lower for word in ['refactor', 'clean', 'restructure']):
            return 'refactoring'
        else:
            return 'general'

    def _extract_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract performance metrics from data"""
        metrics = {}

        # Common metric keys
        metric_keys = ['duration', 'latency', 'throughput', 'accuracy', 'success_rate', 
                      'error_rate', 'performance', 'efficiency', 'speed']

        for key in metric_keys:
            if key in data:
                try:
                    metrics[key] = float(data[key])
                except (ValueError, TypeError):
                    pass

        return metrics

    def create_outcomes_of_intent(self) -> List[OutcomeOfIntent]:
        """Create Outcome of Intent (OTS) entries by matching intents to outcomes"""
        ots_list = []

        # Match intents to outcomes
        for intent in self.intents:
            # Find matching outcomes (by source, text similarity, or timestamp proximity)
            matching_outcomes = self._find_matching_outcomes(intent)

            for outcome in matching_outcomes:
                alignment_score = self._calculate_alignment_score(intent, outcome)
                deviation_analysis = self._analyze_deviation(intent, outcome)
                scaling_factor = self._calculate_scaling_factor(intent, outcome)
                improvement_metrics = self._calculate_improvement_metrics(intent, outcome)

                ots = OutcomeOfIntent(
                    ots_id=f"ots_{len(ots_list)}_{datetime.now().timestamp()}",
                    intent=intent,
                    outcome=outcome,
                    alignment_score=alignment_score,
                    deviation_analysis=deviation_analysis,
                    scaling_factor=scaling_factor,
                    improvement_metrics=improvement_metrics
                )
                ots_list.append(ots)

            # If no matching outcome, create OTS with null outcome
            if not matching_outcomes:
                ots = OutcomeOfIntent(
                    ots_id=f"ots_{len(ots_list)}_{datetime.now().timestamp()}",
                    intent=intent,
                    outcome=None,
                    alignment_score=0.0,
                    deviation_analysis={"status": "no_outcome_found"},
                    scaling_factor=0.0,
                    improvement_metrics={}
                )
                ots_list.append(ots)

        self.ots_list.extend(ots_list)
        self.logger.info(f"Created {len(ots_list)} OTS entries")
        return ots_list

    def _find_matching_outcomes(self, intent: Intent) -> List[Outcome]:
        """Find outcomes that match an intent"""
        matches = []

        # Match by intent_id if available
        for outcome in self.outcomes:
            if outcome.intent_id == intent.intent_id:
                matches.append(outcome)

        # If no direct match, try text similarity
        if not matches:
            for outcome in self.outcomes:
                similarity = self._text_similarity(intent.intent_text, outcome.outcome_text)
                if similarity > 0.3:  # Threshold for matching
                    matches.append(outcome)

        return matches

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (Jaccard similarity)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _calculate_alignment_score(self, intent: Intent, outcome: Outcome) -> float:
        """Calculate how well outcome aligns with intent (0.0 to 1.0)"""
        score = 0.0

        # Text similarity
        text_sim = self._text_similarity(intent.intent_text, outcome.outcome_text)
        score += text_sim * 0.4

        # Outcome type alignment
        if outcome.outcome_type == 'success':
            score += 0.3
        elif outcome.outcome_type == 'partial':
            score += 0.15

        # Intent type vs outcome type alignment
        if intent.intent_type == 'bug_fix' and outcome.outcome_type in ['fix', 'success']:
            score += 0.2
        elif intent.intent_type == 'feature_request' and outcome.outcome_type in ['implementation', 'success']:
            score += 0.2
        elif intent.intent_type == 'improvement' and 'improvement' in outcome.outcome_text.lower():
            score += 0.1

        return min(score, 1.0)

    def _analyze_deviation(self, intent: Intent, outcome: Outcome) -> Dict[str, Any]:
        """Analyze deviation between intent and outcome"""
        deviation = {
            "has_deviation": False,
            "deviation_type": None,
            "deviation_details": []
        }

        # Check for scope deviation
        intent_words = set(intent.intent_text.lower().split())
        outcome_words = set(outcome.outcome_text.lower().split())

        missing_in_outcome = intent_words - outcome_words
        extra_in_outcome = outcome_words - intent_words

        if missing_in_outcome:
            deviation["has_deviation"] = True
            deviation["deviation_type"] = "scope_reduction"
            deviation["deviation_details"].append(f"Missing elements: {missing_in_outcome}")

        if extra_in_outcome:
            deviation["has_deviation"] = True
            if deviation["deviation_type"] is None:
                deviation["deviation_type"] = "scope_expansion"
            deviation["deviation_details"].append(f"Extra elements: {extra_in_outcome}")

        return deviation

    def _calculate_scaling_factor(self, intent: Intent, outcome: Outcome) -> float:
        """Calculate progressive scaling factor"""
        if not outcome.metrics:
            return 1.0

        # Use performance metrics to calculate scaling
        # Higher performance = higher scaling factor
        scaling = 1.0

        if 'performance' in outcome.metrics:
            scaling = outcome.metrics['performance'] / 100.0  # Normalize
        elif 'efficiency' in outcome.metrics:
            scaling = outcome.metrics['efficiency'] / 100.0
        elif 'speed' in outcome.metrics:
            # Normalize speed (assume baseline of 1.0)
            scaling = outcome.metrics['speed']

        return max(scaling, 0.1)  # Minimum 0.1

    def _calculate_improvement_metrics(self, intent: Intent, outcome: Outcome) -> Dict[str, float]:
        """Calculate improvement metrics"""
        metrics = {}

        if outcome.metrics:
            # Calculate improvement over baseline
            for key, value in outcome.metrics.items():
                baseline = 1.0  # Default baseline
                improvement = (value - baseline) / baseline if baseline > 0 else 0.0
                metrics[f"{key}_improvement"] = improvement

        return metrics

    def mine_all(self) -> Dict[str, int]:
        """Mine all data sources"""
        self.logger.info("🔍 Starting comprehensive data mining of Lumina...")

        counts = {
            'intents': 0,
            'outcomes': 0,
            'ots': 0
        }

        # Mine intents
        intents = self.mine_ask_intents()
        counts['intents'] = len(intents)

        # Mine outcomes
        workflow_outcomes = self.mine_workflow_outcomes()
        code_outcomes = self.mine_code_implementation_outcomes()
        counts['outcomes'] = len(workflow_outcomes) + len(code_outcomes)

        # Create OTS entries
        ots = self.create_outcomes_of_intent()
        counts['ots'] = len(ots)

        # Save all data
        self._save_mined_data()

        self.logger.info(f"✅ Mining complete: {counts}")
        return counts


class ProgressiveInfiniteScaling:
    """Progressive infinite scaling measurement system"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.logger = get_logger("ProgressiveInfiniteScaling")

        # Scaling metrics
        self.metrics: Dict[str, ProgressiveScalingMetric] = {}

        # Data directory
        self.data_dir = self.project_root / "data" / "progressive_scaling"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing metrics
        self._load_metrics()

    def _load_metrics(self) -> None:
        """Load existing scaling metrics"""
        metrics_file = self.data_dir / "scaling_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    for metric_data in data:
                        metric = ProgressiveScalingMetric(**metric_data)
                        # Reconstruct measurements deque
                        for m in metric_data.get('measurements', []):
                            metric.measurements.append(m)
                        self.metrics[metric.metric_name] = metric
                self.logger.info(f"Loaded {len(self.metrics)} scaling metrics")
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")

    def _save_metrics(self) -> None:
        """Save scaling metrics"""
        metrics_file = self.data_dir / "scaling_metrics.json"
        try:
            with open(metrics_file, 'w') as f:
                json.dump([m.to_dict() for m in self.metrics.values()], f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")

    def update_metric(self, metric_name: str, value: float, baseline: Optional[float] = None) -> None:
        """Update a scaling metric"""
        if metric_name not in self.metrics:
            # Create new metric
            self.metrics[metric_name] = ProgressiveScalingMetric(
                metric_name=metric_name,
                current_value=value,
                baseline_value=baseline if baseline is not None else value,
                scaling_factor=1.0,
                trend='stable',
                improvement_rate=0.0,
                infinite_scaling_potential=float('inf')
            )
        else:
            # Update existing metric
            metric = self.metrics[metric_name]
            metric.current_value = value
            if baseline is not None:
                metric.baseline_value = baseline

        # Add measurement
        metric = self.metrics[metric_name]
        metric.measurements.append({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })

        # Recalculate
        metric.scaling_factor = metric.calculate_scaling_factor()
        metric.improvement_rate = metric.calculate_improvement_rate()

        # Determine trend
        if len(metric.measurements) >= 3:
            recent = [m['value'] for m in list(metric.measurements)[-3:]]
            if recent[-1] > recent[0]:
                metric.trend = 'increasing'
            elif recent[-1] < recent[0]:
                metric.trend = 'decreasing'
            else:
                metric.trend = 'stable'

        metric.timestamp = datetime.now()
        self._save_metrics()

    def calculate_infinite_scaling_potential(self, metric_name: str) -> float:
        """Calculate theoretical infinite scaling potential"""
        if metric_name not in self.metrics:
            return 0.0

        metric = self.metrics[metric_name]

        if len(metric.measurements) < 2:
            return metric.scaling_factor

        # Extrapolate based on improvement rate
        if metric.improvement_rate > 0:
            # Project forward to "infinite" (very large number)
            time_horizon = 1000  # Arbitrary large number
            projected_value = metric.current_value + (metric.improvement_rate * time_horizon)
            potential = projected_value / metric.baseline_value if metric.baseline_value > 0 else 1.0
            return max(potential, metric.scaling_factor)
        else:
            return metric.scaling_factor

    def get_improvement_report(self) -> Dict[str, Any]:
        """Get comprehensive improvement report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_metrics': len(self.metrics),
            'metrics': {},
            'overall_improvement': 0.0,
            'trends': {
                'increasing': 0,
                'decreasing': 0,
                'stable': 0
            }
        }

        total_scaling = 0.0
        for metric_name, metric in self.metrics.items():
            metric_report = {
                'current_value': metric.current_value,
                'baseline_value': metric.baseline_value,
                'scaling_factor': metric.scaling_factor,
                'trend': metric.trend,
                'improvement_rate': metric.improvement_rate,
                'infinite_scaling_potential': self.calculate_infinite_scaling_potential(metric_name),
                'measurement_count': len(metric.measurements)
            }
            report['metrics'][metric_name] = metric_report
            total_scaling += metric.scaling_factor

            report['trends'][metric.trend] = report['trends'].get(metric.trend, 0) + 1

        if len(self.metrics) > 0:
            report['overall_improvement'] = total_scaling / len(self.metrics)

        return report


class LuminaFeedbackLoop:
    """Feedback loop system that uses data mining and progressive scaling"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaFeedbackLoop")

        # Initialize subsystems
        self.data_miner = LuminaDataMiner(project_root)
        self.scaling = ProgressiveInfiniteScaling(project_root)

        # Feedback loop state
        self.cycle_count = 0
        self.feedback_history: List[Dict[str, Any]] = []

    def run_feedback_cycle(self) -> Dict[str, Any]:
        """Run a complete feedback loop cycle"""
        self.cycle_count += 1
        cycle_id = f"cycle_{self.cycle_count}_{datetime.now().timestamp()}"

        print(f"   🔄 Data Mining Cycle {self.cycle_count} started...", flush=True)
        self.logger.info(f"🔄 Starting feedback loop cycle {self.cycle_count}")

        # Step 1: Mine data
        print("      [1/6] Mining data...", flush=True)
        mining_results = self.data_miner.mine_all()
        print(f"         ✅ Mined {mining_results.get('intents', 0)} intents, {mining_results.get('outcomes', 0)} outcomes", flush=True)

        # Step 2: Analyze OTS (Outcomes of Intent)
        print("      [2/6] Analyzing OTS...", flush=True)
        ots_analysis = self._analyze_ots()
        print(f"         ✅ Analyzed {ots_analysis.get('total_ots', 0)} OTS entries", flush=True)

        # Step 3: Calculate progressive scaling metrics
        print("      [3/6] Calculating scaling metrics...", flush=True)
        scaling_metrics = self._calculate_scaling_from_ots()
        print(f"         ✅ Calculated {len(scaling_metrics)} metrics", flush=True)

        # Step 4: Generate improvement recommendations
        print("      [4/6] Generating recommendations...", flush=True)
        recommendations = self._generate_recommendations(ots_analysis, scaling_metrics)
        print(f"         ✅ Generated {len(recommendations)} recommendations", flush=True)

        # Step 5: Update scaling metrics
        print("      [5/6] Updating scaling metrics...", flush=True)
        for metric_name, value in scaling_metrics.items():
            self.scaling.update_metric(metric_name, value)
        print(f"         ✅ Updated {len(scaling_metrics)} metrics", flush=True)

        # Step 6: Generate feedback report
        print("      [6/6] Generating feedback report...", flush=True)
        feedback_report = {
            'cycle_id': cycle_id,
            'cycle_number': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'mining_results': mining_results,
            'ots_analysis': ots_analysis,
            'scaling_metrics': scaling_metrics,
            'recommendations': recommendations,
            'improvement_report': self.scaling.get_improvement_report()
        }

        self.feedback_history.append(feedback_report)
        self._save_feedback_history()
        print(f"         ✅ Report saved", flush=True)

        print(f"      ✅ Data Mining Cycle {self.cycle_count} complete", flush=True)
        self.logger.info(f"✅ Feedback loop cycle {self.cycle_count} complete")
        return feedback_report

    def _analyze_ots(self) -> Dict[str, Any]:
        """Analyze Outcomes of Intent"""
        ots_list = self.data_miner.ots_list

        if not ots_list:
            return {
                'total_ots': 0,
                'average_alignment': 0.0,
                'alignment_distribution': {},
                'deviation_analysis': {}
            }

        alignments = [ots.alignment_score for ots in ots_list]
        avg_alignment = statistics.mean(alignments) if alignments else 0.0

        # Distribution
        distribution = {
            'high_alignment': len([a for a in alignments if a >= 0.8]),
            'medium_alignment': len([a for a in alignments if 0.5 <= a < 0.8]),
            'low_alignment': len([a for a in alignments if a < 0.5])
        }

        # Deviation analysis
        deviations = [ots.deviation_analysis for ots in ots_list]
        deviation_types = defaultdict(int)
        for dev in deviations:
            if dev.get('has_deviation'):
                deviation_types[dev.get('deviation_type', 'unknown')] += 1

        return {
            'total_ots': len(ots_list),
            'average_alignment': avg_alignment,
            'alignment_distribution': distribution,
            'deviation_analysis': dict(deviation_types),
            'scaling_factors': [ots.scaling_factor for ots in ots_list if ots.scaling_factor > 0]
        }

    def _calculate_scaling_from_ots(self) -> Dict[str, float]:
        """Calculate scaling metrics from OTS data"""
        metrics = {}

        ots_list = self.data_miner.ots_list

        if not ots_list:
            return metrics

        # Average alignment as a scaling metric
        alignments = [ots.alignment_score for ots in ots_list]
        metrics['alignment_scaling'] = statistics.mean(alignments) if alignments else 0.0

        # Average scaling factor
        scaling_factors = [ots.scaling_factor for ots in ots_list if ots.scaling_factor > 0]
        metrics['outcome_scaling'] = statistics.mean(scaling_factors) if scaling_factors else 1.0

        # Improvement metrics
        all_improvements = []
        for ots in ots_list:
            all_improvements.extend(ots.improvement_metrics.values())

        if all_improvements:
            metrics['improvement_scaling'] = statistics.mean(all_improvements)

        # Intent completion rate
        completed = len([ots for ots in ots_list if ots.outcome is not None])
        metrics['completion_rate'] = completed / len(ots_list) if ots_list else 0.0

        return metrics

    def _generate_recommendations(self, ots_analysis: Dict[str, Any], 
                                 scaling_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate improvement recommendations"""
        recommendations = []

        # Check alignment
        if ots_analysis.get('average_alignment', 0.0) < 0.7:
            recommendations.append({
                'type': 'alignment',
                'priority': 'high',
                'message': 'Average intent-outcome alignment is below 70%. Focus on better intent capture and outcome tracking.',
                'action': 'Improve intent documentation and outcome measurement'
            })

        # Check completion rate
        completion_rate = scaling_metrics.get('completion_rate', 0.0)
        if completion_rate < 0.8:
            recommendations.append({
                'type': 'completion',
                'priority': 'medium',
                'message': f'Only {completion_rate*100:.1f}% of intents have tracked outcomes. Improve outcome tracking.',
                'action': 'Implement better outcome tracking mechanisms'
            })

        # Check scaling trends
        improvement_report = self.scaling.get_improvement_report()
        if improvement_report['overall_improvement'] < 1.0:
            recommendations.append({
                'type': 'scaling',
                'priority': 'high',
                'message': 'Overall improvement is below baseline. Review and optimize processes.',
                'action': 'Analyze bottlenecks and optimize workflows'
            })

        return recommendations

    def _save_feedback_history(self) -> None:
        """Save feedback history"""
        history_file = self.data_dir / "feedback_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.feedback_history, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving feedback history: {e}")

    @property
    def data_dir(self) -> Path:
        data_dir = self.project_root / "data" / "lumina_feedback_loop"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def run_continuous(self, interval_seconds: int = 3600) -> None:
        """Run feedback loop continuously"""
        import time

        self.logger.info(f"🔄 Starting continuous feedback loop (interval: {interval_seconds}s)")

        while True:
            try:
                self.run_feedback_cycle()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                self.logger.info("🛑 Stopping feedback loop")
                break
            except Exception as e:
                self.logger.error(f"Error in feedback cycle: {e}")
                time.sleep(interval_seconds)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Lumina Data Mining Feedback Loop")
        parser.add_argument("--mine", action="store_true", help="Run data mining only")
        parser.add_argument("--cycle", action="store_true", help="Run single feedback cycle")
        parser.add_argument("--continuous", action="store_true", help="Run continuous feedback loop")
        parser.add_argument("--interval", type=int, default=3600, help="Interval for continuous mode (seconds)")
        parser.add_argument("--report", action="store_true", help="Generate improvement report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        feedback_loop = LuminaFeedbackLoop(project_root)

        if args.mine:
            results = feedback_loop.data_miner.mine_all()
            print(f"✅ Mining complete: {results}")

        elif args.cycle:
            report = feedback_loop.run_feedback_cycle()
            print(json.dumps(report, indent=2, default=str))

        elif args.continuous:
            feedback_loop.run_continuous(args.interval)

        elif args.report:
            report = feedback_loop.scaling.get_improvement_report()
            print(json.dumps(report, indent=2, default=str))

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()