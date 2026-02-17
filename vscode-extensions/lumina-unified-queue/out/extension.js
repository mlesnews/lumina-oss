"use strict";
/**
 * LUMINA Unified Queue Status Bar Extension
 * Displays unified queue (sources, problems, tasks) in IDE footer
 *
 * Part of LUMINA Core
 *
 * @author JARVIS System
 * @date 2026-01-10
 * @tags #JARVIS @LUMINA #CURSOR #FOOTER #QUEUE #UNIFIED
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
function activate(context) {
    console.log('LUMINA Unified Queue Status Bar is now active!');
    const config = vscode.workspace.getConfiguration('lumina.unifiedQueue');
    const updateInterval = config.get('updateInterval', 2000);
    const showInStatusBar = config.get('showInStatusBar', true);
    const showDetails = config.get('showDetails', true);
    if (!showInStatusBar) {
        return;
    }
    // Create status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 900 // Priority - appears before other items
    );
    statusBarItem.command = 'lumina.unifiedQueue.showDetails';
    statusBarItem.tooltip = 'Click to show unified queue details';
    // Get workspace root
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
        vscode.window.showWarningMessage('No workspace folder found. Unified queue status will not be displayed.');
        return;
    }
    const queueStateFile = path.join(workspaceRoot, 'data', 'unified_queue', 'queue_state.json');
    function updateStatusBar() {
        try {
            if (!fs.existsSync(queueStateFile)) {
                statusBarItem.text = '$(list-unordered) Queue: 0';
                statusBarItem.tooltip = 'Unified Queue: No items\nClick to open queue viewer';
                statusBarItem.show();
                return;
            }
            const stateData = fs.readFileSync(queueStateFile, 'utf8');
            const state = JSON.parse(stateData);
            const summary = state.summary;
            const total = summary.total_items;
            const pending = summary.pending_count;
            const processing = summary.processing_count;
            const completed = summary.completed_count;
            const failed = summary.failed_count;
            // Build display text
            let displayText = '$(list-unordered)';
            // Show total with active indicator
            if (processing > 0) {
                displayText += ` $(sync~spin) ${total}`;
            }
            else if (pending > 0) {
                displayText += ` $(clock) ${total}`;
            }
            else {
                displayText += ` ${total}`;
            }
            // Add status indicators
            const indicators = [];
            if (processing > 0) {
                indicators.push(`⚙️${processing}`);
            }
            if (pending > 0) {
                indicators.push(`⏳${pending}`);
            }
            if (failed > 0) {
                indicators.push(`❌${failed}`);
            }
            if (completed > 0 && total <= 10) {
                indicators.push(`✅${completed}`);
            }
            if (indicators.length > 0) {
                displayText += ' ' + indicators.join(' ');
            }
            statusBarItem.text = displayText;
            // Build tooltip
            const tooltipParts = [
                '**Unified Queue**',
                `Total: ${total}`,
                `Pending: ${pending}`,
                `Processing: ${processing}`,
                `Completed: ${completed}`,
                `Failed: ${failed}`
            ];
            // Add type breakdown
            if (Object.keys(summary.by_type).length > 0) {
                tooltipParts.push('');
                tooltipParts.push('**By Type:**');
                for (const [type, count] of Object.entries(summary.by_type)) {
                    const icons = {
                        'source': '🔗',
                        'problem': '⚠️',
                        'task': '📝',
                        'notification': '🔔',
                        'alert': '🚨',
                        'chat_history': '💬'
                    };
                    const icon = icons[type] || '•';
                    tooltipParts.push(`  ${icon} ${type}: ${count}`);
                }
            }
            tooltipParts.push('');
            tooltipParts.push('Click to show details');
            statusBarItem.tooltip = tooltipParts.join('\n');
            statusBarItem.show();
        }
        catch (error) {
            console.error('Error updating unified queue status bar:', error);
            statusBarItem.text = '$(error) Queue: Error';
            statusBarItem.tooltip = 'Error reading queue state';
            statusBarItem.show();
        }
    }
    // Initial update
    updateStatusBar();
    // Set up file watcher
    const queueStateWatcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(workspaceRoot, 'data/unified_queue/queue_state.json'));
    queueStateWatcher.onDidChange(() => {
        updateStatusBar();
    });
    queueStateWatcher.onDidCreate(() => {
        updateStatusBar();
    });
    // Set up interval update
    const interval = setInterval(() => {
        updateStatusBar();
    }, updateInterval);
    // Register command to show details
    const showDetailsCommand = vscode.commands.registerCommand('lumina.unifiedQueue.showDetails', () => {
        try {
            if (!fs.existsSync(queueStateFile)) {
                vscode.window.showInformationMessage('Queue state file not found. Queue is empty.');
                return;
            }
            const stateData = fs.readFileSync(queueStateFile, 'utf8');
            const state = JSON.parse(stateData);
            const summary = state.summary;
            const items = state.items || [];
            // Build details message
            const details = [
                '**Unified Queue Summary**',
                '',
                `**Total Items:** ${summary.total_items}`,
                `**Pending:** ${summary.pending_count}`,
                `**Processing:** ${summary.processing_count}`,
                `**Completed:** ${summary.completed_count}`,
                `**Failed:** ${summary.failed_count}`,
                ''
            ];
            // Add type breakdown
            if (Object.keys(summary.by_type).length > 0) {
                details.push('**By Type:**');
                for (const [type, count] of Object.entries(summary.by_type)) {
                    const icons = {
                        'source': '🔗',
                        'problem': '⚠️',
                        'task': '📝',
                        'notification': '🔔',
                        'alert': '🚨',
                        'chat_history': '💬'
                    };
                    const icon = icons[type] || '•';
                    details.push(`  ${icon} ${type}: ${count}`);
                }
                details.push('');
            }
            // Add status breakdown
            if (Object.keys(summary.by_status).length > 0) {
                details.push('**By Status:**');
                for (const [status, count] of Object.entries(summary.by_status)) {
                    details.push(`  ${status}: ${count}`);
                }
                details.push('');
            }
            // Show recent items
            const recentItems = items
                .filter(item => item.status !== 'completed')
                .sort((a, b) => a.priority - b.priority)
                .slice(0, 5);
            if (recentItems.length > 0) {
                details.push('**Recent Items:**');
                for (const item of recentItems) {
                    const icons = {
                        'source': '🔗',
                        'problem': '⚠️',
                        'task': '📝',
                        'chat_history': '💬'
                    };
                    const icon = icons[item.item_type] || '•';
                    const statusIcons = {
                        'pending': '⏳',
                        'processing': '⚙️',
                        'failed': '❌'
                    };
                    const statusIcon = statusIcons[item.status] || '•';
                    details.push(`  ${icon} ${statusIcon} ${item.title.substring(0, 40)}`);
                }
            }
            details.push('');
            details.push('Run `python scripts/python/unified_queue_viewer.py` for full view');
            vscode.window.showInformationMessage(details.join('\n'), { modal: true });
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error reading queue state: ${error}`);
        }
    });
    // Register command to open queue viewer
    const openViewerCommand = vscode.commands.registerCommand('lumina.unifiedQueue.openViewer', () => {
        const terminal = vscode.window.createTerminal('Unified Queue Viewer');
        terminal.sendText('python scripts/python/unified_queue_viewer.py');
        terminal.show();
    });
    // Register refresh command
    const refreshCommand = vscode.commands.registerCommand('lumina.unifiedQueue.refresh', () => {
        updateStatusBar();
        vscode.window.showInformationMessage('Unified queue status refreshed');
    });
    context.subscriptions.push(statusBarItem, queueStateWatcher, showDetailsCommand, openViewerCommand, refreshCommand);
    // Cleanup interval on deactivate
    context.subscriptions.push({
        dispose: () => clearInterval(interval)
    });
}
function deactivate() {
    // Cleanup
}
//# sourceMappingURL=extension.js.map