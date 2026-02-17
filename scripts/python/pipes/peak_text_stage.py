#!/usr/bin/env python3
"""
@PEAK Text Processing Stage for Pipes

Integrates @PEAK Text Processor (AWK + SED + Perl) into pipe system.
Perfect synergy with siphon/pipe commands.

#PEAK #AWK #SED #PERL #PIPES #SYPHON
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.python.pipes.core import PipeStage, PipeContext
from scripts.python.peak_text_processor import PeakTextProcessor, ProcessingMode


class PeakTextStage(PipeStage):
    """
    @PEAK Text Processing Stage

    Combines AWK, SED, and Perl logic for text processing in pipes.
    """

    def __init__(
        self,
        name: str,
        mode: str = "unified",
        field_delimiter: Optional[str] = None,
        sed_commands: Optional[List[str]] = None,
        perl_expressions: Optional[List[str]] = None,
        project_root: Optional[Path] = None
    ):
        """
        Initialize @peak text processing stage.

        Args:
            name: Stage name
            mode: Processing mode (awk, sed, perl, unified)
            field_delimiter: Field delimiter for AWK-style processing
            sed_commands: List of SED commands
            perl_expressions: List of Perl expressions
            project_root: Project root directory
        """
        super().__init__(name)

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent

        self.project_root = project_root
        self.mode = ProcessingMode(mode)
        self.field_delimiter = field_delimiter
        self.sed_commands = sed_commands or []
        self.perl_expressions = perl_expressions or []

        # Initialize processor
        self.processor = PeakTextProcessor(project_root)
        self.processor.mode = self.mode

        if field_delimiter:
            self.processor.set_field_delimiter(field_delimiter)

        # Add SED commands
        for cmd in self.sed_commands:
            if cmd.startswith("s/"):
                # Substitution
                parts = cmd[2:].split("/")
                if len(parts) >= 3:
                    pattern = parts[0]
                    replacement = parts[1]
                    flags = parts[2] if len(parts) > 2 else "g"
                    self.processor.add_sed_substitute(pattern, replacement, flags)
            elif cmd.startswith("/") and cmd.endswith("/d"):
                # Delete
                pattern = cmd[1:-2]
                self.processor.add_sed_delete(pattern)

        # Add Perl expressions
        for expr in self.perl_expressions:
            self.processor.add_perl_expression(expr)

    def process(self, context: PipeContext) -> PipeContext:
        """
        Process context data with @peak text processor.

        Args:
            context: Pipe context with data to process

        Returns:
            Updated context with processed data
        """
        # Get input data
        input_data = context.data.get("siphoned_data") or context.data

        # Process with @peak text processor
        if isinstance(input_data, dict):
            # Process siphoned data structure
            processed = self.processor.process_siphoned_data(input_data)
        elif isinstance(input_data, list):
            # Process list of lines
            processed_lines = []
            for item in input_data:
                if isinstance(item, str):
                    processed = self.processor.process_line(item)
                    if processed is not None:
                        processed_lines.append(processed)
                else:
                    processed_lines.append(str(item))
            processed = processed_lines
        elif isinstance(input_data, str):
            # Process single string
            processed = self.processor.process_line(input_data)
            if processed is None:
                processed = ""
        else:
            # Convert to string and process
            processed = self.processor.process_line(str(input_data))
            if processed is None:
                processed = ""

        # Update context
        context.set_data("peak_processed_data", processed)
        context.set_data("processing_mode", self.mode.value)
        context.metadata["peak_text_processor"] = {
            "mode": self.mode.value,
            "sed_commands": len(self.sed_commands),
            "perl_expressions": len(self.perl_expressions)
        }

        return context
