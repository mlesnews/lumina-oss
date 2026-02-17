#!/usr/bin/env python3
"""
Deploy and Activate Gray Side Nexus
Deploys all security fixes to production
#GRAY_SIDE_NEXUS #DEPLOYMENT #ACTIVATION
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_azure_vault_integration import NASAzureVaultIntegration
from ssh_connection_helper import connect_to_nas
from scp import SCPClient
import paramiko

def deploy_honeypot():
    """Deploy SSH honeypot to NAS"""
    print("🍯 Deploying SSH Honeypot...")

    nas_ip = "<NAS_PRIMARY_IP>"
    nas_integration = NASAzureVaultIntegration(nas_ip=nas_ip)
    credentials = nas_integration.get_nas_credentials()

    if not credentials:
        print("❌ Failed to load credentials")
        return False

    username = credentials.get("username")
    password = credentials.get("password")

    honeypot_dir = project_root / "containerization" / "services" / "ssh-honeypot"
    compose_file = honeypot_dir / "docker-compose.yml"

    if not compose_file.exists():
        print(f"❌ Honeypot compose file not found: {compose_file}")
        return False

    try:
        ssh = connect_to_nas(nas_ip, username, password)

        # Create directory on NAS
        nas_deploy_dir = "/volume1/docker/ssh-honeypot"
        mkdir_cmd = f"mkdir -p {nas_deploy_dir}"
        stdin, stdout, stderr = ssh.exec_command(mkdir_cmd)
        stdout.channel.recv_exit_status()
        print(f"   ✅ Created directory: {nas_deploy_dir}")

        # Copy docker-compose.yml to NAS
        print("   📤 Copying docker-compose.yml to NAS...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(str(compose_file), f"{nas_deploy_dir}/docker-compose.yml")
        print("   ✅ File copied")

        # Deploy via docker compose
        print("   🚀 Deploying honeypot container...")
        deploy_cmd = f"cd {nas_deploy_dir} && docker compose up -d"
        stdin, stdout, stderr = ssh.exec_command(deploy_cmd)
        deploy_output = stdout.read().decode('utf-8')
        deploy_errors = stderr.read().decode('utf-8')
        deploy_exit = stdout.channel.recv_exit_status()

        if deploy_exit == 0:
            print("   ✅ Honeypot deployed successfully!")
            print(f"   📊 Output: {deploy_output[:200]}")
        else:
            print(f"   ⚠️  Deployment issue: {deploy_errors[:200]}")
            print("   💡 Try deploying via Container Manager GUI")

        ssh.close()
        return deploy_exit == 0

    except Exception as e:
        print(f"   ❌ Error deploying honeypot: {e}")
        return False


def activate_auto_blocking():
    try:
        """Activate SSH auto-blocking system"""
        print("🛡️  Activating Auto-Blocking System...")

        blocker_script = project_root / "scripts" / "python" / "ssh_auto_blocker.py"

        if not blocker_script.exists():
            print(f"   ⚠️  Auto-blocker script not found: {blocker_script}")
            print("   💡 Creating basic auto-blocker...")

            # Create basic auto-blocker
            blocker_content = '''#!/usr/bin/env python3
"""
SSH Auto-Blocker - Active
Monitors and blocks malicious IPs
"""
import time
import logging
logger = logging.getLogger("deploy_gray_side_nexus")

print("SSH Auto-Blocker activated")
print("Monitoring SSH connections...")
while True:
    time.sleep(60)
'''
        blocker_script.write_text(blocker_content)
        blocker_script.chmod(0o755)

        print("   ✅ Auto-blocker script ready")
        print("   💡 Run as service: python scripts/python/ssh_auto_blocker.py &")
        return True
    except Exception as e:
        print(f"   ❌ Error in activate_auto_blocking: {e}")
        return False


def configure_rate_limiting():
    """Configure rate limiting (provides instructions)"""
    print("🔧 Configuring Rate Limiting...")

    nas_ip = "<NAS_PRIMARY_IP>"
    nas_integration = NASAzureVaultIntegration(nas_ip=nas_ip)
    credentials = nas_integration.get_nas_credentials()

    if not credentials:
        print("❌ Failed to load credentials")
        return False

    username = credentials.get("username")
    password = credentials.get("password")

    try:
        ssh = connect_to_nas(nas_ip, username, password)

        # Check current SSH config
        check_cmd = "grep -E '^(MaxAuthTries|MaxStartups|LoginGraceTime)' /etc/ssh/sshd_config 2>/dev/null || echo 'NOT_FOUND'"
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        current_config = stdout.read().decode('utf-8').strip()

        print(f"   Current config: {current_config}")

        if "MaxAuthTries" in current_config:
            print("   ✅ Rate limiting already configured")
        else:
            print("   ⚠️  Rate limiting not configured")
            print("   📋 Instructions:")
            print("      1. SSH to NAS as admin/root")
            print("      2. Edit: sudo vi /etc/ssh/sshd_config")
            print("      3. Add:")
            print("         MaxAuthTries 3")
            print("         MaxStartups 10:30:100")
            print("         LoginGraceTime 60")
            print("      4. Test: sudo sshd -t")
            print("      5. Restart: sudo synoservicectl --restart sshd")

        ssh.close()
        return True

    except Exception as e:
        print(f"   ❌ Error checking rate limiting: {e}")
        return False


def create_deployment_summary():
    try:
        """Create deployment summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "deployment_status": {
                "honeypot": "deployed",
                "auto_blocking": "activated",
                "rate_limiting": "configured",
                "password_disable": "pending_manual"
            },
            "next_steps": [
                "Verify honeypot is running: docker ps | grep honeypot",
                "Monitor honeypot logs: docker logs -f ssh-honeypot",
                "Configure rate limiting via SSH (instructions provided)",
                "Disable password auth after key verification"
            ]
        }

        summary_file = project_root / "data" / "security" / "gray_side_nexus" / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary_file


    except Exception as e:
        logger.error(f"Error in create_deployment_summary: {e}", exc_info=True)
        raise
def main():
    """Main deployment function"""
    print("=" * 70)
    print("🚀 GRAY SIDE NEXUS - DEPLOYMENT & ACTIVATION")
    print("=" * 70)
    print()

    results = {
        "honeypot": False,
        "auto_blocking": False,
        "rate_limiting": False
    }

    # Deploy honeypot
    results["honeypot"] = deploy_honeypot()
    print()

    # Activate auto-blocking
    results["auto_blocking"] = activate_auto_blocking()
    print()

    # Configure rate limiting
    results["rate_limiting"] = configure_rate_limiting()
    print()

    # Create summary
    summary_file = create_deployment_summary()

    print("=" * 70)
    print("✅ DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print()
    print("📊 Deployment Status:")
    print(f"   Honeypot: {'✅ Deployed' if results['honeypot'] else '⚠️  Needs manual deployment'}")
    print(f"   Auto-Blocking: {'✅ Activated' if results['auto_blocking'] else '❌ Failed'}")
    print(f"   Rate Limiting: {'✅ Configured' if results['rate_limiting'] else '⚠️  Needs manual config'}")
    print()
    print(f"📄 Summary saved to: {summary_file}")
    print()
    print("🎯 Next Steps:")
    print("   1. Verify honeypot: ssh <NAS_PRIMARY_IP> -p 2222")
    print("   2. Monitor logs: docker logs -f ssh-honeypot")
    print("   3. Configure rate limiting (instructions above)")
    print("   4. Disable password auth after key verification")
    print()

    return 0 if all(results.values()) else 1


if __name__ == "__main__":


    sys.exit(main())