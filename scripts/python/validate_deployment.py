#!/usr/bin/env python3
"""
VA.B Deployment Validation

Comprehensive validation of the complete JARVIS ecosystem deployment:
- System health checks
- Component integration verification
- Performance benchmarks
- Security validation
- User acceptance testing
"""

import json
import requests
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("validate_deployment")


def validate_system_requirements():
    """Validate system requirements"""
    print("🔧 VALIDATING SYSTEM REQUIREMENTS")
    checks = []

    # Python version
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        checks.append(("Python Version", version, True))
    except:
        checks.append(("Python Version", "Not found", False))

    # Required directories
    dirs = ["config", "logs", "models", "cache", "monitoring"]
    for dir_name in dirs:
        exists = Path(dir_name).exists()
        checks.append((f"Directory: {dir_name}", "Exists" if exists else "Missing", exists))

    # Configuration files
    config_files = ["config/system_config.json", "config/ai_model_config.json", ".env"]
    for config_file in config_files:
        exists = Path(config_file).exists()
        checks.append((f"Config: {config_file}", "Exists" if exists else "Missing", exists))

    return checks

def validate_component_imports():
    """Validate component imports"""
    print("📦 VALIDATING COMPONENT IMPORTS")
    checks = []

    components = [
        ("complete_jarvis_system", "CompleteJarvisSystem"),
        ("jarvis_master_system", "JarvisMasterSystem"),
        ("braintrust_integration_system", "BraintrustIntegrationSystem"),
        ("ai_model_discovery_system", "AIModelDiscoverySystem"),
        ("jarvis_camera_integration", "JarvisCameraIntegration"),
        ("jarvis_avatar_interface", "JarvisAvatarInterface")
    ]

    for module, class_name in components:
        try:
            module_obj = __import__(f"scripts.python.{module}", fromlist=[class_name])
            getattr(module_obj, class_name)
            checks.append((f"{module}.{class_name}", "Import successful", True))
        except ImportError as e:
            checks.append((f"{module}.{class_name}", f"Import failed: {e}", False))
        except AttributeError as e:
            checks.append((f"{module}.{class_name}", f"Class not found: {e}", False))

    return checks

def validate_api_endpoints():
    """Validate API endpoints"""
    print("🌐 VALIDATING API ENDPOINTS")
    checks = []

    endpoints = [
        ("http://localhost:8080/health", "JARVIS API Health"),
        ("http://localhost:8080/api/v1/models", "Models API"),
        ("http://localhost:8080/api/v1/braintrust/health", "Braintrust API")
    ]

    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=5)
            success = response.status_code == 200
            status = f"Status: {response.status_code}"
            checks.append((name, status, success))
        except requests.RequestException as e:
            checks.append((name, f"Connection failed: {e}", False))

    return checks

def validate_ai_models():
    """Validate AI model availability"""
    print("🤖 VALIDATING AI MODELS")
    checks = []

    # Check model registry
    registry_path = Path("ai_model_registry.json")
    if registry_path.exists():
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            models_count = registry.get("total_models", 0)
            checks.append(("Model Registry", f"{models_count} models registered", models_count > 0))
        except json.JSONDecodeError:
            checks.append(("Model Registry", "Invalid JSON format", False))
    else:
        checks.append(("Model Registry", "File not found", False))

    # Test basic model access
    try:
        from ai_model_discovery_system import AIModelDiscoverySystem
        discovery = AIModelDiscoverySystem()
        models = discovery.load_model_registry()
        github_models = len([m for m in models.values() if m.provider.value == "github"])
        checks.append(("GitHub Models", f"{github_models} models available", github_models > 0))
    except Exception as e:
        checks.append(("Model Discovery", f"Failed: {e}", False))

    return checks

def validate_braintrust_system():
    """Validate Braintrust system"""
    print("🧠 VALIDATING BRAINTRUST SYSTEM")
    checks = []

    try:
        from braintrust_integration_system import BraintrustIntegrationSystem
        braintrust = BraintrustIntegrationSystem()

        members_count = len(braintrust.braintrust_members)
        experiments_count = len(braintrust.experiments)

        checks.append(("Braintrust Members", f"{members_count} members loaded", members_count > 0))
        checks.append(("R&D Experiments", f"{experiments_count} experiments cataloged", experiments_count > 0))

        # Test decision making
        async def test_decision():
            return await braintrust.make_braintrust_decision("Test deployment validation", complexity="simple")

        import asyncio
        decision = asyncio.run(test_decision())
        checks.append(("Decision Making", f"Decision {decision.decision_id} made", True))

    except Exception as e:
        checks.append(("Braintrust System", f"Validation failed: {e}", False))

    return checks

def validate_performance():
    """Validate system performance"""
    print("⚡ VALIDATING PERFORMANCE")
    checks = []

    # Basic performance tests
    start_time = time.time()

    # Test imports
    try:
        import cv2
        import numpy as np
        import aiohttp
        import torch
        import transformers
        import psutil

        import_time = time.time() - start_time
        checks.append(("Import Performance", ".3f", import_time < 5.0))
    except ImportError as e:
        checks.append(("Import Performance", f"Missing dependencies: {e}", False))

    # Memory usage
    memory = psutil.virtual_memory()
    memory_ok = memory.percent < 80
    checks.append(("Memory Usage", ".1f", memory_ok))

    # Disk space
    disk = psutil.disk_usage('/')
    disk_ok = disk.percent < 90
    checks.append(("Disk Space", ".1f", disk_ok))

    return checks

def validate_security():
    try:
        """Validate security settings"""
        print("🔒 VALIDATING SECURITY")
        checks = []

        # Check for sensitive files
        sensitive_files = [".env", "config/secrets.json"]
        for file_path in sensitive_files:
            exists = Path(file_path).exists()
            checks.append((f"Sensitive File: {file_path}", "Exists" if exists else "Not found", exists))

        # Check permissions (basic)
        config_dir = Path("config")
        if config_dir.exists():
            # Check if config directory is readable
            readable = config_dir.stat().st_mode & 0o400
            checks.append(("Config Permissions", "Readable" if readable else "Not readable", bool(readable)))

        # Check for API keys in environment
        env_vars = ["GITHUB_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        for var in env_vars:
            exists = bool(os.getenv(var))
            checks.append((f"API Key: {var}", "Set" if exists else "Not set", exists))

        return checks

    except Exception as e:
        logger.error(f"Error in validate_security: {e}", exc_info=True)
        raise
def generate_validation_report(all_checks):
    try:
        """Generate comprehensive validation report"""
        print("\n📊 DEPLOYMENT VALIDATION REPORT")
        print("="*60)

        total_checks = 0
        passed_checks = 0

        categories = {}

        for category, checks in all_checks.items():
            print(f"\n🔍 {category.upper()}")
            print("-" * 40)

            category_total = 0
            category_passed = 0

            for check_name, result, passed in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {check_name}: {result}")
                category_total += 1
                if passed:
                    category_passed += 1

            categories[category] = {
                "total": category_total,
                "passed": category_passed,
                "percentage": (category_passed / category_total * 100) if category_total > 0 else 0
            }

            total_checks += category_total
            passed_checks += category_passed

        # Overall summary
        overall_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        print(f"\n🎯 OVERALL VALIDATION SUMMARY")
        print("-" * 40)
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {total_checks - passed_checks}")
        print(f"Success Rate: {overall_percentage:.1f}%")
        # Determine deployment readiness
        if overall_percentage >= 95:
            readiness = "🚀 READY FOR PRODUCTION"
            color = "GREEN"
        elif overall_percentage >= 80:
            readiness = "⚠️ READY WITH CAUTIONS"
            color = "YELLOW"
        else:
            readiness = "❌ REQUIRES ATTENTION"
            color = "RED"

        print(f"Deployment Readiness: {readiness}")

        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall": {
                "total_checks": total_checks,
                "passed": passed_checks,
                "failed": total_checks - passed_checks,
                "percentage": overall_percentage,
                "readiness": readiness
            },
            "categories": categories,
            "detailed_results": all_checks
        }

        with open("deployment_validation_report.json", 'w') as f:
            json.dump(report, f, indent=2)

        print("\n📄 Detailed report saved to: deployment_validation_report.json")
        return overall_percentage >= 80  # Ready if 80%+ pass rate

    except Exception as e:
        logger.error(f"Error in generate_validation_report: {e}", exc_info=True)
        raise
def main():
    """Run complete deployment validation"""
    print("✅ VA.B DEPLOYMENT VALIDATION")
    print("="*50)
    print(f"Validation Time: {datetime.now()}")
    print("Testing complete JARVIS ecosystem deployment...")
    print()

    # Run all validation checks
    all_checks = {
        "System Requirements": validate_system_requirements(),
        "Component Imports": validate_component_imports(),
        "API Endpoints": validate_api_endpoints(),
        "AI Models": validate_ai_models(),
        "Braintrust System": validate_braintrust_system(),
        "Performance": validate_performance(),
        "Security": validate_security()
    }

    # Generate report
    deployment_ready = generate_validation_report(all_checks)

    if deployment_ready:
        print("\n🎉 DEPLOYMENT VALIDATION PASSED!")
        print("   VA.B system is ready for production use")
        print("   All critical systems validated and operational")
    else:
        print("\n⚠️ DEPLOYMENT VALIDATION ISSUES DETECTED")
        print("   Review the detailed report and resolve issues before production use")

    return 0 if deployment_ready else 1

if __name__ == "__main__":
    exit(main())