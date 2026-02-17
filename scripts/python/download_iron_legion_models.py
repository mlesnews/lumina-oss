#!/usr/bin/env python3
"""
Download Missing Iron Legion Models
Downloads missing model files using huggingface-cli or direct download

Tags: #IRON_LEGION #DOWNLOAD #MODELS @JARVIS @LUMINA @DOIT
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
            timeout=300
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def check_and_download_model(container: str, model_name: str, model_path: str):
    """Check if model exists, download if missing"""
    host = "<NAS_IP>"

    print(f"\n📦 Checking {model_name}...")

    # Check if file exists
    cmd = f"docker exec {container} test -f {model_path} && echo 'EXISTS' || echo 'MISSING'"
    stdout, code = run_ssh_command(host, cmd)

    if "EXISTS" in stdout:
        print(f"  ✅ Model file exists: {model_path}")
        return True

    print(f"  ❌ Model file missing: {model_path}")
    print("  ⚠️  Model download not implemented - requires manual download")
    print(f"  💡 Suggestion: Download model file to {model_path}")
    return False

def main():
    """Main"""
    print("=" * 80)
    print("📥 Download Missing Iron Legion Models")
    print("=" * 80)

    models_to_check = [
        ("iron-legion-mark-ii-llama32-llamacpp", "llama3.2:11b", "/models/Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf"),
        ("iron-legion-mark-iii-qwen-llamacpp", "qwen2.5-coder:1.5b", "/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"),
        ("iron-legion-mark-vi-mixtral-llamacpp", "mixtral:8x7b", "/models/mixtral-8x7b-v0.1.Q4_K_M.gguf"),
        ("iron-legion-mark-vii-gemma-llamacpp", "gemma:2b", "/models/gemma-2b-it.Q4_K_M.gguf"),
    ]

    all_exist = True
    for container, model_name, model_path in models_to_check:
        exists = check_and_download_model(container, model_name, model_path)
        if not exists:
            all_exist = False

    print("\n" + "=" * 80)
    if all_exist:
        print("✅ All models exist")
    else:
        print("⚠️  Some models are missing - manual download required")
        print("\n💡 To download models:")
        print("   1. SSH to KAIJU: ssh <NAS_IP>")
        print("   2. Access container: docker exec -it <container> bash")
        print("   3. Download model using huggingface-cli or wget")
    print("=" * 80)

if __name__ == "__main__":


    main()