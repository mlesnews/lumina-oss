#!/usr/bin/env python3
"""
Complete M Drive Setup - Map NAS and Fix All Models
Maps M drive, finds models, copies them, and fixes containers

Tags: #IRON_LEGION #M_DRIVE #COMPLETE @JARVIS @LUMINA @DOIT
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
            timeout=300
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def main():
    """Main complete setup"""
    host = "<NAS_IP>"
    nas_ip = "<NAS_PRIMARY_IP>"
    nas_path = f"\\\\{nas_ip}\\models"
    local_models_path = "D:\\Ollama\\models"

    print("=" * 80)
    print("🗺️  Complete M Drive Setup - Map NAS and Fix All Models")
    print("=" * 80)

    # Step 1: Map M drive
    print("\n📌 Step 1: Mapping M drive to NAS...")
    print(f"   NAS: {nas_path}")

    # Try to map using net use (will prompt for credentials if needed)
    print("\n   Attempting to map M drive...")
    print("   Note: This may require NAS credentials")

    # Create a PowerShell script to map the drive
    map_script = f"""
$ErrorActionPreference = 'SilentlyContinue'
# Try to map M drive
$result = net use M: {nas_path} /persistent:yes 2>&1
if ($LASTEXITCODE -eq 0) {{
    Write-Host "SUCCESS: M drive mapped"
}} else {{
    Write-Host "FAILED: $result"
    Write-Host "Please run manually: net use M: {nas_path} /persistent:yes"
}}
Test-Path 'M:\\'
"""

    stdout, code = run_ssh_command(host, map_script)
    print(f"   Result: {stdout.strip()}")

    # Check if M drive is accessible
    stdout, code = run_ssh_command(host, "Test-Path 'M:\\'")
    m_drive_mapped = "True" in stdout

    if not m_drive_mapped:
        # Try accessing via UNC path directly
        print(f"\n   M drive not mapped, trying UNC path directly: {nas_path}")
        stdout, code = run_ssh_command(host, f"Test-Path '{nas_path}'")
        if "True" in stdout:
            print("   ✅ Can access NAS via UNC path")
            nas_path_accessible = True
        else:
            print("   ❌ Cannot access NAS - credentials required")
            print("\n   Please manually map M drive:")
            print(f"   net use M: {nas_path} /persistent:yes")
            return
    else:
        print("   ✅ M drive is mapped")
        nas_path_accessible = True

    # Step 2: Search for models
    print("\n📌 Step 2: Searching for models...")

    search_path = "M:\\" if m_drive_mapped else nas_path

    # Find all .gguf files
    cmd = f"Get-ChildItem '{search_path}' -Recurse -Filter '*.gguf' -ErrorAction SilentlyContinue | Select-Object FullName, Name, Length | Format-Table -AutoSize"
    stdout, code = run_ssh_command(host, cmd)

    if stdout.strip() and "FullName" in stdout:
        print("\n   Found .gguf files:")
        lines = [l.strip() for l in stdout.split('\n') if l.strip() and not l.strip().startswith('-') and 'FullName' not in l]
        for line in lines[:30]:  # Show first 30
            if line:
                print(f"     {line}")

    # Search for specific missing models
    print("\n   Searching for missing models:")
    missing_models = {
        "Mark II": ["Llama-3.2-11B-Vision-Instruct", "llama3.2", "llama-3.2-11b"],
        "Mark VII": ["gemma-2b", "gemma2b", "gemma-2b-it"]
    }

    found_models = {}
    for mark, patterns in missing_models.items():
        print(f"\n     {mark}:")
        for pattern in patterns:
            cmd = f"Get-ChildItem '{search_path}' -Recurse -Filter '*{pattern}*.gguf' -ErrorAction SilentlyContinue | Select-Object FullName, Name, Length"
            stdout, code = run_ssh_command(host, cmd)
            if stdout.strip() and "FullName" not in stdout:
                lines = [l.strip() for l in stdout.split('\n') if l.strip() and not l.strip().startswith('FullName')]
                if lines:
                    print(f"       ✅ Found: {pattern}")
                    for line in lines:
                        print(f"         {line}")
                        found_models[mark] = line.split()[0] if line.split() else None
                    break
        if mark not in found_models:
            print("       ❌ Not found")

    # Step 3: Copy models to D:/Ollama/models
    print("\n📌 Step 3: Copying models to D:/Ollama/models...")

    for mark, source_path in found_models.items():
        if source_path:
            filename = source_path.split('\\')[-1]
            dest_path = f"{local_models_path}\\{filename}"

            print(f"\n   Copying {mark}:")
            print(f"     From: {source_path}")
            print(f"     To: {dest_path}")

            # Check if already exists
            stdout, code = run_ssh_command(host, f"Test-Path '{dest_path}'")
            if "True" in stdout:
                print("     ⚠️  File already exists, skipping...")
            else:
                # Copy file
                cmd = f"Copy-Item '{source_path}' -Destination '{dest_path}' -Force -ErrorAction SilentlyContinue; Test-Path '{dest_path}'"
                stdout, code = run_ssh_command(host, cmd)
                if "True" in stdout:
                    print("     ✅ Copied successfully")
                else:
                    print(f"     ❌ Copy failed: {stdout}")

    # Step 4: Verify models in Docker volume
    print("\n📌 Step 4: Verifying models in Docker volume...")

    container = "iron-legion-mark-i-codellama-llamacpp"
    expected_models = {
        "Mark II": "Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf",
        "Mark VII": "gemma-2b-it.Q4_K_M.gguf"
    }

    for mark, filename in expected_models.items():
        cmd = f"docker exec {container} bash -c 'test -f /models/{filename} && echo \"EXISTS\" || echo \"MISSING\"'"
        stdout, code = run_ssh_command(host, cmd)
        if "EXISTS" in stdout:
            print(f"   ✅ {mark}: {filename} exists in container")
        else:
            print(f"   ❌ {mark}: {filename} missing in container")

    # Step 5: Restart containers
    print("\n📌 Step 5: Restarting containers...")

    containers_to_restart = [
        "iron-legion-mark-ii-llama32-llamacpp",
        "iron-legion-mark-vii-gemma-llamacpp"
    ]

    for container_name in containers_to_restart:
        print(f"   Restarting {container_name}...")
        stdout, code = run_ssh_command(host, f"docker restart {container_name}")
        if code == 0:
            print("     ✅ Restarted")
        time.sleep(5)

    print("\n⏳ Waiting 30 seconds for containers to initialize...")
    time.sleep(30)

    # Step 6: Check final status
    print("\n📌 Step 6: Final Status Check...")

    stdout, code = run_ssh_command(host, "docker ps --filter 'name=iron-legion' --format '{{.Names}}\t{{.Status}}' | Sort-Object")
    if stdout.strip():
        print("\n   Container Status:")
        for line in stdout.strip().split('\n'):
            if line.strip():
                print(f"     {line}")

    print("\n" + "=" * 80)
    print("✅ M Drive Setup Complete")
    print("=" * 80)

if __name__ == "__main__":


    main()