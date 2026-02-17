# Windows Copilot Virtual Assistant Plugins

This directory contains Windows Copilot plugin manifests for the Lumina virtual assistants.

## Registered Assistants

1. **JARVIS** - Master AI Assistant for system orchestration and workflow management
2. **Ultron** - Advanced AI Assistant for privacy-sensitive operations
3. **Ultimate Iron Man** - Most advanced version of the Iron Man AI assistant

## Registration

### Automatic Registration

Run the PowerShell script to register all assistants:

```powershell
.\scripts\powershell\register_windows_copilot_plugins.ps1 -RegisterAll
```

### Manual Registration

1. Open Windows Copilot
2. Click on the settings/plugins icon
3. Navigate to "Custom Plugins" or "Add Plugin"
4. Upload each manifest file:
   - `jarvis_manifest.json`
   - `ultron_manifest.json`
   - `ultimate_iron_man_manifest.json`

### Verify Registration

```powershell
.\scripts\powershell\register_windows_copilot_plugins.ps1 -List
```

## Troubleshooting

### Assistants Not Appearing

1. **Restart Windows Copilot**: Close and reopen Windows Copilot
2. **Check Service**: Restart Windows Copilot service (may require admin):
   ```powershell
   Restart-Service -Name "WindowsCopilot" -ErrorAction SilentlyContinue
   ```
3. **Check Registry**: Verify plugins are registered:
   ```powershell
   Get-ChildItem "HKCU:\Software\Microsoft\Windows\CurrentVersion\Copilot\Plugins"
   ```
4. **Check Manifest Format**: Ensure JSON is valid:
   ```powershell
   Get-Content .\jarvis_manifest.json | ConvertFrom-Json
   ```

### API Endpoints

The manifests reference API endpoints that need to be running:

- **JARVIS**: `http://localhost:8000`
- **Ultron**: `http://localhost:8001`
- **Ultimate Iron Man**: `http://localhost:8002`

Ensure these services are running and accessible before using the assistants in Windows Copilot.

## Notes

- Windows Copilot plugin registration may vary by Windows version
- Some features may require Windows 11 23H2 or later
- Plugin registration might require administrator privileges
- The assistants will appear in Windows Copilot's plugin list once registered

## Support

For issues or questions, check:
- Windows Copilot documentation
- Lumina project documentation
- JARVIS system logs
