"""Send one JSON event with standard-library HTTP and Basic auth."""
import base64
import json
import os
import sys
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


url = os.environ.get("LOGSTASH_URL")
password = os.environ.get("LOGSTASH_PASSWORD")
if not url or not password:
    sys.exit("Set LOGSTASH_URL and LOGSTASH_PASSWORD")
event = {"message": "hello from Python", "service": "example-python",
         "level": "info", "attributes": {"language": "python"}}
auth = base64.b64encode(f"shipper:{password}".encode()).decode()
request = urllib.request.Request(url, data=json.dumps(event).encode(), headers={
    "Content-Type": "application/json", "Authorization": f"Basic {auth}"},
    method="POST")
try:
    with urllib.request.build_opener(NoRedirect).open(request, timeout=10) as response:
        if not 200 <= response.status < 300:
            raise RuntimeError("Intake rejected event")
    print("Event accepted. Confirm indexing in Kibana.")
except Exception:
    sys.exit("Send failed. Check connectivity and intake credentials.")
