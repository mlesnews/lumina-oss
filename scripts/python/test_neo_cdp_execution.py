#!/usr/bin/env python3
"""
Test Neo CDP Execution
Verify that CDP is actually executing JavaScript
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from neo_browser_automation_engine import NEOBrowserAutomationEngine
import time

print("Testing Neo CDP Execution...")
print("=" * 70)

neo = NEOBrowserAutomationEngine(project_root)

# Connect
if not neo._connect_cdp():
    print("❌ Failed to connect to CDP")
    sys.exit(1)

print("✅ Connected to CDP")
print("")

# Test 1: Simple script
print("Test 1: Simple return value")
result1 = neo.execute_script("return 'Hello from CDP';")
print(f"   Result: {result1}")
print(f"   Type: {type(result1)}")
print("")

# Test 2: Get page title
print("Test 2: Get page title")
result2 = neo.execute_script("return document.title;")
print(f"   Result: {result2}")
print("")

# Test 3: Get URL
print("Test 3: Get current URL")
result3 = neo.execute_script("return window.location.href;")
print(f"   Result: {result3}")
print("")

# Test 4: Count inputs
print("Test 4: Count input elements")
result4 = neo.execute_script("return document.querySelectorAll('input').length;")
print(f"   Result: {result4}")
print("")

# Test 5: Get all input types
print("Test 5: Get input types")
result5 = neo.execute_script("""
    const inputs = Array.from(document.querySelectorAll('input'));
    return inputs.map(i => ({ type: i.type, placeholder: i.placeholder || '', id: i.id || '' })).slice(0, 5);
""")
print(f"   Result: {result5}")
print("")

# Test 6: Check if ProtonPass is loaded
print("Test 6: Check for ProtonPass elements")
result6 = neo.execute_script("""
    const hasSearch = !!document.querySelector('input[type="search"], input[placeholder*="search" i]');
    const bodyText = document.body.innerText.substring(0, 200);
    return JSON.stringify({ hasSearch: hasSearch, bodyText: bodyText });
""")
print(f"   Result: {result6}")
print("")

print("=" * 70)
print("CDP Execution Test Complete")
