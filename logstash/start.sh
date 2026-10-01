#!/bin/bash
set -euo pipefail
mkdir -p /usr/share/logstash/data
if find /usr/share/logstash/data \( ! -uid 1000 -o ! -gid 0 \) -print -quit | read -r _; then
  chown -R 1000:0 /usr/share/logstash/data
fi
printf '%s\n' 'Mount ownership checked; waiting for Elasticsearch provisioning'
# The output plugin treats initial 401 as fatal. Wait for user provisioning.
for ((attempt=0; attempt<150; attempt++)); do
  if curl --noproxy '*' -fsS --max-time 3 "${ELASTICSEARCH_READY_URL}" >/dev/null 2>&1; then
    exec chroot --userspec=1000:0 / /usr/local/bin/docker-entrypoint
  fi
  if (( attempt % 30 == 0 )); then
    printf '%s\n' 'Elasticsearch provisioning not reachable yet'
  fi
  sleep 2
done
printf '%s\n' 'Elasticsearch bootstrap not ready; refusing to start ingestion' >&2
exit 1
