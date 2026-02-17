#!/usr/bin/env python3
"""Fix the extension format error pattern in notification_lifecycle_diagnostics.py"""

# Read the file
with open("scripts/python/notification_lifecycle_diagnostics.py") as f:
    content = f.read()

# Fix the broken pattern
old = '            "pattern": r".+\\s*\\((?:bad|invalid|malformed)\\s*format)",'
new = '            "pattern": r".+\\s*\\((?:bad|invalid|malformed)\\s*format\\)",'

# Replace
if old in content:
    content = content.replace(old, new)
    with open("scripts/python/notification_lifecycle_diagnostics.py", "w") as f:
        f.write(content)
    print("FIXED: Pattern updated with correct closing parenthesis")
else:
    print("PATTERN NOT FOUND - checking current state...")
    # Check if already fixed
    if r".+\s*\((?:bad|invalid|malformed)\s*format\)" in content:
        print("Pattern appears to be correct now")
