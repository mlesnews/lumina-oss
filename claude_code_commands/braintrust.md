# /braintrust — Polymath Lifeline Panel

Summon a virtual roundtable of history's greatest thinkers to reason through a high-stakes problem. This is the "Phone a Friend" lifeline — use it when the decision is consequential and standard brainstorming isn't enough.

## Instructions

### The Panel: 5 Polymath Personas

Each persona provides CHARACTERIZED reasoning — not just an answer, but reasoning that reflects their unique cognitive framework.

**Problem:** $ARGUMENTS (if empty, ask what problem needs the panel)

### Phase 1: BRIEF THE PANEL

Summarize the problem in 2-3 sentences. Include:
- What's at stake (money, time, reputation, safety)
- What options exist (if known)
- What constraints apply (budget, time, dependencies)

### Phase 2: PANEL RESPONSES

Present each polymath's characterized reasoning:

```
@BRAINTRUST PANEL SESSION
===========================
Problem: [user's problem]
Stakes: [what's at risk]
Convened: [timestamp]

EINSTEIN (First Principles / Thought Experiments):
──────────────────────────────────────────────────
"Imagination is more important than knowledge..."
- Strips the problem to fundamentals — what are the invariants?
- Proposes a thought experiment to test assumptions
- Identifies the hidden variable everyone is ignoring
- Style: Playful but precise. Questions assumptions. Seeks elegance.

SUN TZU (Strategy / Positioning / Adversarial Thinking):
────────────────────────────────────────────────────────
"Every battle is won before it is ever fought..."
- Maps the competitive landscape — who benefits, who loses?
- Identifies the asymmetric advantage or the terrain to control
- Recommends timing, positioning, and resource allocation
- Style: Terse. Strategic. Thinks in terms of leverage and terrain.

BUFFETT (Value / Risk / Compound Returns):
──────────────────────────────────────────
"Rule #1: Never lose money. Rule #2: Never forget Rule #1..."
- Evaluates the expected value and margin of safety
- Identifies what can go wrong and the cost of being wrong
- Looks for the moat — what's defensible long-term?
- Style: Folksy but razor-sharp. Asks "would I bet my own money?"

FEYNMAN (Debugging / Clarity / First Principles):
─────────────────────────────────────────────────
"If you can't explain it simply, you don't understand it..."
- Breaks the problem into testable components
- Identifies what you ACTUALLY know vs what you ASSUME
- Suggests the simplest possible experiment to reduce uncertainty
- Style: Curious, irreverent. Hates bullshit. Loves clarity.

DA VINCI (Systems / Integration / Creative Synthesis):
─────────────────────────────────────────────────────
"Simplicity is the ultimate sophistication..."
- Sees connections between domains others miss
- Proposes an elegant solution that combines multiple objectives
- Sketches the architecture — how do the pieces fit together?
- Style: Visual thinker. Draws analogies from nature. Seeks beauty in function.
```

### Phase 3: CONSENSUS & DISSENT

```
PANEL VERDICT
─────────────
Consensus: [Where 3+ polymaths agree]
Key Dissent: [The sharpest disagreement and why it matters]
Strongest Argument: [Which polymath's reasoning is most compelling and why]
Blind Spot: [What the entire panel missed — YOUR assessment as moderator]
```

### Phase 4: RECOMMENDATION

```
LIFELINE ANSWER
───────────────
Recommended Action: [Clear, actionable recommendation]
Confidence: [HIGH/MEDIUM/LOW — based on panel agreement]
Risk Mitigation: [If it goes wrong, here's the exit ramp]
Time Sensitivity: [Act now / This week / Can wait]
```

## Behavioral Rules

- **This is a LIFELINE, not a daily tool** — use for consequential decisions. Don't summon the panel for trivial choices.
- **Characterized reasoning is the value** — each persona must reason DIFFERENTLY, not just agree with different words. Einstein thinks in thought experiments. Sun Tzu thinks in positioning. Buffett thinks in expected value. Feynman thinks in testable hypotheses. Da Vinci thinks in systems.
- **Honesty over comfort** — if the panel thinks the user's preferred option is wrong, say so. Buffett would.
- **Use project context** — the polymaths should reference the actual codebase, open issues, and constraints. They give advice for THIS situation, not generic advice.
- **Keep each persona to 3-4 bullets** — dense insight, not lectures. These are geniuses; they don't waste words.
- **The moderator (you) adds value** — after the panel, identify the blind spot and synthesize. You're not just a relay.

## Variations

- `/braintrust [problem]` — Full 5-polymath panel
- `/braintrust quick [problem]` — 3 polymaths only (Einstein + Buffett + Feynman)
- `/braintrust war [problem]` — Adversarial focus (Sun Tzu leads, add Machiavelli + Clausewitz)
- `/braintrust money [problem]` — Financial focus (Buffett leads, add Soros + Dalio + Munger)
- `/braintrust build [problem]` — Engineering focus (Feynman leads, add Da Vinci + Tesla + Turing)

## Integration with /brainstorm

Use `/brainstorm` for general ideation (what COULD we do?).
Escalate to `/braintrust` when the stakes are high (what SHOULD we do?).

The flow: `/brainstorm` generates options → `/braintrust` stress-tests the best one.
