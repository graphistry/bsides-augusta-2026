---
name: investigation-loop
description: "Multi-round alert investigation with analyst review between rounds. Use when an analyst hands over a security alert to investigate, or asks to continue, extend, correct or redo a previous investigation round."
---

# Investigation loop

The analyst reviews your work after every round and decides what happens next. Each round has one job: do the work that was asked, report it in the fixed format below, and make the analyst's next decision easy. A round that ends with clear gaps and concrete next steps is a good round, even when the verdict is still open.

## Round 1: from alert to first assessment

1. **Restate the alert.** What fired, which entities (host, user, IP, hash, process), and the time of the event. If the alert leaves an entity or the time unclear, say so in the report and investigate what you can.
2. **Scope.** Set a time window around the event: one hour either side unless an active alert-type skill or SOP says otherwise. List the entities you will pivot on.
3. **Plan three to six checks**, the most decisive first. When an alert-type skill or SOP is active, follow its steps in its order.
4. **Run them.** Keep every query bounded by the time window and a row limit.
5. **Report** in the format below.

Round 1 aims for a first assessment, not completeness. When the plan runs past about ten tool calls, stop and move the remaining checks to Next steps.

## Follow-up rounds

The analyst replies in one of these forms:

| Reply | What to do |
|---|---|
| `Run next steps N1, N3` | Run exactly those steps, nothing else |
| `Continue` | Run all proposed next steps, in order |
| An instruction ("also check X", "pivot on user Y") | Do that |
| A correction ("Z is wrong because...") | Re-examine Z; retract or revise the finding if the analyst is right, and say so plainly |

In every follow-up round:

- Build on the evidence you already have. Do not repeat a query unless the analyst asks or the time window changed.
- Start the report with **What changed**: new findings, retracted findings, and whether the verdict or confidence moved and why.
- Number the round: the analyst's first reply starts round 2.

## Report format (every round)

```markdown
## Round <n>: <one-line headline>

**What changed:** <round 2 onwards only>

### Assessment
VERDICT: <true_positive | false_positive | insufficient_data>
CONFIDENCE: <low | medium | high>
<Two to four sentences on why.>

### Evidence
- <finding> (<source or connector>, <table or query>, <time window>)

### Timeline
<Only when ordering matters: timestamp, entity, event.>

### Gaps and open questions
- <what is unknown, and why it matters for the verdict>

### Next steps
N1. <action> to <what it would confirm or rule out>
N2. ...
```

When further work would not change the verdict, write `NEXT_STEPS: none` instead of a numbered list.

For this skill, this report replaces the default closing Answer block. Keep the `VERDICT:`, `CONFIDENCE:` and `N<number>.` lines exactly as shown: the analyst's tooling reads them.

## Evidence rules

- **Every finding comes from a query result in this thread**, and names its source. No finding from general knowledge about how attacks usually look.
- **Not found means not found.** When an entity or event is absent, write "not found in <source> for <window>". Never fill the gap with what probably happened.
- **Observation before interpretation.** State what the data shows, then what you conclude from it, as separate sentences.
- **Confidence moves only with evidence.** `high` needs either two independent sources that agree, or one decisive artifact, such as a known-bad hash or a confirmed C2 connection. Do not raise confidence because the analyst pushed back; raise it when new evidence arrives.
- **`insufficient_data` is a valid verdict.** Use it when the data needed to decide is missing or out of retention, and list what would decide it under Next steps.
