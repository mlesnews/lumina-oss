# Lumina Core – Kilo Code defaults

This folder is bundled with the **Lumina Core** extension and provides default Kilo Code rules so workspaces get security-by-default when using Kilo Code with Lumina.

## Contents

- **`rules/no_secrets_broadcast.md`** – Full policy: never print, log, or expose API keys, passwords, tokens, or account names in generated code.
- **`rules/secrets.md`** – Short summary and pointer to the full rule.

## Applying to your workspace

1. **Command palette**: **Ctrl+Shift+P** → **Lumina: Apply Kilo Code Setup**
2. The extension copies these rules into your workspace `.kilocode/rules/` (only if files don’t already exist, so your customizations are preserved).

## Kilo Code + Ultron (Ollama)

For connectivity (base URL, context window, spinning fixes), see your repo’s `docs/system/KILO_CODE_ULTRON_CONNECTIVITY.md` if present, or Kilo Code docs: <https://kilo.ai/docs/providers/ollama>.

**Maintained By**: @LUMINA
