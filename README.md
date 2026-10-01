# ELK on Railway

Elasticsearch stores logs, Logstash accepts JSON, and Kibana searches it.
Three services in one **ELK Stack** group; internal traffic stays private.
Only Kibana is public, through Railway HTTPS.

## One-click deploy

The unpublished deployment link is pending the fresh-template gate. This source
is not yet ready to claim one-click deployment. No template has been published.

The intended deployment needs no password or connection setup: Railway generates
all secrets and resolves private service references. Wait for all services to be
healthy before opening Kibana.

## What you get

- Authenticated intake and a restricted Elasticsearch writer.
- Elasticsearch data and Logstash queue volumes; saved Kibana views live in ES.
- Automatic log rollover and retention on new installs. Default retention is
  seven days after rollover; this is a configuration choice, not a capacity claim.

Application logs must be sent explicitly. Railway platform logs are not collected
automatically. This is a single-node stack; volumes provide persistence, not HA
or backups.

## First login

Open **Kibana → Settings → Networking** and follow its HTTPS domain.
Log in as `elastic` with **Elasticsearch → Variables → ELASTIC_PASSWORD**.
Use **Discover → Create data view**: name `Logs`, index pattern `elk-logs`,
time field `@timestamp`. Keep generated credentials and encryption keys stable.

## Send data

In your application's Railway Variables tab, paste:

```text
LOGSTASH_URL=http://${{Logstash.RAILWAY_PRIVATE_DOMAIN}}:8080
LOGSTASH_PASSWORD=${{Logstash.INPUT_PASSWORD}}
```

Run this from that application, in the **same project and environment**:

```bash
curl --fail-with-body --user "shipper:$LOGSTASH_PASSWORD" \
  -H 'Content-Type: application/json' "$LOGSTASH_URL" \
  -d '{"message":"hello from Railway","service":"my-app","level":"info"}'
```

In Discover, select `Logs`, set the time range to **Last 15 minutes**, and search
`message : "hello from Railway"`. A successful intake response means accepted;
finding the event confirms delivery. Private intake is unavailable from your laptop.

## Cost

Previous live test: **$39.74/month RAM + CPU** if its short sampled idle usage
continues for a month: 3.7974 GB RAM and 0.08825 vCPU, seven samples per service
over 199.55 seconds. This is rate arithmetic, not a monthly invoice. Storage,
public egress and workspace subscription/credits are additional considerations.
See [measured cost](../../src/COST.md) for raw measurements and published rates.
A final fresh-run measurement is pending.

## Troubleshooting

1. **Login fails:** use `elastic`, not `kibana_system`. Retrieve the generated
   password from Elasticsearch. Changing its variable alone does not rotate a
   persisted native user; restore the original or follow [rotation](OPERATIONS.md).
2. **No logs:** send from the same environment; check intake credentials and
   Logstash deployment logs. Select `elk-logs` and expand Discover's time range.
3. **Startup/recovery fails:** check Elasticsearch first, then Logstash/Kibana
   logs. Preserve volumes, original secrets and encryption keys when redeploying.
   Never delete data to repair a password mismatch.

## Upgrade

Take and verify supported Elasticsearch snapshots, then upgrade the stack's
three pinned versions together following Elastic's supported upgrade path.
Test the change on a disposable project first. For configuration rollback,
redeploy the last verified source with unchanged secrets, versions and volumes.
Do not downgrade Elasticsearch against upgraded data.
