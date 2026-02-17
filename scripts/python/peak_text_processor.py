#!/usr/bin/env python3
"""
@PEAK Text Processor
Combines AWK, SED, and Perl logic into unified @peak text processing system.

The @peak vision: Maximum power, minimum footprint, nutrient-dense solutions.

Features:
- AWK-style pattern scanning and field processing
- SED-style stream editing and transformation
- Perl-style regex and text manipulation
- Unified interface for all text processing
- Perfect synergy with siphon/pipe commands
- @PEAK quality standards enforced

Author: <COMPANY_NAME> LLC
Date: 2025-01-05

#PEAK #AWK #SED #PERL #TEXT-PROCESSING #SYPHON #PIPE
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union, Iterator
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("PeakTextProcessor")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("PeakTextProcessor")


class ProcessingMode(Enum):
    """Processing modes combining AWK, SED, and Perl"""
    AWK = "awk"          # Pattern scanning, field processing
    SED = "sed"          # Stream editing, substitution
    PERL = "perl"        # Regex, text manipulation
    UNIFIED = "unified"  # All three combined (@peak)


@dataclass
class FieldSpec:
    """AWK-style field specification"""
    delimiter: str = field(default=" ")
    field_numbers: List[int] = field(default_factory=list)  # Empty = all fields
    output_delimiter: str = field(default=" ")


@dataclass
class PatternAction:
    """AWK-style pattern-action pair"""
    pattern: str
    action: Callable[[str, Dict[str, Any]], Optional[str]]
    description: str = ""


@dataclass
class SedCommand:
    """SED-style command"""
    command: str  # s/pattern/replacement/flags, d, p, etc.
    pattern: Optional[str] = None
    replacement: Optional[str] = None
    flags: str = ""


@dataclass
class PerlExpression:
    """Perl-style expression"""
    expression: str
    modifiers: str = ""  # e, g, i, m, s, x


class PeakTextProcessor:
    """
    @PEAK Text Processor

    Combines AWK, SED, and Perl into unified @peak system.
    Maximum power, minimum footprint, nutrient-dense solutions.
    """

    def __init__(self, project_root: Path):
        """
        Initialize @peak text processor.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.mode = ProcessingMode.UNIFIED  # @peak: all modes combined
        self.field_spec = FieldSpec()
        self.pattern_actions: List[PatternAction] = []
        self.sed_commands: List[SedCommand] = []
        self.perl_expressions: List[PerlExpression] = []
        self.line_number = 0
        self.context: Dict[str, Any] = {}

        logger.info("✅ @PEAK Text Processor initialized")
        logger.info("   Combining AWK + SED + Perl into unified @peak system")

    # ============================================================================
    # AWK-STYLE PATTERN SCANNING & FIELD PROCESSING
    # ============================================================================

    def set_field_delimiter(self, delimiter: str, output_delimiter: Optional[str] = None):
        """
        Set field delimiter (AWK-style FS).

        Args:
            delimiter: Input field separator
            output_delimiter: Output field separator (default: same as input)
        """
        self.field_spec.delimiter = delimiter
        if output_delimiter:
            self.field_spec.output_delimiter = output_delimiter
        else:
            self.field_spec.output_delimiter = delimiter

    def process_fields(self, line: str, field_numbers: Optional[List[int]] = None) -> List[str]:
        """
        Process fields from line (AWK-style $1, $2, etc.).

        Args:
            line: Input line
            field_numbers: Field numbers to extract (None = all fields)

        Returns:
            List of field values
        """
        fields = line.split(self.field_spec.delimiter)

        if field_numbers is None:
            field_numbers = self.field_spec.field_numbers or list(range(1, len(fields) + 1))

        # AWK fields are 1-indexed
        result = []
        for num in field_numbers:
            idx = num - 1
            if 0 <= idx < len(fields):
                result.append(fields[idx])

        return result

    def add_pattern_action(self, pattern: str, action: Callable[[str, Dict[str, Any]], Optional[str]], description: str = ""):
        """
        Add AWK-style pattern-action pair.

        Args:
            pattern: Pattern to match (regex)
            action: Action function (line, context) -> output or None
            description: Description of action
        """
        self.pattern_actions.append(PatternAction(
            pattern=pattern,
            action=action,
            description=description
        ))

    def awk_process(self, line: str) -> Optional[str]:
        """
        Process line with AWK-style pattern-action pairs.

        Args:
            line: Input line

        Returns:
            Processed line or None (to skip)
        """
        self.line_number += 1
        self.context["line_number"] = self.line_number
        self.context["line"] = line

        # Process fields
        fields = self.process_fields(line)
        self.context["fields"] = fields
        self.context["NF"] = len(fields)  # AWK-style NF

        # Try pattern-action pairs
        for pattern_action in self.pattern_actions:
            if re.search(pattern_action.pattern, line):
                result = pattern_action.action(line, self.context)
                if result is not None:
                    return result

        # Default: return line as-is
        return line

    # ============================================================================
    # SED-STYLE STREAM EDITING
    # ============================================================================

    def add_sed_substitute(self, pattern: str, replacement: str, flags: str = "g"):
        """
        Add SED-style substitution (s/pattern/replacement/flags).

        Args:
            pattern: Pattern to match
            replacement: Replacement string
            flags: Flags (g=global, i=ignore case, etc.)
        """
        self.sed_commands.append(SedCommand(
            command="s",
            pattern=pattern,
            replacement=replacement,
            flags=flags
        ))

    def add_sed_delete(self, pattern: str):
        """
        Add SED-style delete command (/pattern/d).

        Args:
            pattern: Pattern to match for deletion
        """
        self.sed_commands.append(SedCommand(
            command="d",
            pattern=pattern
        ))

    def add_sed_print(self, pattern: str):
        """
        Add SED-style print command (/pattern/p).

        Args:
            pattern: Pattern to match for printing
        """
        self.sed_commands.append(SedCommand(
            command="p",
            pattern=pattern
        ))

    def sed_process(self, line: str) -> Optional[str]:
        """
        Process line with SED-style commands.

        Args:
            line: Input line

        Returns:
            Processed line or None (to skip/delete)
        """
        result = line

        for sed_cmd in self.sed_commands:
            if sed_cmd.command == "s":
                # Substitution
                if sed_cmd.pattern and sed_cmd.replacement is not None:
                    flags = 0
                    if "i" in sed_cmd.flags:
                        flags |= re.IGNORECASE
                    if "m" in sed_cmd.flags:
                        flags |= re.MULTILINE
                    if "s" in sed_cmd.flags:
                        flags |= re.DOTALL

                    count = 0 if "g" in sed_cmd.flags else 1
                    result = re.sub(sed_cmd.pattern, sed_cmd.replacement, result, count=count, flags=flags)

            elif sed_cmd.command == "d":
                # Delete
                if sed_cmd.pattern and re.search(sed_cmd.pattern, result):
                    return None  # Skip this line

            elif sed_cmd.command == "p":
                # Print (already handled by returning result)
                if sed_cmd.pattern and re.search(sed_cmd.pattern, result):
                    pass  # Will be printed

        return result

    # ============================================================================
    # PERL-STYLE REGEX & TEXT MANIPULATION
    # ============================================================================

    def add_perl_expression(self, expression: str, modifiers: str = ""):
        """
        Add Perl-style expression.

        Args:
            expression: Perl expression (e.g., s/pattern/replacement/)
            modifiers: Modifiers (e, g, i, m, s, x)
        """
        self.perl_expressions.append(PerlExpression(
            expression=expression,
            modifiers=modifiers
        ))

    def perl_process(self, line: str) -> str:
        """
        Process line with Perl-style expressions.

        Args:
            line: Input line

        Returns:
            Processed line
        """
        result = line

        for perl_expr in self.perl_expressions:
            # Parse Perl expression
            # Simple implementation - can be extended
            if perl_expr.expression.startswith("s/"):
                # Substitution: s/pattern/replacement/
                parts = perl_expr.expression[2:].split("/")
                if len(parts) >= 3:
                    pattern = parts[0]
                    replacement = parts[1]

                    flags = 0
                    if "i" in perl_expr.modifiers:
                        flags |= re.IGNORECASE
                    if "m" in perl_expr.modifiers:
                        flags |= re.MULTILINE
                    if "s" in perl_expr.modifiers:
                        flags |= re.DOTALL

                    count = 0 if "g" in perl_expr.modifiers else 1
                    result = re.sub(pattern, replacement, result, count=count, flags=flags)

            elif perl_expr.expression.startswith("tr/"):
                # Transliteration: tr/from/to/
                parts = perl_expr.expression[3:].split("/")
                if len(parts) >= 2:
                    from_chars = parts[0]
                    to_chars = parts[1]
                    result = result.translate(str.maketrans(from_chars, to_chars))

        return result

    # ============================================================================
    # UNIFIED @PEAK PROCESSING
    # ============================================================================

    def process_line(self, line: str) -> Optional[str]:
        """
        Process line with unified @peak system (AWK + SED + Perl).

        Args:
            line: Input line

        Returns:
            Processed line or None (to skip)
        """
        result = line

        # Step 1: AWK-style pattern scanning
        if self.mode in [ProcessingMode.AWK, ProcessingMode.UNIFIED]:
            awk_result = self.awk_process(result)
            if awk_result is None:
                return None  # Skip line
            result = awk_result

        # Step 2: SED-style stream editing
        if self.mode in [ProcessingMode.SED, ProcessingMode.UNIFIED]:
            sed_result = self.sed_process(result)
            if sed_result is None:
                return None  # Skip line
            result = sed_result

        # Step 3: Perl-style regex manipulation
        if self.mode in [ProcessingMode.PERL, ProcessingMode.UNIFIED]:
            result = self.perl_process(result)

        return result

    def process_stream(self, input_stream: Iterator[str]) -> Iterator[str]:
        """
        Process stream of lines (perfect synergy with siphon/pipe).

        Args:
            input_stream: Iterator of input lines

        Yields:
            Processed lines
        """
        for line in input_stream:
            processed = self.process_line(line.rstrip("\n"))
            if processed is not None:
                yield processed

    def process_file(self, file_path: Path) -> List[str]:
        try:
            """
            Process file and return results.

            Args:
                file_path: Path to input file

            Returns:
                List of processed lines
            """
            results = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in self.process_stream(f):
                    results.append(line)
            return results

        except Exception as e:
            self.logger.error(f"Error in process_file: {e}", exc_info=True)
            raise
    # ============================================================================
    # SIPHON/PIPE INTEGRATION
    # ============================================================================

    def process_siphoned_data(self, siphoned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process siphoned data (perfect synergy with siphon command).

        Args:
            siphoned_data: Data from siphon command

        Returns:
            Processed data
        """
        processed = {
            "success": True,
            "processed_items": [],
            "total_items": 0,
            "mode": self.mode.value
        }

        # Extract text items from siphoned data
        items = siphoned_data.get("items", [])
        if not items:
            # Try other common structures
            items = siphoned_data.get("emails", [])
            items = siphoned_data.get("files", [])

        processed["total_items"] = len(items)

        for item in items:
            # Convert item to text line
            if isinstance(item, dict):
                # Try to extract text content
                text = item.get("content", item.get("body", item.get("text", str(item))))
            else:
                text = str(item)

            # Process line
            processed_line = self.process_line(text)
            if processed_line is not None:
                processed["processed_items"].append(processed_line)

        return processed

    # ============================================================================
    # COMMAND-LINE INTERFACE
    # ============================================================================

    @staticmethod
    def from_args(args: argparse.Namespace) -> 'PeakTextProcessor':
        """
        Create processor from command-line arguments.

        Args:
            args: Parsed arguments

        Returns:
            PeakTextProcessor instance
        """
        processor = PeakTextProcessor(args.project_root)

        # Set mode
        if args.mode:
            processor.mode = ProcessingMode(args.mode)

        # Set field delimiter
        if args.field_delimiter:
            processor.set_field_delimiter(args.field_delimiter, args.output_delimiter)

        # Add AWK patterns
        if args.awk_pattern:
            for pattern in args.awk_pattern:
                processor.add_pattern_action(
                    pattern=pattern,
                    action=lambda line, ctx: line,  # Default: pass through
                    description="Command-line pattern"
                )

        # Add SED commands
        if args.sed_command:
            for cmd in args.sed_command:
                if cmd.startswith("s/"):
                    # Substitution
                    parts = cmd[2:].split("/")
                    if len(parts) >= 3:
                        pattern = parts[0]
                        replacement = parts[1]
                        flags = parts[2] if len(parts) > 2 else "g"
                        processor.add_sed_substitute(pattern, replacement, flags)
                elif cmd.startswith("/") and cmd.endswith("/d"):
                    # Delete
                    pattern = cmd[1:-2]
                    processor.add_sed_delete(pattern)

        # Add Perl expressions
        if args.perl_expr:
            for expr in args.perl_expr:
                processor.add_perl_expression(expr, args.perl_modifiers or "")

        return processor


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="@PEAK Text Processor - Combines AWK, SED, and Perl into unified @peak system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # AWK-style field processing
  peak_text --mode awk --field-delimiter "," --input file.csv

  # SED-style substitution
  peak_text --mode sed --sed-command "s/old/new/g" --input file.txt

  # Perl-style regex
  peak_text --mode perl --perl-expr "s/pattern/replacement/g" --input file.txt

  # Unified @peak mode (all three combined)
  peak_text --mode unified --input file.txt

  # Perfect synergy with siphon/pipe
  siphon email:"query" | peak_text --mode unified | pipe hvac_email

  # Process from stdin
  cat file.txt | peak_text --sed-command "s/old/new/g"
        """
    )

    parser.add_argument(
        "--mode",
        choices=["awk", "sed", "perl", "unified"],
        default="unified",
        help="Processing mode (default: unified @peak mode)"
    )

    parser.add_argument(
        "--input",
        type=Path,
        help="Input file (default: stdin)"
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: stdout)"
    )

    parser.add_argument(
        "--field-delimiter",
        help="Field delimiter for AWK-style processing (default: space)"
    )

    parser.add_argument(
        "--output-delimiter",
        help="Output field delimiter (default: same as input)"
    )

    parser.add_argument(
        "--awk-pattern",
        action="append",
        help="AWK-style pattern to match (can specify multiple)"
    )

    parser.add_argument(
        "--sed-command",
        action="append",
        help="SED-style command (e.g., s/old/new/g, /pattern/d)"
    )

    parser.add_argument(
        "--perl-expr",
        action="append",
        help="Perl-style expression (e.g., s/pattern/replacement/)"
    )

    parser.add_argument(
        "--perl-modifiers",
        help="Perl expression modifiers (e.g., gi, ms)"
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Project root directory"
    )

    args = parser.parse_args()

    # Create processor
    processor = PeakTextProcessor.from_args(args)

    # Determine input source
    if args.input:
        # Process file
        results = processor.process_file(args.input)
    else:
        # Process stdin (perfect synergy with siphon/pipe)
        results = list(processor.process_stream(sys.stdin))

    # Determine output destination
    if args.output:
        # Write to file
        with open(args.output, 'w', encoding='utf-8') as f:
            for line in results:
                f.write(line + "\n")
        logger.info(f"✅ Processed {len(results)} lines, written to {args.output}")
    else:
        # Write to stdout (perfect synergy with piping)
        for line in results:
            print(line)

    sys.exit(0)


if __name__ == "__main__":


    main()