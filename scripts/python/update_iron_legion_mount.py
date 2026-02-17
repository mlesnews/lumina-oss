#!/usr/bin/env python3
"""
Update Iron Legion to Mount M Drive
Updates Docker containers to mount M drive for models

Tags: #IRON_LEGION #M_DRIVE #MOUNT @JARVIS @LUMINA @DOIT
"""

import json
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

def check_m_drive_access():
    """Check if M drive is accessible and find models"""
    host = "<NAS_IP>"

    print("🔍 Checking M drive access...\n")

    # Try different M drive paths
    m_paths = [
        "M:\\",
        "M:\\models",
        "\\\\M\\models",
        "\\\\<NAS_IP>\\M\\models"
    ]

    for path in m_paths:
        cmd = f"if (Test-Path '{path}') {{ Write-Host 'EXISTS: {path}'; Get-ChildItem '{path}' -Filter '*.gguf' -ErrorAction SilentlyContinue | Select-Object -First 3 Name }}"
        stdout, code = run_ssh_command(host, cmd)
        if "EXISTS" in stdout:
            print(f"  ✅ Found: {path}")
            if stdout.strip() and "Name" in stdout:
                print("     Models found!")
                return path

    print("  ❌ M drive not found in common locations")
    return None

def update_docker_compose_mount(m_drive_path: str):
    """Update docker-compose to mount M drive"""
    print(f"\n📝 To mount M drive ({m_drive_path}), update docker-compose.yml:")
    print("   volumes:")
    print("     - type: bind")
    print(f"       source: {m_drive_path}")
    print("       target: /models")
    print("       bind:")
    print("         propagation: shared")

def main():
    """Main"""
    print("=" * 80)
    print("🔧 Update Iron Legion to Mount M Drive")
    print("=" * 80)

    # Check current setup
    print("\n📊 Current Setup:")
    host = "<NAS_IP>"
    stdout, code = run_ssh_command(host, "docker volume inspect iron-legion-llamacpp_iron-legion-models --format '{{json .Options}}'")
    if code == 0:
        try:
            options = json.loads(stdout)
            current_path = options.get("device", "unknown")
            print(f"  📍 Current mount: {current_path}")
        except:
            print(f"  📍 Current mount: {stdout.strip()}")

    # Check M drive
    m_path = check_m_drive_access()

    if m_path:
        print(f"\n✅ M drive found at: {m_path}")
        update_docker_compose_mount(m_path)
        print("\n💡 Next steps:")
        print("  1. Update docker-compose.iron-legion.yml with M drive mount")
        print("  2. Stop containers: docker-compose down")
        print("  3. Start containers: docker-compose up -d")
    else:
        print("\n⚠️  M drive not found")
        print("\n💡 Options:")
        print("  1. Mount M drive as network share first")
        print("  2. Or specify exact path to models on M drive")
        print("  3. Current models are in D:/Ollama/models (already mounted)")

    print("\n" + "=" * 80)

if __name__ == "__main__":


    main()