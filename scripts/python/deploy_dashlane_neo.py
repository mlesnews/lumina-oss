import sys
import os
import json
import requests
import zipfile
from pathlib import Path

# Add scripts/python to path
LUMINA_ROOT = Path(os.environ.get("LUMINA_ROOT", str(Path.home() / "lumina")))
script_dir = LUMINA_ROOT / "scripts" / "python"
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DashlaneNeoIntegration")

DASHLANE_EXTENSION_ID = "fdjamakpfbbddfjaooikfcpapjohcfmg"
EXTENSION_URL = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=114.0&acceptformat=crx2,crx3&x=id%3D{DASHLANE_EXTENSION_ID}%26uc"

def deploy_dashlane_to_neo():
    project_root = LUMINA_ROOT
    extension_dir = project_root / "data" / "extensions" / "dashlane"
    extension_dir.mkdir(parents=True, exist_ok=True)

    crx_file = extension_dir / "dashlane.crx"
    zip_file = extension_dir / "dashlane.zip"

    print("\n📦 Deploying Dashlane Extension to Neo Browser Environment")
    print("=" * 60)

    # 1. Download Extension
    if not (extension_dir / "manifest.json").exists():
        print(f"🔍 Downloading Dashlane extension ({DASHLANE_EXTENSION_ID})...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(EXTENSION_URL, headers=headers, timeout=30)
            response.raise_for_status()

            with open(crx_file, 'wb') as f:
                f.write(response.content)

            # 2. Extract CRX (it's basically a ZIP with a header)
            # We convert to ZIP by stripping the header if necessary, but most zip libraries handle it
            # Actually, standard zipfile might fail if header is present.
            # Simple workaround: just rename and try, or use a tool.
            shutil = __import__('shutil')
            shutil.copy(crx_file, zip_file)

            print(f"📦 Extracting extension to {extension_dir}...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extension_dir)

            print("✅ Extension extracted successfully.")
        except Exception as e:
            print(f"❌ Failed to download or extract extension: {e}")
            return False
    else:
        print("✅ Dashlane extension already exists in data/extensions/dashlane")

    # 3. Update NEO Automation Engine Config
    print("\n🛠️  Updating NEO Automation Engine to load Dashlane...")
    engine_file = project_root / "scripts" / "python" / "neo_browser_automation_engine.py"

    if engine_file.exists():
        with open(engine_file, 'r', encoding='utf-8') as f:
            content = f.read()

        load_flag = f"--load-extension={extension_dir.absolute()}"
        if load_flag not in content:
            # Inject the flag into the launch arguments
            # Finding the list of args
            if 'args.extend([' in content:
                new_content = content.replace(
                    'args.extend([',
                    f'args.extend([\n                "{load_flag}",'
                )
                with open(engine_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("✅ Updated neo_browser_automation_engine.py with Dashlane extension path.")
            else:
                print("⚠️  Could not automatically inject flag into engine script. Manual update required.")
        else:
            print("✅ NEO engine already configured to load Dashlane.")

    print("\n🏁 Deployment complete. Neo Browser will now load Dashlane on next launch.")
    return True

if __name__ == "__main__":
    deploy_dashlane_to_neo()
