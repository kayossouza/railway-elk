"""Parse configs and enforce a small set of repository invariants."""
import ast
import json
from pathlib import Path
import re
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
files = [p for p in ROOT.rglob("*") if p.is_file()
         and not any(part in {".git", "__pycache__", "node_modules"} for part in p.parts)]
for path in files:
    text = path.read_text()
    assert len(text.splitlines()) <= 400, path
    assert "\u2014" not in text, f"Em dash: {path}"
    if path.suffix == ".json":
        json.loads(text)
    if path.suffix in {".yml", ".yaml"}:
        yaml.safe_load(text)
    if path.suffix == ".py":
        ast.parse(text)
    if path.suffix == ".sh":
        subprocess.run(["bash", "-n", str(path)], check=True)
    if path.suffix in {".cjs", ".mjs"}:
        subprocess.run(["node", "--check", str(path)], check=True)
for service in ("elasticsearch", "logstash", "kibana"):
    directory = ROOT / service
    dockerfile = (directory / "Dockerfile").read_text()
    assert re.search(r"^FROM docker\.elastic\.co/.+:9\.5\.4@sha256:[0-9a-f]{64}$",
                     dockerfile, re.M), service
    config = json.loads((directory / "railway.json").read_text())
    assert config["build"]["dockerfilePath"] == "Dockerfile"
    assert config["deploy"]["healthcheckPath"].startswith("/")
formatted = subprocess.run(["gofmt", "-d", "examples/go/main.go"], cwd=ROOT,
                           check=True, capture_output=True).stdout
assert not formatted, "Run gofmt"
summary = json.loads((ROOT / "cost-summary.json").read_text())
for short, name in [("es", "Elasticsearch"), ("ls", "Logstash"), ("kb", "Kibana")]:
    metrics = json.loads((ROOT / f"docs/cost/idle-{short}.json").read_text())["measurements"]
    expected = next(service for service in summary["services"] if service["service"] == name)
    for metric, target in [("MEMORY_USAGE_GB", "ram_mean_gb"), ("CPU_USAGE", "cpu_mean_vcpu")]:
        values = [sample["value"] for sample in metrics[metric]
                  if sample["ts"] in expected["sample_times"]]
        assert len(values) == expected["samples"]
        assert abs(sum(values) / len(values) - expected[target]) < 1e-12
assert abs(10 * summary["totals"]["ram_gb"] + 20 * summary["totals"]["cpu_vcpu"]
           - summary["monthly_ram_cpu_at_sampled_idle_usd"]) < 1e-10
for path in files:
    if path.suffix == ".md":
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if not target.startswith(("https://", "http://", "#")):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
print("PASS: JSON/YAML, Python/Node/shell syntax, Go formatting, image pins, file limits, cost arithmetic, local links")
