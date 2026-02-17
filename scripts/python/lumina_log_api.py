#!/usr/bin/env python3
"""
Lumina Log API - Integrated Log Parsing and Aggregation
Part of Lumina API with Jarvis-directed execution and SYPHON/Matrix integration

Features:
- Pattern matching and registry
- Intelligent execution via Jarvis
- SYPHON workflow integration for testing/simulations
- Matrix/lattice comparison for pattern analysis
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
from enum import Enum

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Flask not installed. Install with: pip install flask flask-cors")
    exit(1)

try:
    from centralized_log_parser import CentralizedLogParser, LogSource, LogLevel
    from log_aggregation_service import LogAggregationService
except ImportError:
    CentralizedLogParser = None
    LogAggregationService = None

try:
    from jarvis_10000_year_simulation import Jarvis10000YearSimulation, MatrixLattice
except ImportError:
    Jarvis10000YearSimulation = None
    MatrixLattice = None

try:
    from syphon_system import SYPHONSystem
except ImportError:
    SYPHONSystem = None

from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LuminaLogAPI")

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global instances
log_parser: Optional[CentralizedLogParser] = None
log_service: Optional[LogAggregationService] = None
simulation: Optional[Jarvis10000YearSimulation] = None
syphon: Optional[SYPHONSystem] = None


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))


def get_log_parser() -> CentralizedLogParser:
    try:
        """Get or create log parser instance"""
        global log_parser
        if log_parser is None and CentralizedLogParser:
            project_root = Path(__file__).parent.parent.parent
            log_parser = CentralizedLogParser(project_root=project_root)
        return log_parser


    except Exception as e:
        logger.error(f"Error in get_log_parser: {e}", exc_info=True)
        raise
def get_log_service() -> LogAggregationService:
    try:
        """Get or create log aggregation service"""
        global log_service
        if log_service is None and LogAggregationService:
            project_root = Path(__file__).parent.parent.parent
            log_service = LogAggregationService(project_root=project_root, interval=300)
        return log_service


    except Exception as e:
        logger.error(f"Error in get_log_service: {e}", exc_info=True)
        raise
def get_simulation() -> Optional[Jarvis10000YearSimulation]:
    try:
        """Get or create simulation instance"""
        global simulation
        if simulation is None and Jarvis10000YearSimulation:
            project_root = Path(__file__).parent.parent.parent
            simulation = Jarvis10000YearSimulation(project_root)
        return simulation


    except Exception as e:
        logger.error(f"Error in get_simulation: {e}", exc_info=True)
        raise
def get_syphon() -> Optional[SYPHONSystem]:
    try:
        """Get or create SYPHON system instance"""
        global syphon
        if syphon is None and SYPHONSystem:
            project_root = Path(__file__).parent.parent.parent
            syphon = SYPHONSystem(project_root)
        return syphon


    except Exception as e:
        logger.error(f"Error in get_syphon: {e}", exc_info=True)
        raise
# ============================================================================
# Health and Status Endpoints
# ============================================================================

@app.route('/lumina/logs/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Lumina Log API",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "log_parser": log_parser is not None,
            "log_service": log_service is not None,
            "simulation": simulation is not None,
            "syphon": syphon is not None
        }
    })


# ============================================================================
# Log Parsing Endpoints
# ============================================================================

@app.route('/lumina/logs/parse', methods=['POST', 'GET'])
def parse_logs():
    """Parse all logs and aggregate patterns"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        result = parser.parse_all_logs()

        return jsonify({
            "success": True,
            "data": result,
            "message": "Logs parsed and aggregated successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error parsing logs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/logs/startup', methods=['GET'])
def get_startup_logs():
    """Get startup logs (IDE or services)"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        source_param = request.args.get('source', 'all')
        if source_param == 'ide':
            source = LogSource.IDE_STARTUP
        elif source_param == 'service':
            source = LogSource.SERVICE_STARTUP
        else:
            source = None

        startup_logs = parser.get_startup_logs(source)

        return jsonify({
            "success": True,
            "count": len(startup_logs),
            "logs": [entry.to_dict() for entry in startup_logs[-100:]]  # Last 100
        }), 200
    except Exception as e:
        logger.error(f"Error getting startup logs: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Pattern Registry Endpoints
# ============================================================================

@app.route('/lumina/logs/patterns', methods=['GET'])
def get_patterns():
    """Get all registered patterns"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        pattern_summary = parser.get_pattern_summary()

        return jsonify({
            "success": True,
            "data": pattern_summary
        }), 200
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/logs/patterns/<pattern_id>', methods=['GET'])
def get_pattern(pattern_id: str):
    """Get specific pattern details"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        if pattern_id not in parser.patterns:
            return jsonify({"error": f"Pattern {pattern_id} not found"}), 404

        pattern = parser.patterns[pattern_id]

        return jsonify({
            "success": True,
            "pattern": pattern.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting pattern: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/logs/patterns', methods=['POST'])
def add_pattern():
    """Add or update a pattern"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Create pattern from data
        from centralized_log_parser import LogPattern
        pattern = LogPattern(
            pattern_id=data.get('pattern_id', f"custom_{datetime.now().timestamp()}"),
            pattern_name=data.get('pattern_name', 'Custom Pattern'),
            regex=data.get('regex', ''),
            description=data.get('description', ''),
            category=data.get('category', 'custom'),
            severity=data.get('severity', 'info'),
            occurrences=0,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            examples=[]
        )

        parser.patterns[pattern.pattern_id] = pattern
        parser._save_patterns()

        return jsonify({
            "success": True,
            "pattern": pattern.to_dict(),
            "message": "Pattern added successfully"
        }), 201
    except Exception as e:
        logger.error(f"Error adding pattern: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Aggregation Endpoints
# ============================================================================

@app.route('/lumina/logs/aggregate', methods=['POST', 'GET'])
def aggregate_logs():
    """Aggregate logs by patterns and time"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        # Get parameters
        time_window = request.args.get('time_window', 'hour')
        source_filter = request.args.get('source', None)

        # Discover and parse logs
        log_files = parser.discover_log_files()
        all_entries = []
        for log_file in log_files:
            entries = parser.parse_log_file(log_file)
            if source_filter:
                entries = [e for e in entries if e.source.value == source_filter]
            all_entries.extend(entries)

        # Aggregate by patterns
        pattern_aggregation = parser.aggregate_by_patterns(all_entries)

        # Aggregate by time
        time_aggregation = parser.aggregate_by_time(all_entries, time_window=time_window)

        return jsonify({
            "success": True,
            "data": {
                "pattern_aggregation": pattern_aggregation,
                "time_aggregation": time_aggregation,
                "total_entries": len(all_entries)
            }
        }), 200
    except Exception as e:
        logger.error(f"Error aggregating logs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/logs/trends', methods=['GET'])
def get_trends():
    """Get pattern trends over time"""
    try:
        service = get_log_service()
        if not service:
            return jsonify({"error": "Log service not available"}), 503

        pattern_id = request.args.get('pattern_id', None)
        hours = int(request.args.get('hours', 24))

        trends = service.get_pattern_trends(pattern_id, hours)

        return jsonify({
            "success": True,
            "data": trends,
            "hours": hours
        }), 200
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Debugging and Insights Endpoints
# ============================================================================

@app.route('/lumina/logs/insights', methods=['GET'])
def get_insights():
    """Get debugging insights"""
    try:
        service = get_log_service()
        if not service:
            return jsonify({"error": "Log service not available"}), 503

        insights = service.get_debugging_insights()

        return jsonify({
            "success": True,
            "data": insights
        }), 200
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Jarvis-Directed Execution Endpoints
# ============================================================================

@app.route('/lumina/logs/jarvis/analyze', methods=['POST'])
def jarvis_analyze():
    """
    Jarvis-directed log analysis
    Intelligently determines what analysis to perform based on current state
    """
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        # Get current state
        data = request.get_json() or {}
        focus = data.get('focus', 'all')
        urgency = data.get('urgency', 'normal')

        # Jarvis decision: What analysis is needed?
        decision_context = DecisionContext(
            action="analyze_logs",
            context={
                "focus": focus,
                "urgency": urgency,
                "available_patterns": len(parser.patterns)
            }
        )

        # Use decision tree to determine action
        decision = decide('jarvis_log_analysis', decision_context)

        # Execute based on decision
        if decision.outcome == DecisionOutcome.PROCEED:
            # Parse and aggregate
            result = parser.parse_all_logs()

            # Get insights
            service = get_log_service()
            if service:
                insights = service.get_debugging_insights()
                result['insights'] = insights

            return jsonify({
                "success": True,
                "data": result,
                "jarvis_decision": {
                    "outcome": decision.outcome.value,
                    "reasoning": decision.reasoning,
                    "recommended_actions": decision.recommended_actions
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Jarvis determined analysis not needed",
                "jarvis_decision": {
                    "outcome": decision.outcome.value,
                    "reasoning": decision.reasoning
                }
            }), 200

    except Exception as e:
        logger.error(f"Error in Jarvis analysis: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/logs/jarvis/execute', methods=['POST'])
def jarvis_execute():
    """
    Jarvis-directed execution
    Intelligently executes log operations as needed
    """
    try:
        data = request.get_json() or {}
        operation = data.get('operation', 'auto')

        parser = get_log_parser()
        service = get_log_service()

        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        # Jarvis decision: What should be executed?
        decision_context = DecisionContext(
            action="execute_log_operations",
            context={
                "operation": operation,
                "service_running": service is not None and service.running if service else False
            }
        )

        decision = decide('jarvis_log_execution', decision_context)

        results = {}

        if decision.outcome == DecisionOutcome.PROCEED:
            # Execute based on decision
            if 'parse' in decision.recommended_actions:
                results['parse'] = parser.parse_all_logs()

            if 'aggregate' in decision.recommended_actions and service:
                service._aggregate_cycle()
                results['aggregate'] = "completed"

            if 'start_service' in decision.recommended_actions and service:
                if not service.running:
                    service.start()
                    results['service'] = "started"

            return jsonify({
                "success": True,
                "results": results,
                "jarvis_decision": {
                    "outcome": decision.outcome.value,
                    "reasoning": decision.reasoning,
                    "actions_taken": decision.recommended_actions
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Jarvis determined execution not needed",
                "jarvis_decision": {
                    "outcome": decision.outcome.value,
                    "reasoning": decision.reasoning
                }
            }), 200

    except Exception as e:
        logger.error(f"Error in Jarvis execution: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# SYPHON Workflow Integration (Testing/Simulations)
# ============================================================================

@app.route('/lumina/logs/syphon/test', methods=['POST'])
def syphon_test():
    """
    Route log pattern testing through SYPHON workflow
    For testing and simulations
    """
    try:
        syphon_system = get_syphon()
        if not syphon_system:
            return jsonify({"error": "SYPHON system not available"}), 503

        data = request.get_json() or {}
        pattern_id = data.get('pattern_id')
        test_scenario = data.get('test_scenario', 'default')

        # Extract test data through SYPHON
        test_data = {
            "pattern_id": pattern_id,
            "test_scenario": test_scenario,
            "timestamp": datetime.now().isoformat()
        }

        # Process through SYPHON
        # (SYPHON extracts actionable intelligence from test scenarios)
        extracted = syphon_system.extract_actionable_intelligence(
            source_type="test",
            content=json.dumps(test_data)
        )

        return jsonify({
            "success": True,
            "data": {
                "test_data": test_data,
                "syphon_extracted": extracted.to_dict() if hasattr(extracted, 'to_dict') else str(extracted)
            },
            "message": "Test routed through SYPHON workflow"
        }), 200

    except Exception as e:
        logger.error(f"Error in SYPHON test: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/logs/syphon/simulate', methods=['POST'])
def syphon_simulate():
    """
    Route log pattern simulation through SYPHON and Matrix comparison
    Uses 10,000 year simulation framework for pattern analysis
    """
    try:
        syphon_system = get_syphon()
        sim = get_simulation()

        if not syphon_system:
            return jsonify({"error": "SYPHON system not available"}), 503
        if not sim:
            return jsonify({"error": "Simulation system not available"}), 503

        data = request.get_json() or {}
        pattern_id = data.get('pattern_id')
        cycles = data.get('cycles', 1000)  # Default to 1000 cycles (not full 10k)

        # Extract through SYPHON first
        sim_data = {
            "pattern_id": pattern_id,
            "cycles": cycles,
            "timestamp": datetime.now().isoformat()
        }

        extracted = syphon_system.extract_actionable_intelligence(
            source_type="simulation",
            content=json.dumps(sim_data)
        )

        # Run simulation with matrix comparison
        # Compare patterns across different matrix lattices
        simulation_result = sim.run_simulation(
            target_cycles=cycles,
            acceleration_factor=1000.0,
            focus_area=f"log_pattern_{pattern_id}"
        )

        # Map to our real dimensions (as user mentioned)
        # The simulation uses 21 vectors as potential dimensions
        # We map to our actual log pattern dimensions
        dimension_mapping = {
            "performance": MatrixLattice.PERFORMANCE if MatrixLattice else None,
            "reliability": MatrixLattice.RELIABILITY if MatrixLattice else None,
            "resource": MatrixLattice.RESOURCE if MatrixLattice else None,
            "security": MatrixLattice.SECURITY if MatrixLattice else None,
            "maintainability": MatrixLattice.MAINTAINABILITY if MatrixLattice else None,
        }

        return jsonify({
            "success": True,
            "data": {
                "pattern_id": pattern_id,
                "simulation_result": simulation_result,
                "syphon_extracted": extracted.to_dict() if hasattr(extracted, 'to_dict') else str(extracted),
                "dimension_mapping": {k: v.value if v else None for k, v in dimension_mapping.items()},
                "note": "Simulation uses 21 vectors as potential dimensions, mapped to real log pattern dimensions"
            },
            "message": "Simulation routed through SYPHON and Matrix comparison"
        }), 200

    except Exception as e:
        logger.error(f"Error in SYPHON simulation: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Output Locations Endpoint
# ============================================================================

@app.route('/lumina/logs/outputs', methods=['GET'])
def get_output_locations():
    """Get all output file locations"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

        service = get_log_service()

        outputs = {
            "aggregation_results": str(parser.aggregated_data_dir / "aggregation_*.json"),
            "pattern_registry": str(parser.patterns_file),
            "pattern_trends": str(service.aggregation_history_dir / "pattern_trends.json") if service else None,
            "aggregation_history": str(service.aggregation_history_dir) if service else None,
            "base_directory": str(parser.aggregated_data_dir)
        }

        return jsonify({
            "success": True,
            "outputs": outputs
        }), 200
    except Exception as e:
        logger.error(f"Error getting output locations: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import sys

    project_root = Path(__file__).parent.parent.parent

    port = 8001  # Different port from R5 API
    host = '0.0.0.0'

    logger.info(f"Starting Lumina Log API server on {host}:{port}")
    logger.info(f"Project root: {project_root}")
    logger.info("Endpoints:")
    logger.info("  GET  /lumina/logs/health - Health check")
    logger.info("  POST /lumina/logs/parse - Parse all logs")
    logger.info("  GET  /lumina/logs/startup - Get startup logs")
    logger.info("  GET  /lumina/logs/patterns - Get all patterns")
    logger.info("  GET  /lumina/logs/patterns/<id> - Get pattern")
    logger.info("  POST /lumina/logs/patterns - Add pattern")
    logger.info("  GET  /lumina/logs/aggregate - Aggregate logs")
    logger.info("  GET  /lumina/logs/trends - Get pattern trends")
    logger.info("  GET  /lumina/logs/insights - Get debugging insights")
    logger.info("  POST /lumina/logs/jarvis/analyze - Jarvis-directed analysis")
    logger.info("  POST /lumina/logs/jarvis/execute - Jarvis-directed execution")
    logger.info("  POST /lumina/logs/syphon/test - SYPHON test workflow")
    logger.info("  POST /lumina/logs/syphon/simulate - SYPHON simulation with Matrix")
    logger.info("  GET  /lumina/logs/outputs - Get output locations")

    app.run(host=host, port=port, debug=False)

