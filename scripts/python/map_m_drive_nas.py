#!/usr/bin/env python3
"""
Map M Drive to NAS and Find Models
Maps M drive to NAS and searches for missing model files

Tags: #IRON_LEGION #MAP_M_DRIVE #NAS @JARVIS @LUMINA @DOIT
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
    """Main mapping and search"""
    host = "<NAS_IP>"
    nas_ip = "<NAS_PRIMARY_IP>"

    print("=" * 80)
    print("🗺️  Map M Drive to NAS and Find Models")
    print("=" * 80)

    # Check if M drive exists
    print("\n🔍 Checking M drive status...")
    stdout, code = run_ssh_command(host, "Test-Path 'M:\\'")
    if "True" in stdout:
        print("  ✅ M drive is already mapped")
    else:
        print("  ❌ M drive is not mapped")

    # Try to map M drive
    print(f"\n🗺️  Mapping M drive to {nas_ip}...")

    # Try different share names
    shares_to_try = ["models", "Models", "MODELS", "ollama", "Ollama", "OLLAMA", "llm", "LLM"]

    for share in shares_to_try:
        print(f"  Trying \\\\{nas_ip}\\{share}...")
        # Use net use with credentials prompt (will need user input)
        cmd = f"$cred = Get-Credential -Message 'Enter NAS credentials'; $net = New-Object System.Management.Automation.PSCredential('user', $cred.Password); net use M: \\\\{nas_ip}\\{share} /persistent:yes /user:$($cred.UserName) 2>&1"

        # Alternative: Try without credentials first
        cmd_simple = f"New-PSDrive -Name 'M' -PSProvider FileSystem -Root '\\\\{nas_ip}\\{share}' -Persist -ErrorAction SilentlyContinue"
        stdout, code = run_ssh_command(host, cmd_simple)

        # Check if it worked
        stdout2, code2 = run_ssh_command(host, "Test-Path 'M:\\'")
        if "True" in stdout2:
            print(f"  ✅ Successfully mapped M: to \\\\{nas_ip}\\{share}")
            break

    # Check M drive again
    stdout, code = run_ssh_command(host, "Test-Path 'M:\\'")
    if "True" not in stdout:
        print("\n⚠️  Could not automatically map M drive")
        print("   Please map manually using:")
        print(f"   net use M: \\\\{nas_ip}\\models /persistent:yes")
        print("   Or provide NAS credentials")
        return

    # Search for models on M drive
    print("\n🔍 Searching for models on M drive...")

    # Find all .gguf files
    cmd = "Get-ChildItem 'M:\\' -Recurse -Filter '*.gguf' -ErrorAction SilentlyContinue | Select-Object FullName, Name, Length"
    stdout, code = run_ssh_command(host, cmd)

    if stdout.strip():
        print("\n📋 Found .gguf files on M drive:")
        lines = [l.strip() for l in stdout.split('\n') if l.strip() and not l.strip().startswith('-')]
        for line in lines[:20]:  # Show first 20
            print(f"  {line}")

    # Search specifically for missing models
    print("\n🔍 Searching for missing models...")
    missing_models = [
        "Llama-3.2-11B-Vision-Instruct",
        "llama3.2",
        "llama-3.2",
        "gemma-2b",
        "gemma2b"
    ]

    for model_pattern in missing_models:
        cmd = f"Get-ChildItem 'M:\\' -Recurse -Filter '*{model_pattern}*.gguf' -ErrorAction SilentlyContinue | Select-Object FullName, Name"
        stdout, code = run_ssh_command(host, cmd)
        if stdout.strip() and not stdout.strip().startswith('FullName'):
            print(f"\n  ✅ Found {model_pattern}:")
            lines = [l.strip() for l in stdout.split('\n') if l.strip() and not l.strip().startswith('FullName')]
            for line in lines:
                print(f"    {line}")

    print("\n" + "=" * 80)
    print("✅ M Drive Mapping Complete")
    print("=" * 80)

if __name__ == "__main__":


    main()