#!/usr/bin/env python3
"""
JARVIS Configure KAIJU Ollama to Use D Drive Models

The 7 models are downloaded on KAIJU's D drive but Ollama doesn't see them.
This script helps configure Ollama to use the D drive models directory.

Tags: #KAIJU #OLLAMA #MODELS #D-DRIVE #IRON-LEGION
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISConfigureKAIJUModels")


class JARVISConfigureKAIJUOllamaModels:
    """
    Configure Ollama on KAIJU to use D drive models
    """

    def __init__(self):
        self.logger = logger
        self.kaiju_host = "<NAS_PRIMARY_IP>"

        # Common D drive model paths on KAIJU
        self.possible_model_paths = [
            r"D:\Ollama\models",
            r"D:\models",
            r"D:\Program Files\Ollama\models",
            r"D:\Dropbox\my_projects\.lumina\models",
        ]

        self.logger.info("✅ JARVIS KAIJU Ollama Model Configurator initialized")

    def generate_instructions(self) -> Dict[str, Any]:
        """
        Generate instructions for configuring Ollama on KAIJU to use D drive models
        """
        self.logger.info("="*80)
        self.logger.info("KAIJU OLLAMA MODEL CONFIGURATION INSTRUCTIONS")
        self.logger.info("="*80)
        self.logger.info("")

        instructions = {
            "timestamp": datetime.now().isoformat(),
            "problem": "7 models on D drive but Ollama doesn't see them",
            "solution_options": [],
            "recommended_solution": None
        }

        # Solution 1: Set OLLAMA_MODELS environment variable
        solution1 = {
            "method": "Set OLLAMA_MODELS Environment Variable",
            "description": "Configure Ollama to use D drive models directory",
            "steps": [
                "1. SSH into KAIJU (<NAS_PRIMARY_IP>)",
                "2. Find the exact path to models on D drive (e.g., D:\\Ollama\\models or D:\\models)",
                "3. Set OLLAMA_MODELS environment variable:",
                "   Windows: setx OLLAMA_MODELS \"D:\\Ollama\\models\"",
                "   Or in System Properties → Environment Variables",
                "4. Restart Ollama service",
                "5. Verify: ollama list (should show all 7 models)"
            ],
            "pros": [
                "Simple configuration",
                "Ollama will automatically use D drive models",
                "No need to copy/move files"
            ],
            "cons": [
                "Requires Ollama restart",
                "Need to know exact path"
            ]
        }

        # Solution 2: Import models into Ollama
        solution2 = {
            "method": "Import Models into Ollama",
            "description": "Use ollama import or copy models to Ollama's default location",
            "steps": [
                "1. SSH into KAIJU",
                "2. Find Ollama's default model location:",
                "   Windows: %USERPROFILE%\\.ollama\\models",
                "   Or check: ollama show (model name) --path",
                "3. Copy models from D drive to Ollama location:",
                "   robocopy \"D:\\Ollama\\models\" \"%USERPROFILE%\\.ollama\\models\" /E",
                "4. Or use ollama import for each model",
                "5. Verify: ollama list"
            ],
            "pros": [
                "Models in standard location",
                "No environment variable needed"
            ],
            "cons": [
                "Requires copying files (duplicates storage)",
                "Takes time to copy"
            ]
        }

        # Solution 3: Symbolic link
        solution3 = {
            "method": "Create Symbolic Link",
            "description": "Link Ollama's model directory to D drive",
            "steps": [
                "1. SSH into KAIJU",
                "2. Find Ollama's default model location",
                "3. Create symbolic link:",
                "   mklink /D \"%USERPROFILE%\\.ollama\\models\" \"D:\\Ollama\\models\"",
                "4. Restart Ollama",
                "5. Verify: ollama list"
            ],
            "pros": [
                "No duplication",
                "Models stay on D drive",
                "Ollama sees them automatically"
            ],
            "cons": [
                "Requires admin rights",
                "Symbolic links can be tricky"
            ]
        }

        instructions["solution_options"] = [solution1, solution2, solution3]
        instructions["recommended_solution"] = solution1  # Easiest

        return instructions

    def create_configure_script(self, model_path: str = r"D:\Ollama\models") -> str:
        """
        Create a PowerShell script to configure Ollama on KAIJU
        """
        script = f'''# Configure Ollama on KAIJU to Use D Drive Models
# Run this script on KAIJU (<NAS_PRIMARY_IP>)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "KAIJU Ollama Model Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Model path on D drive
$MODEL_PATH = "{model_path}"

# Check if path exists
if (-not (Test-Path $MODEL_PATH)) {{
    Write-Host "❌ Model path not found: $MODEL_PATH" -ForegroundColor Red
    Write-Host "Please verify the correct path to models on D drive" -ForegroundColor Yellow
    exit 1
}}

Write-Host "✅ Model path found: $MODEL_PATH" -ForegroundColor Green
Write-Host ""

# Set OLLAMA_MODELS environment variable (User level)
Write-Host "Setting OLLAMA_MODELS environment variable..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $MODEL_PATH, "User")

# Also set for current session
$env:OLLAMA_MODELS = $MODEL_PATH

Write-Host "✅ OLLAMA_MODELS set to: $MODEL_PATH" -ForegroundColor Green
Write-Host ""

# Restart Ollama service
Write-Host "Restarting Ollama service..." -ForegroundColor Yellow
try {{
    Restart-Service -Name "Ollama" -ErrorAction Stop
    Write-Host "✅ Ollama service restarted" -ForegroundColor Green
}} catch {{
    Write-Host "⚠️  Could not restart Ollama service: $_" -ForegroundColor Yellow
    Write-Host "   You may need to restart Ollama manually" -ForegroundColor Yellow
}}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Wait a moment for service to start
Start-Sleep -Seconds 3

# Check Ollama
try {{
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    $models = ($response.Content | ConvertFrom-Json).models
    Write-Host "✅ Ollama is running" -ForegroundColor Green
    Write-Host "Available models: $($models.Count)" -ForegroundColor Cyan
    $models | ForEach-Object {{
        Write-Host "  - $($_.name)" -ForegroundColor White
    }}
}} catch {{
    Write-Host "❌ Ollama not responding: $_" -ForegroundColor Red
    Write-Host "   Check if Ollama service is running" -ForegroundColor Yellow
}}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Verify all 7 models appear in 'ollama list'" -ForegroundColor White
Write-Host "2. If models don't appear, check:" -ForegroundColor White
Write-Host "   - Model path is correct" -ForegroundColor Gray
Write-Host "   - Models are in correct format (Ollama format)" -ForegroundColor Gray
Write-Host "   - Ollama service has access to D drive" -ForegroundColor Gray
Write-Host "3. Test from laptop: curl http://<NAS_PRIMARY_IP>:11434/api/tags" -ForegroundColor White
Write-Host ""
'''
        return script


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Configure KAIJU Ollama to use D drive models")
        parser.add_argument("--model-path", default=r"D:\Ollama\models", help="Path to models on D drive")
        parser.add_argument("--generate-script", action="store_true", help="Generate PowerShell configuration script")

        args = parser.parse_args()

        configurator = JARVISConfigureKAIJUOllamaModels()

        if args.generate_script:
            script = configurator.create_configure_script(args.model_path)
            script_path = Path(__file__).parent.parent / "powershell" / "configure_kaiju_ollama_models.ps1"
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.write_text(script, encoding='utf-8')
            print(f"✅ Configuration script created: {script_path}")
            print("")
            print("To use:")
            print(f"  1. Copy script to KAIJU (<NAS_PRIMARY_IP>)")
            print(f"  2. Run on KAIJU: .\\configure_kaiju_ollama_models.ps1")
            print(f"  3. Or SSH and run remotely")
        else:
            instructions = configurator.generate_instructions()
            print(json.dumps(instructions, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()