#!/usr/bin/env python3
"""
WSL backup to NAS with homelab credentials. #automation

Maps the NAS backups share using credentials from Azure Key Vault (Triad), ProtonPass,
or NAS-DSM config (same sources used by @MANUS, Synology DSM API, and other AI flows).
Then runs the PowerShell WSL backup script so exports go to \\<NAS_PRIMARY_IP>\\backups\\WSL-backups.

Usage:
  python scripts/python/backup_wsl_to_nas.py              # Map share, run backup
  python scripts/python/backup_wsl_to_nas.py --no-map     # Skip mapping (share already accessible)
  python scripts/python/backup_wsl_to_nas.py --skip-home  # Pass -SkipHomeArchive to PowerShell

Credential order: Key Vault (nas-username, nas-password) -> ProtonPass CLI -> NAS-DSM config (nas_user).
Tags: #automation #WSL #NAS @JARVIS @LUMINA @MANUS @triad
"""

import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Config defaults (match wsl_backup_config.json)
NAS_HOST = "<NAS_PRIMARY_IP>"
NAS_BACKUPS_SHARE = f"\\\\{NAS_HOST}\\backups"
WSL_BACKUPS_SUBFOLDER = "WSL-backups"


def _is_local_backup_path(path: str) -> bool:
    """True if path is a local drive (e.g. B:\\WSL-backups); no net use needed."""
    if not path:
        return False
    p = path.replace("/", "\\").strip()
    return len(p) >= 2 and p[1] == ":" and p[0].isalpha()


def _load_config():
    """Load backup path from wsl_backup_config.json. Returns (share_for_net_use_or_none, ps1_path)."""
    cfg_path = project_root / "config" / "wsl_backup_config.json"
    ps1 = project_root / "scripts" / "powershell" / "backup_wsl_to_nas.ps1"
    if not cfg_path.exists():
        return NAS_BACKUPS_SHARE, str(ps1)
    try:
        import json

        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        unc = cfg.get("nas_backup_unc") or (NAS_BACKUPS_SHARE + "\\" + WSL_BACKUPS_SUBFOLDER)
        if _is_local_backup_path(unc):
            return None, str(ps1)  # No mapping; backup script uses local path
        # Parent share for net use: \\<NAS_PRIMARY_IP>\backups
        parts = [p for p in unc.replace("/", "\\").rstrip("\\").split("\\") if p]
        if len(parts) >= 2:
            share = "\\\\" + "\\".join(parts[:2])
        else:
            share = NAS_BACKUPS_SHARE
        return share, str(ps1)
    except Exception:
        return NAS_BACKUPS_SHARE, str(ps1)


def _get_config_nas_user():
    """NAS-DSM config username (same as used by @MANUS, sync_holocrons_to_nas_dsm, Synology API)."""
    for name in ("nas_dsm_jupyter_config.json", "lumina_nas_ssh_config.json"):
        cfg_path = project_root / "config" / name
        if not cfg_path.exists():
            continue
        try:
            import json

            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("nas_user"):
                return cfg["nas_user"]
        except Exception:
            pass
    return "mlesn"


def _get_nas_credentials():
    """Get NAS username/password: Key Vault -> ProtonPass -> NAS-DSM config username + password from vault/ProtonPass (no secrets in logs)."""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
    except ImportError:
        return None
    integration = NASAzureVaultIntegration(nas_ip=NAS_HOST)
    # 1) Key Vault (and internal ProtonPass fallback)
    creds = integration.get_nas_credentials()
    # 2) Explicit ProtonPass if vault returned nothing (same path MANUS/DSM use)
    if not creds or not creds.get("password"):
        try:
            creds = integration.get_nas_credentials_from_protonpass()
        except Exception:
            pass
    # 3) Username from NAS-DSM config when we have password but no username (same as @MANUS/DSM flows)
    if creds and creds.get("password"):
        if not creds.get("username"):
            creds = {"username": _get_config_nas_user(), "password": creds["password"]}
        return creds
    return None


def _map_nas_share_windows(unc_share: str, username: str, password: str) -> bool:
    """Map NAS share on Windows via net use. Credentials passed in memory only; not logged."""
    if sys.platform != "win32":
        return False
    # net use \\<NAS_PRIMARY_IP>\backups /user:<NAS_PRIMARY_IP>\username password /persistent:no
    user_arg = f"{NAS_HOST}\\{username}"
    try:
        r = subprocess.run(
            ["net", "use", unc_share, "/user:" + user_arg, password, "/persistent:no"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if r.returncode == 0:
            return True
        # 1219 = multiple connections to same share; treat as success
        if "1219" in (r.stderr or "") or "1219" in (r.stdout or ""):
            return True
        return False
    except Exception:
        return False


def _run_backup_script(ps1_path: str, skip_home: bool) -> int:
    """Invoke backup_wsl_to_nas.ps1 via PowerShell."""
    if not Path(ps1_path).exists():
        print(f"ERROR: Backup script not found: {ps1_path}")
        return 1
    args = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps1_path]
    if skip_home:
        args.append("-SkipHomeArchive")
    try:
        r = subprocess.run(args, cwd=str(project_root), timeout=3600)
        return r.returncode
    except subprocess.TimeoutExpired:
        print("ERROR: Backup script timed out")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to run backup script: {e}")
        return 1


def main():
    import argparse

    p = argparse.ArgumentParser(
        description="WSL backup to NAS using homelab (Azure Vault) credentials"
    )
    p.add_argument(
        "--no-map", action="store_true", help="Skip mapping NAS share (already accessible)"
    )
    p.add_argument(
        "--skip-home", action="store_true", help="Do not create home archive for default distro"
    )
    args = p.parse_args()

    unc_share, ps1_path = _load_config()

    if not args.no_map and sys.platform == "win32" and unc_share is not None:
        creds = _get_nas_credentials()
        if not creds:
            print("No NAS credentials available. Run: az login")
            try:
                from prompt_nas_login import print_nas_login_prompts

                print_nas_login_prompts()
            except ImportError:
                print("Ensure nas-username and nas-password exist in Key Vault (jarvis-lumina).")
            print("   Then re-run: python scripts/python/backup_wsl_to_nas.py")
            print(
                "   Or sync from ProtonPass first: python scripts/python/sync_nas_credentials_protonpass_to_vault.py"
            )
            return 1
        print("Mapping NAS share (credentials from Key Vault)...")
        if _map_nas_share_windows(unc_share, creds["username"], creds["password"]):
            print("NAS share mapped successfully.")
        else:
            print("WARNING: net use failed; continuing in case share is already accessible.")

    return _run_backup_script(ps1_path, args.skip_home)


if __name__ == "__main__":
    sys.exit(main())
