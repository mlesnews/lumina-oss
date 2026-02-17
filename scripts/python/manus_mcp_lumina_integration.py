#!/usr/bin/env python3
"""
MANUS MCP Lumina Integration

Integrates MANUS and ElevenLabs MCP servers with the Lumina ecosystem.
Handles Azure Key Vault integration for all secrets.

@MANUS @MCP @LUMINA @AZURE_KEY_VAULT
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from azure_service_bus_integration import AzureKeyVaultClient

    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("Warning: Azure Key Vault client not available", file=sys.stderr)


VAULT_URL = "https://jarvis-lumina.vault.azure.net/"


def get_secret_from_vault(secret_name: str, fallback: Optional[str] = None) -> str:
    """Get secret from Azure Key Vault"""
    if not KEY_VAULT_AVAILABLE:
        if fallback:
            return fallback
        raise ValueError(
            f"Azure Key Vault not available and no fallback provided for: {secret_name}"
        )

    try:
        key_vault = AzureKeyVaultClient(VAULT_URL)
        secret = key_vault.get_secret(secret_name)
        print(f"✅ Retrieved secret from Key Vault: {secret_name}", file=sys.stderr)
        return secret
    except Exception as e:
        print(f"⚠️  Error retrieving secret {secret_name} from Key Vault: {e}", file=sys.stderr)
        if fallback:
            print("   Using fallback value", file=sys.stderr)
            return fallback
        raise


def setup_elevenlabs_secret() -> Dict[str, str]:
    """Setup ElevenLabs secrets from Azure Key Vault"""
    secrets = {}

    try:
        # Required: API key
        api_key = get_secret_from_vault("elevenlabs-api-key")
        secrets["ELEVENLABS_API_KEY"] = api_key
        # Optional: API residency
        try:
            residency = get_secret_from_vault("elevenlabs-residency", fallback="us")
            secrets["ELEVENLABS_API_RESIDENCY"] = residency
        except:
            secrets["ELEVENLABS_API_RESIDENCY"] = "us"

        print("✅ ElevenLabs secrets configured from Azure Key Vault", file=sys.stderr)
        return secrets

    except Exception as e:
        print(f"❌ Failed to setup ElevenLabs secrets: {e}", file=sys.stderr)
        print("   Please ensure secrets are stored in Azure Key Vault:", file=sys.stderr)
        print("     - elevenlabs-api-key (required)", file=sys.stderr)
        print("     - elevenlabs-residency (optional, default: us)", file=sys.stderr)
        raise


def generate_docker_env_file(output_path: Path) -> None:
    """Generate .env file for Docker Compose with secrets from Azure Key Vault"""
    env_vars = {}

    try:
        # Get ElevenLabs secrets
        elevenlabs_secrets = setup_elevenlabs_secret()
        env_vars.update(elevenlabs_secrets)

        # Set defaults for other environment variables
        env_vars.setdefault("ELEVENLABS_MCP_OUTPUT_MODE", "files")
        env_vars.setdefault("ELEVENLABS_MCP_BASE_PATH", "/app/output")

        # Write .env file
        env_content = "\n".join([f"{key}={value}" for key, value in env_vars.items()])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write("# MCP Servers Environment Variables\n")
            f.write("# Generated from Azure Key Vault\n")
            f.write("# DO NOT COMMIT THIS FILE - Contains sensitive secrets\n\n")
            f.write(env_content)

        print(f"✅ Generated .env file: {output_path}", file=sys.stderr)

    except Exception as e:
        print(f"❌ Failed to generate .env file: {e}", file=sys.stderr)
        raise


def verify_docker_setup() -> bool:
    """Verify Docker and Docker Compose are available"""
    try:
        # Check Docker
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ Docker is not available", file=sys.stderr)
            return False
        print(f"✅ Docker found: {result.stdout.strip()}", file=sys.stderr)

        # Check Docker Compose
        result = subprocess.run(
            ["docker", "compose", "version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            print("❌ Docker Compose is not available", file=sys.stderr)
            return False
        print(f"✅ Docker Compose found: {result.stdout.strip()}", file=sys.stderr)

        return True

    except FileNotFoundError:
        print("❌ Docker or Docker Compose not found in PATH", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("❌ Docker/Docker Compose check timed out", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}", file=sys.stderr)
        return False


def start_mcp_servers(docker_compose_path: Path) -> None:
    """Start MCP servers using Docker Compose"""
    if not verify_docker_setup():
        raise RuntimeError("Docker setup verification failed")

    # Change to docker-compose directory
    original_dir = os.getcwd()
    os.chdir(docker_compose_path)

    try:
        print("🚀 Starting MCP servers...", file=sys.stderr)

        # Build and start services
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "--build"], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed to start MCP servers: {result.stderr}", file=sys.stderr)
            raise RuntimeError(f"Docker Compose failed: {result.stderr}")

        print("✅ MCP servers started successfully", file=sys.stderr)
        print(result.stdout, file=sys.stderr)

    finally:
        os.chdir(original_dir)


def check_service_status(docker_compose_path: Path) -> None:
    """Check status of MCP servers"""
    original_dir = os.getcwd()
    os.chdir(docker_compose_path)

    try:
        result = subprocess.run(["docker", "compose", "ps"], capture_output=True, text=True)

        print("\n📊 MCP Servers Status:", file=sys.stderr)
        print(result.stdout, file=sys.stderr)

    finally:
        os.chdir(original_dir)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Lumina MCP Integration")
    parser.add_argument(
        "--generate-env", action="store_true", help="Generate .env file from Azure Key Vault"
    )
    parser.add_argument(
        "--start", action="store_true", help="Start MCP servers using Docker Compose"
    )
    parser.add_argument("--status", action="store_true", help="Check status of MCP servers")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=project_root / "containerization" / "services" / "mcp-servers" / ".env",
        help="Path to .env file (default: containerization/services/mcp-servers/.env)",
    )
    parser.add_argument(
        "--docker-compose-path",
        type=Path,
        default=project_root / "containerization" / "services" / "mcp-servers",
        help="Path to docker-compose.yml directory",
    )

    args = parser.parse_args()

    try:
        if args.generate_env:
            generate_docker_env_file(args.env_file)

        if args.start:
            # Ensure .env file exists
            if not args.env_file.exists():
                print("⚠️  .env file not found, generating from Azure Key Vault...", file=sys.stderr)
                generate_docker_env_file(args.env_file)

            start_mcp_servers(args.docker_compose_path)

        if args.status:
            check_service_status(args.docker_compose_path)

        if not any([args.generate_env, args.start, args.status]):
            parser.print_help()

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
