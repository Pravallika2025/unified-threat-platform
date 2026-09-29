# 🧭 Step-by-Step Project Architecture & Implementation Guide
### Unified Multi-Environment Cyber Threat Detection & Response Platform

This guide arranges all components, files, and modules of the repository in sequential, step-by-step order from data ingestion to live response and compliance.

---

## 📑 Table of Contents (Step-by-Step Order)

- [Step 1: Academic Flashcard & Project Overview](#step-1-academic-flashcard--project-overview)
- [Step 2: Threat Ingestion & Detection Rule Engine](#step-2-threat-ingestion--detection-rule-engine)
- [Step 3: Backend REST API & Authentication](#step-3-backend-rest-api--authentication)
- [Step 4: Machine Learning Anomaly Detection & Risk Scoring](#step-4-machine-learning-anomaly-detection--risk-scoring)
- [Step 5: Tamper-Evident Cryptographic Audit Trail](#step-5-tamper-evident-cryptographic-audit-trail)
- [Step 6: Alert Dispatch & Real-Time SMTP Email Protocol](#step-6-alert-dispatch--real-time-smtp-email-protocol)
- [Step 7: Frontend SOC Dashboard & Operator Governance](#step-7-frontend-soc-dashboard--operator-governance)
- [Step 8: Verified Live Deployment & Local Execution Links](#step-8-verified-live-deployment--local-execution-links)

---

## 🎯 Step 1: Academic Flashcard & Project Overview
**Directory:** [`docs/`](docs/)

| File | Purpose | Link |
| :--- | :--- | :--- |
| `docs/project_flash_card.html` | High-definition interactive web presentation flashcard matching the required university format | [View File](docs/project_flash_card.html) |
| `docs/project_flash_card.pdf` | Printable A4 Academic Poster PDF for thesis evaluation | [View File](docs/project_flash_card.pdf) |
| `docs/project_flash_card.png` | 300 DPI high-resolution poster graphic | [View File](docs/project_flash_card.png) |
| `docs/PROJECT_FLASH_CARD.md` | Markdown documentation of all research questions & technical answers | [View File](docs/PROJECT_FLASH_CARD.md) |

---

## 📡 Step 2: Threat Ingestion & Detection Rule Engine
**Directory:** [`detection-content/`](detection-content/)

The detection engine ingests security events across cloud, campus network, and endpoint environments.
- **Rules Directory:** [`detection-content/rules/`](detection-content/rules/)
  - `brute_force_login.yaml` — Multi-attempt credential attack detection.
  - `privilege_escalation.yaml` — Unauthorized role promotion detection.
  - `data_exfiltration.yaml` — Outbound data transfer spikes over threshold.
  - `ransomware_canary.yaml` — Rapid file modification & canary file encryption detection.
  - `cloud_credential_access.yaml` — Cloud IAM access token theft detection.
- **Schema & Validation:** [`detection-content/schemas/`](detection-content/schemas/) — Strict JSON schemas validating rule integrity before loading into memory.

---

## ⚙️ Step 3: Backend REST API & Authentication
**Directory:** [`backend/`](backend/)

Built with **FastAPI (Python 3.11+)** and **Pydantic v2**:
- **Application Core:** [`backend/app/core/`](backend/app/core/)
  - `config.py` — Central environment settings, CORS configurations, and secrets.
  - `database.py` — Async SQLAlchemy engine with SQLite / PostgreSQL support.
  - `security.py` — Argon2 password hashing and JWT access/refresh token generation.
- **Domain Modules:** [`backend/app/modules/`](backend/app/modules/)
  - `auth/` — User login, MFA TOTP verification, and session management.
  - `users/` — Operator management, role assignment, and account governance.
  - `detection/` — Ingestion worker and real-time rule evaluation pipeline.
  - `incidents/` — Incident tracking lifecycle (Open → Investigating → Contained → Resolved).

---

## 🧠 Step 4: Machine Learning Anomaly Detection & Risk Scoring
**Directory:** [`backend/app/modules/analytics/`](backend/app/modules/analytics/)

- **Dynamic Risk Score Engine (`risk_calculator.py`):**
  $$\text{Risk Score} = (\text{Rule Severity} \times 0.4) + (\text{Asset Criticality} \times 0.35) + (\text{Anomaly Z-Score} \times 0.25)$$
- **Anomaly Baseline Engine (`baseline.py`):** Calculates continuous rolling Gaussian distributions ($Z$-score outlier cutoff $\ge 2.5$).
- **Kill-Chain Correlation (`correlator.py`):** Tracks MITRE ATT&CK stages (Reconnaissance → Initial Access → Lateral Movement → Exfiltration).

---

## 🔒 Step 5: Tamper-Evident Cryptographic Audit Trail
**Directory:** [`backend/app/modules/audit/`](backend/app/modules/audit/)

Provides mathematical proof of log integrity for regulatory and legal compliance:
- **Hash-Chain Service (`audit_service.py`):**
  $$\text{Hash}_n = \text{SHA-256}(\text{Record}_n \,||\, \text{Timestamp} \,||\, \text{Action} \,||\, \text{Hash}_{n-1})$$
- **Verification Script:** [`scripts/verify_audit_chain.py`](scripts/verify_audit_chain.py) — Verifies the entire database hash chain to ensure zero tampering.

---

## 📧 Step 6: Alert Dispatch & Real-Time SMTP Email Protocol
**Directory:** [`backend/app/modules/notifications/`](backend/app/modules/notifications/)

3-Channel notification architecture prevents alert fatigue:
1. **WebSocket Dispatch:** Broadcasts every security event instantaneously to connected SOC consoles.
2. **Real-Time SMTP Protocol (`email_notifier.py`):** Sends styled HTML emergency emails via Google SMTP (`smtp.gmail.com:587`) or custom mail server directly to Security Officers and Administrators for **HIGH** and **CRITICAL** threats.
3. **Webhook Fan-Out:** Pushes JSON alerts to external SIEM / Slack / Microsoft Teams webhooks.

---

## 💻 Step 7: Frontend SOC Dashboard & Operator Governance
**Directory:** [`frontend/`](frontend/)

Modern single-page application built with **React 18 + TypeScript + Vite + Tailwind CSS**:
- **Live SOC Monitor:** Real-time event ingestion stream and severity distribution charts.
- **Incident Investigation:** Detailed incident timeline, evidence artifacts, and containment approval gate.
- **Operator Governance (`/users`):** Full administrator console to create, assign roles, and toggle status for Security Analysts and Auditors.
- **Real-Time SMTP Settings Modal (`/alerts`):** In-app UI allowing security administrators to test and configure live SMTP mail credentials on the fly.
- **Gemini AI Security Analyst (`/ai-analyst`):** Generative AI assistant analyzing raw security logs and suggesting concrete mitigation playbooks.

---

## 🌐 Step 8: Verified Live Deployment & Local Execution Links

### ☁️ Production Cloud Links (Available 24/7 Globally)
- 🚀 **Live Production Dashboard (Vercel):** [https://frontend-phi-indol-81.vercel.app](https://frontend-phi-indol-81.vercel.app)
- ⚡ **Live Production Mirror (GitHub Pages):** [https://pravallika2025.github.io/unified-threat-platform/](https://pravallika2025.github.io/unified-threat-platform/)
- 📑 **Interactive OpenAPI Swagger Docs:** [https://pravallika2025.github.io/unified-threat-platform/docs/](https://pravallika2025.github.io/unified-threat-platform/docs/)
- 📖 **Alternative API Reference (ReDoc):** [https://pravallika2025.github.io/unified-threat-platform/redoc/](https://pravallika2025.github.io/unified-threat-platform/redoc/)
- 📊 **Raw OpenAPI 3.1 Spec:** [https://pravallika2025.github.io/unified-threat-platform/openapi.json](https://pravallika2025.github.io/unified-threat-platform/openapi.json)

### 💻 Localhost Running Links (Active When Local Servers Are Started)
- 🌐 **Frontend Local Dashboard:** [http://localhost:5173](http://localhost:5173)
- 📑 **Backend Local Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 📖 **Backend Local ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 🔑 **Default Credentials:** `admin@threatplatform.dev` / `Admin@12345`

### 🚀 One-Click Local Launcher
Simply double-click [`start.bat`](start.bat) in the project root to automatically launch both the Python backend API and the React frontend dashboard simultaneously!
