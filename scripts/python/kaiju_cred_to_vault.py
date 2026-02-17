#!/usr/bin/env python3
"""
Extract KAIJU Windows password from ProtonPass → Azure Key Vault.
COMPUSEC compliant: password never touches disk or display.
One-time use script — delete after successful run.
"""
import subprocess, json, sys, os

PASS_CLI = r"C:\Users\mlesn\AppData\Local\Microsoft\WinGet\Packages\Proton.ProtonPass.CLI_Microsoft.Winget.Source_8wekyb3d8bbwe\pass-cli.exe"
VAULT_NAME = "jarvis-lumina"
SECRET_NAME = "kaiju-windows-password"

def main():
    # Step 1: Find the Microsoft Account item
    r = subprocess.run(
        ['cmd.exe', '/c', PASS_CLI, 'item', 'list', 'Personal',
         '--filter-type', 'login', '--output', 'json'],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode != 0:
        print(f"ERROR: item list failed: {r.stderr[:100]}")
        return 1

    data = json.loads(r.stdout)
    items = data.get('items', [])

    # Find by title or username
    target_uuid = None
    for i in items:
        c = i.get('content', {})
        title = c.get('title', '').lower()
        inner = c.get('content', {})
        username = inner.get('username', '').lower()
        if 'microsoft account' in title or 'mlesnewski@gmail' in username:
            target_uuid = c.get('item_uuid')
            break

    if not target_uuid:
        print("ERROR: Microsoft Account item not found")
        return 1

    print(f"Found item: {target_uuid[:8]}...")

    # Step 2: Get share_id for the item
    share_id = None
    item_title = None
    for i in items:
        c = i.get('content', {})
        title = c.get('title', '').lower()
        inner = c.get('content', {})
        username = inner.get('username', '').lower()
        if 'microsoft account' in title or 'mlesnewski@gmail' in username:
            share_id = i.get('share_id')
            item_title = c.get('title')
            target_uuid = c.get('item_uuid')
            break

    print(f"  share_id: {share_id[:8] if share_id else 'none'}...")
    print(f"  title: '{item_title}'")

    # Step 3: Extract password using correct URI format or flags
    password = None

    # Method 1: --vault-name + --item-title + --field password
    view_r = subprocess.run(
        ['cmd.exe', '/c', PASS_CLI, 'item', 'view',
         '--vault-name', 'Personal', '--item-title', item_title, '--field', 'password'],
        capture_output=True, text=True, timeout=15
    )
    candidate = view_r.stdout.strip().replace('\r', '')
    if candidate and len(candidate) > 3:
        password = candidate
        print(f"Extracted via --item-title --field password [REDACTED]")

    # Method 2: pass:// URI
    if not password and share_id and target_uuid:
        uri = f"pass://{share_id}/{target_uuid}/password"
        view_r2 = subprocess.run(
            ['cmd.exe', '/c', PASS_CLI, 'item', 'view', uri],
            capture_output=True, text=True, timeout=15
        )
        candidate = view_r2.stdout.strip().replace('\r', '')
        if candidate and len(candidate) > 3:
            password = candidate
            print(f"Extracted via pass:// URI [REDACTED]")

    # Method 3: JSON output + parse
    if not password:
        view_r3 = subprocess.run(
            ['cmd.exe', '/c', PASS_CLI, 'item', 'view',
             '--vault-name', 'Personal', '--item-title', item_title, '--output', 'json'],
            capture_output=True, text=True, timeout=15
        )
        if view_r3.returncode == 0 and view_r3.stdout.strip():
            try:
                jdata = json.loads(view_r3.stdout)
                # Try multiple paths for password
                content = jdata.get('content', {})
                inner = content.get('content', {})
                pw = inner.get('password', '')
                if not pw:
                    pw = content.get('password', '')
                if pw and len(pw) > 3:
                    password = pw
                    print(f"Extracted via JSON [REDACTED]")
                else:
                    # COMPUSEC: show structure keys only
                    print(f"  JSON top keys: {sorted(jdata.keys())}")
                    print(f"  content keys: {sorted(content.keys())}")
                    if inner:
                        print(f"  inner keys: {sorted(inner.keys())}")
            except Exception as e:
                print(f"  JSON parse error: {e}")

    # Method 4: Human output fallback
    if not password:
        view_r4 = subprocess.run(
            ['cmd.exe', '/c', PASS_CLI, 'item', 'view',
             '--vault-name', 'Personal', '--item-title', item_title],
            capture_output=True, text=True, timeout=15
        )
        print(f"  Human view: exit={view_r4.returncode}, len={len(view_r4.stdout)}")
        for line in view_r4.stdout.split('\n'):
            line = line.strip()
            if ':' in line:
                field_name = line.split(':')[0].strip().lower()
                value = line.split(':', 1)[1].strip()
                # COMPUSEC: field names only, redact password-related lengths
                if 'password' in field_name or 'secret' in field_name:
                    print(f"    '{field_name}': [REDACTED]")
                else:
                    print(f"    '{field_name}': len={len(value)}")
                if 'password' in field_name and value and len(value) > 3 and value != '***':
                    password = value
                    print(f"  Extracted via human parse [REDACTED]")

    if not password:
        print("ERROR: Could not extract password")
        return 1

    # Step 3: Store in Azure Key Vault
    vault_r = subprocess.run(
        ['az', 'keyvault', 'secret', 'set',
         '--vault-name', VAULT_NAME,
         '--name', SECRET_NAME,
         '--value', password],
        capture_output=True, text=True, timeout=30
    )

    # Clear password from memory
    password = None

    if vault_r.returncode == 0:
        print(f"SUCCESS: Stored as {VAULT_NAME}/{SECRET_NAME}")
        return 0
    else:
        print(f"ERROR: Vault store failed: {vault_r.stderr[:150]}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
