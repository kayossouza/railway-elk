# Operating boundaries and recovery

Use EVIDENCE.md in the review bundle for current test status. This package supports
producers in the same Railway project/environment only. ES and intake have no
public endpoint. Deployment readiness is not a delivery guarantee: send a unique
canary and search for its original fields through Kibana.

## Envelope, rejection and queues

Searchable envelope: `@timestamp` (date), `message` (text), `service` and `level`
(keywords), and `attributes` (flattened object). Unknown top-level fields are
preserved in `_source` but not indexed. Put arbitrary application properties in
`attributes`; flattened values have keyword semantics, not numeric range semantics.
The reserved `elk_test_run` and `sequence` fields support proof fixtures.
Invalid dates/types go to the mounted DLQ on permanent output rejection. Malformed
JSON is tagged `_jsonparsefailure` by the JSON codec; its original text remains in
`message`. HTTP success means accepted, not indexed or validated.

The persistent queue and DLQ each have a configured 64mb ceiling (logstash.yml).
DLQ `drop_newer` preserves older rejects but loses new rejects when full. It is
neither automatic replay nor unlimited durability. Inspect indexing errors and
`GET :9600/_node/stats/pipelines` (private network), including queue and DLQ size.
Alert before capacity is exhausted. Queue-full intake may block/time out; use
bounded producer timeouts, exponential backoff with jitter and a durable producer
spool. A timed-out request may already have been accepted: retries may duplicate.
This design does not guarantee exactly once. Do not increase checkpoint.writes
without establishing and accepting a loss budget.

For DLQ inspection, run an isolated one-off Logstash pipeline in the existing
Logstash container as UID 1000. Use a separate settings directory with
`api.enabled: false`, `queue.type: memory`, `config.reload.automatic: false`,
and `pipeline.workers: 1`, and a separate `--path.data /tmp/elk-dlq-reader`.
Save this pipeline to a file and pass `-f FILE` (not `-e` with production settings):

```text
input { dead_letter_queue {
  path => "/usr/share/logstash/data/dead_letter_queue"
  pipeline_id => "main"
  commit_offsets => false
} }
output { stdout { codec => rubydebug { metadata => true } } }
```

Treat output as sensitive log data, never public evidence. Copy recoverable events
into a protected operator file, correct the offending fields, and resubmit through
intake. Confirm indexed originals before removing any DLQ segments. Failed replay
is not recursively re-enqueued. Stop the one-off reader after inspection.

## Retention and existing installs

New volumes get built-in ILM: rollover at `LOG_ROLLOVER_SIZE` (default `1gb`) or
one day, delete backing indices `LOG_RETENTION` (default `7d`) after rollover.
These are explicit conservative configuration choices, not measured optimal sizes
or durations. `forever` omits deletion. ILM deletion removes entire backing indices;
it is not exact per-event age enforcement and ILM polling adds delay.
Retention bounds age, not total disk use; monitor occupancy and disk watermarks.
Change a policy deliberately using `PUT /_ilm/policy/elk_logs`; variables do not
silently rewrite an existing installation's policy. See lifecycle.py for the body.

Existing fixed `elk-logs` indices and mapping are preserved on restart. For migration,
stop producers, snapshot and verify, install the new template/policy using a distinct
alias (for example `elk-logs-v2`), grant writer access to that prefix, and change
Logstash/Kibana together. Old data remains searchable with a separate data view.
Do not delete or rename the original index to force alias creation. Recovery of
legacy incompatible mappings remains manual; the DLQ protects new permanent rejects.

## Credentials

Startup starts ES even if provisioning metadata or consumer passwords disagree.
Readiness remains unavailable until actual admin and consumer authentication works.
A marker is not an authentication authority. Original secrets and Kibana encryption
keys must be retained with backups. Restart exhaustion needs operator intervention:
fix the underlying auth/disk/network error, then explicitly redeploy the affected
service and verify a real ingest/search canary.

Rotate one native user at a time with `python3 /opt/elk/rotate.py USER` in the ES
container. It prompts privately for current admin and new password, verifies actual
authentication, and makes an idempotent password change. Then update that identity's
Railway variable using the dashboard; consumer reference variables remain unchanged.
Redeploy the consumer and ES, run ingest/search or Kibana login, then use
`--finalize` after consumer verification to atomically update the marker.
No command should contain passwords in argv. Do not change unrelated customized users.
If interrupted after the API change, retry with the same new secret, update the
variable and redeploy; until then the affected consumer is unavailable. For admin
rotation, use the new admin password on retry. Repeating finalize is safe.
Lost admin password: use Elastic's supported `elasticsearch-reset-password -u elastic -i`
in the existing container, then restore matching variables and verify authentication.
Do not delete the volume or reset other users. See [Elastic's reset-password docs](https://www.elastic.co/docs/reference/elasticsearch/command-line-tools/reset-password). The tool requires the file realm to be enabled.

## Optional snapshots (not an automatic backup)

External snapshots require user-owned storage and credentials. No external account,
new spend or automatic backup is provisioned here. For S3-compatible storage use
Elastic's supported S3 repository plugin (bundled), secure settings via
`elasticsearch-keystore add s3.client.default.access_key` and `secret_key` (private
prompts). Configure `s3.client.default.endpoint` and
`s3.client.default.region` in elasticsearch.yml for the owner's provider, restart
as required for client settings, then reload secure credentials. Register
`PUT /_snapshot/elk_backup` with type `s3` and repository settings `bucket`
and `base_path`. See [S3 repository documentation](https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore/s3-repository).
Run `POST /_snapshot/elk_backup/_verify` before use. Take
`PUT /_snapshot/elk_backup/SNAPSHOT?wait_for_completion=true` with
`include_global_state:true` and feature_states including `security` and `kibana`.
Inspect `GET /_snapshot/elk_backup/SNAPSHOT`: require `SUCCESS` and no failed shards.
Capture index list and encryption keys in a protected recovery inventory.

Restore into a separate empty stack of the same Elastic version, with original
secrets/keys, producers stopped and LS/Kibana stopped. Register the repository
read-only; restore the verified snapshot including global state/security/Kibana
feature states. Restoring security changes active credentials; use original keys.
Restart clients, verify saved views and document identities, then ingest a canary.
Never restore over the working source stack. External repository restoration is
untested here until owner-provided storage is available; volume redeploy is not backup.
An older image is not a rollback of an Elastic data-format upgrade. Restore a
verified snapshot into the original version instead.

## Limited viewer

Admin is for provisioning/recovery. Create a role with ES `read` and `view_index_metadata`
on `elk-logs*`, and Kibana space privileges `feature.discover: ["read"]` via `PUT /api/security/role/elk_viewer` (successful response 204):

```json
{"elasticsearch":{"cluster":[],"indices":[{"names":["elk-logs*"],"privileges":["read","view_index_metadata"]}]},"kibana":[{"base":[],"feature":{"discover":["read"]},"spaces":["default"]}]}
```

Use authenticated private requests with `kbn-xsrf` header. Create a native user assigned only that role. Validate Discover
access and denial of writes/admin APIs; do not grant `superuser` for routine viewing.
