const { LOGSTASH_URL: url, LOGSTASH_PASSWORD: password } = process.env;
if (!url || !password) {
  console.error('Set LOGSTASH_URL and LOGSTASH_PASSWORD');
  process.exit(1);
}
try {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Basic ${Buffer.from(`shipper:${password}`).toString('base64')}`,
    },
    body: JSON.stringify({
      message: 'hello from Node', service: 'example-node', level: 'info',
      attributes: { language: 'node' },
    }),
    signal: AbortSignal.timeout(10000),
    redirect: 'error',
  });
  if (!response.ok) throw new Error(`Intake returned HTTP ${response.status}`);
  console.log('Event accepted. Confirm indexing in Kibana.');
} catch {
  console.error('Send failed. Check connectivity and intake credentials.');
  process.exit(1);
}
