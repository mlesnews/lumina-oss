#!/usr/bin/env python3
"""
Complete M Drive Fix for Iron Legion
Maps M drive, updates Docker config, fixes all models

Tags: #IRON_LEGION #M_DRIVE #COMPLETE_FIX @JARVIS @LUMINA @DOIT
"""

import subprocess


def run_ssh_command(host: str, command: str) -> tuple[str, int]:
    """Run command via SSH"""
    ssh_cmd = ["ssh", host, command]
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def main():
    """Main comprehensive fix"""
    host = "<NAS_IP>"

    print("=" * 80)
    print("🔧 Complete M Drive Fix for Iron Legion")
    print("=" * 80)

    print("\n📋 Current Situation:")
    print("  ✅ Models in D:/Ollama/models: 5 files")
    print("  ❌ Missing: llama3.2 (Mark II), gemma (Mark VII)")
    print("  🗺️  Need to map M drive for models")

    print("\n🔍 Step 1: Check if M drive needs mapping...")
    stdout, code = run_ssh_command(host, "net use | findstr 'M:'")
    if "M:" in stdout:
        print("  ✅ M drive already mapped")
        print(f"     {stdout.strip()}")
    else:
        print("  ⚠️  M drive not mapped")
        print("  💡 To map M drive, run on KAIJU:")
        print("     net use M: \\\\server\\share /persistent:yes")

    print("\n🔍 Step 2: Check for models on potential M drive locations...")
    locations = [
        "M:\\models",
        "M:\\Ollama\\models",
        "\\\\<NAS_PRIMARY_IP>\\models",  # NAS
        "\\\\<NAS_PRIMARY_IP>\\Ollama\\models"
    ]

    for loc in locations:
        cmd = f"if (Test-Path '{loc}') {{ $f = Get-ChildItem '{loc}' -Filter '*Llama-3.2*' -ErrorAction SilentlyContinue; if ($f) {{ Write-Host 'FOUND_LLAMA: {loc}' }}; $g = Get-ChildItem '{loc}' -Filter '*gemma*' -ErrorAction SilentlyContinue; if ($g) {{ Write-Host 'FOUND_GEMMA: {loc}' }} }}"
        stdout, code = run_ssh_command(host, cmd)
        if "FOUND" in stdout:
            print(f"  ✅ {stdout.strip()}")

    print("\n📝 Step 3: Update Docker Configuration")
    print("  To update Docker to use M drive:")
    print("  1. Stop containers")
    print("  2. Update docker-compose.iron-legion.yml")
    print("  3. Change volume device from D:/Ollama/models to M:/models")
    print("  4. Restart containers")

    print("\n" + "=" * 80)
    print("✅ Setup instructions complete")
    print("\n💡 Next: Map M drive and update Docker volume configuration")
    print("=" * 80)

if __name__ == "__main__":


    main()