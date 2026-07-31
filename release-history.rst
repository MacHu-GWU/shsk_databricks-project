.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.1 (2026-07-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release. Adds the ``databricks`` Claude Code plugin, laid out under
  ``.claude/skills/databricks/`` with its manifest in ``.claude-plugin/plugin.json``
  so it can be published from this repo via a ``databricks--v{version}`` git tag.
- Adds the first skill in that plugin, ``databricks-docs``. It answers Databricks
  questions from the official documentation at the time of asking rather than from
  training-cutoff memory. It searches a locally cached copy of the
  ``docs.databricks.com`` ``llms.txt`` index (252 entries across 15 sections),
  puts only the matching lines into context, and reads just the pages that matched.
  Because that index covers roughly 4.5% of the site, the skill also descends from
  an area landing page to its child links when a topic is not indexed directly.
- ``databricks-docs`` ships a documented recall procedure for the cases where these
  lookups silently fail: widen the query with the vendor's own vocabulary, translate
  non-English queries first (Databricks publishes no Chinese documentation), fall
  back to a whole section, then descend a landing page — and only then report that
  something is undocumented.

**Minor Improvements**

- ``mise run list-plugins`` and ``mise run tag-plugin`` discover, validate, and tag
  every Claude Code plugin under ``.claude/skills/``.

**Miscellaneous**

- Adds repo-local authoring skills that are not part of the published plugin:
  ``docs-skill-builder`` (which generated ``databricks-docs`` from a measured probe
  of the docs site), ``maintain-claude-plugins``, ``write-agent-skill``, and
  ``skill-subagent-design``.
- Every published document ships an English original and a Chinese translation,
  with English authoritative.
