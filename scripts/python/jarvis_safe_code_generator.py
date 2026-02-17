#!/usr/bin/env python3
"""
JARVIS Safe Code Generator

Wraps code generation with Systems Disaster Recovery Engineer validation.
Prevents magic eight-ball behavior by checking existing code before generating.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_systems_disaster_recovery_engineer import JARVISSystemsDisasterRecoveryEngineer
    DISASTER_RECOVERY_AVAILABLE = True
except ImportError:
    DISASTER_RECOVERY_AVAILABLE = False
    JARVISSystemsDisasterRecoveryEngineer = None


def generate_code_safely(code: str, target_file: Path,
                        project_root: Optional[Path] = None,
                        function_name: Optional[str] = None,
                        class_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate code safely with validation

    This prevents magic eight-ball behavior by:
    1. Checking if code already exists
    2. Validating syntax
    3. Checking for conflicts
    4. Creating backups
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    if not DISASTER_RECOVERY_AVAILABLE:
        # Fallback: just write the code (not recommended)
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(code)
            return {
                'success': True,
                'file': str(target_file),
                'warning': 'Disaster recovery not available - code written without validation'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # Use Systems Disaster Recovery Engineer
    engineer = JARVISSystemsDisasterRecoveryEngineer(project_root)
    return engineer.generate_code_safely(code, target_file, function_name, class_name)


def write_data_safely(data: Dict[str, Any], target_path: Path,
                     project_root: Optional[Path] = None,
                     data_type: str = "general") -> Dict[str, Any]:
    """
    Write data safely with validation

    This prevents data conflicts by:
    1. Checking for existing data
    2. Validating structure
    3. Creating backups
    4. Ensuring proper location
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    if not DISASTER_RECOVERY_AVAILABLE:
        # Fallback: just write the data (not recommended)
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return {
                'success': True,
                'file': str(target_path),
                'warning': 'Disaster recovery not available - data written without validation'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # Use Systems Disaster Recovery Engineer
    engineer = JARVISSystemsDisasterRecoveryEngineer(project_root)
    return engineer.write_data_safely(data, target_path, data_type)


# Export for use in other modules
__all__ = ['generate_code_safely', 'write_data_safely']
