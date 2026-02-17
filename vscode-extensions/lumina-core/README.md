# Lumina Complete - VSIX Extension

Complete Lumina ecosystem integration for VS Code/Cursor with:

- ✅ **GitHub Integration** (Public & Private repositories)
- ✅ **GitLens Integration** (Automatic followup, PR integration)
- ✅ **Local Enterprise Git** (NAS-based repositories)
- ✅ **NAS Cloud Services** (Synology DSM integration)
- ✅ **Storage Providers** (Dropbox, OneDrive, ProtonDrive, NAS)
- ✅ **Local AI Services** (ULTRON/KAIJU auto-start)
- ✅ **Resource Awareness** (CPU/Memory monitoring)
- ✅ **File Cleanup Stack** (persistent queue + open-docs count in status bar)

## Features

### Git/GitHub/GitLens
- Public and private GitHub repository support
- GitLens automatic followup automation
- PR integration and workflow management
- Local enterprise Git on NAS

### NAS Cloud Services
- Synology DSM integration
- Network drive mapping
- Cloud storage aggregation
- Automated sync management

### Storage Providers
- Dropbox integration
- OneDrive integration
- ProtonDrive integration
- NAS storage management
- Aggregated storage path

### Local AI Services
- ULTRON auto-start
- KAIJU auto-start
- Resource-aware scaling
- CPU threshold monitoring

### Kilo Code setup (Lumina Core defaults)
- **Apply Kilo Code Setup** – Copies Lumina’s default Kilo Code rules (no-secrets policy) into your workspace `.kilocode/rules/`. Use when you want Kilo Code to follow Lumina’s security rules (never print or log API keys, passwords, tokens). Command: **Ctrl+Shift+P** → **Lumina: Apply Kilo Code Setup**. Existing rule files are not overwritten.

## Installation

### BDA: Build, Deploy, Activate (#automation)

**Circle back**: See `docs/system/LUMINA_EXTENSION_BDA.md`.

From `vscode-extensions/lumina-core`:

```powershell
.\build_and_install.ps1
```

Then in Cursor: **Developer: Reload Window** (or restart Cursor) to **activate**.

### Manual steps

```bash
# Dependencies (once)
npm install

# Build the extension
npm run compile

# Package as VSIX
npm run package
# → lumina-core-3.0.0.vsix

# Install into Cursor (or VS Code)
cursor --install-extension lumina-core-3.0.0.vsix --force
# or: code --install-extension lumina-core-3.0.0.vsix --force
```

## Configuration

All settings are available in VS Code settings under `lumina.*`:

- `lumina.enabled` - Enable/disable Lumina ecosystem
- `lumina.git.github` - GitHub integration settings
- `lumina.git.gitlens` - GitLens integration settings
- `lumina.git.localEnterprise` - Local enterprise Git settings
- `lumina.nas.*` - NAS cloud services settings
- `lumina.storage.*` - Storage provider settings
- `lumina.ai.*` - Local AI services settings

## Commands

- `Lumina: Show Status` - Display full ecosystem status
- `Lumina: Show Active AI Models` - Show ULTRON/KAIJU status
- `Lumina: Show Git/GitLens Status` - Show Git integration status
- `Lumina: Show NAS Status` - Show NAS connection status
- `Lumina: Show Storage Providers` - List enabled storage providers
- `Lumina: Sync to NAS` - Trigger NAS sync
- `Lumina: Auto-Start Local AI` - Start local AI services
- **File Cleanup Stack** (Explorer): Add current file, add files with problems, remove from stack, open file. Status bar shows open document count (click → focus File Cleanup Stack).
- **Lumina: Apply Kilo Code Setup** – Copy default Kilo Code rules (no-secrets) into `.kilocode/rules/`.

## Documentation (part of Lumina Core)

- **Cursor IDE QOL index**: `docs/system/CURSOR_IDE_QOL_INDEX.md` — single index of all Cursor IDE customizations, features, configs, scripts, and docs (JARVIS chat, hotkeys, Kilo Code, model config, etc.). Start here if you're not seeing customizations.
- **Lumina JARVIS Chat** (companion extension in the Core set): `applications/ide_chat` — dedicated JARVIS chat panel; install from that folder and use **Lumina: Open JARVIS Chat** (`jarvis.chat.open`).
- **Core vs Premium vs CE**: `docs/system/LUMINA_EXTENSIONS_CORE_PREMIUM_NAMING.md`

## Requirements

- VS Code 1.80.0 or higher
- GitLens extension (eamodio.gitlens)
- GitHub Copilot extension (github.copilot)
- GitHub Copilot Chat extension (github.copilot-chat)

## License

MIT
