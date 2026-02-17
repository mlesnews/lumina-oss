#!/usr/bin/env python3
"""Verify the extension_format_error pattern fix works."""

import re

# Read the file
with open("scripts/python/notification_lifecycle_diagnostics.py") as f:
    content = f.read()

# Find the extension_format_error pattern specifically
pattern_match = re.search(r'"extension_format_error".*?"pattern":\s*r"([^"]+)"', content, re.DOTALL)
if pattern_match:
    pattern = pattern_match.group(1)
    print(f"Pattern from file: {repr(pattern)}")
    print(f"Open parens: {pattern.count('(')}")
    print(f"Close parens: {pattern.count(')')}")

    # Try to compile
    try:
        compiled = re.compile(pattern)
        print("✅ Compiled successfully!")

        # Test cases
        test_cases = [
            ("vscode.git (bad format) Expected: <provider>.<name>", True),
            ("python.ext (invalid format) Expected: <provider>.<name>", True),
            ("docker.tools (malformed format) Expected: <provider>.<name>", True),
            ("Extension recommendation has bad format", True),
            ("This should not match (good format)", False),
        ]
        print("\nTest cases:")
        all_pass = True
        for tc, expected in test_cases:
            m = compiled.search(tc)
            matched = bool(m)
            status = "PASS" if matched == expected else "FAIL"
            if status == "FAIL":
                all_pass = False
            print(f"  [{status}] '{tc}'")

        print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}")
    except Exception as e:
        print(f"❌ Compile error: {e}")
else:
    print("Pattern not found in file")
