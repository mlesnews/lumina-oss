# Memory Quality Scorer

`lumina.memory_score` is a 10-dimension grader for AI memory files (`MEMORY.md`,
`CLAUDE.md`, `.cursorrules`, `copilot-instructions.md`, `.aider.conf.yml`,
`.windsurfrules`, etc.).

It is built on the framework's own `HealthAggregator` — the framework eats its
own cooking. Zero external dependencies, stdlib only.

## What It Does

Given a memory file or a directory of memory files, the scorer:

1. Parses the file(s) and extracts structural and content metrics.
2. Runs 10 dimension analyzers in parallel, each returning a `(score, detail)`
   tuple where score is in `[0.0, 1.0]`.
3. Feeds those scores into a weighted `HealthAggregator` and produces an
   overall `0–100` score, a letter grade, a lifecycle stage, and a
   recommendation.

Output formats: human-readable text report, Markdown report card, or JSON.

## CLI Usage

```bash
# Score a single file
python -m lumina.memory_score path/to/CLAUDE.md

# Score an entire memory directory (uses MEMORY.md or CLAUDE.md as primary)
python -m lumina.memory_score path/to/memory/

# Output formats
python -m lumina.memory_score CLAUDE.md --format json
python -m lumina.memory_score CLAUDE.md --markdown
python -m lumina.memory_score CLAUDE.md --verbose      # adds lifecycle line
python -m lumina.memory_score CLAUDE.md --lumina       # same as --verbose
```

Short flags: `-j` for JSON, `-m` for Markdown, `-v` for verbose.

## Programmatic Usage

```python
from lumina.memory_score import score_memory_file, score_memory_directory

report = score_memory_file("CLAUDE.md")
print(f"Grade: {report.grade} ({report.score_pct:.1f}/100)")
print(report.to_text())

# Or for a directory:
report = score_memory_directory("./memory/")
print(report.to_markdown())
```

Custom dimension weights:

```python
from lumina.memory_score import MemoryScorer

scorer = MemoryScorer(weights={
    "structure": 0.10,
    "completeness": 0.15,
    "conciseness": 0.10,
    "freshness": 0.05,
    "modularity": 0.10,
    "cross_referencing": 0.10,
    "actionability": 0.20,
    "coverage": 0.10,
    "platform_compliance": 0.05,
    "meta_awareness": 0.05,
})  # weights must sum to 1.0
report = scorer.score_file("CLAUDE.md")
```

`report.to_dict()` gives a JSON-serializable dict with grade, score, per-dimension
breakdown, lifecycle stage, and recommendation.

## The 10 Dimensions

| # | Dimension | Default Weight | What It Measures |
|---|-----------|---------------:|------------------|
| 1 | `structure` | 12% | Frontmatter, heading hierarchy, tables, code blocks |
| 2 | `completeness` | 12% | Coverage of the 15 canonical memory domains (identity, tools, workflows, conventions, environment, security, architecture, agents, rules, memory, testing, deployment, monitoring, communication, roadmap) |
| 3 | `conciseness` | 10% | File size discipline vs. platform line limits (200 lines for `MEMORY.md`, 150 for topic files, 500 for `CLAUDE.md`) |
| 4 | `freshness` | 8% | Recency signals — "last updated" markers, version stamps, dated entries |
| 5 | `modularity` | 12% | Index-plus-topic-files pattern vs. a single mega-file; ratio of topic files to index entries |
| 6 | `cross_referencing` | 8% | Density of `#TAGS`, `@AGENT` refs, file backlinks, explicit "See also:" / "Connects to:" pointers |
| 7 | `actionability` | **15%** | Density of imperative rules — "never / always / must / do not / ensure / verify" — versus passive prose |
| 8 | `coverage` | 8% | Breadth across topic areas when scoring a directory (how many domains have dedicated files) |
| 9 | `platform_compliance` | 7% | Respects platform conventions (line limits, no embedded secrets, valid frontmatter where required) |
| 10 | `meta_awareness` | 8% | Self-references — does the memory know it's memory? Mentions of audits, lifecycle, deprecation, line limits, hooks, schedules |

Actionability is the heaviest dimension by design: a memory file that doesn't
tell the AI *what to do* is decoration, not memory.

### Freshness Scoring

The `freshness` dimension is intentionally runtime-relative. `parser.py`
extracts unique `20xx-xx-xx` date strings, picks the most recent date, and
`score_freshness` compares it with `datetime.date.today()` using real calendar
days.

| Most recent date age | Freshness score |
|---------------------:|----------------:|
| 0-1 days | 1.00 |
| 2-7 days | 0.90 |
| 8-14 days | 0.75 |
| 15-30 days | 0.60 |
| 31-90 days | 0.40 |
| 91+ days | 0.20 |
| No dates or invalid selected date | 0.30 |

Operational constraints:

- Dates must be present as valid `YYYY-MM-DD` strings beginning with `20`; the
  parser does not read natural-language dates or file modification times.
- Directory scoring uses the primary `MEMORY.md` or `CLAUDE.md` file for the
  freshness dimension, even though other dimensions can inspect satellite files.
- Freshness naturally decays as time passes. If a memory file is still accurate,
  update its visible "Last updated" marker rather than changing scorer weights.

## Grading

The aggregator maps the weighted score (0–100) to one of five labels and an
Illithid lifecycle stage:

| Score | Grade | Label | Lifecycle Stage |
|------:|:-----:|-------|-----------------|
| 90–100 | A | `A_EXEMPLARY` | Elder Brain — exemplary, fully self-aware aggregate consciousness |
| 80–89 | B | `B_HEALTHY` | Ulitharid — advanced, cross-referenced, actionable, pattern-generating |
| 65–79 | C | `C_ADEQUATE` | Illithid — functional, indexed and structured but lacks depth |
| 50–64 | D | `D_DEGRADED` | Tadpole — immature, needs frontmatter and indexing |
| 0–49  | F | `F_CRITICAL` | Tadpole — raw, unstructured, orphaned |

The "Illithid lifecycle" naming is an internal flavor choice; the underlying
math is just weighted dimension scoring through `HealthAggregator`.

## Architecture

```
lumina/memory_score/
  __init__.py        # public API (score_memory_file, score_memory_directory, MemoryScorer)
  __main__.py        # python -m lumina.memory_score entry
  cli.py             # argument parsing and output rendering
  parser.py          # MemoryFileMetrics + parse_file / parse_directory
  dimensions.py      # the 10 score_* analyzer functions
  scorer.py          # MemoryScorer orchestrator + MemoryScoreReport
  constants.py       # weights, thresholds, domain keywords, line limits, secret patterns
```

The scorer:

1. `parse_file` / `parse_directory` extract `MemoryFileMetrics` — frontmatter
   flag, heading counts, table/code-block counts, line count, format type,
   detected domains, cross-ref counts, and so on.
2. Each of the 10 `score_*` functions in `dimensions.py` reads those metrics
   and returns `(score, detail)`.
3. `MemoryScorer._score_metrics` registers a `HealthAggregator` with the
   default (or caller-provided) weights and grade thresholds, feeds each
   analyzer's score in via `agg.score(name, value, detail)`, then calls
   `agg.evaluate()` to produce the final weighted report.
4. `MemoryScoreReport` wraps the `HealthReport` and adds the letter grade,
   Illithid lifecycle stage, and renderers (`to_text`, `to_markdown`,
   `to_dict`).

This is the same `HealthAggregator` documented in `docs/ARCHITECTURE.md` — the
scorer is a demonstration that the framework's own primitives are enough to
build a non-trivial quality tool.

## See Also

- `docs/ARCHITECTURE.md` — `HealthAggregator` and other core primitives
- `examples/memory_scorer/demo.py` — runnable programmatic example
- `tests/test_memory_scorer.py` — full test coverage
