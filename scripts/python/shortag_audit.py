#!/usr/bin/env python3
"""
Shortag Registry Audit Tool
Finds tags that are referenced but not defined as top-level entries
"""

import json
import re
from pathlib import Path
import logging
logger = logging.getLogger("shortag_audit")



def audit_shortag_registry():
    try:
        """Audit the shortag registry for missing tag definitions"""

        lumina_path = Path(__file__).parent.parent.parent
        registry_path = lumina_path / "config" / "shortag_registry.json"

        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Get all defined tags (top-level keys in 'tags')
        defined_tags = set(data.get('tags', {}).keys())

        # Convert to string and find all @TAG references
        content = json.dumps(data)
        referenced = set(re.findall(r'@[A-Z][A-Z0-9_]+', content))

        # Find missing (referenced but not defined)
        missing = referenced - defined_tags

        print("=" * 60)
        print("  SHORTAG REGISTRY AUDIT")
        print("=" * 60)
        print(f"  Defined tags:      {len(defined_tags)}")
        print(f"  Referenced tags:   {len(referenced)}")
        print(f"  Missing defs:      {len(missing)}")
        print("=" * 60)
        print()

        if missing:
            print("⚠️  MISSING TAGS (referenced but NOT defined):")
            print("-" * 60)
            for tag in sorted(missing):
                print(f"  ❌ {tag}")
            print()
        else:
            print("✅ All referenced tags are defined!")
            print()

        print("📋 DEFINED TAGS:")
        print("-" * 60)
        for tag in sorted(defined_tags):
            print(f"  ✓ {tag}")

        return {
            'defined': sorted(defined_tags),
            'referenced': sorted(referenced),
            'missing': sorted(missing)
        }


    except Exception as e:
        logger.error(f"Error in audit_shortag_registry: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    result = audit_shortag_registry()
