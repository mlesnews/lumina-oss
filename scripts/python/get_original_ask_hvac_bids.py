"""
Get Original @ASK for HVAC Bids
Retrieves the original @ASK request (c1fa7198-7bf3-46ae-8865-2a67f0085988) 
from the @ASK database system.

#JARVIS #LUMINA #ASK
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ask_database_integrated_system import ASKDatabaseSystem
except ImportError:
    print("⚠ @ASK database system not found. Trying alternative methods...")
    ASKDatabaseSystem = None

def search_ask_cache(request_id: str, project_root: Path) -> dict:
    """Search ask_cache for the request ID."""
    ask_cache_dir = project_root / "data" / "ask_cache"

    if not ask_cache_dir.exists():
        return {}

    # Search discovered_asks.json (may be large, so we'll search in chunks)
    discovered_file = ask_cache_dir / "discovered_asks.json"
    if discovered_file.exists():
        try:
            # Try to read and search
            print(f"Searching {discovered_file.name} for Request ID: {request_id}")
            # File is too large, use grep instead
            import subprocess
            result = subprocess.run(
                ["grep", "-i", request_id, str(discovered_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                # Found it, try to extract JSON
                lines = result.stdout.split('\n')
                for line in lines[:5]:  # Check first few matches
                    if request_id.lower() in line.lower():
                        try:
                            # Try to parse as JSON
                            data = json.loads(line)
                            return data
                        except:
                            # Try to extract JSON from line
                            import re
                            json_match = re.search(r'\{.*\}', line)
                            if json_match:
                                try:
                                    return json.loads(json_match.group())
                                except:
                                    pass
        except Exception as e:
            print(f"Error searching discovered_asks.json: {e}")

    return {}

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent.parent
    request_id = "c1fa7198-7bf3-46ae-8865-2a67f0085988"

    print("="*80)
    print("RETRIEVING ORIGINAL @ASK FOR HVAC BIDS")
    print("="*80)
    print(f"\nRequest ID: {request_id}")
    print("\nSearching @ASK database...")

    # Try @ASK database system
    if ASKDatabaseSystem:
        try:
            ask_db = ASKDatabaseSystem(project_root)
            # Try to get by request ID
            result = ask_db.get_ask_by_id(request_id)
            if result:
                print("\n✓ Found @ASK in database!")
                print(f"\n@ASK Details:")
                print(json.dumps(result, indent=2, default=str))
                return
        except Exception as e:
            print(f"⚠ Error querying @ASK database: {e}")

    # Try ask_cache
    print("\nSearching ask_cache...")
    result = search_ask_cache(request_id, project_root)

    if result:
        print("\n✓ Found @ASK in cache!")
        print(f"\n@ASK Details:")
        print(json.dumps(result, indent=2, default=str))

        # Save to HVAC bids directory
        output_file = project_root / "data" / "hvac_bids" / f"original_ask_{request_id}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n✓ Saved to: {output_file}")
    else:
        print("\n⚠ @ASK not found in cache.")
        print("\nThe original @ASK may be:")
        print("  1. In the @ASK database (enhanced_memory.db)")
        print("  2. In ask_cache/discovered_asks.json (file is very large)")
        print("  3. In another @ASK storage location")
        print("\nYou can also search Gmail directly using the Request ID:")
        print(f"  Search: {request_id} has:attachment")

if __name__ == "__main__":


    main()