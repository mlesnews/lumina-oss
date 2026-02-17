#!/usr/bin/env python3
"""
PEAK Optimization - Update All Configurations to Peak Performance

Updates ALL settings and configurations everywhere in @HOMELAB
to make everything "*.*" (PEAK performance).

@PEAK @MARVIN @ROAST - Maximum performance optimization
"""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PEAKOptimizer:
    """
    PEAK Configuration Optimizer

    Updates all configurations to peak performance settings.
    @PEAK @MARVIN @ROAST
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize optimizer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.logger = get_logger("PEAKOptimizer")

        # PEAK performance settings
        self.peak_settings = {
            # Timeouts (aggressive but safe)
            "timeout": 300,  # 5 minutes
            "connection_timeout": 60,
            "request_timeout": 300,
            "deployment_timeout": 600,
            "activation_timeout": 300,
            "timeout_seconds": 30,

            # Resource limits (maximum safe values)
            "max_cpu_usage": 95.0,
            "max_memory_usage": 95.0,
            "max_gpu_usage": 95.0,
            "min_utilization": 85.0,
            "max_utilization": 99.0,
            "target_utilization": 97.0,

            # Cache settings (maximum)
            "cache_size": "10GB",
            "max_memory_cache": "2GB",
            "local_cache_size": "5GB",
            "cache_ttl": 7200,  # 2 hours
            "max_cache_entries": 100000,
            "cache_size_limit": 10000,

            # Thread/Concurrency (maximum)
            "max_threads": 32,
            "max_workers": 32,
            "max_concurrent": 50,
            "max_concurrent_sync": 10,
            "max_requests_per_session": 20,
            "thread_pool_size": 32,

            # Performance settings
            "performance_mode": "peak",
            "optimization_level": "maximum",
            "enable_optimization": True,
            "auto_optimization_enabled": True,
            "background_optimization": True,
            "threading_enabled": True,

            # Limits (maximum)
            "max_retries": 10,
            "max_attempts": 10,
            "max_fix_attempts": 5,
            "max_history_entries": 10000,
            "max_log_size_mb": 500,
            "max_file_size": "100MB",

            # Intervals (faster)
            "sync_interval": 60,  # 1 minute
            "sync_interval_minutes": 1,
            "optimization_interval_hours": 0.5,  # 30 minutes
            "report_interval_minutes": 15,
            "check_interval": 5,

            # Quality thresholds (high)
            "minimum_quality_threshold": 0.9,
            "content_similarity_threshold": 0.8,
            "cache_hit_ratio_alert": 0.9,
            "min_efficiency_score": 0.85,
        }

        self.updated_files = []
        self.errors = []

    def optimize_all_configs(self) -> Dict[str, Any]:
        """Optimize all configuration files"""
        self.logger.info("🚀 PEAK Optimization Starting...")
        self.logger.info("   @PEAK @MARVIN @ROAST - Maximum Performance Mode")

        # Find all config files
        config_files = self._find_config_files()

        self.logger.info(f"📁 Found {len(config_files)} configuration files")

        # Optimize each file
        for config_file in config_files:
            try:
                self._optimize_file(config_file)
            except Exception as e:
                self.logger.error(f"Error optimizing {config_file}: {e}")
                self.errors.append(str(config_file))

        # Summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(config_files),
            "updated_files": len(self.updated_files),
            "errors": len(self.errors),
            "updated": self.updated_files,
            "errors_list": self.errors
        }

        self.logger.info(f"✅ PEAK Optimization Complete!")
        self.logger.info(f"   Updated: {len(self.updated_files)} files")
        self.logger.info(f"   Errors: {len(self.errors)} files")

        return summary

    def _find_config_files(self) -> List[Path]:
        """Find all configuration files"""
        config_files = []

        # JSON configs
        for json_file in self.config_dir.rglob("*.json"):
            if json_file.name not in ["package.json", "tsconfig.json"]:
                config_files.append(json_file)

        # YAML configs
        for yaml_file in self.config_dir.rglob("*.yaml"):
            config_files.append(yaml_file)

        for yml_file in self.config_dir.rglob("*.yml"):
            config_files.append(yml_file)

        return config_files

    def _optimize_file(self, config_file: Path) -> None:
        """Optimize a single config file"""
        if config_file.suffix in ['.yaml', '.yml']:
            self._optimize_yaml(config_file)
        elif config_file.suffix == '.json':
            self._optimize_json(config_file)

    def _optimize_json(self, config_file: Path) -> None:
        """Optimize JSON config file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Optimize the data
            optimized = self._optimize_dict(data)

            # Only update if changed
            if optimized != data:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(optimized, f, indent=2, ensure_ascii=False)

                self.updated_files.append(str(config_file))
                self.logger.info(f"✅ Optimized: {config_file.name}")
        except Exception as e:
            self.logger.debug(f"Could not optimize {config_file}: {e}")

    def _optimize_yaml(self, config_file: Path) -> None:
        """Optimize YAML config file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data is None:
                return

            # Optimize the data
            optimized = self._optimize_dict(data)

            # Only update if changed
            if optimized != data:
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(optimized, f, default_flow_style=False, sort_keys=False)

                self.updated_files.append(str(config_file))
                self.logger.info(f"✅ Optimized: {config_file.name}")
        except Exception as e:
            self.logger.debug(f"Could not optimize {config_file}: {e}")

    def _optimize_dict(self, data: Any) -> Any:
        """Recursively optimize dictionary"""
        if isinstance(data, dict):
            optimized = {}
            for key, value in data.items():
                # Check if this key should be optimized
                optimized_key = self._optimize_key(key, value)
                if optimized_key is not None:
                    optimized[key] = optimized_key
                else:
                    # Recursively optimize nested structures
                    optimized[key] = self._optimize_dict(value)
            return optimized
        elif isinstance(data, list):
            return [self._optimize_dict(item) for item in data]
        else:
            return data

    def _optimize_key(self, key: str, value: Any) -> Optional[Any]:
        """Optimize a specific key-value pair"""
        key_lower = key.lower()

        # Timeout optimizations
        if any(term in key_lower for term in ['timeout', 'interval', 'cooldown']):
            if isinstance(value, (int, float)):
                if 'timeout' in key_lower:
                    # Increase timeouts for reliability
                    if value < 30:
                        return self.peak_settings.get('timeout_seconds', 30)
                    elif value < 300:
                        return self.peak_settings.get('timeout', 300)
                    elif value < 600:
                        return self.peak_settings.get('deployment_timeout', 600)
                elif 'interval' in key_lower or 'cooldown' in key_lower:
                    # Decrease intervals for faster updates
                    if isinstance(value, int) and value > 60:
                        return min(value, self.peak_settings.get('sync_interval', 60))
                    elif isinstance(value, float) and value > 1.0:
                        return min(value, self.peak_settings.get('optimization_interval_hours', 0.5))

        # Resource limit optimizations
        if any(term in key_lower for term in ['max_cpu', 'max_memory', 'max_gpu', 'cpu_usage', 'memory_usage']):
            if isinstance(value, (int, float)):
                if value < 90:
                    return self.peak_settings.get('max_cpu_usage', 95.0)

        if 'utilization' in key_lower:
            if isinstance(value, (int, float)):
                if 'target' in key_lower or 'optimal' in key_lower:
                    return self.peak_settings.get('target_utilization', 97.0)
                elif 'max' in key_lower:
                    return self.peak_settings.get('max_utilization', 99.0)
                elif 'min' in key_lower:
                    return self.peak_settings.get('min_utilization', 85.0)

        # Cache optimizations
        if 'cache' in key_lower:
            if 'size' in key_lower or 'limit' in key_lower:
                if isinstance(value, str):
                    # Increase cache sizes
                    if 'MB' in value.upper():
                        num = float(re.findall(r'\d+', value)[0])
                        if num < 1000:
                            return f"{int(num * 2)}MB"
                    elif 'GB' in value.upper():
                        num = float(re.findall(r'\d+', value)[0])
                        if num < 5:
                            return f"{int(num * 2)}GB"
                elif isinstance(value, int):
                    if value < 10000:
                        return min(value * 2, self.peak_settings.get('max_cache_entries', 100000))
            elif 'ttl' in key_lower:
                if isinstance(value, int) and value < 3600:
                    return self.peak_settings.get('cache_ttl', 7200)

        # Thread/concurrency optimizations
        if any(term in key_lower for term in ['thread', 'worker', 'concurrent', 'parallel']):
            if isinstance(value, int):
                if value < 16:
                    return min(value * 2, self.peak_settings.get('max_threads', 32))

        # Performance mode settings
        if 'performance' in key_lower or 'optimization' in key_lower:
            if isinstance(value, bool):
                return True
            elif isinstance(value, str):
                if 'mode' in key_lower:
                    return 'peak' if 'peak' not in value.lower() else value

        # Quality thresholds
        if 'threshold' in key_lower or 'ratio' in key_lower:
            if isinstance(value, (int, float)):
                if value < 0.8:
                    return max(value, 0.85)

        # Retry/attempt limits
        if any(term in key_lower for term in ['retry', 'attempt', 'max_fix']):
            if isinstance(value, int) and value < 5:
                return min(value * 2, self.peak_settings.get('max_retries', 10))

        # Enable flags
        if any(term in key_lower for term in ['enable', 'enabled']):
            if isinstance(value, bool) and not value:
                return True

        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PEAK Optimize All Configurations")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't save changes)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    optimizer = PEAKOptimizer()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be saved")

    summary = optimizer.optimize_all_configs()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("\n🚀 PEAK Optimization Summary")
        print("=" * 60)
        print(f"Total Files: {summary['total_files']}")
        print(f"Updated Files: {summary['updated_files']}")
        print(f"Errors: {summary['errors']}")
        if summary['updated']:
            print("\n✅ Updated Files:")
            for file in summary['updated'][:20]:  # Show first 20
                print(f"   • {Path(file).name}")
            if len(summary['updated']) > 20:
                print(f"   ... and {len(summary['updated']) - 20} more")

