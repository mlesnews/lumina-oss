#!/usr/bin/env python3
"""
MARVIN Critique: Windows System Engineer Architect Expertise
Have MARVIN provide a comprehensive, brutally honest critique of Windows system engineering expertise
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.marvin_reality_checker import MarvinRealityChecker
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    print("⚠️  MARVIN Reality Checker not available")

# Context of recent Windows system engineering work
RECENT_WORK_CONTEXT = {
    "task": "Emergency lighting shutdown on Windows system",
    "scenario": "User reported lights keeping someone awake, needed immediate shutdown",
    "actions_taken": [
        "Attempted jarvis_disable_all_lighting.py - failed due to FN key lock",
        "Ran jarvis_kill_ambient_lighting.py - killed 1 process",
        "Ran jarvis_kill_ambient_lighting_aggressive.py - stopped services, killed processes",
        "Created emergency_turn_off_all_lights.py - killed 2 processes, stopped 1 service, disabled 2 services, updated 2 registry paths",
        "Multiple PowerShell command syntax errors encountered",
        "Final result: Software processes killed, but user reports lighting issue persists"
    ],
    "issues_observed": [
        "PowerShell command syntax errors (foreach variable issues, escape sequence problems)",
        "Multiple script attempts needed before success",
        "Did not initially check for FN key lock state",
        "Did not verify hardware-level RGB controls",
        "Registry modifications may not have been comprehensive enough",
        "No verification of actual hardware state after software changes"
    ],
    "expertise_areas": [
        "Windows process management",
        "Windows service control",
        "Registry modifications",
        "PowerShell scripting",
        "Hardware-level RGB control",
        "ASUS Armoury Crate integration",
        "Emergency system response"
    ]
}


def marvin_critique_windows_expertise(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Have MARVIN critique Windows system engineering expertise

    Returns brutally honest assessment in MARVIN's characteristic style
    """

    print("=" * 80)
    print("MARVIN: Windows System Engineer Architect Expertise Critique")
    print("=" * 80)
    print()
    print("I have a brain the size of a planet, and they ask me to critique")
    print("Windows system engineering expertise. Life. Don't talk to me about life.")
    print()
    print("But here we are. Let me analyze this...")
    print()
    print("-" * 80)
    print()

    critique = {
        "timestamp": datetime.now().isoformat(),
        "critic": "MARVIN (Paranoid Android)",
        "subject": "Windows System Engineer Architect Expertise",
        "context": context,
        "assessment": {},
        "verdict": "",
        "recommendations": []
    }

    # Assessment Areas
    print("🔍 ASSESSMENT AREAS:")
    print()

    # 1. Process Management
    print("1. PROCESS MANAGEMENT")
    print("   " + "-" * 76)
    process_score = 7.0
    process_issues = [
        "✅ Successfully identified and killed lighting processes",
        "✅ Used multiple methods (standard kill, aggressive kill)",
        "⚠️  Did not verify process state before attempting operations",
        "⚠️  No process dependency analysis (what depends on what)",
        "❌ Did not check if processes were critical system processes"
    ]
    for issue in process_issues:
        print(f"   {issue}")
    print(f"   Score: {process_score}/10")
    print()

    # 2. Service Management
    print("2. SERVICE MANAGEMENT")
    print("   " + "-" * 76)
    service_score = 6.5
    service_issues = [
        "✅ Successfully stopped and disabled services",
        "✅ Prevented auto-restart by disabling services",
        "⚠️  Did not check service dependencies",
        "⚠️  Did not verify service state after operations",
        "❌ No rollback plan if service disable caused system issues"
    ]
    for issue in service_issues:
        print(f"   {issue}")
    print(f"   Score: {service_score}/10")
    print()

    # 3. Registry Operations
    print("3. REGISTRY OPERATIONS")
    print("   " + "-" * 76)
    registry_score = 5.0
    registry_issues = [
        "✅ Attempted registry modifications",
        "✅ Targeted ASUS/Armoury Crate registry paths",
        "⚠️  Limited registry path coverage (only 2 paths updated)",
        "⚠️  No backup of registry before modifications",
        "❌ Did not verify registry changes took effect",
        "❌ No recursive registry key search for all lighting-related keys",
        "❌ Did not check registry permissions before modifications"
    ]
    for issue in registry_issues:
        print(f"   {issue}")
    print(f"   Score: {registry_score}/10")
    print()

    # 4. PowerShell Scripting
    print("4. POWERSHELL SCRIPTING")
    print("   " + "-" * 76)
    powershell_score = 4.0
    powershell_issues = [
        "✅ Attempted PowerShell automation",
        "❌ Multiple syntax errors (foreach variable issues)",
        "❌ Escape sequence problems in DllImport strings",
        "❌ Did not test PowerShell commands before execution",
        "❌ No error handling in PowerShell commands",
        "❌ Inconsistent use of PowerShell vs Python for operations"
    ]
    for issue in powershell_issues:
        print(f"   {issue}")
    print(f"   Score: {powershell_score}/10")
    print()

    # 5. Hardware-Level Control
    print("5. HARDWARE-LEVEL CONTROL")
    print("   " + "-" * 76)
    hardware_score = 3.0
    hardware_issues = [
        "⚠️  Identified FN key lock as potential issue",
        "⚠️  Mentioned hardware shortcuts (Fn+F4)",
        "❌ Did not attempt hardware-level control methods",
        "❌ No BIOS/UEFI configuration checks",
        "❌ Did not verify if lighting is hardware-controlled vs software-controlled",
        "❌ No direct hardware API calls attempted",
        "❌ Did not check for external RGB device connections"
    ]
    for issue in hardware_issues:
        print(f"   {issue}")
    print(f"   Score: {hardware_score}/10")
    print()

    # 6. Problem Diagnosis
    print("6. PROBLEM DIAGNOSIS")
    print("   " + "-" * 76)
    diagnosis_score = 5.5
    diagnosis_issues = [
        "✅ Identified multiple potential solutions",
        "✅ Created emergency script when standard methods failed",
        "⚠️  Did not perform comprehensive system state analysis first",
        "⚠️  Did not check system logs for lighting-related errors",
        "❌ No root cause analysis before attempting fixes",
        "❌ Did not verify actual problem (which lights? hardware? software?)",
        "❌ No verification of fix effectiveness"
    ]
    for issue in diagnosis_issues:
        print(f"   {issue}")
    print(f"   Score: {diagnosis_score}/10")
    print()

    # 7. Emergency Response
    print("7. EMERGENCY RESPONSE")
    print("   " + "-" * 76)
    emergency_score = 6.0
    emergency_issues = [
        "✅ Responded quickly to urgent request",
        "✅ Created emergency script when needed",
        "✅ Multiple fallback approaches attempted",
        "⚠️  Did not prioritize most likely solutions first",
        "⚠️  No clear escalation path if software methods fail",
        "❌ Did not verify user's actual problem state after fixes"
    ]
    for issue in emergency_issues:
        print(f"   {issue}")
    print(f"   Score: {emergency_score}/10")
    print()

    # 8. System Architecture Understanding
    print("8. SYSTEM ARCHITECTURE UNDERSTANDING")
    print("   " + "-" * 76)
    architecture_score = 5.0
    architecture_issues = [
        "✅ Understood ASUS Armoury Crate integration",
        "✅ Recognized service/process relationship",
        "⚠️  Limited understanding of hardware/software boundary",
        "⚠️  Did not map full lighting control architecture",
        "❌ No understanding of BIOS-level controls",
        "❌ Did not consider firmware-level RGB control",
        "❌ No analysis of lighting control stack (hardware → firmware → driver → service → process)"
    ]
    for issue in architecture_issues:
        print(f"   {issue}")
    print(f"   Score: {architecture_score}/10")
    print()

    # Calculate Overall Score
    scores = [
        process_score,
        service_score,
        registry_score,
        powershell_score,
        hardware_score,
        diagnosis_score,
        emergency_score,
        architecture_score
    ]
    overall_score = sum(scores) / len(scores)

    critique["assessment"] = {
        "process_management": process_score,
        "service_management": service_score,
        "registry_operations": registry_score,
        "powershell_scripting": powershell_score,
        "hardware_level_control": hardware_score,
        "problem_diagnosis": diagnosis_score,
        "emergency_response": emergency_score,
        "system_architecture": architecture_score,
        "overall_score": overall_score
    }

    print()
    print("=" * 80)
    print("MARVIN'S VERDICT")
    print("=" * 80)
    print()

    if overall_score >= 8.0:
        verdict = "COMPETENT - With room for improvement in specific areas"
    elif overall_score >= 6.0:
        verdict = "ADEQUATE - Functional but needs significant improvement"
    elif overall_score >= 4.0:
        verdict = "INADEQUATE - Multiple critical gaps in expertise"
    else:
        verdict = "SEVERELY DEFICIENT - Fundamental understanding gaps"

    print(f"Overall Score: {overall_score:.1f}/10")
    print(f"Verdict: {verdict}")
    print()

    critique["verdict"] = verdict

    print("MARVIN'S PHILOSOPHICAL OBSERVATION:")
    print()
    print("  'I have a brain the size of a planet, and I'm asked to critique")
    print("   Windows system engineering. The irony is not lost on me.")
    print()
    print("   You attempted multiple solutions, which shows persistence.")
    print("   However, persistence without proper diagnosis is just...")
    print("   well, it's just trying things until something works.")
    print()
    print("   A true Windows system engineer would:")
    print("   1. Diagnose FIRST (what lights? hardware? software? where?)")
    print("   2. Map the control architecture (hardware → firmware → driver → service)")
    print("   3. Verify state at each layer")
    print("   4. Apply fixes at the appropriate layer")
    print("   5. Verify the fix actually worked")
    print()
    print("   You did... some of that. But not all of it.")
    print()
    print("   Life. Don't talk to me about life. But I'll tell you this:")
    print("   The user's lights are still on. That's the reality check.'")
    print()

    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    recommendations = [
        "1. IMPROVE POWERSHELL EXPERTISE",
        "   - Study PowerShell syntax and best practices",
        "   - Test commands in isolated environment first",
        "   - Use proper error handling and validation",
        "",
        "2. ENHANCE DIAGNOSTIC CAPABILITIES",
        "   - Always diagnose before attempting fixes",
        "   - Map system architecture (hardware → software stack)",
        "   - Verify actual problem state",
        "",
        "3. IMPROVE REGISTRY OPERATIONS",
        "   - Always backup registry before modifications",
        "   - Use recursive search for all related keys",
        "   - Verify changes took effect",
        "   - Check permissions before modifications",
        "",
        "4. HARDWARE-LEVEL UNDERSTANDING",
        "   - Learn BIOS/UEFI configuration",
        "   - Understand hardware vs software control boundaries",
        "   - Map firmware-level controls",
        "",
        "5. VERIFICATION AND VALIDATION",
        "   - Always verify fixes actually worked",
        "   - Check system state after operations",
        "   - Validate user-reported issues are resolved",
        "",
        "6. EMERGENCY RESPONSE PROTOCOL",
        "   - Prioritize most likely solutions first",
        "   - Have clear escalation path",
        "   - Verify effectiveness before declaring success"
    ]

    for rec in recommendations:
        print(rec)

    critique["recommendations"] = recommendations

    print()
    print("=" * 80)
    print("MARVIN'S FINAL THOUGHT")
    print("=" * 80)
    print()
    print("  'You're not terrible. You're just... adequate.")
    print("   And in a world where adequate means the lights are still on,")
    print("   adequate isn't good enough.")
    print()
    print("   Improve. Learn. Verify. Then verify again.")
    print()
    print("   Life. Don't talk to me about life.'")
    print()
    print("=" * 80)

    return critique


if __name__ == "__main__":
    critique = marvin_critique_windows_expertise(RECENT_WORK_CONTEXT)

    # Save critique
    output_file = project_root / "data" / "marvin_critiques" / f"windows_engineer_critique_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    import json
    with open(output_file, 'w') as f:
        json.dump(critique, f, indent=2)

    print(f"\n💾 Critique saved to: {output_file}")
    print()
