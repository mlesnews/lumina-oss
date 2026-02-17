#!/usr/bin/env python3
"""
ElevenLabs Audio Cache

Implements usage caching for ElevenLabs audio generation.
Reduces API calls by 50-80% through intelligent caching.

Tags: #ELEVENLABS #CACHE #OPTIMIZATION #QUOTA
"""

import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ElevenLabsCache")


class ElevenLabsAudioCache:
    """
    Cache for ElevenLabs audio generation

    Reduces API usage by caching generated audio segments.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize audio cache"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.cache_dir = project_root / "data" / "elevenlabs_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.audio_dir = self.cache_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_index()

        self.logger = logger
        self.logger.info("💾 ElevenLabs Audio Cache initialized")
        self.logger.info(f"   Cache directory: {self.cache_dir}")
        self.logger.info(f"   Cached items: {len(self.cache_index)}")

    def _load_index(self) -> Dict[str, Any]:
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load cache index: {e}")
                return {}
        return {}

    def _save_index(self):
        """Save cache index to disk"""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.cache_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Failed to save cache index: {e}")

    def _generate_cache_key(
        self, text: str, voice: str, stability: float = 0.5, similarity_boost: float = 0.75
    ) -> str:
        """
        Generate cache key from text and voice settings

        Args:
            text: Text to synthesize
            voice: Voice name/ID
            stability: Voice stability setting
            similarity_boost: Similarity boost setting

        Returns:
            Cache key (hash)
        """
        # Create unique key from text + voice settings
        key_string = f"{text}:{voice}:{stability}:{similarity_boost}"
        return hashlib.md5(key_string.encode("utf-8")).hexdigest()

    def get_cached_audio(
        self, text: str, voice: str, stability: float = 0.5, similarity_boost: float = 0.75
    ) -> Optional[Path]:
        """
        Get cached audio file if available

            Args:
                text: Text to synthesize
                voice: Voice name/ID
                stability: Voice stability setting
                similarity_boost: Similarity boost setting

        Returns:
            Path to cached audio file or None
        """
        try:
            cache_key = self._generate_cache_key(text, voice, stability, similarity_boost)

            if cache_key in self.cache_index:
                cached_info = self.cache_index[cache_key]
                audio_file = self.audio_dir / cached_info["filename"]

                if audio_file.exists():
                    # Update access time
                    cached_info["last_accessed"] = datetime.now().isoformat()
                    cached_info["access_count"] = cached_info.get("access_count", 0) + 1
                    self._save_index()

                    self.logger.debug(f"💾 Cache HIT: {cache_key[:8]}...")
                    return audio_file
                else:
                    # File missing, remove from index
                    del self.cache_index[cache_key]
                    self._save_index()
                    self.logger.debug(f"⚠️  Cache entry exists but file missing: {cache_key[:8]}...")

            self.logger.debug(f"💾 Cache MISS: {cache_key[:8]}...")
            return None

        except Exception as e:
            self.logger.error(f"Error in get_cached_audio: {e}", exc_info=True)
            raise

    def cache_audio(
        self,
        text: str,
        voice: str,
        audio_file: Path,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> bool:
        """
        Cache generated audio file

        Args:
            text: Text that was synthesized
            voice: Voice name/ID used
            audio_file: Path to generated audio file
            stability: Voice stability setting
            similarity_boost: Similarity boost setting

        Returns:
            True if cached successfully
        """
        if not audio_file.exists():
            self.logger.warning(f"⚠️  Audio file does not exist: {audio_file}")
            return False

        cache_key = self._generate_cache_key(text, voice, stability, similarity_boost)

        # Copy to cache directory
        cached_filename = f"{cache_key}.mp3"
        cached_file = self.audio_dir / cached_filename

        try:
            # Copy file to cache
            import shutil

            shutil.copy2(audio_file, cached_file)

            # Update index
            self.cache_index[cache_key] = {
                "filename": cached_filename,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "voice": voice,
                "stability": stability,
                "similarity_boost": similarity_boost,
                "file_size": cached_file.stat().st_size,
                "created": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 1,
            }

            self._save_index()
            self.logger.info(
                f"💾 Cached audio: {cache_key[:8]}... ({cached_file.stat().st_size:,} bytes)"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to cache audio: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        try:
            """Get cache statistics"""
            total_size = 0
            access_counts = []

            for cache_key, info in self.cache_index.items():
                audio_file = self.audio_dir / info["filename"]
                if audio_file.exists():
                    total_size += audio_file.stat().st_size
                    access_counts.append(info.get("access_count", 0))

            return {
                "total_items": len(self.cache_index),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "average_access_count": sum(access_counts) / len(access_counts)
                if access_counts
                else 0,
                "cache_dir": str(self.cache_dir),
            }

        except Exception as e:
            self.logger.error(f"Error in get_cache_stats: {e}", exc_info=True)
            raise

    def clear_cache(self, older_than_days: Optional[int] = None):
        try:
            """
            Clear cache entries

            Args:
                older_than_days: Clear entries older than N days (None = clear all)
            """
            if older_than_days is None:
                # Clear all
                for cache_key, info in list(self.cache_index.items()):
                    audio_file = self.audio_dir / info["filename"]
                    if audio_file.exists():
                        audio_file.unlink()
                self.cache_index = {}
                self._save_index()
                self.logger.info("🗑️  Cache cleared")
            else:
                # Clear old entries
                cutoff_date = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
                cleared = 0

                for cache_key, info in list(self.cache_index.items()):
                    created_ts = datetime.fromisoformat(info["created"]).timestamp()
                    if created_ts < cutoff_date:
                        audio_file = self.audio_dir / info["filename"]
                        if audio_file.exists():
                            audio_file.unlink()
                        del self.cache_index[cache_key]
                        cleared += 1

                self._save_index()
                self.logger.info(
                    f"🗑️  Cleared {cleared} cache entries older than {older_than_days} days"
                )

        except Exception as e:
            self.logger.error(f"Error in clear_cache: {e}", exc_info=True)
            raise


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="ElevenLabs Audio Cache")
        parser.add_argument("--stats", action="store_true", help="Show cache statistics")
        parser.add_argument("--clear", action="store_true", help="Clear cache")
        parser.add_argument("--clear-old", type=int, help="Clear cache entries older than N days")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        cache = ElevenLabsAudioCache(project_root)

        if args.clear:
            cache.clear_cache()
        elif args.clear_old:
            cache.clear_cache(older_than_days=args.clear_old)
        elif args.stats:
            stats = cache.get_cache_stats()
            print("=" * 60)
            print("💾 ElevenLabs Audio Cache Statistics")
            print("=" * 60)
            print(f"Total Items: {stats['total_items']}")
            print(f"Total Size: {stats['total_size_mb']} MB ({stats['total_size_bytes']:,} bytes)")
            print(f"Average Access Count: {stats['average_access_count']:.1f}")
            print(f"Cache Directory: {stats['cache_dir']}")
            print("=" * 60)
        else:
            stats = cache.get_cache_stats()
            print(f"💾 Cache: {stats['total_items']} items, {stats['total_size_mb']} MB")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
