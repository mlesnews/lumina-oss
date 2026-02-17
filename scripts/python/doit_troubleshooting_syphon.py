#!/usr/bin/env python3
"""
@DOIT #TROUBLESHOOTING #DECISIONING @SYPHON
Specialized execution script for Cursor Local AI issues.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from decisioning_troubleshooting_system import get_decisioning_system, TroubleshootingContext
    from r5_living_context_matrix import R5LivingContextMatrix
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    print("=" * 80)
    print("@DOIT #TROUBLESHOOTING #DECISIONING @SYPHON Execution")
    print("=" * 80)

    system = get_decisioning_system()

    # 1. Track the current situation
    issue = "Cursor reports 'Invalid Model' for 'Ultron' cluster name despite workspace settings update."
    symptoms = [
        "Error message: 'The model Ultron does not work with your current plan or api key'",
        "Workspace settings (.vscode/settings.json) have been updated with 'ultron' and 'Ultron' aliases",
        "Local Ollama is confirmed running at http://localhost:11434",
        "Model qwen2.5:72b is confirmed pulled and available"
    ]

    # 2. Add specific intelligence extraction questions (@SYPHON)
    questions = [
        system.track_question("@? Is Cursor prioritizing global user settings over workspace settings?", source="syphon"),
        system.track_question("@? Does the model ID 'Ultron' in the selector map exactly to the 'name' field in settings.json?", source="syphon"),
        system.track_question("@? Is 'localOnly: true' sufficient to bypass cloud plan checks in the latest Cursor version?", source="syphon"),
        system.track_question("@? Should the apiBase use the /v1 suffix or not?", source="syphon")
    ]

    # 3. Create troubleshooting context
    context = system.create_troubleshooting_context(
        issue=issue,
        symptoms=symptoms,
        questions=questions
    )

    # 4. Make decision
    print("\n🎯 Analyzing intelligence and making decision...")
    result = system.make_decision(context)

    print("-" * 80)
    print(f"DECISION: {result.decision}")
    print(f"RATIONALE:\n{result.rationale}")
    print("-" * 80)

    # 5. SYPHON Extra Action: Propose definitive fix
    print("\n🚀 @SYPHON Actionable Intelligence:")

    # We suspect Cursor might be case-sensitive or requires specific fields
    # Or it might need the OpenAI-compatible endpoint format

    recs = [
        "1. Recommend the user check GLOBAL settings (Ctrl+Shift+P -> Open User Settings JSON) for conflicting 'Ultron' definitions.",
        "2. Add model name variants like 'Ultron-Cluster' or 'ULTRON-LOCAL' to ensure uniqueness.",
        "3. Try adding the '/v1' suffix to the apiBase URL: http://localhost:11434/v1",
        "4. Force-refresh the model list in Cursor by toggling the 'Use Ollama' setting off and on."
    ]

    for rec in recs:
        print(f"   • {rec}")

    print("\n" + "=" * 80)
    print("EXECUTION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":


    main()