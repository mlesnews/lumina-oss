#!/usr/bin/env python3
"""
Bitcoin Financial Services Platform - Deployment Configuration

Production deployment setup
"""

import sys
from pathlib import Path
from datetime import datetime
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Deployment configuration
deployment_config = {
    "service_name": "bitcoin-financial-services-platform",
    "version": "1.0.0",
    "environment": "production",
    "api": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": False
    },
    "database": {
        "type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "name": "bitcoin_platform"
    },
    "payment": {
        "provider": "stripe",
        "test_mode": True
    },
    "deployment": {
        "platform": "aws",  # or azure, gcp
        "region": "us-east-1",
        "instance_type": "t3.medium"
    }
}

# Save configuration
config_file = project_root / "config" / "bitcoin_platform_deployment.json"
config_file.parent.mkdir(parents=True, exist_ok=True)

with open(config_file, 'w') as f:
    json.dump(deployment_config, f, indent=2)

print(f"✅ Deployment configuration saved to: {config_file}")

