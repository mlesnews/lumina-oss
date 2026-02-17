"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
/**
 * Cursor Voice Controls Extension
 *
 * Provides full VCR controls (Play, Pause, Stop, Skip Forward, Skip Back, Fast Forward, Fast Rewind)
 * for Cursor voice transcription.
 * Pause effectively mutes the transcription without stopping it completely.
 */
var VoiceState;
(function (VoiceState) {
    VoiceState["Stopped"] = "stopped";
    VoiceState["Playing"] = "playing";
    VoiceState["Paused"] = "paused";
})(VoiceState || (VoiceState = {}));
class VoiceControls {
    constructor() {
        this.state = VoiceState.Stopped;
        this.transcriptionHistory = [];
        this.currentSegmentIndex = -1;
        this.playbackSpeed = 1.0; // Normal speed
        this.skipInterval = 5; // seconds to skip
        // Auto-hide functionality
        this.autoHideEnabled = true;
        this.hideTimeout = null;
        this.hoverTimeout = 2000; // Hide after 2 seconds of no hover
        this.isHovering = false;
        this.statusBarHoverDisposable = null;
        // Hands-free auto-send functionality
        this.autoSendEnabled = true;
        this.pauseDuration = 4000; // Default 4 seconds (3-5 range)
        this.lastTranscriptionTime = 0;
        this.autoSendTimeout = null;
        this.pendingText = '';
        this.isMonitoring = false;
        // Create status bar item
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 1000);
        this.statusBarItem.command = 'cursorVoiceControls.toggle';
        this.updateStatusBar();
        this.setupAutoHide();
        this.setupAutoSend();
        // Create output channel for logging
        this.outputChannel = vscode.window.createOutputChannel('Cursor Voice Controls');
    }
    setupAutoHide() {
        if (!this.autoHideEnabled) {
            this.statusBarItem.show();
            return;
        }
        // Show initially, then set up auto-hide
        this.statusBarItem.show();
        this.startHideTimer();
        // Set up hover detection (using tooltip/mouse events if available)
        // Note: VS Code doesn't directly support hover events on status bar items
        // So we'll use a different approach - hide when not actively used
        this.statusBarItem.tooltip = `Click to toggle voice transcription\nCurrent state: ${this.state}\nAuto-hide: ${this.autoHideEnabled ? 'Enabled' : 'Disabled'}`;
    }
    startHideTimer() {
        if (!this.autoHideEnabled)
            return;
        // Clear existing timer
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
        }
        // Hide after timeout (unless actively playing)
        this.hideTimeout = setTimeout(() => {
            if (this.state === VoiceState.Stopped && !this.isHovering) {
                this.statusBarItem.hide();
                this.log('Status bar auto-hidden (not hovering, stopped state)');
            }
        }, this.hoverTimeout);
    }
    cancelHideTimer() {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }
        // Show status bar when user interacts
        this.statusBarItem.show();
    }
    enableAutoHide(enabled) {
        this.autoHideEnabled = enabled;
        if (enabled) {
            this.setupAutoHide();
        }
        else {
            this.cancelHideTimer();
            this.statusBarItem.show();
        }
        this.log(`Auto-hide ${enabled ? 'enabled' : 'disabled'}`);
    }
    setAutoHideDelay(delay) {
        this.hoverTimeout = delay;
        this.log(`Auto-hide delay set to ${delay}ms`);
    }
    setupAutoSend() {
        // Load configuration
        const config = vscode.workspace.getConfiguration('cursorVoiceControls');
        this.autoSendEnabled = config.get('autoSend', true);
        this.pauseDuration = config.get('pauseDuration', 4000); // Default 4 seconds
        // Watch for configuration changes
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('cursorVoiceControls.autoSend')) {
                this.autoSendEnabled = config.get('autoSend', true);
                this.log(`Auto-send ${this.autoSendEnabled ? 'enabled' : 'disabled'}`);
            }
            if (e.affectsConfiguration('cursorVoiceControls.pauseDuration')) {
                this.pauseDuration = config.get('pauseDuration', 4000);
                this.log(`Auto-send pause duration set to ${this.pauseDuration}ms`);
            }
        });
    }
    enableAutoSend(enabled) {
        this.autoSendEnabled = enabled;
        if (!enabled) {
            this.cancelAutoSend();
        }
        this.log(`Auto-send ${enabled ? 'enabled' : 'disabled'}`);
    }
    setPauseDuration(duration) {
        // Clamp to 3-5 second range (3000-5000ms)
        this.pauseDuration = Math.max(3000, Math.min(5000, duration));
        this.log(`Auto-send pause duration set to ${this.pauseDuration}ms`);
    }
    startAutoSendTimer() {
        if (!this.autoSendEnabled || this.state !== VoiceState.Playing) {
            return;
        }
        // Clear existing timer
        this.cancelAutoSend();
        // Start new timer
        this.autoSendTimeout = setTimeout(() => {
            if (this.pendingText.trim().length > 0 && this.state === VoiceState.Playing) {
                this.log(`Auto-sending after ${this.pauseDuration}ms pause`);
                this.autoSend();
            }
        }, this.pauseDuration);
        this.log(`Auto-send timer started (${this.pauseDuration}ms)`);
    }
    cancelAutoSend() {
        if (this.autoSendTimeout) {
            clearTimeout(this.autoSendTimeout);
            this.autoSendTimeout = null;
        }
    }
    autoSend() {
        if (this.pendingText.trim().length === 0) {
            return;
        }
        this.log(`Auto-sending: ${this.pendingText.substring(0, 50)}...`);
        // Try to send the message to Cursor's chat
        try {
            // Attempt to send via Cursor's chat API
            // This may need to be adjusted based on Cursor's actual API
            vscode.commands.executeCommand('workbench.action.chat.send', this.pendingText);
            // Clear pending text
            this.pendingText = '';
            this.lastTranscriptionTime = 0;
            // Show notification
            vscode.window.showInformationMessage(`✅ Auto-sent (${this.pauseDuration}ms pause detected)`);
        }
        catch (error) {
            this.log(`Error auto-sending: ${error}`);
            // Fallback: try alternative method
            this.fallbackAutoSend();
        }
        this.cancelAutoSend();
    }
    fallbackAutoSend() {
        // Fallback method: simulate Enter key press in chat input
        // This is a workaround if direct API doesn't work
        this.log('Using fallback auto-send method');
        // Note: This would require access to the chat input, which may not be directly available
        // The actual implementation may need to be adjusted based on Cursor's architecture
    }
    /**
     * Monitor transcription for pauses and auto-send
     * Called when new transcription text is received
     */
    monitorTranscription(text) {
        if (!this.autoSendEnabled || this.state !== VoiceState.Playing) {
            return;
        }
        const now = Date.now();
        // Update pending text
        if (this.pendingText) {
            this.pendingText += ' ' + text;
        }
        else {
            this.pendingText = text;
        }
        // Update last transcription time
        this.lastTranscriptionTime = now;
        // Reset auto-send timer (new input detected)
        this.startAutoSendTimer();
        this.log(`Transcription monitored: "${text.substring(0, 30)}..." (pending: ${this.pendingText.length} chars)`);
    }
    /**
     * Cancel auto-send (if user is still thinking)
     */
    cancelAutoSendNow() {
        this.cancelAutoSend();
        this.pendingText = '';
        this.log('Auto-send cancelled by user');
        vscode.window.showInformationMessage('⏸ Auto-send cancelled');
    }
    updateStatusBar() {
        const icons = {
            [VoiceState.Stopped]: '⏹',
            [VoiceState.Playing]: '▶',
            [VoiceState.Paused]: '⏸'
        };
        const labels = {
            [VoiceState.Stopped]: 'Voice: Stopped',
            [VoiceState.Playing]: 'Voice: Playing',
            [VoiceState.Paused]: 'Voice: Paused (Muted)'
        };
        this.statusBarItem.text = `${icons[this.state]} ${labels[this.state]}`;
        this.statusBarItem.tooltip = `Click to toggle voice transcription\nCurrent state: ${this.state}`;
        this.statusBarItem.show();
    }
    log(message) {
        this.outputChannel.appendLine(`[${new Date().toISOString()}] ${message}`);
    }
    async play() {
        if (this.state === VoiceState.Playing) {
            vscode.window.showInformationMessage('Voice transcription is already playing');
            return;
        }
        this.state = VoiceState.Playing;
        this.updateStatusBar();
        this.cancelHideTimer(); // Show when active
        this.isMonitoring = true;
        this.pendingText = '';
        this.lastTranscriptionTime = Date.now();
        this.log('Voice transcription started/resumed (auto-send monitoring active)');
        // Try to activate Cursor's voice transcription
        try {
            // Send command to activate voice (if Cursor exposes this)
            await vscode.commands.executeCommand('workbench.action.chat.voice.start');
        }
        catch (error) {
            // If command doesn't exist, log and continue
            this.log(`Note: Direct voice activation command not available: ${error}`);
        }
        vscode.window.showInformationMessage(`▶ Voice transcription playing (auto-send: ${this.autoSendEnabled ? 'ON' : 'OFF'})`);
    }
    async pause() {
        if (this.state === VoiceState.Stopped) {
            vscode.window.showWarningMessage('Voice transcription is not active. Use Play first.');
            return;
        }
        if (this.state === VoiceState.Paused) {
            // Resume from pause
            return this.play();
        }
        this.state = VoiceState.Paused;
        this.updateStatusBar();
        this.log('Voice transcription paused (muted)');
        // Try to pause Cursor's voice transcription
        try {
            await vscode.commands.executeCommand('workbench.action.chat.voice.pause');
        }
        catch (error) {
            this.log(`Note: Direct voice pause command not available: ${error}`);
        }
        vscode.window.showInformationMessage('⏸ Voice transcription paused (muted)');
    }
    async stop() {
        if (this.state === VoiceState.Stopped) {
            vscode.window.showInformationMessage('Voice transcription is already stopped');
            return;
        }
        // Cancel auto-send before stopping
        this.cancelAutoSend();
        this.isMonitoring = false;
        this.pendingText = '';
        this.state = VoiceState.Stopped;
        this.updateStatusBar();
        this.log('Voice transcription stopped');
        // Start auto-hide timer when stopped
        this.startHideTimer();
        // Try to stop Cursor's voice transcription
        try {
            await vscode.commands.executeCommand('workbench.action.chat.voice.stop');
        }
        catch (error) {
            this.log(`Note: Direct voice stop command not available: ${error}`);
        }
        vscode.window.showInformationMessage('⏹ Voice transcription stopped');
    }
    async toggle() {
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
    /**
     * Skip Forward - Jump to next transcription segment or skip ahead
     * Function: Navigate to next sentence/segment in transcription history
     */
    async skipForward() {
        this.cancelHideTimer(); // Show when user interacts
        if (this.transcriptionHistory.length === 0) {
            vscode.window.showInformationMessage('No transcription history available');
            return;
        }
        if (this.currentSegmentIndex < this.transcriptionHistory.length - 1) {
            this.currentSegmentIndex++;
            const segment = this.transcriptionHistory[this.currentSegmentIndex];
            this.log(`Skipped forward to segment ${this.currentSegmentIndex + 1}/${this.transcriptionHistory.length}`);
            // Show current segment in editor or notification
            vscode.window.showInformationMessage(`⏩ Segment ${this.currentSegmentIndex + 1}: ${segment.text.substring(0, 50)}...`);
            // Try to navigate in chat/transcription view
            try {
                await vscode.commands.executeCommand('workbench.action.chat.nextMessage');
            }
            catch (error) {
                this.log(`Note: Next message command not available: ${error}`);
            }
        }
        else {
            vscode.window.showInformationMessage('⏩ Already at end of transcription');
        }
        // Restart hide timer after interaction
        this.startHideTimer();
    }
    /**
     * Skip Back - Jump to previous transcription segment or rewind
     * Function: Navigate to previous sentence/segment in transcription history
     */
    async skipBack() {
        this.cancelHideTimer(); // Show when user interacts
        if (this.transcriptionHistory.length === 0) {
            vscode.window.showInformationMessage('No transcription history available');
            return;
        }
        if (this.currentSegmentIndex > 0) {
            this.currentSegmentIndex--;
            const segment = this.transcriptionHistory[this.currentSegmentIndex];
            this.log(`Skipped back to segment ${this.currentSegmentIndex + 1}/${this.transcriptionHistory.length}`);
            // Show current segment
            vscode.window.showInformationMessage(`⏪ Segment ${this.currentSegmentIndex + 1}: ${segment.text.substring(0, 50)}...`);
            // Try to navigate in chat/transcription view
            try {
                await vscode.commands.executeCommand('workbench.action.chat.previousMessage');
            }
            catch (error) {
                this.log(`Note: Previous message command not available: ${error}`);
            }
        }
        else {
            vscode.window.showInformationMessage('⏪ Already at beginning of transcription');
        }
        // Restart hide timer after interaction
        this.startHideTimer();
    }
    /**
     * Fast Forward - Skip ahead more aggressively or increase playback speed
     * Function: Skip ahead by larger intervals (e.g., 10-30 seconds) or speed up playback
     */
    async fastForward() {
        if (this.state === VoiceState.Stopped) {
            vscode.window.showWarningMessage('Voice transcription is not active');
            return;
        }
        // Increase playback speed (if applicable)
        this.playbackSpeed = Math.min(this.playbackSpeed * 1.5, 4.0); // Max 4x speed
        this.log(`Fast forward: Playback speed increased to ${this.playbackSpeed.toFixed(1)}x`);
        // Skip ahead by larger interval
        const skipAmount = this.skipInterval * 2; // Double the skip interval
        this.log(`Fast forward: Skipping ahead ${skipAmount} seconds`);
        vscode.window.showInformationMessage(`⏩⏩ Fast forward: ${this.playbackSpeed.toFixed(1)}x speed, skipping ${skipAmount}s`);
        // Try to skip ahead in transcription
        try {
            // If there's a way to skip time in transcription, use it
            await vscode.commands.executeCommand('workbench.action.chat.skipForward', skipAmount);
        }
        catch (error) {
            this.log(`Note: Fast forward command not available: ${error}`);
        }
    }
    /**
     * Fast Rewind - Rewind more aggressively or decrease playback speed
     * Function: Go back by larger intervals (e.g., 10-30 seconds) or slow down playback
     */
    async fastRewind() {
        if (this.state === VoiceState.Stopped) {
            vscode.window.showWarningMessage('Voice transcription is not active');
            return;
        }
        // Decrease playback speed (if applicable)
        this.playbackSpeed = Math.max(this.playbackSpeed / 1.5, 0.25); // Min 0.25x speed
        this.log(`Fast rewind: Playback speed decreased to ${this.playbackSpeed.toFixed(1)}x`);
        // Skip back by larger interval
        const skipAmount = this.skipInterval * 2; // Double the skip interval
        this.log(`Fast rewind: Skipping back ${skipAmount} seconds`);
        vscode.window.showInformationMessage(`⏪⏪ Fast rewind: ${this.playbackSpeed.toFixed(1)}x speed, skipping back ${skipAmount}s`);
        // Try to skip back in transcription
        try {
            await vscode.commands.executeCommand('workbench.action.chat.skipBack', skipAmount);
        }
        catch (error) {
            this.log(`Note: Fast rewind command not available: ${error}`);
        }
    }
    /**
     * Add transcription segment to history
     */
    addTranscriptionSegment(text, timestamp) {
        const segment = {
            text,
            timestamp: timestamp || Date.now(),
            duration: undefined
        };
        this.transcriptionHistory.push(segment);
        this.currentSegmentIndex = this.transcriptionHistory.length - 1;
        this.log(`Added transcription segment: ${text.substring(0, 50)}...`);
        // Monitor for auto-send
        if (this.isMonitoring && this.state === VoiceState.Playing) {
            this.monitorTranscription(text);
        }
    }
    getState() {
        return this.state;
    }
    getPlaybackSpeed() {
        return this.playbackSpeed;
    }
    dispose() {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
        }
        if (this.autoSendTimeout) {
            clearTimeout(this.autoSendTimeout);
        }
        if (this.statusBarHoverDisposable) {
            this.statusBarHoverDisposable.dispose();
        }
        this.statusBarItem.dispose();
        this.outputChannel.dispose();
    }
}
let voiceControls;
function activate(context) {
    voiceControls = new VoiceControls();
    // Load configuration
    const config = vscode.workspace.getConfiguration('cursorVoiceControls');
    const autoHide = config.get('autoHide', true);
    const autoHideDelay = config.get('autoHideDelay', 2000);
    voiceControls.enableAutoHide(autoHide);
    if (autoHideDelay) {
        voiceControls.setAutoHideDelay(autoHideDelay);
    }
    // Watch for configuration changes
    vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('cursorVoiceControls.autoHide')) {
            const newAutoHide = config.get('autoHide', true);
            voiceControls.enableAutoHide(newAutoHide);
        }
        if (e.affectsConfiguration('cursorVoiceControls.autoHideDelay')) {
            const newDelay = config.get('autoHideDelay', 2000);
            voiceControls.setAutoHideDelay(newDelay);
        }
    });
    // Register commands
    const playCommand = vscode.commands.registerCommand('cursorVoiceControls.play', () => {
        voiceControls.play();
    });
    const pauseCommand = vscode.commands.registerCommand('cursorVoiceControls.pause', () => {
        voiceControls.pause();
    });
    const stopCommand = vscode.commands.registerCommand('cursorVoiceControls.stop', () => {
        voiceControls.stop();
    });
    const toggleCommand = vscode.commands.registerCommand('cursorVoiceControls.toggle', () => {
        voiceControls.toggle();
    });
    const skipForwardCommand = vscode.commands.registerCommand('cursorVoiceControls.skipForward', () => {
        voiceControls.skipForward();
    });
    const skipBackCommand = vscode.commands.registerCommand('cursorVoiceControls.skipBack', () => {
        voiceControls.skipBack();
    });
    const fastForwardCommand = vscode.commands.registerCommand('cursorVoiceControls.fastForward', () => {
        voiceControls.fastForward();
    });
    const fastRewindCommand = vscode.commands.registerCommand('cursorVoiceControls.fastRewind', () => {
        voiceControls.fastRewind();
    });
    const toggleAutoHideCommand = vscode.commands.registerCommand('cursorVoiceControls.toggleAutoHide', () => {
        const currentAutoHide = config.get('autoHide', true);
        config.update('autoHide', !currentAutoHide, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`Auto-hide ${!currentAutoHide ? 'enabled' : 'disabled'}`);
    });
    const toggleAutoSendCommand = vscode.commands.registerCommand('cursorVoiceControls.toggleAutoSend', () => {
        const currentAutoSend = config.get('autoSend', true);
        config.update('autoSend', !currentAutoSend, vscode.ConfigurationTarget.Global);
        voiceControls.enableAutoSend(!currentAutoSend);
        vscode.window.showInformationMessage(`Auto-send ${!currentAutoSend ? 'enabled' : 'disabled'}`);
    });
    const cancelAutoSendCommand = vscode.commands.registerCommand('cursorVoiceControls.cancelAutoSend', () => {
        voiceControls.cancelAutoSendNow();
    });
    context.subscriptions.push(playCommand, pauseCommand, stopCommand, toggleCommand, skipForwardCommand, skipBackCommand, fastForwardCommand, fastRewindCommand, toggleAutoHideCommand, toggleAutoSendCommand, cancelAutoSendCommand, voiceControls);
    vscode.window.showInformationMessage('Cursor Voice Controls activated - Use status bar or commands to control voice transcription');
}
exports.activate = activate;
function deactivate() {
    if (voiceControls) {
        voiceControls.dispose();
    }
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map