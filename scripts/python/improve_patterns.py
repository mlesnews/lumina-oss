#!/usr/bin/env python3
"""Improve the notification patterns for better coverage."""
import re

# Read the current file
with open('scripts/python/notification_lifecycle_diagnostics.py', 'r') as f:
    content = f.read()

# Improved patterns
improvements = {
    # extension_activation_failed - handle "failed to load" and "activation was cancelled"
    '"extension_activation_failed": {': '''
        "extension_activation_failed": {
            "pattern": r"(?:Extension|ELEMENT): .+?(?:failed to activate|failed to load|activation (?:was|cancelled|failed))",
''',

    # github_access_error - handle more variations
    '"github_access_error": {': '''
        "github_access_error": {
            "pattern": r"(?:No GitHub|GitHub authentication|ERROR: GitHub token|invalid.*GitHub)",
''',

    # extension_dependency_error - handle more variations
    '"extension_dependency_error": {': '''
        "extension_dependency_error": {
            "pattern": r"(?:Cannot activate|Extension .+ failed to activate).+depends on|ERROR: .+missing dependency",
''',
}

# Apply improvements
for old_key, new_content in improvements.items():
    if old_key in content:
        # Find the full block to replace
        # This is a simple string replacement approach
        content = content.replace(old_key, new_content)
        print(f"✅ Replaced: {old_key[:50]}...")
    else:
        print(f"❌ Not found: {old_key[:50]}...")

# Write back
with open('scripts/python/notification_lifecycle_diagnostics.py', 'w') as f:
    f.write(content)

print("\nPatterns updated!")
