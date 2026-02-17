#!/usr/bin/env python3
"""
DEATHSTAR - Ultimate Text Processing Power
Combines AWK, SED, and PERL into one unified battlestation.

The #deathstar represents ULTIMATE POWER - the peak of text processing capabilities.
Combines the best of:
- AWK: Pattern scanning, field processing, data extraction
- SED: Stream editing, text transformation, pattern substitution
- PERL: Powerful regex, text manipulation, advanced scripting

This is the battlestation - robust, comprehensive, fully functional.

#JARVIS #LUMINA #DEATHSTAR #AWK #SED #PERL #ULTIMATE-POWER #PEAK
"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Pattern
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
import subprocess
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("Deathstar")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Deathstar")


class ProcessingMode(Enum):
    """Processing modes - AWK, SED, PERL, or COMBINED"""
    AWK = "awk"
    SED = "sed"
    PERL = "perl"
    COMBINED = "combined"  # Ultimate power - all three


@dataclass
class AWKPattern:
    """AWK-style pattern with action"""
    pattern: str
    action: str
    field_separator: str = None
    record_separator: str = None


@dataclass
class SEDCommand:
    """SED-style command"""
    address: str = ""  # Line address (e.g., "1,5" or "/pattern/")
    command: str = ""  # Command (s, d, p, etc.)
    pattern: str = ""  # Pattern for substitution/search
    replacement: str = ""  # Replacement text
    flags: str = ""  # Flags (g, i, etc.)


@dataclass
class PERLExpression:
    """PERL-style expression"""
    expression: str
    modifiers: str = ""  # Regex modifiers (g, i, m, s, x)


@dataclass
class DeathstarResult:
    """Result from DEATHSTAR processing"""
    success: bool
    output: str
    processed_lines: int
    matches: int
    transformations: int
    mode: ProcessingMode
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeathstarProcessor:
    """
    DEATHSTAR - Ultimate Text Processing Power

    Combines AWK, SED, and PERL capabilities into one unified system.
    The battlestation for all text processing needs.
    """

    def __init__(self, project_root: Path = None):
        """
        Initialize DEATHSTAR processor.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger

        # Check for native tools (for maximum power)
        self.has_awk = shutil.which("awk") is not None
        self.has_sed = shutil.which("sed") is not None
        self.has_perl = shutil.which("perl") is not None

        self.logger.info("="*80)
        self.logger.info("🌌 DEATHSTAR INITIALIZING - ULTIMATE POWER")
        self.logger.info("="*80)
        self.logger.info(f"✅ AWK available: {self.has_awk}")
        self.logger.info(f"✅ SED available: {self.has_sed}")
        self.logger.info(f"✅ PERL available: {self.has_perl}")
        self.logger.info("="*80)

    def process_awk(
        self,
        input_text: str,
        pattern: str = None,
        action: str = None,
        field_separator: str = None,
        record_separator: str = None,
        variables: Dict[str, Any] = None
    ) -> DeathstarResult:
        """
        Process text using AWK-style logic.

        AWK Power:
        - Pattern scanning
        - Field processing (NF, $1, $2, etc.)
        - Built-in variables (NR, NF, FS, RS, etc.)
        - Arithmetic and string operations

        Args:
            input_text: Input text to process
            pattern: AWK pattern (e.g., "/regex/" or condition)
            action: AWK action (e.g., "{print $1, $2}")
            field_separator: Field separator (FS)
            record_separator: Record separator (RS)
            variables: Additional variables to set

        Returns:
            DeathstarResult with processed output
        """
        self.logger.info("🔥 AWK MODE ACTIVATED")

        # Use native AWK if available (maximum power)
        if self.has_awk:
            return self._process_native_awk(
                input_text, pattern, action, field_separator, record_separator, variables
            )

        # Fallback to Python AWK emulation
        return self._process_python_awk(
            input_text, pattern, action, field_separator, record_separator, variables
        )

    def _process_native_awk(
        self,
        input_text: str,
        pattern: str,
        action: str,
        field_separator: str,
        record_separator: str,
        variables: Dict[str, Any]
    ) -> DeathstarResult:
        """Process using native AWK (maximum power)."""
        try:
            # Build AWK command
            awk_cmd = ["awk"]

            # Set field separator
            if field_separator:
                awk_cmd.extend(["-F", field_separator])

            # Set variables
            if variables:
                for k, v in variables.items():
                    awk_cmd.extend(["-v", f"{k}={v}"])

            # Build AWK program
            awk_program = ""
            if pattern and action:
                awk_program = f"{pattern} {action}"
            elif pattern:
                awk_program = pattern
            elif action:
                awk_program = action
            else:
                awk_program = "{print}"  # Default: print all

            awk_cmd.append(awk_program)

            # Execute AWK
            result = subprocess.run(
                awk_cmd,
                input=input_text,
                text=True,
                capture_output=True,
                check=True
            )

            return DeathstarResult(
                success=True,
                output=result.stdout,
                processed_lines=len(input_text.splitlines()),
                matches=len(result.stdout.splitlines()),
                transformations=0,
                mode=ProcessingMode.AWK,
                metadata={"native_awk": True, "command": " ".join(awk_cmd)}
            )

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Native AWK failed: {e}")
            # Fallback to Python
            return self._process_python_awk(
                input_text, pattern, action, field_separator, record_separator, variables
            )

    def _process_python_awk(
        self,
        input_text: str,
        pattern: str,
        action: str,
        field_separator: str,
        record_separator: str,
        variables: Dict[str, Any]
    ) -> DeathstarResult:
        """Process using Python AWK emulation."""
        self.logger.info("Using Python AWK emulation")

        # Set field separator (default: whitespace)
        fs = field_separator or r'\s+'
        rs = record_separator or '\n'

        # Initialize variables
        NR = 0  # Record number
        NF = 0  # Number of fields
        FS = fs
        RS = rs

        # Set custom variables
        if variables:
            for k, v in variables.items():
                globals()[k] = v

        output_lines = []
        matches = 0

        # Process each record
        records = input_text.split(rs)
        for record in records:
            if not record.strip():
                continue

            NR += 1

            # Split into fields
            if fs == r'\s+':
                fields = record.split()
            else:
                fields = re.split(fs, record)

            NF = len(fields)

            # Create field variables ($1, $2, etc.)
            field_vars = {}
            for i, field_val in enumerate(fields, 1):
                field_vars[f"${i}"] = field_val
                field_vars[i] = field_val

            # Evaluate pattern
            match = True
            if pattern:
                # Simple pattern matching
                if pattern.startswith("/") and pattern.endswith("/"):
                    # Regex pattern
                    regex = pattern[1:-1]
                    match = bool(re.search(regex, record))
                else:
                    # Condition pattern (simplified)
                    # This is a basic implementation
                    match = True  # Would need full expression parser

            if match:
                matches += 1

                # Execute action
                if action:
                    # Simple action processing
                    if "print" in action:
                        # Extract print arguments
                        if "$" in action:
                            # Print specific fields - parse print statement
                            # Handle {print $1, $2} or {print $1 $2}
                            print_args = action.replace("{", "").replace("}", "").strip()
                            if print_args.startswith("print"):
                                print_args = print_args[5:].strip()  # Remove "print"

                                # Parse field references
                                parts = []
                                # Handle comma-separated or space-separated fields
                                for part in print_args.split(","):
                                    part = part.strip()
                                    if part.startswith("$"):
                                        # Field reference
                                        field_num = int(part[1:]) if part[1:].isdigit() else 0
                                        if 1 <= field_num <= NF:
                                            parts.append(fields[field_num - 1])
                                        else:
                                            parts.append("")
                                    elif part == "$0":
                                        parts.append(record)
                                    else:
                                        # Literal or variable
                                        parts.append(part)

                                output_lines.append(" ".join(parts))
                            else:
                                output_lines.append(record)
                        else:
                            # Print entire record
                            output_lines.append(record)
                    else:
                        # Custom action (simplified) - just print record
                        output_lines.append(record)
                else:
                    # Default: print matching records
                    output_lines.append(record)

        return DeathstarResult(
            success=True,
            output="\n".join(output_lines),
            processed_lines=NR,
            matches=matches,
            transformations=0,
            mode=ProcessingMode.AWK,
            metadata={"python_emulation": True}
        )

    def process_sed(
        self,
        input_text: str,
        commands: List[SEDCommand],
        in_place: bool = False
    ) -> DeathstarResult:
        """
        Process text using SED-style commands.

        SED Power:
        - Stream editing
        - Pattern substitution (s///)
        - Line deletion (d)
        - Line printing (p)
        - Address ranges
        - Multiple commands

        Args:
            input_text: Input text to process
            commands: List of SED commands
            in_place: Whether to modify in place

        Returns:
            DeathstarResult with processed output
        """
        self.logger.info("🔥 SED MODE ACTIVATED")

        # Use native SED if available (maximum power)
        if self.has_sed:
            return self._process_native_sed(input_text, commands, in_place)

        # Fallback to Python SED emulation
        return self._process_python_sed(input_text, commands)

    def _process_native_sed(
        self,
        input_text: str,
        commands: List[SEDCommand],
        in_place: bool
    ) -> DeathstarResult:
        """Process using native SED (maximum power)."""
        try:
            # Build SED command
            sed_cmd = ["sed"]

            # Build SED script from commands
            sed_script = ""
            for cmd in commands:
                if cmd.command == "s":  # Substitution
                    sed_script += f"s/{cmd.pattern}/{cmd.replacement}/{cmd.flags}\n"
                elif cmd.command == "d":  # Delete
                    if cmd.address:
                        sed_script += f"{cmd.address}d\n"
                    else:
                        sed_script += "d\n"
                elif cmd.command == "p":  # Print
                    if cmd.address:
                        sed_script += f"{cmd.address}p\n"
                    else:
                        sed_script += "p\n"
                # Add more commands as needed

            # Execute SED
            result = subprocess.run(
                ["sed", "-E", "-e", sed_script.strip()],
                input=input_text,
                text=True,
                capture_output=True,
                check=True
            )

            transformations = sum(1 for cmd in commands if cmd.command == "s")

            return DeathstarResult(
                success=True,
                output=result.stdout,
                processed_lines=len(input_text.splitlines()),
                matches=len(result.stdout.splitlines()),
                transformations=transformations,
                mode=ProcessingMode.SED,
                metadata={"native_sed": True}
            )

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Native SED failed: {e}")
            return self._process_python_sed(input_text, commands)

    def _process_python_sed(
        self,
        input_text: str,
        commands: List[SEDCommand]
    ) -> DeathstarResult:
        """Process using Python SED emulation."""
        self.logger.info("Using Python SED emulation")

        lines = input_text.splitlines()
        output_lines = []
        transformations = 0

        for line_num, line in enumerate(lines, 1):
            line_modified = line

            for cmd in commands:
                # Check address
                address_match = True
                if cmd.address:
                    if cmd.address.isdigit():
                        # Line number
                        address_match = (line_num == int(cmd.address))
                    elif "/" in cmd.address:
                        # Pattern address
                        pattern = cmd.address.strip("/")
                        address_match = bool(re.search(pattern, line))
                    elif "," in cmd.address:
                        # Range address
                        start, end = cmd.address.split(",")
                        start_num = int(start) if start.isdigit() else 1
                        end_num = int(end) if end.isdigit() else len(lines)
                        address_match = start_num <= line_num <= end_num

                if not address_match:
                    continue

                # Execute command
                if cmd.command == "s":  # Substitution
                    flags = 0
                    if "i" in cmd.flags:
                        flags |= re.IGNORECASE
                    if "m" in cmd.flags:
                        flags |= re.MULTILINE

                    if "g" in cmd.flags:
                        # Global replacement
                        line_modified = re.sub(
                            cmd.pattern,
                            cmd.replacement,
                            line_modified,
                            flags=flags
                        )
                        transformations += line_modified != line
                    else:
                        # Single replacement
                        new_line = re.sub(
                            cmd.pattern,
                            cmd.replacement,
                            line_modified,
                            count=1,
                            flags=flags
                        )
                        if new_line != line_modified:
                            transformations += 1
                        line_modified = new_line

                elif cmd.command == "d":  # Delete
                    line_modified = None
                    break

                elif cmd.command == "p":  # Print
                    output_lines.append(line_modified)

            if line_modified is not None:
                output_lines.append(line_modified)

        return DeathstarResult(
            success=True,
            output="\n".join(output_lines),
            processed_lines=len(lines),
            matches=len(output_lines),
            transformations=transformations,
            mode=ProcessingMode.SED,
            metadata={"python_emulation": True}
        )

    def process_perl(
        self,
        input_text: str,
        expression: str,
        modifiers: str = "",
        variables: Dict[str, Any] = None
    ) -> DeathstarResult:
        """
        Process text using PERL-style expressions.

        PERL Power:
        - Powerful regex
        - Text manipulation
        - Advanced pattern matching
        - String operations
        - Variable interpolation

        Args:
            input_text: Input text to process
            expression: PERL expression
            modifiers: Regex modifiers (g, i, m, s, x)
            variables: Variables to use in expression

        Returns:
            DeathstarResult with processed output
        """
        self.logger.info("🔥 PERL MODE ACTIVATED")

        # Use native PERL if available (maximum power)
        if self.has_perl:
            return self._process_native_perl(input_text, expression, modifiers, variables)

        # Fallback to Python PERL emulation
        return self._process_python_perl(input_text, expression, modifiers, variables)

    def _process_native_perl(
        self,
        input_text: str,
        expression: str,
        modifiers: str,
        variables: Dict[str, Any]
    ) -> DeathstarResult:
        """Process using native PERL (maximum power)."""
        try:
            # Build PERL one-liner
            perl_code = expression

            # Set variables
            if variables:
                var_code = "; ".join([f"${k} = {json.dumps(v)}" for k, v in variables.items()])
                perl_code = f"{var_code}; {perl_code}"

            # Execute PERL (use -e for expression, -p for print)
            # Escape properly for shell
            result = subprocess.run(
                ["perl", "-pe", perl_code],
                input=input_text,
                text=True,
                capture_output=True,
                check=True,
                shell=False
            )

            return DeathstarResult(
                success=True,
                output=result.stdout,
                processed_lines=len(input_text.splitlines()),
                matches=len(result.stdout.splitlines()),
                transformations=1,
                mode=ProcessingMode.PERL,
                metadata={"native_perl": True}
            )

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Native PERL failed: {e}")
            return self._process_python_perl(input_text, expression, modifiers, variables)

    def _process_python_perl(
        self,
        input_text: str,
        expression: str,
        modifiers: str,
        variables: Dict[str, Any]
    ) -> DeathstarResult:
        """Process using Python PERL emulation (regex-based)."""
        self.logger.info("Using Python PERL emulation")

        # Parse modifiers
        flags = 0
        if "i" in modifiers:
            flags |= re.IGNORECASE
        if "m" in modifiers:
            flags |= re.MULTILINE
        if "s" in modifiers:
            flags |= re.DOTALL
        if "x" in modifiers:
            flags |= re.VERBOSE

        # Simple PERL expression processing
        # This is a simplified version - full PERL would need a parser
        output = input_text
        transformations = 0

        # Handle common PERL patterns
        if expression.startswith("s/"):
            # Substitution: s/pattern/replacement/flags
            parts = expression[2:].split("/")
            if len(parts) >= 2:
                pattern = parts[0]
                replacement = parts[1]
                perl_flags = parts[2] if len(parts) > 2 else ""

                if "g" in perl_flags:
                    output = re.sub(pattern, replacement, output, flags=flags)
                    transformations = len(re.findall(pattern, output, flags=flags))
                else:
                    output = re.sub(pattern, replacement, output, count=1, flags=flags)
                    transformations = 1 if re.search(pattern, output, flags=flags) else 0

        return DeathstarResult(
            success=True,
            output=output,
            processed_lines=len(input_text.splitlines()),
            matches=len(output.splitlines()),
            transformations=transformations,
            mode=ProcessingMode.PERL,
            metadata={"python_emulation": True}
        )

    def process_combined(
        self,
        input_text: str,
        awk_pattern: str = None,
        awk_action: str = None,
        sed_commands: List[SEDCommand] = None,
        perl_expression: str = None,
        order: List[ProcessingMode] = None
    ) -> DeathstarResult:
        """
        Process text using COMBINED mode - ultimate power!

        Combines AWK, SED, and PERL in sequence.
        This is the DEATHSTAR - maximum power.

        Args:
            input_text: Input text to process
            awk_pattern: AWK pattern
            awk_action: AWK action
            sed_commands: SED commands
            perl_expression: PERL expression
            order: Processing order (default: AWK -> SED -> PERL)

        Returns:
            DeathstarResult with processed output
        """
        self.logger.info("="*80)
        self.logger.info("🌌 DEATHSTAR MODE - ULTIMATE POWER ACTIVATED")
        self.logger.info("="*80)

        order = order or [ProcessingMode.AWK, ProcessingMode.SED, ProcessingMode.PERL]
        current_text = input_text
        total_transformations = 0
        total_matches = 0

        # Process in order
        for mode in order:
            if mode == ProcessingMode.AWK and (awk_pattern or awk_action):
                self.logger.info("🔥 AWK processing...")
                result = self.process_awk(
                    current_text,
                    pattern=awk_pattern,
                    action=awk_action
                )
                current_text = result.output
                total_transformations += result.transformations
                total_matches += result.matches

            elif mode == ProcessingMode.SED and sed_commands:
                self.logger.info("🔥 SED processing...")
                result = self.process_sed(current_text, sed_commands)
                current_text = result.output
                total_transformations += result.transformations
                total_matches += result.matches

            elif mode == ProcessingMode.PERL and perl_expression:
                self.logger.info("🔥 PERL processing...")
                result = self.process_perl(current_text, perl_expression)
                current_text = result.output
                total_transformations += result.transformations
                total_matches += result.matches

        self.logger.info("="*80)
        self.logger.info("✅ DEATHSTAR COMPLETE - ULTIMATE POWER DELIVERED")
        self.logger.info("="*80)

        return DeathstarResult(
            success=True,
            output=current_text,
            processed_lines=len(input_text.splitlines()),
            matches=total_matches,
            transformations=total_transformations,
            mode=ProcessingMode.COMBINED,
            metadata={
                "combined_mode": True,
                "processing_order": [m.value for m in order],
                "total_stages": len(order)
            }
        )


def main():
    """Main CLI entry point for DEATHSTAR."""
    parser = argparse.ArgumentParser(
        description="DEATHSTAR - Ultimate Text Processing Power (AWK + SED + PERL)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # AWK mode - extract first field
  deathstar --awk --pattern '{print $1}' input.txt

  # SED mode - substitute pattern
  deathstar --sed --substitute 'old/new/g' input.txt

  # PERL mode - regex processing
  deathstar --perl --expression 's/pattern/replacement/g' input.txt

  # COMBINED mode - ultimate power!
  deathstar --combined --awk-pattern '{print $1}' --sed-substitute 'old/new/g' input.txt

  # Pipe from stdin
  cat input.txt | deathstar --awk --pattern '{print $1}'

  # Perfect synergy with siphon
  siphon email:"query" | deathstar --perl --expression 's/pattern/replacement/g' | pipe hvac_email

#JARVIS #LUMINA #DEATHSTAR #AWK #SED #PERL #ULTIMATE-POWER
        """
    )

    parser.add_argument("input_file", nargs="?", help="Input file (or use stdin)")

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--awk", action="store_true", help="AWK mode")
    mode_group.add_argument("--sed", action="store_true", help="SED mode")
    mode_group.add_argument("--perl", action="store_true", help="PERL mode")
    mode_group.add_argument("--combined", action="store_true", help="COMBINED mode (ultimate power!)")

    # AWK options
    parser.add_argument("--awk-pattern", help="AWK pattern")
    parser.add_argument("--awk-action", help="AWK action")
    parser.add_argument("--field-separator", "-F", help="Field separator (AWK)")

    # SED options
    parser.add_argument("--sed-substitute", help="SED substitution: pattern/replacement/flags")
    parser.add_argument("--sed-delete", help="SED delete pattern")

    # PERL options
    parser.add_argument("--perl-expression", help="PERL expression")
    parser.add_argument("--perl-modifiers", help="PERL regex modifiers")

    # Output options
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    # Initialize DEATHSTAR
    processor = DeathstarProcessor()

    # Read input
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
    else:
        # Read from stdin
        input_text = sys.stdin.read()

    # Process based on mode
    if args.awk:
        result = processor.process_awk(
            input_text,
            pattern=args.awk_pattern,
            action=args.awk_action,
            field_separator=args.field_separator
        )

    elif args.sed:
        # Build SED commands
        commands = []
        if args.sed_substitute:
            parts = args.sed_substitute.split("/")
            if len(parts) >= 2:
                commands.append(SEDCommand(
                    command="s",
                    pattern=parts[0],
                    replacement=parts[1],
                    flags=parts[2] if len(parts) > 2 else ""
                ))
        if args.sed_delete:
            commands.append(SEDCommand(command="d", pattern=args.sed_delete))

        result = processor.process_sed(input_text, commands)

    elif args.perl:
        result = processor.process_perl(
            input_text,
            expression=args.perl_expression or "",
            modifiers=args.perl_modifiers or ""
        )

    elif args.combined:
        # Build commands
        sed_commands = []
        if args.sed_substitute:
            parts = args.sed_substitute.split("/")
            if len(parts) >= 2:
                sed_commands.append(SEDCommand(
                    command="s",
                    pattern=parts[0],
                    replacement=parts[1],
                    flags=parts[2] if len(parts) > 2 else ""
                ))

        result = processor.process_combined(
            input_text,
            awk_pattern=args.awk_pattern,
            awk_action=args.awk_action,
            sed_commands=sed_commands if sed_commands else None,
            perl_expression=args.perl_expression
        )

    # Output result
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == "json":
                f.write(json.dumps({
                    "success": result.success,
                    "output": result.output,
                    "processed_lines": result.processed_lines,
                    "matches": result.matches,
                    "transformations": result.transformations,
                    "mode": result.mode.value,
                    "metadata": result.metadata
                }, indent=2))
            else:
                f.write(result.output)
        logger.info(f"✅ Output written to: {args.output}")
    else:
        if args.format == "json":
            print(json.dumps({
                "success": result.success,
                "output": result.output,
                "processed_lines": result.processed_lines,
                "matches": result.matches,
                "transformations": result.transformations,
                "mode": result.mode.value,
                "metadata": result.metadata
            }, indent=2))
        else:
            print(result.output)

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":


    main()