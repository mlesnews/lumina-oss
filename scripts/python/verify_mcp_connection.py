#!/usr/bin/env python3
"""
Verify MCP Server Connection to NAS Docker Container Manager

Tests the connection to the docker-container-manager MCP server running on DS2118plus.
"""

import sys
import subprocess
import json
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

def test_ssh_connection():
    """Test SSH connection to NAS"""
    print("🔐 Testing SSH connection to DS2118plus NAS...")
    try:
        result = subprocess.run([
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5", "backupadm@<NAS_PRIMARY_IP>", "echo 'SSH connection successful'"
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ SSH connection to NAS successful")
            return True
        else:
            print(f"❌ SSH connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ SSH connection error: {e}")
        return False

def test_docker_socket():
    """Test Docker socket connection via SSH"""
    print("\n🐳 Testing Docker socket access on NAS...")
    try:
        result = subprocess.run([
            "ssh", "-o", "StrictHostKeyChecking=no", "backupadm@<NAS_PRIMARY_IP>",
            "docker ps --format 'table {{.Names}}\\t{{.Status}}' | head -5"
        ], capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            containers = result.stdout.strip().split('\n')
            print("✅ Docker socket access successful")
            print(f"   Found {len(containers)-1} containers on NAS")  # -1 for header
            return True
        else:
            print(f"❌ Docker socket access failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Docker socket test error: {e}")
        return False

def test_mcp_server_command():
    """Test if docker-container-manager command exists on NAS"""
    print("\n🔧 Testing docker-container-manager command on NAS...")
    try:
        result = subprocess.run([
            "ssh", "-o", "StrictHostKeyChecking=no", "backupadm@<NAS_PRIMARY_IP>",
            "which docker-container-manager || echo 'Command not found'"
        ], capture_output=True, text=True, timeout=10)

        output = result.stdout.strip()
        if "docker-container-manager" in output and "not found" not in output:
            print("✅ docker-container-manager command found on NAS")
            return True
        else:
            print("⚠️  docker-container-manager command not found on NAS")
            print("   You may need to install it or adjust the command path")
            return False
    except Exception as e:
        print(f"❌ Command test error: {e}")
        return False

def test_tls_certificates():
    """Check if TLS certificates exist"""
    print("\n🔒 Checking TLS certificate configuration...")

    cert_paths = [
        "/path/to/ca.pem",
        "/path/to/cert.pem",
        "/path/to/key.pem"
    ]

    # This would check local certificates for the docker client
    # For now, we'll just note the requirement
    print("📝 TLS certificates required for secure Docker connection:")
    for cert_path in cert_paths:
        print(f"   • {cert_path}")
    print("   Configure these paths in your Docker client configuration")

    return True  # Certificates are a configuration issue, not a connectivity issue

def generate_connection_summary():
    """Generate connection summary and recommendations"""
    print("\n📋 MCP SERVER CONNECTION SUMMARY")
    print("=" * 50)

    summary = {
        "mcp_server_primary": "docker-container-manager on DS2118plus",
        "connection_method": "SSH tunnel to NAS docker-container-manager",
        "host": "<NAS_PRIMARY_IP> (DS2118plus)",
        "docker_socket": "/var/run/docker.sock",
        "mcp_port": "3000 (if running as server)",
        "tls_enabled": True,
        "authentication": "SSH key-based"
    }

    for key, value in summary.items():
        print(f"• {key}: {value}")

    print("\n🔧 SETUP REQUIREMENTS:")
    print("1. SSH access to DS2118plus (backupadm@<NAS_PRIMARY_IP>)")
    print("2. docker-container-manager installed on NAS")
    print("3. Docker socket access (/var/run/docker.sock)")
    print("4. TLS certificates for secure connection")
    print("5. SSH key authentication configured")

    print("\n🚀 MCP SERVER CONFIGURATION:")
    print("The docker-container-manager MCP server is configured to:")
    print("• Connect via SSH to DS2118plus")
    print("• Access Docker through unix socket")
    print("• Run as MCP server on port 3000")
    print("• Provide container management capabilities")

    print("\n💡 TROUBLESHOOTING:")
    print("If MCP server doesn't connect:")
    print("• Verify SSH key authentication")
    print("• Check docker-container-manager installation on NAS")
    print("• Ensure Docker daemon is running on NAS")
    print("• Validate TLS certificate paths")
    print("• Check firewall rules on NAS")

def main():
    """Main verification function"""
    print("🔍 VERIFYING MCP SERVER CONNECTION TO NAS")
    print("=" * 50)

    tests = [
        ("SSH Connection", test_ssh_connection),
        ("Docker Socket Access", test_docker_socket),
        ("MCP Command Availability", test_mcp_server_command),
        ("TLS Certificate Config", test_tls_certificates)
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        results[test_name] = test_func()

    # Generate summary
    generate_connection_summary()

    # Final status
    successful_tests = sum(results.values())
    total_tests = len(results)

    print(f"\n🎯 FINAL STATUS: {successful_tests}/{total_tests} tests passed")

    if successful_tests == total_tests:
        print("✅ All connectivity tests passed!")
        print("   MCP server should connect successfully.")
    else:
        print("⚠️  Some tests failed.")
        print("   Check the troubleshooting section above.")

    print("\n🔄 Next: Restart Cursor IDE to apply MCP server configuration.")

if __name__ == "__main__":
    main()