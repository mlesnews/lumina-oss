#!/usr/bin/env python3
"""
Complete Flow: @syphon => @pipe => @peak <=> @reality

Demonstrates the complete flow from search to inference.

Tags: #SYPHON #PIPE #PEAK #REALITY #FLOW @JARVIS @LUMINA
"""

from typing import Dict, Any
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add scripts/python to path
scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("Flow")


def complete_flow(
    pattern: str,
    path: str = "scripts/python/lumina"
) -> Dict[str, Any]:
    """
    Complete flow: @syphon => @pipe => @peak <=> @reality

    Args:
        pattern: Pattern to search for
        path: Path to search

    Returns:
        Complete flow results
    """
    logger.info("🔄 Starting complete flow: @syphon => @pipe => @peak <=> @reality")

    # Step 1: @syphon - Search
    logger.info("Step 1: @syphon - Searching...")
    try:
        from .syphon import Syphon
    except ImportError:
        from lumina.syphon import Syphon
    syphon = Syphon()
    syphon_results = syphon.search(pattern, path)

    if 'error' in syphon_results:
        return {
            'error': syphon_results['error'],
            'flow_complete': False
        }

    # Step 2: @pipe - Process
    logger.info("Step 2: @pipe - Processing...")
    try:
        from .pipe import Pipe
    except ImportError:
        from lumina.pipe import Pipe
    pipe = Pipe()
    processed = pipe.process(syphon_results)

    if not processed.get('processed', False):
        return {
            'error': 'Processing failed',
            'flow_complete': False
        }

    # Step 3: @peak - Gateway
    logger.info("Step 3: @peak - Gateway to systems...")
    try:
        try:
            from .peak import LuminaPeak
        except ImportError:
            from lumina.peak import LuminaPeak
        lumina = LuminaPeak()

        # Access Library (Jedi Archives)
        if lumina.digest:
            library = lumina.digest
            knowledge = library.knowledge(pattern)
            logger.info(f"✅ Accessed Library (Jedi Archives) for '{pattern}'")
        else:
            knowledge = {'error': 'Library not available'}

        # Step 4: @reality - Inference
        logger.info("Step 4: @reality - Applying inference...")

        # Simple Reality
        simple_result = None
        if lumina.simple:
            simple_result = lumina.simple.balance()
            logger.info("✅ Simple Reality inference applied")

        # Hybrid Reality
        hybrid_result = None
        if lumina.reality:
            # Use processed data for inference
            query = f"Analyze pattern '{pattern}' with {processed['data']['total_matches']} matches"
            hybrid_result = lumina.reality.infer(query, maintain_balance=True)
            logger.info("✅ Hybrid Reality inference applied")

        # Bidirectional: Reality updates Peak
        logger.info("Bidirectional: Reality → Peak (state update)")

        return {
            'flow_complete': True,
            'steps': {
                'syphon': {
                    'pattern': pattern,
                    'matches': syphon_results['match_count'],
                    'status': 'complete'
                },
                'pipe': {
                    'processed': True,
                    'categories': processed['data']['categories'],
                    'summary': processed['data']['summary'],
                    'status': 'complete'
                },
                'peak': {
                    'initialized': lumina.initialized,
                    'library_accessed': knowledge.get('error') is None,
                    'status': 'complete'
                },
                'reality': {
                    'simple': simple_result is not None,
                    'hybrid': hybrid_result is not None,
                    'status': 'complete'
                }
            },
            'results': {
                'knowledge': knowledge,
                'simple_reality': simple_result,
                'hybrid_reality': hybrid_result
            }
        }

    except Exception as e:
        logger.error(f"Error in Peak/Reality: {e}")
        return {
            'error': str(e),
            'flow_complete': False,
            'steps': {
                'syphon': {'status': 'complete'},
                'pipe': {'status': 'complete'},
                'peak': {'status': 'error'},
                'reality': {'status': 'error'}
            }
        }


def main():
    """Example usage - Complete flow"""
    print("=" * 80)
    print("🔄 COMPLETE FLOW: @syphon => @pipe => @peak <=> @reality")
    print("=" * 80)
    print()

    # Execute complete flow
    result = complete_flow("balance", "scripts/python/lumina")

    if result.get('flow_complete'):
        print("✅ FLOW COMPLETE")
        print("-" * 80)

        steps = result['steps']
        print("STEPS:")
        print(f"  1. @syphon: {steps['syphon']['status']} ({steps['syphon']['matches']} matches)")
        print(f"  2. @pipe: {steps['pipe']['status']} ({len(steps['pipe']['categories'])} categories)")
        print(f"  3. @peak: {steps['peak']['status']} (Library: {'✅' if steps['peak']['library_accessed'] else '❌'})")
        print(f"  4. @reality: {steps['reality']['status']} (Simple: {'✅' if steps['reality']['simple'] else '❌'}, Hybrid: {'✅' if steps['reality']['hybrid'] else '❌'})")
        print()

        if 'results' in result:
            results = result['results']
            print("RESULTS:")
            print("-" * 80)
            if 'knowledge' in results and 'error' not in results['knowledge']:
                print(f"  Library: {results['knowledge'].get('topic', 'N/A')}")
            if results.get('simple_reality'):
                print("  Simple Reality: ✅ Applied")
            if results.get('hybrid_reality'):
                print("  Hybrid Reality: ✅ Applied")
    else:
        print("❌ FLOW INCOMPLETE")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print()
    print("=" * 80)
    print("🔄 Flow: @syphon => @pipe => @peak <=> @reality")
    print("=" * 80)


if __name__ == "__main__":


    main()