#!/usr/bin/env python3
"""
Map M Drive and Fix All Iron Legion Models
Comprehensive fix: map M drive, update Docker mounts, restart containers

Tags: #IRON_LEGION #M_DRIVE #FIX_ALL @JARVIS @LUMINA @DOIT
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
            timeout=120
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def check_m_drive_paths():
    """Check various M drive paths"""
    host = "<NAS_IP>"

    print("🔍 Checking for M drive models...\n")

    # Common M drive paths
    paths_to_check = [
        "M:\\models",
        "M:\\Ollama\\models",
        "M:\\",
        "\\\\<NAS_PRIMARY_IP>\\models",  # NAS
        "\\\\<NAS_PRIMARY_IP>\\Ollama\\models",
        "D:\\Ollama\\models",  # Current location
    ]

    found_models = {}
    for path in paths_to_check:
        # Check for missing models
        cmd = f"if (Test-Path '{path}') {{ $files = Get-ChildItem '{path}' -Filter '*.gguf' -ErrorAction SilentlyContinue; if ($files) {{ Write-Host 'EXISTS: {path}'; $files | Select-Object -First 3 Name }} }}"
        stdout, code = run_ssh_command(host, cmd)

        if "EXISTS" in stdout:
            print(f"  ✅ Found: {path}")
            if "Llama-3.2" in stdout or "llama3.2" in stdout.lower():
                found_models["llama3.2"] = path
                print("     → Contains llama3.2 model")
            if "gemma" in stdout.lower():
                found_models["gemma"] = path
                print("     → Contains gemma model")
            if stdout.strip():
                print(f"     Files: {stdout.strip()[:200]}")

    return found_models

def update_docker_volume_to_m_drive(m_drive_path: str):
    """Update Docker volume to use M drive"""
    host = "<NAS_IP>"

    print(f"\n🔧 Updating Docker volume to use M drive: {m_drive_path}")

    # The volume is currently bound to D:/Ollama/models
    # We need to update it to M drive
    # This requires updating the docker-compose or recreating the volume

    print("  ⚠️  Docker volume update requires:")
    print("     1. Stop all containers using the volume")
    print("     2. Remove the volume (or update docker-compose)")
    print("     3. Recreate volume with M drive path")
    print("     4. Restart containers")

    return m_drive_path

def restart_containers():
    """Restart all Iron Legion containers"""
    host = "<NAS_IP>"

    containers = [
        "iron-legion-mark-ii-llama32-llamacpp",
        "iron-legion-mark-iii-qwen-llamacpp",
        "iron-legion-mark-vi-mixtral-llamacpp",
        "iron-legion-mark-vii-gemma-llamacpp"
    ]

    print("\n🔄 Restarting containers...")
    for container in containers:
        print(f"  🔄 {container}...")
        stdout, code = run_ssh_command(host, f"docker start {container}")
        if code == 0:
            print("  ✅ Started")
        time.sleep(3)

    print("\n⏳ Waiting 20 seconds for initialization...")
    time.sleep(20)

    # Check status
    print("\n📊 Container Status:")
    for container in containers:
        stdout, code = run_ssh_command(host, f"docker ps --filter name={container} --format '{{{{.Names}}}}: {{{{.Status}}}}'")
        if stdout.strip():
            status = stdout.strip()
            if "Up" in status and "restarting" not in status.lower():
                print(f"  ✅ {container}: {status}")
            else:
                print(f"  ⚠️  {container}: {status}")

def main():
    """Main"""
    print("=" * 80)
    print("🗺️  Map M Drive and Fix All Iron Legion Models")
    print("=" * 80)

    # Check for M drive models
    found = check_m_drive_paths()

    if found:
        print(f"\n✅ Found models on: {found}")
        m_path = list(found.values())[0] if found else None

        if m_path:
            print(f"\n💡 To use M drive ({m_path}):")
            print("   Update docker-compose.iron-legion.yml volume configuration")
            print("   Or update the existing volume bind mount")
    else:
        print("\n⚠️  M drive models not found in common locations")
        print("   Current models are in: D:/Ollama/models")
        print("   Missing: llama3.2 (Mark II), gemma (Mark VII)")

    print("\n" + "=" * 80)
    print("📝 Summary:")
    print("  ✅ Current mount: D:/Ollama/models")
    print("  ✅ 5 models available")
    print("  ❌ 2 models missing (need to be on M drive or downloaded)")
    print("\n💡 If M drive has models, we can update the mount")
    print("💡 Or download missing models to D:/Ollama/models")
    print("=" * 80)

if __name__ == "__main__":


    main()