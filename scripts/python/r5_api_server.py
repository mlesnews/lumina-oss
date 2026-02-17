"""
Lumina API Server (Unified)
REST API for R5 Living Context Matrix and Log Parsing/Aggregation
Integrates with n8n workflows, Jupyter notebooks, Jarvis, SYPHON, and Matrix simulations
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Flask not installed. Install with: pip install flask flask-cors")
    exit(1)

from r5_living_context_matrix import R5LivingContextMatrix, R5Config
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Import log parsing components (optional)
try:
    from centralized_log_parser import CentralizedLogParser, LogSource, LogLevel
    from log_aggregation_service import LogAggregationService
    LOG_PARSING_AVAILABLE = True
except ImportError:
    LOG_PARSING_AVAILABLE = False
    CentralizedLogParser = None
    LogAggregationService = None

# Import simulation components (optional)
try:
    from jarvis_10000_year_simulation import Jarvis10000YearSimulation, MatrixLattice
    SIMULATION_AVAILABLE = True
except ImportError:
    SIMULATION_AVAILABLE = False
    Jarvis10000YearSimulation = None
    MatrixLattice = None

# Import SYPHON (optional)
try:
    from syphon_system import SYPHONSystem
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LuminaAPI")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for n8n and Jupyter integration

# Global instances
r5_system: Optional[R5LivingContextMatrix] = None
log_parser: Optional[CentralizedLogParser] = None
log_service: Optional[LogAggregationService] = None
simulation: Optional[Jarvis10000YearSimulation] = None
syphon: Optional[SYPHONSystem] = None



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def get_r5_system() -> R5LivingContextMatrix:
    try:
        """Get or create R5 system instance"""
        global r5_system
        if r5_system is None:
            # Default project root
            project_root = Path(__file__).parent.parent.parent
            r5_system = R5LivingContextMatrix(project_root)
        return r5_system


    except Exception as e:
        logger.error(f"Error in get_r5_system: {e}", exc_info=True)
        raise
def get_log_parser() -> Optional[CentralizedLogParser]:
    try:
        """Get or create log parser instance"""
        global log_parser
        if log_parser is None and LOG_PARSING_AVAILABLE and CentralizedLogParser:
            project_root = Path(__file__).parent.parent.parent
            log_parser = CentralizedLogParser(project_root=project_root)
        return log_parser


    except Exception as e:
        logger.error(f"Error in get_log_parser: {e}", exc_info=True)
        raise
def get_log_service() -> Optional[LogAggregationService]:
    try:
        """Get or create log aggregation service"""
        global log_service
        if log_service is None and LOG_PARSING_AVAILABLE and LogAggregationService:
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
        if simulation is None and SIMULATION_AVAILABLE and Jarvis10000YearSimulation:
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
        if syphon is None and SYPHON_AVAILABLE and SYPHONSystem:
            project_root = Path(__file__).parent.parent.parent
            syphon = SYPHONSystem(project_root)
        return syphon


    except Exception as e:
        logger.error(f"Error in get_syphon: {e}", exc_info=True)
        raise
@app.route('/r5/health', methods=['GET'])
@app.route('/lumina/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Lumina API (Unified)",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "r5": r5_system is not None,
            "log_parser": log_parser is not None,
            "log_service": log_service is not None,
            "simulation": simulation is not None,
            "syphon": syphon is not None
        }
    })


@app.route('/r5/session', methods=['POST'])
def ingest_session():
    """Ingest a new chat session"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        r5 = get_r5_system()
        session_id = r5.ingest_session(data)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Session ingested successfully"
        }), 201
    except Exception as e:
        logger.error(f"Error ingesting session: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/r5/aggregate', methods=['POST', 'GET'])
def aggregate():
    """Aggregate all sessions"""
    try:
        r5 = get_r5_system()
        aggregated = r5.aggregate_sessions()

        return jsonify({
            "success": True,
            "data": aggregated,
            "message": "Sessions aggregated successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error aggregating sessions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/r5/data', methods=['GET'])
def get_data():
    """Get aggregated data"""
    try:
        r5 = get_r5_system()
        aggregated = r5.aggregate_sessions()

        return jsonify({
            "success": True,
            "data": aggregated
        }), 200
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/r5/peak/extract', methods=['POST'])
def extract_peak_patterns():
    """Extract @PEAK patterns from sessions"""
    try:
        r5 = get_r5_system()
        aggregated = r5.aggregate_sessions()

        patterns = aggregated.get("peak_patterns", [])

        return jsonify({
            "success": True,
            "patterns": patterns,
            "count": len(patterns)
        }), 200
    except Exception as e:
        logger.error(f"Error extracting patterns: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/r5/jupyter/export', methods=['GET', 'POST'])
def export_for_jupyter():
    """Export data formatted for Jupyter notebooks"""
    try:
        r5 = get_r5_system()
        jupyter_data = r5.export_for_jupyter()

        return jsonify({
            "success": True,
            "data": jupyter_data,
            "format": "jupyter"
        }), 200
    except Exception as e:
        logger.error(f"Error exporting for Jupyter: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/r5/stats', methods=['GET'])
def get_stats():
    """Get R5 system statistics"""
    try:
        r5 = get_r5_system()

        session_files = list((r5.config.data_directory / "sessions").glob("*.json"))
        aggregated_files = list((r5.config.data_directory / "aggregated").glob("*.json"))

        stats = {
            "total_sessions": len(session_files),
            "total_aggregated": len(aggregated_files),
            "data_directory": str(r5.config.data_directory),
            "output_file": str(r5.config.output_file),
            "features": {
                "peak_extraction": r5.config.peak_extraction_enabled,
                "whatif_scenarios": r5.config.whatif_enabled,
                "matrix_visualization": r5.config.matrix_visualization_enabled
            },
            "integrations": {
                "n8n": r5.config.n8n_webhook_url is not None,
                "jupyter": r5.config.jupyter_notebook_path is not None
            }
        }

        return jsonify({
            "success": True,
            "stats": stats
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/r5/config', methods=['GET'])
def get_config():
    """Get R5 configuration"""
    try:
        r5 = get_r5_system()

        config = {
            "data_directory": str(r5.config.data_directory),
            "output_file": str(r5.config.output_file),
            "aggregation_interval": r5.config.aggregation_interval,
            "max_sessions": r5.config.max_sessions,
            "features": {
                "peak_extraction": r5.config.peak_extraction_enabled,
                "whatif_scenarios": r5.config.whatif_enabled,
                "matrix_visualization": r5.config.matrix_visualization_enabled
            },
            "integrations": {
                "n8n_webhook_url": r5.config.n8n_webhook_url,
                "jupyter_notebook_path": str(r5.config.jupyter_notebook_path) if r5.config.jupyter_notebook_path else None
            }
        }

        return jsonify({
            "success": True,
            "config": config
        }), 200
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Log Parsing Endpoints (Lumina API)
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


@app.route('/lumina/logs/aggregate', methods=['POST', 'GET'])
def aggregate_logs():
    """Aggregate logs by patterns and time"""
    try:
        parser = get_log_parser()
        if not parser:
            return jsonify({"error": "Log parser not available"}), 503

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


@app.route('/lumina/logs/jarvis/execute', methods=['POST'])
def jarvis_execute():
    """Jarvis-directed execution - intelligently executes log operations as needed"""
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


@app.route('/lumina/logs/syphon/simulate', methods=['POST'])
def syphon_simulate():
    """Route log pattern simulation through SYPHON and Matrix comparison"""
    try:
        syphon_system = get_syphon()
        sim = get_simulation()

        if not syphon_system:
            return jsonify({"error": "SYPHON system not available"}), 503
        if not sim:
            return jsonify({"error": "Simulation system not available"}), 503

        data = request.get_json() or {}
        pattern_id = data.get('pattern_id')
        cycles = data.get('cycles', 1000)  # Default to 1000 cycles

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
        simulation_result = sim.run_simulation(
            target_cycles=cycles,
            acceleration_factor=1000.0,
            focus_area=f"log_pattern_{pattern_id}"
        )

        return jsonify({
            "success": True,
            "data": {
                "pattern_id": pattern_id,
                "simulation_result": simulation_result,
                "syphon_extracted": extracted.to_dict() if hasattr(extracted, 'to_dict') else str(extracted),
                "note": "Simulation uses 21 vectors as potential dimensions, mapped to real log pattern dimensions"
            },
            "message": "Simulation routed through SYPHON and Matrix comparison"
        }), 200

    except Exception as e:
        logger.error(f"Error in SYPHON simulation: {e}")
        return jsonify({"error": str(e)}), 500


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


# ============================================================================
# WOPR Experiment Framework Endpoints
# ============================================================================

@app.route('/wopr/experiments/create', methods=['POST'])
def wopr_create_experiment():
    """Create A/B experiment through WOPR workflow"""
    try:
        from wopr_experiment_framework import WOPRExperimentFramework

        data = request.get_json() or {}

        name = data.get('name', 'Unnamed Experiment')
        description = data.get('description', '')
        control_config = data.get('control_config', {})
        experiment_config = data.get('experiment_config', {})
        capture_current = data.get('capture_current', True)

        framework = WOPRExperimentFramework()

        # Capture current situation if requested
        current_situation = None
        if capture_current:
            current_situation = framework.capture_current_situation()

        # Create experiment
        experiment_id = framework.create_experiment(
            name=name,
            description=description,
            control_config=control_config,
            experiment_config=experiment_config,
            current_situation=current_situation
        )

        return jsonify({
            "success": True,
            "experiment_id": experiment_id,
            "message": "Experiment created through WOPR workflow"
        }), 201

    except Exception as e:
        logger.error(f"Error creating WOPR experiment: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/wopr/experiments/<experiment_id>/run', methods=['POST'])
def wopr_run_experiment(experiment_id: str):
    """Run A/B experiment through WOPR pipeline"""
    try:
        from wopr_experiment_framework import WOPRExperimentFramework

        data = request.get_json() or {}
        duration = data.get('duration', 60.0)

        framework = WOPRExperimentFramework()

        # Run experiment through pipeline
        comparison = framework.run_experiment(experiment_id, duration=duration)

        return jsonify({
            "success": True,
            "experiment_id": experiment_id,
            "comparison": comparison.to_dict(),
            "message": "Experiment completed through WOPR pipeline"
        }), 200

    except Exception as e:
        logger.error(f"Error running WOPR experiment: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/wopr/experiments/<experiment_id>', methods=['GET'])
def wopr_get_experiment(experiment_id: str):
    """Get experiment details"""
    try:
        from wopr_experiment_framework import WOPRExperimentFramework

        framework = WOPRExperimentFramework()
        experiment = framework.get_experiment(experiment_id)

        return jsonify({
            "success": True,
            "experiment": experiment
        }), 200

    except Exception as e:
        logger.error(f"Error getting WOPR experiment: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/wopr/experiments', methods=['GET'])
def wopr_list_experiments():
    """List all WOPR experiments"""
    try:
        from wopr_experiment_framework import WOPRExperimentFramework

        framework = WOPRExperimentFramework()
        experiments = framework.list_experiments()

        return jsonify({
            "success": True,
            "experiments": experiments,
            "count": len(experiments)
        }), 200

    except Exception as e:
        logger.error(f"Error listing WOPR experiments: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/wopr/experiments/capture', methods=['POST', 'GET'])
def wopr_capture_situation():
    """Capture current situation as baseline"""
    try:
        from wopr_experiment_framework import WOPRExperimentFramework

        framework = WOPRExperimentFramework()
        situation = framework.capture_current_situation()

        return jsonify({
            "success": True,
            "situation": situation,
            "message": "Current situation captured"
        }), 200

    except Exception as e:
        logger.error(f"Error capturing situation: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Workflow Memory Persistence Endpoints
# ============================================================================

@app.route('/lumina/workflows/memory/store', methods=['POST'])
def store_workflow_memory():
    """Store workflow in persistent memory"""
    try:
        from workflow_memory_persistence import WorkflowMemoryPersistence, MemoryTier

        data = request.get_json() or {}
        workflow_data = data.get('workflow_data', {})
        workflow_type = data.get('workflow_type', 'general')
        memory_tier_str = data.get('memory_tier', 'short_term')
        importance = data.get('importance', 1.0)
        tags = data.get('tags', [])
        success = data.get('success', True)

        memory_tier = MemoryTier(memory_tier_str)

        persistence = WorkflowMemoryPersistence()
        workflow_id = persistence.store_workflow(
            workflow_data=workflow_data,
            workflow_type=workflow_type,
            memory_tier=memory_tier,
            importance=importance,
            tags=tags,
            success=success
        )

        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "memory_tier": memory_tier.value,
            "message": "Workflow stored in persistent memory"
        }), 201

    except Exception as e:
        logger.error(f"Error storing workflow memory: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/workflows/memory/<workflow_id>', methods=['GET'])
def get_workflow_memory(workflow_id: str):
    """Retrieve workflow from memory"""
    try:
        from workflow_memory_persistence import WorkflowMemoryPersistence

        persistence = WorkflowMemoryPersistence()
        workflow = persistence.retrieve_workflow(workflow_id)

        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404

        return jsonify({
            "success": True,
            "workflow": workflow.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving workflow memory: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/workflows/memory/search', methods=['GET'])
def search_workflow_memories():
    """Search workflows in memory"""
    try:
        from workflow_memory_persistence import WorkflowMemoryPersistence, MemoryTier

        query = request.args.get('query', '')
        workflow_type = request.args.get('workflow_type')
        memory_tier_str = request.args.get('memory_tier')
        limit = int(request.args.get('limit', 10))

        memory_tier = MemoryTier(memory_tier_str) if memory_tier_str else None

        persistence = WorkflowMemoryPersistence()
        workflows = persistence.search_workflows(
            query=query,
            workflow_type=workflow_type,
            memory_tier=memory_tier,
            limit=limit
        )

        return jsonify({
            "success": True,
            "workflows": [wf.to_dict() for wf in workflows],
            "count": len(workflows)
        }), 200

    except Exception as e:
        logger.error(f"Error searching workflow memories: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/workflows/memory/promote/<workflow_id>', methods=['POST'])
def promote_workflow_memory(workflow_id: str):
    """Promote workflow to long-term memory"""
    try:
        from workflow_memory_persistence import WorkflowMemoryPersistence

        persistence = WorkflowMemoryPersistence()
        success = persistence.promote_to_long_term(workflow_id)

        if not success:
            return jsonify({"error": "Workflow not found"}), 404

        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow promoted to long-term memory"
        }), 200

    except Exception as e:
        logger.error(f"Error promoting workflow memory: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/workflows/memory/blocks', methods=['GET'])
def get_workflow_building_blocks():
    """Get workflow building blocks"""
    try:
        from workflow_memory_persistence import WorkflowMemoryPersistence, BuildingBlockType

        block_type_str = request.args.get('block_type')
        workflow_type = request.args.get('workflow_type')

        block_type = BuildingBlockType(block_type_str) if block_type_str else None

        persistence = WorkflowMemoryPersistence()
        blocks = persistence.get_building_blocks(
            block_type=block_type,
            workflow_type=workflow_type
        )

        return jsonify({
            "success": True,
            "blocks": [block.to_dict() for block in blocks],
            "count": len(blocks)
        }), 200

    except Exception as e:
        logger.error(f"Error getting building blocks: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/lumina/workflows/memory/stats', methods=['GET'])
def get_workflow_memory_stats():
    """Get workflow memory statistics"""
    try:
        from workflow_memory_persistence import WorkflowMemoryPersistence

        persistence = WorkflowMemoryPersistence()
        stats = persistence.get_workflow_statistics()

        return jsonify({
            "success": True,
            "statistics": stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting workflow memory stats: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import sys

    # Get project root from command line or use default
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path(__file__).parent.parent.parent

    # Initialize R5 system
    r5_system = R5LivingContextMatrix(project_root)

    # Start API server
    port = 8000
    host = '0.0.0.0'

    logger.info(f"Starting Lumina API server (Unified) on {host}:{port}")
    logger.info(f"Project root: {project_root}")
    logger.info("R5 Endpoints:")
    logger.info("  GET  /r5/health - Health check")
    logger.info("  POST /r5/session - Ingest session")
    logger.info("  GET  /r5/aggregate - Aggregate sessions")
    logger.info("  GET  /r5/data - Get aggregated data")
    logger.info("  POST /r5/peak/extract - Extract @PEAK patterns")
    logger.info("  GET  /r5/jupyter/export - Export for Jupyter")
    logger.info("  GET  /r5/stats - Get statistics")
    logger.info("  GET  /r5/config - Get configuration")
    logger.info("Lumina Log Endpoints:")
    logger.info("  GET  /lumina/health - Health check")
    logger.info("  POST /lumina/logs/parse - Parse all logs")
    logger.info("  GET  /lumina/logs/startup - Get startup logs")
    logger.info("  GET  /lumina/logs/patterns - Get all patterns")
    logger.info("  GET  /lumina/logs/patterns/<id> - Get pattern")
    logger.info("  GET  /lumina/logs/aggregate - Aggregate logs")
    logger.info("  GET  /lumina/logs/insights - Get debugging insights")
    logger.info("  POST /lumina/logs/jarvis/execute - Jarvis-directed execution")
    logger.info("  POST /lumina/logs/syphon/simulate - SYPHON simulation with Matrix")
    logger.info("  GET  /lumina/logs/outputs - Get output locations")
    logger.info("WOPR Experiment Endpoints:")
    logger.info("  POST /wopr/experiments/create - Create A/B experiment")
    logger.info("  POST /wopr/experiments/<id>/run - Run experiment through pipeline")
    logger.info("  GET  /wopr/experiments/<id> - Get experiment details")
    logger.info("  GET  /wopr/experiments - List all experiments")
    logger.info("  POST /wopr/experiments/capture - Capture current situation")
    logger.info("Workflow Memory Endpoints:")
    logger.info("  POST /lumina/workflows/memory/store - Store workflow in memory")
    logger.info("  GET  /lumina/workflows/memory/<id> - Get workflow from memory")
    logger.info("  GET  /lumina/workflows/memory/search - Search workflows")
    logger.info("  POST /lumina/workflows/memory/promote/<id> - Promote to long-term")
    logger.info("  GET  /lumina/workflows/memory/blocks - Get building blocks")
    logger.info("  GET  /lumina/workflows/memory/stats - Get statistics")

    app.run(host=host, port=port, debug=False)

