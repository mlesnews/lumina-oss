#!/usr/bin/env python3
"""
DEATHSTAR Pipe Stage
Integrates DEATHSTAR processing into LUMINA pipes.

#JARVIS #LUMINA #DEATHSTAR #PIPES #AWK #SED #PERL
"""

from pathlib import Path
from typing import Any, Dict, Optional
from scripts.python.pipes.core import PipeStage, PipeContext, PipeStageType
from scripts.python.deathstar_processor import (
    DeathstarProcessor,
    ProcessingMode,
    SEDCommand
)

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("DeathstarStage")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DeathstarStage")


class DeathstarStage(PipeStage):
    """
    DEATHSTAR Pipe Stage - Ultimate text processing power.

    Can be used in any pipe to apply AWK, SED, or PERL processing.
    """

    def __init__(
        self,
        name: str,
        mode: ProcessingMode,
        config: Dict[str, Any],
        project_root: Path = None
    ):
        """
        Initialize DEATHSTAR stage.

        Args:
            name: Stage name
            mode: Processing mode (AWK, SED, PERL, COMBINED)
            config: Configuration for the mode
            project_root: Project root directory
        """
        super().__init__(name, PipeStageType.TRANSFORM)
        self.mode = mode
        self.config = config
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.processor = DeathstarProcessor(self.project_root)

    def process(self, context: PipeContext) -> PipeContext:
        """
        Process context data through DEATHSTAR.

        Args:
            context: Pipe context with data

        Returns:
            Updated context with processed data
        """
        logger.info(f"🔥 DEATHSTAR STAGE: {self.name} - {self.mode.value.upper()} MODE")

        # Get input data
        input_data = context.data

        # Convert to text if needed
        if isinstance(input_data, dict):
            # Try to extract text from common keys
            text = input_data.get("text") or input_data.get("content") or str(input_data)
        elif isinstance(input_data, str):
            text = input_data
        else:
            text = str(input_data)

        # Process based on mode
        if self.mode == ProcessingMode.AWK:
            result = self.processor.process_awk(
                text,
                pattern=self.config.get("pattern"),
                action=self.config.get("action"),
                field_separator=self.config.get("field_separator"),
                record_separator=self.config.get("record_separator"),
                variables=self.config.get("variables", {})
            )

        elif self.mode == ProcessingMode.SED:
            # Build SED commands from config
            commands = []
            for cmd_config in self.config.get("commands", []):
                commands.append(SEDCommand(
                    address=cmd_config.get("address", ""),
                    command=cmd_config.get("command", "s"),
                    pattern=cmd_config.get("pattern", ""),
                    replacement=cmd_config.get("replacement", ""),
                    flags=cmd_config.get("flags", "")
                ))

            result = self.processor.process_sed(text, commands)

        elif self.mode == ProcessingMode.PERL:
            result = self.processor.process_perl(
                text,
                expression=self.config.get("expression", ""),
                modifiers=self.config.get("modifiers", ""),
                variables=self.config.get("variables", {})
            )

        elif self.mode == ProcessingMode.COMBINED:
            # Build commands for combined mode
            sed_commands = []
            for cmd_config in self.config.get("sed_commands", []):
                sed_commands.append(SEDCommand(
                    address=cmd_config.get("address", ""),
                    command=cmd_config.get("command", "s"),
                    pattern=cmd_config.get("pattern", ""),
                    replacement=cmd_config.get("replacement", ""),
                    flags=cmd_config.get("flags", "")
                ))

            result = self.processor.process_combined(
                text,
                awk_pattern=self.config.get("awk_pattern"),
                awk_action=self.config.get("awk_action"),
                sed_commands=sed_commands if sed_commands else None,
                perl_expression=self.config.get("perl_expression"),
                order=self.config.get("order")
            )

        else:
            raise ValueError(f"Unknown processing mode: {self.mode}")

        # Update context with processed data
        context.add_data("processed_text", result.output)
        context.add_data("deathstar_result", {
            "success": result.success,
            "processed_lines": result.processed_lines,
            "matches": result.matches,
            "transformations": result.transformations,
            "mode": result.mode.value,
            "metadata": result.metadata
        })

        # Add metadata
        context.metadata["deathstar_stage"] = self.name
        context.metadata["deathstar_mode"] = self.mode.value
        context.metadata["deathstar_transformations"] = result.transformations

        logger.info(f"✅ DEATHSTAR processed {result.processed_lines} lines, {result.transformations} transformations")

        return context
