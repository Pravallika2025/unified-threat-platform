.PHONY: up down seed api web test arch fmt rules

up:    ; docker compose up --build
down:  ; docker compose down -v
seed:  ; cd backend && python -m app.seeds.run
api:   ; cd backend && uvicorn app.main:app --reload
web:   ; cd frontend && npm run dev
test:  ; cd backend && pytest -q
arch:  ; cd backend && lint-imports
fmt:   ; cd backend && ruff format app && ruff check --fix app
rules: ; python scripts/validate_rules.py
