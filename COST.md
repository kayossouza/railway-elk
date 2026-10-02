# Measured cost

Historical quality-test project: `bounty-test-elk-3`, Pro workspace, after smoke and recovery tests.
Idle window: **2026-10-01T21:08:18.971916+00:00 → 2026-10-01T21:12:18.989018+00:00**, **240.017102 seconds**.
No producer, SSH, deploy or Kibana browser traffic during the window. Platform
probes and normal background work remain. This is a short small-workload sample.

| Service | Samples | Mean RAM GB | Peak RAM GB | Mean vCPU | Peak vCPU |
|---|---:|---:|---:|---:|---:|
| Elasticsearch | 8 | 1.585055744 | 1.665200128 | 0.059367437 | 0.098971200 |
| Logstash | 8 | 0.729494016 | 0.732196864 | 0.012570813 | 0.019050067 |
| Kibana | 8 | 0.898765312 | 0.919314432 | 0.041415975 | 0.088427967 |

Total means: **3.213315072 GB RAM**, **0.113354225 vCPU**.
At [Railway's published rates](https://docs.railway.com/pricing/plans), checked
2026-10-01, maintaining these sampled levels for a billing month gives
**$34.400235220/month RAM + CPU**. This is a conditional usage scenario, not an
invoice, sustained-load forecast, proven minimum or competitor-savings claim.
RAM includes native memory and filesystem cache, not just JVM/V8 heaps.

```text
10 × RAM GB + 20 × vCPU
+ 0.15 × actual occupied volume GB + 0.05 × actual public egress GB
```

Final provider project meter snapshot: **$0.016969290547** for this
project's test usage, including reported storage and public egress. It may lag
and is not a final invoice. Allocated volume capacity is not occupied storage;
provider occupancy snapshots can lag writes. Storage growth and monthly traffic
are excluded from the RAM/CPU scenario; no arbitrary allowance is invented.
Workspace subscription and included credits must not be double counted.

Raw CPU/RAM samples are in [docs/cost](docs/cost). The provenance file records
hashes of the historical provider exports and the project meter value.
[cost-summary.json](cost-summary.json) contains sample times, full precision and
calculation limits. Samples outside the stated idle window are not averaged.
Free/Trial compatibility and long-term load capacity were not validated.

No new idle cost window was measured for this documentation package.
