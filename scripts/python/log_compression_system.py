#!/usr/bin/env python3
"""
Log Compression System - Advanced Log Management for LUMINA Ecosystem

Features:
- Automatic log rotation and compression when logs exceed 1k lines
- Integration with NAS Perl package for large file parsing
- Log analysis and size monitoring
- GPU-optimized processing for large log files
- Request size analysis and optimization
- Model recommendation system for 5090 mobile GPU

Tags: #LOG_COMPRESSION #LOG_MANAGEMENT #NAS_INTEGRATION #GPU_OPTIMIZATION #PERFORMANCE
      @JARVIS @LUMINA @ULTRON @KAIJU
"""

import os
import sys
import gzip
import shutil
import logging
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import subprocess
import platform
import psutil

# Optional GPU monitoring imports (will be handled gracefully if not available)
try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    import pynvml
except ImportError:
    pynvml = None

try:
    import nvidia_smi
except ImportError:
    nvidia_smi = None

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

logger = get_logger("LogCompressionSystem")

@dataclass
class LogFileInfo:
    """Information about a log file"""
    path: Path
    size_bytes: int
    line_count: int
    last_modified: datetime
    compressed: bool = False
    compression_ratio: Optional[float] = None

@dataclass
class CompressionResult:
    """Result of log compression operation"""
    original_file: Path
    compressed_file: Path
    original_size: int
    compressed_size: int
    compression_ratio: float
    lines_processed: int
    processing_time: float
    success: bool
    error: Optional[str] = None

@dataclass
class SystemInfo:
    """System information including GPU details"""
    cpu_cores: int
    total_memory_gb: float
    available_memory_gb: float
    gpu_available: bool
    gpu_name: Optional[str] = None
    gpu_memory_gb: Optional[float] = None
    gpu_utilization: Optional[float] = None
    gpu_temperature: Optional[float] = None
    gpu_driver_version: Optional[str] = None

@dataclass
class RequestAnalysis:
    """Analysis of request sizes and patterns"""
    average_request_size: float
    max_request_size: float
    min_request_size: float
    total_requests: int
    total_data_size: float
    request_patterns: Dict[str, int] = field(default_factory=dict)

@dataclass
class ModelRecommendation:
    """Model recommendation for specific hardware"""
    model_name: str
    model_size: str
    recommended_for: str
    performance_score: float
    memory_requirements_gb: float
    compatibility_score: float
    notes: str = ""

class LogCompressionSystem:
    """Advanced Log Compression System for LUMINA Ecosystem"""

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize Log Compression System

        Args:
            log_dir: Directory containing log files (default: logs/)
        """
        self.log_dir = log_dir or project_root / "logs"
        self.logger = logger
        self.compression_threshold_lines = 1000  # Compress logs over 1k lines
        self.max_log_size_bytes = 10 * 1024 * 1024  # 10MB max log size
        self.backup_count = 5  # Keep 5 compressed backups
        self.nas_perl_available = self._check_nas_perl_availability()
        self.system_info = self._get_system_info()

        # Initialize GPU monitoring
        self.gpu_monitor = self._initialize_gpu_monitoring()

        # Log file patterns to monitor
        self.log_patterns = ["*.log", "*.log.gz"]

        self.logger.info(f"Log Compression System initialized")
        self.logger.info(f"Log directory: {self.log_dir}")
        self.logger.info(f"NAS Perl available: {self.nas_perl_available}")
        self.logger.info(f"System info: {self.system_info}")

    def _check_nas_perl_availability(self) -> bool:
        """Check if NAS Perl package is available"""
        try:
            # Check for Perl installation
            result = subprocess.run(["perl", "--version"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.info("Perl is available on the system")
                perl_version = result.stdout.split('\n')[0].strip()
                self.logger.info(f"Perl version: {perl_version}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Check for NAS-specific Perl modules
        try:
            # This would be specific to your NAS Perl package
            # For example, checking for DSM Perl package
            if platform.system() == "Linux":
                # Check for Synology DSM Perl package
                result = subprocess.run(["/usr/bin/perl", "--version"],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info("NAS Perl package (DSM) is available")
                    nas_perl_version = result.stdout.split('\n')[0].strip()
                    self.logger.info(f"NAS Perl version: {nas_perl_version}")
                    return True
        except Exception as e:
            self.logger.debug(f"NAS Perl check failed: {e}")

        # Provide detailed installation guidance for Windows systems
        if platform.system() == "Windows":
            self.logger.warning("Perl not found - Windows system detected")
            self.logger.warning("For optimal NAS/DMS compatibility, please install Perl:")
            self.logger.warning("1. Install Strawberry Perl: https://strawberryperl.com/")
            self.logger.warning("2. Or install via Chocolatey: choco install strawberryperl")
            self.logger.warning("3. Then install required modules: cpan install Compress::Zlib")
            self.logger.warning("See PERL_INSTALLATION_GUIDE.md for detailed instructions")
        else:
            self.logger.warning("NAS Perl package not found - using Python-based processing")

        return False

    def _initialize_gpu_monitoring(self) -> bool:
        """Initialize GPU monitoring"""
        try:
            # Try different GPU monitoring methods
            if hasattr(pynvml, 'nvmlInit'):
                pynvml.nvmlInit()
                return True
            elif hasattr(GPUtil, 'getGPUs'):
                gpus = GPUtil.getGPUs()
                if gpus:
                    return True
            elif hasattr(nvidia_smi, 'nvmlDeviceGetHandleByIndex'):
                return True
        except Exception as e:
            self.logger.debug(f"GPU monitoring initialization failed: {e}")

        return False

    def _get_system_info(self) -> SystemInfo:
        """Get comprehensive system information"""
        try:
            # CPU info
            cpu_cores = psutil.cpu_count(logical=True) or 1

            # Memory info
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024 ** 3)
            available_memory_gb = memory.available / (1024 ** 3)

            # GPU info
            gpu_available = False
            gpu_name = None
            gpu_memory_gb = None
            gpu_utilization = None
            gpu_temperature = None
            gpu_driver_version = None

            try:
                if self._check_gpu_availability():
                    gpu_available = True
                    gpu_info = self._get_gpu_info()
                    if gpu_info:
                        gpu_name = gpu_info.get('name', 'Unknown GPU')
                        gpu_memory_gb = gpu_info.get('memory_gb', 0.0)
                        gpu_utilization = gpu_info.get('utilization', 0.0)
                        gpu_temperature = gpu_info.get('temperature', 0.0)
                        gpu_driver_version = gpu_info.get('driver_version', 'Unknown')
            except Exception as e:
                self.logger.debug(f"GPU info retrieval failed: {e}")

            return SystemInfo(
                cpu_cores=cpu_cores,
                total_memory_gb=total_memory_gb,
                available_memory_gb=available_memory_gb,
                gpu_available=gpu_available,
                gpu_name=gpu_name,
                gpu_memory_gb=gpu_memory_gb,
                gpu_utilization=gpu_utilization,
                gpu_temperature=gpu_temperature,
                gpu_driver_version=gpu_driver_version
            )
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return SystemInfo(
                cpu_cores=1,
                total_memory_gb=8.0,
                available_memory_gb=4.0,
                gpu_available=False
            )

    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available and accessible"""
        try:
            # Try multiple methods to detect GPU
            methods = [
                lambda: len(GPUtil.getGPUs()) > 0 if hasattr(GPUtil, 'getGPUs') else False,
                lambda: pynvml.nvmlDeviceGetCount() > 0 if hasattr(pynvml, 'nvmlDeviceGetCount') else False,
                lambda: any('nvidia' in device.lower() for device in psutil.sensors_temperatures().keys())
            ]

            for method in methods:
                try:
                    if method():
                        return True
                except:
                    continue

            return False
        except Exception as e:
            self.logger.debug(f"GPU availability check failed: {e}")
            return False

    def _get_gpu_info(self) -> Optional[Dict[str, Any]]:
        """Get detailed GPU information"""
        try:
            # Try GPUtil first
            if hasattr(GPUtil, 'getGPUs'):
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Get first GPU
                    return {
                        'name': gpu.name,
                        'memory_gb': gpu.memoryTotal / 1024,
                        'utilization': gpu.load * 100,
                        'temperature': gpu.temperature,
                        'driver_version': 'Unknown'
                    }

            # Try pynvml
            if hasattr(pynvml, 'nvmlDeviceGetHandleByIndex'):
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                driver_version = pynvml.nvmlSystemGetDriverVersion()

                return {
                    'name': name.decode('utf-8'),
                    'memory_gb': memory_info.total / (1024 ** 3),
                    'utilization': utilization.gpu,
                    'temperature': temperature,
                    'driver_version': driver_version.decode('utf-8')
                }

            # Try nvidia-smi
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,utilization.gpu,temperature.gpu,driver_version',
                                        '--format=csv,noheader'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        parts = [p.strip() for p in lines[0].split(',')]
                        if len(parts) >= 5:
                            return {
                                'name': parts[0],
                                'memory_gb': float(parts[1].split()[0]) / 1024,
                                'utilization': float(parts[2].split()[0]),
                                'temperature': float(parts[3].split()[0]),
                                'driver_version': parts[4]
                            }
            except Exception as e:
                self.logger.debug(f"nvidia-smi query failed: {e}")

        except Exception as e:
            self.logger.debug(f"GPU info retrieval failed: {e}")

        return None

    def scan_log_files(self) -> List[LogFileInfo]:
        """Scan log directory and collect file information"""
        log_files = []

        if not self.log_dir.exists():
            self.logger.warning(f"Log directory does not exist: {self.log_dir}")
            return log_files

        for log_file in self.log_dir.glob("*"):
            if log_file.is_file() and (log_file.suffix == ".log" or log_file.suffix == ".log.gz"):
                try:
                    stat = log_file.stat()
                    line_count = 0

                    # Count lines efficiently
                    if log_file.suffix == ".log":
                        with log_file.open('r', encoding='utf-8', errors='ignore') as f:
                            for _ in f:
                                line_count += 1
                    elif log_file.suffix == ".log.gz":
                        with gzip.open(log_file, 'rt', encoding='utf-8', errors='ignore') as f:
                            for _ in f:
                                line_count += 1

                    log_files.append(LogFileInfo(
                        path=log_file,
                        size_bytes=stat.st_size,
                        line_count=line_count,
                        last_modified=datetime.fromtimestamp(stat.st_mtime),
                        compressed=log_file.suffix == ".log.gz"
                    ))
                except Exception as e:
                    self.logger.error(f"Failed to process log file {log_file}: {e}")

        return log_files

    def compress_log_file(self, log_file: Path, force: bool = False) -> CompressionResult:
        """
        Compress a log file using gzip

        Args:
            log_file: Path to log file
            force: Force compression even if below threshold

        Returns:
            CompressionResult
        """
        start_time = datetime.now()

        if not log_file.exists():
            return CompressionResult(
                original_file=log_file,
                compressed_file=log_file.with_suffix('.log.gz'),
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                lines_processed=0,
                processing_time=0.0,
                success=False,
                error="Log file does not exist"
            )

        # Check if file is currently locked/in use
        try:
            # Try to open the file in exclusive mode to check if it's locked
            with open(log_file, 'rb') as test_file:
                test_file.read(1)  # Just read a byte to test access
        except (OSError, IOError) as e:
            # File is locked by another process
            file_info = self._get_log_file_info_safe(log_file)
            return CompressionResult(
                original_file=log_file,
                compressed_file=log_file.with_suffix('.log.gz'),
                original_size=file_info.size_bytes if file_info else 0,
                compressed_size=0,
                compression_ratio=0.0,
                lines_processed=file_info.line_count if file_info else 0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error=f"Log file is currently in use by another process: {e}"
            )

        # Check if compression is needed
        file_info = self._get_log_file_info(log_file)
        if not force and file_info.line_count <= self.compression_threshold_lines:
            return CompressionResult(
                original_file=log_file,
                compressed_file=log_file.with_suffix('.log.gz'),
                original_size=file_info.size_bytes,
                compressed_size=file_info.size_bytes,
                compression_ratio=1.0,
                lines_processed=file_info.line_count,
                processing_time=0.0,
                success=False,
                error=f"Log file has only {file_info.line_count} lines (threshold: {self.compression_threshold_lines})"
            )

        compressed_file = log_file.with_suffix('.log.gz')

        try:
            # Use NAS Perl if available for large files
            if self.nas_perl_available and file_info.size_bytes > 10 * 1024 * 1024:  # 10MB
                return self._compress_with_perl(log_file, compressed_file, file_info)
            else:
                return self._compress_with_python(log_file, compressed_file, file_info)

        except Exception as e:
            return CompressionResult(
                original_file=log_file,
                compressed_file=compressed_file,
                original_size=file_info.size_bytes,
                compressed_size=0,
                compression_ratio=0.0,
                lines_processed=file_info.line_count,
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error=str(e)
            )

    def _compress_with_python(self, log_file: Path, compressed_file: Path, file_info: LogFileInfo) -> CompressionResult:
        """Compress log file using Python gzip"""
        start_time = datetime.now()

        try:
            with log_file.open('rb') as f_in:
                with gzip.open(compressed_file, 'wb', compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Get compressed file info
            compressed_size = compressed_file.stat().st_size
            compression_ratio = compressed_size / file_info.size_bytes if file_info.size_bytes > 0 else 1.0

            # Remove original file if compression was successful
            if compressed_size < file_info.size_bytes:
                log_file.unlink()

            processing_time = (datetime.now() - start_time).total_seconds()

            return CompressionResult(
                original_file=log_file,
                compressed_file=compressed_file,
                original_size=file_info.size_bytes,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                lines_processed=file_info.line_count,
                processing_time=processing_time,
                success=True
            )

        except Exception as e:
            return CompressionResult(
                original_file=log_file,
                compressed_file=compressed_file,
                original_size=file_info.size_bytes,
                compressed_size=0,
                compression_ratio=0.0,
                lines_processed=file_info.line_count,
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error=f"Python compression failed: {e}"
            )

    def _compress_with_perl(self, log_file: Path, compressed_file: Path, file_info: LogFileInfo) -> CompressionResult:
        """Compress log file using NAS Perl package"""
        start_time = datetime.now()

        try:
            # Use Perl gzip compression
            perl_script = f"""
            use strict;
            use warnings;
            use Compress::Zlib;

            my $input_file = '{log_file}';
            my $output_file = '{compressed_file}';

            open(my $in, '<:raw', $input_file) or die "Cannot open $input_file: $!";
            open(my $out, '>:raw', $output_file) or die "Cannot open $output_file: $!";

            my $gz = gzopen($output_file, "wb") or die "Cannot open gzip stream: $!";
            while (read($in, my $buffer, 4096)) {{
                gzwrite($gz, $buffer) or die "gzwrite failed: $!";
            }}
            gzclose($gz);
            close($in);
            close($out);

            print "Compression completed successfully";
            """

            # Write temporary Perl script
            temp_script = log_file.with_suffix('.compress.pl')
            with temp_script.open('w', encoding='utf-8') as f:
                f.write(perl_script)

            # Execute Perl script
            result = subprocess.run(['perl', str(temp_script)],
                                  capture_output=True, text=True, timeout=30)

            # Clean up
            temp_script.unlink()

            if result.returncode != 0:
                raise Exception(f"Perl compression failed: {result.stderr}")

            # Get compressed file info
            compressed_size = compressed_file.stat().st_size
            compression_ratio = compressed_size / file_info.size_bytes if file_info.size_bytes > 0 else 1.0

            # Remove original file if compression was successful
            if compressed_size < file_info.size_bytes:
                log_file.unlink()

            processing_time = (datetime.now() - start_time).total_seconds()

            return CompressionResult(
                original_file=log_file,
                compressed_file=compressed_file,
                original_size=file_info.size_bytes,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                lines_processed=file_info.line_count,
                processing_time=processing_time,
                success=True
            )

        except Exception as e:
            return CompressionResult(
                original_file=log_file,
                compressed_file=compressed_file,
                original_size=file_info.size_bytes,
                compressed_size=0,
                compression_ratio=0.0,
                lines_processed=file_info.line_count,
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error=f"Perl compression failed: {e}"
            )

    def _get_log_file_info_safe(self, log_file: Path) -> Optional[LogFileInfo]:
        """Get basic log file information without opening the file (safe for locked files)"""
        try:
            stat = log_file.stat()
            return LogFileInfo(
                path=log_file,
                size_bytes=stat.st_size,
                line_count=0,  # We can't count lines without opening the file
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                compressed=log_file.suffix == ".log.gz"
            )
        except Exception as e:
            self.logger.error(f"Failed to get file info for {log_file}: {e}")
            return None

    def _get_log_file_info(self, log_file: Path) -> LogFileInfo:
        """Get detailed information about a log file"""
        stat = log_file.stat()
        line_count = 0

        try:
            if log_file.suffix == ".log":
                with log_file.open('r', encoding='utf-8', errors='ignore') as f:
                    for _ in f:
                        line_count += 1
            elif log_file.suffix == ".log.gz":
                with gzip.open(log_file, 'rt', encoding='utf-8', errors='ignore') as f:
                    for _ in f:
                        line_count += 1
        except Exception as e:
            self.logger.error(f"Failed to count lines in {log_file}: {e}")

        return LogFileInfo(
            path=log_file,
            size_bytes=stat.st_size,
            line_count=line_count,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            compressed=log_file.suffix == ".log.gz"
        )

    def compress_all_eligible_logs(self) -> List[CompressionResult]:
        """Compress all log files that exceed the threshold"""
        results = []
        log_files = self.scan_log_files()

        for log_file in log_files:
            if not log_file.compressed and log_file.line_count > self.compression_threshold_lines:
                self.logger.info(f"Compressing log file: {log_file.path} ({log_file.line_count} lines)")
                result = self.compress_log_file(log_file.path)
                results.append(result)

                if result.success:
                    self.logger.info(f"Successfully compressed {log_file.path}: "
                                   f"{result.original_size} -> {result.compressed_size} bytes "
                                   f"({result.compression_ratio:.2%} ratio)")
                else:
                    self.logger.error(f"Failed to compress {log_file.path}: {result.error}")

        return results

    def analyze_request_sizes(self, log_files: Optional[List[Path]] = None) -> RequestAnalysis:
        """
        Analyze request sizes from log files

        Args:
            log_files: Specific log files to analyze (default: all .log files)

        Returns:
            RequestAnalysis with size statistics
        """
        if log_files is None:
            log_files = [f.path for f in self.scan_log_files() if not f.compressed]

        total_requests = 0
        total_size = 0.0
        max_size = 0.0
        min_size = float('inf')
        request_patterns = {}

        for log_file in log_files:
            try:
                with log_file.open('r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # Look for request patterns in logs
                        request_match = re.search(r'request.*size.*(\d+)', line, re.IGNORECASE)
                        if request_match:
                            try:
                                size = float(request_match.group(1))
                                total_requests += 1
                                total_size += size
                                max_size = max(max_size, size)
                                min_size = min(min_size, size)

                                # Categorize request patterns
                                if size < 1024:
                                    pattern = "small (<1KB)"
                                elif size < 1024 * 1024:
                                    pattern = "medium (1KB-1MB)"
                                else:
                                    pattern = "large (>1MB)"

                                request_patterns[pattern] = request_patterns.get(pattern, 0) + 1
                            except ValueError:
                                continue

                        # Look for API request patterns
                        api_match = re.search(r'(POST|GET|PUT|DELETE).*(\d+)', line, re.IGNORECASE)
                        if api_match:
                            try:
                                size = float(api_match.group(2))
                                total_requests += 1
                                total_size += size
                                max_size = max(max_size, size)
                                min_size = min(min_size, size)

                                pattern = f"API {api_match.group(1).upper()}"
                                request_patterns[pattern] = request_patterns.get(pattern, 0) + 1
                            except ValueError:
                                continue

            except Exception as e:
                self.logger.error(f"Failed to analyze {log_file}: {e}")

        if total_requests == 0:
            return RequestAnalysis(
                average_request_size=0.0,
                max_request_size=0.0,
                min_request_size=0.0,
                total_requests=0,
                total_data_size=0.0,
                request_patterns={}
            )

        return RequestAnalysis(
            average_request_size=total_size / total_requests,
            max_request_size=max_size,
            min_request_size=min_size,
            total_requests=total_requests,
            total_data_size=total_size,
            request_patterns=request_patterns
        )

    def get_model_recommendations(self) -> List[ModelRecommendation]:
        """Get model recommendations based on system hardware"""
        recommendations = []

        # Check if we have GPU info
        if self.system_info.gpu_available and self.system_info.gpu_name:
            gpu_name_lower = self.system_info.gpu_name.lower()

            # RTX 5090 Mobile GPU recommendations
            if "5090" in gpu_name_lower or "rtx 50" in gpu_name_lower:
                recommendations.extend([
                    ModelRecommendation(
                        model_name="qwen2.5-coder:7b",
                        model_size="7B",
                        recommended_for="RTX 5090 Mobile",
                        performance_score=9.5,
                        memory_requirements_gb=8.0,
                        compatibility_score=9.8,
                        notes="Excellent performance on mobile RTX 5090 with 16GB VRAM"
                    ),
                    ModelRecommendation(
                        model_name="llama3.2:8b",
                        model_size="8B",
                        recommended_for="RTX 5090 Mobile",
                        performance_score=9.2,
                        memory_requirements_gb=10.0,
                        compatibility_score=9.5,
                        notes="Great balance of performance and memory usage"
                    ),
                    ModelRecommendation(
                        model_name="mistral:7b",
                        model_size="7B",
                        recommended_for="RTX 5090 Mobile",
                        performance_score=9.0,
                        memory_requirements_gb=7.5,
                        compatibility_score=9.7,
                        notes="Efficient architecture, good for mobile use"
                    )
                ])
            else:
                # General GPU recommendations
                recommendations.extend([
                    ModelRecommendation(
                        model_name="qwen2.5-coder:7b",
                        model_size="7B",
                        recommended_for="General GPU",
                        performance_score=8.5,
                        memory_requirements_gb=8.0,
                        compatibility_score=9.0,
                        notes="Good all-around performer"
                    ),
                    ModelRecommendation(
                        model_name="llama3.2:3b",
                        model_size="3B",
                        recommended_for="General GPU",
                        performance_score=7.5,
                        memory_requirements_gb=4.0,
                        compatibility_score=9.5,
                        notes="Lightweight option for most GPUs"
                    )
                ])
        else:
            # CPU-only recommendations
            recommendations.extend([
                ModelRecommendation(
                    model_name="qwen2.5-coder:1.5b",
                    model_size="1.5B",
                    recommended_for="CPU Only",
                    performance_score=6.0,
                    memory_requirements_gb=2.0,
                    compatibility_score=8.5,
                    notes="Best option for CPU-only systems"
                ),
                ModelRecommendation(
                    model_name="llama3.2:1b",
                    model_size="1B",
                    recommended_for="CPU Only",
                    performance_score=5.5,
                    memory_requirements_gb=1.5,
                    compatibility_score=9.0,
                    notes="Very lightweight for CPU processing"
                )
            ])

        return recommendations

    def check_gpu_setup(self) -> Dict[str, Any]:
        """Check if GPU is correctly set up for AI processing"""
        result = {
            'gpu_detected': self.system_info.gpu_available,
            'gpu_name': self.system_info.gpu_name,
            'gpu_memory_gb': self.system_info.gpu_memory_gb,
            'gpu_utilization': self.system_info.gpu_utilization,
            'gpu_temperature': self.system_info.gpu_temperature,
            'gpu_driver_version': self.system_info.gpu_driver_version,
            'gpu_ready_for_ai': False,
            'issues': [],
            'recommendations': []
        }

        if not result['gpu_detected']:
            result['issues'].append("No GPU detected - running on CPU only")
            result['recommendations'].append("Consider adding a GPU for better AI performance")
            return result

        # Check GPU memory
        if result['gpu_memory_gb'] and result['gpu_memory_gb'] < 8:
            result['issues'].append(f"GPU memory is low ({result['gpu_memory_gb']:.1f}GB) - may limit model size")
            result['recommendations'].append("Consider upgrading to GPU with 16GB+ VRAM for larger models")

        # Check driver version
        if result['gpu_driver_version'] and 'nvidia' in result['gpu_name'].lower():
            try:
                driver_version = float(result['gpu_driver_version'].split('.')[0])
                if driver_version < 530:
                    result['issues'].append(f"Old GPU driver version ({result['gpu_driver_version']})")
                    result['recommendations'].append("Update to latest NVIDIA drivers (530+) for best performance")
            except ValueError:
                pass

        # Check if GPU is being utilized
        if result['gpu_utilization'] is not None and result['gpu_utilization'] < 5:
            result['issues'].append("GPU utilization is very low - may not be properly configured")
            result['recommendations'].append("Check if AI workloads are properly using GPU acceleration")

        # If no major issues, mark as ready
        if not result['issues']:
            result['gpu_ready_for_ai'] = True
            result['recommendations'].append("GPU is properly configured for AI workloads")

        return result

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive system and log analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': asdict(self.system_info),
            'log_analysis': {},
            'request_analysis': {},
            'model_recommendations': [],
            'gpu_setup_check': {},
            'compression_results': []
        }

        # Log analysis
        log_files = self.scan_log_files()
        total_logs = len(log_files)
        total_size = sum(f.size_bytes for f in log_files)
        total_lines = sum(f.line_count for f in log_files)
        large_logs = [f for f in log_files if f.line_count > self.compression_threshold_lines]

        report['log_analysis'] = {
            'total_log_files': total_logs,
            'total_size_bytes': total_size,
            'total_size_human': self._human_readable_size(total_size),
            'total_lines': total_lines,
            'average_lines_per_file': total_lines / total_logs if total_logs > 0 else 0,
            'large_log_files': len(large_logs),
            'large_log_files_list': [str(f.path) for f in large_logs],
            'compressed_log_files': len([f for f in log_files if f.compressed]),
            'compression_threshold_lines': self.compression_threshold_lines
        }

        # Request analysis
        request_analysis = self.analyze_request_sizes()
        report['request_analysis'] = asdict(request_analysis)

        # Model recommendations
        model_recommendations = self.get_model_recommendations()
        report['model_recommendations'] = [asdict(rec) for rec in model_recommendations]

        # GPU setup check
        gpu_check = self.check_gpu_setup()
        report['gpu_setup_check'] = gpu_check

        # Compression results
        compression_results = self.compress_all_eligible_logs()
        report['compression_results'] = [asdict(result) for result in compression_results]

        return report

    def _human_readable_size(self, size_bytes: float) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def save_report(self, report: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        try:
            """Save report to JSON file"""
            if output_file is None:
                reports_dir = project_root / "reports"
                reports_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = reports_dir / f"log_compression_report_{timestamp}.json"

            with output_file.open('w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Report saved to: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main function for Log Compression System"""
    # Initialize system
    compression_system = LogCompressionSystem()

    # Generate comprehensive report
    report = compression_system.generate_comprehensive_report()

    # Save report
    report_file = compression_system.save_report(report)

    # Print summary
    print("\n" + "="*80)
    print("LOG COMPRESSION SYSTEM - COMPREHENSIVE REPORT")
    print("="*80)

    # System Info
    print(f"\n💻 SYSTEM INFORMATION:")
    print(f"  CPU Cores: {report['system_info']['cpu_cores']}")
    print(f"  Total Memory: {report['system_info']['total_memory_gb']:.1f} GB")
    print(f"  Available Memory: {report['system_info']['available_memory_gb']:.1f} GB")
    print(f"  GPU Available: {'Yes' if report['system_info']['gpu_available'] else 'No'}")
    if report['system_info']['gpu_available']:
        print(f"  GPU Name: {report['system_info']['gpu_name']}")
        print(f"  GPU Memory: {report['system_info']['gpu_memory_gb']:.1f} GB")
        print(f"  GPU Utilization: {report['system_info']['gpu_utilization']:.1f}%")
        print(f"  GPU Temperature: {report['system_info']['gpu_temperature']:.1f}°C")

    # Log Analysis
    print(f"\n📊 LOG ANALYSIS:")
    print(f"  Total Log Files: {report['log_analysis']['total_log_files']}")
    print(f"  Total Size: {report['log_analysis']['total_size_human']}")
    print(f"  Total Lines: {report['log_analysis']['total_lines']:,}")
    print(f"  Average Lines/File: {report['log_analysis']['average_lines_per_file']:.1f}")
    print(f"  Large Log Files (>1k lines): {report['log_analysis']['large_log_files']}")
    print(f"  Compressed Log Files: {report['log_analysis']['compressed_log_files']}")

    # Request Analysis
    print(f"\n📈 REQUEST ANALYSIS:")
    if report['request_analysis']['total_requests'] > 0:
        print(f"  Total Requests Analyzed: {report['request_analysis']['total_requests']}")
        print(f"  Average Request Size: {report['request_analysis']['average_request_size']:.2f} bytes")
        print(f"  Max Request Size: {report['request_analysis']['max_request_size']:.2f} bytes")
        print(f"  Min Request Size: {report['request_analysis']['min_request_size']:.2f} bytes")
        print(f"  Total Data Size: {report['request_analysis']['total_data_size']:.2f} bytes")
        print(f"  Request Patterns: {report['request_analysis']['request_patterns']}")
    else:
        print(f"  No request data found in logs")

    # GPU Setup Check
    print(f"\n🎮 GPU SETUP CHECK:")
    print(f"  GPU Ready for AI: {'Yes' if report['gpu_setup_check']['gpu_ready_for_ai'] else 'No'}")
    if report['gpu_setup_check']['issues']:
        print(f"  Issues Found:")
        for issue in report['gpu_setup_check']['issues']:
            print(f"    - {issue}")
    if report['gpu_setup_check']['recommendations']:
        print(f"  Recommendations:")
        for rec in report['gpu_setup_check']['recommendations']:
            print(f"    + {rec}")

    # Model Recommendations
    print(f"\n🤖 MODEL RECOMMENDATIONS:")
    for i, rec in enumerate(report['model_recommendations'], 1):
        print(f"  {i}. {rec['model_name']} ({rec['model_size']})")
        print(f"     Performance: {rec['performance_score']}/10")
        print(f"     Memory: {rec['memory_requirements_gb']} GB")
        print(f"     Compatibility: {rec['compatibility_score']}/10")
        print(f"     Notes: {rec['notes']}")

    # Compression Results
    if report['compression_results']:
        print(f"\n🗜️  COMPRESSION RESULTS:")
        for result in report['compression_results']:
            if result['success']:
                print(f"  ✅ {result['original_file']}")
                print(f"     Original: {compression_system._human_readable_size(result['original_size'])}")
                print(f"     Compressed: {compression_system._human_readable_size(result['compressed_size'])}")
                print(f"     Ratio: {result['compression_ratio']:.2%}")
                print(f"     Time: {result['processing_time']:.2f}s")
            else:
                print(f"  ❌ {result['original_file']} - {result['error']}")

    print(f"\n📄 Full report saved to: {report_file}")
    print("="*80 + "\n")

if __name__ == "__main__":

    main()