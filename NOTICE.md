# Upstream software

Dockerfiles reuse official Elastic Elasticsearch, Logstash and Kibana images.
Their existing software and licenses remain inside those images unchanged.
Custom source in this package does not replace or relicense upstream software.
No competitor repository code was copied.

The local inspection toolchain under ../evidence/build/toolchain/node_modules
and cached npm downloads are unmodified third-party packages with their original
licenses. They are not Docker build inputs or deployment assets. Their files are
excluded from the authored-source line-limit audit; authored source and split
measurement/evidence files pass that limit separately.

## Fix-stage toolchain provenance

Lock parts under lock/ contain generated npm resolution metadata, reconstructed
with SHA-256 checks by toolchain.py before npm ci. @railway/cli 5.63.1 is retained;
its installer receives one documented compatibility adaptation: tar's default
import becomes a namespace import for patched tar 7.5.22. The official CLI binary
and upstream license remain unchanged. npm audit and actual installer/IaC checks
are in evidence/fix. The Python RPM repository remains mutable despite the exact
package version; base-image pinning does not prove fully reproducible builds.
