# Lab 3: Skills, Timelining & Evals

## Overview

In Lab 2 you investigated the B2 incident by asking questions one at a time. Some queries worked on the first try; others took several wrong turns. In this lab you turn that experience into **skills** — reusable automation that makes future investigations faster and more reliable — and then **measure** whether they work.

**Goals:**
1. Practice the flow: **use something → automate it into a Skill → prove the skill's value**
2. Build a timelining skill for the B2 incident
3. Score it: error analysis, then an eval loop that fixes the skill and re-scores it
4. (🔴 Hard mode, Python) Automate the whole flow via the louie-py API

**Running example:** BOTSv3 Incident B2 — AWS Key Compromise (same incident from Lab 2)

**Time:** ~75 minutes — Task 1 ~15m, Task 2 ~25m, Task 3 ~15m, Task 4 ~20m. Task 5 is hard mode, or take-home.

**Notebooks:**
- `lab3_skills_louie.ipynb` — Tasks 1–2, code track [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/graphistry/bsides-augusta-2026/blob/main/labs/lab3/lab3_skills_louie.ipynb)
- `evals_explained.ipynb` / `evals_explained.md` — Task 4: the eval loop, both tracks [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/graphistry/bsides-augusta-2026/blob/main/labs/lab3/evals_explained.ipynb)
- `lab3_api.ipynb` — Task 5: API automation [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/graphistry/bsides-augusta-2026/blob/main/labs/lab3/lab3_api.ipynb)

**No install — Colab.** Open a notebook with its badge, run the Colab cell at the top (clones the repo, installs
louie-py), set `IS_COLAB = True` in the settings cell, and enter your Graphistry Hub login when the setup cell asks.

No-code track: follow the tasks below in Louie desktop.

---

## Task 1: Skills Hello World (~15 min)

### The problem

In Lab 2, you may have noticed the agent:
- Doesn't know to use `index=botsv3`
- Tries wrong sourcetypes before finding the right one
- Doesn't know which fields matter in CloudTrail events
- Takes 3-5 queries to orient itself every time you start a new thread

### The fix: create a BOTS Q skill

A skill encodes what you already know so the agent starts smart.

### Step 1: Baseline (without skill)

Open a **new dthread** in louie and run one of the easier B2 questions:

```
Bud accidentally commits AWS access keys to an external code repository.
Shortly after, he receives a notification from AWS that the account had been
compromised. What is the support case ID that Amazon opens on his behalf?
```

**Observe:**
- How many queries did it take?
- Did it find the right sourcetype on the first try?
- How long before you got the answer?

### Step 2: Create the skill

In the same or new dthread, ask louie to create a skill:

```
Create a new skill called "BOTS Q" that preloads the following context for
BOTSv3 investigations:
- Always use index=botsv3
- Key sourcetypes: aws:cloudtrail for API/IAM activity, stream:smtp and
  ms:o365:reporting:messagetrace for emails, WinEventLog:Security for auth
  events (4624=success, 4625=failure), osquery:results for endpoint telemetry
- The dataset covers August 2018, use earliest=0
- For CloudTrail events, check errorCode to distinguish success from failure
- Start every investigation by scoping the activity, then drill in
```

> **Note:** See `skills/bots_q_template.lui.md` for a reference implementation of what this skill should look like.

### Step 3: Test in a new dthread

Open a **fresh dthread** (important — don't reuse the old one) and use the BOTS Q skill. Run the same question again.

**Compare:**
- Faster? Fewer wrong turns?
- Did it use `index=botsv3` immediately?
- Better first query?

### Step 4: Record your observations

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Time to answer | | |
| Number of queries | | |
| Used correct index on first try? | | |
| Used correct sourcetype on first try? | | |
| Answer correct? | | |

This is a **vibes eval** — you're observing Correctness and Speed before doing anything formal.

---

## Task 2: Mini-Timelining Skill (~25 min)

### Background

Timelining is a key subflow of many investigation tasks: given a clue, go forwards and backwards in time to identify what happened. In this task you'll build a skill that does this for the B2 incident.

### The expected timeline

Open `b2_timeline_attack_phase.md` — this is the **attack phase** of the B2 incident (09:16:12 to 09:28:54). It contains 11 events across 4 attacker IPs.

Key events:
- 09:16:12 — Attacker validates stolen credentials (GetCallerIdentity)
- 09:16:12 — Attacker creates STS token for persistence
- 09:16:14 — Cryptomining campaign begins (RunInstances)
- 09:16:53 — AWS sends notification email (Case 5244329601)
- 09:27:06 — Different attacker uses ElasticWolf for manual exploration

### The clue

Your timelining skill will start from this clue:

> **"Access key AKIAJOGCDXJ5NW5PXUPA was used by IP 35.153.154.221 at 09:16:12"**

From this, the skill should search backwards and forwards to find related events.

### What to expect

With minimal prompt engineering, expect your skill to find **some** of these events but not all. For example:
- It should find the other CloudTrail events for the same key (easy — same filter)
- It may find the email notification (requires knowing to search stream:smtp)
- It may miss the ElasticWolf activity (different IP, 11 minutes later)

### Step 1: Build the skill

Create a new skill (or modify your BOTS Q skill) that adds timelining guidance:

```
Create a timelining skill for BOTSv3 investigations. Given a clue event
(timestamp, IP, key, or username), the skill should:
1. Search index=botsv3 for all events involving the same entities within +/- 30 minutes
2. Expand to related entities found in step 1 (e.g., if you find a new IP, search for that too)
3. Order events chronologically
4. For each event, note: timestamp, actor (IP/user), action, result (success/failure)
5. Identify attack phases: initial access, escalation, impact, detection, response
```

### Step 2: Test it

In a new dthread with the timelining skill, give it the clue:

```
Starting from this clue: Access key AKIAJOGCDXJ5NW5PXUPA was used by IP
35.153.154.221 at 2018-08-20 09:16:12. Build a timeline of the full attack
by searching forwards and backwards from this event.
```

### Step 3: Compare to the reference

Check your skill's output against `b2_timeline_attack_phase.md`:
- How many of the 11 events did it find?
- Did it identify all 4 attacker IPs?
- Did it find the AWS notification email?
- Did it correctly identify attack phases?

### Step 4: Iterate

Try improving your skill's prompt to catch the events it missed. Each iteration should get you closer to the reference timeline.

Stuck? `skills/bidirectional_timeframe.md` is a fuller reference skill for the same job —
backward/forward passes, pivoting on newly found entities, widening the window. Compare it
with what you wrote and borrow what's missing.

---

## Task 3: Eval Skill — Error Analysis (~15 min)

### The concept

The biggest LLM contribution to evals isn't just "correct/incorrect" — it's **error analysis**. Understanding *why* something failed matters more than knowing *that* it failed.

In this task you'll build an eval skill that compares the agent's timelining output against the expected timeline and classifies errors in two categories:

**Accuracy errors** (the answer is wrong):
| Type | Example |
|------|---------|
| Missing event | Didn't find the ElasticWolf activity at 09:27:06 |
| Wrong timestamp | Event timestamp off by more than a few seconds |
| Wrong entity | Attributed activity to wrong IP or user |
| Hallucinated event | Reported an event that doesn't exist in the data |
| Partial | Found the right event but missing key details |

**Speed errors** (the reasoning was inefficient):
| Type | Example |
|------|---------|
| Wrong path | Searched network logs when it should have searched CloudTrail |
| Too many queries | Made 15 Splunk queries when 3 would have sufficed |
| Scope creep | Investigated unrelated events outside the B2 incident |
| Timeout | Ran out of time or context before finishing |

### Build the eval skill

Create a skill that takes:
1. **Agent's timeline output** (your Task 2 timelining skill, re-run on the IR clue below)
2. **Expected timeline** (from `b2_timeline_ir_phase.md` — the IR phase, which the agent hasn't seen)
3. **The original clue**

And produces:
- List of expected events: found / missed / hallucinated
- Accuracy score: X out of Y events correctly identified
- Speed assessment: how many queries, any wrong paths?
- Error classification for each miss

### Test it

1. Run your timelining skill on a **new clue** from the IR phase:

   > **"The IR team executed aws_ir tool at 09:30:53 on the mars host"**

2. Run your eval skill on the output, comparing against `b2_timeline_ir_phase.md`

3. Review the error analysis:
   - Which IR phase events did the timelining skill find?
   - Which did it miss? Why?
   - Were there any hallucinated events?

### The meta-insight

You just used an LLM to evaluate an LLM. The eval skill can be reused on any future timelining task — change the expected timeline and clue, and you get structured error analysis automatically.

---

## Task 4: The Eval Loop — Score, Fix, Re-score (~20 min)

Task 3 gave you one structured error analysis. Now turn it into a **rate**: run the same
questions several times, find what's flaky, fix the skill, and prove the fix.

**Code track:** open `evals_explained.ipynb`. It loads the six B2 questions from
`../lab2/botsv3_b2_tests.json`, runs each through Louie in a fresh thread, checks the
answers, and prints the spreadsheet.

**No-code track:** `evals_explained.md` explains the same loop. Run each B2 question in a
fresh Louie desktop thread and fill in the spreadsheet by hand.

### Step 1: Baseline

Run all six questions once (or one question three times — the notebook starts with Q1 ×3).
Record pass/fail and elapsed time per run.

| Question | Run 1 | Run 2 | Run 3 | Pass rate | Avg time | Notes |
|----------|-------|-------|-------|-----------|----------|-------|

### Step 2: Diagnose one failure

Pick a question that failed or was slow. Read the trace: wrong index? wrong sourcetype?
wrong `stats` function? too many queries? This is the same classification as Task 3.

### Step 3: Fix the skill

Add the missing guidance to your BOTS Q skill (Task 1) — e.g. *"for distinct
errors use `dc(errorMessage)`"* or *"AWS notification emails are in `stream:smtp`"*.

### Step 4: Re-run

Run the same question(s) again with the updated skill. Did the pass rate move? Did
anything else get worse? That before/after pair is your first real eval result — keep it,
you'll want it for the discussion.

### Optional: LLM-as-judge

The last section of the notebook asks Louie to grade an answer and classify the error
(`WRONG_ANSWER` / `HALLUCINATED` / `WRONG_PATH` / `TIMEOUT`). Use it when the expected
answer isn't a single string.

---

## Task 5 (🔴 hard mode, code track): Automate the flow via the louie-py API

If you finish early and are comfortable with Python, reproduce Tasks 1–4 programmatically.
This is how investigations and evals get automated instead of done interactively — and
it's how a production eval pipeline runs. Otherwise treat it as take-home.

See `lab3_api.ipynb` for the full notebook. Key steps:

### Part 1: BOTS task with BOTS skill

```python
from louieai.notebook import lui

# Fresh thread
lui.new(name="B2 Automated - With Skill")

# Run a B2 question
lui("What is the support case ID that Amazon opens for Bud?", agent="Splunk")
print(lui.text)

# Access the data
if lui.df is not None:
    display(lui.df)
```

Compare elapsed time and answer quality between threads with and without the BOTS Q skill.

### Part 2: Timelining via API

```python
lui.new(name="B2 Timeline - Automated")
lui("""Starting from this clue: Access key AKIAJOGCDXJ5NW5PXUPA was used by IP
35.153.154.221 at 2018-08-20 09:16:12. Build a timeline of the full attack.""",
    agent="Splunk")

timeline_output = lui.text
print(timeline_output)
```

### Part 3: Score it against the reference via API

```python
# Load expected timeline
with open("b2_timeline_attack_phase.md") as f:
    expected = f.read()

lui.new(name="B2 Eval - Automated")
lui(f"""Evaluate this investigation timeline against the expected timeline.

Agent's output:
{timeline_output}

Expected timeline:
{expected}

For each expected event, mark it as: found, missed, or hallucinated.
Classify each error as an Accuracy error or Speed error.
Give an overall accuracy score.""")

print(lui.text)
```

This mirrors how a production eval pipeline works — run investigation, run eval, aggregate
results. Task 4 is the same loop by hand.

---

## Key Takeaway

**A skill is automation, and an eval is how you know it worked.** The progression so far:

1. You did something manually (Lab 2 investigation)
2. You noticed what was slow or unreliable (wrong index, wrong sourcetype, no structure)
3. You encoded your knowledge into a skill (BOTS Q, timelining — Tasks 1–2)
4. You proved the skill makes things faster and more correct (vibes eval, then error analysis)
5. You turned the check into a loop with a rate, fixed the skill, and re-scored
6. In Lab 4 you check the score is real by taking the data away

This is the loop: **investigate → analyze failures → build a skill → evaluate → repeat** —
Lab 4 adds the contamination control so the number means something.

---

## Next Lab

In **Lab 4** you take the eval ideas to a different kind of model: turn the Laya decision model from Lab 1 into a calibrated triage router, then check whether your agent's Lab 2–3 score is real or memorized.
