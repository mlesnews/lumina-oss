import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.python.syphon_system import SYPHONSystem


def syphon_docs():
    syphon = SYPHONSystem(project_root)

    docs_content = """
    # Terminal Shell Integration
    Visual Studio Code has the ability to integrate with common shells, allowing the terminal to understand more about what's actually happening inside the shell.
    This additional information enables some useful features such as working directory detection and command detection, decorations, and navigation.

    Supported shells:
    • Linux/macOS: bash, fish, pwsh, zsh
    • Windows: Git Bash, pwsh

    ## Installation
    By default, the shell integration script should automatically activate on supported shells launched from VS Code.
    This is done by injecting arguments and/or environment variables when the shell session launches.
    This automatic injection can be disabled by setting terminal.integrated.shellIntegration.enabled to false.

    Manual installation:
    For complex setups, manual installation is recommended.

    Bash:
    Add the following to your ~/.bashrc file:
    [[ "$TERM_PROGRAM" == "vscode" ]] && . "$(code --locate-shell-integration-path bash)"

    PowerShell:
    Add the following to your PowerShell profile:
    if ($env:TERM_PROGRAM -eq "vscode") { . "$(code --locate-shell-integration-path pwsh)" }

    Zsh:
    Add the following to your ~/.zshrc file:
    [[ "$TERM_PROGRAM" == "vscode" ]] && . "$(code --locate-shell-integration-path zsh)"

    ## Features
    - Command decorations and overview ruler: Blue circles for success, red for failure.
    - Command navigation: Ctrl/Cmd+Up/Down to navigate between commands.
    - Command guide: Visual guide for command output.
    - Sticky scroll: Keeps command at top of viewport.
    - Quick fixes: Suggestions for common errors (git push upstream, port in use).
    - Run recent command: Ctrl+Alt+R to search history.
    - Go to recent directory: Ctrl+G to navigate directories.

    ## Configuration
    - terminal.integrated.shellIntegration.enabled
    - terminal.integrated.shellIntegration.decorationsEnabled
    - terminal.integrated.suggest.enabled
    """

    syphon.syphon_email(
        email_id="docs_vscode_shell_integration",
        subject="VS Code Terminal Shell Integration Documentation",
        body=docs_content,
        from_address="docs@code.visualstudio.com",
        to_address="user@local",
        metadata={
            "url": "https://code.visualstudio.com/docs/terminal/shell-integration",
            "type": "documentation",
        },
    )

    print("Syphoned VS Code Shell Integration docs.")


if __name__ == "__main__":
    syphon_docs()
