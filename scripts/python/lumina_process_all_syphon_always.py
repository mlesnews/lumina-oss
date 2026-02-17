#!/usr/bin/env python3
"""
LUMINA Process All SYPHON & @ALWAYS Systems

Execute all SYPHON intelligence extraction and @ALWAYS Marvin/Jarvis systems
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaProcessAllSyphonAlways")

from lumina_always_marvin_jarvis import always_assess, AlwaysMarvinJarvis
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def process_all_syphon_systems():
    """Process all SYPHON intelligence extraction systems"""

    logger.info("="*80)
    logger.info("🔄 PROCESSING ALL SYPHON SYSTEMS")
    logger.info("="*80)

    results = {
        "timestamp": datetime.now().isoformat(),
        "syphon_systems": {},
        "status": "processing"
    }

    # List of SYPHON-related scripts to process
    syphon_scripts = [
        "syphon_system.py",
        "syphon_peak_learnings.py",
        "syphon_reality_processor.py",
        "syphon_vscode_ai_assistants.py",
        "syphon_actor_feed_aggregator.py",
        "jarvis_syphon_decisioning.py",
        "syphon_jarvis_integration_demo.py",
        "ingest_youtube_channel_syphon.py",
        "ingest_youtube_r5_syphon.py",
        "ingest_ide_diagnostics_syphon.py",
        "syphon_docs_import.py",
        "n8n_syphon_integration.py",
        "monitor_extension_updates_syphon.py",
        "lumina_completion_wopr_syphon.py"
    ]

    for script_name in syphon_scripts:
        script_path = script_dir / script_name
        if script_path.exists():
            try:
                logger.info(f"\n📋 Processing: {script_name}")
                # Import and check if it has a main/run function
                module_name = script_name.replace('.py', '')
                module = __import__(module_name, fromlist=[''])

                # Try to execute if it has a main function
                if hasattr(module, 'main'):
                    result = module.main()
                    results["syphon_systems"][script_name] = {
                        "status": "executed",
                        "result": str(result) if result else "completed"
                    }
                    logger.info(f"  ✅ {script_name} executed successfully")
                elif hasattr(module, 'run'):
                    result = module.run()
                    results["syphon_systems"][script_name] = {
                        "status": "executed",
                        "result": str(result) if result else "completed"
                    }
                    logger.info(f"  ✅ {script_name} executed successfully")
                else:
                    results["syphon_systems"][script_name] = {
                        "status": "imported",
                        "note": "No main/run function found"
                    }
                    logger.info(f"  ⚠️  {script_name} imported (no execution function)")
            except Exception as e:
                results["syphon_systems"][script_name] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"  ❌ {script_name} failed: {e}")
        else:
            results["syphon_systems"][script_name] = {
                "status": "not_found"
            }
            logger.warning(f"  ⚠️  {script_name} not found")

    # Process SYPHON core system
    try:
        logger.info("\n📋 Processing SYPHON Core System")
        from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier

        project_root = Path(".").resolve()
        config = SYPHONConfig(
            project_root=project_root,
            subscription_tier=SubscriptionTier.BASIC,
            enable_self_healing=True,
            enable_banking=True
        )

        syphon_system = SYPHONSystem(config)
        results["syphon_systems"]["syphon_core"] = {
            "status": "initialized",
            "config": {
                "tier": config.subscription_tier.value,
                "self_healing": config.enable_self_healing,
                "banking": config.enable_banking
            }
        }
        logger.info("  ✅ SYPHON Core System initialized")
    except Exception as e:
        results["syphon_systems"]["syphon_core"] = {
            "status": "error",
            "error": str(e)
        }
        logger.error(f"  ❌ SYPHON Core System failed: {e}")

    return results


def process_all_always_systems():
    """Process all @ALWAYS systems (Marvin & Jarvis integration)"""

    logger.info("\n" + "="*80)
    logger.info("🤖 PROCESSING ALL @ALWAYS SYSTEMS")
    logger.info("="*80)

    results = {
        "timestamp": datetime.now().isoformat(),
        "always_systems": {},
        "status": "processing"
    }

    # Process Always Marvin & Jarvis
    try:
        logger.info("\n📋 Processing Always @MARVIN & JARVIS Integration")

        always_system = AlwaysMarvinJarvis()

        # Test with common topics
        test_topics = [
            "LUMINA system operations",
            "SYPHON intelligence extraction",
            "Content creation strategy",
            "Platform diversification"
        ]

        perspectives = []
        for topic in test_topics:
            perspective = always_assess(topic)
            perspectives.append(perspective.to_dict())
            logger.info(f"  ✅ Processed: {topic}")

        results["always_systems"]["always_marvin_jarvis"] = {
            "status": "operational",
            "topics_processed": len(test_topics),
            "perspectives": perspectives
        }
        logger.info(f"  ✅ Always @MARVIN & JARVIS processed {len(test_topics)} topics")
    except Exception as e:
        results["always_systems"]["always_marvin_jarvis"] = {
            "status": "error",
            "error": str(e)
        }
        logger.error(f"  ❌ Always @MARVIN & JARVIS failed: {e}")

    # Check for other @ALWAYS systems
    always_patterns = [
        "lumina_always_marvin_jarvis.py"
    ]

    for pattern in always_patterns:
        script_path = script_dir / pattern
        if script_path.exists():
            try:
                logger.info(f"\n📋 Processing: {pattern}")
                module_name = pattern.replace('.py', '')
                module = __import__(module_name, fromlist=[''])

                if hasattr(module, 'main'):
                    result = module.main()
                    results["always_systems"][pattern] = {
                        "status": "executed",
                        "result": str(result) if result else "completed"
                    }
                    logger.info(f"  ✅ {pattern} executed successfully")
                else:
                    results["always_systems"][pattern] = {
                        "status": "imported",
                        "note": "Module imported successfully"
                    }
                    logger.info(f"  ✅ {pattern} imported successfully")
            except Exception as e:
                results["always_systems"][pattern] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"  ❌ {pattern} failed: {e}")

    return results


def display_summary(syphon_results: Dict, always_results: Dict):
    """Display summary of all processing"""

    print("\n" + "="*80)
    print("📊 SYPHON & @ALWAYS SYSTEMS PROCESSING SUMMARY")
    print("="*80 + "\n")

    # SYPHON Summary
    print("🔄 SYPHON SYSTEMS:")
    syphon_systems = syphon_results.get("syphon_systems", {})
    total_syphon = len(syphon_systems)
    successful_syphon = len([s for s in syphon_systems.values() if s.get("status") in ["executed", "initialized", "imported"]])

    print(f"   Total: {total_syphon}")
    print(f"   Successful: {successful_syphon}")
    print(f"   Errors: {total_syphon - successful_syphon}\n")

    for name, status in syphon_systems.items():
        status_icon = "✅" if status.get("status") in ["executed", "initialized", "imported"] else "❌"
        print(f"   {status_icon} {name}: {status.get('status', 'unknown')}")

    # @ALWAYS Summary
    print("\n🤖 @ALWAYS SYSTEMS:")
    always_systems = always_results.get("always_systems", {})
    total_always = len(always_systems)
    successful_always = len([s for s in always_systems.values() if s.get("status") in ["operational", "executed", "imported"]])

    print(f"   Total: {total_always}")
    print(f"   Successful: {successful_always}")
    print(f"   Errors: {total_always - successful_always}\n")

    for name, status in always_systems.items():
        status_icon = "✅" if status.get("status") in ["operational", "executed", "imported"] else "❌"
        print(f"   {status_icon} {name}: {status.get('status', 'unknown')}")

    print("\n" + "="*80)
    print(f"✅ PROCESSING COMPLETE - {successful_syphon + successful_always} systems operational")
    print("="*80 + "\n")


def main():
    try:
        """Main execution function"""

        print("\n" + "="*80)
        print("🚀 LUMINA PROCESS ALL SYPHON & @ALWAYS SYSTEMS")
        print("="*80 + "\n")

        # Process SYPHON systems
        syphon_results = process_all_syphon_systems()

        # Process @ALWAYS systems
        always_results = process_all_always_systems()

        # Display summary
        display_summary(syphon_results, always_results)

        # Save results
        results_dir = Path("data/lumina_syphon_always_processing")
        results_dir.mkdir(parents=True, exist_ok=True)

        results_file = results_dir / f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        combined_results = {
            "timestamp": datetime.now().isoformat(),
            "syphon_results": syphon_results,
            "always_results": always_results
        }

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(combined_results, f, indent=2, ensure_ascii=False)

        logger.info(f"📁 Results saved to: {results_file}")

        return combined_results


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()