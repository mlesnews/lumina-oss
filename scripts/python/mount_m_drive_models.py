#!/usr/bin/env python3
"""
Mount M Drive Models for Iron Legion
Finds and mounts M drive models to Docker containers

Tags: #IRON_LEGION #M_DRIVE #MOUNT @JARVIS @LUMINA @DOIT
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

def find_m_drive():
    """Find M drive or models location"""
    host = "<NAS_IP>"

    print("🔍 Searching for M drive and models...\n")

    # Check all drives
    print("📀 Checking all drives...")
    stdout, code = run_ssh_command(host, "wmic logicaldisk get name,volumename,size")
    if code == 0:
        print(stdout)

    # Check common model locations
    print("\n📁 Checking common model locations...")
    locations = [
        "M:\\models",
        "M:\\",
        "C:\\models",
        "D:\\models",
        "E:\\models",
        "C:\\Users\\Public\\models",
        "D:\\AI\\models",
        "E:\\AI\\models"
    ]

    found_models = []
    for location in locations:
        cmd = f"if (Test-Path '{location}') {{ Get-ChildItem '{location}' -Filter '*.gguf' -ErrorAction SilentlyContinue | Select-Object -First 1 Name, Length }}"
        stdout, code = run_ssh_command(host, cmd)
        if stdout.strip() and "Name" in stdout:
            found_models.append((location, stdout.strip()))
            print(f"  ✅ Found models in: {location}")
            print(f"     {stdout.strip()[:100]}")

    if not found_models:
        print("  ❌ No model files found in common locations")
        print("\n💡 Please specify the exact path to the M drive or models folder")
        return None

    return found_models

def check_docker_volume():
    """Check current Docker volume location"""
    host = "<NAS_IP>"

    print("\n🐳 Checking Docker volume...")
    stdout, code = run_ssh_command(host, "docker volume inspect iron-legion-llamacpp_iron-legion-models --format '{{.Mountpoint}}' 2>&1")
    if code == 0 and stdout.strip():
        mountpoint = stdout.strip()
        print(f"  📍 Current volume mountpoint: {mountpoint}")
        return mountpoint
    else:
        print("  ⚠️  Could not find volume mountpoint")
        return None

def main():
    """Main"""
    print("=" * 80)
    print("🔧 Mount M Drive Models for Iron Legion")
    print("=" * 80)

    found = find_m_drive()
    volume_mount = check_docker_volume()

    print("\n" + "=" * 80)
    if found:
        print("✅ Found model locations")
        print("\n📝 Next steps:")
        print("  1. Update docker-compose.yml to mount M drive")
        print("  2. Or copy models from M drive to Docker volume")
        print("  3. Restart containers")
    else:
        print("⚠️  M drive or models not found")
        print("\n💡 Options:")
        print("  1. Mount M drive as network share")
        print("  2. Specify exact path to models")
        print("  3. Copy models to Docker volume location")
    print("=" * 80)

if __name__ == "__main__":


    main()