#!/usr/bin/env python3
"""
🚀 ULTRON AUTO - PARALLEL EXECUTION MODE
                    -LUM THE MODERN

ADAPT, IMPROVISE, OVERCOME: Our version of AUTO that CAN run both parallel!

Unlike OEM AUTO (picks one), ULTRON AUTO:
- Analyzes request complexity
- Runs LOCAL + CLOUD in parallel when beneficial
- Returns best result or combines both
- Falls back to single route for simple tasks

@LUMINA @JARVIS @ULTRON -LUM_THE_MODERN
"""

import sys
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ULTRONAutoParallel")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ULTRONAutoParallel")


class ExecutionMode(Enum):
    """Execution modes for ULTRON AUTO"""
    LOCAL_ONLY = "local_only"           # Simple task, local only
    CLOUD_ONLY = "cloud_only"           # Complex task, cloud only
    PARALLEL_BOTH = "parallel_both"     # Run both, return best
    PARALLEL_SMART = "parallel_smart"   # Run both, combine results


@dataclass
class ExecutionResult:
    """Result from model execution"""
    source: str  # "local" or "cloud"
    model: str
    response: str
    latency_ms: float
    tokens_generated: int
    quality_score: float
    cost: float
    success: bool
    error: Optional[str] = None


@dataclass
class AutoDecision:
    """Decision from AUTO analysis"""
    mode: ExecutionMode
    reasoning: str
    should_parallel: bool
    local_model: Optional[str]
    cloud_model: Optional[str]
    estimated_cost: float


class ULTRONAutoParallel:
    """
    ULTRON AUTO - Our version that CAN run parallel!

    ADAPT: Analyzes request to determine best strategy
    IMPROVISE: Runs both local + cloud when beneficial
    OVERCOME: Returns best result or combines both
    """

    def __init__(self):
        # Local endpoints
        self.local_endpoints = {
            "millennium_falc": "http://localhost:11434",
            "iron_legion_i": "http://<NAS_IP>:3001",
            "iron_legion_iv": "http://<NAS_IP>:3004",
            "iron_legion_v": "http://<NAS_IP>:3005",
            "nas": "http://<NAS_PRIMARY_IP>:11434"
        }

        # Local models
        self.local_models = {
            "smollm:135m": {"quality": 0.5, "latency_ms": 7, "best_for": "quick"},
            "llama3.2:3b": {"quality": 0.7, "latency_ms": 30, "best_for": "general"},
            "mistral:latest": {"quality": 0.85, "latency_ms": 200, "best_for": "general"},
            "codellama:13b": {"quality": 0.9, "latency_ms": 2000, "best_for": "code"},
            "llama3:8b": {"quality": 0.85, "latency_ms": 100, "best_for": "general"}
        }

        # Cloud models
        self.cloud_models = {
            "claude-opus-4": {"quality": 1.0, "cost_per_1m": 45.0, "best_for": "complex"},
            "claude-sonnet-4": {"quality": 0.95, "cost_per_1m": 9.0, "best_for": "balanced"},
            "gpt-4o": {"quality": 0.93, "cost_per_1m": 6.25, "best_for": "general"}
        }

        logger.info("=" * 80)
        logger.info("🚀 ULTRON AUTO - PARALLEL EXECUTION MODE")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info("   ADAPT: Smart request analysis")
        logger.info("   IMPROVISE: Parallel execution when beneficial")
        logger.info("   OVERCOME: Best result or combined output")
        logger.info("=" * 80)

    def analyze_request(
        self,
        prompt: str,
        context_tokens: int = 0,
        task_type: Optional[str] = None
    ) -> AutoDecision:
        """
        ADAPT: Analyze request to determine execution strategy.

        Returns decision on whether to run parallel or single route.
        """
        prompt_lower = prompt.lower()
        prompt_length = len(prompt)

        # Quick/simple queries → Local only
        if prompt_length < 100:
            return AutoDecision(
                mode=ExecutionMode.LOCAL_ONLY,
                reasoning="Quick query - Local SmolLM is sufficient (7ms latency)",
                should_parallel=False,
                local_model="smollm:135m",
                cloud_model=None,
                estimated_cost=0.0
            )

        # Code tasks → Smart routing
        if any(kw in prompt_lower for kw in ["code", "function", "class", "implement", "fix", "bug", "python", "javascript", "typescript"]):
            # Complex code keywords → Parallel
            complex_code_keywords = ["comprehensive", "pipeline", "architecture", "system", "framework", "optimize", "refactor", "design pattern"]
            is_complex_code = any(kw in prompt_lower for kw in complex_code_keywords) or prompt_length > 500

            if is_complex_code:
                # Complex code → Parallel (local for speed, cloud for quality)
                return AutoDecision(
                    mode=ExecutionMode.PARALLEL_SMART,
                    reasoning="Complex code - Parallel execution: Local for speed, Cloud for quality",
                    should_parallel=True,
                    local_model="codellama:13b",
                    cloud_model="claude-sonnet-4",
                    estimated_cost=0.05  # Rough estimate
                )
            else:
                # Simple code → Local only
                return AutoDecision(
                    mode=ExecutionMode.LOCAL_ONLY,
                    reasoning="Simple code task - Local CodeLlama excels at this (FREE)",
                    should_parallel=False,
                    local_model="codellama:13b",
                    cloud_model=None,
                    estimated_cost=0.0
                )

        # Large context → Cloud only (local limited to 32k)
        if context_tokens > 32000:
            return AutoDecision(
                mode=ExecutionMode.CLOUD_ONLY,
                reasoning=f"Context {context_tokens} tokens exceeds local limit (32k) - Cloud only",
                should_parallel=False,
                local_model=None,
                cloud_model="claude-opus-4",
                estimated_cost=0.20
            )

        # Complex reasoning/analysis → Parallel
        complex_keywords = ["explain", "analyze", "compare", "why", "how does", "what is", "complex", "detailed"]
        if any(kw in prompt_lower for kw in complex_keywords) and prompt_length > 200:
            return AutoDecision(
                mode=ExecutionMode.PARALLEL_SMART,
                reasoning="Complex reasoning task - Parallel: Local for quick answer, Cloud for depth",
                should_parallel=True,
                local_model="mistral:latest",
                cloud_model="claude-opus-4",
                estimated_cost=0.15
            )

        # General tasks → Parallel smart (local primary, cloud fallback)
        if prompt_length > 300:
            return AutoDecision(
                mode=ExecutionMode.PARALLEL_SMART,
                reasoning="General task - Parallel smart: Local primary, Cloud enhances",
                should_parallel=True,
                local_model="mistral:latest",
                cloud_model="claude-sonnet-4",
                estimated_cost=0.08
            )

        # Default: Local only
        return AutoDecision(
            mode=ExecutionMode.LOCAL_ONLY,
            reasoning="Standard task - Local Mistral is sufficient",
            should_parallel=False,
            local_model="mistral:latest",
            cloud_model=None,
            estimated_cost=0.0
        )

    async def execute_local(
        self,
        prompt: str,
        model: str,
        endpoint: str = "http://localhost:11434"
    ) -> ExecutionResult:
        """Execute on local ULTRON cluster"""
        try:
            start = datetime.now()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        latency = (datetime.now() - start).total_seconds() * 1000

                        return ExecutionResult(
                            source="local",
                            model=model,
                            response=data.get("response", ""),
                            latency_ms=latency,
                            tokens_generated=data.get("eval_count", 0),
                            quality_score=self.local_models.get(model, {}).get("quality", 0.7),
                            cost=0.0,
                            success=True
                        )
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            return ExecutionResult(
                source="local",
                model=model,
                response="",
                latency_ms=0,
                tokens_generated=0,
                quality_score=0.0,
                cost=0.0,
                success=False,
                error=str(e)
            )

    async def execute_cloud(
        self,
        prompt: str,
        model: str
    ) -> ExecutionResult:
        """Execute on cloud API (placeholder - would need actual API keys)"""
        # This is a placeholder - in real implementation, would call actual APIs
        logger.warning(f"Cloud execution for {model} - Placeholder (needs API integration)")

        return ExecutionResult(
            source="cloud",
            model=model,
            response="[Cloud API integration needed]",
            latency_ms=2000,
            tokens_generated=100,
            quality_score=self.cloud_models.get(model, {}).get("quality", 0.9),
            cost=self.cloud_models.get(model, {}).get("cost_per_1m", 0) / 1000,
            success=False,
            error="Cloud API integration not implemented"
        )

    async def execute_parallel(
        self,
        prompt: str,
        local_model: str,
        cloud_model: str
    ) -> Tuple[ExecutionResult, ExecutionResult]:
        """IMPROVISE: Execute both local and cloud in parallel"""
        local_task = self.execute_local(prompt, local_model)
        cloud_task = self.execute_cloud(prompt, cloud_model)

        local_result, cloud_result = await asyncio.gather(local_task, cloud_task)

        return local_result, cloud_result

    def combine_results(
        self,
        local_result: ExecutionResult,
        cloud_result: ExecutionResult
    ) -> Dict[str, Any]:
        """
        OVERCOME: Combine results from both sources.

        Strategies:
        1. Return fastest if both successful
        2. Return highest quality if both successful
        3. Return whichever succeeded if one failed
        4. Combine insights from both
        """
        if not local_result.success and not cloud_result.success:
            return {
                "success": False,
                "error": "Both local and cloud execution failed",
                "local_error": local_result.error,
                "cloud_error": cloud_result.error
            }

        if not local_result.success:
            return {
                "success": True,
                "source": "cloud_only",
                "response": cloud_result.response,
                "model": cloud_result.model,
                "latency_ms": cloud_result.latency_ms,
                "cost": cloud_result.cost,
                "fallback_reason": "Local execution failed"
            }

        if not cloud_result.success:
            return {
                "success": True,
                "source": "local_only",
                "response": local_result.response,
                "model": local_result.model,
                "latency_ms": local_result.latency_ms,
                "cost": local_result.cost,
                "fallback_reason": "Cloud execution failed"
            }

        # Both succeeded - choose best strategy
        # Strategy: Return fastest if quality similar, otherwise return best quality
        quality_diff = abs(local_result.quality_score - cloud_result.quality_score)

        if quality_diff < 0.1:
            # Quality similar - return fastest
            if local_result.latency_ms < cloud_result.latency_ms:
                return {
                    "success": True,
                    "source": "local_fastest",
                    "response": local_result.response,
                    "model": local_result.model,
                    "latency_ms": local_result.latency_ms,
                    "cost": local_result.cost,
                    "parallel_executed": True,
                    "cloud_also_available": True,
                    "cloud_latency_ms": cloud_result.latency_ms
                }
            else:
                return {
                    "success": True,
                    "source": "cloud_fastest",
                    "response": cloud_result.response,
                    "model": cloud_result.model,
                    "latency_ms": cloud_result.latency_ms,
                    "cost": cloud_result.cost,
                    "parallel_executed": True,
                    "local_also_available": True,
                    "local_latency_ms": local_result.latency_ms
                }
        else:
            # Quality differs - return best quality
            if cloud_result.quality_score > local_result.quality_score:
                return {
                    "success": True,
                    "source": "cloud_quality",
                    "response": cloud_result.response,
                    "model": cloud_result.model,
                    "latency_ms": cloud_result.latency_ms,
                    "cost": cloud_result.cost,
                    "quality_score": cloud_result.quality_score,
                    "parallel_executed": True,
                    "local_also_available": True,
                    "local_quality": local_result.quality_score
                }
            else:
                return {
                    "success": True,
                    "source": "local_quality",
                    "response": local_result.response,
                    "model": local_result.model,
                    "latency_ms": local_result.latency_ms,
                    "cost": local_result.cost,
                    "quality_score": local_result.quality_score,
                    "parallel_executed": True,
                    "cloud_also_available": True,
                    "cloud_quality": cloud_result.quality_score
                }

    async def auto_execute(
        self,
        prompt: str,
        context_tokens: int = 0
    ) -> Dict[str, Any]:
        """
        ULTRON AUTO: Main execution method.

        ADAPT → IMPROVISE → OVERCOME
        """
        # ADAPT: Analyze request
        decision = self.analyze_request(prompt, context_tokens)

        logger.info(f"🎯 AUTO Decision: {decision.mode.value}")
        logger.info(f"   Reasoning: {decision.reasoning}")

        # Execute based on decision
        if decision.mode == ExecutionMode.LOCAL_ONLY:
            result = await self.execute_local(prompt, decision.local_model)
            return {
                "success": result.success,
                "source": "local_only",
                "response": result.response,
                "model": result.model,
                "latency_ms": result.latency_ms,
                "cost": result.cost,
                "decision": decision.reasoning
            }

        elif decision.mode == ExecutionMode.CLOUD_ONLY:
            result = await self.execute_cloud(prompt, decision.cloud_model)
            return {
                "success": result.success,
                "source": "cloud_only",
                "response": result.response,
                "model": result.model,
                "latency_ms": result.latency_ms,
                "cost": result.cost,
                "decision": decision.reasoning
            }

        elif decision.mode in [ExecutionMode.PARALLEL_BOTH, ExecutionMode.PARALLEL_SMART]:
            # IMPROVISE: Run both in parallel
            local_result, cloud_result = await self.execute_parallel(
                prompt,
                decision.local_model,
                decision.cloud_model
            )

            # OVERCOME: Combine results
            combined = self.combine_results(local_result, cloud_result)
            combined["decision"] = decision.reasoning
            combined["parallel_mode"] = decision.mode.value

            return combined

        else:
            return {
                "success": False,
                "error": "Unknown execution mode",
                "decision": decision.reasoning
            }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ULTRON AUTO - Parallel Execution")
    parser.add_argument("--query", type=str, required=True, help="Query to execute")
    parser.add_argument("--context", type=int, default=0, help="Context tokens")
    parser.add_argument("--analyze", action="store_true", help="Only analyze, don't execute")

    args = parser.parse_args()

    auto = ULTRONAutoParallel()

    if args.analyze:
        decision = auto.analyze_request(args.query, args.context)
        print(f"\n🎯 AUTO ANALYSIS:")
        print(f"   Mode: {decision.mode.value}")
        print(f"   Parallel: {decision.should_parallel}")
        print(f"   Local Model: {decision.local_model or 'N/A'}")
        print(f"   Cloud Model: {decision.cloud_model or 'N/A'}")
        print(f"   Est. Cost: ${decision.estimated_cost:.4f}")
        print(f"   Reasoning: {decision.reasoning}")
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(auto.auto_execute(args.query, args.context))

            print(f"\n🚀 ULTRON AUTO RESULT:")
            print(f"   Success: {result['success']}")
            print(f"   Source: {result.get('source', 'unknown')}")
            print(f"   Model: {result.get('model', 'N/A')}")
            print(f"   Latency: {result.get('latency_ms', 0):.0f}ms")
            print(f"   Cost: ${result.get('cost', 0):.4f}")
            if result.get('parallel_executed'):
                print(f"   ⚡ PARALLEL EXECUTION: Both local and cloud ran!")
            print(f"\n   Response:")
            print(f"   {result.get('response', result.get('error', 'No response'))}")
        finally:
            loop.close()


if __name__ == "__main__":


    main()