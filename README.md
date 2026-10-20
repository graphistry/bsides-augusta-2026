# From AI Copilot to Commander

**AI Agents and RAG for Security Automation and Investigation — a two-day hands-on
training, BSides Augusta 2026.**
Building AI systems that reliably run security investigations.

📅 **October 21–22, 2026 · 09:00–17:00 ET both days** (one-hour lunch each day)
Instructors: **Sindre · Leo** (Graphistry / Louie.ai), with Louie.ai staff on the floor.
This is the full two-day course — the BSides Canberra and BSides Las Vegas 2026 workshops
were one-day distillations of it.

📦 **Repo:** <https://github.com/graphistry/bsides-augusta-2026>
🔑 **Sign up first (free):** a [**Graphistry Hub**](https://hub.graphistry.com) account —
you'll use it for the Louie paths and to render graphs.

---

## The idea

Modern security work is moving from *using* an AI assistant to *commanding* a fleet of
them. But agents are unreliable in a way that compounds: if each step of an
investigation is **70% reliable, a 10-step run lands at ~3%.** And you cannot simply carry
over AI coding practices — assumptions like unit tests no longer apply. This course is
about what actually moves that number, and about being able to **prove** it moved.

Everything is built around one spine:

> **plan → run → eval**

Day 1 is the **copilot** half: run models with and without tools, reach a real Splunk
cyber range through an agent harness, and investigate a multi-domain incident. Day 2 is
the **commander** half: make the agent reliable with skills and planning, build an eval
loop that measures whether your changes helped (and whether the score is even real), and
ship a full investigation deliverable.

You leave with a working investigation agent, a reusable timelining skill, an eval loop,
and a defensible, evidence-based opinion about what AI can and cannot do in your SOC.

## Who it's for

Beginner to intermediate. No prior AI, ML, or agent experience needed, no GPU required.

- **Analysts** (SOC, IR, DFIR, hunt, threat intel, vuln mgmt) — go beyond copilots.
- **Engineers and developers** — build agents, scale RAG, connect your own tools.
- **Leaders** — understand ROI, technology trajectories, and how to responsibly target outcomes.

Every lab has a **prompt-first (no-code)** path and a **code-first (Python)** path.

## The labs

One incident — **BOTSv3 Incident B2, an AWS key compromise** spanning email, CloudTrail,
IAM, and EC2 — runs across the whole course, so each lab builds on the last.

| Lab | Day | Time | What you do |
|-----|-----|------|-------------|
| **[Lab 1 — DIY LLM](labs/lab1/lab1_guide.md)** | 1 | 60m | Run an OSS LLM locally and watch it hallucinate on SOC questions. Then reach Splunk three ways (MCP harness, `louie-py`, Louie desktop) and run your first query + graph. |
| **[Lab 2 — AI CTF](labs/lab2/lab2_guide.md)** | 1 | 105m | Investigate B2 — **BYO agent** (Claude Code / OpenCode over MCP) or **running with Louie** — across all six forensic questions, then compare the two harnesses. |
| **[Lab 3 — Skills & Timelining](labs/lab3/lab3_guide.md)** | 1–2 | 75m + 45m | Build a BOTS Q skill and prove it helps, author a timelining skill, run it on the attack chain, score it against a reference. Day 2: automate the flow via the `louie-py` API. |
| **[Lab 4 — Evals & Leaderboard](labs/lab4/lab4_guide.md)** | 2 | 120m | Score the skill, error-analyze the failures, fix it, watch the score move — then check whether the score is contamination. |
| **[Capstone — IR report + graphs](labs/capstone/capstone_guide.md)** | 2 | 120m | In-room, instructor-reviewed: an IR report for B2 plus a timeline-entity graph and an infrastructure graph on Graphistry Hub. |

Full schedule, lab breakdown, tracks, and the mapping to the one-day BSides editions:
**[`labs/README.md`](labs/README.md)**.

## Schedule

Two days, 09:00–17:00 ET, one-hour lunch each day. Room logistics and any day-of changes
are in the session GDoc.

### Day 1 — Copilot: models, harnesses, investigation

| Time | Length | Block |
|------|--------|-------|
| 09:00–09:30 | 30m | Intro & logistics |
| 09:30–10:00 | 30m | Talk — LLMs, agents & harnesses: why reliability compounds |
| 10:00–11:00 | 60m | **Lab 1** — DIY LLM: a local OSS model hallucinating on SOC questions, then reach Splunk three ways |
| 11:00–11:15 | 15m | Break |
| 11:15–11:45 | 30m | Talk — DB MCPs & the semantic layer, CTFs & bots-bench |
| 11:45–12:30 | 45m | **Lab 2 (part 1)** — AI CTF: BOTSv3 B2, Q1–Q3 |
| 12:30–13:30 | 60m | Lunch |
| 13:30–14:30 | 60m | **Lab 2 (part 2)** — Q4–Q6, vibes evals, BYO agent vs Louie |
| 14:30–15:00 | 30m | Talk — Skills, memory & planning |
| 15:00–15:15 | 15m | Break |
| 15:15–16:30 | 75m | **Lab 3 (Tasks 1–2)** — BOTS Q skill, timelining skill, vibes evals |
| 16:30–17:00 | 30m | Day 1 wrap — what moved the number, Day 2 preview |

### Day 2 — Commander: evals, automation, delivery

| Time | Length | Block |
|------|--------|-------|
| 09:00–09:15 | 15m | Recap & Day 1 leftovers |
| 09:15–09:45 | 30m | Talk — Evals & AI investigation factories |
| 09:45–11:00 | 75m | **Lab 4 (Tasks 1–2)** — Evals: error analysis, the eval loop |
| 11:00–11:15 | 15m | Break |
| 11:15–12:00 | 45m | **Lab 4 (Task 3)** — Contamination: is the score real? |
| 12:00–12:30 | 30m | Talk — RAG, semantic layers & self-planning agents |
| 12:30–13:30 | 60m | Lunch |
| 13:30–14:15 | 45m | **Lab 3 (Task 3)** — Automate the flow via the `louie-py` API (no-code track: skill hardening) |
| 14:15–16:15 | 120m | **Capstone** — IR report + timeline-entity graph + infrastructure graph |
| 16:15–16:30 | 15m | Break |
| 16:30–17:00 | 30m | Capstone review, group discussion & your SOC's next steps |

Lab time is about 8h45m of the 14 hours; talks and discussion about 3h30m; the rest is
breaks and lunch.

## Three ways to reach Splunk

The course meets you at your comfort level — pick a lane, or try them all:

- **BYO agent** — your own coding agent (Claude Code, OpenCode, Codex) over the Splunk
  **MCP** server. The raw harness experience, and the baseline everything else improves on.
- **`louie-py`** — the code-first client: a few lines of Python that query Splunk and
  return dataframes *and* Graphistry graphs.
- **Louie desktop** — the same copilot in a no-code GUI ([download.louie.ai](https://download.louie.ai)).

## Getting started

```bash
git clone https://github.com/graphistry/bsides-augusta-2026.git
cd bsides-augusta-2026
```

Then do **[Lab 1](labs/lab1/lab1_guide.md)** before Day 1 if you can — it installs
everything and catches account, connector, and credential problems early. Grab your free
**[Graphistry Hub](https://hub.graphistry.com)** account now if you don't have one.

Bring a laptop with a modern browser, Wi-Fi, and its power adapter. You'll need:

- **Splunk access** with BOTSv3 loaded (cyber-range credentials provided in-session)
- **Python 3.12+** — required by the Splunk **MCP** server (`splunk-mcp-server2`) and the
  `louie-py` code path. **Not needed if you only use Louie desktop** (no code).
- **Claude Code CLI** or **OpenCode** (for the BYO-agent path; optional otherwise)
- For Lab 1's local-LLM part: a Google account (the Colab notebook installs Ollama for you), or
  **[Ollama](https://ollama.com)** locally with a small model pulled (`ollama pull phi3:mini`, ~2 GB —
  **pull it before the session**, conference Wi-Fi will not cooperate)
- A free **[Graphistry Hub](https://hub.graphistry.com)** account (for the Louie paths)

Setup commands and credential handling: see **[`labs/README.md#setup`](labs/README.md#setup)**.

## Working through the labs with an AI assistant

These are teaching exercises. If you pair with an LLM, the intent is that it helps you
*write and debug code* — not that it solves the CTF or opens the answer key for you. The
lab notebooks say so explicitly; the evals lab (Lab 4) relaxes this since its result is
already known.

## Repository layout

```
labs/          the course — one folder per lab, plus labs/README.md
  lab1/ ...    DIY LLM: a local OSS model hallucinating, then reach Splunk three ways (+ mcp_config.json)
  lab2/ ...    AI CTF: BOTSv3 B2 investigation
  lab3/ ...    skills, timelining, API automation
  lab4/ ...    evals and contamination
  capstone/ .. in-room capstone: IR report + graphs
```

> **Credentials never get committed** — `.env` / `env` and the instructor answer key
> are gitignored. Never paste live secrets into a notebook or commit.
