# How Evals Actually Work — A Practical Guide

## The simplest eval that actually works

You need three things:

1. A question
2. An expected answer (or a way to check correctness)
3. A loop that runs it multiple times

Here's a real eval for one B2 question, in ~30 lines of Python:

```python
import subprocess, json, re

question = "What is the support case ID that Amazon opens for Bud?"
expected = "5244329601"

results = []
for run in range(3):  # Run 3 times because non-deterministic
    proc = subprocess.run(
        ["claude", "-p", "--mcp-config", "../lab0/mcp_config.json",
         f"Answer this using Splunk (index=botsv3). "
         f"End with ANSWER: <your answer>\n\nQuestion: {question}"],
        capture_output=True, text=True, timeout=300
    )
    
    # Extract answer from output
    answer_match = re.search(r"ANSWER:\s*(.+)", proc.stdout)
    answer = answer_match.group(1).strip() if answer_match else ""
    
    correct = expected in answer
    results.append({"run": run, "correct": correct, "answer": answer})
    print(f"Run {run}: {'PASS' if correct else 'FAIL'} — got '{answer[:50]}'")

pass_rate = sum(r["correct"] for r in results) / len(results)
print(f"\nPass rate: {pass_rate:.0%} over {len(results)} runs")
```

That's a working eval. It's not fancy, but it answers the key question: *does this work reliably?*

---

## Why you run it multiple times

This is the big difference from unit tests. If you run it once and it passes, you don't know if you got lucky. Run it 3-5 times:

```
Run 0: PASS — got '5244329601'
Run 1: PASS — got '5244329601'  
Run 2: FAIL — got 'I could not find the support case'

Pass rate: 67% over 3 runs
```

Now you know something useful: it works most of the time but not always. A unit test is pass/fail. An eval gives you a **rate**.

---

## How to check answers when they're not exact

Three levels, from simple to sophisticated:

**Level 1: Substring match** (what bots-bench mostly does)
```python
correct = "5244329601" in agent_output
```
Works for factual answers with a unique string.

**Level 2: Regex pattern**
```python
correct = bool(re.search(r"xenial\s+xerus", agent_output, re.IGNORECASE))
```
Works when casing or formatting varies.

**Level 3: LLM-as-judge** (for open-ended answers)
```python
judge_prompt = f"""
The question was: {question}
The expected answer is: {expected}
The agent said: {agent_output}

Is the agent's answer correct? Reply YES or NO, then explain why.
"""
judge_response = call_llm(judge_prompt)
correct = "YES" in judge_response
```
Works when the answer is a narrative, not a single value. Trade-off: the judge can be wrong too.

---

## What a "proper" eval looks like in practice

It's a spreadsheet, not a framework. Seriously.

| Question | Run 1 | Run 2 | Run 3 | Pass Rate | Avg Time | Notes |
|----------|-------|-------|-------|-----------|----------|-------|
| Support case ID | PASS | PASS | FAIL | 67% | 8s | Failed run searched wrong sourcetype |
| User agent string | PASS | PASS | PASS | 100% | 5s | Consistent |
| IAM key with most errors | FAIL | PASS | FAIL | 33% | 22s | Often uses wrong stats function |
| Ubuntu codename | FAIL | FAIL | FAIL | 0% | 45s | Can't look up AMI IDs |

This tells you:
- **What's reliable** (user agent: 100%, ship it)
- **What's flaky** (support case: 67%, needs a skill to stabilize it)
- **What's broken** (Ubuntu codename: 0%, needs a different approach entirely)
- **What's slow** (IAM key: 22s avg, too many queries)

---

## The eval loop

The eval isn't a one-time check. It's a loop:

```
1. Run eval → "33% pass rate on IAM key question"
2. Diagnose why → "agent uses dc(errorCode) instead of dc(errorMessage)"
3. Fix it → add guidance to skill: "use dc(errorMessage) for distinct errors"
4. Run eval again → "100% pass rate on IAM key question"
5. Check you didn't break anything else → run all questions
```

This is the same red-green-refactor loop as TDD, just with probabilities instead of pass/fail.

---

## The same eval loop using louie-py

The Claude CLI example above works, but if you're using louie-py you can do the whole thing in a notebook — no subprocess, no output parsing:

```python
import os, re, time, json
from louieai._client import LouieClient
from louieai.notebook import Cursor

# Authenticate via environment variables
# Set: GRAPHISTRY_USERNAME, GRAPHISTRY_PASSWORD, GRAPHISTRY_HOST
# Or:  GRAPHISTRY_HUB_KEY_ID, GRAPHISTRY_HUB_KEY_SECRET, GRAPHISTRY_HOST
louie_client = LouieClient(
    server_url=os.environ.get("LOUIE_HOST", "https://den.louie.ai"),
    # personal key:  personal_key_id=..., personal_key_secret=...   (see evals_explained.ipynb)
    username=os.environ["GRAPHISTRY_USERNAME"],
    password=os.environ["GRAPHISTRY_PASSWORD"],
    graphistry_server=os.environ.get("GRAPHISTRY_HOST", "hub.graphistry.com"),
    timeout=600.0,
    streaming_timeout=600.0,
)
lui = Cursor(client=louie_client)

# Load questions
with open("../lab2/botsv3_b2_tests.json") as f:
    b2_tests = json.load(f)

def check_answer(output: str, patterns: list[str]) -> bool:
    """Check if output matches any expected pattern."""
    for pattern in patterns:
        if pattern.startswith("re:"):
            if re.search(pattern[3:], output, re.IGNORECASE):
                return True
        elif pattern.lower() in output.lower():
            return True
    return False

# Run each question 3 times
for qid, q in b2_tests.items():
    print(f"\n--- {q['name']} ---")
    passes = 0
    for run in range(3):
        lui = lui.new(name=f"Eval {qid} run {run}")  # Fresh thread each time
        start = time.time()
        lui(q["question"], agent="SplunkAgent")
        elapsed = time.time() - start

        correct = check_answer(lui.text or "", q["expected_patterns"])
        if correct:
            passes += 1
        print(f"  Run {run}: {'PASS' if correct else 'FAIL'} ({elapsed:.1f}s)")

    print(f"  Pass rate: {passes}/3")
```

**What's different from the CLI version:**
- `lui = lui.new()` creates a fresh thread each run (`.new()` returns a new cursor, it does not reset the old one) (same as starting a new Claude session)
- `lui.text` gives you the answer directly — no subprocess output parsing
- Each run is isolated — the agent doesn't remember previous attempts
- You can also access `lui.df` if the agent returned tabular data

**Adding LLM-as-judge with louie-py:**

```python
# After getting the agent's answer...
agent_answer = lui.text

# Open a new thread and ask louie to judge the answer
lui = lui.new(name=f"Judge {qid}")
lui(f"""The question was: {q['question']}
The expected answer is: {q['expected_output']}
The agent said: {agent_answer}

Is the agent's answer correct? Reply YES or NO.
If NO, classify the error:
- WRONG_ANSWER: agent gave a specific but incorrect answer
- HALLUCINATED: agent made up data not in the results
- WRONG_PATH: agent searched the wrong sourcetype or field
- TIMEOUT: agent didn't finish
""")

judgment = lui.text
correct = "YES" in (judgment or "").upper()
```

This is the same LLM-as-judge pattern, but you don't need to manage API keys or HTTP calls — louie handles it.

---

## The honest summary

| What you can automate today | What still needs a human |
|---------------------------|------------------------|
| Run the same questions N times | Decide which questions matter |
| Check answers with substring/regex | Evaluate quality of reasoning |
| Measure speed and tool call count | Judge if the SPL was elegant |
| Track pass rates over time | Decide when "good enough" is good enough |
| Use LLM-as-judge for open-ended answers | Validate the judge isn't wrong |

Start with the simple version (substring match, 3 runs, a spreadsheet). You can get fancier later, but most teams never need to.
