---
name: databricks-docs
description: Look up authoritative, up-to-date Databricks documentation covering the core platform, Unity Catalog data governance and security, data engineering (Lakeflow Jobs and Declarative Pipelines), SQL and analytics, machine learning and AI (agents, MLflow, model serving), developer tools (CLI, SDKs, asset bundles), compute, administration, integrations, migration, and troubleshooting. Use when the user asks how a Databricks feature works, what a config field or SQL clause does, how to set up jobs, pipelines, clusters, catalogs, or agents, when troubleshooting a Databricks error, or when you need current official docs rather than training-cutoff knowledge. Also trigger on Chinese phrasing such as 数砖 / Databricks 文档 / 官方文档 / 怎么配置 / 如何设置 / 报错 / 数据血缘 / 权限 / 作业调度 / 流水线.
argument-hint: [topic]
allowed-tools: Bash(python3 *), WebFetch
---

# Databricks Docs

Answers Databricks questions from the official docs on demand: searches a cached copy of the
47 KB `llms.txt` index by section or regex, then reads the matching pages with WebFetch. Always
prefer this skill over recalling docs from memory — Databricks renames and reorganizes fast
(`dlt/` became `ldp/`, "Delta Live Tables" became "Lakeflow Declarative Pipelines", "Workflows"
became "Lakeflow Jobs").

If the user passed an argument (`$ARGUMENTS`), treat it as the topic. Otherwise infer it.

## When to use this skill

The index's own 15 sections, largest first:

- **Machine learning and AI** — agents, MLflow, model serving, feature store, Genie
- **Core platform** — Unity Catalog, catalogs, schemas, volumes, workspace, compute, notebooks
- **Developer tools** — CLI, SDKs, asset bundles, VS Code extension, REST API, CI/CD
- **Data governance and security** — permissions, row filters and column masks, lineage, audit
- **Data engineering** — Lakeflow Jobs, Lakeflow Declarative Pipelines, ingestion, Auto Loader
- **SQL and analytics** — SQL warehouses, queries, dashboards, alerts
- **Data sources and formats** — Delta Lake, tables, external data, connectors
- **Overview and getting started**, **Administration**, **Reference and language-specific
  guides**, **Integrations and connectors**, **Migration and best practices**, **Specialized
  features**, **Additional resources**, **Troubleshooting and support**

Out of scope:

- **Azure Databricks.** `docs.databricks.com/azure/…` does not exist; Microsoft hosts those
  docs on `learn.microsoft.com`. This index covers AWS (default) and GCP.
- **DevHub** (`developers.databricks.com`) — a separate site with its own 19 KB `llms.txt`,
  not covered here.
- **Your workspace's actual data.** Reading tables, running SQL, or inspecting Unity Catalog
  objects needs the Databricks CLI or a Databricks MCP server, not this skill.

## How this site works

Measured 2026-07-30; the numbers and the reasoning are in the top entry of
[references/mechanism.md](references/mechanism.md).

- **Index**: `https://docs.databricks.com/llms.txt` — 47,150 B (~11,787 tokens), 252 entries,
  15 sections, 98% with prose descriptions.
- **Coverage**: 252 index entries vs 5,645 sitemap URLs (**4.5%**) — **hub-level**. Many entries
  point at an area landing page, not a leaf. Expect a second hop for specific topics.
- **Content**: HTML only. Every plain-text convention 404s (`.md`, `/index.md`, `.txt`, and an
  `Accept: text/markdown` header all fail). Pages measure 21 KB–51 KB of raw HTML — use
  WebFetch, which converts to markdown first. Never curl a page body.
- **Gotchas**:
  - Index URLs are cloud/locale-neutral (`/jobs/scheduled`) and **301 to `/aws/en/…`**. Follow
    the redirect; cite the URL that actually served the content.
  - `www.databricks.com/llms.txt` is the **marketing** index (36 entries, mostly product pages).
    It is not this index. Its "Databricks-owned LLM manifests" section is what points here.
  - The docs host publishes no `llms-full.txt`. The marketing site links one — never fetch it.
  - Docs exist in English, Japanese, and Portuguese only. There is no Chinese edition.

## Procedure

### 1. Find candidate pages

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/docs_query.py search '<term>|<synonym>|<the word the docs would use>'
```

The index is fetched once and cached for 24 h, so repeat queries cost no requests. Only matching
lines enter context — never load the whole index.

Routing commands, cheapest first:

| Command | Measured cost | Use when |
| :--- | :--- | :--- |
| `search '<regex>'` | ~60–1,300 tok | always start here |
| `sections` | ~253 tok | search missed and you need the map |
| `section '<name>'` | 222–1,617 tok | full recall inside one area |

Databricks renames things, so search the current *and* the former name as one alternation —
`'Delta Live Tables|declarative pipeline|ldp'`, `'Workflows|Lakeflow Jobs'`.

### 2. If the search comes back empty

Do **not** conclude the topic is undocumented. Escalate:

1. Widen with synonyms — the docs' word is often not the user's. Measured on this site:
   `cron` returns 0 matches; `'schedul|orchestrat|trigger|recurring'` finds **Job scheduling**.
   `row-level security` returns 0; `'row filter|column mask|fine-grained'` finds **Row and
   column filters**.
2. If the query was not in English, retry with English terms. This index is English-only, and
   there is no Chinese edition of the docs at all — `数据血缘` scores 0 matches, `lineage`
   finds the page. A non-English miss says nothing about coverage.
3. `sections`, then `section '<most plausible>'` for full recall inside it.
4. **Descend a hub entry.** The index covers 4.5% of the site, so the leaf you want often is
   not listed at all — only its area landing page is. WebFetch the landing page and read its
   own child links. Measured: `vacuum|retention` returns 0 index matches, but the `/delta/`
   landing page links straight to `/tables/operations/vacuum`.
5. Only then say it is not in the docs, and state what you searched.

### 3. Read the pages

```
WebFetch url=<url-from-search>
        prompt="<the user's actual question, not 'summarize this page'>"
```

Pages are HTML-only (21 KB–51 KB raw). WebFetch converts to markdown before it reaches context —
do not curl them. `docs_query.py get <url>` exists but only prints this instruction, because
piping raw Databricks HTML into context wastes tokens.

Fetch **1–3 pages per batch**, then judge whether that answers the question. Loop if not, to a
cap of **9 pages**. At 9 and still short, stop and tell the user what you read and what is
missing — do not silently continue or fill the gap with guesses.

## Context budget

| Step | Measured cost | Notes |
| :--- | :--- | :--- |
| `search` (narrow) | ~58 tok | `row filter\|column mask\|fine-grained` → 230 B |
| `search` (typical) | ~160–200 tok | `lineage` → 643 B; `schedul\|...` → 781 B |
| `search` (broad) | ~1,290 tok | `Unity Catalog` → 5,147 B, 23 hits |
| `sections` | ~253 tok | 1,013 B |
| `section` | 222–1,617 tok | Troubleshooting 890 B … ML and AI 6,468 B |
| page via WebFetch | ~0.3–1k tok | from 21–51 KB of raw HTML |

Typical question: search + 1–2 pages ≈ **1–2k tokens**. Loading the index whole would be
~11,787 tokens, which is why nothing here does that. Read **one** section at a time; if you
cannot tell which section to read, that is a signal to search again with better terms, not to
load several.

## Rules

- **Never invent a doc URL.** Not in the index → search wider, or descend a hub. Databricks
  renames slugs (`dlt/` → `ldp/`); an invented URL is a confident 404.
- **Never load the whole index**, and never touch the marketing site's `llms-full.txt`.
- **Cite the URL that served the content** — the post-redirect `/aws/en/…` one.
- **A 404 on a page URL means the index is stale** — re-run
  `/docs-skill-builder check .claude/skills/databricks/skills/databricks-docs`.
- **Say which cloud you are answering for.** The default is AWS; GCP pages live under
  `/gcp/en/` and can differ. Azure is not on this host at all.
- **Pass through what the docs say.** The user wants current authoritative behavior, not a
  synthesis with your prior knowledge.
