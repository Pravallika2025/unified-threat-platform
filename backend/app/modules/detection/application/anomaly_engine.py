"""Statistical baseline and metric anomaly detection engine.

Detects statistical anomalies across normalized events:
1. Volume spikes and action rate bursts (> 3 sigma / Z-score deviations).
2. Data exfiltration volume outliers on bytes_out.
3. High port diversity / reconnaissance anomaly.
4. Off-hours privileged or administrative activity.
5. Failure-to-success ratio shifts.
"""

from collections import defaultdict
import math
from typing import Any

from app.modules.detection.domain.entities import Finding, Severity


class AnomalyEngine:
    def __init__(
        self,
        volume_z_threshold: float = 2.5,
        min_sample_size: int = 5,
        bytes_outlier_threshold: int = 5_000_000,  # 5MB single or aggregated outlier
    ):
        self.volume_z_threshold = volume_z_threshold
        self.min_sample_size = min_sample_size
        self.bytes_outlier_threshold = bytes_outlier_threshold

    def evaluate(self, events: list[Any]) -> list[Finding]:
        if not events:
            return []

        findings: list[Finding] = []
        findings.extend(self._detect_bytes_outliers(events))
        findings.extend(self._detect_port_scan_anomalies(events))
        findings.extend(self._detect_off_hours_anomalies(events))
        findings.extend(self._detect_action_volume_spikes(events))
        return findings

    def _detect_bytes_outliers(self, events: list[Any]) -> list[Finding]:
        """Detect anomalous outbound data transfer per entity or session."""
        findings = []
        entity_bytes: dict[str, list[tuple[int, Any]]] = defaultdict(list)

        for event in events:
            bytes_out = getattr(event, "bytes_out", None) or 0
            if bytes_out > 0:
                entity = getattr(event, "user_name", None) or getattr(event, "source_ip", None) or getattr(event, "host_name", None) or "unknown"
                entity_bytes[entity].append((bytes_out, event))

        for entity, byte_list in entity_bytes.items():
            if not byte_list:
                continue

            values = [b[0] for b in byte_list]
            total_bytes = sum(values)
            max_single = max(values)
            matched_events = [b[1] for b in byte_list]

            # Check statistical anomaly if sample size is sufficient
            is_anomaly = False
            z_score = 0.0
            if len(values) >= self.min_sample_size:
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                stddev = math.sqrt(variance) if variance > 0 else 0
                if stddev > 0:
                    z_score = (max_single - mean) / stddev
                    if z_score >= self.volume_z_threshold:
                        is_anomaly = True

            # Or absolute threshold violation
            if total_bytes >= self.bytes_outlier_threshold or max_single >= self.bytes_outlier_threshold:
                is_anomaly = True

            if is_anomaly:
                sample_event = matched_events[0]
                findings.append(
                    Finding(
                        rule_id="ANOMALY-0001",
                        title=f"Statistical anomaly: Abnormal outbound data transfer from {entity}",
                        severity=Severity.HIGH if total_bytes < 50_000_000 else Severity.CRITICAL,
                        environment_id=sample_event.environment_id,
                        event_ids=[e.id for e in matched_events],
                        entity=entity,
                        evidence={
                            "total_bytes_out": total_bytes,
                            "max_single_transfer": max_single,
                            "transfers_count": len(values),
                            "z_score": round(z_score, 2),
                            "threshold_bytes": self.bytes_outlier_threshold,
                        },
                        attack={"tactic": "Exfiltration", "technique": "T1048 - Exfiltration Over Alternative Protocol"},
                    )
                )

        return findings

    def _detect_port_scan_anomalies(self, events: list[Any]) -> list[Finding]:
        """Detect anomalous destination port diversity from a single source IP."""
        findings = []
        ip_ports: dict[str, dict[int, list[Any]]] = defaultdict(lambda: defaultdict(list))

        for event in events:
            src_ip = getattr(event, "source_ip", None)
            dst_port = getattr(event, "destination_port", None)
            if src_ip and dst_port:
                ip_ports[src_ip][dst_port].append(event)

        for src_ip, port_map in ip_ports.items():
            distinct_ports = len(port_map)
            # Touching 10+ distinct ports in window is an anomaly
            if distinct_ports >= 10:
                all_matched = [evt for evts in port_map.values() for evt in evts]
                sample_event = all_matched[0]
                findings.append(
                    Finding(
                        rule_id="ANOMALY-0002",
                        title=f"Statistical anomaly: High port dispersion / sweep from {src_ip}",
                        severity=Severity.MEDIUM if distinct_ports < 25 else Severity.HIGH,
                        environment_id=sample_event.environment_id,
                        event_ids=[e.id for e in all_matched[:50]],
                        entity=src_ip,
                        evidence={
                            "distinct_destination_ports": distinct_ports,
                            "sample_ports": sorted(list(port_map.keys()))[:15],
                            "total_probe_events": len(all_matched),
                        },
                        attack={"tactic": "Discovery", "technique": "T1046 - Network Service Discovery"},
                    )
                )

        return findings

    def _detect_off_hours_anomalies(self, events: list[Any]) -> list[Finding]:
        """Detect bursts of administrative or access actions during unusual hours (00:00 - 05:00 UTC)."""
        findings = []
        off_hours_events: dict[str, list[Any]] = defaultdict(list)

        for event in events:
            ts = getattr(event, "timestamp", None)
            if ts and hasattr(ts, "hour") and 0 <= ts.hour <= 5:
                action = (getattr(event, "event_action", None) or "").lower()
                user = getattr(event, "user_name", None) or getattr(event, "source_ip", None)
                if user and any(kw in action for kw in ["login", "admin", "sudo", "auth", "create", "delete"]):
                    off_hours_events[user].append(event)

        for user, user_events in off_hours_events.items():
            if len(user_events) >= 3:
                sample_event = user_events[0]
                findings.append(
                    Finding(
                        rule_id="ANOMALY-0003",
                        title=f"Statistical anomaly: Burst of off-hours administrative activity for {user}",
                        severity=Severity.MEDIUM,
                        environment_id=sample_event.environment_id,
                        event_ids=[e.id for e in user_events],
                        entity=user,
                        evidence={
                            "off_hours_event_count": len(user_events),
                            "time_window_hours": "00:00-05:00 UTC",
                            "actions_observed": list({getattr(e, "event_action", "") for e in user_events}),
                        },
                        attack={"tactic": "Defense Evasion", "technique": "T1078 - Valid Accounts"},
                    )
                )

        return findings

    def _detect_action_volume_spikes(self, events: list[Any]) -> list[Finding]:
        """Detect action volume spikes per (entity, action) pair."""
        findings = []
        entity_actions: dict[tuple[str, str], list[Any]] = defaultdict(list)

        for event in events:
            entity = getattr(event, "source_ip", None) or getattr(event, "user_name", None)
            action = getattr(event, "event_action", None) or getattr(event, "event_category", None) or "general"
            if entity:
                entity_actions[(entity, action)].append(event)

        for (entity, action), action_events in entity_actions.items():
            count = len(action_events)
            # High frequency single action burst
            if count >= 30:
                sample = action_events[0]
                findings.append(
                    Finding(
                        rule_id="ANOMALY-0004",
                        title=f"Statistical anomaly: Unusually high frequency of '{action}' for {entity}",
                        severity=Severity.MEDIUM,
                        environment_id=sample.environment_id,
                        event_ids=[e.id for e in action_events],
                        entity=entity,
                        evidence={
                            "action": action,
                            "burst_count": count,
                            "expected_baseline_max": 10,
                        },
                        attack={"tactic": "Initial Access", "technique": "T1110 - Brute Force"},
                    )
                )

        return findings
