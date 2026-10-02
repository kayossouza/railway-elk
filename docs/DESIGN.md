# Packaging decisions

Reuse the existing service Dockerfiles, configuration and startup wrappers without
changing runtime behavior. Keep each service as its own Railway root directory.
Exclude local provisioning scripts, dependencies, caches and reviewer state.
Manual template wiring is documented in TEMPLATE.md; resolved secrets are never
part of the repository. The deploy button links to template KPF5VY.

Compared with adding language SDKs or a shared logging library, standard-library
HTTP producers keep the examples copyable and dependency-free. They send the
same JSON envelope and authenticate against the existing Logstash HTTP input.
They reject redirects to avoid forwarding credentials to another destination.
They use bounded timeouts and report failures without printing credential values.
Durable spooling and automatic retries remain application responsibilities.

Sources inspected:

- Existing source runtime and historical Railway test/cost records.
- [Elastic HTTP input documentation](https://www.elastic.co/docs/reference/logstash/plugins/plugins-inputs-http).
- [Railway resource pricing](https://docs.railway.com/pricing/plans), checked 2026-10-01.

The local contract receiver verifies producer behavior. A real Logstash test
verifies authenticated intake and JSON decoding, with stdout replacing the
Elasticsearch output. It does not prove Elasticsearch indexing or Kibana search.
CI builds local image tags, never pushes images and never deploys services.

Rollback for packaging changes is a Git revert followed by rebuilding the prior
source. Runtime configuration rollback requires unchanged data-compatible image
versions, credentials and volumes. Data-format upgrades require a compatible
verified snapshot restore, not a downgrade against upgraded data.
