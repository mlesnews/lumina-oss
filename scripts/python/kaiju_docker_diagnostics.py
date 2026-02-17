#!/usr/bin/env python3
"""
KAIJU Docker Diagnostics
Connects to KAIJU_NO_8 via SSH and checks Docker containers and Ollama status

Tags: #KAIJU #DOCKER #DIAGNOSTICS #SSH @JARVIS @LUMINA @DOIT
"""

import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

def run_ssh_command(host: str, command: str, user: str = None) -> tuple[str, int]:
    """Run command via SSH"""
    if user:
        ssh_cmd = ["ssh", f"{user}@{host}", command]
    else:
        ssh_cmd = ["ssh", host, command]

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return "Command timed out", 1
    except Exception as e:
        return str(e), 1

def check_docker_containers(host: str = "<NAS_IP>", user: str = None):
    """Check Docker containers on KAIJU"""
    print(f"\n🐳 Checking Docker containers on {host}...")

    # List all containers
    stdout, code = run_ssh_command(host, "docker ps -a", user)
    if code == 0:
        print("✅ Docker containers:")
        print(stdout)
    else:
        print(f"❌ Error: {stdout}")
        return None

    # Check for Ollama containers
    stdout, code = run_ssh_command(host, "docker ps --filter 'name=ollama' --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'", user)
    if code == 0 and stdout.strip():
        print("\n✅ Ollama containers:")
        print(stdout)
    else:
        print("\n⚠️  No Ollama containers found")

    # Check for Iron Legion containers
    stdout, code = run_ssh_command(host, "docker ps --filter 'name=iron' --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'", user)
    if code == 0 and stdout.strip():
        print("\n✅ Iron Legion containers:")
        print(stdout)

    return stdout

def check_ollama_service(host: str = "<NAS_IP>", user: str = None):
    """Check Ollama service status"""
    print(f"\n🔍 Checking Ollama service on {host}...")

    # Check if Ollama is running (systemd)
    stdout, code = run_ssh_command(host, "systemctl is-active ollama 2>/dev/null || echo 'not-systemd'", user)
    if "active" in stdout:
        print(f"✅ Ollama service: {stdout.strip()}")
    else:
        print("⚠️  Ollama not running as systemd service")

    # Check Ollama process
    stdout, code = run_ssh_command(host, "ps aux | grep -i ollama | grep -v grep", user)
    if code == 0 and stdout.strip():
        print("✅ Ollama process found:")
        print(stdout)
    else:
        print("⚠️  No Ollama process found")

    # Check ports
    stdout, code = run_ssh_command(host, "netstat -tuln | grep -E ':(11434|11437)' || ss -tuln | grep -E ':(11434|11437)'", user)
    if code == 0 and stdout.strip():
        print("\n✅ Ports 11434/11437:")
        print(stdout)
    else:
        print("\n⚠️  Ports 11434/11437 not listening")

def check_ollama_api(host: str = "<NAS_IP>", user: str = None):
    """Check Ollama API from KAIJU locally"""
    print(f"\n🌐 Testing Ollama API from {host}...")

    # Test localhost:11434
    stdout, code = run_ssh_command(host, "curl -s http://localhost:11434/api/tags 2>&1 | head -20", user)
    if code == 0 and "models" in stdout:
        print("✅ localhost:11434/api/tags - Working")
        print(stdout[:500])
    else:
        print(f"❌ localhost:11434/api/tags - {stdout[:200]}")

    # Test localhost:11437
    stdout, code = run_ssh_command(host, "curl -s http://localhost:11437/api/tags 2>&1 | head -20", user)
    if code == 0 and "models" in stdout:
        print("\n✅ localhost:11437/api/tags - Working")
        print(stdout[:500])
    elif "404" in stdout or "Not Found" in stdout:
        print("\n⚠️  localhost:11437/api/tags - 404 (router may need config)")
    else:
        print(f"\n❌ localhost:11437/api/tags - {stdout[:200]}")

def check_docker_compose(host: str = "<NAS_IP>", user: str = None):
    """Check for docker-compose files"""
    print(f"\n📋 Checking for docker-compose on {host}...")

    # Find docker-compose files
    stdout, code = run_ssh_command(host, "find ~ -name 'docker-compose*.yml' -o -name 'docker-compose*.yaml' 2>/dev/null | head -10", user)
    if code == 0 and stdout.strip():
        print("✅ Found docker-compose files:")
        print(stdout)
    else:
        print("⚠️  No docker-compose files found in home directory")

def main():
    """Main diagnostic"""
    import argparse

    parser = argparse.ArgumentParser(description="KAIJU Docker Diagnostics")
    parser.add_argument("--host", default="<NAS_IP>", help="KAIJU hostname or IP")
    parser.add_argument("--user", help="SSH username (optional)")

    args = parser.parse_args()

    print("=" * 80)
    print("🔧 KAIJU Docker Diagnostics")
    print("=" * 80)
    print(f"Host: {args.host}")
    print(f"User: {args.user or 'default'}")
    print("=" * 80)

    # Run diagnostics
    check_docker_containers(args.host, args.user)
    check_ollama_service(args.host, args.user)
    check_ollama_api(args.host, args.user)
    check_docker_compose(args.host, args.user)

    print("\n" + "=" * 80)
    print("✅ Diagnostics complete")
    print("=" * 80)

if __name__ == "__main__":


    main()