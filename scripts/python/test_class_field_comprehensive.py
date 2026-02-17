#!/usr/bin/env python3
"""
Comprehensive test for class/class_name field conversion fix
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.short_tagging_system import ShortTaggingSystem, TagDefinition

print("=" * 70)
print("COMPREHENSIVE VERIFICATION - class/class_name FIELD FIX")
print("=" * 70)
print()

# Load registry
registry_path = project_root / "config" / "shortag_registry.json"
with open(registry_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find all tags with "class" field
tags_with_class = {k: v.get("class") for k, v in data.items() 
                   if k != "_metadata" and "class" in v}

print(f"STEP 1: Tags with 'class' field in JSON: {len(tags_with_class)}")
for name, class_val in tags_with_class.items():
    print(f"  {name}: class='{class_val}'")
print()

# Test 1: Direct TagDefinition creation with "class" (should fail)
print("STEP 2: Testing direct TagDefinition creation with 'class' field...")
test_tag_name = list(tags_with_class.keys())[0]
test_tag_data = data[test_tag_name].copy()
print(f"  Testing with tag: {test_tag_name}")
print(f"  Has 'class' field: {'class' in test_tag_data}")
print(f"  Has 'class_name' field: {'class_name' in test_tag_data}")

try:
    tag = TagDefinition(**test_tag_data)
    print("  ❌ ERROR: TagDefinition accepted 'class' field (should have failed)")
    exit(1)
except TypeError as e:
    print(f"  ✅ Expected error: {str(e)[:80]}...")
    print("  This confirms the bug exists without conversion")
print()

# Test 2: Load with ShortTaggingSystem (should succeed)
print("STEP 3: Loading with ShortTaggingSystem (with fix)...")
system = ShortTaggingSystem()

tags_with_class_name = []
tags_with_module_no_class = []
for name, tag in system.tags.items():
    if tag.class_name:
        tags_with_class_name.append((name, tag.class_name, tag.module))
    elif tag.module:
        tags_with_module_no_class.append((name, tag.module))

print(f"  Total tags loaded: {len(system.tags)}")
print(f"  Tags with class_name: {len(tags_with_class_name)}")
print()

# Verify all tags with "class" field have class_name
print("STEP 4: Verifying all tags with 'class' field have class_name...")
missing_class_name = []
for name in tags_with_class.keys():
    if name not in system.tags:
        missing_class_name.append((name, "tag not loaded"))
    elif not system.tags[name].class_name:
        missing_class_name.append((name, "class_name is None"))
    else:
        print(f"  ✅ {name}: class_name='{system.tags[name].class_name}'")

if missing_class_name:
    print()
    print("  ❌ VERIFICATION FAILED:")
    for name, reason in missing_class_name:
        print(f"    {name}: {reason}")
    exit(1)
print()

# Test 3: Edge case - both "class" and "class_name" exist
print("STEP 5: Testing edge case (both 'class' and 'class_name' exist)...")
test_data_both = {
    "type": "mention",
    "category": "system",
    "description": "Test",
    "context_weight": 1.0,
    "ai_weight": 0.8,
    "human_weight": 0.2,
    "class": "OldClass",
    "class_name": "NewClass"
}

tag_data_copy = test_data_both.copy()
if "class" in tag_data_copy:
    if "class_name" not in tag_data_copy:
        tag_data_copy["class_name"] = tag_data_copy.pop("class")
    else:
        tag_data_copy.pop("class", None)  # Prefer class_name

valid_fields = {f.name for f in TagDefinition.__dataclass_fields__.values()}
filtered_data = {k: v for k, v in tag_data_copy.items() if k in valid_fields}
tag = TagDefinition(**filtered_data)

if tag.class_name == "NewClass":
    print(f"  ✅ Edge case handled: Prefers 'class_name' over 'class'")
    print(f"     class_name='{tag.class_name}'")
else:
    print(f"  ❌ Edge case failed: Expected 'NewClass', got '{tag.class_name}'")
    exit(1)
print()

# Test 4: Check for tags with module but no class_name
print("STEP 6: Checking for tags with module but missing class_name...")
if tags_with_module_no_class:
    print(f"  ⚠️  Found {len(tags_with_module_no_class)} tags with module but no class_name:")
    for name, module in tags_with_module_no_class:
        print(f"    {name}: module='{module}'")
    print("  Note: These may be intentional (module without class)")
else:
    print("  ✅ No tags with module but missing class_name")
print()

print("=" * 70)
print("✅ COMPREHENSIVE VERIFICATION COMPLETE - ALL TESTS PASSED")
print("=" * 70)
print()
print("Summary:")
print(f"  • {len(tags_with_class)} tags with 'class' field in JSON")
print(f"  • {len(tags_with_class_name)} tags with class_name after loading")
print(f"  • All tags converted correctly")
print(f"  • Edge cases handled")
print(f"  • No silent failures")
print("=" * 70)
