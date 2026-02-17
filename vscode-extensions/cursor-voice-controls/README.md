# Cursor Voice Controls Extension

Full VCR controls (Play, Pause, Stop) for Cursor voice transcription.

## Features

### Basic Controls
- **▶ Play**: Start or resume voice transcription
- **⏸ Pause**: Pause voice transcription (effectively mutes it without stopping)
- **⏹ Stop**: Stop voice transcription completely
- **Toggle**: Click status bar to toggle between states

### Auto-Hide Feature
- **Auto-Hide**: Status bar automatically hides when stopped and not actively hovering (like Windows taskbar)
- **Hover to Show**: Status bar appears when you hover over the area or interact with controls
- **Always Visible When Active**: Status bar stays visible when playing/paused
- **Configurable**: Enable/disable and adjust delay in settings

### Hands-Free Auto-Send (NEW!)
- **Auto-Send After Pause**: Automatically sends transcription after 3-5 second pause (configurable)
- **No Manual Click Required**: Perfect for hands-free operation - just speak and pause
- **Cancel Anytime**: Press `Ctrl+Shift+Escape` to cancel auto-send if you're still thinking
- **Configurable Pause Duration**: Adjust pause duration (3-5 seconds) in settings
- **Smart Monitoring**: Only auto-sends when actively transcribing (playing state)

### Navigation Controls
- **⏩ Skip Forward**: Jump to next transcription segment/sentence
- **⏪ Skip Back**: Jump to previous transcription segment/sentence
- **⏩⏩ Fast Forward**: Skip ahead by larger intervals (10-30s) or increase playback speed
- **⏪⏪ Fast Rewind**: Skip back by larger intervals (10-30s) or decrease playback speed

## Usage

### Status Bar
- Click the status bar icon to toggle voice transcription
- Status shows current state: Stopped, Playing, or Paused (Muted)

### Commands
- `Cursor Voice Controls: Play` - Start/resume transcription
- `Cursor Voice Controls: Pause` - Pause transcription (mute)
- `Cursor Voice Controls: Stop` - Stop transcription
- `Cursor Voice Controls: Toggle` - Toggle between states

### Keyboard Shortcuts

**Basic Controls:**
- `Ctrl+Shift+V` (Mac: `Cmd+Shift+V`) - Play
- `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`) - Pause
- `Ctrl+Shift+S` (Mac: `Cmd+Shift+S`) - Stop

**Navigation Controls:**
- `Ctrl+Shift+Right` (Mac: `Cmd+Shift+Right`) - Skip Forward (Next Segment)
- `Ctrl+Shift+Left` (Mac: `Cmd+Shift+Left`) - Skip Back (Previous Segment)
- `Ctrl+Shift+Up` (Mac: `Cmd+Shift+Up`) - Fast Forward (Skip Ahead)
- `Ctrl+Shift+Down` (Mac: `Cmd+Shift+Down`) - Fast Rewind (Skip Back)

**Hands-Free Controls:**
- `Ctrl+Shift+Escape` (Mac: `Cmd+Shift+Escape`) - Cancel Auto-Send (if still thinking)

## States

- **Stopped**: Voice transcription is off
- **Playing**: Voice transcription is active and recording
- **Paused**: Voice transcription is paused (muted) - can be resumed

## Installation

1. Copy this extension to your Cursor extensions directory
2. Run `npm install` in the extension directory
3. Run `npm run compile` to build
4. Reload Cursor IDE

## Function Mappings

### Skip Forward (⏩)
**Function**: Navigate to next transcription segment/sentence
- Jumps to next message/segment in transcription history
- Useful for reviewing long transcriptions
- Shows current segment in notification

### Skip Back (⏪)
**Function**: Navigate to previous transcription segment/sentence
- Jumps to previous message/segment in transcription history
- Useful for reviewing what was just transcribed
- Shows current segment in notification

### Fast Forward (⏩⏩)
**Function**: Skip ahead aggressively or increase playback speed
- Skips ahead by larger intervals (default: 10-30 seconds)
- Increases playback speed (up to 4x)
- Useful for quickly moving through long transcriptions

### Fast Rewind (⏪⏪)
**Function**: Rewind aggressively or decrease playback speed
- Skips back by larger intervals (default: 10-30 seconds)
- Decreases playback speed (down to 0.25x)
- Useful for reviewing previous sections

## Configuration

### Settings

Open Cursor Settings and search for "Cursor Voice Controls":

- **`cursorVoiceControls.autoHide`** (default: `true`)
  - Enable/disable auto-hide for status bar item
  
- **`cursorVoiceControls.autoHideDelay`** (default: `2000` ms, min: 500, max: 10000)
  - Delay before status bar auto-hides
  
- **`cursorVoiceControls.autoSend`** (default: `true`) ⭐ NEW
  - Enable/disable hands-free auto-send after pause
  
- **`cursorVoiceControls.pauseDuration`** (default: `4000` ms, min: 3000, max: 5000) ⭐ NEW
  - Pause duration in milliseconds before auto-sending (3-5 second range)

### Commands

- `Cursor Voice Controls: Toggle Auto-Send` - Enable/disable hands-free auto-send
- `Cursor Voice Controls: Cancel Auto-Send` - Cancel pending auto-send

## How Hands-Free Auto-Send Works

1. **Start Voice Transcription**: Press Play or use `Ctrl+Shift+V`
2. **Speak Naturally**: Just talk - your words are transcribed
3. **Pause for 3-5 Seconds**: When you're done speaking, pause (default: 4 seconds)
4. **Auto-Send**: The message is automatically sent - no clicking needed!
5. **Cancel if Needed**: Press `Ctrl+Shift+Escape` if you want to add more before sending

**Perfect for hands-free operation!** Just speak, pause, and your message is sent automatically.

## Integration

This extension integrates with Cursor's built-in voice transcription system and provides enhanced controls for better workflow management. The navigation controls work with transcription history and chat messages.

The hands-free auto-send feature is designed for seamless voice-driven collaboration, allowing you to work completely hands-free without needing to manually click send buttons.
