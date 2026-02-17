#!/usr/bin/env python3
"""
Terminal Diagnostic Tool
Checks common terminal configuration issues on Windows
"""
import sys
import os
import platform
import subprocess
from pathlib import Path

def check_terminal_environment():
    """Diagnose terminal environment"""
    print("=" * 80)
    print("🔍 TERMINAL DIAGNOSTIC REPORT")
    print("=" * 80)

    # 1. Platform Info
    print("\n📊 Platform Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python: {sys.version}")
    print(f"   Python Executable: {sys.executable}")

    # 2. Environment Variables
    print("\n🌍 Key Environment Variables:")
    shell_vars = ['SHELL', 'COMSPEC', 'TERM', 'PSModulePath', 'PATH']
    for var in shell_vars:
        value = os.environ.get(var, 'Not Set')
        if var == 'PATH':
            print(f"   {var}: {len(value.split(os.pathsep))} entries")
        else:
            print(f"   {var}: {value[:80] if len(str(value)) > 80 else value}")

    # 3. Test Shell Execution
    print("\n🧪 Testing Shell Execution:")
    try:
        if platform.system() == "Windows":
            # Test PowerShell
            result = subprocess.run(['powershell', '-Command', 'Write-Host "PowerShell OK"'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ PowerShell: Working")
            else:
                print(f"   ❌ PowerShell: Exit code {result.returncode}")

            # Test CMD
            result = subprocess.run(['cmd', '/c', 'echo CMD OK'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ CMD: Working")
            else:
                print(f"   ❌ CMD: Exit code {result.returncode}")
        else:
            # Test bash
            result = subprocess.run(['bash', '-c', 'echo "Bash OK"'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ Bash: Working")
            else:
                print(f"   ❌ Bash: Exit code {result.returncode}")
    except Exception as e:
        print(f"   ⚠️  Shell test error: {e}")

    # 4. Check for Common Issues
    print("\n⚠️  Common Issues Checklist:")
    issues = []

    # Check if running as admin (can cause issues)
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0 if platform.system() == "Windows" else False
        if is_admin:
            issues.append("Running as Administrator (may cause terminal issues)")
            print("   ⚠️  Running as Administrator")
        else:
            print("   ✅ Not running as Administrator")
    except:
        pass

    # Check Python path
    python_path = Path(sys.executable)
    if not python_path.exists():
        issues.append(f"Python executable not found: {python_path}")
        print(f"   ❌ Python path invalid: {python_path}")
    else:
        print(f"   ✅ Python path valid: {python_path}")

    # 5. Recommendations
    print("\n💡 Recommendations:")
    if platform.system() == "Windows":
        print("   1. Check VS Code/Cursor terminal.integrated settings")
        print("   2. Ensure 'Use legacy console' is disabled in cmd.exe properties")
        print("   3. Try setting terminal.integrated.defaultProfile.windows to 'PowerShell' or 'Command Prompt'")
        print("   4. Check if anti-virus is blocking terminal processes")
        print("   5. Ensure VS Code/Cursor is not in compatibility mode")

    if issues:
        print(f"\n❌ Found {len(issues)} potential issue(s)")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ No obvious issues detected")

    print("\n" + "=" * 80)
    return len(issues) == 0

if __name__ == "__main__":
    success = check_terminal_environment()
    sys.exit(0 if success else 1)
