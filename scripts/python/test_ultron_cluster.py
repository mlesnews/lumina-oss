#!/usr/bin/env python3
"""Test ULTRON cluster connectivity using Python"""

import requests
import time

def test_endpoint(name, url, timeout=5):
    """Test if an endpoint is reachable"""
    print(f"\n=== Testing {name} ===")
    print(f"URL: {url}")

    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = time.time() - start_time

        if response.status_code == 200:
            print(f"✅ Success (HTTP {response.status_code})")
            print(f"Response time: {response_time:.2f} seconds")

            # Try to parse JSON if it's an API endpoint
            if url.endswith('/api/tags'):
                try:
                    data = response.json()
                    if 'models' in data:
                        print(f"Models available: {len(data['models'])}")
                        for model in data['models']:
                            print(f"  - {model['name']}")
                except Exception as e:
                    print(f"⚠️  Failed to parse JSON: {e}")

            return True
        else:
            print(f"❌ Failed (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ Timeout after {timeout} seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_all_endpoints():
    """Test all ULTRON cluster endpoints"""
    print("=== ULTRON Cluster Connectivity Test ===")
    print("Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()

    endpoints = [
        ("Local Ollama", "http://localhost:11434/api/tags"),
        ("KAIJU Iron Legion", "http://<NAS_PRIMARY_IP>:11437/api/tags"),
        ("ULTRON Router", "http://<NAS_PRIMARY_IP>:3008/health"),
        ("KAIJU Alternative 1", "http://kaiju_no_8:11437/api/tags"),
        ("KAIJU Alternative 2", "http://<NAS_IP>:11437/api/tags"),
    ]

    results = []
    for name, url in endpoints:
        success = test_endpoint(name, url)
        results.append((name, success))

    print("\n=== Summary ===")
    for name, success in results:
        status = "✅ ONLINE" if success else "❌ OFFLINE"
        print(f"{name}: {status}")

    # Check if we have any working endpoints
    working_endpoints = [name for name, success in results if success]

    if not working_endpoints:
        print("\n⚠️  All endpoints are offline!")
        print("\nTroubleshooting steps:")
        print("1. Check if Ollama is running locally: ollama serve")
        print("2. Verify network connectivity to KAIJU Iron Legion")
        print("3. Check if ULTRON router service is running")
    else:
        print(f"\n✅ {len(working_endpoints)} endpoint(s) are online")

    return working_endpoints

if __name__ == "__main__":
    test_all_endpoints()
