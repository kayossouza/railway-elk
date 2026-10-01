"""Built-in ILM and bounded mapping for NEW installations; no destructive migration."""
import os


def configure(api):
    retention = os.environ.get("LOG_RETENTION", "7d")
    rollover = os.environ.get("LOG_ROLLOVER_SIZE", "1gb")
    import re
    if retention != "forever" and not re.fullmatch(r"[1-9][0-9]*[dhms]", retention):
        raise ValueError("Invalid LOG_RETENTION")
    if not re.fullmatch(r"[1-9][0-9]*(mb|gb)", rollover):
        raise ValueError("Invalid LOG_ROLLOVER_SIZE")
    phases = {"hot": {"actions": {"rollover": {"max_primary_shard_size": rollover, "max_age": "1d"}}}}
    if retention != "forever":
        phases["delete"] = {"min_age": retention, "actions": {"delete": {}}}
    api("/_ilm/policy/elk_logs", {"policy": {"phases": phases}})
    api("/_index_template/elk_logs", {
        "index_patterns": ["elk-logs-*"], "priority": 501,
        "template": {"settings": {"number_of_shards": 1, "number_of_replicas": 0,
            "index.lifecycle.name": "elk_logs", "index.lifecycle.rollover_alias": "elk-logs"},
            "mappings": {"dynamic": False, "properties": {
                "@timestamp": {"type": "date"}, "message": {"type": "text"},
                "service": {"type": "keyword"}, "level": {"type": "keyword"},
                "elk_test_run": {"type": "keyword"}, "sequence": {"type": "long"},
                "attributes": {"type": "flattened"}}}}})
    import urllib.error
    try:
        api("/elk-logs/_alias")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        api("/elk-logs-000001", {"aliases": {"elk-logs": {"is_write_index": True}}})
