#!/usr/bin/env python3
"""
#Syphon Perl Integration

Uses Perl for text processing when available (Perl is the best language for text).
Falls back to Python if Perl is not available.

Tags: #SYPHON #PERL #TEXT_PROCESSING #PYTHON #FALLBACK @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
perl_script = script_dir.parent / "perl" / "syphon_search.pl"
DEFAULT_WSL_DISTRO = os.getenv("SYPHON_WSL_DISTRO", "kali-linux")

try:
    from lumina_core.logging import get_logger
    logger = get_logger("SyphonPerlIntegration")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SyphonPerlIntegration")


def check_wsl_available() -> bool:
    """Check if WSL is available"""
    try:
        result = subprocess.run(
            ['wsl', '--list', '--quiet'],
            capture_output=True,
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_kali_wsl_available() -> bool:
    """Check if the preferred WSL distribution is available"""
    try:
        result = subprocess.run(
            ['wsl', '--list', '--verbose'],
            capture_output=True,
            timeout=5,
            text=False
        )
        if result.returncode == 0:
            decoded = _decode_wsl_output(result.stdout)
            # Check if preferred distro is in the list
            return DEFAULT_WSL_DISTRO.lower() in decoded.lower()
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _decode_wsl_output(output: bytes) -> str:
    """Decode WSL command output safely"""
    try:
        return output.decode("utf-16-le")
    except UnicodeDecodeError:
        return output.decode("utf-8", errors="ignore")


def check_perl_available(use_wsl: bool = False, wsl_distro: Optional[str] = None) -> bool:
    """Check if Perl is available on the system (optionally via WSL)"""
    try:
        if use_wsl and check_wsl_available():
            if wsl_distro:
                # Check Perl in a specific WSL distribution
                result = subprocess.run(
                    ['wsl', '-d', wsl_distro, 'perl', '-v'],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                return result.returncode == 0
            # Check Perl in default WSL
            result = subprocess.run(
                ['wsl', 'perl', '-v'],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
        else:
            # Check Perl natively
            result = subprocess.run(
                ['perl', '-v'],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def syphon_with_perl(
    pattern: str,
    directory: Path,
    max_results: int = 100,
    use_wsl: bool = True
) -> Optional[List[Dict[str, Any]]]:
    """
    Use Perl for text searching (Perl is the best for text processing)
    Can use WSL for native Linux Perl on Windows.

    Args:
        pattern: Regex pattern to search
        directory: Directory to search
        max_results: Maximum results to return
        use_wsl: Use WSL if available (default: True)

    Returns:
        List of matches or None if Perl unavailable
    """
    # Try WSL first if on Windows
    perl_available = False
    use_wsl_perl = False

    # Try preferred WSL distro first
    if use_wsl and check_kali_wsl_available():
        try:
            # Test WSL access (with timeout to avoid hanging)
            test_cmd = subprocess.run(
                ['wsl', '-d', DEFAULT_WSL_DISTRO, 'echo', 'test'],
                capture_output=True,
                timeout=5,
                text=True
            )
            if test_cmd.returncode == 0:
                if check_perl_available(use_wsl=True, wsl_distro=DEFAULT_WSL_DISTRO):
                    perl_available = True
                    use_wsl_perl = True
                    logger.info("Using Perl via %s WSL (hardened Kali Linux)", DEFAULT_WSL_DISTRO)
        except (subprocess.TimeoutExpired, Exception):
            # WSL distro may need initialization
            logger.debug("%s WSL detected but may need initialization", DEFAULT_WSL_DISTRO)

    # Fallback to default WSL if kali-linux not accessible
    if not perl_available and use_wsl and check_wsl_available():
        if check_perl_available(use_wsl=True):
            perl_available = True
            use_wsl_perl = True
            logger.info("Using Perl via default WSL (Linux Perl)")

    # Fallback to native Perl
    if not perl_available:
        if check_perl_available(use_wsl=False):
            perl_available = True
            logger.info("Using native Perl")

    if not perl_available:
        logger.debug("Perl not available, will use Python fallback")
        return None

    # Convert Windows path to WSL path if using WSL
    if use_wsl_perl:
        # Convert Windows path to WSL path (e.g., C:\Users\... -> /mnt/c/Users/...)
        wsl_path = str(directory).replace('\\', '/')
        if wsl_path[1] == ':':
            # Windows drive letter (C: -> /mnt/c)
            drive = wsl_path[0].lower()
            wsl_path = f"/mnt/{drive}{wsl_path[2:]}"

        perl_script_wsl = str(perl_script).replace('\\', '/')
        if perl_script_wsl[1] == ':':
            drive = perl_script_wsl[0].lower()
            perl_script_wsl = f"/mnt/{drive}{perl_script_wsl[2:]}"
    else:
        wsl_path = str(directory)
        perl_script_wsl = str(perl_script)

    if not perl_script.exists():
        logger.warning(f"Perl script not found: {perl_script}")
        return None

    try:
        # Escape pattern for shell
        escaped_pattern = pattern.replace('"', '\\"')

        if use_wsl_perl:
            # Try kali-linux WSL first, fallback to default WSL
            wsl_distro = DEFAULT_WSL_DISTRO if check_kali_wsl_available() else None

            if wsl_distro:
                # Run Perl via kali-linux WSL
                result = subprocess.run(
                    ['wsl', '-d', wsl_distro, 'perl', perl_script_wsl, escaped_pattern, wsl_path, str(max_results)],
                    capture_output=True,
                    timeout=30,
                    text=True,
                    encoding='utf-8'
                )
            else:
                # Run Perl via default WSL
                result = subprocess.run(
                    ['wsl', 'perl', perl_script_wsl, escaped_pattern, wsl_path, str(max_results)],
                    capture_output=True,
                    timeout=30,
                    text=True,
                    encoding='utf-8'
                )
        else:
            # Run Perl natively
            result = subprocess.run(
                ['perl', str(perl_script), escaped_pattern, str(directory), str(max_results)],
                capture_output=True,
                timeout=30,
                text=True,
                encoding='utf-8'
            )

        if result.returncode != 0:
            logger.warning(f"Perl script failed: {result.stderr}")
            return None

        # Parse JSON output
        matches = json.loads(result.stdout)

        # Ensure line numbers are valid int32
        for match in matches:
            if 'line' in match:
                match['line'] = min(match['line'], 2147483647)

        logger.info(f"Perl found {len(matches)} matches")
        return matches

    except subprocess.TimeoutExpired:
        logger.warning("Perl search timed out")
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Perl output: {e}")
        return None
    except Exception as e:
        logger.warning(f"Perl search failed: {e}")
        return None


def syphon_with_python(
    pattern: str,
    directory: Path,
    max_results: int = 100
) -> List[Dict[str, Any]]:
    """
    Python fallback for text searching

    Args:
        pattern: Regex pattern to search
        directory: Directory to search
        max_results: Maximum results to return

    Returns:
        List of matches
    """
    matches = []
    compiled_pattern = re.compile(pattern, re.IGNORECASE)

    file_count = 0
    max_files = 50

    search_dir = directory / "scripts" / "python"
    if not search_dir.exists():
        return matches

    for py_file in search_dir.rglob("*.py"):
        if file_count >= max_files or len(matches) >= max_results:
            break

        try:
            file_size = py_file.stat().st_size
            if file_size > 1_000_000:  # 1MB limit
                continue

            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

                matches_in_file = 0
                max_matches_per_file = 10

                for line_num, line in enumerate(lines, 1):
                    if len(matches) >= max_results:
                        break
                    if matches_in_file >= max_matches_per_file:
                        break
                    if line_num > 2147483647:  # int32 max
                        break

                    if compiled_pattern.search(line):
                        matches.append({
                            "file": str(py_file.relative_to(directory)),
                            "line": line_num,
                            "content": line.strip()[:80],
                            "pattern": pattern
                        })
                        matches_in_file += 1

            file_count += 1
        except Exception as e:
            logger.debug(f"Error processing {py_file}: {e}")
            continue

    return matches[:max_results]


def syphon_search(
    pattern: str,
    directory: Optional[Path] = None,
    max_results: int = 100,
    prefer_perl: bool = True,
    use_wsl: bool = True
) -> List[Dict[str, Any]]:
    """
    Smart #syphon search - uses Perl if available (best for text), Python otherwise
    Can use WSL for native Linux Perl on Windows.

    Args:
        pattern: Regex pattern to search
        directory: Directory to search (defaults to project root)
        max_results: Maximum results to return
        prefer_perl: Prefer Perl if available (default: True)
        use_wsl: Use WSL if available on Windows (default: True)

    Returns:
        List of matches
    """
    if directory is None:
        directory = project_root

    # Try Perl first if preferred (Perl is best for text processing)
    if prefer_perl:
        perl_results = syphon_with_perl(pattern, directory, max_results, use_wsl=use_wsl)
        if perl_results is not None:
            logger.info("✅ Using Perl for text search (best for text processing)")
            return perl_results

    # Fallback to Python
    logger.info("Using Python fallback for text search")
    return syphon_with_python(pattern, directory, max_results)


def syphon_pin_operations(
    project_root: Path,
    max_results: int = 100,
    use_perl: bool = True,
    use_wsl: bool = True
) -> List[Dict[str, Any]]:
    """
    Use #syphon to find all pin-related operations

    Uses Perl if available (best for text processing), Python otherwise.
    Can use WSL for native Linux Perl on Windows.

    Args:
        project_root: Project root directory
        max_results: Maximum number of results
        use_perl: Use Perl if available (default: True)
        use_wsl: Use WSL if available on Windows (default: True)

    Returns:
        List of pin operation locations
    """
    # Search for pin-related patterns
    patterns = [
        (r"\.pin_file\(", "pin_file call"),
        (r"\.unpin_file\(", "unpin_file call"),
        (r"is_pinned", "is_pinned check"),
        (r"pin_reason", "pin_reason usage"),
        (r"auto.*pin", "auto pin pattern"),
        (r"pin.*manager", "pin manager")
    ]

    all_results = []

    for pattern, pattern_name in patterns:
        if len(all_results) >= max_results:
            break

        # Use smart syphon (Perl if available, Python otherwise)
        matches = syphon_search(
            pattern=pattern,
            directory=project_root,
            max_results=max_results - len(all_results),
            prefer_perl=use_perl,
            use_wsl=use_wsl
        )

        # Add pattern name to results
        for match in matches:
            match['pattern'] = pattern_name
            all_results.append(match)

    return all_results[:max_results]


if __name__ == "__main__":
    """Test Perl integration"""

    print("="*80)
    print("🔍 SYPHON PERL INTEGRATION TEST")
    print("="*80)

    # Test WSL availability
    wsl_available = check_wsl_available()
    kali_wsl_available = check_kali_wsl_available()

    print(f"WSL Available: {wsl_available}")
    print(f"Kali Linux WSL Available: {kali_wsl_available}")
    print(f"Preferred WSL Distro: {DEFAULT_WSL_DISTRO}")

    # Test Perl availability (native and WSL)
    perl_native = check_perl_available(use_wsl=False)
    if kali_wsl_available:
        perl_wsl = check_perl_available(use_wsl=True, wsl_distro=DEFAULT_WSL_DISTRO)
    else:
        perl_wsl = check_perl_available(use_wsl=True) if wsl_available else False

    print(f"Perl (Native): {perl_native}")
    if kali_wsl_available:
        print(f"Perl ({DEFAULT_WSL_DISTRO} WSL): {perl_wsl}")
    elif wsl_available:
        print(f"Perl (Default WSL): {perl_wsl}")

    if kali_wsl_available and perl_wsl:
        print(f"✅ Perl via {DEFAULT_WSL_DISTRO} WSL detected - will use hardened Kali Linux Perl (best for text)")
    elif perl_wsl:
        print("✅ Perl via WSL detected - will use native Linux Perl (best for text)")
    elif perl_native:
        print("✅ Native Perl detected - will use Perl for text processing (best for text)")
    else:
        print("⚠️  Perl not available - will use Python fallback")
        if kali_wsl_available:
            print(f"   💡 Tip: Initialize {DEFAULT_WSL_DISTRO} WSL and install Perl:")
            print(f"      wsl -d {DEFAULT_WSL_DISTRO}")
            print("      sudo apt-get update && sudo apt-get install -y perl")

    print()

    # Test search
    results = syphon_pin_operations(
        project_root=project_root,
        max_results=10,
        use_perl=True,
        use_wsl=True
    )

    print(f"Found {len(results)} pin-related operations")
    for result in results[:5]:
        print(f"  {result['file']}:{result['line']} - {result['content'][:60]}...")

    print("\n" + "="*80)
    print("✅ SYPHON PERL INTEGRATION TEST COMPLETE")
    print("="*80)
