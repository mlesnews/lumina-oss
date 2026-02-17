#!/usr/bin/env python3
"""Fix missing newlines at end of files"""
from pathlib import Path

root = Path(__file__).parent
files = list(root.rglob('*.py'))
fixed = 0

for f in files:
    if f.name == 'kilo_code_fixer.py' or f.name == 'fix_newlines.py':
        continue
    try:
        with open(f, 'rb') as file:
            content = file.read()
            if not content.endswith(b'\n'):
                with open(f, 'ab') as file:
                    file.write(b'\n')
                fixed += 1
    except Exception:
        pass

print(f'✅ Fixed {fixed} files missing newlines')
