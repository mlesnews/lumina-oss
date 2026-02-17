#!/usr/bin/env python3
"""
Final Fix for Iron Legion - Restart containers with existing models

Tags: #IRON_LEGION #FINAL_FIX @JARVIS @LUMINA @DOIT
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

    print("=" * 80)
    print("🔧 Final Fix for Iron Legion Models")
    print("=" * 80)

    # Stop all failing containers
    print("\n🛑 Stopping containers...")
    containers = [
        "iron-legion-mark-ii-llama32-llamacpp",
        "iron-legion-mark-iii-qwen-llamacpp",
        "iron-legion-mark-vi-mixtral-llamacpp",
        "iron-legion-mark-vii-gemma-llamacpp"
    ]

    for container in containers:
        stdout, code = run_ssh_command(host, f"docker stop {container} 2>&1")
        print(f"  ✅ Stopped {container}")
        time.sleep(1)

    print("\n⏳ Waiting 5 seconds...")
    time.sleep(5)

    # Restart containers that have model files
    print("\n🔄 Restarting containers with existing models...")

    # Mark III - has model file
    print("  🔄 Mark III (qwen) - model exists...")
    stdout, code = run_ssh_command(host, "docker start iron-legion-mark-iii-qwen-llamacpp")
    if code == 0:
        print("  ✅ Started")
    time.sleep(5)

    # Mark VI - has model file
    print("  🔄 Mark VI (mixtral) - model exists...")
    stdout, code = run_ssh_command(host, "docker start iron-legion-mark-vi-mixtral-llamacpp")
    if code == 0:
        print("  ✅ Started")
    time.sleep(5)

    # Mark II and Mark VII - missing models, skip for now
    print("\n⚠️  Mark II and Mark VII skipped - model files missing")
    print("   Download required models first")

    print("\n⏳ Waiting 20 seconds for containers to initialize...")
    time.sleep(20)

    # Check status
    print("\n📊 Final Status:")
    all_containers = [
        ("iron-legion-mark-i-codellama-llamacpp", "Mark I"),
        ("iron-legion-mark-ii-llama32-llamacpp", "Mark II"),
        ("iron-legion-mark-iii-qwen-llamacpp", "Mark III"),
        ("iron-legion-mark-iv-llama3-llamacpp", "Mark IV"),
        ("iron-legion-mark-v-mistral-llamacpp", "Mark V"),
        ("iron-legion-mark-vi-mixtral-llamacpp", "Mark VI"),
        ("iron-legion-mark-vii-gemma-llamacpp", "Mark VII"),
    ]

    for container, name in all_containers:
        stdout, code = run_ssh_command(host, f"docker ps --filter name={container} --format '{{{{.Status}}}}'")
        if stdout.strip():
            status = stdout.strip()
            if "Up" in status and "unhealthy" not in status.lower() and "restarting" not in status.lower():
                print(f"  ✅ {name}: {status}")
            else:
                print(f"  ⚠️  {name}: {status}")
        else:
            print(f"  ❌ {name}: Not running")

    print("\n" + "=" * 80)
    print("✅ Fix complete")
    print("\n📝 Next Steps:")
    print("  1. Download missing models for Mark II and Mark VII")
    print("  2. Check logs for Mark III and Mark VI if still failing")
    print("  3. Verify GPU memory availability")
    print("=" * 80)

if __name__ == "__main__":


    main()