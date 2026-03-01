# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes                |
| < 0.1   | No                 |

## Reporting a Vulnerability

**Do NOT open a public issue for security vulnerabilities.**

Instead, please report security issues via one of these channels:

1. **GitHub Security Advisory:** Use the [Report a vulnerability](https://github.com/mlesnews/lumina-oss/security/advisories/new) feature
2. **Email:** mlesnews@users.noreply.github.com

### What to include

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Potential impact

### Response timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix or mitigation:** Within 30 days for confirmed vulnerabilities

### Scope

This policy covers the `lumina-aios` Python package and all code in this repository, including:

- Core framework (`lumina/`)
- Claude Code hooks (`claude_code_hooks/`)
- Examples (`examples/`)
- CI/CD configurations (`.github/`)

### Out of scope

- The private `lumina-premium` repository (separate security policy)
- Third-party dependencies (report to their maintainers)
- Social engineering or phishing attacks

## Security Design

Lumina AIOS is designed with security as a core principle:

- **Zero dependencies** — no supply chain attack surface in the core package
- **Secret scanner** (`lumina.safety.secret_scanner`) — detects API keys, tokens, and private keys in code and output
- **COMPUSEC guard** (`claude_code_hooks/compusec_guard.py`) — blocks secret exposure in Claude Code tool calls
- **Secrets redactor** (`claude_code_hooks/secrets_redactor.py`) — post-execution output scrubbing
- **CI secret scanning** — TruffleHog + custom Iron Curtain patterns on every push

## Acknowledgments

We appreciate responsible disclosure and will credit reporters (with permission) in release notes.
