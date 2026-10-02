# Railway setup

[Deploy the template](https://railway.com/deploy/elk-stack-2) to create the configured
stack. The following inventory also supports manual setup.

Create services named `Elasticsearch`, `Logstash` and `Kibana` in the same project,
environment and region. Connect each to its corresponding repository directory
as its root. Each directory contains a Dockerfile and `railway.json`.

| Service root | Volume mount | Healthcheck | PORT |
|---|---|---|---|
| `/elasticsearch` | `/usr/share/elasticsearch/data` | `/ready` | `8081` |
| `/logstash` | `/usr/share/logstash/data` | `/_node/pipelines/main` | `9600` |
| `/kibana` | None; saved objects live in Elasticsearch | `/ready` | `8082` |

Copy the inventory from [variables.json](variables.json) into the template editor.
`${{secret(...)}}` entries are Railway template generators, not literal passwords.
For manual dashboard setup, generate independent random credentials and encryption
keys using a password manager and enter them directly into Railway Variables.
Use the lengths specified in the inventory. Keep reference expressions as references.
Never commit resolved values. Keep values stable across restarts and redeploys.

Deploy Elasticsearch first, then its consumers. Expose only Kibana through a
Railway HTTPS domain targeting its UI port `5601`, not its readiness port.
Leave Elasticsearch and Logstash without public domains or TCP proxies.
Optionally group the services as `ELK Stack` on the architecture canvas.
Grouping is visual organization; networking supplies isolation.

The Dockerfiles and configuration files are the source for ports, heap sizes,
queue limits and restart policy. [OPERATIONS.md](OPERATIONS.md) explains retention
and existing-volume behavior. The service sources preserve the tested Railway runtime.
