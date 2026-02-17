#!/usr/bin/env python3
"""
Fix SYPHON JSON parsing error
Identify and repair the JSON syntax error in extracted_data.json
"""

import json
import re
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("fix_syphon_json")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def fix_json_syntax_error(file_path: Path):
    """Fix JSON syntax errors in SYPHON data file"""

    print(f"🔍 Analyzing JSON file: {file_path}")

    # Read the entire file
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    print(f"📏 File size: {len(content):,} characters")

    # Try to find where the JSON parsing fails
    try:
        # Find the last valid JSON object before the error
        lines = content.split('\n')

        print(f"📄 Total lines: {len(lines):,}")

        # Look for the problematic area around line 7542
        error_line = 7542
        start_line = max(0, error_line - 10)
        end_line = min(len(lines), error_line + 10)

        print(f"\n🔍 Examining lines around error (line {error_line}):")
        for i in range(start_line, end_line):
            if i < len(lines):
                line_content = lines[i].strip()
                if line_content:
                    marker = ">>> " if i == error_line else "    "
                    print(f"{marker}Line {i+1:4d}: {line_content[:100]}{'...' if len(line_content) > 100 else ''}")

        # Try to parse incrementally to find the error
        print("\n🔧 Attempting incremental JSON parsing...")

        # Find all object boundaries
        brace_count = 0
        in_string = False
        string_char = None
        escape_next = False

        valid_objects = []
        current_object = ""
        object_start = 0

        i = 0
        while i < len(content):
            char = content[i]

            # Handle string escaping
            if escape_next:
                escape_next = False
                current_object += char
                i += 1
                continue

            if char == '\\':
                escape_next = True
                current_object += char
                i += 1
                continue

            # Handle string start/end
            if not in_string and char in ['"', "'"]:
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                in_string = False
                string_char = None

            # Count braces when not in string
            if not in_string:
                if char == '{':
                    if brace_count == 0:
                        object_start = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found complete object
                        object_end = i + 1
                        object_content = content[object_start:object_end]

                        # Try to parse this object
                        try:
                            parsed = json.loads(object_content)
                            valid_objects.append(object_content)
                            print(f"✅ Valid object found: {parsed.get('data_id', 'unknown')}")
                        except json.JSONDecodeError as e:
                            print(f"❌ Invalid object at position {object_start}-{object_end}: {e}")
                            # Try to fix common issues
                            fixed_content = fix_common_json_issues(object_content)
                            if fixed_content != object_content:
                                try:
                                    parsed = json.loads(fixed_content)
                                    valid_objects.append(fixed_content)
                                    print(f"🔧 Fixed object: {parsed.get('data_id', 'unknown')}")
                                except:
                                    print(f"💥 Could not fix object, skipping...")
                            else:
                                print(f"💥 Could not fix object, skipping...")

            current_object += char
            i += 1

        print(f"\n📊 Found {len(valid_objects)} valid JSON objects")

        # Reconstruct valid JSON array
        if valid_objects:
            fixed_content = "[\n" + ",\n".join(valid_objects) + "\n]"

            # Test the fixed JSON
            try:
                parsed = json.loads(fixed_content)
                print(f"✅ Fixed JSON is valid with {len(parsed)} objects")

                # Backup original file
                backup_path = file_path.with_suffix('.json.backup')
                file_path.rename(backup_path)
                print(f"💾 Original file backed up to: {backup_path}")

                # Write fixed file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"✨ Fixed JSON written to: {file_path}")

                return True

            except json.JSONDecodeError as e:
                print(f"❌ Fixed JSON still invalid: {e}")
                return False
        else:
            print("❌ No valid objects found")
            return False

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

def fix_common_json_issues(content: str) -> str:
    """Fix common JSON syntax issues"""
    # Remove trailing commas before closing braces/brackets
    content = re.sub(r',(\s*[}\]])', r'\1', content)

    # Fix unescaped quotes in strings (basic)
    # This is tricky, so we'll be conservative

    return content

def main():
    try:
        """Main entry point"""
        syphon_file = Path(__file__).parent.parent / "data" / "syphon" / "extracted_data.json"

        if not syphon_file.exists():
            print(f"❌ SYPHON file not found: {syphon_file}")
            return 1

        print("🚨 SYPHON JSON CORRUPTION DETECTED")
        print("🔧 Attempting automatic repair...")
        print("=" * 50)

        success = fix_json_syntax_error(syphon_file)

        if success:
            print("\n🎉 SYPHON JSON REPAIRED SUCCESSFULLY!")
            print("✅ System should now function normally")
            return 0
        else:
            print("\n💥 SYPHON JSON REPAIR FAILED")
            print("⚠️  Manual intervention required")
            return 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import sys


    sys.exit(main())