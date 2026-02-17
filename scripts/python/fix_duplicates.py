#!/usr/bin/env python3
"""Fix duplicate pattern lines in notification_lifecycle_diagnostics.py"""
import re

# Read the file
with open('scripts/python/notification_lifecycle_diagnostics.py', 'r') as f:
    content = f.read()

# Remove duplicate pattern lines for extension_dependency_error
# Pattern line is the one with just "pattern": r"..."
content = re.sub(
    r'("pattern": r"(?:Cannot activate|Extension \.+ failed to activate)\.+depends on\|ERROR: \.+missing dependency",)\n\s+"pattern": r"Cannot activate',
    r'\1',
    content
)

# Remove duplicate pattern lines for extension_activation_failed
content = re.sub(
    r'("pattern": r"\(?:\(?:Extension\|ELEMENT\)\: \.+?\?\(?:failed to activate\|failed to load\|activation \?\?:w\|cancelled\|failed\)\?",)\n\s+"pattern": r"Extension',
    r'\1',
    content
)

# Remove duplicate pattern lines for github_access_error
content = re.sub(
    r'("pattern": r"\(?:\(?:No GitHub\|GitHub authentication\|ERROR\: GitHub token\|invalid\.\*GitHub\)\?",)\n\s+"pattern": r"No GitHub',
    r'\1',
    content
)

# Write back
with open('scripts/python/notification_lifecycle_diagnostics.py', 'w') as f:
    f.write(content)

print("Duplicates removed!")
