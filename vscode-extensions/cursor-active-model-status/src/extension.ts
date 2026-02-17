import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface ModelStatus {
    active_model: string;
    model_type: string;
    provider?: string;
    endpoint?: string;
    is_local?: boolean;
    context_length?: number;
    description?: string;
    cluster_nodes?: number;
    cluster_type?: string;
    cluster_routing?: string;
    last_updated?: string;
    status?: string;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Cursor Active Model Status extension is now active!');

    const config = vscode.workspace.getConfiguration('cursorActiveModelStatus');
    const updateInterval = config.get<number>('updateInterval', 1000);
    const showInStatusBar = config.get<boolean>('showInStatusBar', true);

    // Create status bar item
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        1000 // Priority - higher numbers appear more to the left
    );
    statusBarItem.command = 'cursorActiveModelStatus.showDetails';
    statusBarItem.tooltip = 'Click to show active model details';

    // Get workspace root
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
        vscode.window.showWarningMessage('No workspace folder found. Active model status will not be displayed.');
        return;
    }

    const statusFile = path.join(workspaceRoot, 'data', 'cursor_active_model_status.json');

    function updateStatusBar() {
        try {
            if (!fs.existsSync(statusFile)) {
                statusBarItem.text = '$(sync~spin) Model: Unknown';
                statusBarItem.show();
                return;
            }

            const statusData = fs.readFileSync(statusFile, 'utf8');
            const status: ModelStatus = JSON.parse(statusData);

            const modelName = status.active_model || 'Unknown';
            const modelType = status.model_type || 'unknown';
            
            // Create display text
            let displayText = `$(circuit-board) ${modelName}`;
            
            // Add type indicator
            if (modelType === 'local') {
                displayText += ' $(home)';
            } else if (modelType === 'cloud') {
                displayText += ' $(cloud)';
            } else if (modelType === 'virtual_cluster') {
                displayText += ' $(server)';
            } else if (modelType === 'auto') {
                displayText += ' $(sync~spin)';
            }

            statusBarItem.text = displayText;
            statusBarItem.tooltip = `Active Model: ${modelName}\nType: ${modelType}\n${status.is_local ? 'Local' : 'Cloud'}\nClick for details`;
            
            if (showInStatusBar) {
                statusBarItem.show();
            }
        } catch (error) {
            console.error('Error updating status bar:', error);
            statusBarItem.text = '$(error) Model: Error';
            statusBarItem.show();
        }
    }

    // Initial update
    updateStatusBar();

    // Set up file watcher
    const statusFileWatcher = vscode.workspace.createFileSystemWatcher(
        new vscode.RelativePattern(workspaceRoot, 'data/cursor_active_model_status.json')
    );

    statusFileWatcher.onDidChange(() => {
        updateStatusBar();
    });

    // Set up interval update
    const interval = setInterval(() => {
        updateStatusBar();
    }, updateInterval);

    // Register command to show details
    const showDetailsCommand = vscode.commands.registerCommand('cursorActiveModelStatus.showDetails', () => {
        try {
            if (!fs.existsSync(statusFile)) {
                vscode.window.showInformationMessage('Model status file not found. Run the tracker script first.');
                return;
            }

            const statusData = fs.readFileSync(statusFile, 'utf8');
            const status: ModelStatus = JSON.parse(statusData);

            const details = [
                `**Active Model:** ${status.active_model || 'Unknown'}`,
                `**Type:** ${status.model_type || 'unknown'}`,
                `**Provider:** ${status.provider || 'unknown'}`,
                `**Location:** ${status.is_local ? 'Local' : 'Cloud'}`,
            ];

            if (status.endpoint) {
                details.push(`**Endpoint:** ${status.endpoint}`);
            }

            if (status.context_length) {
                details.push(`**Context Length:** ${status.context_length.toLocaleString()} tokens`);
            }

            if (status.cluster_nodes) {
                details.push(`**Cluster Nodes:** ${status.cluster_nodes}`);
                details.push(`**Cluster Type:** ${status.cluster_type || 'unknown'}`);
                details.push(`**Routing:** ${status.cluster_routing || 'unknown'}`);
            }

            if (status.description) {
                details.push(`**Description:** ${status.description}`);
            }

            if (status.last_updated) {
                const lastUpdated = new Date(status.last_updated);
                details.push(`**Last Updated:** ${lastUpdated.toLocaleString()}`);
            }

            vscode.window.showInformationMessage(details.join('\n'), { modal: true });
        } catch (error) {
            vscode.window.showErrorMessage(`Error reading model status: ${error}`);
        }
    });

    // Register refresh command
    const refreshCommand = vscode.commands.registerCommand('cursorActiveModelStatus.refresh', () => {
        updateStatusBar();
        vscode.window.showInformationMessage('Active model status refreshed');
    });

    context.subscriptions.push(
        statusBarItem,
        statusFileWatcher,
        showDetailsCommand,
        refreshCommand
    );

    // Cleanup interval on deactivate
    context.subscriptions.push({
        dispose: () => clearInterval(interval)
    });
}

export function deactivate() {
    // Cleanup
}
