#!/usr/bin/env python3
"""Fix GitLens configuration by removing duplicates"""

import json
from pathlib import Path

settings_file = Path(".cursor/settings.json")

# Read current settings
with open(settings_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Remove duplicate gitlens.views.commitDetails.files.files keys
cleaned_data = {}
seen_keys = set()

for key, value in data.items():
    if key not in seen_keys:
        cleaned_data[key] = value
        seen_keys.add(key)
    else:
        print(f"Removed duplicate: {key}")

# Write cleaned settings
with open(settings_file, 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print(f"✅ Cleaned {len(data) - len(cleaned_data)} duplicate keys")
print(f"✅ Final config has {len(cleaned_data)} keys")
