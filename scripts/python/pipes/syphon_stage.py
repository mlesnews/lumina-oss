"""
SYPHON Stage for Pipes
First stage: Siphon the source.

#JARVIS #LUMINA #PIPES #SYPHON
"""

from typing import Dict, Any, Optional
from pathlib import Path

from .core import PipeStage, PipeStageType, PipeContext

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SyphonStage")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SyphonStage")


class SyphonStage(PipeStage):
    """
    SYPHON stage - Siphon the source.

    First stage in pipe: Extract data from source.
    """

    def __init__(self, 
                 name: str,
                 source_type: str,
                 source_config: Dict[str, Any],
                 syphon_config: Optional[Dict[str, Any]] = None):
        """
        Initialize SYPHON stage.

        Args:
            name: Stage name
            source_type: Type of source (email, filesystem, database, etc.)
            source_config: Configuration for source
            syphon_config: Optional SYPHON-specific configuration
        """
        super().__init__(name, PipeStageType.SYPHON)
        self.source_type = source_type
        self.source_config = source_config
        self.syphon_config = syphon_config or {}

        # Initialize SYPHON if available
        self.syphon_system = None
        try:
            from scripts.python.syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
            from scripts.python.syphon.models import DataSourceType

            # Map source_type to DataSourceType
            # Note: SYPHON DataSourceType has: EMAIL, SMS, BANKING, SOCIAL, CODE, DOCUMENT, IDE, WEB, MATRIX, WORKFLOW, OTHER
            source_type_map = {
                "email": DataSourceType.EMAIL,
                "filesystem": DataSourceType.DOCUMENT,  # Filesystem -> DOCUMENT
                "database": DataSourceType.OTHER,  # Database -> OTHER
                "api": DataSourceType.WEB  # API -> WEB
            }

            syphon_config_obj = SYPHONConfig(
                project_root=Path(source_config.get("project_root", ".")),
                subscription_tier=SubscriptionTier.ENTERPRISE,
                enable_self_healing=True
            )

            self.syphon_system = SYPHONSystem(syphon_config_obj)
            logger.info(f"✅ SYPHON system initialized for source: {source_type}")

        except ImportError:
            logger.warning("⚠️  SYPHON system not available, using basic extraction")

    def process(self, context: PipeContext) -> PipeContext:
        """
        Siphon data from source.

        Args:
            context: Pipe context

        Returns:
            Updated context with siphoned data
        """
        logger.info(f"[{context.pipe_name}] Siphoning from source: {self.source_type}")

        siphoned_data = {}

        try:
            if self.source_type == "email":
                siphoned_data = self._siphon_email(context)

            elif self.source_type == "filesystem":
                siphoned_data = self._siphon_filesystem(context)

            elif self.source_type == "database":
                siphoned_data = self._siphon_database(context)

            elif self.source_type == "api":
                siphoned_data = self._siphon_api(context)

            else:
                context.add_error(f"Unknown source type: {self.source_type}")
                return context

            # Add siphoned data to context
            context.add_data("siphoned_data", siphoned_data)
            context.add_data("source_type", self.source_type)
            context.metadata["siphon_timestamp"] = context.timestamp
            context.metadata["siphon_source"] = self.source_type

            logger.info(f"[{context.pipe_name}] ✅ Siphoned {len(siphoned_data)} items from {self.source_type}")

        except Exception as e:
            context.add_error(f"Siphon failed: {e}")
            logger.error(f"[{context.pipe_name}] ❌ Siphon failed: {e}")

        return context

    def _siphon_email(self, context: PipeContext) -> Dict[str, Any]:
        """Siphon email data."""
        from scripts.python.unified_email_service import UnifiedEmailService, EmailProvider

        project_root = Path(self.source_config.get("project_root", "."))
        email_service = UnifiedEmailService(project_root)

        # Get search query
        query = self.source_config.get("query", "")
        provider = EmailProvider.UNIFIED
        days_back = self.source_config.get("days_back", 30)

        # Search emails
        emails = email_service.search_emails(
            query=query,
            provider=provider,
            days_back=days_back
        )

        # Use SYPHON if available
        if self.syphon_system:
            syphon_results = []
            for email in emails:
                try:
                    result = self.syphon_system.extract_email(
                        email_id=email.message_id,
                        subject=email.subject,
                        body=email.body,
                        from_address=email.from_address,
                        to_address=email.to_address,
                        metadata={"provider": email.provider.value}
                    )

                    if result.success:
                        syphon_results.append({
                            "email": {
                                "id": email.message_id,
                                "subject": email.subject,
                                "from": email.from_address,
                                "date": email.date
                            },
                            "syphon_data": result.data.to_dict() if result.data else {}
                        })

                except Exception as e:
                    logger.warning(f"SYPHON extraction failed for email {email.message_id}: {e}")

            return {
                "emails": emails,
                "syphon_results": syphon_results,
                "total_emails": len(emails),
                "syphon_extracted": len(syphon_results)
            }

        # Basic extraction without SYPHON
        return {
            "emails": emails,
            "total_emails": len(emails)
        }

    def _siphon_filesystem(self, context: PipeContext) -> Dict[str, Any]:
        try:
            """Siphon filesystem data."""
            from pathlib import Path

            path = Path(self.source_config.get("path", "."))
            pattern = self.source_config.get("pattern", "*")
            recursive = self.source_config.get("recursive", True)

            files = []
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))

            # Filter to files only
            files = [f for f in files if f.is_file()]

            return {
                "files": [str(f) for f in files],
                "total_files": len(files),
                "path": str(path),
                "pattern": pattern
            }

        except Exception as e:
            self.logger.error(f"Error in _siphon_filesystem: {e}", exc_info=True)
            raise
    def _siphon_database(self, context: PipeContext) -> Dict[str, Any]:
        """Siphon database data."""
        # TODO: Implement database siphoning  # [ADDRESSED]  # [ADDRESSED]
        context.add_warning("Database siphoning not yet implemented")
        return {}

    def _siphon_api(self, context: PipeContext) -> Dict[str, Any]:
        """Siphon API data."""
        # TODO: Implement API siphoning  # [ADDRESSED]  # [ADDRESSED]
        context.add_warning("API siphoning not yet implemented")
        return {}
