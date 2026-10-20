# Lab 0: Setup — Reach Splunk Three Ways

## Overview

The workshop lets you drive Splunk three different ways. Lab 0 gets all three working by
running the *same* first query through each:

1. **Claude Code over Splunk MCP** — a coding agent (Claude Code, or another harness
   like OpenCode / Codex) calling Splunk through MCP. The harness path used in **Lab 2**.
2. **louie-py** — the code-first client: Python that queries Splunk and returns
   dataframes *and* Graphistry graphs. The code track in **Lab 3** and the capstone.
3. **Louie desktop** — the same Louie copilot in a GUI, no code. The no-code track in
   **Lab 3** and the capstone.

**The shared task — a first look at the B2 incident.** Pull the AWS CloudTrail activity
for the compromised access key `AKIAJOGCDXJ5NW5PXUPA` from BOTSv3 (`index=botsv3
sourcetype=aws:cloudtrail`), counted by source IP, API call, and error code — and, for
the Louie approaches, draw it as an **attacker IP → AWS API call** graph with edges
coloured by outcome (success vs. denied). It's the same shape as a firewall src → dst
graph, and it's the incident you'll investigate for real in Lab 2: four attacker IPs
fanning out into the calls they tried, and which ones IAM let through.

```spl
index=botsv3 sourcetype="aws:cloudtrail" userIdentity.accessKeyId="AKIAJOGCDXJ5NW5PXUPA"
| stats count by sourceIPAddress, eventName, errorCode
```

**You'll need a free Graphistry Hub account.** The two Louie approaches (2 and 3) sign
in with Graphistry Hub credentials, and the graphs render on that server — so if you
don't already have one, sign up (free) at
[**hub.graphistry.com**](https://hub.graphistry.com). It's the default `GRAPHISTRY_HOST`
for the workshop; the username/password (or personal key) from there is what goes in
your `.env`.

**Do this before the workshop if you can.** You only strictly need *your* track working,
but trying all three is the point — and it catches account, connector, and install
problems early.

**Time:** ~35 minutes (less if you did it beforehand) • **Notebook:** `lab0_setup.ipynb`

---

## Approach 1 — Claude Code over Splunk MCP

A coding agent talks to Splunk through Splunk's own MCP server,
[`splunk/splunk-mcp-server2`](https://github.com/splunk/splunk-mcp-server2). It provides
SPL validation guardrails, sensitive-data sanitization, and supports both stdio and SSE
transport. The same `mcp_config.json` works with Claude Code, OpenCode, Codex, or Cursor.

### Prerequisites
```bash
# Check Claude Code is installed
claude --version

# Check Python
python --version   # 3.12+
```

**Python 3.12+ is a requirement of the Splunk MCP server** (`splunk-mcp-server2`). It's
needed for this path and the `louie-py` path — but **not** for Louie desktop (Approach 3),
which runs entirely in the app.

### Install the Splunk MCP server
```bash
# Clone the repo
git clone https://github.com/splunk/splunk-mcp-server2.git
cd splunk-mcp-server2/python

# Create a virtual environment and install
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set the path so the MCP config can find it:
```bash
export SPLUNK_MCP_PATH="/path/to/splunk-mcp-server2"
```

### Configure Splunk credentials
```bash
export SPLUNK_HOST="your-splunk-host.company.com"
export SPLUNK_PORT=8089
export SPLUNK_USERNAME="your-username"
export SPLUNK_PASSWORD="your-password"
```

### MCP server configuration
`mcp_config.json` lives in this lab's folder (`lab0/`) and wires the env vars
above into the server:
```json
{
  "mcpServers": {
    "splunk": {
      "command": "${SPLUNK_MCP_PATH}/python/.venv/bin/python",
      "args": ["${SPLUNK_MCP_PATH}/python/server.py"],
      "cwd": "${SPLUNK_MCP_PATH}/python",
      "env": {
        "SPLUNK_HOST": "${SPLUNK_HOST}",
        "SPLUNK_PORT": "${SPLUNK_PORT}",
        "SPLUNK_USERNAME": "${SPLUNK_USERNAME}",
        "SPLUNK_PASSWORD": "${SPLUNK_PASSWORD}",
        "TRANSPORT": "stdio"
      }
    }
  }
}
```
This launches `splunk-mcp-server2` over stdio, exposing:

- **`validate_spl`** — check an SPL query for risk before running it
- **`search_oneshot`** — run an SPL query and return results
- **`search_export`** — run a query and export results (for larger datasets)
- **`get_indexes`** — list the indexes on the Splunk instance
- **`get_saved_searches`** — list saved searches
- **`run_saved_search`** — run one of them
- **`get_config`** — show the server's current configuration

The server includes built-in **SPL validation guardrails** and **sensitive-data
sanitization** (masks credit card numbers, SSNs, etc. in results).

The notebook's env-check and config cells confirm the `SPLUNK_*` vars are set, that
`claude`/`python` are installed, that `server.py` exists, and that `mcp_config.json`
parses. Then run your first query in a **terminal** (from this `lab0/` folder):
```bash
claude --mcp-config ./mcp_config.json
```
> Using the Splunk MCP tools, search `index=botsv3 sourcetype=aws:cloudtrail` for events where `userIdentity.accessKeyId` is `AKIAJOGCDXJ5NW5PXUPA`, count them by `sourceIPAddress`, `eventName` and `errorCode`, and show me the table.

You should see a handful of source IPs, a couple of dozen distinct API calls, and a mix of
empty `errorCode` (success) and denials.

Graphs are a Louie feature — that's Approaches 2 and 3.

---

## Approach 2 — louie-py (code)

Louie holds the **Splunk connector**, runs the agents (`SplunkAgent` writes the SPL),
and hands back dataframes (`lui.df`) *and* Graphistry graphs (`lui.g` / `lui.url`).

**Connect** — put credentials in `.env` at the repo root, then run the connect cell:
```bash
cp .env.example .env    # then edit: GRAPHISTRY_HUB_KEY_ID / _SECRET (or username/password), LOUIE_HOST
```

**Query + graph**
```python
lui("In index=botsv3 sourcetype=aws:cloudtrail, find every API call made with access key AKIAJOGCDXJ5NW5PXUPA (field userIdentity.accessKeyId) and count the events by sourceIPAddress, eventName and errorCode. Return the table.", agent="SplunkAgent")
df = lui.df   # sourceIPAddress, eventName, errorCode, count
g = (graphistry.edges(df, "sourceIPAddress", "eventName")
       .bind(edge_weight="count")
       .encode_edge_color("outcome", categorical_mapping={"success": "#2ECC71"}, default_mapping="#E74C3C"))
g.plot(render=False)
```
The notebook derives `outcome` (success when `errorCode` is empty) and re-aggregates if the
agent returned raw events instead of counts; set `SRC_COL` / `DST_COL` if column names differ.

> **Learn more — go deeper on graph hunting.** You just turned a table into a Graphistry
> graph in one line. If that clicked, we run a whole workshop on investigating with graphs
> (shaping nodes/edges, visual encodings, GFQL, UMAP hunting):
> **[Graph hunting at BSides →](https://github.com/graphistry/bsideslv-training-2026)** —
> our graph training at BSides.

---

## Approach 3 — Louie desktop (no code)

The same copilot in a GUI, using the **same Louie account and Splunk connector** as
Approach 2 — so if Approach 2 worked, this will too. **No Python, no CLI, no MCP server**
— just the desktop app, so this is the lightest-weight way in.

1. Install **Louie desktop** — download the installer for your OS from
   **https://download.louie.ai**, run it, and open the app.
2. Sign in with your Graphistry Hub / Louie credentials (the same ones in your `.env`).
3. New thread → select the **SplunkAgent** / Splunk connector.
4. Ask: *"In index=botsv3 sourcetype=aws:cloudtrail, find every API call made with access key AKIAJOGCDXJ5NW5PXUPA (field userIdentity.accessKeyId) and count the events by sourceIPAddress, eventName and errorCode. Return the table."*
5. Follow up: *"Add a column called outcome that is "success" when errorCode is empty and "denied" otherwise. Then graph sourceIPAddress → eventName with edges colored by outcome: green for success, red for denied."* — the app renders it inline.

   > Why the extra column: `errorCode` is blank on successful calls, and colouring straight
   > off a column that mixes blanks and strings makes Graphistry's encoder throw. Deriving
   > `outcome` first sidesteps it.

> Remaining desktop specifics (connector name, sign-in) are confirmed at the
> session; grab a facilitator if anything isn't obvious.

---

---

## Success criteria

- **Approach 1:** env vars set, `claude`/`python` found, `splunk-mcp-server2: found`,
  `mcp_config.json` prints, harness returns a table in the terminal.
- **Approach 2:** `packages installed` → `Authenticated with ...` → `louie-py ready.`,
  `Got N rows x M columns`, and a `SUCCESS` URL opening an attacker IP → API call graph
  (four source IPs; green successes, red denials).
- **Approach 3:** the desktop app returns a table and renders the graph.

Get **at least your track** working and you're ready for Lab 2.

## Troubleshooting

See the table at the bottom of `lab0_setup.ipynb` — it covers unset `SPLUNK_*` vars, a
missing `claude` CLI or MCP server, the `mcp_config.json` path, missing Louie
credentials, an unconfigured connector (affects Approaches 2 and 3), a query that
returns no rows, plot/connection errors, missing edge columns, and desktop sign-in.

