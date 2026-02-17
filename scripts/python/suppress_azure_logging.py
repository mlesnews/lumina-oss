#!/usr/bin/env python3
"""
Suppress Verbose Azure SDK Logging
Suppresses INFO-level Azure SDK logs to reduce noise

Tags: #LOGGING #AZURE #SUPPRESS @JARVIS
"""

import logging

# Suppress verbose Azure SDK logging
AZURE_LOGGERS_TO_SUPPRESS = [
    'azure.core.pipeline.policies.http_logging_policy',
    'azure.identity._credentials.environment',
    'azure.identity._credentials.managed_identity',
    'azure.identity._credentials.azure_cli',
    'azure.core.pipeline',
    'azure.identity',
    'azure.keyvault',
    'azure.keyvault.secrets',
    'urllib3.connectionpool',
    'urllib3.util.retry',
    'requests.packages.urllib3',
    'msal'
]

def suppress_azure_logging():
    """Suppress verbose Azure SDK logging"""
    for logger_name in AZURE_LOGGERS_TO_SUPPRESS:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)  # Only show warnings and errors
        logger.propagate = False  # Don't propagate to root logger


# Auto-suppress on import
suppress_azure_logging()
