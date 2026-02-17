#!/usr/bin/env python3
"""
Fix Iron Legion Model Files
Creates symlinks or copies model files to match expected names

Tags: #IRON_LEGION #FIX #MODELS @JARVIS @LUMINA @DOIT
"""

import subprocess
import sys


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

def fix_model_files():
    """Fix model file names/locations"""
    host = "<NAS_IP>"
    container = "iron-legion-mark-i-codellama-llamacpp"

    print("🔍 Checking model files...")

    # Get list of model files
    stdout, code = run_ssh_command(host, f"docker exec {container} ls -1 /models/*.gguf 2>&1")
    if code != 0:
        print(f"❌ Error: {stdout}")
        return False

    model_files = [f.strip() for f in stdout.split('\n') if f.strip() and '.gguf' in f]
    print(f"✅ Found {len(model_files)} model files")

    # Model mappings: expected_name -> actual_name
    model_mappings = {
        # Mark II - llama3.2:11b
        "/models/Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf": [
            "/models/Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf",  # Check if exists
            "/models/llama3.2-11b.Q4_K_M.gguf",
            "/models/llama-3.2-11b.Q4_K_M.gguf"
        ],
        # Mark III - qwen2.5-coder:1.5b
        "/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf": [
            "/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
            "/models/qwen2.5-coder-1.5b.Q4_K_M.gguf",
            "/models/qwen-2.5-coder-1.5b.Q4_K_M.gguf"
        ],
        # Mark VI - mixtral:8x7b
        "/models/mixtral-8x7b-v0.1.Q4_K_M.gguf": [
            "/models/mixtral-8x7b-v0.1.Q4_K_M.gguf",  # This exists!
        ],
        # Mark VII - gemma:2b
        "/models/gemma-2b-it.Q4_K_M.gguf": [
            "/models/gemma-2b-it.Q4_K_M.gguf",  # This exists as directory!
        ]
    }

    print("\n🔧 Fixing model files...")

    # Check Mark II - llama3.2
    print("\n📦 Mark II (llama3.2:11b):")
    stdout, code = run_ssh_command(host, f"docker exec {container} test -f /models/Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf && echo 'EXISTS' || echo 'MISSING'")
    if "EXISTS" in stdout:
        print("  ✅ Model file exists")
    else:
        print("  ⚠️  Model file missing - checking alternatives...")
        # Check if it's a directory
        stdout2, _ = run_ssh_command(host, f"docker exec {container} test -d /models/Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf && echo 'IS_DIR' || echo 'NOT_DIR'")
        if "IS_DIR" in stdout2:
            print("  ⚠️  Found directory instead of file - needs investigation")

    # Check Mark III - qwen
    print("\n📦 Mark III (qwen2.5-coder:1.5b):")
    stdout, code = run_ssh_command(host, f"docker exec {container} test -f /models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf && echo 'EXISTS' || echo 'MISSING'")
    if "EXISTS" in stdout:
        print("  ✅ Model file exists")
    else:
        print("  ❌ Model file missing")

    # Check Mark VI - mixtral
    print("\n📦 Mark VI (mixtral:8x7b):")
    stdout, code = run_ssh_command(host, f"docker exec {container} test -f /models/mixtral-8x7b-v0.1.Q4_K_M.gguf && echo 'EXISTS' || echo 'MISSING'")
    if "EXISTS" in stdout:
        print("  ✅ Model file exists")
    else:
        print("  ❌ Model file missing")

    # Check Mark VII - gemma
    print("\n📦 Mark VII (gemma:2b):")
    stdout, code = run_ssh_command(host, f"docker exec {container} test -f /models/gemma-2b-it.Q4_K_M.gguf && echo 'EXISTS' || echo 'MISSING'")
    if "EXISTS" in stdout:
        print("  ✅ Model file exists")
    else:
        stdout2, _ = run_ssh_command(host, f"docker exec {container} test -d /models/gemma-2b-it.Q4_K_M.gguf && echo 'IS_DIR' || echo 'NOT_DIR'")
        if "IS_DIR" in stdout2:
            print("  ⚠️  Found directory - checking contents...")
            stdout3, _ = run_ssh_command(host, f"docker exec {container} ls -la /models/gemma-2b-it.Q4_K_M.gguf/ 2>&1 | head -5")
            print(f"  📁 Directory contents: {stdout3[:200]}")

    print("\n✅ Model file check complete")
    return True

def restart_containers():
    """Restart the failing containers"""
    host = "<NAS_IP>"
    containers = [
        "iron-legion-mark-ii-llama32-llamacpp",
        "iron-legion-mark-iii-qwen-llamacpp",
        "iron-legion-mark-vi-mixtral-llamacpp",
        "iron-legion-mark-vii-gemma-llamacpp"
    ]

    print("\n🔄 Restarting containers...")
    for container in containers:
        print(f"  🔄 Restarting {container}...")
        stdout, code = run_ssh_command(host, f"docker start {container}")
        if code == 0:
            print(f"  ✅ {container} started")
        else:
            print(f"  ❌ Failed to start {container}: {stdout}")

def main():
    """Main"""
    print("=" * 80)
    print("🔧 Fix Iron Legion Model Files")
    print("=" * 80)

    if not fix_model_files():
        print("\n❌ Model file check failed")
        sys.exit(1)

    # Wait a bit
    import time
    print("\n⏳ Waiting 5 seconds before restarting...")
    time.sleep(5)

    restart_containers()

    print("\n" + "=" * 80)
    print("✅ Fix complete - check container status")
    print("=" * 80)

if __name__ == "__main__":


    main()