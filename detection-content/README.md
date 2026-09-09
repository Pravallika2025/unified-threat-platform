# Detection Content

Rules are **data, not code**. Adding a detection means adding a YAML file here and
calling `POST /api/v1/alerts/rules/reload` — no Python change, no redeploy.

## Rule shape

```yaml
id: AUTH-0001                  # unique, prefix by category
title: Possible brute force attack
description: Many failed logins for one account or from one source
severity: high                 # critical | high | medium | low | info
enabled: true
environments: [all]            # or [hospital, government]
source_types: [all]            # or [windows_security, linux_auth]
attack:
  tactic: TA0006
  technique: T1110
logic:
  type: threshold              # threshold | match | sequence | anomaly
  where:
    - { field: event_action, op: eq, value: login_failed }
  group_by: [source_ip, user_name]
  count: 10
  window: 5m
risk:
  impact: 3
  likelihood: 4
response_suggestions: [monitor, block_ip]
```

## Rule types

| type | Engine | Status |
|---|---|---|
| `threshold` | RuleEngine — N matching events per group inside a sliding window | Implemented |
| `match` | RuleEngine — every event satisfying the conditions | Implemented |
| `sequence` | CorrelationService | Partial (clustering only) |
| `anomaly` | AnomalyEngine | Stub |

## Condition operators

`eq` `ne` `gt` `gte` `lt` `lte` `in` `not_in` `contains` `regex`

Fields are the canonical names from `NormalizedEvent`: `event_action`, `event_outcome`,
`event_category`, `source_ip`, `destination_ip`, `destination_port`, `user_name`,
`host_name`, `process_name`, `file_hash`, `url`, `bytes_out`.

## Before you commit a rule

Run `python scripts/validate_rules.py`. A rule that fires on every event is worse
than no rule — tune the threshold against real data before enabling it.
