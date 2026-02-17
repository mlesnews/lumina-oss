#!/usr/bin/env python3
"""
PIPE Command
Unix-style pipe command for ALL AI Chat workflows and ALL LUMINA workflows.

Usage:
    pipe <pipe_name> [source] [destination]
    siphon <source> | pipe <pipe_name> | <destination>

Like Unix pipes, but for ALL LUMINA workflows.

#JARVIS #LUMINA #PIPES #COMMAND #UNIX #ALL-WORKFLOWS
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.pipes.core import Pipe, PipeContext
from scripts.python.pipes.syphon_stage import SyphonStage
from scripts.python.pipes.hvac_email_pipe import HVACEmailPipe, create_hvac_email_pipe

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("PipeCommand")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("PipeCommand")


def discover_pipes(project_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Discover all available pipes in LUMINA.

    Args:
        project_root: Project root directory

    Returns:
        Dictionary of pipe_name -> pipe_info
    """
    pipes = {}

    # Built-in pipes
    pipes["hvac_email"] = {
        "name": "hvac_email",
        "aliases": ["hvac"],
        "description": "HVAC bid email processing pipe",
        "type": "builtin"
    }

    # Discover pipes from config files
    pipes_dir = project_root / "data" / "pipes"
    if pipes_dir.exists():
        for pipe_dir in pipes_dir.iterdir():
            if pipe_dir.is_dir():
                config_file = pipe_dir / "pipe_config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        pipes[config["name"]] = {
                            "name": config["name"],
                            "description": config.get("description", ""),
                            "type": "configured",
                            "stages": config.get("stages", [])
                        }
                    except Exception as e:
                        logger.debug(f"Failed to load pipe config {config_file}: {e}")

    return pipes


def load_pipe(pipe_name: str, project_root: Path) -> Optional[Pipe]:
    try:
        """
        Load a pipe by name.

        Supports ALL LUMINA workflows - not just HVAC.

        Args:
            pipe_name: Name of pipe to load
            project_root: Project root directory

        Returns:
            Pipe instance or None
        """
        # Built-in pipes
        if pipe_name == "hvac_email" or pipe_name == "hvac":
            return create_hvac_email_pipe(project_root)

        # Try to load from config
        pipe_config_file = project_root / "data" / "pipes" / pipe_name / "pipe_config.json"
        if pipe_config_file.exists():
            with open(pipe_config_file, 'r') as f:
                config = json.load(f)

            # Reconstruct pipe from config
            pipe = Pipe(
                name=config["name"],
                project_root=project_root,
                description=config.get("description", "")
            )

            # Load stages from config
            # This would need to be implemented based on stage types
            logger.warning(f"Loading pipe from config not fully implemented for: {pipe_name}")
            return pipe

        return None


    except Exception as e:
        logger.error(f"Error in load_pipe: {e}", exc_info=True)
        raise
def read_stdin() -> Optional[Dict[str, Any]]:
    """
    Read data from stdin (for Unix-style piping from siphon command).

    Designed for perfect synergy with siphon command output.

    Returns:
        Parsed data or None
    """
    import sys

    if sys.stdin.isatty():
        return None

    try:
        data = sys.stdin.read()
        if not data:
            return None

        # Try to parse as JSON (siphon outputs JSON by default)
        try:
            parsed = json.loads(data)

            # If this is siphon output, extract siphoned_data for pipe processing
            if isinstance(parsed, dict) and "siphoned_data" in parsed:
                # Perfect synergy detected - siphon output
                logger.info("✅ Perfect synergy detected: Received data from siphon command")
                logger.debug(f"   Source type: {parsed.get('source_type', 'unknown')}")
                logger.debug(f"   Items siphoned: {len(parsed.get('siphoned_data', {}).get('items', [])) if isinstance(parsed.get('siphoned_data'), dict) else 'N/A'}")

                # Return siphoned data in format pipe expects
                return {
                    "siphoned_data": parsed["siphoned_data"],
                    "source_type": parsed.get("source_type"),
                    "metadata": parsed.get("metadata", {}),
                    "_from_siphon": True  # Flag for tracking synergy
                }

            return parsed

        except json.JSONDecodeError:
            # If not JSON, treat as text
            logger.debug("Received non-JSON input, treating as text")
            return {"text": data, "format": "text"}

    except Exception as e:
        logger.error(f"Failed to read stdin: {e}")
        return None


def write_stdout(data: Dict[str, Any], format: str = "json"):
    """
    Write data to stdout (for Unix-style piping).

    Args:
        data: Data to write
        format: Output format (json, text, yaml)
    """
    if format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    elif format == "text":
        if isinstance(data, dict):
            # Try to extract meaningful text
            if "final_data" in data:
                print(str(data["final_data"]))
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


def pipe_command(
    pipe_name: str,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    input_data: Optional[Dict[str, Any]] = None,
    output_format: str = "json",
    **kwargs
) -> Dict[str, Any]:
    """
    Execute pipe command.

    Args:
        pipe_name: Name of pipe to execute
        source: Source to siphon from (if not provided via stdin)
        destination: Destination to pipe to (if not stdout)
        input_data: Input data (from stdin or source)
        output_format: Output format (json, text, yaml)
        **kwargs: Additional pipe-specific arguments

    Returns:
        Pipe result
    """
    logger.info("="*80)
    logger.info(f"PIPE COMMAND: {pipe_name}")
    logger.info("="*80)

    # Load pipe
    pipe = load_pipe(pipe_name, project_root)

    if not pipe:
        # Discover all available pipes for better error message
        available_pipes = discover_pipes(project_root)
        pipe_names = list(available_pipes.keys())

        error_msg = f"Pipe '{pipe_name}' not found"
        logger.error(f"❌ {error_msg}")
        logger.info("💡 Tip: Use 'pipe --list' to see all available pipes")
        logger.info("💡 Tip: Use 'siphon <source> | pipe <name>' for perfect synergy!")
        return {
            "success": False,
            "error": error_msg,
            "available_pipes": pipe_names,
            "suggestion": f"Use 'pipe --list' to see all available pipes",
            "synergy_tip": "Use 'siphon <source> | pipe <name>' for perfect synergy"
        }

    # Get input data
    if input_data is None:
        # Try stdin first (Unix-style piping from siphon command - perfect synergy!)
        input_data = read_stdin()

        # If no stdin, try source (using internal siphon stage for synergy)
        if input_data is None and source:
            # Siphon from source using internal siphon stage
            logger.info(f"Using internal siphon stage to extract from: {source}")
            logger.info("💡 Tip: Use 'siphon <source> | pipe <name>' for explicit separation")
            syphon_stage = SyphonStage(
                name="siphon_source",
                source_type=source.split(":")[0] if ":" in source else "filesystem",
                source_config={
                    "project_root": str(project_root),
                    "path": source.split(":")[1] if ":" in source else source
                }
            )

            # Create temporary context to siphon
            temp_context = PipeContext(
                pipe_name="temp_siphon",
                stage_name="siphon",
                data={}
            )

            try:
                temp_context = syphon_stage.process(temp_context)
                input_data = temp_context.get_data("siphoned_data", {})
            except Exception as e:
                logger.error(f"Failed to siphon from source: {e}")
                input_data = {}

    # Execute pipe
    logger.info(f"Executing pipe: {pipe_name}")
    result = pipe.execute(initial_data=input_data)

    # Handle destination
    if destination:
        if destination == "stdout" or destination == "-":
            write_stdout(result.to_dict(), output_format)
        elif destination.startswith("file:"):
            # Write to file
            file_path = Path(destination[5:])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Results written to: {file_path}")
        else:
            # Try to write to destination as file path
            file_path = Path(destination)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Results written to: {file_path}")
    else:
        # Default: write to stdout
        write_stdout(result.to_dict(), output_format)

    return result.to_dict()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PIPE Command - Unix-style pipes for ALL AI Chat workflows and ALL LUMINA workflows (perfect synergy with siphon command)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available pipes
  pipe --list

  # Basic pipe execution
  pipe hvac_email

  # Pipe with source (uses internal siphon)
  pipe hvac_email --source email:"hvac OR furnace"

  # Unix-style piping from siphon command (perfect synergy!)
  siphon email:"hvac OR furnace" | pipe hvac_email

  # Pipe to file
  pipe hvac_email --destination file:results.json

  # Pipe with custom query
  pipe hvac_email --query "from:fletcher" --days 30

  # Pipe to stdout (default)
  pipe hvac_email --destination stdout

  # Chain: siphon → pipe → another pipe
  siphon email:"query" | pipe hvac_email | pipe analyze

  # Works with ANY LUMINA workflow pipe
  pipe <any_pipe_name> [options]

Note: PIPE and SIPHON are designed for perfect synergy.
      SIPHON extracts, PIPE processes - complementary commands!
        """
    )

    parser.add_argument(
        "pipe_name",
        nargs="?",
        help="Name of pipe to execute (e.g., hvac_email, hvac). Use --list to see all available pipes."
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available pipes"
    )

    parser.add_argument(
        "--source",
        help="Source to siphon from (e.g., email:\"query\", filesystem:/path). Or use 'siphon <source> | pipe <name>' for perfect synergy!"
    )

    parser.add_argument(
        "--destination",
        help="Destination to pipe to (stdout, file:path, or file path)"
    )

    parser.add_argument(
        "--format",
        choices=["json", "text", "yaml"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--query",
        help="Custom query for email pipes"
    )

    parser.add_argument(
        "--days",
        type=int,
        help="Days to search back for email pipes"
    )

    parser.add_argument(
        "--budget",
        type=float,
        help="Budget for HVAC comparison pipes"
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

    # List pipes if requested
    if args.list:
        pipes = discover_pipes(project_root)
        print("\n" + "="*80)
        print("AVAILABLE PIPES - ALL LUMINA WORKFLOWS")
        print("="*80)
        print()

        if not pipes:
            print("No pipes found.")
        else:
            for pipe_name, pipe_info in sorted(pipes.items()):
                print(f"  {pipe_name}")
                if pipe_info.get("aliases"):
                    print(f"    Aliases: {', '.join(pipe_info['aliases'])}")
                if pipe_info.get("description"):
                    print(f"    Description: {pipe_info['description']}")
                print(f"    Type: {pipe_info.get('type', 'unknown')}")
                if pipe_info.get("stages"):
                    print(f"    Stages: {len(pipe_info['stages'])}")
                print()

        print("="*80)
        print(f"Total: {len(pipes)} pipe(s) available")
        print()
        print("Usage: pipe <pipe_name> [options]")
        print()
        sys.exit(0)

    # Require pipe_name if not listing
    if not args.pipe_name:
        parser.error("pipe_name is required (or use --list to see available pipes)")

    # Build kwargs for pipe-specific options
    kwargs = {}
    if args.query:
        kwargs["query"] = args.query
    if args.days:
        kwargs["days"] = args.days
    if args.budget:
        kwargs["budget"] = args.budget

    # Execute pipe command
    result = pipe_command(
        pipe_name=args.pipe_name,
        source=args.source,
        destination=args.destination,
        output_format=args.format,
        **kwargs
    )

    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":


    main()