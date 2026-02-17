#!/usr/bin/env python3
"""
Standalone MCP Triage Server
Minimal server for triage endpoint only - no R5 dependencies
Runs on port 8000 for @DOIT @TRIAGE integration
"""

import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional

app = Flask(__name__)
CORS(app)

# Simple triage logic (can be enhanced with AI later)
def triage_issue(text: str, severity: Optional[str] = None) -> Dict[str, Any]:
    """
    Simple triage classification
    Returns: {category, priority, notes}
    """
    text_lower = text.lower()

    # Immediate: Critical errors, system down, security issues
    if any(word in text_lower for word in ['critical', 'down', 'security', 'breach', 'data loss', 'corrupt']):
        return {
            "category": "critical",
            "priority": "Immediate",
            "notes": "Critical issue requiring immediate attention"
        }

    # Urgent: High priority features, blocking issues
    if any(word in text_lower for word in ['urgent', 'blocking', 'broken', 'failing', 'error', 'bug']):
        return {
            "category": "urgent",
            "priority": "Urgent",
            "notes": "Urgent issue requiring prompt resolution"
        }

    # Elevated: Normal priority work
    if any(word in text_lower for word in ['implement', 'add', 'create', 'build', 'develop']):
        return {
            "category": "development",
            "priority": "Elevated",
            "notes": "Standard development task"
        }

    # Routine: Low priority, maintenance
    return {
        "category": "general",
        "priority": "Routine",
        "notes": "Routine task"
    }

@app.route('/triage', methods=['POST'])
def triage_endpoint():
    """Triage endpoint for @DOIT @TRIAGE"""
    try:
        data = request.json
        text = data.get('text', '')
        severity = data.get('severity')

        result = triage_issue(text, severity)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "MCP Triage Server"}), 200

@app.route('/r5/health', methods=['GET'])
def r5_health():
    """R5-compatible health check"""
    return jsonify({"status": "healthy", "service": "MCP Triage Server"}), 200

if __name__ == '__main__':
    print("="*60)
    print("MCP Triage Server (Standalone)")
    print("="*60)
    print("Starting on 0.0.0.0:8000")
    print("Endpoints:")
    print("  POST /triage - Triage issue")
    print("  GET  /health - Health check")
    print("="*60)
    app.run(host='0.0.0.0', port=8000, debug=False)
