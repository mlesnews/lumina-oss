#!/usr/bin/env python3
"""
Kenny Systematic Debug - Logical Analysis

Systematic debugging approach:
1. Compare original working code vs enhanced code (line-by-line)
2. Identify exact differences
3. Test each component in isolation
4. Document findings objectively

Tags: #KENNY #DEBUGGING #LOGIC #SYSTEMATIC @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import difflib

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHONConfig = None
    DataSourceType = None

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def compare_files(file1: Path, file2: Path) -> List[Tuple[str, str, str]]:
    """
    Compare two files line by line

    Returns:
        List of (line_num, type, content) where type is:
        - 'equal': Lines are identical
        - 'delete': Line in file1 but not file2
        - 'insert': Line in file2 but not file1
        - 'replace': Lines differ
    """
    try:
        with open(file1, 'r', encoding='utf-8') as f1:
            lines1 = f1.readlines()
        with open(file2, 'r', encoding='utf-8') as f2:
            lines2 = f2.readlines()
    except Exception as e:
        print(f"Error reading files: {e}")
        return []

    diff = list(difflib.unified_diff(lines1, lines2, lineterm='', n=0))

    differences = []
    for line in diff:
        if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
            continue
        if line.startswith('-'):
            differences.append(('delete', line[1:].rstrip()))
        elif line.startswith('+'):
            differences.append(('insert', line[1:].rstrip()))
        elif line.startswith(' '):
            differences.append(('equal', line[1:].rstrip()))

    return differences

def extract_sprite_rendering_code(file_path: Path) -> Dict[str, List[str]]:
    """Extract sprite rendering code sections"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}

    sections = {
        'draw_function': [],
        'body_rendering': [],
        'face_rendering': [],
        'canvas_creation': []
    }

    in_draw_function = False
    in_body = False
    in_face = False

    for i, line in enumerate(lines):
        # Find draw function
        if 'def draw' in line.lower() or 'def _draw' in line.lower():
            in_draw_function = True
            sections['draw_function'].append(f"{i+1}: {line.rstrip()}")

        if in_draw_function:
            sections['draw_function'].append(f"{i+1}: {line.rstrip()}")

            # Find body rendering
            if 'body' in line.lower() and ('ellipse' in line.lower() or 'oval' in line.lower()):
                in_body = True
            if in_body:
                sections['body_rendering'].append(f"{i+1}: {line.rstrip()}")
                if line.strip().endswith(')') and 'ellipse' in line.lower():
                    in_body = False

            # Find face rendering
            if 'face' in line.lower() and ('ellipse' in line.lower() or 'oval' in line.lower()):
                in_face = True
            if in_face:
                sections['face_rendering'].append(f"{i+1}: {line.rstrip()}")
                if line.strip().endswith(')') and 'ellipse' in line.lower():
                    in_face = False

            # End of function
            if line.strip().startswith('def ') and i > 0:
                in_draw_function = False

    return sections

def main():
    """Main systematic debugging"""
    print("=" * 80)
    print("🔍 KENNY SYSTEMATIC DEBUG - LOGICAL ANALYSIS")
    print("=" * 80)
    print()

    original_file = project_root / "scripts" / "python" / "ironman_virtual_assistant.py"
    enhanced_file = project_root / "scripts" / "python" / "kenny_imva_enhanced.py"

    print("STEP 1: Extract sprite rendering code from both files")
    print("-" * 80)

    original_sections = extract_sprite_rendering_code(original_file)
    enhanced_sections = extract_sprite_rendering_code(enhanced_file)

    print("\nORIGINAL (ironman_virtual_assistant.py):")
    print("Body Rendering:")
    for line in original_sections.get('body_rendering', [])[:10]:
        print(f"  {line}")

    print("\nENHANCED (kenny_imva_enhanced.py):")
    print("Body Rendering:")
    for line in enhanced_sections.get('body_rendering', [])[:10]:
        print(f"  {line}")

    print("\n" + "=" * 80)
    print("STEP 2: Key Differences Identified")
    print("-" * 80)
    print("1. Original uses PIL with multiple layers and gradients")
    print("2. Enhanced uses simple ellipse with fill only")
    print("3. Need to verify if outline parameter is the issue")
    print()

    print("=" * 80)
    print("STEP 3: Test Hypothesis")
    print("-" * 80)
    print("Hypothesis: Froot Loop caused by outline parameter in PIL ellipse")
    print("Test: Remove outline completely (already done)")
    print("Result: Need user verification")
    print()

    print("=" * 80)
    print("LOGICAL CONCLUSION:")
    print("-" * 80)
    print("1. Code changes have been made but not verified")
    print("2. Need visual verification from user")
    print("3. If issue persists, root cause is elsewhere (not in sprite code)")
    print("4. May need to check: image creation, canvas placement, or transparency")
    print("=" * 80)

if __name__ == "__main__":


    main()