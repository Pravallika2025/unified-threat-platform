# Build notes

## Bugs found and fixed while getting this running

These are recorded because each one is a trap you could hit again after editing.

1. **A repository method named `list` shadowed the builtin.** Inside a class body,
   `async def list(...)` binds `list` in the class namespace, so any *later*
   `-> list[Model]` annotation raised `TypeError: 'function' object is not
   subscriptable` at import time. Fixed with `from __future__ import annotations`
   in the affected modules. If you add a method named `list`, `dict`, or `type`,
   add that import too.

2. **`EmailStr` rejects `.local` domains** as special-use, so the original seeded
   `admin@platform.local` could never sign in. Seed accounts now use
   `@threatplatform.dev`.

3. **The audit chain never wrote a single row.** `sequence` was `Integer,
   autoincrement=True` but not a primary key, so no database populated it and every
   insert failed a NOT NULL check. `sequence` is now the primary key; `id` stays as
   a unique UUID.

4. **The audit chain failed verification after a restart.** Hashes committed to
   `created_at.isoformat()`, but SQLite drops tzinfo, so the value read back
   hashed differently than the value written. `canonical_timestamp()` normalises
   both sides to naive UTC.

5. **Auditing in middleware deadlocked on SQLite.** The middleware opened a second
   session while the request's transaction was still open. Auditing now happens in
   the request's own session — which is also more correct, since the audit entry is
   atomic with the change it records.

6. **Commits landed after the response was sent.** FastAPI closes dependency
   generators *after* handing the response to the client, so a caller could get
   200 OK and immediately issue a follow-up request that did not see the write.
   This broke the ingest → normalize → detect chain intermittently. Fixed with
   `UnitOfWorkRoute`, which commits before returning the response.
   Note: `include_router` preserves the *sub*-router's route class, so every module
   router sets `route_class=UnitOfWorkRoute` itself. A new route file must do the
   same or its writes will not commit.

7. **Naive vs aware datetime comparisons.** Any timestamp read from SQLite and
   compared in Python needs `as_utc()`. Comparisons done in SQL are fine.

## Not implemented yet

Clearly marked with TODO in the code:

- Anomaly and behaviour detection engines (return empty lists today)
- Sequence/kill-chain correlation (clustering by entity works; ordering does not)
- Threat-intel feed sync (the indicator table and matcher work; nothing populates
  them automatically)
- PDF and HTML report renderers (JSON and CSV work)
- Email and webhook notification channels (in-app WebSocket works)
- Real response executors — **everything runs through `NoopExecutor` in
  development and changes nothing.** `FirewallExecutor` deliberately raises
  `NotImplementedError` rather than silently doing nothing.
- Rollback of executed actions
- Retention enforcement
- Celery scheduling (the task functions exist and work; nothing calls them on a timer)

## Before this goes anywhere near production

- Set a real `SECRET_KEY` and change both seeded passwords.
- Move to Postgres. The SQLite path exists so the project runs with zero setup.
- Enable MFA for every `super_admin`.
- Deleting audit rows breaks the hash chain. Export and verify before any
  retention pass; never delete in place.
- Keep `dry_run` on until you have tested a real executor against a lab device,
  and give every executor a hard allowlist it can never act on.
