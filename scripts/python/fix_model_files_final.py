#!/usr/bin/env python3
"""
Fix Model Files - Final Solution
Uses directory name as prefix to find actual .gguf files

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
            timeout=120
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def main():
    """Main fix"""
    host = "<NAS_IP>"

    print("=" * 80)
    print("🔧 Fix Model Files - Final Solution")
    print("=" * 80)

    # Step 1: Remove directories
    print("\n📌 Step 1: Removing empty directories...")
    cmd = "if (Test-Path 'D:\\Ollama\\models\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf' -PathType Container) { Remove-Item 'D:\\Ollama\\models\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf' -Recurse -Force; Write-Host 'Removed Mark II directory' }; if (Test-Path 'D:\\Ollama\\models\\gemma-2b-it.Q4_K_M.gguf' -PathType Container) { Remove-Item 'D:\\Ollama\\models\\gemma-2b-it.Q4_K_M.gguf' -Recurse -Force; Write-Host 'Removed Mark VII directory' }"
    stdout, code = run_ssh_command(host, cmd)
    print(stdout)

    # Step 2: Find files using prefix (directory name without suffix)
    print("\n📌 Step 2: Finding actual .gguf files using prefix...")

    # Mark II: Look for files starting with "Llama-3.2-11B"
    print("  Searching for Llama-3.2-11B* files...")
    cmd = "Get-ChildItem 'D:\\Ollama\\models' -Filter 'Llama-3.2-11B*.gguf' -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.Length -gt 1GB } | Select-Object -First 1 -ExpandProperty FullName"
    stdout1, _ = run_ssh_command(host, cmd)

    if not stdout1.strip():
        # Search D drive
        cmd = "Get-ChildItem 'D:\\' -Recurse -Filter 'Llama-3.2-11B*.gguf' -ErrorAction SilentlyContinue -Depth 3 | Where-Object { -not $_.PSIsContainer -and $_.Length -gt 1GB } | Select-Object -First 1 -ExpandProperty FullName"
        stdout1, _ = run_ssh_command(host, cmd)

    markII_path = stdout1.strip() if stdout1.strip() else None

    # Mark VII: Look for files starting with "gemma-2b"
    print("  Searching for gemma-2b* files...")
    cmd = "Get-ChildItem 'D:\\Ollama\\models' -Filter 'gemma-2b*.gguf' -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.Length -gt 1MB } | Select-Object -First 1 -ExpandProperty FullName"
    stdout2, _ = run_ssh_command(host, cmd)

    if not stdout2.strip():
        # Search D drive
        cmd = "Get-ChildItem 'D:\\' -Recurse -Filter 'gemma-2b*.gguf' -ErrorAction SilentlyContinue -Depth 3 | Where-Object { -not $_.PSIsContainer -and $_.Length -gt 1MB } | Select-Object -First 1 -ExpandProperty FullName"
        stdout2, _ = run_ssh_command(host, cmd)

    markVII_path = stdout2.strip() if stdout2.strip() else None

    # Step 3: Copy files
    print("\n📌 Step 3: Copying files...")

    if markII_path:
        print(f"  ✅ Found Mark II: {markII_path.split(chr(92))[-1]}")
        cmd = f"Copy-Item '{markII_path}' -Destination 'D:\\Ollama\\models\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf' -Force; Test-Path 'D:\\Ollama\\models\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf' -PathType Leaf"
        stdout, code = run_ssh_command(host, cmd)
        if "True" in stdout:
            print("  ✅ Mark II copied successfully")
        else:
            print("  ❌ Mark II copy failed")
    else:
        print("  ❌ Mark II file not found")

    if markVII_path:
        print(f"  ✅ Found Mark VII: {markVII_path.split(chr(92))[-1]}")
        cmd = f"Copy-Item '{markVII_path}' -Destination 'D:\\Ollama\\models\\gemma-2b-it.Q4_K_M.gguf' -Force; Test-Path 'D:\\Ollama\\models\\gemma-2b-it.Q4_K_M.gguf' -PathType Leaf"
        stdout, code = run_ssh_command(host, cmd)
        if "True" in stdout:
            print("  ✅ Mark VII copied successfully")
        else:
            print("  ❌ Mark VII copy failed")
    else:
        print("  ❌ Mark VII file not found")

    # Step 4: Verify
    print("\n📌 Step 4: Verifying files...")
    cmd = "Get-ChildItem 'D:\\Ollama\\models' -Filter '*.gguf' | Where-Object { -not $_.PSIsContainer } | Select-Object Name, Length | Format-Table -AutoSize"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print(stdout)

    # Step 5: Restart containers
    print("\n📌 Step 5: Restarting containers...")
    for container in ["iron-legion-mark-ii-llama32-llamacpp", "iron-legion-mark-vii-gemma-llamacpp"]:
        print(f"  Restarting {container}...")
        cmd = f"docker restart {container}"
        stdout, code = run_ssh_command(host, cmd)
        if code == 0:
            print("    ✅ Restarted")
        time.sleep(3)

    print("\n⏳ Waiting 45 seconds...")
    time.sleep(45)

    # Step 6: Final check
    print("\n📌 Step 6: Final Status...")
    cmd = "docker ps --filter 'name=iron-legion-mark-ii' --filter 'name=iron-legion-mark-vii' --format '{{.Names}}\t{{.Status}}'"
    stdout, code = run_ssh_command(host, cmd)
    if stdout.strip():
        print(stdout)

    print("\n" + "=" * 80)
    print("✅ Fix Complete")
    print("=" * 80)

if __name__ == "__main__":


    main()