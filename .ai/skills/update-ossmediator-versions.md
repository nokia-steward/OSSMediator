# Skill: Update OSSMediator Versions

## Purpose
Bump the platform versions shipped by this open-source repository:
Go and Alpine for the collector and Elasticsearch plugin images, and Grafana
and OpenSearch for MediatorSetup.

OSSMediator is the open-source version of NOD. Subscription-only bumps — the
dashboard-reporter plugin, `oss-grafana`, and `oss-opensearch` — belong to
`gitlabe2.ext.net.nokia.com/nod/ossmediator` and its `update-nod-versions` skill.
Do not edit those repositories from this skill.

## Trigger Phrases
- "update OSSMediator versions"
- "bump Go, Alpine, Grafana, or OpenSearch"
- "refresh open-source OSSMediator dependency versions"

## Owner / Script
- Script: none. Edit the pins in this repo directly. There is no
  `update_nod_versions.py` here.
- Docs: `CHANGELOG.md`, `MediatorSetup/UPGRADE.md`

## Inputs
| Param | Description | Default |
|---|---|---|
| Go version | `golang` image tag and the `go` line in each `go.mod` | leave unchanged |
| Alpine version | `alpine` image tag | leave unchanged |
| Grafana version | `grafana/grafana` tag and the Grafana package URLs | leave unchanged |
| OpenSearch version | runtime OpenSearch image tag and datasource `version` fields | leave unchanged |

Ask for any version the user did not name. Do not invent a "latest" tag.

## Environment
- Network access when resolving the Grafana package URL for a new version, and when running `go mod tidy`.
- `go` on `PATH` when the Go version changes.

## Prechecks
1. Confirm these files exist:
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
2. Read the root `VERSION` file. The changelog section for that release is `X.Y.Z` after removing a trailing `-SNAPSHOT`.

## Steps
1. Apply only the versions the user supplied.
2. Go: set `FROM golang:<version>` in both Dockerfiles and the `go` directive in all three `go.mod` files, then tidy:

```bash
(cd OSSMediatorCollector && go mod tidy)
(cd OSSMediatorCollector/storesecret && go mod tidy)
(cd ElasticsearchPlugin && go mod tidy)
```

3. Alpine: set `FROM alpine:<version>` in both Dockerfiles.
4. Grafana: set `grafana/grafana:<version>` in `MediatorSetup/mediator_docker_startup.sh`. In `MediatorSetup/startup.sh` and `MediatorSetup/startup_without_elasticsearch.sh`, replace the package URLs with the official `dl.grafana.com` RPM and DEB for that version, including the build id in the filename. Take that build id from the published package URL. Leave `min_grafana_version` unchanged unless the user changes the minimum supported Grafana.
5. OpenSearch: set `opensearchproject/opensearch:<version>` in `MediatorSetup/mediator_docker_startup.sh` and `MediatorSetup/startup.sh`. Set every datasource `version:` in `dac_oss_datasources.yaml` to that same version.
6. In `CHANGELOG.md`, under `# X.Y.Z`, record the changed pins in `SECURITY UPDATE`, grouped as `OSSMediator` for Go and Alpine and `MediatorSetup` for OpenSearch and Grafana. Match the punctuation of the current top section. Create `# X.Y.Z` under the intro when that section is missing.

Leave `MediatorSetup/data_migration.sh` unchanged. It pins older images for a one-time migration. Leave the OpenSearch tarball in `ElasticsearchPlugin/Dockerfile` unchanged. That tarball is the unit-test server.

## What This Updates / Does
- `OSSMediatorCollector/Dockerfile` and `ElasticsearchPlugin/Dockerfile` — `golang:<version>`, `alpine:<version>`
- `OSSMediatorCollector/go.mod`, `OSSMediatorCollector/storesecret/go.mod`, `ElasticsearchPlugin/go.mod`, and their `go.sum` files when tidy runs
- `MediatorSetup/mediator_docker_startup.sh` — Grafana and OpenSearch image tags
- `MediatorSetup/startup.sh` — Grafana package URLs and the OpenSearch image tag
- `MediatorSetup/startup_without_elasticsearch.sh` — Grafana package URLs
- `MediatorSetup/grafana_data/provisioning/datasources/dac_oss_datasources.yaml` — OpenSearch `version` fields
- `CHANGELOG.md` — `SECURITY UPDATE` lines for the versions that changed

## Verification
1. `python .ai/scripts/validate-skills.py` is not required for the version edit. Confirm the diff instead.
2. `git diff` shows only the requested version pins, changelog lines, and `go.sum` updates from tidy.
3. The Go image tag, the three `go` directives, and the changelog Go version are the same string.
4. The Alpine tags and the changelog Alpine version are the same string.
5. The Grafana image tag, both startup scripts' package versions, and the changelog Grafana version are the same string.
6. The OpenSearch image tags, every datasource `version:`, and the changelog OpenSearch version are the same string.
7. When Go changed and `go` is available, `go vet ./...` passes in `OSSMediatorCollector`, `OSSMediatorCollector/storesecret`, and `ElasticsearchPlugin`.

## Failure Handling
- A Grafana package URL that returns 404 has the wrong build id. Look up the published filename for that version and replace the URL. Do not guess the build id.
- If `go mod tidy` fails, stop and report the module and the error. A newer Go line can stay in `go.mod` only when the user accepts fixing the compile error before another tidy.
- Do not cut a git tag or run `release.sh` as part of this skill. Packaging and tagging are a separate outcome.

## Rollback
```bash
git checkout -- OSSMediatorCollector/Dockerfile ElasticsearchPlugin/Dockerfile OSSMediatorCollector/go.mod OSSMediatorCollector/go.sum OSSMediatorCollector/storesecret/go.mod OSSMediatorCollector/storesecret/go.sum ElasticsearchPlugin/go.mod ElasticsearchPlugin/go.sum MediatorSetup/mediator_docker_startup.sh MediatorSetup/startup.sh MediatorSetup/startup_without_elasticsearch.sh MediatorSetup/grafana_data/provisioning/datasources/dac_oss_datasources.yaml CHANGELOG.md
```

## Outputs / Artifacts
- The edited pin files and, when tidy ran, updated `go.sum` files.
- A short summary of each version changed and each file modified, suitable for the changelog or a pull request.
