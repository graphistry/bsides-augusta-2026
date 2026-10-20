# Capstone — IR Report with Timeline Graph & Knowledge Graph

> **In the room, ~75 minutes, in pairs.** Instructors walk the room and review as you go
> (see Part 6). Aim for the IR report plus one graph in the slot; finish the second graph and the
> stretch goals at home if you need to.

## Overview

You've investigated the B2 incident (Lab 2), built skills and scored them with evals (Lab 3), and checked the scores are real (Lab 4). Now you'll produce a **complete investigation deliverable** for the B2 AWS Key Compromise incident:

1. **IR Report** — structured incident response document
2. **Timeline-Entity Graph** — interactive Graphistry visualization showing the attack sequence
3. **Infrastructure Graph** — visualization showing attacker vs legitimate infrastructure

**Your deliverables** will be reviewed by instructors. The graphs are shareable — you'll upload them to Graphistry Hub and submit the URLs.

---

## Part 1: The Incident

**BOTSv3 Incident B2: AWS Key Compromise**

You already know this incident from Lab 2. Quick recap:
- Bud (bstoll) pushes AWS credentials to public GitHub at 09:16:06
- Automated attacker validates credentials within 6 seconds
- Attacker generates STS token, attempts privilege escalation, launches 576 EC2 instances for cryptomining
- All instances blocked by service limits
- AWS notifies Frothly at 09:16:53 (47 seconds after first malicious activity)
- IR team disables key by 09:36:12 (~20 minutes)
- STS token not explicitly revoked (critical gap)

Your job: produce the IR report and visualizations that tell this story.

---

## Part 2: The Graph Format

We use a JSON format for Graphistry graphs with nodes and edges. Each node has an ID, label, type, color, and size. Each edge has source, destination, type, and optional timestamp/weight.

### Timeline-Entity Graph

Shows events as nodes connected by `PRECEDES` edges (temporal backbone), with entity nodes (IPs, users, keys) connected by involvement edges.

**Node types and colors:**

| Node Type | Color | Example |
|-----------|-------|---------|
| `event_attack` | Red `#E74C3C` | Attacker validates credentials |
| `event_detection` | Orange `#E67E22` | AWS sends notification email |
| `event_response` | Blue `#4A90D9` | IR team disables key |
| `event_normal` | Gray `#BDC3C7` | Routine activity |
| `entity_attacker` | Dark Red `#C0392B` | Attacker IP |
| `entity_credential` | Purple `#9B59B6` | Compromised access key |
| `entity_user` | Teal `#1ABC9C` | IAM user, employee |

**Edge types:**

| Edge Type | Color | Meaning |
|-----------|-------|---------|
| `PRECEDES` | Gray `#95A5A6` | Temporal order (event A → event B) |
| `USES` | Yellow `#F1C40F` | Actor uses credential/tool |
| `TARGETS` | Red `#E74C3C` | Attack targets a resource |
| `DETECTS` | Orange `#E67E22` | System detects activity |
| `RESPONDS` | Blue `#3498DB` | IR action taken |

### Infrastructure Graph

Shows attacker infrastructure vs legitimate infrastructure as distinct clusters. The key forensic finding is often a `DISTINCT_FROM` edge proving two systems are independent.

**Node types:** `attacker_ip`, `attacker_tool`, `legitimate_ip`, `credential`, `service`

---

## Part 3: Building Your Graphs

### Option A: Use louie (recommended)

In a louie dthread, ask the agent to build the graph JSON:

```
Using the B2 incident data from Splunk (index=botsv3), build a timeline-entity
graph in JSON format. Follow this schema:

{
  "graph_key": "b2_timeline",
  "title": "B2 AWS Key Compromise — Timeline",
  "nodes": [
    {"id": "EV01", "label": "Event description\nTimestamp", "node_type": "event_attack", "color": "#E74C3C", "size": 50}
  ],
  "edges": [
    {"src": "EV01", "dst": "EV02", "edge_type": "PRECEDES", "color": "#95A5A6"}
  ]
}

Include events from 09:16:06 (git push) through 09:36:12 (key disabled).
Add entity nodes for: the compromised key, attacker IPs, the IAM user, the STS token.
Connect events with PRECEDES edges and entities with USES/TARGETS edges.
```

### Option B: Build it in the notebook

Use `capstone.ipynb` — it has helper functions to construct the graph JSON step by step from Splunk query results.

### Option C: Build it manually

Use the reference format and your Lab 2 investigation notes to construct the JSON by hand.

---

## Part 4: Uploading to Graphistry

Once you have your graph JSON, upload it to Graphistry Hub for interactive exploration:

```python
import graphistry
import pandas as pd

graphistry.register(
    api=3,
    server="hub.graphistry.com",
    username="your-username",
    password="your-password"
)

# Load your graph JSON
import json
with open("my_b2_timeline_graph.json") as f:
    graph = json.load(f)

# Convert to DataFrames
nodes_df = pd.DataFrame(graph["nodes"])
edges_df = pd.DataFrame(graph["edges"])

# Upload to Graphistry
g = graphistry.nodes(nodes_df, "id").edges(edges_df, "src", "dst")
g = g.bind(point_title="label", point_color="color", point_size="size")
g = g.bind(edge_title="edge_type", edge_color="color")

url = g.plot(render=False)
print(f"Interactive graph: {url}")
```

Save the URL — this is part of your deliverable.

---

## Part 5: IR Report Template

Your report should follow this structure. The agent can draft it, but you review and edit.

```markdown
# Incident Response Report: B2 AWS Key Compromise

## 1. Executive Summary
- What happened (2-3 sentences)
- Severity: HIGH
- Status: Contained (key disabled), Eradication pending (STS token not revoked)

## 2. Incident Details
- **Detection time**: 09:16:53 UTC (AWS automated detection)
- **Incident type**: Credential compromise + attempted cryptojacking
- **Affected systems**: AWS account 622676721278, IAM user web_admin
- **Attack vector**: Credentials exposed in public GitHub repository

## 3. Timeline
| Time (UTC) | Actor | Event | Evidence |
|------------|-------|-------|----------|
| 09:16:06 | bstoll | Git push completes — credentials now public | WinEventLog |
| 09:16:12 | 35.153.154.221 | GetCallerIdentity SUCCESS | CloudTrail |
| ... | ... | ... | ... |

## 4. Timeline Graph
[Link to Graphistry interactive timeline]

## 5. Attack Chain (MITRE ATT&CK)
- **Initial Access** (T1078.004): Valid cloud credentials exposed on GitHub
- **Persistence** (T1098.001): STS token generated via GetSessionToken
- **Discovery** (T1526): GetCallerIdentity, ListAccessKeys
- **Impact** (T1496): 576 RunInstances attempts for cryptomining

## 6. Infrastructure Graph
[Link to Graphistry infrastructure visualization]

## 7. Indicators of Compromise
| Type | Value | Context |
|------|-------|---------|
| Access Key | AKIAJOGCDXJ5NW5PXUPA | Compromised — disabled |
| STS Token | ASIAZB6TMXZ7LL6JBJQA | Derived — NOT revoked |
| IP | 35.153.154.221 | Initial scanner |
| IP | 139.198.18.205 | Cryptominer (637 calls) |
| IP | 209.107.196.112 | Credential enumerator |
| IP | 82.102.18.111 | ElasticWolf manual recon |
| User Agent | ElasticWolf/5.1.6 | Manual AWS console tool |

## 8. Evidence Log
Key SPL queries used:
- `index=botsv3 sourcetype="aws:cloudtrail" userIdentity.accessKeyId="AKIAJOGCDXJ5NW5PXUPA" | ...`
- (your queries)

## 9. Recommendations
- **Immediate**: Revoke STS sessions, delete compromised key, rotate SSH key
- **Short-term**: Implement pre-commit secret scanning, enable CloudTrail alerts
- **Long-term**: Migrate to IAM roles (no long-term credentials), deploy GuardDuty

## 10. Critical Finding
The STS token (ASIAZB6TMXZ7LL6JBJQA) generated at 09:16:12 was NOT revoked.
Disabling the access key does NOT invalidate existing STS sessions.
This is a common gap in AWS incident response.
```

---

## Part 6: Deliverables

Submit for instructor review (post your report and graph URLs in the class Discord, or show an instructor in the room):

1. **IR Report** (markdown) following the template above
2. **Timeline-Entity Graph** — Graphistry URL showing the attack sequence
3. **Infrastructure Graph** — Graphistry URL showing attacker vs legitimate infra
4. **SPL Queries** — key queries used (so instructors can verify findings)

### Evaluation criteria

| Criteria | What we're looking for |
|----------|----------------------|
| **IR Report completeness** | All sections addressed, executive summary is clear |
| **Timeline accuracy** | Events are correct, in order, with evidence references |
| **Timeline graph quality** | Nodes/edges make sense, temporal backbone is clear, entities are connected |
| **Infrastructure graph** | Shows attacker IPs/tools vs legitimate systems |
| **IOCs** | Complete — all 4 attacker IPs, both credential types, user agents |
| **Critical finding** | Identifies the STS token gap |
| **SPL reproducibility** | Queries can be run against BOTSv3 and produce the claimed results |
| **Recommendations** | Specific and actionable, not generic |

---

## Part 7: Stretch Goals

- **Add a hypothesis graph**: Bipartite graph showing evidence items supporting/contradicting hypotheses (was this automated scanning? coordinated team? insider-assisted?)
- **Devil's Advocate**: Explicitly argue *against* your leading conclusion. What would need to be true for this NOT to be credential theft?
- **MITRE ATT&CK Navigator layer**: Export your attack chain as a Navigator JSON layer
- **Propose your own project**: Have an idea for an AI investigation tool relevant to your work? Discuss with an instructor.

---

## Alternative capstone: get past the classifier

Prefer to attack? Laya and models like it can be prompt-injected through the data they read.
Take your Lab 4 router and craft **malicious CloudTrail events** that it routes as routine:
attacker activity with a benign-looking user agent, a misleading field value, or text aimed at
the model hidden in a string field. Then defend: what enrichment, threshold, or second check
catches your own attack? Report how many of your crafted events got through before and after.
