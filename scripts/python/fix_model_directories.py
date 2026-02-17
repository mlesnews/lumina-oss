#!/usr/bin/env python3
"""
Fix Model Directories - Convert directories to actual .gguf files
Root cause: Model "files" are actually directories, not files

Tags: #IRON_LEGION #FIX_DIRECTORIES #ROOT_CAUSE @JARVIS @LUMINA @DOIT
"""

import subprocess
import os

def run_ssh_command(host: str, command: str) -> tuple[str, int]:
    """Run command via SSH"""
    ssh_cmd = ["ssh", host, command]
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def main():
    """Main fix"""
    host = "<NAS_IP>"

    print("=" * 80)
    print("🔧 Fix Model Directories - Root Cause Analysis")
    print("=" * 80)

    # Check if model paths are directories
    print("\n📋 Checking model file types...")

    models_to_check = [
        ("Mark II", "Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf"),
        ("Mark VII", "gemma-2b-it.Q4_K_M.gguf")
    ]

    for mark, filename in models_to_check:
        cmd = f"docker exec iron-legion-mark-i-codellama-llamacpp bash -c 'test -d /models/{filename} && echo \"DIRECTORY\" || (test -f /models/{filename} && echo \"FILE\")'"
        stdout, code = run_ssh_command(host, cmd)
        file_type = stdout.strip()
        print(f"  {mark} ({filename}): {file_type}")

    # Find actual .gguf files inside directories or elsewhere
    print("\n🔍 Searching for actual .gguf files...")

    # Check inside directories
    cmd = "docker exec iron-legion-mark-i-codellama-llamacpp bash -c 'find /models/Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf -name \"*.gguf\" -type f 2>/dev/null | head -1'"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print(f"  ✅ Found Mark II file inside directory: {stdout.strip()}")

    cmd = "docker exec iron-legion-mark-i-codellama-llamacpp bash -c 'find /models/gemma-2b-it.Q4_K_M.gguf -name \"*.gguf\" -type f 2>/dev/null | head -1'"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print(f"  ✅ Found Mark VII file inside directory: {stdout.strip()}")

    # Search D drive for actual files
    print("\n🔍 Searching D drive for actual model files...")

    cmd = "Get-ChildItem 'D:\\' -Recurse -Filter 'Llama-3.2-11B-Vision-Instruct*.gguf' -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.Length -gt 1GB } | Select-Object -First 1 -ExpandProperty FullName"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print(f"  ✅ Found Mark II on D drive: {stdout.strip()}")

    cmd = "Get-ChildItem 'D:\\' -Recurse -Filter 'gemma-2b-it*.gguf' -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.Length -gt 1MB } | Select-Object -First 1 -ExpandProperty FullName"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print(f"  ✅ Found Mark VII on D drive: {stdout.strip()}")

    print("\n" + "=" * 80)
    print("💡 Root Cause: Model 'files' are directories, not actual .gguf files")
    print("   Solution: Find actual .gguf files and copy them properly")
    print("=" * 80)

if __name__ == "__main__":


    main()