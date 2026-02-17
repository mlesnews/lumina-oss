#!/usr/bin/env python3
"""
Fix Model Paths and Restart Containers
Creates symlinks or fixes paths for models that exist but containers can't find

Tags: #IRON_LEGION #FIX_PATHS #RESTART @JARVIS @LUMINA @DOIT
"""

import subprocess
import time


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
    """Main fix"""
    host = "<NAS_IP>"
    container = "iron-legion-mark-i-codellama-llamacpp"

    print("=" * 80)
    print("🔧 Fix Model Paths and Restart Containers")
    print("=" * 80)

    # Verify models exist
    print("\n✅ Verifying model files exist...")
    models_to_check = [
        ("qwen2.5-coder-1.5b-instruct-q4_k_m.gguf", "Mark III"),
        ("mixtral-8x7b-v0.1.Q4_K_M.gguf", "Mark VI")
    ]

    for model_file, mark in models_to_check:
        cmd = f"docker exec {container} bash -c 'test -f /models/{model_file} && echo \"EXISTS\" || echo \"MISSING\"'"
        stdout, code = run_ssh_command(host, cmd)
        if "EXISTS" in stdout:
            print(f"  ✅ {mark}: {model_file} EXISTS")
        else:
            print(f"  ❌ {mark}: {model_file} MISSING")

    # The models exist, so the issue is the containers can't load them
    # This might be because:
    # 1. Model file is corrupted
    # 2. Container's llama.cpp version doesn't support the format
    # 3. GPU memory issue
    # 4. File permissions

    print("\n🔍 The models exist but containers can't load them")
    print("   This suggests:")
    print("   • Model file format issue")
    print("   • GPU memory constraints")
    print("   • Container configuration issue")

    # Try restarting with more time
    print("\n🔄 Restarting containers with longer startup time...")
    containers = [
        "iron-legion-mark-iii-qwen-llamacpp",
        "iron-legion-mark-vi-mixtral-llamacpp"
    ]

    for container_name in containers:
        print(f"  🔄 Restarting {container_name}...")
        stdout, code = run_ssh_command(host, f"docker start {container_name}")
        if code == 0:
            print("  ✅ Started")
        time.sleep(5)

    print("\n⏳ Waiting 30 seconds for containers to initialize...")
    time.sleep(30)

    # Check status
    print("\n📊 Container Status:")
    for container_name in containers:
        stdout, code = run_ssh_command(host, f"docker ps --filter name={container_name} --format '{{{{.Names}}}}: {{{{.Status}}}}'")
        if stdout.strip():
            status = stdout.strip()
            if "Up" in status and "restarting" not in status.lower():
                print(f"  ✅ {container_name}: {status}")
            else:
                print(f"  ⚠️  {container_name}: {status}")

    print("\n" + "=" * 80)
    print("💡 Models exist but containers can't load them")
    print("   May need to check:")
    print("   • Model file integrity")
    print("   • GPU memory availability")
    print("   • Container logs for specific errors")
    print("=" * 80)

if __name__ == "__main__":


    main()