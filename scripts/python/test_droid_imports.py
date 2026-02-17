"""Test droid system imports"""
import sys
from pathlib import Path

# Add current directory to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

print("Testing imports...")
print(f"Python path: {sys.path[:3]}")

try:
    print("\n1. Testing droid_actor_system import...")
    from droid_actor_system import DroidActorSystem, verify_workflow_with_droid_actor
    print("   ✓ droid_actor_system imported successfully")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. Testing v3_verification import...")
    from v3_verification import V3VerificationSystem, V3Verification
    print("   ✓ v3_verification imported successfully")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. Testing r5_living_context_matrix import...")
    from r5_living_context_matrix import R5LivingContextMatrix
    print("   ✓ r5_living_context_matrix imported successfully")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n4. Testing jarvis_helpdesk_integration import...")
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    print("   ✓ jarvis_helpdesk_integration imported successfully")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\nImport test complete!")

