# ELK Stack

Elasticsearch stores logs, Logstash accepts authenticated JSON, and Kibana searches
it. Three grouped services, private internal connections and persistent data/queue
volumes. Only Kibana is public through Railway HTTPS.

Deploy the unpublished draft without editing variables. Credentials and encryption
keys are generated automatically. Follow README.md to log in, send an event and
find it in Discover. Applications must send logs from the same project/environment;
Railway platform logs are not collected automatically.

Default retention is seven days after rollover. This single-node stack is not HA,
and volumes are not backups. See OPERATIONS.md for recovery and COST.md for measured
usage. Private-source repository access is required; the template is unpublished.
