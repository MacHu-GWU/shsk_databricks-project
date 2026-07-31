# databricks-docs

An on-demand lookup skill for the official Databricks documentation. It answers Databricks
questions from `docs.databricks.com` at query time instead of from training-cutoff memory —
which matters for this vendor in particular, because Databricks renames things aggressively
(`dlt/` → `ldp/`, Delta Live Tables → Lakeflow Declarative Pipelines, Workflows → Lakeflow Jobs).

---

## How it works

Two independent mechanisms, both chosen from measurements rather than assumptions. The numbers,
the reasoning, and the rejected alternatives are in the top entry of
[references/mechanism.md](references/mechanism.md), an append-only log.

### Finding the page — T1 section-routed, plus T4 hub-descend

The index is `https://docs.databricks.com/llms.txt`: 47,150 B, 252 entries, 15 sections, 98% of
them carrying a real prose description. That is a good index — but it covers **4.5%** of the
site (252 entries against 5,645 sitemap URLs). It tells you *which area*, often not *which page*.

So the skill does two things:

1. Filters the index outside the model's context — `search` prints only matching lines, so a
   query costs 60–1,300 tokens instead of the 11,787 it would take to load the index whole.
   The index is cached for 24 h, so repeat queries cost no network requests.
2. When the answer is not in the index at all, **descends** — fetches the area landing page and
   follows its own child links. Measured: `vacuum` returns zero index matches, yet
   `/tables/operations/vacuum` is one link away from the `/delta/` landing page.

### Reading the page — C1, WebFetch only

Databricks serves HTML and nothing else. `.md`, `/index.md`, `.txt`, an `Accept: text/markdown`
header, and `?plain=1` were all tested; three 404 and three return the identical HTML. Pages
run 21 KB–51 KB raw, so they are read with WebFetch — which converts HTML to markdown *before*
anything reaches the context window. `docs_query.py get` deliberately refuses to download page
bodies and tells you to use WebFetch instead.

### Recall

The failure mode for a docs skill is silent: the agent searches, gets nothing, and reports "not
documented". `SKILL.md` encodes an escalation ladder — widen with synonyms, translate
non-English queries, list sections, read one whole section, descend a hub — and only then
conclude absence, stating what was searched. Two of these are load-bearing here:

- **Vocabulary mismatch.** `cron` → 0 matches; `schedul|orchestrat|trigger|recurring` → the
  **Job scheduling** page. `row-level security` → 0; `row filter|column mask` → **Row and column
  filters**.
- **Language.** Databricks publishes docs in English, Japanese, and Portuguese — no Chinese
  edition. `数据血缘` scores 0; `lineage` finds the page. A non-English miss says nothing about
  coverage.

---

## Usage

```
/databricks-docs how do I schedule a job with a cron expression
```

Or just ask a Databricks question — the description triggers on English and Chinese phrasing.

Under the hood:

```bash
python3 scripts/docs_query.py search 'schedul|orchestrat|trigger'
python3 scripts/docs_query.py sections
python3 scripts/docs_query.py section 'Data engineering'
python3 scripts/docs_query.py stats
python3 scripts/docs_query.py refresh
```

`scripts/docs_query.py` is copied verbatim from `docs-skill-builder`; everything site-specific
lives in `scripts/docs-source.json`. Do not fork the script — change the JSON.

The cached index lands in `~/.cache/claude-docs-skills/databricks-docs/index.txt`. It is derived
and disposable; delete it any time, and never commit it.

---

## Scope

Covered: the 15 sections of the docs index — core platform and Unity Catalog, data engineering
(Lakeflow Jobs and Declarative Pipelines), SQL and analytics, machine learning and AI, developer
tools, governance and security, administration, integrations, migration, troubleshooting.

Not covered:

| Out of scope | Where it lives |
| :--- | :--- |
| Azure Databricks | `learn.microsoft.com` — `docs.databricks.com/azure/…` 404s |
| DevHub | `developers.databricks.com`, its own 19,085 B `llms.txt` |
| Your workspace's data | the Databricks CLI or a Databricks MCP server |

The index covers AWS (the default target of every neutral URL) and GCP under `/gcp/en/`. Pages
can differ between them; the skill is told to say which cloud it answered for.

## Relationship to the official Databricks Claude Code plugin

Databricks ships its own plugin with hand-written skills for the CLI, Apps, Lakebase, Model
Serving, Lakeflow Jobs, Spark Declarative Pipelines, and DABs. That is **complementary**, not
redundant: it encodes opinionated workflows, while this skill reads the live documentation. No
official documentation MCP server or docs search API exists as of 2026-07-30 — the Databricks
Managed MCP servers expose workspace *data*, not docs.

## Maintenance

```
/docs-skill-builder check .claude/skills/databricks/skills/databricks-docs
```

Re-probes the site and diffs against the top entry of
[references/mechanism.md](references/mechanism.md), then appends its own entry — including when
the answer is "nothing changed", because a check that leaves no trace is indistinguishable from a
check that never ran. That log is append-only: entries are never rewritten, so it records what
was believed at the time and why that stopped being true.

The triggers that would change the design — `.md` twins appearing, coverage rising, the index
moving — are under **What would overturn it** in the top entry, alongside the hand-written assets
a rebuild must not throw away.
