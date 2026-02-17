#!/usr/bin/env python3
"""
SYPHON Command
Extract intelligence from sources - works seamlessly with pipe command.

Usage:
    siphon <source_type>:<source> [options]
    siphon email:"query" | pipe <pipe_name>
    siphon filesystem:/path | pipe <pipe_name>

Designed for perfect synergy with pipe command.

#JARVIS #LUMINA #SYPHON #COMMAND #PIPE-SYNERGY
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.pipes.syphon_stage import SyphonStage
from scripts.python.pipes.core import PipeContext

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SiphonCommand")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SiphonCommand")


def siphon_command(
    source: str,
    output_format: str = "json",
    destination: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute siphon command.

    Args:
        source: Source to siphon from (format: "type:value" or just value)
        output_format: Output format (json, text, yaml)
        destination: Destination to write to (stdout, file:path, or file path)
        **kwargs: Additional source-specific options

    Returns:
        Siphoned data
    """
    logger.info("="*80)
    logger.info(f"SYPHON COMMAND: {source}")
    logger.info("="*80)

    # Parse source
    if ":" in source:
        source_type, source_value = source.split(":", 1)
    else:
        # Default to filesystem if no type specified
        source_type = "filesystem"
        source_value = source

    # Build source config
    source_config = {
        "project_root": str(project_root),
    }

    # Add source-specific config
    if source_type == "email":
        source_config["query"] = source_value
        source_config["days_back"] = kwargs.get("days", 30)
    elif source_type == "filesystem":
        source_config["path"] = source_value
        source_config["pattern"] = kwargs.get("pattern", "*")
        source_config["recursive"] = kwargs.get("recursive", True)
    elif source_type == "database":
        source_config["connection"] = source_value
    elif source_type == "api":
        source_config["url"] = source_value
    else:
        error_msg = f"Unknown source type: {source_type}"
        logger.error(f"❌ {error_msg}")
        logger.info("💡 Tip: Supported source types: email, filesystem, database, api")
        logger.info("💡 Tip: Pipe output to pipe command: 'siphon <source> | pipe <name>'")
        return {
            "success": False,
            "error": error_msg,
            "supported_types": ["email", "filesystem", "database", "api"],
            "synergy_tip": "Pipe output to pipe command: 'siphon <source> | pipe <name>'"
        }

    # Create syphon stage
    syphon_stage = SyphonStage(
        name="siphon_command",
        source_type=source_type,
        source_config=source_config
    )

    # Create context
    context = PipeContext(
        pipe_name="siphon_command",
        stage_name="siphon",
        data={}
    )

    # Execute siphon
    try:
        context = syphon_stage.process(context)
        siphoned_data = context.get_data("siphoned_data", {})

        result = {
            "success": True,
            "source_type": source_type,
            "source": source_value,
            "siphoned_data": siphoned_data,
            "metadata": context.metadata,
            "warnings": context.warnings,
            "errors": context.errors
        }

        item_count = len(siphoned_data.get("items", [])) if isinstance(siphoned_data, dict) else len(siphoned_data) if isinstance(siphoned_data, list) else 0
        logger.info(f"✅ Siphoned {item_count} item(s) from {source_type}")
        logger.info("💡 Tip: Pipe this output to a pipe command: 'siphon <source> | pipe <pipe_name>'")

    except Exception as e:
        error_msg = f"Siphon failed: {e}"
        logger.error(f"❌ {error_msg}")
        logger.info("💡 Tip: Check source configuration and connectivity")
        logger.info("💡 Tip: Once fixed, pipe to pipe command: 'siphon <source> | pipe <name>'")
        result = {
            "success": False,
            "error": error_msg,
            "source_type": source_type,
            "source": source_value,
            "synergy_tip": "Once fixed, pipe to pipe command: 'siphon <source> | pipe <name>'"
        }

    # Handle destination
    if destination:
        if destination == "stdout" or destination == "-":
            write_stdout(result, output_format)
        elif destination.startswith("file:"):
            file_path = Path(destination[5:])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Results written to: {file_path}")
        else:
            file_path = Path(destination)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Results written to: {file_path}")
    else:
        # Default: write to stdout (optimized for piping to pipe command - perfect synergy!)
        # Pipe command expects JSON with siphoned_data structure
        if output_format != "json":
            logger.info("💡 Switching to JSON format for optimal pipe command synergy")
            logger.info("   Pipe command automatically detects siphon output format")
        write_stdout(result, "json")  # Always JSON for pipe compatibility

    return result


def write_stdout(data: Dict[str, Any], format: str = "json"):
    """
    Write data to stdout (for Unix-style piping to pipe command).

    Args:
        data: Data to write
        format: Output format (json, text, yaml)
    """
    if format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    elif format == "text":
        if isinstance(data, dict):
            if "siphoned_data" in data:
                print(str(data["siphoned_data"]))
            elif "message" in data:
                print(data["message"])
            else:
                print(str(data))
        else:
            print(str(data))
    elif format == "yaml":
        try:
            import yaml
            print(yaml.dump(data, default_flow_style=False))
        except ImportError:
            logger.warning("YAML not available, falling back to JSON")
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SYPHON Command - Extract intelligence from sources (perfect synergy with pipe command)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Siphon emails
  siphon email:"hvac OR furnace"

  # Siphon filesystem
  siphon filesystem:/path/to/files

  # Unix-style piping to pipe command (perfect synergy!)
  siphon email:"hvac OR furnace" | pipe hvac_email

  # Siphon to file
  siphon email:"query" --destination file:results.json

  # Siphon with options
  siphon email:"query" --days 60 --destination stdout

  # Chain: siphon → pipe → another pipe
  siphon email:"query" | pipe hvac_email | pipe analyze

Note: SIPHON and PIPE are designed to work together seamlessly.
      SIPHON extracts, PIPE processes - perfect synergy!
        """
    )

    parser.add_argument(
        "source",
        help="Source to siphon from (format: type:value, e.g., email:\"query\", filesystem:/path)"
    )

    parser.add_argument(
        "--destination",
        help="Destination to write to (stdout, file:path, or file path). Default: stdout (optimized for piping to pipe command - perfect synergy!)"
    )

    parser.add_argument(
        "--format",
        choices=["json", "text", "yaml"],
        default="json",
        help="Output format (default: json, optimized for perfect synergy with pipe command). Pipe command automatically detects siphon output."
    )

    # Source-specific options
    parser.add_argument(
        "--days",
        type=int,
        help="Days to search back (for email source)"
    )

    parser.add_argument(
        "--pattern",
        help="File pattern (for filesystem source)"
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Recursive search (for filesystem source)"
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Project root directory"
    )

    args = parser.parse_args()

    global project_root
    project_root = args.project_root

    # Build kwargs
    kwargs = {}
    if args.days:
        kwargs["days"] = args.days
    if args.pattern:
        kwargs["pattern"] = args.pattern
    if args.recursive:
        kwargs["recursive"] = args.recursive

    # Execute siphon command
    result = siphon_command(
        source=args.source,
        output_format=args.format,
        destination=args.destination,
        **kwargs
    )

    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":


    main()