#!/usr/bin/env python3
"""
Fix Terminal Now - Immediate Fix

Sends direct ANSI escape sequences to fix terminal sequence issues immediately.
This should clear the orange triangle warning in your current terminal.

Run this in the terminal with the orange triangle.
"""

import sys
import time

print("🔧 Fixing terminal sequence issues...", flush=True)

# Send proper sequence markers directly
# These are ANSI escape sequences for shell integration

# Command start (A)
print("\033]133;A\033\\", end="", flush=True)
time.sleep(0.1)

# Command end (B)
print("\033]133;B\033\\", end="", flush=True)
time.sleep(0.1)

# Prompt ready (P)
print("\033]133;P\033\\", end="", flush=True)
time.sleep(0.1)

print("\n✅ Terminal sequence reset sent!")
print("   The orange triangle should disappear now or on the next command.", flush=True)
