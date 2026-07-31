# databricks-docs — mechanism log

How this skill reads Databricks' documentation, and why. Newest entry first; the top entry
describes the current mechanism. Entries are appended, never rewritten.

## 2026-07-30 — build · docs-skill-builder 0.1.1

**Verdict.** First entry. Establishes the mechanism: section-routed regex search over
`docs.databricks.com/llms.txt` with a hub-descend second hop, and WebFetch for page bodies.

**How the site is read.** The index is `https://docs.databricks.com/llms.txt` — an `llms.txt`
manifest of 47,150 B (~11,787 tokens) holding 252 entries across 15 `##` sections, 98% of them
carrying a real prose description and none bare. Sections run from 890 B (Troubleshooting and
support, 5 entries) to 6,468 B (Machine learning and AI, 32 entries). The AWS/English sitemap
lists 5,645 URLs, so the index covers **4.5%** of the site: it is a curated hub index, not a page
list. Queries go through `scripts/docs_query.py`, which caches the index for 24 h under
`~/.cache/claude-docs-skills/` and prints only matching lines, so one search costs 60–1,300
tokens instead of the 11,787 a whole-index load would. Page bodies are HTML and nothing else —
21,136 B for `/jobs/scheduled`, 24,639 B for the Unity Catalog landing page, 50,782 B for
`/getting-started/concepts` — and are read with WebFetch, which reduces HTML to markdown outside
the context window. Index URLs are cloud- and locale-neutral and 301 to `/aws/en/…`; `/gcp/en/`
is a real, slightly different variant (50,298 B for the same page) and `/azure/en/` 404s, because
Microsoft hosts the Azure Databricks docs on `learn.microsoft.com`. `robots.txt` declares seven
sitemaps — aws/gcp × en/ja/pt, plus `/api/` — so there is no Chinese edition to fall back on.

**Why this design.** Index tier **T1 + T4**, content tier **C1**. 47,150 B sits inside the
40–150 KB band with 15 real sections and 98% prose, comfortably past the ≥ 4 sections / ≥ 50%
prose bar for section routing, with `search` kept as the flat escape hatch. T4 is layered on
because of the 4.5% coverage figure alone, and that was verified rather than assumed:
`vacuum|retention` returns zero index matches, yet `/tables/operations/vacuum` is one link from
the `/delta/` landing page. Without the second hop this skill would confidently miss most of the
site. C1 because all six registered plain-text conventions failed — `.md`, `/index.md` and
`.txt` 404 against a calibrated 12,999 B error page, while `Accept: text/markdown` and `?plain=1`
return the identical 50,782 B of HTML; `.md` and `/index.md` were re-checked by hand against the
canonical `/aws/en/` path and 404 there too. Rejected: T0, because 11,787 tokens per question is
roughly ten times the measured search-then-fetch path; T2, because descriptions this good make
section routing genuinely informative, and T2 is what you fall back to when the map is useless;
T3, because the sitemap has 5,645 URLs and zero descriptions — a recall backstop, not a primary
index; T5, which fails the catalog's first condition outright (prose is 98%, not under 30%) and
would commit a second source of truth that only decays.

Also rejected *as the index*: `www.databricks.com/llms.txt`, which the build request pointed at.
It is the marketing manifest — 12,873 B, 36 entries, 24 of them `www` product pages, exactly one
pointing into the docs. It earned its place as a discovery artifact rather than as the index: its
own "Databricks-owned LLM manifests" section is what names `docs.databricks.com/llms.txt`.

Vendor tooling was checked so this skill would not silently duplicate it. Databricks ships an
official Claude Code plugin with hand-written skills for the CLI, Apps, Lakebase, Model Serving,
Lakeflow Jobs, Spark Declarative Pipelines and DABs — complementary, since it encodes opinionated
workflows while this skill reads the live text. The Databricks Managed MCP servers expose
workspace *data*, not documentation. No official docs MCP server or docs search API exists.

**Acceptance test.** All four catalog tests run and measured. Easy lookup: `Unity Catalog`, 23
hits, 5,147 B. Vocabulary mismatch: `cron` → 0 matches, `schedul|orchestrat|trigger|recurring` →
4 hits, 781 B, landing on **Job scheduling**; and `row-level security` → 0, `row filter|column
mask|fine-grained` → 1 hit, 230 B, landing on **Row and column filters**. Hub descend:
`vacuum|retention` → 0, reached via the `/delta/` landing page. Non-English: `数据血缘` → 0,
`lineage` → 3 hits, 643 B, landing on **Data lineage**. Content fetch: WebFetch on
`/jobs/scheduled`, 21,136 B of raw HTML, returning the Quartz cron syntax and the 10 s minimum
interval between runs. No test needed the whole index.

**What would overturn it.** `.md` twins appear → C1 becomes C0, a large token win worth
rebuilding for on its own. Coverage rises past roughly 30%, meaning the index starts listing
leaves → drop the T4 second hop, since the extra fetch stops paying for itself. Prose
descriptions fall below 50%, or the index grows past 150 KB → T1 collapses to T2 and `search`
should be documented as the primary path rather than the escape hatch. A Chinese locale appears
in `robots.txt` (today: en, ja, pt only) → the translate-first rule needs revisiting. Databricks
ships an official docs MCP server or search API → this skill may become redundant; re-evaluate
before maintaining it. The index moves, 404s, or goes behind auth → broken, not degraded; rebuild.

**Rebuild must preserve.** The Chinese trigger phrases in `description` (数砖, Databricks 文档,
官方文档, 怎么配置, 如何设置, 报错, 数据血缘, 权限, 作业调度, 流水线) — the index is English-only
and no script can derive them; they exist because this user works in Chinese. The rename pairs in
the search guidance (`dlt/` → `ldp/`, Delta Live Tables → Lakeflow Declarative Pipelines,
Workflows → Lakeflow Jobs), which come from watching the vendor rather than from the index, and
are the highest-value recall hint for this site. The out-of-scope list — Azure on
`learn.microsoft.com`, DevHub on `developers.databricks.com` with its own 19,085 B `llms.txt` —
both established by hand checks the probe does not perform.
