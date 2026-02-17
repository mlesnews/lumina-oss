"""
Google Drive API Access Script
Read files from Google Drive

#JARVIS #LUMINA #GOOGLE #DRIVE
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import logging
from typing import Dict, List, Optional, Any

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("GoogleDriveAccess")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GoogleDriveAccess")


class GoogleDriveAccess:
    """Access Google Drive files.

    Supports both Azure Key Vault and local storage for credentials.
    """

    def __init__(self, project_root: Path, use_azure_vault: bool = True):
        """Initialize Google Drive access.

        Args:
            project_root: Project root directory
            use_azure_vault: If True, try to get credentials from Azure Key Vault first
        """
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.token_file = self.config_dir / "google_drive_token.pickle"
        self.credentials_file = self.config_dir / "google_drive_credentials.json"
        self.use_azure_vault = use_azure_vault
        self.vault_client = None
        self.service = None

        # Try to initialize Azure Key Vault if requested
        if self.use_azure_vault:
            self._init_azure_vault()

    def _init_azure_vault(self) -> None:
        """Initialize Azure Key Vault client if available."""
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            import os
            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            self.vault_client = AzureKeyVaultClient(vault_url=vault_url)
            logger.info("✅ Azure Key Vault client initialized")
        except Exception as e:
            logger.debug(f"Azure Key Vault not available: {e}")
            self.vault_client = None

    def _get_credentials_from_vault(self, secret_name: str = "google-api-credentials") -> Optional[str]:
        """Get credentials from Azure Key Vault."""
        if not self.vault_client:
            return None

        try:
            # Try common names
            for name in [secret_name, "google-oauth2-credentials", "gmail-oauth2-credentials", 
                        "google-drive-credentials", "google-credentials"]:
                try:
                    creds_json = self.vault_client.get_secret(name)
                    logger.info(f"✅ Found credentials in Key Vault: {name}")
                    return creds_json
                except:
                    continue
            return None
        except Exception as e:
            logger.debug(f"Error getting credentials from vault: {e}")
            return None

    def initialize_api(self) -> bool:
        """Initialize Google Drive API."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import pickle

            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

            creds = None

            # Load existing token
            if self.token_file.exists():
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Try to get credentials from Azure Key Vault first
                    creds_json = None
                    if self.vault_client:
                        creds_json = self._get_credentials_from_vault()

                    if creds_json:
                        # Save credentials from vault to local file temporarily
                        import json
                        try:
                            # Validate it's JSON
                            json.loads(creds_json)
                            with open(self.credentials_file, 'w') as f:
                                f.write(creds_json)
                            logger.info(f"✅ Loaded credentials from Azure Key Vault")
                        except:
                            logger.warning("Credentials from vault are not valid JSON")
                            creds_json = None

                    # Fall back to local file if vault didn't work
                    if not creds_json and not self.credentials_file.exists():
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.info("\n📋 To set up Google Drive access:")
                        logger.info("1. Go to Google Cloud Console: https://console.cloud.google.com/")
                        logger.info("2. Create a project (or use existing)")
                        logger.info("3. Enable Google Drive API")
                        logger.info("4. Create OAuth 2.0 credentials (Desktop app)")
                        logger.info(f"5. Download credentials and save as: {self.credentials_file}")
                        logger.info("   OR store in Azure Key Vault as 'google-api-credentials'")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save credentials
                self.token_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)

            # Build Drive service
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("✅ Google Drive API initialized")
            return True

        except ImportError:
            logger.error("Google API libraries not installed")
            logger.info("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False
        except Exception as e:
            logger.error(f"Error initializing Google Drive API: {e}")
            return False

    def list_files(self, query: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """List files in Google Drive."""
        if not self.service:
            if not self.initialize_api():
                return []

        try:
            query_params = {}
            if query:
                query_params['q'] = query
            query_params['pageSize'] = max_results
            query_params['fields'] = 'files(id, name, mimeType, modifiedTime, size)'

            results = self.service.files().list(**query_params).execute()
            files = results.get('files', [])

            logger.info(f"Found {len(files)} file(s)")
            return files

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []

    def get_file_by_name(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get file by name."""
        files = self.list_files(query=f"name='{filename}'", max_results=1)
        return files[0] if files else None

    def download_file(self, file_id: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """Download file from Google Drive."""
        if not self.service:
            if not self.initialize_api():
                return None

        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'download')

            # Download file content
            request = self.service.files().get_media(fileId=file_id)

            if output_path is None:
                output_dir = self.project_root / "data" / "google_drive_downloads"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / file_name

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                from googleapiclient.http import MediaIoBaseDownload
                import io
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.info(f"Download progress: {int(status.progress() * 100)}%")

            logger.info(f"✅ Downloaded: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None

    def read_text_file(self, file_id: str) -> Optional[str]:
        """Read text file content directly."""
        if not self.service:
            if not self.initialize_api():
                return None

        try:
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()

            # Try to decode as text
            if isinstance(content, bytes):
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    return content.decode('utf-8', errors='ignore')
            return str(content)

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return None


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Access Google Drive files")
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--list", action="store_true", help="List files")
    parser.add_argument("--search", type=str, help="Search for file by name")
    parser.add_argument("--download", type=str, help="Download file by ID")
    parser.add_argument("--read", type=str, help="Read text file by ID")
    parser.add_argument("--filename", type=str, help="File name to search for")

    args = parser.parse_args()

    drive = GoogleDriveAccess(args.project_root)

    if args.list:
        print("\n📁 Listing files in Google Drive...")
        files = drive.list_files()
        for f in files:
            print(f"  - {f.get('name')} ({f.get('id')})")

    elif args.search or args.filename:
        query = args.search or args.filename
        print(f"\n🔍 Searching for: {query}")
        file = drive.get_file_by_name(query)
        if file:
            print(f"✅ Found: {file.get('name')} ({file.get('id')})")
            print(f"   Type: {file.get('mimeType')}")
            print(f"   Modified: {file.get('modifiedTime')}")
        else:
            print("❌ File not found")

    elif args.download:
        print(f"\n⬇️  Downloading file: {args.download}")
        path = drive.download_file(args.download)
        if path:
            print(f"✅ Saved to: {path}")

    elif args.read:
        print(f"\n📄 Reading file: {args.read}")
        content = drive.read_text_file(args.read)
        if content:
            print("\n" + "="*80)
            print(content[:2000])  # First 2000 chars
            if len(content) > 2000:
                print("\n... (truncated)")
            print("="*80)

    else:
        parser.print_help()


if __name__ == "__main__":


    main()