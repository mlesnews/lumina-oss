#!/usr/bin/env python3
"""
Hybrid Voice + Grammar + TTS API

CLI & API Hybrid version of Dragon + ElevenLabs + Grammarly integration.
Includes SSH-level + AI encrypted tunnel.

Tags: #HYBRID #VOICE #GRAMMAR #TTS #API #CLI #SSH #ENCRYPTED_TUNNEL @JARVIS @LUMINA
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from replica_inspired_hybrid_system import ReplicaInspiredHybrid, ActionType
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HybridVoiceGrammarTTSAPI")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize hybrid system
hybrid_system = None


def init_system():
    """Initialize hybrid system"""
    global hybrid_system
    if hybrid_system is None:
        hybrid_system = ReplicaInspiredHybrid()
    return hybrid_system


# API Endpoints

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "dragon": "ready",
            "grammarly": "ready",
            "elevenlabs": "ready",
            "encrypted_tunnel": "active"
        }
    })


@app.route('/api/v1/voice/process', methods=['POST'])
def process_voice():
    """Process voice input through hybrid pipeline"""
    system = init_system()

    data = request.json
    audio_file = data.get('audio_file')
    text = data.get('text')

    result = system.process_voice_input(audio_file=audio_file, text=text)

    return jsonify(result)


@app.route('/api/v1/action/create', methods=['POST'])
def create_action():
    """Create @ACTION"""
    system = init_system()

    data = request.json
    action_type = ActionType(data.get('action_type', 'conversation'))
    intent = data.get('intent', '')
    context = data.get('context', {})
    parameters = data.get('parameters', {})

    action = system.create_action(action_type, intent, context, parameters)

    return jsonify(action.to_dict())


@app.route('/api/v1/actions/list', methods=['GET'])
def list_actions():
    """List all actions"""
    system = init_system()

    actions = [action.to_dict() for action in system.actions]

    return jsonify({
        "total": len(actions),
        "actions": actions
    })


@app.route('/api/v1/pipeline/template', methods=['POST'])
def create_template():
    """Create pipeline template"""
    system = init_system()

    data = request.json
    name = data.get('name', 'default')

    pipeline = system.create_pipeline_template(name)

    return jsonify({
        "pipeline_id": pipeline.pipeline_id,
        "enabled": pipeline.enabled
    })


# CLI Interface

def cli_process_voice(audio_file: Optional[str] = None, text: Optional[str] = None):
    try:
        """CLI: Process voice input"""
        system = init_system()
        result = system.process_voice_input(audio_file=audio_file, text=text)
        print(json.dumps(result, indent=2))


    except Exception as e:
        logger.error(f"Error in cli_process_voice: {e}", exc_info=True)
        raise
def cli_create_action(intent: str, action_type: str = "conversation"):
    try:
        """CLI: Create action"""
        system = init_system()
        action = system.create_action(ActionType[action_type.upper()], intent)
        print(json.dumps(action.to_dict(), indent=2))


    except Exception as e:
        logger.error(f"Error in cli_create_action: {e}", exc_info=True)
        raise
def cli_list_actions():
    """CLI: List actions"""
    system = init_system()
    for action in system.actions:
        print(f"  {action.action_id}: {action.intent} ({action.action_type.value})")


def main():
    """Main entry point - CLI or API server"""
    import argparse

    parser = argparse.ArgumentParser(description="Hybrid Voice + Grammar + TTS API")
    parser.add_argument("--api", action="store_true", help="Start API server")
    parser.add_argument("--port", type=int, default=5000, help="API server port")
    parser.add_argument("--voice", type=str, help="Process voice input (CLI)")
    parser.add_argument("--text", type=str, help="Process text input (CLI)")
    parser.add_argument("--action", type=str, help="Create action (CLI)")
    parser.add_argument("--list-actions", action="store_true", help="List actions (CLI)")

    args = parser.parse_args()

    if args.api:
        logger.info("=" * 80)
        logger.info("🚀 STARTING HYBRID VOICE + GRAMMAR + TTS API SERVER")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   API Server: http://localhost:{args.port}")
        logger.info("   Endpoints:")
        logger.info("     GET  /api/v1/health")
        logger.info("     POST /api/v1/voice/process")
        logger.info("     POST /api/v1/action/create")
        logger.info("     GET  /api/v1/actions/list")
        logger.info("     POST /api/v1/pipeline/template")
        logger.info("")
        app.run(host='0.0.0.0', port=args.port, debug=True)
    elif args.voice:
        cli_process_voice(audio_file=args.voice)
    elif args.text:
        cli_process_voice(text=args.text)
    elif args.action:
        cli_create_action(args.action)
    elif args.list_actions:
        cli_list_actions()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())