# Contributing to Lumina

Welcome! Lumina is an open-source AI agent framework born from real-world enterprise usage. We'd love your help.

## Code of Conduct

Be respectful, inclusive, and constructive. Check out [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.11+
- GitHub account
- Git

### Setup Development Environment

```bash
# Clone the repo
git clone https://github.com/your-username/lumina.git
cd lumina

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Project Structure

```
lumina/
├── config/                           # Configuration files
│   ├── ai_token_request_tracker.json
│   └── github_copilot_peak_patterns.json
├── scripts/python/                   # Reusable modules
│   ├── ai_request_tracker.py
│   ├── learner_system.py
│   └── aiq_triage_jedi.py
├── docs/
│   ├── ARCHITECTURE.md               # Design docs
│   ├── GETTING_STARTED.md            # Quick start
│   └── patterns/                     # Pattern documentation
├── examples/                         # Example usage
├── tests/                            # Test suite
└── .editorconfig, .gitignore, etc.
```

## How to Contribute

### 1. Check Issues & Discussions

Before starting work:

```bash
# Look for issues labeled:
# - good first issue
# - help wanted
# - feature request

# Or start a discussion if you have ideas
```

### 2. Fork & Branch

```bash
# Create your fork (GitHub UI)

# Clone your fork
git clone https://github.com/YOUR-USERNAME/lumina.git
cd lumina

# Create feature branch
git checkout -b feature/your-feature-name

# Or bugfix branch
git checkout -b fix/your-bugfix-name
```

### 3. Make Changes

Follow these guidelines:

#### Code Style

```python
# Use concise, idiomatic Python
# Reference patterns in docstrings
# Include tests with new code

"""
PUBLIC: Module Description
Location: lumina/scripts/python/example.py
License: MIT

Brief description of what this module does.
"""

def my_function(arg1: str, arg2: int) -> dict:
    """One-line description. Multi-line if needed."""
    pass
```

#### File Headers

All files must include PUBLIC header:

```python
# .py files
"""
PUBLIC: Open-Source Framework Module
Location: lumina/scripts/python/module.py
License: MIT / Apache 2.0
"""

# .json files
{
  "_public_marker": "PUBLIC - Open Source Template",
  "your_config": {...}
}

# .md files
# Lumina Pattern: Name
# Classification: 🟢 PUBLIC - Open-Source
```

#### Testing

```bash
# Write tests alongside code
pytest tests/test_my_feature.py -v

# Ensure 85%+ coverage
pytest --cov=lumina tests/

# Run linting
pylint lumina/
black --check lumina/
```

#### Documentation

```bash
# Update docs/ if you change functionality
# Keep examples current
# Add your feature to README.md (if user-facing)
```

### 4. Pre-Push Validation

Before pushing, run all checks:

```bash
# 1. Linting & formatting
black lumina/
pylint lumina/

# 2. Tests
pytest tests/

# 3. Type checking
mypy lumina/

# 4. Sanitization (no sensitive data)
python scripts/python/pre_push_sanitization.py

# 5. Coverage
pytest --cov=lumina --cov-report=html tests/
```

### 5. Commit Messages

Use conventional commits:

```
feat: Add new feature
fix: Fix the bug
docs: Update documentation
test: Add test coverage
refactor: Restructure code
chore: Maintenance tasks

Example:
feat: Add Master/Padawan learner integration

- Implements teaching workflow (0.5x tokens)
- Implements learning workflow (1.0x tokens)
- Adds session classification
- Refs #42
```

### 6. Create Pull Request

Push to your fork:

```bash
git push origin feature/your-feature-name
```

Go to GitHub → Create Pull Request

**PR Template** (auto-filled):

```markdown
## Description

What does this PR do?

## Type

- [ ] Feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Test improvement
- [ ] Refactoring

## How Has This Been Tested?

Describe tests you've added/run:
```bash
pytest tests/test_my_feature.py
```

## Checklist

- [ ] Code follows style guide (black, pylint)
- [ ] Tests pass (`pytest`)
- [ ] Coverage maintained (85%+)
- [ ] Documentation updated
- [ ] No sensitive data (security check)
- [ ] Commit messages are clear
- [ ] Related issues linked (#42)

```

### 7. Respond to Review

Maintainers will review your PR. Be responsive:

- Address feedback promptly
- Ask clarifying questions
- Push additional commits (don't force-push)
- Mark conversations as resolved when done

### 8. Merge!

Once approved, a maintainer will merge your PR. Your change is now part of Lumina!

---

## Types of Contributions We Need

### Code

- **Bug fixes** - Report with minimal reproduction
- **Performance improvements** - Include benchmarks
- **New features** - Discuss in issues first
- **Refactoring** - Improve readability/maintainability
- **Tests** - Increase coverage

### Documentation

- **Getting started guides** - Especially for beginners
- **Pattern examples** - Real-world usage
- **API documentation** - Clarify complex features
- **Troubleshooting** - Help users solve problems
- **Translations** - Make Lumina global

### Community

- **Answer questions** - Help in discussions
- **Report issues** - Detail, reproducibility, environment
- **Suggest improvements** - Use discussions
- **Share your pattern** - Tell us what works
- **Feedback** - What could be better?

---

## Development Workflow

### Local Testing

```bash
# Watch for changes (requires pytest-watch)
ptw -- --cov

# Test specific module
pytest tests/test_learner_system.py -v

# Test specific function
pytest tests/test_learner_system.py::test_log_learning_interaction -v
```

### Debugging

```bash
# Add breakpoint
import pdb; pdb.set_trace()

# Or use Python 3.7+ breakpoint()
breakpoint()  # Will drop into debugger

# Run with debugging
pytest --pdb tests/test_my_feature.py
```

### Coverage

```bash
# View coverage report
pytest --cov=lumina --cov-report=html tests/
open htmlcov/index.html  # View in browser
```

---

## Submitting an Issue

### Bug Report

```markdown
## Description
Brief description of the bug

## Reproduction Steps
1. ...
2. ...
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happened

## Environment
- Python: 3.11
- OS: Windows/Mac/Linux
- Lumina version: v2.0

## Logs
```

Error message here

```
```

### Feature Request

```markdown
## Problem
What problem does this solve?

## Proposed Solution
How should it work?

## Alternative Solutions
Other approaches considered?

## Use Case
Who would benefit and why?
```

---

## Becoming a Maintainer

We're looking for active contributors to help maintain Lumina:

- **3+ months** active contribution
- **5+ PRs** merged
- **Clear communication** & helpfulness
- **Interest in long-term involvement**

Talk to us in discussions if interested!

---

## Code Ownership & Recognition

### Attribution

Your contributions will be:

- ✅ Listed in CONTRIBUTORS.md
- ✅ Credited in release notes
- ✅ Visible in GitHub commit history
- ✅ Part of the community story

### Licensing

By contributing, you agree your code will be:

- Licensed under MIT / Apache 2.0 (as specified in LICENSE)
- Available for educational use
- Usable by the open-source community

### Trademarks

"Lumina" is a trademark of [Your Organization]. Usage is permitted for the open-source project.

---

## Getting Help

### Documentation

- [README.md](README.md) - Project overview
- [GETTING_STARTED.md](docs/GETTING_STARTED.md) - Quick start
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Design deep dive
- [API Docs](docs/api/) - Module reference

### Community

- **GitHub Discussions** - Ask questions, share patterns
- **GitHub Issues** - Report bugs, request features
- **Email** - [contact email if applicable]

### Office Hours (Planned)

Weekly community calls - check Discussions for schedule

---

## FAQ

**Q: I found a security issue. How do I report it?**

A: Please email security@[domain] instead of opening a public issue. We'll handle it promptly.

**Q: Can I submit a pattern from my own project?**

A: Yes! Share in discussions first. If it fits the Lumina philosophy, we'll help integrate it.

**Q: What if my contribution doesn't get merged?**

A: We value all contributions. If a PR isn't accepted, we'll explain why and suggest next steps. You can always use the code in your own fork.

**Q: How long does review take?**

A: Typically 3-7 days. We try to be responsive. Feel free to ping if it's been longer.

**Q: Do I get paid to contribute?**

A: Lumina is volunteer-driven. Contributions are appreciated! If you're interested in paid work, mention in discussions.

---

## Code of Conduct

By participating, you agree to our Code of Conduct:

- Be respectful of all contributors
- Avoid harassment, discrimination, or trolling
- Provide constructive feedback
- Report violations to [contact info]

---

## License

All contributions to Lumina are licensed under MIT / Apache 2.0. By submitting a PR, you agree to this licensing.

---

## Thank You

Thank you for contributing to Lumina. You're helping build the future of AI agent frameworks. 🚀

**Happy contributing!**
