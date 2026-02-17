#!/usr/bin/env python3
"""
JARVIS Tool Registry - We Are Creating Tools

Comprehensive registry and management system for all JARVIS tools
Tracks, discovers, and manages tools we've created

"WE ARE CREATING TOOLS JARVIS"
"""

import sys
import json
import importlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISToolRegistry")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ToolCategory(Enum):
    """Tool categories"""
    GRAMMAR = "grammar"
    AI_COORDINATION = "ai_coordination"
    INTEGRATION = "integration"
    DATAFEED = "datafeed"
    PATHFINDER = "pathfinder"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"
    SYSTEM = "system"
    OTHER = "other"


class ToolStatus(Enum):
    """Tool status"""
    ACTIVE = "active"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


@dataclass
class Tool:
    """JARVIS Tool Definition"""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    status: ToolStatus
    file_path: Path
    module_name: str
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['category'] = self.category.value
        data['status'] = self.status.value
        data['file_path'] = str(self.file_path)
        return data


class JARVISToolRegistry:
    """
    JARVIS Tool Registry

    Comprehensive registry and management system for all JARVIS tools
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize tool registry"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISToolRegistry")

        # Registry storage
        self.registry: Dict[str, Tool] = {}
        self.registry_file = self.project_root / "data" / "system" / "jarvis_tool_registry.json"
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

        # Auto-discover and register tools
        self._discover_tools()

        # Load existing registry
        self._load_registry()

        self.logger.info("🔧 JARVIS Tool Registry initialized")
        self.logger.info(f"   Registered tools: {len(self.registry)}")

    def _discover_tools(self):
        try:
            """Auto-discover tools in scripts/python"""
            tools_dir = self.project_root / "scripts" / "python"

            if not tools_dir.exists():
                return

            # Discover all Python files
            for py_file in tools_dir.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                # Try to register tool
                self._register_tool_from_file(py_file)

        except Exception as e:
            self.logger.error(f"Error in _discover_tools: {e}", exc_info=True)
            raise
    def _register_tool_from_file(self, file_path: Path):
        """Register a tool from a Python file"""
        tool_id = file_path.stem

        # Skip if already registered
        if tool_id in self.registry:
            return

        # Determine category and status from file name
        category = self._determine_category(file_path)
        status = self._determine_status(file_path)

        # Read file to extract info
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract description from docstring
            description = self._extract_description(content)

            # Extract class/function names
            class_name, function_name = self._extract_components(content)

            # Create tool
            tool = Tool(
                tool_id=tool_id,
                name=self._format_name(tool_id),
                description=description,
                category=category,
                status=status,
                file_path=file_path,
                module_name=f"scripts.python.{tool_id}",
                class_name=class_name,
                function_name=function_name,
                capabilities=self._extract_capabilities(content)
            )

            self.registry[tool_id] = tool
            self.logger.debug(f"  Discovered tool: {tool.name}")
        except Exception as e:
            self.logger.debug(f"  Error registering {file_path.name}: {e}")

    def _determine_category(self, file_path: Path) -> ToolCategory:
        """Determine tool category from file name"""
        name = file_path.stem.lower()

        if "grammar" in name or "grammarly" in name:
            return ToolCategory.GRAMMAR
        elif "coordination" in name or "ai_coordination" in name:
            return ToolCategory.AI_COORDINATION
        elif "integration" in name:
            return ToolCategory.INTEGRATION
        elif "datafeed" in name or "roamwise" in name:
            return ToolCategory.DATAFEED
        elif "pathfinder" in name or "atlas" in name:
            return ToolCategory.PATHFINDER
        elif "monitor" in name or "health" in name:
            return ToolCategory.MONITORING
        elif "optimize" in name or "peak" in name:
            return ToolCategory.OPTIMIZATION
        elif "jarvis" in name or "system" in name:
            return ToolCategory.SYSTEM
        else:
            return ToolCategory.OTHER

    def _determine_status(self, file_path: Path) -> ToolStatus:
        """Determine tool status"""
        name = file_path.stem.lower()

        if "experimental" in name or "test" in name:
            return ToolStatus.EXPERIMENTAL
        elif "deprecated" in name:
            return ToolStatus.DEPRECATED
        elif "in_progress" in name or "wip" in name:
            return ToolStatus.IN_PROGRESS
        else:
            return ToolStatus.READY

    def _extract_description(self, content: str) -> str:
        """Extract description from docstring"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                # Found docstring start
                desc_lines = []
                quote = '"""' if '"""' in line else "'''"
                start_idx = line.find(quote) + 3
                if start_idx < len(line):
                    desc_lines.append(line[start_idx:].strip())

                # Continue reading docstring
                for j in range(i + 1, min(i + 10, len(lines))):
                    if quote in lines[j]:
                        break
                    desc_lines.append(lines[j].strip())

                return ' '.join(desc_lines).strip()

        return "No description available"

    def _extract_components(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract class and function names"""
        class_name = None
        function_name = None

        lines = content.split('\n')
        for line in lines:
            if 'class ' in line and not class_name:
                parts = line.split('class ')
                if len(parts) > 1:
                    class_name = parts[1].split('(')[0].split(':')[0].strip()
            if 'def main(' in line or 'def run(' in line:
                if not function_name:
                    parts = line.split('def ')
                    if len(parts) > 1:
                        function_name = parts[1].split('(')[0].strip()

        return class_name, function_name

    def _extract_capabilities(self, content: str) -> List[str]:
        """Extract capabilities from content"""
        capabilities = []

        # Look for common capability patterns
        capability_keywords = [
            "auto-correct", "spell check", "grammar check",
            "coordination", "sync", "integration",
            "monitor", "health check", "status",
            "optimize", "performance", "tuning",
            "pathfinder", "pathfinding", "atlas",
            "datafeed", "blend", "hybrid"
        ]

        content_lower = content.lower()
        for keyword in capability_keywords:
            if keyword in content_lower:
                capabilities.append(keyword.replace(" ", "_"))

        return capabilities

    def _format_name(self, tool_id: str) -> str:
        """Format tool name from ID"""
        return tool_id.replace("_", " ").title()

    def register_tool(self, tool: Tool):
        """Manually register a tool"""
        self.registry[tool.tool_id] = tool
        self._save_registry()
        self.logger.info(f"  ✅ Registered tool: {tool.name}")

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get a tool by ID"""
        return self.registry.get(tool_id)

    def list_tools(self, category: Optional[ToolCategory] = None, 
                   status: Optional[ToolStatus] = None) -> List[Tool]:
        """List tools with optional filters"""
        tools = list(self.registry.values())

        if category:
            tools = [t for t in tools if t.category == category]

        if status:
            tools = [t for t in tools if t.status == status]

        return sorted(tools, key=lambda t: t.name)

    def execute_tool(self, tool_id: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute a tool"""
        tool = self.get_tool(tool_id)
        if not tool:
            return {"success": False, "error": f"Tool not found: {tool_id}"}

        try:
            # Update usage
            tool.usage_count += 1
            tool.last_used = datetime.now().isoformat()
            self._save_registry()

            # Execute tool
            cmd = ["python", str(tool.file_path)]
            if args:
                cmd.extend(args)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            return {
                "success": result.returncode == 0,
                "tool_id": tool_id,
                "tool_name": tool.name,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_id": tool_id
            }

    def get_registry_summary(self) -> Dict[str, Any]:
        """Get registry summary"""
        tools_by_category = {}
        tools_by_status = {}

        for tool in self.registry.values():
            cat = tool.category.value
            if cat not in tools_by_category:
                tools_by_category[cat] = 0
            tools_by_category[cat] += 1

            stat = tool.status.value
            if stat not in tools_by_status:
                tools_by_status[stat] = 0
            tools_by_status[stat] += 1

        return {
            "total_tools": len(self.registry),
            "by_category": tools_by_category,
            "by_status": tools_by_status,
            "timestamp": datetime.now().isoformat()
        }

    def _save_registry(self):
        """Save registry to file"""
        try:
            data = {
                "tools": {tid: tool.to_dict() for tid, tool in self.registry.items()},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.debug(f"Error saving registry: {e}")

    def _load_registry(self):
        """Load registry from file"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for tid, tool_data in data.get("tools", {}).items():
                        # Reconstruct tool
                        tool = Tool(
                            tool_id=tool_data["tool_id"],
                            name=tool_data["name"],
                            description=tool_data["description"],
                            category=ToolCategory(tool_data["category"]),
                            status=ToolStatus(tool_data["status"]),
                            file_path=Path(tool_data["file_path"]),
                            module_name=tool_data["module_name"],
                            class_name=tool_data.get("class_name"),
                            function_name=tool_data.get("function_name"),
                            dependencies=tool_data.get("dependencies", []),
                            capabilities=tool_data.get("capabilities", []),
                            created_date=tool_data.get("created_date", datetime.now().isoformat()),
                            last_used=tool_data.get("last_used"),
                            usage_count=tool_data.get("usage_count", 0),
                            metadata=tool_data.get("metadata", {})
                        )
                        self.registry[tid] = tool
        except Exception as e:
            self.logger.debug(f"Error loading registry: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Tool Registry")
    parser.add_argument("--list", action="store_true", help="List all tools")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--status", type=str, help="Filter by status")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    parser.add_argument("--tool", type=str, help="Show tool details")
    parser.add_argument("--execute", type=str, help="Execute a tool")
    parser.add_argument("--args", nargs="+", help="Arguments for tool execution")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    registry = JARVISToolRegistry()

    if args.summary:
        summary = registry.get_registry_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("\n🔧 JARVIS Tool Registry Summary")
            print("="*60)
            print(f"Total Tools: {summary['total_tools']}")
            print("\nBy Category:")
            for cat, count in summary['by_category'].items():
                print(f"  {cat}: {count}")
            print("\nBy Status:")
            for stat, count in summary['by_status'].items():
                print(f"  {stat}: {count}")

    elif args.tool:
        tool = registry.get_tool(args.tool)
        if tool:
            if args.json:
                print(json.dumps(tool.to_dict(), indent=2))
            else:
                print(f"\n🔧 Tool: {tool.name}")
                print("="*60)
                print(f"ID: {tool.tool_id}")
                print(f"Description: {tool.description}")
                print(f"Category: {tool.category.value}")
                print(f"Status: {tool.status.value}")
                print(f"File: {tool.file_path}")
                print(f"Usage Count: {tool.usage_count}")
                if tool.capabilities:
                    print(f"Capabilities: {', '.join(tool.capabilities)}")
        else:
            print(f"❌ Tool not found: {args.tool}")

    elif args.execute:
        result = registry.execute_tool(args.execute, args.args)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print(f"✅ Executed: {result['tool_name']}")
                if result.get("stdout"):
                    print(result["stdout"])
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                if result.get("stderr"):
                    print(result["stderr"])

    elif args.list:
        category = ToolCategory(args.category) if args.category else None
        status = ToolStatus(args.status) if args.status else None
        tools = registry.list_tools(category, status)

        if args.json:
            print(json.dumps([t.to_dict() for t in tools], indent=2))
        else:
            print("\n🔧 JARVIS Tools")
            print("="*60)
            for tool in tools:
                status_icon = "✅" if tool.status == ToolStatus.ACTIVE else "⏳" if tool.status == ToolStatus.READY else "🔬"
                print(f"{status_icon} {tool.name} ({tool.tool_id})")
                print(f"   {tool.description[:60]}...")
                print(f"   Category: {tool.category.value} | Status: {tool.status.value}")
                print()

    else:
        parser.print_help()

