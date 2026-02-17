#!/usr/bin/env python3
"""
STRIDE 13 - Consistent Chain of Asks and Summaries

String a chain of asks and summaries. One after another.
Left foot, right foot, left foot, right foot.
So we don't break our stride.

Prime number: 13 (Stride number - consistent rhythm)

Tags: #STRIDE #CHAIN #ASK #SUMMARY #MOMENTUM @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from master_jarvis_agent_chat_processor import MasterJARVISAgentChatProcessor
    from oracle_11_queue import ORACLE11, ItemType
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("STRIDE13")
ts_logger = get_timestamp_logger()


class StrideFoot(Enum):
    """Stride foot - left or right"""
    LEFT = "left"  # Ask
    RIGHT = "right"  # Summary


@dataclass
class StrideStep:
    """A step in the stride chain"""
    step_id: str
    foot: StrideFoot
    ask_id: Optional[str] = None
    ask_content: Optional[str] = None
    summary: Optional[str] = None
    timestamp: str = ""
    next_step_id: Optional[str] = None
    previous_step_id: Optional[str] = None


@dataclass
class StrideChain:
    """A chain of stride steps"""
    chain_id: str
    steps: List[StrideStep]
    current_step: int = 0
    stride_pattern: List[StrideFoot] = field(default_factory=lambda: [StrideFoot.LEFT, StrideFoot.RIGHT])
    momentum: float = 1.0  # Momentum multiplier (1.0 = normal, >1.0 = accelerating)


class STRIDE13:
    """
    STRIDE 13 - Consistent Chain of Asks and Summaries

    String a chain of asks and summaries. One after another.
    Left foot, right foot, left foot, right foot.
    So we don't break our stride.

    Prime number: 13 (Stride number - consistent rhythm)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize STRIDE 13"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "stride_13_chains"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.master_processor = MasterJARVISAgentChatProcessor(project_root=project_root)
        self.oracle = ORACLE11(project_root=project_root)

        self.chains: Dict[str, StrideChain] = {}
        self.current_chain: Optional[StrideChain] = None

        logger.info("🚶 STRIDE 13 initialized")
        logger.info("   Consistent chain of asks and summaries")
        logger.info("   Left foot, right foot - don't break stride")
        logger.info("   Prime number: 13 (Stride number)")

    def create_chain(self, chain_id: Optional[str] = None) -> StrideChain:
        """Create a new stride chain"""
        if chain_id is None:
            chain_id = f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        chain = StrideChain(
            chain_id=chain_id,
            steps=[],
            stride_pattern=[StrideFoot.LEFT, StrideFoot.RIGHT],  # Left (Ask), Right (Summary)
        )

        self.chains[chain_id] = chain
        self.current_chain = chain

        logger.info(f"🔗 Stride chain created: {chain_id}")
        return chain

    def add_ask(self, ask_content: str, chain_id: Optional[str] = None) -> StrideStep:
        """Add an ask (left foot)"""
        if chain_id is None:
            if self.current_chain is None:
                self.create_chain()
            chain = self.current_chain
        else:
            chain = self.chains.get(chain_id)
            if chain is None:
                chain = self.create_chain(chain_id)

        # Create ask step (left foot)
        step = StrideStep(
            step_id=f"step_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            foot=StrideFoot.LEFT,
            ask_content=ask_content,
            timestamp=datetime.now().isoformat(),
        )

        # Link to previous step
        if chain.steps:
            previous_step = chain.steps[-1]
            previous_step.next_step_id = step.step_id
            step.previous_step_id = previous_step.step_id

        chain.steps.append(step)
        chain.current_step = len(chain.steps) - 1

        logger.info(f"👣 Left foot (ASK): {step.step_id}")
        logger.info(f"   Content: {ask_content[:50]}...")

        # Queue in Oracle
        self.oracle.queue_operator_request(ask_content, priority=5)

        return step

    def add_summary(self, summary: str, chain_id: Optional[str] = None) -> StrideStep:
        """Add a summary (right foot)"""
        if chain_id is None:
            if self.current_chain is None:
                self.create_chain()
            chain = self.current_chain
        else:
            chain = self.chains.get(chain_id)
            if chain is None:
                chain = self.create_chain(chain_id)

        # Create summary step (right foot)
        step = StrideStep(
            step_id=f"step_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            foot=StrideFoot.RIGHT,
            summary=summary,
            timestamp=datetime.now().isoformat(),
        )

        # Link to previous step
        if chain.steps:
            previous_step = chain.steps[-1]
            previous_step.next_step_id = step.step_id
            step.previous_step_id = previous_step.step_id

        chain.steps.append(step)
        chain.current_step = len(chain.steps) - 1

        logger.info(f"👣 Right foot (SUMMARY): {step.step_id}")
        logger.info(f"   Summary: {summary[:50]}...")

        return step

    def stride(self, ask_content: str, summary: str, chain_id: Optional[str] = None) -> Tuple[StrideStep, StrideStep]:
        """Complete stride: left foot (ask) + right foot (summary)"""
        ask_step = self.add_ask(ask_content, chain_id)
        summary_step = self.add_summary(summary, chain_id)

        logger.info(f"🚶 Stride complete: {ask_step.step_id} → {summary_step.step_id}")

        return ask_step, summary_step

    def stride_chain(self, asks_and_summaries: List[Tuple[str, str]], chain_id: Optional[str] = None) -> StrideChain:
        """Create a chain of strides"""
        if chain_id is None:
            chain = self.create_chain()
        else:
            chain = self.chains.get(chain_id)
            if chain is None:
                chain = self.create_chain(chain_id)

        logger.info(f"🔗 Creating stride chain: {len(asks_and_summaries)} strides")

        for ask, summary in asks_and_summaries:
            self.stride(ask, summary, chain_id)

        # Calculate momentum
        chain.momentum = 1.0 + (len(chain.steps) * 0.01)  # Momentum increases with chain length

        logger.info(f"✅ Stride chain complete: {len(chain.steps)} steps, momentum: {chain.momentum:.2f}")

        return chain

    def continue_stride(self, ask_content: str, chain_id: Optional[str] = None) -> StrideStep:
        """Continue stride - add next step based on pattern"""
        if chain_id is None:
            if self.current_chain is None:
                self.create_chain()
            chain = self.current_chain
        else:
            chain = self.chains.get(chain_id)
            if chain is None:
                chain = self.create_chain(chain_id)

        # Determine next foot based on last step
        if not chain.steps:
            # First step - start with left foot (ask)
            next_foot = StrideFoot.LEFT
        else:
            last_step = chain.steps[-1]
            # Alternate: if last was left (ask), next is right (summary), and vice versa
            next_foot = StrideFoot.RIGHT if last_step.foot == StrideFoot.LEFT else StrideFoot.LEFT

        if next_foot == StrideFoot.LEFT:
            return self.add_ask(ask_content, chain_id)
        else:
            # For summary, we need the summary content
            # This would typically come from processing the ask
            return self.add_summary(ask_content, chain_id)  # Using ask_content as placeholder

    def get_chain_status(self, chain_id: Optional[str] = None) -> Dict[str, Any]:
        """Get chain status"""
        if chain_id is None:
            chain = self.current_chain
        else:
            chain = self.chains.get(chain_id)

        if chain is None:
            return {"error": "Chain not found"}

        return {
            "chain_id": chain.chain_id,
            "total_steps": len(chain.steps),
            "current_step": chain.current_step,
            "momentum": chain.momentum,
            "left_foot_steps": len([s for s in chain.steps if s.foot == StrideFoot.LEFT]),
            "right_foot_steps": len([s for s in chain.steps if s.foot == StrideFoot.RIGHT]),
            "stride_pattern": [f.value for f in chain.stride_pattern],
        }

    def save_chain(self, chain_id: Optional[str] = None):
        try:
            """Save chain to disk"""
            if chain_id is None:
                chain = self.current_chain
            else:
                chain = self.chains.get(chain_id)

            if chain is None:
                return

            file_path = self.data_dir / f"{chain.chain_id}.json"

            data = {
                "chain_id": chain.chain_id,
                "steps": [
                    {
                        "step_id": s.step_id,
                        "foot": s.foot.value,
                        "ask_id": s.ask_id,
                        "ask_content": s.ask_content,
                        "summary": s.summary,
                        "timestamp": s.timestamp,
                        "next_step_id": s.next_step_id,
                        "previous_step_id": s.previous_step_id,
                    }
                    for s in chain.steps
                ],
                "current_step": chain.current_step,
                "momentum": chain.momentum,
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Chain saved: {file_path}")


        except Exception as e:
            self.logger.error(f"Error in save_chain: {e}", exc_info=True)
            raise
def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="STRIDE 13 - Consistent Chain of Asks and Summaries")
    parser.add_argument("--ask", type=str, help="Add ask (left foot)")
    parser.add_argument("--summary", type=str, help="Add summary (right foot)")
    parser.add_argument("--stride", nargs=2, metavar=("ASK", "SUMMARY"), help="Complete stride (ask + summary)")
    parser.add_argument("--chain", nargs="+", help="Create chain: --chain ASK1 SUMMARY1 ASK2 SUMMARY2 ...")
    parser.add_argument("--status", action="store_true", help="Show chain status")
    parser.add_argument("--save", action="store_true", help="Save current chain")

    args = parser.parse_args()

    print("="*80)
    print("🚶 STRIDE 13 - CONSISTENT CHAIN OF ASKS AND SUMMARIES")
    print("="*80)
    print()
    print("String a chain of asks and summaries")
    print("One after another")
    print("Left foot, right foot, left foot, right foot")
    print("So we don't break our stride")
    print("Prime number: 13 (Stride number)")
    print()

    stride = STRIDE13()

    if args.ask:
        step = stride.add_ask(args.ask)
        print(f"👣 Left foot (ASK): {step.step_id}")
        print(f"   Content: {args.ask[:100]}...")
        print()

    if args.summary:
        step = stride.add_summary(args.summary)
        print(f"👣 Right foot (SUMMARY): {step.step_id}")
        print(f"   Summary: {args.summary[:100]}...")
        print()

    if args.stride:
        ask, summary = args.stride
        ask_step, summary_step = stride.stride(ask, summary)
        print(f"🚶 Stride complete:")
        print(f"   Left foot (ASK): {ask_step.step_id}")
        print(f"   Right foot (SUMMARY): {summary_step.step_id}")
        print()

    if args.chain:
        # Parse chain: ASK1 SUMMARY1 ASK2 SUMMARY2 ...
        if len(args.chain) % 2 != 0:
            print("❌ Error: Chain must have even number of arguments (ask, summary pairs)")
        else:
            asks_and_summaries = [(args.chain[i], args.chain[i+1]) for i in range(0, len(args.chain), 2)]
            chain = stride.stride_chain(asks_and_summaries)
            print(f"🔗 Chain created: {chain.chain_id}")
            print(f"   Steps: {len(chain.steps)}")
            print(f"   Momentum: {chain.momentum:.2f}")
            print()

    if args.status:
        status = stride.get_chain_status()
        if "error" not in status:
            print("📊 CHAIN STATUS:")
            print(f"   Chain ID: {status['chain_id']}")
            print(f"   Total Steps: {status['total_steps']}")
            print(f"   Current Step: {status['current_step']}")
            print(f"   Momentum: {status['momentum']:.2f}")
            print(f"   Left Foot (ASK): {status['left_foot_steps']}")
            print(f"   Right Foot (SUMMARY): {status['right_foot_steps']}")
            print()
        else:
            print(f"❌ {status['error']}")
            print()

    if args.save:
        stride.save_chain()
        print("💾 Chain saved")
        print()

    if not any([args.ask, args.summary, args.stride, args.chain, args.status, args.save]):
        # Default: show status
        status = stride.get_chain_status()
        if "error" not in status:
            print("📊 CURRENT CHAIN:")
            print(f"   Steps: {status['total_steps']}")
            print(f"   Momentum: {status['momentum']:.2f}")
        else:
            print("   No active chain")
        print()
        print("Use --ask CONTENT to add ask (left foot)")
        print("Use --summary CONTENT to add summary (right foot)")
        print("Use --stride ASK SUMMARY to complete stride")
        print("Use --chain ASK1 SUMMARY1 ASK2 SUMMARY2 ... to create chain")
        print("Use --status to show status")
        print("Use --save to save chain")
        print()


if __name__ == "__main__":


    main()