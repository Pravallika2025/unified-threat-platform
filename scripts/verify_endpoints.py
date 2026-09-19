# scripts/verify_endpoints.py
import urllib.request
import json
import sys

urls = {
    "frontend_localhost": "http://localhost:5173",
    "frontend_vercel": "https://frontend-phi-indol-81.vercel.app",
    "backend_localhost_health": "http://localhost:8000/api/v1/health",
    "backend_vercel_health": "https://frontend-phi-indol-81.vercel.app/api/v1/health",
    "backend_swagger": "https://frontend-phi-indol-81.vercel.app/docs",
}

for name, url in urls.items():
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            status = resp.status
            data = resp.read().decode("utf-8")
            try:
                json_data = json.loads(data)
                preview = json.dumps(json_data)[:200]
            except Exception:
                preview = data[:200]
            print(f"{name}: {status}\n{preview}\n")
    except Exception as e:
        print(f"{name}: ERROR {e}")
        sys.exit(1)
