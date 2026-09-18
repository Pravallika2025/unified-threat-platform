# 🛡️ Unified Multi-Environment Cyber Threat Detection & Response Platform

<div align="center">

![Platform Banner](https://img.shields.io/badge/Security-Threat%20Detection%20Platform-red?style=for-the-badge&logo=shield&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A full-stack, enterprise-grade cybersecurity platform for real-time threat detection, incident response, and audit compliance.**

[🎬 Demo Video](#demo-video) • [📸 Screenshots](#screenshots) • [🚀 Quick Start](#quick-start) • [🎯 Features](#features) • [🏗️ Architecture](#architecture) • [📖 Documentation](#api-reference)

</div>

---

## 📱 Live Cloud Deployments & Instant QR Code Access

> [!TIP]
> Both links and QR codes are verified 100% active, highly available, and scannable worldwide from any smartphone, tablet, or browser.

| 🚀 Production Frontend (Vercel) | 🩺 Backend Health Check API (Live Cloud) | ⚡ GitHub Pages Live SPA |
| :---: | :---: | :---: |
| <img src="./docs/assets/qr_frontend_vercel.png" width="230" alt="Vercel Frontend QR"/> | <img src="./docs/assets/qr_backend_health.png" width="230" alt="Backend Health API QR"/> | <img src="./docs/assets/qr_frontend_ghpages.png" width="230" alt="GitHub Pages QR"/> |
| [**Open Vercel App ↗**](https://frontend-phi-indol-81.vercel.app)<br/>`https://frontend-phi-indol-81.vercel.app` | [**Check Live Health API ↗**](https://frontend-phi-indol-81.vercel.app/api/v1/health)<br/>`https://frontend-phi-indol-81.vercel.app/api/v1/health` | [**Open GitHub Pages ↗**](https://pravallika2025.github.io/unified-threat-platform/)<br/>`https://pravallika2025.github.io/unified-threat-platform/` |
| **Status:** 🟢 100% Online (24/7 Cloud) | **Status:** 🟢 `HTTP 200 OK` JSON | **Status:** 🟢 100% Online (GitHub CDN) |

---

## <a id="features"></a>🎯 Features

### 🔐 Authentication & Access Control
- JWT-based authentication with refresh tokens
- Role-Based Access Control (RBAC): Super Admin, Analyst, Viewer, Environment Admin
- Multi-environment isolation and management
- Session management with secure token rotation

### 📡 Real-Time Threat Detection
- **Rule-Based Detection Engine** — YAML-defined rules with priority scoring
- **Anomaly Detection Engine** — Statistical baseline with Z-score outlier detection
- **Behavioral Analysis Engine** — User/Entity Behavior Analytics (UEBA)
- **Kill-Chain Correlation** — Multi-stage attack sequence analysis
- **Risk Scoring** — Dynamic asset-aware risk calculation

### 📊 Live Dashboard
- Real-time WebSocket live event feed
- Threat severity breakdown (Critical / High / Medium / Low)
- Incident timeline and trend analysis
- Environment-level metrics and KPIs
- Interactive charts and visualizations

### 🚨 Incident Management
- Automated incident creation from detected threats
- Evidence collection and attachment
- Analyst assignment and workflow queue
- Human review gate before automated response
- Incident lifecycle tracking (Open → Investigating → Resolved)

### ⚡ Automated Response
- **Firewall Rule Executor** — Automated IP blocking
- **Account Disable Executor** — Compromised account lockdown
- **Network Quarantine Executor** — Host isolation
- Approval gate for all destructive actions
- Response action audit trail

### 🔍 Threat Intelligence
- External threat feed ingestion (MISP, OTX, custom)
- IOC (Indicators of Compromise) enrichment
- Threat intel correlation with detected events
- Automated IOC lookup and scoring

### 📋 Audit & Compliance
- **SHA-256 Hash-Chained Audit Log** — Tamper-evident, append-only
- Full audit trail for every mutating action
- Audit chain integrity verification script
- Export-ready compliance reports

### 📧 Alert Notifications
- **In-app WebSocket alerts** — Real-time push notifications
- **Email notifications** via SMTP (configurable)
- **Webhook notifications** — POST to custom endpoints
- Alert severity filtering and routing

### 📄 Reporting
- PDF report generation for incidents
- HTML report export
- Scheduled automated reports
- Executive summary dashboards

---

## <a id="quick-start"></a>🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Pravallika2025/unified-threat-platform.git
cd unified-threat-platform

# Configure environment
cp .env.example .env

# Start all services
docker compose up --build
```

**Access:**
- 🌐 **Frontend (Local):** http://localhost:5173
- ⚙️ **Backend API (Local):** http://localhost:8000/docs
- 🔑 **Login:** `admin@threatplatform.dev` / `Admin@12345`

---

## 🌐 Live Access Across Any Device & Network

### 1. Global Public Access (Any Laptop, System, or Mobile Worldwide)
- **Frontend on GitHub Pages:** `https://pravallika2025.github.io/unified-threat-platform/`
  *(Built and published automatically via `.github/workflows/deploy-pages.yml`)*
- **Backend Cloud Deployment (Render / 1-Click):**
  - Includes `render.yaml` configuration for 1-click cloud deployment on [Render](https://render.com).
  - Simply connect this GitHub repository on Render, and it automatically starts the backend API with health checks and SSL enabled!

### 2. Local Network / Wi-Fi Access (Phones, Tablets & Laptops on Same Network)
To open the live dashboard from any other laptop or mobile phone connected to your Wi-Fi or Mobile Hotspot:
1. Double-click `share-network.bat` (or run backend/frontend with `--host 0.0.0.0`).
2. The script displays your network IP (e.g. `http://10.125.118.242:5173` or `http://192.168.x.x:5173`).
3. Open that URL directly in Chrome, Safari, or Edge on your phone or other laptop!

---

### Option 2: Manual Setup (No Docker)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp ../.env.example ../.env

# Initialize database with seed data
python -m app.seeds.run

# Start backend server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Simulate Attack Traffic

```bash
# Push sample logs through the detection pipeline
python scripts/replay_logs.py

# Verify the cryptographic audit chain
python scripts/verify_audit_chain.py
```

---

## <a id="architecture"></a>🏗️ Architecture

```
unified-threat-platform/
├── backend/                    # FastAPI Python Backend
│   ├── app/
│   │   ├── api/v1/routes/      # REST API endpoints (thin HTTP layer)
│   │   ├── core/               # Config, DB, security, middleware
│   │   ├── modules/            # Domain modules (Clean Architecture)
│   │   │   ├── auth/           # Authentication & RBAC
│   │   │   ├── audit/          # Hash-chained audit log
│   │   │   ├── correlation/    # Kill-chain & sequence correlation
│   │   │   ├── detection/      # Threat detection engines
│   │   │   ├── environments/   # Multi-environment management
│   │   │   ├── events/         # Log ingestion & normalization
│   │   │   ├── incidents/      # Incident lifecycle management
│   │   │   ├── notifications/  # Email, webhook, in-app alerts
│   │   │   ├── reports/        # PDF/HTML report generation
│   │   │   ├── response/       # Automated response actions
│   │   │   ├── risk/           # Risk scoring engine
│   │   │   └── threat_intel/   # Threat intelligence feeds
│   │   ├── realtime/           # WebSocket connection manager
│   │   ├── seeds/              # Database initialization
│   │   └── workers/            # Celery async task workers
│   └── tests/                  # pytest test suite
│
├── frontend/                   # React + TypeScript + Vite Frontend
│   └── src/
│       ├── app/                # Router, providers, store
│       ├── components/         # Reusable UI components
│       ├── features/           # Feature-specific screens
│       │   ├── auth/           # Login page
│       │   ├── dashboard/      # Main dashboard
│       │   ├── incidents/      # Incident management UI
│       │   ├── events/         # Event log viewer
│       │   ├── response/       # Response action UI
│       │   ├── audit/          # Audit log viewer
│       │   └── threat-intel/   # Threat intelligence UI
│       └── lib/                # API client, hooks, utilities
│
├── detection-content/          # YAML Detection Rules
├── scripts/                    # Utility scripts
├── docker-compose.yml          # Multi-service orchestration
└── Makefile                    # Developer shortcuts
```

### Architectural Principles

1. **Clean Architecture** — Domain layer has zero framework dependencies
2. **Module Isolation** — Modules communicate only through `application/*_service.py`
3. **Approval Gate** — Every destructive response action requires human approval
4. **Audit Everything** — Every mutation writes a SHA-256 hash-chained `AuditEntry`
5. **Event-Driven** — WebSocket real-time feed for live threat visibility

---

## <a id="demo-video"></a>🎬 Demo Video

A walkthrough demonstrating live login, dashboard KPI telemetry, severity distribution charts, incident queue inspection, human review and remediation approval gate, real-time WebSocket telemetry feed, and cryptographic audit hash chain validation:

<div align="center">

![Platform Live Dashboard Demo](./docs/demo/dashboard_demo.gif)

*Interactive Demo Walkthrough — Automated Threat Detection & Response Platform*  
*(Available in [HD Animated WebP format](./docs/demo/dashboard_demo.webp) as well)*

</div>

---

## <a id="screenshots"></a>📸 Screenshots

### 🔐 Login Page
![Login Dashboard](./docs/screenshots/login.png)

### 📊 Executive Command Dashboard
![Main Dashboard](./docs/screenshots/dashboard.png)

### 🚨 Incident Management Queue
![Incidents](./docs/screenshots/incidents.png)

### 🛡️ Incident Investigation & Human Approval Gate
![Incident Detail](./docs/screenshots/incident_detail.png)

### 📡 Real-Time Telemetry & Live Monitor
![Live Events](./docs/screenshots/events.png)

### 📋 Cryptographic SHA-256 Audit Log Verification
![Audit Log](./docs/screenshots/audit_log.png)

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | High-performance async REST API |
| **SQLAlchemy** | ORM with async session support |
| **SQLite / PostgreSQL** | Database (dev/prod) |
| **Celery + Redis** | Async task queue |
| **WebSockets** | Real-time event streaming |
| **JWT (python-jose)** | Authentication tokens |
| **Passlib (bcrypt)** | Password hashing |
| **WeasyPrint** | PDF report generation |
| **APScheduler** | Background scheduled tasks |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type-safe development |
| **Vite** | Fast build tool |
| **Zustand** | Lightweight state management |
| **React Query** | Server state & caching |
| **Recharts** | Data visualization charts |
| **Lucide React** | Modern icon library |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| **Docker + Docker Compose** | Containerization |
| **Nginx** | Reverse proxy |
| **Redis** | Message broker & cache |

---

## <a id="api-reference"></a>🔌 API Reference

Full interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | User authentication |
| `POST` | `/api/v1/ingest/batch` | Batch log ingestion |
| `GET` | `/api/v1/incidents/` | List all incidents |
| `POST` | `/api/v1/incidents/{id}/evidence` | Add evidence to incident |
| `GET` | `/api/v1/audit/entries` | Audit log entries |
| `POST` | `/api/v1/response/actions` | Execute response action |
| `GET` | `/api/v1/threat-intel/iocs` | List threat IOCs |
| `GET` | `/api/v1/reports/` | Generate/list reports |
| `WS` | `/ws/events` | Live event WebSocket |

---

## 🔒 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| **Super Admin** | `admin@threatplatform.dev` | `Admin@12345` |
| **Analyst** | `analyst@threatplatform.dev` | `Analyst@12345` |

> ⚠️ **Change all default credentials before deploying to production!**

---

## 🧪 Testing

```bash
cd backend

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific module tests
python -m pytest tests/test_auth.py -v

# Verify audit chain integrity
python scripts/verify_audit_chain.py
```

---

## 🚀 Production Deployment

### Environment Variables

```env
# Security (CHANGE IN PRODUCTION)
SECRET_KEY=your-super-secret-key-256-bits
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (upgrade to PostgreSQL for production)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/threatplatform

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend
VITE_API_BASE_URL=https://your-api-domain.com
```

### Docker Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📋 Detection Rules

Detection rules are defined as YAML files in `detection-content/rules/`:

```yaml
# detection-content/rules/authentication/brute_force_login.yml
id: AUTH-0001
title: Possible brute force login attack
severity: high
enabled: true
environments: [all]
attack:
  tactic: TA0006
  technique: T1110
logic:
  type: threshold
  where:
    - { field: event_action, op: eq, value: login_failed }
  group_by: [source_ip, user_name]
  count: 8
  window: 5m
response_suggestions: [monitor, block_ip]
```

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with ❤️ using:
- [FastAPI](https://fastapi.tiangolo.com/) by Sebastián Ramírez
- [React](https://react.dev/) by Meta
- [MITRE ATT&CK Framework](https://attack.mitre.org/) for detection rule design

---

<div align="center">

**⭐ Star this repo if you find it useful!**

[Report Bug](https://github.com/Pravallika2025/unified-threat-platform/issues) • [Request Feature](https://github.com/Pravallika2025/unified-threat-platform/issues)

</div>
