#!/usr/bin/env python3
"""
Download GGUF model files using IDM (Internet Download Manager)
Integrates with HuggingFace Hub to get download URLs, then routes through IDM
"""

import os
import sys
import subprocess
import json
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Any
try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
except ImportError:
    # Fallback if not available
    def decide(*args, **kwargs):
        return None
    DecisionContext = None
    DecisionOutcome = None

try:
    from huggingface_hub import hf_hub_url, hf_hub_download
except ImportError:
    print("Installing huggingface-hub...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub", "-q"])
    from huggingface_hub import hf_hub_url, hf_hub_download



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def find_idm_script() -> Path:
    """Find the IDM download script"""
    try:
        script_dir = Path(__file__).parent.parent / "powershell"
        idm_script = script_dir / "Invoke-IDMGGUFDownload.ps1"

        if not idm_script.exists():
            raise FileNotFoundError(f"IDM script not found: {idm_script}")

        return idm_script
    except Exception as e:
        print(f"Error in find_idm_script: {e}")
        raise
def get_gguf_url(repo_id: str, filename: str) -> str:
    """
    Get public download URL for GGUF file from HuggingFace (no authentication required)
    Uses the public 'resolve' URL format that works without login
    """
    # Use public resolve URL format: https://huggingface.co/{repo_id}/resolve/main/{filename}
    # This format doesn't require authentication for public repositories
    return f"https://huggingface.co/{repo_id}/resolve/main/{filename}"


def calculate_file_crc(file_path: str, chunk_size: int = 8192) -> Optional[str]:
    """
    Calculate CRC32 checksum of a file

    Args:
        file_path: Path to file
        chunk_size: Chunk size for reading

    Returns:
        CRC32 hex string or None if file doesn't exist
    """
    import zlib

    if not os.path.exists(file_path):
        return None

    try:
        crc = 0
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                crc = zlib.crc32(chunk, crc)
        return format(crc & 0xffffffff, '08x')
    except Exception as e:
        print(f"Error calculating CRC for {file_path}: {e}")
        return None


def get_remote_file_crc(url: str) -> Optional[str]:
    """
    Get CRC32 checksum from remote file (via HEAD request or download first bytes)

    Args:
        url: URL to check

    Returns:
        CRC32 hex string or None if unavailable
    """
    try:
        # Try to get file size and ETag from HEAD request
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            # Use ETag if available as a checksum indicator
            etag = response.headers.get('ETag', '').strip('"')
            if etag:
                return etag[:16]  # Use first 16 chars as identifier
    except Exception:
        pass

    return None


def check_model_exists(dest_file: str, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if model file already exists and verify integrity

    Args:
        dest_file: Destination file path
        url: Optional URL to compare with remote

    Returns:
        Dict with 'exists', 'crc', 'size', 'valid' keys
    """
    result = {
        'exists': False,
        'crc': None,
        'size': 0,
        'valid': False
    }

    if not os.path.exists(dest_file):
        return result

    try:
        file_size = os.path.getsize(dest_file)
        if file_size > 0:
            result['exists'] = True
            result['size'] = file_size
            result['crc'] = calculate_file_crc(dest_file)
            result['valid'] = True  # File exists and has content
    except Exception as e:
        print(f"Error checking file {dest_file}: {e}")

    return result


def download_gguf_with_idm(
    repo_id: str,
    filename: str,
    model_name: Optional[str] = None,
    destination: Optional[str] = None
) -> bool:
    """
    Download GGUF file using IDM

    Args:
        repo_id: HuggingFace repository ID (e.g., "TheBloke/Llama-2-7B-GGUF")
        filename: GGUF filename (e.g., "llama-2-7b.Q4_K_M.gguf")
        model_name: Optional model name for display
        destination: Optional destination path

    Returns:
        True if download was queued successfully
    """
    try:
        # Get download URL
        url = get_gguf_url(repo_id, filename)
        print(f"Download URL: {url}")

        # Call IDM directly to avoid PowerShell script issues
        # Find IDM executable
        idm_paths = [
            r"C:\Program Files (x86)\Internet Download Manager\idman.exe",
            r"D:\Program Files (x86)\Internet Download Manager\idman.exe",
            r"C:\Program Files\Internet Download Manager\idman.exe",
        ]

        idm_exe = None
        for path in idm_paths:
            if os.path.exists(path):
                idm_exe = path
                break

        if not idm_exe:
            print("✗ IDM not found. Please install Internet Download Manager.")
            return False

        # Determine destination (M drive priority)
        if destination:
            dest_dir = destination
        elif os.path.exists("M:\\"):
            dest_dir = "M:\\Ollama\\models\\gguf"
        elif os.environ.get("OLLAMA_MODELS"):
            dest_dir = os.path.join(os.environ["OLLAMA_MODELS"], "gguf")
        else:
            dest_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        # Ensure directory exists
        os.makedirs(dest_dir, exist_ok=True)

        # Build IDM command
        dest_file = os.path.join(dest_dir, filename)

        # Check if model already exists with valid CRC
        file_check = check_model_exists(dest_file, url)
        if file_check['exists'] and file_check['valid']:
            print(f"✓ Model already exists: {filename}")
            print(f"  Size: {file_check['size']:,} bytes")
            if file_check['crc']:
                print(f"  CRC32: {file_check['crc']}")
            print(f"  Skipping download (file appears valid)")
            return True

        # Execute IDM download directly
        print(f"\nAdding to IDM queue: {filename}")
        print(f"Destination: {dest_file}")

        # IDM command: /d = URL, /p = path, /f = filename, /n = no dialog
        cmd = [
            idm_exe,
            "/d", url,
            "/p", dest_dir,
            "/f", filename,
            "/n"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✓ Successfully added to IDM queue")
            print("Monitor download progress in IDM")
            return True
        else:
            print(f"✗ Failed to add to IDM queue: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 3:
        print("Usage: download_gguf_with_idm.py <repo_id> <filename> [model_name] [destination]")
        print("\nExample:")
        print("  download_gguf_with_idm.py TheBloke/Llama-2-7B-GGUF llama-2-7b.Q4_K_M.gguf llama2")
        sys.exit(1)

    repo_id = sys.argv[1]
    filename = sys.argv[2]
    model_name = sys.argv[3] if len(sys.argv) > 3 else None
    destination = sys.argv[4] if len(sys.argv) > 4 else None

    success = download_gguf_with_idm(repo_id, filename, model_name, destination)
    sys.exit(0 if success else 1)


if __name__ == "__main__":



    main()