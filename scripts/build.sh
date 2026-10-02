#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for service in elasticsearch logstash kibana; do
  docker build --platform linux/amd64 -t "elk-local/$service:test" "$service"
done
