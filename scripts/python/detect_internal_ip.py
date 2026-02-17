#!/usr/bin/env python3
"""
Detect Internal IP Address on 10.17.17.x Network

Finds the actual IPv4 address on the internal network for email configuration.
"""

import socket
import subprocess
import sys
from pathlib import Path
import logging
logger = logging.getLogger("detect_internal_ip")


def get_local_ip():
    """Get local IP address by connecting to external server"""
    try:
        # Connect to external server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def get_network_interfaces():
    """Get all network interfaces using ipconfig (Windows)"""
    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    except Exception as e:
        print(f"Error running ipconfig: {e}")
        return None

def find_10_17_17_ip():
    """Find IP address on 10.17.17.x network"""
    interfaces = get_network_interfaces()
    if not interfaces:
        return None

    # Parse ipconfig output
    lines = interfaces.split('\n')
    current_adapter = None
    ip_addresses = []

    for line in lines:
        line = line.strip()
        if line and not line.startswith('-'):
            if 'adapter' in line.lower() or 'ethernet' in line.lower() or 'wi-fi' in line.lower():
                current_adapter = line
            elif 'IPv4' in line or 'IP Address' in line:
                # Extract IP address
                parts = line.split(':')
                if len(parts) > 1:
                    ip = parts[-1].strip()
                    if ip.startswith('10.17.17.'):
                        ip_addresses.append({
                            'adapter': current_adapter,
                            'ip': ip
                        })

    return ip_addresses

def main():
    try:
        """Main function"""
        print("\n" + "=" * 80)
        print("🔍 DETECTING INTERNAL IP ADDRESS (10.17.17.x Network)")
        print("=" * 80)
        print()

        # Method 1: Find 10.17.17.x addresses from ipconfig
        network_ips = find_10_17_17_ip()

        if network_ips:
            print("✅ Found IP addresses on 10.17.17.x network:")
            print()
            for item in network_ips:
                print(f"   Adapter: {item['adapter']}")
                print(f"   IP Address: {item['ip']}")
                print()

            # Use first one found
            primary_ip = network_ips[0]['ip']
            print(f"📌 Primary IP: {primary_ip}")
            print()

            # Check if it matches the configured server
            config_file = Path(__file__).parent.parent.parent / "config" / "outlook" / "hybrid_email_config.json"
            if config_file.exists():
                import json
                with open(config_file, 'r') as f:
                    config = json.load(f)

                configured_server = config.get("nas_mail_hub", {}).get("imap", {}).get("server", "")
                if configured_server != primary_ip:
                    print(f"⚠️  Note: Configured server is {configured_server}, but your IP is {primary_ip}")
                    print(f"   The server should be accessible from your IP on the same network.")
        else:
            print("⚠️  No IP addresses found on 10.17.17.x network")
            print()
            print("Current network interfaces:")
            interfaces = get_network_interfaces()
            if interfaces:
                # Show relevant parts
                lines = interfaces.split('\n')
                for i, line in enumerate(lines):
                    if 'IPv4' in line or 'IP Address' in line or '10.' in line:
                        print(f"   {line.strip()}")

            # Try alternative method
            local_ip = get_local_ip()
            if local_ip:
                print()
                print(f"📌 Detected local IP: {local_ip}")
                if local_ip.startswith('10.17.17.'):
                    print("   ✅ This is on the 10.17.17.x network!")
                else:
                    print(f"   ⚠️  This is NOT on 10.17.17.x network (it's {'.'.join(local_ip.split('.')[:3])}.x)")

        print()
        print("=" * 80)
        print()
        print("💡 Email Server Configuration:")
        print("   Server: <NAS_PRIMARY_IP> (NAS Mail Hub)")
        print("   Your IP should be on the same 10.17.17.x network")
        print("   VPN may route traffic differently, but internal IP should remain the same")
        print()

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()