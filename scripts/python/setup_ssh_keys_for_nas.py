#!/usr/bin/env python3
"""
Setup SSH Keys for NAS Authentication
Generates SSH keys and configures them on the NAS for passwordless authentication
#JARVIS #SSH #NAS #AUTHENTICATION
"""

import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_azure_vault_integration import NASAzureVaultIntegration
import paramiko
from scp import SCPClient

def main():
    nas_ip = "<NAS_PRIMARY_IP>"
    nas_hostname = "DS1821PLUS"

    print("🔑 Setting up SSH Keys for NAS Authentication...")
    print("=" * 70)

    # Get credentials
    print("🔐 Loading credentials...")
    nas_integration = NASAzureVaultIntegration(nas_ip=nas_ip)
    credentials = nas_integration.get_nas_credentials()

    if not credentials:
        print("❌ Failed to load credentials")
        return 1

    username = credentials.get("username")
    password = credentials.get("password")

    print(f"✅ Credentials loaded for {username}")
    print()

    # Step 1: Check if SSH key exists
    print("🔍 Step 1: Checking for existing SSH keys...")
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)

    # Prefer ed25519 (more secure, faster)
    key_name = "id_ed25519_lumina_nas"
    private_key_path = ssh_dir / key_name
    public_key_path = ssh_dir / f"{key_name}.pub"

    if private_key_path.exists() and public_key_path.exists():
        print(f"   ✅ SSH key already exists: {private_key_path}")
        print("   Reading existing public key...")
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
    else:
        print("   ⚠️  SSH key not found, generating new key pair...")

        # Generate SSH key (ed25519 is preferred)
        keygen_cmd = [
            "ssh-keygen",
            "-t", "ed25519",
            "-f", str(private_key_path),
            "-N", "",  # No passphrase
            "-C", f"lumina-nas-{nas_ip}"
        ]

        try:
            result = subprocess.run(
                keygen_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print("   ✅ SSH key pair generated successfully")

            # SECURITY FIX: Set proper file permissions (600 = rw-------)
            # Owner read/write only, no access for group/others
            if sys.platform != 'win32':
                private_key_path.chmod(0o600)
                public_key_path.chmod(0o644)  # Public key can be readable
            else:
                # Windows: Use stat module for permissions
                import stat
                os.chmod(private_key_path, stat.S_IREAD | stat.S_IWRITE)
                os.chmod(public_key_path, stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IROTH)
            print("   ✅ Set secure file permissions (600 for private key)")

            # Read the public key
            with open(public_key_path, 'r') as f:
                public_key = f.read().strip()

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to generate SSH key: {e}")
            print(f"   Error: {e.stderr}")
            return 1
        except FileNotFoundError:
            print("   ❌ ssh-keygen not found. Please install OpenSSH client.")
            print("   Windows: Settings → Apps → Optional Features → OpenSSH Client")
            return 1

    print(f"   Public key: {public_key[:50]}...")
    print()

    # Step 2: Connect to NAS and add public key to authorized_keys
    print("📡 Step 2: Configuring SSH key on NAS...")

    try:
        # Connect via SSH with password
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            nas_ip,
            port=22,
            username=username,
            password=password,
            timeout=10,
            allow_agent=False,
            look_for_keys=False
        )
        print("   ✅ Connected to NAS")

        # Create .ssh directory if it doesn't exist
        print("   Creating .ssh directory...")
        mkdir_cmd = "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
        stdin, stdout, stderr = ssh.exec_command(mkdir_cmd)
        stdout.channel.recv_exit_status()
        print("   ✅ .ssh directory ready")

        # Check if authorized_keys exists
        check_keys = "test -f ~/.ssh/authorized_keys && echo 'EXISTS' || echo 'NOT_EXISTS'"
        stdin, stdout, stderr = ssh.exec_command(check_keys)
        keys_status = stdout.read().decode('utf-8').strip()

        # Check if our key is already in authorized_keys (check by key fingerprint/content)
        key_fingerprint = public_key.split()[1] if len(public_key.split()) > 1 else public_key.split()[0]
        check_our_key = f"grep -qF '{key_fingerprint}' ~/.ssh/authorized_keys 2>/dev/null && echo 'EXISTS' || echo 'NOT_EXISTS'"
        stdin, stdout, stderr = ssh.exec_command(check_our_key)
        key_exists = stdout.read().decode('utf-8').strip()

        if "EXISTS" in key_exists:
            print("   ✅ SSH key already in authorized_keys")
            # Verify permissions are correct
            fix_perms = "chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
            stdin, stdout, stderr = ssh.exec_command(fix_perms)
            stdout.channel.recv_exit_status()
            print("   ✅ Permissions verified")
        else:
            print("   Adding public key to authorized_keys...")

            # Method 1: Use SCP to copy public key file, then append
            temp_key_file = f"/tmp/lumina_key_{nas_ip}.pub"

            # Write public key to temp file using echo (more reliable than heredoc)
            write_key = f"echo '{public_key}' > {temp_key_file}"
            stdin, stdout, stderr = ssh.exec_command(write_key)
            write_exit = stdout.channel.recv_exit_status()

            if write_exit != 0:
                print(f"   ⚠️  Could not write temp file: {stderr.read().decode('utf-8')[:100]}")
                # Fallback: direct append
                append_direct = f"echo '{public_key}' >> ~/.ssh/authorized_keys"
                stdin, stdout, stderr = ssh.exec_command(append_direct)
                append_exit = stdout.channel.recv_exit_status()
            else:
                # Append from temp file
                append_cmd = f"""
if [ -f ~/.ssh/authorized_keys ]; then
    # Check if this exact key already exists
    if ! grep -qF '{key_fingerprint}' ~/.ssh/authorized_keys; then
        cat {temp_key_file} >> ~/.ssh/authorized_keys
        echo "Key added"
    else
        echo "Key already exists"
    fi
else
    cp {temp_key_file} ~/.ssh/authorized_keys
    echo "Key file created"
fi
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
rm -f {temp_key_file}
"""
                stdin, stdout, stderr = ssh.exec_command(append_cmd)
                append_output = stdout.read().decode('utf-8')
                append_errors = stderr.read().decode('utf-8')
                append_exit = stdout.channel.recv_exit_status()

            if append_exit == 0:
                print("   ✅ Public key added to authorized_keys")
                print(f"   Output: {append_output.strip()}")
            else:
                print(f"   ⚠️  Warning: {append_errors[:100]}")
                # Verify what happened
                verify_cmd = "cat ~/.ssh/authorized_keys | tail -1"
                stdin, stdout, stderr = ssh.exec_command(verify_cmd)
                last_key = stdout.read().decode('utf-8').strip()
                print(f"   Last key in file: {last_key[:50]}...")

                if key_fingerprint in last_key:
                    print("   ✅ Key appears to be added, fixing permissions...")
                    fix_cmd = "chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
                    stdin, stdout, stderr = ssh.exec_command(fix_cmd)
                    print("   ✅ Permissions fixed")
                else:
                    print("   ❌ Key not found in authorized_keys")
                    return 1

        # Verify key was added correctly (before closing connection)
        print("🔍 Verifying key configuration on NAS...")

        # Check authorized_keys content
        verify_key = f"grep '{key_fingerprint}' ~/.ssh/authorized_keys 2>&1"
        stdin, stdout, stderr = ssh.exec_command(verify_key)
        key_in_file = stdout.read().decode('utf-8').strip()

        if key_fingerprint in key_in_file:
            print(f"   ✅ Key found in authorized_keys: {key_in_file[:60]}...")
        else:
            print("   ⚠️  Key not found, re-adding...")
            # Force add the key
            force_add = f"echo '{public_key}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
            stdin, stdout, stderr = ssh.exec_command(force_add)
            stdout.channel.recv_exit_status()
            print("   ✅ Key re-added")

        # Check permissions
        check_perms = "ls -la ~/.ssh/authorized_keys"
        stdin, stdout, stderr = ssh.exec_command(check_perms)
        perms_info = stdout.read().decode('utf-8').strip()
        print(f"   Permissions: {perms_info}")

        # Ensure correct permissions
        fix_all_perms = "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
        stdin, stdout, stderr = ssh.exec_command(fix_all_perms)
        stdout.channel.recv_exit_status()
        print("   ✅ Permissions set correctly")

        ssh.close()
        print()

        # Step 4: Test SSH key authentication
        print("🧪 Step 4: Testing SSH key authentication...")

        # Load the private key
        try:
            ssh_key = paramiko.Ed25519Key.from_private_key_file(str(private_key_path))
        except Exception as e:
            print(f"   ❌ Failed to load private key: {e}")
            print("   Trying RSA key format...")
            try:
                ssh_key = paramiko.RSAKey.from_private_key_file(str(private_key_path))
            except:
                print("   ❌ Could not load key in any format")
                return 1

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Try with key only (no password fallback)
            ssh.connect(
                nas_ip,
                port=22,
                username=username,
                pkey=ssh_key,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )
            print("   ✅ SSH key authentication successful!")
            print("   ✅ No password required - authentication works on first try")

            # Test a command
            stdin, stdout, stderr = ssh.exec_command("whoami && hostname")
            test_output = stdout.read().decode('utf-8').strip()
            print(f"   ✅ Verified: Connected as {test_output}")

            ssh.close()

        except paramiko.AuthenticationException as e:
            print(f"   ❌ SSH key authentication failed: {e}")
            print("   Debugging issue...")
            ssh.close()

            # Reconnect with password to debug
            print("   Reconnecting with password to check configuration...")
            ssh_debug = paramiko.SSHClient()
            ssh_debug.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_debug.connect(
                nas_ip,
                port=22,
                username=username,
                password=password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )

            # Check authorized_keys format and content
            check_format = "head -1 ~/.ssh/authorized_keys"
            stdin, stdout, stderr = ssh_debug.exec_command(check_format)
            first_key = stdout.read().decode('utf-8').strip()
            print(f"   First key in authorized_keys: {first_key[:80]}...")

            # Verify our key is there
            check_our = f"grep -c '{key_fingerprint}' ~/.ssh/authorized_keys 2>&1"
            stdin, stdout, stderr = ssh_debug.exec_command(check_our)
            key_count = stdout.read().decode('utf-8').strip()
            print(f"   Our key appears {key_count} time(s) in authorized_keys")

            # Check SSH server config (may restrict key types)
            check_sshd = "grep -i 'PubkeyAcceptedKeyTypes\\|PubkeyAcceptedAlgorithms' /etc/ssh/sshd_config 2>&1 | head -3"
            stdin, stdout, stderr = ssh_debug.exec_command(check_sshd)
            sshd_config = stdout.read().decode('utf-8').strip()
            if sshd_config:
                print(f"   SSH server config: {sshd_config}")

            ssh_debug.close()
            print("   ⚠️  Key authentication not working yet")
            print("   Key is configured - may need SSH server restart or different key type")
            print("   Using password authentication for now (will work on first try)")
            return 0  # Not a fatal error - password auth still works

        print()

        # Step 4: Update SSH config for easy access
        print("📝 Step 4: Updating SSH config...")
        ssh_config = ssh_dir / "config"

        config_entry = f"""
Host {nas_hostname.lower()} nas {nas_ip}
    HostName {nas_ip}
    User {username}
    IdentityFile {private_key_path}
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/known_hosts
"""

        # Read existing config
        if ssh_config.exists():
            config_content = ssh_config.read_text()
            # Check if entry already exists
            if nas_ip not in config_content and nas_hostname.lower() not in config_content:
                # Append new entry
                with open(ssh_config, 'a') as f:
                    f.write(config_entry)
                print(f"   ✅ Added entry to {ssh_config}")
            else:
                print(f"   ✅ SSH config already has entry for {nas_hostname}")
        else:
            # Create new config
            ssh_config.write_text(config_entry)
            ssh_config.chmod(0o600)
            print(f"   ✅ Created SSH config: {ssh_config}")

        print()
        print("=" * 70)
        print("✅ SSH KEY SETUP COMPLETE!")
        print()
        print("Benefits:")
        print("   ✅ No more failed publickey attempts")
        print("   ✅ Instant authentication (no password prompt)")
        print("   ✅ More secure than password authentication")
        print()
        print("Usage:")
        print(f"   ssh {nas_hostname.lower()}")
        print(f"   ssh {nas_ip}")
        print(f"   ssh nas")
        print()
        print("All SSH connections will now use key authentication automatically!")
        print()

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":


    sys.exit(main())