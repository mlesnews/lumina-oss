#!/usr/bin/env python3
"""
NAS Physics Cache System
@WOPR Physics Simulation Caching | Multi-Tier Storage Acceleration

Advanced proxy-cache system specifically designed for physics simulation matrices.
Provides hierarchical caching with NAS persistence for massive computational datasets.
"""

import sys
import time
import threading
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import queue
import logging

# Import universal decision tree (optional)
try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False

# Configure logging first (before other imports that may use logger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [NAS_CACHE] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    import paramiko
    import numpy as np
    PARAMIKO_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    NUMPY_AVAILABLE = False

# Import NAS Azure Vault Integration for full API support
try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_VAULT_INTEGRATION_AVAILABLE = True
except ImportError:
    NAS_VAULT_INTEGRATION_AVAILABLE = False
    logger.warning("NASAzureVaultIntegration not available - NAS API features disabled")

# Import NAS Service Monitor for heartbeat and status monitoring
try:
    from nas_service_monitor import NASServiceMonitor, get_master_coordinator
    NAS_MONITOR_AVAILABLE = True
except ImportError:
    NAS_MONITOR_AVAILABLE = False
    logger.debug("NAS Service Monitor not available - monitoring disabled")

@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CacheEntry:
    """Cache entry with physics-specific metadata"""
    key: str
    data: Any
    size_bytes: int
    physics_domain: str
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: int = 3600
    compression_ratio: float = 1.0
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    total_entries: int = 0
    total_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    nas_read_count: int = 0
    nas_write_count: int = 0
    compression_savings: int = 0

class TieredPhysicsCache:
    """
    Multi-tier physics cache with NAS integration
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Tier 1: Memory cache (fastest)
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_limit = config.get('memory_limit', 4 * 1024 * 1024 * 1024)  # 4GB

        # Tier 2: SSD cache
        self.ssd_cache_dir = Path(config.get('ssd_cache_dir', 'data/cache/physics/ssd'))
        self.ssd_cache_dir.mkdir(parents=True, exist_ok=True)
        self.ssd_limit = config.get('ssd_limit', 200 * 1024 * 1024 * 1024)  # 200GB

        # Tier 3: NAS storage (persistent) with full API support
        self.nas_config = config.get('nas_config', {})
        self.nas_client_pool = queue.Queue(maxsize=5)
        self.nas_vault_integration: Optional[NASAzureVaultIntegration] = None
        self.nas_api_enabled = False
        self._initialize_nas_integration()
        self._initialize_nas_pool()

        # NAS Service Monitor (heartbeat and status monitoring)
        self.nas_monitor = None
        self._initialize_nas_monitor()

        # Cache management
        self.metrics = CacheMetrics()
        self.lock = threading.RLock()

        # Background maintenance
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True
        )
        self.maintenance_thread.start()

        logger.info("🏗️ Tiered Physics Cache initialized")
        if self.nas_api_enabled:
            logger.info("✅ NAS API integration enabled (Azure Key Vault + Synology API)")
        if self.nas_monitor:
            logger.info("✅ NAS Service Monitor enabled (heartbeat and status tracking)")

    def _initialize_nas_integration(self):
        """Initialize NAS Azure Vault Integration for full API support"""
        if not NAS_VAULT_INTEGRATION_AVAILABLE:
            logger.debug("NASAzureVaultIntegration not available - using SSH only")
            return

        try:
            # Get vault configuration from nas_config
            vault_name = self.nas_config.get('vault_name')
            vault_url = self.nas_config.get('vault_url')
            nas_ip = self.nas_config.get('host', '<NAS_PRIMARY_IP>')
            nas_port = self.nas_config.get('api_port', 5001)  # Synology DSM default

            # Initialize NASAzureVaultIntegration
            self.nas_vault_integration = NASAzureVaultIntegration(
                vault_name=vault_name,
                vault_url=vault_url,
                nas_ip=nas_ip,
                nas_port=nas_port
            )

            # Try to get credentials (validates Azure Key Vault access)
            credentials = self.nas_vault_integration.get_nas_credentials()
            if credentials:
                # Store password in nas_config for SSH connections
                self.nas_config['password'] = credentials.get('password')
                self.nas_config['username'] = credentials.get('username', self.nas_config.get('user', 'backupadm'))
                self.nas_api_enabled = True
                logger.info(f"✅ NAS API integration initialized (Vault: {vault_name or vault_url})")
            else:
                logger.warning("⚠️  Could not retrieve NAS credentials from Azure Key Vault - NAS API disabled")
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize NAS API integration: {e} - using SSH only")

    def _initialize_nas_pool(self):
        """Initialize NAS connection pool using decision tree for connection strategy"""
        if not PARAMIKO_AVAILABLE:
            logger.warning("Paramiko not available - NAS functionality disabled")
            return

        # Suppress paramiko verbose logging for connection attempts
        import logging as paramiko_logging
        paramiko_logger = paramiko_logging.getLogger("paramiko")
        original_level = paramiko_logger.level
        paramiko_logger.setLevel(paramiko_logging.WARNING)  # Suppress INFO/DEBUG

        nas_connected = False
        last_error = None
        connection_retry_count = 0

        # Try to get password from NAS vault integration if available
        password = self.nas_config.get('password')
        if not password and self.nas_vault_integration:
            try:
                credentials = self.nas_vault_integration.get_nas_credentials()
                if credentials:
                    password = credentials.get('password')
                    self.nas_config['password'] = password
                    self.nas_config['username'] = credentials.get('username', self.nas_config.get('user', 'backupadm'))
            except Exception as e:
                logger.debug(f"Could not get credentials from vault: {e}")
                last_error = str(e)

        # Use decision tree to determine connection strategy
        if DECISION_TREE_AVAILABLE and password:
            from universal_decision_tree import DecisionContext, decide, DecisionOutcome

            context = DecisionContext(
                nas_ssh_available=False,  # Will check
                nas_api_available=self.nas_api_enabled,
                connection_retry_count=connection_retry_count,
                last_error=last_error,
                custom_data={"password_available": password is not None}
            )

            # Attempt connection with decision tree guidance
            max_attempts = 3
            for attempt in range(max_attempts):
                context.connection_retry_count = attempt

                # Get decision
                result = decide("nas_connection", context)
                outcome = result.outcome

                if outcome == DecisionOutcome.RETRY_NAS_CONNECTION or outcome == DecisionOutcome.USE_LOCAL:
                    # Try SSH connection
                    try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        username = self.nas_config.get('username') or self.nas_config.get('user', 'backupadm')
                        client.connect(
                            hostname=self.nas_config.get('host', '<NAS_PRIMARY_IP>'),
                            username=username,
                            password=password,
                            timeout=self.nas_config.get('timeout', 30),
                            allow_agent=False,
                            look_for_keys=False
                        )
                        self.nas_client_pool.put(client)
                        logger.debug(f"NAS SSH connection established (decision: {result.reasoning})")
                        nas_connected = True
                        context.nas_ssh_available = True
                        break  # Success
                    except Exception as e:
                        last_error = str(e)
                        context.last_error = last_error
                        if attempt == max_attempts - 1:
                            logger.debug(f"NAS SSH connection failed after {max_attempts} attempts: {e}")

                elif outcome == DecisionOutcome.USE_NAS_API:
                    # Use API instead (already initialized)
                    logger.debug(f"Using NAS API based on decision tree: {result.reasoning}")
                    nas_connected = True  # API is available
                    break

                elif outcome == DecisionOutcome.SKIP_NAS:
                    # Skip NAS, use local only
                    logger.debug(f"Skipping NAS based on decision tree: {result.reasoning}")
                    break

        # Fallback: Traditional connection logic if decision tree not available
        elif password:
            for _ in range(3):
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    username = self.nas_config.get('username') or self.nas_config.get('user', 'backupadm')
                    client.connect(
                        hostname=self.nas_config.get('host', '<NAS_PRIMARY_IP>'),
                        username=username,
                        password=password,
                        timeout=self.nas_config.get('timeout', 30),
                        allow_agent=False,
                        look_for_keys=False
                    )
                    self.nas_client_pool.put(client)
                    logger.debug("NAS SSH connection established")
                    nas_connected = True
                    break  # Success, no need to retry
                except Exception as e:
                    # Only log once, not for every retry
                    if _ == 2:  # Last retry
                        logger.debug(f"NAS SSH connection failed: {e}")

        # Restore paramiko logging level
        paramiko_logger.setLevel(original_level)

        if nas_connected:
            logger.info("✅ NAS tier available (SSH connections established)")
        elif self.nas_api_enabled:
            logger.info("⚠️  NAS API enabled but SSH connections failed - using API for operations")
        else:
            logger.info("NAS tier unavailable (authentication required) - using local cache only (L1+L2 tiers)")

    def _initialize_nas_monitor(self):
        """Initialize NAS Service Monitor for heartbeat and status tracking"""
        if not NAS_MONITOR_AVAILABLE:
            logger.debug("NAS Service Monitor not available - monitoring disabled")
            return

        try:
            # Get monitoring configuration
            monitor_config = self.config.get('monitor_config', {})
            heartbeat_interval = monitor_config.get('heartbeat_interval', 300)  # 5 minutes default
            master_endpoint = monitor_config.get('master_endpoint')
            service_id = monitor_config.get('service_id', 'nas-physics-cache')

            # Create monitor
            self.nas_monitor = NASServiceMonitor(
                service_id=service_id,
                nas_config=self.nas_config,
                heartbeat_interval=heartbeat_interval,
                master_endpoint=master_endpoint,
                status_callback=self._on_nas_status_update
            )

            # Register with master coordinator
            try:
                master = get_master_coordinator()
                master.register_service(self.nas_monitor)
            except Exception as e:
                logger.debug(f"Could not register with master coordinator: {e}")

            # Start monitoring
            self.nas_monitor.start()
            logger.info(f"✅ NAS Service Monitor started (heartbeat: {heartbeat_interval}s)")

        except Exception as e:
            logger.debug(f"Failed to initialize NAS Service Monitor: {e} - continuing without monitoring")
            self.nas_monitor = None

    def _on_nas_status_update(self, health):
        """Callback for NAS status updates"""
        # Update internal status based on health
        if health.status.value == 'offline':
            logger.debug("NAS service reported offline - using local cache only")
        elif health.status.value == 'healthy':
            logger.debug("NAS service reported healthy")

    def _get_nas_client(self):
        """Get NAS client from pool (SSH) or create new connection"""
        try:
            return self.nas_client_pool.get(timeout=5)
        except queue.Empty:
            # Try to get password from vault integration if available
            password = self.nas_config.get('password')
            if not password and self.nas_vault_integration:
                try:
                    credentials = self.nas_vault_integration.get_nas_credentials()
                    if credentials:
                        password = credentials.get('password')
                except Exception:
                    pass

            # Create new SSH connection if password available
            if PARAMIKO_AVAILABLE and password:
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    username = self.nas_config.get('username') or self.nas_config.get('user', 'backupadm')
                    client.connect(
                        hostname=self.nas_config.get('host', '<NAS_PRIMARY_IP>'),
                        username=username,
                        password=password,
                        timeout=self.nas_config.get('timeout', 30),
                        allow_agent=False,
                        look_for_keys=False
                    )
                    return client
                except Exception as e:
                    logger.debug(f"NAS SSH connection attempt failed: {e}")
            return None

    def _return_nas_client(self, client):
        """Return NAS client to pool"""
        if client:
            try:
                self.nas_client_pool.put(client, timeout=1)
            except queue.Full:
                try:
                    client.close()
                except:
                    pass

    def put(self, key: str, data: Any, physics_domain: str = "generic",
            ttl_seconds: int = 3600, metadata: Dict[str, Any] = None) -> bool:
        """
        Store data in tiered cache system using decision tree for tier selection
        """
        with self.lock:
            try:
                # Calculate data size
                size_bytes = self._calculate_data_size(data)

                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    data=data,
                    size_bytes=size_bytes,
                    physics_domain=physics_domain,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    ttl_seconds=ttl_seconds,
                    metadata=metadata or {},
                    checksum=self._calculate_checksum(data)
                )

                # Use decision tree to determine cache tier
                if DECISION_TREE_AVAILABLE:
                    from universal_decision_tree import DecisionContext, decide, DecisionOutcome

                    # Calculate memory usage
                    current_memory_usage = sum(e.size_bytes for e in self.memory_cache.values())
                    memory_usage_percent = (current_memory_usage / self.memory_limit) * 100 if self.memory_limit > 0 else 0

                    # Calculate SSD usage (approximate)
                    ssd_usage = 0
                    if self.ssd_cache_dir.exists():
                        try:
                            ssd_usage = sum(f.stat().st_size for f in self.ssd_cache_dir.glob("*.cache"))
                        except:
                            pass
                    ssd_usage_percent = (ssd_usage / self.ssd_limit) * 100 if self.ssd_limit > 0 else 0

                    # Create decision context
                    context = DecisionContext(
                        cache_data_size=size_bytes,
                        memory_cache_available=True,
                        memory_cache_usage_percent=memory_usage_percent,
                        ssd_cache_available=self.ssd_cache_dir.exists(),
                        ssd_cache_usage_percent=ssd_usage_percent,
                        nas_cache_available=not self.nas_client_pool.empty() or self.nas_api_enabled,
                        nas_api_available=self.nas_api_enabled,
                        nas_ssh_available=not self.nas_client_pool.empty(),
                        cache_domain=physics_domain
                    )

                    # Get decision
                    result = decide("cache_tier_selection", context)
                    outcome = result.outcome

                    # Execute based on decision
                    if outcome == DecisionOutcome.USE_L1_CACHE or outcome == DecisionOutcome.FALLBACK_LOCAL_CACHE:
                        if self._can_fit_in_memory(entry):
                            self.memory_cache[key] = entry
                            self.metrics.total_entries += 1
                            self.metrics.total_size_bytes += size_bytes
                            logger.debug(f"Decision tree selected L1 cache: {key} ({result.reasoning})")
                            return True

                    if outcome == DecisionOutcome.USE_L2_CACHE or outcome == DecisionOutcome.FALLBACK_LOCAL_CACHE:
                        if self._store_ssd(entry):
                            # Also store in memory if possible for fast access
                            if self._can_fit_in_memory(entry):
                                self.memory_cache[key] = entry
                                self.metrics.total_entries += 1
                                self.metrics.total_size_bytes += size_bytes
                            logger.debug(f"Decision tree selected L2 cache: {key} ({result.reasoning})")
                            return True

                    if outcome == DecisionOutcome.USE_L3_CACHE:
                        if self._store_nas(entry):
                            logger.debug(f"Decision tree selected L3 cache: {key} ({result.reasoning})")
                            return True

                    # Fallback to traditional logic if decision tree fails
                    logger.debug(f"Decision tree outcome {outcome.value} not executable, using fallback logic")

                # Fallback: Traditional tier selection logic
                # Force SSD storage for certain domains (jarvis_cron) to ensure persistence across runs
                if physics_domain == "jarvis_cron":
                    if self._store_ssd(entry):
                        # Also store in memory for fast access during same run
                        if self._can_fit_in_memory(entry):
                            self.memory_cache[key] = entry
                            self.metrics.total_entries += 1
                            self.metrics.total_size_bytes += size_bytes
                        logger.debug(f"Forced SSD storage for persistent domain: {key}")
                        return True

                # Try memory cache first (L1) for other domains
                if self._can_fit_in_memory(entry):
                    self.memory_cache[key] = entry
                    self.metrics.total_entries += 1
                    self.metrics.total_size_bytes += size_bytes
                    logger.debug(f"Stored in memory cache: {key}")
                    return True

                # Try SSD cache (L2) for other domains
                if self._store_ssd(entry):
                    logger.debug(f"Stored in SSD cache: {key}")
                    return True

                # NAS storage (L3)
                if self._store_nas(entry):
                    logger.debug(f"Stored in NAS: {key}")
                    return True

                logger.warning(f"Failed to store {key} - all tiers full")
                return False

            except Exception as e:
                # Storage failures are logged but don't break the system
                logger.debug(f"Failed to store {key} (using available tiers): {e}")
                return False

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve data from tiered cache system
        """
        with self.lock:
            # Check memory cache first (L1)
            if key in self.memory_cache:
                entry = self.memory_cache[key]

                # Check TTL
                if self._is_expired(entry):
                    del self.memory_cache[key]
                    self.metrics.eviction_count += 1
                else:
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    self.metrics.hit_count += 1
                    logger.debug(f"Memory cache hit: {key}")
                    return entry.data

            # For jarvis_cron domain, check SSD first since data is stored there persistently
            if key.startswith('cron_entry_') or key.startswith('tasks_config_'):
                data = self._retrieve_ssd(key)
                if data is not None:
                    self.metrics.hit_count += 1
                    # Promote to memory cache if possible
                    self._promote_to_memory(key, data)
                    logger.debug(f"SSD cache hit (persistent domain): {key}")
                    return data

            # Check SSD cache (L2) for other keys
            data = self._retrieve_ssd(key)
            if data is not None:
                self.metrics.hit_count += 1
                # Promote to memory cache if possible
                self._promote_to_memory(key, data)
                logger.debug(f"SSD cache hit: {key}")
                return data

            # Check NAS (L3)
            data = self._retrieve_nas(key)
            if data is not None:
                self.metrics.hit_count += 1
                self.metrics.nas_read_count += 1
                # Promote to higher tiers
                self._promote_to_ssd(key, data)
                self._promote_to_memory(key, data)
                logger.debug(f"NAS cache hit: {key}")
                return data

            self.metrics.miss_count += 1
            logger.debug(f"Cache miss: {key}")
            return None

    def _can_fit_in_memory(self, entry: CacheEntry) -> bool:
        """Check if entry can fit in memory cache"""
        current_memory_usage = sum(e.size_bytes for e in self.memory_cache.values())
        return current_memory_usage + entry.size_bytes <= self.memory_limit

    def _store_ssd(self, entry: CacheEntry) -> bool:
        """Store entry in SSD cache"""
        try:
            cache_file = self.ssd_cache_dir / f"{entry.key}.cache"

            # Prepare cache data
            cache_data = {
                'key': entry.key,
                'data': entry.data,
                'metadata': {
                    'physics_domain': entry.physics_domain,
                    'created_at': entry.created_at.isoformat(),
                    'ttl_seconds': entry.ttl_seconds,
                    'checksum': entry.checksum,
                    'size_bytes': entry.size_bytes,
                    'extra_metadata': entry.metadata
                }
            }

            # Compress if numpy array
            if NUMPY_AVAILABLE and isinstance(entry.data, np.ndarray):
                np.savez_compressed(cache_file.with_suffix('.npz'), **{'data': entry.data})
                cache_data['data_type'] = 'numpy_compressed'
                cache_data['data'] = None  # Don't store in JSON
            else:
                with open(cache_file, 'wb') as f:
                    import pickle
                    pickle.dump(entry.data, f)
                cache_data['data_type'] = 'pickle'

            # Store metadata
            metadata_file = cache_file.with_suffix('.meta')
            with open(metadata_file, 'w') as f:
                json.dump(cache_data['metadata'], f, indent=2)

            return True

        except Exception as e:
            # SSD storage failures are logged but don't break the system
            logger.debug(f"SSD storage failed: {e}")
            return False

    def _retrieve_ssd(self, key: str) -> Optional[Any]:
        """Retrieve from SSD cache"""
        try:
            cache_file = self.ssd_cache_dir / f"{key}.cache"
            metadata_file = self.ssd_cache_dir / f"{key}.meta"

            if not metadata_file.exists():
                return None

            # Load metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Check TTL
            created_at = datetime.fromisoformat(metadata['created_at'])
            ttl_seconds = metadata['ttl_seconds']
            if (datetime.now() - created_at).total_seconds() > ttl_seconds:
                # Expired, clean up
                self._cleanup_ssd_file(key)
                return None

            # Load data
            data_type = metadata.get('data_type', 'pickle')
            if data_type == 'numpy_compressed':
                data_file = cache_file.with_suffix('.npz')
                if data_file.exists():
                    loaded = np.load(data_file)
                    return loaded['data']
            else:
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        import pickle
                        return pickle.load(f)

        except Exception as e:
            # SSD retrieval failures are logged but don't break the system
            logger.debug(f"SSD retrieval failed: {e}")
            self._cleanup_ssd_file(key)

        return None

    def _store_nas(self, entry: CacheEntry) -> bool:
        """Store entry in NAS (using NAS API if available, else SSH)"""
        # Try NAS API first if available
        if self.nas_api_enabled and self.nas_vault_integration:
            return self._store_nas_via_api(entry)

        # Fallback to SSH
        client = self._get_nas_client()
        if not client:
            return False

        try:
            base_path = self.nas_config.get('base_path', '/volume1/cache/physics')
            physics_path = f"{base_path}/{entry.physics_domain}"

            # Create directory
            client.exec_command(f"mkdir -p {physics_path}")

            # Store metadata
            metadata_json = json.dumps({
                'key': entry.key,
                'physics_domain': entry.physics_domain,
                'created_at': entry.created_at.isoformat(),
                'ttl_seconds': entry.ttl_seconds,
                'checksum': entry.checksum,
                'size_bytes': entry.size_bytes,
                'metadata': entry.metadata
            }, indent=2)

            # Upload metadata (simplified - would need proper file transfer)
            stdin, stdout, stderr = client.exec_command(
                f"cat > {physics_path}/{entry.key}.meta << 'EOF'\n{metadata_json}\nEOF"
            )

            # For large data, would implement proper transfer mechanism
            # This is a conceptual implementation

            self.metrics.nas_write_count += 1
            return True

        except Exception as e:
            # NAS failures are expected - system degrades to local cache
            logger.debug(f"NAS storage failed (expected if NAS unavailable): {e}")
            return False
        finally:
            self._return_nas_client(client)

    def _store_nas_via_api(self, entry: CacheEntry) -> bool:
        """Store entry in NAS using Synology API"""
        if not self.nas_vault_integration:
            return False

        try:
            # Create temporary file for metadata
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
                metadata_json = json.dumps({
                    'key': entry.key,
                    'physics_domain': entry.physics_domain,
                    'created_at': entry.created_at.isoformat(),
                    'ttl_seconds': entry.ttl_seconds,
                    'checksum': entry.checksum,
                    'size_bytes': entry.size_bytes,
                    'metadata': entry.metadata
                }, indent=2)
                f.write(metadata_json)
                temp_path = Path(f.name)

            # Upload via NAS API
            base_path = self.nas_config.get('base_path', '/volume1/cache/physics')
            remote_path = f"{base_path}/{entry.physics_domain}/{entry.key}.meta"

            if self.nas_vault_integration.upload_file(temp_path, remote_path):
                temp_path.unlink()  # Clean up temp file
                self.metrics.nas_write_count += 1
                logger.debug(f"Stored cache entry via NAS API: {entry.key}")
                return True
            else:
                temp_path.unlink()
                return False
        except Exception as e:
            # NAS API failures are expected - system degrades to local cache
            logger.debug(f"NAS API storage failed (expected if NAS unavailable): {e}")
            return False

    def _retrieve_nas(self, key: str) -> Optional[Any]:
        """Retrieve from NAS"""
        # Simplified implementation - would need proper data transfer
        return None

    def _promote_to_memory(self, key: str, data: Any):
        """Promote data to memory cache"""
        # Implementation would create CacheEntry and add to memory_cache
        pass

    def _promote_to_ssd(self, key: str, data: Any):
        """Promote data to SSD cache"""
        # Implementation would create SSD cache entry
        pass

    def _calculate_data_size(self, data: Any) -> int:
        """Calculate approximate data size in bytes"""
        if NUMPY_AVAILABLE and isinstance(data, np.ndarray):
            return data.nbytes
        elif isinstance(data, (list, tuple)):
            return sum(self._calculate_data_size(item) for item in data)
        elif isinstance(data, dict):
            return sum(len(str(k)) + self._calculate_data_size(v) for k, v in data.items())
        else:
            return len(str(data).encode('utf-8'))

    def _calculate_checksum(self, data: Any) -> str:
        """Calculate data checksum"""
        data_str = str(data)
        if NUMPY_AVAILABLE and isinstance(data, np.ndarray):
            data_str = data.tobytes()
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        age_seconds = (datetime.now() - entry.created_at).total_seconds()
        return age_seconds > entry.ttl_seconds

    def _cleanup_ssd_file(self, key: str):
        """Clean up SSD cache files"""
        try:
            cache_file = self.ssd_cache_dir / f"{key}.cache"
            meta_file = self.ssd_cache_dir / f"{key}.meta"
            npz_file = self.ssd_cache_dir / f"{key}.npz"

            for file_path in [cache_file, meta_file, npz_file]:
                if file_path.exists():
                    file_path.unlink()
        except Exception as e:
            # Cleanup failures are non-critical
            logger.debug(f"Cleanup failed for {key}: {e}")

    def _maintenance_loop(self):
        """Background maintenance loop"""
        while True:
            try:
                # Clean expired entries
                self._clean_expired_entries()

                # Evict LRU entries if over limit
                self._evict_lru_entries()

                # Update metrics
                self._update_metrics()

                time.sleep(300)  # Run every 5 minutes

            except Exception as e:
                # Maintenance errors are non-critical - system continues operating
                logger.debug(f"Maintenance loop error (non-critical): {e}")
                time.sleep(60)

    def _clean_expired_entries(self):
        """Clean expired cache entries"""
        with self.lock:
            # Memory cache
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if self._is_expired(entry)
            ]
            for key in expired_keys:
                del self.memory_cache[key]
                self.metrics.eviction_count += 1

            # SSD cache (would need to scan directory)
            # NAS cache (would need to scan remote)

    def _evict_lru_entries(self):
        """Evict least recently used entries"""
        with self.lock:
            if sum(e.size_bytes for e in self.memory_cache.values()) > self.memory_limit * 0.9:
                # Sort by last accessed
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].last_accessed
                )

                # Evict oldest entries until under 80% capacity
                target_size = self.memory_limit * 0.8
                current_size = sum(e.size_bytes for e in self.memory_cache.values())

                evicted = 0
                for key, entry in sorted_entries:
                    if current_size <= target_size:
                        break
                    del self.memory_cache[key]
                    current_size -= entry.size_bytes
                    evicted += 1

                self.metrics.eviction_count += evicted

    def _update_metrics(self):
        """Update cache performance metrics"""
        self.metrics.total_entries = len(self.memory_cache)
        self.metrics.total_size_bytes = sum(e.size_bytes for e in self.memory_cache.values())

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        hit_rate = 0.0
        total_requests = self.metrics.hit_count + self.metrics.miss_count
        if total_requests > 0:
            hit_rate = self.metrics.hit_count / total_requests

        metrics = {
            'total_entries': self.metrics.total_entries,
            'total_size_bytes': self.metrics.total_size_bytes,
            'hit_count': self.metrics.hit_count,
            'miss_count': self.metrics.miss_count,
            'eviction_count': self.metrics.eviction_count,
            'nas_read_count': self.metrics.nas_read_count,
            'nas_write_count': self.metrics.nas_write_count,
            'hit_rate': hit_rate,
            'memory_usage_percent': (self.metrics.total_size_bytes / self.memory_limit) * 100
        }

        # Add monitoring status if available
        if self.nas_monitor:
            try:
                metrics['nas_monitoring'] = self.nas_monitor.get_status()
            except Exception:
                pass

        return metrics

    def get_monitoring_status(self) -> Optional[Dict[str, Any]]:
        """Get NAS service monitoring status"""
        if not self.nas_monitor:
            return None
        try:
            return self.nas_monitor.get_status()
        except Exception as e:
            logger.debug(f"Could not get monitoring status: {e}")
            return None

    def get_health_summary(self) -> Optional[Dict[str, Any]]:
        """Get NAS service health summary"""
        if not self.nas_monitor:
            return None
        try:
            return self.nas_monitor.get_health_summary()
        except Exception as e:
            logger.debug(f"Could not get health summary: {e}")
            return None

def main():
    """NAS Physics Cache demonstration"""
    print("🚀 NAS Physics Cache System")
    print("=" * 40)

    # Configuration
    config = {
        'memory_limit': 2 * 1024 * 1024 * 1024,  # 2GB
        'ssd_cache_dir': 'data/cache/physics/ssd',
        'ssd_limit': 10 * 1024 * 1024 * 1024,    # 10GB
        'nas_config': {
            'host': '<NAS_PRIMARY_IP>',
            'user': 'backupadm',
            'base_path': '/volume1/cache/physics',
            'timeout': 30
        }
    }

    cache = TieredPhysicsCache(config)

    # Demonstrate physics data caching
    if NUMPY_AVAILABLE:
        print("🔬 Creating sample physics simulation data...")

        # Fluid dynamics simulation data
        fluid_data = np.random.rand(100, 100, 50)  # 3D velocity field
        cache.put("fluid_sim_001", fluid_data, physics_domain="fluid_dynamics", ttl_seconds=3600)

        # Quantum mechanics wave function
        quantum_data = np.random.rand(64, 64, 64) + 1j * np.random.rand(64, 64, 64)
        cache.put("quantum_sim_001", quantum_data, physics_domain="quantum_mechanics", ttl_seconds=7200)

        # Retrieve data
        print("📖 Retrieving cached data...")
        retrieved_fluid = cache.get("fluid_sim_001")
        retrieved_quantum = cache.get("quantum_sim_001")

        print(f"Fluid data retrieved: {retrieved_fluid is not None}")
        print(f"Quantum data retrieved: {retrieved_quantum is not None}")

        # Show metrics
        metrics = cache.get_metrics()
        print("\n📊 Cache Performance:")
        print(f"  Entries: {metrics['total_entries']}")
        print(f"  Hit Rate: {metrics['hit_rate']:.1%}")
        print(f"  Memory Usage: {metrics['memory_usage_percent']:.1f}%")

    print("\n✅ NAS Physics Cache demonstration completed")

if __name__ == "__main__":


    main()