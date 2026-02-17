"""
Neo Browser Connectivity Diagnostics Script

Helps diagnose Neo browser network connectivity issues.
"""
import sys
import subprocess
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("NeoDiagnostics")

def run_powershell_command(command: str) -> tuple[str, int]:
    """Run a PowerShell command and return output and exit code."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return "", 1

def test_connectivity():
    """Test connectivity to Google services."""
    logger.info("\n" + "="*80)
    logger.info("CONNECTIVITY TESTS")
    logger.info("="*80)

    endpoints = [
        ("Google", "google.com"),
        ("Google Accounts", "accounts.google.com"),
        ("OAuth2 API", "oauth2.googleapis.com"),
        ("Google APIs", "www.googleapis.com"),
    ]

    results = {}
    for name, host in endpoints:
        logger.info(f"\nTesting {name} ({host})...")
        command = f"Test-NetConnection {host} -Port 443 -InformationLevel Quiet"
        output, code = run_powershell_command(command)
        success = code == 0
        results[name] = success
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"  {status}")

    return results

def check_dns_resolution():
    """Check DNS resolution for Google services."""
    logger.info("\n" + "="*80)
    logger.info("DNS RESOLUTION TESTS")
    logger.info("="*80)

    hosts = ["google.com", "accounts.google.com", "oauth2.googleapis.com"]
    results = {}

    for host in hosts:
        logger.info(f"\nResolving {host}...")
        command = f"Resolve-DnsName {host} -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty IPAddress"
        output, code = run_powershell_command(command)
        if output and output.strip():
            logger.info(f"  ✅ Resolved to: {output.strip()}")
            results[host] = True
        else:
            logger.info(f"  ❌ Failed to resolve")
            results[host] = False

    return results

def check_firewall_rules():
    """Check firewall rules for browsers."""
    logger.info("\n" + "="*80)
    logger.info("FIREWALL RULES CHECK")
    logger.info("="*80)

    logger.info("\nChecking for browser-related firewall rules...")

    # Check for common browser processes
    browsers = ["chrome", "edge", "firefox", "neo"]
    found_rules = []

    for browser in browsers:
        command = f"Get-NetFirewallRule | Where-Object {{$_.DisplayName -like '*{browser}*'}} | Select-Object DisplayName, Enabled, Direction | Format-Table -AutoSize"
        output, code = run_powershell_command(command)
        if output and output.strip() and "DisplayName" in output:
            logger.info(f"\n  {browser.upper()} rules found:")
            logger.info(output)
            found_rules.append(browser)

    if not found_rules:
        logger.info("  ⚠️  No browser-specific firewall rules found")
        logger.info("  💡 You may need to add Neo browser to firewall exceptions")

    return found_rules

def check_proxy_settings():
    """Check proxy settings."""
    logger.info("\n" + "="*80)
    logger.info("PROXY SETTINGS CHECK")
    logger.info("="*80)

    logger.info("\nChecking system proxy settings...")

    command = "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings' | Select-Object ProxyEnable, ProxyServer, AutoConfigURL | Format-List"
    output, code = run_powershell_command(command)

    if output:
        logger.info(output)

    # Check registry for proxy settings
    command = "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings' -Name ProxyEnable -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProxyEnable"
    proxy_enabled, _ = run_powershell_command(command)

    if proxy_enabled and proxy_enabled.strip() == "1":
        logger.info("\n  ⚠️  Proxy is ENABLED")
        logger.info("  💡 If Neo has connectivity issues, check proxy configuration")
    else:
        logger.info("\n  ℹ️  Proxy is DISABLED (or not configured)")

    return proxy_enabled == "1" if proxy_enabled else False

def check_browser_processes():
    """Check if browser processes are running."""
    logger.info("\n" + "="*80)
    logger.info("BROWSER PROCESSES")
    logger.info("="*80)

    browsers = {
        "Chrome": "chrome",
        "Edge": "msedge",
        "Firefox": "firefox",
        "Neo": "neo"
    }

    running_browsers = []

    for name, process_name in browsers.items():
        command = f"Get-Process -Name '{process_name}' -ErrorAction SilentlyContinue | Select-Object -First 1"
        output, code = run_powershell_command(command)
        if code == 0 and output.strip():
            logger.info(f"  ✅ {name} is running")
            running_browsers.append(name)
        else:
            logger.info(f"  ⚠️  {name} is not running")

    return running_browsers

def print_recommendations(connectivity_results, dns_results, proxy_enabled):
    """Print recommendations based on diagnostics."""
    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATIONS")
    logger.info("="*80)

    all_connectivity_ok = all(connectivity_results.values())
    all_dns_ok = all(dns_results.values())

    if not all_connectivity_ok:
        logger.info("\n❌ Connectivity issues detected:")
        logger.info("  1. Check internet connection")
        logger.info("  2. Check firewall settings")
        logger.info("  3. Check proxy settings")
        logger.info("  4. Try resetting network adapter")

    if not all_dns_ok:
        logger.info("\n❌ DNS resolution issues detected:")
        logger.info("  1. Flush DNS: ipconfig /flushdns")
        logger.info("  2. Check DNS server settings")
        logger.info("  3. Try using different DNS server (8.8.8.8, 1.1.1.1)")

    if proxy_enabled:
        logger.info("\n⚠️  Proxy is enabled:")
        logger.info("  1. Verify proxy configuration is correct")
        logger.info("  2. Check if Neo browser proxy settings match system settings")
        logger.info("  3. Try disabling proxy temporarily to test")

    logger.info("\n💡 For Neo browser specifically:")
    logger.info("  1. Allow Neo through Windows Firewall (Private + Public)")
    logger.info("  2. Add Neo to antivirus whitelist")
    logger.info("  3. Check Neo browser proxy settings")
    logger.info("  4. Verify Neo browser can access Google services manually")

    logger.info("\n📋 Use manual OAuth flow if Neo connectivity issues persist:")
    logger.info("   python scripts/python/authenticate_google_oauth_manual.py --test")

def main():
    """Main diagnostics function."""
    logger.info("="*80)
    logger.info("NEO BROWSER CONNECTIVITY DIAGNOSTICS")
    logger.info("="*80)

    # Run diagnostics
    connectivity_results = test_connectivity()
    dns_results = check_dns_resolution()
    firewall_rules = check_firewall_rules()
    proxy_enabled = check_proxy_settings()
    running_browsers = check_browser_processes()

    # Print recommendations
    print_recommendations(connectivity_results, dns_results, proxy_enabled)

    logger.info("\n" + "="*80)
    logger.info("DIAGNOSTICS COMPLETE")
    logger.info("="*80)

if __name__ == "__main__":


    main()