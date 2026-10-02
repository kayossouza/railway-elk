# Contributing

Keep changes small and explain the problem, resulting behavior and validation.
Do not include credentials, private logs, personal data or Railway state files.
Keep authored files at or below 400 lines. Preserve upstream license notices.

Run the development commands in the README. Python configuration parsing uses
`requirements-dev.txt`; Node and Go examples use only their standard libraries.
Docker is required for image builds and the real Logstash integration test:

```bash
bash scripts/test_logstash.sh
```

For runtime changes, test intake, rejected authentication, indexing and recovery
in an authorized disposable environment. Record exact commands, commit SHA and
raw output. Do not claim mocked HTTP tests prove Elasticsearch indexing.
Include rollback or fix-forward steps. Preserve secrets and volumes during
configuration rollback; data-format upgrades need compatible snapshots.

Open a pull request with a clear description and evidence. Maintainers handle
release and template publication. CI never pushes images or deploys services.
