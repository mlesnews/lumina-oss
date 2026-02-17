#!/usr/bin/env python3
"""
API Metrics Endpoint
Additional metrics endpoints for monitoring

Provides detailed metrics for observability.
"""

import sys
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# This module provides additional endpoint implementations
# that can be added to the API server

def get_metrics_endpoints():
    """Get additional metrics endpoints for API server"""

    endpoints = {
        "/api/v1/metrics/performance": {
            "method": "GET",
            "handler": "get_performance_metrics",
            "description": "Get performance metrics",
            "auth_required": True
        },
        "/api/v1/metrics/business": {
            "method": "GET",
            "handler": "get_business_metrics",
            "description": "Get business metrics",
            "auth_required": True
        },
        "/api/v1/metrics/health/detailed": {
            "method": "GET",
            "handler": "get_detailed_health",
            "description": "Get detailed health check",
            "auth_required": False
        }
    }

    return endpoints
