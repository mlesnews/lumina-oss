# PowerToys Voice Button Macro Setup

## Objective
Map **Right Alt** button to **Control+Shift+Space** (Voice Activation)

## Method 1: PowerToys Keyboard Manager (Recommended)

### Steps:
1. **Install PowerToys** (if not already installed)
   - Download from: https://github.com/microsoft/PowerToys
   - Or install from Microsoft Store

2. **Open PowerToys**
   - Launch PowerToys from Start Menu
   - Go to **Keyboard Manager**

3. **Add Remap**
   - Click **"Remap a shortcut"**
   - In **"Shortcut"** field, press **Right Alt**
   - In **"Mapped to"** field, press **Control+Shift+Space**
   - Click **OK**

4. **Apply**
   - The remap is active immediately
   - Right Alt will now trigger Control+Shift+Space

### Alternative: Remap a key
- Click **"Remap a key"**
- Select **Right Alt** → **Remap to** → **Custom shortcut**
- Enter: **Ctrl+Shift+Space**

## Method 2: AutoHotkey Script

1. **Install AutoHotkey**
   - Download from: https://www.autohotkey.com/
   - Install the application

2. **Run Script**
   - Double-click `voice_button_macro.ahk`
   - Script runs in background
   - Right Alt triggers Control+Shift+Space

3. **Auto-Start** (Optional)
   - Copy script to Windows Startup folder:
     `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

## Method 3: Custom Python Macro

1. **Install keyboard library**
   ```bash
   pip install keyboard
   ```

2. **Run macro**
   ```bash
   python scripts/python/jarvis_voice_button_macro.py --custom
   ```

   **Note**: Requires administrator privileges on Windows

## Verification

1. Press **Right Alt**
2. Should trigger voice activation (Control+Shift+Space)
3. Check if voice interface activates

## Troubleshooting

- **Right Alt not working**: Check if PowerToys is running
- **Requires admin**: Some methods require administrator privileges
- **Conflicts**: Check for other software using Right Alt
- **PowerToys not found**: Install from Microsoft Store or GitHub

## Current Configuration

- **Trigger**: Right Alt
- **Action**: Control+Shift+Space
- **Purpose**: Voice activation button
- **Status**: Ready to configure

@JARVIS @LUMINA #VOICE_BUTTON #MACRO #POWERTOYS
