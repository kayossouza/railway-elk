# Validation

The service files preserve tested runtime commit
`7b7ea32f1154a08f8965f5c0bf4c9f2ebded6f6c` byte for byte.
The saved Railway template provisions three services, generated credentials,
persistent Elasticsearch and Logstash volumes, and a public Kibana domain.

Local checks:

```bash
python3 scripts/lint.py
python3 scripts/test_examples.py
bash scripts/build.sh
bash scripts/test_logstash.sh
```

Lint checks configuration, syntax, image pins, file lengths, cost arithmetic
and local links. Example tests exercise JSON intake and authentication.
Image and pipeline checks require Docker.

Runtime verification requires a fresh template deployment, three healthy
services, authenticated intake and an indexed event returned through Kibana.

Rollback: revert documentation changes or redeploy a verified compatible
runtime revision. Preserve secrets, encryption keys and volumes.
Do not downgrade Elasticsearch against upgraded data.
