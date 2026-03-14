"""
CLI entry point for memory quality scoring.

Usage:
    python -m lumina.memory_score path/to/CLAUDE.md
    python -m lumina.memory_score path/to/memory/directory/
    python -m lumina.memory_score path/to/CLAUDE.md --format json
    python -m lumina.memory_score path/to/CLAUDE.md --format markdown
    python -m lumina.memory_score path/to/CLAUDE.md --verbose
    python -m lumina.memory_score path/to/CLAUDE.md --lumina
"""

import json
import os
import sys

from .scorer import MemoryScorer


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)

    target = args[0]
    fmt = "text"
    verbose = False

    # Parse flags
    for i, arg in enumerate(args[1:], 1):
        if arg == "--format" and i + 1 < len(args):
            fmt = args[i + 1]
        elif arg in ("--json", "-j"):
            fmt = "json"
        elif arg in ("--markdown", "--md", "-m"):
            fmt = "markdown"
        elif arg in ("--verbose", "-v", "--lumina"):
            verbose = True

    scorer = MemoryScorer()

    try:
        if os.path.isdir(target):
            report = scorer.score_directory(target)
        elif os.path.isfile(target):
            report = scorer.score_file(target)
        else:
            print(f"Error: {target} not found", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if fmt == "json":
        print(json.dumps(report.to_dict(), indent=2))
    elif fmt == "markdown":
        print(report.to_markdown())
    else:
        print(report.to_text(verbose=verbose))


if __name__ == "__main__":
    main()
