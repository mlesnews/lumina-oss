#!/usr/bin/env python3
"""Test pattern fix for extension_format_error."""

import re

pattern = r".+\s*\((?:bad|invalid|malformed)\s*format)"
print(f"Pattern: {pattern}")
print(f"Open parens: {pattern.count('(')}, Close parens: {pattern.count(')')}")

test_cases = [
    ("vscode.git (bad format) Expected: <provider>.<name>", True),
    ("python.ext (invalid format) Expected: <provider>.<name>", True),
    ("docker.tools (malformed format) Expected: <provider>.<name>", True),
    ("extension.id (bad format)", True),
    ("test (bad format)", True),
    ("This is fine (good format)", False),
]

print("\nPattern Test Results:")
print("-" * 60)
all_passed = True
for tc, expected in test_cases:
    match = re.search(pattern, tc)
    status = "PASS" if bool(match) == expected else "FAIL"
    if status == "FAIL":
        all_passed = False
    print(f"  [{status}] '{tc}'")

print("-" * 60)
print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
