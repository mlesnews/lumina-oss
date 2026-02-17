#!/usr/bin/env python3
"""
🔧 **Kilo Code Assistant Bridge**

Integration bridge for Kilo Code - Advanced Python-focused coding assistant.
Provides intelligent code completion, generation, and analysis with attribution tracking.

Features:
- Python-optimized code completion
- Context-aware suggestions
- Performance benchmarking
- Attribution compliance

@V3_WORKFLOWED: True
@TEST_FIRST: True
@PYTHON_OPTIMIZED: True
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Local imports
script_dir = Path(__file__).parent.parent.parent.parent.parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("KiloCodeBridge")


@dataclass
class CodeSuggestion:
    """Code suggestion with metadata"""
    code: str
    confidence: float
    reasoning: str
    language: str
    context_type: str
    line_number: Optional[int] = None
    indentation_level: int = 0


@dataclass
class CodeAnalysis:
    """Code analysis result"""
    issues: List[Dict[str, Any]]
    suggestions: List[CodeSuggestion]
    quality_score: float
    complexity_score: float
    readability_score: float


class KiloCodeBridge:
    """
    Bridge to Kilo Code Assistant - Specialized for Python development.

    Kilo Code provides intelligent coding assistance with:
    - Context-aware code completion
    - Python-specific optimizations
    - Quality analysis and suggestions
    - Performance benchmarking
    """

    def __init__(self):
        self.name = "kilo_code"
        self.version = "1.0.0"
        self.capabilities = [
            "code_completion",
            "code_generation",
            "code_analysis",
            "python_optimization",
            "debugging_assistance"
        ]

        # Attribution engine (will be set by framework)
        self.attribution_engine = None

        # Performance tracking
        self.request_count = 0
        self.success_count = 0
        self.average_latency = 0.0

        # Python-specific patterns
        self.python_patterns = {
            'function_def': re.compile(r'def\s+(\w+)\s*\([^)]*\)\s*:'),
            'class_def': re.compile(r'class\s+(\w+)[\s\(:]'),
            'import_statement': re.compile(r'^(?:from\s+[\w.]+\s+)?import\s+[\w.,\s]+'),
            'list_comprehension': re.compile(r'\[.*for.*in.*\]'),
            'dict_comprehension': re.compile(r'\{.*for.*in.*\}'),
            'async_function': re.compile(r'async\s+def\s+(\w+)'),
        }

        logger.info("✅ Kilo Code Bridge initialized")

    async def initialize(self):
        """Initialize the Kilo Code bridge"""
        logger.info("   🚀 Initializing Kilo Code assistant...")

        # Load Python-specific models/training data
        await self._load_python_models()

        # Initialize performance monitoring
        self._init_performance_monitoring()

        logger.info("   ✅ Kilo Code assistant ready")

    async def _load_python_models(self):
        """Verify LLM endpoint availability for code generation."""
        logger.debug("   Checking LLM endpoint for code generation...")

        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("http://localhost:8080/health")
                if resp.status_code == 200:
                    self._llm_available = True
                    logger.debug("   LLM gateway available for code generation")
                else:
                    self._llm_available = False
                    logger.debug("   LLM gateway returned non-200, using template fallback")
        except Exception:
            self._llm_available = False
            logger.debug("   LLM gateway not reachable, using template fallback")

    def _init_performance_monitoring(self):
        """Initialize performance monitoring"""
        logger.debug("   📊 Initializing performance monitoring...")

        # Set up performance tracking
        self.performance_metrics = {
            'requests_processed': 0,
            'average_response_time': 0.0,
            'success_rate': 0.0,
            'quality_score': 0.0
        }

    async def process_request(self, request: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a coding assistance request

        Args:
            request: Request dictionary with capability, code, context, etc.
            context: Additional context information

        Returns:
            Response dictionary with results and attribution
        """

        capability = request.get('capability', 'code_completion')
        code_context = request.get('code', '')
        language = request.get('language', 'python')
        user_id = request.get('user_id', 'anonymous')

        logger.debug(f"   🔧 Processing {capability} request for {language}")

        start_time = asyncio.get_event_loop().time()

        try:
            # Route to appropriate handler
            if capability == 'code_completion':
                result = await self._handle_code_completion(code_context, context or {})
            elif capability == 'code_generation':
                result = await self._handle_code_generation(request, context or {})
            elif capability == 'code_analysis':
                result = await self._handle_code_analysis(code_context, context or {})
            else:
                result = await self._handle_generic_request(request, context or {})

            # Calculate latency
            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000

            # Record attribution
            if self.attribution_engine:
                attribution_record = self.attribution_engine.record_usage(
                    extension=self.name,
                    capability=capability,
                    user_id=user_id,
                    quality_score=result.get('quality_score', result.get('confidence', 0.0)),
                    usage_context=f"{language}:{capability}",
                    latency_ms=latency_ms
                )

                # Add attribution to result
                result['attribution'] = {
                    'text': attribution_record.attribution_text,
                    'extension': self.name,
                    'capability': capability
                }

            # Update performance metrics
            self._update_performance_metrics(True, latency_ms, result.get('quality_score', 0.8))

            result['success'] = True
            result['latency_ms'] = latency_ms
            result['extension'] = self.name

            return result

        except Exception as e:
            # Record failure
            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000

            self._update_performance_metrics(False, latency_ms, 0.0)

            logger.error(f"   ❌ Kilo Code request failed: {e}")

            return {
                'success': False,
                'error': str(e),
                'extension': self.name,
                'capability': capability,
                'latency_ms': latency_ms
            }

    async def _handle_code_completion(self, code_context: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code completion requests"""

        # Analyze the code context
        context_analysis = self._analyze_code_context(code_context)

        # Generate completion suggestions
        suggestions = await self._generate_completion_suggestions(code_context, context_analysis)

        # Filter and rank suggestions
        filtered_suggestions = self._filter_suggestions(suggestions, context)

        result = {
            'suggestions': [s.__dict__ for s in filtered_suggestions],
            'context_analysis': context_analysis,
            'quality_score': self._calculate_completion_quality(filtered_suggestions),
            'confidence': max([s.confidence for s in filtered_suggestions]) if filtered_suggestions else 0.0
        }

        return result

    async def _handle_code_generation(self, request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code generation requests"""

        description = request.get('description', '')
        template = request.get('template', 'function')
        language = request.get('language', 'python')

        # Generate code based on description
        generated_code = await self._generate_code_from_description(description, template, language)

        # Analyze generated code
        analysis = await self._analyze_generated_code(generated_code)

        result = {
            'generated_code': generated_code,
            'analysis': analysis.__dict__ if analysis else None,
            'quality_score': analysis.quality_score if analysis else 0.7,
            'confidence': 0.85  # Base confidence for generation
        }

        return result

    async def _handle_code_analysis(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code analysis requests"""

        analysis = await self._analyze_code(code, context)

        result = {
            'analysis': analysis.__dict__,
            'issues_count': len(analysis.issues),
            'suggestions_count': len(analysis.suggestions),
            'quality_score': analysis.quality_score,
            'complexity_score': analysis.complexity_score,
            'readability_score': analysis.readability_score
        }

        return result

    async def _handle_generic_request(self, request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic coding assistance requests"""

        # Provide general coding assistance
        capability = request.get('capability', 'general')

        assistance = {
            'type': 'general_assistance',
            'capability': capability,
            'suggestions': [
                "Consider using type hints for better code clarity",
                "Implement proper error handling",
                "Add docstrings to functions and classes",
                "Use meaningful variable names"
            ],
            'quality_score': 0.6,
            'confidence': 0.7
        }

        return assistance

    def _analyze_code_context(self, code_context: str) -> Dict[str, Any]:
        """Analyze the code context to understand what kind of completion is needed"""

        analysis = {
            'language': 'python',
            'context_type': 'unknown',
            'indentation_level': 0,
            'in_function': False,
            'in_class': False,
            'imports': [],
            'variables': [],
            'last_line': '',
            'cursor_position': len(code_context)
        }

        if not code_context.strip():
            analysis['context_type'] = 'empty'
            return analysis

        lines = code_context.split('\n')
        analysis['last_line'] = lines[-1] if lines else ''

        # Count indentation
        if lines:
            last_line = lines[-1]
            analysis['indentation_level'] = len(last_line) - len(last_line.lstrip())

        # Check context patterns
        full_code = code_context

        # Check if we're in a function
        if re.search(r'def\s+\w+\s*\(', full_code):
            analysis['in_function'] = True
            analysis['context_type'] = 'function_body'

        # Check if we're in a class
        if re.search(r'class\s+\w+', full_code):
            analysis['in_class'] = True
            if not analysis['in_function']:
                analysis['context_type'] = 'class_body'

        # Check for imports
        import_matches = self.python_patterns['import_statement'].findall(full_code)
        analysis['imports'] = import_matches

        # Determine context type based on last line
        last_line = analysis['last_line'].strip()
        if not last_line:
            analysis['context_type'] = 'new_line'
        elif last_line.endswith(':'):
            analysis['context_type'] = 'block_start'
        elif '=' in last_line and not last_line.endswith('='):
            analysis['context_type'] = 'assignment'
        elif last_line.startswith('def '):
            analysis['context_type'] = 'function_definition'
        elif last_line.startswith('class '):
            analysis['context_type'] = 'class_definition'
        elif last_line.startswith('import ') or last_line.startswith('from '):
            analysis['context_type'] = 'import_statement'
        else:
            analysis['context_type'] = 'statement'

        return analysis

    async def _generate_completion_suggestions(self, code_context: str,
                                             context_analysis: Dict[str, Any]) -> List[CodeSuggestion]:
        """Generate code completion suggestions"""

        suggestions = []

        context_type = context_analysis.get('context_type', 'unknown')

        if context_type == 'function_definition':
            # Suggest function body
            suggestions.append(CodeSuggestion(
                code='\n    """Function docstring"""\n    pass',
                confidence=0.9,
                reasoning="Complete function definition with docstring and pass statement",
                language='python',
                context_type='function_completion',
                indentation_level=context_analysis.get('indentation_level', 0)
            ))

        elif context_type == 'class_definition':
            # Suggest class body
            suggestions.append(CodeSuggestion(
                code='\n    def __init__(self):\n        pass',
                confidence=0.85,
                reasoning="Add constructor method to class",
                language='python',
                context_type='class_completion',
                indentation_level=context_analysis.get('indentation_level', 0)
            ))

        elif context_type == 'assignment':
            # Suggest common assignment patterns
            suggestions.extend([
                CodeSuggestion(
                    code=' = []',
                    confidence=0.8,
                    reasoning="Initialize empty list",
                    language='python',
                    context_type='assignment_completion'
                ),
                CodeSuggestion(
                    code=' = {}',
                    confidence=0.8,
                    reasoning="Initialize empty dictionary",
                    language='python',
                    context_type='assignment_completion'
                ),
                CodeSuggestion(
                    code=' = None',
                    confidence=0.7,
                    reasoning="Initialize with None",
                    language='python',
                    context_type='assignment_completion'
                )
            ])

        elif context_type in ['new_line', 'statement']:
            # Suggest common Python statements
            suggestions.extend([
                CodeSuggestion(
                    code='print(f"")',
                    confidence=0.75,
                    reasoning="Add debug print statement",
                    language='python',
                    context_type='statement_suggestion'
                ),
                CodeSuggestion(
                    code='if __name__ == "__main__":',
                    confidence=0.7,
                    reasoning="Add main guard",
                    language='python',
                    context_type='statement_suggestion'
                )
            ])

        # Add import suggestions if no imports detected
        if not context_analysis.get('imports') and len(code_context.strip()) < 100:
            suggestions.append(CodeSuggestion(
                code='import os\nimport sys\n',
                confidence=0.6,
                reasoning="Add common imports",
                language='python',
                context_type='import_suggestion'
            ))

        return suggestions

    async def _generate_code_from_description(self, description: str, template: str, language: str) -> str:
        """Generate code from natural language description using local LLM.

        Sends the description to the LiteLLM gateway for real code generation.
        Falls back to template scaffolding if the LLM is unavailable.
        """
        # Try LLM-powered generation first
        try:
            import httpx

            system_prompt = (
                f"You are an expert {language} developer. Generate clean, production-ready "
                f"{language} code based on the user's description. "
                f"The code should be a {template} (function, class, or module). "
                "Include proper docstrings, type hints, and error handling. "
                "Return ONLY the code, no explanations or markdown fences."
            )

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "http://localhost:8080/v1/chat/completions",
                    json={
                        "model": "ollama/qwen2.5-coder:7b",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": description},
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1000,
                    },
                )
                if resp.status_code == 200:
                    code = resp.json()["choices"][0]["message"]["content"]
                    # Strip markdown fences if the model included them
                    code = re.sub(r'^```\w*\n', '', code)
                    code = re.sub(r'\n```$', '', code)
                    return code.strip()

        except Exception as e:
            logger.debug(f"LLM code generation unavailable ({e}), using template fallback")

        # Fallback: structural template without TODO stubs
        if template == 'function':
            func_name = self._extract_function_name(description)
            return (
                f'def {func_name}(*args, **kwargs):\n'
                f'    """{description}"""\n'
                f'    raise NotImplementedError("{func_name} requires implementation")\n'
            )
        elif template == 'class':
            class_name = self._extract_class_name(description)
            return (
                f'class {class_name}:\n'
                f'    """{description}"""\n'
                f'\n'
                f'    def __init__(self):\n'
                f'        raise NotImplementedError("{class_name} requires implementation")\n'
            )
        else:
            return (
                f'def process(*args, **kwargs):\n'
                f'    """{description}"""\n'
                f'    raise NotImplementedError("Requires implementation")\n'
            )

    def _extract_function_name(self, description: str) -> str:
        """Extract function name from description"""
        # Simple extraction - look for verbs
        words = description.lower().split()
        verbs = ['calculate', 'get', 'process', 'create', 'find', 'convert', 'validate']

        for word in words:
            if word in verbs:
                return f"{word}_data"

        return "process_data"

    def _extract_class_name(self, description: str) -> str:
        """Extract class name from description"""
        # Look for nouns that could be class names
        words = description.title().split()
        nouns = [word for word in words if len(word) > 3]

        if nouns:
            return nouns[0]

        return "DataProcessor"

    async def _analyze_generated_code(self, code: str) -> CodeAnalysis:
        """Analyze generated code quality"""

        issues = []
        suggestions = []

        # Basic quality checks
        lines = code.split('\n')

        # Check for TODO comments
        if 'TODO' in code:
            issues.append({
                'type': 'incomplete',
                'severity': 'medium',
                'message': 'Code contains TODO comments indicating incomplete implementation'
            })

        # Check line length
        long_lines = [i for i, line in enumerate(lines) if len(line) > 88]
        if long_lines:
            issues.append({
                'type': 'style',
                'severity': 'low',
                'message': f'Found {len(long_lines)} lines longer than 88 characters'
            })

        # Check for docstrings
        if 'def ' in code and '"""' not in code:
            suggestions.append(CodeSuggestion(
                code='    """Function docstring"""',
                confidence=0.8,
                reasoning="Add docstring to function",
                language='python',
                context_type='documentation'
            ))

        # Calculate quality scores
        quality_score = 0.8  # Base quality
        if issues:
            quality_score -= len(issues) * 0.1
        if suggestions:
            quality_score += 0.1

        complexity_score = min(1.0, len(lines) / 50)  # Simple complexity measure
        readability_score = 0.7  # Basic readability score

        return CodeAnalysis(
            issues=issues,
            suggestions=suggestions,
            quality_score=max(0.0, min(1.0, quality_score)),
            complexity_score=complexity_score,
            readability_score=readability_score
        )

    async def _analyze_code(self, code: str, context: Dict[str, Any]) -> CodeAnalysis:
        """Perform comprehensive code analysis"""

        issues = []
        suggestions = []

        # Run various checks
        issues.extend(self._check_code_style(code))
        issues.extend(self._check_potential_bugs(code))
        issues.extend(self._check_performance_issues(code))

        suggestions.extend(await self._generate_improvement_suggestions(code))

        # Calculate scores
        quality_score = self._calculate_overall_quality(code, issues)
        complexity_score = self._calculate_complexity(code)
        readability_score = self._calculate_readability(code)

        return CodeAnalysis(
            issues=issues,
            suggestions=suggestions,
            quality_score=quality_score,
            complexity_score=complexity_score,
            readability_score=readability_score
        )

    def _check_code_style(self, code: str) -> List[Dict[str, Any]]:
        """Check code style issues"""
        issues = []

        # Check line length
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 88:
                issues.append({
                    'type': 'style',
                    'severity': 'low',
                    'line': i + 1,
                    'message': f'Line too long ({len(line)} > 88 characters)'
                })

        # Check for unused imports (simplified check)
        import_lines = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
        if len(import_lines) > 10:
            issues.append({
                'type': 'style',
                'severity': 'medium',
                'message': 'Many imports detected - consider organizing imports'
            })

        return issues

    def _check_potential_bugs(self, code: str) -> List[Dict[str, Any]]:
        """Check for potential bugs"""
        issues = []

        # Check for bare except clauses
        if 'except:' in code:
            issues.append({
                'type': 'bug',
                'severity': 'high',
                'message': 'Bare except clause found - too broad exception handling'
            })

        # Check for print statements in production code
        if 'print(' in code and 'if __name__' not in code:
            issues.append({
                'type': 'bug',
                'severity': 'medium',
                'message': 'Print statements found outside main guard - consider using logging'
            })

        return issues

    def _check_performance_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for performance issues"""
        issues = []

        # Check for inefficient list operations
        if '+=' in code and '[' in code:
            issues.append({
                'type': 'performance',
                'severity': 'low',
                'message': 'Consider using list.extend() instead of += for better performance'
            })

        return issues

    async def _generate_improvement_suggestions(self, code: str) -> List[CodeSuggestion]:
        """Generate improvement suggestions"""
        suggestions = []

        # Suggest type hints if not present
        if 'def ' in code and '->' not in code:
            suggestions.append(CodeSuggestion(
                code=' -> None',
                confidence=0.7,
                reasoning="Add return type annotation",
                language='python',
                context_type='type_hint'
            ))

        # Suggest error handling
        if 'try:' not in code and ('open(' in code or 'requests.' in code):
            suggestions.append(CodeSuggestion(
                code='try:\n    # Code here\nexcept Exception as e:\n    print(f"Error: {e}")',
                confidence=0.8,
                reasoning="Add error handling for I/O operations",
                language='python',
                context_type='error_handling'
            ))

        return suggestions

    def _calculate_overall_quality(self, code: str, issues: List[Dict]) -> float:
        """Calculate overall code quality score"""
        base_score = 0.8

        # Penalize for issues
        severity_weights = {'high': 0.3, 'medium': 0.2, 'low': 0.1}
        for issue in issues:
            severity = issue.get('severity', 'low')
            base_score -= severity_weights.get(severity, 0.1)

        return max(0.0, min(1.0, base_score))

    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity score"""
        lines = len(code.split('\n'))
        functions = len(re.findall(r'def\s+', code))
        classes = len(re.findall(r'class\s+', code))

        # Simple complexity formula
        complexity = min(1.0, (lines / 200) + (functions / 10) + (classes / 5))

        return complexity

    def _calculate_readability(self, code: str) -> float:
        """Calculate code readability score"""
        # Simple readability metrics
        lines = code.split('\n')

        # Average line length
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0

        # Comment ratio
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        comment_ratio = comment_lines / len(lines) if lines else 0

        # Readability score based on line length and comments
        length_score = max(0, 1 - (avg_line_length - 50) / 50)  # Prefer ~50 chars
        comment_score = min(1.0, comment_ratio * 5)  # Prefer some comments

        readability = (length_score + comment_score) / 2

        return max(0.0, min(1.0, readability))

    def _filter_suggestions(self, suggestions: List[CodeSuggestion],
                          context: Dict[str, Any]) -> List[CodeSuggestion]:
        """Filter and rank suggestions based on context"""

        # Sort by confidence
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        # Limit to top suggestions
        return suggestions[:5]

    def _calculate_completion_quality(self, suggestions: List[CodeSuggestion]) -> float:
        """Calculate quality score for completion suggestions"""
        if not suggestions:
            return 0.0

        avg_confidence = sum(s.confidence for s in suggestions) / len(suggestions)
        return avg_confidence

    def _update_performance_metrics(self, success: bool, latency_ms: float, quality_score: float):
        """Update performance metrics"""
        self.request_count += 1
        if success:
            self.success_count += 1

        # Update average latency
        self.average_latency = (
            (self.average_latency * (self.request_count - 1)) + latency_ms
        ) / self.request_count

        # Update success rate
        self.performance_metrics['requests_processed'] = self.request_count
        self.performance_metrics['average_response_time'] = self.average_latency
        self.performance_metrics['success_rate'] = self.success_count / self.request_count
        self.performance_metrics['quality_score'] = quality_score

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            'status': 'ok',
            'name': self.name,
            'version': self.version,
            'capabilities': self.capabilities,
            'performance': self.performance_metrics,
            'uptime': 'active'
        }

    async def shutdown(self):
        """Shutdown the bridge"""
        logger.info("   🛑 Shutting down Kilo Code bridge...")
        # Cleanup operations here
        logger.info("   ✅ Kilo Code bridge shutdown complete")