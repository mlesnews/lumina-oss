#!/usr/bin/env python3
"""Test tag loading to verify the class/class_name issue"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.short_tagging_system import ShortTaggingSystem, TagDefinition

# Load registry directly
registry_path = project_root / "config" / "shortag_registry.json"
with open(registry_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("Testing Tag Loading - class vs class_name Issue")
print("=" * 70)
print()

# Check which tags have "class" field
tags_with_class = []
for tag_name, tag_data in data.items():
    if tag_name != "_metadata" and "class" in tag_data:
        tags_with_class.append((tag_name, tag_data.get("class")))

print(f"Tags with 'class' field in JSON: {len(tags_with_class)}")
for name, class_val in tags_with_class:
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
    print(f"  {name}: class_name='{class_name}', module='{module}'")
print()

if tags_with_module_no_class:
    print(f"⚠️  Tags with module but NO class_name: {len(tags_with_module_no_class)}")
    for name, module in tags_with_module_no_class:
        print(f"  {name}: module='{module}'")
    print()

# Test direct TagDefinition creation with "class" field
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
except TypeError as e:
    print(f"  ✅ Expected error: {e}")
    print("  This confirms the bug exists")
print()

# Test with conversion
print("Testing with conversion (class -> class_name)...")
test_data_converted = test_data.copy()
if "class" in test_data_converted and "class_name" not in test_data_converted:
    test_data_converted["class_name"] = test_data_converted.pop("class")

try:
    tag = TagDefinition(**test_data_converted)
    print(f"  ✅ Success: class_name='{tag.class_name}'")
except Exception as e:
    print(f"  ❌ Error: {e}")
print()

print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
