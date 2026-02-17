#!/usr/bin/env python3
"""Simple regex test."""

import re

# Test the pattern
p = r".+\s*\((?:bad|invalid|malformed)\s*format)"
print("Pattern:", p)
print("Length:", len(p))

# Count parens
print("Open parens:", p.count("("))
print("Close parens:", p.count(")"))

# Try to compile
try:
    compiled = re.compile(p)
    print("✅ Compiled successfully!")
except Exception as e:
    print("❌ Compile error:", e)
