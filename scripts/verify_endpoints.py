# scripts/verify_endpoints.py
import urllib.request
import json
import sys

cloud_urls = {
    "frontend_vercel": "https://frontend-phi-indol-81.vercel.app",
    "backend_vercel_health": "https://frontend-phi-indol-81.vercel.app/api/v1/health",
    "backend_swagger_ui": "https://frontend-phi-indol-81.vercel.app/docs",
    "backend_openapi_json": "https://frontend-phi-indol-81.vercel.app/openapi.json",
    "frontend_github_pages": "https://pravallika2025.github.io/unified-threat-platform/",
}

local_urls = {
    "frontend_localhost": "http://localhost:5173",
    "backend_localhost_health": "http://localhost:8000/api/v1/health",
    "backend_localhost_docs": "http://localhost:8000/docs",
}

print("=" * 60)
print("VERIFYING LIVE CLOUD PRODUCTION ENDPOINTS")
print("=" * 60)

cloud_success = True
for name, url in cloud_urls.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EndpointVerifier/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            data = resp.read().decode("utf-8", errors="ignore")
            try:
                json_data = json.loads(data)
                preview = json.dumps(json_data)[:120]
            except Exception:
                preview = data[:120].replace("\n", " ")
            print(f"[OK] {name} ({status}): {url}\n     Preview: {preview}...\n")
    except Exception as e:
        print(f"[FAILED] {name}: {url}\n         ERROR: {e}\n")
        cloud_success = False

print("=" * 60)
print("CHECKING LOCALHOST ENDPOINTS (Optional - if servers running)")
print("=" * 60)

for name, url in local_urls.items():
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            status = resp.status
            print(f"[ACTIVE] {name} ({status}): {url}")
    except Exception:
        print(f"[OFFLINE] {name}: Local server not started (run start.bat to start)")

print("=" * 60)
if cloud_success:
    print("[SUCCESS] All cloud production endpoints & Swagger docs verified working 100%!")
else:
    print("[ERROR] Some cloud endpoints failed. Please check network/deployments.")
    sys.exit(1)
