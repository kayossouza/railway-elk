"""Test producers on real Logstash HTTP intake, with stdout instead of ES."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
name = "elk-example-test-" + secrets.token_hex(4)
env = dict(os.environ, INPUT_PASSWORD=secrets.token_urlsafe())
commands = {"node": ["node", "examples/node/send.mjs"],
            "python": ["python3", "examples/python/send.py"],
            "go": ["go", "run", "examples/go/main.go"]}


def docker(*args):
    return subprocess.run(["docker", *args], env=env, check=True,
                          capture_output=True, text=True).stdout


try:
    docker("run", "-d", "--platform", "linux/amd64", "--name", name, "--user", "1000:0",
           "-p", "127.0.0.1::8080", "-e", "INPUT_PASSWORD",
           "-e", "LS_JAVA_OPTS=-Xms256m -Xmx256m -XX:TieredStopAtLevel=1",
           "-v", f"{ROOT / 'scripts/intake-test.conf'}:/tmp/intake.conf:ro",
           "--entrypoint", "/usr/share/logstash/bin/logstash",
           "elk-local/logstash:test", "-f", "/tmp/intake.conf",
           "--path.data", "/tmp/test-data")
    port = docker("port", name, "8080/tcp").strip().rsplit(":", 1)[1]
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 600
    while True:
        try:
            urllib.request.urlopen(urllib.request.Request(url, data=b"{}"), timeout=2)
            raise AssertionError("Unauthenticated intake succeeded")
        except urllib.error.HTTPError as error:
            assert error.code == 401, error.code
            break
        except (OSError, TimeoutError):
            if docker("inspect", "--format", "{{.State.Running}}", name).strip() != "true":
                raise RuntimeError("Logstash exited during startup")
            if time.monotonic() > deadline:
                raise RuntimeError("Logstash did not become ready")
            time.sleep(1)
    print("PASS real Logstash: unauthenticated request rejected")
    for language, command in commands.items():
        producer_env = dict(os.environ, LOGSTASH_URL=url,
                            LOGSTASH_PASSWORD=env["INPUT_PASSWORD"])
        result = subprocess.run(command, cwd=ROOT, env=producer_env,
                                capture_output=True, timeout=60)
        assert result.returncode == 0, result.stderr.decode()
        producer_env["LOGSTASH_PASSWORD"] = secrets.token_urlsafe()
        result = subprocess.run(command, cwd=ROOT, env=producer_env,
                                capture_output=True, timeout=60)
        assert result.returncode != 0
        print(f"PASS real Logstash: {language} accepted; wrong password rejected")
    deadline = time.monotonic() + 30
    while True:
        events = []
        for line in docker("logs", name).splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        found = {event.get("service") for event in events if isinstance(event, dict)}
        if all(f"example-{language}" in found for language in commands):
            break
        if time.monotonic() > deadline:
            raise AssertionError("Missing decoded Logstash output")
        time.sleep(1)
    for language in commands:
        event = next(e for e in events if e.get("service") == f"example-{language}")
        assert event["attributes"]["language"] == language
        assert event["level"] == "info" and event["@timestamp"]
        assert "_jsonparsefailure" not in event.get("tags", [])
    print("PASS real Logstash: all producer JSON decoded with timestamps")
finally:
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
