#!/usr/bin/env python3
"""
Bitcoin Financial Services Platform - Production API

REST API for Bitcoin Financial Services Platform
Production-ready, marketable product

"MAKE IT SO NUMBER ONE"
"""

import sys
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any, Optional
import json

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from bitcoin_financial_workflows import (
        BitcoinWorkflowSystem,
        ClientProfile,
        RiskTolerance,
        AllocationModel
    )
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logging.error(f"Import error: {e}")

app = Flask(__name__)
CORS(app)
logger = get_logger("BitcoinPlatformAPI")

# Initialize workflow system
workflow_system = BitcoinWorkflowSystem()


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "operational",
        "service": "Bitcoin Financial Services Platform",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/assess-suitability', methods=['POST'])
def assess_suitability():
    """Assess client suitability for Bitcoin allocation"""
    try:
        data = request.json

        # Create client profile
        profile = ClientProfile(
            client_id=data.get('client_id', f"client_{datetime.now().timestamp()}"),
            risk_tolerance=RiskTolerance(data.get('risk_tolerance', 'moderate')),
            investment_horizon_years=data.get('investment_horizon_years', 10),
            bitcoin_knowledge_level=data.get('bitcoin_knowledge_level', 3),
            financial_sophistication=data.get('financial_sophistication', 'accredited'),
            current_portfolio_value=data.get('current_portfolio_value'),
            max_drawdown_tolerance=data.get('max_drawdown_tolerance')
        )

        # Assess suitability
        suitability = workflow_system.assess_client_suitability(profile)

        return jsonify({
            "success": True,
            "suitability": suitability.to_dict(),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Suitability assessment error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/v1/calculate-allocation', methods=['POST'])
def calculate_allocation():
    """Calculate Bitcoin allocation for client"""
    try:
        data = request.json

        # Create client profile
        profile = ClientProfile(
            client_id=data.get('client_id'),
            risk_tolerance=RiskTolerance(data.get('risk_tolerance', 'moderate')),
            investment_horizon_years=data.get('investment_horizon_years', 10),
            bitcoin_knowledge_level=data.get('bitcoin_knowledge_level', 3),
            financial_sophistication=data.get('financial_sophistication', 'accredited'),
            current_portfolio_value=data.get('current_portfolio_value'),
            max_drawdown_tolerance=data.get('max_drawdown_tolerance')
        )

        # Calculate allocation
        allocation = workflow_system.calculate_allocation(
            profile,
            portfolio_value=data.get('portfolio_value', 1000000.0)
        )

        return jsonify({
            "success": True,
            "allocation": allocation.to_dict(),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Allocation calculation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/v1/monitor-risk', methods=['POST'])
def monitor_risk():
    """Monitor Bitcoin position risk"""
    try:
        data = request.json

        risk_metrics = workflow_system.monitor_risk(
            client_id=data.get('client_id'),
            bitcoin_position_value=data.get('bitcoin_position_value', 0),
            portfolio_value=data.get('portfolio_value', 1000000.0),
            allocation_percentage=data.get('allocation_percentage', 2.5)
        )

        return jsonify({
            "success": True,
            "risk_metrics": risk_metrics.to_dict(),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Risk monitoring error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/v1/generate-report', methods=['POST'])
def generate_report():
    """Generate client report"""
    try:
        data = request.json

        report = workflow_system.generate_client_report(
            client_id=data.get('client_id'),
            allocation=data.get('allocation'),
            risk_metrics=data.get('risk_metrics')
        )

        return jsonify({
            "success": True,
            "report": report,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Report generation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/v1/onboard-client', methods=['POST'])
def onboard_client():
    """Complete client onboarding workflow"""
    try:
        data = request.json

        # Create client profile
        profile = ClientProfile(
            client_id=data.get('client_id', f"client_{datetime.now().timestamp()}"),
            risk_tolerance=RiskTolerance(data.get('risk_tolerance', 'moderate')),
            investment_horizon_years=data.get('investment_horizon_years', 10),
            bitcoin_knowledge_level=data.get('bitcoin_knowledge_level', 3),
            financial_sophistication=data.get('financial_sophistication', 'accredited'),
            current_portfolio_value=data.get('current_portfolio_value'),
            max_drawdown_tolerance=data.get('max_drawdown_tolerance')
        )

        # Execute onboarding
        success, results = workflow_system.execute_onboarding_workflow(
            profile,
            portfolio_value=data.get('portfolio_value', 1000000.0)
        )

        return jsonify({
            "success": success,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Onboarding error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


if __name__ == '__main__':
    logger.info("🚀 Bitcoin Financial Services Platform API starting...")
    logger.info("   Production-ready, marketable product")
    logger.info("   'MAKE IT SO NUMBER ONE'")

    # Run on port 5000 (production would use proper WSGI server)
    app.run(host='0.0.0.0', port=5000, debug=False)

