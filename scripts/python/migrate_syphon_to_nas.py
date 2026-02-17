import os
import shutil
import json
from pathlib import Path

def migrate_to_nas():
    project_root = Path(__file__).parent.parent.parent
    policy_file = project_root / "config" / "storage_policy.json"
    
    if not policy_file.exists():
        print("❌ Storage policy file not found.")
        return

    with open(policy_file, "r") as f:
        policy = json.load(f)

    if not policy.get("zero_local_storage_enforced"):
        print("ℹ️  Zero local storage policy not enforced. Skipping migration.")
        return

    nas_root = Path(policy["nas_paths"]["root"])
    
    # Check if NAS is accessible
    if not os.path.exists(nas_root.parent):
        print(f"❌ NAS root parent {nas_root.parent} is not accessible. Is the drive mapped?")
        return

    mappings = [
        (project_root / "data" / "syphon", Path(policy["nas_paths"]["syphon_raw"])),
        (project_root / "data" / "syphon_intelligence", Path(policy["nas_paths"]["syphon_intelligence"])),
        (project_root / "data" / "syphon_lumina_hourly", Path(policy["nas_paths"]["syphon_raw"])),
    ]

    for local_dir, nas_dir in mappings:
        if local_dir.exists():
            print(f"📦 Migrating {local_dir} -> {nas_dir}")
            nas_dir.mkdir(parents=True, exist_ok=True)
            
            for item in local_dir.iterdir():
                if item.is_file():
                    target = nas_dir / item.name
                    print(f"  📄 Moving {item.name}")
                    shutil.copy2(item, target)
                    # item.unlink() # Delete after copy verified
            
            print(f"✅ Migration of {local_dir.name} complete.")
            # shutil.rmtree(local_dir) # Delete local dir after copy verified
        else:
            print(f"ℹ️  Local directory {local_dir} does not exist. Skipping.")

if __name__ == "__main__":
    migrate_to_nas()
