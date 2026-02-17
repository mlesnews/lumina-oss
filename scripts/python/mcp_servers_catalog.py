#!/usr/bin/env python3
"""
MCP Servers Catalog - Popular MCP Servers from Docker Hub/Marketplace
#JARVIS #MCP #DOCKER-HUB

Comprehensive catalog of MCP servers available for deployment to NAS.
All servers are lightweight and suitable for Synology Container Manager.
"""

from typing import Dict, Any, List

# Popular MCP Servers from Docker Hub/Marketplace
MCP_SERVERS_CATALOG: Dict[str, Dict[str, Any]] = {
    # Workflow & Automation
    "n8n": {
        "name": "n8n",
        "description": "n8n - Workflow Automation Platform",
        "image": "n8nio/n8n:latest",
        "port": 5678,
        "memory_limit": "2g",
        "cpu_limit": "2.0",
        "restart_policy": "unless-stopped",
        "volumes": ["n8n-data:/home/node/.n8n"],
        "env_vars": {
            "N8N_BASIC_AUTH_ACTIVE": "true",
            "N8N_BASIC_AUTH_USER": "admin",
            "N8N_HOST": "<NAS_PRIMARY_IP>",
            "N8N_PORT": "5678",
            "N8N_PROTOCOL": "http",
            "WEBHOOK_URL": "http://<NAS_PRIMARY_IP>:5678/"
        },
        "healthcheck": {
            "test": ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5678/healthz"],
            "interval": "30s",
            "timeout": "10s",
            "retries": 3,
            "start_period": "30s"
        }
    },

    # AWS MCP Servers (from awslabs)
    "aws-diagram": {
        "name": "aws-diagram-mcp-server",
        "description": "AWS Diagram MCP Server - Generate AWS architecture diagrams",
        "image": "public.ecr.aws/aws-mcp-servers/aws-diagram-mcp-server:latest",
        "port": 8087,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "volumes": ["aws-diagram-data:/app/data"],
        "env_vars": {
            "AWS_REGION": "us-east-1"
        }
    },

    "aws-documentation": {
        "name": "aws-documentation-mcp-server",
        "description": "AWS Documentation MCP Server - Access AWS documentation",
        "image": "public.ecr.aws/aws-mcp-servers/aws-documentation-mcp-server:latest",
        "port": 8088,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "volumes": ["aws-docs-cache:/app/cache"]
    },

    "aws-cdk": {
        "name": "cdk-mcp-server",
        "description": "AWS CDK MCP Server - CDK project management",
        "image": "public.ecr.aws/aws-mcp-servers/cdk-mcp-server:latest",
        "port": 8089,
        "memory_limit": "1g",
        "cpu_limit": "1.5",
        "restart_policy": "unless-stopped",
        "volumes": ["cdk-projects:/app/projects"]
    },

    "aws-terraform": {
        "name": "terraform-mcp-server",
        "description": "Terraform MCP Server - Infrastructure as Code",
        "image": "public.ecr.aws/aws-mcp-servers/terraform-mcp-server:latest",
        "port": 8090,
        "memory_limit": "1g",
        "cpu_limit": "1.5",
        "restart_policy": "unless-stopped",
        "volumes": ["terraform-workspaces:/app/workspaces"]
    },

    "aws-lambda": {
        "name": "lambda-mcp-server",
        "description": "AWS Lambda MCP Server - Lambda function management",
        "image": "public.ecr.aws/aws-mcp-servers/lambda-mcp-server:latest",
        "port": 8091,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "env_vars": {
            "AWS_REGION": "us-east-1"
        }
    },

    "aws-cost-analysis": {
        "name": "cost-analysis-mcp-server",
        "description": "AWS Cost Analysis MCP Server - Cost optimization",
        "image": "public.ecr.aws/aws-mcp-servers/cost-analysis-mcp-server:latest",
        "port": 8092,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped"
    },

    "aws-bedrock-kb": {
        "name": "bedrock-kb-retrieval-mcp-server",
        "description": "AWS Bedrock Knowledge Base MCP Server - RAG capabilities",
        "image": "public.ecr.aws/aws-mcp-servers/bedrock-kb-retrieval-mcp-server:latest",
        "port": 8093,
        "memory_limit": "1g",
        "cpu_limit": "1.5",
        "restart_policy": "unless-stopped",
        "volumes": ["bedrock-kb-data:/app/data"]
    },

    "aws-nova-canvas": {
        "name": "nova-canvas-mcp-server",
        "description": "AWS Nova Canvas MCP Server - Visual canvas for AI",
        "image": "public.ecr.aws/aws-mcp-servers/nova-canvas-mcp-server:latest",
        "port": 8094,
        "memory_limit": "1g",
        "cpu_limit": "1.5",
        "restart_policy": "unless-stopped",
        "volumes": ["nova-canvas-data:/app/data"]
    },

    # Synology-specific MCP Servers
    "synology-download": {
        "name": "synology-download-mcp",
        "description": "Synology Download Station MCP Server - Manage downloads",
        "image": "ghcr.io/akitchin/synology-download-mcp:latest",
        "port": 8095,
        "memory_limit": "256m",
        "cpu_limit": "0.5",
        "restart_policy": "unless-stopped",
        "env_vars": {
            "SYNOLOGY_HOST": "<NAS_PRIMARY_IP>",
            "SYNOLOGY_PORT": "5000"
        }
    },

    "synolink": {
        "name": "mcp-synolink",
        "description": "SynoLink MCP Server - File operations on Synology NAS",
        "image": "ghcr.io/do-boo/mcp-synolink:latest",
        "port": 8096,
        "memory_limit": "256m",
        "cpu_limit": "0.5",
        "restart_policy": "unless-stopped",
        "env_vars": {
            "SYNOLOGY_HOST": "<NAS_PRIMARY_IP>"
        }
    },

    # Database MCP Servers
    "postgres": {
        "name": "postgres-mcp-server",
        "description": "PostgreSQL MCP Server - Database operations",
        "image": "modelcontextprotocol/server-postgres:latest",
        "port": 8097,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "volumes": ["postgres-mcp-data:/app/data"]
    },

    "sqlite": {
        "name": "sqlite-mcp-server",
        "description": "SQLite MCP Server - SQLite database operations",
        "image": "modelcontextprotocol/server-sqlite:latest",
        "port": 8098,
        "memory_limit": "256m",
        "cpu_limit": "0.5",
        "restart_policy": "unless-stopped",
        "volumes": ["sqlite-databases:/app/databases"]
    },

    # File System MCP Servers
    "filesystem": {
        "name": "filesystem-mcp-server",
        "description": "Filesystem MCP Server - File operations",
        "image": "modelcontextprotocol/server-filesystem:latest",
        "port": 8099,
        "memory_limit": "256m",
        "cpu_limit": "0.5",
        "restart_policy": "unless-stopped",
        "volumes": [
            "/volume1:/mnt/volume1:ro",  # Read-only access to NAS volumes
            "filesystem-mcp-data:/app/data"
        ]
    },

    # Git MCP Servers
    "git": {
        "name": "git-mcp-server",
        "description": "Git MCP Server - Git operations",
        "image": "modelcontextprotocol/server-git:latest",
        "port": 8100,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "volumes": [
            "git-repos:/app/repos",
            "/root/.ssh:/root/.ssh:ro"  # SSH keys for Git
        ]
    },

    # Web & API MCP Servers
    "brave-search": {
        "name": "brave-search-mcp-server",
        "description": "Brave Search MCP Server - Web search",
        "image": "modelcontextprotocol/server-brave-search:latest",
        "port": 8101,
        "memory_limit": "256m",
        "cpu_limit": "0.5",
        "restart_policy": "unless-stopped",
        "env_vars": {
            "BRAVE_API_KEY": ""  # Set from Azure Key Vault
        }
    },

    "puppeteer": {
        "name": "puppeteer-mcp-server",
        "description": "Puppeteer MCP Server - Web automation",
        "image": "modelcontextprotocol/server-puppeteer:latest",
        "port": 8102,
        "memory_limit": "1g",
        "cpu_limit": "1.5",
        "restart_policy": "unless-stopped",
        "volumes": ["puppeteer-data:/app/data"]
    },

    # Development Tools
    "github": {
        "name": "github-mcp-server",
        "description": "GitHub MCP Server - GitHub operations",
        "image": "modelcontextprotocol/server-github:latest",
        "port": 8103,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "env_vars": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": ""  # Set from Azure Key Vault
        }
    },

    "slack": {
        "name": "slack-mcp-server",
        "description": "Slack MCP Server - Slack integration",
        "image": "modelcontextprotocol/server-slack:latest",
        "port": 8104,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "env_vars": {
            "SLACK_BOT_TOKEN": "",  # Set from Azure Key Vault
            "SLACK_TEAM_ID": ""
        }
    },

    # Custom/Local MCP Servers
    "manus": {
        "name": "manus-mcp-server",
        "description": "MANUS MCP Server - Unified Control Interface",
        "image": None,  # Build from local Dockerfile
        "dockerfile_path": "../manus-mcp-server/Dockerfile",
        "context_path": "../manus-mcp-server",
        "port": 8085,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "volumes": [
            "manus-data:/app/data",
            "manus-logs:/app/logs"
        ]
    },

    "elevenlabs": {
        "name": "elevenlabs-mcp-server",
        "description": "ElevenLabs MCP Server - Text-to-Speech",
        "image": None,  # Build from local Dockerfile
        "dockerfile_path": "../elevenlabs-mcp-server/Dockerfile",
        "context_path": "../elevenlabs-mcp-server",
        "port": 8086,
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "restart_policy": "unless-stopped",
        "volumes": [
            "elevenlabs-output:/app/output",
            "elevenlabs-data:/app/data"
        ],
        "env_vars": {
            "AZURE_KEY_VAULT_URL": "https://jarvis-lumina.vault.azure.net/",
            "ELEVENLABS_MCP_BASE_PATH": "/app/output"
        }
    }
}


def get_mcp_server(key: str) -> Dict[str, Any]:
    """Get MCP server configuration by key"""
    return MCP_SERVERS_CATALOG.get(key, {})


def list_all_mcp_servers() -> List[str]:
    """List all available MCP server keys"""
    return list(MCP_SERVERS_CATALOG.keys())


def get_mcp_servers_by_category() -> Dict[str, List[str]]:
    """Get MCP servers grouped by category"""
    categories = {
        "workflow": ["n8n"],
        "aws": [
            "aws-diagram", "aws-documentation", "aws-cdk", "aws-terraform",
            "aws-lambda", "aws-cost-analysis", "aws-bedrock-kb", "aws-nova-canvas"
        ],
        "synology": ["synology-download", "synolink"],
        "database": ["postgres", "sqlite"],
        "filesystem": ["filesystem"],
        "git": ["git"],
        "web": ["brave-search", "puppeteer"],
        "development": ["github", "slack"],
        "custom": ["manus", "elevenlabs"]
    }
    return categories


def get_recommended_servers() -> List[str]:
    """Get recommended MCP servers for NAS deployment"""
    return [
        "n8n",
        "manus",
        "elevenlabs",
        "filesystem",
        "git",
        "synology-download",
        "synolink"
    ]
