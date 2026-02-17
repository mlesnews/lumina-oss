#!/usr/bin/env python3
"""
Matrix Extractor for SYPHON
Universal Matrix Simulation Pipe integration
"""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING

from syphon.models import SyphonData, DataSourceType, ExtractionResult
from syphon.extractors import BaseExtractor

if TYPE_CHECKING:
    from syphon.core import SYPHONConfig

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class MatrixExtractor(BaseExtractor):
    """
    Universal Matrix Simulation Pipe Extractor for SYPHON

    Pipes ANY data source through dual A & B matrix/lattice simulations.
    Integrates with @r5d4 (R5-D4) for knowledge aggregation.

    Can ingest:
    - Subprocess output (any command)
    - File streams (line-by-line or JSON)
    - Queue data (from other systems)
    - Iterator data (any Python iterator)
    - SYPHON extracted data (from other extractors)
    """

    def __init__(self, config: "SYPHONConfig"):
        super().__init__(config)
        self.matrix_pipe = None
        self.logger = get_logger("MatrixExtractor")
        self._initialize_matrix_pipe()

    def _initialize_matrix_pipe(self):
        """Initialize universal matrix simulation pipe"""
        try:
            from universal_matrix_simulation_pipe import (
                UniversalMatrixSimulationPipe,
                SubprocessDataSource,
                FileDataSource,
                QueueDataSource,
                IteratorDataSource
            )

            self.matrix_pipe = UniversalMatrixSimulationPipe(
                project_root=self.config.project_root,
                enable_r5=True  # Enable R5-D4 integration
            )
            self.logger.info("✅ Universal Matrix Simulation Pipe initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  Matrix simulation pipe not available: {e}")
            self.matrix_pipe = None

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence and pipe through matrix simulations.

        Supports multiple content types:
        - Subprocess command (list of strings)
        - File path (Path or str)
        - Queue object
        - Iterator
        - SYPHON data (from other extractors)
        """
        if not self.matrix_pipe:
            return ExtractionResult(
                success=False,
                error="Matrix simulation pipe not available"
            )

        try:
            from universal_matrix_simulation_pipe import (
                SubprocessDataSource,
                FileDataSource,
                QueueDataSource,
                IteratorDataSource
            )

            # Determine data source type from content
            data_source = None
            source_name = metadata.get("source_name", "unknown")

            # Subprocess command
            if isinstance(content, list) and len(content) > 0:
                data_source = SubprocessDataSource(content, source_name)
                self.logger.info(f"📥 Setting up subprocess source: {content[0]}")

            # File path
            elif isinstance(content, (str, Path)):
                file_path = Path(content)
                if file_path.exists():
                    format_type = metadata.get("format", "line")
                    data_source = FileDataSource(file_path, source_name, format_type)
                    self.logger.info(f"📥 Setting up file source: {file_path}")
                else:
                    return ExtractionResult(
                        success=False,
                        error=f"File not found: {file_path}"
                    )

            # Queue
            elif hasattr(content, 'get') and hasattr(content, 'put'):
                data_source = QueueDataSource(content, source_name)
                self.logger.info(f"📥 Setting up queue source: {source_name}")

            # Iterator
            elif hasattr(content, '__iter__') and not isinstance(content, (str, bytes)):
                parser = metadata.get("parser")
                data_source = IteratorDataSource(content, source_name, parser)
                self.logger.info(f"📥 Setting up iterator source: {source_name}")

            # SYPHON data (from other extractors)
            elif isinstance(content, dict) and content.get("source_type"):
                # Convert SYPHON data to iterator
                def syphon_iterator():
                    yield {
                        'timestamp': content.get('extracted_at', datetime.now().isoformat()),
                        'data': content,
                        'source': content.get('source_type', 'syphon')
                    }
                data_source = IteratorDataSource(syphon_iterator(), source_name)
                self.logger.info(f"📥 Setting up SYPHON data source: {source_name}")

            else:
                return ExtractionResult(
                    success=False,
                    error=f"Unsupported content type: {type(content)}"
                )

            # Set data source and start pipeline
            self.matrix_pipe.set_data_source(data_source)

            # Set custom parser if provided
            if "parser" in metadata and callable(metadata["parser"]):
                self.matrix_pipe.set_data_parser(metadata["parser"])

            # Start pipeline in background thread
            pipe_thread = threading.Thread(
                target=self.matrix_pipe.run,
                args=(metadata.get("duration"),),
                daemon=True
            )
            pipe_thread.start()

            # Extract intelligence from content (for SYPHON)
            content_str = str(content) if not isinstance(content, str) else content
            actionable_items = self._extract_actionable_items(content_str)
            tasks = self._extract_tasks(content_str)
            decisions = self._extract_decisions(content_str)
            intelligence = self._extract_intelligence(content_str)

            syphon_data = SyphonData(
                data_id=f"matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.MATRIX,
                source_id=source_name,
                content=content_str[:1000],  # Truncate for storage
                metadata={
                    **metadata,
                    "matrix_pipe_active": True,
                    "matrix_a_config": self.matrix_pipe.matrix_a_config,
                    "matrix_b_config": self.matrix_pipe.matrix_b_config,
                    "r5_integration": self.matrix_pipe.r5_system is not None
                },
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            self.logger.info(f"✅ Matrix simulation pipe started for: {source_name}")

            return ExtractionResult(
                success=True,
                data=syphon_data,
                metadata={
                    "matrix_pipe": self.matrix_pipe,
                    "thread": pipe_thread
                }
            )

        except Exception as e:
            self.logger.error(f"Matrix extraction failed: {e}", exc_info=True)
            return ExtractionResult(success=False, error=str(e))

    def stop_pipeline(self):
        """Stop the matrix simulation pipeline"""
        if self.matrix_pipe:
            self.matrix_pipe.stop()
