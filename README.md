# ELK on Railway

Elasticsearch stores logs, Logstash accepts JSON, and Kibana searches it.
Three services in one **ELK Stack** group; internal traffic stays private.
Only Kibana is public, through Railway HTTPS.

## One-click deploy

[Deploy the unpublished ELK draft](https://railway.com/deploy/KPF5VY).
Select your workspace and click **Deploy**. For an existing empty project, select
it, click **Review and deploy**, then **Deploy Template**. No variable editing,
CLI, scripts or manual wiring is needed. Wait for all three services to be healthy.
This private test draft requires source-repository access; it is not published in
the marketplace. For the quality gate, use the empty project `bounty-test-elk-3`.

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
Choose **Explore on my own** on the welcome screen. Keep generated credentials
and encryption keys stable. Send the first event
below before creating a data view.

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

To try it without an application, install/login to the current Railway CLI, link your
ELK project (`railway link`), then copy this command. It uses the generated
credential inside Logstash and prints no secret:

```bash
railway ssh --service Logstash -- \
  'curl --fail-with-body --user "shipper:$INPUT_PASSWORD" -H "Content-Type: application/json" http://127.0.0.1:8080 -d "{\"message\":\"hello from Railway\",\"service\":\"my-app\",\"level\":\"info\"}"'
```

After sending data, open **☰ → Analytics → Discover**. Open the data-view
selector (initially **All logs**) and choose **Create a data view**: name `Logs`, index
pattern `elk-logs`, time field `@timestamp`. Select `Logs`, set the time range to
**Last 15 minutes**, and search
`message : "hello from Railway"`. A successful intake response means accepted;
finding the event confirms delivery. Private intake is unavailable from your laptop.
For a smoke test, use each service’s deployment menu to **Redeploy**, then
**Restart**; wait for that deployment to become healthy and search the same event.
Send another event to confirm recovery. Keep secrets and volumes unchanged.

## Cost

Previous live test: **$39.74/month RAM + CPU** if its short sampled idle usage
continues for a month: 3.7974 GB RAM and 0.08825 vCPU, seven samples per service
over 199.55 seconds. This is rate arithmetic, not a monthly invoice. Storage,
public egress and workspace subscription/credits are additional considerations.
See [measured cost](COST.md) for raw measurements and published rates.
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
