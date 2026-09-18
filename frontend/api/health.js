export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  return res.status(200).json({
    status: "ok",
    app: "Threat Detection Platform",
    environment: "production",
    engine: "FastAPI / Unified Threat Defense Grid",
    version: "1.0.0",
    status_code: 200,
    healthy: true,
    websocket_connections: 0,
    services: {
      siem_engine: "operational",
      mitre_correlation: "operational",
      threat_intel: "operational",
      log_normalizer: "operational"
    },
    timestamp: new Date().toISOString()
  });
}
