#!/usr/bin/env python3
"""
Verify the class/class_name field conversion fix
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.short_tagging_system import ShortTaggingSystem, TagDefinition

print("=" * 70)
print("VERIFYING class/class_name FIELD CONVERSION FIX")
print("=" * 70)
print()

# Load registry directly
registry_path = project_root / "config" / "shortag_registry.json"
with open(registry_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find all tags with "class" field
tags_with_class = {k: v.get("class") for k, v in data.items() 
                   if k != "_metadata" and "class" in v}

print(f"Tags with 'class' field in JSON: {len(tags_with_class)}")
for name, class_val in tags_with_class.items():
    print(f"  {name}: class='{class_val}'")
print()

# Test loading with ShortTaggingSystem
print("Loading with ShortTaggingSystem...")
system = ShortTaggingSystem()

print(f"Total tags loaded: {len(system.tags)}")
print()

# Check which tags have class_name after loading
tags_with_class_name = []
tags_with_module_no_class = []
for name, tag in system.tags.items():
    if tag.class_name:
        tags_with_class_name.append((name, tag.class_name, tag.module))
    elif tag.module:
        tags_with_module_no_class.append((name, tag.module))

print(f"Tags with class_name after loading: {len(tags_with_class_name)}")
for name, class_name, module in tags_with_class_name:
    print(f"  ✅ {name}: class_name='{class_name}', module='{module}'")
print()

if tags_with_module_no_class:
    print(f"⚠️  Tags with module but NO class_name: {len(tags_with_module_no_class)}")
    for name, module in tags_with_module_no_class:
        print(f"  {name}: module='{module}'")
    print()

# Verify all tags with "class" field have class_name
missing_class_name = []
for name in tags_with_class.keys():
    if name not in system.tags:
        missing_class_name.append((name, "tag not loaded"))
    elif not system.tags[name].class_name:
        missing_class_name.append((name, "class_name is None"))

if missing_class_name:
    print("❌ VERIFICATION FAILED:")
    for name, reason in missing_class_name:
        print(f"  {name}: {reason}")
    print()
    exit(1)
else:
    print("✅ VERIFICATION PASSED:")
    print("  All tags with 'class' field have class_name set correctly")
    print()

# Test direct TagDefinition creation with "class" field (should fail without conversion)
print("Testing direct TagDefinition creation with 'class' field...")
test_data = {
    "type": "mention",
    "category": "system",
    "description": "Test",
    "context_weight": 1.0,
    "ai_weight": 0.8,
    "human_weight": 0.2,
    "class": "TestClass"  # Using "class" instead of "class_name"
}

try:
    # This should fail without conversion
    tag = TagDefinition(**test_data)
    print("  ❌ ERROR: TagDefinition accepted 'class' field (should have failed)")
    exit(1)
except TypeError as e:
    print(f"  ✅ Expected error: {e}")
    print("  This confirms the bug exists without conversion")
print()

# Test with conversion (simulating the fix)
print("Testing with conversion (class -> class_name)...")
test_data_converted = test_data.copy()
if "class" in test_data_converted and "class_name" not in test_data_converted:
    test_data_converted["class_name"] = test_data_converted.pop("class")

valid_fields = {f.name for f in TagDefinition.__dataclass_fields__.values()}
filtered_data = {k: v for k, v in test_data_converted.items() if k in valid_fields}

try:
    tag = TagDefinition(**filtered_data)
    print(f"  ✅ Success: class_name='{tag.class_name}'")
except Exception as e:
    print(f"  ❌ Error: {e}")
    exit(1)
print()

print("=" * 70)
print("✅ FIX VERIFICATION COMPLETE - ALL TESTS PASSED")
print("=" * 70)
print()
print("Summary:")
print(f"  • {len(tags_with_class)} tags with 'class' field in JSON")
print(f"  • {len(tags_with_class_name)} tags with class_name after loading")
print(f"  • All tags converted correctly")
print(f"  • No silent failures")
print("=" * 70)
