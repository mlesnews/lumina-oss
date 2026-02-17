import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

interface FileSession {
    filePath: string;
    openedAt: Date;
    lastAccessed: Date;
    isPinned: boolean;
    pinReason?: string;
    workspace: string;
    fileType: string;
}

class FileAutoCloseManager {
    private activeFiles: Map<string, FileSession> = new Map();
    private pinnedFiles: Set<string> = new Set();
    private checkInterval: NodeJS.Timeout | null = null;
    private dataDir: string;

    constructor(private context: vscode.ExtensionContext) {
        this.dataDir = path.join(context.globalStorageUri.fsPath, 'fileAutoClose');
        this.ensureDataDir();

        // Load existing data
        this.loadData();

        // Start monitoring
        this.startMonitoring();
    }

    private ensureDataDir(): void {
        if (!fs.existsSync(this.dataDir)) {
            fs.mkdirSync(this.dataDir, { recursive: true });
        }
    }

    private loadData(): void {
        try {
            // Load active files
            const activeFile = path.join(this.dataDir, 'active_files.json');
            if (fs.existsSync(activeFile)) {
                const data = JSON.parse(fs.readFileSync(activeFile, 'utf8'));
                for (const [filePath, session] of Object.entries(data)) {
                    const sess = session as any;
                    this.activeFiles.set(filePath, {
                        ...sess,
                        openedAt: new Date(sess.openedAt),
                        lastAccessed: new Date(sess.lastAccessed)
                    });
                }
            }

            // Load pinned files
            const pinnedFile = path.join(this.dataDir, 'pinned_files.json');
            if (fs.existsSync(pinnedFile)) {
                const data = JSON.parse(fs.readFileSync(pinnedFile, 'utf8'));
                this.pinnedFiles = new Set(data.pinnedFiles || []);
            }
        } catch (error) {
            console.error('Failed to load file auto-close data:', error);
        }
    }

    private saveData(): void {
        try {
            // Save active files
            const activeData: any = {};
            for (const [filePath, session] of this.activeFiles.entries()) {
                activeData[filePath] = {
                    ...session,
                    openedAt: session.openedAt.toISOString(),
                    lastAccessed: session.lastAccessed.toISOString()
                };
            }
            fs.writeFileSync(
                path.join(this.dataDir, 'active_files.json'),
                JSON.stringify(activeData, null, 2)
            );

            // Save pinned files
            fs.writeFileSync(
                path.join(this.dataDir, 'pinned_files.json'),
                JSON.stringify({ pinnedFiles: Array.from(this.pinnedFiles) }, null, 2)
            );
        } catch (error) {
            console.error('Failed to save file auto-close data:', error);
        }
    }

    public registerFileOpen(document: vscode.TextDocument): void {
        const filePath = path.resolve(document.uri.fsPath);
        const workspace = vscode.workspace.getWorkspaceFolder(document.uri)?.uri.fsPath || '';

        if (this.activeFiles.has(filePath)) {
            // Update last accessed
            const session = this.activeFiles.get(filePath)!;
            session.lastAccessed = new Date();
        } else {
            // Create new session
            const session: FileSession = {
                filePath,
                openedAt: new Date(),
                lastAccessed: new Date(),
                isPinned: this.pinnedFiles.has(filePath),
                workspace,
                fileType: this.getFileType(filePath)
            };
            this.activeFiles.set(filePath, session);
        }

        this.saveData();
    }

    public pinFile(filePath: string, reason?: string): boolean {
        const resolvedPath = path.resolve(filePath);
        this.pinnedFiles.add(resolvedPath);

        if (this.activeFiles.has(resolvedPath)) {
            const session = this.activeFiles.get(resolvedPath)!;
            session.isPinned = true;
            session.pinReason = reason;
        }

        this.saveData();
        return true;
    }

    public unpinFile(filePath: string): boolean {
        const resolvedPath = path.resolve(filePath);
        this.pinnedFiles.delete(resolvedPath);

        if (this.activeFiles.has(resolvedPath)) {
            const session = this.activeFiles.get(resolvedPath)!;
            session.isPinned = false;
            session.pinReason = undefined;
        }

        this.saveData();
        return true;
    }

    private getFileType(filePath: string): string {
        const ext = path.extname(filePath).toLowerCase();
        const typeMap: { [key: string]: string } = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql'
        };
        return typeMap[ext] || 'unknown';
    }

    private startMonitoring(): void {
        const config = vscode.workspace.getConfiguration('luminaFileAutoClose');
        const enabled = config.get('enabled', true);
        const checkInterval = config.get('checkIntervalSeconds', 60);

        if (enabled) {
            this.checkInterval = setInterval(() => {
                this.processAutoClose();
            }, checkInterval * 1000);
        }
    }

    private stopMonitoring(): void {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }

    private async processAutoClose(): Promise<void> {
        const config = vscode.workspace.getConfiguration('luminaFileAutoClose');
        const autoCloseMinutes = config.get('autoCloseMinutes', 30);
        const showNotifications = config.get('showNotifications', true);

        const candidates: string[] = [];

        // Find files eligible for auto-close
        for (const [filePath, session] of this.activeFiles.entries()) {
            if (!session.isPinned) {
                const ageMinutes = (Date.now() - session.openedAt.getTime()) / (1000 * 60);
                if (ageMinutes >= autoCloseMinutes) {
                    candidates.push(filePath);
                }
            }
        }

        let closedCount = 0;
        for (const filePath of candidates.slice(0, 5)) { // Limit concurrent closes
            try {
                // Evaluate with V3 + JARVIS decisioning
                const shouldClose = await this.evaluateFileForClose(filePath);

                if (shouldClose) {
                    const success = await this.closeFileInVSCode(filePath);
                    if (success) {
                        this.activeFiles.delete(filePath);
                        closedCount++;

                        if (showNotifications) {
                            vscode.window.showInformationMessage(
                                `Auto-closed file: ${path.basename(filePath)}`
                            );
                        }
                    }
                }
            } catch (error) {
                console.error(`Failed to process auto-close for ${filePath}:`, error);
            }
        }

        if (closedCount > 0) {
            this.saveData();
        }
    }

    private async evaluateFileForClose(filePath: string): Promise<boolean> {
        const session = this.activeFiles.get(filePath);
        if (!session) return false;

        const config = vscode.workspace.getConfiguration('luminaFileAutoClose');
        const v3Threshold = config.get('v3ConfidenceThreshold', 0.7);
        const jarvisEnabled = config.get('jarvisOverrideEnabled', true);

        // V3 Decisioning
        const v3Decision = this.v3Evaluate(session);

        // JARVIS Override (simplified for extension)
        if (jarvisEnabled) {
            const jarvisDecision = await this.jarvisEvaluate(session, v3Decision);
            return jarvisDecision.shouldClose;
        }

        return v3Decision.score >= v3Threshold;
    }

    private v3Evaluate(session: FileSession): { score: number; reason: string } {
        let score = 0;
        const reasons: string[] = [];

        // Age factor
        const ageMinutes = (Date.now() - session.openedAt.getTime()) / (1000 * 60);
        if (ageMinutes > 60) score += 0.4;
        else if (ageMinutes > 30) score += 0.2;

        // File type importance
        const importantTypes = ['python', 'javascript', 'typescript', 'java', 'cpp'];
        if (importantTypes.includes(session.fileType)) {
            score -= 0.2;
        }

        // Source files are important
        if (session.filePath.includes('/src/') || session.filePath.includes('\\src\\')) {
            score -= 0.1;
        }

        return { score, reason: reasons.join('; ') || 'V3 evaluation' };
    }

    private async jarvisEvaluate(session: FileSession, v3Decision: { score: number }):
        Promise<{ shouldClose: boolean; reason: string }> {

        // Check for critical indicators
        const criticalIndicators: string[] = [];

        // Check if file is currently being edited
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && path.resolve(activeEditor.document.uri.fsPath) === session.filePath) {
            criticalIndicators.push('currently_edited');
        }

        // Check if file has unsaved changes
        const tabs = vscode.window.tabGroups.all.flatMap(tg => tg.tabs);
        const fileTab = tabs.find(tab =>
            tab.input instanceof vscode.TabInputText &&
            path.resolve(tab.input.uri.fsPath) === session.filePath
        );
        if (fileTab && (fileTab as any).isDirty) {
            criticalIndicators.push('unsaved_changes');
        }

        // JARVIS decision
        if (criticalIndicators.length > 0) {
            return {
                shouldClose: false,
                reason: `JARVIS override: ${criticalIndicators.join(', ')}`
            };
        }

        // Check for auto-close indicators
        const closeIndicators: string[] = [];
        const ageHours = (Date.now() - session.openedAt.getTime()) / (1000 * 60 * 60);

        if (ageHours > 2) {
            closeIndicators.push('very_old');
        }

        if (closeIndicators.length > 0) {
            return {
                shouldClose: true,
                reason: `JARVIS override: ${closeIndicators.join(', ')}`
            };
        }

        // Return V3 decision
        return {
            shouldClose: v3Decision.score >= 0.7,
            reason: v3Decision.reason
        };
    }

    private async closeFileInVSCode(filePath: string): Promise<boolean> {
        try {
            // Find the tab for this file
            const tabs = vscode.window.tabGroups.all.flatMap(tg => tg.tabs);
            const fileTab = tabs.find(tab =>
                tab.input instanceof vscode.TabInputText &&
                path.resolve(tab.input.uri.fsPath) === filePath
            );

            if (fileTab) {
                // Close the tab
                await vscode.window.tabGroups.close(fileTab);
                return true;
            }

            return false;
        } catch (error) {
            console.error(`Failed to close file ${filePath}:`, error);
            return false;
        }
    }

    public getStatus(): any {
        const activeFiles = Array.from(this.activeFiles.values());
        const pinnedCount = activeFiles.filter(s => s.isPinned).length;

        return {
            activeFiles: activeFiles.length,
            pinnedFiles: pinnedCount,
            autoCloseThreshold: vscode.workspace.getConfiguration('luminaFileAutoClose').get('autoCloseMinutes', 30)
        };
    }

    public dispose(): void {
        this.stopMonitoring();
        this.saveData();
    }
}

let fileManager: FileAutoCloseManager | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('Lumina File Auto-Close extension is now active!');

    // Initialize the file manager
    fileManager = new FileAutoCloseManager(context);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('luminaFileAutoClose.closeFile', async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                const success = await fileManager!.closeFileInVSCode(activeEditor.document.uri.fsPath);
                if (success) {
                    vscode.window.showInformationMessage('File closed successfully');
                } else {
                    vscode.window.showErrorMessage('Failed to close file');
                }
            }
        }),

        vscode.commands.registerCommand('luminaFileAutoClose.pinFile', async (uri?: vscode.Uri) => {
            let filePath: string;

            if (uri) {
                filePath = uri.fsPath;
            } else {
                const activeEditor = vscode.window.activeTextEditor;
                if (!activeEditor) {
                    vscode.window.showErrorMessage('No active file to pin');
                    return;
                }
                filePath = activeEditor.document.uri.fsPath;
            }

            const reason = await vscode.window.showInputBox({
                prompt: 'Reason for pinning (optional)',
                placeHolder: 'e.g., Currently working on this file'
            });

            const success = fileManager!.pinFile(filePath, reason);
            if (success) {
                vscode.window.showInformationMessage(
                    `File pinned: ${path.basename(filePath)}`
                );
            }
        }),

        vscode.commands.registerCommand('luminaFileAutoClose.unpinFile', async (uri?: vscode.Uri) => {
            let filePath: string;

            if (uri) {
                filePath = uri.fsPath;
            } else {
                const activeEditor = vscode.window.activeTextEditor;
                if (!activeEditor) {
                    vscode.window.showErrorMessage('No active file to unpin');
                    return;
                }
                filePath = activeEditor.document.uri.fsPath;
            }

            const success = fileManager!.unpinFile(filePath);
            if (success) {
                vscode.window.showInformationMessage(
                    `File unpinned: ${path.basename(filePath)}`
                );
            }
        }),

        vscode.commands.registerCommand('luminaFileAutoClose.showStatus', () => {
            const status = fileManager!.getStatus();
            const message = `Active Files: ${status.activeFiles}, Pinned: ${status.pinnedFiles}, Auto-close after: ${status.autoCloseThreshold} minutes`;
            vscode.window.showInformationMessage(message);
        }),

        vscode.commands.registerCommand('luminaFileAutoClose.evaluateFile', async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                vscode.window.showErrorMessage('No active file to evaluate');
                return;
            }

            const filePath = activeEditor.document.uri.fsPath;
            const shouldClose = await fileManager!.evaluateFileForClose(filePath);

            const message = shouldClose
                ? `File should be closed: ${path.basename(filePath)}`
                : `File should remain open: ${path.basename(filePath)}`;

            vscode.window.showInformationMessage(message);
        })
    );

    // Track file openings
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(document => {
            if (document.uri.scheme === 'file') {
                fileManager!.registerFileOpen(document);
            }
        }),

        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor && editor.document.uri.scheme === 'file') {
                fileManager!.registerFileOpen(editor.document);
            }
        })
    );

    // Register existing open documents
    vscode.workspace.textDocuments.forEach(document => {
        if (document.uri.scheme === 'file') {
            fileManager!.registerFileOpen(document);
        }
    });
}

export function deactivate() {
    if (fileManager) {
        fileManager.dispose();
    }
}



