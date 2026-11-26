# AI Skills

This folder is the **single source of truth** for reusable AI-agent skills in
this repo.

OSSMediator is the open-source version of NOD. Subscription NOD has more
features, including the separate `oss-grafana` and `oss-opensearch` repos and
the dashboard-reporter plugin. Skills here change only this open-source
repository. The subscription counterpart lives in
`gitlabe2.ext.net.nokia.com/nod/ossmediator` and its skill is
`update-nod-versions`.

Tool-specific adapters under `.github/prompts/`, `.cursor/rules/`, and
`.gemini/prompts/` are thin wrappers that point back to files in this folder —
update the skill here first, then keep adapters in sync (see
`../scripts/sync-tool-adapters.py`).

## Index

| Skill | File | Summary |
|---|---|---|
| Update OSSMediator Versions | [`update-ossmediator-versions.md`](./update-ossmediator-versions.md) | Bump Go, Alpine, Grafana, and OpenSearch versions in this open-source repo. |

## Adding a new skill
1. Copy `../templates/skill-template.md` to `<verb-noun>.md` in this folder.
2. Fill in every section (`Purpose`, `Trigger Phrases`, `Owner / Script`,
   `Inputs`, `Environment`, `Prechecks`, `Steps`, `What This Updates / Does`,
   `Verification`, `Failure Handling`, `Rollback`, `Outputs / Artifacts`).
3. Run `python .ai/scripts/validate-skills.py` from the repository root to confirm required sections exist.
4. Add a row to the index table above.
5. Run `python .ai/scripts/sync-tool-adapters.py` from the repository root to regenerate thin adapter
   files for Copilot / Cursor / Gemini.

## Naming convention
- File names are verb-first and kebab-case: `update-ossmediator-versions.md`,
  `prepare-release.md`, `triage-prod-incident.md`.
- One outcome per skill file — keep it focused.
