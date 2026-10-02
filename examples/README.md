# Send a JSON event

Each program sends one event using Basic auth, a bounded timeout and no external
libraries. These are tiny producers, not durable logging agents. They exit with
failure on rejected intake or connection errors. They do not retry automatically;
a retry after a timeout can duplicate an already accepted event.

On a Railway application in the same project and environment, add:

```text
LOGSTASH_URL=http://${{Logstash.RAILWAY_PRIVATE_DOMAIN}}:8080
LOGSTASH_PASSWORD=${{Logstash.INPUT_PASSWORD}}
```

Then copy a program into your application and run it:

```bash
node examples/node/send.mjs
python3 examples/python/send.py
go run examples/go/main.go
```

The Node example requires the built-in `fetch` and `AbortSignal.timeout` APIs.
CI uses Node 22, Python 3.12 and Go 1.23. These are selected test runtimes, not
claims about the oldest compatible versions.

Search `service : "example-node"`, `service : "example-python"` or
`service : "example-go"` in Kibana's `elk-logs` data view. Logstash adds
`@timestamp` when an event has no timestamp. Put custom searchable fields in
`attributes`. Do not send passwords, tokens or personal data.

For a local contract test, run `python3 scripts/test_examples.py`. It supplies
an ephemeral loopback URL and an in-memory random credential. For a real local
Logstash intake test, build the images and run `bash scripts/test_logstash.sh`.
Neither test requires Railway credentials. The integration test checks JSON
output and rejected authentication, not Elasticsearch indexing or Kibana search.
