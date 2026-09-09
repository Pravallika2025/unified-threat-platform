"""Data retention — section 11.

TODO: implement per-environment retention windows. Two hard constraints:
  1. Deleting audit rows breaks the hash chain. Export-then-truncate with a signed
     manifest, or move to cold storage; never delete in place.
  2. Evidence attached to an open incident is never eligible for deletion.
"""

DEFAULT_RETENTION_DAYS = {
    "raw_events": 90,
    "normalized_events": 180,
    "alerts": 365,
    "incidents": 1095,
    "audit_log": 2555,  # 7 years
}
