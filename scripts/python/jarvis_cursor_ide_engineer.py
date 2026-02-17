#!/usr/bin/env python3
"""
JARVIS Cursor IDE Engineer

Optimizes Cursor IDE configuration and usage to reach peak potential.
Analyzes current setup, identifies gaps, and implements best practices.

Tags: #CURSOR-IDE #PRODUCTIVITY #ENGINEERING @CURSOR-ENGINEER
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorIDE")


class JARVISCursorIDEEngineer:
    """
    JARVIS Cursor IDE Engineer

    Optimizes Cursor IDE for peak performance and productivity.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.cursor_dir = project_root / ".cursor"
        self.config_dir = project_root / "config"
        self.cursor_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ JARVIS Cursor IDE Engineer initialized")

    def analyze_current_setup(self) -> Dict[str, Any]:
        """Analyze current Cursor IDE setup"""
        self.logger.info("🔍 Analyzing current Cursor IDE setup...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "settings_file": str(self.cursor_dir / "settings.json"),
            "settings_exists": (self.cursor_dir / "settings.json").exists(),
            "mcp_config_exists": (self.cursor_dir / "mcp_config.json").exists(),
            "cursorrules_exists": (self.project_root / ".cursorrules").exists(),
            "keybindings_exists": (self.cursor_dir / "keybindings.json").exists(),
            "features": {
                "chat": True,  # Always available
                "composer": True,  # Always available
                "agent": True,  # Always available
                "inline_completion": True,
                "codebase_indexing": True,
                "refactoring": True,
                "test_generation": True
            },
            "models_configured": 0,
            "gitlens_configured": False,
            "missing_features": [],
            "optimization_opportunities": []
        }

        # Check settings.json
        if analysis["settings_exists"]:
            try:
                with open(self.cursor_dir / "settings.json", 'r') as f:
                    settings = json.load(f)

                    # Count models
                    if "cursor.chat.customModels" in settings:
                        analysis["models_configured"] += len(settings["cursor.chat.customModels"])
                    if "cursor.composer.customModels" in settings:
                        analysis["models_configured"] += len(settings["cursor.composer.customModels"])
                    if "cursor.agent.customModels" in settings:
                        analysis["models_configured"] += len(settings["cursor.agent.customModels"])

                    # Check GitLens
                    analysis["gitlens_configured"] = "gitlens.autolinks" in settings
            except Exception as e:
                self.logger.warning(f"⚠️  Error reading settings.json: {e}")

        # Check for missing features
        if not analysis["cursorrules_exists"]:
            analysis["missing_features"].append(".cursorrules file for project-specific rules")

        if not analysis["keybindings_exists"]:
            analysis["missing_features"].append("Custom keybindings.json for productivity shortcuts")

        # Optimization opportunities
        analysis["optimization_opportunities"] = [
            "Create .cursorrules file for LUMINA-specific coding standards",
            "Configure custom keybindings for common workflows",
            "Enable advanced Composer features (multi-file editing)",
            "Optimize Agent settings for autonomous coding",
            "Configure codebase indexing for faster context",
            "Set up refactoring preferences",
            "Enable test generation features",
            "Configure inline completion preferences",
            "Set up workspace-specific settings",
            "Enable advanced debugging features"
        ]

        return analysis

    def create_cursorrules(self) -> Dict[str, Any]:
        """Create .cursorrules file for LUMINA project"""
        self.logger.info("📝 Creating .cursorrules file for LUMINA...")

        cursorrules_content = """# LUMINA Project Rules for Cursor IDE

## Project Context
- Project: LUMINA - AI-Powered Development Ecosystem
- Primary Language: Python 3.11+
- Framework: Custom JARVIS/MANUS/MARVIN ecosystem
- Architecture: Local-first AI, ULTRON cluster, KAIJU NAS integration

## Code Standards

### Python
- Always use type hints (typing module)
- Follow PEP 8 style guide
- Use f-strings for string formatting
- Prefer pathlib.Path over os.path
- Use dataclasses for data structures
- Always include docstrings (Google style)
- Use logging.getLogger() for logging
- Never use print() for production code (use logger)

### Error Handling
- Always use try/except with specific exceptions
- Log errors with context (exc_info=True)
- Return structured error responses (Dict[str, Any])
- Never silently swallow exceptions

### Imports
- Group imports: stdlib, third-party, local
- Use absolute imports for project modules
- Add project root to sys.path when needed
- Handle ImportError gracefully with fallbacks

### File Structure
- Scripts in scripts/python/
- Config in config/
- Data in data/
- Docs in docs/
- Tests in tests/ (when created)

### Naming Conventions
- Classes: PascalCase (e.g., JARVISSystem)
- Functions/Methods: snake_case (e.g., get_system_status)
- Constants: UPPER_SNAKE_CASE (e.g., MAX_RETRIES)
- Files: snake_case (e.g., jarvis_system.py)
- Private: _leading_underscore

### Documentation
- Always include module docstrings
- Document all public functions/classes
- Include usage examples in docstrings
- Tag with relevant tags (e.g., #JARVIS, @TEAM)

### Git Integration
- Commit messages: [CATEGORY] Description
- Categories: FEATURE, FIX, CONFIG, DOCS, REFACTOR, TEST
- Reference issues: #123, JARVIS-100, LUMINA-50

### LUMINA-Specific
- Always check for local-first AI (ULTRON/KAIJU)
- Use JARVIS systems for automation
- Integrate with MANUS for control
- Use MARVIN for reality checks
- Tag with @AIQ for consensus decisions
- Use #JEDI-COUNCIL for critical approvals

### Testing (When Implemented)
- Unit tests for all modules
- Integration tests for workflows
- Use pytest framework
- Mock external dependencies
- Test error handling paths

### Performance
- Use async/await for I/O operations
- Cache expensive operations
- Batch operations when possible
- Monitor resource usage
- Optimize for local-first (ULTRON/KAIJU)

### Security
- Never hardcode credentials
- Use Azure Key Vault for secrets
- Validate all inputs
- Sanitize file paths
- Use secure defaults

## AI Assistant Guidelines

### When Using Cursor Chat/Composer/Agent:
- Always consider existing codebase patterns
- Check for similar implementations before creating new ones
- Use existing utilities and helpers
- Follow established architecture patterns
- Integrate with existing systems (JARVIS, MANUS, MARVIN)
- Consider local-first AI routing (ULTRON/KAIJU)
- Tag code appropriately (#JARVIS, @TEAM, etc.)

### Code Generation:
- Generate complete, working code
- Include error handling
- Add logging
- Include type hints
- Add docstrings
- Follow project structure

### Refactoring:
- Maintain backward compatibility
- Update all related code
- Update documentation
- Test thoroughly
- Consider impact on integrations

## Project-Specific Patterns

### JARVIS Systems:
- Use JARVIS prefix for JARVIS-related modules
- Initialize with project_root: Path
- Use lumina_logger for logging
- Return Dict[str, Any] for structured responses
- Include CLI interface (main() function)

### MANUS Integration:
- Use MANUSUnifiedControl for automation
- ControlArea enum for control areas
- Use ControlOperation for operations
- Return OperationResult for results

### Database:
- Use enhanced_memory.db for persistent storage
- Use SQLite for local storage
- Use NAS for backups
- Always use transactions
- Include error handling

### Network:
- Use NASAzureVaultIntegration for NAS credentials
- Check connectivity before operations
- Handle timeouts gracefully
- Log network operations

## Anti-Patterns (Never Do)

- Don't create duplicate functionality
- Don't ignore existing utilities
- Don't hardcode paths (use project_root)
- Don't skip error handling
- Don't use cloud APIs when local available
- Don't commit without proper messages
- Don't skip documentation
- Don't ignore linting errors
- Don't create circular dependencies
- Don't bypass security measures
"""

        cursorrules_path = self.project_root / ".cursorrules"
        try:
            with open(cursorrules_path, 'w', encoding='utf-8') as f:
                f.write(cursorrules_content)
            self.logger.info(f"✅ Created .cursorrules at {cursorrules_path}")
            return {"success": True, "path": str(cursorrules_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create .cursorrules: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def create_keybindings(self) -> Dict[str, Any]:
        """Create custom keybindings for Cursor IDE"""
        self.logger.info("⌨️  Creating custom keybindings for Cursor IDE...")

        keybindings = [
            {
                "key": "ctrl+k ctrl+j",
                "command": "cursor.chat.focus",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+c",
                "command": "cursor.composer.open",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+a",
                "command": "cursor.agent.start",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+shift+j",
                "command": "cursor.chat.new",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+r",
                "command": "cursor.refactor",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+t",
                "command": "cursor.test.generate",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+i",
                "command": "cursor.index.codebase",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+s",
                "command": "cursor.summarize",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+d",
                "command": "cursor.debug.explain",
                "when": "editorTextFocus"
            },
            {
                "key": "ctrl+k ctrl+e",
                "command": "cursor.edit.inline",
                "when": "editorTextFocus"
            }
        ]

        keybindings_path = self.cursor_dir / "keybindings.json"
        try:
            with open(keybindings_path, 'w', encoding='utf-8') as f:
                json.dump(keybindings, f, indent=2)
            self.logger.info(f"✅ Created keybindings.json at {keybindings_path}")
            return {"success": True, "path": str(keybindings_path), "keybindings": len(keybindings)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create keybindings.json: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def optimize_settings(self) -> Dict[str, Any]:
        """Optimize Cursor IDE settings"""
        self.logger.info("⚙️  Optimizing Cursor IDE settings...")

        settings_path = self.cursor_dir / "settings.json"
        if not settings_path.exists():
            return {"success": False, "error": "settings.json not found"}

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Add optimized settings
            optimizations = {
                "cursor.chat.enabled": True,
                "cursor.chat.autoFocus": True,
                "cursor.chat.maxHistory": 100,
                "cursor.chat.contextWindow": 32768,
                "cursor.composer.enabled": True,
                "cursor.composer.autoApply": False,
                "cursor.composer.maxFiles": 50,
                "cursor.composer.contextWindow": 32768,
                "cursor.agent.enabled": True,
                "cursor.agent.autoStart": False,
                "cursor.agent.maxSteps": 50,
                "cursor.agent.contextWindow": 32768,
                "cursor.inlineCompletion.enabled": True,
                "cursor.inlineCompletion.delay": 100,
                "cursor.inlineCompletion.maxSuggestions": 5,
                "cursor.codebaseIndexing.enabled": True,
                "cursor.codebaseIndexing.autoIndex": True,
                "cursor.codebaseIndexing.maxFiles": 10000,
                "cursor.refactoring.enabled": True,
                "cursor.refactoring.autoSuggest": True,
                "cursor.testGeneration.enabled": True,
                "cursor.testGeneration.framework": "pytest",
                "cursor.debugging.enabled": True,
                "cursor.debugging.autoExplain": True,
                "cursor.summarization.enabled": True,
                "cursor.summarization.autoTrigger": True,
                "cursor.summarization.threshold": 10000,
                "editor.inlineSuggest.enabled": True,
                "editor.inlineSuggest.showToolbar": "always",
                "editor.suggestSelection": "first",
                "editor.wordBasedSuggestions": "off",
                "editor.quickSuggestions": {
                    "other": True,
                    "comments": False,
                    "strings": False
                },
                "editor.suggestOnTriggerCharacters": True,
                "editor.acceptSuggestionOnCommitCharacter": True,
                "editor.tabCompletion": "on",
                "editor.formatOnSave": True,
                "editor.formatOnPaste": False,
                "editor.codeActionsOnSave": {
                    "source.fixAll": "explicit",
                    "source.organizeImports": "explicit"
                },
                "files.autoSave": "afterDelay",
                "files.autoSaveDelay": 1000,
                "files.watcherExclude": {
                    "**/.git/objects/**": True,
                    "**/.git/subtree-cache/**": True,
                    "**/node_modules/**": True,
                    "**/__pycache__/**": True,
                    "**/.pytest_cache/**": True,
                    "**/.venv/**": True
                },
                "search.exclude": {
                    "**/node_modules": True,
                    "**/__pycache__": True,
                    "**/.pytest_cache": True,
                    "**/.venv": True,
                    "**/.git": False
                },
                "python.analysis.typeCheckingMode": "basic",
                "python.analysis.autoImportCompletions": True,
                "python.analysis.diagnosticMode": "workspace",
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": False,
                "python.linting.flake8Enabled": True,
                "python.formatting.provider": "black",
                "python.testing.pytestEnabled": True,
                "python.testing.unittestEnabled": False
            }

            # Merge optimizations
            for key, value in optimizations.items():
                settings[key] = value

            # Write back
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Optimized settings.json with {len(optimizations)} settings")
            return {"success": True, "optimizations": len(optimizations)}

        except Exception as e:
            self.logger.error(f"❌ Failed to optimize settings: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def create_optimization_guide(self) -> Dict[str, Any]:
        """Create comprehensive optimization guide"""
        self.logger.info("📚 Creating Cursor IDE optimization guide...")

        guide_content = """# Cursor IDE Peak Performance Guide for LUMINA

## 🎯 Overview

This guide helps you reach peak potential with Cursor IDE in the LUMINA project.

## 🚀 Quick Start

### Essential Shortcuts:
- `Ctrl+K Ctrl+J` - Focus Chat
- `Ctrl+K Ctrl+C` - Open Composer
- `Ctrl+K Ctrl+A` - Start Agent
- `Ctrl+Shift+J` - New Chat
- `Ctrl+K Ctrl+R` - Refactor
- `Ctrl+K Ctrl+T` - Generate Tests
- `Ctrl+K Ctrl+I` - Index Codebase
- `Ctrl+K Ctrl+S` - Summarize
- `Ctrl+K Ctrl+D` - Debug Explain
- `Ctrl+K Ctrl+E` - Inline Edit

## 💡 Best Practices

### 1. Use Chat for Questions
- Ask about codebase structure
- Get explanations
- Request code examples
- Debug issues

### 2. Use Composer for Multi-File Changes
- Refactor across files
- Add features spanning multiple files
- Update related code together
- Generate comprehensive changes

### 3. Use Agent for Autonomous Tasks
- Complex refactoring
- Feature implementation
- Bug fixes across codebase
- Code generation with context

### 4. Leverage Inline Completion
- Let Cursor suggest as you type
- Accept suggestions with Tab
- Use Ctrl+→ to accept word-by-word
- Use Ctrl+Enter for multi-line

### 5. Codebase Indexing
- Index entire codebase for better context
- Update index regularly
- Use indexed context in Chat/Composer/Agent

## 🎨 Advanced Features

### Codebase Indexing
- Automatically indexes your codebase
- Provides better context to AI
- Faster code suggestions
- Better refactoring suggestions

### Refactoring
- Right-click → Refactor
- Or use `Ctrl+K Ctrl+R`
- AI suggests improvements
- Applies changes safely

### Test Generation
- Right-click → Generate Tests
- Or use `Ctrl+K Ctrl+T`
- Generates pytest tests
- Follows project patterns

### Summarization
- Automatically summarizes long conversations
- Use `Ctrl+K Ctrl+S` to manually trigger
- Keeps context window manageable
- Preserves important information

### Debugging
- Use `Ctrl+K Ctrl+D` to explain code
- Get AI explanations of complex logic
- Understand error messages
- Debug with AI assistance

## 🔧 Configuration

### Models
- **ULTRON Cluster**: Primary model (32K context)
- **ULTRON Router**: Smart routing (32K context)
- **KAIJU Iron Legion**: Fallback (8K context)

### Context Window
- Chat: 32,768 tokens
- Composer: 32,768 tokens
- Agent: 32,768 tokens

### Auto-Save
- Enabled with 1s delay
- Prevents data loss
- Auto-commits via JARVIS

### Formatting
- Format on save: Enabled
- Provider: Black (Python)
- Organize imports: Enabled
- Fix all: Enabled

## 📋 Workflow Tips

### 1. Start with Chat
- Ask questions first
- Understand requirements
- Get code examples
- Plan approach

### 2. Use Composer for Implementation
- Create multi-file changes
- Ensure consistency
- Test as you go
- Review before applying

### 3. Use Agent for Complex Tasks
- Let Agent work autonomously
- Monitor progress
- Review changes
- Iterate as needed

### 4. Leverage Inline Completion
- Type naturally
- Accept helpful suggestions
- Learn from patterns
- Build muscle memory

### 5. Regular Maintenance
- Update codebase index
- Summarize long conversations
- Clean up old chats
- Review and optimize

## 🎯 LUMINA-Specific

### Project Rules
- See `.cursorrules` for project-specific rules
- Follow LUMINA coding standards
- Use JARVIS/MANUS/MARVIN patterns
- Tag appropriately (#JARVIS, @TEAM)

### Integration
- JARVIS for automation
- MANUS for control
- MARVIN for reality checks
- ULTRON/KAIJU for AI

### Git Integration
- Auto-commit via JARVIS
- Proper commit messages
- Reference issues
- Follow conventions

## 🚨 Common Mistakes to Avoid

1. **Don't ignore inline suggestions** - They're often helpful
2. **Don't skip codebase indexing** - Better context = better code
3. **Don't forget to summarize** - Keeps context manageable
4. **Don't ignore refactoring suggestions** - They improve code quality
5. **Don't skip testing** - Use test generation features
6. **Don't work in isolation** - Use Chat to understand codebase
7. **Don't ignore .cursorrules** - They guide AI behavior
8. **Don't skip formatting** - Format on save is your friend

## 📊 Performance Tips

1. **Index codebase regularly** - Better context
2. **Use local models (ULTRON/KAIJU)** - Faster responses
3. **Summarize long chats** - Manage context window
4. **Close unused files** - Reduce context size
5. **Use Composer for multi-file** - More efficient
6. **Leverage Agent for complex tasks** - Autonomous work
7. **Accept inline suggestions** - Faster coding
8. **Use shortcuts** - Muscle memory

## 🎓 Learning Resources

- Cursor IDE Documentation
- LUMINA Project Documentation
- `.cursorrules` file
- This guide
- Community resources

## ✅ Checklist

- [ ] Read `.cursorrules` file
- [ ] Learn keyboard shortcuts
- [ ] Configure models (ULTRON/KAIJU)
- [ ] Enable codebase indexing
- [ ] Set up auto-save
- [ ] Configure formatting
- [ ] Practice with Chat
- [ ] Try Composer
- [ ] Experiment with Agent
- [ ] Use inline completion
- [ ] Generate tests
- [ ] Try refactoring
- [ ] Use summarization
- [ ] Debug with AI

---

**Remember**: Cursor IDE is a powerful tool. The more you use it, the better it gets at understanding your codebase and helping you code faster and better.

**Peak Potential**: Use all features together - Chat for understanding, Composer for multi-file changes, Agent for autonomous work, and inline completion for speed.
"""

        guide_path = self.project_root / "CURSOR_IDE_PEAK_PERFORMANCE_GUIDE.md"
        try:
            with open(guide_path, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            self.logger.info(f"✅ Created optimization guide at {guide_path}")
            return {"success": True, "path": str(guide_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create guide: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def full_optimization(self) -> Dict[str, Any]:
        """Perform full Cursor IDE optimization"""
        self.logger.info("🚀 Performing full Cursor IDE optimization...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "analysis": self.analyze_current_setup(),
            "cursorrules": self.create_cursorrules(),
            "keybindings": self.create_keybindings(),
            "settings": self.optimize_settings(),
            "guide": self.create_optimization_guide()
        }

        # Summary
        results["summary"] = {
            "cursorrules_created": results["cursorrules"]["success"],
            "keybindings_created": results["keybindings"]["success"],
            "settings_optimized": results["settings"]["success"],
            "guide_created": results["guide"]["success"],
            "total_optimizations": sum([
                results["cursorrules"]["success"],
                results["keybindings"]["success"],
                results["settings"]["success"],
                results["guide"]["success"]
            ])
        }

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor IDE Engineer")
        parser.add_argument("--analyze", action="store_true", help="Analyze current setup")
        parser.add_argument("--optimize", action="store_true", help="Perform full optimization")
        parser.add_argument("--cursorrules", action="store_true", help="Create .cursorrules file")
        parser.add_argument("--keybindings", action="store_true", help="Create keybindings.json")
        parser.add_argument("--settings", action="store_true", help="Optimize settings.json")
        parser.add_argument("--guide", action="store_true", help="Create optimization guide")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        engineer = JARVISCursorIDEEngineer(project_root)

        if args.analyze:
            result = engineer.analyze_current_setup()
            print(json.dumps(result, indent=2, default=str))

        elif args.cursorrules:
            result = engineer.create_cursorrules()
            print(json.dumps(result, indent=2, default=str))

        elif args.keybindings:
            result = engineer.create_keybindings()
            print(json.dumps(result, indent=2, default=str))

        elif args.settings:
            result = engineer.optimize_settings()
            print(json.dumps(result, indent=2, default=str))

        elif args.guide:
            result = engineer.create_optimization_guide()
            print(json.dumps(result, indent=2, default=str))

        elif args.optimize:
            result = engineer.full_optimization()
            print(json.dumps(result, indent=2, default=str))

        else:
            # Default: full optimization
            result = engineer.full_optimization()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()