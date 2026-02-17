#!/usr/bin/env python3
"""
Deploy Iron Legion Router via DSM Container Manager using Neo Browser Automation
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from neo_browser_automation_engine import NeoBrowserAutomationEngine
except ImportError:
    print("Neo browser automation not found, trying alternative...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        USE_SELENIUM = True
    except ImportError:
        print("Selenium not available, trying Playwright...")
        try:
            from playwright.sync_api import sync_playwright
            USE_PLAYWRIGHT = True
        except ImportError:
            print("No browser automation available")
            sys.exit(1)

def deploy_via_dsm():
    """Deploy router via DSM Container Manager GUI"""

    nas_ip = "<NAS_PRIMARY_IP>"
    dsm_url = f"https://{nas_ip}:5001"
    project_path = "/volume1/docker/iron-legion-router"

    print(f"Opening DSM: {dsm_url}")
    print(f"Project path: {project_path}")

    try:
        if 'NeoBrowserAutomationEngine' in globals():
            neo = NeoBrowserAutomationEngine()
            neo.open_url(dsm_url)
            # Navigate to Container Manager
            neo.click_element("//a[contains(text(), 'Container Manager')]")
            # Navigate to Project tab
            neo.click_element("//button[contains(text(), 'Project')]")
            # Click Create
            neo.click_element("//button[contains(text(), 'Create')]")
            # Select docker-compose.yml
            neo.click_element(f"//input[@value='{project_path}']")
            # Click Deploy
            neo.click_element("//button[contains(text(), 'Deploy')]")
            print("✅ Deployment initiated via Neo")

        elif USE_SELENIUM:
            chrome_options = Options()
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            driver = webdriver.Chrome(options=chrome_options)

            driver.get(dsm_url)
            # Login if needed
            # Navigate to Container Manager
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Container Manager"))
            ).click()

            # Project tab
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Project')]"))
            ).click()

            # Create project
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Create')]"))
            ).click()

            # Select path
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//input[@value='{project_path}']"))
            ).click()

            # Deploy
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Deploy')]"))
            ).click()

            print("✅ Deployment initiated via Selenium")
            driver.quit()

        elif USE_PLAYWRIGHT:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()

                page.goto(dsm_url)
                # Login if needed
                page.click("text=Container Manager")
                page.click("button:has-text('Project')")
                page.click("button:has-text('Create')")
                page.fill(f"input[value='{project_path}']", project_path)
                page.click("button:has-text('Deploy')")

                print("✅ Deployment initiated via Playwright")
                browser.close()

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Deploying Iron Legion Router via DSM...")
    success = deploy_via_dsm()
    if success:
        print("✅ Deployment complete")
    else:
        print("❌ Deployment failed")
