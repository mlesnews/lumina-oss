#!/usr/bin/env python3
"""Get password from clipboard"""

import sys

# Try different clipboard methods
try:
    import pyperclip
    password = pyperclip.paste()
    print(password)
    sys.exit(0)
except ImportError:
    pass
except:
    pass

try:
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    password = root.clipboard_get()
    print(password)
    sys.exit(0)
except:
    pass

# Windows clipboard
try:
    import win32clipboard
    win32clipboard.OpenClipboard()
    password = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    print(password)
    sys.exit(0)
except:
    pass

print("", file=sys.stderr)
sys.exit(1)
