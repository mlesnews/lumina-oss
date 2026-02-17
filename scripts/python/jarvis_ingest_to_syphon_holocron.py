#!/usr/bin/env python3
"""
JARVIS Ingest to SYPHON and Holocron
Ingests documentation into SYPHON for tracking and Holocron for archival

Tags: #JARVIS #SYPHON #HOLOCRON #JEDIARCHIVES @JARVIS @SYPHON @HOLOCRON
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISIngestToSYPHONHolocron")


def ingest_to_syphon(document_path: Path, metadata: Dict[str, Any]) -> bool:
    """Ingest document into SYPHON intelligence extraction system"""
    try:
        from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
        from syphon.models import DataSourceType

        logger.info(f"📥 Ingesting to SYPHON: {document_path.name}")

        # Read document content
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Initialize SYPHON
        project_root = Path(__file__).parent.parent.parent
        config = SYPHONConfig(
            project_root=project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE,
            enable_self_healing=True
        )
        syphon = SYPHONSystem(config)

        # Ingest document
        result = syphon.extract(
            source_type=DataSourceType.DOCUMENTATION,
            content=content,
            metadata={
                **metadata,
                'source_file': str(document_path),
                'ingested_at': datetime.now().isoformat(),
                'ingested_by': 'JARVIS'
            }
        )

        if result.success:
            logger.info(f"   ✅ SYPHON ingested: {result.extracted_count if hasattr(result, 'extracted_count') else 0} items extracted")
            return True
        else:
            logger.warning(f"   ⚠️  SYPHON ingestion failed: {result.error}")
            return False

    except ImportError:
        logger.debug("SYPHON not available")
        return False
    except Exception as e:
        logger.error(f"SYPHON ingestion error: {e}")
        return False


def ingest_to_holocron(document_path: Path, metadata: Dict[str, Any]) -> bool:
    """Ingest document into Holocron archive"""
    try:
        project_root = Path(__file__).parent.parent.parent
        holocron_dir = project_root / "data" / "holocron"
        holocron_dir.mkdir(parents=True, exist_ok=True)

        # Create entry
        entry_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{document_path.stem}"
        entry_file = holocron_dir / f"{entry_id}.json"

        # Read document content
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()

        entry = {
            'entry_id': entry_id,
            'timestamp': datetime.now().isoformat(),
            'source_file': str(document_path),
            'content': content,
            'metadata': metadata,
            'type': 'documentation',
            'categories': metadata.get('tags', []),
            'tags': metadata.get('tags', [])
        }

        # Save entry
        with open(entry_file, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)

        # Update Holocron index
        index_file = holocron_dir / "HOLOCRON_INDEX.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {'entries': [], 'last_updated': None}

        index['entries'].append({
            'entry_id': entry_id,
            'timestamp': entry['timestamp'],
            'source_file': str(document_path),
            'type': 'documentation',
            'categories': metadata.get('tags', [])
        })
        index['last_updated'] = datetime.now().isoformat()

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        logger.info(f"   ✅ Holocron archived: {entry_id}")
        return True

    except Exception as e:
        logger.error(f"Holocron ingestion error: {e}")
        return False


def ingest_to_jedi_archives(document_path: Path, metadata: Dict[str, Any]) -> bool:
    """Ingest document into Jedi Archives database"""
    try:
        project_root = Path(__file__).parent.parent.parent
        jedi_archives_dir = project_root / "data" / "jedi_archives"
        jedi_archives_dir.mkdir(parents=True, exist_ok=True)

        # Create archive entry
        archive_id = f"{datetime.now().strftime('%Y%m%d')}_{document_path.stem}"
        archive_file = jedi_archives_dir / f"{archive_id}.json"

        # Read document content
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()

        archive_entry = {
            'archive_id': archive_id,
            'timestamp': datetime.now().isoformat(),
            'source_file': str(document_path),
            'content': content,
            'metadata': metadata,
            'library_category': metadata.get('library_category', 'general'),
            'curated': metadata.get('curated', False),
            'youtube_content': metadata.get('youtube_content', False)
        }

        # Save archive entry
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archive_entry, f, indent=2, ensure_ascii=False)

        logger.info(f"   ✅ Jedi Archives stored: {archive_id}")
        return True

    except Exception as e:
        logger.error(f"Jedi Archives ingestion error: {e}")
        return False


def main():
    try:
        """Main ingestion function"""
        import argparse

        parser = argparse.ArgumentParser(description="Ingest document to SYPHON and Holocron")
        parser.add_argument("document", type=str, help="Path to document to ingest")
        parser.add_argument("--helpdesk-ticket", type=str, help="Helpdesk ticket ID (PM123456789)")
        parser.add_argument("--github-pr", type=str, help="GitHub PR number")
        parser.add_argument("--tags", type=str, nargs="+", help="Tags for categorization")
        parser.add_argument("--library-category", type=str, help="Library category")
        parser.add_argument("--curated", action="store_true", help="Mark as curated content")
        parser.add_argument("--youtube-content", action="store_true", help="Mark as YouTube content source")

        args = parser.parse_args()

        document_path = Path(args.document)
        if not document_path.exists():
            logger.error(f"Document not found: {document_path}")
            return 1

        logger.info("=" * 80)
        logger.info("📚 INGESTING TO SYPHON & HOLOCRON")
        logger.info("=" * 80)
        logger.info("")

        # Build metadata
        metadata = {
            'helpdesk_ticket': args.helpdesk_ticket,
            'github_pr': args.github_pr,
            'tags': args.tags or [],
            'library_category': args.library_category,
            'curated': args.curated,
            'youtube_content': args.youtube_content
        }

        # Ingest to all systems
        results = {
            'syphon': ingest_to_syphon(document_path, metadata),
            'holocron': ingest_to_holocron(document_path, metadata),
            'jedi_archives': ingest_to_jedi_archives(document_path, metadata)
        }

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ INGESTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   SYPHON: {'✅' if results['syphon'] else '❌'}")
        logger.info(f"   Holocron: {'✅' if results['holocron'] else '❌'}")
        logger.info(f"   Jedi Archives: {'✅' if results['jedi_archives'] else '❌'}")
        logger.info("")

        return 0 if all(results.values()) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())