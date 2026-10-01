# Measured usage and cost

Latest observed idle window: **2026-10-01T19:46:58.706975+00:00 → 2026-10-01T19:50:18.255225+00:00**,
**199.548250 seconds**. All services were healthy; no producer,
browser or SSH activity. Platform probes and normal background work remain.
The DLQ was filled by the deliberate adverse test, so this is not pristine
empty-stack idle. Measurement ends before the last ES upload, which only reorders
fresh-install provisioning steps; no savings from that change are claimed.

| Service | Samples | Mean RAM GB | Peak RAM GB | Mean vCPU | Peak vCPU |
|---|---:|---:|---:|---:|---:|
| Elasticsearch | 7 | 2.016190464 | 2.016649216 | 0.046470643 | 0.065285433 |
| Logstash | 7 | 0.835510857 | 0.836661248 | 0.016162019 | 0.037944867 |
| Kibana | 7 | 0.945715493 | 0.975761408 | 0.025621038 | 0.074811467 |

Raw samples, sample timestamps, exact arithmetic and limits:
[calculation](../evidence/fix/cost-summary.json), `idle-es.stdout`,
`idle-ls.stdout`, `idle-kb.stdout` and adjacent timestamped command records under
`evidence/fix/`. Samples are observed means/peaks, not continuous extrema.

Published monthly formula ([Railway pricing](https://docs.railway.com/pricing/plans),
verified 2026-10-01):

```text
10 × measured RAM GB + 20 × measured vCPU
+ 0.15 × actual occupied volume GB + 0.05 × actual public egress GB
```

Observed idle RAM/CPU sum: **3.797416814 GB**,
**0.088253700 vCPU**. At the published monthly rates, keeping
exactly that sampled RAM/CPU level for a full billing month would yield
**$39.739242137** for RAM/CPU only. This is a
conditional scenario, not a forecast, final bill, minimum or competitor comparison.
No public-traffic or storage-growth assumption is added.

Provider current-period project meter at the recorded snapshot:
**$0.033532616221**, including failed deploys, temporary diagnostic
processes, mapping rejection, queue tests and browser activity. It may lag and is
not a final invoice. Source: `usage-final.stdout` and `.meta.json`. Occupancy
snapshots may lag writes; allocated capacity is not occupied-storage cost.
Subscription fees/credits belong to the workspace and are kept separate; do not
add full subscription plus full metered usage twice.

Earlier observed runs and shorter workload/startup samples are retained in
[COST.previous.md](COST.previous.md) and EVIDENCE.previous.md. They are historical,
not blended into this latest window. No alternative was measured with comparable
idle/ingest/search/recovery workloads, so no cheapest/savings claim is supported.
