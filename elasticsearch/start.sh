#!/bin/bash
set -euo pipefail
mkdir -p /usr/share/elasticsearch/data
if find /usr/share/elasticsearch/data \( ! -uid 1000 -o ! -gid 0 \) -print -quit | read -r _; then
  chown -R 1000:0 /usr/share/elasticsearch/data
fi
exec chroot --userspec=1000:0 / python3 /opt/elk/bootstrap.py
