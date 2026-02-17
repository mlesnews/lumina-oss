#!/usr/bin/env python3
"""
Download Router
Routes downloads to appropriate cloud storage via NAS DSM Cloud Sync package

Uses existing DSM Cloud Sync package on NAS to aggregate cloud storage providers
and intelligently routes downloads based on file type, size, source, and keywords.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DownloadRouter")

# Import NAS integration
try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_INTEGRATION_AVAILABLE = True
except ImportError:
    NAS_INTEGRATION_AVAILABLE = False
    logger.warning("NAS integration not available")

# Import IDM integration
try:
    from idm_kaiju_integration import IDMKaijuIntegration
    IDM_AVAILABLE = True
except ImportError:
    IDM_AVAILABLE = False
    logger.warning("IDM integration not available")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RoutingDecision:
    """Download routing decision"""
    destination: str  # Provider name (dropbox, onedrive, etc.)
    destination_path: Path
    provider: Dict[str, Any]
    reason: str
    priority: int


class DownloadRouter:
    """
    Routes downloads to cloud storage providers via NAS DSM Cloud Sync

    Uses NAS as cloud aggregator - downloads go to NAS Cloud Sync paths,
    which automatically sync to configured cloud providers (Dropbox, OneDrive, etc.)
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize download router

        Args:
            config_path: Path to routing configuration
        """
        self.config_path = config_path or project_root / "config" / "download_routing_config.json"
        self.config: Dict[str, Any] = {}

        # NAS integration for cloud sync paths
        self.nas_integration: Optional[NASAzureVaultIntegration] = None

        # IDM integration
        self.idm: Optional[IDMKaijuIntegration] = None

        self._load_config()
        self._initialize_integrations()

    def _load_config(self) -> None:
        """Load routing configuration"""
        if not self.config_path.exists():
            logger.warning(f"Routing config not found: {self.config_path}")
            self.config = {}
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"Loaded routing config from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load routing config: {e}")
            self.config = {}

    def _initialize_integrations(self) -> None:
        """Initialize NAS and IDM integrations"""
        nas_config = self.config.get("nas_cloud_aggregator", {})

        # Initialize NAS integration for Cloud Sync paths
        if NAS_INTEGRATION_AVAILABLE and nas_config.get("enabled", True):
            try:
                self.nas_integration = NASAzureVaultIntegration(
                    nas_ip=nas_config.get("nas_host", "<NAS_PRIMARY_IP>"),
                    nas_port=5001
                )
                logger.info("NAS integration initialized")
            except Exception as e:
                logger.warning(f"NAS integration failed: {e}")

        # Initialize IDM integration
        if IDM_AVAILABLE:
            try:
                self.idm = IDMKaijuIntegration()
                if self.idm.is_available():
                    logger.info("IDM integration available")
            except Exception as e:
                logger.warning(f"IDM integration failed: {e}")

    def _get_file_type(self, file_path: Path) -> str:
        """
        Determine file type category

        Args:
            file_path: Path to file

        Returns:
            File type category
        """
        ext = file_path.suffix.lower()

        # Document types
        if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf']:
            return "documents"

        # Media types
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
            return "media"

        # Video types
        if ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
            return "videos"

        # Large files
        if ext in ['.gguf', '.bin', '.iso', '.img', '.dmg']:
            return "large_files"

        return "general"

    def _get_size_category(self, file_size_bytes: int) -> str:
        """Get file size category"""
        size_mb = file_size_bytes / (1024 * 1024)
        if size_mb < 10:
            return "small"
        elif size_mb < 100:
            return "medium"
        elif size_mb < 1000:
            return "large"
        else:
            return "very_large"

    def _find_provider(self, file_path: Path, source: Optional[str] = None, keywords: Optional[List[str]] = None) -> Optional[RoutingDecision]:
        try:
            """
            Find appropriate cloud storage provider for file

            Args:
                file_path: Path to file
                source: Download source (tv_monitor, youtube, idm_general, browser, etc.)
                keywords: Optional keywords from context

            Returns:
                RoutingDecision or None
            """
            providers = self.config.get("cloud_storage_providers", {})
            routing_rules = self.config.get("routing_rules", {})

            file_type = self._get_file_type(file_path)
            file_size = file_path.stat().st_size if file_path.exists() else 0
            size_category = self._get_size_category(file_size)
            ext = file_path.suffix.lower()

            # Check routing rules (priority order)

            # 1. By source
            if source and source in routing_rules.get("by_source", {}):
                provider_name = routing_rules["by_source"][source]
                if provider_name in providers and providers[provider_name].get("enabled", False):
                    provider = providers[provider_name]
                    destination_path = self._get_provider_path(provider, file_path)
                    if destination_path:
                        return RoutingDecision(
                            destination=provider_name,
                            destination_path=destination_path,
                            provider=provider,
                            reason=f"Source-based routing: {source}",
                            priority=provider.get("priority", 99)
                        )

            # 2. By keywords
            if keywords:
                for keyword in keywords:
                    if keyword in routing_rules.get("by_keywords", {}):
                        provider_name = routing_rules["by_keywords"][keyword]
                        if provider_name in providers and providers[provider_name].get("enabled", False):
                            provider = providers[provider_name]
                            destination_path = self._get_provider_path(provider, file_path)
                            if destination_path:
                                return RoutingDecision(
                                    destination=provider_name,
                                    destination_path=destination_path,
                                    provider=provider,
                                    reason=f"Keyword-based routing: {keyword}",
                                    priority=provider.get("priority", 99)
                                )

            # 3. By file type
            if file_type in routing_rules.get("by_file_type", {}):
                provider_name = routing_rules["by_file_type"][file_type]
                if provider_name in providers and providers[provider_name].get("enabled", False):
                    provider = providers[provider_name]
                    destination_path = self._get_provider_path(provider, file_path)
                    if destination_path:
                        return RoutingDecision(
                            destination=provider_name,
                            destination_path=destination_path,
                            provider=provider,
                            reason=f"File type routing: {file_type}",
                            priority=provider.get("priority", 99)
                        )

            # 4. By size
            if size_category in routing_rules.get("by_size", {}):
                provider_name = routing_rules["by_size"][size_category]
                if provider_name in providers and providers[provider_name].get("enabled", False):
                    provider = providers[provider_name]
                    destination_path = self._get_provider_path(provider, file_path)
                    if destination_path:
                        return RoutingDecision(
                            destination=provider_name,
                            destination_path=destination_path,
                            provider=provider,
                            reason=f"Size-based routing: {size_category}",
                            priority=provider.get("priority", 99)
                        )

            # 5. Check provider file extensions
            for provider_name, provider in providers.items():
                if not provider.get("enabled", False):
                    continue

                provider_exts = provider.get("file_extensions", [])
                if ext in provider_exts:
                    destination_path = self._get_provider_path(provider, file_path)
                    if destination_path:
                        # Check file size limit
                        max_size_mb = provider.get("max_file_size_mb", 999999)
                        file_size_mb = file_size / (1024 * 1024)
                        if file_size_mb <= max_size_mb:
                            return RoutingDecision(
                                destination=provider_name,
                                destination_path=destination_path,
                                provider=provider,
                                reason=f"File extension match: {ext}",
                                priority=provider.get("priority", 99)
                            )

            # 6. Default to configured default destination
            nas_config = self.config.get("nas_cloud_aggregator", {})
            default_dest = nas_config.get("default_destination", "dropbox")
            if default_dest in providers and providers[default_dest].get("enabled", False):
                provider = providers[default_dest]
                destination_path = self._get_provider_path(provider, file_path)
                if destination_path:
                    return RoutingDecision(
                        destination=default_dest,
                        destination_path=destination_path,
                        provider=provider,
                        reason="Default destination",
                        priority=provider.get("priority", 99)
                    )

            return None

        except Exception as e:
            self.logger.error(f"Error in _find_provider: {e}", exc_info=True)
            raise
    def _get_provider_path(self, provider: Dict[str, Any], file_path: Path) -> Optional[Path]:
        try:
            """
            Get destination path for provider

            Uses NAS Cloud Sync path if available, otherwise local path

            Args:
                provider: Provider configuration
                file_path: Source file path

            Returns:
                Destination path or None
            """
            # Prefer NAS Cloud Sync path (NAS acts as aggregator)
            nas_sync_path = provider.get("nas_sync_path")
            if nas_sync_path:
                # Check if NAS path is accessible
                nas_host = self.config.get('nas_cloud_aggregator', {}).get('nas_host', '<NAS_PRIMARY_IP>')
                sync_path_win = nas_sync_path.lstrip('/').replace('/', '\\')
                nas_path = Path(f"\\\\{nas_host}") / sync_path_win
                if nas_path.exists() or self._check_network_path(nas_path):
                    return nas_path / file_path.name

            # Fallback to local path
            local_path = provider.get("local_path")
            if local_path:
                local_path_expanded = Path(local_path).expanduser()
                if local_path_expanded.exists():
                    return local_path_expanded / file_path.name

            # Fallback to mapped drive
            mapped_drive = provider.get("mapped_drive")
            if mapped_drive:
                mapped_path = Path(mapped_drive)
                if mapped_path.exists():
                    return mapped_path / file_path.name

            # Fallback to network path
            network_path = provider.get("network_path")
            if network_path:
                net_path = Path(network_path)
                if net_path.exists() or self._check_network_path(net_path):
                    return net_path / file_path.name

            return None

        except Exception as e:
            self.logger.error(f"Error in _get_provider_path: {e}", exc_info=True)
            raise
    def _check_network_path(self, path: Path) -> bool:
        """Check if network path is accessible"""
        try:
            if str(path).startswith("\\\\") and path.exists():
                return True
        except (OSError, PermissionError):
            pass
        return False

    def route_download(
        self,
        file_path: Path,
        source: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        move: bool = True
    ) -> Optional[RoutingDecision]:
        """
        Route download to appropriate cloud storage provider

        Args:
            file_path: Path to downloaded file
            source: Download source (tv_monitor, youtube, idm_general, browser, etc.)
            keywords: Optional keywords from context
            move: If True, move file; if False, copy file

        Returns:
            RoutingDecision if successful, None otherwise
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        # Find appropriate provider
        decision = self._find_provider(file_path, source=source, keywords=keywords)
        if not decision:
            logger.warning(f"Could not determine routing for {file_path}")
            return None

        logger.info(f"Routing {file_path.name} to {decision.destination}: {decision.reason}")

        # Ensure destination directory exists
        try:
            decision.destination_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create destination directory: {e}")
            return None

        # Move or copy file
        try:
            if move:
                shutil.move(str(file_path), str(decision.destination_path))
                logger.info(f"✓ Moved to {decision.destination_path}")
            else:
                shutil.copy2(str(file_path), str(decision.destination_path))
                logger.info(f"✓ Copied to {decision.destination_path}")

            return decision
        except Exception as e:
            logger.error(f"Failed to route file: {e}")
            return None

    def route_download_via_idm(
        self,
        url: str,
        filename: Optional[str] = None,
        source: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> bool:
        """
        Route download via IDM to appropriate cloud storage

        Downloads to NAS Cloud Sync path, which automatically syncs to cloud providers

        Args:
            url: URL to download
            filename: Optional filename
            source: Download source
            keywords: Optional keywords

        Returns:
            True if download was queued successfully
        """
        if not self.idm or not self.idm.is_available():
            logger.error("IDM not available")
            return False

        # Create temporary file path to determine routing
        temp_file = Path(filename) if filename else Path(url.split('/')[-1].split('?')[0])

        # Find routing decision
        decision = self._find_provider(temp_file, source=source, keywords=keywords)
        if not decision:
            logger.warning(f"Could not determine routing for {url}, using default")
            return False

        # Download directly to destination via IDM
        logger.info(f"Downloading {url} to {decision.destination} via IDM")
        success = self.idm.download(
            url=url,
            filename=temp_file.name,
            destination=decision.destination_path.parent,
            description=f"{source or 'download'} -> {decision.destination}"
        )

        return success


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Download Router")
        parser.add_argument("file", help="File to route")
        parser.add_argument("--source", help="Download source")
        parser.add_argument("--keywords", nargs="+", help="Keywords")
        parser.add_argument("--copy", action="store_true", help="Copy instead of move")
        parser.add_argument("--idm", help="Download URL via IDM")

        args = parser.parse_args()

        router = DownloadRouter()

        if args.idm:
            success = router.route_download_via_idm(
                url=args.idm,
                filename=args.file,
                source=args.source,
                keywords=args.keywords
            )
            sys.exit(0 if success else 1)
        else:
            file_path = Path(args.file)
            decision = router.route_download(
                file_path=file_path,
                source=args.source,
                keywords=args.keywords,
                move=not args.copy
            )

            if decision:
                print(f"✓ Routed to {decision.destination}: {decision.destination_path}")
                print(f"  Reason: {decision.reason}")
                sys.exit(0)
            else:
                print("✗ Routing failed")
                sys.exit(1)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()