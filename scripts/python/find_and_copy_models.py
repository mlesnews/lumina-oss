#!/usr/bin/env python3
"""
Find and Copy Models from KAIJU to NAS
"""
import subprocess
import os
import glob

def run_ssh_command(host, command):
    """Run command via SSH"""
    ssh_cmd = ["ssh", host, command]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=300)
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def main():
    host = "<NAS_IP>"
    nas_host = "<NAS_PRIMARY_IP>"

    print("=" * 80)
    print("Finding and Copying Models")
    print("=" * 80)

    # Find models on KAIJU
    print("\nSearching for models on KAIJU...")

    # Search for Mark II
    cmd = "Get-ChildItem 'D:\\' -Recurse -Filter '*llama*3.2*.gguf' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName"
    stdout, code = run_ssh_command(host, cmd)
    markII_path = stdout.strip() if code == 0 and stdout.strip() else None

    if not markII_path:
        cmd = "Get-ChildItem 'C:\\', 'E:\\', 'F:\\', 'G:\\' -Recurse -Filter '*llama*3.2*.gguf' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName"
        stdout, code = run_ssh_command(host, cmd)
        markII_path = stdout.strip() if code == 0 and stdout.strip() else None

    # Search for Mark VII
    cmd = "Get-ChildItem 'D:\\' -Recurse -Filter '*gemma*2b*.gguf' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName"
    stdout, code = run_ssh_command(host, cmd)
    markVII_path = stdout.strip() if code == 0 and stdout.strip() else None

    if not markVII_path:
        cmd = "Get-ChildItem 'C:\\', 'E:\\', 'F:\\', 'G:\\' -Recurse -Filter '*gemma*2b*.gguf' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName"
        stdout, code = run_ssh_command(host, cmd)
        markVII_path = stdout.strip() if code == 0 and stdout.strip() else None

    # Copy to NAS and local
    if markII_path:
        print(f"\nFound Mark II: {markII_path}")
        print("Copying to NAS...")
        cmd = f"scp {markII_path} {nas_host}:/volume1/models/"
        stdout, code = run_ssh_command(host, cmd)
        if code == 0:
            print("  Copied to NAS")
        else:
            print(f"  NAS copy: {stdout}")

        print("Copying to D:\\Ollama\\models...")
        cmd = f"Copy-Item '{markII_path}' -Destination 'D:\\Ollama\\models\\' -Force"
        stdout, code = run_ssh_command(host, cmd)
        if code == 0:
            print("  Copied to local")
    else:
        print("\nMark II model not found")

    if markVII_path:
        print(f"\nFound Mark VII: {markVII_path}")
        print("Copying to NAS...")
        cmd = f"scp {markVII_path} {nas_host}:/volume1/models/"
        stdout, code = run_ssh_command(host, cmd)
        if code == 0:
            print("  Copied to NAS")
        else:
            print(f"  NAS copy: {stdout}")

        print("Copying to D:\\Ollama\\models...")
        cmd = f"Copy-Item '{markVII_path}' -Destination 'D:\\Ollama\\models\\' -Force"
        stdout, code = run_ssh_command(host, cmd)
        if code == 0:
            print("  Copied to local")
    else:
        print("\nMark VII model not found")

    # Verify
    print("\nVerifying files...")
    cmd = "Get-ChildItem 'D:\\Ollama\\models' -Filter '*.gguf' | Select-Object Name | Sort-Object Name"
    stdout, code = run_ssh_command(host, cmd)
    if stdout:
        print(stdout)

    print("\n" + "=" * 80)
    print("Done")
    print("=" * 80)

if __name__ == "__main__":


    main()