# /brainstorm — Multi-Perspective Ideation Session

Generate structured brainstorming from multiple viewpoints on a topic, problem, or decision.

## Instructions

### Format: 3-Perspective Dialectic + Synthesis

Run a structured 3-phase brainstorming session. The user's topic follows the command.

**Topic:** $ARGUMENTS (if empty, brainstorm the previous AI response in this conversation; if no previous response, do a self-assessment of the current project state)

### Variation Detection

Parse the first word of $ARGUMENTS for modifiers:

- **`quick [topic]`** — Compressed: 1 bullet per perspective + recommendation
- **`deep [topic]`** — Extended: thorough exploration + detailed analysis + implementation plan
- **(no modifier)** — Standard 3-perspective session (default)

### Phase 1: DIVERGE (Generate Ideas)

Present 3 distinct perspectives on the topic:

```
@BRAINSTORM SESSION
====================
Topic: [user's topic]
Started: [timestamp]

Optimist (Builder):
───────────────────
"Here's what we COULD do..."
- [3-5 bold, ambitious ideas — focus on opportunity, leverage, upside]
- [Think big, assume resources exist, explore moonshots]
- [Connect to existing capabilities that could amplify]

Critic (Realist):
─────────────────
"Here's what will ACTUALLY happen..."
- [3-5 grounded counterpoints — focus on risk, cost, complexity]
- [What breaks? What's the hidden dependency? What's the maintenance burden?]
- [Reference past failures or near-misses if relevant]

Analyst (Logician):
───────────────────
"The logical approach would be..."
- [3-5 data-driven observations — focus on trade-offs, metrics, precedent]
- [What does the evidence suggest? What's the expected value?]
- [Rank options by effort-to-impact ratio]
```

### Phase 2: CONVERGE (Synthesize)

After the 3 perspectives, synthesize:

```
SYNTHESIS
─────────
Agreement Zone: [Where all 3 perspectives align]
Key Tension: [The core trade-off or disagreement]
Blind Spots: [What none of the 3 perspectives addressed]
```

### Phase 3: ACTIONABLE OUTPUT

```
RECOMMENDED PATH
────────────────
1. [Concrete next step — can be done THIS session]
2. [Follow-up — within 24 hours]
3. [Larger play — if the above two succeed]

DECISION NEEDED: [If there's a fork, present it as a clear A/B choice]
```

## Behavioral Rules

- **Match the user's energy** — if they're exploring ("what if we..."), be expansive. If they're stuck ("how do I..."), be directive.
- **Use project context** — reference existing systems, open issues, capabilities. Don't brainstorm in a vacuum.
- **Optimist is never naive** — optimistic but aware of constraints (budget, time, team size)
- **Critic is never nihilistic** — critical but constructive (identifies risks to MANAGE, not to abandon)
- **Analyst always quantifies** — if possible, attach numbers (hours, dollars, probability, % improvement)
- **Keep it tight** — each perspective is 3-5 bullets, not essays
- **End with ONE clear recommendation** — brainstorming without a conclusion is noise
