#!/usr/bin/env python3
"""
MANUS-NEO Browser Automation System

Uses local AI + browser automation to complete tasks like:
- Account signups
- Form filling
- API key retrieval
- Automated web interactions

Integration:
- Local LLM (Ollama/other) for decision-making
- Playwright for browser control
- NEO browser support (when available)
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MANUS-NEO")

try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️  Playwright not installed. Install: pip install playwright && playwright install")


class LocalAIController:
    """
    Local AI controller for browser automation decisions

    Can use Ollama, LM Studio, or other local LLM APIs
    """

    def __init__(self, api_url: str = None, model: str = None):
        self.api_url = api_url or os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
        self.model = model or os.getenv("LOCAL_LLM_MODEL", "llama3")
        self.available = False
        self._check_availability()

    def _check_availability(self):
        """Check if local LLM is available"""
        try:
            import requests
            # Try Ollama first
            response = requests.get(f"{self.api_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.available = True
                logger.info(f"✅ Local LLM available: {self.api_url} ({self.model})")
                return
        except:
            pass

        # Try LM Studio
        try:
            import requests
            response = requests.get("http://localhost:1234/v1/models", timeout=2)
            if response.status_code == 200:
                self.api_url = "http://localhost:1234/v1"
                self.available = True
                logger.info(f"✅ Local LLM available: LM Studio")
                return
        except:
            pass

        logger.warning("⚠️  Local LLM not available - will use rule-based logic")

    def decide_action(self, context: str, available_actions: List[str]) -> Dict[str, Any]:
        """
        Use local AI to decide next browser action

        Args:
            context: Current page context/state
            available_actions: List of possible actions

        Returns:
            Dict with chosen action and reasoning
        """
        if not self.available:
            # Fallback to simple rule-based logic
            return self._rule_based_decision(context, available_actions)

        prompt = f"""You are controlling a browser to complete a task. 

Current context:
{context}

Available actions:
{json.dumps(available_actions, indent=2)}

Choose the next action. Respond with JSON:
{{
    "action": "action_name",
    "element": "selector or description",
    "value": "value to enter if needed",
    "reasoning": "why this action"
}}
"""

        try:
            import requests

            # Ollama format
            if "11434" in self.api_url:
                response = requests.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("response", "")
                    # Extract JSON from response
                    return self._extract_json(text)

            # LM Studio format (OpenAI-compatible)
            elif "1234" in self.api_url:
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    text = result["choices"][0]["message"]["content"]
                    return self._extract_json(text)
        except Exception as e:
            logger.debug(f"AI decision failed: {e}")

        # Fallback
        return self._rule_based_decision(context, available_actions)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
        import re
        # Try to find JSON block
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass

        # Default fallback
        return {"action": "wait", "reasoning": "Could not parse AI response"}

    def _rule_based_decision(self, context: str, available_actions: List[str]) -> Dict[str, Any]:
        """Rule-based fallback decision logic"""
        context_lower = context.lower()

        # Look for signup/sign in buttons
        if "sign up" in context_lower or "register" in context_lower:
            for action in available_actions:
                if "signup" in action.lower() or "register" in action.lower():
                    return {"action": "click", "element": action, "reasoning": "Found signup button"}

        # Look for email fields
        if "email" in context_lower:
            return {"action": "fill", "element": "email", "value": "user@example.com", "reasoning": "Fill email field"}

        # Default: wait
        return {"action": "wait", "duration": 1, "reasoning": "Analyzing page"}


class MANUSNEOBrowser:
    """
    MANUS-NEO Browser Automation

    Controls browser with local AI decision-making
    """

    def __init__(self, headless: bool = False, ai_controller: LocalAIController = None):
        self.headless = headless
        self.ai = ai_controller or LocalAIController()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed. Run: pip install playwright && playwright install")

    def start(self):
        """Start browser"""
        logger.info("🌐 Starting MANUS-NEO Browser...")
        self.playwright = sync_playwright().start()

        # Try to use system Chrome/Edge (NEO if available)
        try:
            # Try Chromium first (built-in)
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            logger.info("   ✅ Using Chromium")
        except:
            try:
                # Try Chrome
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    channel="chrome"
                )
                logger.info("   ✅ Using Chrome")
            except:
                # Fallback to Chromium
                self.browser = self.playwright.chromium.launch(headless=self.headless)
                logger.info("   ✅ Using Chromium (fallback)")

        self.page = self.browser.new_page()
        logger.info("   ✅ Browser ready")

    def navigate(self, url: str):
        """Navigate to URL"""
        logger.info(f"🔗 Navigating to: {url}")
        self.page.goto(url, wait_until="networkidle")
        time.sleep(2)  # Let page settle

    def get_page_context(self) -> str:
        """Get current page context for AI"""
        try:
            title = self.page.title()
            url = self.page.url

            # Get all interactive elements
            elements = self.page.query_selector_all("button, a, input, select, textarea")

            element_info = []
            for el in elements[:20]:  # Limit to first 20
                try:
                    text = el.inner_text()[:50]
                    tag = el.evaluate("el => el.tagName.toLowerCase()")
                    visible = el.is_visible()
                    if visible and text.strip():
                        element_info.append(f"{tag}: '{text.strip()}'")
                except:
                    continue

            context = f"""
Page: {title}
URL: {url}
Interactive Elements:
{chr(10).join(element_info)}
"""
            return context
        except Exception as e:
            return f"Error getting context: {e}"

    def find_elements(self, selector: str = None) -> List[Dict[str, Any]]:
        """Find elements on page"""
        elements = []

        try:
            if selector:
                found = self.page.query_selector_all(selector)
            else:
                found = self.page.query_selector_all("button, a, input[type='submit'], input[type='button']")

            for el in found:
                try:
                    if el.is_visible():
                        text = el.inner_text()[:100]
                        tag = el.evaluate("el => el.tagName.toLowerCase()")
                        el_id = el.get_attribute("id") or ""
                        el_class = el.get_attribute("class") or ""

                        elements.append({
                            "tag": tag,
                            "text": text.strip(),
                            "id": el_id,
                            "class": el_class,
                            "selector": f"{tag}" + (f"#{el_id}" if el_id else "") + (f".{el_class.split()[0]}" if el_class else "")
                        })
                except:
                    continue
        except Exception as e:
            logger.debug(f"Element finding error: {e}")

        return elements

    def execute_ai_action(self, action: Dict[str, Any]) -> bool:
        """Execute an AI-decided action"""
        action_type = action.get("action", "wait")
        element_desc = action.get("element", "")
        value = action.get("value", "")

        logger.info(f"🤖 AI Action: {action_type} - {element_desc}")
        logger.info(f"   Reasoning: {action.get('reasoning', 'N/A')}")

        try:
            if action_type == "click":
                # Try to find and click element
                elements = self.find_elements()
                for el_info in elements:
                    if element_desc.lower() in el_info["text"].lower() or element_desc in el_info["selector"]:
                        # Click it
                        el = self.page.query_selector(el_info["selector"])
                        if el:
                            el.click()
                            time.sleep(2)
                            logger.info(f"   ✅ Clicked: {el_info['text']}")
                            return True

            elif action_type == "fill":
                # Fill input field
                input_el = self.page.query_selector(f"input[type='{element_desc}'], input[name*='{element_desc}'], input[placeholder*='{element_desc}']")
                if input_el:
                    input_el.fill(value)
                    time.sleep(0.5)
                    logger.info(f"   ✅ Filled: {element_desc}")
                    return True

            elif action_type == "wait":
                duration = action.get("duration", 1)
                time.sleep(duration)
                return True

            return False
        except Exception as e:
            logger.debug(f"Action execution error: {e}")
            return False

    def automate_elevenlabs_signup(self, email: str, password: str) -> Dict[str, Any]:
        """
        Automate ElevenLabs account signup

        Args:
            email: Email for account
            password: Password for account

        Returns:
            Dict with success status and API key if successful
        """
        logger.info("🎙️  Starting ElevenLabs signup automation...")

        try:
            # Navigate to signup page
            self.navigate("https://elevenlabs.io")
            time.sleep(3)

            # Look for signup button
            signup_buttons = self.page.query_selector_all("a, button")
            for btn in signup_buttons:
                try:
                    text = btn.inner_text().lower()
                    if "sign up" in text or "signup" in text or "register" in text:
                        btn.click()
                        logger.info("   ✅ Clicked signup button")
                        time.sleep(3)
                        break
                except:
                    continue

            # Get current page context
            context = self.get_page_context()
            logger.info(f"📄 Page context:\n{context[:500]}")

            # AI-driven form filling
            max_steps = 10
            for step in range(max_steps):
                # Find available actions
                elements = self.find_elements()
                action_list = [f"{e['text']} ({e['tag']})" for e in elements]

                # Get AI decision
                decision = self.ai.decide_action(context, action_list)

                # Execute action
                if not self.execute_ai_action(decision):
                    logger.warning(f"   ⚠️  Action failed at step {step+1}")

                # Check if we're done (reached API key page)
                current_url = self.page.url
                if "api-key" in current_url.lower() or "profile" in current_url.lower():
                    logger.info("   ✅ Reached API key page!")
                    # Try to extract API key
                    api_key = self._extract_api_key()
                    if api_key:
                        return {
                            "success": True,
                            "api_key": api_key,
                            "message": "Account created and API key retrieved"
                        }

                # Update context
                context = self.get_page_context()
                time.sleep(2)

            return {
                "success": False,
                "error": "Signup automation incomplete - manual steps may be required",
                "current_url": self.page.url
            }

        except Exception as e:
            logger.error(f"❌ Signup automation failed: {e}")
            return {"success": False, "error": str(e)}

    def _extract_api_key(self) -> Optional[str]:
        """Extract API key from page"""
        try:
            # Look for API key in page content
            page_text = self.page.inner_text("body")

            # Common patterns
            import re
            patterns = [
                r'api[_-]?key["\s:]+([a-zA-Z0-9_-]{20,})',
                r'sk[-_][a-zA-Z0-9_-]{20,}',
                r'[a-f0-9]{32,}',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    # Return longest match (likely the key)
                    key = max(matches, key=len)
                    if len(key) > 20:  # Reasonable key length
                        logger.info(f"   ✅ Found potential API key: {key[:20]}...")
                        return key

            # Look for input fields with API key
            inputs = self.page.query_selector_all("input[type='text'], input[readonly], code, pre")
            for inp in inputs:
                try:
                    value = inp.input_value() if hasattr(inp, 'input_value') else inp.inner_text()
                    if len(value) > 20 and any(c.isalnum() for c in value):
                        logger.info(f"   ✅ Found potential API key in input")
                        return value.strip()
                except:
                    continue

            return None
        except Exception as e:
            logger.debug(f"API key extraction error: {e}")
            return None

    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("🔒 Browser closed")


def automate_elevenlabs_setup(email: str = None, password: str = None) -> Dict[str, Any]:
    """
    Main function to automate ElevenLabs setup

    Args:
        email: Email for account (if None, will prompt or use default)
        password: Password (if None, will generate secure password)

    Returns:
        Dict with success status and API key
    """
    import secrets
    import string

    # Generate secure password if not provided
    if not password:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(16))
        logger.info(f"🔑 Generated secure password")

    # Use provided email or prompt
    if not email:
        email = input("Enter email for ElevenLabs account (or press Enter for default): ").strip()
        if not email:
            email = f"lumina_{datetime.now().strftime('%Y%m%d')}@example.com"
            logger.warning(f"⚠️  Using placeholder email: {email}")
            logger.warning("   You'll need to verify email manually")

    logger.info(f"📧 Using email: {email}")

    # Start automation
    browser = None
    try:
        browser = MANUSNEOBrowser(headless=False)  # Visible so user can monitor
        browser.start()

        result = browser.automate_elevenlabs_signup(email, password)

        # If successful, store API key in vault
        if result.get("success") and result.get("api_key"):
            api_key = result["api_key"]
            logger.info("🔐 Storing API key in Azure Key Vault...")

            subprocess.run([
                "az", "keyvault", "secret", "set",
                "--vault-name", "jarvis-lumina",
                "--name", "elevenlabs-api-key",
                "--value", api_key
            ], check=True, capture_output=True)

            logger.info("✅ ElevenLabs API key stored in Key Vault!")
            result["vault_stored"] = True

        return result

    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        return {"success": False, "error": str(e)}

    finally:
        if browser:
            browser.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="MANUS-NEO Browser Automation")
    parser.add_argument("--setup-elevenlabs", action="store_true", help="Automate ElevenLabs signup")
    parser.add_argument("--email", type=str, help="Email for account")
    parser.add_argument("--password", type=str, help="Password for account")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    if args.setup_elevenlabs:
        result = automate_elevenlabs_setup(email=args.email, password=args.password)

        print("\n" + "="*70)
        if result.get("success"):
            print("✅ ElevenLabs Setup Complete!")
            if result.get("api_key"):
                print(f"   API Key: {result['api_key'][:20]}...")
            if result.get("vault_stored"):
                print("   ✅ Key stored in Azure Key Vault")
        else:
            print("❌ Setup Incomplete")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if result.get("current_url"):
                print(f"   Current URL: {result['current_url']}")
            print("\n   💡 You may need to complete signup manually:")
            print("      1. Go to the current URL")
            print("      2. Complete verification steps")
            print("      3. Get API key from Profile → API Key")
            print("      4. Store with: az keyvault secret set --vault-name jarvis-lumina --name elevenlabs-api-key --value <key>")
        print("="*70)
    else:
        parser.print_help()


if __name__ == "__main__":



    main()