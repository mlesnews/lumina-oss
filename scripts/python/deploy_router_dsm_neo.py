#!/usr/bin/env python3
"""
Deploy Iron Legion Router via DSM Container Manager using Neo Browser Automation
"""

import sys
from pathlib import Path
import time

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

from neo_browser_automation_engine import NEOBrowserAutomationEngine

def deploy_via_dsm():
    """Deploy router via DSM Container Manager GUI using Neo"""

    nas_ip = "<NAS_PRIMARY_IP>"
    dsm_url = f"https://{nas_ip}:5001"
    project_path = "/volume1/docker/iron-legion-router"

    print(f"🚀 Deploying Iron Legion Router via DSM")
    print(f"   NAS: {dsm_url}")
    print(f"   Project: {project_path}")
    print()

    try:
        # Initialize Neo
        neo = NEOBrowserAutomationEngine(project_root)

        # Launch browser
        print("Opening DSM in Neo browser...")
        neo.launch(url=dsm_url, headless=False)
        time.sleep(5)  # Wait for page load

        # Navigate to Container Manager
        print("Navigating to Container Manager...")
        neo.navigate(f"{dsm_url}/#/ContainerManager")
        time.sleep(3)

        # Wait for page to load
        print("Waiting for DSM to load...")
        neo.wait_for_navigation(timeout=30)
        time.sleep(3)

        # Click Project tab
        print("Opening Project tab...")
        neo.execute_script("""
            var projectBtn = Array.from(document.querySelectorAll('button, a, [role="button"]')).find(el => {
                var text = (el.textContent || el.innerText || '').toLowerCase();
                return text.includes('project');
            });
            if (projectBtn) {
                projectBtn.click();
                return true;
            }
            return false;
        """)
        time.sleep(5)

        # Click Create button
        print("Clicking Create...")
        neo.execute_script("""
            var createBtn = Array.from(document.querySelectorAll('button, [role="button"]')).find(el => {
                var text = (el.textContent || el.innerText || '').toLowerCase();
                return text.includes('create') || text.includes('new');
            });
            if (createBtn) {
                createBtn.click();
                return true;
            }
            return false;
        """)
        time.sleep(5)

        # Select "From docker-compose.yml" option
        print("Selecting docker-compose.yml option...")
        neo.execute_script("""
            var composeOption = Array.from(document.querySelectorAll('button, option, div[role="button"], label')).find(el => {
                var text = (el.textContent || el.innerText || '').toLowerCase();
                return text.includes('docker-compose') || text.includes('compose') || text.includes('yml');
            });
            if (composeOption) {
                composeOption.click();
                return true;
            }
            return false;
        """)
        time.sleep(3)

        # Enter project path
        print(f"Entering project path: {project_path}")
        neo.execute_script(f"""
            var inputs = document.querySelectorAll('input[type="text"], input[type="path"], input');
            var filled = false;
            for (var i = 0; i < inputs.length; i++) {{
                var placeholder = (inputs[i].placeholder || '').toLowerCase();
                if (inputs[i].value === '' || placeholder.includes('path') || placeholder.includes('directory')) {{
                    inputs[i].value = '{project_path}';
                    inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    inputs[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    filled = true;
                    break;
                }}
            }}
            return filled;
        """)
        time.sleep(3)

        # Click Deploy/Start button
        print("Starting deployment...")
        deployed = neo.execute_script("""
            var deployBtn = Array.from(document.querySelectorAll('button, [role="button"]')).find(el => {
                var text = (el.textContent || el.innerText || '').toLowerCase();
                return text.includes('deploy') || text.includes('start') || text.includes('create') || 
                       text.includes('apply') || el.className.toLowerCase().includes('deploy');
            });
            if (deployBtn) {
                deployBtn.click();
                return true;
            }
            return false;
        """)
        time.sleep(10)

        # Wait for deployment to start
        print("Waiting for deployment to initialize...")
        time.sleep(10)

        # Check deployment status
        print("Checking deployment status...")
        status = neo.get_element_text("//div[contains(@class, 'status')] | //span[contains(@class, 'status')]")
        if status:
            print(f"   Status: {status}")

        print()
        print("✅ Deployment initiated via DSM Container Manager")
        print(f"   Check Container Manager for progress")
        print(f"   Router will be available at: http://{nas_ip}:3000")

        # Keep browser open for monitoring
        print()
        print("Browser will remain open for monitoring...")
        print("Press Ctrl+C to close when done")

        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nClosing browser...")
            neo.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    print("=" * 80)
    print("Iron Legion Router - DSM Deployment via Neo")
    print("=" * 80)
    print()

    success = deploy_via_dsm()

    print()
    print("=" * 80)
    if success:
        print("✅ Deployment Complete")
    else:
        print("❌ Deployment Failed")
    print("=" * 80)
