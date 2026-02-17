"""
Run HVAC Email Pipe
Execute the complete HVAC email processing pipe.

#JARVIS #LUMINA #PIPES #HVAC
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.pipes.hvac_email_pipe import create_hvac_email_pipe

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("RunHVACEmailPipe")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RunHVACEmailPipe")


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="Run HVAC Email Pipe")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--budget", type=float, default=20000, help="Budget for comparison")
        parser.add_argument("--query", type=str, help="Custom email search query")
        parser.add_argument("--days", type=int, default=90, help="Days to search back")

        args = parser.parse_args()

        print("\n" + "="*80)
        print("LUMINA PIPE SYSTEM - HVAC EMAIL PIPE")
        print("="*80)
        print("Architecture: Siphon → Pipe → Destination")
        print("Like running a city - lots of pipes for different purposes.")
        print()

        # Create pipe
        pipe = create_hvac_email_pipe(args.project_root, args.budget)

        # Customize query if provided
        if args.query:
            # Find syphon stage and update query
            for stage in pipe.stages:
                if hasattr(stage, 'source_config') and stage.source_type == "email":
                    stage.source_config["query"] = args.query
                    stage.source_config["days_back"] = args.days
                    logger.info(f"Updated search query: {args.query}")
                    break

        # Print pipe info
        pipe_info = pipe.get_pipe_info()
        print("Pipe Configuration:")
        print(f"  Name: {pipe_info['name']}")
        print(f"  Description: {pipe_info['description']}")
        print(f"  Stages: {pipe_info['stage_count']}")
        print()
        print("Stages:")
        for i, stage_info in enumerate(pipe_info['stages'], 1):
            print(f"  {i}. {stage_info['name']} ({stage_info['type']})")
        print()

        # Save pipe config
        config_file = pipe.save_pipe_config()
        print(f"📄 Pipe config saved to: {config_file}")
        print()

        # Execute pipe
        print("Executing pipe...")
        print()

        result = pipe.execute()

        # Print result summary
        print("\n" + "="*80)
        print("PIPE EXECUTION RESULT")
        print("="*80)
        print(f"Success: {'✅' if result.success else '❌'}")
        print(f"Stages executed: {len(result.stages_executed)}/{pipe_info['stage_count']}")
        print(f"Execution time: {result.execution_time_seconds:.2f}s")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  ❌ {error}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")

        # Print key results
        if result.success:
            final_data = result.final_data
            print("\nResults:")

            if "bid_count" in final_data:
                print(f"  📄 Bids extracted: {final_data['bid_count']}")

            if "analysis_count" in final_data:
                print(f"  🔍 Analyses completed: {final_data['analysis_count']}")

            if "bids_file" in final_data:
                print(f"  💾 Bids saved to: {final_data['bids_file']}")

            if "analyses_file" in final_data:
                print(f"  💾 Analyses saved to: {final_data['analyses_file']}")

            if "comparison_file" in final_data:
                print(f"  💾 Comparison saved to: {final_data['comparison_file']}")

        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()