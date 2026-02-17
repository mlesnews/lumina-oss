#!/usr/bin/env python3
"""
Fix Invalid Model Error for @HOMELAB Localhosts

Diagnoses and fixes "INVALID MODEL" errors for local AI models on all @HOMELAB localhosts:
- Ollama (localhost:11434)
- Iron Legion (localhost:3000)

Tags: #HOMELAB #INVALID_MODEL #FIX #OLLAMA #IRON_LEGION @JARVIS @LUMINA
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixHomelabInvalidModel")


class HomelabModelValidator:
    """Validate and fix invalid model errors on homelab localhosts"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.data_dir = project_root / "data" / "homelab_model_validation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.endpoints = {
            "ollama": "http://localhost:11434",
            "iron_legion": "http://localhost:3000"
        }

        self.available_models = {
            "ollama": [],
            "iron_legion": []
        }

        self.invalid_models_found = []
        self.fixes_applied = []

    def check_ollama_models(self) -> Dict[str, Any]:
        """Check available Ollama models"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING OLLAMA MODELS (localhost:11434)")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "endpoint": self.endpoints["ollama"],
            "accessible": False,
            "models": [],
            "error": None
        }

        try:
            response = requests.get(
                f"{self.endpoints['ollama']}/api/tags",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                result["accessible"] = True
                result["models"] = [model.get("name", "") for model in models]
                self.available_models["ollama"] = result["models"]

                logger.info(f"✅ Ollama accessible: {self.endpoints['ollama']}")
                logger.info(f"   Found {len(result['models'])} models:")
                for model in result["models"]:
                    logger.info(f"      - {model}")
            else:
                result["error"] = f"HTTP {response.status_code}"
                logger.warning(f"   ⚠️  Ollama returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection refused - Ollama not running"
            logger.warning(f"   ❌ Ollama not accessible: Connection refused")
        except requests.exceptions.Timeout:
            result["error"] = "Timeout - Ollama not responding"
            logger.warning(f"   ❌ Ollama timeout")
        except Exception as e:
            result["error"] = str(e)
            logger.warning(f"   ❌ Ollama error: {e}")

        logger.info("")
        return result

    def check_iron_legion_models(self) -> Dict[str, Any]:
        """Check available Iron Legion models"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING IRON LEGION MODELS (localhost:3000)")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "endpoint": self.endpoints["iron_legion"],
            "accessible": False,
            "models": [],
            "error": None
        }

        try:
            response = requests.get(
                f"{self.endpoints['iron_legion']}/v1/models",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                result["accessible"] = True
                result["models"] = [model.get("id", "") for model in models]
                self.available_models["iron_legion"] = result["models"]

                logger.info(f"✅ Iron Legion accessible: {self.endpoints['iron_legion']}")
                logger.info(f"   Found {len(result['models'])} models:")
                for model in result["models"]:
                    logger.info(f"      - {model}")
            else:
                result["error"] = f"HTTP {response.status_code}"
                logger.warning(f"   ⚠️  Iron Legion returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection refused - Iron Legion not running"
            logger.warning(f"   ❌ Iron Legion not accessible: Connection refused")
        except requests.exceptions.Timeout:
            result["error"] = "Timeout - Iron Legion not responding"
            logger.warning(f"   ❌ Iron Legion timeout")
        except Exception as e:
            result["error"] = str(e)
            logger.warning(f"   ❌ Iron Legion error: {e}")

        logger.info("")
        return result

    def scan_config_files_for_invalid_models(self) -> List[Dict[str, Any]]:
        """Scan config files for invalid model references"""
        logger.info("=" * 80)
        logger.info("🔍 SCANNING CONFIG FILES FOR INVALID MODELS")
        logger.info("=" * 80)
        logger.info("")

        invalid_refs = []

        # Config files to check
        config_files = [
            "local_ai_config.json",
            "iron_legion_cluster_config.json",
            "mcp_config_localhost.json",
            "homelab_mcp_hybrid_config.json",
            "cursor_ultron_model_config.json",
            "ollama_model_mapping.json"
        ]

        for config_file in config_files:
            config_path = self.config_dir / config_file
            if not config_path.exists():
                continue

            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Recursively search for model references
                invalid_in_file = self._find_invalid_models_in_dict(
                    config, 
                    config_path,
                    ""
                )

                if invalid_in_file:
                    invalid_refs.extend(invalid_in_file)
                    logger.info(f"   ⚠️  {config_file}: Found {len(invalid_in_file)} invalid model references")
            except Exception as e:
                logger.warning(f"   ⚠️  Error reading {config_file}: {e}")

        if not invalid_refs:
            logger.info("   ✅ No invalid model references found in config files")

        logger.info("")
        self.invalid_models_found = invalid_refs
        return invalid_refs

    def _find_invalid_models_in_dict(self, obj: Any, file_path: Path, path: str) -> List[Dict[str, Any]]:
        """Recursively find invalid model references in dict/list"""
        invalid_refs = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key

                # Check if this is a model field
                if key.lower() in ["model", "model_name", "model_id", "name"] and isinstance(value, str):
                    # Check if model is invalid
                    if self._is_invalid_model(value):
                        invalid_refs.append({
                            "file": str(file_path),
                            "path": current_path,
                            "value": value,
                            "type": "invalid_model_name"
                        })

                # Recurse
                invalid_refs.extend(self._find_invalid_models_in_dict(value, file_path, current_path))

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                invalid_refs.extend(self._find_invalid_models_in_dict(item, file_path, current_path))

        return invalid_refs

    def _is_invalid_model(self, model_name: str) -> bool:
        """Check if model name is invalid"""
        if not model_name or not isinstance(model_name, str):
            return False

        # Check if model exists in available models
        model_lower = model_name.lower()

        # Check Ollama models
        ollama_models = [m.lower() for m in self.available_models["ollama"]]
        if model_lower in ollama_models:
            return False

        # Check Iron Legion models
        iron_legion_models = [m.lower() for m in self.available_models["iron_legion"]]
        if model_lower in iron_legion_models:
            return False

        # Known invalid patterns
        invalid_patterns = [
            "llama3.2:3b",  # Invalid format
            "invalid",
            "none",
            "null",
            "undefined"
        ]

        if any(pattern in model_lower for pattern in invalid_patterns):
            return True

        # If we have available models but this one isn't in the list, it might be invalid
        all_available = ollama_models + iron_legion_models
        if all_available and model_lower not in all_available:
            # But allow common valid patterns
            valid_patterns = ["auto", "default", "primary", "secondary"]
            if any(pattern in model_lower for pattern in valid_patterns):
                return False
            # If endpoint is accessible but model not found, it's likely invalid
            if self.available_models["ollama"] or self.available_models["iron_legion"]:
                return True

        return False

    def fix_invalid_models(self) -> Dict[str, Any]:
        """Fix invalid model references"""
        logger.info("=" * 80)
        logger.info("🔧 FIXING INVALID MODEL REFERENCES")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "files_checked": 0,
            "files_fixed": 0,
            "models_fixed": 0,
            "errors": []
        }

        # Group invalid refs by file
        files_to_fix = {}
        for ref in self.invalid_models_found:
            file_path = ref["file"]
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(ref)

        for file_path, refs in files_to_fix.items():
            results["files_checked"] += 1
            logger.info(f"Fixing {Path(file_path).name}...")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                original_config = json.dumps(config, indent=2)
                fixed = False

                # Fix each invalid reference
                for ref in refs:
                    path_parts = ref["path"].split(".")
                    current = config

                    # Navigate to the value
                    for part in path_parts[:-1]:
                        if "[" in part:
                            key, index = part.split("[")
                            index = int(index.rstrip("]"))
                            current = current[key][index]
                        else:
                            current = current[part]

                    # Get the key to fix
                    last_part = path_parts[-1]
                    old_value = current[last_part]

                    # Determine replacement
                    new_value = self._get_replacement_model(old_value)

                    if new_value and new_value != old_value:
                        current[last_part] = new_value
                        fixed = True
                        results["models_fixed"] += 1
                        logger.info(f"   ✅ Fixed: {ref['path']} = '{old_value}' → '{new_value}'")

                # Save if changed
                if fixed:
                    new_config = json.dumps(config, indent=2)
                    if new_config != original_config:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_config)
                        results["files_fixed"] += 1
                        self.fixes_applied.append(file_path)
                        logger.info(f"   ✅ File fixed: {Path(file_path).name}")
            except Exception as e:
                error_msg = f"Error fixing {file_path}: {e}"
                results["errors"].append(error_msg)
                logger.warning(f"   ⚠️  {error_msg}")

        logger.info("")
        return results

    def _get_replacement_model(self, invalid_model: str) -> Optional[str]:
        """Get replacement model for invalid model name"""
        # Try to find a suitable replacement from available models
        available = self.available_models["ollama"] + self.available_models["iron_legion"]

        if not available:
            # No models available, use "auto" as fallback
            return "auto"

        # Try to match based on model type
        invalid_lower = invalid_model.lower()

        # Code models
        if "code" in invalid_lower or "coder" in invalid_lower:
            code_models = [m for m in available if "code" in m.lower() or "coder" in m.lower()]
            if code_models:
                return code_models[0]

        # General models
        if "llama" in invalid_lower:
            llama_models = [m for m in available if "llama" in m.lower()]
            if llama_models:
                return llama_models[0]

        # Default to first available model
        return available[0] if available else "auto"

    def generate_report(self) -> Dict[str, Any]:
        try:
            """Generate diagnostic and fix report"""
            logger.info("=" * 80)
            logger.info("📊 GENERATING REPORT")
            logger.info("=" * 80)
            logger.info("")

            # Check models
            ollama_result = self.check_ollama_models()
            iron_legion_result = self.check_iron_legion_models()

            # Scan for invalid models
            invalid_refs = self.scan_config_files_for_invalid_models()

            # Fix if requested
            fix_results = None
            if invalid_refs:
                fix_results = self.fix_invalid_models()

            report = {
                "timestamp": datetime.now().isoformat(),
                "ollama": ollama_result,
                "iron_legion": iron_legion_result,
                "invalid_models_found": len(invalid_refs),
                "invalid_references": invalid_refs,
                "fix_results": fix_results,
                "recommendations": []
            }

            # Generate recommendations
            if not ollama_result["accessible"]:
                report["recommendations"].append({
                    "issue": "Ollama not accessible",
                    "action": "Start Ollama service: docker-compose up -d ollama or start Ollama Desktop",
                    "priority": "HIGH"
                })

            if not iron_legion_result["accessible"]:
                report["recommendations"].append({
                    "issue": "Iron Legion not accessible",
                    "action": "Start Iron Legion cluster: docker-compose up -d iron-legion",
                    "priority": "HIGH"
                })

            if invalid_refs:
                report["recommendations"].append({
                    "issue": "Invalid model references found",
                    "action": "Run fix command to automatically replace invalid models",
                    "priority": "MEDIUM"
                })

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.data_dir / f"model_validation_{timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"💾 Report saved: {report_file}")
            logger.info("")

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix Invalid Model Error for @HOMELAB Localhosts")
    parser.add_argument("action", choices=["check", "fix", "report"], 
                       help="Action to perform: check (diagnose), fix (auto-fix), report (full report)")

    args = parser.parse_args()

    validator = HomelabModelValidator(project_root)

    if args.action == "check":
        logger.info("🔍 Checking local AI models...")
        ollama_result = validator.check_ollama_models()
        iron_legion_result = validator.check_iron_legion_models()

        print("\n" + "=" * 80)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        print()
        print(f"Ollama (localhost:11434): {'✅ Accessible' if ollama_result['accessible'] else '❌ Not accessible'}")
        if ollama_result['accessible']:
            print(f"   Models: {len(ollama_result['models'])}")
        else:
            print(f"   Error: {ollama_result.get('error', 'Unknown')}")
        print()
        print(f"Iron Legion (localhost:3000): {'✅ Accessible' if iron_legion_result['accessible'] else '❌ Not accessible'}")
        if iron_legion_result['accessible']:
            print(f"   Models: {len(iron_legion_result['models'])}")
        else:
            print(f"   Error: {iron_legion_result.get('error', 'Unknown')}")
        print()

    elif args.action == "fix":
        logger.info("🔧 Fixing invalid model errors...")
        validator.check_ollama_models()
        validator.check_iron_legion_models()
        validator.scan_config_files_for_invalid_models()
        fix_results = validator.fix_invalid_models()

        print("\n" + "=" * 80)
        print("🔧 FIX RESULTS")
        print("=" * 80)
        print()
        print(f"Files checked: {fix_results['files_checked']}")
        print(f"Files fixed: {fix_results['files_fixed']}")
        print(f"Models fixed: {fix_results['models_fixed']}")
        if fix_results['errors']:
            print(f"\nErrors: {len(fix_results['errors'])}")
            for error in fix_results['errors']:
                print(f"  - {error}")
        print()

    elif args.action == "report":
        report = validator.generate_report()

        print("\n" + "=" * 80)
        print("📊 FULL DIAGNOSTIC REPORT")
        print("=" * 80)
        print()
        print(f"Ollama: {'✅' if report['ollama']['accessible'] else '❌'} {len(report['ollama']['models'])} models")
        print(f"Iron Legion: {'✅' if report['iron_legion']['accessible'] else '❌'} {len(report['iron_legion']['models'])} models")
        print(f"Invalid references found: {report['invalid_models_found']}")
        if report['recommendations']:
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  [{rec['priority']}] {rec['issue']}: {rec['action']}")
        print()


if __name__ == "__main__":


    main()