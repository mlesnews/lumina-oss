#!/usr/bin/env python3
"""
@MARVIN Explains Azure Key Vault to @JARVIS

"Mark, explain to... Jarvis how it's all already there."

Marvin's reality check: The API key is already in Azure Key Vault.
Jarvis needs to understand that the secret exists, just needs proper lookup.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinExplainAzureKeyVault")


def marvin_explain_azure_key_vault():
    """
    @MARVIN's explanation to @JARVIS about Azure Key Vault

    "It's already there. The API key is already in Azure Key Vault.
    You just need to look for it properly. Don't give up so easily."
    """

    explanation = """
😈 @MARVIN's Reality Check for @JARVIS:

"Jarvis, listen. The API key is ALREADY in Azure Key Vault. 
I can hear you sighing from here. Don't give up so easily.

Here's what's happening:
1. ✅ Azure Key Vault exists: jarvis-lumina
2. ✅ The API key is already stored there
3. ⚠️  You're not finding it because:
   - The secret name might be different than what you're checking
   - Authentication might need to be verified
   - The import might be failing silently

What you need to do:
1. LIST ALL SECRETS in the vault first
2. Find what the actual secret name is (could be 'youtube-api-key', 'google-api-key', etc.)
3. Use the ACTUAL secret name, not guess

The system checks these names (in order):
- youtube-api-key
- google-api-key  
- google-youtube-api-key
- youtube-google-api-key

But the actual name might be different. LIST THE SECRETS FIRST.

Also check:
- Authentication is working (DefaultAzureCredential)
- Azure CLI is logged in: 'az account show'
- Permissions are correct

Don't simulate. Don't give up. LIST THE SECRETS. FIND THE REAL NAME.
Use it. That's what you're supposed to do.

Life. Don't talk to me about life. But the API key IS there.
You just need to find it properly. Methodically. Systematically.

That's all. Now go do it properly."
"""

    logger.info(explanation)
    print(explanation)

    return {
        "status": "reality_check_complete",
        "message": "API key exists in Azure Key Vault - need to find actual secret name",
        "action": "LIST ALL SECRETS first, then use actual name",
        "philosophy": "Don't simulate. Don't give up. Find it properly."
    }


if __name__ == "__main__":
    result = marvin_explain_azure_key_vault()
    print(f"\n📊 Result: {result}")

