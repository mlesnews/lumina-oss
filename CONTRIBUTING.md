# Contributing to Lumina AIOS

## Getting Started

```bash
git clone https://github.com/mlesnews/lumina-oss.git
cd lumina-oss
pip install -e ".[dev]"
pytest tests/ -v
```

**Requirements:** Python 3.10+, Git. No other dependencies.

## Making Changes

1. Fork the repo and create a branch: `git checkout -b feat/your-feature`
2. Write code + tests (maintain 67+ tests passing)
3. Run tests: `pytest tests/ -v`
4. Commit with conventional format: `feat: Add X` / `fix: Fix Y`
5. Open a PR

## Code Style

- Python 3.10+ type hints
- Stdlib only — no pip dependencies in the core `lumina/` package
- Every module has a docstring with usage example
- Tests in `tests/` with `test_` prefix

## What We Need

- **Bug fixes** with reproduction steps
- **New safety/workflow primitives** that follow existing patterns
- **Claude Code hooks** for the `claude_code_hooks/` collection
- **Examples** in `examples/`
- **Documentation** improvements

## License

By contributing, you agree your code is licensed under MIT (see [LICENSE](LICENSE)).
