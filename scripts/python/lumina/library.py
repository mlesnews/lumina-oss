#!/usr/bin/env python3
"""
Lumina Library - Our Personal Jedi Archives

"Always start with @peak, begin with the Lumina Library, our very own personal #JediArchives"

The Lumina Library is our personal Jedi Archives - containing all knowledge,
patterns, wisdom, and crystallized learnings from our journey.

Tags: #JEDI_ARCHIVES #LUMINA_LIBRARY #KNOWLEDGE #WISDOM @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaLibrary")


class LuminaLibrary:
    """
    Lumina Library - Our Personal Jedi Archives

    Just as the Jedi Archives on Coruscant contained all knowledge of the galaxy,
    the Lumina Library contains all knowledge of our system, our learnings,
    our patterns, our wisdom.

    Access through Lumina Peak:
        from lumina.peak import LuminaPeak
        lumina = LuminaPeak()
        library = lumina.digest  # The Jedi Archives
    """

    def __init__(self, digest=None):
        """
        Initialize Lumina Library (Jedi Archives).

        Args:
            digest: LuminaDigest instance (if None, will be lazy-loaded)
        """
        self._digest = digest
        logger.info("📚 Initializing Lumina Library (Jedi Archives)...")

    @property
    def digest(self):
        """Lazy-load digest if not provided"""
        if self._digest is None:
            try:
                from .digest import LuminaDigest
                self._digest = LuminaDigest()
            except ImportError:
                try:
                    from lumina.digest import LuminaDigest
                    self._digest = LuminaDigest()
                except ImportError:
                    logger.warning("Lumina Digest not available")
                    return None
        return self._digest

    def knowledge(self, topic: str) -> Dict[str, Any]:
        """
        Search the Jedi Archives for knowledge.

        Args:
            topic: Topic to search for

        Returns:
            Knowledge from the Archives
        """
        if not self.digest:
            return {'error': 'Jedi Archives (Digest) not available'}

        return self.digest.knowledge(topic)

    def weekly_digest(self) -> Dict[str, Any]:
        """
        Generate weekly digest from the Archives.

        Returns:
            Weekly summary of Archives content
        """
        if not self.digest:
            return {'error': 'Jedi Archives (Digest) not available'}

        return self.digest.generate_weekly_digest()

    def topic_digest(self, topic: str) -> Dict[str, Any]:
        """
        Generate topic-focused digest from the Archives.

        Args:
            topic: Topic to focus on

        Returns:
            Topic-focused summary
        """
        if not self.digest:
            return {'error': 'Jedi Archives (Digest) not available'}

        return self.digest.generate_topic_digest(topic)

    def quick_reference(self, topic: str) -> Dict[str, Any]:
        """
        Get quick reference from the Archives.

        Args:
            topic: Topic to reference

        Returns:
            Quick reference guide
        """
        if not self.digest:
            return {'error': 'Jedi Archives (Digest) not available'}

        return self.digest.generate_quick_reference(topic)

    def search(self, query: str) -> Dict[str, Any]:
        """
        Search the Archives.

        Args:
            query: Search query

        Returns:
            Search results from Archives
        """
        if not self.digest:
            return {'error': 'Jedi Archives (Digest) not available'}

        # Use knowledge method for search
        return self.digest.knowledge(query)

    def get_status(self) -> Dict[str, Any]:
        """Get status of the Jedi Archives"""
        if not self.digest:
            return {
                'available': False,
                'error': 'Jedi Archives (Digest) not available'
            }

        return {
            'available': True,
            'holocron_entries': len(self.digest.holocron_entries) if hasattr(self.digest, 'holocron_entries') else 0,
            'documentation_items': self.digest.documentation_count if hasattr(self.digest, 'documentation_count') else 0,
            'description': 'Our personal Jedi Archives - all knowledge, patterns, and wisdom'
        }


def main():
    """Example usage - Accessing the Jedi Archives"""
    print("=" * 80)
    print("📚 LUMINA LIBRARY - Our Personal Jedi Archives")
    print("=" * 80)
    print()

    # Access through Peak (recommended)
    try:
        from lumina.peak import LuminaPeak
        lumina = LuminaPeak()
        library = lumina.digest  # The Jedi Archives

        print("ACCESSING THROUGH PEAK:")
        print("-" * 80)
        print("✅ Gateway: Lumina Peak")
        print("✅ Archives: Lumina Library (Digest)")
        print()

        # Search the Archives
        print("SEARCHING THE ARCHIVES:")
        print("-" * 80)
        knowledge = library.knowledge("balance")
        if 'error' not in knowledge:
            print(f"✅ Found knowledge about: {knowledge.get('topic', 'N/A')}")
            print(f"   Source: {knowledge.get('source', 'N/A')}")
        else:
            print(f"❌ {knowledge.get('error', 'Unknown error')}")
        print()

        # Status
        if hasattr(library, 'get_status'):
            status = library.get_status()
            print("ARCHIVES STATUS:")
            print("-" * 80)
            print(f"  Available: {status.get('available', False)}")
            if status.get('available'):
                print(f"  Holocron Entries: {status.get('holocron_entries', 0)}")
                print(f"  Documentation Items: {status.get('documentation_items', 0)}")
        print()

    except Exception as e:
        print(f"❌ Error accessing through Peak: {e}")
        print()
        print("DIRECT ACCESS (Fallback):")
        print("-" * 80)
        library = LuminaLibrary()
        status = library.get_status()
        print(f"  Available: {status.get('available', False)}")

    print("=" * 80)
    print("📚 Always start with @peak, begin with the Lumina Library")
    print("   Our very own personal #JediArchives")
    print("=" * 80)


if __name__ == "__main__":


    main()