# Template specification

Unpublished Railway draft: [KPF5VY](https://railway.com/deploy/KPF5VY).
Source: private `kayossouza/railway-elk`, branch `main`, with one root per service.
This task does not authorize publication, public source or a Station submission.
Deployer access to the private repository is required.

| Service / source root | Private ports | Persistent mount | Deployment healthcheck |
|---|---|---|---|
| Elasticsearch / `/elasticsearch` | 9200 API, 8081 readiness | `/usr/share/elasticsearch/data` | `PORT=8081`, `/ready` |
| Logstash / `/logstash` | 8080 intake, 9600 API | `/usr/share/logstash/data` | `PORT=9600`, `/_node/pipelines/main` |
| Kibana / `/kibana` | 5601 UI, 8082 readiness | Saved objects in Elasticsearch | `PORT=8082`, `/ready` |

All three belong to the ELK Stack group in one environment and region. Only
Kibana has a Railway HTTPS domain, targeting 5601. Neither Elasticsearch nor
Logstash has a public domain or TCP proxy. Grouping organizes the canvas;
project/environment networking supplies isolation.

## Configuration

`variables.json` is the complete template variable inventory. Independent native
and intake credentials use `${{secret(48)}}`; Kibana encryption keys use
`${{secret(64)}}`. Consumer credentials and hosts use Railway references.
There are no blank user inputs. Ports, intake username and heap limits are image
defaults; Railway healthcheck ports and mounted-volume ownership settings remain
explicit variables. `composer.json` is a local review manifest, not an import file.

Upstream Elastic images are pinned by version and digest in each Dockerfile.
Small in-container wrappers provision identities, repair mount ownership and
check dependency readiness. They add no service and require no operator script.
The first native-user lookup permits an absent user (404); auth failures remain
fatal. Subsequent starts authenticate existing identities and preserve data.

## Data and recovery

Authenticated JSON intake writes through the restricted `logstash_writer` user
to the `elk-logs` alias. New installs configure one primary, zero replicas, rollover
at 1 GB or one day and deletion seven days after rollover. These are configuration
choices, not proven capacity or exact per-event expiry. Existing policies are
preserved. Unknown fields stay in `_source`; use `attributes` for searchable
application properties.

Logstash has mounted persistent queue and DLQ storage, each configured to 64 MB.
Acceptance is not proof of indexing; retries can duplicate events, and bounded
storage can fill. Volumes are persistence, not backups or high availability.
Keep original credentials and encryption keys across redeploys. Follow
[OPERATIONS](OPERATIONS.md) for rotation, snapshots and recovery.

[README](README.md) is the user workflow. [COST](COST.md) contains the measured
scenario. Reviewer run records and requirement coverage are in the parent
`EVIDENCE.md` and `HANDOFF.md`, outside the deployable source package.
