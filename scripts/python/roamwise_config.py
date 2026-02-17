#!/usr/bin/env python3
"""
RoamWise Configuration

Configuration for SiderAI Wisebase and RoamResearch connections
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RoamWiseConfig:
    """Configuration manager for RoamWise"""

    def __init__(self, config_file: Optional[Path] = None):
        if config_file is None:
            config_file = Path(__file__).parent.parent.parent / "config" / "roamwise_config.json"

        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Default config
        self.config = {
            "siderai_wisebase": {
                "api_key": os.getenv("SIDERAI_WISEBASE_API_KEY", ""),
                "base_url": "https://api.sider.ai/wisebase",
                "enabled": True
            },
            "roamresearch": {
                "api_key": os.getenv("ROAMRESEARCH_API_KEY", ""),
                "base_url": "https://roamresearch.com/api",
                "graph_name": "lesnewski_lifetime",
                "account_type": "lifetime",
                "enabled": True
            },
            "roamwise": {
                "domain": "<LOCAL_HOSTNAME>",  # Primary domain (also supports lowercase)
                "port": 5000,
                "data_dir": "data/roamwise",
                "pathfinder": {
                    "style": "wow_atlas",
                    "grid_size": 10,
                    "max_connections": 7
                }
            }
        }

        # Load existing config
        self.load()

    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    self._merge_config(self.config, loaded)
            except Exception as e:
                print(f"Error loading config: {e}")

    def _merge_config(self, base: Dict, update: Dict):
        """Recursively merge config dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def save(self):
        try:
            """Save configuration to file"""
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in save: {e}", exc_info=True)
            raise
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set config value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()

