#!/usr/bin/env python3
"""
VA.B Configuration Generator

Generates all necessary configuration files for the complete JARVIS ecosystem:
- System configuration
- AI model settings
- Braintrust parameters
- Camera and avatar settings
- API endpoints and authentication
"""

import json
import os
from pathlib import Path
from datetime import datetime
import secrets
import logging
logger = logging.getLogger("generate_config")


def generate_system_config():
    """Generate main system configuration"""
    config = {
        "system": {
            "name": "VA.B - Virtual Assistant Build",
            "version": "1.0.0",
            "deployment_id": f"VA_B_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "environment": os.getenv("DEPLOYMENT_ENVIRONMENT", "production"),
            "log_level": os.getenv("LOG_LEVEL", "INFO")
        },
        "jarvis": {
            "enabled": True,
            "default_role": "core_assistant",
            "conversation_timeout": 3600,  # 1 hour
            "max_conversation_history": 1000,
            "emotional_analysis": True,
            "avatar_enabled": True
        },
        "braintrust": {
            "enabled": True,
            "consensus_required": "majority",
            "max_members_per_decision": 5,
            "decision_timeout": 300,  # 5 minutes
            "experimental_mode": False
        },
        "ai_models": {
            "default_provider": "github",
            "default_model": "github/gpt-4o-mini",
            "local_models_enabled": True,
            "cost_tracking": True,
            "max_tokens_per_request": 4096,
            "rate_limiting": {
                "requests_per_minute": 60,
                "tokens_per_minute": 100000
            }
        },
        "camera": {
            "enabled": True,
            "device_id": int(os.getenv("CAMERA_DEVICE_ID", "0")),
            "width": int(os.getenv("CAMERA_WIDTH", "1280")),
            "height": int(os.getenv("CAMERA_HEIGHT", "720")),
            "fps": 30,
            "facial_analysis": True,
            "emotion_tracking": True
        },
        "api": {
            "enabled": True,
            "host": "0.0.0.0",
            "port": 8080,
            "ssl_enabled": False,
            "cors_origins": ["*"],
            "rate_limiting": {
                "requests_per_minute": 100,
                "burst_limit": 20
            }
        },
        "security": {
            "api_key_required": True,
            "api_key_length": 32,
            "encryption_enabled": True,
            "session_timeout": 3600,
            "max_login_attempts": 5
        },
        "federation": {
            "enabled": True,
            "repositories": [
                "lumina_bridge",
                "kaiju_no_8_warp_engine",
                "iron_legion_ai_cluster"
            ],
            "sync_interval": 300,  # 5 minutes
            "conflict_resolution": "braintrust"
        },
        "monitoring": {
            "enabled": True,
            "metrics_interval": 60,  # 1 minute
            "alerts_enabled": True,
            "log_rotation": "daily",
            "performance_tracking": True
        },
        "backup": {
            "enabled": True,
            "interval": 3600,  # 1 hour
            "retention_days": 30,
            "compress_backups": True
        }
    }

    return config

def generate_braintrust_config():
    """Generate Braintrust configuration"""
    config = {
        "members": {
            "braintrust_core": {
                "active": True,
                "priority": 1,
                "decision_weight": 1.0,
                "specializations": ["coordination", "arbitration"]
            },
            "rr_system": {
                "active": True,
                "priority": 2,
                "decision_weight": 0.9,
                "specializations": ["risk_assessment", "reliability"]
            },
            "marvin_ai": {
                "active": True,
                "priority": 3,
                "decision_weight": 0.8,
                "specializations": ["deep_analysis", "creativity"]
            },
            "jarvis_imva": {
                "active": True,
                "priority": 1,
                "decision_weight": 0.95,
                "specializations": ["technical", "user_interface"]
            },
            "doit_executor": {
                "active": True,
                "priority": 1,
                "decision_weight": 0.9,
                "specializations": ["execution", "motivation"]
            },
            "ace_acva": {
                "active": True,
                "priority": 2,
                "decision_weight": 0.8,
                "specializations": ["gaming", "performance"]
            }
        },
        "consensus_rules": {
            "unanimous_required_complexity": ["critical"],
            "majority_required_complexity": ["complex", "critical"],
            "plurality_allowed_complexity": ["moderate", "complex"],
            "advisory_only_complexity": ["simple", "experimental"]
        },
        "decision_categories": {
            "technical": ["jarvis_imva", "rr_system"],
            "business": ["braintrust_core", "doit_executor"],
            "creative": ["marvin_ai", "jarvis_imva"],
            "gaming": ["ace_acva", "jarvis_imva"],
            "experimental": ["marvin_ai", "kenny_system"]
        }
    }

    return config

def generate_ai_model_config():
    """Generate AI model configuration"""
    config = {
        "providers": {
            "github": {
                "enabled": True,
                "priority": 1,
                "api_key": os.getenv("GITHUB_TOKEN", ""),
                "base_url": "https://models.github.ai/inference",
                "models": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "claude-3-5-sonnet",
                    "claude-3-haiku",
                    "gemini-1.5-pro",
                    "llama-3.1-405b-instruct"
                ]
            },
            "openai": {
                "enabled": bool(os.getenv("OPENAI_API_KEY")),
                "priority": 2,
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
            },
            "anthropic": {
                "enabled": bool(os.getenv("ANTHROPIC_API_KEY")),
                "priority": 2,
                "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                "models": ["claude-3-5-sonnet", "claude-3-haiku"]
            },
            "ollama": {
                "enabled": True,
                "priority": 3,
                "base_url": "http://localhost:11434",
                "models": []  # Will be discovered at runtime
            }
        },
        "routing_rules": {
            "local_tier": {
                "cost_threshold": 0.0,
                "latency_requirement": "any",
                "privacy_requirement": "high",
                "providers": ["ollama", "lm_studio", "gpt4all"]
            },
            "free_tier": {
                "cost_threshold": 0.001,
                "latency_requirement": "fast",
                "privacy_requirement": "medium",
                "providers": ["github", "google"]
            },
            "premium_tier": {
                "cost_threshold": 0.01,
                "latency_requirement": "fastest",
                "privacy_requirement": "any",
                "providers": ["openai", "anthropic"]
            }
        },
        "task_mappings": {
            "code_generation": ["github/gpt-4o", "anthropic/claude-3-5-sonnet", "openai/gpt-4o"],
            "conversation": ["github/gpt-4o-mini", "ollama/llama3.1"],
            "analysis": ["anthropic/claude-3-5-sonnet", "openai/gpt-4"],
            "creative": ["openai/gpt-4o", "anthropic/claude-3-5-sonnet"],
            "fast_response": ["github/gpt-4o-mini", "ollama/llama3.1"]
        }
    }

    return config

def generate_api_config():
    """Generate API configuration"""
    config = {
        "endpoints": {
            "jarvis": {
                "path": "/api/v1/jarvis",
                "methods": ["POST"],
                "description": "JARVIS conversation endpoint"
            },
            "braintrust": {
                "path": "/api/v1/braintrust",
                "methods": ["POST"],
                "description": "Braintrust decision endpoint"
            },
            "models": {
                "path": "/api/v1/models",
                "methods": ["GET", "POST"],
                "description": "AI model management"
            },
            "camera": {
                "path": "/api/v1/camera",
                "methods": ["GET", "POST"],
                "description": "Camera control and analysis"
            },
            "federation": {
                "path": "/api/v1/federation",
                "methods": ["GET", "POST"],
                "description": "Repository federation management"
            }
        },
        "authentication": {
            "required": True,
            "type": "bearer_token",
            "token_length": 32,
            "expiration_hours": 24
        },
        "rate_limiting": {
            "enabled": True,
            "requests_per_minute": 100,
            "burst_limit": 20,
            "backoff_strategy": "exponential"
        },
        "cors": {
            "enabled": True,
            "allow_origins": ["*"],
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"]
        }
    }

    return config

def generate_monitoring_config():
    """Generate monitoring configuration"""
    config = {
        "metrics": {
            "system": {
                "cpu_usage": True,
                "memory_usage": True,
                "disk_usage": True,
                "network_io": True
            },
            "application": {
                "response_time": True,
                "error_rate": True,
                "throughput": True,
                "active_users": True
            },
            "ai_models": {
                "usage_count": True,
                "cost_tracking": True,
                "performance_metrics": True,
                "error_rates": True
            }
        },
        "alerts": {
            "enabled": True,
            "rules": [
                {
                    "name": "high_cpu_usage",
                    "condition": "cpu_usage > 90",
                    "severity": "warning",
                    "action": "log"
                },
                {
                    "name": "memory_pressure",
                    "condition": "memory_usage > 85",
                    "severity": "critical",
                    "action": "restart_service"
                },
                {
                    "name": "api_errors",
                    "condition": "error_rate > 5",
                    "severity": "warning",
                    "action": "alert"
                }
            ]
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "rotation": "daily",
            "retention_days": 30,
            "compress_old": True
        },
        "dashboards": {
            "enabled": True,
            "port": 3000,
            "metrics_endpoint": "/metrics",
            "health_endpoint": "/health"
        }
    }

    return config

def generate_secrets():
    """Generate secure secrets for the system"""
    secrets_config = {
        "api_key_secret": secrets.token_hex(32),
        "encryption_key": secrets.token_hex(32),
        "jwt_secret": secrets.token_hex(32),
        "session_secret": secrets.token_hex(32),
        "generated_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
    }

    return secrets_config

def save_config(name: str, config: dict):
    try:
        """Save configuration to file"""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        config_path = config_dir / f"{name}.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Generated {name}.json")

    except Exception as e:
        logger.error(f"Error in save_config: {e}", exc_info=True)
        raise
def main():
    try:
        """Generate all configuration files"""
        print("🔧 Generating VA.B Configuration Files")
        print("="*50)

        # Create config directory
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        # Generate all configurations
        configs = {
            "system_config": generate_system_config(),
            "braintrust_config": generate_braintrust_config(),
            "ai_model_config": generate_ai_model_config(),
            "api_config": generate_api_config(),
            "monitoring_config": generate_monitoring_config(),
            "secrets": generate_secrets()
        }

        # Save all configurations
        for name, config in configs.items():
            save_config(name, config)

        print("\n✅ All configuration files generated!")
        print("📁 Location: config/ directory")
        print("\n📋 Generated files:")
        for name in configs.keys():
            print(f"   • {name}.json")

        # Generate summary
        summary = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "files_generated": list(configs.keys()),
            "total_files": len(configs),
            "status": "ready_for_deployment"
        }

        with open(config_dir / "generation_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n📊 Configuration generation complete!")
        print("🎯 VA.B system ready for deployment!")
    except Exception as e:
        print(f"\n❌ Error generating configuration: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()