#!/usr/bin/env python3
"""Fix the regex pattern in notification_lifecycle_diagnostics.py"""

# Read the file
with open("scripts/python/notification_lifecycle_diagnostics.py") as f:
    content = f.read()

# Fix the pattern - remove the extra closing paren
old_pattern = r'"pattern": r".+\s*\((?:bad|invalid|malformed)\s*format)"'
new_pattern = r'"pattern": r".+\s*\((?:bad|invalid|malformed)\s*format"'

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open("scripts/python/notification_lifecycle_diagnostics.py", "w") as f:
        f.write(content)
    print("✅ Fixed the pattern!")
else:
    print("Pattern not found. Let me check what's there:")
    # Find the line
    for i, line in enumerate(content.split("\n")):
        if "extension_format_error" in line and "pattern" in line:
            print(f"Line {i}: {repr(line)}")
