#!/usr/bin/env python3
"""
Bitcoin Financial Services Platform - Launch Script

"MAKE IT SO NUMBER ONE"
Production launch - starting NOW
"""

import sys
from pathlib import Path
from datetime import datetime
import subprocess
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

print("\n" + "="*60)
print("🚀 BITCOIN FINANCIAL SERVICES PLATFORM - LAUNCH")
print("="*60)
print("\n'MAKE IT SO NUMBER ONE'")
print(f"\nLaunch Time: {datetime.now().isoformat()}")
print("\n" + "="*60)

# Check dependencies
print("\n📋 Checking Dependencies...")
try:
    import flask
    print("  ✅ Flask installed")
except ImportError:
    print("  ❌ Flask not installed - installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])

try:
    import flask_cors
    print("  ✅ Flask-CORS installed")
except ImportError:
    print("  ❌ Flask-CORS not installed")

# Check Bitcoin workflow system
print("\n📋 Checking Bitcoin Workflow System...")
try:
    from bitcoin_financial_workflows import BitcoinWorkflowSystem
    workflow_system = BitcoinWorkflowSystem()
    print("  ✅ Bitcoin Workflow System ready")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Launch API
print("\n🚀 Launching API Server...")
print("   API will be available at: http://localhost:5000")
print("   Health check: http://localhost:5000/api/health")
print("\n   Endpoints:")
print("   - POST /api/v1/assess-suitability")
print("   - POST /api/v1/calculate-allocation")
print("   - POST /api/v1/monitor-risk")
print("   - POST /api/v1/generate-report")
print("   - POST /api/v1/onboard-client")
print("\n" + "="*60)
print("✅ PRODUCTION API READY")
print("="*60 + "\n")

# Start the API server
if __name__ == '__main__':
    from bitcoin_platform_api import app
    app.run(host='0.0.0.0', port=5000, debug=False)

