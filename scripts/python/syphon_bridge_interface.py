#!/usr/bin/env python3
"""
SYPHON Bridge Interface - Python Side
Provides interface for Perl SYPHON components to communicate with Python systems

@V3_WORKFLOWED: True
@RULE_COMPLIANT: True
@TEST_FIRST: True
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import argparse

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from syphon_wopr_data_intake_framework import SyphonWoprDataIntakeFramework

class SyphonBridgeInterface:
    """Python interface for SYPHON bridge communication"""

    def __init__(self):
        self.framework = None
        self._initialized = False

    def initialize_framework(self):
        """Initialize the SYPHON framework if not already done"""
        if not self._initialized:
            try:
                self.framework = SyphonWoprDataIntakeFramework()
                self._initialized = True
                print("✅ SYPHON Python framework initialized", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to initialize SYPHON framework: {e}", file=sys.stderr)
                sys.exit(1)

    def process_intelligence(self, params):
        """Process intelligence through Python SYPHON framework"""
        self.initialize_framework()

        try:
            # Extract parameters
            intelligence_assets = params.get('intelligence_assets', [])
            simulation_params = params.get('simulation_params', {})

            # Process through WOPR simulation
            paths = self.framework.process_wopr_simulation(intelligence_assets, simulation_params)

            # Generate decisions
            decision_context = params.get('decision_context', {})
            decisions = self.framework.generate_peak_path_decisions(paths, decision_context)

            result = {
                'success': True,
                'paths_generated': len(paths),
                'decisions_made': len(decisions),
                'paths': [path.__dict__ if hasattr(path, '__dict__') else path for path in paths],
                'decisions': [decision.__dict__ if hasattr(decision, '__dict__') else decision for decision in decisions]
            }

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    def get_intelligence_report(self, params):
        """Generate intelligence report via Python framework"""
        self.initialize_framework()

        try:
            report = self.framework.generate_intelligence_report()
            return {
                'success': True,
                'report': report
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_asset_by_hash(self, params):
        """Get intelligence asset by hash (would need DB access)"""
        # This would require direct DB access or framework method
        return {
            'success': False,
            'error': 'Method not implemented in Python bridge',
            'note': 'Use Perl interface for asset queries'
        }

def main():
    parser = argparse.ArgumentParser(description='SYPHON Python Bridge Interface')
    parser.add_argument('method', help='Method to call')
    parser.add_argument('params', nargs='?', help='JSON parameters')

    args = parser.parse_args()

    # Parse parameters if provided
    params = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON parameters: {e}", file=sys.stderr)
            sys.exit(1)

    # Initialize bridge interface
    bridge = SyphonBridgeInterface()

    # Call the requested method
    if args.method == 'process_intelligence':
        result = bridge.process_intelligence(params)
    elif args.method == 'get_intelligence_report':
        result = bridge.get_intelligence_report(params)
    elif args.method == 'get_asset_by_hash':
        result = bridge.get_asset_by_hash(params)
    else:
        result = {
            'success': False,
            'error': f'Unknown method: {args.method}',
            'available_methods': ['process_intelligence', 'get_intelligence_report', 'get_asset_by_hash']
        }

    # Output result as JSON
    print(json.dumps(result, indent=2, default=str))

if __name__ == '__main__':
    main()
