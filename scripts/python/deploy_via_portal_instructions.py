#!/usr/bin/env python3
"""
Quick deployment instructions for Azure Portal
Opens browser to Azure Portal with function code ready to paste
"""
import webbrowser
import pyperclip
from pathlib import Path

# Read function code
function_path = Path(__file__).parent.parent.parent / "azure_functions" / "RenderIronLegion" / "__init__.py"
with open(function_path, 'r') as f:
    code = f.read()

# Copy to clipboard
try:
    pyperclip.copy(code)
    print("✅ Function code copied to clipboard")
except:
    print("⚠️  Could not copy to clipboard - install pyperclip")

# Open Azure Portal
portal_url = "https://portal.azure.com/#@/resource/subscriptions/resourceGroups/jarvis-lumina-rg/providers/Microsoft.Web/sites/jarvis-lumina-functions/functions"
print(f"🌐 Opening Azure Portal...")
print(f"📋 Function code is ready to paste")
print(f"\nSteps:")
print(f"1. Portal will open to your Function App")
print(f"2. Click 'Functions' → 'Create'")
print(f"3. Choose 'HTTP trigger'")
print(f"4. Name: RenderIronLegion")
print(f"5. Paste code from clipboard")
print(f"6. Save")

try:
    webbrowser.open(portal_url)
except:
    print(f"⚠️  Could not open browser - go to: {portal_url}")
