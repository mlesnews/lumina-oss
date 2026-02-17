#!/usr/bin/env python3
"""
Analyze Lumina OTS and Progressive Scaling

Analysis and visualization script for Outcomes of Intent (OTS) and
progressive infinite scaling metrics.

@LUMINA @ANALYSIS @OTS @SCALING
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import statistics

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_data_mining_feedback_loop import (
    LuminaDataMiner,
    ProgressiveInfiniteScaling,
    LuminaFeedbackLoop
)

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaOTSAnalysis")


def analyze_ots_distribution(data_miner: LuminaDataMiner) -> Dict[str, Any]:
    """Analyze OTS distribution and patterns"""
    logger.info(f"Analyzing {len(data_miner.ots_list)} OTS entries...")
    ots_list = data_miner.ots_list

    if not ots_list:
        return {"error": "No OTS data found"}

    logger.info("Calculating alignment distribution...")
    # Alignment distribution
    alignments = [ots.alignment_score for ots in ots_list]

    # Scaling factor distribution
    scaling_factors = [ots.scaling_factor for ots in ots_list if ots.scaling_factor > 0]

    # Intent type distribution
    intent_types = {}
    for ots in ots_list:
        intent_type = ots.intent.intent_type
        intent_types[intent_type] = intent_types.get(intent_type, 0) + 1

    # Outcome type distribution
    outcome_types = {}
    for ots in ots_list:
        if ots.outcome:
            outcome_type = ots.outcome.outcome_type
            outcome_types[outcome_type] = outcome_types.get(outcome_type, 0) + 1

    # Deviation analysis
    deviation_types = {}
    for ots in ots_list:
        if ots.deviation_analysis.get('has_deviation'):
            dev_type = ots.deviation_analysis.get('deviation_type', 'unknown')
            deviation_types[dev_type] = deviation_types.get(dev_type, 0) + 1

    analysis = {
        'total_ots': len(ots_list),
        'with_outcomes': len([ots for ots in ots_list if ots.outcome is not None]),
        'without_outcomes': len([ots for ots in ots_list if ots.outcome is None]),
        'alignment_stats': {
            'mean': statistics.mean(alignments) if alignments else 0.0,
            'median': statistics.median(alignments) if alignments else 0.0,
            'stdev': statistics.stdev(alignments) if len(alignments) > 1 else 0.0,
            'min': min(alignments) if alignments else 0.0,
            'max': max(alignments) if alignments else 0.0
        },
        'scaling_stats': {
            'mean': statistics.mean(scaling_factors) if scaling_factors else 0.0,
            'median': statistics.median(scaling_factors) if scaling_factors else 0.0,
            'stdev': statistics.stdev(scaling_factors) if len(scaling_factors) > 1 else 0.0,
            'min': min(scaling_factors) if scaling_factors else 0.0,
            'max': max(scaling_factors) if scaling_factors else 0.0
        },
        'intent_type_distribution': intent_types,
        'outcome_type_distribution': outcome_types,
        'deviation_distribution': deviation_types,
        'alignment_buckets': {
            'high (0.8-1.0)': len([a for a in alignments if 0.8 <= a <= 1.0]),
            'medium (0.5-0.8)': len([a for a in alignments if 0.5 <= a < 0.8]),
            'low (0.0-0.5)': len([a for a in alignments if 0.0 <= a < 0.5])
        }
    }

    return analysis


def analyze_scaling_trends(scaling: ProgressiveInfiniteScaling) -> Dict[str, Any]:
    """Analyze progressive scaling trends"""
    logger.info(f"Analyzing {len(scaling.metrics)} scaling metrics...")
    metrics = scaling.metrics

    if not metrics:
        return {"error": "No scaling metrics found"}

    trends = {
        'total_metrics': len(metrics),
        'metrics_analysis': {},
        'overall_trends': {
            'increasing': 0,
            'decreasing': 0,
            'stable': 0
        },
        'improvement_summary': {
            'average_improvement_rate': 0.0,
            'total_improvement': 0.0,
            'metrics_improving': 0,
            'metrics_declining': 0
        }
    }

    total_improvement_rate = 0.0
    total_improvement = 0.0

    for metric_name, metric in metrics.items():
        metric_analysis = {
            'current_value': metric.current_value,
            'baseline_value': metric.baseline_value,
            'scaling_factor': metric.scaling_factor,
            'trend': metric.trend,
            'improvement_rate': metric.improvement_rate,
            'infinite_scaling_potential': scaling.calculate_infinite_scaling_potential(metric_name),
            'measurement_count': len(metric.measurements)
        }

        trends['metrics_analysis'][metric_name] = metric_analysis
        trends['overall_trends'][metric.trend] += 1

        total_improvement_rate += metric.improvement_rate
        total_improvement += metric.scaling_factor

        if metric.improvement_rate > 0:
            trends['improvement_summary']['metrics_improving'] += 1
        elif metric.improvement_rate < 0:
            trends['improvement_summary']['metrics_declining'] += 1

    if len(metrics) > 0:
        trends['improvement_summary']['average_improvement_rate'] = total_improvement_rate / len(metrics)
        trends['improvement_summary']['total_improvement'] = total_improvement / len(metrics)

    return trends


def generate_comprehensive_report(project_root: Path) -> Dict[str, Any]:
    """Generate comprehensive analysis report"""
    logger.info("📊 Generating comprehensive OTS and Scaling analysis...")

    # Initialize systems
    logger.info("Initializing data miner...")
    data_miner = LuminaDataMiner(project_root)
    logger.info("Initializing scaling system...")
    scaling = ProgressiveInfiniteScaling(project_root)

    logger.info("Analyzing OTS...")

    # Analyze OTS
    ots_analysis = analyze_ots_distribution(data_miner)

    # Analyze scaling
    scaling_analysis = analyze_scaling_trends(scaling)

    # Generate recommendations
    recommendations = []

    # OTS recommendations
    if ots_analysis.get('alignment_stats', {}).get('mean', 0.0) < 0.7:
        recommendations.append({
            'category': 'OTS Alignment',
            'priority': 'high',
            'issue': 'Average alignment score is below 70%',
            'recommendation': 'Improve intent documentation and outcome tracking to increase alignment',
            'action': 'Review low-alignment OTS entries and improve tracking'
        })

    if ots_analysis.get('without_outcomes', 0) > ots_analysis.get('total_ots', 1) * 0.2:
        recommendations.append({
            'category': 'OTS Coverage',
            'priority': 'medium',
            'issue': f"{ots_analysis.get('without_outcomes', 0)} intents have no tracked outcomes",
            'recommendation': 'Implement better outcome tracking mechanisms',
            'action': 'Add outcome tracking to all intent sources'
        })

    # Scaling recommendations
    if scaling_analysis.get('improvement_summary', {}).get('average_improvement_rate', 0.0) < 0:
        recommendations.append({
            'category': 'Scaling Trends',
            'priority': 'high',
            'issue': 'Average improvement rate is negative',
            'recommendation': 'Review declining metrics and address root causes',
            'action': 'Analyze metrics with negative trends and optimize'
        })

    report = {
        'timestamp': datetime.now().isoformat(),
        'ots_analysis': ots_analysis,
        'scaling_analysis': scaling_analysis,
        'recommendations': recommendations,
        'summary': {
            'total_intents': len(data_miner.intents),
            'total_outcomes': len(data_miner.outcomes),
            'total_ots': len(data_miner.ots_list),
            'total_scaling_metrics': len(scaling.metrics),
            'overall_alignment': ots_analysis.get('alignment_stats', {}).get('mean', 0.0),
            'overall_scaling': scaling_analysis.get('improvement_summary', {}).get('total_improvement', 0.0)
        }
    }

    return report


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Analyze Lumina OTS and Progressive Scaling")
        parser.add_argument("--ots", action="store_true", help="Analyze OTS distribution")
        parser.add_argument("--scaling", action="store_true", help="Analyze scaling trends")
        parser.add_argument("--full", action="store_true", help="Generate full comprehensive report")
        parser.add_argument("--output", type=Path, help="Output file path (JSON)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent

        if args.full or (not args.ots and not args.scaling):
            # Generate full report
            report = generate_comprehensive_report(project_root)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"✅ Report saved to: {args.output}")
            else:
                print(json.dumps(report, indent=2, default=str))

        else:
            data_miner = LuminaDataMiner(project_root)
            scaling = ProgressiveInfiniteScaling(project_root)

            if args.ots:
                analysis = analyze_ots_distribution(data_miner)
                print(json.dumps(analysis, indent=2, default=str))

            if args.scaling:
                analysis = analyze_scaling_trends(scaling)
                print(json.dumps(analysis, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()