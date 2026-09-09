#!/usr/bin/env python3
"""Push sample logs through the full pipeline and show what comes out.

  python scripts/replay_logs.py

Requires the API to be running. Uses the seeded admin account.
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

API = "http://localhost:8000/api/v1"
EMAIL = "admin@threatplatform.dev"
PASSWORD = "Admin@12345"


def post(path: str, body: dict, token: str | None = None) -> dict:
    request = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def get(path: str, token: str) -> dict:
    request = urllib.request.Request(
        f"{API}{path}", headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def build_records() -> list[dict]:
    """12 failed SSH logins from one address inside two minutes.

    This is what AUTH-0001 is written to catch (threshold is 8 in 5m).
    Addresses are from the RFC 5737 documentation range.
    """
    now = datetime.now(timezone.utc)
    records = []
    for i in range(12):
        ts = (now - timedelta(seconds=110 - i * 9)).isoformat()
        records.append(
            {
                "raw": (
                    f"{ts} sshd[4021]: Failed password for invalid user admin "
                    f"from 203.0.113.77 port 5{i:03d} ssh2"
                ),
                "timestamp": ts,
            }
        )
    # A couple of benign lines so the run is not uniformly hostile.
    records.append({"raw": f"{now.isoformat()} sshd[4022]: Accepted password for jsmith from 198.51.100.10 port 22 ssh2"})
    return records


def main() -> int:
    try:
        tokens = post("/auth/login", {"email": EMAIL, "password": PASSWORD})
    except urllib.error.URLError as exc:
        print(f"Could not reach the API at {API} — is it running?\n  {exc}")
        return 1

    token = tokens["access_token"]
    environments = get("/environments", token)
    if not environments:
        print("No environments found. Run: python -m app.seeds.run")
        return 1

    env = environments[0]
    print(f"Environment: {env['name']} ({env['type']})")

    result = post(
        "/ingestion/events",
        {"environment_id": env["id"], "source_type": "user_upload", "records": build_records()},
        token,
    )
    print(f"  1. Ingested   : {result['accepted']} accepted, {result['rejected']} rejected")

    normalized = post("/ingestion/normalize?limit=500", {}, token)
    print(f"  2. Normalized : {normalized['normalized']} events")

    alerts = post(
        "/alerts/detect", {"environment_id": env["id"], "lookback_minutes": 60}, token
    )
    print(f"  3. Detected   : {len(alerts)} alerts")
    for alert in alerts:
        print(f"       [{alert['severity']:8}] risk {alert['risk_score']:3}  {alert['title']}")
        print(f"                  entity: {alert['entity']}")

    incidents = get("/incidents?limit=5", token)
    print(f"  4. Incidents  : {len(incidents)} open")
    for incident in incidents[:5]:
        print(f"       {incident['reference']}  {incident['status']:14} risk {incident['risk_score']}")

    audit = get("/audit/verify", token)
    print(f"  5. Audit chain: valid={audit['valid']} ({audit['checked']} entries)")

    print("\nOpen http://localhost:5173 to see this on the dashboard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
