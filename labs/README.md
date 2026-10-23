# From AI Copilot to Commander — BSides Augusta 2026 labs (two days)

Hands-on labs for building AI systems that reliably run security investigations.

This is the full two-day course. The BSides Canberra and Las Vegas 2026 workshops were one-day
distillations of it; **labs are renumbered** — see the mapping below if you are working from
those materials.

## Labs

| Lab | Day | Time | Topic | What you'll do |
|-----|-----|------|-------|----------------|
| **Lab 0** | 1 | 35m | Setup | Reach Splunk **three ways** — Claude Code over MCP (Lab 2's harness), louie-py (code), and Louie desktop (no-code) — running the same first query in each: pull the CloudTrail activity for B2's compromised access key and graph it as attacker IP → AWS API call. Do it before the workshop if you can. |
| **Lab 1** | 1 | 60m | DIY LLM + decision API | **Part A:** run an OSS LLM locally (Ollama) and watch it hallucinate on the B2 questions, closed-book. **Part B:** run [Laya](https://github.com/NandhaKishorM/laya), an open-source Jev-compatible decision model, zero-shot on B2 CloudTrail events — it starts worse than random — and pull the first two levers. |
| **Lab 2** | 1 | 60m | AI CTF | Investigate BOTSv3 Incident B2 two ways — **BYO agent** (Claude Code / OpenCode over MCP) or **running with Louie** (the `Splunk` agent writes the SPL) — answering the **six** forensic questions across email, CloudTrail, IAM, and EC2. |
| **Lab 3** | 2 | 60m | Skills, timelining & evals | Build a BOTS Q skill and prove it helps, author a timelining skill, score it against a reference, error-analyze it, then run the eval loop: fix the skill and watch the score move. Hard mode: automate it via the louie-py API. |
| **Lab 4** | 2 | 60m | Triage router & contamination | **Part A:** turn Laya into a calibrated router that suppresses routine events before they reach the expensive agent, and report on holdout once. **Part B:** check whether your agent's B2 score is real or memorized. |
| **Capstone** | 2 | 45m | IR report + graphs | In the room, in pairs: an IR report for B2 with a timeline-entity graph and an infrastructure graph on Graphistry Hub. Alternative: craft events that get past your own classifier. |

Every lab has three levels: 🟢 **base**, 🟡 **stretch**, and 🔴 **hard mode**. If the base
level feels easy, keep going.

## Schedule

Two days, 09:00–17:00 ET, one-hour lunch each day. See the
[top-level README](../README.md#schedule) for the full schedule with talks.

| Day 1 | Block | Day 2 | Block |
|-------|-------|-------|-------|
| 09:40–10:15 | **Lab 0** | 11:00–12:00 | **Lab 3** |
| 11:00–12:00 | **Lab 1** | 14:30–15:30 | **Lab 4** |
| 14:00–15:00 | **Lab 2** | 15:30–16:15 | **Capstone** |

### Renumbering from the one-day BSides editions (Canberra)

| One-day (Canberra) | Two-day (Augusta) | Notes |
|--------------------|-------------------|-------|
| Lab 1 Part B (setup) | **Lab 0** | `lab1_setup.ipynb` → `lab0/lab0_setup.ipynb`; `mcp_config.json` moved to `lab0/` |
| Lab 1 Part A (DIY LLM) | **Lab 1 Part A** | Local Ollama cell split out into `lab1_ollama_local.ipynb` |
| *(new)* | **Lab 1 Part B** | Laya zero-shot, `lab1_laya_zeroshot.ipynb` |
| Lab 2 | **Lab 2** | Unchanged apart from the `../lab0/mcp_config.json` path |
| Lab 3 Tasks 1–2 | **Lab 3 Tasks 1–2** | |
| Lab 4 Tasks 1–2 (eval skill, eval loop) | **Lab 3 Tasks 3–4** | `evals_explained.*` moved to `lab3/` |
| Lab 3 Task 3 (API) | **Lab 3 Task 5** | Hard mode |
| *(new)* | **Lab 4 Part A** | Laya triage router, `lab4_laya_triage_router.ipynb` |
| Lab 4 Task 3 (contamination) | **Lab 4 Part B** | |
| Capstone (take-home) | **Capstone (in the room)** | Adds the "get past the classifier" alternative |

## Two tracks

Every investigation lab can be done without writing code, or code-first:

- **Lab 2** runs two ways — **BYO agent** (Claude Code / OpenCode over MCP, the raw harness) or **running with Louie** (the `Splunk` agent writes the SPL, via `louie-py` or Louie desktop).
- **Lab 3** and the **capstone** each have a **no-code** path (natural-language UI, follow the markdown guide) and a **code-first** path (Python notebook via `louie-py`).
- **Labs 1 and 4** (Laya) are notebooks: run the cells for the base level, edit them for stretch and hard mode.

The BYO-agent harness in Lab 2 is the baseline everything else improves on.

**Lab 0** is for **everyone**: it stands up all three interfaces — the Splunk MCP harness that Lab 2 needs, the `louie-py` client, and Louie desktop — and runs the same first query through each. Do it first; it's where environment, connector, and credential problems get caught before they cost you lab time.

## Prerequisites

- **Splunk access** with BOTSv3 loaded (credentials provided in-session)
- **Python 3.12+**, Jupyter, pandas — required by the Splunk **MCP** server
  (`splunk-mcp-server2`), the `louie-py` code path, and the Laya notebooks. **Not needed for
  the Louie desktop (no-code) path.**
- **Claude Code CLI** installed and authenticated (`claude --version`)
- **Lab 1 Part A:** either a Google account (the Colab notebook installs Ollama for you) or **Ollama** locally with a small model already pulled — `ollama pull phi3:mini` (~2 GB), **before** the session.
- **Labs 1 Part B and 4:** `pip install laya==0.4.8` and `python -c "import laya; laya.load()"` (~1 GB of weights), **before** the session. 8 GB+ RAM, no GPU needed.
- **Graphistry account** for the louie-py track (free at hub.graphistry.com)
- Optional: **Codex CLI**, `splunk-sdk` (capstone only)

## Setup

```bash
# Splunk MCP server (set up in Lab 0, used in Lab 2)
git clone https://github.com/splunk/splunk-mcp-server2.git
cd splunk-mcp-server2/python
python -m venv .venv && source .venv/bin/activate
pip install -e .
cd ../..
export SPLUNK_MCP_PATH="$(pwd)/splunk-mcp-server2"

# Splunk credentials (provided in-session)
export SPLUNK_HOST="..." SPLUNK_PORT=8089
export SPLUNK_USERNAME="..." SPLUNK_PASSWORD="..."

# louie-py client (set up in Lab 0, used in Labs 3-4 and the capstone)
pip install louieai
export GRAPHISTRY_USERNAME="..." GRAPHISTRY_PASSWORD="..."

# Laya decision model (Labs 1 and 4)
pip install graphistry laya==0.4.8 pandas
python -c "import laya; laya.load()"
```

Notebooks read credentials from the environment. To load them from a file instead, set `LAB_ENV_FILE=/path/to/env`.

> **Never commit credentials.** `.env` and `env` are both gitignored.

## Files

```
lab0/  lab0_guide.md
       lab0_setup.ipynb          <- reach Splunk three ways
       mcp_config.json           <- Splunk MCP config (Lab 2 launches with --mcp-config ../lab0/mcp_config.json)

lab1/  lab1_guide.md
       lab1_ollama_colab.ipynb   <- Part A in Colab: install Ollama, closed-book SOC questions
       lab1_ollama_local.ipynb   <- Part A with a local Ollama
       lab1_laya_zeroshot.ipynb  <- Part B: Laya zero-shot on B2 CloudTrail

lab2/  botsv3_b2_tests.json      <- canonical question set (all labs read this)
       botsv3_b2_hints.json      <- instructor-only approaches (gitignored)
       lab2_guide.md
       lab2_splunk_mcp.ipynb

lab3/  lab3_guide.md
       lab3_skills_louie.ipynb   <- Tasks 1-2, louie-py track
       evals_explained.ipynb / .md   <- Task 4: the eval loop
       lab3_api.ipynb            <- Task 5 (hard mode): API automation
       b2_timeline_attack_phase.md   <- reference timelines
       b2_timeline_ir_phase.md
       skills/bots_q_template.lui.md
       skills/bidirectional_timeframe.md

lab4/  lab4_guide.md
       lab4_laya_triage_router.ipynb   <- Part A: Laya triage router
       data/b2_cloudtrail_fallback.csv <- 374 events; attacker rows from B2 evidence, routine rows synthetic
       build_fallback.py               <- regenerates the CSV, documents real vs synthetic
       contamination_explained.ipynb   <- Part B: is the score real?
       contamination_test_prompts.md   <- copy-paste closed-book prompts

capstone/  capstone_guide.md     <- in-room capstone: IR report + graphs
           capstone.ipynb
```

## The running example

**BOTSv3 Incident B2 — AWS Key Compromise.** An employee commits AWS access keys to a public repo. AWS notices and opens a support case, but an adversary already has the keys and uses them to enumerate IAM, create keys, and launch EC2 instances.

The same incident runs across every lab, so each builds on the last. Lab 1 asks the B2 questions closed-book to a local model and scores Laya on B2 CloudTrail events; Lab 0 graphs the compromised key's CloudTrail activity as the setup query.

## The point

If each step of an investigation is 70% reliable, a 10-step run lands at ~3%. These labs are about what actually moves that number — and about being able to prove it moved.
