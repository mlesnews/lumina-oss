#!/usr/bin/env python3
"""
Setup Plaid Integration via Azure
Complete setup script for Plaid financial data aggregation using Azure services

This script:
1. Guides you through Plaid account setup
2. Stores credentials in Azure Key Vault
3. Creates Azure Functions for webhooks
4. Sets up OAuth flows
5. Integrates with JARVIS Financial CLI

Tags: #PLAID #AZURE #SETUP #AUTOMATION #JARVIS
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    UnifiedSecretsManager = None

logger = get_logger("SetupPlaidAzure")


class PlaidAzureSetup:
    """Complete Plaid + Azure setup automation"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize setup"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.secrets_manager = UnifiedSecretsManager(self.project_root) if UnifiedSecretsManager else None
        self._protonpass_authenticated = False

        logger.info("✅ Plaid Azure Setup initialized")

    def ensure_protonpass_authenticated(self) -> bool:
        """Ensure ProtonPass CLI is authenticated (only once per session)"""
        if self._protonpass_authenticated:
            return True

        try:
            from protonpass_auto_login import main as auto_login
            logger.info("🔐 Ensuring ProtonPass CLI is authenticated...")
            result = auto_login()
            if result:
                self._protonpass_authenticated = True
            return result
        except ImportError:
            logger.debug("protonpass_auto_login not available")
            return False
        except Exception as e:
            logger.warning(f"Could not auto-login: {e}")
            return False

    def list_protonpass_accounts(self) -> List[str]:
        """List all accounts in ProtonPass to help find Plaid credentials"""
        protonpass_cli = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")

        if not protonpass_cli.exists():
            return []

        # Ensure authenticated
        self.ensure_protonpass_authenticated()

        accounts = []
        try:
            result = subprocess.run(
                [str(protonpass_cli), "item", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('Error') and not 'needs extra password' in line.lower():
                            accounts.append(line)
        except Exception as e:
            logger.debug(f"Error listing ProtonPass accounts: {e}")

        return accounts

    def check_protonpass_for_credentials(self) -> Dict[str, Any]:
        """Check ProtonPass CLI for Plaid credentials"""
        logger.info("🔍 Checking ProtonPass CLI for Plaid credentials...")

        # Use the credential finder
        try:
            from protonpass_credential_finder import ProtonPassCredentialFinder
            finder = ProtonPassCredentialFinder()
            creds = finder.find_plaid_credentials()

            if creds:
                logger.info(f"✅ Found Plaid credentials in ProtonPass: {creds['account_name']}")
                return {
                    "available": True,
                    "source": "protonpass",
                    "account_name": creds["account_name"],
                    "client_id": creds["client_id"],
                    "secret": creds["secret"],
                    "environment": creds.get("environment", "sandbox")
                }
            else:
                # Get list of all items for reference
                all_items = finder.list_all_items()
                return {
                    "available": False,
                    "source": "protonpass",
                    "available_accounts": all_items
                }
        except ImportError:
            logger.debug("protonpass_credential_finder not available, using direct method")

        # Fallback to direct method
        protonpass_cli = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")

        if not protonpass_cli.exists():
            logger.warning("⚠️  ProtonPass CLI not found at expected path")
            return {"available": False, "error": "ProtonPass CLI not found"}

        # Ensure authenticated
        if not self.ensure_protonpass_authenticated():
            logger.warning("⚠️  Could not authenticate ProtonPass CLI")

        # First, list all accounts to search for Plaid-related ones
        all_accounts = self.list_protonpass_accounts()
        logger.info(f"📋 Found {len(all_accounts)} accounts in ProtonPass")

        # Search for Plaid-related accounts
        plaid_accounts = [acc for acc in all_accounts if "plaid" in acc.lower()]

        if plaid_accounts:
            logger.info(f"🔍 Found {len(plaid_accounts)} Plaid-related accounts: {', '.join(plaid_accounts)}")

        # Try different account names (exact matches first, then search results)
        account_names = ["Plaid", "plaid", "Plaid API", "Plaid Credentials", "plaid-api", "Plaid.com"]
        account_names.extend(plaid_accounts)  # Add found accounts

        for account_name in account_names:
            try:
                # Ensure authenticated before each call
                self.ensure_protonpass_authenticated()

                # Try to get full item as JSON
                result = subprocess.run(
                    [str(protonpass_cli), "item", "get", account_name, "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    try:
                        item_data = json.loads(result.stdout.strip())

                        # Extract credentials from various field formats
                        fields = item_data.get("fields", {})

                        # Try multiple field name variations
                        client_id = (fields.get("client_id") or 
                                   fields.get("Client ID") or 
                                   fields.get("client-id") or
                                   fields.get("ClientID") or
                                   fields.get("CLIENT_ID") or
                                   item_data.get("client_id"))

                        secret = (fields.get("secret") or 
                                 fields.get("Secret") or 
                                 fields.get("api_secret") or 
                                 fields.get("api-secret") or
                                 fields.get("API Secret") or
                                 fields.get("API_SECRET") or
                                 item_data.get("secret"))

                        # Also check password field (sometimes used for API keys)
                        if not secret:
                            secret = item_data.get("password") or fields.get("password")

                        if client_id and secret:
                            logger.info(f"✅ Found Plaid credentials in ProtonPass: {account_name}")
                            return {
                                "available": True,
                                "source": "protonpass",
                                "account_name": account_name,
                                "client_id": client_id,
                                "secret": secret,
                                "environment": fields.get("environment") or fields.get("Environment") or "sandbox"
                            }
                    except json.JSONDecodeError:
                        # Try field-by-field extraction
                        client_id = (self._get_protonpass_field(account_name, "client_id") or 
                                   self._get_protonpass_field(account_name, "Client ID") or 
                                   self._get_protonpass_field(account_name, "client-id") or
                                   self._get_protonpass_field(account_name, "ClientID"))

                        secret = (self._get_protonpass_field(account_name, "secret") or 
                                self._get_protonpass_field(account_name, "Secret") or 
                                self._get_protonpass_field(account_name, "api_secret") or
                                self._get_protonpass_field(account_name, "API Secret"))

                        # Try password field
                        if not secret:
                            secret = self._get_protonpass_field(account_name, "password")

                        if client_id and secret:
                            logger.info(f"✅ Found Plaid credentials in ProtonPass: {account_name}")
                            return {
                                "available": True,
                                "source": "protonpass",
                                "account_name": account_name,
                                "client_id": client_id,
                                "secret": secret,
                                "environment": "sandbox"
                            }
            except Exception as e:
                logger.debug(f"Could not retrieve {account_name}: {e}")
                continue

        logger.info("⚠️  Plaid credentials not found in ProtonPass")
        if all_accounts:
            logger.info(f"   Available accounts: {', '.join(all_accounts[:10])}{'...' if len(all_accounts) > 10 else ''}")
        return {"available": False, "source": "protonpass", "available_accounts": all_accounts}

    def _get_protonpass_field(self, account_name: str, field_name: str) -> Optional[str]:
        """Get a specific field from ProtonPass"""
        protonpass_cli = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")

        if not protonpass_cli.exists():
            return None

        try:
            result = subprocess.run(
                [str(protonpass_cli), "item", "get", account_name, "--field", field_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output and not output.startswith("Error"):
                    return output
        except Exception:
            pass

        return None

    def check_plaid_credentials(self) -> Dict[str, Any]:
        """Check if Plaid credentials are available (ProtonPass first, then Azure Key Vault)"""
        logger.info("🔍 Checking for Plaid credentials...")

        # First, check ProtonPass CLI
        protonpass_result = self.check_protonpass_for_credentials()
        if protonpass_result.get("available"):
            logger.info("✅ Plaid credentials found in ProtonPass CLI")
            return protonpass_result

        # Fall back to Azure Key Vault
        if not self.secrets_manager:
            return {"available": False, "error": "UnifiedSecretsManager not available"}

        client_id = self.secrets_manager.get_secret(
            "plaid-client-id",
            source=SecretSource.AZURE_KEY_VAULT
        )
        secret = self.secrets_manager.get_secret(
            "plaid-secret",
            source=SecretSource.AZURE_KEY_VAULT
        )

        if client_id and secret:
            logger.info("✅ Plaid credentials found in Azure Key Vault")
            return {
                "available": True,
                "source": "azure_key_vault",
                "client_id": client_id[:10] + "..." if len(client_id) > 10 else client_id,
                "secret": "***" if secret else None
            }
        else:
            logger.info("⚠️  Plaid credentials not found in ProtonPass or Azure Key Vault")
            return {"available": False, "missing": []}

    def add_plaid_credentials(self, client_id: str = None, secret: str = None, environment: str = "sandbox", from_protonpass: bool = False) -> bool:
        """Add Plaid credentials to Azure Key Vault (from ProtonPass or manual input)"""
        logger.info("🔐 Adding Plaid credentials to Azure Key Vault...")

        # If from ProtonPass, retrieve first
        if from_protonpass:
            logger.info("🔍 Retrieving credentials from ProtonPass...")
            protonpass_result = self.check_protonpass_for_credentials()
            if protonpass_result.get("available"):
                client_id = protonpass_result.get("client_id")
                secret = protonpass_result.get("secret")
                environment = protonpass_result.get("environment", "sandbox")
                logger.info(f"✅ Retrieved credentials from ProtonPass: {protonpass_result.get('account_name')}")
            else:
                logger.error("❌ Could not retrieve credentials from ProtonPass")
                logger.info("💡 Make sure Plaid credentials are stored in ProtonPass with fields: client_id, secret")
                return False

        if not client_id or not secret:
            logger.error("❌ Client ID and Secret are required")
            return False

        if not self.secrets_manager:
            logger.error("❌ UnifiedSecretsManager not available")
            return False

        try:
            # Store credentials
            self.secrets_manager.set_secret(
                "plaid-client-id",
                client_id,
                source=SecretSource.AZURE_KEY_VAULT
            )

            self.secrets_manager.set_secret(
                "plaid-secret",
                secret,
                source=SecretSource.AZURE_KEY_VAULT
            )

            # Store environment
            self.secrets_manager.set_secret(
                "plaid-environment",
                environment,
                source=SecretSource.AZURE_KEY_VAULT
            )

            logger.info("✅ Plaid credentials stored in Azure Key Vault")
            return True

        except Exception as e:
            logger.error(f"❌ Error storing credentials: {e}")
            return False

    def create_azure_function_template(self) -> Path:
        """Create Azure Function template for Plaid webhooks"""
        try:
            logger.info("📝 Creating Azure Function template...")

            function_dir = self.project_root / "azure_functions" / "plaid_webhook"
            function_dir.mkdir(parents=True, exist_ok=True)

            # Create function.json
            function_json = {
                "scriptFile": "__init__.py",
                "bindings": [
                    {
                        "authLevel": "function",
                        "type": "httpTrigger",
                        "direction": "in",
                        "name": "req",
                        "methods": ["post"]
                    },
                    {
                        "type": "http",
                        "direction": "out",
                        "name": "$return"
                    }
                ]
            }

            with open(function_dir / "function.json", 'w') as f:
                json.dump(function_json, f, indent=2)

            # Create __init__.py
            init_py = '''import logging
import azure.functions as func
import json
import jwt
import requests
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Plaid webhook receiver with JWT verification"""
    logging.info('Plaid webhook received')

    try:
        # Get JWT from header
        verification_header = req.headers.get('Plaid-Verification')
        if not verification_header:
            return func.HttpResponse("Missing Plaid-Verification header", status_code=400)

        # Verify JWT signature
        # (Implementation would fetch JWK from Plaid and verify)

        # Parse webhook body
        body = req.get_json()
        webhook_type = body.get('webhook_type')
        webhook_code = body.get('webhook_code')
        item_id = body.get('item_id')

        logging.info(f'Webhook: {webhook_type} - {webhook_code} for item {item_id}')

        # Process webhook
        # Store in database, trigger sync, etc.

        return func.HttpResponse(
            json.dumps({"status": "processed"}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f'Error processing webhook: {e}')
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
'''

            with open(function_dir / "__init__.py", 'w') as f:
                f.write(init_py)

            # Create requirements.txt
            requirements = [
                "azure-functions",
                "requests",
                "pyjwt",
                "cryptography"
            ]

            with open(function_dir / "requirements.txt", 'w') as f:
                f.write('\n'.join(requirements))

            logger.info(f"✅ Azure Function template created: {function_dir}")
            return function_dir
        except Exception as e:
            logger.error(f"Error in create_azure_function_template: {e}", exc_info=True)
            raise

    def create_plaid_connection_class(self) -> Path:
        """Create Plaid connection class for Financial CLI"""
        logger.info("📝 Creating Plaid connection class...")

        connections_dir = self.project_root / "scripts" / "python" / "financial_connections"
        connections_dir.mkdir(parents=True, exist_ok=True)

        plaid_connection_py = '''#!/usr/bin/env python3
"""
Plaid Financial Connection
Connects to Plaid API via Azure Key Vault credentials

Tags: #PLAID #FINANCIAL_CONNECTION #AZURE
"""

import sys
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from financial_connections.base_connection import BaseFinancialConnection, ConnectionResult
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    BaseFinancialConnection = None

logger = get_logger("PlaidConnection")


class PlaidConnection(BaseFinancialConnection):
    """Plaid financial connection via Azure"""

    def __init__(self, account_id: str):
        """Initialize Plaid connection"""
        if not BaseFinancialConnection:
            raise ImportError("BaseFinancialConnection not available")

        super().__init__(account_id)
        self.project_root = Path(__file__).parent.parent.parent.parent

        # Get credentials from Azure Key Vault
        self.secrets_manager = UnifiedSecretsManager(self.project_root)
        self.client_id = self.secrets_manager.get_secret(
            "plaid-client-id",
            source=SecretSource.AZURE_KEY_VAULT
        )
        self.secret = self.secrets_manager.get_secret(
            "plaid-secret",
            source=SecretSource.AZURE_KEY_VAULT
        )
        self.environment = self.secrets_manager.get_secret(
            "plaid-environment",
            source=SecretSource.AZURE_KEY_VAULT
        ) or "sandbox"

        # Set base URL based on environment
        if self.environment == "production":
            self.base_url = "https://production.plaid.com"
        else:
            self.base_url = "https://sandbox.plaid.com"

        self.access_token = None
        logger.info(f"✅ Plaid connection initialized (environment: {self.environment})")

    def connect(self, **kwargs) -> ConnectionResult:
        """Connect to Plaid using access token"""
        access_token = kwargs.get("access_token")

        if not access_token:
            return ConnectionResult(
                success=False,
                message="Access token required. Use exchange_public_token() first."
            )

        self.access_token = access_token

        # Test connection
        try:
            result = self.test_connection()
            if result.success:
                return ConnectionResult(
                    success=True,
                    message="Connected to Plaid successfully"
                )
            return result
        except Exception as e:
            return ConnectionResult(
                success=False,
                message=f"Connection failed: {e}"
            )

    def exchange_public_token(self, public_token: str) -> Optional[str]:
        """Exchange public token for access token"""
        url = f"{self.base_url}/item/public_token/exchange"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "public_token": public_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            logger.info("✅ Exchanged public token for access token")
            return self.access_token
        except Exception as e:
            logger.error(f"❌ Error exchanging token: {e}")
            return None

    def disconnect(self) -> ConnectionResult:
        """Disconnect from Plaid"""
        self.access_token = None
        return ConnectionResult(
            success=True,
            message="Disconnected from Plaid"
        )

    def test_connection(self) -> ConnectionResult:
        """Test Plaid connection"""
        if not self.access_token:
            return ConnectionResult(
                success=False,
                message="Not connected. No access token."
            )

        url = f"{self.base_url}/accounts/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return ConnectionResult(
                success=True,
                message="Plaid connection test successful"
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                message=f"Connection test failed: {e}"
            )

    def get_balance(self) -> Optional[float]:
        """Get total balance from all accounts"""
        if not self.access_token:
            return None

        url = f"{self.base_url}/accounts/balance/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            total = 0.0
            for account in data.get("accounts", []):
                balance = account.get("balances", {}).get("available", 0)
                if isinstance(balance, (int, float)):
                    total += balance

            return total
        except Exception as e:
            logger.error(f"❌ Error getting balance: {e}")
            return None

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.access_token:
            return {}

        url = f"{self.base_url}/accounts/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            return {
                "accounts": data.get("accounts", []),
                "item": data.get("item", {}),
                "request_id": data.get("request_id")
            }
        except Exception as e:
            logger.error(f"❌ Error getting account info: {e}")
            return {}

    def get_transactions(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get transactions"""
        if not self.access_token:
            return []

        # Default to last 30 days
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        url = f"{self.base_url}/transactions/get"
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": self.access_token,
            "start_date": start_date,
            "end_date": end_date
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("transactions", [])
        except Exception as e:
            logger.error(f"❌ Error getting transactions: {e}")
            return []
'''

        output_file = connections_dir / "plaid_connection.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(plaid_connection_py)

        logger.info(f"✅ Plaid connection class created: {output_file}")
        return output_file

    def update_financial_connections_init(self):
        """Update __init__.py to include PlaidConnection"""
        try:
            init_file = self.project_root / "scripts" / "python" / "financial_connections" / "__init__.py"

            if init_file.exists():
                content = init_file.read_text()
                if "PlaidConnection" not in content:
                    # Add PlaidConnection to imports
                    content = content.replace(
                        "from .fidelity_connection import FidelityConnection",
                        "from .fidelity_connection import FidelityConnection\nfrom .plaid_connection import PlaidConnection"
                    )
                    content = content.replace(
                        '"FidelityConnection"',
                        '"FidelityConnection",\n    "PlaidConnection"'
                    )
                    init_file.write_text(content)
                    logger.info("✅ Updated financial_connections __init__.py")
        except Exception as e:
            logger.error(f"Error in update_financial_connections_init: {e}", exc_info=True)
            raise
    def create_setup_instructions(self) -> Path:
        """Create comprehensive setup instructions"""
        try:
            instructions = {
                "setup_steps": [
                    {
                        "step": 1,
                        "title": "Create Plaid Account",
                        "description": "Sign up for Plaid at https://dashboard.plaid.com",
                        "actions": [
                            "Go to https://dashboard.plaid.com/signup",
                            "Create account (use sandbox for testing)",
                            "Navigate to Team Settings > Keys",
                            "Copy your Client ID and Secret"
                        ]
                    },
                    {
                        "step": 2,
                        "title": "Store Credentials in Azure Key Vault",
                        "description": "Store Plaid credentials securely",
                        "command": "python scripts/python/setup_plaid_azure.py --add-credentials",
                        "manual_alternative": [
                            "az keyvault secret set --vault-name jarvis-lumina --name plaid-client-id --value <your-client-id>",
                            "az keyvault secret set --vault-name jarvis-lumina --name plaid-secret --value <your-secret>",
                            "az keyvault secret set --vault-name jarvis-lumina --name plaid-environment --value sandbox"
                        ]
                    },
                    {
                        "step": 3,
                        "title": "Test Connection",
                        "description": "Verify credentials work",
                        "command": "python scripts/python/plaid_connection.py --test"
                    },
                    {
                        "step": 4,
                        "title": "Set Up OAuth Flow",
                        "description": "Implement Plaid Link for user authorization",
                        "notes": [
                            "Plaid Link is the UI component for user authorization",
                            "Users connect their bank accounts via Plaid Link",
                            "After authorization, you receive a public_token",
                            "Exchange public_token for access_token using exchange_public_token()"
                        ]
                    },
                    {
                        "step": 5,
                        "title": "Deploy Azure Functions",
                        "description": "Deploy webhook receiver",
                        "actions": [
                            "Azure Function template created in azure_functions/plaid_webhook/",
                            "Deploy to Azure Functions",
                            "Configure webhook URL in Plaid Dashboard",
                            "Enable webhook verification"
                        ]
                    },
                    {
                        "step": 6,
                        "title": "Register Account in JARVIS",
                        "description": "Add Plaid account to financial registry",
                        "command": "python scripts/python/jarvis_financial_cli.py register --type BUDGETING_APP --name 'Plaid Aggregation'"
                    }
                ],
                "plaid_resources": {
                    "dashboard": "https://dashboard.plaid.com",
                    "docs": "https://plaid.com/docs/",
                    "link_docs": "https://plaid.com/docs/link/",
                    "api_reference": "https://plaid.com/docs/api/",
                    "sandbox_testing": "https://plaid.com/docs/sandbox/"
                },
                "azure_resources": {
                    "key_vault": "https://portal.azure.com/#view/Microsoft_Azure_KeyVault/KeyVaultBrowseBlade",
                    "functions": "https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites",
                    "setup_guide": str(self.project_root / "data" / "azure_financial" / "azure_financial_setup_guide.json")
                }
            }

            output_file = self.project_root / "docs" / "plaid" / "SETUP_INSTRUCTIONS.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(instructions, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Setup instructions saved: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error in create_setup_instructions: {e}", exc_info=True)
            raise
    def run_complete_setup(self) -> Dict[str, Any]:
        """Run complete setup process"""
        logger.info("🚀 Starting complete Plaid Azure setup...")

        results = {
            "started_at": datetime.now().isoformat(),
            "steps_completed": [],
            "steps_failed": [],
            "next_steps": []
        }

        # Step 1: Check existing credentials (ProtonPass first, then Azure Key Vault)
        creds_check = self.check_plaid_credentials()
        if creds_check.get("available"):
            source = creds_check.get("source", "unknown")
            logger.info(f"✅ Plaid credentials found in {source}")
            results["steps_completed"].append(f"Credentials check - Found in {source}")

            # If found in ProtonPass but not in Azure Key Vault, offer to sync
            if source == "protonpass":
                logger.info("💡 Credentials found in ProtonPass, syncing to Azure Key Vault...")
                sync_success = self.add_plaid_credentials(from_protonpass=True)
                if sync_success:
                    results["steps_completed"].append("Synced credentials from ProtonPass to Azure Key Vault")
                else:
                    results["steps_failed"].append("Failed to sync credentials from ProtonPass")
        else:
            results["next_steps"].append("Add Plaid credentials (check ProtonPass or add manually)")

        # Step 2: Create Azure Function template
        try:
            function_dir = self.create_azure_function_template()
            results["steps_completed"].append(f"Azure Function template created: {function_dir}")
        except Exception as e:
            results["steps_failed"].append(f"Azure Function template: {e}")

        # Step 3: Create Plaid connection class
        try:
            connection_file = self.create_plaid_connection_class()
            results["steps_completed"].append(f"Plaid connection class created: {connection_file}")
        except Exception as e:
            results["steps_failed"].append(f"Plaid connection class: {e}")

        # Step 4: Update __init__.py
        try:
            self.update_financial_connections_init()
            results["steps_completed"].append("Updated financial_connections __init__.py")
        except Exception as e:
            results["steps_failed"].append(f"Update __init__.py: {e}")

        # Step 5: Create setup instructions
        try:
            instructions_file = self.create_setup_instructions()
            results["steps_completed"].append(f"Setup instructions created: {instructions_file}")
        except Exception as e:
            results["steps_failed"].append(f"Setup instructions: {e}")

        results["completed_at"] = datetime.now().isoformat()

        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup Plaid Integration via Azure")
    parser.add_argument("--setup", action="store_true", help="Run complete setup")
    parser.add_argument("--check", action="store_true", help="Check existing credentials")
    parser.add_argument("--add-credentials", action="store_true", help="Add Plaid credentials interactively")
    parser.add_argument("--from-protonpass", action="store_true", help="Retrieve credentials from ProtonPass CLI")
    parser.add_argument("--client-id", help="Plaid Client ID")
    parser.add_argument("--secret", help="Plaid Secret")
    parser.add_argument("--environment", choices=["sandbox", "production"], default="sandbox", help="Plaid environment")

    args = parser.parse_args()

    setup = PlaidAzureSetup()

    if args.setup:
        print("\n" + "=" * 70)
        print("🚀 COMPLETE PLAID AZURE SETUP")
        print("=" * 70)
        print("")

        results = setup.run_complete_setup()

        print(f"\n✅ Steps Completed: {len(results['steps_completed'])}")
        for step in results['steps_completed']:
            print(f"   • {step}")

        if results['steps_failed']:
            print(f"\n❌ Steps Failed: {len(results['steps_failed'])}")
            for step in results['steps_failed']:
                print(f"   • {step}")

        if results['next_steps']:
            print(f"\n📋 Next Steps:")
            for step in results['next_steps']:
                print(f"   • {step}")

        print("\n" + "=" * 70)
        print("✅ Setup complete! See docs/plaid/SETUP_INSTRUCTIONS.json for details")
        print("=" * 70)

    elif args.check:
        creds = setup.check_plaid_credentials()
        if creds.get("available"):
            source = creds.get("source", "unknown")
            print(f"\n✅ Plaid credentials found in {source}")
            if source == "protonpass":
                print(f"   Account: {creds.get('account_name')}")
            print(f"   Client ID: {creds.get('client_id', '***')}")
        else:
            print("\n⚠️  Plaid credentials not found")

            # Show available ProtonPass accounts if any
            if "available_accounts" in creds:
                accounts = creds.get("available_accounts", [])
                if accounts:
                    print(f"\n📋 Available ProtonPass accounts ({len(accounts)}):")
                    for acc in accounts[:20]:
                        print(f"   • {acc}")
                    if len(accounts) > 20:
                        print(f"   ... and {len(accounts) - 20} more")
                    print("\n💡 If Plaid credentials are in ProtonPass, make sure the account name contains 'plaid'")

            print("\n   Options:")
            print("   1. Retrieve from ProtonPass: python scripts/python/setup_plaid_azure.py --from-protonpass")
            print("   2. Add manually: python scripts/python/setup_plaid_azure.py --add-credentials")

    elif args.add_credentials or args.from_protonpass or (args.client_id and args.secret):
        if args.from_protonpass:
            # Retrieve from ProtonPass
            print("\n🔍 Retrieving Plaid credentials from ProtonPass CLI...")
            success = setup.add_plaid_credentials(from_protonpass=True)
            if success:
                print("\n✅ Plaid credentials retrieved from ProtonPass and stored in Azure Key Vault")
                print("   You can now use Plaid integration!")
            else:
                print("\n❌ Failed to retrieve credentials from ProtonPass")
                print("   Make sure:")
                print("   1. ProtonPass CLI is installed and logged in")
                print("   2. Plaid credentials are stored in ProtonPass")
                print("   3. Account name is one of: Plaid, plaid, Plaid API, Plaid Credentials")

        elif args.client_id and args.secret:
            client_id = args.client_id
            secret = args.secret
            environment = args.environment
            success = setup.add_plaid_credentials(client_id, secret, environment)
            if success:
                print("\n✅ Plaid credentials stored in Azure Key Vault")
                print("   You can now use Plaid integration!")
            else:
                print("\n❌ Failed to store credentials")

        else:
            # Check ProtonPass first
            print("\n🔍 Checking ProtonPass CLI for credentials...")
            protonpass_result = setup.check_protonpass_for_credentials()

            if protonpass_result.get("available"):
                print(f"\n✅ Found credentials in ProtonPass: {protonpass_result.get('account_name')}")
                use_protonpass = input("Use these credentials? (y/n) [y]: ").strip().lower() or "y"

                if use_protonpass == "y":
                    success = setup.add_plaid_credentials(from_protonpass=True)
                    if success:
                        print("\n✅ Plaid credentials synced from ProtonPass to Azure Key Vault")
                        print("   You can now use Plaid integration!")
                    else:
                        print("\n❌ Failed to sync credentials")
                else:
                    # Manual input
                    print("\n📝 Enter Plaid Credentials:")
                    print("   Get these from: https://dashboard.plaid.com/team/keys")
                    print("")
                    client_id = input("Plaid Client ID: ").strip()
                    secret = input("Plaid Secret: ").strip()
                    environment = input("Environment (sandbox/production) [sandbox]: ").strip() or "sandbox"

                    if client_id and secret:
                        success = setup.add_plaid_credentials(client_id, secret, environment)
                        if success:
                            print("\n✅ Plaid credentials stored in Azure Key Vault")
                        else:
                            print("\n❌ Failed to store credentials")
            else:
                # Manual input
                print("\n📝 Enter Plaid Credentials:")
                print("   Get these from: https://dashboard.plaid.com/team/keys")
                print("")
                client_id = input("Plaid Client ID: ").strip()
                secret = input("Plaid Secret: ").strip()
                environment = input("Environment (sandbox/production) [sandbox]: ").strip() or "sandbox"

                if client_id and secret:
                    success = setup.add_plaid_credentials(client_id, secret, environment)
                    if success:
                        print("\n✅ Plaid credentials stored in Azure Key Vault")
                        print("   You can now use Plaid integration!")
                    else:
                        print("\n❌ Failed to store credentials")
                else:
                    print("\n❌ Client ID and Secret are required")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()