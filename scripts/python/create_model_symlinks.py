#!/usr/bin/env python3
"""
Create Model Symlinks for Missing Iron Legion Models
Creates symlinks for models that might have different names

Tags: #IRON_LEGION #SYMLINKS #FIX @JARVIS @LUMINA @DOIT
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
    container = "iron-legion-mark-i-codellama-llamacpp"

    print("=" * 80)
    print("🔗 Create Model Symlinks for Iron Legion")
    print("=" * 80)

    # Check what's in /models
    print("\n📋 Files in /models:")
    stdout, code = run_ssh_command(host, f"docker exec {container} bash -c 'ls -1 /models/*.gguf 2>&1'")
    if code == 0:
        print(stdout)

    # Try to create symlinks for missing models
    print("\n🔗 Creating symlinks for missing models...")

    # Mark II - Try to find llama3.2 variant
    print("\n📦 Mark II (llama3.2:11b):")
    print("  Looking for Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf")

    # Check if there's a similar file
    cmd = f"docker exec {container} bash -c 'ls -1 /models/*llama*3*2* 2>/dev/null || ls -1 /models/*Llama*3*2* 2>/dev/null || echo \"NOT_FOUND\"'"
    stdout, code = run_ssh_command(host, cmd)
    if "NOT_FOUND" not in stdout and stdout.strip():
        print(f"  ✅ Found similar: {stdout.strip()}")
        # Could create symlink here if needed
    else:
        print("  ❌ Not found - needs download")

    # Mark VII - Try to find gemma variant
    print("\n📦 Mark VII (gemma:2b):")
    print("  Looking for gemma-2b-it.Q4_K_M.gguf")

    cmd = f"docker exec {container} bash -c 'ls -1 /models/*gemma* 2>/dev/null || echo \"NOT_FOUND\"'"
    stdout, code = run_ssh_command(host, cmd)
    if "NOT_FOUND" not in stdout and stdout.strip():
        print(f"  ✅ Found: {stdout.strip()}")
    else:
        print("  ❌ Not found - needs download")

    print("\n" + "=" * 80)
    print("💡 If models exist with different names, we can create symlinks")
    print("💡 Otherwise, models need to be downloaded to D:/Ollama/models")
    print("=" * 80)

if __name__ == "__main__":


    main()