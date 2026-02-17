#!/usr/bin/env python3
"""
JARVIS Systems Disaster Recovery Engineer

Applies IT standards, prevents duplicate code generation,
manages data properly, and ensures code quality before generation.
"""

import sys
import json
import ast
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
import logging
import difflib

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDisasterRecovery")


class CodeAnalyzer:
    """Analyzes existing code to prevent duplicates"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.code_index = {}
        self.function_signatures = {}
        self.class_definitions = {}
        self._index_codebase()

    def _index_codebase(self):
        """Index all existing code in codebase"""
        logger.info("Indexing codebase to prevent duplicates...")

        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                self._index_file(py_file)
            except Exception as e:
                logger.debug(f"Could not index {py_file}: {e}")

        logger.info(f"✅ Indexed {len(self.code_index)} files, {len(self.function_signatures)} functions, {len(self.class_definitions)} classes")

    def _index_file(self, file_path: Path):
        """Index a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Store file content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            self.code_index[str(file_path)] = {
                'hash': content_hash,
                'size': len(content),
                'lines': content.count('\n')
            }

            # Parse AST to extract functions and classes
            try:
                tree = ast.parse(content, filename=str(file_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_sig = self._get_function_signature(node)
                        if func_sig not in self.function_signatures:
                            self.function_signatures[func_sig] = []
                        self.function_signatures[func_sig].append(str(file_path))

                    elif isinstance(node, ast.ClassDef):
                        class_sig = self._get_class_signature(node)
                        if class_sig not in self.class_definitions:
                            self.class_definitions[class_sig] = []
                        self.class_definitions[class_sig].append(str(file_path))
            except SyntaxError:
                pass  # Skip files with syntax errors

        except Exception as e:
            logger.debug(f"Error indexing {file_path}: {e}")

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get function signature"""
        args = [arg.arg for arg in node.args.args]
        return f"{node.name}({', '.join(args)})"

    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Get class signature"""
        bases = [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) for base in node.bases]
        return f"class {node.name}({', '.join(bases)})"

    def check_duplicate_code(self, new_code: str, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Check if code already exists"""
        new_hash = hashlib.md5(new_code.encode()).hexdigest()

        # Check for exact duplicates
        for existing_file, file_info in self.code_index.items():
            if file_info['hash'] == new_hash:
                return {
                    'is_duplicate': True,
                    'duplicate_type': 'exact',
                    'existing_file': existing_file,
                    'similarity': 100.0
                }

        # Check for similar code
        similarities = []
        for existing_file, file_info in self.code_index.items():
            if file_path and existing_file == str(file_path):
                continue  # Skip the same file

            try:
                existing_path = Path(existing_file)
                if existing_path.exists():
                    with open(existing_path, 'r', encoding='utf-8', errors='ignore') as f:
                        existing_content = f.read()

                    similarity = self._calculate_similarity(new_code, existing_content)
                    if similarity > 80.0:  # 80% similarity threshold
                        similarities.append({
                            'file': existing_file,
                            'similarity': similarity
                        })
            except:
                pass

        if similarities:
            max_similar = max(similarities, key=lambda x: x['similarity'])
            return {
                'is_duplicate': True,
                'duplicate_type': 'similar',
                'existing_file': max_similar['file'],
                'similarity': max_similar['similarity'],
                'all_similar': similarities
            }

        return {
            'is_duplicate': False,
            'similarity': 0.0
        }

    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate code similarity"""
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')

        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return matcher.ratio() * 100.0

    def check_existing_function(self, function_name: str, args: List[str]) -> Optional[str]:
        """Check if function already exists"""
        sig = f"{function_name}({', '.join(args)})"
        if sig in self.function_signatures:
            return self.function_signatures[sig][0]  # Return first file with this function
        return None

    def check_existing_class(self, class_name: str) -> Optional[str]:
        """Check if class already exists"""
        for class_sig, files in self.class_definitions.items():
            if class_sig.startswith(f"class {class_name}"):
                return files[0]  # Return first file with this class
        return None


class DataManager:
    """Manages data properly with IT standards"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_directories = self._discover_data_directories()
        self.data_index = {}
        self._index_data()

    def _discover_data_directories(self) -> List[Path]:
        try:
            """Discover all data directories"""
            data_dirs = []

            # Standard data locations
            standard_dirs = [
                self.project_root / "data",
                self.project_root / "config",
                self.project_root / "reports"
            ]

            for dir_path in standard_dirs:
                if dir_path.exists():
                    data_dirs.append(dir_path)

            # Find all data directories
            for dir_path in self.project_root.rglob("*"):
                if dir_path.is_dir() and "data" in dir_path.name.lower():
                    if dir_path not in data_dirs:
                        data_dirs.append(dir_path)

            return data_dirs

        except Exception as e:
            self.logger.error(f"Error in _discover_data_directories: {e}", exc_info=True)
            raise
    def _index_data(self):
        """Index all data files"""
        logger.info("Indexing data files...")

        for data_dir in self.data_directories:
            for data_file in data_dir.rglob("*"):
                if data_file.is_file():
                    try:
                        file_info = {
                            'path': str(data_file),
                            'size': data_file.stat().st_size,
                            'modified': datetime.fromtimestamp(data_file.stat().st_mtime).isoformat(),
                            'type': data_file.suffix
                        }

                        # For JSON files, index structure
                        if data_file.suffix == '.json':
                            try:
                                with open(data_file, 'r') as f:
                                    data = json.load(f)
                                    file_info['structure'] = self._get_json_structure(data)
                            except:
                                pass

                        self.data_index[str(data_file)] = file_info
                    except Exception as e:
                        logger.debug(f"Error indexing {data_file}: {e}")

        logger.info(f"✅ Indexed {len(self.data_index)} data files")

    def _get_json_structure(self, data: Any, path: str = "") -> Dict[str, Any]:
        """Get JSON structure"""
        if isinstance(data, dict):
            structure = {}
            for key, value in data.items():
                structure[key] = self._get_json_structure(value, f"{path}.{key}")
            return structure
        elif isinstance(data, list) and len(data) > 0:
            return [self._get_json_structure(data[0], f"{path}[0]")]
        else:
            return type(data).__name__

    def check_data_conflicts(self, new_data: Dict[str, Any], target_path: Path) -> Dict[str, Any]:
        """Check for data conflicts"""
        conflicts = []

        # Check if file exists
        if target_path.exists():
            try:
                with open(target_path, 'r') as f:
                    existing_data = json.load(f)

                # Compare structures
                new_structure = self._get_json_structure(new_data)
                existing_structure = self._get_json_structure(existing_data)

                if new_structure != existing_structure:
                    conflicts.append({
                        'type': 'structure_mismatch',
                        'message': 'Data structure differs from existing file'
                    })
            except:
                conflicts.append({
                    'type': 'read_error',
                    'message': 'Could not read existing file'
                })

        return {
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        }

    def get_data_location(self, data_type: str) -> Optional[Path]:
        """Get appropriate data location for data type"""
        # Map data types to directories
        type_map = {
            'log': self.project_root / "data" / "logs",
            'workflow': self.project_root / "data" / "workflow_logs",
            'health': self.project_root / "data" / "health_reports",
            'milestone': self.project_root / "data" / "milestones",
            'analysis': self.project_root / "data" / "lumina_analysis",
            'config': self.project_root / "config"
        }

        return type_map.get(data_type.lower())


class JARVISSystemsDisasterRecoveryEngineer:
    """
    Systems Disaster Recovery Engineer

    Applies IT standards:
    - Prevents duplicate code generation
    - Manages data properly
    - Ensures code quality
    - Applies IT standards
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Initialize components
        self.code_analyzer = CodeAnalyzer(project_root)
        self.data_manager = DataManager(project_root)

        # IT Standards
        self.it_standards = self._load_it_standards()

        # Recovery log
        self.recovery_log_dir = project_root / "data" / "disaster_recovery_logs"
        self.recovery_log_dir.mkdir(parents=True, exist_ok=True)

    def _load_it_standards(self) -> Dict[str, Any]:
        """Load IT standards"""
        return {
            'code_generation': {
                'check_existing': True,
                'prevent_duplicates': True,
                'similarity_threshold': 80.0,
                'validate_syntax': True,
                'check_imports': True
            },
            'data_management': {
                'validate_structure': True,
                'check_conflicts': True,
                'backup_before_write': True,
                'version_control': True
            },
            'file_operations': {
                'check_existing': True,
                'prevent_overwrite': False,  # Allow overwrite with validation
                'backup_existing': True
            }
        }

    def validate_code_before_generation(self, new_code: str, 
                                       target_file: Path,
                                       function_name: Optional[str] = None,
                                       class_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate code before generation - prevents magic eight-ball behavior

        Checks:
        - Does this code already exist?
        - Does this function/class already exist?
        - Is the code valid?
        - Does it conflict with existing code?
        """
        self.logger.info(f"🔍 Validating code before generation: {target_file}")

        validation_result = {
            'valid': False,
            'can_generate': False,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }

        # 1. Check for duplicate code
        duplicate_check = self.code_analyzer.check_duplicate_code(new_code, target_file)

        if duplicate_check['is_duplicate']:
            if duplicate_check['duplicate_type'] == 'exact':
                validation_result['errors'].append(
                    f"Exact duplicate code exists in: {duplicate_check['existing_file']}"
                )
                validation_result['recommendations'].append(
                    f"Use existing code from: {duplicate_check['existing_file']}"
                )
            else:
                validation_result['warnings'].append(
                    f"Similar code ({duplicate_check['similarity']:.1f}%) exists in: {duplicate_check['existing_file']}"
                )
                validation_result['recommendations'].append(
                    f"Review existing code and modify if needed"
                )

        # 2. Check for existing functions/classes
        if function_name:
            existing_func = self.code_analyzer.check_existing_function(function_name, [])
            if existing_func:
                validation_result['warnings'].append(
                    f"Function '{function_name}' already exists in: {existing_func}"
                )
                validation_result['recommendations'].append(
                    f"Consider extending existing function or using different name"
                )

        if class_name:
            existing_class = self.code_analyzer.check_existing_class(class_name)
            if existing_class:
                validation_result['warnings'].append(
                    f"Class '{class_name}' already exists in: {existing_class}"
                )
                validation_result['recommendations'].append(
                    f"Consider extending existing class or using different name"
                )

        # 3. Validate syntax
        try:
            ast.parse(new_code)
            validation_result['syntax_valid'] = True
        except SyntaxError as e:
            validation_result['errors'].append(f"Syntax error: {e}")

        # 4. Check if file exists and should be overwritten
        if target_file.exists():
            validation_result['warnings'].append(f"File already exists: {target_file}")
            validation_result['recommendations'].append("Backup existing file before overwriting")

        # Determine if can generate
        validation_result['can_generate'] = (
            len(validation_result['errors']) == 0 and
            validation_result.get('syntax_valid', False)
        )
        validation_result['valid'] = validation_result['can_generate']

        # Log validation
        self._log_validation(target_file, validation_result)

        return validation_result

    def validate_data_before_write(self, data: Dict[str, Any], 
                                  target_path: Path,
                                  data_type: str = "general") -> Dict[str, Any]:
        """Validate data before writing"""
        self.logger.info(f"🔍 Validating data before write: {target_path}")

        validation_result = {
            'valid': False,
            'can_write': False,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }

        # 1. Check data conflicts
        conflicts = self.data_manager.check_data_conflicts(data, target_path)

        if conflicts['has_conflicts']:
            for conflict in conflicts['conflicts']:
                validation_result['warnings'].append(conflict['message'])

        # 2. Validate JSON structure
        try:
            json.dumps(data)  # Test JSON serialization
            validation_result['json_valid'] = True
        except TypeError as e:
            validation_result['errors'].append(f"Invalid JSON: {e}")

        # 3. Check appropriate data location
        recommended_location = self.data_manager.get_data_location(data_type)
        if recommended_location and target_path.parent != recommended_location:
            validation_result['warnings'].append(
                f"Data type '{data_type}' typically stored in: {recommended_location}"
            )
            validation_result['recommendations'].append(
                f"Consider using: {recommended_location}"
            )

        # 4. Backup existing file if needed
        if target_path.exists():
            validation_result['warnings'].append(f"File exists - backup recommended")
            validation_result['recommendations'].append("Create backup before overwriting")

        validation_result['can_write'] = len(validation_result['errors']) == 0
        validation_result['valid'] = validation_result['can_write']

        return validation_result

    def _log_validation(self, target_file: Path, result: Dict[str, Any]):
        """Log validation result"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': str(target_file),
            'valid': result['valid'],
            'can_generate': result.get('can_generate', False),
            'warnings': result.get('warnings', []),
            'errors': result.get('errors', [])
        }

        log_file = self.recovery_log_dir / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to log validation: {e}")

    def generate_code_safely(self, code: str, target_file: Path,
                            function_name: Optional[str] = None,
                            class_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate code safely with validation

        This is the proper way to generate code - not like a magic eight-ball
        """
        # Validate first
        validation = self.validate_code_before_generation(
            code, target_file, function_name, class_name
        )

        if not validation['can_generate']:
            return {
                'success': False,
                'error': 'Code validation failed',
                'validation': validation
            }

        # Backup existing file if needed
        if target_file.exists() and self.it_standards['file_operations']['backup_existing']:
            backup_file = target_file.with_suffix(f"{target_file.suffix}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            try:
                import shutil
                shutil.copy2(target_file, backup_file)
                self.logger.info(f"✅ Backed up existing file: {backup_file}")
            except Exception as e:
                self.logger.warning(f"Could not backup file: {e}")

        # Write code
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(code)

            self.logger.info(f"✅ Code generated safely: {target_file}")

            # Re-index codebase
            self.code_analyzer._index_file(target_file)

            # Auto-commit change
            self._auto_commit_file_change(target_file, "code_generation")

            return {
                'success': True,
                'file': str(target_file),
                'validation': validation
            }
        except Exception as e:
            self.logger.error(f"Error restoring file {source_file}: {e}")
            return {'success': False, 'error': str(e)}

    def _auto_commit_file_change(self, file_path: Path, operation: str):
        """Auto-commit a file change"""
        try:
            from jarvis_auto_git_manager import JARVISAutoGitManager

            git_manager = JARVISAutoGitManager(self.project_root)
            # Only commit if there are changes (don't commit on every file)
            # This will be batched
            pass  # Batched commits handled at workflow level
        except Exception as e:
            pass

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'validation': validation
            }

    def write_data_safely(self, data: Dict[str, Any], target_path: Path,
                          data_type: str = "general") -> Dict[str, Any]:
        """Write data safely with validation"""
        # Validate first
        validation = self.validate_data_before_write(data, target_path, data_type)

        if not validation['can_write']:
            return {
                'success': False,
                'error': 'Data validation failed',
                'validation': validation
            }

        # Backup existing file if needed
        if target_path.exists() and self.it_standards['data_management']['backup_before_write']:
            backup_file = target_path.with_suffix(f"{target_path.suffix}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            try:
                import shutil
                shutil.copy2(target_path, backup_file)
                self.logger.info(f"✅ Backed up existing data: {backup_file}")
            except Exception as e:
                self.logger.warning(f"Could not backup data: {e}")

        # Write data
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"✅ Data written safely: {target_path}")

            # Re-index data
            self.data_manager._index_data()

            return {
                'success': True,
                'file': str(target_path),
                'validation': validation
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'validation': validation
            }

    def get_codebase_summary(self) -> Dict[str, Any]:
        """Get summary of codebase state"""
        return {
            'total_files': len(self.code_analyzer.code_index),
            'total_functions': len(self.code_analyzer.function_signatures),
            'total_classes': len(self.code_analyzer.class_definitions),
            'data_files': len(self.data_manager.data_index),
            'data_directories': len(self.data_manager.data_directories)
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Systems Disaster Recovery Engineer")
        parser.add_argument("--validate-code", type=str, help="Validate code file")
        parser.add_argument("--validate-data", type=str, help="Validate data file")
        parser.add_argument("--summary", action="store_true", help="Get codebase summary")
        parser.add_argument("--reindex", action="store_true", help="Re-index codebase")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        engineer = JARVISSystemsDisasterRecoveryEngineer(project_root)

        if args.validate_code:
            code_file = Path(args.validate_code)
            if code_file.exists():
                with open(code_file, 'r') as f:
                    code = f.read()

                validation = engineer.validate_code_before_generation(code, code_file)
                print(f"\n✅ Validation: {validation['valid']}")
                if validation['warnings']:
                    print(f"⚠️  Warnings: {len(validation['warnings'])}")
                if validation['errors']:
                    print(f"❌ Errors: {len(validation['errors'])}")

        elif args.summary:
            summary = engineer.get_codebase_summary()
            print("\n" + "="*80)
            print("CODEBASE SUMMARY")
            print("="*80)
            print(f"Python Files: {summary['total_files']}")
            print(f"Functions: {summary['total_functions']}")
            print(f"Classes: {summary['total_classes']}")
            print(f"Data Files: {summary['data_files']}")
            print(f"Data Directories: {summary['data_directories']}")

        elif args.reindex:
            engineer.code_analyzer._index_codebase()
            engineer.data_manager._index_data()
            print("✅ Codebase re-indexed")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()