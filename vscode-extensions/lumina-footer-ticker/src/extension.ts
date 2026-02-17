/**
 * LUMINA Footer Ticker Banner Extension
 * Airport ticker / LED sign effect for Cursor IDE footer
 * Shows ACTUAL operational data - not just labels
 * 
 * Part of LUMINA Core
 * 
 * @author JARVIS System
 * @date 2026-01-09
 * @updated 2026-02-04 - Added real data fetching
 * @tags #JARVIS @LUMINA #CURSOR #FOOTER #TICKER #BANNER #LUMINA_CORE
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface TickerItem {
    id: string;
    text: string;
    priority: number;
    icon?: string;
    data_source?: string;
    value?: string;
}

interface TickerData {
    ai_model: string;
    gpu_status: string;
    todo_count: string;
    ticket_queue: string;
    git_branch: string;
    git_status: string;
    nas_status: string;
    session_time: string;
    api_cost: string;
    agents_active: string;
    errors: string;
    warnings: string;
}

// Session start time for duration tracking
const sessionStartTime = Date.now();

export function activate(context: vscode.ExtensionContext) {
    console.log('LUMINA Footer Ticker Banner is now active!');

    const config = vscode.workspace.getConfiguration('lumina.footerTicker');
    const enabled = config.get<boolean>('enabled', true);

    if (!enabled) {
        return;
    }

    // Create ticker status bar item
    const tickerItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        1000
    );

    let currentIndex = 0;
    let isPaused = false;
    let cachedData: TickerData = getDefaultData();
    let lastDataRefresh = 0;

    // Refresh data every 30 seconds (commands can be slow)
    const DATA_REFRESH_INTERVAL = 30000;

    // Update ticker display with real data
    async function updateTicker() {
        if (isPaused) {
            return;
        }

        // Refresh data periodically
        const now = Date.now();
        if (now - lastDataRefresh > DATA_REFRESH_INTERVAL) {
            lastDataRefresh = now;
            cachedData = await fetchAllData();
        }

        // Build display items with real values
        const items = buildTickerItems(cachedData);
        
        if (items.length === 0) {
            return;
        }

        // Show 4 items at a time for readability
        const visibleCount = 4;
        const visibleItems: string[] = [];
        
        for (let i = 0; i < visibleCount; i++) {
            const item = items[(currentIndex + i) % items.length];
            visibleItems.push(item);
        }

        const displayText = visibleItems.join('  │  ');

        tickerItem.text = displayText;
        tickerItem.tooltip = buildTooltip(cachedData);
        tickerItem.command = 'lumina.footerTicker.toggle';
        tickerItem.show();

        // Rotate to next item
        currentIndex = (currentIndex + 1) % items.length;
    }

    // Update display every 3 seconds
    const displayInterval = setInterval(updateTicker, 3000);
    
    // Initial update
    updateTicker();

    // Toggle pause command
    const toggleCommand = vscode.commands.registerCommand('lumina.footerTicker.toggle', () => {
        isPaused = !isPaused;
        if (!isPaused) {
            updateTicker();
        }
        vscode.window.showInformationMessage(
            `LUMINA Footer Ticker: ${isPaused ? 'Paused' : 'Resumed'}`
        );
    });

    // Force refresh command
    const refreshCommand = vscode.commands.registerCommand('lumina.footerTicker.refresh', async () => {
        lastDataRefresh = 0;
        await updateTicker();
        vscode.window.showInformationMessage('LUMINA Footer Ticker: Data refreshed');
    });

    context.subscriptions.push(tickerItem);
    context.subscriptions.push(toggleCommand);
    context.subscriptions.push(refreshCommand);
    context.subscriptions.push({
        dispose: () => clearInterval(displayInterval)
    });
}

function getDefaultData(): TickerData {
    return {
        ai_model: 'Loading...',
        gpu_status: 'Loading...',
        todo_count: 'Loading...',
        ticket_queue: 'Loading...',
        git_branch: 'Loading...',
        git_status: 'Loading...',
        nas_status: 'Loading...',
        session_time: formatSessionTime(),
        api_cost: 'N/A',
        agents_active: 'Loading...',
        errors: '0',
        warnings: '0'
    };
}

async function fetchAllData(): Promise<TickerData> {
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';
    
    // Fetch all data in parallel for speed
    const [
        aiModel,
        gpuStatus,
        todoCount,
        ticketQueue,
        gitBranch,
        gitStatus,
        nasStatus,
        agentsActive,
        diagnostics
    ] = await Promise.all([
        fetchAiModel(),
        fetchGpuStatus(),
        fetchTodoCount(workspaceRoot),
        fetchTicketQueue(workspaceRoot),
        fetchGitBranch(workspaceRoot),
        fetchGitStatus(workspaceRoot),
        fetchNasStatus(),
        fetchAgentsActive(workspaceRoot),
        fetchDiagnostics()
    ]);

    return {
        ai_model: aiModel,
        gpu_status: gpuStatus,
        todo_count: todoCount,
        ticket_queue: ticketQueue,
        git_branch: gitBranch,
        git_status: gitStatus,
        nas_status: nasStatus,
        session_time: formatSessionTime(),
        api_cost: 'N/A', // Would need API tracking
        agents_active: agentsActive,
        errors: diagnostics.errors.toString(),
        warnings: diagnostics.warnings.toString()
    };
}

async function fetchAiModel(): Promise<string> {
    try {
        const { stdout } = await execAsync('ollama ps', { timeout: 5000 });
        const lines = stdout.trim().split('\n');
        if (lines.length > 1) {
            // Parse the model name from ollama ps output
            const modelLine = lines[1];
            const parts = modelLine.split(/\s+/);
            if (parts.length > 0) {
                const modelName = parts[0];
                // Try to get GPU percentage from nvidia-smi
                return modelName;
            }
        }
        return 'No model';
    } catch {
        return 'Ollama offline';
    }
}

async function fetchGpuStatus(): Promise<string> {
    try {
        const { stdout } = await execAsync(
            'nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits',
            { timeout: 5000 }
        );
        const parts = stdout.trim().split(',').map(s => s.trim());
        if (parts.length >= 2) {
            const used = Math.round(parseInt(parts[0]) / 1024);
            const total = Math.round(parseInt(parts[1]) / 1024);
            const percent = Math.round((used / total) * 100);
            return `${used}GB/${total}GB (${percent}%)`;
        }
        return 'N/A';
    } catch {
        return 'No GPU';
    }
}

async function fetchTodoCount(workspaceRoot: string): Promise<string> {
    try {
        const roadmapPath = path.join(workspaceRoot, 'data', 'roadmap', 'master_roadmap.json');
        if (fs.existsSync(roadmapPath)) {
            const data = JSON.parse(fs.readFileSync(roadmapPath, 'utf-8'));
            let pending = 0;
            let high = 0;
            
            // Count tasks from roadmap structure
            if (data.tasks && Array.isArray(data.tasks)) {
                for (const task of data.tasks) {
                    if (task.status === 'pending' || task.status === 'in_progress') {
                        pending++;
                        if (task.priority === 'high' || task.priority === 'critical') {
                            high++;
                        }
                    }
                }
            }
            // Also check phases structure
            if (data.phases && Array.isArray(data.phases)) {
                for (const phase of data.phases) {
                    if (phase.milestones && Array.isArray(phase.milestones)) {
                        for (const milestone of phase.milestones) {
                            if (milestone.status !== 'completed' && milestone.status !== 'done') {
                                pending++;
                            }
                        }
                    }
                }
            }
            
            return high > 0 ? `${pending} (${high} high)` : `${pending} pending`;
        }
        return '0';
    } catch {
        return 'Error';
    }
}

async function fetchTicketQueue(workspaceRoot: string): Promise<string> {
    try {
        const ticketsDir = path.join(workspaceRoot, 'data', 'helpdesk', 'tickets');
        if (fs.existsSync(ticketsDir)) {
            const files = fs.readdirSync(ticketsDir).filter(f => f.endsWith('.json'));
            let open = 0;
            
            for (const file of files) {
                try {
                    const ticketPath = path.join(ticketsDir, file);
                    const ticket = JSON.parse(fs.readFileSync(ticketPath, 'utf-8'));
                    if (ticket.status === 'open' || ticket.status === 'in_progress' || 
                        ticket.status === 'pending' || !ticket.status) {
                        open++;
                    }
                } catch {
                    // Skip invalid tickets
                }
            }
            
            return `${open} open`;
        }
        return '0';
    } catch {
        return 'Error';
    }
}

async function fetchGitBranch(workspaceRoot: string): Promise<string> {
    try {
        const { stdout } = await execAsync('git branch --show-current', { 
            cwd: workspaceRoot,
            timeout: 3000 
        });
        const branch = stdout.trim();
        // Truncate long branch names
        if (branch.length > 25) {
            return branch.substring(0, 22) + '...';
        }
        return branch || 'detached';
    } catch {
        return 'No repo';
    }
}

async function fetchGitStatus(workspaceRoot: string): Promise<string> {
    try {
        const { stdout } = await execAsync('git status --porcelain', { 
            cwd: workspaceRoot,
            timeout: 5000 
        });
        const lines = stdout.trim().split('\n').filter(l => l.length > 0);
        const count = lines.length;
        return count > 0 ? `${count} files` : 'Clean';
    } catch {
        return 'N/A';
    }
}

async function fetchNasStatus(): Promise<string> {
    try {
        // Try to ping NAS (<NAS_PRIMARY_IP> per host_identity_registry)
        const { stdout } = await execAsync('ping -n 1 -w 1000 <NAS_PRIMARY_IP>', { timeout: 3000 });
        if (stdout.includes('TTL=') || stdout.includes('time=')) {
            return 'Online';
        }
        return 'Offline';
    } catch {
        return 'Offline';
    }
}

async function fetchAgentsActive(workspaceRoot: string): Promise<string> {
    try {
        const instancesPath = path.join(workspaceRoot, 'data', 'jarvis_instances', 'instances.json');
        if (fs.existsSync(instancesPath)) {
            const data = JSON.parse(fs.readFileSync(instancesPath, 'utf-8'));
            if (data.instances && Array.isArray(data.instances)) {
                const active = data.instances.filter((i: any) => 
                    i.status === 'active' || i.status === 'running'
                ).length;
                return `${active} active`;
            }
        }
        return '0';
    } catch {
        return 'N/A';
    }
}

function fetchDiagnostics(): { errors: number; warnings: number } {
    let errors = 0;
    let warnings = 0;
    
    // Get diagnostics from VS Code
    const allDiagnostics = vscode.languages.getDiagnostics();
    for (const [, diagnostics] of allDiagnostics) {
        for (const diag of diagnostics) {
            if (diag.severity === vscode.DiagnosticSeverity.Error) {
                errors++;
            } else if (diag.severity === vscode.DiagnosticSeverity.Warning) {
                warnings++;
            }
        }
    }
    
    return { errors, warnings };
}

function formatSessionTime(): string {
    const elapsed = Date.now() - sessionStartTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

function buildTickerItems(data: TickerData): string[] {
    const items: string[] = [];
    
    // AI Model & GPU
    items.push(`🤖 ${data.ai_model}`);
    items.push(`📊 ${data.gpu_status}`);
    
    // Work items
    items.push(`📋 ${data.todo_count}`);
    items.push(`🎫 ${data.ticket_queue}`);
    
    // Git status
    items.push(`🌿 ${data.git_branch}`);
    if (data.git_status !== 'Clean') {
        items.push(`⚠️ ${data.git_status}`);
    }
    
    // Infrastructure
    items.push(`💾 NAS: ${data.nas_status}`);
    
    // Session
    items.push(`⏰ ${data.session_time}`);
    
    // Diagnostics (only if there are issues)
    const errors = parseInt(data.errors) || 0;
    const warnings = parseInt(data.warnings) || 0;
    if (errors > 0) {
        items.push(`❌ ${errors} errors`);
    }
    if (warnings > 0) {
        items.push(`⚠️ ${warnings} warnings`);
    }
    
    // Agents
    if (data.agents_active !== '0' && data.agents_active !== 'N/A') {
        items.push(`🤝 ${data.agents_active}`);
    }
    
    return items;
}

function buildTooltip(data: TickerData): string {
    return `LUMINA Footer Ticker
━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Model: ${data.ai_model}
📊 GPU VRAM: ${data.gpu_status}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 TODOs: ${data.todo_count}
🎫 Tickets: ${data.ticket_queue}
🤝 Agents: ${data.agents_active}
━━━━━━━━━━━━━━━━━━━━━━━━
🌿 Branch: ${data.git_branch}
⚠️ Uncommitted: ${data.git_status}
💾 NAS: ${data.nas_status}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Session: ${data.session_time}
❌ Errors: ${data.errors}
⚠️ Warnings: ${data.warnings}
━━━━━━━━━━━━━━━━━━━━━━━━
Click to pause/resume
Run 'LUMINA: Refresh Footer' to force update`;
}

export function deactivate() {
    // Cleanup
}
