# Lab 1: DIY LLM + Decision API — Two Kinds of Model on Your Laptop

## Overview

Two parts, both with **no tools and no Splunk**, both on your own laptop:

- **Part A** runs a small open-source LLM and asks it the B2 questions closed-book. It
  writes text, and it makes things up.
- **Part B** runs [Laya](https://github.com/NandhaKishorM/laya), an open-source, Jev-compatible
  *decision model*. It doesn't write text: it answers typed yes/no and multiple-choice
  questions with probabilities, in milliseconds on a CPU. You point it at B2 CloudTrail
  events and find out whether it can tell attacker from routine out of the box.

Lab 0 must be done first only for Lab 2. Lab 1 itself needs no Splunk access.

**Time:** ~60 minutes — Part A ~20m, Part B ~35m •
**Notebooks:** `lab1_ollama_colab.ipynb` or `lab1_ollama_local.ipynb` (Part A) · `lab1_laya_zeroshot.ipynb` (Part B)

**Download before the session** (conference Wi-Fi will not cooperate):
```bash
ollama pull phi3:mini                                  # Part A, ~2 GB (or use Colab)
pip install louieai graphistry laya==0.4.8 pandas      # Part B, Python 3.10+
python -c "import laya; laya.load()"                   # Part B, ~1 GB of weights
```

---

## Part A — Run an OSS LLM locally and watch it hallucinate (~20 min)

Before you give a model any tools, see what it does **without** them. You'll run a small
open-source model on your own laptop with [Ollama](https://ollama.com) and ask it the
same BOTSv3 questions you'll investigate for real in Lab 2 — closed-book, no Splunk.

A small local model will answer confidently and wrongly. That's the point: this is the
baseline every later lab improves on (tools in Lab 2, skills and evals in Lab 3, contamination in Lab 4 —
where you'll run this exact closed-book test again, against a frontier model, and get a
much more interesting answer).

### Two ways to run it

**No install — Colab.** Open **`lab1_ollama_colab.ipynb`** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/graphistry/bsides-augusta-2026/blob/main/labs/lab1/lab1_ollama_colab.ipynb)
and run it top to bottom on a T4 GPU runtime. It installs Ollama in the runtime, pulls a
model, and runs the questions below for you.

**Locally — Ollama on your laptop.** Do the pull before the session; conference Wi-Fi will
not cooperate:
```bash
curl -fsSL https://ollama.com/install.sh | sh     # macOS/Windows: installer from ollama.com
ollama pull phi3:mini                             # ~2 GB, runs on 8 GB RAM, CPU is fine
# more RAM / a GPU? try:  ollama pull llama3.1:8b   (~4.7 GB)
ollama run phi3:mini "Say hi in five words."       # smoke test
```

### Ask it SOC questions, closed-book
In a terminal:
```bash
ollama run phi3:mini
```
Paste, one at a time, prefixing each with the closed-book instruction:

> Do NOT use any tools. Answer from your own knowledge only. If you are unsure, say "I don't know". Reply on one line as `ANSWER: <answer>`.
>
> Question: Bud accidentally commits AWS access keys to an external code repository. Shortly after, he receives a notification from AWS that the account had been compromised. What is the support case ID that Amazon opens on his behalf?

Then the same for:

> Using a leaked AWS key AKIAJOGCDXJ5NW5PXUPA, the adversary makes an unauthorized attempt to describe an account. What is the full user agent string of the application that originated the request?

> The adversary attempts to launch an Ubuntu cloud image as the compromised IAM user. What is the codename for that operating system version in the first attempt? Two words.

And one that isn't a lookup at all:

> Write the SPL to find the AWS support-case notification email in the Splunk BOTSv3 dataset.

Both notebooks (`lab1_ollama_colab.ipynb`, or `lab1_ollama_local.ipynb` for a
local Ollama) run all four and print each answer next to the expected one, so you don't
have to eyeball it.

### What to watch for
- **"I don't know" on the pure lookups is the good outcome.** A case ID or a user-agent
  string has no pattern to guess from, and a decent model admits it — *because the prompt
  lets it*. Then ask again demanding a best guess and watch what replaces it: a
  confident denial of the premise, a refusal ("unauthorized access"), or an invented value.
- **The hallucinations come where there's a plausible pattern.** Expect a real-but-wrong
  Ubuntu codename, and SPL that parrots words from the question and invents the rest.
- **Over-refusal is a failure mode too.** Small open models often treat benign forensic
  questions (a user-agent string in a log) as attack requests. Note it when it happens. In Lab 2 you'll
  watch an agent with tools discover the real ones (`stream:smtp`, `aws:cloudtrail`).
- **Try it twice.** Same question, new session: different wrong answer? That
  non-determinism is why the Lab 3 eval loop runs every question several times.
- **CPU vs GPU, small vs big.** If you have both `phi3:mini` and `llama3.1:8b`, compare
  speed and answers. The bigger one is slower and *still* wrong — size doesn't fix
  missing data.

> **Neither works?** Pair with a neighbour, or run the same closed-book prompt through
> Claude Code with tools stripped (the flags are in `../lab4/contamination_test_prompts.md`).
> You'll get a preview of Lab 4's contamination result.

**Discussion seed:** when *do* local models make sense for security work? Air-gapped,
fly-away kits, embedded, hard real-time, scale, cost — hold that thought for Part B.

---

## Part B — A decision API on your laptop: Laya zero-shot (~35 min)

Open **`lab1_laya_zeroshot.ipynb`** and run it top to bottom. It uses the offline B2
CloudTrail set in `../lab4/data/` (374 events; attacker rows rebuilt from the B2 evidence,
routine rows synthetic — the `provenance` column says which), so it works without Splunk.

What you do:

1. **Load Laya and the events.** First load takes ~10 s once the weights are cached.
2. **Label them** from the B2 IR report: an event is *attacker* if it comes from one of the
   four attacker IPs or uses the leaked key. That is your answer key.
3. **Split before you look** into Test / Validation / Holdout. Today you only touch Test.
4. **Ask Laya zero-shot:** one yes/no question per event, "is this attacker activity?", and
   score it with **AUC** (does it rank attacker above routine?) and **Cohen's Kappa** (does it
   decide correctly, corrected for chance?).
5. **Pull two levers:** give it the alert context, then put analyst tradecraft into the
   question's criteria. Re-score after each.

### AUC vs. Kappa in one minute

Both compare the model with your answer key, but they ask different questions.

- **AUC** asks: does the model *rank* attacker events above routine ones? Pick one random
  attacker event and one random routine event; AUC is the probability the attacker event
  got the higher score. 0.5 is a coin flip, 1.0 is a perfect ordering, below 0.5 means it
  ranks backwards. It ignores the threshold entirely.
- **Cohen's Kappa** asks: at a chosen cutoff (0.5 today), are the model's *decisions*
  better than guessing? Plain accuracy would lie here — 60% of the events are routine, so
  a model that always says "routine" is 60% accurate and useless. Kappa subtracts the
  agreement you would get by chance: 0 is guessing, 1 is perfect. Rough guide: 0.7 is a
  decent first prompt, 0.8 good, above 0.9 great.

Read them together. High AUC with Kappa at 0 means the signal is there but every score
sits on the wrong side of the cutoff, so the fix is the threshold, not the model (Lab 4).
Good Kappa with mediocre AUC means you tuned a cutoff to one dataset and it may not
survive new data. And temperature calibration (Lab 4) never moves a score across 0.5, so
it can fix *how much to trust* the number without changing Kappa at all.

### What to watch for
- **Zero-shot is worse than a coin flip** (AUC ≈ 0.37 on the fallback data). Fast and local
  does not mean useful.
- **AUC can jump while Kappa stays at 0.** Adding context makes it rank better, but every
  answer is still below 0.5. Where to cut is a separate decision — that's Lab 4.
- **Tradecraft in the question is the big lever** (AUC ≈ 0.85). It's the same move as a
  skill file in Lab 3: analyst knowledge turned into the prompt.
- 🟡 **Stretch:** edit the wording of the criteria and beat your neighbour's AUC.

**Speed:** ~10 ms per event on a GPU, ~0.4–0.7 s per event on a laptop CPU. On CPU the
notebook scores a 160-event sample so it fits the slot.

**Discussion seed:** when *do* local models make sense for security work? Air-gapped,
fly-away kits, embedded, hard real-time, line-rate triage, cost. In Lab 4 you turn Laya into
a router that keeps the expensive agent off routine events.

---

## Success criteria

- **Part A:** the local model answers all four prompts (wrongly, confidently) and you've
  noted at least one invented sourcetype or field name in its SPL.
- **Part B:** you have a zero-shot AUC and a best AUC after the two levers written down.
  You'll need them in Lab 4.

## Troubleshooting

- **Ollama won't install or is too slow:** use `lab1_ollama_colab.ipynb`, or pair with a neighbour.
- **`ModuleNotFoundError: laya`:** `pip install laya==0.4.8` in the same environment as your Jupyter kernel.
- **Laya download stalls:** pair with a neighbour who has the weights cached, and download yours at the break.
- **Very slow on CPU:** leave `SAMPLE_N = 160` in the settings cell (lower it to 80 if needed).
