#!/usr/bin/env python3
"""Test SSH connectivity to Kaiju_no_8 and check Ollama status"""

import subprocess
import time

def test_ssh_connectivity():
    """Test SSH connection to Kaiju_no_8"""
    print("=== Testing SSH Connection to Kaiju_no_8 (<NAS_IP>) ===")
    try:
        # Try to run a simple command
        result = subprocess.run(
            ["ssh", "mlesn@<NAS_IP>", "echo 'SSH Connection Successful'"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ SSH connection successful")
            print("Output:", result.stdout.strip())
            return True
        else:
            print("❌ SSH connection failed with return code:", result.returncode)
            print("Error:", result.stderr.strip())
            return False

    except subprocess.TimeoutExpired:
        print("❌ SSH connection timed out")
        return False
    except Exception as e:
        print(f"❌ SSH connection error: {e}")
        return False

def check_ollama_status():
    """Check if Ollama is running on Kaiju_no_8"""
    print("\n=== Checking Ollama Status on Kaiju_no_8 ===")
    try:
        # Check if Ollama process is running
        result = subprocess.run(
            ["ssh", "mlesn@<NAS_IP>", "tasklist | findstr ollama"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ Ollama is running on Kaiju_no_8")
            print("Process info:", result.stdout.strip())
            return True
        else:
            print("❌ Ollama not running on Kaiju_no_8")
            if result.stderr:
                print("Error:", result.stderr.strip())
            return False

    except Exception as e:
        print(f"❌ Error checking Ollama status: {e}")
        return False

def check_ollama_endpoint():
    """Test if Ollama API endpoint is responding"""
    print("\n=== Testing Ollama API Endpoint ===")
    try:
        result = subprocess.run(
            ["ssh", "mlesn@<NAS_IP>", 
             "curl -s http://localhost:11434/api/tags || curl -s http://localhost:11437/api/tags"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and "models" in result.stdout:
            print("✅ Ollama API endpoint responding")
            return True
        else:
            print("❌ Ollama API endpoint not responding")
            if result.stdout:
                print("Response:", result.stdout.strip())
            if result.stderr:
                print("Error:", result.stderr.strip())
            return False

    except Exception as e:
        print(f"❌ Error testing API endpoint: {e}")
        return False

def start_ollama_service():
    """Try to start Ollama service on Kaiju_no_8"""
    print("\n=== Starting Ollama Service ===")
    try:
        result = subprocess.run(
            ["ssh", "mlesn@<NAS_IP>", 
             "net start Ollama || sc start Ollama || ollama serve"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✅ Ollama service started successfully")
            time.sleep(5)  # Wait for service to fully start
            return True
        else:
            print("❌ Failed to start Ollama service")
            print("Output:", result.stdout.strip())
            print("Error:", result.stderr.strip())
            return False

    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

if __name__ == "__main__":
    print("ULTRON Cluster Repair - Kaiju_no_8")
    print("=" * 50)

    # Step 1: Test SSH connectivity
    ssh_connected = test_ssh_connectivity()
    if not ssh_connected:
        print("\n❌ Cannot connect to Kaiju_no_8. Please check:")
        print("   - Network connectivity")
        print("   - SSH service is running")
        print("   - Firewall settings")
        exit(1)

    # Step 2: Check Ollama status
    ollama_running = check_ollama_status()
    if not ollama_running:
        print("\n🔧 Attempting to start Ollama service...")
        ollama_running = start_ollama_service()

    # Step 3: Test API endpoint
    api_responding = check_ollama_endpoint()

    print("\n" + "=" * 50)
    print("Repair Completed")
    print("=" * 50)

    print(f"SSH Connectivity: {'✅' if ssh_connected else '❌'}")
    print(f"Ollama Service: {'✅' if ollama_running else '❌'}")
    print(f"API Endpoint: {'✅' if api_responding else '❌'}")

    if ssh_connected and ollama_running and api_responding:
        print("\n✅ Kaiju_no_8 ULTRON cluster node is operational!")
    else:
        print("\n❌ Kaiju_no_8 ULTRON cluster node is not fully operational.")
        print("Please check the error messages above.")
