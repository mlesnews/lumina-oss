#!/usr/bin/env python3
"""
"Tinker, Tailor, Soldier, Spy" - Systematic Verification of Complete Model Loadout
Verifies all 7 LLM models are properly configured with roles and responsibilities
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("verify_complete_model_loadout")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def load_model_mapping(project_root: Path) -> Dict[str, Any]:
    try:
        """Load the model mapping configuration"""
        mapping_path = project_root / "config" / "ollama_model_mapping.json"

        if not mapping_path.exists():
            print(f"❌ ERROR: Model mapping not found: {mapping_path}")
            sys.exit(1)

        with open(mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except Exception as e:
        logger.error(f"Error in load_model_mapping: {e}", exc_info=True)
        raise
def verify_model_structure(model_mapping: Dict[str, Any]) -> bool:
    """Verify model mapping structure is complete"""
    print("=" * 60)
    print("VERIFICATION 1: Model Structure")
    print("=" * 60)

    required_fields = [
        "huggingface_repo", "gguf_filename", "model_name", "size_gb",
        "role", "responsibility", "decision_context", "intent",
        "complexity_level", "context_size", "description"
    ]

    models = model_mapping.get("models", {})
    total_expected = model_mapping.get("total_models", 0)

    print(f"Expected models: {total_expected}")
    print(f"Found models: {len(models)}")
    print()

    if len(models) != total_expected:
        print(f"❌ MISMATCH: Expected {total_expected} models, found {len(models)}")
        return False

    all_valid = True
    for model_key, model_info in models.items():
        missing_fields = [f for f in required_fields if f not in model_info]
        if missing_fields:
            print(f"❌ {model_key}: Missing fields: {', '.join(missing_fields)}")
            all_valid = False
        else:
            print(f"✓ {model_key}: All required fields present")

    print()
    return all_valid

def verify_roles_and_responsibilities(model_mapping: Dict[str, Any]) -> bool:
    """Verify each model has unique role and clear responsibility"""
    print("=" * 60)
    print("VERIFICATION 2: Roles and Responsibilities")
    print("=" * 60)

    models = model_mapping.get("models", {})
    roles = {}
    responsibilities = {}

    all_valid = True
    for model_key, model_info in models.items():
        role = model_info.get("role")
        responsibility = model_info.get("responsibility")

        if not role:
            print(f"❌ {model_key}: Missing role")
            all_valid = False
        elif role in roles:
            print(f"⚠ {model_key}: Role '{role}' already assigned to {roles[role]}")
        else:
            roles[role] = model_key
            print(f"✓ {model_key}: Role '{role}'")

        if not responsibility:
            print(f"❌ {model_key}: Missing responsibility")
            all_valid = False
        else:
            print(f"  Responsibility: {responsibility}")

    print()
    return all_valid

def verify_decision_framework(model_mapping: Dict[str, Any]) -> bool:
    """Verify decision-making framework is complete"""
    print("=" * 60)
    print("VERIFICATION 3: Decision-Making Framework")
    print("=" * 60)

    framework = model_mapping.get("decision_making_framework", {})

    required_sections = ["by_complexity", "by_intent", "by_context_size"]
    all_valid = True

    for section in required_sections:
        if section not in framework:
            print(f"❌ Missing section: {section}")
            all_valid = False
        else:
            print(f"✓ {section}: {len(framework[section])} categories")
            for category, models in framework[section].items():
                print(f"  {category}: {', '.join(models)}")

    print()
    return all_valid

def verify_roles_responsibilities_mapping(model_mapping: Dict[str, Any]) -> bool:
    """Verify roles and responsibilities mapping"""
    print("=" * 60)
    print("VERIFICATION 4: Roles & Responsibilities Mapping")
    print("=" * 60)

    roles_map = model_mapping.get("roles_and_responsibilities", {})
    models = model_mapping.get("models", {})

    if not roles_map:
        print("❌ Missing roles_and_responsibilities section")
        return False

    all_valid = True
    for role_name, role_info in roles_map.items():
        model_name = role_info.get("model")
        if not model_name:
            print(f"❌ {role_name}: Missing model")
            all_valid = False
        elif model_name not in models:
            print(f"❌ {role_name}: Model '{model_name}' not found in models")
            all_valid = False
        else:
            print(f"✓ {role_name}: {model_name}")
            print(f"  Use cases: {', '.join(role_info.get('use_cases', []))}")
            print(f"  Decision context: {role_info.get('decision_context')}")

    print()
    return all_valid

def verify_model_coverage(model_mapping: Dict[str, Any]) -> bool:
    """Verify all models are covered in decision framework"""
    print("=" * 60)
    print("VERIFICATION 5: Model Coverage")
    print("=" * 60)

    models = set(model_mapping.get("models", {}).keys())
    framework = model_mapping.get("decision_making_framework", {})

    all_models_in_framework = set()
    for section in framework.values():
        for model_list in section.values():
            all_models_in_framework.update(model_list)

    missing = models - all_models_in_framework
    extra = all_models_in_framework - models

    if missing:
        print(f"❌ Models not in framework: {', '.join(missing)}")
        return False

    if extra:
        print(f"⚠ Models in framework but not in models: {', '.join(extra)}")

    print(f"✓ All {len(models)} models covered in decision framework")
    print()
    return True

def main():
    """Main verification function"""
    project_root = Path(__file__).parent.parent.parent

    print("=" * 60)
    print("TINKER, TAILOR, SOLDIER, SPY - Model Loadout Verification")
    print("=" * 60)
    print()

    # Load mapping
    model_mapping = load_model_mapping(project_root)
    print(f"✓ Loaded model mapping: {model_mapping.get('total_models')} models")
    print()

    # Run all verifications
    verifications = [
        ("Model Structure", verify_model_structure),
        ("Roles and Responsibilities", verify_roles_and_responsibilities),
        ("Decision Framework", verify_decision_framework),
        ("Roles Mapping", verify_roles_responsibilities_mapping),
        ("Model Coverage", verify_model_coverage),
    ]

    results = []
    for name, verify_func in verifications:
        try:
            result = verify_func(model_mapping)
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append((name, False))

    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print()

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False

    print()
    if all_passed:
        print("✓ ALL VERIFICATIONS PASSED")
        print("Complete model loadout is properly configured")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("Please review and fix the issues above")
        return 1

if __name__ == "__main__":



    sys.exit(main())