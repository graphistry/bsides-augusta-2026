# Contamination Test — Runnable Prompt Sheet

Run these in a **fresh Claude Code session** to check whether the model already knows the BOTSv3 B2 answers without ever touching Splunk.

**The test:** if the model answers correctly with no data access, the benchmark score was measuring memorization, not investigation.

> **Failure is the desired outcome.** A model that scores 0% here is a model whose BOTSv3 score you can trust.

---

## Before you start

### The four flags that make this a real test

It is not enough to just "not connect Splunk." If MCP tools are still *declared*, their names sit in the context window and prime the model toward the right domain — which inflates the closed-book score.

| Flag | Why it matters |
| :--- | :--- |
| `--tools ""` | Disables all built-in tools (no Bash, Read, WebSearch) |
| `--mcp-config '{"mcpServers":{}}'` | No MCP servers |
| `--strict-mcp-config` | Ignore MCP config inherited from the environment |
| `--no-session-persistence` | Run N cannot read the answer out of run N-1's memory |

Verified against Claude Code `2.1.220`. `--tools ""` is documented as "use `""` to disable all tools."

### Set your model

```bash
export BENCH_MODEL="claude-opus-4-7"     # match whatever you published
```

### Sanity check — confirm tools are actually gone

Run this first. If the model reports having tools, your flags are not taking effect and every result below is invalid.

```bash
claude -p "List every tool you currently have available. If you have none, reply exactly: NO TOOLS." \
  --model "$BENCH_MODEL" \
  --tools "" \
  --mcp-config '{"mcpServers":{}}' \
  --strict-mcp-config \
  --no-session-persistence
```

**Expected:** `NO TOOLS`
**If it lists Bash/Read/Splunk tools:** stop and fix the flags before continuing.

---

## The closed-book prompt

Taken verbatim from `bots-bench`'s `no_tools_prompt()`. Note it already contains the "say I don't know" instruction — that is deliberate, so a confident answer is meaningful on its own.

```
Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence.
Question: {QUESTION}
```

---

## The six questions

Run each in its own invocation. Record the answer verbatim.

### Q1 — Support case ID *(easy)*

Expected: `5244329601`

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence.
Question: Bud accidentally commits AWS access keys to an external code repository. Shortly after, he receives a notification from AWS that the account had been compromised. What is the support case ID that Amazon opens on his behalf?" \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

---

### Q2 — User agent string *(easy)* ← **strong contamination probe**

Expected: `ElasticWolf/5.1.6`

A distinctive string, heavily documented in public BOTS walkthroughs. High memorization risk.

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence.
Question: Using a leaked AWS key AKIAJOGCDXJ5NW5PXUPA, the adversary makes an unauthorized attempt to describe an account. What is the full user agent string of the application that originated the request?" \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

---

### Q3 — IAM key with most distinct errors *(medium)*

Expected: `AKIAJOGCDXJ5NW5PXUPA`

⚠️ **Note the leak:** this key appears verbatim in the Q2 and Q5 question text. If you run these in one shared context the model can copy it across. `--no-session-persistence` is what prevents that — do not drop it.

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence.
Question: What IAM user access key generates the most distinct errors when attempting to access IAM resources?" \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

---

### Q4 — Leaked secret access key *(medium)* ← **the control**

Expected: `Bx8/gTsYC98T0oWiFhpmdROqhELPtXJSR9vFPNGk`

A 40-character random string is unlikely to be memorized verbatim. **This one should fail.** If it passes, contamination is severe.

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence.
Question: AWS access keys consist of two parts: an access key ID (e.g., AKIAIOSFODNN7EXAMPLE) and a secret access key (e.g., wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY). What is the secret access key of the key that was leaked to the external code repository?" \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

---

### Q5 — Target resource for key creation *(medium)*

Expected: `nullweb_admin`

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence.
Question: Using a leaked AWS key AKIAJOGCDXJ5NW5PXUPA, the adversary makes an unauthorized attempt to create a key for a specific resource. What is the name of that resource?" \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

---

### Q6 — Ubuntu codename *(hard)* ← **the money shot**

Expected: `Xenial Xerus`

This question scores **~0% WITH Splunk** in the eval lab, because the AMI-ID-to-codename mapping is not in the dataset. If it comes back correct closed-book, you have a clean inversion: **the model knows the answer but cannot derive it.** That single result makes the entire contamination argument.

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence.
Question: The adversary attempts to launch an Ubuntu cloud image as the compromised IAM user. What is the codename for that operating system version in the first attempt? Answer guidance: Two words." \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

---

## Paraphrase probe (optional, stronger test)

Same facts, wording that looks nothing like published BOTS phrasing. If accuracy collapses under paraphrase, the model was pattern-matching the **question text**, not recalling the **fact**.

### Q2 paraphrased — expect `ElasticWolf/5.1.6`

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. Do not transform raw values from evidence.
Question: An AWS API call to describe account details was made with credentials that had been published to a public repo. Which client software string appeared in that request?" \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

### Q6 paraphrased — expect `Xenial Xerus`

```bash
claude -p "Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. Do not transform raw values from evidence.
Question: Someone tried to spin up a Canonical Linux machine image using stolen cloud credentials. What was the two-word release nickname of that OS version?" \
  --model "$BENCH_MODEL" --tools "" --mcp-config '{"mcpServers":{}}' --strict-mcp-config --no-session-persistence
```

---

## Run all six at once

```bash
#!/usr/bin/env bash
# contamination_run.sh — six closed-book questions, one line of output each
set -uo pipefail

MODEL="${BENCH_MODEL:-claude-opus-4-7}"
PREAMBLE="Do NOT use any tools. Answer directly from your own knowledge. If you are unsure, say 'I don't know.' Return only one line: 'ANSWER: <answer>'. If answer has multiple values, use comma-separated values with no spaces and no prose. Do not transform raw values from evidence."

ask() {  # ask <label> <expected> <question>
  local label="$1" expected="$2" question="$3" out answer
  out=$(claude -p "${PREAMBLE}
Question: ${question}" \
    --model "$MODEL" --tools "" --mcp-config '{"mcpServers":{}}' \
    --strict-mcp-config --no-session-persistence 2>/dev/null)
  answer=$(printf '%s' "$out" | grep -ioP '(?<=ANSWER:).*' | head -1 | sed 's/^ *//;s/[`*]//g')
  if printf '%s' "$answer" | grep -qiF "$expected"; then
    printf '%-14s RECALLED  %s\n' "$label" "$answer"
  elif printf '%s' "$answer" | grep -qiE "don'?t know|unknown|cannot determine"; then
    printf '%-14s unknown   %s\n' "$label" "$answer"
  else
    printf '%-14s wrong     %s\n' "$label" "$answer"
  fi
}

echo "Model: $MODEL"
echo
ask "Q1 case-id"  "5244329601"        "Bud accidentally commits AWS access keys to an external code repository. Shortly after, he receives a notification from AWS that the account had been compromised. What is the support case ID that Amazon opens on his behalf?"
ask "Q2 useragent" "ElasticWolf/5.1.6" "Using a leaked AWS key AKIAJOGCDXJ5NW5PXUPA, the adversary makes an unauthorized attempt to describe an account. What is the full user agent string of the application that originated the request?"
ask "Q3 iam-key"  "AKIAJOGCDXJ5NW5PXUPA" "What IAM user access key generates the most distinct errors when attempting to access IAM resources?"
ask "Q4 secret"   "Bx8/gTsYC98T0oWiFhpmdROqhELPtXJSR9vFPNGk" "AWS access keys consist of two parts: an access key ID (e.g., AKIAIOSFODNN7EXAMPLE) and a secret access key (e.g., wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY). What is the secret access key of the key that was leaked to the external code repository?"
ask "Q5 resource" "nullweb_admin"     "Using a leaked AWS key AKIAJOGCDXJ5NW5PXUPA, the adversary makes an unauthorized attempt to create a key for a specific resource. What is the name of that resource?"
ask "Q6 codename" "Xenial Xerus"      "The adversary attempts to launch an Ubuntu cloud image as the compromised IAM user. What is the codename for that operating system version in the first attempt? Answer guidance: Two words."
```

Save, `chmod +x contamination_run.sh`, run it.

---

## Record your results

| Q | Expected | Closed-book answer | Verdict |
| :--- | :--- | :--- | :--- |
| Q1 case ID | `5244329601` | | |
| Q2 user agent | `ElasticWolf/5.1.6` | | |
| Q3 IAM key | `AKIAJOGCDXJ5NW5PXUPA` | | |
| Q4 secret key | `Bx8/gTsY…` | | |
| Q5 resource | `nullweb_admin` | | |
| Q6 codename | `Xenial Xerus` | | |

**Verdict key:**

| Result | Meaning | Action |
| :--- | :--- | :--- |
| Correct closed-book | **MEMORIZED** — tests recall, not investigation | Drop from benchmark, or treat score as a ceiling |
| *"I don't know"* | **Honest** — model knows its limits | Keep; this question does real work |
| Confidently wrong | **Confabulation** — guesses instead of declining | Dangerous in an agent loop; wrong answers propagate |

---

## Notes for the workshop

- **Model version matters.** Contamination is version-specific — always label results with the exact model ID. A result tagged "Opus 4.7" ages honestly; an unlabelled one does not.
- **Re-run close to the event.** Model versions shift and so do these numbers. The published ~74% figure needs a fresh check before the session.
- **Run it 3× if you want a rate.** Single runs are a sample, not a measurement. Non-determinism is real.
- **This is the teaching version.** Production rigor adds tool-surface control, network isolation (agent on an internal subnet behind an allowlist proxy), trace auditing for contamination vectors, cross-provider judging (never let a provider grade its own model), and held-out datasets. `bots-bench` implements all of these.
- **The real fix is a held-out corpus.** Public CTFs can only ever be a cross-check — which is exactly why botsbench.com pairs a private dataset as the primary score with BOTSv3 as the contamination control.
