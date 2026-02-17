#!/usr/bin/env python3
"""
WOPR Experiment Framework
A/B Control and Experiment Creation and Comparison

WOPR can create A (control) and B (experiment) scenarios, run them through
the pipeline, and compare outcomes to the current situation.

Author: WOPR Operations Team
Date: 2025-01-28
Classification: ROGUE AI DEFENSE INTELLIGENCE
"""

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    import logging
    get_logger = logging.getLogger

try:
    from centralized_log_parser import CentralizedLogParser, LogSource
    LOG_PARSING_AVAILABLE = True
except ImportError:
    LOG_PARSING_AVAILABLE = False
    CentralizedLogParser = None

try:
    from syphon_system import SYPHONSystem
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

try:
    from jarvis_10000_year_simulation import Jarvis10000YearSimulation, MatrixLattice
    SIMULATION_AVAILABLE = True
except ImportError:
    SIMULATION_AVAILABLE = False
    Jarvis10000YearSimulation = None
    MatrixLattice = None

from universal_decision_tree import decide, DecisionContext, DecisionOutcome

logger = get_logger("WOPRExperiment")


class ExperimentStatus(Enum):
    """Experiment status"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScenarioType(Enum):
    """Scenario type"""
    CONTROL = "control"  # A - Current situation
    EXPERIMENT = "experiment"  # B - Proposed change


@dataclass
class ExperimentScenario:
    """A single scenario (A or B)"""
    scenario_id: str
    scenario_type: ScenarioType
    name: str
    description: str
    configuration: Dict[str, Any]
    baseline_state: Dict[str, Any] = field(default_factory=dict)
    created: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type.value,
            "name": self.name,
            "description": self.description,
            "configuration": self.configuration,
            "baseline_state": self.baseline_state,
            "created": self.created.isoformat()
        }


@dataclass
class ExperimentResult:
    """Result from running a scenario"""
    scenario_id: str
    scenario_type: ScenarioType
    metrics: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    patterns: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type.value,
            "metrics": self.metrics,
            "logs": self.logs,
            "patterns": self.patterns,
            "errors": self.errors,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ExperimentComparison:
    """Comparison between A and B scenarios"""
    experiment_id: str
    control_result: ExperimentResult
    experiment_result: ExperimentResult
    differences: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    winner: Optional[str] = None  # "control" or "experiment"
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "experiment_id": self.experiment_id,
            "control_result": self.control_result.to_dict(),
            "experiment_result": self.experiment_result.to_dict(),
            "differences": self.differences,
            "recommendations": self.recommendations,
            "winner": self.winner,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


class WOPRExperimentFramework:
    """
    WOPR A/B Experiment Framework

    Creates control (A) and experiment (B) scenarios, runs them through
    the pipeline, and compares outcomes.
    """

    def __init__(self, project_root: Optional[Path] = None, wopr_path: Optional[Path] = None):
        """Initialize experiment framework"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        if wopr_path is None:
            wopr_path = project_root / "data" / "wopr_plans"

        self.project_root = project_root
        self.wopr_path = Path(wopr_path)
        self.experiments_dir = self.wopr_path / "experiments"
        self.experiments_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.log_parser = None
        if LOG_PARSING_AVAILABLE and CentralizedLogParser:
            self.log_parser = CentralizedLogParser(project_root=project_root)

        self.syphon = None
        if SYPHON_AVAILABLE and SYPHONSystem:
            self.syphon = SYPHONSystem(project_root)

        self.simulation = None
        if SIMULATION_AVAILABLE and Jarvis10000YearSimulation:
            self.simulation = Jarvis10000YearSimulation(project_root)

        logger.info("WOPR Experiment Framework initialized")

    def create_experiment(
        self,
        name: str,
        description: str,
        control_config: Dict[str, Any],
        experiment_config: Dict[str, Any],
        current_situation: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create an A/B experiment

        Args:
            name: Experiment name
            description: Experiment description
            control_config: Control scenario (A) configuration
            experiment_config: Experiment scenario (B) configuration
            current_situation: Current situation baseline (optional)

        Returns:
            Experiment ID
        """
        experiment_id = str(uuid4())

        # Create scenarios
        control_scenario = ExperimentScenario(
            scenario_id=f"{experiment_id}_control",
            scenario_type=ScenarioType.CONTROL,
            name=f"{name} - Control (A)",
            description=f"Control scenario for {description}",
            configuration=control_config,
            baseline_state=current_situation or {}
        )

        experiment_scenario = ExperimentScenario(
            scenario_id=f"{experiment_id}_experiment",
            scenario_type=ScenarioType.EXPERIMENT,
            name=f"{name} - Experiment (B)",
            description=f"Experiment scenario for {description}",
            configuration=experiment_config,
            baseline_state=current_situation or {}
        )

        # Save experiment
        experiment_data = {
            "experiment_id": experiment_id,
            "name": name,
            "description": description,
            "status": ExperimentStatus.CREATED.value,
            "created": datetime.now().isoformat(),
            "control_scenario": control_scenario.to_dict(),
            "experiment_scenario": experiment_scenario.to_dict(),
            "current_situation": current_situation
        }

        experiment_file = self.experiments_dir / f"{experiment_id}.json"
        with open(experiment_file, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Created experiment: {experiment_id} - {name}")

        return experiment_id

    def capture_current_situation(self) -> Dict[str, Any]:
        """
        Capture current situation as baseline

        Returns:
            Current situation snapshot
        """
        situation = {
            "timestamp": datetime.now().isoformat(),
            "system_state": {},
            "log_patterns": {},
            "metrics": {}
        }

        # Capture log patterns if available
        if self.log_parser:
            try:
                # Get recent patterns
                pattern_summary = self.log_parser.get_pattern_summary()
                situation["log_patterns"] = {
                    "total_patterns": pattern_summary.get("total_patterns", 0),
                    "patterns": pattern_summary.get("patterns", {})
                }

                # Get startup logs
                startup_logs = self.log_parser.get_startup_logs()
                situation["startup_logs_count"] = len(startup_logs)
            except Exception as e:
                logger.warning(f"Error capturing log patterns: {e}")

        return situation

    def run_scenario(
        self,
        scenario: ExperimentScenario,
        duration: float = 60.0
    ) -> ExperimentResult:
        """
        Run a scenario through the pipeline

        Args:
            scenario: Scenario to run
            duration: Duration to run scenario (seconds)

        Returns:
            Experiment result
        """
        logger.info(f"Running scenario: {scenario.name} ({scenario.scenario_type.value})")

        start_time = time.time()
        result = ExperimentResult(
            scenario_id=scenario.scenario_id,
            scenario_type=scenario.scenario_type
        )

        try:
            # Apply scenario configuration
            # (In real implementation, this would apply config changes)
            logger.debug(f"Applying configuration: {scenario.configuration}")

            # Run through SYPHON workflow if available
            if self.syphon:
                try:
                    # Extract actionable intelligence from scenario
                    syphon_data = {
                        "scenario_id": scenario.scenario_id,
                        "scenario_type": scenario.scenario_type.value,
                        "configuration": scenario.configuration,
                        "timestamp": datetime.now().isoformat()
                    }

                    extracted = self.syphon.extract_actionable_intelligence(
                        source_type="experiment",
                        content=json.dumps(syphon_data)
                    )

                    result.metrics["syphon_extracted"] = True
                    result.metrics["syphon_items"] = len(extracted.actionable_items) if hasattr(extracted, 'actionable_items') else 0
                except Exception as e:
                    logger.warning(f"SYPHON processing error: {e}")
                    result.errors.append(f"SYPHON error: {e}")

            # Run scenario for specified duration
            # (In real implementation, this would run actual operations)
            time.sleep(min(duration, 5.0))  # Cap at 5 seconds for demo

            # Collect metrics
            if self.log_parser:
                try:
                    # Parse logs during scenario
                    log_files = self.log_parser.discover_log_files()
                    entries = []
                    for log_file in log_files[:5]:  # Limit for performance
                        entries.extend(self.log_parser.parse_log_file(log_file))

                    # Aggregate patterns
                    pattern_agg = self.log_parser.aggregate_by_patterns(entries)

                    result.logs = [e.to_dict() for e in entries[-50:]]  # Last 50
                    result.patterns = pattern_agg.get("pattern_details", {})
                    result.metrics["log_entries"] = len(entries)
                    result.metrics["patterns_matched"] = pattern_agg.get("patterns_matched", 0)
                except Exception as e:
                    logger.warning(f"Log parsing error: {e}")
                    result.errors.append(f"Log parsing error: {e}")

            # Run through Matrix comparison if available
            if self.simulation:
                try:
                    # Run simulation for pattern analysis
                    sim_result = self.simulation.run_simulation(
                        target_cycles=100,  # Quick simulation
                        acceleration_factor=1000.0,
                        focus_area=f"experiment_{scenario.scenario_id}"
                    )

                    result.metrics["simulation_cycles"] = sim_result.get("cycles", 0)
                    result.metrics["peak_solutions"] = sim_result.get("peak_solutions", 0)
                except Exception as e:
                    logger.warning(f"Simulation error: {e}")
                    result.errors.append(f"Simulation error: {e}")

            result.metrics["success"] = True
            result.metrics["scenario_applied"] = True

        except Exception as e:
            logger.error(f"Error running scenario: {e}")
            result.errors.append(str(e))
            result.metrics["success"] = False

        result.duration = time.time() - start_time
        result.timestamp = datetime.now()

        logger.info(f"Scenario completed: {scenario.name} (duration: {result.duration:.2f}s)")

        return result

    def run_experiment(
        self,
        experiment_id: str,
        duration: float = 60.0
    ) -> ExperimentComparison:
        """
        Run both A and B scenarios and compare

        Args:
            experiment_id: Experiment ID
            duration: Duration to run each scenario (seconds)

        Returns:
            Experiment comparison
        """
        # Load experiment
        experiment_file = self.experiments_dir / f"{experiment_id}.json"
        if not experiment_file.exists():
            raise ValueError(f"Experiment {experiment_id} not found")

        with open(experiment_file, 'r', encoding='utf-8') as f:
            experiment_data = json.load(f)

        # Update status
        experiment_data["status"] = ExperimentStatus.RUNNING.value
        experiment_data["started"] = datetime.now().isoformat()
        with open(experiment_file, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Running experiment: {experiment_id}")

        # Reconstruct scenarios
        control_data = experiment_data["control_scenario"]
        experiment_data_scenario = experiment_data["experiment_scenario"]

        control_scenario = ExperimentScenario(
            scenario_id=control_data["scenario_id"],
            scenario_type=ScenarioType(control_data["scenario_type"]),
            name=control_data["name"],
            description=control_data["description"],
            configuration=control_data["configuration"],
            baseline_state=control_data.get("baseline_state", {})
        )

        experiment_scenario = ExperimentScenario(
            scenario_id=experiment_data_scenario["scenario_id"],
            scenario_type=ScenarioType(experiment_data_scenario["scenario_type"]),
            name=experiment_data_scenario["name"],
            description=experiment_data_scenario["description"],
            configuration=experiment_data_scenario["configuration"],
            baseline_state=experiment_data_scenario.get("baseline_state", {})
        )

        # Run control scenario (A)
        logger.info("Running control scenario (A)...")
        control_result = self.run_scenario(control_scenario, duration)

        # Run experiment scenario (B)
        logger.info("Running experiment scenario (B)...")
        experiment_result = self.run_scenario(experiment_scenario, duration)

        # Compare results
        comparison = self.compare_results(experiment_id, control_result, experiment_result)

        # Update experiment status
        experiment_data["status"] = ExperimentStatus.COMPLETED.value
        experiment_data["completed"] = datetime.now().isoformat()
        experiment_data["comparison"] = comparison.to_dict()
        with open(experiment_file, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Experiment completed: {experiment_id}")

        return comparison

    def compare_results(
        self,
        experiment_id: str,
        control_result: ExperimentResult,
        experiment_result: ExperimentResult
    ) -> ExperimentComparison:
        """
        Compare A and B results

        Args:
            experiment_id: Experiment ID
            control_result: Control (A) result
            experiment_result: Experiment (B) result

        Returns:
            Comparison results
        """
        logger.info("Comparing results...")

        comparison = ExperimentComparison(
            experiment_id=experiment_id,
            control_result=control_result,
            experiment_result=experiment_result
        )

        # Compare metrics
        control_metrics = control_result.metrics
        experiment_metrics = experiment_result.metrics

        differences = {}
        recommendations = []

        # Compare key metrics
        for key in set(control_metrics.keys()) | set(experiment_metrics.keys()):
            control_val = control_metrics.get(key)
            experiment_val = experiment_metrics.get(key)

            if control_val != experiment_val:
                if isinstance(control_val, (int, float)) and isinstance(experiment_val, (int, float)):
                    diff = experiment_val - control_val
                    diff_pct = (diff / control_val * 100) if control_val != 0 else 0
                    differences[key] = {
                        "control": control_val,
                        "experiment": experiment_val,
                        "difference": diff,
                        "difference_percent": diff_pct
                    }
                else:
                    differences[key] = {
                        "control": control_val,
                        "experiment": experiment_val
                    }

        comparison.differences = differences

        # Determine winner (simplified logic)
        # In real implementation, this would use more sophisticated analysis
        control_score = 0
        experiment_score = 0

        # Compare pattern counts (fewer is better for errors)
        control_patterns = control_result.patterns
        experiment_patterns = experiment_result.patterns

        control_error_count = sum(
            1 for p in control_patterns.values()
            if p.get("severity") in ["error", "critical"]
        )
        experiment_error_count = sum(
            1 for p in experiment_patterns.values()
            if p.get("severity") in ["error", "critical"]
        )

        if experiment_error_count < control_error_count:
            experiment_score += 2
            recommendations.append(f"Experiment has {control_error_count - experiment_error_count} fewer error patterns")
        elif control_error_count < experiment_error_count:
            control_score += 2

        # Compare log entry counts
        control_logs = control_result.metrics.get("log_entries", 0)
        experiment_logs = experiment_result.metrics.get("log_entries", 0)

        if abs(control_logs - experiment_logs) > 10:
            if experiment_logs < control_logs:
                experiment_score += 1
                recommendations.append("Experiment produced fewer log entries")
            else:
                control_score += 1

        # Compare success rates
        if control_result.metrics.get("success") and not experiment_result.metrics.get("success"):
            control_score += 3
            recommendations.append("Control scenario succeeded, experiment failed")
        elif experiment_result.metrics.get("success") and not control_result.metrics.get("success"):
            experiment_score += 3
            recommendations.append("Experiment succeeded, control failed")

        # Determine winner
        if experiment_score > control_score:
            comparison.winner = "experiment"
            comparison.confidence = min(experiment_score / 5.0, 1.0)
            recommendations.append("Experiment (B) appears to be better")
        elif control_score > experiment_score:
            comparison.winner = "control"
            comparison.confidence = min(control_score / 5.0, 1.0)
            recommendations.append("Control (A) appears to be better")
        else:
            comparison.winner = "tie"
            comparison.confidence = 0.5
            recommendations.append("Results are inconclusive - both scenarios similar")

        comparison.recommendations = recommendations

        logger.info(f"Comparison complete: Winner = {comparison.winner} (confidence: {comparison.confidence:.2f})")

        return comparison

    def get_experiment(self, experiment_id: str) -> Dict[str, Any]:
        try:
            """Get experiment data"""
            experiment_file = self.experiments_dir / f"{experiment_id}.json"
            if not experiment_file.exists():
                raise ValueError(f"Experiment {experiment_id} not found")

            with open(experiment_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in get_experiment: {e}", exc_info=True)
            raise
    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments"""
        experiments = []
        for experiment_file in self.experiments_dir.glob("*.json"):
            try:
                with open(experiment_file, 'r', encoding='utf-8') as f:
                    exp_data = json.load(f)
                    experiments.append({
                        "experiment_id": exp_data.get("experiment_id", experiment_file.stem),
                        "name": exp_data.get("name", "Unknown"),
                        "status": exp_data.get("status", "unknown"),
                        "created": exp_data.get("created", "")
                    })
            except Exception as e:
                logger.warning(f"Error reading experiment {experiment_file}: {e}")

        return sorted(experiments, key=lambda x: x.get("created", ""), reverse=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WOPR Experiment Framework")
    parser.add_argument("--create", action="store_true", help="Create new experiment")
    parser.add_argument("--run", help="Run experiment by ID")
    parser.add_argument("--list", action="store_true", help="List experiments")
    parser.add_argument("--show", help="Show experiment by ID")
    parser.add_argument("--capture", action="store_true", help="Capture current situation")

    args = parser.parse_args()

    framework = WOPRExperimentFramework()

    if args.capture:
        situation = framework.capture_current_situation()
        print(json.dumps(situation, indent=2))

    elif args.create:
        # Example: Create experiment
        current = framework.capture_current_situation()

        experiment_id = framework.create_experiment(
            name="Log Parsing Optimization",
            description="Test optimized log parsing vs current",
            control_config={"log_parser": "current", "aggregation": "standard"},
            experiment_config={"log_parser": "optimized", "aggregation": "enhanced"},
            current_situation=current
        )

        print(f"Created experiment: {experiment_id}")

    elif args.run:
        comparison = framework.run_experiment(args.run, duration=30.0)
        print(json.dumps(comparison.to_dict(), indent=2))

    elif args.show:
        experiment = framework.get_experiment(args.show)
        print(json.dumps(experiment, indent=2))

    elif args.list:
        experiments = framework.list_experiments()
        print(json.dumps(experiments, indent=2))

    else:
        parser.print_help()

