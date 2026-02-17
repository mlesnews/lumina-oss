#!/usr/bin/env python3
"""
🔧 **Lumina Jarvis Integration Manager**

Manages the loading, registration, and orchestration of external extensions,
coding assistants, and development tools. Provides plugin architecture for
seamless integration while maintaining attribution compliance.

@V3_WORKFLOWED: True
@TEST_FIRST: True
@ETHICAL_INTEGRATION: Enforced
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import importlib
import inspect
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass
import asyncio

# Local imports
script_dir = Path(__file__).parent.parent.parent.parent
project_root = script_dir.parent
if str(project_root) not in os.sys.path:
    os.sys.path.insert(0, str(project_root))

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

logger = get_logger("JarvisIntegrationManager")


@dataclass
class ExtensionInfo:
    """Information about a registered extension"""
    name: str
    class_ref: Type
    metadata: Dict[str, Any]
    instance: Optional[Any] = None
    status: str = "registered"  # registered, loaded, active, error
    capabilities: List[str] = None
    last_used: Optional[float] = None


@dataclass
class IntegrationResult:
    """Result of an integration operation"""
    success: bool
    extension_name: str
    operation: str
    data: Any = None
    error: Optional[str] = None
    attribution_required: bool = False
    attribution_text: Optional[str] = None


class JarvisIntegrationManager:
    """
    Integration manager for Jarvis extensions framework.

    Handles loading, registration, and management of external tools,
    coding assistants, and development extensions with proper attribution.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.extensions_dir = self.project_root / "lumina_core" / "jarvis" / "extensions"

        # Extension registry
        self.extensions: Dict[str, ExtensionInfo] = {}
        self.capabilities_map: Dict[str, List[str]] = {}  # capability -> [extension_names]

        # Dependencies
        self.attribution_engine = None
        self.capability_router = None

        # Initialize components
        self._init_dependencies()

        logger.info("✅ Jarvis Integration Manager initialized")

    def _init_dependencies(self):
        """Initialize dependent components"""
        try:
            from attribution_engine import get_attribution_engine
            self.attribution_engine = get_attribution_engine()
        except ImportError:
            logger.warning("   ⚠️  Attribution engine not available")

        try:
            from capability_router import get_capability_router
            self.capability_router = get_capability_router()
        except ImportError:
            logger.warning("   ⚠️  Capability router not available")

    async def auto_discover_extensions(self) -> List[IntegrationResult]:
        """
        Automatically discover and register extensions from filesystem

        Scans the extensions directory structure and registers all valid extensions.
        """
        results = []

        # Define extension categories
        categories = {
            "coding_assistants": ["kilo_code", "rue_code", "klein_code", "creator_1_code"],
            "ides": ["cursor_ide", "vscode", "jetbrains"],
            "assistants": ["github_copilot", "tabnine", "amazon_q"]
        }

        for category, expected_extensions in categories.items():
            category_path = self.extensions_dir / category

            if not category_path.exists():
                logger.debug(f"   Category directory not found: {category}")
                continue

            for extension_dir in category_path.iterdir():
                if extension_dir.is_dir():
                    extension_name = extension_dir.name

                    # Check if it's an expected extension or auto-discover
                    if extension_name in expected_extensions or True:  # Allow auto-discovery
                        result = await self.register_extension_from_path(extension_dir)
                        results.append(result)

        logger.info(f"   🔍 Auto-discovered {len(results)} extensions")
        return results

    async def register_extension_from_path(self, extension_path: Path) -> IntegrationResult:
        """Register an extension from its directory path"""
        extension_name = extension_path.name

        try:
            # Load metadata
            metadata_file = extension_path / "attribution.json"
            capabilities_file = extension_path / "capabilities.json"

            if not metadata_file.exists():
                return IntegrationResult(
                    success=False,
                    extension_name=extension_name,
                    operation="register",
                    error="attribution.json not found"
                )

            # Load attribution metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Load capabilities if available
            capabilities = []
            if capabilities_file.exists():
                with open(capabilities_file, 'r') as f:
                    capabilities_data = json.load(f)
                    capabilities = list(capabilities_data.keys())

            # Find and load the extension class
            bridge_file = extension_path / f"{extension_name}_bridge.py"
            if not bridge_file.exists():
                # Try alternative naming
                bridge_file = extension_path / f"{extension_name.replace('_', '')}_bridge.py"
                if not bridge_file.exists():
                    return IntegrationResult(
                        success=False,
                        extension_name=extension_name,
                        operation="register",
                        error="bridge file not found"
                    )

            # Import the bridge module
            module_name = f"lumina_core.jarvis.extensions.{extension_path.parent.name}.{extension_name}.{extension_name}_bridge"
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                # Try alternative import path
                try:
                    spec = importlib.util.spec_from_file_location(extension_name, bridge_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                except Exception as e:
                    return IntegrationResult(
                        success=False,
                        extension_name=extension_name,
                        operation="register",
                        error=f"Failed to import bridge: {e}"
                    )

            # Find the bridge class
            bridge_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    name.endswith('Bridge') and
                    hasattr(obj, 'process_request')):
                    bridge_class = obj
                    break

            if not bridge_class:
                return IntegrationResult(
                    success=False,
                    extension_name=extension_name,
                    operation="register",
                    error="Bridge class not found"
                )

            # Register the extension
            result = await self.register_extension(
                extension_name=extension_name,
                extension_class=bridge_class,
                metadata=metadata
            )

            # Update capabilities mapping
            if capabilities:
                for capability in capabilities:
                    if capability not in self.capabilities_map:
                        self.capabilities_map[capability] = []
                    if extension_name not in self.capabilities_map[capability]:
                        self.capabilities_map[capability].append(extension_name)

            return result

        except Exception as e:
            return IntegrationResult(
                success=False,
                extension_name=extension_name,
                operation="register",
                error=f"Registration failed: {e}"
            )

    async def register_extension(self, extension_name: str, extension_class: Type,
                               metadata: Dict[str, Any]) -> IntegrationResult:
        """
        Register an extension with the integration manager

        Args:
            extension_name: Unique name for the extension
            extension_class: The bridge class for the extension
            metadata: Attribution and capability metadata

        Returns:
            IntegrationResult indicating success/failure
        """

        try:
            # Create extension info
            extension_info = ExtensionInfo(
                name=extension_name,
                class_ref=extension_class,
                metadata=metadata,
                capabilities=metadata.get('capabilities_used', [])
            )

            # Store in registry
            self.extensions[extension_name] = extension_info

            # Register with capability router if available
            if self.capability_router:
                await self.capability_router.register_extension(extension_name, extension_info)

            logger.info(f"   ✅ Registered extension: {extension_name}")

            return IntegrationResult(
                success=True,
                extension_name=extension_name,
                operation="register",
                data={"capabilities": extension_info.capabilities}
            )

        except Exception as e:
            logger.error(f"   ❌ Failed to register extension {extension_name}: {e}")

            return IntegrationResult(
                success=False,
                extension_name=extension_name,
                operation="register",
                error=str(e)
            )

    async def load_extension(self, extension_name: str) -> IntegrationResult:
        """Load and initialize an extension instance"""
        if extension_name not in self.extensions:
            return IntegrationResult(
                success=False,
                extension_name=extension_name,
                operation="load",
                error="Extension not registered"
            )

        extension_info = self.extensions[extension_name]

        try:
            # Create instance
            instance = extension_info.class_ref()

            # Initialize if async init method exists
            if hasattr(instance, 'initialize') and inspect.iscoroutinefunction(instance.initialize):
                await instance.initialize()
            elif hasattr(instance, 'initialize'):
                instance.initialize()

            # Store instance
            extension_info.instance = instance
            extension_info.status = "active"

            logger.info(f"   🚀 Loaded extension: {extension_name}")

            return IntegrationResult(
                success=True,
                extension_name=extension_name,
                operation="load"
            )

        except Exception as e:
            extension_info.status = "error"
            logger.error(f"   ❌ Failed to load extension {extension_name}: {e}")

            return IntegrationResult(
                success=False,
                extension_name=extension_name,
                operation="load",
                error=str(e)
            )

    async def unload_extension(self, extension_name: str) -> IntegrationResult:
        """Unload an extension instance"""
        if extension_name not in self.extensions:
            return IntegrationResult(
                success=False,
                extension_name=extension_name,
                operation="unload",
                error="Extension not registered"
            )

        extension_info = self.extensions[extension_name]

        try:
            # Shutdown if shutdown method exists
            if extension_info.instance:
                if hasattr(extension_info.instance, 'shutdown') and inspect.iscoroutinefunction(extension_info.instance.shutdown):
                    await extension_info.instance.shutdown()
                elif hasattr(extension_info.instance, 'shutdown'):
                    extension_info.instance.shutdown()

            # Clear instance
            extension_info.instance = None
            extension_info.status = "registered"

            logger.info(f"   🛑 Unloaded extension: {extension_name}")

            return IntegrationResult(
                success=True,
                extension_name=extension_name,
                operation="unload"
            )

        except Exception as e:
            logger.error(f"   ❌ Failed to unload extension {extension_name}: {e}")

            return IntegrationResult(
                success=False,
                extension_name=extension_name,
                operation="unload",
                error=str(e)
            )

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request by routing it to the appropriate extension

        Args:
            request: Request dictionary with capability, context, etc.

        Returns:
            Response dictionary with results and attribution
        """

        capability = request.get('capability', request.get('type', 'unknown'))
        context = request.get('context', {})

        # Find best extension for this capability
        if self.capability_router:
            extension_name = await self.capability_router.find_optimal_extension(capability, context)
        else:
            # Simple fallback: find any extension that supports this capability
            extension_name = None
            for ext_name, ext_info in self.extensions.items():
                if capability in ext_info.capabilities:
                    extension_name = ext_name
                    break

        if not extension_name:
            return {
                'success': False,
                'error': f'No extension available for capability: {capability}',
                'capability': capability
            }

        # Ensure extension is loaded
        if self.extensions[extension_name].status != "active":
            load_result = await self.load_extension(extension_name)
            if not load_result.success:
                return {
                    'success': False,
                    'error': f'Failed to load extension: {load_result.error}',
                    'extension': extension_name
                }

        # Process request
        extension_info = self.extensions[extension_name]
        instance = extension_info.instance

        try:
            # Call the extension
            start_time = asyncio.get_event_loop().time()

            if inspect.iscoroutinefunction(instance.process_request):
                result = await instance.process_request(request, context)
            else:
                result = instance.process_request(request, context)

            end_time = asyncio.get_event_loop().time()
            latency_ms = (end_time - start_time) * 1000

            # Record attribution if engine available
            attribution_record = None
            if self.attribution_engine:
                attribution_record = self.attribution_engine.record_usage(
                    extension=extension_name,
                    capability=capability,
                    user_id=request.get('user_id'),
                    quality_score=result.get('quality_score', result.get('confidence', 0.0)),
                    usage_context=json.dumps(context)[:200],  # Limit context size
                    latency_ms=latency_ms
                )

            # Update last used
            extension_info.last_used = asyncio.get_event_loop().time()

            # Prepare response
            response = {
                'success': True,
                'extension': extension_name,
                'capability': capability,
                'latency_ms': latency_ms,
                'result': result
            }

            # Add attribution info
            if attribution_record:
                response['attribution'] = {
                    'required': True,
                    'text': attribution_record.attribution_text,
                    'extension': extension_name
                }

            return response

        except Exception as e:
            logger.error(f"   ❌ Extension {extension_name} failed: {e}")

            # Record failed usage
            if self.attribution_engine:
                self.attribution_engine.record_usage(
                    extension=extension_name,
                    capability=capability,
                    user_id=request.get('user_id'),
                    quality_score=0.0,
                    usage_context=f"Error: {str(e)}",
                    latency_ms=0
                )

            return {
                'success': False,
                'extension': extension_name,
                'capability': capability,
                'error': str(e)
            }

    def get_extension_status(self, extension_name: str = None) -> Dict[str, Any]:
        """Get status of extensions"""
        if extension_name:
            if extension_name not in self.extensions:
                return {'error': 'Extension not found'}

            ext_info = self.extensions[extension_name]
            return {
                'name': ext_info.name,
                'status': ext_info.status,
                'capabilities': ext_info.capabilities,
                'last_used': ext_info.last_used,
                'metadata': ext_info.metadata
            }

        # Return all extensions
        return {
            'extensions': {
                name: {
                    'status': info.status,
                    'capabilities': info.capabilities,
                    'last_used': info.last_used
                }
                for name, info in self.extensions.items()
            },
            'capabilities_map': self.capabilities_map,
            'total_extensions': len(self.extensions),
            'active_extensions': len([e for e in self.extensions.values() if e.status == 'active'])
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all extensions"""
        results = {}

        for name, ext_info in self.extensions.items():
            health_result = {'status': 'unknown', 'details': {}}

            if ext_info.instance and hasattr(ext_info.instance, 'health_check'):
                try:
                    if inspect.iscoroutinefunction(ext_info.instance.health_check):
                        health_result = await ext_info.instance.health_check()
                    else:
                        health_result = ext_info.instance.health_check()
                except Exception as e:
                    health_result = {'status': 'error', 'details': {'error': str(e)}}
            else:
                # Basic health check
                health_result = {
                    'status': 'ok' if ext_info.status == 'active' else 'inactive',
                    'details': {'registered': True, 'loaded': ext_info.instance is not None}
                }

            results[name] = health_result

        return {
            'timestamp': asyncio.get_event_loop().time(),
            'extensions_health': results,
            'overall_status': 'healthy' if all(r['status'] == 'ok' for r in results.values()) else 'degraded'
        }

    async def reload_extension(self, extension_name: str) -> IntegrationResult:
        """Reload an extension (unload and reload)"""
        # Unload first
        unload_result = await self.unload_extension(extension_name)
        if not unload_result.success:
            return unload_result

        # Reload
        load_result = await self.load_extension(extension_name)
        return load_result

    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get summary of all available capabilities"""
        capabilities = {}
        extensions_by_capability = {}

        for ext_name, ext_info in self.extensions.items():
            for capability in ext_info.capabilities:
                if capability not in capabilities:
                    capabilities[capability] = []
                    extensions_by_capability[capability] = []

                capabilities[capability].append({
                    'extension': ext_name,
                    'status': ext_info.status
                })

                extensions_by_capability[capability].append(ext_name)

        return {
            'capabilities': list(capabilities.keys()),
            'capability_count': len(capabilities),
            'extensions_by_capability': extensions_by_capability,
            'total_mappings': sum(len(exts) for exts in extensions_by_capability.values())
        }


# Global instance
_integration_manager = None


def get_integration_manager() -> JarvisIntegrationManager:
    """Get or create integration manager instance"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = JarvisIntegrationManager()
    return _integration_manager


async def initialize_integration_framework() -> bool:
    """Initialize the complete integration framework"""
    manager = get_integration_manager()

    # Auto-discover extensions
    discovery_results = await manager.auto_discover_extensions()

    successful_registrations = sum(1 for r in discovery_results if r.success)
    total_discovered = len(discovery_results)

    logger.info(f"   🔍 Extension Discovery: {successful_registrations}/{total_discovered} successful")

    # Load active extensions
    loaded_count = 0
    for name in manager.extensions.keys():
        load_result = await manager.load_extension(name)
        if load_result.success:
            loaded_count += 1

    logger.info(f"   🚀 Extension Loading: {loaded_count}/{len(manager.extensions)} loaded")

    return loaded_count > 0


async def process_integration_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to process integration requests"""
    manager = get_integration_manager()
    return await manager.process_request(request)


if __name__ == "__main__":
    # Test the integration manager
    import asyncio

    async def test():
        print("🔧 **Jarvis Integration Manager Test**")
        print("=" * 50)

        manager = get_integration_manager()

        # Initialize framework
        print("\n🚀 Initializing Framework...")
        success = await initialize_integration_framework()
        print(f"   Framework initialized: {success}")

        # Get status
        status = manager.get_extension_status()
        print("\n📊 Extension Status:")
        print(f"   Total Extensions: {status['total_extensions']}")
        print(f"   Active Extensions: {status['active_extensions']}")

        # Get capabilities
        capabilities = manager.get_capabilities_summary()
        print("\n🔧 Capabilities:")
        print(f"   Total Capabilities: {capabilities['capability_count']}")

        # Test request processing
        if status['total_extensions'] > 0:
            print("\n🧪 Testing Request Processing...")
            test_request = {
                'capability': 'code_completion',
                'language': 'python',
                'context': 'def hello_world():',
                'user_id': 'test_user'
            }

            result = await manager.process_request(test_request)
            print(f"   Test Result: {'✅ Success' if result.get('success') else '❌ Failed'}")

            if result.get('success'):
                print(f"   Extension Used: {result.get('extension')}")
                print(f"   Latency: {result.get('latency_ms', 0):.1f}ms")

    asyncio.run(test())