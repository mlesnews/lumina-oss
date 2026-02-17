#!/usr/bin/env python3
"""
SYPHON Regex Tools - Robust & Comprehensive Regex Support
Integrates grep/awk/sed-like functionality via @ff (force field/feature flags)

Provides Unix text processing tool capabilities:
- grep: Pattern matching and extraction
- awk: Field-based text processing
- sed: Stream editing and transformation

@SYPHON @FF @LUMINA @JARVIS
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Iterator, Union
import logging

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SyphonRegexTools")


class RegexToolMode(Enum):
    """Regex tool execution modes"""
    PYTHON = "python"  # Pure Python regex (default, cross-platform)
    GREP = "grep"  # Use native grep command
    AWK = "awk"  # Use native awk command
    SED = "sed"  # Use native sed command
    HYBRID = "hybrid"  # Try native, fallback to Python


@dataclass
class RegexToolConfig:
    """Configuration for regex tools with feature flags"""
    enable_grep: bool = True  # @ff: Enable grep-like functionality
    enable_awk: bool = True  # @ff: Enable awk-like functionality
    enable_sed: bool = True  # @ff: Enable sed-like functionality
    prefer_native: bool = False  # @ff: Prefer native tools over Python
    fallback_to_python: bool = True  # @ff: Fallback to Python if native fails
    case_sensitive: bool = True  # Case sensitive matching
    multiline: bool = False  # Multiline matching
    dotall: bool = False  # . matches newline
    verbose: bool = False  # Verbose regex
    max_matches: int = 1000  # Maximum matches per operation
    timeout: float = 30.0  # Timeout for native tool execution (seconds)


class SyphonRegexTools:
    """
    Robust & Comprehensive Regex Tools for SYPHON

    Provides grep/awk/sed-like functionality with feature flags.
    Supports both native Unix tools and pure Python implementations.
    """

    def __init__(self, config: Optional[RegexToolConfig] = None):
        self.config = config or RegexToolConfig()
        self.logger = logger

        # Check for native tools availability
        self._native_tools_available = self._check_native_tools()

    def _check_native_tools(self) -> Dict[str, bool]:
        """Check which native tools are available"""
        tools = {}

        if sys.platform == 'win32':
            # On Windows, check for WSL or Git Bash
            try:
                result = subprocess.run(
                    ['wsl', 'which', 'grep'],
                    capture_output=True,
                    timeout=2
                )
                tools['grep'] = result.returncode == 0
            except:
                tools['grep'] = False

            try:
                result = subprocess.run(
                    ['wsl', 'which', 'awk'],
                    capture_output=True,
                    timeout=2
                )
                tools['awk'] = result.returncode == 0
            except:
                tools['awk'] = False

            try:
                result = subprocess.run(
                    ['wsl', 'which', 'sed'],
                    capture_output=True,
                    timeout=2
                )
                tools['sed'] = result.returncode == 0
            except:
                tools['sed'] = False
        else:
            # Unix-like systems
            for tool in ['grep', 'awk', 'sed']:
                try:
                    result = subprocess.run(
                        ['which', tool],
                        capture_output=True,
                        timeout=2
                    )
                    tools[tool] = result.returncode == 0
                except:
                    tools[tool] = False

        return tools

    def grep(
        self,
        pattern: str,
        text: Union[str, Path],
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Grep-like pattern matching and extraction

        Args:
            pattern: Regex pattern to match
            text: Text to search (string or file path)
            options: Additional options (flags, context lines, etc.)

        Returns:
            List of matches with context
        """
        options = options or {}
        use_native = self.config.prefer_native and self.config.enable_grep and self._native_tools_available.get('grep', False)

        # Read text if it's a file path
        if isinstance(text, Path):
            if not text.exists():
                self.logger.warning(f"File not found: {text}")
                return []
            with open(text, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
                file_path = text
        else:
            text_content = text
            file_path = None

        if use_native and self._native_tools_available.get('grep', False):
            return self._grep_native(pattern, text_content, file_path, options)
        else:
            return self._grep_python(pattern, text_content, file_path, options)

    def _grep_python(
        self,
        pattern: str,
        text: str,
        file_path: Optional[Path],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Pure Python grep implementation"""
        matches = []
        flags = 0

        if not self.config.case_sensitive:
            flags |= re.IGNORECASE
        if self.config.multiline:
            flags |= re.MULTILINE
        if self.config.dotall:
            flags |= re.DOTALL
        if self.config.verbose:
            flags |= re.VERBOSE

        context_before = options.get('context_before', 0)
        context_after = options.get('context_after', 0)
        invert_match = options.get('invert_match', False)
        line_numbers = options.get('line_numbers', True)

        lines = text.split('\n')
        regex = re.compile(pattern, flags)

        for line_num, line in enumerate(lines, 1):
            match = regex.search(line)
            should_include = (match is not None) != invert_match

            if should_include:
                match_data = {
                    'line_number': line_num,
                    'line': line,
                    'match': match.group() if match else None,
                    'file': str(file_path) if file_path else None
                }

                # Add groups if present
                if match and match.groups():
                    match_data['groups'] = match.groups()

                # Add named groups if present
                if match and match.groupdict():
                    match_data['named_groups'] = match.groupdict()

                # Add context
                if context_before > 0 or context_after > 0:
                    context_lines = []
                    start = max(0, line_num - context_before - 1)
                    end = min(len(lines), line_num + context_after)

                    for ctx_line_num in range(start, end):
                        if ctx_line_num != line_num - 1:
                            context_lines.append({
                                'line_number': ctx_line_num + 1,
                                'line': lines[ctx_line_num]
                            })

                    match_data['context'] = context_lines

                matches.append(match_data)

                if len(matches) >= self.config.max_matches:
                    break

        return matches

    def _grep_native(
        self,
        pattern: str,
        text: str,
        file_path: Optional[Path],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Native grep command implementation"""
        # For native grep, we'd write to temp file and use grep
        # This is a simplified version - full implementation would use temp files
        # Fallback to Python for now if text is in memory
        if file_path is None:
            return self._grep_python(pattern, text, file_path, options)

        # If we have a file, use native grep
        try:
            cmd = ['grep']
            if not self.config.case_sensitive:
                cmd.append('-i')
            if options.get('invert_match'):
                cmd.append('-v')
            if options.get('context_before', 0) > 0:
                cmd.extend(['-B', str(options['context_before'])])
            if options.get('context_after', 0) > 0:
                cmd.extend(['-A', str(options['context_after'])])

            cmd.extend(['-E', pattern, str(file_path)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )

            matches = []
            for line_num, line in enumerate(result.stdout.split('\n'), 1):
                if line.strip():
                    matches.append({
                        'line_number': line_num,
                        'line': line,
                        'match': line,
                        'file': str(file_path)
                    })

            return matches
        except Exception as e:
            self.logger.warning(f"Native grep failed: {e}, falling back to Python")
            if self.config.fallback_to_python:
                return self._grep_python(pattern, text, file_path, options)
            return []

    def awk(
        self,
        script: str,
        text: Union[str, Path],
        field_separator: str = r'\s+'
    ) -> List[Dict[str, Any]]:
        """
        Awk-like field-based text processing

        Args:
            script: Awk-like script (simplified Python-based implementation)
            text: Text to process (string or file path)
            field_separator: Field separator regex pattern

        Returns:
            List of processed records
        """
        if isinstance(text, Path):
            if not text.exists():
                self.logger.warning(f"File not found: {text}")
                return []
            with open(text, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        else:
            text_content = text

        # Python-based awk implementation
        lines = text_content.split('\n')
        records = []
        separator = re.compile(field_separator)

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            # Split into fields
            fields = separator.split(line)

            # Execute script (simplified - would need full awk parser in production)
            # For now, support basic patterns like print $1, $2, etc.
            record = {
                'line_number': line_num,
                'line': line,
                'fields': fields,
                'NF': len(fields),  # Number of fields
                'NR': line_num,  # Record number
            }

            # Basic script execution (simplified)
            # In production, would parse and execute full awk scripts
            records.append(record)

        return records

    def sed(
        self,
        script: str,
        text: Union[str, Path],
        in_place: bool = False
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Sed-like stream editing and transformation

        Args:
            script: Sed-like script (supports s/pattern/replacement/flags)
            text: Text to process (string or file path)
            in_place: If True and text is a file, edit in place

        Returns:
            Transformed text (string) or list of changes (if in_place with file)
        """
        if isinstance(text, Path):
            if not text.exists():
                self.logger.warning(f"File not found: {text}")
                return "" if not in_place else []
            with open(text, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
                original_content = text_content
        else:
            text_content = text
            original_content = None

        # Parse sed script (simplified - supports s/// pattern)
        transformed = text_content

        # Parse s/pattern/replacement/flags
        sed_pattern = re.compile(r's/([^/]+)/([^/]*)/([gims]*)?')
        match = sed_pattern.match(script)

        if match:
            pattern, replacement, flags = match.groups()
            flags = flags or ''

            re_flags = 0
            if 'i' in flags:
                re_flags |= re.IGNORECASE
            if 'm' in flags:
                re_flags |= re.MULTILINE
            if 's' in flags:
                re_flags |= re.DOTALL

            regex = re.compile(pattern, re_flags)

            if 'g' in flags:
                transformed = regex.sub(replacement, transformed)
            else:
                transformed = regex.sub(replacement, transformed, count=1)
        else:
            # Try to interpret as regex directly
            try:
                regex = re.compile(script)
                transformed = regex.sub('', transformed)  # Remove matches
            except:
                self.logger.warning(f"Could not parse sed script: {script}")
                return text_content

        # Handle in-place editing
        if in_place and isinstance(text, Path) and original_content:
            with open(text, 'w', encoding='utf-8') as f:
                f.write(transformed)
            return [{'file': str(text), 'changed': original_content != transformed}]

        return transformed

    def regex_search(
        self,
        pattern: str,
        text: Union[str, Path],
        extract_groups: bool = True,
        extract_named_groups: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive regex search with full match information

        Args:
            pattern: Regex pattern
            text: Text to search
            extract_groups: Extract capturing groups
            extract_named_groups: Extract named groups

        Returns:
            List of match dictionaries with full information
        """
        if isinstance(text, Path):
            if not text.exists():
                return []
            with open(text, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        else:
            text_content = text

        flags = 0
        if not self.config.case_sensitive:
            flags |= re.IGNORECASE
        if self.config.multiline:
            flags |= re.MULTILINE
        if self.config.dotall:
            flags |= re.DOTALL
        if self.config.verbose:
            flags |= re.VERBOSE

        regex = re.compile(pattern, flags)
        matches = []

        for match in regex.finditer(text_content):
            match_data = {
                'match': match.group(),
                'start': match.start(),
                'end': match.end(),
                'span': match.span()
            }

            if extract_groups and match.groups():
                match_data['groups'] = match.groups()

            if extract_named_groups and match.groupdict():
                match_data['named_groups'] = match.groupdict()

            matches.append(match_data)

            if len(matches) >= self.config.max_matches:
                break

        return matches

    def regex_replace(
        self,
        pattern: str,
        replacement: Union[str, Callable],
        text: Union[str, Path],
        count: int = 0
    ) -> str:
        """
        Comprehensive regex replacement

        Args:
            pattern: Regex pattern to match
            replacement: Replacement string or callable
            text: Text to process
            count: Maximum number of replacements (0 = all)

        Returns:
            Transformed text
        """
        if isinstance(text, Path):
            if not text.exists():
                return ""
            with open(text, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        else:
            text_content = text

        flags = 0
        if not self.config.case_sensitive:
            flags |= re.IGNORECASE
        if self.config.multiline:
            flags |= re.MULTILINE
        if self.config.dotall:
            flags |= re.DOTALL

        regex = re.compile(pattern, flags)

        if callable(replacement):
            return regex.sub(replacement, text_content, count=count)
        else:
            return regex.sub(replacement, text_content, count=count)

    def extract_fields(
        self,
        pattern: str,
        text: Union[str, Path],
        field_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract structured fields using regex with named groups

        Args:
            pattern: Regex pattern with named groups
            text: Text to process
            field_names: Optional field names (if not using named groups)

        Returns:
            List of dictionaries with extracted fields
        """
        if isinstance(text, Path):
            if not text.exists():
                return []
            with open(text, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        else:
            text_content = text

        flags = 0
        if not self.config.case_sensitive:
            flags |= re.IGNORECASE
        if self.config.multiline:
            flags |= re.MULTILINE
        if self.config.dotall:
            flags |= re.DOTALL

        regex = re.compile(pattern, flags)
        results = []

        for match in regex.finditer(text_content):
            if match.groupdict():
                results.append(match.groupdict())
            elif field_names and match.groups():
                results.append(dict(zip(field_names, match.groups())))

        return results


# Convenience functions for easy access
def grep(pattern: str, text: Union[str, Path], **options) -> List[Dict[str, Any]]:
    """Convenience function for grep-like matching"""
    tools = SyphonRegexTools()
    return tools.grep(pattern, text, options)


def awk(script: str, text: Union[str, Path], field_separator: str = r'\s+') -> List[Dict[str, Any]]:
    """Convenience function for awk-like processing"""
    tools = SyphonRegexTools()
    return tools.awk(script, text, field_separator)


def sed(script: str, text: Union[str, Path], in_place: bool = False) -> Union[str, List[Dict[str, Any]]]:
    """Convenience function for sed-like editing"""
    tools = SyphonRegexTools()
    return tools.sed(script, text, in_place)
