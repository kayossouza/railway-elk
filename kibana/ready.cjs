// A redacted readiness bridge: Kibana's unauthenticated status can remain stale
// during ES failure. Check the destination with the existing server identity.
const http = require('node:http');
const {spawn} = require('node:child_process');
const child = spawn('/usr/local/bin/kibana-docker', [], {stdio: 'inherit'});
let stopping = false;
let expectedShutdown = false;
for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => {
    stopping = true;
    expectedShutdown = true;
    child.kill(signal);
  });
}
const server = http.createServer(async (req, res) => {
  let good = false;
  try {
    if (req.url === '/ready' && !stopping) {
      const auth = Buffer.from(`kibana_system:${process.env.KIBANA_PASSWORD}`).toString('base64');
      const [es, kb] = await Promise.all([
        fetch(`${process.env.ELASTICSEARCH_URL}/_cluster/health?wait_for_status=yellow&timeout=1s`, {
          headers: {Authorization: `Basic ${auth}`}, signal: AbortSignal.timeout(3000),
        }),
        fetch(`http://127.0.0.1:${process.env.UI_PORT || '5601'}/api/status`, {
          signal: AbortSignal.timeout(3000),
        }),
      ]);
      if (es.ok && kb.ok) {
        const cluster = await es.json();
        const status = await kb.json();
        good = ['yellow', 'green'].includes(cluster.status) && !cluster.timed_out &&
               status.status.overall.level === 'available';
      }
    }
  } catch (_) {
    // No response body, credentials or URLs enter logs or the public probe body.
  }
  res.writeHead(good ? 200 : 503, {'Content-Type': 'text/plain'});
  res.end(good ? 'ready\n' : 'unavailable\n');
});
server.listen(Number(process.env.PORT || '8082'), '::');
server.on('error', () => {
  stopping = true;
  console.error('Kibana readiness listener failed');
  child.kill('SIGTERM');
});
child.on('error', () => {
  console.error('Kibana upstream process failed to start');
  process.exit(1);
});
child.on('exit', (code, signal) => {
  stopping = true;
  server.close();
  process.exit(expectedShutdown ? 0 : (code || 1));
});
