import axios from "axios";
import { exec } from "child_process";
import * as fs from "fs";
import * as path from "path";
import { promisify } from "util";
import * as vscode from "vscode";

const execAsync = promisify(exec);

// @DOIT Infinite Memory - Never Forget
let DOIT_DEFINITION: any = null;

function loadDOITDefinition(workspaceRoot: string): any {
  if (DOIT_DEFINITION) {
    return DOIT_DEFINITION;
  }

  const memoryLocations = [
    path.join(
      workspaceRoot,
      "data",
      "memory",
      "infinite",
      "DOIT_DEFINITION.json"
    ),
    path.join(workspaceRoot, "data", "holocrons", "DOIT_DEFINITION.json"),
    path.join(workspaceRoot, "config", "core_definitions", "DOIT.json"),
  ];

  for (const location of memoryLocations) {
    try {
      if (fs.existsSync(location)) {
        DOIT_DEFINITION = JSON.parse(fs.readFileSync(location, "utf-8"));
        console.log(`@DOIT definition loaded from: ${location}`);
        return DOIT_DEFINITION;
      }
    } catch (error) {
      console.error(`Error loading @DOIT from ${location}:`, error);
    }
  }

  // Fallback definition - @MEM@PERSIST@INFINITE
  DOIT_DEFINITION = {
    tag: "@DOIT",
    meaning: "DO IT - Execute, Action, Implementation",
    full_definition:
      "@DOIT = Execute the action. Do the work. Implement the solution. Take action. Complete the task. Make it happen. No delay. No questions. Just do it.",
    core_principle:
      "Action over words. Execution over planning. Doing over discussing. Results over intentions.",
    persistence: {
      "@MEM": "Must be remembered in memory - always available",
      "@PERSIST": "Must persist forever - never deleted, never forgotten",
      "@INFINITE":
        "Must be infinite - always accessible, always remembered, always applied",
    },
  };

  return DOIT_DEFINITION;
}

interface LuminaConfig {
  enabled: boolean;
  git: {
    github: {
      enabled: boolean;
      public: boolean;
      private: boolean;
    };
    gitlens: {
      enabled: boolean;
      automaticFollowup: boolean;
      prIntegration: boolean;
    };
    localEnterprise: {
      enabled: boolean;
      nasPath: string;
      autoSync: boolean;
    };
  };
  nas: {
    enabled: boolean;
    ip: string;
    path: string;
  };
  storage: {
    providers: string[];
    aggregatedPath: string;
  };
  ai: {
    autoStart: boolean;
    resourceAwareness: boolean;
    cpuThreshold: number;
  };
}

let todoStatusBarItem: vscode.StatusBarItem;
let todoStatusWatcher: vscode.FileSystemWatcher | undefined;
let todoStatusRefreshInterval: NodeJS.Timeout | undefined;

let luminaCoreOutputChannel: vscode.OutputChannel | null = null;

function luminaLog(message: string, showChannel = false): void {
  if (!luminaCoreOutputChannel) {
    luminaCoreOutputChannel = vscode.window.createOutputChannel("Lumina Core");
    luminaCoreOutputChannel.show(true);
  }
  const ts = new Date().toISOString();
  luminaCoreOutputChannel.appendLine(`[${ts}] ${message}`);
  if (showChannel && luminaCoreOutputChannel) {
    luminaCoreOutputChannel.show(true);
  }
}

function luminaLogError(message: string): void {
  luminaLog(message, true);
}

export function activate(context: vscode.ExtensionContext) {
  // Create and show output channel first so it appears in View → Output → "Lumina Core" even if later code fails
  try {
    luminaCoreOutputChannel = vscode.window.createOutputChannel("Lumina Core");
    luminaCoreOutputChannel.appendLine(
      `[${new Date().toISOString()}] Lumina Core extension activating... (View → Output → "Lumina Core" for this log)`
    );
    luminaCoreOutputChannel.show(true);
  } catch (e) {
    console.error("[Lumina Core] Failed to create output channel:", e);
  }

  context.subscriptions.push(
    vscode.commands.registerCommand("lumina.showOutput", () => {
      if (!luminaCoreOutputChannel) {
        luminaCoreOutputChannel =
          vscode.window.createOutputChannel("Lumina Core");
        luminaCoreOutputChannel.appendLine(
          "[Lumina Core] Output channel. Run this command again or open View → Output → Lumina Core."
        );
      }
      luminaCoreOutputChannel.show(true);
    })
  );

  luminaLog("activate() started");
  console.log("Lumina Core extension is now active!");

  // CA skeleton (Cline/Continue): webview first so sidebar resolves immediately; rest deferred in setImmediate.
  try {
    // Chat view is now provided by lumina-jarvis-chat extension

    // Defer heavy init so activate() returns quickly and the sidebar doesn’t spin.
    // Single command the welcome view needs so "Open JARVIS Chat" works before full init.
    context.subscriptions.push(
      vscode.commands.registerCommand("lumina.openJarvisChat", async () => {
        try {
          await vscode.commands.executeCommand("jarvis.chat.open");
        } catch {
          vscode.window.showInformationMessage(
            "Lumina JARVIS Chat (custom panel) is not installed. Install it for a chat interface like Kilo Code: run .\\applications\\ide_chat\\build_and_install.ps1 from the repo root, then reload Cursor. See docs/system/CURSOR_IDE_QOL_INDEX.md."
          );
        }
      })
    );
    luminaLog(
      "openJarvisChat command registered; scheduling full activation in 300ms"
    );
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    luminaLogError(`Lumina Core activation error (webview/commands): ${msg}`);
    if (e instanceof Error && e.stack) luminaLog(e.stack);
    console.error("[Lumina Core] Activation error:", e);
  }

  context.subscriptions.push({
    dispose: () => {
      luminaCoreOutputChannel?.dispose();
      luminaCoreOutputChannel = null;
    },
  });

  setTimeout(() => {
    try {
      luminaLog("Full activation starting...");
      runLuminaFullActivation(context);
      luminaLog("Full activation completed");
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      luminaLogError(`Full activation failed: ${msg}`);
      if (err instanceof Error && err.stack) luminaLog(err.stack);
      console.error("[Lumina Core] Full activation failed:", err);
    }
  }, 300);
}

function runLuminaFullActivation(context: vscode.ExtensionContext): void {
  luminaLog("initializeFileCleanupStack...");
  initializeFileCleanupStack(context);
  luminaLog("File cleanup stack initialized");

  // @DOIT Infinite Memory - Load and remember @DOIT definition
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (workspaceFolders && workspaceFolders.length > 0) {
    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    luminaLog(`Loading DOIT from workspace: ${workspaceRoot}`);
    const doitDefinition = loadDOITDefinition(workspaceRoot);
    console.log("@DOIT definition loaded: @MEM@PERSIST@INFINITE");
    luminaLog(`DOIT loaded: ${doitDefinition?.tag ?? "fallback"}`);
  }

  luminaLog("Registering commands...");
  // Register commands
  const openLuminaAIChatCmd = vscode.commands.registerCommand(
    "lumina.openLuminaAIChat",
    async () => {
      try {
        await vscode.commands.executeCommand("workbench.action.chat.open");
      } catch {
        try {
          await vscode.commands.executeCommand("workbench.action.chat.focus");
        } catch {
          // Fallback: user can use Ctrl+L
        }
      }
      vscode.window.showInformationMessage(
        "Lumina AI Chat: Use Voice (Play/Pause/Stop), Open Voice Request Queue, or Set Listening Mode from the command palette. Ctrl+L opens chat."
      );
    }
  );

  // Open JARVIS Chat is registered in activate() so welcome view works before full init.

  // Accept All Changes — executes the Chat/Composer "Accept All" / "Keep All" UI so proposed edits land in the buffer (accept-changes workflow).
  const acceptAllChangesCmd = vscode.commands.registerCommand(
    "lumina.acceptAllChanges",
    async () => {
      const candidates = [
        "workbench.action.chat.acceptAll",
        "aichat.acceptAll",
        "editor.action.inlineSuggest.acceptAll",
      ];
      for (const id of candidates) {
        try {
          await vscode.commands.executeCommand(id);
          vscode.window.showInformationMessage(
            `Accept All: ran command "${id}".`
          );
          return;
        } catch {
          // Try next
        }
      }
      vscode.window.showInformationMessage(
        'Accept All Changes: No Cursor command found. Use the "Accept All" / "Keep All" button in Chat or set a keyboard shortcut (e.g. Ctrl+Shift+A). See docs/workflow/CURSOR_WORKFLOW_SOLUTIONS.md.'
      );
    }
  );

  const openVoiceRequestQueueCmd = vscode.commands.registerCommand(
    "lumina.voiceRequestQueue.open",
    () => {
      openVoiceRequestQueuePanel();
    }
  );
  const addCurrentToVoiceQueueCmd = vscode.commands.registerCommand(
    "lumina.voiceRequestQueue.addCurrent",
    async () => {
      let text = luminaVoiceControls?.getPendingText()?.trim() || "";
      if (!text) {
        const editor = vscode.window.activeTextEditor;
        if (editor && !editor.selection.isEmpty) {
          text = editor.document.getText(editor.selection);
        }
      }
      if (!text) {
        vscode.window.showWarningMessage(
          "No text to add. Speak with voice (Play) or select text in the editor."
        );
        return;
      }
      const item = addToVoiceRequestQueue(text, "manual");
      if (item) {
        vscode.window.showInformationMessage("Added to Voice Request Queue");
        luminaVoiceControls?.clearPendingText();
      }
    }
  );
  const setListeningModeActiveCmd = vscode.commands.registerCommand(
    "lumina.voiceRequestQueue.setListeningModeActive",
    async () => {
      await vscode.workspace
        .getConfiguration("lumina.voiceRequestQueue")
        .update("listeningMode", "active", vscode.ConfigurationTarget.Global);
      vscode.window.showInformationMessage(
        "Listening mode: Active (auto-send or add to queue)"
      );
    }
  );
  const setListeningModePassiveCmd = vscode.commands.registerCommand(
    "lumina.voiceRequestQueue.setListeningModePassive",
    async () => {
      await vscode.workspace
        .getConfiguration("lumina.voiceRequestQueue")
        .update("listeningMode", "passive", vscode.ConfigurationTarget.Global);
      vscode.window.showInformationMessage(
        "Listening mode: Passive (voice segments go to queue only)"
      );
    }
  );

  const showStatusCmd = vscode.commands.registerCommand(
    "lumina.showStatus",
    () => {
      showLuminaStatus();
    }
  );

  const showActiveModelsCmd = vscode.commands.registerCommand(
    "lumina.showActiveModels",
    () => {
      showActiveAIModels();
    }
  );

  const showGitStatusCmd = vscode.commands.registerCommand(
    "lumina.showGitStatus",
    () => {
      showGitStatus();
    }
  );

  const showNASStatusCmd = vscode.commands.registerCommand(
    "lumina.showNASStatus",
    () => {
      showNASStatus();
    }
  );

  const showStorageProvidersCmd = vscode.commands.registerCommand(
    "lumina.showStorageProviders",
    () => {
      showStorageProviders();
    }
  );

  const syncToNASCmd = vscode.commands.registerCommand(
    "lumina.syncToNAS",
    () => {
      syncToNAS();
    }
  );

  const autoStartLocalAICmd = vscode.commands.registerCommand(
    "lumina.autoStartLocalAI",
    () => {
      autoStartLocalAI();
    }
  );

  const showTodoStatus = vscode.commands.registerCommand(
    "lumina.showTodoStatus",
    () => {
      showTodoStatusPanel();
    }
  );

  const refreshTodoStatus = vscode.commands.registerCommand(
    "lumina.refreshTodoStatus",
    () => {
      refreshTodoStatusDisplay();
    }
  );

  const showTPSReportCmd = vscode.commands.registerCommand(
    "lumina.showTPSReport",
    () => {
      showTPSReportPanel();
    }
  );

  const generateTPSReportCmd = vscode.commands.registerCommand(
    "lumina.generateTPSReport",
    () => {
      generateTPSReport();
    }
  );

  const showLiveAIModelStatusCmd = vscode.commands.registerCommand(
    "lumina.showLiveAIModelStatus",
    () => {
      showLiveAIModelStatusPanel();
    }
  );

  const monitorLiveAIModelCmd = vscode.commands.registerCommand(
    "lumina.monitorLiveAIModel",
    () => {
      monitorLiveAIModel();
    }
  );

  const copyAgentRequestIdUrlCmd = vscode.commands.registerCommand(
    "lumina.copyAgentRequestIdUrl",
    () => {
      copyAgentRequestIdUrl();
    }
  );

  const applyKiloCodeSetupCmd = vscode.commands.registerCommand(
    "lumina.applyKiloCodeSetup",
    async () => {
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) {
        vscode.window.showErrorMessage(
          "Lumina: Apply Kilo Code Setup requires an open workspace folder."
        );
        return;
      }
      const extensionPath = context.extensionPath;
      const sourceDir = path.join(
        extensionPath,
        "defaults",
        "kilocode",
        "rules"
      );
      const targetDir = path.join(
        workspaceFolder.uri.fsPath,
        ".kilocode",
        "rules"
      );
      if (!fs.existsSync(sourceDir)) {
        vscode.window.showErrorMessage(
          "Lumina: Kilo Code defaults not found in extension."
        );
        return;
      }
      try {
        if (!fs.existsSync(targetDir)) {
          fs.mkdirSync(targetDir, { recursive: true });
        }
        const files = fs
          .readdirSync(sourceDir)
          .filter((f: string) => f.endsWith(".md"));
        let copied = 0;
        for (const file of files) {
          const src = path.join(sourceDir, file);
          const dest = path.join(targetDir, file);
          if (!fs.existsSync(dest)) {
            fs.copyFileSync(src, dest);
            copied++;
          }
        }
        if (copied > 0) {
          vscode.window.showInformationMessage(
            `Lumina: Kilo Code setup applied. ${copied} rule file(s) copied to .kilocode/rules/. Reload Kilo Code or start a new chat to use them.`
          );
        } else {
          vscode.window.showInformationMessage(
            "Lumina: Kilo Code rules already present in .kilocode/rules/. No files overwritten."
          );
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        vscode.window.showErrorMessage(
          `Lumina: Apply Kilo Code Setup failed: ${message}`
        );
      }
    }
  );

  // File Auto-Close Commands
  const fileAutoCloseCloseFile = vscode.commands.registerCommand(
    "lumina.fileAutoClose.closeFile",
    async () => {
      const activeEditor = vscode.window.activeTextEditor;
      if (activeEditor && fileAutoCloseManager) {
        const success = await fileAutoCloseManager.closeFileInVSCode(
          activeEditor.document.uri.fsPath
        );
        if (success) {
          vscode.window.showInformationMessage("File closed successfully");
        } else {
          vscode.window.showErrorMessage("Failed to close file");
        }
      }
    }
  );

  const fileAutoClosePinFile = vscode.commands.registerCommand(
    "lumina.fileAutoClose.pinFile",
    async (uri?: vscode.Uri) => {
      if (!fileAutoCloseManager) return;
      let filePath: string;
      if (uri) {
        filePath = uri.fsPath;
      } else {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
          vscode.window.showErrorMessage("No active file to pin");
          return;
        }
        filePath = activeEditor.document.uri.fsPath;
      }
      const reason = await vscode.window.showInputBox({
        prompt: "Reason for pinning (optional)",
        placeHolder: "e.g., Currently working on this file",
      });
      const success = fileAutoCloseManager.pinFile(filePath, reason);
      if (success) {
        vscode.window.showInformationMessage(
          `File pinned: ${path.basename(filePath)}`
        );
      }
    }
  );

  const fileAutoCloseUnpinFile = vscode.commands.registerCommand(
    "lumina.fileAutoClose.unpinFile",
    async (uri?: vscode.Uri) => {
      if (!fileAutoCloseManager) return;
      let filePath: string;
      if (uri) {
        filePath = uri.fsPath;
      } else {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
          vscode.window.showErrorMessage("No active file to unpin");
          return;
        }
        filePath = activeEditor.document.uri.fsPath;
      }
      const success = fileAutoCloseManager.unpinFile(filePath);
      if (success) {
        vscode.window.showInformationMessage(
          `File unpinned: ${path.basename(filePath)}`
        );
      }
    }
  );

  const fileAutoCloseShowStatus = vscode.commands.registerCommand(
    "lumina.fileAutoClose.showStatus",
    () => {
      if (!fileAutoCloseManager) return;
      const status = fileAutoCloseManager.getStatus();
      const message = `Active Files: ${status.activeFiles}, Pinned: ${status.pinnedFiles}, Auto-close after: ${status.autoCloseThreshold} minutes`;
      vscode.window.showInformationMessage(message);
    }
  );

  const fileAutoCloseEvaluateFile = vscode.commands.registerCommand(
    "lumina.fileAutoClose.evaluateFile",
    async () => {
      if (!fileAutoCloseManager) return;
      const activeEditor = vscode.window.activeTextEditor;
      if (!activeEditor) {
        vscode.window.showErrorMessage("No active file to evaluate");
        return;
      }
      const filePath = activeEditor.document.uri.fsPath;
      const shouldClose = await fileAutoCloseManager.evaluateFileForClose(
        filePath
      );
      const message = shouldClose
        ? `File should be closed: ${path.basename(filePath)}`
        : `File should remain open: ${path.basename(filePath)}`;
      vscode.window.showInformationMessage(message);
    }
  );

  context.subscriptions.push(
    openLuminaAIChatCmd,
    acceptAllChangesCmd,
    openVoiceRequestQueueCmd,
    addCurrentToVoiceQueueCmd,
    setListeningModeActiveCmd,
    setListeningModePassiveCmd,
    showStatusCmd,
    showActiveModelsCmd,
    showGitStatusCmd,
    showNASStatusCmd,
    showStorageProvidersCmd,
    syncToNASCmd,
    autoStartLocalAICmd,
    showTodoStatus,
    refreshTodoStatus,
    showTPSReportCmd,
    generateTPSReportCmd,
    showLiveAIModelStatusCmd,
    monitorLiveAIModelCmd,
    copyAgentRequestIdUrlCmd,
    applyKiloCodeSetupCmd,
    fileAutoCloseCloseFile,
    fileAutoClosePinFile,
    fileAutoCloseUnpinFile,
    fileAutoCloseShowStatus,
    fileAutoCloseEvaluateFile
  );
  luminaLog("All commands registered and subscribed");

  // Initialize todo status bar
  initializeTodoStatusBar(context);

  // Initialize file auto-close manager
  fileAutoCloseManager = new FileAutoCloseManager(context);

  // Track file openings for auto-close
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument((document) => {
      if (document.uri.scheme === "file" && fileAutoCloseManager) {
        fileAutoCloseManager.registerFileOpen(document);
      }
    }),
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (
        editor &&
        editor.document.uri.scheme === "file" &&
        fileAutoCloseManager
      ) {
        fileAutoCloseManager.registerFileOpen(editor.document);
      }
    })
  );

  // Register existing open documents
  vscode.workspace.textDocuments.forEach((document) => {
    if (document.uri.scheme === "file" && fileAutoCloseManager) {
      fileAutoCloseManager.registerFileOpen(document);
    }
  });

  // Initialize unified queue
  initializeUnifiedQueue(context);

  // Initialize voice request queue (Jarvis/Lumina AI Chat)
  initializeVoiceRequestQueue(context);

  // File Cleanup Stack already initialized at top of activate() for early data provider registration

  // Initialize editor validation scheduler (Ruff + Mypy when focus leaves editor)
  initializeEditorValidationScheduler(context);

  // Initialize footer ticker
  initializeFooterTicker(context);

  // Initialize voice controls
  initializeVoiceControls(context);

  // Initialize active model status
  initializeActiveModelStatus(context);

  // Initialize progress status indicator
  initializeProgressStatus(context);

  // Initialize footer customization (ask-heap-stack and notifications)
  initializeFooterCustomization(context);
  luminaLog(
    "All inits done (todo, file auto-close, queue, voice, footer, progress)"
  );

  // Show status on startup
  vscode.window.showInformationMessage("Lumina Core extension activated!");
}

async function showLuminaStatus() {
  const config = getLuminaConfig();
  const status = await getLuminaStatus(config);

  const panel = vscode.window.createWebviewPanel(
    "luminaStatus",
    "Lumina Status",
    vscode.ViewColumn.One,
    {}
  );

  panel.webview.html = generateStatusHTML(status);
}

async function showActiveAIModels() {
  try {
    // Check ULTRON
    const ultronStatus = await checkService("http://localhost:11434/api/tags");
    // Check KAIJU
    const kaijuStatus = await checkService("http://<NAS_PRIMARY_IP>:11434/api/tags");

    const message =
      `Active AI Models:\n\n` +
      `ULTRON: ${ultronStatus ? "✅ Running" : "❌ Stopped"}\n` +
      `KAIJU: ${kaijuStatus ? "✅ Running" : "❌ Stopped"}`;

    vscode.window.showInformationMessage(message);
  } catch (error) {
    vscode.window.showErrorMessage(`Error checking AI models: ${error}`);
  }
}

async function showGitStatus() {
  const config = getLuminaConfig();
  const gitStatus = {
    github: {
      enabled: config.git.github.enabled,
      public: config.git.github.public,
      private: config.git.github.private,
    },
    gitlens: {
      enabled: config.git.gitlens.enabled,
      automaticFollowup: config.git.gitlens.automaticFollowup,
      prIntegration: config.git.gitlens.prIntegration,
    },
    localEnterprise: {
      enabled: config.git.localEnterprise.enabled,
      nasPath: config.git.localEnterprise.nasPath,
      autoSync: config.git.localEnterprise.autoSync,
    },
  };

  const message =
    `Git/GitLens Status:\n\n` +
    `GitHub: ${gitStatus.github.enabled ? "✅" : "❌"} (Public: ${
      gitStatus.github.public ? "✅" : "❌"
    }, Private: ${gitStatus.github.private ? "✅" : "❌"})\n` +
    `GitLens: ${gitStatus.gitlens.enabled ? "✅" : "❌"} (Auto-Followup: ${
      gitStatus.gitlens.automaticFollowup ? "✅" : "❌"
    }, PR Integration: ${gitStatus.gitlens.prIntegration ? "✅" : "❌"})\n` +
    `Local Enterprise Git: ${
      gitStatus.localEnterprise.enabled ? "✅" : "❌"
    } (NAS: ${gitStatus.localEnterprise.nasPath})`;

  vscode.window.showInformationMessage(message);
}

async function showNASStatus() {
  const config = getLuminaConfig();
  const nasStatus = await checkNASConnection(config.nas.ip);

  const message =
    `NAS Cloud Services:\n\n` +
    `Status: ${nasStatus ? "✅ Connected" : "❌ Disconnected"}\n` +
    `IP: ${config.nas.ip}\n` +
    `Path: ${config.nas.path}`;

  vscode.window.showInformationMessage(message);
}

async function showStorageProviders() {
  const config = getLuminaConfig();
  const providers = config.storage.providers;

  const message =
    `Storage Providers:\n\n` +
    `Enabled: ${providers.join(", ")}\n` +
    `Aggregated Path: ${config.storage.aggregatedPath}`;

  vscode.window.showInformationMessage(message);
}

async function syncToNAS() {
  vscode.window.showInformationMessage("Syncing to NAS...");
  // Implement NAS sync logic
}

async function autoStartLocalAI() {
  vscode.window.showInformationMessage("Starting local AI services...");
  // Implement auto-start logic
}

function getLuminaConfig(): LuminaConfig {
  const config = vscode.workspace.getConfiguration("lumina");

  return {
    enabled: config.get<boolean>("enabled", true),
    git: {
      github: config.get("git.github", {
        enabled: true,
        public: true,
        private: true,
      }),
      gitlens: config.get("git.gitlens", {
        enabled: true,
        automaticFollowup: true,
        prIntegration: true,
      }),
      localEnterprise: config.get("git.localEnterprise", {
        enabled: true,
        nasPath: "N:\\git\\repositories",
        autoSync: true,
      }),
    },
    nas: {
      enabled: config.get<boolean>("nas.enabled", true),
      ip: config.get<string>("nas.ip", "<NAS_PRIMARY_IP>"),
      path: config.get<string>("nas.path", "N:\\"),
    },
    storage: {
      providers: config.get<string[]>("storage.providers", [
        "dropbox",
        "onedrive",
        "protondrive",
        "nas",
      ]),
      aggregatedPath: config.get<string>(
        "storage.aggregatedPath",
        "N:\\cloud_storage_aggregated"
      ),
    },
    ai: {
      autoStart: config.get<boolean>("ai.autoStart", true),
      resourceAwareness: config.get<boolean>("ai.resourceAwareness", true),
      cpuThreshold: config.get<number>("ai.cpuThreshold", 70),
    },
  };
}

async function getLuminaStatus(config: LuminaConfig): Promise<any> {
  return {
    enabled: config.enabled,
    git: {
      github: config.git.github.enabled,
      gitlens: config.git.gitlens.enabled,
      localEnterprise: config.git.localEnterprise.enabled,
    },
    nas: {
      enabled: config.nas.enabled,
      connected: await checkNASConnection(config.nas.ip),
    },
    storage: {
      providers: config.storage.providers,
      aggregatedPath: config.storage.aggregatedPath,
    },
    ai: {
      autoStart: config.ai.autoStart,
      resourceAwareness: config.ai.resourceAwareness,
    },
  };
}

async function checkService(endpoint: string): Promise<boolean> {
  try {
    const response = await axios.get(endpoint, { timeout: 2000 });
    return response.status === 200;
  } catch {
    return false;
  }
}

async function checkNASConnection(ip: string): Promise<boolean> {
  try {
    const response = await axios.get(`http://${ip}:5001/webapi`, {
      timeout: 2000,
    });
    return response.status === 200;
  } catch {
    return false;
  }
}

function generateStatusHTML(status: any): string {
  return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .status-item { margin: 10px 0; }
        .enabled { color: green; }
        .disabled { color: red; }
    </style>
</head>
<body>
    <h1>Lumina Complete Status</h1>
    <div class="status-item">
        <strong>Ecosystem:</strong> <span class="${
          status.enabled ? "enabled" : "disabled"
        }">${status.enabled ? "Enabled" : "Disabled"}</span>
    </div>
    <div class="status-item">
        <strong>GitHub:</strong> <span class="${
          status.git.github ? "enabled" : "disabled"
        }">${status.git.github ? "Enabled" : "Disabled"}</span>
    </div>
    <div class="status-item">
        <strong>GitLens:</strong> <span class="${
          status.git.gitlens ? "enabled" : "disabled"
        }">${status.git.gitlens ? "Enabled" : "Disabled"}</span>
    </div>
    <div class="status-item">
        <strong>Local Enterprise Git:</strong> <span class="${
          status.git.localEnterprise ? "enabled" : "disabled"
        }">${status.git.localEnterprise ? "Enabled" : "Disabled"}</span>
    </div>
    <div class="status-item">
        <strong>NAS:</strong> <span class="${
          status.nas.connected ? "enabled" : "disabled"
        }">${status.nas.connected ? "Connected" : "Disconnected"}</span>
    </div>
    <div class="status-item">
        <strong>Storage Providers:</strong> ${status.storage.providers.join(
          ", "
        )}
    </div>
    <div class="status-item">
        <strong>AI Auto-Start:</strong> <span class="${
          status.ai.autoStart ? "enabled" : "disabled"
        }">${status.ai.autoStart ? "Enabled" : "Disabled"}</span>
    </div>
</body>
</html>`;
}

function initializeTodoStatusBar(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("lumina");
  const showStatusBar = config.get<boolean>("todo.statusBar", true);

  if (!showStatusBar) {
    return;
  }

  // Create status bar item
  todoStatusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100
  );
  todoStatusBarItem.command = "lumina.showTodoStatus";
  todoStatusBarItem.tooltip = "Click to view detailed todo status";
  context.subscriptions.push(todoStatusBarItem);

  // Initial update
  refreshTodoStatusDisplay();

  // Setup file watcher for auto-refresh
  const autoRefresh = config.get<boolean>("todo.autoRefresh", true);
  if (autoRefresh) {
    setupTodoStatusWatcher(context);
  }

  // Setup interval refresh
  const refreshInterval = config.get<number>("todo.refreshInterval", 30000);
  if (refreshInterval > 0) {
    todoStatusRefreshInterval = setInterval(() => {
      refreshTodoStatusDisplay();
    }, refreshInterval);
    context.subscriptions.push({
      dispose: () => {
        if (todoStatusRefreshInterval) {
          clearInterval(todoStatusRefreshInterval);
        }
      },
    });
  }

  // Show status bar
  todoStatusBarItem.show();
}

function setupTodoStatusWatcher(context: vscode.ExtensionContext) {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders || workspaceFolders.length === 0) {
    return;
  }

  const workspaceRoot = workspaceFolders[0].uri.fsPath;
  const masterTodosPath = path.join(
    workspaceRoot,
    "data",
    "todo",
    "master_todos.json"
  );
  const padawanTodosPath = path.join(
    workspaceRoot,
    "data",
    "ask_database",
    "master_padawan_todos.json"
  );
  const statusPath = path.join(
    workspaceRoot,
    "data",
    "cursor_ide_status",
    "todo_status.json"
  );

  // Watch master todos
  const masterWatcher = vscode.workspace.createFileSystemWatcher(
    new vscode.RelativePattern(workspaceRoot, "data/todo/master_todos.json")
  );
  masterWatcher.onDidChange(() => refreshTodoStatusDisplay());
  masterWatcher.onDidCreate(() => refreshTodoStatusDisplay());
  masterWatcher.onDidDelete(() => refreshTodoStatusDisplay());

  // Watch padawan todos
  const padawanWatcher = vscode.workspace.createFileSystemWatcher(
    new vscode.RelativePattern(
      workspaceRoot,
      "data/ask_database/master_padawan_todos.json"
    )
  );
  padawanWatcher.onDidChange(() => refreshTodoStatusDisplay());
  padawanWatcher.onDidCreate(() => refreshTodoStatusDisplay());
  padawanWatcher.onDidDelete(() => refreshTodoStatusDisplay());

  // Watch status file
  const statusWatcher = vscode.workspace.createFileSystemWatcher(
    new vscode.RelativePattern(
      workspaceRoot,
      "data/cursor_ide_status/todo_status.json"
    )
  );
  statusWatcher.onDidChange(() => updateStatusBarFromFile(workspaceRoot));

  context.subscriptions.push(masterWatcher, padawanWatcher, statusWatcher);
}

async function refreshTodoStatusDisplay() {
  try {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
      return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const statusScript = path.join(
      workspaceRoot,
      "scripts",
      "python",
      "cursor_ide_todo_status_display.py"
    );

    // Run status update script
    try {
      await execAsync(`python "${statusScript}"`, { cwd: workspaceRoot });
    } catch (error) {
      console.error("Error running todo status script:", error);
    }

    // Update status bar from file
    await updateStatusBarFromFile(workspaceRoot);
  } catch (error) {
    console.error("Error refreshing todo status:", error);
    if (todoStatusBarItem) {
      todoStatusBarItem.text = "$(error) Todo Status Error";
      todoStatusBarItem.backgroundColor = new vscode.ThemeColor(
        "statusBarItem.errorBackground"
      );
    }
  }
}

async function updateStatusBarFromFile(workspaceRoot: string) {
  try {
    const statusPath = path.join(
      workspaceRoot,
      "data",
      "cursor_ide_status",
      "todo_status.json"
    );

    if (!fs.existsSync(statusPath)) {
      if (todoStatusBarItem) {
        todoStatusBarItem.text = "$(sync~spin) Todo Status...";
      }
      return;
    }

    const statusData = JSON.parse(fs.readFileSync(statusPath, "utf-8"));
    const masterPeak = statusData.master?.peak_percentage || 0;
    const padawanPeak = statusData.padawan?.peak_percentage || 0;
    const overallPeak = statusData.overall_percentage || 0;

    if (todoStatusBarItem) {
      todoStatusBarItem.text = `$(checklist) @MASTER: ${masterPeak.toFixed(
        1
      )}% | @PADAWAN: ${padawanPeak.toFixed(1)}% | @PEAK: ${overallPeak.toFixed(
        1
      )}%`;

      // Color based on percentage
      if (overallPeak >= 75) {
        todoStatusBarItem.backgroundColor = undefined; // Green (default)
      } else if (overallPeak >= 50) {
        todoStatusBarItem.backgroundColor = new vscode.ThemeColor(
          "statusBarItem.warningBackground"
        );
      } else {
        todoStatusBarItem.backgroundColor = new vscode.ThemeColor(
          "statusBarItem.errorBackground"
        );
      }
    }
  } catch (error) {
    console.error("Error updating status bar:", error);
    if (todoStatusBarItem) {
      todoStatusBarItem.text = "$(error) Todo Status Error";
    }
  }
}

async function showTodoStatusPanel() {
  try {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
      vscode.window.showErrorMessage("No workspace folder found");
      return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const statusPath = path.join(
      workspaceRoot,
      "data",
      "cursor_ide_status",
      "todo_status.json"
    );

    // Refresh status first
    await refreshTodoStatusDisplay();

    // Wait a moment for file to be written
    await new Promise((resolve) => setTimeout(resolve, 500));

    let statusData: any;
    if (fs.existsSync(statusPath)) {
      statusData = JSON.parse(fs.readFileSync(statusPath, "utf-8"));
    } else {
      vscode.window.showWarningMessage(
        "Todo status file not found. Generating..."
      );
      await refreshTodoStatusDisplay();
      await new Promise((resolve) => setTimeout(resolve, 1000));
      if (fs.existsSync(statusPath)) {
        statusData = JSON.parse(fs.readFileSync(statusPath, "utf-8"));
      } else {
        vscode.window.showErrorMessage("Failed to generate todo status");
        return;
      }
    }

    const panel = vscode.window.createWebviewPanel(
      "luminaTodoStatus",
      "Todo Status (@MASTER/@PADAWAN)",
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
      }
    );

    panel.webview.html = generateTodoStatusHTML(statusData);
  } catch (error) {
    vscode.window.showErrorMessage(`Error showing todo status: ${error}`);
  }
}

function generateTodoStatusHTML(status: any): string {
  const master = status.master || {};
  const padawan = status.padawan || {};
  const masterMetrics = master.metrics || {};
  const padawanMetrics = padawan.metrics || {};

  const masterPeak = master.peak_percentage || 0;
  const padawanPeak = padawan.peak_percentage || 0;
  const overallPeak = status.overall_percentage || 0;

  const getColorClass = (percentage: number) => {
    if (percentage >= 75) return "status-high";
    if (percentage >= 50) return "status-medium";
    return "status-low";
  };

  return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .header {
            border-bottom: 2px solid var(--vscode-panel-border);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            color: var(--vscode-textLink-foreground);
        }
        .status-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 5px;
            background: var(--vscode-editor-background);
        }
        .status-section h2 {
            margin-top: 0;
            color: var(--vscode-textLink-foreground);
        }
        .peak-display {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .status-high { background: rgba(0, 200, 0, 0.2); color: #4caf50; }
        .status-medium { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
        .status-low { background: rgba(244, 67, 54, 0.2); color: #f44336; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .metric-item {
            padding: 10px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 3px;
        }
        .metric-label {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 18px;
            font-weight: bold;
        }
        .overall-status {
            margin-top: 30px;
            padding: 20px;
            border: 2px solid var(--vscode-textLink-foreground);
            border-radius: 5px;
            text-align: center;
        }
        .refresh-button {
            margin-top: 20px;
            padding: 10px 20px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .refresh-button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .timestamp {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Todo Status - @PEAK Quantification</h1>
    </div>

    <div class="status-section">
        <h2>@AGENT@MASTER.TODOLIST</h2>
        <div class="peak-display ${getColorClass(masterPeak)}">
            @PEAK: ${masterPeak.toFixed(2)}%
        </div>
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Total Todos</div>
                <div class="metric-value">${master.total_todos || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Active</div>
                <div class="metric-value">${master.active_todos || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Complete</div>
                <div class="metric-value">${master.completed_todos || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Pending</div>
                <div class="metric-value">${masterMetrics.pending || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">In Progress</div>
                <div class="metric-value">${
                  masterMetrics.in_progress || 0
                }</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">High Priority</div>
                <div class="metric-value">${
                  masterMetrics.high_priority || 0
                }</div>
            </div>
        </div>
    </div>

    <div class="status-section">
        <h2>@SUBAGENT@PADAWAN.LIST</h2>
        <div class="peak-display ${getColorClass(padawanPeak)}">
            @PEAK: ${padawanPeak.toFixed(2)}%
        </div>
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Total Todos</div>
                <div class="metric-value">${padawan.total_todos || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Active</div>
                <div class="metric-value">${padawan.active_todos || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Complete</div>
                <div class="metric-value">${padawan.completed_todos || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Pending</div>
                <div class="metric-value">${padawanMetrics.pending || 0}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">In Progress</div>
                <div class="metric-value">${
                  padawanMetrics.in_progress || 0
                }</div>
            </div>
        </div>
        ${
          Object.keys(padawan.padawan_assignments || {}).length > 0
            ? `
        <div style="margin-top: 15px;">
            <strong>Padawan Assignments:</strong>
            <ul>
                ${Object.entries(padawan.padawan_assignments || {})
                  .map(([name, count]) => `<li>${name}: ${count} todos</li>`)
                  .join("")}
            </ul>
        </div>
        `
            : ""
        }
    </div>

    <div class="overall-status">
        <h2>OVERALL STATUS</h2>
        <div class="peak-display ${getColorClass(
          overallPeak
        )}" style="font-size: 32px;">
            @PEAK: ${overallPeak.toFixed(2)}%
        </div>
        <div class="timestamp">
            Last Updated: ${new Date(
              status.timestamp || Date.now()
            ).toLocaleString()}
        </div>
    </div>

    <button class="refresh-button" onclick="refreshStatus()">🔄 Refresh Status</button>

    <script>
        const vscode = acquireVsCodeApi();
        function refreshStatus() {
            vscode.postMessage({ command: 'refresh' });
        }
    </script>
</body>
</html>`;
}

async function showTPSReportPanel() {
  try {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
      vscode.window.showErrorMessage("No workspace folder found");
      return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const tpsScript = path.join(
      workspaceRoot,
      "scripts",
      "python",
      "generate_tps_reports.py"
    );

    // Run TPS report generation
    try {
      const { stdout } = await execAsync(`python "${tpsScript}"`, {
        cwd: workspaceRoot,
      });

      // Find latest TPS report
      const reportsDir = path.join(workspaceRoot, "data", "tps_reports");
      const reports = fs
        .readdirSync(reportsDir)
        .filter((f) => f.startsWith("TPS-") && f.endsWith(".json"))
        .sort()
        .reverse();

      if (reports.length > 0) {
        const latestReport = JSON.parse(
          fs.readFileSync(path.join(reportsDir, reports[0]), "utf-8")
        );

        const panel = vscode.window.createWebviewPanel(
          "luminaTPSReport",
          "TPS Reports - Daily Morning Briefing",
          vscode.ViewColumn.One,
          {
            enableScripts: true,
            retainContextWhenHidden: true,
          }
        );

        panel.webview.html = generateTPSReportHTML(latestReport);
      } else {
        vscode.window.showInformationMessage(
          "No TPS reports found. Generating..."
        );
        await execAsync(`python "${tpsScript}"`, { cwd: workspaceRoot });
      }
    } catch (error) {
      vscode.window.showErrorMessage(`Error generating TPS report: ${error}`);
    }
  } catch (error) {
    vscode.window.showErrorMessage(`Error showing TPS report: ${error}`);
  }
}

async function generateTPSReport() {
  try {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
      vscode.window.showErrorMessage("No workspace folder found");
      return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const tpsScript = path.join(
      workspaceRoot,
      "scripts",
      "python",
      "generate_tps_reports.py"
    );

    vscode.window.showInformationMessage("Generating TPS Report...");

    try {
      const { stdout } = await execAsync(`python "${tpsScript}"`, {
        cwd: workspaceRoot,
      });
      vscode.window.showInformationMessage(
        "✅ TPS Report generated successfully!"
      );

      // Open the report
      await showTPSReportPanel();
    } catch (error) {
      vscode.window.showErrorMessage(`Error generating TPS report: ${error}`);
    }
  } catch (error) {
    vscode.window.showErrorMessage(`Error: ${error}`);
  }
}

function generateTPSReportHTML(report: any): string {
  return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .header {
            border-bottom: 2px solid var(--vscode-panel-border);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 5px;
        }
        .url-item {
            padding: 5px;
            margin: 5px 0;
            background: var(--vscode-textBlockQuote-background);
            border-left: 3px solid var(--vscode-textLink-foreground);
            font-family: monospace;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 TPS REPORTS - DAILY MORNING BRIEFING</h1>
        <p>Report Date: ${report.report_date || "N/A"}</p>
        <p>Previous Day: ${report.previous_day || "N/A"}</p>
    </div>

    <div class="section">
        <h2>SUMMARY</h2>
        <p>Total Events: ${report.summary?.total_events || 0}</p>
        <p>Major Events: ${report.summary?.major_events_count || 0}</p>
        <p>Minor Events: ${report.summary?.minor_events_count || 0}</p>
    </div>

    <div class="section">
        <h2>@PEAK SUMMARY</h2>
        <p>Average @PEAK: ${
          report.peak_summary?.average_peak?.toFixed(2) || 0
        }%</p>
        <p>Max @PEAK: ${report.peak_summary?.max_peak?.toFixed(2) || 0}%</p>
    </div>

    <div class="section">
        <h2>HOLOCRON INTERNAL URLs (COPY-PASTE READY)</h2>
        ${(report.internal_urls || [])
          .map(
            (url: string, i: number) =>
              `<div class="url-item">${i + 1}. ${url}</div>`
          )
          .join("")}
    </div>
</body>
</html>`;
}

async function showLiveAIModelStatusPanel() {
  try {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
      vscode.window.showErrorMessage("No workspace folder found");
      return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const monitorScript = path.join(
      workspaceRoot,
      "scripts",
      "python",
      "live_ai_model_monitor.py"
    );
    const liveFeedPath = path.join(
      workspaceRoot,
      "data",
      "ai_model_monitoring",
      "live_feed.json"
    );

    // Run monitoring script
    try {
      await execAsync(`python "${monitorScript}"`, { cwd: workspaceRoot });

      // Wait for file to be written
      await new Promise((resolve) => setTimeout(resolve, 500));

      if (fs.existsSync(liveFeedPath)) {
        const statusData = JSON.parse(fs.readFileSync(liveFeedPath, "utf-8"));

        const panel = vscode.window.createWebviewPanel(
          "luminaLiveAIModel",
          "LIVE AI Model Monitoring - Forensic Audit",
          vscode.ViewColumn.One,
          {
            enableScripts: true,
            retainContextWhenHidden: true,
          }
        );

        panel.webview.html = generateLiveAIModelHTML(statusData);
      } else {
        vscode.window.showWarningMessage("Live feed not found. Generating...");
        await execAsync(`python "${monitorScript}"`, { cwd: workspaceRoot });
        await new Promise((resolve) => setTimeout(resolve, 1000));
        if (fs.existsSync(liveFeedPath)) {
          const statusData = JSON.parse(fs.readFileSync(liveFeedPath, "utf-8"));
          const panel = vscode.window.createWebviewPanel(
            "luminaLiveAIModel",
            "LIVE AI Model Monitoring - Forensic Audit",
            vscode.ViewColumn.One,
            { enableScripts: true, retainContextWhenHidden: true }
          );
          panel.webview.html = generateLiveAIModelHTML(statusData);
        }
      }
    } catch (error) {
      vscode.window.showErrorMessage(`Error monitoring AI model: ${error}`);
    }
  } catch (error) {
    vscode.window.showErrorMessage(`Error: ${error}`);
  }
}

async function monitorLiveAIModel() {
  try {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
      vscode.window.showErrorMessage("No workspace folder found");
      return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const monitorScript = path.join(
      workspaceRoot,
      "scripts",
      "python",
      "live_ai_model_monitor.py"
    );

    vscode.window.showInformationMessage("Monitoring LIVE AI Model...");

    try {
      const { stdout } = await execAsync(`python "${monitorScript}"`, {
        cwd: workspaceRoot,
      });
      vscode.window.showInformationMessage("✅ Live AI Model status updated!");

      // Open the status panel
      await showLiveAIModelStatusPanel();
    } catch (error) {
      vscode.window.showErrorMessage(`Error monitoring AI model: ${error}`);
    }
  } catch (error) {
    vscode.window.showErrorMessage(`Error: ${error}`);
  }
}

function generateLiveAIModelHTML(status: any): string {
  const spectrum = status.spectrum || {};
  const hog = status.hog || {};
  const performance = status.performance || {};

  return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .header {
            border-bottom: 2px solid var(--vscode-panel-border);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 5px;
        }
        .status-legendary { color: #00ff00; }
        .status-excellent { color: #90ee90; }
        .status-good { color: #ffff00; }
        .status-fair { color: #ffa500; }
        .status-poor { color: #ff6347; }
        .status-degraded { color: #ff0000; }
        .warning { color: #ff6347; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 LIVE AI MODEL MONITORING - FORENSIC AUDIT</h1>
        <p>Status ID: ${status.status_id || "N/A"}</p>
        <p>Timestamp: ${status.timestamp || "N/A"}</p>
    </div>

    <div class="section">
        <h2>CUSTOM HEADER TRACKING</h2>
        <p>Header: ${status.header?.header_string || "N/A"}</p>
        <p>Model ID: ${status.header?.model_identifier || "N/A"}</p>
        <p>Positive: ${status.header?.positive_metric || "N/A"}</p>
        <p>Negative: ${status.header?.negative_metric || "N/A"}</p>
    </div>

    <div class="section">
        <h2>SPECTRUM ANALYSIS (Legendary → Degraded)</h2>
        <p class="status-${
          spectrum.current_status?.toLowerCase() || "unknown"
        }">
            Current Status: ${
              spectrum.current_status?.toUpperCase() || "UNKNOWN"
            }
        </p>
        <p>Status Score: ${spectrum.status_score?.toFixed(2) || 0}/100</p>
        <p>Confidence: ${spectrum.confidence_level?.toFixed(2) || 0}%</p>
        <p>Trend: ${spectrum.trend?.toUpperCase() || "UNKNOWN"}</p>
        ${(spectrum.anomalies_detected || [])
          .map((a: string) => `<p class="warning">⚠️  ${a}</p>`)
          .join("")}
    </div>

    <div class="section">
        <h2>@HoG (HEART OF GOLD) PROBABILITY ENGINE</h2>
        <p>Reality Evolution Score: ${
          hog.reality_evolution_score?.toFixed(2) || 0
        }</p>
        <p>Matrix-Lattice Stability: ${
          hog.matrix_lattice_stability?.toFixed(2) || 0
        }%</p>
        <p>Sheeba Power Level: ${
          hog.sheeba_power_level?.toFixed(2) || 0
        }% (DESTROYER_OF_WORLDS)</p>
        <p>Shoggoth Fear Level: ${
          hog.shoggoth_fear_level?.toFixed(2) || 0
        }% (Even @SHOGGOTH::TREMBLES::)</p>
        <p>Cthulhu Status: ${
          hog.cthulhu_sleep_status?.toUpperCase() || "UNKNOWN"
        }</p>
        ${
          hog.cthulhu_sleep_status !== "sleeping"
            ? '<p class="warning">⚠️  DON\'T PANIC - Throw a towel over the octopus!</p>'
            : ""
        }
    </div>

    <div class="section">
        <h2>PERFORMANCE METRICS</h2>
        <p>Response Time: ${performance.response_time_ms?.toFixed(2) || 0}ms</p>
        <p>Accuracy: ${performance.accuracy_score?.toFixed(2) || 0}%</p>
        <p>Coherence: ${performance.coherence_score?.toFixed(2) || 0}%</p>
        <p>@PEAK: ${performance.peak_percentage?.toFixed(2) || 0}%</p>
    </div>

    <div class="section">
        <h2>LIVE FEED URL</h2>
        <p style="font-family: monospace; word-break: break-all;">${
          status.live_feed_url || "N/A"
        }</p>
    </div>
</body>
</html>`;
}

/**
 * Extract request ID from text using various patterns
 */
function extractRequestId(text: string): string | undefined {
  if (!text) return undefined;

  // Pattern 1: Standard UUID format
  const uuidPattern =
    /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;

  // Pattern 2: request_id="..." or requestId="..." or request_id: "..."
  const requestIdPattern1 = /request[_-]?id["\s:=]+([0-9a-f-]{36,})/i;

  // Pattern 3: "request_id": "..." (JSON format)
  const requestIdPattern2 = /"request[_-]?id"\s*:\s*"([0-9a-f-]{36,})"/i;

  // Pattern 4: Request ID: ... (log format)
  const requestIdPattern3 = /Request\s+ID[:\s]+([0-9a-f-]{36,})/i;

  // Pattern 5: cursor://request/... (already a URL)
  const cursorUrlPattern = /cursor:\/\/request\/([0-9a-f-]{36,})/i;

  // Try patterns in order of specificity
  let match = text.match(cursorUrlPattern);
  if (match) return match[1];

  match = text.match(requestIdPattern2);
  if (match) return match[1];

  match = text.match(requestIdPattern1);
  if (match) return match[1];

  match = text.match(requestIdPattern3);
  if (match) return match[1];

  match = text.match(uuidPattern);
  if (match) return match[0];

  return undefined;
}

async function copyAgentRequestIdUrl() {
  try {
    // Try to extract request ID from active editor selection or document
    let requestId: string | undefined;

    const activeEditor = vscode.window.activeTextEditor;
    if (activeEditor) {
      const selection = activeEditor.selection;
      const selectedText = activeEditor.document.getText(selection);

      // Try to find request ID in selected text
      if (selectedText && !selection.isEmpty) {
        requestId = extractRequestId(selectedText);
      }

      // If no selection or no ID found, try current line
      if (!requestId) {
        const line = activeEditor.document.lineAt(selection.active.line);
        const lineText = line.text;
        requestId = extractRequestId(lineText);
      }

      // If still not found, try nearby lines (within 5 lines)
      if (!requestId) {
        const currentLine = selection.active.line;
        const startLine = Math.max(0, currentLine - 5);
        const endLine = Math.min(
          activeEditor.document.lineCount - 1,
          currentLine + 5
        );

        for (let i = startLine; i <= endLine; i++) {
          const line = activeEditor.document.lineAt(i);
          const found = extractRequestId(line.text);
          if (found) {
            requestId = found;
            break;
          }
        }
      }
    }

    // If still no request ID found, prompt user
    if (!requestId) {
      const input = await vscode.window.showInputBox({
        prompt: "Enter Request ID to generate internal URL",
        placeHolder: "e.g., 45199e50-8c15-46e6-b1ea-9e6ad674ba89",
        validateInput: (value) => {
          if (!value || value.trim().length === 0) {
            return "Request ID cannot be empty";
          }
          const trimmed = value.trim();
          // Allow UUID format or any alphanumeric string (some IDs might not be UUIDs)
          const uuidPattern =
            /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
          const alphanumericPattern = /^[0-9a-z_-]+$/i;
          if (
            !uuidPattern.test(trimmed) &&
            !alphanumericPattern.test(trimmed)
          ) {
            return "Request ID should be a valid UUID or alphanumeric string";
          }
          return null;
        },
      });

      if (!input) {
        return; // User cancelled
      }

      requestId = input.trim();
    }

    // Generate internal URL
    // Format: cursor://request/{requestId}
    const internalUrl = `cursor://request/${requestId}`;

    // Copy to clipboard
    await vscode.env.clipboard.writeText(internalUrl);

    // Show confirmation with option to open
    const action = await vscode.window.showInformationMessage(
      `✅ Copied Request ID URL to clipboard: ${internalUrl}`,
      "Open URL"
    );

    if (action === "Open URL") {
      try {
        await vscode.env.openExternal(vscode.Uri.parse(internalUrl));
      } catch (error) {
        // If URL scheme not supported, just show the URL
        vscode.window.showInformationMessage(`URL: ${internalUrl}`);
      }
    }
  } catch (error) {
    vscode.window.showErrorMessage(`Error copying request ID URL: ${error}`);
    console.error("Error in copyAgentRequestIdUrl:", error);
  }
}

// ============================================================================
// FILE AUTO-CLOSE FUNCTIONALITY (Consolidated from lumina-file-auto-close)
// ============================================================================

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
    this.dataDir = path.join(
      context.globalStorageUri.fsPath,
      "luminaCore",
      "fileAutoClose"
    );
    this.ensureDataDir();
    this.loadData();
    this.startMonitoring();
  }

  private ensureDataDir(): void {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  private loadData(): void {
    try {
      const activeFile = path.join(this.dataDir, "active_files.json");
      if (fs.existsSync(activeFile)) {
        const data = JSON.parse(fs.readFileSync(activeFile, "utf8"));
        for (const [filePath, session] of Object.entries(data)) {
          const sess = session as any;
          this.activeFiles.set(filePath, {
            ...sess,
            openedAt: new Date(sess.openedAt),
            lastAccessed: new Date(sess.lastAccessed),
          });
        }
      }
      const pinnedFile = path.join(this.dataDir, "pinned_files.json");
      if (fs.existsSync(pinnedFile)) {
        const data = JSON.parse(fs.readFileSync(pinnedFile, "utf8"));
        this.pinnedFiles = new Set(data.pinnedFiles || []);
      }
    } catch (error) {
      console.error("Failed to load file auto-close data:", error);
    }
  }

  private saveData(): void {
    try {
      const activeData: any = {};
      for (const [filePath, session] of this.activeFiles.entries()) {
        activeData[filePath] = {
          ...session,
          openedAt: session.openedAt.toISOString(),
          lastAccessed: session.lastAccessed.toISOString(),
        };
      }
      fs.writeFileSync(
        path.join(this.dataDir, "active_files.json"),
        JSON.stringify(activeData, null, 2)
      );
      fs.writeFileSync(
        path.join(this.dataDir, "pinned_files.json"),
        JSON.stringify({ pinnedFiles: Array.from(this.pinnedFiles) }, null, 2)
      );
    } catch (error) {
      console.error("Failed to save file auto-close data:", error);
    }
  }

  public registerFileOpen(document: vscode.TextDocument): void {
    const filePath = path.resolve(document.uri.fsPath);
    const workspace =
      vscode.workspace.getWorkspaceFolder(document.uri)?.uri.fsPath || "";

    if (this.activeFiles.has(filePath)) {
      const session = this.activeFiles.get(filePath)!;
      session.lastAccessed = new Date();
    } else {
      const session: FileSession = {
        filePath,
        openedAt: new Date(),
        lastAccessed: new Date(),
        isPinned: this.pinnedFiles.has(filePath),
        workspace,
        fileType: this.getFileType(filePath),
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
      ".py": "python",
      ".js": "javascript",
      ".ts": "typescript",
      ".java": "java",
      ".cpp": "cpp",
      ".c": "c",
      ".cs": "csharp",
      ".php": "php",
      ".rb": "ruby",
      ".go": "go",
      ".rs": "rust",
      ".md": "markdown",
      ".json": "json",
      ".yaml": "yaml",
      ".yml": "yaml",
      ".xml": "xml",
      ".html": "html",
      ".css": "css",
      ".sql": "sql",
    };
    return typeMap[ext] || "unknown";
  }

  private startMonitoring(): void {
    const config = vscode.workspace.getConfiguration("lumina.fileAutoClose");
    const enabled = config.get("enabled", true);
    const checkInterval = config.get("checkIntervalSeconds", 60);

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
    const config = vscode.workspace.getConfiguration("lumina.fileAutoClose");
    const autoCloseMinutes = config.get("autoCloseMinutes", 30);
    const showNotifications = config.get("showNotifications", true);

    const candidates: string[] = [];
    for (const [filePath, session] of this.activeFiles.entries()) {
      if (!session.isPinned) {
        const ageMinutes =
          (Date.now() - session.openedAt.getTime()) / (1000 * 60);
        if (ageMinutes >= autoCloseMinutes) {
          candidates.push(filePath);
        }
      }
    }

    let closedCount = 0;
    for (const filePath of candidates.slice(0, 5)) {
      try {
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

  public async evaluateFileForClose(filePath: string): Promise<boolean> {
    const session = this.activeFiles.get(filePath);
    if (!session) return false;

    const config = vscode.workspace.getConfiguration("lumina.fileAutoClose");
    const v3Threshold = config.get("v3ConfidenceThreshold", 0.7);
    const jarvisEnabled = config.get("jarvisOverrideEnabled", true);

    const v3Decision = this.v3Evaluate(session);
    if (jarvisEnabled) {
      const jarvisDecision = await this.jarvisEvaluate(session, v3Decision);
      return jarvisDecision.shouldClose;
    }
    return v3Decision.score >= v3Threshold;
  }

  private v3Evaluate(session: FileSession): { score: number; reason: string } {
    let score = 0;
    const ageMinutes = (Date.now() - session.openedAt.getTime()) / (1000 * 60);
    if (ageMinutes > 60) score += 0.4;
    else if (ageMinutes > 30) score += 0.2;

    const importantTypes = [
      "python",
      "javascript",
      "typescript",
      "java",
      "cpp",
    ];
    if (importantTypes.includes(session.fileType)) {
      score -= 0.2;
    }

    if (
      session.filePath.includes("/src/") ||
      session.filePath.includes("\\src\\")
    ) {
      score -= 0.1;
    }

    return { score, reason: "V3 evaluation" };
  }

  private async jarvisEvaluate(
    session: FileSession,
    v3Decision: { score: number; reason: string }
  ): Promise<{ shouldClose: boolean; reason: string }> {
    const criticalIndicators: string[] = [];
    const activeEditor = vscode.window.activeTextEditor;
    if (
      activeEditor &&
      path.resolve(activeEditor.document.uri.fsPath) === session.filePath
    ) {
      criticalIndicators.push("currently_edited");
    }

    const tabs = vscode.window.tabGroups.all.flatMap((tg) => tg.tabs);
    const fileTab = tabs.find(
      (tab) =>
        tab.input instanceof vscode.TabInputText &&
        path.resolve(tab.input.uri.fsPath) === session.filePath
    );
    if (fileTab && (fileTab as any).isDirty) {
      criticalIndicators.push("unsaved_changes");
    }

    if (criticalIndicators.length > 0) {
      return {
        shouldClose: false,
        reason: `JARVIS override: ${criticalIndicators.join(", ")}`,
      };
    }

    const ageHours =
      (Date.now() - session.openedAt.getTime()) / (1000 * 60 * 60);
    if (ageHours > 2) {
      return { shouldClose: true, reason: "JARVIS override: very_old" };
    }

    return {
      shouldClose: v3Decision.score >= 0.7,
      reason: "JARVIS override: v3 evaluation",
    };
  }

  public async closeFileInVSCode(filePath: string): Promise<boolean> {
    try {
      const tabs = vscode.window.tabGroups.all.flatMap((tg) => tg.tabs);
      const fileTab = tabs.find(
        (tab) =>
          tab.input instanceof vscode.TabInputText &&
          path.resolve(tab.input.uri.fsPath) === filePath
      );
      if (fileTab) {
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
    const pinnedCount = activeFiles.filter((s) => s.isPinned).length;
    return {
      activeFiles: activeFiles.length,
      pinnedFiles: pinnedCount,
      autoCloseThreshold: vscode.workspace
        .getConfiguration("lumina.fileAutoClose")
        .get("autoCloseMinutes", 30),
    };
  }

  public dispose(): void {
    this.stopMonitoring();
    this.saveData();
  }
}

let fileAutoCloseManager: FileAutoCloseManager | null = null;

// ============================================================================
// EDITOR VALIDATION SCHEDULER (Ruff + Mypy when focus leaves editor)
// ============================================================================
// Runs "Editor validation (Ruff + Mypy)" only when:
// - Focus is not on the editor pane (activeTextEditor undefined or window unfocused)
// - At least bufferMinutes since last file save
// - Then every intervalMinutes while conditions hold

const EDITOR_VALIDATION_TASK_LABEL = "Editor validation (Ruff + Mypy)";

class EditorValidationScheduler {
  private lastFileChangeAt: number = 0;
  private lastRunAt: number = 0;
  private checkTimer: NodeJS.Timeout | undefined;
  private readonly context: vscode.ExtensionContext;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
  }

  start(): void {
    const config = vscode.workspace.getConfiguration("lumina.editorValidation");
    if (!config.get<boolean>("enabled", true)) return;

    const checkIntervalSeconds = config.get<number>("checkIntervalSeconds", 60);
    this.lastFileChangeAt = Date.now();
    this.lastRunAt = 0;

    vscode.workspace.onDidSaveTextDocument(
      () => {
        this.lastFileChangeAt = Date.now();
      },
      null,
      this.context.subscriptions
    );

    this.checkTimer = setInterval(() => {
      this.maybeRunValidation();
    }, checkIntervalSeconds * 1000);
  }

  private editorHasFocus(): boolean {
    const state = vscode.window.state as { focused?: boolean };
    if (state && state.focused === false) return false;
    return vscode.window.activeTextEditor !== undefined;
  }

  private async maybeRunValidation(): Promise<void> {
    const config = vscode.workspace.getConfiguration("lumina.editorValidation");
    if (!config.get<boolean>("enabled", true)) return;
    if (this.editorHasFocus()) return;

    const bufferMinutes = config.get<number>("bufferMinutes", 30);
    const intervalMinutes = config.get<number>("intervalMinutes", 10);
    const now = Date.now();
    const bufferMs = bufferMinutes * 60 * 1000;
    const intervalMs = intervalMinutes * 60 * 1000;

    if (now - this.lastFileChangeAt < bufferMs) return;
    if (this.lastRunAt > 0 && now - this.lastRunAt < intervalMs) return;

    const task = await this.findValidationTask();
    if (task) {
      this.lastRunAt = now;
      await vscode.tasks.executeTask(task);
    }
  }

  private async findValidationTask(): Promise<vscode.Task | undefined> {
    const tasks = await vscode.tasks.fetchTasks();
    return tasks.find((t) => t.name === EDITOR_VALIDATION_TASK_LABEL);
  }

  dispose(): void {
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = undefined;
    }
  }
}

let editorValidationScheduler: EditorValidationScheduler | undefined;

function initializeEditorValidationScheduler(
  context: vscode.ExtensionContext
): void {
  const config = vscode.workspace.getConfiguration("lumina.editorValidation");
  if (!config.get<boolean>("enabled", true)) return;

  editorValidationScheduler = new EditorValidationScheduler(context);
  editorValidationScheduler.start();
  context.subscriptions.push({
    dispose: () => {
      editorValidationScheduler?.dispose();
      editorValidationScheduler = undefined;
    },
  });
}

// ============================================================================
// UNIFIED QUEUE FUNCTIONALITY (Consolidated from lumina-unified-queue)
// ============================================================================

interface QueueItem {
  item_id: string;
  item_type: string;
  status: string;
  title: string;
  priority: number;
  progress: number;
  error?: string;
}

interface QueueState {
  items: QueueItem[];
  summary: {
    total_items: number;
    by_type: Record<string, number>;
    by_status: Record<string, number>;
    pending_count: number;
    processing_count: number;
    completed_count: number;
    failed_count: number;
  };
  saved_at: string;
}

let unifiedQueueStatusBarItem: vscode.StatusBarItem | null = null;
let unifiedQueueWatcher: vscode.FileSystemWatcher | undefined;
let unifiedQueueInterval: NodeJS.Timeout | undefined;

function initializeUnifiedQueue(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("lumina.unifiedQueue");
  const updateInterval = config.get<number>("updateInterval", 2000);
  const showInStatusBar = config.get<boolean>("showInStatusBar", true);

  if (!showInStatusBar) return;

  unifiedQueueStatusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    900
  );
  unifiedQueueStatusBarItem.command = "lumina.unifiedQueue.showDetails";
  unifiedQueueStatusBarItem.tooltip = "Click to show unified queue details";

  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!workspaceRoot) return;

  const queueStateFile = path.join(
    workspaceRoot,
    "data",
    "unified_queue",
    "queue_state.json"
  );

  function updateStatusBar() {
    try {
      if (!fs.existsSync(queueStateFile)) {
        unifiedQueueStatusBarItem!.text = "$(list-unordered) Queue: 0";
        unifiedQueueStatusBarItem!.tooltip =
          "Unified Queue: No items\nClick to open queue viewer";
        unifiedQueueStatusBarItem!.show();
        return;
      }

      const stateData = fs.readFileSync(queueStateFile, "utf8");
      const state: QueueState = JSON.parse(stateData);
      const summary = state.summary;
      const total = summary.total_items;
      const pending = summary.pending_count;
      const processing = summary.processing_count;
      const completed = summary.completed_count;
      const failed = summary.failed_count;

      let displayText = "$(list-unordered)";
      if (processing > 0) {
        displayText += ` $(sync~spin) ${total}`;
      } else if (pending > 0) {
        displayText += ` $(clock) ${total}`;
      } else {
        displayText += ` ${total}`;
      }

      const indicators: string[] = [];
      if (processing > 0) indicators.push(`⚙️${processing}`);
      if (pending > 0) indicators.push(`⏳${pending}`);
      if (failed > 0) indicators.push(`❌${failed}`);
      if (completed > 0 && total <= 10) indicators.push(`✅${completed}`);

      if (indicators.length > 0) {
        displayText += " " + indicators.join(" ");
      }

      unifiedQueueStatusBarItem!.text = displayText;
      unifiedQueueStatusBarItem!.tooltip = `Unified Queue\nTotal: ${total}\nPending: ${pending}\nProcessing: ${processing}\nCompleted: ${completed}\nFailed: ${failed}\n\nClick to show details`;
      unifiedQueueStatusBarItem!.show();
    } catch (error) {
      console.error("Error updating unified queue status bar:", error);
      unifiedQueueStatusBarItem!.text = "$(error) Queue: Error";
      unifiedQueueStatusBarItem!.show();
    }
  }

  updateStatusBar();

  unifiedQueueWatcher = vscode.workspace.createFileSystemWatcher(
    new vscode.RelativePattern(
      workspaceRoot,
      "data/unified_queue/queue_state.json"
    )
  );
  unifiedQueueWatcher.onDidChange(() => updateStatusBar());
  unifiedQueueWatcher.onDidCreate(() => updateStatusBar());

  unifiedQueueInterval = setInterval(() => updateStatusBar(), updateInterval);

  const showDetailsCommand = vscode.commands.registerCommand(
    "lumina.unifiedQueue.showDetails",
    () => {
      try {
        if (!fs.existsSync(queueStateFile)) {
          vscode.window.showInformationMessage(
            "Queue state file not found. Queue is empty."
          );
          return;
        }

        const stateData = fs.readFileSync(queueStateFile, "utf8");
        const state: QueueState = JSON.parse(stateData);
        const summary = state.summary;

        const details: string[] = [
          "**Unified Queue Summary**",
          "",
          `**Total Items:** ${summary.total_items}`,
          `**Pending:** ${summary.pending_count}`,
          `**Processing:** ${summary.processing_count}`,
          `**Completed:** ${summary.completed_count}`,
          `**Failed:** ${summary.failed_count}`,
          "",
          "Run `python scripts/python/unified_queue_viewer.py` for full view",
        ];

        vscode.window.showInformationMessage(details.join("\n"), {
          modal: true,
        });
      } catch (error) {
        vscode.window.showErrorMessage(`Error reading queue state: ${error}`);
      }
    }
  );

  const openViewerCommand = vscode.commands.registerCommand(
    "lumina.unifiedQueue.openViewer",
    () => {
      const terminal = vscode.window.createTerminal("Unified Queue Viewer");
      terminal.sendText("python scripts/python/unified_queue_viewer.py");
      terminal.show();
    }
  );

  const refreshCommand = vscode.commands.registerCommand(
    "lumina.unifiedQueue.refresh",
    () => {
      updateStatusBar();
      vscode.window.showInformationMessage("Unified queue status refreshed");
    }
  );

  context.subscriptions.push(
    unifiedQueueStatusBarItem,
    unifiedQueueWatcher,
    showDetailsCommand,
    openViewerCommand,
    refreshCommand
  );

  context.subscriptions.push({
    dispose: () => {
      if (unifiedQueueInterval) clearInterval(unifiedQueueInterval);
    },
  });
}

// ============================================================================
// FOOTER TICKER FUNCTIONALITY (Consolidated from lumina-footer-ticker)
// ============================================================================

interface TickerItem {
  id: string;
  text: string;
  priority: number;
  icon?: string;
  metadata?: any;
}

let footerTickerItem: vscode.StatusBarItem | null = null;
let footerTickerInterval: NodeJS.Timeout | undefined;

function initializeFooterTicker(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("lumina.footerTicker");
  const enabled = config.get<boolean>("enabled", true);
  if (!enabled) return;

  const tickerItems = loadTickerItems(context);
  if (tickerItems.length === 0) return;

  footerTickerItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    1000
  );

  let currentIndex = 0;
  let isPaused = false;

  function updateTicker() {
    if (isPaused || tickerItems.length === 0) return;

    const visibleCount = 5;
    const visibleItems: TickerItem[] = [];
    for (let i = 0; i < visibleCount; i++) {
      const item = tickerItems[(currentIndex + i) % tickerItems.length];
      visibleItems.push(item);
    }

    const displayText = visibleItems
      .map((item) => {
        const icon = item.icon ? `${item.icon} ` : "";
        return `${icon}${item.text}`;
      })
      .join("  •  ");

    footerTickerItem!.text = `$(sync~spin) ${displayText}`;
    footerTickerItem!.tooltip = `LUMINA Footer Ticker\n\nAll items:\n${tickerItems
      .map((item) => `${item.icon || ""} ${item.text}`)
      .join("\n")}\n\nClick to pause/resume`;
    footerTickerItem!.command = "lumina.footerTicker.toggle";
    footerTickerItem!.show();

    currentIndex = (currentIndex + 1) % tickerItems.length;
  }

  updateTicker();
  footerTickerInterval = setInterval(updateTicker, 3000);

  const toggleCommand = vscode.commands.registerCommand(
    "lumina.footerTicker.toggle",
    () => {
      isPaused = !isPaused;
      if (!isPaused) {
        updateTicker();
      }
      vscode.window.showInformationMessage(
        `LUMINA Footer Ticker: ${isPaused ? "Paused" : "Resumed"}`
      );
    }
  );

  context.subscriptions.push(footerTickerItem);
  context.subscriptions.push(toggleCommand);
  context.subscriptions.push({
    dispose: () => {
      if (footerTickerInterval) clearInterval(footerTickerInterval);
    },
  });
}

function loadTickerItems(context: vscode.ExtensionContext): TickerItem[] {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  if (workspaceFolder) {
    const configPath = path.join(
      workspaceFolder.uri.fsPath,
      "config",
      "footer_ticker_config.json"
    );

    if (fs.existsSync(configPath)) {
      try {
        const configData = JSON.parse(fs.readFileSync(configPath, "utf-8"));
        return configData.items || [];
      } catch (error) {
        console.error("Failed to load ticker config:", error);
      }
    }
  }

  return [
    { id: "cursor_model", text: "Cursor Model", priority: 0, icon: "🤖" },
    { id: "branch", text: "Git Branch", priority: 1, icon: "🌿" },
    { id: "errors", text: "Errors", priority: 2, icon: "❌" },
    { id: "warnings", text: "Warnings", priority: 3, icon: "⚠️" },
    { id: "language", text: "Language", priority: 4, icon: "📝" },
  ];
}

// ============================================================================
// VOICE REQUEST QUEUE (Jarvis/Lumina AI Chat - multiple items, editable, passive/active)
// ============================================================================

export interface VoiceRequestQueueItem {
  id: string;
  text: string;
  status: "pending" | "sent";
  createdAt: number;
  source: "active" | "passive" | "manual";
}

const VOICE_QUEUE_STORAGE_KEY = "lumina.voiceRequestQueue.items";
let voiceRequestQueueContext: vscode.ExtensionContext | null = null;
let voiceRequestQueueItems: VoiceRequestQueueItem[] = [];

function loadVoiceRequestQueue(): void {
  if (!voiceRequestQueueContext) return;
  const raw = voiceRequestQueueContext.workspaceState.get<
    VoiceRequestQueueItem[]
  >(VOICE_QUEUE_STORAGE_KEY);
  voiceRequestQueueItems = Array.isArray(raw) ? raw : [];
}

function persistVoiceRequestQueue(): void {
  if (!voiceRequestQueueContext) return;
  voiceRequestQueueContext.workspaceState.update(
    VOICE_QUEUE_STORAGE_KEY,
    voiceRequestQueueItems
  );
}

export function getVoiceRequestQueueItems(): VoiceRequestQueueItem[] {
  return [...voiceRequestQueueItems];
}

export function addToVoiceRequestQueue(
  text: string,
  source: "active" | "passive" | "manual"
): VoiceRequestQueueItem | null {
  const trimmed = text.trim();
  if (!trimmed) return null;
  const item: VoiceRequestQueueItem = {
    id: `vq-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    text: trimmed,
    status: "pending",
    createdAt: Date.now(),
    source,
  };
  voiceRequestQueueItems.push(item);
  persistVoiceRequestQueue();
  return item;
}

export function updateVoiceRequestQueueItem(id: string, text: string): boolean {
  const item = voiceRequestQueueItems.find((i) => i.id === id);
  if (!item || item.status !== "pending") return false;
  item.text = text.trim() || item.text;
  persistVoiceRequestQueue();
  return true;
}

export function removeVoiceRequestQueueItem(id: string): boolean {
  const idx = voiceRequestQueueItems.findIndex((i) => i.id === id);
  if (idx === -1) return false;
  voiceRequestQueueItems.splice(idx, 1);
  persistVoiceRequestQueue();
  return true;
}

export async function sendVoiceRequestQueueItemToChat(
  id: string
): Promise<boolean> {
  const item = voiceRequestQueueItems.find((i) => i.id === id);
  if (!item || !item.text.trim()) return false;
  try {
    await vscode.commands.executeCommand(
      "workbench.action.chat.send",
      item.text
    );
    item.status = "sent";
    persistVoiceRequestQueue();
    return true;
  } catch {
    return false;
  }
}

function initializeVoiceRequestQueue(context: vscode.ExtensionContext): void {
  voiceRequestQueueContext = context;
  loadVoiceRequestQueue();
}

let voiceRequestQueuePanel: vscode.WebviewPanel | null = null;

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function generateVoiceRequestQueueHTML(items: VoiceRequestQueueItem[]): string {
  const rows = items
    .map((item) => {
      const textEsc = escapeHtml(item.text);
      const dateStr = new Date(item.createdAt).toLocaleString();
      const isPending = item.status === "pending";
      return `
        <tr data-id="${escapeHtml(item.id)}">
            <td><input type="text" class="item-text" value="${textEsc}" ${
        !isPending ? "disabled" : ""
      } data-id="${escapeHtml(item.id)}" /></td>
            <td class="meta">${dateStr} · ${item.source}</td>
            <td class="status">${item.status}</td>
            <td class="actions">
                ${
                  isPending
                    ? `<button class="btn btn-update" data-id="${escapeHtml(
                        item.id
                      )}">Update</button>`
                    : ""
                }
                ${
                  isPending
                    ? `<button class="btn btn-send" data-id="${escapeHtml(
                        item.id
                      )}">Send to chat</button>`
                    : ""
                }
                <button class="btn btn-delete" data-id="${escapeHtml(
                  item.id
                )}">Delete</button>
            </td>
        </tr>`;
    })
    .join("");
  return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: var(--vscode-font-family); padding: 16px; background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); }
        h2 { margin-top: 0; color: var(--vscode-textLink-foreground); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid var(--vscode-panel-border); }
        th { font-weight: 600; }
        .item-text { width: 100%; padding: 6px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); }
        .meta { font-size: 12px; color: var(--vscode-descriptionForeground); }
        .btn { padding: 4px 10px; margin-right: 4px; cursor: pointer; }
        .btn-send { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; }
        .btn-update, .btn-delete { background: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground); border: none; }
        .empty { color: var(--vscode-descriptionForeground); padding: 20px; }
    </style>
</head>
<body>
    <h2>Voice Request Queue (Jarvis / Lumina AI Chat)</h2>
    <p>Edit items, then Send to chat. Listening mode: use command palette &quot;Set Listening Mode - Active/Passive&quot;.</p>
    ${
      items.length === 0
        ? '<p class="empty">No items. Use voice (Play) in passive mode, or &quot;Add Current to Voice Queue&quot;.</p>'
        : `
    <table>
        <thead><tr><th>Text</th><th>Added</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>${rows}</tbody>
    </table>`
    }
    <script>
        const vscode = acquireVsCodeApi();
        document.querySelectorAll('.btn-update').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const input = document.querySelector('.item-text[data-id="' + id + '"]');
                const text = input ? input.value : '';
                vscode.postMessage({ type: 'edit', id, text });
            });
        });
        document.querySelectorAll('.btn-send').forEach(btn => {
            btn.addEventListener('click', () => vscode.postMessage({ type: 'send', id: btn.getAttribute('data-id') }));
        });
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', () => vscode.postMessage({ type: 'delete', id: btn.getAttribute('data-id') }));
        });
    </script>
</body>
</html>`;
}

function openVoiceRequestQueuePanel(): void {
  if (voiceRequestQueuePanel) {
    voiceRequestQueuePanel.reveal();
    voiceRequestQueuePanel.webview.html = generateVoiceRequestQueueHTML(
      getVoiceRequestQueueItems()
    );
    return;
  }
  const panel = vscode.window.createWebviewPanel(
    "luminaVoiceRequestQueue",
    "Voice Request Queue (Lumina AI Chat)",
    vscode.ViewColumn.One,
    { enableScripts: true, retainContextWhenHidden: true }
  );
  voiceRequestQueuePanel = panel;
  panel.onDidDispose(() => {
    voiceRequestQueuePanel = null;
  });
  panel.webview.html = generateVoiceRequestQueueHTML(
    getVoiceRequestQueueItems()
  );
  panel.webview.onDidReceiveMessage(
    async (msg: { type: string; id?: string; text?: string }) => {
      if (msg.type === "edit" && msg.id != null && msg.text != null) {
        updateVoiceRequestQueueItem(msg.id, msg.text);
      } else if (msg.type === "delete" && msg.id) {
        removeVoiceRequestQueueItem(msg.id);
      } else if (msg.type === "send" && msg.id) {
        const ok = await sendVoiceRequestQueueItemToChat(msg.id);
        if (ok) vscode.window.showInformationMessage("Sent to chat");
        else vscode.window.showErrorMessage("Failed to send to chat");
      }
      if (voiceRequestQueuePanel) {
        voiceRequestQueuePanel.webview.html = generateVoiceRequestQueueHTML(
          getVoiceRequestQueueItems()
        );
      }
    }
  );
}

// ============================================================================
// FILE CLEANUP STACK (Persistent queue for files to fix/validate/close – now under Explorer)
// ============================================================================

const FILE_CLEANUP_STACK_STORAGE_KEY = "lumina.fileCleanupStack.uris";
let fileCleanupStackContext: vscode.ExtensionContext | null = null;
let fileCleanupStackUris: string[] = [];

function loadFileCleanupStack(): void {
  if (!fileCleanupStackContext) return;
  const raw = fileCleanupStackContext.workspaceState.get<string[]>(
    FILE_CLEANUP_STACK_STORAGE_KEY
  );
  fileCleanupStackUris = Array.isArray(raw) ? raw : [];
}

function persistFileCleanupStack(): void {
  if (!fileCleanupStackContext) return;
  fileCleanupStackContext.workspaceState.update(
    FILE_CLEANUP_STACK_STORAGE_KEY,
    fileCleanupStackUris
  );
}

function getDiagnosticCounts(uri: vscode.Uri): {
  errors: number;
  warnings: number;
  infos: number;
} {
  const diagnostics = vscode.languages.getDiagnostics(uri);
  let errors = 0,
    warnings = 0,
    infos = 0;
  for (const d of diagnostics) {
    if (d.severity === vscode.DiagnosticSeverity.Error) errors++;
    else if (d.severity === vscode.DiagnosticSeverity.Warning) warnings++;
    else if (d.severity === vscode.DiagnosticSeverity.Information) infos++;
  }
  return { errors, warnings, infos };
}

function formatDiagnosticDescription(uri: vscode.Uri): string {
  const { errors, warnings, infos } = getDiagnosticCounts(uri);
  const parts: string[] = [];
  if (errors > 0) parts.push(`${errors} error${errors !== 1 ? "s" : ""}`);
  if (warnings > 0)
    parts.push(`${warnings} warning${warnings !== 1 ? "s" : ""}`);
  if (infos > 0) parts.push(`${infos} info`);
  return parts.length > 0 ? parts.join(", ") : "clean";
}

interface FileCleanupStackItem {
  uri: vscode.Uri;
  uriString: string;
}

class FileCleanupStackTreeDataProvider
  implements vscode.TreeDataProvider<FileCleanupStackItem>
{
  private _onDidChangeTreeData = new vscode.EventEmitter<
    FileCleanupStackItem | undefined | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getChildren(_element?: FileCleanupStackItem): FileCleanupStackItem[] {
    return fileCleanupStackUris
      .filter((s) => s.length > 0)
      .map((uriString) => ({ uri: vscode.Uri.parse(uriString), uriString }));
  }

  getTreeItem(element: FileCleanupStackItem): vscode.TreeItem {
    const item = new vscode.TreeItem(
      element.uri,
      vscode.TreeItemCollapsibleState.None
    );
    item.resourceUri = element.uri;
    item.description = formatDiagnosticDescription(element.uri);
    item.tooltip = `${path.basename(element.uri.fsPath)}\n${
      element.uri.fsPath
    }\n${item.description}`;
    item.command = {
      command: "lumina.fileCleanupStack.open",
      title: "Open",
      arguments: [element.uri],
    };
    return item;
  }
}

let fileCleanupStackTreeProvider: FileCleanupStackTreeDataProvider | null =
  null;

function initializeFileCleanupStack(context: vscode.ExtensionContext): void {
  fileCleanupStackContext = context;
  loadFileCleanupStack();

  fileCleanupStackTreeProvider = new FileCleanupStackTreeDataProvider();
  const viewId = "lumina.fileCleanupStack";
  // Register provider for the canonical view ID defined in package.json
  vscode.window.registerTreeDataProvider(viewId, fileCleanupStackTreeProvider);
  const treeView = vscode.window.createTreeView(viewId, {
    treeDataProvider: fileCleanupStackTreeProvider,
    showCollapseAll: false,
  });

  const addCurrentCmd = vscode.commands.registerCommand(
    "lumina.fileCleanupStack.addCurrent",
    () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || editor.document.uri.scheme !== "file") {
        vscode.window.showWarningMessage(
          "No file open to add to Cleanup Stack."
        );
        return;
      }
      const uriString = editor.document.uri.toString();
      if (fileCleanupStackUris.includes(uriString)) {
        vscode.window.showInformationMessage("File already in Cleanup Stack.");
        return;
      }
      fileCleanupStackUris.push(uriString);
      persistFileCleanupStack();
      fileCleanupStackTreeProvider?.refresh();
      vscode.window.showInformationMessage(
        `Added "${path.basename(editor.document.uri.fsPath)}" to Cleanup Stack.`
      );
    }
  );

  const addFilesWithDiagnosticsCmd = vscode.commands.registerCommand(
    "lumina.fileCleanupStack.addFilesWithDiagnostics",
    () => {
      const allDiagnostics = vscode.languages.getDiagnostics();
      const uris = new Set<string>();
      for (const [uri, diagnostics] of allDiagnostics) {
        if (uri.scheme === "file" && diagnostics.length > 0)
          uris.add(uri.toString());
      }
      let added = 0;
      for (const uriString of uris) {
        if (!fileCleanupStackUris.includes(uriString)) {
          fileCleanupStackUris.push(uriString);
          added++;
        }
      }
      persistFileCleanupStack();
      fileCleanupStackTreeProvider?.refresh();
      vscode.window.showInformationMessage(
        `Added ${added} file(s) with problems to Cleanup Stack.`
      );
    }
  );

  const removeCmd = vscode.commands.registerCommand(
    "lumina.fileCleanupStack.remove",
    (itemOrUri: FileCleanupStackItem | vscode.Uri) => {
      const uriString =
        itemOrUri && "uriString" in itemOrUri
          ? itemOrUri.uriString
          : itemOrUri && "toString" in itemOrUri
          ? (itemOrUri as vscode.Uri).toString()
          : undefined;
      if (!uriString) return;
      const idx = fileCleanupStackUris.indexOf(uriString);
      if (idx === -1) return;
      fileCleanupStackUris.splice(idx, 1);
      persistFileCleanupStack();
      fileCleanupStackTreeProvider?.refresh();
    }
  );

  const openCmd = vscode.commands.registerCommand(
    "lumina.fileCleanupStack.open",
    (arg: vscode.Uri | FileCleanupStackItem) => {
      const uri =
        arg && "uri" in arg
          ? (arg as FileCleanupStackItem).uri
          : (arg as vscode.Uri);
      if (uri) vscode.window.showTextDocument(uri, { preview: false });
    }
  );

  const refreshCmd = vscode.commands.registerCommand(
    "lumina.fileCleanupStack.refresh",
    () => {
      fileCleanupStackTreeProvider?.refresh();
    }
  );

  const diagSubscription = vscode.languages.onDidChangeDiagnostics(() => {
    fileCleanupStackTreeProvider?.refresh();
  });

  const focusCmd = vscode.commands.registerCommand(
    "lumina.fileCleanupStack.focus",
    () => {
      // The view is in the Explorer panel - focus explorer to show File Cleanup Stack
      vscode.commands.executeCommand("workbench.view.explorer");
    }
  );

  context.subscriptions.push(
    treeView,
    addCurrentCmd,
    addFilesWithDiagnosticsCmd,
    removeCmd,
    openCmd,
    refreshCmd,
    focusCmd,
    diagSubscription
  );

  // Open documents count (status bar, left – like Problems count)
  initializeOpenDocumentsCount(context);
}

// ============================================================================
// OPEN DOCUMENTS COUNT (Status bar queue number – works with File Cleanup Stack)
// ============================================================================

let openDocumentsStatusBarItem: vscode.StatusBarItem | null = null;

function getOpenDocumentsCount(): number {
  return vscode.workspace.textDocuments.filter((d) => d.uri.scheme === "file")
    .length;
}

function updateOpenDocumentsStatusBar(): void {
  if (!openDocumentsStatusBarItem) return;
  const n = getOpenDocumentsCount();
  openDocumentsStatusBarItem.text = `$(files) ${n}`;
  openDocumentsStatusBarItem.tooltip = `${n} document${
    n !== 1 ? "s" : ""
  } open in editor. Click to open File Cleanup Stack.`;
  openDocumentsStatusBarItem.show();
}

function initializeOpenDocumentsCount(context: vscode.ExtensionContext): void {
  openDocumentsStatusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    900 // Left side, high priority (near "upper left" of status bar)
  );
  openDocumentsStatusBarItem.command = "lumina.fileCleanupStack.focus";

  updateOpenDocumentsStatusBar();

  const onOpen = vscode.workspace.onDidOpenTextDocument(() =>
    updateOpenDocumentsStatusBar()
  );
  const onClose = vscode.workspace.onDidCloseTextDocument(() =>
    updateOpenDocumentsStatusBar()
  );

  context.subscriptions.push(openDocumentsStatusBarItem, onOpen, onClose);
}

// ============================================================================
// VOICE CONTROLS FUNCTIONALITY (Consolidated from cursor-voice-controls)
// ============================================================================

enum VoiceState {
  Stopped = "stopped",
  Playing = "playing",
  Paused = "paused",
}

interface TranscriptionSegment {
  text: string;
  timestamp: number;
  duration?: number;
}

class LuminaVoiceControls {
  private state: VoiceState = VoiceState.Stopped;
  private statusBarItem: vscode.StatusBarItem;
  private outputChannel: vscode.OutputChannel;
  private transcriptionHistory: TranscriptionSegment[] = [];
  private currentSegmentIndex: number = -1;
  private playbackSpeed: number = 1.0;
  private skipInterval: number = 5;
  private autoHideEnabled: boolean = true;
  private hideTimeout: NodeJS.Timeout | null = null;
  private hoverTimeout: number = 2000;
  private autoSendEnabled: boolean = true;
  private pauseDuration: number = 4000;
  private lastTranscriptionTime: number = 0;
  private autoSendTimeout: NodeJS.Timeout | null = null;
  private pendingText: string = "";
  private isMonitoring: boolean = false;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      1000
    );
    this.statusBarItem.command = "lumina.voiceControls.toggle";
    this.updateStatusBar();
    this.setupAutoHide();
    this.setupAutoSend();
    this.outputChannel = vscode.window.createOutputChannel(
      "Lumina Voice Controls"
    );
  }

  private setupAutoHide(): void {
    if (!this.autoHideEnabled) {
      this.statusBarItem.show();
      return;
    }
    this.statusBarItem.show();
    this.startHideTimer();
    this.statusBarItem.tooltip = `Click to toggle voice transcription\nCurrent state: ${
      this.state
    }\nAuto-hide: ${this.autoHideEnabled ? "Enabled" : "Disabled"}`;
  }

  private startHideTimer(): void {
    if (!this.autoHideEnabled) return;
    if (this.hideTimeout) {
      clearTimeout(this.hideTimeout);
    }
    this.hideTimeout = setTimeout(() => {
      if (this.state === VoiceState.Stopped) {
        this.statusBarItem.hide();
        this.log("Status bar auto-hidden");
      }
    }, this.hoverTimeout);
  }

  private cancelHideTimer(): void {
    if (this.hideTimeout) {
      clearTimeout(this.hideTimeout);
      this.hideTimeout = null;
    }
    this.statusBarItem.show();
  }

  private setupAutoSend(): void {
    const config = vscode.workspace.getConfiguration("lumina.voiceControls");
    this.autoSendEnabled = config.get<boolean>("autoSend", true);
    this.pauseDuration = config.get<number>("pauseDuration", 4000);
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("lumina.voiceControls.autoSend")) {
        this.autoSendEnabled = config.get<boolean>("autoSend", true);
        this.log(`Auto-send ${this.autoSendEnabled ? "enabled" : "disabled"}`);
      }
      if (e.affectsConfiguration("lumina.voiceControls.pauseDuration")) {
        this.pauseDuration = config.get<number>("pauseDuration", 4000);
        this.log(`Auto-send pause duration set to ${this.pauseDuration}ms`);
      }
    });
  }

  private startAutoSendTimer(): void {
    if (!this.autoSendEnabled || this.state !== VoiceState.Playing) return;
    this.cancelAutoSend();
    this.autoSendTimeout = setTimeout(() => {
      if (
        this.pendingText.trim().length > 0 &&
        this.state === VoiceState.Playing
      ) {
        this.log(`Auto-sending after ${this.pauseDuration}ms pause`);
        this.autoSend();
      }
    }, this.pauseDuration);
  }

  private cancelAutoSend(): void {
    if (this.autoSendTimeout) {
      clearTimeout(this.autoSendTimeout);
      this.autoSendTimeout = null;
    }
  }

  private autoSend(): void {
    if (this.pendingText.trim().length === 0) return;
    this.log(`Auto-sending: ${this.pendingText.substring(0, 50)}...`);
    try {
      vscode.commands.executeCommand(
        "workbench.action.chat.send",
        this.pendingText
      );
      this.pendingText = "";
      this.lastTranscriptionTime = 0;
      vscode.window.showInformationMessage(
        `✅ Auto-sent (${this.pauseDuration}ms pause detected)`
      );
    } catch (error) {
      this.log(`Error auto-sending: ${error}`);
    }
    this.cancelAutoSend();
  }

  public monitorTranscription(text: string): void {
    if (!this.autoSendEnabled || this.state !== VoiceState.Playing) return;
    if (this.pendingText) {
      this.pendingText += " " + text;
    } else {
      this.pendingText = text;
    }
    this.lastTranscriptionTime = Date.now();
    this.startAutoSendTimer();
    this.log(`Transcription monitored: "${text.substring(0, 30)}..."`);
  }

  private updateStatusBar(): void {
    const icons = {
      [VoiceState.Stopped]: "⏹",
      [VoiceState.Playing]: "▶",
      [VoiceState.Paused]: "⏸",
    };
    const labels = {
      [VoiceState.Stopped]: "Voice: Stopped",
      [VoiceState.Playing]: "Voice: Playing",
      [VoiceState.Paused]: "Voice: Paused (Muted)",
    };
    this.statusBarItem.text = `${icons[this.state]} ${labels[this.state]}`;
    this.statusBarItem.tooltip = `Click to toggle voice transcription\nCurrent state: ${this.state}`;
    this.statusBarItem.show();
  }

  private log(message: string): void {
    this.outputChannel.appendLine(`[${new Date().toISOString()}] ${message}`);
  }

  public async play(): Promise<void> {
    if (this.state === VoiceState.Playing) {
      vscode.window.showInformationMessage(
        "Voice transcription is already playing"
      );
      return;
    }
    this.state = VoiceState.Playing;
    this.updateStatusBar();
    this.cancelHideTimer();
    this.isMonitoring = true;
    this.pendingText = "";
    this.lastTranscriptionTime = Date.now();
    this.log("Voice transcription started/resumed");
    try {
      await vscode.commands.executeCommand("workbench.action.chat.voice.start");
    } catch (error) {
      this.log(`Note: Direct voice activation command not available: ${error}`);
    }
    vscode.window.showInformationMessage(
      `▶ Voice transcription playing (auto-send: ${
        this.autoSendEnabled ? "ON" : "OFF"
      })`
    );
  }

  public async pause(): Promise<void> {
    if (this.state === VoiceState.Stopped) {
      vscode.window.showWarningMessage(
        "Voice transcription is not active. Use Play first."
      );
      return;
    }
    if (this.state === VoiceState.Paused) {
      return this.play();
    }
    this.state = VoiceState.Paused;
    this.updateStatusBar();
    this.log("Voice transcription paused (muted)");
    try {
      await vscode.commands.executeCommand("workbench.action.chat.voice.pause");
    } catch (error) {
      this.log(`Note: Direct voice pause command not available: ${error}`);
    }
    vscode.window.showInformationMessage(
      "⏸ Voice transcription paused (muted)"
    );
  }

  public async stop(): Promise<void> {
    if (this.state === VoiceState.Stopped) {
      vscode.window.showInformationMessage(
        "Voice transcription is already stopped"
      );
      return;
    }
    this.cancelAutoSend();
    this.isMonitoring = false;
    this.pendingText = "";
    this.state = VoiceState.Stopped;
    this.updateStatusBar();
    this.log("Voice transcription stopped");
    this.startHideTimer();
    try {
      await vscode.commands.executeCommand("workbench.action.chat.voice.stop");
    } catch (error) {
      this.log(`Note: Direct voice stop command not available: ${error}`);
    }
    vscode.window.showInformationMessage("⏹ Voice transcription stopped");
  }

  public async toggle(): Promise<void> {
    switch (this.state) {
      case VoiceState.Stopped:
        await this.play();
        break;
      case VoiceState.Playing:
        await this.pause();
        break;
      case VoiceState.Paused:
        await this.play();
        break;
    }
  }

  public enableAutoHide(enabled: boolean): void {
    this.autoHideEnabled = enabled;
    if (enabled) {
      this.setupAutoHide();
    } else {
      this.cancelHideTimer();
      this.statusBarItem.show();
    }
    this.log(`Auto-hide ${enabled ? "enabled" : "disabled"}`);
  }

  public setAutoHideDelay(delay: number): void {
    this.hoverTimeout = delay;
    this.log(`Auto-hide delay set to ${delay}ms`);
  }

  /** Listening mode: passive = add to voice queue only; active = pendingText + optional auto-send */
  public getListeningMode(): "active" | "passive" {
    const config = vscode.workspace.getConfiguration(
      "lumina.voiceRequestQueue"
    );
    return (
      (config.get<string>("listeningMode", "active") as "active" | "passive") ||
      "active"
    );
  }

  public getPendingText(): string {
    return this.pendingText || "";
  }

  public clearPendingText(): void {
    this.pendingText = "";
    this.lastTranscriptionTime = 0;
    this.cancelAutoSend();
  }

  public addTranscriptionSegment(text: string, timestamp?: number): void {
    const segment: TranscriptionSegment = {
      text,
      timestamp: timestamp || Date.now(),
      duration: undefined,
    };
    this.transcriptionHistory.push(segment);
    this.currentSegmentIndex = this.transcriptionHistory.length - 1;
    this.log(`Added transcription segment: ${text.substring(0, 50)}...`);
    if (this.getListeningMode() === "passive") {
      const added = addToVoiceRequestQueue(text, "passive");
      if (added) this.log("Added to voice request queue (passive mode)");
      return;
    }
    if (this.isMonitoring && this.state === VoiceState.Playing) {
      this.monitorTranscription(text);
    }
  }

  public dispose(): void {
    if (this.hideTimeout) clearTimeout(this.hideTimeout);
    if (this.autoSendTimeout) clearTimeout(this.autoSendTimeout);
    this.statusBarItem.dispose();
    this.outputChannel.dispose();
  }
}

let luminaVoiceControls: LuminaVoiceControls | null = null;

function initializeVoiceControls(context: vscode.ExtensionContext) {
  luminaVoiceControls = new LuminaVoiceControls();
  const config = vscode.workspace.getConfiguration("lumina.voiceControls");
  const autoHide = config.get<boolean>("autoHide", true);
  const autoHideDelay = config.get<number>("autoHideDelay", 2000);
  luminaVoiceControls.enableAutoHide(autoHide);
  if (autoHideDelay) {
    luminaVoiceControls.setAutoHideDelay(autoHideDelay);
  }

  const playCommand = vscode.commands.registerCommand(
    "lumina.voiceControls.play",
    () => {
      luminaVoiceControls!.play();
    }
  );
  const pauseCommand = vscode.commands.registerCommand(
    "lumina.voiceControls.pause",
    () => {
      luminaVoiceControls!.pause();
    }
  );
  const stopCommand = vscode.commands.registerCommand(
    "lumina.voiceControls.stop",
    () => {
      luminaVoiceControls!.stop();
    }
  );
  const toggleCommand = vscode.commands.registerCommand(
    "lumina.voiceControls.toggle",
    () => {
      luminaVoiceControls!.toggle();
    }
  );

  context.subscriptions.push(
    playCommand,
    pauseCommand,
    stopCommand,
    toggleCommand,
    luminaVoiceControls
  );
}

// ============================================================================
// ACTIVE MODEL STATUS FUNCTIONALITY (Consolidated from cursor-active-model-status)
// ============================================================================

interface ModelStatus {
  active_model: string;
  actual_model?: string; // Resolved actual model name (not "Auto")
  is_auto_mode?: boolean; // True if currently in auto mode
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

let activeModelStatusBarItem: vscode.StatusBarItem | null = null;
let activeModelWatcher: vscode.FileSystemWatcher | undefined;
let activeModelInterval: NodeJS.Timeout | undefined;

/**
 * Get the actual model name from status, resolving "Auto" placeholders
 * Priority: actual_model → description → active_model
 */
function getActualModelName(status: ModelStatus): string {
  // Priority 1: Use explicit actual_model if available
  if (status.actual_model && status.actual_model.trim().length > 0) {
    return status.actual_model;
  }

  // Priority 2: Extract from description if it contains model info
  if (status.description && status.description.trim().length > 0) {
    // Look for common model patterns in description
    const modelPatterns = [
      /model[:\s]+([\w-]+)/i,
      /using[:\s]+([\w-]+)/i,
      /resolved[:\s]+([\w-]+)/i,
      /([\w-]+@[\w-]+)/, // Handle model@provider format
    ];

    for (const pattern of modelPatterns) {
      const match = status.description.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }

    // If description doesn't have a pattern, use it as-is if it's short enough
    if (status.description.length < 50 && !status.description.includes(" ")) {
      return status.description;
    }
  }

  // Priority 3: Use active_model directly
  if (status.active_model && status.active_model.trim().length > 0) {
    return status.active_model;
  }

  return "Unknown";
}

/**
 * Check if the model is in auto mode
 */
function isAutoMode(status: ModelStatus): boolean {
  // Explicit flag check
  if (status.is_auto_mode === true) {
    return true;
  }

  // Check for common auto mode patterns
  const autoPatterns = [
    /^auto$/i,
    /auto[-_]?mode/i,
    /automatically/i,
    /auto[-_]?select/i,
    /^@/, // @ prefix often indicates dynamic/auto selection
  ];

  if (
    status.active_model &&
    autoPatterns.some((p) => p.test(status.active_model))
  ) {
    return true;
  }

  if (status.description && /auto/i.test(status.description)) {
    return true;
  }

  return false;
}

function initializeActiveModelStatus(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("lumina.activeModelStatus");
  const updateInterval = config.get<number>("updateInterval", 1000);
  const showInStatusBar = config.get<boolean>("showInStatusBar", true);

  if (!showInStatusBar) return;

  activeModelStatusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    1000
  );
  activeModelStatusBarItem.command = "lumina.activeModelStatus.showDetails";
  activeModelStatusBarItem.tooltip = "Click to show active model details";

  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!workspaceRoot) return;

  const statusFile = path.join(
    workspaceRoot,
    "data",
    "cursor_active_model_status.json"
  );

  function updateStatusBar() {
    try {
      if (!fs.existsSync(statusFile)) {
        activeModelStatusBarItem!.text = "$(sync~spin) Model: Unknown";
        activeModelStatusBarItem!.show();
        return;
      }

      const statusData = fs.readFileSync(statusFile, "utf8");
      const status: ModelStatus = JSON.parse(statusData);

      // Use getActualModelName to resolve "Auto" placeholders
      const actualModelName = getActualModelName(status);
      const modelType = status.model_type || "unknown";
      const autoMode = isAutoMode(status);

      let displayText = `$(circuit-board) ${actualModelName}`;

      // Add visual indicators for model type
      if (modelType === "local") {
        displayText += " $(home)";
      } else if (modelType === "cloud") {
        displayText += " $(cloud)";
      } else if (modelType === "virtual_cluster") {
        displayText += " $(server)";
      }

      // Add visual indicator for auto mode
      if (autoMode) {
        displayText += " $(sync~spin) AUTO";
        activeModelStatusBarItem!.backgroundColor = new vscode.ThemeColor(
          "statusBarItem.warningBackground"
        );
      } else {
        activeModelStatusBarItem!.backgroundColor = undefined;
      }

      activeModelStatusBarItem!.text = displayText;
      activeModelStatusBarItem!.tooltip = `Active Model: ${actualModelName}\nType: ${modelType}\n${
        status.is_local ? "Local" : "Cloud"
      }\n${
        autoMode ? "🔄 Auto Mode (model resolved)" : "✅ Direct Selection"
      }\n\nClick for details`;
      activeModelStatusBarItem!.show();
    } catch (error) {
      console.error("Error updating active model status bar:", error);
      activeModelStatusBarItem!.text = "$(error) Model: Error";
      activeModelStatusBarItem!.backgroundColor = undefined;
      activeModelStatusBarItem!.show();
    }
  }

  updateStatusBar();

  activeModelWatcher = vscode.workspace.createFileSystemWatcher(
    new vscode.RelativePattern(
      workspaceRoot,
      "data/cursor_active_model_status.json"
    )
  );
  activeModelWatcher.onDidChange(() => updateStatusBar());

  activeModelInterval = setInterval(() => updateStatusBar(), updateInterval);

  const showDetailsCommand = vscode.commands.registerCommand(
    "lumina.activeModelStatus.showDetails",
    () => {
      try {
        if (!fs.existsSync(statusFile)) {
          vscode.window.showInformationMessage(
            "Model status file not found. Run the tracker script first."
          );
          return;
        }

        const statusData = fs.readFileSync(statusFile, "utf8");
        const status: ModelStatus = JSON.parse(statusData);

        // Use getActualModelName to resolve "Auto" placeholders
        const actualModelName = getActualModelName(status);
        const autoMode = isAutoMode(status);

        const details = [
          `**Active Model:** ${status.active_model || "Unknown"}`,
          `**Resolved Model:** ${
            actualModelName === status.active_model
              ? "(direct)"
              : "(auto-resolved)"
          }`,
          `**Type:** ${status.model_type || "unknown"}`,
          `**Provider:** ${status.provider || "unknown"}`,
          `**Location:** ${status.is_local ? "Local" : "Cloud"}`,
          `**Mode:** ${autoMode ? "🔄 Auto (resolved)" : "✅ Direct"}`,
        ];

        if (status.endpoint) {
          details.push(`**Endpoint:** ${status.endpoint}`);
        }
        if (status.context_length) {
          details.push(
            `**Context Length:** ${status.context_length.toLocaleString()} tokens`
          );
        }
        if (status.cluster_nodes) {
          details.push(`**Cluster Nodes:** ${status.cluster_nodes}`);
          details.push(`**Cluster Type:** ${status.cluster_type || "unknown"}`);
          details.push(`**Routing:** ${status.cluster_routing || "unknown"}`);
        }
        if (status.description) {
          details.push(`**Description:** ${status.description}`);
        }
        if (status.last_updated) {
          const lastUpdated = new Date(status.last_updated);
          details.push(`**Last Updated:** ${lastUpdated.toLocaleString()}`);
        }

        vscode.window.showInformationMessage(details.join("\n"), {
          modal: true,
        });
      } catch (error) {
        vscode.window.showErrorMessage(`Error reading model status: ${error}`);
      }
    }
  );

  const refreshCommand = vscode.commands.registerCommand(
    "lumina.activeModelStatus.refresh",
    () => {
      updateStatusBar();
      vscode.window.showInformationMessage("Active model status refreshed");
    }
  );

  context.subscriptions.push(
    activeModelStatusBarItem,
    activeModelWatcher,
    showDetailsCommand,
    refreshCommand
  );

  context.subscriptions.push({
    dispose: () => {
      if (activeModelInterval) clearInterval(activeModelInterval);
    },
  });
}

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

const STALE_PROGRESS_MS = 90 * 1000;
const DONE_PROGRESS_STATUSES = ["Ready", "Complete", "Idle", "Done", "Stopped"];

function isProgressStale(status: ProgressStatus): boolean {
  const done = DONE_PROGRESS_STATUSES.some(
    (s) => (status.status || "").toLowerCase() === s.toLowerCase()
  );
  if (done) return false;
  const ts = status.timestamp ? new Date(status.timestamp).getTime() : 0;
  return ts > 0 && Date.now() - ts > STALE_PROGRESS_MS;
}

function getEffectiveProgressStatusForFile(
  progressStatusFile: string
): ProgressStatus {
  if (!fs.existsSync(progressStatusFile)) {
    return {
      agent: "JARVIS",
      status: "Ready",
      progress: 100,
      message: "",
      timestamp: new Date().toISOString(),
    };
  }
  try {
    const status: ProgressStatus = JSON.parse(
      fs.readFileSync(progressStatusFile, "utf8")
    );
    if (isProgressStale(status)) {
      return {
        agent: status.agent || "JARVIS",
        status: "Ready",
        progress: 100,
        message: "Stale display reset",
        timestamp: new Date().toISOString(),
      };
    }
    return status;
  } catch {
    return {
      agent: "JARVIS",
      status: "Ready",
      progress: 100,
      message: "",
      timestamp: new Date().toISOString(),
    };
  }
}

function initializeProgressStatus(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("lumina.progress");
  const enabled = config.get<boolean>("enabled", true);
  const updateInterval = config.get<number>("updateInterval", 2000);

  if (!enabled) return;

  progressStatusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100
  );
  progressStatusBarItem.command = "lumina.showProgress";
  progressStatusBarItem.tooltip =
    "LUMINA Progress Status - Airport Signboard Style\nClick to show details";
  context.subscriptions.push(progressStatusBarItem);

  // Register commands first so they always exist (even when no workspace folder yet)
  const resetProgressCommand = vscode.commands.registerCommand(
    "lumina.resetProgressDisplay",
    () => {
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!root) {
        vscode.window.showWarningMessage(
          "Open a workspace folder first to reset LUMINA progress."
        );
        return;
      }
      try {
        const dataDir = path.join(root, "data");
        if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
        const progressStatusFile = path.join(
          root,
          "data",
          "progress_status.json"
        );
        const payload: ProgressStatus = {
          agent: "JARVIS",
          status: "Ready",
          progress: 100,
          message: "",
          timestamp: new Date().toISOString(),
        };
        fs.writeFileSync(
          progressStatusFile,
          JSON.stringify(payload, null, 2),
          "utf8"
        );
        if (progressStatusBarItem) {
          progressStatusBarItem.text = "$(sync~spin) LUMINA | Ready";
          progressStatusBarItem.show();
        }
        vscode.window.showInformationMessage(
          "LUMINA progress display reset to Ready."
        );
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to reset progress: ${error}`);
      }
    }
  );

  const showProgressCommand = vscode.commands.registerCommand(
    "lumina.showProgress",
    () => {
      const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!root) {
        vscode.window.showWarningMessage(
          "Open a workspace folder first to show LUMINA progress."
        );
        return;
      }
      try {
        const progressStatusFile = path.join(
          root,
          "data",
          "progress_status.json"
        );
        const status = getEffectiveProgressStatusForFile(progressStatusFile);
        const panel = vscode.window.createWebviewPanel(
          "luminaProgress",
          "LUMINA Progress Status - Airport Signboard",
          vscode.ViewColumn.One,
          { enableScripts: true, retainContextWhenHidden: true }
        );
        panel.webview.html = generateProgressStatusHTML(status);
      } catch (error) {
        vscode.window.showErrorMessage(
          `Error showing progress status: ${error}`
        );
      }
    }
  );

  context.subscriptions.push(showProgressCommand, resetProgressCommand);
  luminaLog(
    "initializeProgressStatus: reset/show progress commands registered"
  );

  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!workspaceRoot) {
    luminaLog(
      "initializeProgressStatus: no workspace folder, status bar will not update until folder opened"
    );
    return;
  }

  const progressStatusFile = path.join(
    workspaceRoot,
    "data",
    "progress_status.json"
  );
  luminaLog(
    `initializeProgressStatus: progress file path: ${progressStatusFile}`
  );

  // If no progress file, write default Ready so the bar does not stay stuck
  try {
    if (!fs.existsSync(progressStatusFile)) {
      const dataDir = path.join(workspaceRoot, "data");
      if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
      const payload: ProgressStatus = {
        agent: "JARVIS",
        status: "Ready",
        progress: 100,
        message: "",
        timestamp: new Date().toISOString(),
      };
      fs.writeFileSync(
        progressStatusFile,
        JSON.stringify(payload, null, 2),
        "utf8"
      );
      luminaLog(
        "initializeProgressStatus: wrote default progress_status.json (Ready)"
      );
    }
  } catch (e) {
    luminaLog(
      `initializeProgressStatus: could not write default progress file: ${e}`
    );
  }

  function getEffectiveProgressStatus(): ProgressStatus {
    return getEffectiveProgressStatusForFile(progressStatusFile);
  }

  function updateProgressStatus() {
    try {
      const status = getEffectiveProgressStatus();

      // Airport signboard style: scrolling text effect
      const agentName = status.agent || "JARVIS";
      const statusText = status.status || "Ready";
      const progressPercent = status.progress || 0;
      const message = status.message || "";

      // Create scrolling effect by rotating through status parts
      const statusParts = [
        `${agentName}`,
        `${statusText}`,
        progressPercent > 0 ? `${progressPercent}%` : "",
        message ? message.substring(0, 30) : "",
      ].filter((p) => p.length > 0);

      const isReady =
        (statusText || "").toLowerCase() === "ready" && progressPercent >= 100;
      const icon = isReady ? "$(check)" : "$(sync~spin)";
      if (statusParts.length > 0) {
        const currentPart =
          statusParts[currentProgressIndex % statusParts.length];
        progressStatusBarItem!.text = `${icon} LUMINA | ${currentPart}`;
        currentProgressIndex++;
      } else {
        progressStatusBarItem!.text = `${icon} LUMINA | Ready`;
      }

      progressStatusBarItem!.tooltip = `LUMINA Progress Status\nAgent: ${agentName}\nStatus: ${statusText}\nProgress: ${progressPercent}%\n${
        message ? `Message: ${message}` : ""
      }\n\nClick to show details`;
      progressStatusBarItem!.show();
    } catch (error) {
      console.error("Error updating progress status:", error);
      progressStatusBarItem!.text = "$(sync~spin) LUMINA | Status...";
      progressStatusBarItem!.show();
    }
  }

  luminaLog("initializeProgressStatus: running first updateProgressStatus()");
  updateProgressStatus();

  progressStatusWatcher = vscode.workspace.createFileSystemWatcher(
    new vscode.RelativePattern(workspaceRoot, "data/progress_status.json")
  );
  progressStatusWatcher.onDidChange(() => updateProgressStatus());
  progressStatusWatcher.onDidCreate(() => updateProgressStatus());

  progressStatusInterval = setInterval(
    () => updateProgressStatus(),
    updateInterval
  );

  context.subscriptions.push(progressStatusWatcher);

  context.subscriptions.push({
    dispose: () => {
      if (progressStatusInterval) clearInterval(progressStatusInterval);
    },
  });

  luminaLog(
    "initializeProgressStatus: done (watcher + interval set; bar updates from progress_status.json or shows Ready if stale/missing)"
  );
}

function generateProgressStatusHTML(status: ProgressStatus): string {
  const agent = status.agent || "JARVIS";
  const statusText = status.status || "Ready";
  const progress = status.progress || 0;
  const message = status.message || "";

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
        <div class="message">${message || "System operational"}</div>
        <div class="timestamp">Last Updated: ${new Date(
          status.timestamp || Date.now()
        ).toLocaleString()}</div>
    </div>
</body>
</html>`;
}

export function deactivate() {
  if (todoStatusRefreshInterval) {
    clearInterval(todoStatusRefreshInterval);
  }
  if (fileAutoCloseManager) {
    fileAutoCloseManager.dispose();
  }
  if (unifiedQueueInterval) {
    clearInterval(unifiedQueueInterval);
  }
  if (footerTickerInterval) {
    clearInterval(footerTickerInterval);
  }
  if (luminaVoiceControls) {
    luminaVoiceControls.dispose();
  }
  if (activeModelInterval) {
    clearInterval(activeModelInterval);
  }
  if (progressStatusInterval) {
    clearInterval(progressStatusInterval);
  }
  if (footerCustomizationInterval) {
    clearInterval(footerCustomizationInterval);
  }
}

// ============================================================================
// FOOTER CUSTOMIZATION (Ask Heap Stack and Notifications IDE-QUEUE)
// ============================================================================

let askHeapStackStatusBarItem: vscode.StatusBarItem | null = null;
let notificationsStatusBarItem: vscode.StatusBarItem | null = null;
let footerCustomizationInterval: NodeJS.Timeout | undefined;

function initializeFooterCustomization(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("lumina.footer");
  const enabled = config.get<boolean>("enabled", true);
  const showAskHeapStack = config.get<boolean>("showAskHeapStack", true);
  const showNotifications = config.get<boolean>("showNotifications", true);

  if (!enabled) return;

  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!workspaceRoot) return;

  // Create ask-heap-stack status bar item (PREFIX - left side, high priority)
  if (showAskHeapStack) {
    askHeapStackStatusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      1000 // High priority - appears first (prefix)
    );
    askHeapStackStatusBarItem.command = "lumina.footer.showAskHeapStack";
    askHeapStackStatusBarItem.tooltip = "Ask Heap Stack - Current/Total";
    context.subscriptions.push(askHeapStackStatusBarItem);
  }

  // Create notifications status bar item (SUFFIX - right side, low priority)
  if (showNotifications) {
    notificationsStatusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      1 // Low priority - appears last (suffix)
    );
    notificationsStatusBarItem.command = "lumina.footer.showNotifications";
    notificationsStatusBarItem.tooltip = "Notifications [IDE-QUEUE]";
    context.subscriptions.push(notificationsStatusBarItem);
  }

  // Update status bar items
  updateFooterStatusBarItems();

  // Update every 2 seconds
  footerCustomizationInterval = setInterval(
    () => updateFooterStatusBarItems(),
    2000
  );

  // Register commands
  const showAskHeapStackCommand = vscode.commands.registerCommand(
    "lumina.footer.showAskHeapStack",
    () => {
      const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!workspaceRoot) {
        vscode.window.showInformationMessage(
          "Ask Heap Stack: No workspace found"
        );
        return;
      }

      const askHeapStackFile = path.join(
        workspaceRoot,
        "data",
        "ask_heap_stack",
        "ask_heap_stack.json"
      );
      let askCurrent = 0;
      let askTotal = 0;

      if (fs.existsSync(askHeapStackFile)) {
        try {
          const data = JSON.parse(fs.readFileSync(askHeapStackFile, "utf-8"));
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
    "lumina.footer.showNotifications",
    () => {
      const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!workspaceRoot) {
        vscode.window.showInformationMessage(
          "Notifications [IDE-QUEUE]: No workspace found"
        );
        return;
      }

      const notificationsFile = path.join(
        workspaceRoot,
        "data",
        "ide_notifications",
        "notifications.json"
      );
      let notificationCount = 0;
      let notifications: any[] = [];

      if (fs.existsSync(notificationsFile)) {
        try {
          const data = JSON.parse(fs.readFileSync(notificationsFile, "utf-8"));
          notificationCount = data.count || data.notifications?.length || 0;
          notifications = data.notifications || [];
        } catch (e) {
          // Ignore errors
        }
      }

      const message = `Notifications [IDE-QUEUE]: ${notificationCount} notification${
        notificationCount !== 1 ? "s" : ""
      }`;
      if (notifications.length > 0) {
        const details = notifications
          .slice(0, 5)
          .map(
            (n: any, i: number) =>
              `${i + 1}. ${n.title || n.message || "Notification"}`
          )
          .join("\n");
        vscode.window.showInformationMessage(
          `${message}\n\n${details}${notifications.length > 5 ? "\n..." : ""}`
        );
      } else {
        vscode.window.showInformationMessage(message);
      }
    }
  );

  context.subscriptions.push(showAskHeapStackCommand, showNotificationsCommand);

  context.subscriptions.push({
    dispose: () => {
      if (footerCustomizationInterval)
        clearInterval(footerCustomizationInterval);
    },
  });
}

function updateFooterStatusBarItems() {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!workspaceRoot) {
    return;
  }

  const config = vscode.workspace.getConfiguration("lumina.footer");
  const showAskHeapStack = config.get<boolean>("showAskHeapStack", true);
  const showNotifications = config.get<boolean>("showNotifications", true);

  // Get ask-heap-stack data
  if (showAskHeapStack && askHeapStackStatusBarItem) {
    const askHeapStackFile = path.join(
      workspaceRoot,
      "data",
      "ask_heap_stack",
      "ask_heap_stack.json"
    );
    let askCurrent = 0;
    let askTotal = 0;

    if (fs.existsSync(askHeapStackFile)) {
      try {
        const data = JSON.parse(fs.readFileSync(askHeapStackFile, "utf-8"));
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
    const notificationsFile = path.join(
      workspaceRoot,
      "data",
      "ide_notifications",
      "notifications.json"
    );
    let notificationCount = 0;

    if (fs.existsSync(notificationsFile)) {
      try {
        const data = JSON.parse(fs.readFileSync(notificationsFile, "utf-8"));
        notificationCount = data.count || data.notifications?.length || 0;
      } catch (e) {
        // Ignore errors
      }
    }

    // Update notifications status bar (SUFFIX)
    notificationsStatusBarItem.text = `$(bell) (${notificationCount}) #notifications [IDE-QUEUE]`;
    notificationsStatusBarItem.show();
  }
}
