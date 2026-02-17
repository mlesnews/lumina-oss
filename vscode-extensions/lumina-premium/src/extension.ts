/**
 * Lumina Premium Extension
 * 
 * Private paid add-on/expansion for Lumina Core
 * NOT PUBLISHED TO MARKETPLACE
 * 
 * This is a private paid add-on that extends Lumina Core functionality.
 * Additional expansions may be created in the future.
 * 
 * @author Lumina Team
 * @tags #LUMINA #PREMIUM #PRIVATE #PAID #ADDON #EXPANSION
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// ============================================================================
// PROGRESS STATUS INDICATOR (Airport Signboard Style for JARVIS/AI/Agents)
// ============================================================================

interface ProgressStatus {
    agent: string;
    status: string;
    progress: number;
    message: string;
    timestamp: string;
}

let progressStatusBarItem: vscode.StatusBarItem | null = null;
let progressStatusInterval: NodeJS.Timeout | undefined;
let progressStatusWatcher: vscode.FileSystemWatcher | undefined;
let currentProgressIndex: number = 0;

function initializeProgressStatus(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('lumina.progress');
    const enabled = config.get<boolean>('enabled', true);
    const updateInterval = config.get<number>('updateInterval', 2000);

    if (!enabled) return;

    progressStatusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    progressStatusBarItem.command = 'lumina.showProgress';
    progressStatusBarItem.tooltip = 'LUMINA Progress Status - Airport Signboard Style\nClick to show details';

    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) return;

    const progressStatusFile = path.join(workspaceRoot, 'data', 'progress_status.json');

    function updateProgressStatus() {
        try {
            if (!fs.existsSync(progressStatusFile)) {
                // Default airport signboard style message
                progressStatusBarItem!.text = '$(sync~spin) LUMINA | JARVIS/AI/Agents | Ready';
                progressStatusBarItem!.show();
                return;
            }

            const statusData = fs.readFileSync(progressStatusFile, 'utf8');
            const status: ProgressStatus = JSON.parse(statusData);

            // Airport signboard style: scrolling text effect
            const agentName = status.agent || 'JARVIS';
            const statusText = status.status || 'Ready';
            const progressPercent = status.progress || 0;
            const message = status.message || '';

            // Create scrolling effect by rotating through status parts
            const statusParts = [
                `${agentName}`,
                `${statusText}`,
                progressPercent > 0 ? `${progressPercent}%` : '',
                message ? message.substring(0, 30) : ''
            ].filter(p => p.length > 0);

            if (statusParts.length > 0) {
                const currentPart = statusParts[currentProgressIndex % statusParts.length];
                progressStatusBarItem!.text = `$(sync~spin) LUMINA | ${currentPart}`;
                currentProgressIndex++;
            } else {
                progressStatusBarItem!.text = '$(sync~spin) LUMINA | Ready';
            }

            progressStatusBarItem!.tooltip = `LUMINA Progress Status\nAgent: ${agentName}\nStatus: ${statusText}\nProgress: ${progressPercent}%\n${message ? `Message: ${message}` : ''}\n\nClick to show details`;
            progressStatusBarItem!.show();
        } catch (error) {
            console.error('Error updating progress status:', error);
            progressStatusBarItem!.text = '$(sync~spin) LUMINA | Status...';
            progressStatusBarItem!.show();
        }
    }

    updateProgressStatus();

    progressStatusWatcher = vscode.workspace.createFileSystemWatcher(
        new vscode.RelativePattern(workspaceRoot, 'data/progress_status.json')
    );
    progressStatusWatcher.onDidChange(() => updateProgressStatus());
    progressStatusWatcher.onDidCreate(() => updateProgressStatus());

    progressStatusInterval = setInterval(() => updateProgressStatus(), updateInterval);

    const showProgressCommand = vscode.commands.registerCommand('lumina.showProgress', () => {
        try {
            if (!fs.existsSync(progressStatusFile)) {
                vscode.window.showInformationMessage('Progress status file not found. System is ready.');
                return;
            }

            const statusData = fs.readFileSync(progressStatusFile, 'utf8');
            const status: ProgressStatus = JSON.parse(statusData);

            const panel = vscode.window.createWebviewPanel(
                'luminaProgress',
                'LUMINA Progress Status - Airport Signboard',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            panel.webview.html = generateProgressStatusHTML(status);
        } catch (error) {
            vscode.window.showErrorMessage(`Error showing progress status: ${error}`);
        }
    });

    context.subscriptions.push(
        progressStatusBarItem,
        progressStatusWatcher,
        showProgressCommand
    );

    context.subscriptions.push({
        dispose: () => {
            if (progressStatusInterval) clearInterval(progressStatusInterval);
        }
    });
}

function generateProgressStatusHTML(status: ProgressStatus): string {
    const agent = status.agent || 'JARVIS';
    const statusText = status.status || 'Ready';
    const progress = status.progress || 0;
    const message = status.message || '';

    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Courier New', monospace;
            padding: 20px;
            background: #000;
            color: #0f0;
            overflow: hidden;
        }
        .signboard {
            border: 3px solid #0f0;
            padding: 20px;
            background: #001100;
            text-align: center;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 10px #0f0; }
            50% { box-shadow: 0 0 20px #0f0, 0 0 30px #0f0; }
        }
        .agent-name {
            font-size: 32px;
            font-weight: bold;
            color: #0ff;
            text-shadow: 0 0 10px #0ff;
            margin-bottom: 10px;
        }
        .status-text {
            font-size: 24px;
            color: #0f0;
            margin: 10px 0;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #003300;
            border: 2px solid #0f0;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #0f0, #0ff);
            width: ${progress}%;
            animation: progressPulse 1s infinite;
            box-shadow: 0 0 10px #0f0;
        }
        @keyframes progressPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        .message {
            font-size: 18px;
            color: #ff0;
            margin-top: 20px;
            min-height: 50px;
            overflow: hidden;
        }
        .timestamp {
            font-size: 12px;
            color: #666;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="signboard">
        <div class="agent-name">${agent}</div>
        <div class="status-text">${statusText}</div>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        <div class="message">${message || 'System operational'}</div>
        <div class="timestamp">Last Updated: ${new Date(status.timestamp || Date.now()).toLocaleString()}</div>
    </div>
</body>
</html>`;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Lumina Premium extension is now active!');

    // Check for valid license
    const config = vscode.workspace.getConfiguration('lumina.premium');
    const enabled = config.get<boolean>('enabled', false);
    const licenseKey = config.get<string>('licenseKey', '');

    if (!enabled || !licenseKey) {
        vscode.window.showWarningMessage(
            'Lumina Premium (Private Paid Add-On) requires a valid license key. Please configure your license in settings.'
        );
        return;
    }

    // Register premium commands
    const showFeaturesCommand = vscode.commands.registerCommand('lumina.premium.showFeatures', () => {
        vscode.window.showInformationMessage(
            'Lumina Premium (Private Paid Add-On) Features:\n' +
            '• Advanced AI integrations\n' +
            '• Premium cloud services\n' +
            '• Exclusive workflows\n' +
            '• Priority support\n' +
            '\nThis is a private paid add-on expansion.\nMore features coming soon!'
        );
    });

    context.subscriptions.push(showFeaturesCommand);

    // Initialize progress status indicator
    initializeProgressStatus(context);

    // Initialize footer customization (ask-heap-stack and notifications)
    initializeFooterCustomization(context);

    vscode.window.showInformationMessage('Lumina Premium extension activated!');
}

// ============================================================================
// FOOTER CUSTOMIZATION (Ask Heap Stack and Notifications IDE-QUEUE)
// ============================================================================

let askHeapStackStatusBarItem: vscode.StatusBarItem | null = null;
let notificationsStatusBarItem: vscode.StatusBarItem | null = null;
let footerCustomizationInterval: NodeJS.Timeout | undefined;

function initializeFooterCustomization(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('lumina.footer');
    const enabled = config.get<boolean>('enabled', true);
    const showAskHeapStack = config.get<boolean>('showAskHeapStack', true);
    const showNotifications = config.get<boolean>('showNotifications', true);

    if (!enabled) return;

    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) return;

    // Create ask-heap-stack status bar item (PREFIX - left side, high priority)
    if (showAskHeapStack) {
        askHeapStackStatusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            1000  // High priority - appears first (prefix)
        );
        askHeapStackStatusBarItem.command = 'lumina.footer.showAskHeapStack';
        askHeapStackStatusBarItem.tooltip = 'Ask Heap Stack - Current/Total';
        context.subscriptions.push(askHeapStackStatusBarItem);
    }

    // Create notifications status bar item (SUFFIX - right side, low priority)
    if (showNotifications) {
        notificationsStatusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            1  // Low priority - appears last (suffix)
        );
        notificationsStatusBarItem.command = 'lumina.footer.showNotifications';
        notificationsStatusBarItem.tooltip = 'Notifications [IDE-QUEUE]';
        context.subscriptions.push(notificationsStatusBarItem);
    }

    // Update status bar items
    updateFooterStatusBarItems();

    // Update every 2 seconds
    footerCustomizationInterval = setInterval(() => updateFooterStatusBarItems(), 2000);

    // Register commands
    const showAskHeapStackCommand = vscode.commands.registerCommand(
        'lumina.footer.showAskHeapStack',
        () => {
            const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!workspaceRoot) {
                vscode.window.showInformationMessage('Ask Heap Stack: No workspace found');
                return;
            }

            const askHeapStackFile = path.join(workspaceRoot, 'data', 'ask_heap_stack', 'ask_heap_stack.json');
            let askCurrent = 0;
            let askTotal = 0;

            if (fs.existsSync(askHeapStackFile)) {
                try {
                    const data = JSON.parse(fs.readFileSync(askHeapStackFile, 'utf-8'));
                    askCurrent = data.current || 0;
                    askTotal = data.total || 0;
                } catch (e) {
                    // Ignore errors
                }
            }

            vscode.window.showInformationMessage(
                `Ask Heap Stack: ${askCurrent}/${askTotal}\n` +
                `Current: ${askCurrent} active items\n` +
                `Total: ${askTotal} total items`
            );
        }
    );

    const showNotificationsCommand = vscode.commands.registerCommand(
        'lumina.footer.showNotifications',
        () => {
            const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!workspaceRoot) {
                vscode.window.showInformationMessage('Notifications [IDE-QUEUE]: No workspace found');
                return;
            }

            const notificationsFile = path.join(workspaceRoot, 'data', 'ide_notifications', 'notifications.json');
            let notificationCount = 0;
            let notifications: any[] = [];

            if (fs.existsSync(notificationsFile)) {
                try {
                    const data = JSON.parse(fs.readFileSync(notificationsFile, 'utf-8'));
                    notificationCount = data.count || (data.notifications?.length || 0);
                    notifications = data.notifications || [];
                } catch (e) {
                    // Ignore errors
                }
            }

            const message = `Notifications [IDE-QUEUE]: ${notificationCount} notification${notificationCount !== 1 ? 's' : ''}`;
            if (notifications.length > 0) {
                const details = notifications.slice(0, 5).map((n: any, i: number) => 
                    `${i + 1}. ${n.title || n.message || 'Notification'}`
                ).join('\n');
                vscode.window.showInformationMessage(`${message}\n\n${details}${notifications.length > 5 ? '\n...' : ''}`);
            } else {
                vscode.window.showInformationMessage(message);
            }
        }
    );

    context.subscriptions.push(
        showAskHeapStackCommand,
        showNotificationsCommand
    );

    context.subscriptions.push({
        dispose: () => {
            if (footerCustomizationInterval) clearInterval(footerCustomizationInterval);
        }
    });
}

function updateFooterStatusBarItems() {
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
        return;
    }

    const config = vscode.workspace.getConfiguration('lumina.footer');
    const showAskHeapStack = config.get<boolean>('showAskHeapStack', true);
    const showNotifications = config.get<boolean>('showNotifications', true);

    // Get ask-heap-stack data
    if (showAskHeapStack && askHeapStackStatusBarItem) {
        const askHeapStackFile = path.join(workspaceRoot, 'data', 'ask_heap_stack', 'ask_heap_stack.json');
        let askCurrent = 0;
        let askTotal = 0;

        if (fs.existsSync(askHeapStackFile)) {
            try {
                const data = JSON.parse(fs.readFileSync(askHeapStackFile, 'utf-8'));
                askCurrent = data.current || 0;
                askTotal = data.total || 0;
            } catch (e) {
                // Ignore errors
            }
        }

        // Update ask-heap-stack status bar (PREFIX)
        askHeapStackStatusBarItem.text = `$(list-ordered) (${askCurrent}/${askTotal}) #ask-heap-stack`;
        askHeapStackStatusBarItem.show();
    }

    // Get notifications data
    if (showNotifications && notificationsStatusBarItem) {
        const notificationsFile = path.join(workspaceRoot, 'data', 'ide_notifications', 'notifications.json');
        let notificationCount = 0;

        if (fs.existsSync(notificationsFile)) {
            try {
                const data = JSON.parse(fs.readFileSync(notificationsFile, 'utf-8'));
                notificationCount = data.count || (data.notifications?.length || 0);
            } catch (e) {
                // Ignore errors
            }
        }

        // Update notifications status bar (SUFFIX)
        notificationsStatusBarItem.text = `$(bell) (${notificationCount}) #notifications [IDE-QUEUE]`;
        notificationsStatusBarItem.show();
    }
}

export function deactivate() {
    // Cleanup
    if (progressStatusInterval) {
        clearInterval(progressStatusInterval);
    }
    if (footerCustomizationInterval) {
        clearInterval(footerCustomizationInterval);
    }
}
