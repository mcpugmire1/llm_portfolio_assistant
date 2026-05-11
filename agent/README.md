# Triage / Discovery Agent Assets

Operational assets — inputs to the Cowork orchestrator that drives Matt's
JD triage workflow. Source of truth lives here; Cowork's designated
folder is a copy that flows from this repo.

## Layout

- `triage/` — JD triage agent (operational v1)
  - `synthesis_prompt.md` — Three-layer logic (capability + filter + thin fit),
    voice constraints, Pass-mode handling, `engagement_mode` decision rules.
  - `filter_config.json` — Matt's hard rules (geographic, comp) + redline
    phrases for screen probes + `engagement_mode` definitions.
- `discovery/` — Reserved for v2 ATS-based push-model discovery (planning
  session pending; the 32-company seed list will live here).

## Triage flow

```
Matt → Cowork (Claude Desktop)
     → shells to `scripts/assess_jd.py < jd.txt`
     → engine produces JSON envelope (schema_version 1)
     → Cowork applies triage/synthesis_prompt.md + triage/filter_config.json
     → writes assessment back to Notion Application Tracker row
```

## Source of truth

This repo. Cowork's working folder is a copy. When updating any file
here: edit in this repo, copy to Cowork's folder, restart Cowork to pick
up the new prompt or config.

## Cowork setup checklist

Cowork-side configuration depends on Claude Desktop's connector model.
See: [Get started with Claude Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)
for the authoritative setup walkthrough.

When configuring Cowork for the first time, drop these files into the
designated folder:

- `agent/triage/synthesis_prompt.md`
- `agent/triage/filter_config.json`
- `echo_star_stories_nlp.jsonl` (repo root — the STAR story corpus)
- Opportunity Filter v3 doc (external)
- How I Work and Lead doc (external)

Connect the Gmail + Notion connectors in Claude Desktop settings.

`scripts/assess_jd.py` self-bootstraps `sys.path` to include the repo
root, so it works regardless of how Cowork shells out — no `PYTHONPATH`
gymnastics or `cd` required. Env vars load from the repo's `.env`
automatically via `services.pinecone_service`.

## v2 — `discovery/`

Reserved for the ATS-based push-model discovery agent against the
32-company seed list. Separate planning session when triage is
operational and producing real assessments. Architecture intent: query
Greenhouse / Lever / Workday ATS instances for new postings against the
seed list, push candidates into the Notion Application Tracker, and let
the triage agent process them in batch.
