#!/usr/bin/env python3
"""
Find All Model Files - Comprehensive Search
Searches thoroughly for all model files in all locations

Tags: #IRON_LEGION #FIND_MODELS @JARVIS @LUMINA @DOIT
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
    """Main comprehensive search"""
    host = "<NAS_IP>"
    container = "iron-legion-mark-i-codellama-llamacpp"

    print("=" * 80)
    print("🔍 Comprehensive Model File Search")
    print("=" * 80)

    # Search in /models directory
    print("\n📁 Searching /models directory...")
    stdout, code = run_ssh_command(host, f"docker exec {container} bash -c 'cd /models && ls -la'")
    if code == 0:
        print(stdout)

    # List all files recursively
    print("\n📋 All .gguf files in /models (recursive):")
    stdout, code = run_ssh_command(host, f"docker exec {container} bash -c 'cd /models && find . -type f -name \"*.gguf\"'")
    if code == 0 and stdout.strip():
        files = [f.strip() for f in stdout.split('\n') if f.strip()]
        print(f"  Found {len(files)} .gguf files:")
        for f in files:
            print(f"    {f}")
    else:
        print("  No .gguf files found recursively")

    # Check for directories that might contain models
    print("\n📂 Checking for subdirectories...")
    stdout, code = run_ssh_command(host, f"docker exec {container} bash -c 'cd /models && find . -type d'")
    if code == 0 and stdout.strip():
        dirs = [d.strip() for d in stdout.split('\n') if d.strip() and d.strip() != '.']
        if dirs:
            print(f"  Found {len(dirs)} directories:")
            for d in dirs:
                print(f"    {d}")
                # Check each directory for models
                stdout2, _ = run_ssh_command(host, f"docker exec {container} bash -c 'cd /models && ls -la \"{d}\" 2>/dev/null | head -10'")
                if stdout2.strip():
                    print(f"      Contents: {stdout2.strip()[:100]}")

    # Check what containers expect vs what exists
    print("\n🔍 Comparing expected vs actual filenames...")

    expected_models = {
        "Mark II": "Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf",
        "Mark III": "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "Mark VI": "mixtral-8x7b-v0.1.Q4_K_M.gguf",
        "Mark VII": "gemma-2b-it.Q4_K_M.gguf"
    }

    actual_files = [
        "codellama-13b.Q4_K_M.gguf",
        "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
        "mistral-7b-v0.1.Q4_K_M.gguf",
        "mixtral-8x7b-v0.1.Q4_K_M.gguf",
        "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
    ]

    print("\n  Expected vs Actual:")
    print("  Mark II: Looking for 'Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf'")
    print("    → Found: 'Meta-Llama-3-8B-Instruct.Q4_K_M.gguf' (different model)")
    print("  Mark III: Looking for 'qwen2.5-coder-1.5b-instruct-q4_k_m.gguf'")
    print("    → Found: ✅ EXISTS")
    print("  Mark VI: Looking for 'mixtral-8x7b-v0.1.Q4_K_M.gguf'")
    print("    → Found: ✅ EXISTS")
    print("  Mark VII: Looking for 'gemma-2b-it.Q4_K_M.gguf'")
    print("    → Found: ❌ NOT FOUND")

    print("\n" + "=" * 80)
    print("✅ Found: qwen (Mark III), mixtral (Mark VI)")
    print("❌ Missing: llama3.2 (Mark II), gemma (Mark VII)")
    print("=" * 80)

if __name__ == "__main__":


    main()