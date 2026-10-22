# From AI Copilot to Commander

**AI Agents and RAG for Security Automation and Investigation — a two-day hands-on
training, BSides Augusta 2026.**
Building AI systems that reliably run security investigations.

📅 **October 21–22, 2026 · 09:00–17:00 ET both days** (one-hour lunch each day)
📍 Bit room, first floor, Hull-McKnight building, Georgia Cyber Center. Check in at the
BSides Augusta desk on Wednesday morning.
Instructors: **Leo Meyerovich** and **Sindre Breda** (Graphistry / Louie.ai), with Louie.ai
staff on the floor. Sindre runs the room both days. Leo teaches Day 1 until the afternoon
and the first half of Day 2.
This is the full two-day course — the BSides Canberra and BSides Las Vegas 2026 workshops
were one-day distillations of it.

📦 **Repo:** <https://github.com/graphistry/bsides-augusta-2026>
💬 **Chat:** the class Discord channel (invite sent by email). Links, questions and lab
help during and after the class.
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

Day 1 is the **copilot** half: run models on your own laptop, including a small decision
model, reach a real Splunk cyber range through an agent harness, and investigate a
multi-domain incident. Day 2 is the **commander** half: make the agent reliable with
skills and planning, build an eval loop that measures whether your changes helped (and
whether the score is even real), turn a cheap model into a calibrated triage router,
secure the whole thing, and ship a full investigation deliverable.

You leave with a working investigation agent, a reusable timelining skill, an eval loop,
a measured triage router, and a defensible, evidence-based opinion about what AI can and
cannot do in your SOC.

## Who it's for

Beginner to advanced. No prior AI, ML, or agent experience needed, no GPU required.

- **Analysts** (SOC, IR, DFIR, hunt, threat intel, vuln mgmt) — go beyond copilots.
- **Engineers and platform teams** — build agents, run models on-prem, connect your own tools.
- **Leaders** — understand ROI, technology trajectories, and how to responsibly target outcomes.

Every lab has a **prompt-first (no-code)** path and a **code-first (Python)** path, and
three levels: **base**, **stretch**, and **hard mode** (e.g. an uncontaminated CTF, your own
MCP, subagents). If the base level feels easy, keep going.

## The labs

One incident — **BOTSv3 Incident B2, an AWS key compromise** spanning email, CloudTrail,
IAM, and EC2 — runs across the whole course, so each lab builds on the last.

| Lab | Day | Time | What you do |
|-----|-----|------|-------------|
| **[Lab 0 — Setup](labs/lab0/lab0_guide.md)** | 1 | 35m | Reach Splunk three ways (MCP harness, `louie-py`, Louie desktop) and run your first query + graph. |
| **[Lab 1 — DIY LLM + decision API](labs/lab1/lab1_guide.md)** | 1 | 60m | Run an OSS LLM locally and watch it hallucinate on SOC questions. Then run [Laya](https://github.com/NandhaKishorM/laya), an open-source Jev-compatible decision model, zero-shot on B2 CloudTrail events: it starts *worse than random* — see what context fixes. |
| **[Lab 2 — AI CTF](labs/lab2/lab2_guide.md)** | 1 | 60m | Investigate B2 — **BYO agent** (Claude Code / OpenCode over MCP) or **running with Louie** — across the six forensic questions, with vibes evals. |
| **[Lab 3 — Skills, timelining & evals](labs/lab3/lab3_guide.md)** | 2 | 75m | Build a BOTS Q skill and a timelining skill, run it on the attack chain, score it against a reference, error-analyze and fix it. Code track: automate via the `louie-py` API. |
| **[Lab 4 — Triage router & contamination](labs/lab4/lab4_guide.md)** | 2 | 75m | Turn Laya into a router that suppresses routine events before they reach the expensive agent: test / validation / holdout splits, temperature calibration, a recall-vs-suppression threshold. Then check whether your agent's CTF score is contamination. |
| **[Capstone — IR report + graphs](labs/capstone/capstone_guide.md)** | 2 | 75m | In-room, instructor-reviewed: an IR report for B2 plus a timeline-entity graph and an infrastructure graph on Graphistry Hub. Alternative: craft malicious events that get past your own classifier. |

Full lab breakdown, tracks, and the mapping to the one-day BSides editions:
**[`labs/README.md`](labs/README.md)**.

## Schedule

Two days, 09:00–17:00 ET, one-hour lunch each day. Room logistics and any day-of changes
go out on Discord.

### Day 1 — Copilot: models, harnesses, investigation

| Time | Length | Block |
|------|--------|-------|
| 09:00–09:40 | 40m | Intro, group intros & use cases |
| 09:40–10:15 | 35m | **Lab 0** — Setup: reach Splunk three ways |
| 10:15–10:35 | 20m | Talk — AI fundamentals: vectors, generation, decision APIs (Jev) |
| 10:35–11:00 | 25m | Talk — Self-hosting: MoE, quantization, open-weight models (incl. 10m break) |
| 11:00–12:00 | 60m | **Lab 1** — DIY LLM + decision API (local LLM, Laya zero-shot) |
| 12:00–13:00 | 60m | Lunch |
| 13:00–13:45 | 45m | Talk — Modern harnesses, thick MCPs & the semantic layer |
| 13:45–14:00 | 15m | Break |
| 14:00–15:00 | 60m | **Lab 2** — AI CTF: BOTSv3 B2 + vibes evals |
| 15:00–15:45 | 45m | Talk — Agents, skills & planning: BOTS baselines, plan.md, planning tricks |
| 15:45–16:00 | 15m | Break |
| 16:00–16:30 | 30m | Talk — Maturity & evolution: evals & AI investigation factories |
| 16:30–17:00 | 30m | Group discussion |

### Day 2 — Commander: evals, security, delivery

| Time | Length | Block |
|------|--------|-------|
| 09:00–09:30 | 30m | Recap & Day 1 leftovers |
| 09:30–10:00 | 30m | Talk — Evals in a SOC setting: adversarial evals & skill testing |
| 10:00–11:15 | 75m | **Lab 3** — Skills, timelining & evals |
| 11:15–11:30 | 15m | Break |
| 11:30–12:15 | 45m | Talk — Securing agents (proxies, auto mode, monitors, MCP vs skills) & compliance |
| 12:15–13:15 | 60m | Lunch |
| 13:15–14:30 | 75m | **Lab 4** — Triage router & contamination |
| 14:30–14:45 | 15m | Break |
| 14:45–16:00 | 75m | **Capstone** — IR report + graphs (or: get past the classifier) |
| 16:00–16:30 | 30m | Talk — RAG & memory, architecture & team patterns, future themes |
| 16:30–17:00 | 30m | Round-robin "one thing you'll try next week", exit survey |

Excluding lunch, that is 14 hours: about 6h20m of labs, 6h30m of talks and discussion,
and 1h10m of breaks.

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

Then do **[Lab 0](labs/lab0/lab0_guide.md)** before Day 1 if you can — it installs
everything and catches account, connector, and credential problems early.

Bring a laptop (8 GB+ RAM) with a modern browser, Wi-Fi, and its power adapter. You'll need:

- **Splunk access** with BOTSv3 loaded (cyber-range credentials provided in-session)
- **Python 3.12+** — required by the Splunk **MCP** server (`splunk-mcp-server2`), the
  `louie-py` code path, and the Laya labs. **Not needed if you only use Louie desktop** (no code).
- **Claude Code CLI** or **OpenCode** (for the BYO-agent path; optional otherwise)
- A free **[Graphistry Hub](https://hub.graphistry.com)** account (for the Louie paths)

**Download these before Wednesday** — conference Wi-Fi will not cooperate with 20 people
pulling gigabytes at once:

```bash
# Laya decision model (Labs 1 and 4) — ~1 GB of weights, no GPU needed
pip install louieai graphistry laya==0.4.8 pandas
python -c "import laya; laya.load()"

# Small local LLM (Lab 1) — ~2 GB. Or use the Colab notebook, which installs Ollama for you.
ollama pull phi3:mini
```

Setup commands and credential handling: see **[`labs/README.md#setup`](labs/README.md#setup)**.

## Working through the labs with an AI assistant

These are teaching exercises. If you pair with an LLM, the intent is that it helps you
*write and debug code* — not that it solves the CTF or opens the answer key for you. The
lab notebooks say so explicitly; the evals labs (Labs 3–4) relax this since the result is
already known.

## Repository layout

```
labs/          the course — one folder per lab, plus labs/README.md
resources/     reference material from the talks (PLAN.md task plan template)
  lab0/ ...    setup: reach Splunk three ways (+ mcp_config.json)
  lab1/ ...    DIY LLM + decision API: local OSS model, Laya zero-shot
  lab2/ ...    AI CTF: BOTSv3 B2 investigation
  lab3/ ...    skills, timelining, evals, API automation
  lab4/ ...    Laya triage router, contamination check (+ offline fallback data)
  capstone/ .. in-room capstone: IR report + graphs
```

> **Credentials never get committed** — `.env` / `env` and the instructor answer key
> are gitignored. Never paste live secrets into a notebook or commit.
