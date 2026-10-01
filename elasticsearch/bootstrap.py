"""Supervise upstream ES, provision once, expose redacted authenticated readiness."""
import base64
import hashlib
import http.server
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request

ENV = {k: os.environ[k] for k in
       ("ELASTIC_PASSWORD", "KIBANA_PASSWORD", "LOGSTASH_PASSWORD")}
MARKER = Path("/usr/share/elasticsearch/data/.elk-bootstrap.json")
FINGERPRINT = hashlib.sha256(json.dumps(ENV, sort_keys=True).encode()).hexdigest()
READY = False
CLIENT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def api(path, body=None, user="elastic", password=None, allow_missing=False):
    auth = base64.b64encode(f"{user}:{password or ENV['ELASTIC_PASSWORD']}".encode()).decode()
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request("http://127.0.0.1:9200" + path, data=data,
                                 method="GET" if body is None else "PUT",
                                 headers={"Authorization": "Basic " + auth,
                                          "Content-Type": "application/json"})
    try:
        with CLIENT.open(req, timeout=5) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if allow_missing and body is None and exc.code == 404:
            return {}
        raise


def healthy():
    try:
        state = api("/_cluster/health?wait_for_status=yellow&timeout=1s")
        return state["status"] in ("yellow", "green") and not state.get("timed_out")
    except (OSError, urllib.error.URLError, ValueError):
        return False


class Probe(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        good = self.path == "/ready" and READY and healthy()
        self.send_response(200 if good else 503)
        self.end_headers()
        self.wfile.write(b"ready\n" if good else b"unavailable\n")

    def log_message(self, *_):
        pass


class Server(http.server.ThreadingHTTPServer):
    address_family = socket.AF_INET6


child = subprocess.Popen(["/usr/local/bin/docker-entrypoint.sh", "eswrapper"],
                         cwd="/usr/share/elasticsearch")


def stop(signum, _frame):
    global READY
    READY = False
    child.send_signal(signum)


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
server = Server(("::", int(os.environ.get("PORT", "8081"))), Probe)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    deadline = time.monotonic() + 300
    while not healthy():
        if child.poll() is not None:
            raise RuntimeError("Elasticsearch exited before bootstrap")
        if time.monotonic() > deadline:
            raise RuntimeError("Elasticsearch bootstrap readiness timed out")
        time.sleep(2)
    if not api("/_security/user/logstash_writer", allow_missing=True):
        api("/_security/user/elastic/_password", {"password": ENV["ELASTIC_PASSWORD"]})
        api("/_security/role/elk_writer", {
            "cluster": ["monitor"],
            "indices": [{"names": ["elk-logs", "elk-logs-*"],
                         "privileges": ["create_index", "create_doc", "auto_configure"]}]})
        # Writer creation is the final provisioning step. On an interrupted fresh
        # install, retry lifecycle/server setup before declaring initialization done.
        api("/_security/user/kibana_system/_password", {"password": ENV["KIBANA_PASSWORD"]})
        from lifecycle import configure
        configure(api)
        api("/_security/user/logstash_writer", {
            "password": ENV["LOGSTASH_PASSWORD"], "roles": ["elk_writer"]})
        temp = MARKER.with_suffix(".tmp")
        temp.write_text(json.dumps({"fingerprint": FINGERPRINT}))
        temp.replace(MARKER)
    for user, key in [("kibana_system", "KIBANA_PASSWORD"),
                      ("logstash_writer", "LOGSTASH_PASSWORD")]:
        api("/_security/_authenticate", user=user, password=ENV[key])
    READY = True
    print("ELK bootstrap complete; authenticated readiness enabled", flush=True)
    result = child.wait()
except Exception as exc:
    # Do not print API response bodies, requests or credential values.
    print(f"ELK bootstrap failed: {type(exc).__name__}: {exc}", flush=True)
    print("Database remains running for credential recovery; readiness unavailable", flush=True)
    result = child.wait()
finally:
    READY = False
    server.shutdown()
raise SystemExit(result)
