"""Evaluates threshold and match rules against normalized events.

Deliberately simple and deterministic — every finding must be explainable to an analyst.
"""

import logging
import operator
import re
from collections import defaultdict
from datetime import timedelta
from typing import Any

from app.modules.detection.domain.entities import DetectionRule, Finding, RuleType

logger = logging.getLogger(__name__)

OPERATORS = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
    "contains": lambda a, b: b is not None and str(b).lower() in str(a or "").lower(),
    "regex": lambda a, b: bool(re.search(str(b), str(a or ""), re.IGNORECASE)),
}


def parse_window(window: str) -> timedelta:
    """'5m' -> 5 minutes. Supports s, m, h, d."""
    units = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
    unit = window[-1].lower()
    if unit not in units:
        raise ValueError(f"Unsupported window unit in '{window}'")
    return timedelta(**{units[unit]: int(window[:-1])})


class RuleEngine:
    def evaluate(self, rule: DetectionRule, events: list[Any]) -> list[Finding]:
        if not rule.enabled or not events:
            return []
        if rule.rule_type == RuleType.THRESHOLD:
            return self._threshold(rule, events)
        if rule.rule_type == RuleType.MATCH:
            return self._match(rule, events)
        return []  # SEQUENCE -> correlation engine, ANOMALY -> anomaly engine

    # ---------- rule types ----------

    def _match(self, rule: DetectionRule, events: list[Any]) -> list[Finding]:
        matched = [e for e in events if self._conditions_pass(rule.logic.get("where", []), e)]
        if not matched:
            return []
        return [
            Finding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                environment_id=event.environment_id,
                event_ids=[event.id],
                entity=event.source_ip or event.user_name or event.host_name or "unknown",
                evidence={
                    "matched_on": rule.logic.get("where", []),
                    "event_action": event.event_action,
                    "source_ip": event.source_ip,
                    "user_name": event.user_name,
                    "message": (event.message or "")[:500],
                },
                attack=rule.attack,
            )
            for event in matched
        ]

    def _threshold(self, rule: DetectionRule, events: list[Any]) -> list[Finding]:
        logic = rule.logic
        threshold = int(logic.get("count", 5))
        window = parse_window(logic.get("window", "5m"))
        group_fields: list[str] = logic.get("group_by", ["source_ip"])

        candidates = [e for e in events if self._conditions_pass(logic.get("where", []), e)]
        if not candidates:
            return []

        groups: dict[tuple, list[Any]] = defaultdict(list)
        for event in candidates:
            key = tuple(str(getattr(event, f, None)) for f in group_fields)
            if all(part in ("None", "") for part in key):
                continue
            groups[key].append(event)

        findings: list[Finding] = []
        for key, group_events in groups.items():
            group_events.sort(key=lambda e: e.timestamp)
            hit = self._sliding_window_hit(group_events, threshold, window)
            if hit is None:
                continue
            findings.append(
                Finding(
                    rule_id=rule.id,
                    title=rule.title,
                    severity=rule.severity,
                    environment_id=hit[0].environment_id,
                    event_ids=[e.id for e in hit],
                    entity=" / ".join(k for k in key if k != "None"),
                    evidence={
                        "threshold": threshold,
                        "observed": len(hit),
                        "window": logic.get("window", "5m"),
                        "grouped_by": dict(zip(group_fields, key)),
                        "first_seen": hit[0].timestamp.isoformat(),
                        "last_seen": hit[-1].timestamp.isoformat(),
                    },
                    attack=rule.attack,
                )
            )
        return findings

    # ---------- helpers ----------

    @staticmethod
    def _sliding_window_hit(events: list[Any], threshold: int, window: timedelta):
        left = 0
        for right in range(len(events)):
            while events[right].timestamp - events[left].timestamp > window:
                left += 1
            if right - left + 1 >= threshold:
                return events[left : right + 1]
        return None

    @staticmethod
    def _conditions_pass(conditions: list[dict] | dict, event: Any) -> bool:
        if not conditions:
            return True
        if isinstance(conditions, dict):
            conditions = [conditions]

        for condition in conditions:
            field = condition.get("field")
            op = OPERATORS.get(condition.get("op", "eq"))
            expected = condition.get("value")
            if field is None or op is None:
                logger.warning("Malformed condition skipped: %s", condition)
                return False

            actual = getattr(event, field, None)
            if actual is None and field in (event.extra or {}):
                actual = event.extra[field]

            try:
                if not op(actual, expected):
                    return False
            except TypeError:
                return False
        return True
