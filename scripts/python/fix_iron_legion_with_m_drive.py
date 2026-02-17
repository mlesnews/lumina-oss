#!/usr/bin/env python3
"""
Fix Iron Legion Models - Check M Drive and Update Mounts
Looks for models on M drive and updates container mounts

Tags: #IRON_LEGION #M_DRIVE #FIX @JARVIS @LUMINA @DOIT
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
            timeout=60
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def main():
    """Main"""
    host = "<NAS_IP>"

    print("=" * 80)
    print("🔧 Fix Iron Legion Models - M Drive Check")
    print("=" * 80)

    # Current models in D:/Ollama/models
    print("\n📊 Current Models in D:/Ollama/models:")
    stdout, code = run_ssh_command(host, "Get-ChildItem 'D:\\Ollama\\models' -Filter '*.gguf' | Select-Object Name")
    if code == 0:
        print(stdout)

    # Check for M drive
    print("\n🔍 Checking for M drive...")

    # Try to find M drive as network share
    stdout, code = run_ssh_command(host, "net use")
    if "M:" in stdout:
        print("  ✅ M drive found as network share")
        print(stdout)
    else:
        print("  ⚠️  M drive not mapped as network share")

    # Check if M drive path exists
    m_paths = [
        "M:\\",
        "M:\\models",
        "M:\\Ollama\\models",
        "\\\\<NAS_PRIMARY_IP>\\models",  # NAS
        "\\\\<NAS_IP>\\M\\models"
    ]

    print("\n🔍 Checking M drive paths...")
    found_path = None
    for path in m_paths:
        cmd = f"if (Test-Path '{path}') {{ Write-Host 'EXISTS: {path}'; Get-ChildItem '{path}' -Filter '*.gguf' -ErrorAction SilentlyContinue | Select-Object -First 2 Name }}"
        stdout, code = run_ssh_command(host, cmd)
        if "EXISTS" in stdout:
            print(f"  ✅ Found: {path}")
            if stdout.strip() and "Name" in stdout:
                print(f"     {stdout.strip()}")
                found_path = path
                break

    # Missing models
    print("\n❌ Missing Models:")
    missing = [
        ("Mark II", "Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf"),
        ("Mark VII", "gemma-2b-it.Q4_K_M.gguf")
    ]

    for mark, model_file in missing:
        print(f"  • {mark}: {model_file}")

    # Summary
    print("\n" + "=" * 80)
    print("📝 Summary:")
    print("  ✅ Current mount: D:/Ollama/models")
    print("  ✅ Models available: codellama, llama3, mistral, mixtral, qwen")
    print("  ❌ Missing: llama3.2 (Mark II), gemma (Mark VII)")

    if found_path:
        print(f"\n  ✅ M drive found at: {found_path}")
        print("  💡 To mount M drive:")
        print("     1. Update docker-compose.iron-legion.yml")
        print("     2. Change volume mount from D:/Ollama/models to M drive path")
        print("     3. Restart containers")
    else:
        print("\n  ⚠️  M drive not found")
        print("  💡 Options:")
        print("     1. Map M drive as network share: net use M: \\\\server\\share")
        print("     2. Or download missing models to D:/Ollama/models")
        print("     3. Or specify exact M drive path if different")

    print("=" * 80)

if __name__ == "__main__":


    main()