# Cursor Active Model Status

Displays the currently active model in Cursor IDE's status bar, showing the actual model being used even when the selector shows "Auto".

## Features

- ✅ **Real-time Model Display**: Shows the active model in the status bar
- ✅ **Auto Mode Support**: Displays actual model even when selector says "Auto"
- ✅ **Visual Indicators**: Icons for local, cloud, and cluster models
- ✅ **Detailed Information**: Click to see full model details
- ✅ **Automatic Updates**: Updates when model changes

## Installation

### Prerequisites

1. **Python Tracker Script** (required):
   ```bash
   # From project root
   python scripts/python/cursor_active_model_tracker.py --monitor
   ```

2. **Extension Setup**:
   ```bash
   cd vscode-extensions/cursor-active-model-status
   npm install
   npm run compile
   ```

### Install in Cursor IDE

**Option 1: Development Mode**
1. Open this folder in Cursor IDE
2. Press `F5` to launch extension development host
3. The extension will be active in the new window

**Option 2: Package and Install**
1. Install `vsce`: `npm install -g @vscode/vsce`
2. Package extension: `vsce package`
3. Install `.vsix` file in Cursor IDE:
   - Open Command Palette (`Ctrl+Shift+P`)
   - Run "Extensions: Install from VSIX..."
   - Select the generated `.vsix` file

## Usage

### Status Bar Display

The active model appears in the status bar (bottom right):

- **Local Model**: `$(circuit-board) ULTRON $(home)`
- **Cloud Model**: `$(circuit-board) GPT-4 $(cloud)`
- **Virtual Cluster**: `$(circuit-board) ULTRON $(server)`
- **Auto Mode**: `$(circuit-board) Auto $(sync~spin)`

### Commands

- **Refresh Status**: `Ctrl+Shift+P` → "Refresh Active Model Status"
- **Show Details**: Click the status bar item or `Ctrl+Shift+P` → "Show Active Model Details"

### Configuration

Add to your Cursor settings (`.cursor/settings.json`):

```json
{
  "cursorActiveModelStatus.updateInterval": 1000,
  "cursorActiveModelStatus.showInStatusBar": true
}
```

## Requirements

- Cursor IDE 1.80.0 or higher
- Python tracker script running (see Prerequisites)

## Status File

The extension reads from `data/cursor_active_model_status.json`, which is updated by the Python tracker script.

## Troubleshooting

### Status Not Showing

1. **Check tracker is running**:
   ```bash
   python scripts/python/cursor_active_model_tracker.py --status
   ```

2. **Start tracker**:
   ```bash
   python scripts/python/start_cursor_model_tracker.py
   ```

3. **Reload Cursor window**: `Ctrl+Shift+P` → "Reload Window"

### Model Shows "Unknown"

1. Verify `.cursor/settings.json` has model configuration
2. Run tracker update: `python scripts/python/cursor_active_model_tracker.py --update`
3. Check status file exists: `data/cursor_active_model_status.json`

## Development

### Build

```bash
npm run compile
```

### Watch Mode

```bash
npm run watch
```

### Test

1. Press `F5` to launch extension development host
2. Test status bar display
3. Test commands

## License

Part of the Lumina ecosystem.
