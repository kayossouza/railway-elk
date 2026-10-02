"""Exercise every producer against an authenticated loopback HTTP receiver."""
import base64
import http.server
import json
import os
from pathlib import Path
import secrets
import subprocess
import threading

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = secrets.token_urlsafe()
EVENTS = []
STATUS = 200


class Receiver(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        expected = "Basic " + base64.b64encode(f"shipper:{PASSWORD}".encode()).decode()
        if self.headers.get("Authorization") != expected:
            self.send_response(401)
            self.end_headers()
            return
        assert self.headers.get("Content-Type") == "application/json"
        event = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        EVENTS.append(event)
        self.send_response(STATUS)
        if STATUS == 302:
            self.send_header("Location", "/redirected")
        self.end_headers()

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Receiver)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
commands = {"node": ["node", "examples/node/send.mjs"],
            "python": ["python3", "examples/python/send.py"],
            "go": ["go", "run", "examples/go/main.go"]}
try:
    for language, command in commands.items():
        env = dict(os.environ, LOGSTASH_URL=f"http://127.0.0.1:{server.server_port}",
                   LOGSTASH_PASSWORD=PASSWORD)
        STATUS = 200
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=60)
        assert result.returncode == 0, result.stderr.decode()
        event = EVENTS[-1]
        assert event == {"message": f"hello from { {'node':'Node','python':'Python','go':'Go'}[language]}",
                         "service": f"example-{language}", "level": "info",
                         "attributes": {"language": language}}
        for status in (500, 302):
            STATUS = status
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=60)
            assert result.returncode != 0
        STATUS = 200
        env["LOGSTASH_PASSWORD"] = secrets.token_urlsafe()
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=60)
        assert result.returncode != 0
        env.pop("LOGSTASH_PASSWORD")
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=60)
        assert result.returncode != 0
        print(f"PASS {language}: JSON, Basic auth, rejection, redirect, missing variable")
finally:
    server.shutdown()
    server.server_close()
