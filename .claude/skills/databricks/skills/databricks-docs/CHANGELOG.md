# Changelog

All notable changes to the `databricks-docs` skill are documented here.

## [0.1.2] - 2026-07-30

Conformance pass against the updated `docs-skill-builder` spec. **The mechanism did not change**
— the site was not re-probed, because the trigger was a spec revision an hour after the build,
not drift at `docs.databricks.com`. Only the document set moved.

- **`references/mechanism.md` is now an append-only log**, newest entry first, in the entry
  format the template prescribes: *Verdict / How the site is read / Why this design / What would
  overturn it / Rebuild must preserve*, written as prose and inside the ≤ 1000-word budget for a
  mechanism-establishing entry. The raw probe dump and the loose tables it replaced are gone; the
  measurements they carried are in the entry. No past entry was rewritten — the file held none,
  since it predated the log format by an hour.
- **Added the two missing translations**, `SKILL-cn.md` and `references/mechanism-cn.md`. All
  three pairs (`SKILL`, `README`, `mechanism`) are now present and were written in the same pass
  as their English originals, which stay authoritative.
- **Removed the translation notice from `README.md`.** Under the new rule the English files never
  mention that a translation exists; the convention lives only in the `-cn.md` files. `README-cn.md`
  now opens with the standard note.
- Cross-references retargeted from "the fact sheet" to "the top entry of the log" in `SKILL.md`,
  `README.md`, and both translations, and the `check` description updated to say that every check
  appends an entry — including a no-change one.
- Re-ran the routing acceptance tests against the cached index to confirm nothing broke: same
  results, same byte counts as 0.1.1.

## [0.1.1] - 2026-07-30

- Initial release. Built by `docs-skill-builder` 0.1.1 from a measured probe of
  `docs.databricks.com`; the full fact sheet and the reasoning are in
  [references/mechanism.md](references/mechanism.md).

### Mechanism

- **Index: T1 (section-routed) + T4 (hub-descend)** against
  `https://docs.databricks.com/llms.txt` — 47,150 B, 252 entries, 15 sections, 98% prose
  descriptions. T4 is layered on because the index covers only 4.5% of the site (252 entries vs
  5,645 sitemap URLs), so entries frequently name an area landing page rather than the page that
  answers the question.
- **Content: C1 (`html-webfetch`)**. All six plain-text conventions fail — `.md`, `/index.md`,
  `.txt` return 404, and `Accept: text/markdown` / `?plain=1` return the same HTML. Pages are
  21 KB–51 KB of raw HTML, so they are read with WebFetch and never curled.
- Built against the **docs** `llms.txt`, not `www.databricks.com/llms.txt` (36 entries, mostly
  product marketing) that the build request pointed at. The marketing index's own
  "Databricks-owned LLM manifests" section is what names the docs index.

### Recall aids specific to this vendor

- Rename pairs written into the search guidance: `dlt/` → `ldp/`, Delta Live Tables → Lakeflow
  Declarative Pipelines, Workflows → Lakeflow Jobs.
- Chinese trigger phrases in `description`; the index is English-only and Databricks publishes
  no Chinese edition (declared locales are en, ja, pt).
- Scope boundaries recorded: Azure Databricks docs live on `learn.microsoft.com`, DevHub on
  `developers.databricks.com`.

### Acceptance test

All four catalog tests run and reported with measured byte counts, including the two that
matter — a vocabulary-mismatch lookup (`cron` → 0 hits, `schedul|orchestrat|trigger|recurring`
→ **Job scheduling**, 781 B) and a hub descend (`vacuum` → 0 index hits, reached via the
`/delta/` landing page). No test required loading the whole index.
