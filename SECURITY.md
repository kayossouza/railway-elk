# Security

Do not put vulnerabilities containing credentials or exploit details in public
issues. Use GitHub's private vulnerability reporting feature if enabled. Otherwise contact the
maintainer through a private channel listed on their GitHub profile. No monitored
security mailbox or response-time promise is established by this package.

Include the affected revision, impact and minimal reproduction without real
credentials or personal data. Rotate any exposed credentials through the process
in OPERATIONS.md. Never attach Railway variable dumps.

Only Kibana should have a public HTTPS domain. Elasticsearch and Logstash use
private HTTP with authentication. This package does not provide internal TLS,
network isolation between applications in one environment, automatic backups or
high availability. Review those boundaries before handling sensitive logs.

Only the currently maintained revision receives fixes. No historical release
support window is promised. Elastic image vulnerabilities and licensing remain
subject to upstream notices; upgrade pinned images together after testing.
