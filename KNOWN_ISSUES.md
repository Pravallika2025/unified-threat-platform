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

## Implemented & Verified Capabilities

The following subsystems are implemented, tested, and active:

- **Anomaly & Behaviour Engines:** Implemented (`AnomalyEngine`, `BehaviourEngine`), detecting volumetric bytes outliers, rapid port sweeps, and concurrent off-hours access.
- **Sequence / Kill-Chain Correlation:** Implemented (`KillChainBuilder`), ordering incident stages chronologically according to MITRE ATT&CK progression.
- **Threat-Intel Feed Sync:** Implemented (`FeedSyncService`), pulling indicators from AbuseIPDB, MITRE ATT&CK, and custom feeds.
- **Reporting System:** Implemented (`ReportService`, `HtmlRenderer`, `PdfRenderer`), supporting PDF, interactive HTML, CSV, and JSON exports with compliance signatures.
- **Notification Channels:** Multi-channel alert dispatching via in-app WebSockets, SMTP emails (for high/critical incidents), and HMAC-SHA256 signed webhooks.
- **Active Response & Remediation:** Implemented with `FirewallExecutor` (with strict IP allowlists), `AccountDisableExecutor`, and `EdrIsolateExecutor`.
- **Response Rollback:** Implemented with `RollbackService` allowing analysts to safely undo mitigation actions with tracked rollback tokens.
- **Retention & Data Lifecycle:** Implemented (`RetentionService`), pruning expired raw and normalized events while safeguarding active incident evidence and maintaining the cryptographic audit hash chain.
- **Automated Scheduling:** In-process `AsyncScheduler` integrated into FastAPI lifespan runs detection pipeline ticks every 60s, feed syncs every 6h, and daily retention enforcement.

## Before this goes anywhere near production

- Set a real `SECRET_KEY` and change both seeded passwords.
- Move to Postgres. The SQLite path exists so the project runs with zero setup.
- Enable MFA for every `super_admin`.
- Deleting audit rows breaks the hash chain. Export and verify before any
  retention pass; never delete in place.
- Keep `dry_run` on until you have tested a real executor against a lab device,
  and give every executor a hard allowlist it can never act on.
