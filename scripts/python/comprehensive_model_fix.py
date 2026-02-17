#!/usr/bin/env python3
"""
Comprehensive Model Fix - Find and Copy Actual .gguf Files
Fixes directory issue by finding actual files and copying them

Tags: #IRON_LEGION #COMPREHENSIVE_FIX #ROOT_CAUSE @JARVIS @LUMINA @DOIT
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
    """Main comprehensive fix"""
    host = "<NAS_IP>"

    print("=" * 80)
    print("🔧 Comprehensive Model Fix - Root Cause Solution")
    print("=" * 80)

    # Step 1: Remove empty directories
    print("\n📌 Step 1: Removing empty directories...")
    cmd = "Remove-Item 'D:\\Ollama\\models\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item 'D:\\Ollama\\models\\gemma-2b-it.Q4_K_M.gguf' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host 'Directories removed'"
    stdout, code = run_ssh_command(host, cmd)
    print(f"  {stdout.strip()}")

    # Step 2: Find actual .gguf files on D drive
    print("\n📌 Step 2: Searching for actual .gguf files on D drive...")

    # Search for Mark II (llama3.2)
    print("  Searching for Llama-3.2-11B model...")
    cmd = "Get-ChildItem 'D:\\' -Recurse -Filter '*.gguf' -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*Llama*3.2*11B*' -and $_.PSIsContainer -eq $false -and $_.Length -gt 1GB } | Select-Object -First 1 | ForEach-Object { $_.FullName }"
    stdout, code = run_ssh_command(host, cmd)
    markII_path = stdout.strip() if stdout.strip() else None

    if markII_path:
        print(f"  ✅ Found Mark II: {markII_path}")
    else:
        print("  ❌ Mark II file not found")

    # Search for Mark VII (gemma)
    print("  Searching for gemma-2b model...")
    cmd = "Get-ChildItem 'D:\\' -Recurse -Filter '*.gguf' -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*gemma*2b*' -and $_.PSIsContainer -eq $false -and $_.Length -gt 1MB } | Select-Object -First 1 | ForEach-Object { $_.FullName }"
    stdout, code = run_ssh_command(host, cmd)
    markVII_path = stdout.strip() if stdout.strip() else None

    if markVII_path:
        print(f"  ✅ Found Mark VII: {markVII_path}")
    else:
        print("  ❌ Mark VII file not found")

    # Step 3: Copy files
    print("\n📌 Step 3: Copying actual .gguf files...")

    if markII_path:
        print(f"  Copying Mark II from {markII_path}...")
        cmd = f"Copy-Item '{markII_path}' -Destination 'D:\\Ollama\\models\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf' -Force; if (Test-Path 'D:\\Ollama\\models\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf') {{ Write-Host 'Mark II copied successfully' }} else {{ Write-Host 'Mark II copy failed' }}"
        stdout, code = run_ssh_command(host, cmd)
        print(f"  {stdout.strip()}")

    if markVII_path:
        print(f"  Copying Mark VII from {markVII_path}...")
        cmd = f"Copy-Item '{markVII_path}' -Destination 'D:\\Ollama\\models\\gemma-2b-it.Q4_K_M.gguf' -Force; if (Test-Path 'D:\\Ollama\\models\\gemma-2b-it.Q4_K_M.gguf') {{ Write-Host 'Mark VII copied successfully' }} else {{ Write-Host 'Mark VII copy failed' }}"
        stdout, code = run_ssh_command(host, cmd)
        print(f"  {stdout.strip()}")

    # Step 4: Verify files
    print("\n📌 Step 4: Verifying files...")
    cmd = "Get-ChildItem 'D:\\Ollama\\models' -Filter '*.gguf' | Where-Object { -not $_.PSIsContainer } | Select-Object Name, @{N='SizeGB';E={[math]::Round($_.Length/1GB,2)}} | Format-Table -AutoSize"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print(stdout)

    # Step 5: Verify in container
    print("\n📌 Step 5: Verifying in Docker container...")
    cmd = "docker exec iron-legion-mark-i-codellama-llamacpp bash -c 'ls -lh /models/*.gguf 2>&1'"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        lines = [l for l in stdout.split('\n') if 'llama.*3.*2' in l.lower() or 'gemma' in l.lower() or '.gguf' in l]
        for line in lines[:10]:
            print(f"  {line}")

    # Step 6: Restart containers
    print("\n📌 Step 6: Restarting containers...")
    containers = [
        "iron-legion-mark-ii-llama32-llamacpp",
        "iron-legion-mark-vii-gemma-llamacpp"
    ]

    for container in containers:
        print(f"  Restarting {container}...")
        cmd = f"docker restart {container}"
        stdout, code = run_ssh_command(host, cmd)
        if code == 0:
            print(f"    ✅ Restarted")
        time.sleep(3)

    print("\n⏳ Waiting 45 seconds for containers to initialize...")
    time.sleep(45)

    # Step 7: Check final status
    print("\n📌 Step 7: Final Status Check...")
    cmd = "docker ps --filter 'name=iron-legion' --format '{{.Names}}\t{{.Status}}' | Sort-Object"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print("\n  Container Status:")
        for line in stdout.strip().split('\n'):
            if line.strip():
                if 'Up' in line and 'restarting' not in line.lower():
                    print(f"    ✅ {line}")
                elif 'restarting' in line.lower():
                    print(f"    ⚠️  {line}")
                else:
                    print(f"    {line}")

    print("\n" + "=" * 80)
    print("✅ Comprehensive Fix Complete")
    print("=" * 80)

if __name__ == "__main__":


    main()