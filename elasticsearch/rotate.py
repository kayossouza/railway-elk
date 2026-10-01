"""Private interactive, resumable native identity rotation; no secrets in argv."""
import argparse
import base64
import getpass
import hashlib
import json
import os
from pathlib import Path
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('user', choices=['elastic', 'kibana_system', 'logstash_writer'])
parser.add_argument('--finalize', action='store_true')
args = parser.parse_args()
admin = getpass.getpass('Current admin password: ')
new = getpass.getpass('New identity password: ')
if not new:
    raise SystemExit('Empty password refused')
client = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(path, user, password, body=None):
    token = base64.b64encode((user + ':' + password).encode()).decode()
    req = urllib.request.Request('http://127.0.0.1:9200' + path,
        headers={'Authorization':'Basic '+token,'Content-Type':'application/json'},
        data=None if body is None else json.dumps(body).encode(),
        method='GET' if body is None else 'POST')
    with client.open(req, timeout=10) as response:
        return json.load(response)
request('/_security/_authenticate', 'elastic', admin)
if not args.finalize:
    request('/_security/user/' + args.user + '/_password', 'elastic', admin, {'password':new})
request('/_security/_authenticate', args.user, new)
if args.finalize:
    keys = {'elastic':'ELASTIC_PASSWORD','kibana_system':'KIBANA_PASSWORD','logstash_writer':'LOGSTASH_PASSWORD'}
    values = {key:os.environ[key] for key in keys.values()}
    if values[keys[args.user]] != new:
        raise SystemExit('Runtime variable differs; redeploy with new secret before finalize')
    for user,key in keys.items():
        request('/_security/_authenticate',user,values[key])
    marker=Path('/usr/share/elasticsearch/data/.elk-bootstrap.json')
    temporary=marker.with_suffix('.tmp')
    temporary.write_text(json.dumps({'fingerprint':hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()}))
    temporary.replace(marker)
print('Native authentication verified; '+ ('metadata finalized' if args.finalize else 'update matching Railway variable, redeploy and verify consumer before finalize'))
