#!/usr/bin/env python3
"""
Fix Iron Legion Model Assignments
                    -LUM THE MODERN

Ensure each Iron Legion node has its intended specialized model.
"""
import requests
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("IronLegionModelFix")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("IronLegionModelFix")

# Intended model assignments from config
INTENDED_MODELS = {
    3001: {"model": "codellama:13b", "name": "Mark I - Code Expert"},
    3002: {"model": "llama3.2:11b", "name": "Mark II - General Purpose"},
    3003: {"model": "qwen2.5-coder:1.5b-base", "name": "Mark III - Quick Response"},
    3004: {"model": "llama3:8b", "name": "Mark IV - Balanced Expert"},
    3005: {"model": "mistral:7b", "name": "Mark V - Reasoning Expert"},
    3006: {"model": "mixtral:8x7b", "name": "Mark VI - Complex Expert"},
    3007: {"model": "gemma:2b", "name": "Mark VII - Fallback Expert"}
}

def check_current_models() -> Dict[int, List[str]]:
    """Check what models are currently loaded on each node"""
    current = {}

    for port in range(3001, 3008):
        try:
            # Try Ollama API first
            r = requests.get(f"http://<NAS_IP>:{port}/api/tags", timeout=5)
            if r.status_code == 200:
                models = [m.get("name", "") for m in r.json().get("models", [])]
                current[port] = models
            else:
                # Try OpenAI-compatible API
                r = requests.get(f"http://<NAS_IP>:{port}/", timeout=5)
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if "model" in data:
                            current[port] = [data["model"]]
                    except:
                        current[port] = []
        except Exception as e:
            logger.warning(f"   Port {port}: Error - {e}")
            current[port] = []

    return current

def analyze_mismatches(current: Dict[int, List[str]]) -> List[Dict]:
    """Analyze mismatches between intended and current models"""
    mismatches = []

    for port, intended in INTENDED_MODELS.items():
        current_models = current.get(port, [])
        intended_model = intended["model"]

        # Handle model name variations
        intended_variants = [
            intended_model,
            intended_model.replace("-base", ""),
            intended_model.replace(":8x7b", ""),
            intended_model.split(":")[0]  # Just the base name
        ]

        has_intended = any(
            any(variant in model or model in variant for variant in intended_variants)
            for model in current_models
        )

        if not has_intended:
            mismatches.append({
                "port": port,
                "name": intended["name"],
                "intended": intended_model,
                "current": current_models,
                "status": "MISMATCH"
            })
        else:
            logger.info(f"   ✅ {intended['name']}: Has intended model")

    return mismatches

def generate_fix_instructions(mismatches: List[Dict]) -> List[str]:
    """Generate instructions to fix model assignments"""
    instructions = []

    for mismatch in mismatches:
        port = mismatch["port"]
        intended = mismatch["intended"]
        name = mismatch["name"]

        instructions.append(f"\n📋 {name} (Port {port}):")
        instructions.append(f"   Intended: {intended}")
        instructions.append(f"   Current: {', '.join(mismatch['current']) if mismatch['current'] else 'None'}")
        instructions.append(f"   Action: Pull model '{intended}' to this node")
        instructions.append(f"   Command: ssh to KAIJU and run: ollama pull {intended}")
        instructions.append(f"   Or: Configure Docker container on port {port} to use {intended}")

    return instructions

def main():
    try:
        logger.info("=" * 80)
        logger.info("🔧 IRON LEGION MODEL ASSIGNMENT ANALYSIS")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

        # Check current models
        logger.info("\n📊 Checking current model assignments...")
        current_models = check_current_models()

        for port, models in current_models.items():
            name = INTENDED_MODELS[port]["name"]
            logger.info(f"   {name} (port {port}): {', '.join(models) if models else 'No models'}")

        # Analyze mismatches
        logger.info("\n🔍 Analyzing mismatches...")
        mismatches = analyze_mismatches(current_models)

        if mismatches:
            logger.warning(f"\n⚠️  Found {len(mismatches)} mismatches:")
            for mismatch in mismatches:
                logger.warning(f"   {mismatch['name']}: Expected '{mismatch['intended']}', found {mismatch['current']}")

            # Generate fix instructions
            logger.info("\n" + "=" * 80)
            logger.info("🔧 FIX INSTRUCTIONS")
            logger.info("=" * 80)
            instructions = generate_fix_instructions(mismatches)
            for instruction in instructions:
                logger.info(instruction)
        else:
            logger.info("\n✅ All nodes have correct model assignments!")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Total Nodes: 7")
        logger.info(f"   Correct: {7 - len(mismatches)}")
        logger.info(f"   Mismatches: {len(mismatches)}")
        logger.info("=" * 80)

        # Save report
        report = {
            "analysis_date": str(Path(__file__).stat().st_mtime),
            "intended_models": INTENDED_MODELS,
            "current_models": current_models,
            "mismatches": mismatches,
            "fix_instructions": generate_fix_instructions(mismatches) if mismatches else []
        }

        report_path = project_root / "data" / "iron_legion_model_analysis.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"\n💾 Report saved: {report_path}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()