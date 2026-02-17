#!/usr/bin/env python3
"""
Test Browser DNS and Connectivity via CDP
Check if browser can resolve and connect to sites

Tags: #BROWSER #DNS #CDP #TROUBLESHOOTING
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from neo_browser_automation_engine import NEOBrowserAutomationEngine
import time

print("Testing Browser DNS and Connectivity via CDP...")
print("=" * 70)

neo = NEOBrowserAutomationEngine(project_root)

# Connect to browser
if not neo._connect_cdp():
    print("❌ Failed to connect to CDP")
    sys.exit(1)

print("✅ Connected to CDP")
print("")

# Test 1: Get current URL
print("Test 1: Get current page URL")
result1 = neo.execute_script("return window.location.href;")
print(f"   Current URL: {result1}")
print("")

# Test 2: Try to navigate to a test site
print("Test 2: Navigate to google.com")
if neo.navigate("https://www.google.com"):
    print("   ✅ Navigation command sent")
    time.sleep(3)
    result2 = neo.execute_script("return window.location.href;")
    print(f"   Current URL after navigation: {result2}")
else:
    print("   ❌ Navigation failed")
print("")

# Test 3: Check if page loaded
print("Test 3: Check if page loaded successfully")
result3 = neo.execute_script("""
    return JSON.stringify({
        url: window.location.href,
        title: document.title,
        readyState: document.readyState,
        hasContent: document.body ? document.body.innerText.length > 0 : false
    });
""")
print(f"   Page status: {result3}")
print("")

# Test 4: Try to fetch a resource
print("Test 4: Test fetch API (browser-side network)")
result4 = neo.execute_script("""
    return fetch('https://www.google.com', { method: 'HEAD', mode: 'no-cors' })
        .then(() => 'Success')
        .catch(err => 'Error: ' + err.message);
""")
print(f"   Fetch result: {result4}")
print("")

# Test 5: Check DNS resolution in browser
print("Test 5: Check DNS via browser")
result5 = neo.execute_script("""
    // Try to create an image from a URL to test DNS
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve('Image loaded - DNS working');
        img.onerror = () => resolve('Image failed - DNS issue');
        img.src = 'https://www.google.com/favicon.ico?' + Date.now();
        setTimeout(() => resolve('Timeout'), 3000);
    });
""")
print(f"   DNS test: {result5}")
print("")

print("=" * 70)
print("Browser DNS/Connectivity Test Complete")
