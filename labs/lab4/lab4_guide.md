# Lab 4: Triage Router & Contamination

## Overview

Two ways to check that a number means what you think it means.

- **Part A** goes back to Laya, the small decision model from Lab 1. You make it useful, make its
  confidence honest, and turn it into a **router** that suppresses routine CloudTrail events
  before they reach the expensive agent — then report on holdout once.
- **Part B** goes back to your agent's B2 score from Labs 2–3 and asks whether it measured
  investigation or memorization.

**Time:** ~75 minutes — Part A ~50m, Part B ~25m

**Notebooks:**
- `lab4_laya_triage_router.ipynb` — Part A
- `contamination_explained.ipynb` — Part B, code track
- `contamination_test_prompts.md` — Part B, copy-paste closed-book prompts (no notebook needed)

**Data:** `data/b2_cloudtrail_fallback.csv` — 374 events. Attacker rows are rebuilt from the
B2 evidence; routine rows are **synthetic** (see the `provenance` column and `build_fallback.py`).
The notebook can also pull the live window through Louie (`DATA_SOURCE = "louie_splunk"`).

**Running example:** BOTSv3 Incident B2 — AWS Key Compromise

---

## Part A: Distill your agent into a cheap triage router (~50 min)

```
CloudTrail events ──► Laya (small decision model, ms per event, runs on your laptop)
                         ├── confident "routine"  ──► suppress
                         └── everything else      ──► the expensive agent / an analyst
```

Open **`lab4_laya_triage_router.ipynb`**. The first sections repeat Lab 1 Part B quickly
(load, label, split, zero-shot, context, tradecraft), so you can start here even if you
skipped Lab 1. Then:

1. **Lever 3, deterministic enrichment.** Laya sees one event at a time with no memory. Add a
   one-line note computed in Python ("this IP was never seen for this user before the alert")
   and re-score.
2. **Lever 4, the threshold.** Pick the cut-off on Test, then check it once on Validation.
3. **Calibrate.** Fit a temperature on Validation and watch ECE (the gap between stated
   confidence and actual accuracy) drop. Temperature fixes *trust*, not *decisions*.
4. **Make the routing decision.** Choose a recall target (default 95%) and see how much
   routine traffic never reaches the agent, and what that saves.
5. **Report on Holdout. Once.** No more tuning after that cell.

### What to watch for
- **How you phrase a fact matters more than the fact.** The same "IP never seen before" signal
  as a JSON boolean barely helps; as a plain-English note placed *first* it takes AUC to ~0.99.
  Small models read text, and they only read the first 512 tokens.
- ⚠️ **The fallback data flatters enrichment:** each synthetic routine user has exactly one IP.
  On real CloudTrail, expect a smaller gain.
- **Holdout recall can miss the target** (e.g. 89% against a 95% target on a small CPU sample).
  A few events swing it. That's the point of reporting holdout honestly.
- **Persistent miss:** the attacker's `GetCallerIdentity`. A successful identity check looks
  routine on its own. What context would catch it?

### Levels
- 🟡 **Stretch — label bias:** swap the answer labels from false/true to A/B (same meaning) and
  count how many routing decisions flip.
- 🟡 **Stretch — failure analysis:** group the router's mistakes. Which hard negatives fooled it?
- 🔴 **Hard mode:** take it out of distribution (a different BOTSv3 window), wire Laya in as
  the first step of your Lab 3 agent, or plot source IP → event name coloured by P(attacker)
  in Graphistry to see where the model is unsure.

**Share-out:** your holdout AUC, Kappa, and the share of routine events you suppress at your
recall target — and where you would (and wouldn't) deploy this.

---

## Part B: Is the Score Real? — The Contamination Test (~25 min)

BOTSv3 is public. The questions, answers, and walkthroughs are on the open internet, so
they are very likely in every frontier model's training data. Before you trust the score
from Lab 3's eval loop, ask what it is **with the data taken away**.

**The test:** ask the same six questions with **no tools at all**. If the model still
answers correctly, it memorized — and your Splunk score measured recall, not investigation.

You already ran this in Lab 1 Part A against a small local model, and it made things up.
Now run it against the frontier model you used for the score — the interesting case is
when it *doesn't* make things up, because it remembers.

> **Failure is the desired outcome.** A model that scores 0% here is a model whose BOTSv3
> score you can trust.

**Code track:** `contamination_explained.ipynb` runs the closed-book test for all six
questions via the Claude Code CLI and prints a with-tools vs. no-tools comparison table.

**No-code / terminal track:** `contamination_test_prompts.md` has the same test as
copy-paste `claude -p` commands.

### Steps

1. Run the **sanity check** first — confirm the model reports `NO TOOLS`. If it lists any
   tools, the flags aren't taking effect and nothing below counts.
2. Run at least **Q2** (user agent string — the strongest contamination probe) and **Q1**.
   Run all six if time allows.
3. Record the closed-book answers next to your Lab 3 Task 4 results.
4. Optional: the **paraphrase probe** — reword a question and see if the memorized answer
   still comes out.
5. Stretch: the **cross-model comparison** — run the same six closed-book questions on a
   second model (a different provider, or a local model) and fill both columns of the results
   table in `contamination_test_prompts.md`. The differences are the lesson: which model knows
   the answers, which one declines, which one cites a public walkthrough it has clearly read.

### What to conclude

- Correct with tools, *"I don't know"* without: the agent investigated. Trust the score.
- Correct both ways: contaminated. The Lab 3 number is not evidence of investigation.
- Wrong both ways: the skill needs work (back to Lab 3), but at least the test is honest.
- Two models disagree closed-book: the one that scores lower is the more trustworthy
  benchmark subject, even if it needed more steering with tools. Capability and
  contamination are different axes — write down where each model sits on both.

---

---

## Key Takeaway

**A skill is automation, and an eval is how you know it worked.** The progression so far:

1. You did something manually (Lab 2 investigation)
2. You noticed what was slow or unreliable (wrong index, wrong sourcetype, no structure)
3. You encoded your knowledge into a skill (BOTS Q, timelining — Lab 3)
4. You proved the skill makes things faster and more correct (vibes eval, then error analysis)
5. You turned the check into a loop with a rate, fixed the skill, and re-scored
6. You checked the score is real by taking the data away
7. You applied the same discipline (splits, calibration, holdout) to a cheap model, and got a
   router you can put a number on

This is the loop: **investigate → analyze failures → build a skill → evaluate → repeat** —
with a contamination control so the number means something.

---

## Next Lab

The **capstone** follows in the room: apply everything from Labs 2–4 to produce a full IR
report for B2 with a timeline-entity graph and an infrastructure graph on Graphistry Hub,
for instructor review. See `../capstone/capstone_guide.md`.
