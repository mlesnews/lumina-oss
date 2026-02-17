#!/usr/bin/env python3
"""
Close IMVA Window

Closes IMVA GUI window by finding the window and sending close message.
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

def close_imva_windows():
    """Close IMVA windows using Windows API"""
    print("=" * 80)
    print("🪟 CLOSING IMVA WINDOWS")
    print("=" * 80)
    print()

    # Method 1: Find and close by window title
    ps_cmd = """
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    using System.Diagnostics;

    public class WindowHelper {
        [DllImport("user32.dll")]
        public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

        [DllImport("user32.dll")]
        public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);

        [DllImport("user32.dll")]
        public static extern bool IsWindowVisible(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

        public static void CloseWindowsWithTitle(string titlePattern) {
            EnumWindows((hWnd, lParam) => {
                if (IsWindowVisible(hWnd)) {
                    StringBuilder sb = new StringBuilder(256);
                    GetWindowText(hWnd, sb, 256);
                    string windowTitle = sb.ToString();
                    if (windowTitle.Contains(titlePattern, StringComparison.OrdinalIgnoreCase)) {
                        PostMessage(hWnd, 0x0010, IntPtr.Zero, IntPtr.Zero); // WM_CLOSE
                        Console.WriteLine($"Closed window: {windowTitle}");
                    }
                }
                return true;
            }, IntPtr.Zero);
        }
    }
"@

    WindowHelper::CloseWindowsWithTitle("JARVIS")
    WindowHelper::CloseWindowsWithTitle("Iron")
    WindowHelper::CloseWindowsWithTitle("IMVA")
    WindowHelper::CloseWindowsWithTitle("Bobblehead")
    """

    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and "error" in result.stderr.lower():
            print(f"Errors: {result.stderr}")
    except Exception as e:
        print(f"Window close error: {e}")

    # Method 2: Kill all Python processes with IMVA in command line
    print()
    print("🔍 Killing IMVA processes...")
    ps_cmd2 = """
    Get-Process python -ErrorAction SilentlyContinue |
    Where-Object {
        $proc = $_;
        $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine;
        $cmdline -like '*ironman*' -or $cmdline -like '*bobblehead*' -or $cmdline -like '*jarvis_ironman*'
    } |
    ForEach-Object {
        Write-Host "Killing PID $($_.Id)"
        Stop-Process -Id $_.Id -Force
    }
    """

    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd2],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print(result.stdout)
    except Exception as e:
        print(f"Process kill error: {e}")

    print()
    print("✅ Window close attempt complete")
    print()

if __name__ == "__main__":
    close_imva_windows()
