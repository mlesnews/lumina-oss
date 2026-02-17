#!/usr/bin/env python3
"""
Map M Drive and Fix Iron Legion Models
Maps M drive (if network share) and updates Docker mounts

Tags: #IRON_LEGION #M_DRIVE #MAP #FIX @JARVIS @LUMINA @DOIT
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

def main():
    """Main"""
    host = "<NAS_IP>"

    print("=" * 80)
    print("🗺️  Map M Drive and Fix Iron Legion Models")
    print("=" * 80)

    # Check current status
    print("\n📊 Current Status:")
    print("  ✅ Models in D:/Ollama/models: 5 files")
    print("  ❌ Missing: Llama-3.2-11B (Mark II), gemma-2b (Mark VII)")

    # Check for network shares
    print("\n🔍 Checking for network shares...")
    stdout, code = run_ssh_command(host, "net share")
    if code == 0 and stdout.strip():
        print("  Network shares found:")
        print(stdout[:500])

    # Check if M drive should be mapped
    print("\n🗺️  To map M drive for models:")
    print("  1. If M drive is a network share:")
    print("     net use M: \\\\server\\share /persistent:yes")
    print("  2. If models are on another drive (R:, H:, etc.):")
    print("     Check that drive for model files")
    print("  3. Update Docker volume to mount M drive:")
    print("     Update docker-compose.iron-legion.yml")

    # Check Docker volume config
    print("\n🐳 Current Docker Volume Config:")
    stdout, code = run_ssh_command(host, "docker volume inspect iron-legion-llamacpp_iron-legion-models --format '{{json .Options}}'")
    if code == 0:
        import json
        try:
            options = json.loads(stdout)
            current_path = options.get("device", "unknown")
            print(f"  📍 Current mount: {current_path}")
            print("  💡 To change to M drive, update to: M:/models or M:/Ollama/models")
        except:
            print(f"  📍 Config: {stdout.strip()}")

    print("\n" + "=" * 80)
    print("📝 Next Steps:")
    print("  1. Map M drive if it's a network share")
    print("  2. Verify models are on M drive")
    print("  3. Update Docker volume mount to point to M drive")
    print("  4. Restart containers")
    print("=" * 80)

    # Provide docker-compose update example
    print("\n📝 Docker Compose Update Example:")
    print("  volumes:")
    print("    iron-legion-models:")
    print("      driver: local")
    print("      driver_opts:")
    print("        type: none")
    print("        o: bind")
    print("        device: M:/models  # or M:/Ollama/models")

if __name__ == "__main__":


    main()