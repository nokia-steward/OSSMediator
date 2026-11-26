# Skill: Update OSSMediator (Open Source)

## Purpose
Maintain this open-source OSSMediator repository: bump platform version pins (Go,
Alpine, Grafana, OpenSearch) **in lockstep across both Go components**
(`OSSMediatorCollector` and `ElasticsearchPlugin`, including each `go.mod`), and
apply MediatorSetup dashboard changes that belong
only in open source — strip subscription-only PDF report links, remove unsupported
NQA and Performance Analysis dashboards, 5G PMQAP profile dashboards (mobility and
network performance), and prune Radio PM release dashboards to
the current release plus the two prior `YYRn` labels.

OSSMediator is the open-source version of NOD. Subscription-only work — the
dashboard-reporter plugin, `oss-grafana`, `oss-opensearch`, and
`gitlabe2.ext.net.nokia.com/nod/ossmediator` (`update-nod-versions`) — stays out of
this skill.

## Trigger Phrases
- "update OSSMediator versions"
- "bump Go, Alpine, Grafana, or OpenSearch"
- "refresh open-source OSSMediator dependency versions"
- "remove dashboard PDF links"
- "remove pdf generation links from dashboards"
- "strip dashboard reporter links"
- "remove Reports links from Grafana dashboards"
- "remove NQA dashboards"
- "remove performance analysis dashboards"
- "drop nqa and performance analysis dashboards"
- "remove nqa and performance analysis from MediatorSetup"
- "remove n-3 radio pm versions"
- "remove n-3 radio dashboards"
- "remove old radio PM release dashboards"
- "drop radio pm dashboards older than three releases"
- "prune radio pm dashboards keep current and two prior releases"

Run only the workflow that matches the user's request. A release prep may run
several workflows in one task when the user asks for all open-source dashboard
cleanup.

## Owner / Script
- Script: none. Edit pins and dashboard JSON in this repo directly.
- Docs: `CHANGELOG.md`, `MediatorSetup/UPGRADE.md`

## Inputs
| Param | Description | Default |
|---|---|---|
| Go version | Same `golang:<tag>` builder image and matching `go` line in **every** module under `OSSMediatorCollector/` and `ElasticsearchPlugin/` | leave unchanged |
| Alpine version | Same `alpine:<tag>` runtime image in **both** component Dockerfiles | leave unchanged |
| Grafana version | `grafana/grafana` tag and the Grafana package URLs | leave unchanged |
| OpenSearch version | runtime OpenSearch image tag and datasource `version` fields | leave unchanged |
| Current radio release | Nokia label `YYRn` (for example `26R3`) for n-3 pruning | required when pruning — ask if missing |
| Changelog | Record dashboard changes under current `VERSION` | yes |

Ask for any version or release label the user did not name. Do not invent a "latest"
tag.

## Environment
- Network access when resolving the Grafana package URL for a new version, and when
  running `go mod tidy`.
- `go` on `PATH` when the Go version changes.
- Python 3 on `PATH` for batch dashboard JSON edits and release pruning checks.

## Prechecks
1. Read the root `VERSION` file. The changelog section is `X.Y.Z` after removing a
   trailing `-SNAPSHOT`.
2. For version bumps, confirm these files exist:
   - `OSSMediatorCollector/Dockerfile`
   - `ElasticsearchPlugin/Dockerfile`
   - `OSSMediatorCollector/go.mod`
   - `OSSMediatorCollector/storesecret/go.mod`
   - `ElasticsearchPlugin/go.mod`
   - `MediatorSetup/mediator_docker_startup.sh`
   - `MediatorSetup/startup.sh`
   - `MediatorSetup/startup_without_elasticsearch.sh`
   - `MediatorSetup/grafana_data/provisioning/datasources/dac_oss_datasources.yaml`
   - `CHANGELOG.md`
3. For dashboard work, confirm `MediatorSetup/grafana_data/dashboards/` exists.
   Provisioning is file-based via
   `MediatorSetup/grafana_data/provisioning/dashboards/dac_oss_dashboards.yaml` — no
   manifest edit is needed when adding or deleting JSON files in that folder.

## Steps

### Workflow A — Version pins
Run only when the user supplies one or more of Go, Alpine, Grafana, or OpenSearch.

When the user says **update OSSMediator versions** without naming only one stack layer,
treat Go and Alpine as a paired **OSSMediator** bump: update collector **and** plugin
together. Never change `OSSMediatorCollector` without the matching edits in
`ElasticsearchPlugin` (and vice versa).

**Pin locations (OSSMediator — keep values identical across this table):**

| Pin | OSSMediatorCollector | ElasticsearchPlugin |
|---|---|---|
| Go builder | `OSSMediatorCollector/Dockerfile` — `FROM golang:<go>` | `ElasticsearchPlugin/Dockerfile` — `FROM golang:<go>` |
| Go toolchain | `OSSMediatorCollector/go.mod`, `OSSMediatorCollector/storesecret/go.mod` | `ElasticsearchPlugin/go.mod` |
| Alpine runtime | `OSSMediatorCollector/Dockerfile` — final `FROM alpine:<alpine>` | `ElasticsearchPlugin/Dockerfile` — final `FROM alpine:<alpine>` |

1. Apply only the versions the user supplied.
2. **Go:** set the **same** `<version>` in both builder-stage `FROM golang:<version>`
   lines and in the `go` directive in all three `go.mod` files
   (`OSSMediatorCollector/go.mod`, `OSSMediatorCollector/storesecret/go.mod`,
   `ElasticsearchPlugin/go.mod`). Then tidy **each** module so `go.sum` stays consistent:

```bash
(cd OSSMediatorCollector && go mod tidy)
(cd OSSMediatorCollector/storesecret && go mod tidy)
(cd ElasticsearchPlugin && go mod tidy)
```

3. **Alpine:** set the **same** `<version>` on the final-stage `FROM alpine:<version>` in
   `OSSMediatorCollector/Dockerfile` and `ElasticsearchPlugin/Dockerfile`.
4. Grafana: set `grafana/grafana:<version>` in `MediatorSetup/mediator_docker_startup.sh`. In `MediatorSetup/startup.sh` and `MediatorSetup/startup_without_elasticsearch.sh`, replace the package URLs with the official `dl.grafana.com` RPM and DEB for that version, including the build id in the filename. Take that build id from the published package URL. Leave `min_grafana_version` unchanged unless the user changes the minimum supported Grafana.
5. OpenSearch: set `opensearchproject/opensearch:<version>` in `MediatorSetup/mediator_docker_startup.sh` and `MediatorSetup/startup.sh`. Set every datasource `version:` in `dac_oss_datasources.yaml` to that same version.
6. In `CHANGELOG.md`, under `# X.Y.Z`, record changed pins in `SECURITY UPDATE`, grouped as `OSSMediator` for Go and Alpine and `MediatorSetup` for OpenSearch and Grafana. Create `# X.Y.Z` under the intro when that section is missing.

Leave `MediatorSetup/data_migration.sh` unchanged. Leave the OpenSearch tarball in
`ElasticsearchPlugin/Dockerfile` unchanged (unit-test server).

### Workflow B — Remove dashboard PDF links
Open-source builds do not ship dashboard-reporter. Remove every **Reports** link from
dashboard JSON.

1. From the repository root:

```bash
python - <<'PY'
import json
from pathlib import Path

root = Path("MediatorSetup/grafana_data/dashboards")
changed = []
for path in sorted(root.glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    links = data.get("links")
    if not isinstance(links, list):
        continue
    kept = [
        item
        for item in links
        if not (
            isinstance(item, dict)
            and item.get("type") == "link"
            and (
                "mahendrapaipuri-dashboardreporter-app" in str(item.get("url", ""))
                or item.get("tooltip") == "Create pdf report for the dashboard."
            )
        )
    ]
    if kept != links:
        data["links"] = kept
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        changed.append(path.name)

print(f"Updated {len(changed)} file(s)")
for name in changed:
    print(f"  - {name}")
PY
```

2. Under `# X.Y.Z`, add or extend `REMOVED:` with
   `MediatorSetup: Removed dashboard PDF report links from Grafana dashboards.`

Leave panel content, variables, and non-PDF navigation links unchanged.

### Workflow C — Remove NQA and Performance Analysis dashboards
Delete these files when present:

- `MediatorSetup/grafana_data/dashboards/dac_4g_radio_nqa_pm_dashboard.json`
- `MediatorSetup/grafana_data/dashboards/dac_5g_radio_nqa_pm_dashboard.json`
- `MediatorSetup/grafana_data/dashboards/dac_4g_radio_performance_analysis_dashboard.json`
- `MediatorSetup/grafana_data/dashboards/dac_5g_radio_performance_analysis_dashboard.json`
- `MediatorSetup/grafana_data/dashboards/dac_5g_radio_mobility_per_pmqap_profile_dashboard.json`
- `MediatorSetup/grafana_data/dashboards/dac_5g_radio_network_performance_per_pmqap_profile_dashboard.json`

Then search for stale references:

```bash
rg "radio4gnqa|radio5gnqa|4g-radio-analysis|5g-radio-analysis|radio5g-mobility-per-pmqap-profile|radio5g-nw-perf-per-pmqap-profile|dac_.*_pmqap_profile_dashboard" MediatorSetup
```

Resolve any matches before finishing. Under `# X.Y.Z`, extend `REMOVED:` with:

- `MediatorSetup: Removed Radio 4G and 5G NQA PM dashboards.`
- `MediatorSetup: Removed Radio 4G and 5G Performance Analysis dashboards.`
- `MediatorSetup: Removed Radio 5G PMQAP profile dashboards (mobility and network performance).`

Do not remove versioned Radio PM KPI files (`*_dashboard_26R3.json`, etc.) or
`ndac-radio-moss-ne3s-pm-*-report-dashboard.json` here.

### Workflow D — Prune Radio PM releases (keep n − 3)
Keep the **current** `YYRn` and the **two releases before it** (three labels total).
Delete older `dac_5g_radio_{system_program,retainability,accessibility}_dashboard_<release>.json` files.

Versioned filename patterns:

| KPI set | Pattern |
|---|---|
| System program (NRCell) | `dac_5g_radio_system_program_dashboard_<release>.json` |
| Retainability 5G003 | `dac_5g_radio_retainability_dashboard_<release>.json` |
| Accessibility 5G002 | `dac_5g_radio_accessibility_dashboard_<release>.json` |

1. Validate current release matches `^\d{2}R[1-3]$`. Compute the keep set:

```bash
CURRENT_RELEASE=26R3 python - <<'PY'
import os

current = os.environ["CURRENT_RELEASE"]

def previous_release(label: str) -> str:
    year, r = int(label[:2]), int(label[3])
    if r > 1:
        return f"{year:02d}R{r - 1}"
    return f"{year - 1:02d}R3"

keep = {current}
cursor = current
for _ in range(2):
    cursor = previous_release(cursor)
    keep.add(cursor)

print("Keep:", ", ".join(sorted(keep, reverse=True)))
PY
```

2. Delete each versioned file whose `_<release>.json` suffix is not in the keep set.
3. Under `# X.Y.Z`, add `REMOVED:` lines such as
   `MediatorSetup: Removed Radio PM \`25R3\` dashboards.` for each dropped label.

Do not edit `ndac-radio-moss-ne3s-pm-*-report-dashboard.json` unless the user asks.

## What This Updates / Does
- **Workflow A:** `OSSMediatorCollector/Dockerfile`, `ElasticsearchPlugin/Dockerfile`,
  all three `go.mod` and resulting `go.sum` files, MediatorSetup startup scripts,
  `dac_oss_datasources.yaml`, changelog `SECURITY UPDATE`.
- **Workflow B:** `MediatorSetup/grafana_data/dashboards/*.json` — top-level `links` only.
- **Workflow C:** Deletes NQA, Performance Analysis, and PMQAP profile dashboard JSON files.
- **Workflow D:** Deletes outdated version-suffixed 5G Radio PM dashboard JSON files.
- **Workflows B–D:** `CHANGELOG.md` `REMOVED` (and `IMPROVEMENTS` when adding new
  dashboards is a separate import task).

## Verification
**Workflow A**
1. `git diff` shows only requested pins, changelog `SECURITY UPDATE`, and `go.sum` from tidy.
2. **Go:** the collector Dockerfile, plugin Dockerfile, three `go` lines, and changelog
   all use one string. Quick check:

```bash
rg "FROM golang:|^go " OSSMediatorCollector/Dockerfile ElasticsearchPlugin/Dockerfile OSSMediatorCollector/go.mod OSSMediatorCollector/storesecret/go.mod ElasticsearchPlugin/go.mod
```

3. **Alpine:** both final-stage `FROM alpine:` tags and the changelog Alpine line match:

```bash
rg "FROM alpine:" OSSMediatorCollector/Dockerfile ElasticsearchPlugin/Dockerfile
```

4. Grafana and OpenSearch strings match across image tags, scripts, datasources, and changelog.
5. When Go changed and `go` is available, `go vet ./...` passes in `OSSMediatorCollector`,
   `OSSMediatorCollector/storesecret`, and `ElasticsearchPlugin`.

**Workflow B**
```bash
rg "mahendrapaipuri-dashboardreporter-app|Create pdf report for the dashboard" MediatorSetup/grafana_data/dashboards
```
Expect no matches.

**Workflow C**
1. All six Workflow C dashboard paths are absent from the working tree.
2. `rg -i "radio4gnqa|radio5gnqa|4g-radio-analysis|5g-radio-analysis|radio5g-mobility-per-pmqap-profile|radio5g-nw-perf-per-pmqap-profile" MediatorSetup` returns nothing.

**Workflow D**
1. No versioned file remains outside the keep set (update `KEEP` in the check below):

```bash
python - <<'PY'
import re
from pathlib import Path

KEEP = {"26R3", "26R2", "26R1"}  # replace with computed keep set

pat = re.compile(
    r"dac_5g_radio_(?:system_program|retainability|accessibility)_dashboard_(\d{2}R[1-3])\.json$"
)
root = Path("MediatorSetup/grafana_data/dashboards")
extra = [
    path.name
    for path in root.glob("dac_5g_radio_*_dashboard_*.json")
    if (m := pat.search(path.name)) and m.group(1) not in KEEP
]
if extra:
    raise SystemExit("Unexpected old releases:\n  " + "\n  ".join(extra))
print("OK: only kept release suffixes remain")
PY
```

**All workflows**
- `python .ai/scripts/validate-skills.py` after editing this skill file only.

## Failure Handling
- If Go or Alpine differs between `OSSMediatorCollector` and `ElasticsearchPlugin`, or
  between a Dockerfile and its `go.mod`, fix before finishing — partial bumps are not allowed.
- Grafana package URL 404: wrong build id — use the published filename; do not guess.
- `go mod tidy` failure: stop and report; do not tag or run `release.sh` here.
- `json.loads` failure on a dashboard: fix JSON before re-running Workflow B.
- NQA file already missing: note and continue (Workflow C).
- Unexpected UID references after NQA deletion: stop until resolved.
- Radio release not in filenames: confirm the current shipping `YYRn` before deleting (Workflow D).
- If fewer than three releases exist in the tree, still delete any file older than the
  third kept label.

## Rollback
```bash
git checkout -- OSSMediatorCollector/Dockerfile ElasticsearchPlugin/Dockerfile OSSMediatorCollector/go.mod OSSMediatorCollector/go.sum OSSMediatorCollector/storesecret/go.mod OSSMediatorCollector/storesecret/go.sum ElasticsearchPlugin/go.mod ElasticsearchPlugin/go.sum MediatorSetup/mediator_docker_startup.sh MediatorSetup/startup.sh MediatorSetup/startup_without_elasticsearch.sh MediatorSetup/grafana_data/provisioning/datasources/dac_oss_datasources.yaml MediatorSetup/grafana_data/dashboards CHANGELOG.md
```

## Outputs / Artifacts
- Short summary of each workflow run, files touched, and changelog lines added —
  suitable for a pull request.