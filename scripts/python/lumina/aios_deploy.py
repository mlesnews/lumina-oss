#!/usr/bin/env python3
"""
AIOS Deployment and Activation Script

Deploy and activate AIOS - AI Operating System.

Usage:
    python aios_deploy.py --deploy
    python aios_deploy.py --activate
    python aios_deploy.py --status
    python aios_deploy.py --test

Tags: #DEPLOYMENT #ACTIVATION #AIOS @JARVIS @LUMINA
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIOSDeploy")


def check_prerequisites() -> bool:
    """Check if all prerequisites are met"""
    logger.info("🔍 Checking prerequisites...")

    issues = []

    # Check Python version
    if sys.version_info < (3, 11):
        issues.append(f"Python 3.11+ required, found {sys.version}")

    # Check project structure
    if not (project_root / "scripts" / "python" / "lumina").exists():
        issues.append("Lumina directory not found")

    # Check Docker (optional)
    try:
        import docker
    except ImportError:
        logger.warning("Docker not available (optional for infrastructure)")

    if issues:
        logger.error("❌ Prerequisites not met:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False

    logger.info("✅ All prerequisites met")
    return True


def deploy_aios() -> bool:
    """Deploy AIOS"""
    logger.info("🚀 Deploying AIOS...")

    try:
        # Import AIOS
        from lumina.aios import AIOS

        # Initialize (this deploys all components)
        logger.info("Initializing AIOS components...")
        aios = AIOS()

        # Verify deployment
        status = aios.get_status()

        # Count active components
        active = sum(
            sum(1 for v in layer.values() if v is True or (isinstance(v, str) and 'Available' in v))
            for layer in status.values()
            if isinstance(layer, dict)
        )

        logger.info(f"✅ AIOS deployed - {active} components active")
        return True

    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}", exc_info=True)
        return False


def activate_aios() -> bool:
    """Activate AIOS"""
    logger.info("⚡ Activating AIOS...")

    try:
        from lumina.aios import AIOS

        # Initialize and activate
        aios = AIOS()

        # Verify activation
        status = aios.get_status()

        if status['initialized']:
            logger.info("✅ AIOS activated successfully")

            # Test activation
            test_result = aios.execute("test", use_flow=False, use_pegl=False)
            if test_result:
                logger.info("✅ Activation test passed")

            return True
        else:
            logger.error("❌ AIOS not properly initialized")
            return False

    except Exception as e:
        logger.error(f"❌ Activation failed: {e}", exc_info=True)
        return False


def get_status() -> dict:
    """Get AIOS status"""
    try:
        from lumina.aios import AIOS

        aios = AIOS()
        return aios.get_status()

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {'error': str(e)}


def test_aios() -> bool:
    """Test AIOS functionality"""
    logger.info("🧪 Testing AIOS...")

    try:
        from lumina.aios import AIOS

        aios = AIOS()

        # Test 1: Status check
        logger.info("Test 1: Status check")
        status = aios.get_status()
        assert status['initialized'], "AIOS not initialized"
        logger.info("✅ Status check passed")

        # Test 2: Knowledge access
        logger.info("Test 2: Knowledge access")
        if aios.library:
            knowledge = aios.library.knowledge("balance")
            logger.info("✅ Knowledge access working")
        else:
            logger.warning("⚠️  Knowledge layer not available")

        # Test 3: Inference
        logger.info("Test 3: Inference")
        if aios.reality:
            inference = aios.reality.infer("test query", maintain_balance=True)
            logger.info("✅ Inference working")
        else:
            logger.warning("⚠️  Inference layer not available")

        # Test 4: Execution
        logger.info("Test 4: Execution")
        result = aios.execute("balance", use_flow=False, use_pegl=False)
        assert result is not None, "Execution failed"
        logger.info("✅ Execution working")

        logger.info("✅ All tests passed")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


def print_status(status: dict):
    """Print formatted status"""
    print("\n" + "=" * 80)
    print("AIOS STATUS")
    print("=" * 80)

    for layer_name, layer_data in status.items():
        if layer_name == 'initialized':
            print(f"\nInitialized: {'✅' if layer_data else '❌'}")
            continue

        if not isinstance(layer_data, dict):
            continue

        print(f"\n{layer_name.upper().replace('_', ' ')}:")
        for component, available in layer_data.items():
            if isinstance(available, bool):
                icon = "✅" if available else "❌"
            elif isinstance(available, str):
                icon = "✅" if "Available" in available else "❌"
            else:
                icon = "❓"
            print(f"  {icon} {component}")


def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description="AIOS Deployment and Activation")
    parser.add_argument("--deploy", action="store_true", help="Deploy AIOS")
    parser.add_argument("--activate", action="store_true", help="Activate AIOS")
    parser.add_argument("--status", action="store_true", help="Get AIOS status")
    parser.add_argument("--test", action="store_true", help="Test AIOS")
    parser.add_argument("--check-prerequisites", action="store_true", help="Check prerequisites")

    args = parser.parse_args()

    if args.check_prerequisites:
        success = check_prerequisites()
        sys.exit(0 if success else 1)

    if args.deploy:
        success = deploy_aios()
        sys.exit(0 if success else 1)

    if args.activate:
        success = activate_aios()
        sys.exit(0 if success else 1)

    if args.status:
        status = get_status()
        print_status(status)
        sys.exit(0)

    if args.test:
        success = test_aios()
        sys.exit(0 if success else 1)

    # Default: show status
    print("AIOS Deployment and Activation Script")
    print("\nUsage:")
    print("  python aios_deploy.py --deploy              # Deploy AIOS")
    print("  python aios_deploy.py --activate            # Activate AIOS")
    print("  python aios_deploy.py --status              # Get status")
    print("  python aios_deploy.py --test                # Test AIOS")
    print("  python aios_deploy.py --check-prerequisites # Check prerequisites")
    print("\nOr run all:")
    print("  python aios_deploy.py --deploy --activate --test")


if __name__ == "__main__":


    main()