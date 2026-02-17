#!/usr/bin/env python3
"""
Find All Iron Legion Models
Searches all drives for missing model files

Tags: #IRON_LEGION #FIND_MODELS @JARVIS @LUMINA @DOIT
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
            timeout=120
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def search_for_models():
    """Search all drives for missing models"""
    host = "<NAS_IP>"

    print("=" * 80)
    print("🔍 Search for All Iron Legion Models")
    print("=" * 80)

    # Missing models to find
    missing_models = [
        ("Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf", "Mark II"),
        ("gemma-2b-it.Q4_K_M.gguf", "Mark VII"),
        ("llama3.2", "Mark II (any variant)"),
        ("gemma-2b", "Mark VII (any variant)")
    ]

    print("\n🔍 Searching for missing models...\n")

    # Search D drive (most likely location)
    print("📀 Searching D: drive...")
    for model_pattern, mark in missing_models:
        # Search for exact name or pattern
        if ".gguf" in model_pattern:
            search_pattern = f"*{model_pattern.split('.')[0]}*.gguf"
        else:
            search_pattern = f"*{model_pattern}*.gguf"

        cmd = f"Get-ChildItem -Path D:\\ -Recurse -Filter '{search_pattern}' -ErrorAction SilentlyContinue | Select-Object FullName, Length -First 3"
        stdout, code = run_ssh_command(host, cmd)

        if stdout.strip() and "FullName" in stdout:
            print(f"\n  ✅ Found {mark}:")
            # Parse output
            lines = [l.strip() for l in stdout.split('\n') if l.strip() and 'FullName' not in l and '----' not in l]
            for line in lines[:3]:
                if line:
                    print(f"     {line[:100]}")

    # Check Docker volume location
    print("\n🐳 Checking Docker volume location...")
    stdout, code = run_ssh_command(host, "docker volume inspect iron-legion-llamacpp_iron-legion-models --format '{{.Options.device}}'")
    if code == 0 and stdout.strip():
        volume_path = stdout.strip()
        print(f"  📍 Volume path: {volume_path}")

        # Check if missing models are there with different names
        for model_pattern, mark in missing_models:
            if ".gguf" in model_pattern:
                base_name = model_pattern.split('.')[0]
                cmd = f"Get-ChildItem '{volume_path}' -Filter '*{base_name}*' -ErrorAction SilentlyContinue | Select-Object Name"
                stdout2, code2 = run_ssh_command(host, cmd)
                if stdout2.strip() and "Name" in stdout2:
                    print(f"  ✅ Found similar file for {mark}:")
                    print(f"     {stdout2.strip()}")

    # List all .gguf files in D:/Ollama/models
    print("\n📋 All .gguf files in D:/Ollama/models:")
    stdout, code = run_ssh_command(host, "Get-ChildItem 'D:\\Ollama\\models' -Filter '*.gguf' | Select-Object Name, Length")
    if code == 0:
        print(stdout)

    print("\n" + "=" * 80)
    print("✅ Search complete")
    print("=" * 80)

if __name__ == "__main__":
    search_for_models()
