# Unified Multi-Environment Cyber Threat Detection & Response Platform

Defensive security platform: authorized log ingestion -> normalization -> detection ->
risk scoring -> correlation -> incident -> **human review** -> response -> audit.

## Quick start (Docker — recommended)

```bash
cp .env.example .env
docker compose up --build
```

- API:      http://localhost:8000/docs
- Frontend: http://localhost:5173
- Login:    `admin@threatplatform.dev` / `Admin@12345`

## Quick start (no Docker)

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env                                   # defaults to SQLite
python -m app.seeds.run                                # creates tables + admin user + demo env
uvicorn app.main:app --reload

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Try the pipeline end to end

```bash
python scripts/replay_logs.py            # pushes sample logs through ingest -> detect
python scripts/verify_audit_chain.py     # validates the audit hash chain
```

## Layout

| Path | What lives here |
|---|---|
| `backend/app/core/` | Config, DB, security, middleware — no business logic |
| `backend/app/modules/` | One folder per capability, each `domain / application / infrastructure / schemas` |
| `backend/app/api/v1/routes/` | Thin HTTP layer, calls services only |
| `backend/app/realtime/` | WebSocket connection manager + event bus |
| `detection-content/` | Detection rules as YAML — edit without touching Python |
| `frontend/src/features/` | One folder per dashboard screen |
| `deploy/` | Dockerfiles, compose, nginx |

## Architectural rules (enforced in CI)

1. `domain/` imports nothing from FastAPI, SQLAlchemy, or other modules.
2. Modules talk to each other through `application/*_service.py` only — never another module's repository.
3. Every destructive action passes `response/application/approval_gate.py`.
4. Every mutating request writes an `AuditEntry` (hash-chained, append-only).

Run `make arch` to check 1 and 2.

## Status

Working: auth/RBAC, environments, ingestion, normalization, rule-based detection,
risk scoring, incidents + evidence, review queue + decisions, response actions with
approval gate, audit hash chain, dashboard metrics, WebSocket live feed.

Stubbed with clear TODOs: anomaly/behaviour engines, correlation kill-chain,
threat-intel feed sync, PDF reports, email notifications.
