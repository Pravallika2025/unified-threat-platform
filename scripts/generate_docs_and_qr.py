import json
import os
import qrcode
from PIL import Image

def generate_docs():
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
    public_docs_dir = os.path.join(frontend_dir, "public", "docs")
    public_redoc_dir = os.path.join(frontend_dir, "public", "redoc")
    os.makedirs(public_docs_dir, exist_ok=True)
    os.makedirs(public_redoc_dir, exist_ok=True)

    spec_path = os.path.join(backend_dir, "openapi_spec.json")
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    spec["servers"] = [
        {"url": "https://frontend-phi-indol-81.vercel.app", "description": "Cloud Production (Vercel)"},
        {"url": "http://localhost:8000", "description": "Local Development Server"},
        {"url": "/", "description": "Relative Server Path"}
    ]

    # Save to public/openapi.json
    out_spec_path = os.path.join(frontend_dir, "public", "openapi.json")
    with open(out_spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"[+] Written: {out_spec_path}")

    spec_json_str = json.dumps(spec)

    # Generate docs/index.html (Swagger UI)
    swagger_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Threat Platform // API Swagger Documentation</title>
  <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui.min.css" />
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #0f172a;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    .top-header {{
      background: #1e293b;
      border-bottom: 1px solid #334155;
      padding: 14px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .top-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .nav-links {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn {{
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s;
    }}
    .btn-dashboard {{
      background: #0284c7;
      color: #ffffff;
    }}
    .btn-dashboard:hover {{
      background: #0369a1;
    }}
    .btn-secondary {{
      background: #334155;
      color: #cbd5e1;
    }}
    .btn-secondary:hover {{
      background: #475569;
      color: #ffffff;
    }}
    /* Swagger UI Container */
    #swagger-ui {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px;
      background: #ffffff;
      border-radius: 8px;
      margin-top: 16px;
      margin-bottom: 32px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}
    .topbar {{
      display: none !important;
    }}
  </style>
</head>
<body>
  <div class="top-header">
    <div class="top-title">
      <span>🛡️ Threat Detection Platform &mdash; REST API Reference (Swagger UI)</span>
    </div>
    <div class="nav-links">
      <a href="/" class="btn btn-dashboard">← Open SOC Dashboard</a>
      <a href="/redoc" class="btn btn-secondary">Open ReDoc</a>
      <a href="/openapi.json" target="_blank" class="btn btn-secondary">OpenAPI JSON</a>
      <a href="/api/v1/health" target="_blank" class="btn btn-secondary">Health Status</a>
    </div>
  </div>

  <div id="swagger-ui"></div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-bundle.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-standalone-preset.min.js"></script>
  <script>
    const spec = {spec_json_str};
    window.onload = function() {{
      window.ui = SwaggerUIBundle({{
        spec: spec,
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        defaultModelsExpandDepth: 1,
        defaultModelExpandDepth: 1,
        docExpansion: "list"
      }});
    }};
  </script>
</body>
</html>
"""
    swagger_path = os.path.join(public_docs_dir, "index.html")
    with open(swagger_path, "w", encoding="utf-8") as f:
        f.write(swagger_html)
    print(f"[+] Written: {swagger_path}")

    # Generate redoc/index.html (ReDoc)
    redoc_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Threat Platform // ReDoc API Documentation</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
  <style>
    body {{ margin: 0; padding: 0; }}
  </style>
</head>
<body>
  <redoc spec-url="/openapi.json"></redoc>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>
"""
    redoc_path = os.path.join(public_redoc_dir, "index.html")
    with open(redoc_path, "w", encoding="utf-8") as f:
        f.write(redoc_html)
    print(f"[+] Written: {redoc_path}")

def generate_qr_codes():
    docs_assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "assets"))
    os.makedirs(docs_assets_dir, exist_ok=True)

    # 100% verified URLs
    targets = {
        "qr_frontend_vercel.png": "https://frontend-phi-indol-81.vercel.app",
        "qr_frontend_ghpages.png": "https://pravallika2025.github.io/unified-threat-platform/",
        "qr_backend_docs.png": "https://frontend-phi-indol-81.vercel.app/docs",
        "qr_backend_health.png": "https://frontend-phi-indol-81.vercel.app/api/v1/health",
        "qr_frontend_localhost.png": "http://localhost:5173",
    }

    for filename, url in targets.items():
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        out_path = os.path.join(docs_assets_dir, filename)
        img.save(out_path)
        print(f"[+] Generated QR Code for {url} -> {out_path} ({img.size})")

        # Also save JPG version if jpg exists
        jpg_name = filename.replace(".png", ".jpg")
        jpg_path = os.path.join(docs_assets_dir, jpg_name)
        img.convert("RGB").save(jpg_path)
        print(f"[+] Generated QR Code JPG -> {jpg_path}")

if __name__ == "__main__":
    generate_docs()
    generate_qr_codes()
    print("[SUCCESS] All documentation and QR codes successfully generated!")
